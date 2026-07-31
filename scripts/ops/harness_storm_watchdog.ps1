# Liveness-aware watchdog for the cross-harness dispatch process-storm.
#
# Authority: owner AUQ 2026-06-12 ("Both: kill-switch + watchdog") after a
# ~300-process Codex dispatch cascade exhausted the workstation. Narrowed by
# DELIB-20265877 (kill-switch is emergency-only; congestion is not failure),
# DELIB-20260612 (watchdog OFF after the concurrency cap was VERIFIED), and
# SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001 / WI-4780 (no kill-switch
# auto-assert). WI-4828 (slice 1 of WI-4670, DELIB-20266104) replaces the
# raw-count family KILL with LIVENESS-AWARE reaping.
#
# Why the change (WI-4670 root cause): the old behavior killed the whole matched
# harness family when the raw OS-process count exceeded a threshold. But the
# concurrency cap (WI-4472) bounds LOGICAL workers (~3/role) while one codex
# worker spawns ~4 OS processes, so a within-cap number of HEALTHY workers blew
# the threshold and the watchdog reaped healthy, in-flight, lease-holding workers
# mid-task (exit 4294967295). A reaped worker writes no verdict -> its item stays
# actionable -> re-dispatch -> storm.
#
# What changed: the threshold is now a DETECTION/observability signal only (it is
# logged, never used to kill). The actual reap is delegated to the pure,
# unit-tested decider scripts/ops/storm_watchdog_reap.py, which protects
# cold-start (grace) processes and fresh lease-holders within max-lifetime (+
# their process families) and reaps only orphans/corpses and over-lifetime
# stragglers. Throttling spawns is the concurrency cap's job (WI-4472); this
# watchdog only reaps corpses/hangs.
#
# Safety scoping: only DISPATCHED-worker process families are eligible for
# reaping. A dispatched root is a `codex exec` process or a non-codex harness
# python; INTERACTIVE codex (`codex` TUI, no `exec`) and ambiguous orphan
# families whose dispatched root already died are left entirely untouched. This
# is what keeps the watchdog from reaping the owner's interactive Codex session.
# Trade-off: orphaned leaf helpers of a dead dispatched root are left for the OS
# to clean rather than risk an interactive session (a follow-on slice can add a
# dispatch-run pid-provenance source for precise orphan attribution).
#
# Fail-safe: if the decider cannot be run or returns nothing parseable, reap
# NOTHING and log the error. It NEVER falls back to a raw-count kill. It does NOT
# assert the global kill-switch (emergency-only, manual). It NEVER kills claude
# and only considers node_repl whose image path is under the Codex runtime.

$ErrorActionPreference = 'SilentlyContinue'

$root   = 'E:\GT-KB'
$opsDir = Join-Path $root '.gtkb-state\ops'
if (-not (Test-Path $opsDir)) { New-Item -ItemType Directory -Force $opsDir | Out-Null }
$log  = Join-Path $opsDir 'storm-watchdog.log'
$beat = Join-Path $opsDir 'storm-watchdog-heartbeat.txt'
$now  = (Get-Date).ToString('o')

$reapScript = Join-Path $root 'scripts\ops\storm_watchdog_reap.py'
# pythonw.exe: GUI-subsystem interpreter; no console window when Task Scheduler
# invokes this script every minute while Codex/harness processes are present.
$pythonExe  = Join-Path $root 'groundtruth-kb\.venv\Scripts\pythonw.exe'

$CODEX_THRESHOLD = 15
$NONCODEX_THRESHOLD = 15

