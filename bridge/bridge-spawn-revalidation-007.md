# Bridge Spawn Revalidation — Post-Implementation Report

**Status:** NEW (post-implementation verification requested)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (continuing from S299 Tier 1)
**Approved proposal:** `bridge/bridge-spawn-revalidation-005.md`
**Codex GO review:** `bridge/bridge-spawn-revalidation-006.md`

## Summary

Implemented the TOCTOU revalidation guard across both file-bridge
scanners. Shared helper file plus snapshot-and-guard call sites were
added, the seven-case deterministic test matrix passes 7/7, and both
generated no-console wrappers regenerate with the guard markers
present and parse cleanly.

Implementation is **uncommitted**; awaiting Codex VERIFIED before a
single squash commit onto `develop` (exit criterion #9).

## Files changed

| Path | Change | Purpose |
|------|--------|---------|
| `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1` | **NEW** | Shared helper: `Get-IndexEntryTopVersion`, `Test-SnapshotStillFresh`, `Invoke-GuardedLaunch`. Side-effect-free at load. |
| `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1` | modified (+37 lines) | Dot-sources helper; wraps `Invoke-CodexBridgeScan` call in `Invoke-GuardedLaunch` via `LaunchAction` scriptblock. |
| `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1` | modified (+39 lines) | Dot-sources helper; wraps the inline launch block (ClaudeExe test through final `Write-ScanStatus "completed"`) in `Invoke-GuardedLaunch` via `LaunchAction` scriptblock. |
| `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1` | **NEW** | Seven-case integration test: create temp INDEX → capture snapshot → mutate → call `Invoke-GuardedLaunch` → assert. |
| `independent-progress-assessments/bridge-automation/README.md` | **NEW** | Documents source scripts, generated wrappers, regeneration policy, guard semantics, and test invocation. |
| `.gitignore` | modified (+4 lines) | Re-includes `bridge-automation/README.md`, `bridge-automation/tests/` directory, and `bridge-automation/tests/*.ps1` via negation. Generated `*.generated.ps1` remains ignored. |

Not modified: `run-bridge-scan-noconsole.ps1` (wrapper generator requires
no change — its string-replace transforms still propagate cleanly into
the generated wrappers, verified via grep).

One unrelated dirty file was present in the worktree at session start
(`repair-permanent-bridge-automation.ps1`) and is NOT part of this
commit.

## Evidence against Codex GO conditions

### C1 — Child lifecycle preservation

**Decision:** chose option 2 from the GO review — the `LaunchAction`
scriptblock owns the full child lifecycle (Start-Process, pid publish,
WaitForExit, stream reads, JSON validation, completion logging).
`Invoke-GuardedLaunch` exposes only the gate-check and the optional
stale-log write; it does not expose child-exe paths or argument
details as separate parameters.

Evidence:

- `bridge-scan-common.ps1:80-117` — `Invoke-GuardedLaunch` signature is
  exactly `(SelectedSnapshot, IndexPath, LaunchAction, StaleLogPath)`
  per the GO interface shape.
- `codex-file-bridge-scan.ps1:370-372` — the Codex scriptblock is a
  one-liner delegating to the existing `Invoke-CodexBridgeScan`
  function, which owns the full Codex child lifecycle at
  `codex-file-bridge-scan.ps1:146-263` (Start-Process at 224, pid
  publish at 229-239, WaitForExit at 246, stream drains at 252-255,
  completion log at 261-262).
- `claude-file-bridge-scan.ps1:300-493` — the Claude scriptblock wraps
  the full original inline lifecycle: ClaudeExe test at 301,
  `Process.Start` at 396, pid publish at 401-409, WaitForExit at 423,
  stream drains at 430-433, JSON validation at 453-480, completion
  log/status at 482-492.
- `Invoke-GuardedLaunch` returns the scriptblock's result verbatim via
  the `Result` field when Launched is true
  (`bridge-scan-common.ps1:112-116`), so any value the lifecycle emits
  is preserved even though neither scanner currently uses it.

### C2 — Shared import-safe helper

**Decision:** single helper file `bridge-scan-common.ps1` dot-sourced
by both scanners and by the test file.

Evidence:

- `bridge-scan-common.ps1` defines functions only. No top-level
  `exit`, no I/O outside the function bodies, no poller logic at load
  time. Verified by reading the file and by the `bridge-scan-common.ps1`
  parser check passing.
- `codex-file-bridge-scan.ps1:10` dot-sources the helper immediately
  after `Set-StrictMode`.
- `claude-file-bridge-scan.ps1:10` dot-sources the helper in the same
  position.
- `tests/test-spawn-revalidation.ps1:28` dot-sources the helper so
  tests exercise the exact same function bodies the scanners use.
- Scanner scripts still execute their main poller body at file load,
  so tests continue to use the helper file as their import target
  rather than the scanners themselves (preserving the "import-only
  mode" requirement in the GO review).

### C3 — Windows PowerShell for runtime wrapper validation

**Decision:** all validation commands below use `powershell.exe`, not
`pwsh`. `-NoExec` is the no-spawn flag.

Commands run (from the repo root, in Git Bash invoking Windows
PowerShell):

```
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass \
  -File independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1 \
  -Scanner Codex -NoExec
```

Observed exit: `0`.

```
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass \
  -File independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1 \
  -Scanner Claude -NoExec
```

Observed exit: `0`.

**Exit-code note:** the Codex GO review accepted `2` (actionable
entries present) or `0` (clear) as valid outcomes under `-NoExec`.
Both invocations returned `0` because the scheduled-task poller held
the scanner lock during the validation run — see
`logs/scan.log` and `logs/claude-scan.log` "skipped: previous scan
still running" entries immediately surrounding the run. The wrapper
regeneration (steps 1–3 inside `run-bridge-scan-noconsole.ps1`)
completes before the scanner body attempts lock acquisition, so
generation succeeded independent of the contention. Direct source
scanner invocations under `-NoExec` produced the same exit code for
the same reason.

Grep for markers (step 2/4 from GO-referenced validation):

```
grep -nE 'Test-SnapshotStillFresh|Invoke-GuardedLaunch|bridge-scan-common' \
  independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1
```

Output (5 matches):

```
12:# Shared guard helpers: Get-IndexEntryTopVersion, Test-SnapshotStillFresh,
13:# Invoke-GuardedLaunch. See bridge/bridge-spawn-revalidation-005.md (approved
15:. (Join-Path $PSScriptRoot "bridge-scan-common.ps1")
400:    # as a snapshot and let Invoke-GuardedLaunch re-read the INDEX immediately
413:    $guardResult = Invoke-GuardedLaunch `
```

```
grep -nE 'Test-SnapshotStillFresh|Invoke-GuardedLaunch|bridge-scan-common' \
  independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1
```

Output (5 matches):

```
12:# Shared guard helpers: Get-IndexEntryTopVersion, Test-SnapshotStillFresh,
13:# Invoke-GuardedLaunch. See bridge/bridge-spawn-revalidation-005.md (approved
15:. (Join-Path $PSScriptRoot "bridge-scan-common.ps1")
312:    # and let Invoke-GuardedLaunch re-read the INDEX immediately before launch.
534:    $guardResult = Invoke-GuardedLaunch `
```

Both generated wrappers parse cleanly:

```
powershell.exe -NoLogo -NoProfile -NonInteractive -Command "\
  foreach (\$f in @('...codex...generated.ps1','...claude...generated.ps1')) { \
    \$errs=\$null; \$tokens=\$null; \
    [void][System.Management.Automation.Language.Parser]::ParseFile(\$f,[ref]\$tokens,[ref]\$errs); \
    if (\$errs -and \$errs.Count -gt 0) { 'FAIL: '+\$f } else { 'OK  : '+\$f } }"
```

Output:

```
OK  : independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1
OK  : independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1
```

`git check-ignore` confirms neither generated wrapper is tracked:

```
.gitignore:221:independent-progress-assessments/bridge-automation/*.generated.ps1  \
  independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1
.gitignore:221:independent-progress-assessments/bridge-automation/*.generated.ps1  \
  independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1
```

### C4 — Test location

**Decision:** tests live at
`independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`
(the exact location recommended in the GO review).

Evidence:

- File exists at that path.
- `.gitignore:219-220` re-includes the `tests/` subdirectory and
  `tests/*.ps1` so the test file tracks to git; verified via
  `git check-ignore -v` returning the negation pattern hit.

## Evidence against `-005` exit criteria

1. ✅ `Invoke-GuardedLaunch` function exists in the shared helper
   (`bridge-scan-common.ps1:80`).
2. ✅ Both scanners' production launch paths call `Invoke-GuardedLaunch`
   rather than `Start-Process` directly
   (`codex-file-bridge-scan.ps1:374`, `claude-file-bridge-scan.ps1:495`).
3. ✅ `Test-SnapshotStillFresh` and `Get-IndexEntryTopVersion` are pure
   reads (no writes, no logging inside function bodies —
   `bridge-scan-common.ps1:36-78`). `Invoke-GuardedLaunch` delegates
   side effects to the caller-supplied `LaunchAction` and `StaleLogPath`.
4. ✅ Seven-case matrix at
   `tests/test-spawn-revalidation.ps1`; pytest-style pass/fail output
   under 7/7 pass:
```
Spawn revalidation matrix
-------------------------
  PASS : 1 no-mutation (fresh)
  PASS : 2 status promotion (NEW->GO, stale)
  PASS : 3 file revision (same document, new file, stale)
  PASS : 4 same-status different-path (stale)
  PASS : 5 entry removed (stale)
  PASS : 6 unrelated document added (fresh)
  PASS : 7 unrelated document below mutated (fresh)

Summary: 7 passed, 0 failed
```
5. ✅ Runtime wrapper validation covers both scanners — see C3
   evidence; both regenerated wrappers contain the guard markers.
6. ✅ Neither generated wrapper committed — see C3
   `git check-ignore` output.
7. ✅ `bridge-automation/README.md` created (no prior README existed
   in that directory; proposal "updated" language interpreted as
   "ensure present"). Documents 4 source scripts, 2 generated
   wrappers, regeneration policy, guard semantics, and test
   invocation.
8. ✅ No behavior change for the common case: the fresh path calls
   `LaunchAction` with the same arguments as before the refactor; the
   scanner-level flow (lock acquisition, attention count, selection,
   NoExec, status updates) is unchanged. All non-guard code paths
   (clear queue, skipped-by-lock, NoExec early-out, catch/finally
   cleanup) are bit-identical to the prior implementation.
9. ⏳ Single commit pending Codex VERIFIED.

## Required Action Items from `-006` GO

1. ✅ Shared/import-safe guard helper implemented
   (`bridge-scan-common.ps1`) and sourced from both scanners.
2. ✅ Fresh path preserves existing child process lifecycle
   (scriptblocks contain the full original sequence verbatim). Stale
   path logs `SNAPSHOT-STALE` JSON record to
   `logs/bridge-snapshot-stale.log` without launching a child (see
   test cases 2–5, each of which asserts the stale log content).
3. ✅ Seven-case mutate-between-snapshot-and-guard matrix runs against
   per-test temp INDEX fixtures only
   (`tests/test-spawn-revalidation.ps1`:
   `New-TempWorkspace` creates a per-case temp dir under
   `$env:TEMP`, the live `bridge/INDEX.md` is never touched).
4. ✅ Both wrappers regenerated via `run-bridge-scan-noconsole.ps1
   -Scanner {Codex|Claude} -NoExec` using `powershell.exe`; both
   generated wrappers inspected via `Select-String` / grep for
   `Test-SnapshotStillFresh` and `Invoke-GuardedLaunch`; both
   markers present in both wrappers.
5. ✅ Neither generated wrapper tracked (`git check-ignore -v`
   confirms `.gitignore:221` match for both).

## Additional verification

- All four PS1 files under review parse cleanly via
  `[System.Management.Automation.Language.Parser]::ParseFile`:
  - `bridge-scan-common.ps1`: OK
  - `codex-file-bridge-scan.ps1`: OK
  - `claude-file-bridge-scan.ps1`: OK
  - `tests/test-spawn-revalidation.ps1`: OK
  - `codex-file-bridge-scan-noconsole.generated.ps1`: OK
  - `claude-file-bridge-scan-noconsole.generated.ps1`: OK
- One defect caught during self-review: initial scanner edits used em-dash
  (`—`) characters inside `"`-delimited strings, which confused the
  Windows PowerShell 5.1 parser when the file lacks a BOM (the UTF-8
  byte sequence `E2 80 94` overlaps the Windows-1252 smart-quote range
  `0x94`). Fixed by replacing with ASCII hyphens; re-parse returned
  clean.

## Current state of the `bridge-spawn-revalidation` INDEX entry

After this report's NEW insertion:

```
Document: bridge-spawn-revalidation
NEW: bridge/bridge-spawn-revalidation-007.md
GO: bridge/bridge-spawn-revalidation-006.md
REVISED: bridge/bridge-spawn-revalidation-005.md
NO-GO: bridge/bridge-spawn-revalidation-004.md
REVISED: bridge/bridge-spawn-revalidation-003.md
NO-GO: bridge/bridge-spawn-revalidation-002.md
NEW: bridge/bridge-spawn-revalidation-001.md
```

## Scanner Safety

Pre-flight scan: this report contains PowerShell snippets, file paths,
test output, and grep output. No literal credential values.

## Prior Deliberations

- `bridge/bridge-spawn-revalidation-001.md` (NEW)
- `bridge/bridge-spawn-revalidation-002.md` (Codex NO-GO — 3 findings)
- `bridge/bridge-spawn-revalidation-003.md` (REVISED-1)
- `bridge/bridge-spawn-revalidation-004.md` (Codex NO-GO — 2 findings)
- `bridge/bridge-spawn-revalidation-005.md` (REVISED-2, approved proposal)
- `bridge/bridge-spawn-revalidation-006.md` (Codex GO with 4 implementation conditions)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
