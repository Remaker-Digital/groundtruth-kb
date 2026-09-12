# Readiness probe for the GT-KB native domain service, shared by register-domain-service.ps1 and its tests.
# Dot-source this file, then call Wait-GtkbDomainServiceReady. The probe runs the ordinary status command bound to
# the loopback endpoint through GT_AUTHORITY_URL; a failed probe is an expected condition while the service starts,
# so native stderr and non-zero exit codes are captured and never terminate the loop, whatever the caller's
# $ErrorActionPreference (Windows PowerShell 5.1 raises NativeCommandError for redirected native stderr under 'Stop').

function Wait-GtkbDomainServiceReady {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)] [string]$ProbeInterpreter,
        [Parameter(Mandatory = $true)] [string]$OperatorConfig,
        [Parameter(Mandatory = $true)] [int]$Port,
        [int]$Seconds = 60,
        [int]$IntervalSeconds = 2
    )
    $previousUrl = $env:GT_AUTHORITY_URL
    $env:GT_AUTHORITY_URL = ('http://127.0.0.1:{0}' -f $Port)
    $deadline = (Get-Date).AddSeconds($Seconds)
    $attempts = 0
    $lastOutput = ''
    $ready = $false
    try {
        do {
            $attempts += 1
            $ErrorActionPreference = 'Continue'   # scoped to this function; expected probe failures must not throw
            try {
                # Windows PowerShell 5.1 renders redirected native stderr as ErrorRecords; keep their message text only.
                $lastOutput = (& $ProbeInterpreter -m groundtruth_kb --config $OperatorConfig service status --json 2>&1 | ForEach-Object { if ($_ -is [System.Management.Automation.ErrorRecord]) { $_.Exception.Message } else { $_ } } | Out-String)
                $code = $LASTEXITCODE
            } catch {
                $lastOutput = $_.Exception.Message
                $code = -1
            }
            if ($code -eq 0) { $ready = $true; break }
            if ((Get-Date) -ge $deadline) { break }
            Start-Sleep -Seconds $IntervalSeconds
        } while ($true)
    } finally {
        if ($null -eq $previousUrl) { Remove-Item Env:GT_AUTHORITY_URL -ErrorAction SilentlyContinue } else { $env:GT_AUTHORITY_URL = $previousUrl }
    }
    return [pscustomobject]@{ Ready = $ready; Attempts = $attempts; Port = $Port; LastOutput = $lastOutput.Trim() }
}