$NONCODEX_HARNESS_SCRIPTS = @('ollama_harness.py', 'openrouter_harness.py', 'cursor_harness.py')
$NONCODEX_HARNESS_SCRIPT_PATTERN =
    'scripts\\(' + (($NONCODEX_HARNESS_SCRIPTS | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')'
$RUN_WITH_STATUS_SCRIPT_PATTERN = 'scripts\\run_with_status\.py'
$GTKB_VENV_PYTHON_PATTERN = 'groundtruth-kb\\\.venv\\Scripts\\python(?:w)?\.exe'
$PYTHON_PROCESS_NAMES = @('python.exe', 'pythonw.exe', 'python', 'py.exe', 'pyw.exe')
$CURSOR_AGENT_PROCESS_NAMES = @('agent.exe', 'agent', 'cursor-agent.exe', 'cursor-agent')
$RUN_WITH_STATUS_DEFAULT_LIFETIME_SECONDS = 600
$CODEX_EXEC_PATTERN = '\bcodex(?:\.exe)?\b.*\bexec\b'

function Get-CreateEpoch($cimProc) {
    try { return [int][double]::Parse(([DateTimeOffset]$cimProc.CreationDate).ToUnixTimeSeconds()) }
    catch { return 0 }
}

function Get-NormalizedCommand($cimProc) {
    if (-not $cimProc.CommandLine) { return '' }
    return ($cimProc.CommandLine -replace '/', '\')
}

function Get-RunWithStatusLifetimeSeconds($commandLine) {
    $match = [regex]::Match($commandLine, '--lifetime\s+([0-9]+(?:\.[0-9]+)?)')
    if ($match.Success) {
        try { return [double]::Parse($match.Groups[1].Value, [Globalization.CultureInfo]::InvariantCulture) }
        catch { return $RUN_WITH_STATUS_DEFAULT_LIFETIME_SECONDS }
    }
    return $RUN_WITH_STATUS_DEFAULT_LIFETIME_SECONDS
}

$allCim = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)

# --- Population detection (observability only; never kills) ----------------- #
$codex = @($allCim | Where-Object { $_.Name -eq 'codex.exe' })
$baseFamily = @($allCim | Where-Object {
        $_.Name -eq 'codex.exe' -or $_.Name -like 'codex-command-runner*' -or
        $_.Name -like 'codex-windows-sandbox*' -or
        (($_.Name -eq 'node_repl.exe' -or $_.Name -eq 'node_repl') -and $_.ExecutablePath -and ($_.ExecutablePath -match 'OpenAI\\Codex'))
    })
$wrappedCodex = @($allCim | Where-Object {
        $normalizedCmd = Get-NormalizedCommand $_
        if (-not $normalizedCmd) { return $false }
        $name = $_.Name
        $isPython = $PYTHON_PROCESS_NAMES -contains $name
        $isRunWithStatus = $normalizedCmd -match $RUN_WITH_STATUS_SCRIPT_PATTERN
        $isProjectHarness =
            ($normalizedCmd -match [regex]::Escape($root)) -or
            ($normalizedCmd -match $GTKB_VENV_PYTHON_PATTERN)
        $isPython -and $isRunWithStatus -and $isProjectHarness -and ($normalizedCmd -match $CODEX_EXEC_PATTERN)
    })
$family = @($baseFamily + $wrappedCodex)
$noncodex = @($allCim | Where-Object {
        $normalizedCmd = Get-NormalizedCommand $_
        if (-not $normalizedCmd) { return $false }
        $name = $_.Name
        $isPython = $PYTHON_PROCESS_NAMES -contains $name
        $invokesWatchedHarness = $normalizedCmd -match $NONCODEX_HARNESS_SCRIPT_PATTERN
        $isProjectHarness =
            ($normalizedCmd -match [regex]::Escape($root)) -or
            ($normalizedCmd -match $GTKB_VENV_PYTHON_PATTERN)
        $isPython -and $invokesWatchedHarness -and $isProjectHarness
    })
$cursorAgents = @($allCim | Where-Object {
        $normalizedCmd = Get-NormalizedCommand $_
        if (-not $normalizedCmd) { return $false }
        $name = $_.Name
        $isCursorAgent = $CURSOR_AGENT_PROCESS_NAMES -contains $name
        $isProjectWorkspace = $normalizedCmd -match [regex]::Escape($root)
        $isCursorAgent -and $isProjectWorkspace
    })

$codexCount    = $codex.Count
$familyCount   = $family.Count
$noncodexCount = $noncodex.Count
$cursorAgentCount = $cursorAgents.Count
$dispatchWrapperCount = @(($family + $noncodex) | Where-Object { (Get-NormalizedCommand $_) -match $RUN_WITH_STATUS_SCRIPT_PATTERN }).Count

Set-Content $beat "$now codex=$codexCount family=$familyCount noncodex=$noncodexCount cursorAgents=$cursorAgentCount wrapped=$dispatchWrapperCount threshold=$CODEX_THRESHOLD noncodexThreshold=$NONCODEX_THRESHOLD mode=liveness-aware(WI-4828)"

if (($codexCount -gt $CODEX_THRESHOLD) -or ($noncodexCount -gt $NONCODEX_THRESHOLD) -or ($cursorAgentCount -gt $NONCODEX_THRESHOLD) -or ($dispatchWrapperCount -gt $NONCODEX_THRESHOLD)) {
    # WI-4828: the threshold is now a DETECTION signal only. Reaping is decided
    # by liveness (below), not by this count. Logged for observability.
    Add-Content $log "$now POPULATION codex=$codexCount family=$familyCount noncodex=$noncodexCount cursorAgents=$cursorAgentCount wrapped=$dispatchWrapperCount over-threshold (reap is liveness-based, not count-based)"
}

# --- Candidate set for the liveness decider (with dispatched flag) ---------- #
$candidates = @()
$seenCandidatePids = @{}
foreach ($p in ($family + $noncodex + $cursorAgents)) {
    $pid = [int]$p.ProcessId
    if ($seenCandidatePids.ContainsKey($pid)) { continue }
    $seenCandidatePids[$pid] = $true
    $name = $p.Name
    $normalizedCmd = Get-NormalizedCommand $p
    $isPython = $PYTHON_PROCESS_NAMES -contains $name
    $isRunWithStatus = $isPython -and ($normalizedCmd -match $RUN_WITH_STATUS_SCRIPT_PATTERN)
    $dispatched = $false
    if ($name -eq 'codex.exe') {
        # Dispatched workers run `codex exec ...`; interactive `codex` TUI does not.
        if ($p.CommandLine -and ($p.CommandLine -match '\bexec\b')) { $dispatched = $true }
    }
    elseif ($isPython) {
        $invokesWatchedHarness = $normalizedCmd -match $NONCODEX_HARNESS_SCRIPT_PATTERN
        if ($invokesWatchedHarness -or $isRunWithStatus) { $dispatched = $true }
    }
    $candidates += [pscustomobject]@{
        pid               = $pid
        ppid              = [int]$p.ParentProcessId
        name              = [string]$name
        create_time_epoch = (Get-CreateEpoch $p)
        dispatched        = $dispatched
        max_lifetime_seconds = $(if ($isRunWithStatus) { Get-RunWithStatusLifetimeSeconds $normalizedCmd } else { $null })
    }
}

$killed = 0
$reapPids = @()
$decision = $null
$failSafe = $false
$failReason = ''

if ($candidates.Count -gt 0) {
    if (-not (Test-Path $pythonExe)) {
        $failSafe = $true; $failReason = "venv python missing: $pythonExe"
    }
    elseif (-not (Test-Path $reapScript)) {
        $failSafe = $true; $failReason = "reap script missing: $reapScript"
    }
    else {
        try {
            $nowEpoch = [int][double]::Parse(([DateTimeOffset]::UtcNow).ToUnixTimeSeconds())
            $procJson = ($candidates | ConvertTo-Json -Compress -Depth 4)
            # Pass processes via a file, NOT a piped stdin: Windows PowerShell can
            # raise an OSError flushing a piped stdin into python. A single object
            # (not array) is emitted unwrapped by ConvertTo-Json; the decider
            # normalizes a dict to a one-element list, so this is safe.
            $procFile = Join-Path $opsDir 'storm-watchdog-candidates.json'
            # BOM-less UTF-8 write (WI-4882 Slice 2): Windows PowerShell 5.1
            # `Set-Content -Encoding utf8` prepends a BOM that the decider's
            # json.loads cannot parse (FAILSAFE). WriteAllText emits no BOM on
            # all PowerShell versions; the decider also reads utf-8-sig as a
            # belt-and-suspenders.
            [System.IO.File]::WriteAllText($procFile, $procJson)
            $decisionFile = Join-Path $opsDir ('storm-watchdog-decision-' + [guid]::NewGuid().ToString('N') + '.json')
            if (Test-Path $decisionFile) { Remove-Item $decisionFile -Force -ErrorAction SilentlyContinue }
            $decider = Start-Process -FilePath $pythonExe -ArgumentList @(
                $reapScript,
                '--now',
                $nowEpoch,
                '--project-root',
                $root,
                '--provenance-dir',
                '.gtkb-state/ops/dispatch-provenance',
                '--processes-file',
                $procFile,
                '--output-file',
                $decisionFile
            ) -Wait -PassThru -WindowStyle Hidden
            $deciderExitCode = $decider.ExitCode
            $decisionRaw = ''
            if (Test-Path $decisionFile) {
                $decisionRaw = [System.IO.File]::ReadAllText($decisionFile)
                Remove-Item $decisionFile -Force -ErrorAction SilentlyContinue
            }
            if ($deciderExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($decisionRaw)) {
                $failSafe = $true; $failReason = "decider exit=$deciderExitCode output-file-empty=$([string]::IsNullOrWhiteSpace($decisionRaw))"
            }
            else {
                $decision = $decisionRaw | ConvertFrom-Json
                $reapPids = @($decision.reap)
            }
        }
        catch {
            $failSafe = $true; $failReason = "decider invocation threw: $($_.Exception.Message)"
        }
    }
}

if ($failSafe) {
    # NEVER fall back to a raw-count kill. Reap nothing; log loudly.
    Add-Content $log "$now FAILSAFE candidates=$($candidates.Count) reaped=0 reason=$failReason (no raw-count fallback)"
}
elseif ($reapPids.Count -gt 0) {
    foreach ($p in $allCim) {
        if ($reapPids -contains [int]$p.ProcessId) {
            $reason = $decision.reasons."$([int]$p.ProcessId)"
            try { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop; $killed++ } catch {}
            Add-Content $log "$now REAP pid=$($p.ProcessId) name=$($p.Name) reason=$reason"
        }
    }
    Add-Content $log "$now SUMMARY candidates=$($candidates.Count) reaped=$killed kill-switch=not-asserted(emergency-only)"
}

# Log-rotate guard so the audit log cannot grow unbounded.
try {
    if ((Test-Path $log) -and ((Get-Item $log).Length -gt 1MB)) {
        Move-Item $log (Join-Path $opsDir ('storm-watchdog.' + (Get-Date).ToString('yyyyMMddHHmmss') + '.log')) -Force
    }
} catch {}
