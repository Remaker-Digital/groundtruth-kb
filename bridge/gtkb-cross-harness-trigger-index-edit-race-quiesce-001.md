NEW

# Implementation Proposal - Cross-Harness Trigger INDEX Edit Race + Quiesce Window (WI-3280)

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-index-edit-race-quiesce
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-3280

target_paths: ["scripts/cross_harness_bridge_trigger.py", "tests/scripts/test_cross_harness_bridge_trigger.py"]

This NEW proposal adds a quiesce window to the cross-harness trigger to prevent the INDEX edit race observed in S341+S342: Prime writes a bridge document, trigger fires on the Write, Codex updates INDEX before Prime's Edit lands, Prime's Edit fails with "File has been modified since read". Observed multiple times during this S350 session as well.

## Claim

Add a configurable quiesce window (default 5 seconds) between PostToolUse trigger detection and counterpart-harness spawn. During the window, the trigger ignores additional INDEX changes from the same session; this gives Prime time to complete its bridge proposal + INDEX update sequence atomically.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - cross-harness trigger is the active substrate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` - dispatch-on-actionable-change semantic (preserved; quiesce only delays, doesn't drop).
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3280 tracked.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-BRIDGE-PROTOCOL-RELIABILITY authorization including this WI.

## Requirement Sufficiency

Existing requirements sufficient. WI-3280 description specifies the race + 3 enhancement options.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended.

## Proposed Scope

### IP-1: Quiesce window in cross-harness trigger

In `scripts/cross_harness_bridge_trigger.py`:

1. Add `QUIESCE_WINDOW_SECONDS = 5` constant (configurable via env var `GTKB_TRIGGER_QUIESCE_SECONDS`).
2. On PostToolUse invocation, before computing actionable signature change:
   - Read `.gtkb-state/bridge-poller/last-fire.json` (if exists).
   - If `last_fire_at + QUIESCE_WINDOW_SECONDS > now`, skip the spawn but DO update last_fire_at + scheduled_recheck_at.
   - Track scheduled_recheck_at; on next invocation past that timestamp, re-evaluate.
3. After spawn (or skip), write `last_fire_at = now, scheduled_recheck_at = now + QUIESCE_WINDOW_SECONDS`.

Semantics: same session's rapid INDEX changes get batched; the trigger eventually fires after the session quiesces, ensuring a single counterpart dispatch covers the full edit batch.

### IP-2: Tests

Tests verify: rapid edits coalesce, single dispatch after quiesce window, dispatch fires on actual idle state, env var override works.

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Rapid edits coalesce within quiesce | `test_rapid_edits_coalesce_into_single_dispatch` |
| Single dispatch fires after quiesce expires | `test_dispatch_after_quiesce_expires` |
| Env var override changes window | `test_env_var_override_quiesce_seconds` |
| First edit (no prior fire) immediate-dispatch | `test_first_edit_no_quiesce_delay` |
| Quiesce preserves actionable-signature semantic | `test_quiesce_preserves_signature_change_detection` |
| State file written/read correctly | `test_state_file_round_trip` |
| Quiesce respected across separate process invocations | `test_quiesce_across_invocations` |

Run: `python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py -v`.

## Acceptance Criteria

- IP-1, IP-2 landed; 7 tests PASS.
- Both preflights PASS.
- Real-world verification: bridge filing + INDEX edit no longer races during this session's typical pattern.

## Risks / Rollback

- Risk: 5-second quiesce adds latency to dispatch; counterpart Codex review takes longer to start. Mitigation: 5s is sub-perception relative to Codex's ~20-40min review latency; user impact negligible.
- Risk: quiesce state file race between multiple Prime sessions. Mitigation: file-level atomic write (write-temp + rename); per-session-id key in JSON.
- Rollback: revert IP-1 single-function-scope change.

## Recommended Commit Type

`feat` - reliability enhancement; addresses observed friction. ~60 LOC + tests.
