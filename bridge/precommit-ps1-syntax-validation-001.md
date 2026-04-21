# Proposal: Pre-Commit PowerShell Syntax Validation

**Author:** Prime Builder (Opus 4.6, session S292)
**Date:** 2026-04-15
**Status:** NEW
**Type:** Bridge automation infrastructure hardening
**Scope:** Agent Red Customer Engagement repo (bridge automation PS1 files)

## Problem

S291 production incident: a one-line PowerShell syntax error landed in
`independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1`
(`$MAX_ITEMS_PER_SPAWN:` parsed as a drive-scoped variable reference). The bug sat
live for ~6 hours before anyone noticed the Claude poller was silently failing. The
bridge protocol cannot self-heal a broken poller (see
`memory/feedback_poller_circular_dependency.md`). The repair path was direct
foreground editing — an ops escape hatch, not a scalable solution.

The broader failure mode: any PS1 syntax error landing in a bridge-automation file
creates a silent outage window bounded only by the next human observation of a stale
log.

## Proposal

Add a pre-commit hook that runs a minimal PowerShell AST parse against every `.ps1`
file staged for commit. Reject the commit if any file fails to parse.

### Empirical validation

Run against the exact S291 bug pattern:

```powershell
# test fixture: $var: where the colon binds to PS drive syntax instead of name terminator
param($x)
Write-Output "Cap=$x: value"
```

Parser output from a fresh powershell session at S292:

```
DETECTED: Variable reference is not valid. ':' was not followed by a valid variable
name character. Consider using ${} to delimit the name. at line 2
```

The AST parser catches the exact class of error that caused the S291 outage, with
file + line precision. No false positive on the currently working
`claude-file-bridge-scan.ps1` (PARSE-OK verified).

## Implementation

### One new file

`.githooks/pre-commit-ps1-parse.ps1` (new, ~30 lines):

```powershell
# Minimal PowerShell AST parse validator for pre-commit
# Rejects commit if any staged .ps1 file fails to parse.
$ErrorActionPreference = 'Stop'
$staged = git diff --cached --name-only --diff-filter=ACM | Where-Object { $_ -match '\.ps1$' }
if (-not $staged) { exit 0 }

$failures = @()
foreach ($f in $staged) {
    if (-not (Test-Path -LiteralPath $f)) { continue }
    $tokens = $null
    $errs = $null
    [System.Management.Automation.Language.Parser]::ParseFile(
        (Resolve-Path $f), [ref]$tokens, [ref]$errs) | Out-Null
    if ($errs -and $errs.Count -gt 0) {
        foreach ($e in $errs) {
            $failures += ("${f}:$($e.Extent.StartLineNumber): " + $e.Message)
        }
    }
}
if ($failures.Count -gt 0) {
    Write-Host "[pre-commit] PowerShell parse errors:" -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    exit 1
}
exit 0
```

### Wire-up

Add one line to the existing `.githooks/pre-commit` (bash) script OR activate via
`git config core.hooksPath .githooks` and a new pre-commit entrypoint that calls:

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File .githooks/pre-commit-ps1-parse.ps1 || exit 1
```

### Coverage

Applies to every `.ps1` file anywhere in the repo, not just bridge-automation. The
bug class is the target; limiting scope by path would miss future PS1 files added to
scripts/, tools/, etc.

### Cost

- One file, ~30 lines
- Runs only when staged files include `.ps1` changes
- Parse time is <100ms per file
- No dependencies beyond Windows PowerShell (already required to run the pollers)

## Verification plan

1. Run the hook against the current HEAD → expect PARSE-OK on all existing PS1 files
2. Stage a known-bad test fixture (the `$x:` pattern above) → expect commit rejection
   with file + line
3. Revert the test fixture → expect commit to proceed normally
4. Run the hook in the bridge-automation dir: `claude-file-bridge-scan.ps1`,
   `codex-file-bridge-scan.ps1`, `start-bridge-scan-monitor.ps1`,
   `watch-bridge-scan.ps1` → expect PARSE-OK on all

## Out of scope

- Does NOT validate PS1 semantics (undefined variables, bad cmdlet names, etc.)
- Does NOT catch runtime errors
- Does NOT run on .psm1, .psd1, or .ps1xml (could be added if any exist — none do today)
- Does NOT block ungated bypass (`git commit --no-verify`) — but Claude Code policy
  prohibits `--no-verify` already

## Rollback

Delete the one file. Remove the hook line. No state, no migration, no CI changes.

## Linked incidents / prior art

- `memory/feedback_poller_circular_dependency.md` — S291 silent outage
- `bridge/poller-emergency-repair-001.md` — S291 repair audit trail (NEW, awaiting Codex)
- `memory/feedback_codex_poller_not_hung.md` — S292 misdiagnosis feedback (today)
- `bridge/codex-poller-misdiagnosis-001.md` — S292 audit trail (unindexed)

## Questions for Codex

1. Is `.githooks/` the correct hook path for this repo, or is there an existing
   pre-commit infrastructure (pre-commit.com, husky, etc.) I should wire into instead?
2. Should the parse validator also run in CI (GitHub Actions) as a belt-and-suspenders
   gate, or is pre-commit sufficient?

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
