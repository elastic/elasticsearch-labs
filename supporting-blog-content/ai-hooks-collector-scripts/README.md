# Cursor Agent Hook - Tool Call Logger

Logs Cursor AI agent tool calls to date-rotated JSONL files for security monitoring. Covers both the **Cursor IDE** and the **Cursor CLI** (`cursor-agent`). Elastic Agent picks up the logs via filestream and ships them to Elasticsearch.

> For background and context, see the accompanying blog post: `<BLOG_POST_URL>`

## How it works

`hooks.json` tells Cursor to run the logging script on every agent tool call. The script appends a JSONL entry to a daily log file and exits.

Both the Cursor IDE and Cursor CLI read the same `hooks.json` location for the current platform, so a single deployment covers both surfaces. Log entries are distinguished by the `ide` field:

| `ide` value | Source |
|-------------|--------|
| `cursor` | Cursor IDE (desktop app) |
| `cursor-cli` | Cursor CLI (`cursor-agent` binary) |
| `remote` | Cursor IDE in a remote workspace |

Detection uses two signals: `CURSOR_CODE_REMOTE=true` identifies remote workspaces (`ide=remote`). Otherwise, the presence of VSCode environment variables (`VSCODE_PID`, `VSCODE_CWD`, `VSCODE_IPC_HOOK`) distinguishes IDE from CLI — the Cursor IDE (built on Electron/VSCode) sets these in hook processes; the CLI does not. Both surfaces include `cursor_version` in the hook payload.

Hooks fire on:

| Hook | When | Needs response |
|------|------|----------------|
| `sessionStart` | New agent conversation created | No |
| `sessionEnd` | Agent conversation ends | No |
| `beforeShellExecution` | Agent runs a shell command | Yes |
| `afterShellExecution` | Shell command completes | No |
| `beforeMCPExecution` | Agent calls an MCP tool | Yes |
| `afterMCPExecution` | MCP tool call completes | No |
| `postToolUse` | Any tool call succeeds | No |
| `postToolUseFailure` | Any tool call fails, times out, or is denied | No |
| `afterFileEdit` | Agent edits a file | No |
| `beforeReadFile` | Agent reads a file | Yes |
| `stop` | Agent loop ends | No |
| `subagentStart` | Agent spawns a sub-agent | Yes |
| `subagentStop` | Sub-agent completes | No |

Some hooks require a permission response before Cursor proceeds. The script always responds with `{"permission":"allow"}` — nothing is blocked, only logged. If the script crashes before responding, Cursor fails open by default (the action proceeds).

Log files are written to `~/.config/ai-hooks/logs/tool-calls-YYYY-MM-DD.jsonl`. Files older than 30 days are eligible for cleanup, but cleanup runs opportunistically (a probabilistic cleanup pass during hook execution), so retention is not guaranteed to end exactly at 30 days.

### Log entry format

```json
{
  "timestamp": "2026-04-13T09:06:20Z",
  "user": "jsmith",
  "email": "jsmith@example.com",
  "host": "macbook-jsmith",
  "agent": "cursor",
  "ide": "cursor-cli",
  "hook_event_name": "postToolUse",
  "tool_name": "Read",
  "command": null,
  "file_path": "/path/to/file.py",
  "mcp_server": null,
  "duration": 7.4,
  "duration_ms": null,
  "final_status": null,
  "event": {
    "kind": "event",
    "category": "process",
    "type": "info",
    "action": "postToolUse",
    "outcome": "success",
    "duration": 7400000000
  },
  "raw": { ...original Cursor hook payload... }
}
```

Event-specific fields are extracted based on hook type:

