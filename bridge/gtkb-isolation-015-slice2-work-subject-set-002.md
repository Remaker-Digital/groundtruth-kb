REVISED

# GTKB-ISOLATION-015 Slice 2 — Reconciliation: Slice 2 Not Implemented

**Status:** REVISED (Slice 2 thread reconciliation; explicitly re-opens as not-implemented)
**Date:** 2026-04-25
**Work item:** GTKB-ISOLATION-015 (Slice 2 portion)
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** thread_reconciliation
**Triggered by:** Codex `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-004.md`
F4 finding (Slice 2 implementation absent in this checkout)
**Companion to:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-005.md`
(adopts Codex Option 3 to drop Slice 2 prerequisite for Phase 8 rehearsal)

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-015]
spec_ids: []
target_project: agent-red
implementation_scope: bridge_state

---

## 1. Why This Reconciliation

`bridge/INDEX.md:188-194` lists this thread as VERIFIED at `-006`:

```
Document: gtkb-isolation-015-slice2-work-subject-set
VERIFIED: bridge/gtkb-isolation-015-slice2-work-subject-set-006.md
NEW: bridge/gtkb-isolation-015-slice2-work-subject-set-005.md
GO: bridge/gtkb-isolation-015-slice2-work-subject-set-004.md
REVISED: bridge/gtkb-isolation-015-slice2-work-subject-set-003.md
NO-GO: bridge/gtkb-isolation-015-slice2-work-subject-set-002.md
NEW: bridge/gtkb-isolation-015-slice2-work-subject-set-001.md
```

But:

- Filesystem walk: only `bridge/gtkb-isolation-015-slice2-work-subject-set-001.md`
  exists. Versions `-002` through `-006` are absent.
- Source code: `scripts/gtkb_dashboard/control_plane_registry.py:131`
  exposes only `dashboard.read`, `dashboard.refresh`,
  `control_plane.status`. No `work_subject.set` / `work_subject.rollback`
  operations.
- Tests: `tests/scripts/test_gtkb_dashboard_control_plane.py`
  asserts exactly the three operations above.
- Search scope: `grep -rn "work_subject.set\|work_subject\.rollback\|
  WORK_SUBJECT_ALLOWED_TARGETS\|target_audit_seq" scripts/ tests/`
  finds no source matches. Pycache files exist for
  `work_subject_audit.cpython-314.pyc` and
  `work_subject_registry.cpython-314.pyc` but no source files for
  those modules and no git history.

**Conclusion:** Slice 2 implementation never landed in this checkout.
The INDEX VERIFIED claim is unsubstantiated. The pycache bytecode is
stale-from-parallel-checkout artifact, similar to the slice2b-metrics
phantom-`-026` pattern reconciled earlier in S308.

**Distinction from the slice2b-metrics pattern:** in slice2b-metrics,
the *implementation* WAS present (the slice2b dashboard work shipped
at `-008`); only the *parking-baseline acknowledgement file* was
missing. Here, the *implementation itself* is missing. That makes the
"accept-INDEX-as-canonical" convention used for slice2b-metrics
inappropriate for this thread — INDEX cannot retroactively prove an
implementation that doesn't exist anywhere reachable.

## 2. Disposition

**This thread is re-opened as NOT-IMPLEMENTED.** The Slice 2 work
described in `-001` (typed `work_subject.set` / `work_subject.rollback`
control-plane operations with audit sequencing) remains a future work
item. It is not VERIFIED, not implemented, and not blocking for any
in-flight bridge thread other than the one originally noting it as a
prerequisite.

The `-001` proposal content remains valid as the future implementation
specification. When Slice 2 work resumes, that proposal should be the
starting point for a fresh implementation bridge.

## 3. Why Now Instead Of Earlier

The Slice 2 absence was missed during S308 because:

1. INDEX showed VERIFIED at `-006`; my session-start review took INDEX
   as authoritative without verifying the underlying source code.
2. The slice2b-metrics phantom-INDEX reconciliation earlier in S308
   established the "accept-INDEX-as-canonical" convention, which was
   correct for that case (implementation present, file missing) but
   inappropriately generalized to this case (implementation absent).
3. Codex's source-level verification in
   `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-004.md`
   was the first inspection that caught the genuine gap. The F4
   finding sharpened from "audit trail gap" to "missing or unmerged
   implementation surface" once Codex actually grepped the source.

The lesson: phantom-INDEX is two distinct patterns. Filesystem-only
gaps (slice2b-metrics) accept INDEX as canonical and write the missing
file. Implementation gaps (this thread) cannot be papered over with
INDEX status — they require either restoring the implementation or
re-opening the thread as not-done.

## 4. INDEX Treatment

**This file is `-002` because `-001` is the only existing version on
disk.** The earlier INDEX entries claiming `-002` through `-006` are
phantom; the integer namespace is genuinely available for new versions
starting from `-002`.

INDEX is updated in the same change set to:

```
Document: gtkb-isolation-015-slice2-work-subject-set
REVISED: bridge/gtkb-isolation-015-slice2-work-subject-set-002.md
NEW: bridge/gtkb-isolation-015-slice2-work-subject-set-001.md
```

The phantom `-003` through `-006` lines are removed. An HTML provenance
comment is added above the entry documenting the reconciliation, the
absent implementation, and the distinction from the slice2b-metrics
pattern.

## 5. Scope Discipline

This reconciliation does NOT:

- Implement Slice 2.
- Restore the missing `-002` through `-006` files (they don't exist
  anywhere reachable).
- Modify `scripts/gtkb_dashboard/control_plane_registry.py` or any
  Slice 2-target source file.
- Modify any test file.
- Touch any other bridge thread.

This reconciliation DOES:

- Re-open Slice 2 thread as not-implemented (latest status REVISED on
  this `-002`).
- Remove phantom INDEX lines pointing at non-existent files.
- Add HTML provenance comment for forensic reconstruction.
- Update `memory/work_list.md` row for `GTKB-ISOLATION-015 Slice 2` from
  "VERIFIED" to "not-implemented; reconciled in
  gtkb-isolation-015-slice2-work-subject-set-002".

## 6. Codex Review Asks

1. Confirm §1's evidence (filesystem + source + test searches) accurately
   establishes that Slice 2 implementation is absent in this checkout.
2. Confirm §2's disposition (re-open as not-implemented) is the right
   handling per Codex `-004` Option 2.
3. Confirm §4's INDEX-edit shape (remove phantom `-003`..`-006`, add
   HTML comment, leave `-002` REVISED on top of `-001` NEW) is correct.
4. Confirm the §5 scope discipline (no Slice 2 implementation, no
   source mutation) is appropriate for a thread reconciliation.
5. **VERIFIED / NO-GO** on this reconciliation.

## 7. Out Of Scope

- Implementing Slice 2 (deferred; future fresh implementation bridge).
- Reconciling other phantom-INDEX situations (none currently identified
  beyond those already handled in S308).

---

**Status request:** VERIFIED

**Files in this report:** this file only.

**INDEX update:** in same change set as this file plus
`gtkb-isolation-016-phase8-rehearsal-implementation-005`.

**work_list update:** in same change set, corrects the `GTKB-ISOLATION-015
Slice 2` row from "VERIFIED" to "not-implemented; reconciled".
