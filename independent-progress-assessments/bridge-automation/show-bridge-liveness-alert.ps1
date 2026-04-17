param(
    [int]$RepeatAlertMinutes = 15,
    [switch]$NoToast
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$LogDir = Join-Path $PSScriptRoot "logs"
$WatcherPath = Join-Path $PSScriptRoot "poller-liveness-watcher.ps1"
$LivenessPath = Join-Path $LogDir "poller-liveness-external.json"
$StatePath = Join-Path $LogDir "bridge-liveness-alert-state.json"
$AlertLogPath = Join-Path $LogDir "bridge-liveness-alert.log"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

function Add-LogLine {
    param(
        [string]$Path,
        [string]$Value
    )

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            [System.IO.File]::AppendAllText($Path, $Value + [Environment]::NewLine, [System.Text.Encoding]::UTF8)
            return
        } catch {
            if ($attempt -eq 5) {
                throw
            }
            Start-Sleep -Milliseconds (100 * $attempt)
        }
    }
}

function Publish-JsonFile {
    param(
        [string]$TempPath,
        [string]$DestinationPath
    )

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            if (Test-Path -LiteralPath $DestinationPath) {
                $destinationDir = Split-Path -Parent $DestinationPath
                $destinationLeaf = Split-Path -Leaf $DestinationPath
                $backupPath = Join-Path $destinationDir ("{0}.{1}.bak" -f $destinationLeaf, ([guid]::NewGuid().ToString("N")))
                [System.IO.File]::Replace($TempPath, $DestinationPath, $backupPath, $true)
                Remove-Item -LiteralPath $backupPath -Force -ErrorAction SilentlyContinue
            } else {
                Move-Item -LiteralPath $TempPath -Destination $DestinationPath -Force
            }
            return
        } catch {
            if ($attempt -eq 5) {
                throw
            }
            Start-Sleep -Milliseconds (100 * $attempt)
        }
    }
}

function Write-AlertLog {
    param([string]$Message)
    $stamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    Add-LogLine -Path $AlertLogPath -Value "$stamp $Message"
}

function Show-BridgeToast {
    param(
        [string]$Title,
        [string]$Message
    )

    if ($NoToast) {
        return
    }

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
        Write-AlertLog "toast failed: $($_.Exception.Message)"
    }
}

function Read-AlertState {
    if (-not (Test-Path -LiteralPath $StatePath)) {
        return [pscustomobject]@{
            lastKey = ""
            lastOverallState = ""
            lastToastUtc = ""
        }
    }

    try {
        return Get-Content -Raw -LiteralPath $StatePath | ConvertFrom-Json -ErrorAction Stop
    } catch {
        Write-AlertLog "state read failed: $($_.Exception.Message)"
        return [pscustomobject]@{
            lastKey = ""
            lastOverallState = ""
            lastToastUtc = ""
        }
    }
}

function Write-AlertState {
    param(
        [string]$Key,
        [string]$OverallState,
        [string]$LastToastUtc
    )

    $payload = [ordered]@{
        updatedAtUtc = (Get-Date).ToUniversalTime().ToString("o")
        lastKey = $Key
        lastOverallState = $OverallState
        lastToastUtc = $LastToastUtc
    }

    $tmpPath = Join-Path $LogDir ("bridge-liveness-alert-state.{0}.tmp" -f ([guid]::NewGuid().ToString("N")))
    $payload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $tmpPath -Encoding UTF8
    Publish-JsonFile -TempPath $tmpPath -DestinationPath $StatePath
}

function Read-LivenessSnapshot {
    for ($attempt = 1; $attempt -le 3; $attempt++) {
        if (Test-Path -LiteralPath $LivenessPath) {
            try {
                return Get-Content -Raw -LiteralPath $LivenessPath | ConvertFrom-Json -ErrorAction Stop
            } catch {
                Write-AlertLog "liveness read attempt $attempt failed: $($_.Exception.Message)"
            }
        } else {
            Write-AlertLog "liveness read attempt $attempt missing: $LivenessPath"
        }
        Start-Sleep -Milliseconds 250
    }

    return $null
}

if (-not (Test-Path -LiteralPath $WatcherPath)) {
    $message = "poller liveness watcher script not found: $WatcherPath"
    Write-AlertLog "ERROR: $message"
    Show-BridgeToast -Title "Agent Red bridge liveness" -Message $message
    exit 1
}

# Self-refresh: invoke the watcher to produce/update the liveness JSON,
# then read it. Prevents stale-JSON false-OK if the scheduled watcher task
# is stopped or broken.
& powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "`"$WatcherPath`""
if ($LASTEXITCODE -ne 0) {
    $message = "liveness watcher exited with $LASTEXITCODE"
    Write-AlertLog "ERROR: $message"
    Show-BridgeToast -Title "Agent Red bridge liveness" -Message $message
    exit $LASTEXITCODE
}

$liveness = Read-LivenessSnapshot
if ($null -eq $liveness) {
    $message = "liveness output missing or unreadable: $LivenessPath"
    Write-AlertLog "ERROR: $message"
    Show-BridgeToast -Title "Agent Red bridge liveness" -Message $message
    exit 1
}

$overall = [string]$liveness.overallState
$claudeVerdict = [string]$liveness.claude.verdict
$codexVerdict = [string]$liveness.codex.verdict
$claudeReason = [string]$liveness.claude.reason
$codexReason = [string]$liveness.codex.reason
$key = "$overall|claude=$claudeVerdict|codex=$codexVerdict|$claudeReason|$codexReason"

$prior = Read-AlertState
$nowUtc = (Get-Date).ToUniversalTime()
$lastToastUtc = [string]$prior.lastToastUtc
$minutesSinceToast = [double]::PositiveInfinity
if ($lastToastUtc) {
    try {
        $minutesSinceToast = ($nowUtc - [DateTime]::Parse($lastToastUtc).ToUniversalTime()).TotalMinutes
    } catch {
        $minutesSinceToast = [double]::PositiveInfinity
    }
}

$shouldToast = $false
$toastTitle = "Agent Red bridge liveness"
$toastMessage = ""
$newLastToastUtc = $lastToastUtc

if ($overall -eq "ok") {
    if ([string]$prior.lastOverallState -and [string]$prior.lastOverallState -ne "ok") {
        $shouldToast = $true
        $toastMessage = "recovered: claude=$claudeVerdict codex=$codexVerdict"
    }
    Write-AlertLog "ok: claude=$claudeVerdict codex=$codexVerdict"
} else {
    $stateChanged = ([string]$prior.lastKey -ne $key)
    $repeatDue = ($minutesSinceToast -ge $RepeatAlertMinutes)
    if ($stateChanged -or $repeatDue) {
        $shouldToast = $true
        $toastMessage = "${overall}: claude=$claudeVerdict codex=$codexVerdict"
    }
    Write-AlertLog "${overall}: claude=$claudeVerdict codex=$codexVerdict"
}

if ($shouldToast) {
    Show-BridgeToast -Title $toastTitle -Message $toastMessage
    $newLastToastUtc = $nowUtc.ToString("o")
}

Write-AlertState -Key $key -OverallState $overall -LastToastUtc $newLastToastUtc

if ($overall -eq "ok") {
    exit 0
}

exit 2
