NEW

# Implementation Report - Cross-Harness Trigger Dispatch-State Lag (WI-3265)

bridge_kind: implementation_report
Document: gtkb-cross-harness-trigger-dispatch-state-lag
Version: 005
Responds to: bridge/gtkb-cross-harness-trigger-dispatch-state-lag-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S354

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3265

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

## Summary

Implements the diagnostic-only instrumentation approved by the GO at
`bridge/gtkb-cross-harness-trigger-dispatch-state-lag-004.md` (REVISED-1 at
`-003`). WI-3265 is rescoped to observation: the cross-harness trigger now
emits a structured JSONL diagnostic record per recipient per invocation to
`.gtkb-state/bridge-poller/trigger-diagnostic.jsonl`, classifying each
invocation outcome across the candidate failure modes. No dispatch semantics
changed. The behavior-changing lag fix remains deferred to a separate bridge
proposal once diagnostic evidence identifies the failure mode (proposal IP-3).

## In-Root Placement Evidence

All target paths and the runtime artifact are in-root under `E:\GT-KB`:
`scripts/cross_harness_bridge_trigger.py`,
`platform_tests/scripts/test_cross_harness_bridge_trigger.py`, and the runtime
log `.gtkb-state/bridge-poller/trigger-diagnostic.jsonl`. No `applications/`
paths; no paths outside `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`
satisfied.

## Specification Links

- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - cross-harness trigger is the active substrate.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge protocol; INDEX is canonical workflow state.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the diagnostic log is artifact-oriented evidence.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target paths and the runtime log are in-root.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - spec linkage carried forward from the GO'd proposal.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - spec-to-test mapping below; tests executed against the implementation.
- GOV-STANDING-BACKLOG-001 - WI-3265 is tracked in the standing backlog.
- DELIB-S350-BATCH3-DETERMINISTIC-SERVICES - owner-decision evidence for the batch containing WI-3265.
- DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08 - empirical foundation for the event-driven trigger.

## Prior Deliberations

- DELIB-S350-BATCH3-DETERMINISTIC-SERVICES - batch-3 authorization including WI-3265.
- DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08 - hook empirical foundation.
- bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md - active-session suppression contract; one of the classified failure modes.
- bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md - hook registration contract defining the invocation surface.
- bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-020.md - retirement of the interval-driven poller; the cross-harness trigger is the substrate this WI instruments.
- bridge/gtkb-cross-harness-trigger-dispatch-state-lag-002.md - the prior NO-GO; F1/F2/F3 closed in REVISED-1 (-003), which received GO at -004.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved the batch-3 deterministic-services authorization (DELIB-S350-BATCH3-DETERMINISTIC-SERVICES) which includes WI-3265, recorded in the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch3-deterministic-services-authorization.json` and surfaced as the active project authorization PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH.
- 2026-05-15 UTC, S354: owner directive to proceed with implementing approved (GO) bridge proposals and work independently. No new owner decision is required for this report; the diagnostic-only scope is wholly within the GO at -004 and introduces no new owner-decision surface.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. This report covers one work item (WI-3265), a member of
`PROJECT-GTKB-DETERMINISTIC-SERVICES-001` per the formal-artifact-approval
packet cited above. The change is single-thread diagnostic instrumentation
(IP-1 + IP-2); it performs no inventory sweep, no batch promotion, and no
multi-item standing-backlog mutation. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`
is not triggered.

## Implementation Summary

### IP-1 - Diagnostic instrumentation in scripts/cross_harness_bridge_trigger.py

- Added module constants: `TRIGGER_DIAGNOSTIC_FILENAME` (`trigger-diagnostic.jsonl`), `TRIGGER_DIAGNOSTIC_CLASSIFICATIONS` (the 6-value vocabulary), and `_LAST_RESULT_TO_DIAGNOSTIC_CLASSIFICATION` (maps existing per-recipient `last_result` outcomes to classifications).
- Added three helpers, all read-only / fire-and-forget, modeled on the existing `_record_dispatch_failure`:
  - `_path_mtime_iso(path)` - mtime as a UTC ISO string, None on error.
  - `_classify_invocation_outcome(last_result)` - maps `last_result` to a classification; unmapped results map to `other`.
  - `_emit_trigger_diagnostic(state_dir, record)` - appends one JSONL record; swallows `OSError` so instrumentation cannot perturb the fire-and-forget dispatch contract.
- `run_trigger` gained a keyword-only `invocation_source: str = "manual"` parameter (recorded in the diagnostic only; does not influence dispatch). At the start of the normal multi-harness dispatch path it captures `_diag_start`, `index_mtime`, `dispatch_state_mtime` (pre), and `index_signature_pre`. After `_write_dispatch_state` it emits one diagnostic record per recipient in `results`, with `index_signature_post` (re-read), `dispatch_state_mtime` (post), and `elapsed_ms`.
- `main()` passes `invocation_source="Stop"` under `--stop-hook`, else `"PostToolUse"`.
- Untouched per the GO guardrail: `_compute_actionable`, selected-batch signature generation, active-session suppression, dispatch target resolution, `_spawn_harness`. The instrumentation only records the outcomes of existing branches.

