[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Root,
    [int]$Port = 8765,
    [int]$ReadinessSeconds = 60
)

# Registers the scheduled task GTKB-DomainService under the current (owner) account: it runs
# infrastructure/postgresql/domain_service_launcher.py at every logon of this account and on demand,
# restarts it up to three times a minute apart if a trigger-started instance exits, relaunches it by a repetition
# trigger every five minutes when no instance is running, never stops it on a time limit, and ignores battery state. The
# launcher alone carries PGSERVICEFILE; no credential value is stored in the task definition.
# Re-running the script with the same root updates the task in place; a task that points at another
# installation is refused. After starting the task the script probes the service on 127.0.0.1:$Port
# with bounded retries (Wait-GtkbDomainServiceReady in domain-service-readiness.ps1) and fails when the
# service does not answer.

$ErrorActionPreference = 'Stop'
$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path.TrimEnd('\')
$installation = Join-Path $resolvedRoot 'infrastructure\postgresql'
$launcher = Join-Path $installation 'domain_service_launcher.py'
$readiness = Join-Path $installation 'domain-service-readiness.ps1'
$interpreter = Join-Path $resolvedRoot 'groundtruth-kb\.venv\Scripts\pythonw.exe'
$probeInterpreter = Join-Path $resolvedRoot 'groundtruth-kb\.venv\Scripts\python.exe'
$credentials = Join-Path $installation 'credentials\pg_service.conf'
$operatorConfig = Join-Path $installation 'operator-config.toml'
$taskName = 'GTKB-DomainService'

foreach ($required in @($launcher, $readiness, $interpreter, $probeInterpreter, $credentials, $operatorConfig)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Required file is missing: $required" }
}
. $readiness

$arguments = ('"{0}" --root "{1}" --port {2}' -f $launcher, $resolvedRoot, $Port)
$existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existing) {
    $current = ($existing.Actions | ForEach-Object { $_.Execute + ' ' + $_.Arguments }) -join ' '
    if (-not $current.Contains($launcher)) { throw 'The existing task belongs to a different installation; refusing to change it.' }
}

$action = New-ScheduledTaskAction -Execute $interpreter -Argument $arguments -WorkingDirectory $resolvedRoot
$logon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
# A repetition trigger relaunches a dead service within five minutes regardless of how the previous instance ended
# (the restart-on-failure policy below applies only to trigger-started instances); IgnoreNew leaves a running instance alone.
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -MultipleInstances IgnoreNew -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger @($logon, $repeat) -Settings $settings -Principal $principal -Force | Out-Null
Start-ScheduledTask -TaskName $taskName

$probe = Wait-GtkbDomainServiceReady -ProbeInterpreter $probeInterpreter -OperatorConfig $operatorConfig -Port $Port -Seconds $ReadinessSeconds
$task = Get-ScheduledTask -TaskName $taskName
if (-not $probe.Ready) {
    throw ('The domain service did not answer on 127.0.0.1:{0} within {1} s after {2} probe(s) (task state {3}). Last probe output: {4}' -f $Port, $ReadinessSeconds, $probe.Attempts, $task.State, $probe.LastOutput)
}
$task | Select-Object TaskName, State
('ready after {0} probe(s) on 127.0.0.1:{1}' -f $probe.Attempts, $Port)
$probe.LastOutput
