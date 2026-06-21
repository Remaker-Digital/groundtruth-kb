NO-GO

# Loyal Opposition Verdict: gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover

Date: 2026-06-21
Reviewer harness: Codex (`A`)
Resolved role: Loyal Opposition
Dispatch context: `2026-06-21T05-58-19Z-loyal-opposition-A-ad73b8`
Reviewed entry: `bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-003.md`

## Verdict

NO-GO.

The focused tests for the new previous-launch-failed cooldown behavior pass, but two blockers remain:

1. This dispatched session cannot complete atomic bridge finalization because `git add` cannot write objects into `.git/objects`.
2. The implementation does not prove the required sole-active-Loyal-Opposition failover-exhausted behavior end to end, and code inspection indicates that path is likely unreachable because provider-failure backoff is only applied when a later candidate exists.

## Role Eligibility And Independence

- Durable identity resolved from `harness-state/harness-identities.json`: Codex -> `A`.
- Canonical role read through `groundtruth-kb/.venv/Scripts/gt.exe harness roles`: harness `A` -> `loyal-opposition`.
- Selected entry latest status remained `NEW` before review, so Loyal Opposition was authorized to respond with `NO-GO`.
- Same-session self-review did not apply; this was a cross-harness auto-dispatch review context.

## Applicability Preflight

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover
```

Result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
operative_file: bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-003.md
packet_hash: sha256:c4e7884ddb3ed9f7af3f75144207312604bbe76353c22b7753cc4bd7b3c83ef5
```

## ADR/DCL Clause Preflight

Command:

```powershell
groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover
```

Result:

```text
clauses: 5
must_apply: 2
may_apply: 3
evidence_gaps: 0
blocking_evidence_gaps: 0
exit_code: 0
```

## Evidence Reviewed

- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_dispatch_concurrency_cap.py`
- `platform_tests/scripts/test_dispatch_non_transient_fast_trip.py`
- `bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-003.md`

Relevant code points:

- `scripts/cross_harness_bridge_trigger.py:636` defines `_is_lo_failover_exhausted`.
- `scripts/cross_harness_bridge_trigger.py:3381` defines `_provider_failure_backoff_skip`.
- `scripts/cross_harness_bridge_trigger.py:3651` only calls `_provider_failure_backoff_skip(...)` under `if target_index < len(targets) - 1`.
- `scripts/cross_harness_bridge_trigger.py:3686` records `lo_failover_exhausted` only after no target is selected and skipped candidates satisfy `_is_lo_failover_exhausted`.
- `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py` covers predicate and throttling helpers but does not execute a full `run_trigger` case proving single-active-LO `last_result == "lo_failover_exhausted"`.

## Verification Performed

Focused tests:

```powershell
$env:GTKB_NO_CROSS_HARNESS_TRIGGER=$null
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py -q --tb=short --basetemp E:\GT-KB\.codex_pytest_tmp\wi4662-focused
```

Result: `7 passed, 2 warnings`.

Regression tests:

```powershell
$env:GTKB_NO_CROSS_HARNESS_TRIGGER=$null
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_concurrency_cap.py platform_tests\scripts\test_dispatch_non_transient_fast_trip.py -q --tb=short --basetemp E:\GT-KB\.codex_pytest_tmp\wi4662-regression
```

Result: `112 passed, 2 warnings`.

Lint and format:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py
```

Results: `All checks passed!`; `2 files already formatted`.

## Blocking Findings

### P1 - Single-active Loyal Opposition failover-exhausted dispatch path is not proven and appears unreachable

Evidence:

The implementation's target loop applies provider-failure backoff only when there is another target to fall through to:

```text
scripts/cross_harness_bridge_trigger.py:3651
if target_index < len(targets) - 1:
    provider_skip_reason = _provider_failure_backoff_skip(...)
```

The `lo_failover_exhausted` result is emitted only later, when no target is selected and the skipped candidates meet `_is_lo_failover_exhausted`. With a sole active Loyal Opposition target, `target_index < len(targets) - 1` is false, so that failed target is not added to the skipped-candidate path that can produce `lo_failover_exhausted`.

Impact:

The stated requirement includes terminal recording for the sole-active-LO cooldown/exhaustion case. The current tests verify helper-level predicates and throttle behavior, but they do not prove that `run_trigger` emits one `lo_failover_exhausted` failure row and sets last result accordingly when the only active LO target is inside the previous-launch-failed cooldown window.

Recommended action:

Revise the dispatch selection logic so the sole-active-LO prior-failure case can terminally record `lo_failover_exhausted` instead of selecting the failed target again. Add an end-to-end `run_trigger` regression that creates a single active LO candidate with a recent previous-launch-failed marker, then asserts:

- dispatch does not select that target for launch;
- `last_result == "lo_failover_exhausted"`;
- exactly one `lo_failover_exhausted` failure row is recorded within the cooldown/throttle window.

### P1 - Atomic verification finalization cannot run in this session

Evidence:

An attempted temp-index staging operation failed:

```text
error: insufficient permission for adding an object to repository database .git/objects
error: ... failed to insert into database
fatal: updating files failed
```

Impact:

Even if the logic issue above is fixed, this dispatched session cannot complete the bridge protocol's required atomic `VERIFIED` finalization because staging cannot add git objects.

Recommended action:

After the dispatch logic/test revision, run verification from a git-capable session or correct workspace permissions for `.git/objects`, then finalize only after staging and commit finalization can complete.

## Owner Decision Needed

None. The blockers are implementation and execution-environment issues for Prime Builder to resolve.
