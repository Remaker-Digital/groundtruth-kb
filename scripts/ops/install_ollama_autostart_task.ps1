#requires -Version 5.1
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string] $TaskName = "GTKB-Ollama-Serve",
    [string] $OllamaExePath = "",
    [string] $TaskDescription = "Start the local Ollama server for GT-KB dispatch readiness.",
    [switch] $Force
)

Set-StrictMode -Version 3.0
$ErrorActionPreference = "Stop"

function Resolve-OllamaExecutable {
    param([string] $Candidate)

    if ($Candidate) {
        if (-not (Test-Path -LiteralPath $Candidate -PathType Leaf)) {
            throw "Ollama executable not found at '$Candidate'."
        }
        return (Resolve-Path -LiteralPath $Candidate).Path
    }

    $command = Get-Command "ollama.exe" -ErrorAction SilentlyContinue
    if ($command -and $command.Source) {
        return $command.Source
    }

    $defaultPath = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    if (Test-Path -LiteralPath $defaultPath -PathType Leaf) {
        return (Resolve-Path -LiteralPath $defaultPath).Path
    }

    throw "Ollama executable not found. Pass -OllamaExePath explicitly."
}

if ($PSVersionTable.PSEdition -eq "Core" -and -not $IsWindows) {
    throw "This installer targets Windows Task Scheduler."
}

$resolvedOllama = Resolve-OllamaExecutable -Candidate $OllamaExePath
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing -and -not $Force) {
    Write-Host "Scheduled task '$TaskName' already exists. Use -Force to replace it."
    return
}

$action = New-ScheduledTaskAction -Execute $resolvedOllama -Argument "serve"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel LeastPrivilege
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DisallowStartIfOnBatteries:$false -StartWhenAvailable

if ($PSCmdlet.ShouldProcess($TaskName, "Register Ollama autostart scheduled task")) {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $action `
        -Trigger $trigger `
        -Principal $principal `
        -Settings $settings `
        -Description $TaskDescription `
        -Force:$Force | Out-Null
    Write-Host "Registered scheduled task '$TaskName' to run '$resolvedOllama serve' at user logon."
}
