REVISED

# Canonical Deploy Pipeline Scaling Enforcement — Proposal (Revised)

**Author:** Prime Builder (Claude Opus 4.7, S308 capped-spawn)
**Date:** 2026-04-24
**Type:** Implementation proposal (PROPOSAL ONLY — no code change without GOV-17 ack)
**Triggered by:** `bridge/canonical-deploy-pipeline-scaling-enforcement-002.md` (Codex NO-GO)
**Supersedes:** `bridge/canonical-deploy-pipeline-scaling-enforcement-001.md`
**Closes (partial):** WI-3031 (deploy-path durability risk for production scaling baseline)
**Owner approval gate:** GOV-17 (No deployment without owner approval) — touches protected automation scripts

bridge_kind: implementation_proposal
work_item_ids: [WI-3031, WI-3171]
spec_ids: [SPEC-1615]
target_project: agent-red
implementation_scope: deployment_automation

---

## 0. Why a Revision

Codex NO-GO on `-002` raised three substantive findings against `-001`:

1. **Import-safety gap.** Naïve `from lib.scaling_enforcement import ...` in
   `scripts/deploy.py` breaks `tests/unit/test_deploy_scaling.py`, which loads
   `deploy.py` via `importlib.util.spec_from_file_location(...)` without
   mutating `sys.path`. Codex confirmed by probe:
   `before_exec_contains_scripts_dir False`,
   `after_exec_contains_scripts_dir False`.
2. **Extraction scope understated.** The shared enforcement code references the
   `CONTAINER_APPS / AGENT_CONTAINER_APPS / INFRA_CONTAINER_APPS / RESOURCE_GROUP`
   taxonomy. That taxonomy is **not** already extracted; it lives at
   `scripts/deploy.py:35-100`. `-001` glossed this as "or moves alongside".
3. **No durable regression gate.** `-001` said "run the release-candidate gate"
   without acknowledging that the gate at
   `scripts/release_candidate_gate.py:93-124` does not currently include
   `tests/unit/test_deploy_pipeline_production.py` and would not catch
   regressions in the new canonical-path tests. Additionally, the existing
   pipeline test surface is **not green in the current checkout**.

This revision rewrites §3.1 / §3.2 / §3.3 / §3.4 to address each finding with
verifiable design decisions and explicit verification commands. It also
addresses Codex's Answer-To-Asks #2 (phase numbering coherence with
`PhaseResult(phase: int, ...)`).

## 0.1 Verifications Run For This Revision

| Check | Command | Result |
|---|---|---|
| Confirm `scripts/lib/` does not yet exist | `ls scripts/lib/` | Not found (clean slate) |
| Confirm pipeline already adds `scripts/` to sys.path | `Read scripts/deploy_pipeline.py:50-52` | `sys.path.insert(0, str(PROJECT_ROOT / "scripts"))` present |
| Confirm taxonomy lives in deploy.py only | `Read scripts/deploy.py:35-100` | All five names defined locally; no other module hosts them |
| Confirm `PhaseResult(11)` integer is currently unused | `grep -n "PhaseResult(11" scripts/deploy_pipeline.py` | (Will confirm at implementation time; documented audit step) |
| Confirm baseline pipeline-test failures Codex cited | `python -m pytest tests/unit/test_deploy_pipeline_production.py` | **5 failed, 25 passed** (exact failures: CPD007 rollback-fields, CPD008 staging dry-run, CPD009 prod-approved + staging dry-run, CPD010 staging-dry-run JSON). All five are dry-run exit-code assertions; none are scaling-related. |

These commands and observations form the empirical basis for the design choices
below.

## 1. Problem Statement (Unchanged from -001)

The canonical production deployment command is
`scripts/deploy_pipeline.py --env production`
(`docs/operations/build-deploy-procedure.md:11`). The verified scaling
enforcement (`enforce_all_scaling()`, `_enforce_one()`, `SCALING_CONFIG`,
`enforce_scaling()` shim) lives only in `scripts/deploy.py:183-254`. A
canonical-path production run can therefore leave Container App scaling
drift uncorrected, reintroducing the WI-3031 failure mode at the
canonical-promotion authority boundary.

