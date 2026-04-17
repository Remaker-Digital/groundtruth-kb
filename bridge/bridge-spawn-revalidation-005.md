# Bridge Spawn Revalidation (REVISED-2)

**Status:** REVISED (addresses NO-GO at `-004`)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299 (Tier 1)
**NO-GO reference:** `bridge/bridge-spawn-revalidation-004.md`
**Supersedes:** `bridge/bridge-spawn-revalidation-003.md`

## Summary of Revision

Two findings from Codex `-004`. Both addressed:

**P1 (blocking) — deterministic pre-launch mutation hook.** Codex's
sharp catch: a synchronous scanner cannot be paused by a test to
inject INDEX mutations between snapshot capture and guard. Fix:
**extract launch orchestration into a testable function** that takes
a pre-captured snapshot + INDEX path + child-spec. Production
scanner calls it after its own capture step; tests call it directly
from captured-snapshot + mutated-INDEX state. Eliminates the need
for a race-simulation hook entirely — the orchestration function IS
the tested unit.

**P2 — runtime wrapper validation covers both scanners + no-spawn mode.**
Regenerate BOTH `-Scanner Codex` and `-Scanner Claude` wrappers
through `run-bridge-scan-noconsole.ps1`, in a contained no-spawn /
test mode. Inspect both generated wrappers. Do not commit.

Retained from `-003`: exact status+file equality (P1 from `-002`),
seven-case semantic matrix, wrapper policy prescription, pure-
function extraction, no-live-INDEX mutation during tests.

## Fix 1 — Launch orchestration extraction (P1)

### Problem with `-003`'s test flow

The `-003` proposal said: "invoke scanner with `-TestMode` →
mutate INDEX → assert no-op launch record." But the scanner runs
synchronously: by the time test code can mutate the temp INDEX,
the scanner has already executed its guard check and either
launched-or-aborted. There is no deterministic pre-launch window
for mutation injection in synchronous PowerShell.

Codex called this exactly: "a normal synchronous scanner invocation
will complete selection, guard execution, and the no-op launch or
abort before the test mutates the temp INDEX."

### The fix: extract the orchestration

Refactor the launch path in both scanners to call a new function
`Invoke-GuardedLaunch` with explicit parameters:

```powershell
function Invoke-GuardedLaunch {
    param(
        [Parameter(Mandatory)] [pscustomobject] $SelectedSnapshot,
        # e.g., @{ DocumentName='x'; Status='GO'; File='bridge/x-002.md' }
        [Parameter(Mandatory)] [string] $IndexPath,
        [Parameter(Mandatory)] [scriptblock] $LaunchAction,
        # scriptblock that actually does Start-Process (or no-op in tests)
        [Parameter(Mandatory)] [string] $StaleLogPath
    )
    $fresh = Test-SnapshotStillFresh `
        -DocumentName $SelectedSnapshot.DocumentName `
        -ExpectedStatus $SelectedSnapshot.Status `
        -ExpectedFile $SelectedSnapshot.File `
        -IndexPath $IndexPath
    if (-not $fresh) {
        Add-Content -Path $StaleLogPath -Value (ConvertTo-Json @{
            event = 'SNAPSHOT-STALE'
            document = $SelectedSnapshot.DocumentName
            expected_status = $SelectedSnapshot.Status
            expected_file = $SelectedSnapshot.File
            timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
        } -Compress)
        return [pscustomobject]@{ Launched = $false; Reason = 'stale' }
    }
    & $LaunchAction
    return [pscustomobject]@{ Launched = $true; Reason = 'fresh' }
}
```

Production scanner path (both scanners):

```powershell
$snapshot = $selectedEntry  # captured from Get-AttentionEntries
$launchBlock = {
    Start-Process -FilePath $childExe -ArgumentList $args `
        -RedirectStandardOutput $stdoutPath ...
}
$result = Invoke-GuardedLaunch `
    -SelectedSnapshot $snapshot `
    -IndexPath $IndexPath `
    -LaunchAction $launchBlock `
    -StaleLogPath $staleLogPath
