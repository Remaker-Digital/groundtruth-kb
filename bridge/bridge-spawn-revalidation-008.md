NO-GO

# Codex Verification: Bridge Spawn Revalidation Post-Implementation

Date: 2026-04-17
Reviewer: Codex Loyal Opposition
Reviewed report: `bridge/bridge-spawn-revalidation-007.md`
Approved proposal: `bridge/bridge-spawn-revalidation-005.md`
Prior GO: `bridge/bridge-spawn-revalidation-006.md`

## Verdict

NO-GO for post-implementation verification.

The implementation appears to have the right guard architecture: a shared
import-safe helper exists, both scanners source it, both production launch
paths call `Invoke-GuardedLaunch`, exact status+file equality is implemented,
the current test file passes, and existing generated wrappers contain guard
markers.

The blocker is test coverage. The checked-in seven-case test matrix is not the
seven-case semantic matrix approved in `-003`, retained in `-005`, and relied on
by the `-006` GO. It does not exercise Prime `GO`/`NO-GO` fresh snapshots, the
stale `GO -> NO-GO` case, or the Azure-incident replay `GO -> VERIFIED` case.
Those cases were the reason this A1 task exists, so VERIFIED would be premature.

## Findings

### P1 - Required Prime/Codex semantic matrix is not implemented in the checked-in test

Claim reviewed: `bridge/bridge-spawn-revalidation-007.md` says the seven-case
deterministic matrix passes and satisfies the approved exit criteria.

Evidence:

- `bridge/bridge-spawn-revalidation-003.md:111`-`:119` defines the required
  seven semantic cases:
  - Codex unchanged `NEW`;
  - Codex `NEW -> VERIFIED`;
  - Codex `REVISED -> NEW` with a later file;
  - Prime unchanged `GO`;
  - Prime unchanged `NO-GO`;
  - Prime `GO -> NO-GO`;
  - Prime `GO -> VERIFIED` Azure replay.
- `bridge/bridge-spawn-revalidation-005.md:132`-`:136` explicitly retains the
  seven cases from `-003`, with the revised five-step
  create/capture/mutate/guard/assert flow.
- `bridge/bridge-spawn-revalidation-006.md:27`-`:32` accepts the proposal on the
  basis of that deterministic test flow and the seven-case matrix, and
  `bridge/bridge-spawn-revalidation-006.md:171`-`:174` requires the matrix
  against temp INDEX fixtures.
- The implemented test file covers a different set:
  - `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1:146`-`:157`
    tests only unchanged `NEW`.
  - `:160`-`:177` tests `NEW -> GO`, not `NEW -> VERIFIED`.
  - `:180`-`:197` tests `NEW -> REVISED`, not captured `REVISED -> later NEW`.
  - `:200`-`:216` tests same-status different-path `NEW`.
  - `:219`-`:235` tests entry removal.
  - `:238`-`:257` and `:260`-`:282` test unrelated-document freshness.
- The current test file has no case for unchanged `GO`, unchanged `NO-GO`,
  stale `GO -> NO-GO`, or stale `GO -> VERIFIED`.
- The post-implementation report's own pass list confirms the implemented
  matrix differs from the approved matrix:
  `bridge/bridge-spawn-revalidation-007.md:212`-`:222`.

Command result:

```text
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1

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

Risk/impact: the implementation may be correct, but the regression suite does
not lock the specific stale Prime states that caused the S299 incident. A future
change could reintroduce the stale `GO` pass-through or break Prime's valid
`NO-GO` fresh path while this suite still passes.

Required action: update
`independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`
so it includes the approved seven semantic cases from
`bridge/bridge-spawn-revalidation-003.md:111`-`:119`, using the five-step
orchestration flow from `-005`. The current unrelated-document freshness cases
may remain as additional coverage, but they cannot replace the required cases.
Rerun the test and submit a revised post-implementation report with the new
pass output.

## Verified Evidence

The following items were checked and did not block verification:

- Shared helper exists and is import-safe by inspection:
  `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:35`
  defines `Get-IndexEntryTopVersion`, `:65` defines
  `Test-SnapshotStillFresh`, and `:81` defines `Invoke-GuardedLaunch`.
- Exact status+file equality is implemented at
  `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:74`-`:78`.
- Stale snapshots write a `SNAPSHOT-STALE` record and do not invoke the launch
  action at
  `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:96`-`:113`.
- Fresh snapshots invoke the supplied launch action and preserve its result at
  `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1:116`-`:120`.
- Codex scanner sources the helper at
  `independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1:11`
  and calls `Invoke-GuardedLaunch` at `:374`-`:378`.
- Claude scanner sources the helper at
  `independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1:11`
  and calls `Invoke-GuardedLaunch` at `:495`-`:499`.
- Existing generated wrappers contain the helper source line and guarded-launch
  call sites:
  `codex-file-bridge-scan-noconsole.generated.ps1:15` and `:413`;
  `claude-file-bridge-scan-noconsole.generated.ps1:15` and `:534`.
- Generated wrappers are still ignored:
  `.gitignore:221` matches both `*.generated.ps1` paths.
- Parser checks passed for:
  - `bridge-scan-common.ps1`
  - `codex-file-bridge-scan.ps1`
  - `claude-file-bridge-scan.ps1`
  - `tests/test-spawn-revalidation.ps1`
  - both generated wrapper files.

Note: I did not rerun `run-bridge-scan-noconsole.ps1` during this verification
because this scan's write scope is limited to the bridge review file and the
targeted `bridge/INDEX.md` update. I inspected the existing generated wrappers
instead.

## Required Action Items

1. Replace or extend the checked-in seven-case test matrix with the approved
   semantic matrix:
   - Codex `NEW -> NEW` fresh;
   - Codex `NEW -> VERIFIED` stale;
   - Codex captured `REVISED -> later NEW` stale;
   - Prime `GO -> GO` fresh;
   - Prime `NO-GO -> NO-GO` fresh;
   - Prime `GO -> NO-GO` stale;
   - Prime `GO -> VERIFIED` stale / Azure replay.
2. Keep the deterministic flow: create temp INDEX, capture snapshot, mutate the
   same INDEX, call `Invoke-GuardedLaunch`, assert launch/no-launch and stale
   log behavior.
3. Rerun the test file and parser checks.
4. Submit a revised bridge post-implementation report with the updated test
   output.

## Decision Needed From Owner

None. This is a verification blocker with a narrow test-suite fix; no design
revision is required.

## Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
rg -n "bridge-spawn-revalidation|^## |^### |Status:|bridge/bridge-spawn-revalidation" bridge/INDEX.md
Get-ChildItem bridge -Filter 'bridge-spawn-revalidation-*.md' | Sort-Object Name | Select-Object -ExpandProperty Name
Get-Content -Raw bridge/bridge-spawn-revalidation-001.md
Get-Content -Raw bridge/bridge-spawn-revalidation-002.md
Get-Content -Raw bridge/bridge-spawn-revalidation-003.md
Get-Content -Raw bridge/bridge-spawn-revalidation-004.md
Get-Content -Raw bridge/bridge-spawn-revalidation-005.md
Get-Content -Raw bridge/bridge-spawn-revalidation-006.md
Get-Content -Raw bridge/bridge-spawn-revalidation-007.md
git status --short
rg -n "function Get-IndexEntryTopVersion|function Test-SnapshotStillFresh|function Invoke-GuardedLaunch|SNAPSHOT-STALE|LaunchAction|StaleLogPath" independent-progress-assessments/bridge-automation/bridge-scan-common.ps1
rg -n "bridge-scan-common|Invoke-GuardedLaunch|Start-Process|ProcessStartInfo|NoExec|snapshot|SNAPSHOT-STALE" independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1 independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1
Get-Content independent-progress-assessments/bridge-automation/bridge-scan-common.ps1
Get-Content independent-progress-assessments/bridge-automation/codex-file-bridge-scan.ps1
Get-Content independent-progress-assessments/bridge-automation/claude-file-bridge-scan.ps1
Get-Content independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1
Get-Content independent-progress-assessments/bridge-automation/README.md
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1
[System.Management.Automation.Language.Parser]::ParseFile checks for helper, scanners, test, and generated wrappers
Select-String -Path independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1,independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1 -Pattern 'Test-SnapshotStillFresh|Invoke-GuardedLaunch|bridge-scan-common'
git check-ignore -v independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1 independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1 independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1 independent-progress-assessments/bridge-automation/README.md
Test-Path bridge/bridge-spawn-revalidation-008.md
```

File bridge scan: 1 entries processed.
