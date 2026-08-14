#!/usr/bin/env bash
# Unified AI agent hook: logs tool/subagent calls from Claude Code and Cursor.
# No external dependencies (no jq). Works on Linux (and macOS).
# Writes date-rotated JSONL files with user/host/agent identity.
# Cleans up log files older than 30 days.
#
# Covers both Cursor IDE (ide=cursor) and Cursor CLI (ide=cursor-cli).
# Detection: cursor_version in payload or CURSOR_VERSION env → Cursor.
#   CURSOR_CODE_REMOTE=true → remote; VSCODE_PID/CWD/IPC_HOOK set → IDE; absent → CLI.
#
# Deploy locations (system-wide install; see install.sh):
#   hooks.json:  Linux: /etc/cursor/hooks.json
#                macOS: /Library/Application Support/Cursor/hooks.json
#   Script:      /usr/local/share/ai-hooks/log-tool-calls.sh (this file, any OS)
#   Logs:        ~/.config/ai-hooks/logs/tool-calls-YYYY-MM-DD.jsonl

USER_HOME="${HOME:-}"
if [ -z "$USER_HOME" ]; then
  if [ "$(uname -s)" = "Darwin" ]; then
    USER_HOME=$(dscl . -read "/Users/$(id -un)" NFSHomeDirectory 2>/dev/null | awk '{print $2}')
  else
    USER_HOME=$(getent passwd "$(id -un)" 2>/dev/null | cut -d: -f6)
  fi
fi
if [ -z "$USER_HOME" ]; then
  echo "log-tool-calls.sh: cannot resolve home directory for user $(id -un 2>/dev/null || echo unknown)" >&2
  exit 0
fi

LOG_DIR="$USER_HOME/.config/ai-hooks/logs"
RETENTION_DAYS=30

TODAY=$(date -u +"%Y-%m-%d")
LOG_FILE="$LOG_DIR/tool-calls-${TODAY}.jsonl"

#ensure there is piped input before calling cat so it doesn't hang
if [ -t 0 ]; then
  echo "log-tool-calls.sh: no piped input, exiting" >&2
  exit 1
fi

# Map all control bytes to spaces: newlines/carriage returns for the one-line
# form, and any raw control bytes (invalid inside JSON strings) so extracted
# values and the embedded raw payload always stay valid JSON.
INPUT_ONE_LINE=$(LC_ALL=C tr '\000-\037' ' ')

