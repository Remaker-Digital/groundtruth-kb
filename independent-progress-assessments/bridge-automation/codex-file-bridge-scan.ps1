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
$IndexPath = Join-Path $Workspace "bridge\INDEX.md"
$ProtocolPath = Join-Path $Workspace ".claude\rules\file-bridge-protocol.md"
$LogDir = Join-Path $Workspace "independent-progress-assessments\bridge-automation\logs"
$LockPath = Join-Path $LogDir "codex-file-bridge-scan.lock"
$StatusPath = Join-Path $LogDir "codex-scan-status.json"
$StaleLogPath = Join-Path $LogDir "bridge-snapshot-stale.log"
$CodexExe = "C:\Users\micha\AppData\Local\OpenAI\Codex\bin\codex.exe"
$MAX_ITEMS_PER_SPAWN = 1   # Keep automated Codex scans bounded to avoid INDEX.md races.

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-ScanLog {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-Content -LiteralPath (Join-Path $LogDir "scan.log") -Value "$stamp $Message"
}

function Write-ScanStatus {
    param(
        [string]$State,
        [string]$Message,
        [string[]]$AttentionNames = @(),
        [string]$RunStamp = "",
        [string]$StdoutPath = "",
        [string]$StderrPath = "",
        [string]$LastMessagePath = "",
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
        lastMessagePath = $LastMessagePath
        scanLogPath = (Join-Path $LogDir "scan.log")
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
        Write-ScanLog "WARN: Write-ScanStatus failed: $($_.Exception.Message)"
    }
}

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
        # Non-fatal: the status JSON and scan log are the durable signal.
    }
}

function Test-InteractiveCodexDesktopRunning {
    try {
        $processes = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
            $_.Name -ieq "Codex.exe" -and
            $_.CommandLine -match "\\app\\Codex\.exe" -and
            $_.CommandLine -notmatch "--type="
        })
        return ($processes.Count -gt 0)
    } catch {
        Write-ScanLog "WARN: Codex desktop process check failed: $($_.Exception.Message)"
        return $false
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
    return @($entries | Where-Object {
        $_.Versions.Count -gt 0 -and ($_.Versions[0].Status -eq "NEW" -or $_.Versions[0].Status -eq "REVISED")
    })
}

