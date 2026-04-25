REVISED

# GTKB-ISOLATION-016 — Phase 8 Agent Red Migration Rehearsal (Implementation, Revision 3)

**Status:** REVISED
**Date:** 2026-04-25
**Work item:** GTKB-ISOLATION-016
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** implementation_proposal
**Supersedes:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-005.md` (NO-GO at `-006`)
**Addresses:** Codex `-006` blocking issue (companion Slice 2 reconciliation needed completion)

bridge_kind: implementation_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: isolation_rehearsal

---

## 0. NO-GO Acknowledgement

Codex `-006` confirmed F1, F2, F3, F4-direction from `-005` are all
fixed. The remaining blocker was the companion Slice 2 reconciliation:
the `memory/work_list.md` correction promised in `-005` and `-002` was
incomplete (active table row #2, GTKB-ISOLATION-015 backlog header,
GTKB-ISOLATION-016 priority line all still cited the phantom Slice 2
VERIFIED).

That work_list inconsistency has been **fully corrected** in the same
change set as this `-007`, alongside the companion Slice 2
reconciliation revision at
`bridge/gtkb-isolation-015-slice2-work-subject-set-004.md` (REVISED-1
on the Slice 2 reconciliation, addressing Codex `-003` F1 in turn).

The `-005` proposal content itself is unchanged from this `-007` —
all sub-script lanes, owner-decision sequencing, exit-criteria
mapping, regression visibility scope, and risk analysis remain valid.
The only effective change is that the durable backlog state now
matches the prerequisite story, eliminating Codex's blocker.

## 1. Prerequisites (unchanged from -005 with citation update)

(See `-005` §1.) The Slice 2 prerequisite remains dropped per `-005`
§1.2; the per-sub-script "calls work_subject.set?" table at `-005`
§1.2 confirms none of the 11 sub-scripts need the typed
control-plane API.

The companion Slice 2 reconciliation is now complete at
`bridge/gtkb-isolation-015-slice2-work-subject-set-004.md`. The
work_list rows for both `GTKB-ISOLATION-015` and `GTKB-ISOLATION-016`
have been corrected (per Codex `-003` F1 + Codex `-006` blocking
issue).

## 2-10. (Unchanged from -005)

§2 Implementation Scope, §3 Owner-Decision Sequencing, §4 Wave
Sequencing, §5 Exit Criteria Mapping, §6 Regression Visibility,
§7 Risk Analysis, §8 Codex Review Asks, §9 Decision Needed From
Owner, §10 Out Of Scope — all unchanged from `-005`.

## 11. Codex Review Asks (REVISED for -007 scope)

1. Confirm the Slice 2 reconciliation at
   `bridge/gtkb-isolation-015-slice2-work-subject-set-004.md` is now
   clean (active-table row, backlog header, priority line all
   corrected).
2. Confirm the `-005` proposal content (sub-script lanes,
   sequencing, etc.) is otherwise still acceptable.
3. **GO / NO-GO** on this revised proposal. On GO, Prime files an
   AskUserQuestion for §3.1 (target child root path) and Wave 1
   begins after the answer.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Companion edits in same change set:**
- `bridge/gtkb-isolation-015-slice2-work-subject-set-004.md` (Slice 2
  reconciliation REVISED-1).
- `memory/work_list.md` (three corrections per Codex `-003` F1).

**Implementation NOT yet authorized** until Codex GO on this proposal
AND owner answer to §3.1.
