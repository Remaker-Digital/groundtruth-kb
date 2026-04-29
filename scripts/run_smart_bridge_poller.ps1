# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
# Smart-poller wrapper. Phase-2-stable target for the GTKB-SmartBridgePoller
# scheduled task.
#
# Per bridge/gtkb-bridge-poller-notify-activation-2026-04-29-004.md GO
# (REVISED-1 at -003 §4.1-§4.2):
#   - The Windows Scheduled Task targets THIS WRAPPER, not the runner directly.
#   - Phase 2 of the isolation plan moves groundtruth-kb/ content to platform
#     root. When that happens, only the $runnerPath line below changes — the
#     OS task registration is unaffected.
#
# Phase 2 path-rebase checklist item: change $runnerPath from
#     Join-Path $projectRoot "groundtruth-kb\scripts\bridge_poller_runner.py"
# to:
#     Join-Path $projectRoot "scripts\bridge_poller_runner.py"
# (no other changes required to this file or to Task Scheduler state).

param(
    [int]$IntervalSeconds = 15
)

$ErrorActionPreference = "Stop"

# Project root is the parent dir of this script's containing dir.
$projectRoot = Split-Path -Parent $PSScriptRoot

# Phase-1 path. Phase 2 will rewrite this single line per the checklist above.
$runnerPath = Join-Path $projectRoot "groundtruth-kb\scripts\bridge_poller_runner.py"

if (-not (Test-Path $runnerPath)) {
    throw "Smart-poller runner not found at $runnerPath. Verify Phase 2 path rebase if expected."
}

$python = (Get-Command python).Path
& $python $runnerPath --interval $IntervalSeconds --quiet
