#Requires -Version 5.1
# Installs the Cursor agent hook (Windows).
# Run from the windows/ directory or pass the correct path.
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

$HooksSrc  = Join-Path $ScriptDir 'hooks.json'
$ScriptSrc = Join-Path $ScriptDir 'log-tool-calls.ps1'
$HooksDst  = Join-Path $env:USERPROFILE '.cursor\hooks.json'
$ScriptDst = 'C:\ai-hooks\log-tool-calls.ps1'

foreach ($f in @($HooksSrc, $ScriptSrc)) {
    if (-not (Test-Path $f)) {
        Write-Error "Missing $f"
        exit 1
    }
}

Write-Host 'Installing Cursor agent hook...'

New-Item -ItemType Directory -Path 'C:\ai-hooks' -Force | Out-Null
New-Item -ItemType Directory -Path (Split-Path $HooksDst) -Force | Out-Null

Copy-Item $HooksSrc  $HooksDst  -Force
Copy-Item $ScriptSrc $ScriptDst -Force

Write-Host "Installed:"
Write-Host "  $HooksDst"
Write-Host "  $ScriptDst"
Write-Host ""
Write-Host "Restart Cursor to activate hooks."
