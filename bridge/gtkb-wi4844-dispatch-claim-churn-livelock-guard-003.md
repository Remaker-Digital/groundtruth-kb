NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop Prime Builder session
author_metadata_source: explicit implementation report metadata

# GT-KB Bridge Implementation Report - gtkb-wi4844-dispatch-claim-churn-livelock-guard - 003

bridge_kind: implementation_report
Document: gtkb-wi4844-dispatch-claim-churn-livelock-guard
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4844-dispatch-claim-churn-livelock-guard-002.md
Approved proposal: bridge/gtkb-wi4844-dispatch-claim-churn-livelock-guard-001.md
Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4844
Recommended commit type: fix:

## Implementation Claim

Implemented the WI-4844 dispatch claim-churn guard for the daemon live-spawn path and aligned single-harness dispatch state with the existing cross-harness trigger behavior.

The daemon live path now filters Prime Builder selected entries through the canonical work-intent guard before any prompt/spawn decision, recomputes the dispatch signature after filtering, acquires Prime work intent before launching, annotates launches with the work-intent session/slugs, and releases acquired intent when a launch fails. Already-held Prime work is recorded as `work_intent_already_held` and is not passed to `_spawn_harness`.

The single-harness dispatcher now records held-filter telemetry and treats all-held Prime batches as suppressed rather than dispatched. This prevents a held/owner-active thread from stamping `last_dispatched_signature` and hiding future retries behind stale dedupe state.

The cross-harness trigger already had the core filter/acquire path; this slice adds an integration regression proving the trigger passes only unheld Prime items to `_spawn_harness`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required for this WI-4844 implementation. The owner already directed that dispatcher console storms are a release showstopper and that the project must continue until dispatcher release health is achieved.

## Prior Deliberations

- `bridge/gtkb-wi4844-dispatch-claim-churn-livelock-guard-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4844-dispatch-claim-churn-livelock-guard-002.md` - Loyal Opposition GO verdict authorizing implementation.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - project authorization context for harness parity phase 2 release-blocking work.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `test_daemon_live_spawns_filter_prime_work_intent_claims`, `test_single_harness_dispatcher_filters_held_prime_items_before_spawn`, and `test_run_trigger_filters_held_prime_items_before_spawn` prove daemon, single-harness, and trigger dispatch routes suppress held Prime work before worker spawn. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | The focused dispatcher suite verifies selected-entry envelopes still dispatch correctly and that filtered held items are excluded from worker item lists. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | Focused dispatcher regression suite, Ruff check, and Ruff format-check ran clean on the dispatcher implementation/test scope. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation authorization validated the protected target paths before mutation, and this report returns through the approved bridge thread. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The live defect, implementation, verification commands, residual release blocker, and next action are preserved in this bridge report. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target scripts\gtkb_dispatcher_daemon.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target scripts\single_harness_bridge_dispatcher.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target platform_tests\scripts\test_gtkb_dispatcher_daemon.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target platform_tests\scripts\test_single_harness_bridge_dispatcher.py`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target platform_tests\scripts\test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py::test_daemon_live_spawns_filter_prime_work_intent_claims platform_tests\scripts\test_single_harness_bridge_dispatcher.py::test_single_harness_dispatcher_honors_prime_work_intent_filter_project_guard platform_tests\scripts\test_single_harness_bridge_dispatcher.py::test_single_harness_dispatcher_filters_held_prime_items_before_spawn platform_tests\scripts\test_cross_harness_bridge_trigger.py::test_run_trigger_filters_held_prime_items_before_spawn -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\gtkb_dispatcher_daemon.py scripts\single_harness_bridge_dispatcher.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\gtkb_dispatcher_daemon.py scripts\single_harness_bridge_dispatcher.py scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_single_harness_bridge_dispatcher.py platform_tests\scripts\test_cross_harness_bridge_trigger.py`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch daemon status --json`
- `groundtruth-kb\.venv\Scripts\gt.exe bridge dispatch health --json`

## Observed Results

- Target authorization checks: all five mutated protected targets returned `"authorized": true`.
- Narrow regression selection: 4 tests passed in 5.73s.
- Focused dispatcher suite: 183 tests passed in 35.89s.
- Ruff check: `All checks passed!`.
- Ruff format check: `6 files already formatted`.
- Daemon status: active substrate is `cross_harness_trigger`, daemon mode is `shadow`, daemon is running, heartbeat is fresh, and PID provenance is verified.
- Dispatch health remains `WARN` due to a separate release blocker: WI-4885 is an unheld latest `NO-GO` that explicitly says "Hold for Owner Decision" but remains dispatchable to a headless Prime worker. The trigger spawned Codex for WI-4885 at `2026-06-29T12-22-39Z-prime-builder-A-253f6c`; Codex exited `4294967295`; the Prime circuit breaker is now tripped. This is not a WI-4844 duplicate-held-work failure: dispatch state shows `work_intent_held_filtered_count: 1` and selected only `gtkb-wi4885-dispatch-topology-activation`.

## Files Changed

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Operational State Notes

- `harness-state/bridge-substrate.json` is currently set to `cross_harness_trigger` as a release-safety quiesce from the earlier daemon storm diagnosis. That operational state is not claimed as a WI-4844 source-code change.
- Do not re-enable daemon live spawning until the WI-4885 owner-hold dispatchability blocker is fixed or WI-4885 is otherwise made non-dispatchable through governed state.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Rationale: the change fixes a dispatcher reliability defect that could spawn duplicate Prime workers for already-claimed bridge work.

## Acceptance Criteria Status

- [x] Daemon live path filters Prime selected entries against work-intent claims before spawning.
- [x] Daemon live path acquires Prime work intent before launch and releases acquired intent on launch failure.
- [x] Daemon live path recomputes the dispatch signature after held-work filtering.
- [x] Single-harness dispatcher records all-held Prime batches as suppressed, not dispatched.
- [x] Cross-harness trigger integration coverage proves only unheld Prime items reach `_spawn_harness`.
- [x] Focused dispatcher tests, Ruff check, and Ruff format-check pass.
- [ ] Full dispatcher release health is not yet achieved because WI-4885 owner-hold NO-GO dispatchability remains a separate showstopper.

## Risk And Rollback

Rollback is limited to reverting the five WI-4844 code/test paths listed above. The bridge report and verdict files remain append-only. The main residual risk is not this fix but the newly isolated WI-4885 behavior: owner-held NO-GO entries need a deterministic non-dispatchable/suppressed state so headless Prime workers are not repeatedly launched for work requiring an interactive owner decision.

## Loyal Opposition Asks

1. Verify that the daemon, trigger, and single-harness dispatcher now consistently suppress already-held Prime work before worker spawn.
2. Verify the focused dispatcher test, Ruff check, and format-check evidence.
3. Treat WI-4885 owner-hold dispatchability as a separate release blocker rather than a failure of this WI-4844 implementation.
