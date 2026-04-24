NEW

# GTKB-ISOLATION-015 — Phase 7 Integration Slice 1: Post-Implementation Report

**Status:** NEW (post-implementation report for Loyal Opposition VERIFIED review)
**Date:** 2026-04-24
**Work item:** GTKB-ISOLATION-015 (Slice 1 of 2 — does not close the WI)
**Author:** Prime Builder (Claude Opus 4.7, S306 capped-spawn)
**Implements proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-007.md`
**Approved at:** `bridge/gtkb-isolation-015-phase7-full-integration-008.md` (GO)

---

## Scope Statement (per GO Required Action Item #3)

This report covers **Slice 1** only:

- §A — subject-labeled startup / readiness / test outputs + hard-rejection of
  unlabeled combined green claims at the readiness/report layer
- §B — bridge live-state writer / validator (`scripts/gtkb_bridge_writer.py`)
- §C — overlay-aware startup status (informational absent, WARNING on
  stale/root/subject/projection mismatch; never canonical)
- §E — multi-harness counterpart-state detection
- Backlog annotation: `memory/work_list.md` updated with Slice 1/Slice 2/§F
  routing

This report **does not** claim closure of `GTKB-ISOLATION-015`. The durable
backlog entry remains open pending Slice 2 (typed `work_subject.set`
control-plane handler, separate bridge under the same WI). §F (upstream
clean-adopter delivery) is owned by `GTKB-ISOLATION-017` Phase 9 adopter
packaging.

---

## Required Action Items — Verification Matrix

| Action Item from -008 GO | Disposition |
|---|---|
| 1. Repair known-red `tests/scripts/test_session_self_initialization.py` baseline before adding new assertions | **Done Phase 0.** All 7 monkeypatched `discover_role_profile` lambdas (lines 690, 763, 833, 876, 916, 1057, 1140) now accept `**kwargs`. Post-Phase-0 count: 23 passed, 0 failed, 0 skipped. |
| 2. Update `memory/work_list.md` to reflect Slice 1/Slice 2 split | **Done.** `GTKB-ISOLATION-015` entry now carries a "Slice split" subsection citing `-007 REVISED-3` and `-008 GO`, enumerating Slice 1 deliverables, Slice 2 deferred scope, and §F routing to `GTKB-ISOLATION-017`. |
| 3. Keep post-impl report scoped to Slice 1; do not claim `GTKB-ISOLATION-015` closure | **Done.** This report scope statement explicitly flags that `-015` stays open pending Slice 2. |

---

## Implementation Summary

### §A — Subject-labeled outputs + hard-rejection

**`scripts/workstream_focus.py`** (modified):

- Added `TOPOLOGY_MODE_SINGLE`, `TOPOLOGY_MODE_MULTI`, `TOPOLOGY_MODE_DEFAULT`
  constants and a `_TOPOLOGY_MODES` set for validation.
- Extended `_canonical_default()` to emit `topology_mode`.
- Extended `load_state()` to preserve and normalize `topology_mode` from the
  canonical file (invalid values fall back to `TOPOLOGY_MODE_DEFAULT`).
- Extended `startup_focus_snapshot()` to surface `role_slot` and
  `topology_mode` in the snapshot dict.
- Extended `render_startup_focus_lines()` to emit `Bridge role slot:` and
  `Harness topology:` lines, a first-owner-message stimulus reminder, and a
  live bridge authority line naming `bridge/INDEX.md` as the canonical
  handoff/review record.
- Added `render_active_work_subject(project_root, *, snapshot=None,
  overlay_status=None, include_counterpart=True)` composing focus lines +
  overlay note (§C) + counterpart warnings (§E).
- Added `SubjectScopeError` exception class and
  `assert_readiness_subject_scope(application_green, gtkb_green,
  dual_scope_declared, context)` function that hard-rejects unlabeled
  combined green claims at the readiness/report layer.

**`scripts/session_self_initialization.py`** (modified):

- Added imports for `SubjectScopeError`, `assert_readiness_subject_scope`,
  and `render_active_work_subject` (both normal and direct-script fallback
  paths).
- `_render_current_project_state()` now emits subject-labeled lines
  (`Application release blockers:` / `GT-KB release blockers:`,
  `Application Testing/tool rollup:`, etc.), `Bridge role slot:`, and
  `Harness topology:`. Calls `assert_readiness_subject_scope()` with
  `dual_scope_declared` + `subject_readiness.application_green/gtkb_green`
  from `dashboard_intelligence` — raises `SubjectScopeError` on
  combined-green claims that lack an explicit dual-scope declaration.
- `render_report()` now calls `render_active_work_subject(snapshot=...,
  overlay_status=..., include_counterpart=True)` for the `### Active Work
  Subject` section.

### §B — Bridge live-state writer / validator

**`scripts/gtkb_bridge_writer.py`** (new):

- `BridgeEntry`, `DocumentBlock` dataclasses; `parse_index()`, `read_index()`,
  `get_block()` for fresh-read INDEX parsing (never cached).
- `next_file_number(document, project_root)` — max of live index versions and
  on-disk `bridge/<doc>-NNN.md` versions, plus one.
- `validate_transition(document, proposed_status, role_slot, project_root)`
  — enforces the full writer-authority transition table from `-005` / `-007`.
  Rejections are categorized (invalid status, wrong writer role, unknown role
  slot, VERIFIED terminal, Prime-NEW-only-on-new-or-post-GO,
  Prime-REVISED-only-after-NO-GO, LO-GO/NO-GO-only-after-NEW/REVISED,
  LO-VERIFIED-only-after-post-impl-NEW).
- `write_bridge_file(document, version, content, project_root)` — refuses to
  overwrite an existing file (raises `BridgeConflictError`) and re-reads the
  file after write to verify content integrity.
- `insert_index_status(document, version, status, project_root,
  expected_index_raw=None)` — optional stale-snapshot rejection via
  `expected_index_raw`; post-write re-reads the INDEX and asserts the new
  line is visible and is the newest entry for the document.

### §C — Overlay-aware startup status

`overlay_startup_note(status)` in `scripts/workstream_focus.py`:

- `overlay_present=False` → `{"level": "info", "lines": ["No session overlay
  active; …"]}`.
- `overlay_present=True` plus any of `is_stale`, `root_mismatch`,
  `subject_mismatch`, `projection_diff` → `{"level": "warning", "lines":
  [...]}` with a trailing "Session overlays are never canonical for
  Deliberation Archive, MemBase, bridge, or readiness decisions." reminder.
- Fresh present overlay → informational "canonical state lives in
  KB/MemBase/Deliberation Archive/source files."

Rendered into the Active Work Subject block via `render_active_work_subject`.

### §E — Multi-harness counterpart-state detection

`detect_counterpart_state(project_root=None)` in `scripts/workstream_focus.py`:

- Reads per-harness `operating-role.md` active_role values using
  `HARNESS_ROLE_RECORDS` (codex + claude).
- Same role slot across harnesses → WARNING ("counterpart bridge roles may
  collide").
- Different role slots → informational WARNING describing the split ("X is
  prime-builder; counterpart Y is loyal-opposition. Treat bridge message
  authority per operating-role.md").
- Missing counterpart file → no warning, no crash.

### Backlog annotation

`memory/work_list.md` — `GTKB-ISOLATION-015` entry now carries a **Slice
split** subsection citing `-007 REVISED-3` (written) and `-008 GO`, naming
Slice 1 deliverables, Slice 2 deferred scope (typed control-plane handler),
and §F routing to `GTKB-ISOLATION-017`.

---

## Files Touched (commit-local delta)

**New (untracked, will be added in the forthcoming commit):**

- `scripts/gtkb_bridge_writer.py`
- `tests/scripts/test_gtkb_bridge_writer.py`
- `bridge/gtkb-isolation-015-phase7-full-integration-009.md` (this report)

**Modified:**

- `scripts/workstream_focus.py` (§A, §C, §E additions)
- `scripts/session_self_initialization.py` (§A imports + subject-labeled
  state render + hard-rejection integration + `render_active_work_subject`
  call site)
- `tests/scripts/test_session_self_initialization.py` (Phase 0 monkeypatch
  repair + 5 new `_render_current_project_state` integration tests covering
  application labels, GT-KB labels, hard-rejection on unlabeled combined
  green, permitted dual-scope combined green, permitted single-subject
  green)
- `tests/hooks/test_workstream_focus.py` (17 new regression tests for
  enriched startup lines, topology_mode persistence, overlay-note mapping,
  counterpart-state detection, `render_active_work_subject` composition,
  and `assert_readiness_subject_scope` hard-rejection semantics)
- `memory/work_list.md` (Slice split annotation)
- `bridge/INDEX.md` (new NEW line for `-009`)

**Not touched (confirming out-of-scope boundary):**

- `scripts/gtkb_dashboard/control_plane_registry.py` — §D typed
  `work_subject.set` handler is Slice 2, separate bridge.
- `src/` — no application source changes. GOV-16 not triggered.
- Upstream `groundtruth-kb/` — §F is owned by `GTKB-ISOLATION-017`.

---

## Test Evidence

All four lanes run from the Agent Red workspace, latest execution
2026-04-24:

```text
python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
→ 28 passed in 0.27s

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
→ 34 passed, 3 skipped in 0.45s

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
→ 13 passed in 0.66s

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
→ 28 passed, 1 warning in 225.42s (0:03:45)
```

**Combined:** 103 passed, 3 skipped, 0 failed, 0 errors across all four
lanes. No regressions in pre-existing tests.

### New test nodes added (class-qualified where applicable)

`tests/hooks/test_workstream_focus.py` (17 new):

- `test_startup_focus_lines_include_role_slot_topology_mode_stimulus_and_bridge_authority`
- `test_save_state_persists_topology_mode_default`
- `test_overlay_startup_note_absent_is_informational`
- `test_overlay_startup_note_stale_is_warning`
- `test_overlay_startup_note_root_mismatch_is_warning`
- `test_overlay_startup_note_subject_mismatch_is_warning`
- `test_overlay_startup_note_projection_diff_is_warning`
- `test_overlay_startup_note_never_canonical_phrasing`
- `test_detect_counterpart_state_no_counterpart_files_no_warning`
- `test_detect_counterpart_state_same_role_warns`
- `test_detect_counterpart_state_different_role_warns`
- `test_detect_counterpart_state_missing_counterpart_no_crash`
- `test_render_active_work_subject_combines_focus_overlay_and_counterpart`
- `test_assert_readiness_subject_scope_hard_rejects_unlabeled_combined_green`
- `test_assert_readiness_subject_scope_permits_dual_scope_declaration`
- `test_assert_readiness_subject_scope_permits_single_green`

`tests/scripts/test_session_self_initialization.py` (5 new):

- `test_render_current_project_state_labels_application_headers`
- `test_render_current_project_state_labels_gtkb_headers`
- `test_render_current_project_state_hard_rejects_unlabeled_combined_green`
- `test_render_current_project_state_permits_dual_scope_combined_green`
- `test_render_current_project_state_permits_single_subject_green`

`tests/scripts/test_gtkb_bridge_writer.py` (28, pre-staged, all passing):
`test_parse_index_extracts_blocks_and_order`,
`test_parse_index_skips_comments_and_blank_lines`,
`test_next_file_number_new_document`,
`test_next_file_number_with_gap_in_index`,
`test_next_file_number_includes_disk_files_not_in_index`,
`test_prime_new_on_new_document_accepted`,
`test_prime_new_after_go_accepted`,
`test_prime_new_after_no_go_rejected`,
`test_prime_new_after_revised_rejected`,
`test_prime_new_after_verified_rejected`,
`test_prime_revised_after_no_go_accepted`,
`test_prime_revised_after_new_rejected`,
`test_lo_go_after_new_accepted`, `test_lo_go_after_revised_accepted`,
`test_lo_go_after_go_rejected`, `test_lo_verified_after_new_accepted`,
`test_lo_verified_after_go_rejected`, `test_prime_cannot_write_go`,
`test_lo_cannot_write_new`, `test_unknown_role_slot_rejected`,
`test_invalid_status_rejected`, `test_any_transition_after_verified_rejected`,
`test_write_bridge_file_creates_and_verifies`,
`test_write_bridge_file_rejects_existing`,
`test_insert_index_status_prepends_in_document_block`,
`test_insert_index_status_detects_stale_snapshot`,
`test_insert_index_status_fails_when_document_block_missing`,
`test_insert_index_status_rejects_invalid_status`.

---

## Verification Matrix Mapping (from -007 §4)

| -007 Risk | Evidence |
|---|---|
| Phase 0 baseline still red after repair | session_self_init lane 23→28 passed, 0 failed. |
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
| Counterpart subject diverges → WARNING | `test_detect_counterpart_state_different_role_warns`. |
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
