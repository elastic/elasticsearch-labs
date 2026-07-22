#Requires -Version 5.1
# Unified AI agent hook: logs tool/subagent calls from Claude Code and Cursor.
# No external dependencies. Works on Windows.
# Writes date-rotated JSONL files with user/host/agent identity.
# Cleans up log files older than 30 days.
#
# Covers both Cursor IDE (ide=cursor) and Cursor CLI (ide=cursor-cli).
# Detection: cursor_version in payload or CURSOR_VERSION env → Cursor.
#   CURSOR_CODE_REMOTE=true → remote; VSCODE_PID/CWD/IPC_HOOK set → IDE; absent → CLI.
#
# Deploy locations:
#   hooks.json:  %USERPROFILE%\.cursor\hooks.json (user-wide; read by both IDE and CLI)
#                or via Intune to C:\ProgramData\Cursor\hooks.json
#   Script:      C:\ai-hooks\log-tool-calls.ps1 (this file)
#   Logs:        %USERPROFILE%\.config\ai-hooks\logs\tool-calls-YYYY-MM-DD.jsonl

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$LogDir = Join-Path $env:USERPROFILE '.config\ai-hooks\logs'
$RetentionDays = 30

$Today = (Get-Date).ToUniversalTime().ToString('yyyy-MM-dd')
$LogFile = Join-Path $LogDir "tool-calls-$Today.jsonl"

$RawInput = @($input) -join "`n"
$BomIndex = $RawInput.IndexOf('{')
if ($BomIndex -gt 0) {
    $Input_ = $RawInput.Substring($BomIndex)
} else {
    $Input_ = $RawInput
}

# Output permission response FIRST for blocking hooks — before any filesystem work
# that could fail and exit early due to $ErrorActionPreference = 'Stop'
if ($Input_ -match '"hook_event_name"\s*:\s*"(beforeMCPExecution|beforeShellExecution|beforeReadFile|subagentStart|PreToolUse|SubagentStart)"') {
    Write-Output '{"permission":"allow"}'
}

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    & icacls "$LogDir" /inheritance:r /grant:r "${env:USERNAME}:(OI)(CI)F" 2>$null | Out-Null
}

$Timestamp = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')

$CurrentUser = $env:USERNAME
$HostnameVal = $env:COMPUTERNAME

# Detect agent and IDE
$Agent = 'claude-code'
$Ide = 'terminal'

# Check if hook input contains cursor_version (reliable on Windows)
if ($Input_ -match '"cursor_version"' -or $env:CURSOR_VERSION) {
    $Agent = 'cursor'
    if ($env:CURSOR_CODE_REMOTE -eq 'true') {
        $Ide = 'remote'
    } elseif ($env:VSCODE_PID -or $env:VSCODE_CWD -or $env:VSCODE_IPC_HOOK) {
        $Ide = 'cursor'
    } else {
        $Ide = 'cursor-cli'
    }
} elseif ($env:CURSOR_CODE_REMOTE -eq 'true') {
    $Agent = 'cursor'
    $Ide = 'remote'
} else {
    if ($env:VSCODE_PID -or $env:VSCODE_CWD -or $env:VSCODE_IPC_HOOK) {
        $Ide = 'vscode'
    } elseif ($env:JETBRAINS_IDE -or $env:IDEA_INITIAL_DIRECTORY) {
        $Ide = 'jetbrains'
    }
}

# Email: try env var, then git config, then Azure AD UPN (whoami /upn)
$Email = $env:CURSOR_USER_EMAIL
if (-not $Email) {
    try {
        $Email = (& git config --global user.email 2>$null)
    } catch {
        $Email = ''
    }
}
if (-not $Email) {
    try {
        $upn = (& whoami /upn 2>$null)
        if ($upn -and $upn -match '@') { $Email = $upn.Trim() }
    } catch { }
}
if (-not $Email) {
    try {
        $joinPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\CloudDomainJoin\JoinInfo'
        if (Test-Path $joinPath) {
            Get-ChildItem $joinPath -ErrorAction SilentlyContinue | ForEach-Object {
                $info = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
                if ($info.UserEmail -and $info.UserEmail -match '@') {
                    $Email = $info.UserEmail
                }
            }
        }
    } catch { }
}
if (-not $Email) { $Email = '' }