function Invoke-CodexBridgeScan {
    param(
        [int]$AttentionCount,
        [object[]]$SelectedEntries,
        [string[]]$SelectedNames
    )

    if (-not (Test-Path -LiteralPath $CodexExe)) {
        throw "Codex executable not found: $CodexExe"
    }

    $runStamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
    $stdoutPath = Join-Path $LogDir "codex-$runStamp.stdout.log"
    $stderrPath = Join-Path $LogDir "codex-$runStamp.stderr.log"
    $lastMessagePath = Join-Path $LogDir "codex-$runStamp.last-message.md"
    $runMessage = "codex exec running for $($SelectedEntries.Count) selected item(s) (full queue: $AttentionCount): $($SelectedNames -join ', ')"
    Write-ScanLog $runMessage
    Write-ScanStatus -State "running" -Message $runMessage -AttentionNames $SelectedNames -RunStamp $runStamp -StdoutPath $stdoutPath -StderrPath $stderrPath -LastMessagePath $lastMessagePath

    $selectedEntryLines = ($SelectedEntries | ForEach-Object {
        $latest = $_.Versions[0]
        "  - Document: $($_.Name) | Status: $($latest.Status) | File: $($latest.Path)"
    }) -join "`n"

    $prompt = @"
You are Codex running an automated file bridge scan for Agent Red Customer Engagement.

Workspace:
E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement

THIS SPAWN IS CAPPED to $($SelectedEntries.Count) entry/entries (cap=$MAX_ITEMS_PER_SPAWN, oldest-first selection from a queue of $AttentionCount).
Process ONLY the entries listed below. Do NOT read bridge/INDEX.md to discover
additional actionable entries and do NOT action any entry not listed here.
All other actionable entries are reserved for subsequent scan cycles.

Entries to process:
$selectedEntryLines

For each listed entry:
1. Read .claude/rules/file-bridge-protocol.md.
2. Read the full bridge/INDEX.md entry for that document and all referenced version files in that entry.
3. Perform the Loyal Opposition proposal review or verification.
4. Create the next numbered bridge/{descriptive-name}-{NNN}.md review file with verdict, rationale, findings with evidence paths, and required action items or conditions.
5. Update bridge/INDEX.md by inserting the GO, NO-GO, or VERIFIED line at the top of that document's version list.

Important constraints:
- Use only the file bridge protocol and `bridge/INDEX.md` for coordination.
- Respect the project file-safety contract. Only create new bridge review files and make the required targeted bridge/INDEX.md coordination update for processed entries.
- If the bridge item targets groundtruth-kb, inspect E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb for evidence.
- Favor verification over assumption and cite concrete paths and command results.
"@

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = $CodexExe
    $psi.WorkingDirectory = $Workspace
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    # S292 foreground repair (2026-04-15): automated bridge scans do not need
    # Playwright MCP. Leaving it enabled can keep `codex exec` open after the
    # bridge response is written because the npx/node MCP child stays alive.
    $args = @(
        "exec",
        "-C",
        $Workspace,
        "-m",
        "gpt-5.4",
        "-c",
        "mcp_servers.playwright.enabled=false",
        "--dangerously-bypass-approvals-and-sandbox",
        "-o",
        $lastMessagePath,
        "-"
    )
    $psi.Arguments = ($args | ForEach-Object {
        $arg = [string]$_
        if ($arg -match '[\s"]') {
            '"' + ($arg -replace '"', '\"') + '"'
        } else {
            $arg
        }
    }) -join " "

    $proc = [System.Diagnostics.Process]::Start($psi)
    # Publish child pid immediately after Process.Start (before WaitForExit) so
    # the liveness watcher can verify the child is still alive via pid + start-time.
    # This is the real live signal: the status file now contains the child's pid
    # while it is actually running, not after it completes.
    Write-ScanStatus `
        -State "running" `
        -Message $runMessage `
        -AttentionNames $AttentionNames `
        -RunStamp $runStamp `
        -StdoutPath $stdoutPath `
        -StderrPath $stderrPath `
        -LastMessagePath $lastMessagePath `
        -ChildPid $proc.Id `
        -ChildStartUtc $proc.StartTime.ToUniversalTime().ToString("o") `
        -ChildExe $proc.StartInfo.FileName
    $proc.StandardInput.Write($prompt)
    $proc.StandardInput.Close()

    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()
    $codexTimeoutMs = 900000  # 15 minutes; long enough for normal reviews, short enough to avoid silent pileups.
    $completed = $proc.WaitForExit($codexTimeoutMs)
    if (-not $completed) {
        try { $proc.Kill($true) } catch { }
        throw "codex exec timed out after 15 minutes for $($SelectedEntries.Count) selected item(s) (full queue: $AttentionCount)"
    }

    $stdoutTask.Wait()
    $stderrTask.Wait()
    Set-Content -LiteralPath $stdoutPath -Value $stdoutTask.Result
    Set-Content -LiteralPath $stderrPath -Value $stderrTask.Result

    if ($proc.ExitCode -ne 0) {
        throw "codex exec exited with $($proc.ExitCode); stdout=$stdoutPath stderr=$stderrPath"
    }

    Write-ScanLog "codex exec completed for $($SelectedEntries.Count) selected item(s) (full queue: $AttentionCount); stdout=$stdoutPath last=$lastMessagePath"
    Write-ScanStatus -State "completed" -Message "codex exec completed for $($SelectedEntries.Count) selected item(s) (full queue: $AttentionCount)" -AttentionNames $SelectedNames -RunStamp $runStamp -StdoutPath $stdoutPath -StderrPath $stderrPath -LastMessagePath $lastMessagePath
}

