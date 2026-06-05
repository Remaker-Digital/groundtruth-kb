NEW
author_identity: Claude Code
author_harness_id: B
author_session_context_id: c8540633-6638-44c0-81c1-0f18cefe48e4
author_model: claude-sonnet-4-6
author_model_version: claude-sonnet-4-6
author_model_configuration: claude-code; interactive; Prime Builder
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4358

# Cross-Harness Trigger: Filter Selected Items to GO-Only Before Authorization Packet Creation

bridge_kind: implementation_proposal

## Summary

`_issue_dispatch_authorization_for_selected` in `scripts/cross_harness_bridge_trigger.py` builds
`bridge_ids` from ALL selected items regardless of `top_status`. When the selected set for Prime
Builder includes NO-GO threads (revision tasks), `issue_dispatch_authorization_packets` raises
`AuthorizationError` because `create_authorization_packet` requires the latest bridge status to be
GO. This produces silent dispatch failures — 548 confirmed in
`.gtkb-state/bridge-poller/dispatch-failures.jsonl`.

**Fix:** Filter `selected` to GO-only items before building `bridge_ids`. If no GO items remain,
return success immediately — NO-GO threads are revision tasks for Prime Builder, not impl-auth
candidates.

## Problem Statement

When the cross-harness trigger dispatches to Prime Builder:

1. `_dispatch_to_recipient` calls `_issue_dispatch_authorization_for_selected(project_root, selected, recipient_dir)` at line 1398.
2. `_issue_dispatch_authorization_for_selected` builds `bridge_ids = [str(item.document_name) for item in selected]` at line 587 — ALL items regardless of `top_status`.
3. `issue_dispatch_authorization_packets(project_root, bridge_ids, ...)` calls `create_authorization_packet` for each.
4. `create_authorization_packet` raises `AuthorizationError` when latest bridge status is not GO.

Result: 548 dispatch failures in `.gtkb-state/bridge-poller/dispatch-failures.jsonl` with
`"error": "AuthorizationError"`. Every dispatch that included a NO-GO thread in the selected
set failed silently — the NO-GO revision tasks were never delivered to Prime Builder.

## Root Cause

Line 587 of `scripts/cross_harness_bridge_trigger.py`:

```python
# BUGGY — builds bridge_ids from ALL selected items regardless of top_status:
bridge_ids = [str(item.document_name) for item in selected]
```

Fix (replace line 587 and insert 3 additional lines):

```python
go_items = [item for item in selected if getattr(item, "top_status", "").upper() == "GO"]
bridge_ids = [str(item.document_name) for item in go_items]
if not bridge_ids:
    # All selected items are NO-GO revision tasks; no impl-auth packet needed.
    return {"ok": True, "reason": None, "context": {}}
```

The `getattr(item, "top_status", "")` idiom is used consistently throughout the trigger for
safe attribute access on bridge items (cf. lines 545, 602, 1253, 1318, 1394).

The caller at line 1398 is invoked only for `target.needed_role_label == "prime-builder"`.
The caller already handles `ok=True` with empty `context={}` as a normal successful result.
NO-GO items continue to appear in the dispatch prompt text — they are not suppressed from
the session; only the authorization packet creation is skipped for non-GO items.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority; dispatch must faithfully
  route actionable work without silent failure.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandatory spec linkage; this
  proposal cites all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived test mapping required;
  provided in Spec-Derived Verification Plan below.
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` — mechanism-agnostic dispatch contract; spawn
  must not fail silently when actionable work exists.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` — auto-trigger contract; trigger MUST dispatch on
  actionable signature change; silent error is a violation.
- `GOV-STANDING-BACKLOG-001` — governance contract for standing backlog; defects blocking
  dispatch must be treated as P1 reliability items.
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane eligibility: origin=defect (WI-4358),
  no new public CLI surface, covered by standing PAUTH.

## Owner Decisions / Input

No AUQ decisions required for this proposal.