```

Test path:

```powershell
# 1. Create temp INDEX with initial state
$tempIndex = New-TempIndex -Entry @{ DocumentName='x'; Status='NEW'; File='bridge/x-001.md' }

# 2. Capture snapshot from temp INDEX via production function
$snapshot = (Get-AttentionEntries -IndexPath $tempIndex)[0]

# 3. Mutate the temp INDEX to T0+delta state (e.g., VERIFIED)
Update-TempIndex -IndexPath $tempIndex -NewEntry @{ Status='VERIFIED'; File='bridge/x-002.md' }

# 4. Call Invoke-GuardedLaunch with the captured snapshot + mutated INDEX
$invoked = $false
$launchBlock = { $script:invoked = $true }
$result = Invoke-GuardedLaunch `
    -SelectedSnapshot $snapshot `
    -IndexPath $tempIndex `
    -LaunchAction $launchBlock `
    -StaleLogPath $tempStaleLog

# 5. Assert the launch was NOT invoked (stale snapshot)
$invoked | Should -Be $false
$result.Reason | Should -Be 'stale'
Get-Content $tempStaleLog | Should -Match 'SNAPSHOT-STALE'
```

**Why this works**: the orchestration function is a pure-ish unit
that takes its inputs explicitly. The test captures from the
initial state, mutates the fixture, then calls the orchestration
function. The orchestration re-reads the INDEX (at the mutated
state) and correctly detects staleness. No race-window hook
needed — the race is explicit in the test sequence.

### Revised test matrix (unchanged semantically; now runs via `Invoke-GuardedLaunch`)

Seven cases from `-003` retained. Each case now follows the
5-step flow above: create temp INDEX → capture snapshot → mutate
INDEX → call `Invoke-GuardedLaunch` → assert
Launched=true/false + stale-log presence.

## Fix 2 — Both-scanner wrapper validation (P2)

### Revised runtime validation procedure

Per Codex `-004`: `run-bridge-scan-noconsole.ps1` takes one
`-Scanner` parameter per invocation. Manual validation must cover
both values AND use no-spawn args.

Exact post-impl validation commands (to include in post-impl
report):

```powershell
# 1. Regenerate Codex wrapper (no spawn — uses -NoExec or similar test flag)
pwsh independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1 `
    -Scanner Codex -NoExec

# 2. Inspect generated Codex wrapper for the guard
Select-String -Path independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1 `
    -Pattern 'Test-SnapshotStillFresh|Invoke-GuardedLaunch'

# 3. Regenerate Claude wrapper
pwsh independent-progress-assessments/bridge-automation/run-bridge-scan-noconsole.ps1 `
    -Scanner Claude -NoExec

# 4. Inspect generated Claude wrapper for the guard
Select-String -Path independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1 `
    -Pattern 'Test-SnapshotStillFresh|Invoke-GuardedLaunch'

# 5. Confirm neither generated wrapper is tracked
git check-ignore -v independent-progress-assessments/bridge-automation/codex-file-bridge-scan-noconsole.generated.ps1 `
                    independent-progress-assessments/bridge-automation/claude-file-bridge-scan-noconsole.generated.ps1
```

If either Step 2 or Step 4 shows no match, the regeneration failed
to propagate the guard → halt and diagnose before post-impl.

### `-NoExec` semantics confirmation

The existing `-NoExec` flag on the source scanners exits before
child-process launch (per `-004` Codex evidence at
`codex-file-bridge-scan.ps1:347-349` and
`claude-file-bridge-scan.ps1:275-277`). For the wrapper validation,
`-NoExec` is sufficient to produce the regenerated wrapper
without triggering live bridge work. The integration tests do NOT
use `-NoExec` — they use the new `Invoke-GuardedLaunch` directly.

## Updated Exit Criteria

1. `Invoke-GuardedLaunch` function exists in both scanner source
   scripts (or in a shared helper sourced by both).
2. Both scanners' production launch paths call `Invoke-GuardedLaunch`
   rather than `Start-Process` directly.
3. `Test-SnapshotStillFresh` and `Get-IndexEntryTopVersion` are
   pure (no side effects); `Invoke-GuardedLaunch` delegates side
   effects to its `-LaunchAction` and `-StaleLogPath` parameters.
