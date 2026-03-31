param(
  [int]$IntervalMinutes = 3,
  [int]$CadenceMinutes = 9,
  [int]$TimeoutSeconds = 900
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
$scriptPath = Join-Path $projectDir "scripts\codex_bridge_wake.py"
$taskName = "AgentRedCodexBridgeWake"
$userId = "$env:USERDOMAIN\$env:USERNAME"
$startBoundary = (Get-Date).AddMinutes(1).ToString("s")
$arguments = "scripts\codex_bridge_wake.py --cadence-minutes $CadenceMinutes --timeout-seconds $TimeoutSeconds"

$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>$((Get-Date).ToString("s"))</Date>
    <Author>Agent Red / Codex</Author>
    <Description>Wake Codex headless bridge worker when pending bridge work exists.</Description>
  </RegistrationInfo>
  <Triggers>
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
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
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

$xmlPath = Join-Path $projectDir "scripts\tmp-codex-bridge-wake-task.xml"
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

  Write-Output "REGISTERED:$taskName INTERVAL=$IntervalMinutes CADENCE=$CadenceMinutes RUNNER=$runner SCRIPT=$scriptPath"
} finally {
  Remove-Item -LiteralPath $xmlPath -Force -ErrorAction SilentlyContinue
}