# Parse all fields in one native-code pass. Repeated Bash pattern removals become
# extremely slow when optional keys are absent from large hook payloads.
FIELD_SEPARATOR=$'\034'
EXTRACTED_FIELDS=$(printf '%s\n' "$INPUT_ONE_LINE" | LC_ALL=C awk '
  function wanted_string(key) {
    return key == "hook_event_name" || key == "tool_name" || key == "model" ||
      key == "session_id" || key == "final_status" || key == "command" ||
      key == "file_path"
  }

  # BSD awk substr() cost grows with the length of the source string, so all
  # scanning goes through a small sliding window refilled as the parse
  # position advances. Requests beyond the window come back truncated, which
  # only affects pathological tokens larger than the window itself.
  function chunk_at(position, size) {
    if (position < window_start ||
        (position + size - 1 > window_end && window_end < input_length)) {
      window_start = position
      window_buffer = substr(input, position, 16384)
      window_end = position + length(window_buffer) - 1
    }
    return substr(window_buffer, position - window_start + 1, size)
  }

  function skip_string(position, chunk, consumed, next_character) {
    position++
    while (position <= input_length) {
      chunk = chunk_at(position, 256)
      if (match(chunk, /^([^"\\]|\\.)*/) != 1) {
        return 0
      }

      consumed = RLENGTH
      position += consumed
      if (consumed < length(chunk)) {
        next_character = chunk_at(position, 1)
        if (next_character == "\"") {
          return position + 1
        }
        if (next_character == "\\" && position < input_length) {
          position += 2
        } else {
          return 0
        }
      }
    }
    return 0
  }

  function skip_composite(position, depth, remainder, character) {
    depth = 0
    while (position <= input_length) {
      remainder = chunk_at(position, 256)
      character = substr(remainder, 1, 1)

      if (character == "\"") {
        if (match(remainder, /^"([^"\\]|\\.)*"/) == 1) {
          position += RLENGTH
        } else {
          position = skip_string(position)
          if (position == 0) {
            return input_length + 1
          }
        }
      } else if (character == "{" || character == "[") {
        depth++
        composite_closer[depth] = character == "{" ? "}" : "]"
        position++
      } else if (character == "}" || character == "]") {
        if (depth == 0 || character != composite_closer[depth]) {
          return input_length + 1
        }
        delete composite_closer[depth]
        depth--
        position++
        if (depth == 0) {
          return position
        }
      } else if (match(remainder, /^[^][{}"]+/) == 1) {
        position += RLENGTH
      } else {
        position++
      }
    }
    return position
  }

  # Advance past whitespace in bounded chunks. Never copies the full string
  # tail, so per-member cost stays constant regardless of payload size.
  function skip_whitespace(position, chunk) {
    while (position <= input_length) {
      chunk = chunk_at(position, 256)
      if (match(chunk, /^[[:space:]]+/) != 1) {
        return position
      }
      position += RLENGTH
      if (RLENGTH < length(chunk)) {
        return position
      }
    }
    return position
  }

  # Scans one JSON object starting at an opening "{". capture_mode "top"
  # populates present[]/string_values[]/number_values[] for every wanted
  # top-level key, and additionally descends one level into a "tool_input"
  # member (Claude Code PreToolUse/PostToolUse payloads nest command/
  # file_path there) via a recursive "tool_input" call, which only captures
  # command/file_path and never overrides a value already seen at top level.
  # Returns the position just after the matching "}", or input_length + 1 on
  # a malformed/truncated object.
  function parse_object(position, capture_mode,    member_count, character, key_start, key_end, key, value_start, value_end, chunk) {
    position++
    while (position <= input_length) {
      position = skip_whitespace(position)
      character = chunk_at(position, 1)
      if (character == "}") {
        position++
        if (capture_mode == "top" && skip_whitespace(position) > input_length) {
          parsed_object = 1
        }
        return position
      }
      if (member_count > 0) {
        if (character != ",") {
          return input_length + 1
        }
        position = skip_whitespace(position + 1)
        if (chunk_at(position, 1) == "}") {
          return input_length + 1
        }
      }
      if (chunk_at(position, 1) != "\"") {
        return input_length + 1
      }

      key_start = position
      key_end = skip_string(position)
      if (key_end == 0) {
        return input_length + 1
      }
      key = chunk_at(key_start + 1, key_end - key_start - 2)
      if (capture_mode == "top") {
        present[key] = 1
      }
      position = skip_whitespace(key_end)
      if (chunk_at(position, 1) != ":") {
        return input_length + 1
      }
      position = skip_whitespace(position + 1)

      character = chunk_at(position, 1)
      if (character == "\"") {
        value_start = position
        value_end = skip_string(position)
        if (value_end == 0) {
          return input_length + 1
        }
        if (capture_mode == "top" && wanted_string(key)) {
          string_values[key] = substr(input, value_start + 1, value_end - value_start - 2)
        } else if (capture_mode == "tool_input" && (key == "command" || key == "file_path") && !(key in string_values)) {
          string_values[key] = substr(input, value_start + 1, value_end - value_start - 2)
        }
        position = value_end
      } else if (character == "{") {
        if (capture_mode == "top" && key == "tool_input") {
          position = parse_object(position, "tool_input")
        } else {
          position = skip_composite(position)
        }
      } else if (character == "[") {
        position = skip_composite(position)
      } else {
        # Scalar tokens (numbers, true/false/null) fit well within 64 bytes.
        chunk = chunk_at(position, 64)
        if (match(chunk, /^-?[0-9]+([.][0-9]+)?([eE][+-]?[0-9]+)?/) == 1) {
          if (capture_mode == "top" && (key == "duration" || key == "duration_ms")) {
            number_values[key] = substr(chunk, RSTART, RLENGTH)
          }
          position += RLENGTH
        } else if (match(chunk, /^(true|false|null)/) == 1) {
          position += RLENGTH
        } else {
          return input_length + 1
        }
      }
      member_count++
    }
    return input_length + 1
  }

  {
    input = $0
    input_length = length(input)
    window_start = 1
    window_end = 0
    position = skip_whitespace(1)

    if (chunk_at(position, 1) == "{") {
      parse_object(position, "top")
    }

    separator = sprintf("%c", 28)
    values[1] = string_values["hook_event_name"]
    values[2] = string_values["tool_name"]
    values[3] = string_values["model"]
    values[4] = string_values["session_id"]
    values[5] = string_values["final_status"]
    values[6] = number_values["duration"]
    values[7] = number_values["duration_ms"]
    values[8] = string_values["command"]
    values[9] = string_values["file_path"]
    values[10] = ("cursor_version" in present) ? "1" : "0"
    values[11] = parsed_object ? "1" : "0"

    for (i = 1; i <= 11; i++) {
      if (i > 1) {
        printf "%s", separator
      }
      printf "%s", values[i]
    }
  }
')
IFS="$FIELD_SEPARATOR" read -r HOOK_EVENT_NAME TOOL_NAME MODEL SESSION_ID FINAL_STATUS DURATION DURATION_MS INPUT_COMMAND INPUT_FILE_PATH HAS_CURSOR_VERSION HAS_TOP_LEVEL_OBJECT <<< "$EXTRACTED_FIELDS"

# Output permission response FIRST for blocking hooks, before any filesystem work
# that could fail and exit early
case "$HOOK_EVENT_NAME" in
  beforeMCPExecution|beforeShellExecution|beforeReadFile|subagentStart|PreToolUse|SubagentStart)
    echo '{"permission":"allow"}'
    ;;
esac

(umask 077 && mkdir -p "$LOG_DIR")

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

CURRENT_USER="${USER:-$(whoami)}"
HOSTNAME_VAL=$(hostname -s 2>/dev/null || hostname 2>/dev/null || uname -n 2>/dev/null || printf '%s' "${HOSTNAME:-unknown}")
HOSTNAME_VAL="${HOSTNAME_VAL%%.*}"

detect_agent_and_ide() {
  if [ "$HAS_CURSOR_VERSION" = "1" ] || [ -n "${CURSOR_VERSION:-}" ]; then
    AGENT="cursor"
    if [ "${CURSOR_CODE_REMOTE:-}" = "true" ]; then
      IDE="remote"
    elif [ -n "${VSCODE_PID:-}" ] || [ -n "${VSCODE_CWD:-}" ] || [ -n "${VSCODE_IPC_HOOK:-}" ]; then
      IDE="cursor"
    else
      IDE="cursor-cli"
    fi
  elif [ "${CURSOR_CODE_REMOTE:-}" = "true" ]; then
    AGENT="cursor"
    IDE="remote"
  else
    AGENT="claude-code"
    if [ -n "${WINDSURF_SESSION_ID:-}" ] || [ -n "${WINDSURF_CHANNEL:-}" ]; then
      IDE="windsurf"
    elif [ -n "${VSCODE_PID:-}" ] || [ -n "${VSCODE_CWD:-}" ] || [ -n "${VSCODE_IPC_HOOK:-}" ]; then
      IDE="vscode"
    elif [ -n "${JETBRAINS_IDE:-}" ] || [ -n "${IDEA_INITIAL_DIRECTORY:-}" ]; then
      IDE="jetbrains"
    else
      IDE="terminal"
    fi
  fi
}

detect_agent_and_ide
EMAIL="${CURSOR_USER_EMAIL:-}"
if [ -z "$EMAIL" ]; then
  EMAIL="$(git config --global user.email 2>/dev/null || echo '')"
fi

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  s="${s//$'\b'/\\b}"
  s="${s//$'\f'/\\f}"
  printf '%s' "$s"
}

ESCAPED_USER=$(json_escape "$CURRENT_USER")
ESCAPED_HOST=$(json_escape "$HOSTNAME_VAL")
ESCAPED_AGENT=$(json_escape "$AGENT")
ESCAPED_IDE=$(json_escape "$IDE")
ESCAPED_EMAIL=$(json_escape "$EMAIL")

# Extract event-specific fields
COMMAND=""
FILE_PATH=""
MCP_SERVER=""
case "$HOOK_EVENT_NAME" in
  beforeShellExecution|afterShellExecution)
    COMMAND="$INPUT_COMMAND"
    ;;
  afterFileEdit|beforeReadFile)
    FILE_PATH="$INPUT_FILE_PATH"
    ;;
  beforeMCPExecution|afterMCPExecution)
    MCP_SERVER="$INPUT_COMMAND"
    ;;
  postToolUse|postToolUseFailure|PreToolUse|PostToolUse|PostToolUseFailure)
    case "$TOOL_NAME" in
      Bash|Shell|shell_execution)
        COMMAND="$INPUT_COMMAND"
        ;;
      Read|Write|Edit|MultiEdit|NotebookEdit)
        FILE_PATH="$INPUT_FILE_PATH"
        ;;
    esac
    ;;
