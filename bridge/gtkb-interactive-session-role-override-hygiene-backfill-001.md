NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S378-interactive-session-role-override-hygiene-backfill
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3474
target_paths: ["groundtruth.db"]

# GT-KB Interactive Session Role Override - Hygiene Backfill for Slices 4-7

bridge_kind: implementation_proposal

Document: gtkb-interactive-session-role-override-hygiene-backfill
Version: 001 (NEW)
Date: 2026-05-30 UTC

## Summary

Bring the `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` project's MemBase metadata into alignment with the as-shipped Slices 4-7 implementation state. The four slice bridge threads reached VERIFIED earlier and their implementations committed at `aa5ea80b` (Slice 4) and `71f81d96` (Slices 5-7); the project metadata still reflects pre-VERIFIED state.

This is a metadata-only cleanup. No source code, tests, hooks, scripts, configuration, or repository-state files are modified.

## Multi-WI Scope Acknowledgement

This proposal coordinates a single bounded hygiene action across four work items (WI-3474, WI-3475, WI-3476, WI-3477) and references WI-3462 (the Phase-2 implements-link backfill thread) as prior deliberation context. The declared primary `Work Item` field is `WI-3474` per the bridge protocol's single-WI-declaration convention; the cited additional WI IDs are operational scope, not duplicate declarations. The bridge-compliance gate's collision warning is acknowledged and the multi-WI scope is intentional — hygiene operations of this class inherently span a project's WI cohort.

## Premise Verification (live state)

| Surface | Current state | Target state |
|---|---|---|
| WI-3474 `related_bridge_threads` | scoping-004 + slice-3-004 | + slice-4-004 |
| WI-3475 `related_bridge_threads` | `None` | slice-5-004 |
| WI-3476 `related_bridge_threads` | `None` | slice-6-004 |
| WI-3477 `related_bridge_threads` | `None` | slice-7-006 |
| WI-3474..3477 `resolution_status` | `open` | `resolved` (via reconciler) |
| Project `artifact_links` | scoping (related) + slice-1/2/3 (implements) | + slice-4/5/6/7 (implements) |

### In-Root Boundary Affirmation

All operations target MemBase at `E:\GT-KB\groundtruth.db` (in-root). No Agent Red dependency. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## Plan

### Step 1 — Backfill `work_items.related_bridge_threads`

A one-off script `scripts/session-tmp/s378-backfill-role-override-related-threads.py` issues 4 `db.update_work_item()` calls with `changed_by = "prime-builder/claude/B"` and a `change_reason` citing this bridge proposal's GO version.

Target values:
- WI-3474: append `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` to existing list
- WI-3475: `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md`
- WI-3476: `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md`
- WI-3477: `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md`

### Step 2 — Add 4 project `implements` artifact-links

Four `gt projects link-bridge` invocations adding `implements` relationships for slice-4/5/6/7 to `PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE`.

### Step 3 — Run `bridge_verified_backlog_reconciler.py --apply`

The reconciler resolves WIs whose linked bridge threads are all VERIFIED, citing `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`. After Steps 1+2, the 4 WIs become discoverable with proper parent evidence.

## Acceptance Criteria