function ConvertTo-JsonEscaped($s) {
    $s = $s -replace '\\', '\\\\'
    $s = $s -replace '"', '\"'
    $s = $s -replace "`n", '\n'
    $s = $s -replace "`r", '\r'
    $s = $s -replace "`t", '\t'
    $s = $s -replace [char]8, '\b'
    $s = $s -replace [char]12, '\f'
    return $s
}

function Get-JsonStringValue($inputText, $key) {
    $pattern = '(?<!\\)"' + [regex]::Escape($key) + '"\s*:\s*"((?:[^"\\]|\\.)*)"'
    $match = [regex]::Match($inputText, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

function Get-JsonNumberValue($inputText, $key) {
    $pattern = '(?<!\\)"' + [regex]::Escape($key) + '"\s*:\s*([0-9]+(?:\.[0-9]+)?)'
    $match = [regex]::Match($inputText, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

function JsonStringOrNull($value) {
    if ([string]::IsNullOrEmpty($value)) {
        return 'null'
    }
    return '"' + (ConvertTo-JsonEscaped $value) + '"'
}

function JsonNumberOrNull($value) {
    if ([string]::IsNullOrEmpty($value)) {
        return 'null'
    }
    return $value
}

function Get-OutcomeFromFinalStatus($status) {
    if ([string]::IsNullOrEmpty($status)) {
        return $null
    }
    switch ($status.ToLowerInvariant()) {
        'success' { return 'success' }
        'succeeded' { return 'success' }
        'ok' { return 'success' }
        'failure' { return 'failure' }
        'failed' { return 'failure' }
        'error' { return 'failure' }
        'timeout' { return 'failure' }
        'cancelled' { return 'failure' }
        'canceled' { return 'failure' }
        'denied' { return 'failure' }
        Default { return $null }
    }
}

$EscUser = ConvertTo-JsonEscaped $CurrentUser
$EscHost = ConvertTo-JsonEscaped $HostnameVal
$EscAgent = ConvertTo-JsonEscaped $Agent
$EscIde = ConvertTo-JsonEscaped $Ide
$EscEmail = ConvertTo-JsonEscaped $Email

$HookEventName = Get-JsonStringValue $Input_ 'hook_event_name'
$ToolName = Get-JsonStringValue $Input_ 'tool_name'
$Model = Get-JsonStringValue $Input_ 'model'
$SessionId = Get-JsonStringValue $Input_ 'session_id'
$FinalStatus = Get-JsonStringValue $Input_ 'final_status'
$Duration = Get-JsonNumberValue $Input_ 'duration'
$DurationMs = Get-JsonNumberValue $Input_ 'duration_ms'

# Extract event-specific fields
$Command = $null
$FilePath = $null
$McpServer = $null
switch ($HookEventName) {
    'beforeShellExecution' { $Command = Get-JsonStringValue $Input_ 'command' }
    'afterShellExecution'  { $Command = Get-JsonStringValue $Input_ 'command' }
    'afterFileEdit'        { $FilePath = Get-JsonStringValue $Input_ 'file_path' }
    'beforeReadFile'       { $FilePath = Get-JsonStringValue $Input_ 'file_path' }
    { $_ -in 'beforeMCPExecution', 'afterMCPExecution' } {
        $McpServer = Get-JsonStringValue $Input_ 'command'
    }
    { $_ -in 'postToolUse', 'postToolUseFailure', 'PreToolUse', 'PostToolUse', 'PostToolUseFailure' } {
        switch ($ToolName) {
            { $_ -in 'Bash', 'Shell', 'shell_execution' } { $Command = Get-JsonStringValue $Input_ 'command' }
            { $_ -in 'Read', 'Write', 'Edit', 'MultiEdit', 'NotebookEdit' } { $FilePath = Get-JsonStringValue $Input_ 'file_path' }
        }
    }
}

$EventCategory = $null
$EventType = $null
$EventOutcome = $null

if ($HookEventName) {
    switch ($HookEventName) {
        'sessionStart' { $EventCategory = 'session'; $EventType = 'start' }
        'sessionEnd' { $EventCategory = 'session'; $EventType = 'end' }
        'stop' { $EventCategory = 'session'; $EventType = 'end' }
        'beforeShellExecution' { $EventCategory = 'process'; $EventType = 'start' }
        'afterShellExecution' { $EventCategory = 'process'; $EventType = 'end' }
        'beforeMCPExecution' { $EventCategory = 'process'; $EventType = 'start' }
        'afterMCPExecution' { $EventCategory = 'process'; $EventType = 'end' }
        'postToolUse' { $EventCategory = 'process'; $EventType = 'info'; $EventOutcome = 'success' }
        'PostToolUse' { $EventCategory = 'process'; $EventType = 'info'; $EventOutcome = 'success' }
        'postToolUseFailure' { $EventCategory = 'process'; $EventType = 'error'; $EventOutcome = 'failure' }
        'PostToolUseFailure' { $EventCategory = 'process'; $EventType = 'error'; $EventOutcome = 'failure' }
        'beforeReadFile' { $EventCategory = 'file'; $EventType = 'access' }
        'afterFileEdit' { $EventCategory = 'file'; $EventType = 'change' }
        'subagentStart' { $EventCategory = 'process'; $EventType = 'start' }
        'PreToolUse' { $EventCategory = 'process'; $EventType = 'start' }
        'SubagentStart' { $EventCategory = 'process'; $EventType = 'start' }
        'subagentStop' { $EventCategory = 'process'; $EventType = 'end' }
        'SubagentStop' { $EventCategory = 'process'; $EventType = 'end' }
        Default { $EventCategory = 'process'; $EventType = 'info' }
    }
}

$FinalOutcome = Get-OutcomeFromFinalStatus $FinalStatus
if (-not $EventOutcome -and $FinalOutcome) {
    $EventOutcome = $FinalOutcome
}

$EventDuration = $null
if ($DurationMs) {
    $EventDuration = [math]::Round([double]$DurationMs * 1000000)
} elseif ($Duration) {
    $EventDuration = [math]::Round([double]$Duration * 1000000000)
}

$HookEventJson = JsonStringOrNull $HookEventName
$ToolNameJson = JsonStringOrNull $ToolName
$ModelJson = JsonStringOrNull $Model
$SessionIdJson = JsonStringOrNull $SessionId
$CommandJson = JsonStringOrNull $Command
$FilePathJson = JsonStringOrNull $FilePath
$McpServerJson = JsonStringOrNull $McpServer
$FinalStatusJson = JsonStringOrNull $FinalStatus
$DurationJson = JsonNumberOrNull $Duration
$DurationMsJson = JsonNumberOrNull $DurationMs
$EventCategoryJson = JsonStringOrNull $EventCategory
$EventTypeJson = JsonStringOrNull $EventType
$EventOutcomeJson = JsonStringOrNull $EventOutcome
$EventDurationJson = JsonNumberOrNull $EventDuration

$RawPayload = $Input_
if ([string]::IsNullOrWhiteSpace($RawPayload) -or -not $RawPayload.StartsWith('{')) {
    $RawPayload = 'null'
} else {
    $RawPayload = $RawPayload -replace '\r\n|\n|\r', ' '
}

$Line = "{""timestamp"":""$Timestamp"",""user"":""$EscUser"",""email"":""$EscEmail"",""host"":""$EscHost"",""agent"":""$EscAgent"",""ide"":""$EscIde"",""model"":$ModelJson,""session_id"":$SessionIdJson,""hook_event_name"":$HookEventJson,""tool_name"":$ToolNameJson,""command"":$CommandJson,""file_path"":$FilePathJson,""mcp_server"":$McpServerJson,""final_status"":$FinalStatusJson,""duration"":$DurationJson,""duration_ms"":$DurationMsJson,""event"":{""kind"":""event"",""category"":$EventCategoryJson,""type"":$EventTypeJson,""action"":$HookEventJson,""outcome"":$EventOutcomeJson,""duration"":$EventDurationJson},""raw"":$RawPayload}"

[System.IO.File]::AppendAllText($LogFile, "$Line`n", [System.Text.UTF8Encoding]::new($false))

# Probabilistic cleanup (1% chance per run)
if ((Get-Random -Maximum 100) -eq 0) {
    Get-ChildItem -Path $LogDir -Filter 'tool-calls-*.jsonl' -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } |
        Remove-Item -Force -ErrorAction SilentlyContinue
}

exit 0
