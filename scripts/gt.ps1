#!/usr/bin/env pwsh
# GT-KB in-root launcher.
#
# Forwards every argument to the project CLI intact -- including arguments that
# contain embedded newlines -- by splatting the automatic $args array rather
# than reconstructing a command string. String reconstruction is the mechanism
# that truncates newline-bearing arguments (WI-5845) and must not be used here.
#
# The interpreter is resolved by in-root relative path, so this launcher carries
# no dependency on any location outside the project root, per
# ADR-ISOLATION-APPLICATION-PLACEMENT-001.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot 'groundtruth-kb/.venv/Scripts/python.exe'

if (-not (Test-Path -LiteralPath $python)) {
    Write-Error "Project interpreter not found at '$python'."
    exit 1
}

& $python -m groundtruth_kb.cli @args
exit $LASTEXITCODE