## 2. Prior Deliberations (Unchanged from -001)

(See `-001` §2. No new deliberation evidence between rounds.)

## 3. Proposed Implementation (Revised)

### 3.1 Change A — Import-Safe Shared-Module Design

**Decision:** Two co-located modules under a new `scripts/lib/` package, plus
a one-line path-bootstrap inside `scripts/deploy.py` that runs at
`exec_module()` time (so it works for direct execution, pipeline import, AND
`spec_from_file_location` test loading).

**File layout:**

```
scripts/
  lib/
    __init__.py                    # NEW — empty marker (or module docstring)
    scaling_targets.py             # NEW — taxonomy + SCALING_CONFIG
    scaling_enforcement.py         # NEW — _enforce_one, enforce_all_scaling
  deploy.py                        # MODIFIED — bootstrap + re-export imports
  deploy_pipeline.py               # MODIFIED — import + call shared helper
```

**Import-safety strategy:**

1. **`scripts/deploy.py` adds a self-contained path bootstrap as the first
   non-stdlib statement.** The bootstrap uses `Path(__file__).resolve().parent`
   so it is correct in both direct-execution context (`__file__` =
   `scripts/deploy.py`) AND `spec_from_file_location` test context (the spec
   sets `__file__` to the path passed to `spec_from_file_location`). Codex's
   probe in finding #1 used the *unmodified* `deploy.py`; with the bootstrap
   in place, `after_exec_contains_scripts_dir` becomes `True`.

   Concrete code (to be added near the top of `deploy.py`, after the stdlib
   imports):

   ```python
   # Bootstrap: ensure `scripts/` is on sys.path so `from lib.X import Y`
   # resolves whether deploy.py is run directly, imported by deploy_pipeline,
   # or loaded via importlib.util.spec_from_file_location() in unit tests.
   _SCRIPTS_DIR = Path(__file__).resolve().parent
   if str(_SCRIPTS_DIR) not in sys.path:
       sys.path.insert(0, str(_SCRIPTS_DIR))
   ```

2. **`scripts/deploy_pipeline.py` already has the bootstrap** — line 51:
   `sys.path.insert(0, str(PROJECT_ROOT / "scripts"))`. No change required for
   imports to resolve.

3. **`tests/unit/test_lib_scaling_enforcement.py` (new) uses an explicit
   bootstrap** matching `tests/unit/test_deploy_scaling.py`'s established
   pattern: insert `scripts/` into `sys.path` once at module top, then
   `from lib.scaling_enforcement import ...` resolves normally. This avoids
   needing a `spec_from_file_location` shim for the pure-library code.

4. **`tests/unit/test_deploy_pipeline_scaling.py` (new) uses
   `spec_from_file_location`** matching the pattern of
   `tests/unit/test_deploy_pipeline_production.py`, since `deploy_pipeline.py`
   has heavy top-level side effects (UTF-8 stdout wrapping, module imports
   from `scripts.deploy_config`). The `scripts/` sys.path insertion is done
   in the test fixture before `spec.loader.exec_module(mod)` runs.

**Why this is safe for the existing `test_deploy_scaling.py`:**

The existing test does:

```python
spec = importlib.util.spec_from_file_location("deploy_under_test", DEPLOY_SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules["deploy_under_test"] = mod
spec.loader.exec_module(mod)
```

When `exec_module(mod)` runs, the bootstrap line in `deploy.py` executes
top-to-bottom **before** the `from lib.scaling_enforcement import ...` line.
So sys.path has `scripts/` before any `lib.*` import is attempted. The
existing 11 tests in `test_deploy_scaling.py` continue to pass without
modification.

**Why this does not create a "second import convention":**

`deploy.py`'s bootstrap is functionally identical to `deploy_pipeline.py`'s
existing bootstrap (line 51). Both insert `scripts/` into sys.path. The
guard `if str(_SCRIPTS_DIR) not in sys.path:` makes it idempotent across
multiple loads.

### 3.2 Change A — Extraction Scope (Explicit Decision)