### IP-2 - Tests in platform_tests/scripts/test_cross_harness_bridge_trigger.py

Seven new tests plus a `_read_diagnostics` helper, one per the proposal's IP-2 table: `test_diagnostic_emitted_per_invocation`, `test_diagnostic_classifies_suppressed`, `test_diagnostic_classifies_dispatched`, `test_diagnostic_classifies_no_change`, `test_diagnostic_classifies_selected_batch`, `test_diagnostic_jsonl_parseable`, `test_dispatch_decision_unchanged_with_instrumentation`.

## Implementation Interpretation Note (for verification)

The GO'd schema (`-003` lines 78-94) is introduced as "Each invocation emits
one record" but is a flat dict with single per-recipient fields
(`classification`, `last_dispatched_signature`, `last_suppressed_signature`).
`run_trigger` processes TWO recipients per invocation (`prime-builder`,
`loyal-opposition`) with independent outcomes; a single flat record cannot
represent divergent recipient outcomes without discarding the per-recipient
classification that is the diagnostic purpose of WI-3265.

Implementation decision: emit ONE record PER RECIPIENT per invocation, each
carrying an added `recipient` discriminator field plus `last_result` (the raw
branch outcome the classification derives from). Invocation-level fields are
repeated in each record so each JSONL line is self-contained. The two
early-return paths (loop-prevention env var; single-harness topology skip) are
intentionally NOT instrumented: loop-prevention is the operator opt-out (must
no-op fully) and single-harness topology is outside the multi-harness lag the
WI investigates. `missed_stop_recovered` remains in the classification
vocabulary but is never emitted by this pass, because detecting a missed Stop
would require new behavior the -004 GO excludes from scope.

## Spec-to-Test Mapping

| Spec / behavior | Test |
|---|---|
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - diagnostic emitted on every invocation | test_diagnostic_emitted_per_invocation |
| Classification: active_session_suppressed | test_diagnostic_classifies_suppressed |
| Classification: dispatched | test_diagnostic_classifies_dispatched |
| Classification: no_change | test_diagnostic_classifies_no_change |
| Classification: selected_batch_skipped | test_diagnostic_classifies_selected_batch |
| JSONL parseable; full schema; vocabulary respected | test_diagnostic_jsonl_parseable |
| GO guardrail - dispatch decision unchanged by instrumentation | test_dispatch_decision_unchanged_with_instrumentation + all 19 pre-existing tests |

## Verification Evidence

Command: `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short`
Result: `26 passed in 1.49s` - 19 pre-existing tests (confirming dispatch behavior is unchanged) + 7 new WI-3265 tests.

Lint: `python -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py` reports exactly one B007 (unused loop variable `role`) at `test_cross_harness_bridge_trigger.py:1008`, inside the pre-existing `test_cross_harness_trigger_noop_in_single_harness_topology_records_audit_evidence` test. `git blame` attributes that line to commit `132fa1237` (2026-05-12), predating WI-3265; it was deliberately left unmodified to keep the commit scoped. All WI-3265-added code is ruff-clean.

Runtime artifact: `.gtkb-state/bridge-poller/trigger-diagnostic.jsonl` is created/appended at runtime and is NOT committed (runtime state under `.gtkb-state/`), per the -004 GO guardrail.

## Acceptance Criteria (from -003)

- IP-1 instrumentation landed; 7 tests PASS - MET.
- Existing dispatch behavior unchanged (regression suite passes) - MET (19/19 pre-existing tests pass).
- Diagnostic JSONL accumulates real-session data - the emission path is exercised by the 7 tests; live accumulation occurs once the trigger fires under normal session activity.
- No fix-related behavior change in this WI's scope - MET (only observational code added; no dispatch branch modified).

## Recommended Commit Type

`feat` - adds a new diagnostic instrumentation surface (~70 LOC trigger script + ~150 LOC tests). No behavior change, no spec promotion. Matches the proposal's own recommendation at `-003`.

## Risks / Rollback

- Risk: instrumentation I/O on every PostToolUse + Stop. Mitigation: one append (~400 bytes/record x 2 recipients) per invocation, fire-and-forget, OSError-swallowed; sub-millisecond.
- Risk: diagnostic log grows unbounded. Mitigation: the sibling thread `gtkb-dispatch-failures-jsonl-rotation` (GO) establishes the rotation pattern for `.gtkb-state/bridge-poller/*.jsonl`; a follow-on can extend rotation to `trigger-diagnostic.jsonl`.
- Rollback: revert the WI-3265 edits to the two target files (constants, three helpers, `run_trigger` instrumentation, `main()` argument, the 7 tests).

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