$lockStream = $null
try {
    $lockStream = [System.IO.File]::Open($LockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
} catch {
    $priorNames = @()
    $priorRunStamp = ""
    $priorStdoutPath = ""
    $priorStderrPath = ""
    $priorLastMessagePath = ""
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
                $priorLastMessagePath = [string]$prior.lastMessagePath
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
        -LastMessagePath $priorLastMessagePath `
        -ChildPid $priorChildPid `
        -ChildStartUtc $priorChildStartUtc `
        -ChildExe $priorChildExe
    Show-PollerToast -Title "Codex bridge scan" -Message "skipped (prior scan still running)"
    exit 0
}

try {
    if (-not $NoExec -and -not (Test-InteractiveCodexDesktopRunning)) {
        $pausedMessage = "paused: interactive Codex desktop process is not running; scheduled scan will not spawn codex exec"
        Write-ScanLog $pausedMessage
        Write-ScanStatus -State "paused" -Message $pausedMessage
        exit 0
    }

    $attention = @(Get-AttentionEntries)
    if ($attention.Count -eq 0) {
        Write-ScanLog "Bridge scan: clear."
        Write-ScanStatus -State "clear" -Message "Bridge scan: clear."
        Show-PollerToast -Title "Codex bridge scan" -Message "clear (nothing to review)"
        exit 0
    }

    # Oldest-first: INDEX.md is newest-first; reverse a clone so $oldestFirst[0] = oldest entry.
    $oldestFirst = [object[]]$attention.Clone()
    [array]::Reverse($oldestFirst)

    $selectedCount = [Math]::Min($MAX_ITEMS_PER_SPAWN, $oldestFirst.Count)
    $selected = @($oldestFirst[0..($selectedCount - 1)])
    if ($selectedCount -lt $oldestFirst.Count) {
        $skipped = @($oldestFirst[$selectedCount..($oldestFirst.Count - 1)])
    } else {
        $skipped = @()
    }

    $allNames = ($attention | ForEach-Object { $_.Name }) -join ", "
    $selNames = ($selected | ForEach-Object { $_.Name }) -join ", "
    $skipNames = if ($skipped.Count -gt 0) { ($skipped | ForEach-Object { $_.Name }) -join ", " } else { "(none)" }
    $attentionNames = @($attention | ForEach-Object { $_.Name })
    $selectedNames = @($selected | ForEach-Object { $_.Name })

    Write-ScanLog "Bridge scan: $($attention.Count) entries need attention: $allNames"
    if ($skipped.Count -gt 0) {
        Write-ScanLog "Bridge scan cap=${MAX_ITEMS_PER_SPAWN}: selected=[$selNames] skipped=[$skipNames]"
        Write-ScanStatus -State "attention" -Message "Bridge scan: $($attention.Count) entries need attention; cap=${MAX_ITEMS_PER_SPAWN} selected=[$selNames]" -AttentionNames $attentionNames
        Show-PollerToast -Title "Codex bridge scan" -Message "$($selected.Count) of $($attention.Count) selected: $selNames"
    } else {
        Write-ScanStatus -State "attention" -Message "Bridge scan: $($attention.Count) entries need attention: $allNames" -AttentionNames $attentionNames
        Show-PollerToast -Title "Codex bridge scan" -Message "$($attention.Count) entry/entries need attention: $allNames"
    }

    if ($NoExec) {
        exit 2
    }

    # TOCTOU revalidation (bridge-spawn-revalidation-006 GO):
    # Between the INDEX read above ($attention / $selected) and the child-agent
    # spawn below, the other scanner or a manual edit could append a newer
    # verdict to the same entry. Capture the selected entry's top status+file
    # as a snapshot and let Invoke-GuardedLaunch re-read the INDEX immediately
    # before launch; launch only if the snapshot is still the top version.
    $firstSelected = $selected[0]
    $snapshot = [pscustomobject]@{
        DocumentName = $firstSelected.Name
        Status       = $firstSelected.Versions[0].Status
        File         = $firstSelected.Versions[0].Path
    }

    $launchAction = {
        Invoke-CodexBridgeScan -AttentionCount $attention.Count -SelectedEntries $selected -SelectedNames $selectedNames
    }

    $guardResult = Invoke-GuardedLaunch `
        -SelectedSnapshot $snapshot `
        -IndexPath        $IndexPath `
        -LaunchAction     $launchAction `
        -StaleLogPath     $StaleLogPath

    if (-not $guardResult.Launched) {
        $staleMsg = "SNAPSHOT-STALE: aborted launch (document=$($snapshot.DocumentName) expected=$($snapshot.Status):$($snapshot.File))"
        Write-ScanLog $staleMsg
        Write-ScanStatus -State "stale" -Message $staleMsg -AttentionNames $attentionNames
        Show-PollerToast -Title "Codex bridge scan" -Message "snapshot stale - aborted"
        exit 0
    }
} catch {
    Write-ScanLog "ERROR: $($_.Exception.Message)"
    Write-ScanStatus -State "error" -Message "ERROR: $($_.Exception.Message)"
    Show-PollerToast -Title "Codex bridge scan" -Message "error: $($_.Exception.Message)"
    exit 1
} finally {
    if ($null -ne $lockStream) {
        $lockStream.Dispose()
    }
}
