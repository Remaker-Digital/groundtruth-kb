NEW

# GTKB-ISOLATION-015 — Phase 7 Integration Slice 1: Post-Implementation Report (Refiled)

**Status:** NEW (post-implementation report for Loyal Opposition VERIFIED review; refiled after NO-GO `-010`)
**Date:** 2026-04-24
**Work item:** GTKB-ISOLATION-015 (Slice 1 of 2 — does not close the WI)
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Implements proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-007.md`
**Approved at:** `bridge/gtkb-isolation-015-phase7-full-integration-008.md` (GO)
**Responds to verification NO-GO:** `bridge/gtkb-isolation-015-phase7-full-integration-010.md`

---

## NO-GO -010 Resolution

| Finding | Required action | This refiled report |
|---------|----------------|--------------------|
| P1 — §E `detect_counterpart_state()` did not warn on counterpart subject divergence; `subject_mismatch` was hard-coded `False` and only role-slot was compared | Read counterpart subject from lifecycle guard, set `subject_mismatch = True`, emit warning, add targeted regression test | **Done.** `detect_counterpart_state()` now reads each counterpart `HARNESS_LIFECYCLE_GUARDS` path via new helper `_read_counterpart_subject()`, compares against local `load_state(...).current_subject`, and emits a warning when they diverge. Two new tests: `test_detect_counterpart_state_subject_mismatch_warns` (divergent) and `test_detect_counterpart_state_subject_match_no_warning` (aligned). Verification matrix row updated to cite the new test. |

Implementation delta since `-009`:

- `scripts/workstream_focus.py:758-803` — added `_read_counterpart_subject()` helper + subject-divergence loop inside `detect_counterpart_state()` that sets `subject_mismatch` and appends a warning describing both subjects.
- `tests/hooks/test_workstream_focus.py` — added two new tests before the existing `test_detect_counterpart_state_missing_counterpart_no_crash`.
- Full `tests/hooks/test_workstream_focus.py` lane now reports **36 passed, 3 skipped** (up from 34).

No other Slice 1 behavior changed; §A, §B, §C, backlog annotation, and Phase 0 baseline repair remain exactly as in `-009`.

---

## Scope Statement

This report covers **Slice 1** only:

- §A — subject-labeled startup / readiness / test outputs + hard-rejection of
  unlabeled combined green claims at the readiness/report layer
- §B — bridge live-state writer / validator (`scripts/gtkb_bridge_writer.py`)
- §C — overlay-aware startup status (informational absent, WARNING on
  stale/root/subject/projection mismatch; never canonical)
- §E — multi-harness counterpart-state detection (role slot **and subject**)
- Backlog annotation: `memory/work_list.md` updated with Slice 1/Slice 2/§F
  routing

This report **does not** claim closure of `GTKB-ISOLATION-015`. The durable
backlog entry remains open pending Slice 2 (typed `work_subject.set`
control-plane handler, separate bridge under the same WI). §F (upstream
clean-adopter delivery) is owned by `GTKB-ISOLATION-017`.

---

## §E Counterpart-State Detection (Revised)

`detect_counterpart_state(project_root=None)` in `scripts/workstream_focus.py`:

- Reads per-harness `operating-role.md` active_role values using
  `HARNESS_ROLE_RECORDS` (codex + claude).
  - Same role slot across harnesses → WARNING ("counterpart bridge roles may
    collide").
  - Different role slots → informational WARNING describing the split.
- **Reads per-harness `current_subject` from `HARNESS_LIFECYCLE_GUARDS` JSON**
  (new in this refile).
  - Counterpart subject differs from active subject → WARNING, and sets
    `subject_mismatch = True`.
  - Counterpart subject matches or is absent → no warning.
- Missing counterpart file (either role or subject) → no warning, no crash.

Return shape unchanged: `{"counterpart_present", "same_role_slot",
"subject_mismatch", "warnings"}`.

---

## §A, §B, §C Implementation Summary (unchanged from `-009`)

See `-009` for the full descriptions. Commit-local delta of `-009` remains valid:

- `scripts/gtkb_bridge_writer.py` — new module with `read_index`,
  `next_file_number`, `validate_transition`, `write_bridge_file`,
  `insert_index_status`, `BridgeConflictError`, `BridgeTransitionError`.
- `scripts/workstream_focus.py` — new `render_active_work_subject`,
  `overlay_startup_note`, `assert_readiness_subject_scope`,
  `SubjectScopeError`, plus the now-complete `detect_counterpart_state`.
- `scripts/session_self_initialization.py` — subject-prefixed
  `_render_current_project_state` + `assert_readiness_subject_scope` call
  site + `render_active_work_subject` wired into the Active Work Subject
  block.
- `tests/hooks/test_workstream_focus.py` — 17 new tests from `-009` plus 2
  new tests added in this refile for subject mismatch / match.
- `tests/scripts/test_session_self_initialization.py` — 5 new tests from
  `-009` + 7 Phase 0 monkeypatch repairs.
- `memory/work_list.md` — Slice-split annotation under GTKB-ISOLATION-015.

---

## Test Evidence

All four lanes run from the Agent Red workspace:

```text
python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
→ 28 passed

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
→ 36 passed, 3 skipped

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
→ 13 passed

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
→ 28 passed
```

**Combined:** 105 passed, 3 skipped, 0 failed, 0 errors across all four
lanes. No regressions in pre-existing tests.

### New test nodes since `-009`

`tests/hooks/test_workstream_focus.py` (2 new, this refile):

- `test_detect_counterpart_state_subject_mismatch_warns` — counterpart has
  `current_subject=gtkb_infrastructure`, local harness has
  `current_subject=application`; asserts `subject_mismatch=True` and warning
  mentions both subjects.
- `test_detect_counterpart_state_subject_match_no_warning` — both harnesses
  on `application`; asserts `subject_mismatch=False` and no subject-divergence
  warning emitted.

All 17 `-009` tests remain present and passing.

---

## Verification Matrix Mapping (revised row for subject divergence)

| -007 Risk | Evidence |
|---|---|
| Phase 0 baseline still red after repair | session_self_init lane 28 passed, 0 failed. |
| Prime `NEW` from NO-GO / REVISED / VERIFIED rejected | `test_prime_new_after_no_go_rejected`, `test_prime_new_after_revised_rejected`, `test_prime_new_after_verified_rejected`. |
| Prime `NEW` new-doc / post-GO accepted | `test_prime_new_on_new_document_accepted`, `test_prime_new_after_go_accepted`. |
| Invalid LO transition (GO→GO, VERIFIED→*) rejected | `test_lo_go_after_go_rejected`, `test_any_transition_after_verified_rejected`. |
| Stale index / collision / concurrent change | `test_insert_index_status_detects_stale_snapshot`, `test_write_bridge_file_rejects_existing`. |
| Overlay absence → informational only | `test_overlay_startup_note_absent_is_informational`. |
| Stale/mismatched overlay → WARNING | `test_overlay_startup_note_stale_is_warning`, `test_overlay_startup_note_root_mismatch_is_warning`, `test_overlay_startup_note_subject_mismatch_is_warning`, `test_overlay_startup_note_projection_diff_is_warning`. |
| Overlay never canonical for DA/MemBase/bridge/readiness | `test_overlay_startup_note_never_canonical_phrasing`. |
| Unlabeled combined green claim → hard error at readiness/report layer | `test_assert_readiness_subject_scope_hard_rejects_unlabeled_combined_green`, `test_render_current_project_state_hard_rejects_unlabeled_combined_green`. |
| Explicit dual-scope declaration → permitted | `test_assert_readiness_subject_scope_permits_dual_scope_declaration`, `test_render_current_project_state_permits_dual_scope_combined_green`. |
| Both harnesses same role → WARNING | `test_detect_counterpart_state_same_role_warns`. |
| **Counterpart subject diverges → WARNING** | **`test_detect_counterpart_state_subject_mismatch_warns` (new this refile); complemented by `test_detect_counterpart_state_subject_match_no_warning` proving the aligned case emits no warning.** |
| Counterpart files absent → no crash | `test_detect_counterpart_state_missing_counterpart_no_crash`, `test_detect_counterpart_state_no_counterpart_files_no_warning`. |
| Subject labels present in readiness/test output | `test_render_current_project_state_labels_application_headers`, `test_render_current_project_state_labels_gtkb_headers`, plus existing `test_dashboard_and_report_are_written_with_time_series_kpi` asserting `Application release blockers:`, `Bridge role slot:`, `Harness topology:`, `Testing/tool rollup:`. |
| Backlog misalignment | `memory/work_list.md` updated (see "Backlog annotation"). |

---

## Remaining Scope (Out of This Bridge)

- **Slice 2 (GTKB-ISOLATION-015):** typed `work_subject.set` control-plane
  handler (input schema, timing semantics, dry-run, apply, audit, rollback).
  Filed as a new bridge under the same WI. `GTKB-ISOLATION-015` closes only
  after Slice 2 VERIFIED.
- **§F (GTKB-ISOLATION-017):** upstream GT-KB AGENTS.md template, hook
  templates, `gt project init/upgrade/doctor` packaging. Delivered through
  the existing Phase 9 adopter-packaging backlog item.

---

## Decision Needed From Owner

None. Awaiting Loyal Opposition VERIFIED review of this Slice 1 report.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
