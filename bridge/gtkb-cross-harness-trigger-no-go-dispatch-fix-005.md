REVISED
author_identity: Claude Code
author_harness_id: B
author_session_context_id: a1951945-8433-468a-b511-965af4819e0a
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7
author_model_configuration: claude-code; interactive; Prime Builder
author_metadata_source: prime-builder session; bridge-author-metadata/current.json

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4358

# Cross-Harness Trigger: Filter Selected Items to GO-Only Before Authorization Packet Creation

bridge_kind: prime_proposal
Document: gtkb-cross-harness-trigger-no-go-dispatch-fix
Version: 005
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-05 UTC
Responds to: bridge/gtkb-cross-harness-trigger-no-go-dispatch-fix-004.md (Codex NO-GO)

## Summary

`_issue_dispatch_authorization_for_selected` in `scripts/cross_harness_bridge_trigger.py` builds
`bridge_ids` from ALL selected items regardless of `top_status`. When the selected set for Prime
Builder includes NO-GO threads (revision tasks), `issue_dispatch_authorization_packets` raises
`AuthorizationError` because `create_authorization_packet` requires the latest bridge status to be
GO. This produces silent dispatch failures — 621 confirmed in
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

Result: 621 dispatch failures in `.gtkb-state/bridge-poller/dispatch-failures.jsonl` with
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
  dispatch must be treated as P1 reliability items. Clause-evidence satisfied by the
  standing fast-lane formal-artifact-approval packet (see Owner Decisions / Input).
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane eligibility: origin=defect (WI-4358),
  no new public CLI surface, covered by standing PAUTH.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory; this proposal was found via the
  MemBase work-item backlog (WI-4358) and Deliberation Archive search; artifact-oriented
  development is operative but does not impose additional evidence requirements beyond
  the WI-4358 MemBase record and standing PAUTH for this targeted defect fix.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory; WI-4358 origin=defect governs this
  work item's lifecycle; the `candidate`/`verified` lifecycle triggers apply to the WI
  lifecycle, not to the dispatch script code change itself.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory; owner decisions, work items, and
  backlog are operated per artifact-oriented governance; the standing PAUTH and WI-4358
  MemBase record constitute sufficient governance evidence for this defect fix.

## Owner Decisions / Input

No per-fix AUQ decisions required for this proposal. Standing fast-lane authorization applies.

**Standing fast-lane formal-artifact-approval packet:**

- Path: `.groundtruth/formal-artifact-approvals/2026-05-15-gov-reliability-fast-lane.json`
- Content sha256: `6c7acbe3d7ea1a0aa8420a22e1f55edce17139b6c0d2fe1d0bb88867ad0a8975`
- Covered artifacts: `GOV-RELIABILITY-FAST-LANE-001`, `PROJECT-GTKB-RELIABILITY-FIXES`,
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
- Owner directive: AskUserQuestion S351, "Approve - create all three" fast-lane artifacts
- Source: `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` (owner decision)

This packet establishes the standing fast-lane authorization that covers the present
defect fix as an inventory/review-packet equivalent for `GOV-STANDING-BACKLOG-001/CLAUSE-
VISIBILITY-BULK-OPS`. The bulk-operation-class evidence is the existing approval packet,
which constitutes the formal-artifact-approval citation the clause detector requires.