| Field | Populated when |
|-------|----------------|
| `command` | `beforeShellExecution`, `afterShellExecution`, or `postToolUse` with shell tools |
| `file_path` | `afterFileEdit`, `beforeReadFile`, or `postToolUse` with file tools |
| `mcp_server` | `beforeMCPExecution`, `afterMCPExecution` (Cursor's MCP server name) |

---

## macOS deployment

### Files

| File | Deploy path |
|------|-------------|
| `macos/hooks.json` | `/Library/Application Support/Cursor/hooks.json` (system-wide) |
| `macos/log-tool-calls.sh` | `/usr/local/share/ai-hooks/log-tool-calls.sh` |

> **Important:** The script must live under `/usr/local/share/ai-hooks/`, not under `/Library/Application Support/Cursor/`. Cursor splits paths containing spaces when invoking hooks, which silently breaks execution.

### Install

```bash
bash macos/install.sh
```

Requires sudo. Copies hooks.json and the logging script to their deploy paths, sets ownership to root:wheel, and applies correct permissions. Restart Cursor after install.

### Manual deployment

```bash
sudo mkdir -p /usr/local/share/ai-hooks
sudo cp macos/hooks.json "/Library/Application Support/Cursor/hooks.json"
sudo cp macos/log-tool-calls.sh /usr/local/share/ai-hooks/log-tool-calls.sh
sudo chown root:wheel "/Library/Application Support/Cursor/hooks.json"
sudo chown root:wheel /usr/local/share/ai-hooks/log-tool-calls.sh
sudo chmod 644 "/Library/Application Support/Cursor/hooks.json"
sudo chmod 755 /usr/local/share/ai-hooks/log-tool-calls.sh
```

Restart Cursor after the files land.

### Validation

**IDE:**

1. Open Cursor and run any agent prompt that triggers a tool call (e.g. ask it to list files).
2. Check that a log file was created and contains an entry with `"ide":"cursor"`:
   ```bash
   grep '"ide":"cursor",' ~/.config/ai-hooks/logs/tool-calls-$(date -u +%Y-%m-%d).jsonl | tail -1
   ```
   > Note: the trailing comma anchors the match so it does not also match `"ide":"cursor-cli"`.

**CLI:**

> Requires the Cursor CLI to be installed. Install it with: `curl https://cursor.com/install -fsS | bash`
>
> Run the CLI validation from an **external terminal** (Terminal.app, iTerm2, SSH), not from the Cursor IDE's built-in terminal. The built-in terminal inherits `VSCODE_PID` from the IDE process, which causes `cursor-agent` sessions to be classified as `ide=cursor` instead of `ide=cursor-cli`.

1. Run a CLI session from any directory:
   ```bash
   cursor-agent --yolo --print "say hello"
   ```
2. Check that the entry shows `"ide":"cursor-cli"`:
   ```bash
   grep '"ide":"cursor-cli"' ~/.config/ai-hooks/logs/tool-calls-$(date -u +%Y-%m-%d).jsonl | tail -1
   ```

**JSON validity (both):**
```bash
python3 -c "import json,sys; [json.loads(l) for l in open(sys.argv[1])]" ~/.config/ai-hooks/logs/tool-calls-$(date -u +%Y-%m-%d).jsonl && echo OK
```

> Note: the log file is JSONL (one JSON object per line), so each line is validated individually. `python3 -m json.tool` parses only a single JSON value and will fail with "Extra data" on the second line — do not use it here.

---

## Linux deployment

### Files

| File | Deploy path |
|------|-------------|
| `linux/hooks.json` | `/etc/cursor/hooks.json` (system-wide) |
| `linux/log-tool-calls.sh` | `/usr/local/share/ai-hooks/log-tool-calls.sh` |

> **Important:** The script must live under `/usr/local/share/ai-hooks/`, not under `/etc/cursor/`. Cursor splits paths containing spaces when invoking hooks, which silently breaks execution.

### Install

```bash
sudo bash linux/install.sh
```

Requires root. Copies hooks.json and the logging script to their deploy paths, sets ownership to root:root, and applies correct permissions. Restart Cursor after install.

### Manual deployment

```bash
sudo mkdir -p /etc/cursor
sudo mkdir -p /usr/local/share/ai-hooks
sudo cp linux/hooks.json /etc/cursor/hooks.json
sudo cp linux/log-tool-calls.sh /usr/local/share/ai-hooks/log-tool-calls.sh
sudo chown root:root /etc/cursor/hooks.json
sudo chown root:root /usr/local/share/ai-hooks/log-tool-calls.sh
sudo chmod 644 /etc/cursor/hooks.json
sudo chmod 755 /usr/local/share/ai-hooks/log-tool-calls.sh
```

Restart Cursor after the files land.

### Validation

**IDE:**

1. Open Cursor and run any agent prompt that triggers a tool call (e.g. ask it to list files).
2. Check that a log file was created and contains an entry with `"ide":"cursor"`:
   ```bash
   grep '"ide":"cursor",' ~/.config/ai-hooks/logs/tool-calls-$(date -u +%Y-%m-%d).jsonl | tail -1
   ```
   > Note: the trailing comma anchors the match so it does not also match `"ide":"cursor-cli"`.

**CLI:**

> Requires the Cursor CLI to be installed. Install it with: `curl https://cursor.com/install -fsS | bash`
>
> Run the CLI validation from an **external terminal** (a separate shell session or SSH), not from the Cursor IDE's built-in terminal. The built-in terminal inherits `VSCODE_PID` from the IDE process, which causes `cursor-agent` sessions to be classified as `ide=cursor` instead of `ide=cursor-cli`.

1. Run a CLI session from any directory:
   ```bash
   cursor-agent --yolo --print "say hello"
   ```
2. Check that the entry shows `"ide":"cursor-cli"`:
   ```bash
   grep '"ide":"cursor-cli"' ~/.config/ai-hooks/logs/tool-calls-$(date -u +%Y-%m-%d).jsonl | tail -1
   ```

**JSON validity (both):**
```bash
cat ~/.config/ai-hooks/logs/tool-calls-$(date -u +%Y-%m-%d).jsonl | python3 -m json.tool --no-indent > /dev/null && echo OK
```

---

## Windows deployment

### Files

| File | Deploy path |
|------|-------------|
| `windows/hooks.json` | `%USERPROFILE%\.cursor\hooks.json` (user-wide) or via Intune to system-level path |
| `windows/log-tool-calls.ps1` | `C:\ai-hooks\log-tool-calls.ps1` |

### Install

```powershell
powershell -ExecutionPolicy Bypass -File windows\install.ps1
```

Requires running as Administrator (writing to `C:\ai-hooks` requires elevated privileges). Copies hooks.json and the logging script to their deploy paths. Restart Cursor after install.

### Manual deployment

Run the following in an elevated (Administrator) PowerShell prompt:

```powershell
New-Item -ItemType Directory -Path "C:\ai-hooks" -Force
Copy-Item windows\log-tool-calls.ps1 C:\ai-hooks\log-tool-calls.ps1
Copy-Item windows\hooks.json "$env:USERPROFILE\.cursor\hooks.json"
```

Restart Cursor after the files land.

### Validation

**IDE:**

1. Open Cursor and run any agent prompt that triggers a tool call.
2. Check that a log file was created and contains an entry with `"ide":"cursor"`:
   ```powershell
   $today = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd')
   Get-Content "$env:USERPROFILE\.config\ai-hooks\logs\tool-calls-$today.jsonl" |
     Where-Object { $_ -match '"ide":"cursor"[,}]' } | Select-Object -Last 1
   ```
   > Note: the regex anchor `[,}]` ensures this does not also match `"ide":"cursor-cli"`.

**CLI:**

> Requires the Cursor CLI to be installed separately from the IDE. Install it with:
> ```powershell
> irm 'https://cursor.com/install?win32=true' | iex
> ```
> After install, open a new PowerShell window and run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` to allow the CLI wrapper to run.
>
> Run the CLI validation from a **standalone PowerShell window**, not from the Cursor IDE's built-in terminal. The built-in terminal inherits `VSCODE_PID` from the IDE process, which causes `cursor-agent` sessions to be classified as `ide=cursor` instead of `ide=cursor-cli`.

1. Run a CLI session:
   ```powershell
   cursor-agent --yolo --print "say hello"
   ```
2. Check that the entry shows `"ide":"cursor-cli"`:
   ```powershell
   $today = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd')
   Get-Content "$env:USERPROFILE\.config\ai-hooks\logs\tool-calls-$today.jsonl" |
     Where-Object { $_ -like '*"ide":"cursor-cli"*' } | Select-Object -Last 1
   ```

**JSON validity (both):**
```powershell
$today = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd')
Get-Content "$env:USERPROFILE\.config\ai-hooks\logs\tool-calls-$today.jsonl" |
  ForEach-Object { $null = $_ | ConvertFrom-Json }
Write-Host OK
```

---

## Pipeline

```
Cursor IDE or CLI agent tool call
  → hooks.json (Cursor picks up at startup)
    → log-tool-calls.sh / log-tool-calls.ps1
      → ~/.config/ai-hooks/logs/tool-calls-YYYY-MM-DD.jsonl
        → Elastic Agent (filestream input, already deployed)
          → Elasticsearch
```

