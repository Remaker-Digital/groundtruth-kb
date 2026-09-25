[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Root,
    [int]$ReadinessSeconds = 120,
    [switch]$NoOpen
)

# Registers the scheduled task GTKB-Home under the current (owner) account, so that GT-KB Home (the DeepSeek Harness
# Web UI as GT-KB's primary interface, owner ruling D58) starts at every logon of this account (the same trigger as
# GTKB-DomainService), on demand, and again within five minutes if it stops without a requested stop. The action runs infrastructure/deepseek-web/home.py start with the
# installation's pythonw.exe; start is idempotent (a running Home is left alone) and returns once the Home has proven
# its guard, its plugin and its ready line. No credential is stored in the task definition: home.py loads the model
# credential by name when it starts. `gt services stop home` pauses this task so that a stop holds; `gt services start
# home` resumes it. Re-running the script with the same root updates the task in place; a task that points at another
# installation is refused. After starting the task the script waits until home.py status reports a live Home, then opens
# it in the default browser (the first start after installation opens the Home; -NoOpen skips that). The sign-in URL
# goes only to the browser, never to this script's output.

$ErrorActionPreference = 'Stop'
$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
$installation = Join-Path $resolvedRoot 'infrastructure\deepseek-web'
$launcher = Join-Path $installation 'home.py'
$installed = Join-Path $installation 'installed.json'
$interpreter = Join-Path $resolvedRoot 'groundtruth-kb\.venv\Scripts\pythonw.exe'
$probeInterpreter = Join-Path $resolvedRoot 'groundtruth-kb\.venv\Scripts\python.exe'
$taskName = 'GTKB-Home'

foreach ($required in @($launcher, $interpreter, $probeInterpreter)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required file is missing: $required" }
}
if (-not (Test-Path -LiteralPath $installed -PathType Leaf)) {
    throw "GT-KB Home is not installed; run: python infrastructure\deepseek-web\install.py --root $resolvedRoot"
}

$arguments = ('-B "{0}" start' -f $launcher)
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    $current = ($existing.Actions | ForEach-Object { $_.Execute + ' ' + $_.Arguments }) -join ' '
    if (-not $current.Contains($launcher)) { throw 'The existing task belongs to a different installation; refusing to change it.' }
}

$action = New-ScheduledTaskAction -Execute $interpreter -Argument $arguments -WorkingDirectory $resolvedRoot
$logon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
# home.py start exits once the Home is ready or found running; the repetition restarts a Home that has stopped.
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($logon, $repeat) -Settings $settings -Principal $principal -Force | Out-Null
Start-ScheduledTask -TaskName $taskName

$deadline = (Get-Date).AddSeconds($ReadinessSeconds)
$report = $null
do {
    Start-Sleep -Seconds 3
    $output = & $probeInterpreter -B $launcher status
    try { $report = $output | Out-String | ConvertFrom-Json } catch { $report = $null }
} while ((Get-Date) -lt $deadline -and -not ($report -and $report.running -and $report.live))
$task = Get-ScheduledTask -TaskName $taskName
if (-not ($report -and $report.running -and $report.live)) {
    throw ('GT-KB Home did not become live within {0} s (task state {1}); see the newest log under the Home state folder.' -f $ReadinessSeconds, $task.State)
}
$task | Select-Object TaskName, State
('GT-KB Home is live on 127.0.0.1:{0} (credential supplied: {1}); open it any time with: gt home open' -f $report.port, $report.credential_supplied)
if (-not $NoOpen) {
    $signIn = (& $probeInterpreter -B $launcher url | Out-String).Trim()
    if ($signIn -match '^http://127\.0\.0\.1:\d+/\?token=[A-Za-z0-9_-]+$') { Start-Process $signIn; 'Opened GT-KB Home in the default browser.' }
    else { 'GT-KB Home is live but no sign-in URL was available; use: gt home open' }
}
