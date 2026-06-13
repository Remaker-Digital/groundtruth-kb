# WI-4526 cross-harness trigger state-only path audit

Date: 2026-06-13
Role: Loyal Opposition
Harness: Codex A
Work item: WI-4526

## Claim

The live `cross_harness_bridge_trigger.py` implementation already orders both `--reset-recipient` and `--diagnose` as state-only/manual CLI paths before the normal trigger dispatch path. The remaining risk for WI-4526 is not an observed current-code defect in that ordering; it is unresolved backlog disposition and missing direct regression coverage for `--reset-recipient`.

## Evidence

- Durable role check: `harness-state/harness-identities.json` maps Codex to harness ID `A`, and `python -m groundtruth_kb.cli harness roles` reports harness `A` as `loyal-opposition`.
- Bridge queue check: `python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json` reported no Loyal Opposition-actionable entries. Latest bridge states in the scan were `ADVISORY`, `GO`, `VERIFIED`, and `WITHDRAWN`; no latest `NEW` or `REVISED` entries were selected.
- Live bridge-dispatch diagnose check: `python scripts\cross_harness_bridge_trigger.py --diagnose --project-root E:\GT-KB` returned a diagnose summary instead of launching dispatch work. It reported the current dispatch state as degraded because some recipients have stale/no state, but it completed as a manual diagnostic path.
- Code ordering: `scripts/cross_harness_bridge_trigger.py` enters `main()` at line 3694, resolves `state_dir` at lines 3698-3703, handles `--reset-recipient` at lines 3716-3740, handles `--diagnose` at lines 3742-3744, and only reaches `run_trigger(...)` afterward at line 3748.
- Targeted repo-native verification passed:

```powershell
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_diagnose_reports_current_role_recipient_keys_and_single_harness_as_inert platform_tests\scripts\test_cross_harness_bridge_trigger_diagnose.py::test_diagnose_does_not_dispatch_or_modify_state platform_tests\scripts\test_single_harness_bridge_dispatcher.py::test_dispatcher_diagnose_emits_liveness_summary -q --tb=short
```

Result: `3 passed`.

- A direct reset-recipient regression test was attempted but blocked by the implementation-start gate:

```text
BLOCKED (GTKB-IMPLEMENTATION-START-GATE): PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
```

The blocked edit targeted `platform_tests/scripts/test_cross_harness_bridge_trigger.py` and would have asserted that `--reset-recipient loyal-opposition` clears recipient failure/circuit-breaker fields without calling `run_trigger(...)`.

## Risk / impact

If WI-4526 remains open without a Prime disposition, future work may duplicate a repair that appears already present in live code. If the missing reset-recipient regression remains untracked, a later refactor could accidentally move reset handling back behind the dispatch path and revive the original manual CLI wedge.

## Recommended action

Prime Builder should choose one of these paths:

1. Close or update WI-4526 with evidence that the state-only ordering is already implemented, if this code state satisfies the work item.
2. Open a bridge proposal or attach the required authorization packet for a test-only regression update.

Recommended test shape for path 2:

- In `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, add a test such as `test_reset_recipient_is_state_only_and_does_not_dispatch`.
- Seed `.gtkb-state/bridge-poller/dispatch-state.json` with a recipient entry containing nonzero `failure_count` and `circuit_breaker_tripped: true`.
- Monkeypatch `run_trigger` to fail if called.
- Call `trigger.main(["--project-root", str(project_root), "--reset-recipient", "loyal-opposition"])`.
- Assert return code `0`, reset output is printed, `failure_count` is `0`, `circuit_breaker_tripped` is `false`, and dispatch was not invoked.

## Decision needed from owner

None at this time. This is a Prime Builder/backlog disposition issue unless Prime chooses to request owner approval for broader implementation work.