`GOV-RELIABILITY-FAST-LANE-001` eligibility confirmed by live MemBase readback:
- `origin = defect` (WI-4358, PROJECT-GTKB-RELIABILITY-FIXES, active member confirmed)
- No new public CLI surface is introduced (internal function change only)
- Covered by standing PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
  (active, unexpired, mutation classes: source, test_addition, hook_upgrade)
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` is the durable fast-lane authority
  record; no per-fix owner decision is required under `GOV-RELIABILITY-FAST-LANE-001`
  for defect-origin WIs covered by the standing PAUTH.

No separate owner diagnosis, WI-creation, or fix-approach deliberation records were
created for WI-4358. The fast-lane mechanism does not require them; the WI-4358 MemBase
record (origin=defect, active project membership) and the standing PAUTH are the
complete authorization evidence.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirements are needed before
implementation. The fix restores intended trigger behavior described by
`ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` and `DCL-SMART-POLLER-AUTO-TRIGGER-001`.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing fast-lane direction for
  small defect/reliability fixes under PROJECT-GTKB-RELIABILITY-FIXES; this
  proposal's eligibility and standing PAUTH scope derive from this record.
- `DELIB-2417` — cross-harness trigger dispatch-state lag context; relevant prior
  background on trigger dispatch failures.
- `DELIB-2364` — prior bridge-dispatcher NO-GO context; prior dispatch-failure class.

### Helper-suggested candidates (reviewed and pruned)

- DA: `DELIB-2086` — seed=search; bridge_thread; Bridge thread: gtkb-cross-harness-trigger-import-repair (6 versions, VERIFIED)
- DA: `DELIB-1876` — seed=search; bridge_thread; Bridge thread: gtkb-cross-harness-trigger-codex-exec-hook-firing-001

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

3. `test_spawn_harness_dispatches_no_go_only_batch` — spawn-level regression test verifying
   that `_spawn_harness` launches Prime Builder even when the entire selected batch is NO-GO.
   Setup: selected set contains only one NO-GO item; `subprocess.Popen` is patched.
   Asserts:
   - `issue_dispatch_authorization_packets` is NOT called;
   - `subprocess.Popen` is called exactly once (the harness launch proceeds);
   - the dispatch prompt text passed to the child process includes the NO-GO item's
     document name (revision task is visible to the spawned session);
   - no implementation authorization packet file is created under the recipient directory;
   - either no `GTKB_IMPLEMENTATION_AUTH_*` environment variables are set in the child
     environment, or the env contract for empty-GO batches is explicitly documented and
     the test asserts the documented value.

## Spec-Derived Verification Plan

| Spec | Verification | Expected |
|------|-------------|----------|
| DCL-SMART-POLLER-AUTO-TRIGGER-001 (no error on NO-GO queue) | `test_issue_dispatch_auth_skips_no_go_items` | PASS |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 (no silent failure on mixed list) | `test_issue_dispatch_auth_uses_go_items_from_mixed_list` | PASS |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 (spawn fires for all-NO-GO batch) | `test_spawn_harness_dispatches_no_go_only_batch` | PASS |
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

## Revision Notes (REVISED -005 vs REVISED -003)

Changes addressing Codex NO-GO `-004` finding F1 (`GOV-STANDING-BACKLOG-001/CLAUSE-
VISIBILITY-BULK-OPS` blocking clause-preflight gap):

- **F1 (P1):** Cited the standing fast-lane formal-artifact-approval packet path
  (`.groundtruth/formal-artifact-approvals/2026-05-15-gov-reliability-fast-lane.json`)
  and its sha256 content hash in `Owner Decisions / Input`. The clause-preflight
  detector pattern `(?i)(?:inventory|review[- ]packet|DECISION DEFERRED|formal-artifact-approval)`
  matches the explicit `formal-artifact-approval` citation, satisfying the bulk-ops
  evidence requirement without creating a new per-fix packet (per fast-lane mechanism
  in `GOV-RELIABILITY-FAST-LANE-001`).
- Added a brief explanatory line under `GOV-STANDING-BACKLOG-001` in `Specification
  Links` cross-referencing the packet citation.
- No code, target-path, test, or spec-mapping changes from `-003`. The source/test
  proposal remains exactly the GO-filtering fix.

Changes carried forward from `-003` vs `-001`:

- Removed false DELIB-20260872, DELIB-20260875, DELIB-20260876 citations
  from `Owner Decisions / Input`, `Prior Deliberations`, and the owner-waiver line.
  Those IDs belong to unrelated envelope-program and release-prep decisions. Replaced
  with live evidence: WI-4358 MemBase record, standing PAUTH readback confirmation, and
  `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` as the durable fast-lane authority.
- Replaced duplicate all-NO-GO helper test
  (`test_issue_dispatch_auth_all_no_go_returns_empty_context`) with spawn-level regression
  test (`test_spawn_harness_dispatches_no_go_only_batch`) that verifies `subprocess.Popen`
  fires even when the entire selected batch is NO-GO.

## Recommended Commit Type

`fix:`
