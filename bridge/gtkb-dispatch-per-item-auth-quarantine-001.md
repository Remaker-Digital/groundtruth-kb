NEW

# Per-Item Authorization Quarantine for Dispatch Head-of-Line Blocking

bridge_kind: prime_proposal
Document: gtkb-dispatch-per-item-auth-quarantine
Version: 001
Date: 2026-06-23

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: fce4df4c-b66a-422f-a0af-d26c56ad3613
author_model: claude-opus-4-6
author_model_version: claude-opus-4-6
author_model_configuration: Interactive Prime Builder session

Work Item: WI-4770
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING

## Summary

Fix head-of-line blocking defect in `_issue_dispatch_authorization_for_selected()` where a single GO item's `AuthorizationError` blocks the entire Prime Builder dispatch lane.

## Problem

`_issue_dispatch_authorization_for_selected()` (line 1374 of `scripts/cross_harness_bridge_trigger.py`) calls `issue_dispatch_authorization_packets()` which creates authorization packets as a batch via list comprehension. If ANY `create_authorization_packet()` call raises `AuthorizationError` (e.g., a design-only GO thread with empty `target_paths`), the entire PB dispatch lane fails — no other GO items can be dispatched.

Concrete example: `gtkb-wi4586-benchmark-informed-dispatch-enforcement-design` had GO at -002 with `target_paths: []` (design-only proposal). Every PB dispatch attempt hit this thread first (oldest-first ordering), failed authorization, and blocked all other pending GO items. The Part B DEFERRED filing at -003 removes this specific thread from the actionable queue, but the structural defect remains: any future GO'd bridge thread with authorization issues would recreate the same head-of-line blocking.

## Specification Links

- GOV-RELIABILITY-FAST-LANE-001: This is a small defect fix (1 file, ~30 lines, no new API, defect origin)
- GOV-STANDING-BACKLOG-001: WI-4770 created under PROJECT-GTKB-RELIABILITY-FIXES
- SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001: Dispatch substrate behavior contract (the fix preserves dispatcher-agnostic authorization semantics)
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001: Platform binding constraints preserved
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001: Proposal links governing specs; satisfied by this section
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001: Verification plan derives tests from linked specs; satisfied by Spec-Derived Verification Plan section
- GOV-FILE-BRIDGE-AUTHORITY-001: Bridge protocol authority; this proposal uses the governed bridge path
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001: Artifact-oriented governance; WI-4770 + DELIB capture satisfy lifecycle triggers
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001: Development as artifact network; deliberation + WI + proposal chain
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001: Lifecycle triggers for owner decisions and deferred work

## Prior Deliberations

- WI-4658 (`gtkb-dispatch-malformed-status-token-quarantine`): Established the per-item quarantine pattern in `_acquire_prime_work_intent_batch()` for `MalformedBridgeStatusError`. This proposal extends the same pattern to `AuthorizationError` in the authorization phase.
- DELIB-S421 (owner AUQ Part A+B approval, session fce4df4c): Owner approved both the per-item quarantine fix (Part A) and the DEFERRED filing (Part B) for the wi4586 thread.

## Proposed Changes

### File: `scripts/cross_harness_bridge_trigger.py`

**Function: `_issue_dispatch_authorization_for_selected()` (lines 1374-1412)**

Replace the batch `issue_dispatch_authorization_packets()` call with a per-item loop:

1. Loop through `go_items` individually
2. Call `create_authorization_packet()` per item
3. On `AuthorizationError`: quarantine the item — record in `dispatch-failures.jsonl` with reason `impl_auth_quarantined`, continue to next item
4. Collect successful packets
5. If ALL quarantined: return `{"ok": False, "reason": "all_go_items_quarantined", ...}`
6. If some succeeded: write named packets for healthy items via `write_named_packet()`, write `current.json` pointing to first healthy item via `write_packet()`, return `{"ok": True, ...}` with quarantine info

The pattern mirrors `_acquire_prime_work_intent_batch()` (lines 1260-1340) which already handles `MalformedBridgeStatusError` identically.

### target_paths

- `scripts/cross_harness_bridge_trigger.py`

## Requirement Sufficiency

Existing requirements sufficient. The fix implements the per-item quarantine pattern already established by WI-4658 in the work-intent acquisition phase, extending it to the authorization phase.

## Spec-Derived Verification Plan

- GOV-RELIABILITY-FAST-LANE-001: Verify the fix is defect-origin, touches 1 file, <50 lines changed, no new public API
- Functional test: Verify a batch with one bad GO item (empty `target_paths`) and one good GO item produces a successful dispatch for the good item while quarantining the bad item
- Regression test: Verify existing `_issue_dispatch_authorization_for_selected` behavior is preserved for all-healthy batches (no quarantine entries)
- Integration: Run existing `platform_tests/scripts/test_cross_harness_bridge_trigger.py` suite

## Recommended Commit Type

`fix:` — repair to broken dispatch behavior with no new capability surface.

## Risk and Rollback

- **Risk**: Low. The per-item pattern is proven in the sibling function `_acquire_prime_work_intent_batch()`.
- **Rollback**: Revert single function body to batch call.

## Owner Decisions / Input

Owner approved this fix via AskUserQuestion in the prior session segment (session fce4df4c-b66a-422f-a0af-d26c56ad3613, 2026-06-23). The AUQ presented three options:

1. **Both A + B (Recommended)** — fix PB per-item quarantine + DEFER the wi4586 thread
2. Part A only — fix PB per-item quarantine, leave wi4586 as-is
3. Part B only — DEFER wi4586, no code fix

Owner selected option 1. This proposal implements Part A; Part B (DEFERRED filing) is already complete at `bridge/gtkb-wi4586-benchmark-informed-dispatch-enforcement-design-003.md`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
