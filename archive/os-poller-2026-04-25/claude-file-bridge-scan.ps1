param(
    [switch]$NoExec
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Shared guard helpers: Get-IndexEntryTopVersion, Test-SnapshotStillFresh,
# Invoke-GuardedLaunch. See bridge/bridge-spawn-revalidation-005.md (approved
# at -006) for the TOCTOU revalidation contract.
. (Join-Path $PSScriptRoot "bridge-scan-common.ps1")

$Workspace = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
$HarnessName = "claude"
$HarnessId = Get-BridgeScanHarnessId -Workspace $Workspace -HarnessName $HarnessName
$IndexPath = Join-Path $Workspace "bridge\INDEX.md"
$ProtocolPath = Join-Path $Workspace ".claude\rules\file-bridge-protocol.md"
$LogDir = Join-Path $Workspace "independent-progress-assessments\bridge-automation\logs"
$LockPath = Join-Path $LogDir "claude-file-bridge-scan.lock"
$StatusPath = Join-Path $LogDir "claude-scan-status.json"
$StaleLogPath = Join-Path $LogDir "bridge-snapshot-stale.log"
$MAX_ITEMS_PER_SPAWN = 1   # Conservative initial cap; raise after stable 48h at cap=1.

# S290 (WI-3171 poller investigation) — ROOT CAUSE OF 744 SILENT SPAWN FAILURES:
# The previous hardcoded path "C:\Users\micha\.local\bin\claude.exe" points to
# claude.exe version 2.1.39, which is silently broken for headless `-p` mode —
# it exits cleanly with zero API calls, zero tokens, and empty result.
#
# Proof: echo "hi" | claude.exe -p --output-format json (same prompt, same env):
#   2.1.39 : duration_api_ms=0,    num_turns=1, result="",      tokens=0/0
#   2.1.101: duration_api_ms=3604, num_turns=1, result="Hello!", tokens=2/5
#
# The Claude Desktop app keeps its bundled claude-code binary at:
#   %USERPROFILE%\AppData\Roaming\Claude\claude-code\<version>\claude.exe
# Desktop auto-updates this directory, so we discover the latest installed
# version at scan time rather than hardcoding a path that will drift.
$claudeCodeBase = Join-Path $env:USERPROFILE "AppData\Roaming\Claude\claude-code"
$latestClaudeVersion = Get-ChildItem -LiteralPath $claudeCodeBase -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^\d+\.\d+\.\d+$' } |
    Sort-Object { [version]$_.Name } -Descending |
    Select-Object -First 1

if ($null -eq $latestClaudeVersion) {
    throw "No claude-code version directory found under $claudeCodeBase; bridge automation cannot run. Install Claude Desktop or set CLAUDE_EXE env var."
}
$ClaudeExe = Join-Path $latestClaudeVersion.FullName "claude.exe"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-ScanLog {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-Content -LiteralPath (Join-Path $LogDir "claude-scan.log") -Value "$stamp $Message"
}

# S291 foreground repair (2026-04-15): mirror the Codex poller's Write-ScanStatus
# observability hook. Writes a machine-readable JSON status file on every state
# transition so Mike can observe poller liveness without relying on ephemeral
# Windows toasts (which proved insufficient during the 6-hour outage where the
# Claude poller was silently broken by a one-line PowerShell syntax error).
#
# Schema matches codex-scan-status.json field-for-field so a single tail/watcher
# can consume both files. Use a unique temp file per writer so overlapping
# scheduler ticks cannot collide on a fixed *.tmp path.
function Write-ScanStatus {
    param(
        [string]$State,
        [string]$Message,
        [string[]]$AttentionNames = @(),
        [string]$RunStamp = "",
        [string]$StdoutPath = "",
        [string]$StderrPath = "",
        # Child process identity fields — set immediately after Process.Start so
        # the liveness watcher can verify the child is still running via pid lookup.
        # Callers that do not pass these (e.g. "completed") leave them null, which
        # clears stale child data from the previous run.
        [object]$ChildPid = $null,
        [string]$ChildStartUtc = $null,
        [string]$ChildExe = $null
    )

    $now = Get-Date
    $payload = [ordered]@{
        updatedAtUtc = $now.ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
        updatedAtLocal = $now.ToString("yyyy-MM-ddTHH:mm:ssK")
        state = $State
        message = $Message
        attentionCount = @($AttentionNames).Count
        attentionNames = @($AttentionNames)
        runStamp = $RunStamp
        stdoutPath = $StdoutPath
        stderrPath = $StderrPath
        scanLogPath = (Join-Path $LogDir "claude-scan.log")
        indexPath = $IndexPath
        maxItemsPerSpawn = $MAX_ITEMS_PER_SPAWN
        childPid = $ChildPid
        childStartUtc = $ChildStartUtc
        childExe = $ChildExe
    }

    try {
        $tmpName = "{0}.{1}.{2}.tmp" -f ([System.IO.Path]::GetFileName($StatusPath)), $PID, ([guid]::NewGuid().ToString("N"))
        $tmpPath = Join-Path $LogDir $tmpName
        $payload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $tmpPath -Encoding UTF8
        if (Test-Path -LiteralPath $StatusPath) {
            Remove-Item -LiteralPath $StatusPath -Force
        }
        Move-Item -LiteralPath $tmpPath -Destination $StatusPath -Force
    } catch {
        # Non-fatal: if the status file cannot be written, the poller continues.
        # Log via the existing scan log so the failure is at least recorded.
        Write-ScanLog "WARN: Write-ScanStatus failed: $($_.Exception.Message)"
    }
}

# S290 poller repair Round 3 (2026-04-14): emit a Windows toast notification
# on every scan so Mike gets a 3-minute heartbeat without needing to open a
# terminal. Toasts display in the Windows Action Center and persist there
# until dismissed, giving asynchronous visibility into poller liveness.
#
# Uses the native Windows.UI.Notifications WinRT API — no module dependency.
# Works from a hidden scheduled task because the VBS wrapper launches
# powershell in the user's desktop session (shell.Run window mode 0 is
# hidden-but-not-session-0).
#
# Uses AppUserModelID "Microsoft.Windows.Shell.RunDialog" which is
# pre-registered on Windows 10/11 — we don't need to create a shortcut in
# the Start Menu to register our own AUMID.
#
# Non-fatal: if the toast API fails (Do Not Disturb, WinRT unavailable,
# etc.), the failure is swallowed and the poller continues.
function Show-PollerToast {
    param([string]$Title, [string]$Message)
    try {
        [void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime]
        $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $textNodes = $template.GetElementsByTagName("text")
        [void]$textNodes[0].AppendChild($template.CreateTextNode($Title))
        [void]$textNodes[1].AppendChild($template.CreateTextNode($Message))
        $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
        $notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Microsoft.Windows.Shell.RunDialog")
        $notifier.Show($toast)
    } catch {
        # Non-fatal: toast display failed. Do not disturb poller execution.
    }
}

function Get-BridgeEntries {
    param([string[]]$Lines)

    $entries = New-Object System.Collections.Generic.List[object]
    $current = $null

    foreach ($line in $Lines) {
        if ($line -match '^Document:\s*(.+?)\s*$') {
            if ($null -ne $current) {
                $entries.Add([pscustomobject]$current)
            }
            $current = [ordered]@{
                Name = $Matches[1]
                Versions = New-Object System.Collections.Generic.List[object]
            }
            continue
        }

        if ($null -ne $current -and $line -match '^(NEW|REVISED|GO|NO-GO|VERIFIED):\s+(.+?)\s*$') {
            $current.Versions.Add([pscustomobject]@{
                Status = $Matches[1]
                Path = $Matches[2]
            })
        }
    }

    if ($null -ne $current) {
        $entries.Add([pscustomobject]$current)
    }

    return $entries
}

function Get-AttentionEntries {
    if (-not (Test-Path -LiteralPath $ProtocolPath)) {
        throw "Missing file bridge protocol: $ProtocolPath"
    }
    if (-not (Test-Path -LiteralPath $IndexPath)) {
        throw "Missing bridge index: $IndexPath"
    }

    $lines = Get-Content -LiteralPath $IndexPath
    $entries = Get-BridgeEntries -Lines $lines
    # Prime looks for GO or NO-GO that hasn't been actioned yet.
    # VERIFIED is terminal (work complete) — skip unless Prime needs to commit.
    # A GO/NO-GO is "unactioned" only if it is the LATEST status line.
    # If Prime already submitted a NEW/REVISED above it, it was actioned.
    return @($entries | Where-Object {
        if ($_.Versions.Count -eq 0) { return $false }
        $latest = $_.Versions[0].Status
        # Only GO and NO-GO need Prime action (VERIFIED = terminal)
        $latest -eq "GO" -or $latest -eq "NO-GO"
    })
}

$lockStream = $null
try {
    $lockStream = [System.IO.File]::Open($LockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
} catch {
    $priorNames = @()
    $priorRunStamp = ""
    $priorStdoutPath = ""
    $priorStderrPath = ""
    $priorChildPid = $null
    $priorChildStartUtc = ""
    $priorChildExe = ""
    try {
        if (Test-Path -LiteralPath $StatusPath) {
            $prior = Get-Content -LiteralPath $StatusPath -Raw | ConvertFrom-Json -ErrorAction Stop
            if ($prior.state -eq "running") {
                $priorNames = @($prior.attentionNames)
                $priorRunStamp = [string]$prior.runStamp
                $priorStdoutPath = [string]$prior.stdoutPath
                $priorStderrPath = [string]$prior.stderrPath
                $priorChildPid = $prior.childPid
                $priorChildStartUtc = [string]$prior.childStartUtc
                $priorChildExe = [string]$prior.childExe
            }
        }
    } catch {
        # Best effort only; the skip log still records the overlap.
    }
    Write-ScanLog "skipped: previous scan still running"
    Write-ScanStatus `
        -State "skipped" `
        -Message "skipped: previous scan still running" `
        -AttentionNames $priorNames `
        -RunStamp $priorRunStamp `
        -StdoutPath $priorStdoutPath `
        -StderrPath $priorStderrPath `
        -ChildPid $priorChildPid `
        -ChildStartUtc $priorChildStartUtc `
        -ChildExe $priorChildExe
    Show-PollerToast -Title "Bridge scan" -Message "skipped (prior scan still running)"
    exit 0
}

try {
    $RoleAuthority = Test-BridgeScanRoleAuthority `
        -Workspace $Workspace `
        -HarnessId $HarnessId `
        -ExpectedRole "prime-builder" `
        -ScannerName "Claude automated Prime Builder bridge continuation scan"
    Write-ScanLog $RoleAuthority.Message
    if (-not $RoleAuthority.Allowed) {
        $pausedMessage = "paused (role authority blocked): $($RoleAuthority.Message)"
        Write-ScanStatus -State "paused" -Message $pausedMessage
        Show-PollerToast -Title "Bridge scan" -Message "paused (role authority blocked)"
        exit 0
    }

    $attention = @(Get-AttentionEntries)
    if ($attention.Count -eq 0) {
        Write-ScanLog "Bridge scan: clear."
        Write-ScanStatus -State "clear" -Message "Bridge scan: clear."
        Show-PollerToast -Title "Bridge scan" -Message "clear (nothing to action)"
        exit 0
    }

    # Oldest-first: INDEX.md is newest-first; reverse a clone so $oldestFirst[0] = oldest entry.
    # Use [object[]]::Clone() so [array]::Reverse() does not mutate the $attention backing array.
    $oldestFirst = [object[]]$attention.Clone()
    [array]::Reverse($oldestFirst)

    $selectedCount = [Math]::Min($MAX_ITEMS_PER_SPAWN, $oldestFirst.Count)
    $selected      = @($oldestFirst[0..($selectedCount - 1)])
    if ($selectedCount -lt $oldestFirst.Count) {
        $skipped = @($oldestFirst[$selectedCount..($oldestFirst.Count - 1)])
    } else {
        $skipped = @()
    }

    $allNames  = ($attention | ForEach-Object { $_.Name }) -join ", "
    $selNames  = ($selected  | ForEach-Object { $_.Name }) -join ", "
    $skipNames = if ($skipped.Count -gt 0) { ($skipped | ForEach-Object { $_.Name }) -join ", " } else { "(none)" }

    Write-ScanLog "Bridge scan: $($attention.Count) entries need attention: $allNames"
    $attentionNameArray = @($attention | ForEach-Object { $_.Name })
    $selectedNameArray  = @($selected  | ForEach-Object { $_.Name })
    if ($skipped.Count -gt 0) {
        Write-ScanLog "Bridge scan cap=${MAX_ITEMS_PER_SPAWN}: selected=[$selNames] skipped=[$skipNames]"
        Write-ScanStatus -State "attention" -Message "Bridge scan: $($attention.Count) entries need attention; cap=${MAX_ITEMS_PER_SPAWN} selected=[$selNames]" -AttentionNames $attentionNameArray
        Show-PollerToast -Title "Bridge scan" -Message "$($selected.Count) of $($attention.Count) selected: $selNames"
    } else {
        Write-ScanStatus -State "attention" -Message "Bridge scan: $($attention.Count) entries need attention: $allNames" -AttentionNames $attentionNameArray
        Show-PollerToast -Title "Bridge scan" -Message "$($attention.Count) entry/entries need attention: $allNames"
    }

    if ($NoExec) {
        exit 2
    }

    # TOCTOU revalidation (bridge-spawn-revalidation-006 GO):
    # Between the INDEX read above ($attention / $selected) and the child-agent
    # spawn below, Codex or a manual edit could append a newer verdict to the
    # same entry. Capture the selected entry's top status+file as a snapshot
    # and let Invoke-GuardedLaunch re-read the INDEX immediately before launch.
    # The launch scriptblock below owns the full child lifecycle (ClaudeExe
    # test, Process.Start, WaitForExit, JSON validation, logging) so the
    # guard abstraction does not leak process state across its boundary.
    $firstSelected = $selected[0]
    $snapshot = [pscustomobject]@{
        DocumentName = $firstSelected.Name
        Status       = $firstSelected.Versions[0].Status
        File         = $firstSelected.Versions[0].Path
    }

    $launchAction = {
        if (-not (Test-Path -LiteralPath $ClaudeExe)) {
        throw "Claude CLI not found: $ClaudeExe"
    }
    Write-ScanLog "using ClaudeExe=$ClaudeExe (version $($latestClaudeVersion.Name))"

    $runStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $stdoutPath = Join-Path $LogDir "claude-$runStamp.stdout.log"
    $stderrPath = Join-Path $LogDir "claude-$runStamp.stderr.log"

    Write-ScanStatus -State "running" `
        -Message "claude exec running for $($selected.Count) selected item(s) (full queue: $($attention.Count))" `
        -AttentionNames $selectedNameArray `
        -RunStamp $runStamp `
        -StdoutPath $stdoutPath `
        -StderrPath $stderrPath

    # Build per-entry description lines for selected entries only.
    $selectedEntryLines = ($selected | ForEach-Object {
        $latest = $_.Versions[0]
        "  - Document: $($_.Name) | Status: $($latest.Status) | File: $($latest.Path)"
    }) -join "`n"

    # Per S307 hardcoded-path directive: workspace path is interpolated from
    # $Workspace (resolved at script top from $PSScriptRoot), not hardcoded.
    $prompt = @"
You are Prime Builder running an automated file bridge scan for Agent Red Customer Engagement.

Workspace:
$Workspace

Effective role: Prime Builder

Role authority:
- Harness self-identification: $HarnessId
- Role map source: harness-state/harness-registry.json (canonical role registry; legacy role-assignments.json mirror is orphan per Slice 1 retirement)
- Required durable role at spawn time: harness $($RoleAuthority.HarnessId) role $($RoleAuthority.ExpectedRole)
- Observed durable role at spawn time: harness $($RoleAuthority.HarnessId) role $($RoleAuthority.ActiveRole)

THIS SPAWN IS CAPPED to $($selected.Count) entry/entries (cap=$MAX_ITEMS_PER_SPAWN, oldest-first selection from a queue of $($attention.Count)).
Process ONLY the entries listed below. Do NOT read bridge/INDEX.md to discover
additional actionable entries and do NOT action any entry not listed here.
All other actionable entries are reserved for subsequent scan cycles.

Entries to process:
$selectedEntryLines

For each listed entry:
  - GO:       Read the GO file and the approved proposal. Begin implementation per memory/work_list.md.
  - NO-GO:    Read the NO-GO file. Address all findings. Write a revised proposal as the next
              version number. Update bridge/INDEX.md with a REVISED entry for only this document.
  - VERIFIED: Report verified. If implementation is uncommitted, commit it.

Before writing any implementation result, re-read `harness-state/harness-registry.json`.
If harness `$HarnessId` no longer declares role `prime-builder`, report `ROLE-AUTHORITY-BLOCKED`.
Do not implement, revise, or file bridge updates. Every implementation or
revision file you create must include a `## Role Authority` section with the
role map path, harness ID, required role, and observed role.

Key files: CLAUDE.md, memory/MEMORY.md, memory/work_list.md
"@

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $ClaudeExe
    $psi.WorkingDirectory = $Workspace
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true

    # S290 poller repair Round 2 (2026-04-14): inject CLAUDE_CODE_OAUTH_TOKEN
    # from a persisted local file so the scheduled-task spawn inherits the
    # same credentials as an interactive Claude Code session.
    #
    # Root cause of the 401 cascade: when Claude Desktop launches an
    # interactive Claude Code session, its launcher reads the fresh OAuth
    # token from the encrypted `oauth:tokenCache` in
    # %APPDATA%\Claude\config.json and injects it into the child process'
    # environment as CLAUDE_CODE_OAUTH_TOKEN. Windows Task Scheduler spawns
    # run in a completely separate process tree that never sees this env var,
    # so they fall back to reading %USERPROFILE%\.claude\.credentials.json
    # which contains an expired refresh_token post-update → 401.
    #
    # Fix: Prime (running in the interactive session that DOES have a fresh
    # env var) writes the current token to .local/claude-oauth-token.txt
    # once per session. The PS1 reads that file on every spawn and sets
    # the env var on the ProcessStartInfo so the headless spawn inherits
    # working credentials.
    #
    # Security: .local/ is gitignored. The file contains an OAuth access
    # token that expires periodically. When tokens rotate, Prime refreshes
    # the file from the new session's env var.
    $oauthTokenPath = Join-Path $PSScriptRoot ".local\claude-oauth-token.txt"
    if (Test-Path -LiteralPath $oauthTokenPath) {
        $oauthToken = (Get-Content -LiteralPath $oauthTokenPath -Raw).Trim()
        if ($oauthToken) {
            $psi.EnvironmentVariables["CLAUDE_CODE_OAUTH_TOKEN"] = $oauthToken
            Write-ScanLog "injected CLAUDE_CODE_OAUTH_TOKEN from .local/claude-oauth-token.txt ($($oauthToken.Length) bytes)"
        } else {
            Write-ScanLog "WARN: .local/claude-oauth-token.txt exists but is empty; spawn will use default auth path"
        }
    } else {
        Write-ScanLog "WARN: .local/claude-oauth-token.txt missing; spawn will use default auth path (likely to fail with 401 post-update)"
    }

    # S290 (WI-3171 poller investigation): added --output-format json so we can
    # parse num_turns and duration_api_ms to detect zero-turn no-ops. The live
    # spawns between 2026-04-11 and 2026-04-14 all produced 3-byte text output
    # with zero API calls (zero-turn no-ops), and the old wrapper only checked
    # exit code, so 744 broken spawns in 3 days were invisible.
    $psi.Arguments = "--dangerously-skip-permissions -p --output-format json `"$prompt`""

    $proc = [System.Diagnostics.Process]::Start($psi)
    # Publish child pid immediately after Process.Start (before WaitForExit) so
    # the liveness watcher can verify the child is still alive via pid + start-time.
    # This is the real live signal: the status file now contains the child's pid
    # while it is actually running, not after it completes.
    Write-ScanStatus -State "running" `
        -Message ("claude exec running for {0} selected item(s) (full queue: {1})" -f $selected.Count, $attention.Count) `
        -AttentionNames $selectedNameArray `
        -RunStamp $runStamp `
        -StdoutPath $stdoutPath `
        -StderrPath $stderrPath `
        -ChildPid $proc.Id `
        -ChildStartUtc $proc.StartTime.ToUniversalTime().ToString("o") `
        -ChildExe $proc.StartInfo.FileName
    $proc.StandardInput.Close()

    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()
    # S290 poller repair (2026-04-14): reduced spawn timeout from 90 min to
    # 15 min. 90 min was set to cover long implementation runs but let
    # pathological hangs cascade into zombie accumulation. On 2026-04-14 the
    # Claude Code update put claude.exe into a token-refresh hang state that
    # wasn't releasing for the full 90 min, so concurrent scans piled up.
    # 15 min is still generous for any normal implementation run (historical
    # claude.exe round trips complete in <60s for scan-only and <10 min for
    # typical bridge implementation work).
    $claudeTimeoutMs = 900000  # 15 minutes
    $completed = $proc.WaitForExit($claudeTimeoutMs)
    if (-not $completed) {
        try { $proc.Kill($true) } catch { }
        throw ("claude exec timed out after 15 minutes for $($selected.Count) selected item(s) " +
               "(full queue: $($attention.Count)); stdout=$stdoutPath stderr=$stderrPath")
    }

    $stdoutTask.Wait()
    $stderrTask.Wait()
    Set-Content -LiteralPath $stdoutPath -Value $stdoutTask.Result
    Set-Content -LiteralPath $stderrPath -Value $stderrTask.Result

    if ($proc.ExitCode -ne 0) {
        # S290 poller repair: surface authentication failures in the scan log
        # instead of burying them in the stdout file. When claude.exe fails
        # auth, its JSON output usually contains "authentication" or
        # "API Error: 40" — match those so operators see the real cause in
        # claude-scan.log without having to cat the per-run stdout file.
        $rawOutSnippet = ""
        try {
            $rawOutSnippet = (Get-Content -LiteralPath $stdoutPath -Raw -ErrorAction SilentlyContinue) -replace "`r?`n", " "
            if ($rawOutSnippet.Length -gt 500) { $rawOutSnippet = $rawOutSnippet.Substring(0, 500) }
        } catch { $rawOutSnippet = "" }
        $authHint = ""
        if ($rawOutSnippet -match 'authentication|API Error: 40[13]|Invalid.*credential') {
            $authHint = " [AUTH FAILURE: re-login via Claude Desktop or set ANTHROPIC_API_KEY]"
        }
        throw "claude exec exited with $($proc.ExitCode)$authHint; selected=$($selected.Count) full=$($attention.Count); stdout=$stdoutPath stderr=$stderrPath"
    }

    # S290 (WI-3171 poller investigation): validate the JSON result block
    # actually represents a real API interaction. `claude -p --output-format json`
    # always emits a result object on exit 0, even when no API call was made —
    # that state has num_turns=1, duration_api_ms=0, input_tokens=0, result="".
    # Treat any zero-turn/zero-API-duration outcome as a spawn failure so the
    # scan log surfaces it instead of silently reporting "claude exec completed".
    $outSize = (Get-Item -LiteralPath $stdoutPath).Length
    if ($outSize -lt 50) {
        throw "claude exec produced suspiciously small output ($outSize bytes); stdout=$stdoutPath stderr=$stderrPath"
    }

    $rawOut = Get-Content -LiteralPath $stdoutPath -Raw
    try {
        $result = $rawOut | ConvertFrom-Json -ErrorAction Stop
    } catch {
        throw "claude exec produced unparseable JSON output: $($_.Exception.Message); stdout=$stdoutPath stderr=$stderrPath"
    }

    if ($null -eq $result.num_turns -or $result.num_turns -lt 1 -or
        $null -eq $result.duration_api_ms -or $result.duration_api_ms -eq 0) {
        throw ("claude exec was a zero-turn no-op (num_turns={0}, duration_api_ms={1}, input_tokens={2}, output_tokens={3}); " +
               "the headless claude.exe completed cleanly but never called the API; stdout={4} stderr={5}") -f `
               $result.num_turns, $result.duration_api_ms, $result.usage.input_tokens, $result.usage.output_tokens, $stdoutPath, $stderrPath
    }

    if ($result.is_error) {
        throw "claude exec result.is_error=true: $($result.result); stdout=$stdoutPath stderr=$stderrPath"
    }

    Write-ScanLog (("claude exec completed for {0} selected item(s) (full queue: {1}); " +
        "num_turns={2} api_ms={3} in_tokens={4} out_tokens={5}; stdout={6}") -f `
        $selected.Count, $attention.Count, $result.num_turns, $result.duration_api_ms, `
        $result.usage.input_tokens, $result.usage.output_tokens, $stdoutPath)
    Write-ScanStatus -State "completed" `
        -Message ("claude exec completed for {0} selected item(s) (full queue: {1}); num_turns={2} api_ms={3}" -f `
            $selected.Count, $attention.Count, $result.num_turns, $result.duration_api_ms) `
        -AttentionNames $selectedNameArray `
        -RunStamp $runStamp `
        -StdoutPath $stdoutPath `
        -StderrPath $stderrPath
    }

    $guardResult = Invoke-GuardedLaunch `
        -SelectedSnapshot $snapshot `
        -IndexPath        $IndexPath `
        -LaunchAction     $launchAction `
        -StaleLogPath     $StaleLogPath

    if (-not $guardResult.Launched) {
        $staleMsg = "SNAPSHOT-STALE: aborted launch (document=$($snapshot.DocumentName) expected=$($snapshot.Status):$($snapshot.File))"
        Write-ScanLog $staleMsg
        Write-ScanStatus -State "stale" -Message $staleMsg -AttentionNames $attentionNameArray
        Show-PollerToast -Title "Bridge scan" -Message "snapshot stale - aborted"
        exit 0
    }
} catch {
    Write-ScanLog "ERROR: $($_.Exception.Message)"
    Write-ScanStatus -State "error" -Message "ERROR: $($_.Exception.Message)"
    exit 1
} finally {
    if ($null -ne $lockStream) {
        $lockStream.Dispose()
    }
}