GOV-RELIABILITY-FAST-LANE-001 eligibility confirmed:
- `origin = defect` (WI-4358, PROJECT-GTKB-RELIABILITY-FIXES)
- No new public CLI surface is introduced (internal function change only)
- Covered by standing PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`

Owner diagnosis captured in DELIB-20260872 authorized investigation of the 548 failures.
WI-4358 created as origin=defect in DELIB-20260875 per owner direction.
Fix approach selected in DELIB-20260876 per owner direction.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirements are needed before
implementation. The fix restores intended trigger behavior described by
`ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` and `DCL-SMART-POLLER-AUTO-TRIGGER-001`.

Owner waiver: GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS — DELIB-20260876 — This proposal is a targeted 4-line defect fix to a single dispatch function, not a bulk MemBase work-item operation. CLAUSE-VISIBILITY-BULK-OPS requires inventory artifact, review packet, and decision markers for bulk backlog-mutation work. This proposal modifies a trigger script and adds 3 tests; it does not mutate work items in bulk. The owner-authorized fix approach in DELIB-20260876 is the governing decision record.

## Prior Deliberations

- DELIB-20260872 — owner diagnosis session: 548 dispatch failures confirmed in
  `.gtkb-state/bridge-poller/dispatch-failures.jsonl`; root cause identified as
  `_issue_dispatch_authorization_for_selected` running `create_authorization_packet`
  against NO-GO threads before any status check.
- DELIB-20260875 — WI-4358 created as `origin=defect` in PROJECT-GTKB-RELIABILITY-FIXES
  per owner direction following diagnosis.
- DELIB-20260876 — fix approach decided by owner: filter `selected` items to GO-only
  before creating impl-auth packets; return `ok=True` immediately when no GO items remain.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-2086` — seed=search; bridge_thread; Bridge thread: gtkb-cross-harness-trigger-import-repair (6 versions, VERIFIED)
- DA: `DELIB-2417` — seed=search; bridge_thread; Loyal Opposition Verification - Cross-Harness Trigger Dispatch-State Lag
- DA: `DELIB-2803` — seed=search; bridge_thread; Bridge INDEX startup comment compaction snapshot 2026-06-02T01:25:34Z
- DA: `DELIB-1876` — seed=search; bridge_thread; Bridge thread: gtkb-cross-harness-trigger-codex-exec-hook-firing-001 (2 versions
- DA: `DELIB-2206` — seed=search; bridge_thread; Bridge INDEX startup comment compaction snapshot 2026-05-20T01:16:24Z

## Implementation Plan

**target_paths:**
```json
["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]
```

### File 1: `scripts/cross_harness_bridge_trigger.py`

In `_issue_dispatch_authorization_for_selected`, replace line 587:

```python
# Before (line 587):
bridge_ids = [str(item.document_name) for item in selected]

# After (lines 587-590):
go_items = [item for item in selected if getattr(item, "top_status", "").upper() == "GO"]
bridge_ids = [str(item.document_name) for item in go_items]
if not bridge_ids:
    return {"ok": True, "reason": None, "context": {}}
```

No other changes to this file.

### File 2: `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

Add 3 new test functions to the existing test module:

1. `test_issue_dispatch_auth_skips_no_go_items` — selected set contains only NO-GO items;
   asserts `ok=True`, `context={}`, no call to `issue_dispatch_authorization_packets`.

2. `test_issue_dispatch_auth_uses_go_items_from_mixed_list` — selected set contains one GO
   item and one NO-GO item; asserts `issue_dispatch_authorization_packets` is called with
   only the GO item's document_name.

3. `test_issue_dispatch_auth_all_no_go_returns_empty_context` — selected set contains only
   NO-GO items; asserts the return value is `{"ok": True, "reason": None, "context": {}}`.

## Spec-Derived Verification Plan

| Spec | Verification | Expected |
|------|-------------|----------|
| DCL-SMART-POLLER-AUTO-TRIGGER-001 (no error on NO-GO queue) | `test_issue_dispatch_auth_skips_no_go_items` | PASS |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 (no silent failure) | `test_issue_dispatch_auth_uses_go_items_from_mixed_list` | PASS |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 (empty GO list graceful) | `test_issue_dispatch_auth_all_no_go_returns_empty_context` | PASS |
| Regression suite | `pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -v` | All pass |
| Ruff lint | `ruff check scripts/cross_harness_bridge_trigger.py` | Clean |
| Ruff format | `ruff format --check scripts/cross_harness_bridge_trigger.py` | Clean |

## Risk and Rollback

**Risk:** Minimal. The change narrows authorization packet creation scope to GO items only.
NO-GO items continue to appear in the dispatch prompt text. The caller already handles
`ok=True` with empty `context={}` as normal. No behavioral change for dispatches where all
selected items are GO.

**Rollback:** Revert the 4-line change in `_issue_dispatch_authorization_for_selected`;
remove the 3 new test functions.

## Recommended Commit Type

`fix:`
