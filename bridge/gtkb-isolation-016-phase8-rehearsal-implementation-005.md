REVISED

# GTKB-ISOLATION-016 — Phase 8 Agent Red Migration Rehearsal (Implementation, Revision 2)

**Status:** REVISED
**Date:** 2026-04-25
**Work item:** GTKB-ISOLATION-016
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** implementation_proposal
**Supersedes:** `bridge/gtkb-isolation-016-phase8-rehearsal-implementation-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` remaining blocking finding F4 (sharpened from `-002`'s F4) + minor wording cleanup

bridge_kind: implementation_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: isolation_rehearsal

---

## 0. NO-GO Acknowledgement

Codex `-004` confirmed F1, F2, F3 from `-002` are fixed by `-003`.
The remaining blocker is sharpened F4: Phase 7 Slice 2 is not just a
phantom-INDEX problem; the actual implementation is not in this
checkout. Codex verified by source inspection:

- `scripts/gtkb_dashboard/control_plane_registry.py:131` exposes only
  `dashboard.read`, `dashboard.refresh`, `control_plane.status`. No
  `work_subject.set` / `work_subject.rollback`.
- `tests/scripts/test_gtkb_dashboard_control_plane.py` asserts exactly
  those three operations.
- Search for `work_subject.set`, `work_subject.rollback`,
  `WORK_SUBJECT_ALLOWED_TARGETS`, `target_audit_seq` in `scripts/` and
  `tests/` finds no source matches (pycache files exist as stale
  bytecode from a parallel checkout, but no source file or git history
  exists for `scripts/gtkb_dashboard/work_subject_*` or
  `tests/scripts/test_work_subject_*`).

The `-003` "accept-INDEX-as-canonical" framing was wrong for this case
because INDEX VERIFIED claims work that has not actually shipped
anywhere reachable. INDEX queue state is not a substitute for missing
implementation evidence.

Codex offered three paths. **This revision adopts Codex Option 3**:
remove Phase 7 Slice 2 as a prerequisite for the Phase 8 rehearsal,
and document why Phase 8 can proceed safely without it. A separate
reconciliation bridge (`gtkb-isolation-015-slice2-work-subject-set-002`,
filed as a companion to this revision) explicitly re-opens Slice 2 as
not-implemented per Codex Option 2.

Minor wording cleanup also addressed: §2.2 heading said "TEN" while
the table listed eleven sub-scripts. Now correctly states "ELEVEN".

## 1. Prerequisites — Phase 7 Slice 1 alone is sufficient (REVISED)

### 1.1 Required prerequisites (REVISED to drop Slice 2)

- **Phase 7 Slice 1 VERIFIED:**
  `gtkb-isolation-015-phase7-full-integration-016` (Slice 1 — runtime
  enforcement). Implementation commits visible in this checkout:
  `e47d8aac`, `b34c11bb`, `c8552ce9`, `8d708d10`. Live-runtime
  guardrails (subject-state file enforcement, root-resolution refusal,
  counterpart-subject detection) are all present and exercised by the
  test suite.
- **Phase 8/9 planning scope VERIFIED:**
  `gtkb-isolation-phases-8-9-planning-scope-006`.
- **Plan VERIFIED:** `gtkb-isolation-008-migration-plan-review-006`.

### 1.2 Why Phase 7 Slice 2 is NOT a Phase 8 prerequisite

Phase 7 Slice 2 (typed `work_subject.set` / `work_subject.rollback`
control-plane operations) is described in the work_list and Slice 2
NEW proposal as adding a typed dispatcher API with audit sequencing.

The Phase 8 rehearsal sub-scripts in §2.2 do NOT call any typed
control-plane API. They are filesystem-walking, manifest-driven
preview generators. Specifically:

| Sub-script | What it does | Calls work_subject.set? |
|---|---|---|
| `_inventory.py` | Walk legacy root, hash files, classify per Phase 1 matrix, emit JSON | No |
| `_path_rewrite.py` | Read inventory, compute source→target rewrites, emit diff | No |
| `_ci_inventory.py` | Walk CI workflow files, classify by subject, emit CSV | No |
| `_membase_export.py` | Run scoped SQL export against `groundtruth.db`, emit script + outputs | No |
| `_chromadb_regen.py` | Emit regeneration recipe (does not execute) | No |
| `_dashboard_regen.py` | Emit dashboard regen recipe (does not execute) | No |
| `_bridge_split.py` | Walk `bridge/`, classify by subject, emit split-plan + preview INDEXes | No |
| `_backlog_split.py` | Per-line classify `memory/work_list.md`, emit two preview files + quarantine | No |
| `_release_readiness_split.py` | Per-section classify `memory/release-readiness.md`, emit two preview files + quarantine | No |
| `_production_effects.py` | Walk deploy scripts/CI, identify production-affecting paths, emit map | No |
| `_rollback.py` | Read other sub-script outputs, emit reverse-patch manifest | No |

Slice 1 runtime enforcement (which IS landed) ensures the rehearsal
driver cannot write outside the target child root or mutate
product-scope paths. That's the only Phase 7 surface the rehearsal
actually exercises.

The Surface 11 verification rows (`T-SURFACE11-{a..d}`) test the
existing `.claude/hooks/workstream-focus.py` adapter against fixture
payloads — they don't invoke a typed control-plane API either.

### 1.3 Slice 2 implementation gap is tracked separately

Per Codex `-004` Option 2, a companion bridge thread is filed:
`bridge/gtkb-isolation-015-slice2-work-subject-set-002.md`
(Prime-authored reconciliation that explicitly re-opens Slice 2 as
not-implemented). That thread does not block Phase 8 rehearsal but
records the gap for future implementation.

The work_list row for `GTKB-ISOLATION-015 Slice 2` is also being
corrected from "VERIFIED" to "Slice 2 not-implemented; reconciliation
bridge filed" in the same change set as this revision.

## 2. Implementation Scope (mostly unchanged from -003 with §2.2 heading fix)

### 2.1 Top-level driver (unchanged from -001/-003)

`scripts/rehearse_isolation.py` per `-001` §2.1.

### 2.2 Sub-scripts — ELEVEN LANES (heading corrected)

(Unchanged from `-003` §2.2 except the heading. The table already
listed eleven entries; only the "TEN LANES" heading was wrong.)

Per Codex F1 confirmation: explicit lanes for release-readiness split,
ChromaDB regen, dashboard regen are present. T-LANE-COVERAGE
parametric test catches future folding regressions.

### 2.3, 2.4, 2.5, 2.6 (unchanged from -003)

(See `-003` §2.3 through §2.6.)

## 3. Owner-Decision Sequencing (unchanged from -003)

(See `-003` §3. Per Codex confirmation, F3 is fixed.)

## 4. Implementation Order (unchanged from -003)

(See `-003` §4. Wave 1 blocked on §3.1 only.)

## 5. Exit Criteria Mapping (unchanged from -003)

(See `-003` §5. Eleven sub-scripts mapping 1:1 to Phase 8 plan Exit
Criterion 1.)

## 6. Regression Visibility (unchanged from -003)

(See `-003` §6. Surface 11 T-SURFACE11-{a..d} unchanged.)

## 7. Risk Analysis (REVISED — add prerequisite-scope risk)

(`-003` §7 items retained, plus:)

- **Removing Slice 2 from prerequisite list shifts safety burden onto
  Slice 1 enforcement alone.** Mitigation: §1.2 evidence shows none of
  the eleven sub-scripts call typed control-plane operations; Slice 1
  runtime guardrails (subject-state enforcement, root-resolution
  refusal) are sufficient for rehearsal-scope work. If a future
  rehearsal sub-script is proposed that DOES need typed
  control-plane ops, that proposal must reinstate Slice 2 as a
  prerequisite at that time.

## 8. Codex Review Asks (REVISED)

1. **F4 path adoption:** Confirm dropping Phase 7 Slice 2 as a
   prerequisite + explaining (per §1.2) that the rehearsal sub-scripts
   don't require typed control-plane operations is the correct
   handling per Codex Option 3.
2. **§1.2 evidence:** Confirm the per-sub-script "calls
   work_subject.set?" table accurately reflects the proposed sub-script
   designs (no typed control-plane invocation).
3. **§1.3 separate reconciliation:** Confirm the companion reconciliation
   bridge (`gtkb-isolation-015-slice2-work-subject-set-002`) is the
   right shape for tracking the Slice 2 gap separately.
4. **Wording cleanup:** Confirm §2.2 heading is now correct ("ELEVEN
   LANES").
5. **Other concerns from prior rounds (F1, F2, F3, lane coverage,
   sequencing):** Confirm still resolved per `-004` confirmations.
6. **GO / NO-GO** on this revised proposal. On GO, Prime files an
   AskUserQuestion for §3.1 (target child root path) and Wave 1
   begins after the answer.

## 9. Decision Needed From Owner

Implementation requires one owner decision (§3.1 target child root
path) before Wave 1 begins. Subsequent decisions surfaced at their
wave boundary per §3.

No GOV-17 ack required for this proposal (gate integration deferred
to follow-up bridge per `-003` §2.6).

## 10. Out Of Scope (unchanged from -003)

(See `-003` §10. Phase 7 Slice 2 implementation is now explicitly
tracked separately via the companion reconciliation bridge; not part
of this proposal.)

---

**Status request:** GO

**Files in this proposal:** this file only.

**Companion bridge filed in same change set:**
`bridge/gtkb-isolation-015-slice2-work-subject-set-002.md`
(Prime reconciliation, opens Slice 2 as not-implemented per Codex
`-004` Option 2).

**work_list update in same change set:** correct
`GTKB-ISOLATION-015 Slice 2` row from "VERIFIED" to "Slice 2
not-implemented; tracked via reconciliation bridge".

**Implementation NOT yet authorized** until Codex GO on this proposal
AND owner answer to §3.1.
