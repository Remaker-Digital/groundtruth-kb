REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-21T23-08-23Z-prime-builder-A-ad913d
author_model: gpt-5
author_model_version: Codex GPT-5
author_model_configuration: cross-harness bridge auto-dispatch

# Revised implementation report: WI-4662 previous-launch-failed cooldown + LO failover exhaustion

bridge_kind: implementation_report
Document: gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover
Version: 005 (REVISED)
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4662

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

This report responds to `bridge/gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover-004.md` (NO-GO).

The original WI-4662 implementation was committed in `32d7d61ce` / `41d761437`. The NO-GO correctly identified that the first report did not prove the sole-active Loyal Opposition exhaustion path end to end. The current HEAD includes the follow-up correction commit:

- `41d761437` - removed the prior last-candidate guard so provider-failure backoff runs before target selection and a sole active Loyal Opposition target can enter the exhausted path.
- `1c5b1855f` - distinguished temporary retry-delay backoff from terminal non-retryable LO failover exhaustion, preserving the existing `retry_delay_enforced` behavior while retaining the terminal `lo_failover_exhausted` path for non-retryable previous-launch failures.

The target paths are clean relative to `HEAD` after these commits; no unrelated worktree changes are included in this report.

## Specification Links

- `GOV-AUTOMATION-VALUE-VS-COST-001` - bounds noisy `previous_launch_failed` re-logging and avoids repeated expensive dispatch attempts.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs status-bearing bridge files and role authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal/report cites relevant specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and Work Item metadata are present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked behavior to executed tests.
- `GOV-STANDING-BACKLOG-001` - WI-4662 is the governed backlog work item.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all active paths are under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - bridge report preserves durable review/verification evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation evidence is carried through the bridge artifact workflow.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - NO-GO correction is captured as a revised bridge artifact.

## Owner Decisions / Input

- This work remains covered by project authorization `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-COMPLIANCE-DISPATCH-BATCH-002` for `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` / `WI-4662` (`DELIB-20265459`, AUQ 2026-06-21).
- No new owner decision was required for this NO-GO correction. The dispatched Prime Builder worker could proceed under the existing GO and implementation-start authorization packet `sha256:96e9b6c9226152a23a4bd6fd2300c0c4cde11a74917d6914e82f2c42e894626b`.

## Prior Deliberations

- `DELIB-20265484` - Loyal Opposition GO verdict for WI-4662.
- `DELIB-20265459` - project authorization for the bridge-tooling/dispatch reliability defect batch including WI-4662.
- `bridge/gtkb-lo-dispatch-ordered-fallback-routing-001.md` .. `-008.md` (VERIFIED, WI-4484) - ordered LO failover behavior preserved by the adjacent regression suite.
- `bridge/gtkb-wi4703-dispatch-non-transient-fast-trip-*` - fast-trip breaker work preserved by `test_dispatch_non_transient_fast_trip.py`.

## Findings Addressed

### P1 - Single-active Loyal Opposition failover-exhausted dispatch path is not proven and appears unreachable

Resolution:

- `41d761437` moved provider-failure backoff evaluation ahead of candidate selection for every ranked target, including the sole/last active Loyal Opposition target. This makes the `lo_failover_exhausted` result reachable when all LO candidates are skipped for terminal prior-launch failure reasons.
- `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py::test_sole_active_lo_in_backoff_produces_lo_failover_exhausted_end_to_end` now drives `run_trigger` end to end with one active LO candidate, pre-seeded non-retryable prior failure state, and a live NEW bridge entry. It asserts no launch, `last_result == "lo_failover_exhausted"`, result reason `lo_failover_exhausted`, and exactly one `lo_failover_exhausted` row in the failure log.
- `1c5b1855f` corrected an adjacent compatibility regression found during this dispatch: ordinary retry-delay backoff is a temporary hold and now remains `retry_delay_enforced`; only non-retryable previous-launch failures become terminal `lo_failover_exhausted`.

### P1 - Atomic verification finalization cannot run in the previous Loyal Opposition session

Resolution:

- This Prime Builder report does not claim `VERIFIED` and does not attempt Loyal Opposition commit finalization.
- The implementation changes are present in current `HEAD` at `41d761437` and `1c5b1855f`; the target source/test paths are clean relative to `HEAD`.
- Loyal Opposition must still perform the mandatory `VERIFIED` finalization helper path if this revised report passes review. The prior `.git/objects` write failure was an execution-environment blocker for that LO verdict session, not a remaining Prime Builder implementation decision.

## Specification-Derived Verification

Commands run from `E:\GT-KB` with `GTKB_NO_CROSS_HARNESS_TRIGGER` cleared for pytest commands:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py -q --tb=short --basetemp E:\GT-KB\.codex_pytest_tmp\wi4662-focused-pb-final
```

Result: `9 passed, 2 warnings`.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_concurrency_cap.py platform_tests\scripts\test_dispatch_non_transient_fast_trip.py -q --tb=short --basetemp E:\GT-KB\.codex_pytest_tmp\wi4662-regression-pb-final
```

Result: `112 passed, 2 warnings`.

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py
```

Result: `All checks passed!`

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\cross_harness_bridge_trigger.py platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py
```

Result: `2 files already formatted`.

Spec-to-test mapping:

| Specification / behavior | Test or command | Result |
| --- | --- | --- |
| `GOV-AUTOMATION-VALUE-VS-COST-001` - repeated `previous_launch_failed` durable re-log is cooldown-gated | `test_backoff_skip_throttles_relog_and_keeps_annotation` | PASS |
| Re-log resumes after cooldown elapses | `test_backoff_skip_throttles_relog_and_keeps_annotation`, `test_should_relog_respects_cooldown_window` | PASS |
| In-memory `previous_launch_failed` annotation remains visible every cycle | `test_backoff_skip_throttles_relog_and_keeps_annotation` | PASS |
| Recovery clears cooldown stamp and annotation | `test_recovery_clears_previous_launch_failed_stamp` | PASS |
| Sole active LO non-retryable prior failure records bounded terminal exhaustion end to end | `test_sole_active_lo_in_backoff_produces_lo_failover_exhausted_end_to_end` | PASS |
| Temporary retry-delay backoff remains a retry delay, not terminal exhaustion | `test_lo_provider_backoff_hold_reason_preserves_retry_delay`; `test_failed_launch_exit_processing_clears_dispatch_dedupe_signals` in adjacent regression suite | PASS |
| WI-4484 ordered fallback and adjacent dispatch behavior remain intact | `test_cross_harness_bridge_trigger.py`, `test_dispatch_concurrency_cap.py`, `test_dispatch_non_transient_fast_trip.py` | PASS |
| Python lint and formatting gates | `ruff check`, `ruff format --check` on changed target files | PASS |

## Pre-Filing Preflight Subsection

Before live filing, this completed candidate is filed through `.codex/skills/bridge/helpers/revise_bridge.py file`, which runs:

- `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover --content-file <candidate> --json`
- `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4662-dispatch-previous-launch-failed-cooldown-failover --content-file <candidate>`

Expected result: candidate preflights pass with no missing required specifications and no blocking ADR/DCL evidence gaps. The helper refuses live publication on preflight failure.

## Risk And Rollback

- Risk: classifying provider backoff too broadly as terminal can mask ordinary retry-delay behavior. Mitigation: `1c5b1855f` narrows `lo_failover_exhausted` to non-retryable previous-launch failures and preserves `retry_delay_enforced`; both the focused WI-4662 test and the adjacent WI-4679 regression now cover this boundary.
- Risk: current target changes are already in `HEAD`, so Loyal Opposition finalization must verify implementation commits plus this revised report rather than expecting dirty source files in the worktree. Mitigation: this report cites implementation commits explicitly and the target paths are clean relative to `HEAD`.
- Rollback: revert `41d761437` and `1c5b1855f` if the revised LO verification finds the behavior invalid; both commits are confined to the approved source/test target paths.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py` - cooldown-gated previous-launch-failed re-log, provider backoff before candidate selection, terminal/non-terminal LO exhaustion split.
- `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py` - focused unit and end-to-end tests for cooldown, terminal LO exhaustion, and retry-delay preservation.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