1. WI-3475/3476/3477 each have non-empty `related_bridge_threads` referencing the matching VERIFIED slice bridge thread.
2. WI-3474 retains existing 2 entries and adds slice-4.
3. Project `artifact_links` includes 4 new `implements` entries for slice-4/5/6/7.
4. WI-3474..3477 reach `resolution_status = resolved` after reconciler run.
5. `gt projects show PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` reflects cleaned-up state.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 — the resolution-table architecture whose Slices 4/5/6/7 VERIFIED implementations are reflected here.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 — parent architectural decision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this proposal is filed at `-001`; `bridge/INDEX.md` receives a `NEW:` entry.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage gate satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — see Spec-Derived Verification below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project triple in header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 covers all 4 cited WIs but its `allowed_mutation_classes` does NOT include backlog/artifact-link mutations; this proposal requests bridge GO as authorization for those specific mutation classes per this bounded cleanup.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — see PAUTH note above.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — bridge GO is the authorization predicate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root boundary affirmed.
- `GOV-ARTIFACT-APPROVAL-001` — no canonical artifact insertion.
- `GOV-STANDING-BACKLOG-001` — see Clause Scope Clarification below.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — owner decision authorizing the reconciler service this proposal's Step 3 invokes.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` — parent scoping GO.
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` — Slice 4 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-5-focus-menu-role-awareness-004.md` — Slice 5 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-6-attribution-role-awareness-004.md` — Slice 6 VERIFIED.
- `bridge/gtkb-interactive-session-role-override-slice-7-doctor-marker-checks-006.md` — Slice 7 VERIFIED.

## Prior Deliberations

- `bridge/gtkb-interactive-session-role-override-scoping-003.md` — parent 10-slice scoping plan.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` — parent scoping GO.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — reconciler authorization.
- Phase-2 implements-link backfill thread (WI-3462) ran 2026-05-30 and backfilled Slices 1, 2, 3 but did NOT include Slices 4-7. This proposal closes that gap.

## Owner Decisions / Input

This proposal operates under existing approval evidence:

- `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v3 (active); covers WI-3474..3480.
- `DELIB-2507` — the S371 owner directive establishing the project.
- Owner directive S378 (this session): "clean up the WI-3474..3477 status/linkage hygiene gap" (explicit response to AskUserQuestion option `c`).
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — owner authorization for the reconciler service.

No new owner AUQ required.

## Requirement Sufficiency

**Existing requirements sufficient.**

The cleanup brings project metadata into alignment with as-shipped VERIFIED state. No new specifications introduced. `DELIB-S345` already authorizes the reconciler-driven resolution path; this proposal extends the same logic to the prerequisite field-backfill step.

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification:

This is a single-project, four-work-item hygiene operation. No backlog bulk operation (bounded to 4 specific WIs in one project), no `work_items` insert/retire/supersede (single field update per WI plus already-authorized reconciler), no project create/retire, no authorization mutation, no inventory artifact, no review-packet, no formal-artifact-approval packet, no MemBase canonical-artifact insert.

Evidence-pattern tokens: hygiene backfill, four work items, one project, single field update, deterministic reconciler service authorized by DELIB-S345, no canonical artifact insert, no bulk.

## Spec-Derived Verification (Plan)

### Spec-to-test mapping

| Specification | Verification Command | Expected Result |
|---|---|---|
| `DCL-SESSION-ROLE-RESOLUTION-001` | `gt projects show PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE` | 8 artifact_links (scoping + 7 implements) |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` | Same | All 7 WIs reflected with correct project membership |
| `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` | `python scripts/bridge_verified_backlog_reconciler.py --dry-run` | WI-3474..3477 absent from `would_resolve_ids` (already resolved) |
| Cross-cutting governance specs | applicability + clause preflights | Both pass |

### Commands the post-impl report will execute

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/session-tmp/s378-backfill-role-override-related-threads.py --apply
groundtruth-kb/.venv/Scripts/gt.exe projects link-bridge PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE gtkb-interactive-session-role-override-slice-4-axis2-role-awareness --relationship implements --change-reason "..."
# ... 3 more link-bridge calls for slice-5/6/7
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_verified_backlog_reconciler.py --apply
groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
```

## Risk and Rollback

### Risk classes

- **R1 — wrong slice-to-WI mapping.** Mitigation: scoping-004 documents the binding; `gt projects show` confirms current WI titles match intended slices.
- **R2 — concurrent session writes.** Mitigation: MemBase versioning is append-only; backfill script can be re-run idempotently.
- **R3 — reconciler resolves more than the 4 intended WIs.** Mitigation: dry-run output shows exactly which WIs would be resolved; post-impl report compares pre/post `resolved_ids` lists.

### Rollback

Manual MemBase revert via `db.update_work_item` with the old `related_bridge_threads` values, project artifact-link `retire`, and reconciler's `--repair-overbroad` flag.

## Recommended Commit Type

`chore` — metadata hygiene; no behavioral change, no new capability, no defect fix.

## Owner Action Required

None.