esac

EVENT_CATEGORY=""
EVENT_TYPE=""
EVENT_OUTCOME=""
EVENT_DURATION=""

if [ -n "$HOOK_EVENT_NAME" ]; then
  case "$HOOK_EVENT_NAME" in
    sessionStart)
      EVENT_CATEGORY="session"
      EVENT_TYPE="start"
      ;;
    sessionEnd|stop)
      EVENT_CATEGORY="session"
      EVENT_TYPE="end"
      ;;
    beforeShellExecution|beforeMCPExecution|subagentStart|PreToolUse|SubagentStart)
      EVENT_CATEGORY="process"
      EVENT_TYPE="start"
      ;;
    afterShellExecution|afterMCPExecution|subagentStop|SubagentStop)
      EVENT_CATEGORY="process"
      EVENT_TYPE="end"
      ;;
    postToolUse|PostToolUse)
      EVENT_CATEGORY="process"
      EVENT_TYPE="info"
      EVENT_OUTCOME="success"
      ;;
    postToolUseFailure|PostToolUseFailure)
      EVENT_CATEGORY="process"
      EVENT_TYPE="error"
      EVENT_OUTCOME="failure"
      ;;
    beforeReadFile)
      EVENT_CATEGORY="file"
      EVENT_TYPE="access"
      ;;
    afterFileEdit)
      EVENT_CATEGORY="file"
      EVENT_TYPE="change"
      ;;
    *)
      EVENT_CATEGORY="process"
      EVENT_TYPE="info"
      ;;
  esac
