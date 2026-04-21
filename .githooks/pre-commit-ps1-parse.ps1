# Pre-commit PowerShell AST syntax validator
# Reads staged blob content via git-show to parse exactly what will be committed.
# Rejects the commit if any staged .ps1 file fails the AST parse.
#
# Called by .githooks/pre-commit when staged files include .ps1 changes.
# Do not invoke directly during a commit — use the bash pre-commit entrypoint.
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

$ErrorActionPreference = 'Stop'

# Collect staged .ps1 files (Added, Copied, Modified — excludes Deleted)
$staged = git diff --cached --name-only --diff-filter=ACM 2>$null |
    Where-Object { $_ -match '\.ps1$' }

if (-not $staged) { exit 0 }

$failures = @()

foreach ($f in $staged) {
    # Read the staged blob content (index entry), not the worktree file.
    # This ensures we parse exactly what will be committed, regardless of
    # any unstaged working-tree changes.
    $content = git show ":$f" 2>&1
    if ($LASTEXITCODE -ne 0) {
        # Blob unresolvable (e.g., path staged but index entry missing) — skip.
        continue
    }

    # ParseInput parses a string; ParseFile would read the worktree file instead.
    $tokens = $null
    $errs = $null
    [System.Management.Automation.Language.Parser]::ParseInput(
        ($content -join "`n"),
        [ref]$tokens,
        [ref]$errs
    ) | Out-Null

    if ($errs -and $errs.Count -gt 0) {
        foreach ($e in $errs) {
            $line = $e.Extent.StartLineNumber
            $failures += "${f}:${line}: $($e.Message)"
        }
    }
}

if ($failures.Count -gt 0) {
    Write-Host "[pre-commit] PowerShell syntax errors in staged files:" -ForegroundColor Red
    foreach ($msg in $failures) {
        Write-Host "  $msg" -ForegroundColor Red
    }
    Write-Host "[pre-commit] Fix the errors above, re-stage, and recommit." -ForegroundColor Red
    exit 1
}

Write-Host "[pre-commit] PS1 syntax OK ($($staged.Count) file(s) checked)." -ForegroundColor Green
exit 0