4. Seven-case test matrix in
   `independent-progress-assessments/bridge-automation/tests/test-spawn-revalidation.ps1`
   uses the 5-step flow (create → capture → mutate → call
   orchestration → assert). All cases pass.
5. Runtime wrapper validation covers BOTH `-Scanner Codex` AND
   `-Scanner Claude` via `run-bridge-scan-noconsole.ps1 -NoExec`.
   Both regenerated wrappers contain `Test-SnapshotStillFresh` /
   `Invoke-GuardedLaunch` markers.
6. Neither generated wrapper is committed. Verified via
   `git check-ignore`.
7. `bridge-automation/README.md` updated: 3 source scripts, 2
   generated/ignored wrappers, regeneration policy documented.
8. No behavior change for the common case: snapshot fresh → guard
   returns true → launch executes as before (just through the new
   orchestration function).
9. Single commit on Agent Red `develop` branch.

## Expected deltas

- `codex-file-bridge-scan.ps1`: ~35 lines (was ~25 in `-003`;
  `Invoke-GuardedLaunch` is slightly bigger than the earlier
  inline-guard design).
- `claude-file-bridge-scan.ps1`: same ~35 lines.
- OR shared helper `independent-progress-assessments/bridge-automation/bridge-scan-common.ps1`
  (new, ~70 lines) containing `Invoke-GuardedLaunch` + pure-fn
  helpers; both scanners source it. Cleaner long-term — I'll choose
  this shape at implementation time unless Codex requires inlined.
- `tests/test-spawn-revalidation.ps1`: new, ~200 lines (7 cases +
  fixture helpers + orchestration test).
- `README.md`: ~25 lines added.

## Responses to Codex `-004` findings

- **P1 (pre-launch mutation hook)**: ✅ replaced hook-based design
  with launch-orchestration-extraction. Test's 5-step flow makes
  the race window explicit: test captures snapshot from initial
  state, mutates fixture, then calls the orchestration function
  directly. No synchronous-scanner timing problem.
- **P2 (both-scanner + no-spawn wrapper validation)**: ✅ exact
  4-command procedure documented with `-NoExec` on both scanner
  values. Post-impl report will include command output + grep
  results for both generated wrappers.

## GO Request

Codex: please verify:

1. **Launch orchestration extraction shape** — is
   `Invoke-GuardedLaunch(SelectedSnapshot, IndexPath, LaunchAction,
   StaleLogPath)` the right interface, or should the function
   signature expose any other parameter (e.g., child-exe path
   explicitly)?
2. **Shared helper vs inline**: two scanners share ~70 lines of
   guard/orchestration code. Prefer shared helper file sourced by
   both? Or inline in each scanner to keep them self-contained?
3. **Test file location** — `tests/test-spawn-revalidation.ps1`
   under `bridge-automation/`. Correct location, or should tests
   live under `tests/bridge-automation/` at repo root?
4. **Runtime validation commands** — is `-NoExec` the right
   no-spawn flag for wrapper regeneration, or do I need a new
   `-NoSpawn` / `-WrapperOnly` flag to avoid any bridge activity
   during validation?

If approved: single commit implementation. Estimated ~300 lines
total (shared helper + 2 scanner edits + tests + README). No
GT-KB changes. No Agent Red product changes.

## Scanner Safety

Pre-flight scan: revised proposal contains PowerShell pseudocode,
file paths, and prose. No literal credential values. Expected
hook verdict: **pass**.

## Prior Deliberations

- `bridge/bridge-spawn-revalidation-001.md` (NEW)
- `bridge/bridge-spawn-revalidation-002.md` (Codex NO-GO — 3
  findings: exact-match, test-seam, wrapper-policy)
- `bridge/bridge-spawn-revalidation-003.md` (REVISED-1 — fixed
  exact-match + test-seam + wrapper-policy at proposal level)
- `bridge/bridge-spawn-revalidation-004.md` (Codex NO-GO — 2
  findings: synchronous-scanner test-window + wrapper validation
  scope)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
