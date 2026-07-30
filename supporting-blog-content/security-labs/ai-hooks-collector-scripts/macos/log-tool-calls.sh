#!/bin/bash
# Unified AI agent hook: logs tool/subagent calls from Claude Code and Cursor.
# No external dependencies (no jq). Works on macOS and Linux.
# Writes date-rotated JSONL files with user/host/agent identity.
# Cleans up log files older than 30 days.
#
# Covers both Cursor IDE (ide=cursor) and Cursor CLI (ide=cursor-cli).
# Detection: cursor_version in payload or CURSOR_VERSION env → Cursor.
#   CURSOR_CODE_REMOTE=true → remote; VSCODE_PID/CWD/IPC_HOOK set → IDE; absent → CLI.
#
# Deploy locations:
#   hooks.json:  /Library/Application Support/Cursor/hooks.json (system-wide; read by both IDE and CLI)
#   Script:      /usr/local/share/ai-hooks/log-tool-calls.sh (this file)
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

INPUT=$(cat)
INPUT_ONE_LINE="${INPUT//$'\n'/ }"
INPUT_ONE_LINE="${INPUT_ONE_LINE//$'\r'/ }"

# Output permission response FIRST for blocking hooks — before any filesystem work
# that could fail and exit early due to set -euo pipefail
if [[ "$INPUT" == *'"hook_event_name"'*'"beforeMCPExecution"'* ]] || \
   [[ "$INPUT" == *'"hook_event_name"'*'"beforeShellExecution"'* ]] || \
   [[ "$INPUT" == *'"hook_event_name"'*'"beforeReadFile"'* ]] || \
   [[ "$INPUT" == *'"hook_event_name"'*'"subagentStart"'* ]] || \
   [[ "$INPUT" == *'"hook_event_name"'*'"PreToolUse"'* ]] || \
   [[ "$INPUT" == *'"hook_event_name"'*'"SubagentStart"'* ]]; then
  echo '{"permission":"allow"}'
fi

(umask 077 && mkdir -p "$LOG_DIR")

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

CURRENT_USER="${USER:-$(whoami)}"
HOSTNAME_VAL=$(hostname -s 2>/dev/null || hostname 2>/dev/null || uname -n 2>/dev/null || printf '%s' "${HOSTNAME:-unknown}")
HOSTNAME_VAL="${HOSTNAME_VAL%%.*}"

detect_agent_and_ide() {
  if [[ "$INPUT" == *'"cursor_version"'* ]] || [ -n "${CURSOR_VERSION:-}" ]; then
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

extract_json_string() {
  local key="$1"
  local remainder="${INPUT_ONE_LINE#*\"$key\"}"
  if [ "$remainder" = "$INPUT_ONE_LINE" ]; then
    return
  fi
  printf '%s' "$remainder" | sed -nE 's/^[[:space:]]*:[[:space:]]*"(([^"\\]|\\.)*)".*/\1/p' | head -n 1
}

extract_json_number() {
  local key="$1"
  local remainder="${INPUT_ONE_LINE#*\"$key\"}"
  if [ "$remainder" = "$INPUT_ONE_LINE" ]; then
    return
  fi
  printf '%s' "$remainder" | sed -nE 's/^[[:space:]]*:[[:space:]]*([0-9]+(\.[0-9]+)?).*/\1/p' | head -n 1
}

ESCAPED_USER=$(json_escape "$CURRENT_USER")
ESCAPED_HOST=$(json_escape "$HOSTNAME_VAL")
ESCAPED_AGENT=$(json_escape "$AGENT")
ESCAPED_IDE=$(json_escape "$IDE")
ESCAPED_EMAIL=$(json_escape "$EMAIL")

HOOK_EVENT_NAME=$(extract_json_string "hook_event_name")
TOOL_NAME=$(extract_json_string "tool_name")
MODEL=$(extract_json_string "model")
SESSION_ID=$(extract_json_string "session_id")
FINAL_STATUS=$(extract_json_string "final_status")
DURATION=$(extract_json_number "duration")
DURATION_MS=$(extract_json_number "duration_ms")

# Extract event-specific fields
COMMAND=""
FILE_PATH=""
MCP_SERVER=""
case "$HOOK_EVENT_NAME" in
  beforeShellExecution|afterShellExecution)
    COMMAND=$(extract_json_string "command")
    ;;
  afterFileEdit|beforeReadFile)
    FILE_PATH=$(extract_json_string "file_path")
    ;;
  beforeMCPExecution|afterMCPExecution)
    MCP_SERVER=$(extract_json_string "command")
    ;;
  postToolUse|postToolUseFailure|PreToolUse|PostToolUse|PostToolUseFailure)
    case "$TOOL_NAME" in
      Bash|Shell|shell_execution)
        COMMAND=$(extract_json_string "command")
        ;;
      Read|Write|Edit|MultiEdit|NotebookEdit)
        FILE_PATH=$(extract_json_string "file_path")
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

json_string_or_null() {
  local value="$1"
  if [ -n "$value" ]; then
    printf '"%s"' "$(json_escape "$value")"
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

RAW_PAYLOAD="$INPUT"
if [[ -z "$RAW_PAYLOAD" ]] || [[ "$RAW_PAYLOAD" != "{"* ]]; then
  RAW_PAYLOAD="null"
else
  RAW_PAYLOAD="${RAW_PAYLOAD//$'\n'/ }"
  RAW_PAYLOAD="${RAW_PAYLOAD//$'\r'/ }"
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
