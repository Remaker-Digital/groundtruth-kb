$ErrorActionPreference = 'Stop'

$repoRoot = (git rev-parse --show-toplevel 2>$null)
if (-not $repoRoot) { exit 1 }

$venvPython = Join-Path $repoRoot 'groundtruth-kb/.venv/Scripts/python.exe'
if (Test-Path -LiteralPath $venvPython) {
    $pythonBin = $venvPython
} elseif ($env:PYTHON) {
    $pythonBin = $env:PYTHON
} else {
    $pythonBin = 'python'
}

$srcPath = Join-Path $repoRoot 'groundtruth-kb/src'
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = "$srcPath;$env:PYTHONPATH"
} else {
    $env:PYTHONPATH = $srcPath
}

Push-Location $repoRoot
try {
    & $pythonBin -m groundtruth_kb.cli commit preflight
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
