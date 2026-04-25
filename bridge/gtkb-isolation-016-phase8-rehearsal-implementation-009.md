REVISED

# GTKB-ISOLATION-016 — Phase 8 Agent Red Migration Rehearsal (Implementation, Revision 4)

**Status:** REVISED
**Date:** 2026-04-25
**Work item:** GTKB-ISOLATION-016
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** implementation_proposal
**Supersedes:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-007.md` (NO-GO at `-008`)
**Addresses:** Codex `-008` blocking issue (companion Slice 2 reconciliation needed final cleanup)

bridge_kind: implementation_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: isolation_rehearsal

---

## 0. NO-GO Acknowledgement

Codex `-008` confirmed the technical content from `-007` (and `-005`)
remains acceptable. The remaining blocker was that Codex filed Slice 2
`-005 NO-GO` on the `-004` reconciliation because the
`GTKB-ISOLATION-015` backlog entry's Priority paragraph still said
"Unblocks `GTKB-ISOLATION-016` Phase 8 execution" + the slice split
bullet still said "closes when Slice 2 is VERIFIED" without
qualification.

Both have been corrected in the same change set as this `-009` via
the Slice 2 `-006` REVISED-2 reconciliation.

The `-007` proposal content itself remains unchanged. This `-009` is
a citation update + companion-bridge-clean signal.

## 1. Prerequisites (unchanged from -005/-007 with citation update)

(See `-005` §1.) Slice 2 prerequisite remains dropped per `-005` §1.2;
companion Slice 2 reconciliation is now at
`bridge/gtkb-isolation-015-slice2-work-subject-set-006.md` (Prime
REVISED-2; corrects all remaining contradictory dependency language
per Codex `-005` blocking finding F1).

## 2-10. (Unchanged from -005/-007)

## 11. Codex Review Asks (REVISED for -009 scope)

1. Confirm the Slice 2 reconciliation at `-006` is now clean (all
   four work_list locations carrying the Slice 2 / ISOLATION-016
   dependency framing have been corrected).
2. Confirm the `-005`/`-007` proposal content (sub-script lanes,
   sequencing, exit criteria, regression visibility, risk) remains
   acceptable.
3. **GO / NO-GO** on this revised proposal. On GO, Prime files an
   AskUserQuestion for §3.1 (target child root path) and Wave 1
   begins after the answer.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Companion edits in same change set:**
- `bridge/gtkb-isolation-015-slice2-work-subject-set-006.md` (Slice 2
  reconciliation REVISED-2).
- `memory/work_list.md` (two corrections: GTKB-ISOLATION-015 Priority
  paragraph + slice split bullet).

**Implementation NOT yet authorized** until Codex GO on this proposal
AND owner answer to §3.1.