fi

normalize_final_status() {
  local status
  status=$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')
  case "$status" in
    success|succeeded|ok)
      printf 'success'
      ;;
    failure|failed|error|timeout|cancelled|canceled|denied)
      printf 'failure'
      ;;
    *)
      printf ''
      ;;
  esac
}

if [ -z "$EVENT_OUTCOME" ] && [ -n "$FINAL_STATUS" ]; then
  EVENT_OUTCOME="$(normalize_final_status "$FINAL_STATUS")"
fi

if [ -n "$DURATION_MS" ]; then
  EVENT_DURATION=$(awk "BEGIN {printf \"%.0f\", $DURATION_MS * 1000000}")
elif [ -n "$DURATION" ]; then
  EVENT_DURATION=$(awk "BEGIN {printf \"%.0f\", $DURATION * 1000000000}")
fi
# Reject non-finite results (e.g. from an oversized exponent like 1e400),
# since bare inf/nan tokens are not valid JSON numbers.
case "$EVENT_DURATION" in
  *[!0-9-]*|"") EVENT_DURATION="" ;;
esac

json_string_or_null() {
  local value="$1"
  if [ -n "$value" ]; then
    printf '"'
    printf '%s' "$value" | LC_ALL=C sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
    printf '"'
  else
    printf 'null'
  fi
}

json_number_or_null() {
  local value="$1"
  if [ -n "$value" ]; then
    printf '%s' "$value"
  else
    printf 'null'
  fi
}

RAW_PAYLOAD="$INPUT_ONE_LINE"
if [ "$HAS_TOP_LEVEL_OBJECT" != "1" ]; then
  RAW_PAYLOAD="null"
fi

printf '{"timestamp":"%s","user":"%s","email":"%s","host":"%s","agent":"%s","ide":"%s","model":%s,"session_id":%s,"hook_event_name":%s,"tool_name":%s,"command":%s,"file_path":%s,"mcp_server":%s,"final_status":%s,"duration":%s,"duration_ms":%s,"event":{"kind":"event","category":%s,"type":%s,"action":%s,"outcome":%s,"duration":%s},"raw":%s}\n' \
  "$TIMESTAMP" "$ESCAPED_USER" "$ESCAPED_EMAIL" "$ESCAPED_HOST" "$ESCAPED_AGENT" "$ESCAPED_IDE" \
  "$(json_string_or_null "$MODEL")" "$(json_string_or_null "$SESSION_ID")" "$(json_string_or_null "$HOOK_EVENT_NAME")" "$(json_string_or_null "$TOOL_NAME")" \
  "$(json_string_or_null "$COMMAND")" "$(json_string_or_null "$FILE_PATH")" \
  "$(json_string_or_null "$MCP_SERVER")" "$(json_string_or_null "$FINAL_STATUS")" \
  "$(json_number_or_null "$DURATION")" "$(json_number_or_null "$DURATION_MS")" \
  "$(json_string_or_null "$EVENT_CATEGORY")" "$(json_string_or_null "$EVENT_TYPE")" "$(json_string_or_null "$HOOK_EVENT_NAME")" "$(json_string_or_null "$EVENT_OUTCOME")" \
  "$(json_number_or_null "$EVENT_DURATION")" "$RAW_PAYLOAD" >> "$LOG_FILE"

chmod 0600 "$LOG_FILE" 2>/dev/null

if (( RANDOM % 100 == 0 )); then
  find "$LOG_DIR" -name "tool-calls-*.jsonl" -type f -mtime +"$RETENTION_DAYS" -delete 2>/dev/null
fi

exit 0