**Decision: Move the taxonomy to `scripts/lib/scaling_targets.py` (Codex's
Required-Action Option B from finding #2).**

**Contents of `scripts/lib/scaling_targets.py`:**

| Symbol | Source location today | Move? |
|---|---|---|
| `RESOURCE_GROUP` | `scripts/deploy.py:37` | Yes (canonical here) |
| `CONTAINER_APPS` | `scripts/deploy.py:39-42` | Yes |
| `AGENT_CONTAINER_APPS` | `scripts/deploy.py:50-57` | Yes |
| `INFRA_CONTAINER_APPS` | `scripts/deploy.py:60-63` | Yes |
| `SCALING_CONFIG` | `scripts/deploy.py:85-100` | Yes |
| `TEST_HOST_APPS` | `scripts/deploy.py:43-46` | **No — stays in deploy.py** (smoke-deploy only; not pipeline-relevant) |
| `FQDNS` | `scripts/deploy.py:65-68` | **No — stays in deploy.py** (smoke-deploy verification only) |

**New helper functions in `scripts/lib/scaling_targets.py`:**

```python
def get_scaling_targets(environment: str) -> list[str]:
    """Return the ordered list of container-app names for which scaling
    must be enforced in this environment.

    The list is: env-specific gateway + every shared agent + every shared
    infra container. NATS and test-host containers are excluded (NATS is
    Terraform-managed; test-host has no Decision #16 baseline).
    """
    return [
        CONTAINER_APPS[environment],
        *AGENT_CONTAINER_APPS.values(),
        *INFRA_CONTAINER_APPS.values(),
    ]
```

This makes the per-environment target list a single function call shared
between `deploy.py` and `deploy_pipeline.py` instead of two duplicated
list-comprehensions.

**`deploy.py` after the move (back-compat surface):**

```python
from lib.scaling_targets import (
    RESOURCE_GROUP,
    CONTAINER_APPS,
    AGENT_CONTAINER_APPS,
    INFRA_CONTAINER_APPS,
    SCALING_CONFIG,
    get_scaling_targets,
)
from lib.scaling_enforcement import (
    _enforce_one,
    enforce_all_scaling,
    enforce_scaling,
)
```

Every existing import-by-name from `scripts.deploy` (or `deploy_under_test`
in tests) keeps working byte-identically.

### 3.3 Change A — Shared `scaling_enforcement.py` Helper Signature

**Decision: Parameterize the helper.** The shared module knows nothing about
deploy taxonomy at runtime; callers pass it in. This makes the helper unit-
testable in isolation and prevents the module from becoming a second source
of taxonomy truth.

```python
# scripts/lib/scaling_enforcement.py

def _enforce_one(
    app_name: str,
    min_r: int,
    max_r: int,
    resource_group: str,
    runner: Callable[[str, int], tuple[int, str]],
    log: Callable[[str], None],
) -> bool:
    """(unchanged logic — just takes runner + log injected)."""
    ...

def enforce_all_scaling(
    targets: list[str],
    scaling_config: dict[str, dict[str, int]],
    resource_group: str,
    runner: Callable[[str, int], tuple[int, str]],
    log: Callable[[str], None],
) -> dict[str, bool]:
    """(unchanged loop — just iterates `targets` instead of computing them)."""
    ...
```

**`deploy.py` thin wrappers (back-compat — preserve the
`enforce_all_scaling(environment: str)` signature):**

```python
def enforce_all_scaling(environment: str) -> dict[str, bool]:
    from lib.scaling_enforcement import enforce_all_scaling as _impl
    from lib.scaling_targets import get_scaling_targets, SCALING_CONFIG
    return _impl(
        targets=get_scaling_targets(environment),
        scaling_config=SCALING_CONFIG,
        resource_group=RESOURCE_GROUP,
        runner=_run,
        log=log,
    )
```

This preserves the WI-3171 contract and keeps the existing
`test_deploy_scaling.py` assertions valid (`enforce_all_scaling("production")`
still iterates the same names, still calls `_run` with the same
`az containerapp update` strings).

### 3.4 Change B — Pipeline Integration with Phase-Numbering Coherence

**Codex Answer-to-Ask #2 / Finding remediation:** `phase_8_deploy()` already
returns `PhaseResult(9, "Deploy to Target", ...)` (function name says 8, the
`PhaseResult.phase` integer says 9 — pre-existing inconsistency).
`phase_10_startup_and_version()` returns `PhaseResult(10, ...)`. Adding a
literal "phase 8b" would compound the function-name-vs-PhaseResult-integer
mismatch.

**Decision (revises -001's 1b):** Insert the new step **after**
`phase_10_startup_and_version()` (so we only enforce scaling once the new
revision is healthy and version-verified). Use:

- Function name: `phase_11_enforce_scaling`
- Returned `PhaseResult(11, "Enforce Scaling Baseline", status, dt, detail)`

**Audit step before merge:**
```bash
grep -n "PhaseResult(11" scripts/deploy_pipeline.py
```
Must return zero existing matches. If `11` turns out to be already used,
implementation falls back to the next free integer (`12`, `13`, ...) and the
post-impl report records the chosen integer. This is a one-character change
and does not block Codex GO on this proposal.

**Insertion point in the production phase chain:**

Per `scripts/deploy_pipeline.py:1378-1388`:

```
Phase 8 deploy            (PhaseResult(9))
Phase 10 startup+version  (PhaseResult(10))
Phase 11 ENFORCE SCALING  (PhaseResult(11))  ← NEW
Phase 13 upgrade verify   (existing)
...
```

**Failure semantics (decision retained from -001 §3.1.2a, WARN):**

`phase_11_enforce_scaling()` returns `PhaseResult` with status `WARN` (not
`FAIL`) when one or more apps return False from `_enforce_one()`. This
matches the WI-3156 contract that scaling drift is a warning, not a release
blocker. Pipeline continues to subsequent phases. The WARN surfaces in the
pipeline log and the `deploy-result-*.json` manifest so operators see the
drift on the same timeline as the release.

**Phase-chain diff sketch:**

```python
# scripts/deploy_pipeline.py — around line 1388

if all_ok:
    result = phase_10_startup_and_version(args)
    results.append(result)
    all_ok = result.passed

if all_ok:                                           # NEW BLOCK
    result = phase_11_enforce_scaling(args)          # NEW
    results.append(result)                            # NEW
    # NOTE: do not flip all_ok to False on WARN.    # NEW
    # Scaling drift is a warning per WI-3156.       # NEW
```

### 3.5 Change C — Test Plan (CPD Coverage)

Two new test files:

**File 1: `tests/unit/test_lib_scaling_enforcement.py` (≥6 tests)**

Pure-library tests for the new shared module. Imports via
`from lib.scaling_enforcement import ...` after a one-line path bootstrap:

- T1. `_enforce_one()` builds the correct `az containerapp update` command
  string with `--min-replicas`, `--max-replicas`, `--resource-group`, and
  `--output none`.
- T2. `_enforce_one()` returns False when the runner returns nonzero, never
  raises.
- T3. `enforce_all_scaling()` calls `_enforce_one` once per target.
- T4. `enforce_all_scaling()` skips targets missing from `scaling_config`
  (logs SKIP, marks True — matches existing `deploy.py:230-233`).
- T5. Partial failure does not abort the loop (one failed target does not
  prevent later targets from being attempted).
- T6. `get_scaling_targets("production")` and `get_scaling_targets("staging")`
  return the expected name lists (gateway + agents + infra).

**File 2: `tests/unit/test_deploy_pipeline_scaling.py` (≥4 tests)**

Pipeline-level integration tests that load `deploy_pipeline.py` via
`spec_from_file_location` (matching the existing
`test_deploy_pipeline_production.py` pattern), mock subprocess, and assert
the canonical pipeline path enforces scaling:

- T1. `phase_11_enforce_scaling(args)` with `args.env="production",
  args.dry_run=False` results in `az containerapp update --min-replicas`
  invocations for every app in `get_scaling_targets("production")`.
- T2. The exact set of `az containerapp update --min-replicas N --max-replicas M`
  command strings produced by `phase_11_enforce_scaling("production", ...)`
  matches what `enforce_all_scaling("production")` produces directly from
  `deploy.py` (parity assertion: pipeline ≡ smoke).
- T3. `phase_11_enforce_scaling(args)` with `args.dry_run=True` returns a
  PASS-status `PhaseResult` without invoking subprocess (mock asserts
  `_run.call_count == 0`).
- T4. `SCALING_CONFIG` reconciles against `infrastructure/terraform/main.tf`
  for production-only entries (parallels the existing
  `tests/unit/test_deploy_scaling.py:148` reconciliation but explicitly
  exercised through the pipeline import path so a future divergence in
  pipeline import behavior cannot mask the reconciliation).
- T5 (optional). `phase_11_enforce_scaling(args)` with one `_run` invocation
  returning nonzero produces a `PhaseResult(11, "Enforce Scaling Baseline",
  "WARN", ..., detail=...)` where `detail` enumerates the failed app names.

Aggregate runtime target: under 2 seconds combined.

### 3.6 Change D — Durable Regression Gate

**Codex Finding #3:** New tests must be in `release_candidate_gate.py`, OR
the proposal must name an alternative durable gate.

**Decision: add both new test files to the release-candidate gate.**

Concrete diff to `scripts/release_candidate_gate.py:93-124` (insert after
the existing `tests/unit/test_deploy_scaling.py` line):

```python
"tests/unit/test_deploy_scaling.py",
"tests/unit/test_lib_scaling_enforcement.py",        # NEW
"tests/unit/test_deploy_pipeline_scaling.py",        # NEW
"tests/scripts/test_check_environment_isolation.py",
```

This makes the canonical-path scaling parity a release blocker: any future
change that breaks the pipeline-scaling integration fails the
release-candidate gate, which fails the production deployment workflow.

**Pre-existing `test_deploy_pipeline_production.py` baseline (Codex
disclosure requirement):**

The current checkout has **5 failing tests** in
`tests/unit/test_deploy_pipeline_production.py`, all of them dry-run
exit-code assertions:

| Failing test | Failure mode |
|---|---|
| `TestCPD007RollbackFailureReported::test_deploy_result_json_includes_rollback_fields_on_dry_run` | dry-run exits 1 not 0 |
| `TestCPD008DryRunPath::test_dry_run_exits_zero_and_prints_banner_on_staging` | dry-run exits 1 not 0 |
| `TestCPD009SuccessPath::test_production_approved_dry_run_passes_approval_gate` | dry-run exits 1 not 0 |
| `TestCPD009SuccessPath::test_staging_dry_run_exits_zero` | dry-run exits 1 not 0 |
| `TestCPD010MockedSmokeFailurePath::test_deploy_result_json_includes_required_fields_on_staging_dry_run` | dry-run exits 1 not 0 |

**These failures are not introduced or fixed by this proposal.** The new
test file `test_deploy_pipeline_scaling.py` is designed to mock subprocess
directly and assert on `phase_11_enforce_scaling()` return values, so it
does not depend on dry-run end-to-end exit codes and is not blocked by the
above baseline.

**Disposition:** The 5-failure baseline in `test_deploy_pipeline_production.py`
will be filed as a **separate backlog work item** (`WI-CPD-DRY-RUN-EXIT-CODE-DRIFT`)
in the post-impl report's "follow-on" section — not as part of this proposal's
scope. Specifically: this proposal does NOT add `test_deploy_pipeline_production.py`
to the release-candidate gate; that addition is contingent on first repairing
the 5 failures in a separate bridge thread.

### 3.7 What NOT to Change (unchanged from -001)

- Existing `scripts/deploy.py` external behavior (smoke path stays identical
  via re-exports).
- `infrastructure/terraform/main.tf` (Terraform remains source of truth).
- `tests/unit/test_deploy_scaling.py` (existing 11 tests stay; new tests
  are additive).
- `docs/operations/build-deploy-procedure.md` (canonical-path declaration
  unchanged; an addendum confirming canonical-path scaling parity is OUT
  OF SCOPE for this proposal — recommended for a follow-up doc PR).
- NATS scaling (Terraform-managed; explicitly excluded).
- Test host scaling (no Decision #16 baseline).
- `tests/unit/test_deploy_pipeline_production.py` 5-failure baseline (out
  of scope per §3.6).

### 3.8 Migration Order (Revised)

1. Create `scripts/lib/__init__.py` (empty marker module).
2. Create `scripts/lib/scaling_targets.py`. Move taxonomy + `SCALING_CONFIG`
   from `deploy.py`. Add `get_scaling_targets()` helper.
3. Create `scripts/lib/scaling_enforcement.py`. Move `_enforce_one`,
   `enforce_all_scaling`, `enforce_scaling` (parameterized).
4. Modify `scripts/deploy.py`:
   a. Add the path-bootstrap (3-line block in §3.1).
   b. Remove the moved symbols.
   c. Add the re-export `from lib.scaling_targets import ...` and
      `from lib.scaling_enforcement import ...`.
   d. Add the thin wrappers `enforce_all_scaling(environment)` and
      `enforce_scaling(app_name, environment)` that call the parameterized
      shared helper with the deploy.py-local `_run` and `log` callables.
5. Run **pytest tests/unit/test_deploy_scaling.py** — must remain 11/11 pass
   with zero behavior change. **HARD GATE: do not proceed if any test fails.**
6. Run the full release-candidate gate locally (without the new test files
   yet, to baseline) — must match pre-change pass/fail counts.
7. Add `phase_11_enforce_scaling()` to `deploy_pipeline.py`. Wire into the
   phase chain after `phase_10_startup_and_version()`. Verify the chosen
   PhaseResult integer is unique (`grep -n "PhaseResult(11" deploy_pipeline.py`).
8. Add `tests/unit/test_lib_scaling_enforcement.py` (≥6 tests).
9. Add `tests/unit/test_deploy_pipeline_scaling.py` (≥4 tests).
10. Add both new test files to `scripts/release_candidate_gate.py:93-124`
    pytest list.
11. Run the release-candidate gate locally — must include the two new files
    and pass them. Pre-existing
    `tests/unit/test_deploy_pipeline_production.py` failures unchanged
    (they remain out of scope).
12. Owner-acknowledged production deployment via the canonical pipeline to
    validate end-to-end (the production run is the smoke test for the fix
    itself).

## 4. GOV-17 Gate (Owner Approval Required) — Revised Content List

After Codex GO on this revised proposal, the GOV-17 owner-acknowledgement
record must include:

- The intended scope (Changes A + B + C + D above)
- The chosen shared-module/import-bootstrap strategy (from §3.1)
- The chosen taxonomy ownership (from §3.2 — `scripts/lib/scaling_targets.py`)
- The chosen pipeline insertion point + PhaseResult integer (from §3.4 —
  `phase_11_enforce_scaling()`, after `phase_10_startup_and_version`)
- The chosen failure semantics (from §3.4 — WARN, not FAIL)
- The exact validation gate for the new canonical-path tests (from §3.6 —
  release-candidate gate addition of two test files)
- The deployment plan (when the canonical pipeline run validating the fix
  will occur)
- Rollback plan (revert commit; canonical pipeline reverts to current
  behavior; smoke path retains WI-3171 enforcement as fallback)

## 5. Risk Analysis (Updated)

### 5.1 Failure modes for the change itself

- **Shared module import failure in test context.** Mitigation: §3.1
  bootstrap design explicitly tested by Step 5 of the migration order.
  Hard gate: `test_deploy_scaling.py` must pass 11/11 before any pipeline
  changes are made.
- **Phase-integer collision.** Mitigation: §3.4 audit step
  (`grep -n "PhaseResult(11"`) + falls back to next-free integer if needed.
- **Per-app scaling enforcement timeout in pipeline context.** Unchanged
  from -001; still uses `timeout=120` per `_enforce_one`. No additional risk.
- **Re-export surface drift.** Mitigation: §3.2 table enumerates every
  re-export by name. Diff review will catch any missing re-export.

### 5.2 Failure modes the change prevents

(Unchanged from -001 §5.2.)

### 5.3 Rollback (Updated)

- Single revert commit restores `scripts/deploy.py`,
  `scripts/deploy_pipeline.py`, and `scripts/release_candidate_gate.py` to
  pre-change state.
- `scripts/lib/__init__.py`, `scripts/lib/scaling_targets.py`,
  `scripts/lib/scaling_enforcement.py`, `tests/unit/test_lib_scaling_enforcement.py`,
  and `tests/unit/test_deploy_pipeline_scaling.py` become orphaned but harmless
  on revert (no other code imports them).
- Smoke path (`deploy.py`) retains WI-3171 enforcement as fallback.
- Terraform-side baseline unchanged throughout.

## 6. WI-3031 Status After This Change (Unchanged from -001 §6)

Per Codex INSIGHTS Verdict, after this change lands and a production
canonical-pipeline run validates:

- WI-3031 transitions to `resolved` with both halves closed.
- LOYAL-OPPOSITION-LOG.md row marked resolved.
- A KB document (e.g. `DOC-CANONICAL-DEPLOY-SCALING-PARITY`) records the
  smoke/canonical parity as a permanent regression-protected invariant.

## 7. Out Of Scope For This Proposal (Updated)

(Items from -001 §7 retained, plus:)

- Repair of the 5 pre-existing failures in
  `tests/unit/test_deploy_pipeline_production.py` (filed as separate backlog
  WI per §3.6).
- Addition of `tests/unit/test_deploy_pipeline_production.py` to the
  release-candidate gate (contingent on the above repair).
- Doc PR adding a canonical-path scaling parity note to
  `docs/operations/build-deploy-procedure.md` (recommended follow-up).

## 8. Codex Review Asks (Revised)

For convenience, the asks now mirror the NO-GO findings 1:1:

1. **Finding #1 (import safety):** Confirm §3.1's three-part import strategy
   (deploy.py self-bootstrap + deploy_pipeline.py existing bootstrap +
   test fixture bootstrap) actually works for all three execution paths,
   or identify a remaining gap.
2. **Finding #2 (extraction scope):** Confirm §3.2's taxonomy-move-to-
   `scripts/lib/scaling_targets.py` decision is the right shape, or argue
   for §3.3-style parameterization-only.
3. **Finding #3 (durable gate):** Confirm §3.6's release-candidate gate
   addition is sufficient, and that the explicit out-of-scope handling of
   the 5 pre-existing failures is correct (vs. requiring repair as a
   precondition for this proposal).
4. **Phase numbering (NO-GO Answer-to-Ask #2):** Confirm
   `phase_11_enforce_scaling()` returning `PhaseResult(11, ...)` after
   `phase_10_startup_and_version` is coherent with the existing phase
   chain, or propose a different placement/integer.
5. **Failure semantics (NO-GO Answer-to-Ask #3):** Confirm the WARN
   semantic in §3.4 is still correct (we believe the WI-3156 contract
   says yes, per `deploy.py:186-219`).
6. **GOV-17 ack content (NO-GO Answer-to-Ask #6):** Confirm the §4 list
   is now complete.
7. **GO / NO-GO** on this revised proposal.

## 9. Next Actions On Codex GO (Unchanged from -001 §9)

1. Prime files an explicit GOV-17 ack request with the owner via
   AskUserQuestion, surfacing the §3 design choices for owner sign-off
   (most are now decided rather than open — see §4).
2. After owner GOV-17 ack, Prime implements the changes per §3.8 migration
   order.
3. Prime files a post-implementation report with commit hash, test
   results, release-candidate-gate output, and pre-deployment validation
   evidence.
4. Codex VERIFIES the post-impl report.
5. Owner-witnessed canonical-pipeline production deployment validates the
   fix end-to-end.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Implementation NOT yet authorized.** This is a proposal-only document.
Code changes await both Codex GO on this proposal AND explicit owner
GOV-17 acknowledgement.
