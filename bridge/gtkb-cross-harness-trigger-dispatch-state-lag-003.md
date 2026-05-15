REVISED

# Implementation Proposal - Cross-Harness Trigger Dispatch-State Lag - REVISED-1 (WI-3265)

bridge_kind: implementation_proposal
Document: gtkb-cross-harness-trigger-dispatch-state-lag
Version: 003
Responds to: bridge/gtkb-cross-harness-trigger-dispatch-state-lag-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3265

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-002.md`:

- **F1 (P1)** — Proposed fix was not derived from the current trigger state machine; conflated stale-INDEX-read with suppressed/retryable, selected-batch, and missed-Stop states → **closed** by rescoping this WI to **diagnostic-only** (instrumentation, no behavior change). A separate fix proposal lands later once diagnostic data identifies the actual failure mode.
- **F2 (P1)** — Verification command targeted non-existent `tests/scripts/` tree → **closed** with correct path `platform_tests/scripts/test_cross_harness_bridge_trigger.py`.
- **F3 (P2)** — Prior cross-harness trigger deliberations under-cited → **closed** with explicit citations.

## Claim

Rescope WI-3265 to **diagnostic instrumentation only**. The fix is deferred to a follow-on bridge once the diagnostic evidence identifies whether the lag is stale-INDEX, active-session-suppression, selected-batch-signature, or missed-child-Stop. Add structured logging to `cross_harness_bridge_trigger.py` that captures each invocation's classification across the 4 candidate failure modes.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the active substrate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - diagnostic is artifact-oriented evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3265 tracked.
- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner-decision evidence.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - empirical foundation; cited per F3.

## Prior Deliberations (F3 closure)

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - batch-3 authorization.
- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` - hook empirical foundation.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-*` - retirement of interval-driven poller; the cross-harness trigger is the substrate this WI investigates.
- `bridge/gtkb-cross-harness-trigger-active-session-suppression-001-008.md` - active-session suppression contract; one of the 4 candidate failure modes.
- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md` - hook registrations defining the trigger's invocation contract.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved batch-3 authorization including WI-3265.
- 2026-05-15 UTC, S350+: owner directive "keep grinding REVISED-1s through the NO-GO queue".

No new owner decision required. Rescoping to diagnostic-only narrows scope, doesn't expand it.

## Requirement Sufficiency

Existing requirements sufficient. WI-3265 description ("dispatch-state refresh lag") becomes "instrument the trigger to identify which of 4 candidate failure modes is responsible". A fix proposal lands separately after diagnostic evidence arrives.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI (WI-3265); member of PROJECT-GTKB-DETERMINISTIC-SERVICES-001 per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch3-deterministic-services-authorization.json`. Review-packet inventory: IP-1 (diagnostic instrumentation) + IP-2 (tests) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-003.md`; `REVISED:` line prepended; prior `NO-GO: -002` and `NEW: -001` preserved.

## Proposed Scope (rescoped — diagnostic only)

### IP-1: Diagnostic instrumentation in cross_harness_bridge_trigger.py

In `scripts/cross_harness_bridge_trigger.py`, add structured JSONL diagnostic logging to `.gtkb-state/bridge-poller/trigger-diagnostic.jsonl`. Each invocation emits one record:

```python
{
  "timestamp": "<utc-iso>",
  "invocation_source": "<PostToolUse|Stop|manual>",
  "pid": <int>,
  "session_id": "<string>",
  "index_mtime": "<utc-iso>",
  "index_signature_pre": "<hash>",
  "index_signature_post": "<hash>",
  "dispatch_state_mtime_pre": "<utc-iso>",
  "dispatch_state_mtime_post": "<utc-iso>",
  "classification": "<one of: active_session_suppressed | dispatched | no_change | selected_batch_skipped | missed_stop_recovered | other>",
  "last_dispatched_signature": "<hash-or-null>",
  "last_suppressed_signature": "<hash-or-null>",
  "elapsed_ms": <int>
}
```

The `classification` field maps the invocation to one of the 4 candidate failure modes plus the normal cases:

- `active_session_suppressed` — counterpart is active; suppression recorded
- `dispatched` — actionable change detected; counterpart spawned
- `no_change` — no signature change; idle pass
- `selected_batch_skipped` — index has actionable work but selected-batch state filtered it
- `missed_stop_recovered` — diagnostic detected a previously-missed Stop event

**No behavior change.** This WI does not modify dispatch semantics; it observes them.

### IP-2: Tests

In `platform_tests/scripts/test_cross_harness_bridge_trigger.py` (existing test file), add diagnostic-instrumentation tests:

| Behavior | Test |
|---|---|
| Diagnostic JSONL emitted on every invocation | `test_diagnostic_emitted_per_invocation` |
| Classification: active_session_suppressed | `test_diagnostic_classifies_suppressed` |
| Classification: dispatched | `test_diagnostic_classifies_dispatched` |
| Classification: no_change | `test_diagnostic_classifies_no_change` |
| Classification: selected_batch_skipped | `test_diagnostic_classifies_selected_batch` |
| JSONL parseable | `test_diagnostic_jsonl_parseable` |
| Instrumentation does not change dispatch decision | `test_dispatch_decision_unchanged_with_instrumentation` |

Test execution: `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -v`.

### IP-3: Follow-on (NOT in this WI's scope)

After diagnostic evidence accumulates (target: 7 days of observation across normal session activity), file a SEPARATE bridge proposal scoped to the identified failure mode. This WI's `resolution_status` transitions to `verified` after diagnostic instrumentation is operational; the fix is tracked separately.

## Specification-Derived Verification Plan

Tests above directly map: each classification case tests both the diagnostic emission and the non-mutation of dispatch behavior.

## Acceptance Criteria

- IP-1 instrumentation landed; 7 tests PASS.
- IP-2: existing dispatch behavior unchanged (regression suite passes).
- Diagnostic JSONL file accumulates real-session data; manual inspection after 24 hours surfaces classification distribution.
- Both preflights PASS.
- No fix-related behavior change in this WI's scope.

## Risks / Rollback

- Risk: instrumentation adds I/O on every PostToolUse + Stop. Mitigation: JSONL append-only, single write per invocation (~200 bytes); under 1ms.
- Risk: diagnostic log grows unbounded. Mitigation: log rotation tracked separately (sibling bridge `gtkb-dispatch-failures-jsonl-rotation` is GO; same rotation pattern applies).
- Rollback: revert IP-1 diagnostic-emission lines.

## Recommended Commit Type

`feat` - diagnostic instrumentation; ~50 LOC trigger + ~80 LOC tests. No behavior change; no spec promotion.
