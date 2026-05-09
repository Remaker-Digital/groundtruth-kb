# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
# Smart-poller wrapper — interactive use + doctor's -ValidateOnly mode.
#
# DAEMON PATH note (per smart-poller-notify-activation -006 follow-up):
# The Windows Scheduled Task no longer targets THIS .ps1 wrapper directly. On
# Windows 11 with Windows Terminal as default console host, `powershell.exe
# -WindowStyle Hidden` does not reliably hide the launched PowerShell window,
# and the .ps1's `& $pythonw ...` invocation interacts with WshShell.Run such
# that Task Scheduler stops tracking the chain. The daemon path now uses
# `scripts/run_smart_bridge_poller.vbs` invoked via wscript.exe, calling
# pythonw.exe directly. THIS file is retained for:
#   1. Interactive invocation (e.g., manual `powershell -File run_smart_bridge_poller.ps1`)
#   2. Doctor's `-ValidateOnly` mode (validates the wrapper's effective
#      $runnerPath assignment by executing it without starting the poller)
#
# PHASE 2 PATH REBASE: the $runnerPath assignment below MUST be updated in
# parallel with the corresponding `runnerPath = ...` line in
# run_smart_bridge_poller.vbs. Both files share the same Phase-1 → Phase-2
# path transition. Edit BOTH in the Phase 2 path-rebase commit.

param(
    [int]$IntervalSeconds = 15,
    [switch]$ValidateOnly
)

$ErrorActionPreference = "Stop"

# Project root is the parent dir of this script's containing dir.
$projectRoot = Split-Path -Parent $PSScriptRoot

# Phase-1 path. Phase 2 will rewrite this single line per the checklist above.
$runnerPath = Join-Path $projectRoot "groundtruth-kb\scripts\bridge_poller_runner.py"

if (-not (Test-Path $runnerPath)) {
    if ($ValidateOnly) {
        Write-Error "Smart-poller runner not found at $runnerPath. Verify Phase 2 path rebase if expected."
        exit 1
    }
    throw "Smart-poller runner not found at $runnerPath. Verify Phase 2 path rebase if expected."
}

if ($ValidateOnly) {
    # -ValidateOnly mode (per smart-poller-notify-activation -006 Finding 2):
    # Resolve $runnerPath, confirm it exists, exit 0. Used by the doctor check
    # to verify the wrapper's actual assignment (not just a substring match in
    # comments). Does NOT start the long-running poller.
    Write-Output "OK runner=$runnerPath"
    exit 0
}

# Use pythonw.exe (windowless Python variant) so the python child does not
# attach a console. python.exe would inherit/create a console when launched
# from Task Scheduler on Windows 11 + Terminal, surfacing as a visible window
# even when the parent powershell.exe was launched with -WindowStyle Hidden.
# pythonw.exe is the standard Python solution for daemon-mode execution.
$pythonw = (Get-Command pythonw).Path
& $pythonw $runnerPath --interval $IntervalSeconds --quiet
