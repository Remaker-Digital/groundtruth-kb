param(
  [ValidateSet("codex", "prime")]
  [string]$Agent = "codex",

  [ValidateSet("daemon", "once")]
  [string]$Mode = "daemon",

  [int]$IntervalMinutes = 1,
  [int]$PollTimeoutSeconds = 20,
  [int]$PollIntervalMs = 100,
  [bool]$AutoActions = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Escape-Xml([string]$Value) {
  return [System.Security.SecurityElement]::Escape($Value)
}

$projectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonExe = (python -c "import sys; print(sys.executable)").Trim()
if (-not $pythonExe) {
  throw "Could not resolve python executable."
}

$pythonw = Join-Path (Split-Path $pythonExe -Parent) "pythonw.exe"
$runner = if (Test-Path $pythonw) { $pythonw } else { $pythonExe }

$taskName = "AgentRedBridgePoller-$Agent"
$userId = "$env:USERDOMAIN\$env:USERNAME"

$arguments = "bridge_poller.py --agent $Agent"
if ($Mode -eq "once") {
  $arguments += " --once"
} else {
  $arguments += " --timeout-seconds $PollTimeoutSeconds --poll-interval-ms $PollIntervalMs --limit 50"
}
if ($AutoActions) {
  $arguments += " --auto-actions"
}

if ($Mode -eq "once") {
  $startBoundary = (Get-Date).AddMinutes(1).ToString("s")
  $triggerXml = @"
    <CalendarTrigger>
      <StartBoundary>$startBoundary</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
      <Repetition>
        <Interval>PT${IntervalMinutes}M</Interval>
        <Duration>P3650D</Duration>
        <StopAtDurationEnd>false</StopAtDurationEnd>
      </Repetition>
    </CalendarTrigger>
"@
  $executionLimit = "PT4M"
  $description = "Silent bridge poller (one-shot) for $Agent, every $IntervalMinutes minute(s)."
} else {
  $triggerXml = @"
    <LogonTrigger>
      <Enabled>true</Enabled>
      <UserId>$userId</UserId>
      <Delay>PT15S</Delay>
    </LogonTrigger>
"@
  $executionLimit = "PT0S"
  $description = "Silent bridge poller daemon for $Agent (starts at logon)."
}

$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>$((Get-Date).ToString("s"))</Date>
    <Author>Agent Red / Codex</Author>
    <Description>$(Escape-Xml $description)</Description>
  </RegistrationInfo>
  <Triggers>
$triggerXml
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$userId</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>$executionLimit</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>$(Escape-Xml $runner)</Command>
      <Arguments>$(Escape-Xml $arguments)</Arguments>
      <WorkingDirectory>$(Escape-Xml $projectDir)</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

$xmlPath = Join-Path $projectDir "scripts\tmp-bridge-poller-$Agent-task.xml"
$xml | Out-File -FilePath $xmlPath -Encoding Unicode -Force

try {
  & schtasks.exe /Create /TN $taskName /XML $xmlPath /F | Out-Host
  if ($LASTEXITCODE -ne 0) {
    throw "schtasks /Create failed for $taskName (exit $LASTEXITCODE)"
  }

  & schtasks.exe /Run /TN $taskName | Out-Host
  if ($LASTEXITCODE -ne 0) {
    throw "schtasks /Run failed for $taskName (exit $LASTEXITCODE)"
  }

  Write-Output "REGISTERED:$taskName MODE=$Mode RUNNER=$runner ARGS=$arguments"
} finally {
  Remove-Item -LiteralPath $xmlPath -Force -ErrorAction SilentlyContinue
}
