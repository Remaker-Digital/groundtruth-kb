param(
    [int]$IntervalSeconds = 120
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$EnsureScript = Join-Path $PSScriptRoot "ensure-bridge-scan-monitor.ps1"
$AlertScript = Join-Path $PSScriptRoot "show-bridge-liveness-alert.ps1"
$TokenRepairScript = Join-Path $PSScriptRoot "repair-claude-token-handoff.ps1"
$LogDir = Join-Path $PSScriptRoot "logs"
$LogPath = Join-Path $LogDir "bridge-monitor-watchdog.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Write-WatchdogLog {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-Content -LiteralPath $LogPath -Value "$stamp $Message"
}

function Quote-ProcessArgument {
    param([string]$Value)
    if ($null -eq $Value) {
        return '""'
    }

    return '"' + ($Value -replace '\\', '\\' -replace '"', '\"') + '"'
}

function Invoke-HiddenPowerShellScript {
    param([string]$ScriptPath)

    $arguments = @(
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $ScriptPath
    )

    $psi = [System.Diagnostics.ProcessStartInfo]::new()
    $psi.FileName = "powershell.exe"
    $psi.WorkingDirectory = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..\..")).Path
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.Arguments = (($arguments | ForEach-Object { Quote-ProcessArgument $_ }) -join " ")

    $proc = [System.Diagnostics.Process]::Start($psi)
    $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
    $stderrTask = $proc.StandardError.ReadToEndAsync()
    $proc.WaitForExit()
    $stdoutTask.Wait()
    $stderrTask.Wait()

    if ($proc.ExitCode -ne 0) {
        throw "hidden PowerShell script failed with exit $($proc.ExitCode): $ScriptPath; stdout=$($stdoutTask.Result); stderr=$($stderrTask.Result)"
    }
}

if (-not (Test-Path -LiteralPath $EnsureScript)) {
    throw "Monitor ensure script not found: $EnsureScript"
}
if (-not (Test-Path -LiteralPath $AlertScript)) {
    throw "Liveness alert script not found: $AlertScript"
}
if (-not (Test-Path -LiteralPath $TokenRepairScript)) {
    throw "Claude token repair script not found: $TokenRepairScript"
}

$mutex = [System.Threading.Mutex]::new($false, "AgentRedBridgeMonitorWatchdog")
$hasMutex = $false

try {
    $hasMutex = $mutex.WaitOne(0)
    if (-not $hasMutex) {
        Write-WatchdogLog "another watchdog instance is already running; exiting"
        exit 0
    }

    Write-WatchdogLog "watchdog started; interval=${IntervalSeconds}s"
    while ($true) {
        try {
            Invoke-HiddenPowerShellScript -ScriptPath $EnsureScript
            Write-WatchdogLog "ensure completed"
        } catch {
            Write-WatchdogLog "ensure failed: $($_.Exception.Message)"
        }

        try {
            Invoke-HiddenPowerShellScript -ScriptPath $TokenRepairScript
            Write-WatchdogLog "token handoff repair completed"
        } catch {
            Write-WatchdogLog "token handoff repair failed: $($_.Exception.Message)"
        }

        try {
            Invoke-HiddenPowerShellScript -ScriptPath $AlertScript
            Write-WatchdogLog "alert check completed"
        } catch {
            Write-WatchdogLog "alert check failed: $($_.Exception.Message)"
        }

        Start-Sleep -Seconds $IntervalSeconds
    }
} finally {
    if ($hasMutex) {
        try {
            $mutex.ReleaseMutex() | Out-Null
        } catch {
            # Process shutdown may already have released it.
        }
    }
    $mutex.Dispose()
}
