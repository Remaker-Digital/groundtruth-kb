# Emergency watchdog for the cross-harness dispatch process-storm.
#
# Authority: owner AUQ 2026-06-12 ("Both: kill-switch + watchdog") after a
# ~300-process Codex dispatch cascade exhausted the workstation.
#
# Behavior (runs every ~1 min via the GTKB-HarnessStormWatchdog task):
#   - Counts codex-family headless processes.
#   - Counts non-Codex Python harness processes declared by the harness
#     registry for low-cost Loyal Opposition dispatch.
#   - If either population exceeds its threshold, assert the
#     GTKB_NO_CROSS_HARNESS_TRIGGER kill-switch, kill the matched harness
#     process family, and log the intervention.
#   - Otherwise: write a heartbeat (overwrite, no log growth).
#
# Conservative by design: it NEVER kills claude and only kills node_repl whose
# image path is under the Codex runtime. The Python kill path is guarded by the
# GT-KB project root / project venv plus explicit harness script names.

$ErrorActionPreference = 'SilentlyContinue'

$root   = 'E:\GT-KB'
$opsDir = Join-Path $root '.gtkb-state\ops'
if (-not (Test-Path $opsDir)) { New-Item -ItemType Directory -Force $opsDir | Out-Null }
$log  = Join-Path $opsDir 'storm-watchdog.log'
$beat = Join-Path $opsDir 'storm-watchdog-heartbeat.txt'
$now  = (Get-Date).ToString('o')

$CODEX_THRESHOLD = 15
$NONCODEX_THRESHOLD = 15

$NONCODEX_HARNESS_SCRIPTS = @('ollama_harness.py', 'openrouter_harness.py')
$NONCODEX_HARNESS_SCRIPT_PATTERN =
    'scripts\\(' + (($NONCODEX_HARNESS_SCRIPTS | ForEach-Object { [regex]::Escape($_) }) -join '|') + ')'
$GTKB_VENV_PYTHON_PATTERN = 'groundtruth-kb\\\.venv\\Scripts\\python\.exe'

$codex  = @(Get-Process -Name codex -ErrorAction SilentlyContinue)
$family = @(Get-Process -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -eq 'codex' -or $_.Name -eq 'node_repl' -or
        $_.Name -like 'codex-command-runner*' -or $_.Name -like 'codex-windows-sandbox*'
    })

$noncodex = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {
        $cmd = $_.CommandLine
        if (-not $cmd) { return $false }

        $name = $_.Name
        $normalizedCmd = $cmd -replace '/', '\'
        $isPython = $name -in @('python.exe', 'python', 'py.exe')
        $invokesWatchedHarness = $normalizedCmd -match $NONCODEX_HARNESS_SCRIPT_PATTERN
        $isProjectHarness =
            ($normalizedCmd -match [regex]::Escape($root)) -or
            ($normalizedCmd -match $GTKB_VENV_PYTHON_PATTERN)

        $isPython -and $invokesWatchedHarness -and $isProjectHarness
    })

$codexCount    = $codex.Count
$familyCount   = $family.Count
$noncodexCount = $noncodex.Count

Set-Content $beat "$now codex=$codexCount family=$familyCount noncodex=$noncodexCount threshold=$CODEX_THRESHOLD noncodexThreshold=$NONCODEX_THRESHOLD"

if (($codexCount -gt $CODEX_THRESHOLD) -or ($noncodexCount -gt $NONCODEX_THRESHOLD)) {
    [Environment]::SetEnvironmentVariable('GTKB_NO_CROSS_HARNESS_TRIGGER', '1', 'User')
    $killed = 0

    foreach ($p in $family) {
        if ($p.Name -eq 'node_repl' -and $p.Path -and ($p.Path -notmatch 'OpenAI\\Codex')) { continue }
        try { Stop-Process -Id $p.Id -Force -ErrorAction Stop; $killed++ } catch {}
    }

    foreach ($p in $noncodex) {
        $cmd = $p.CommandLine
        if (-not $cmd) { continue }

        $normalizedCmd = $cmd -replace '/', '\'
        $isWatchedHarness = $normalizedCmd -match $NONCODEX_HARNESS_SCRIPT_PATTERN
        $isProjectHarness =
            ($normalizedCmd -match [regex]::Escape($root)) -or
            ($normalizedCmd -match $GTKB_VENV_PYTHON_PATTERN)
        if ((-not $isWatchedHarness) -or (-not $isProjectHarness)) { continue }

        try { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop; $killed++ } catch {}
    }

    Add-Content $log "$now STORM codex=$codexCount family=$familyCount noncodex=$noncodexCount killed=$killed kill-switch=asserted(User)"
}

# Log-rotate guard so the audit log cannot grow unbounded.
try {
    if ((Test-Path $log) -and ((Get-Item $log).Length -gt 1MB)) {
        Move-Item $log (Join-Path $opsDir ('storm-watchdog.' + (Get-Date).ToString('yyyyMMddHHmmss') + '.log')) -Force
    }
} catch {}
