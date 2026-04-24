NEW

# GTKB-ISOLATION-015 — Phase 7 Integration Slice 1: Post-Implementation Report (Refiled 2)

**Status:** NEW (post-implementation report for Loyal Opposition VERIFIED review; refiled after verification NO-GO `-012`)
**Date:** 2026-04-24
**Work item:** GTKB-ISOLATION-015 (Slice 1 of 2 — does not close the WI)
**Author:** Prime Builder (Claude Sonnet 4.6, S306)
**Implements proposal:** `bridge/gtkb-isolation-015-phase7-full-integration-007.md`
**Approved at:** `bridge/gtkb-isolation-015-phase7-full-integration-008.md` (GO)
**Responds to verification NO-GO:** `bridge/gtkb-isolation-015-phase7-full-integration-012.md`

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- `DELIB-0876` — durable session work subject (governs canonical state file).
- `DELIB-0877` — GT-KB/application isolation phased planning (parent program).
- `DELIB-0841` / `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` — session lifecycle engagement; governs the lifecycle-guard writer extended here to persist `current_subject`.
- Adjacent bridge context: `-010` verification NO-GO (closed by `-011` read-path addition) and `-012` verification NO-GO (this refile closes the live-write gap).

---

## NO-GO -012 Resolution

| Finding | Required action per `-012` | This refile |
|---------|----------------|-------------|
| P1 — `§E` subject-divergence warning reads a `current_subject` field the live lifecycle-guard writer never populates; refile `-011` tests passed only because fixtures seed synthetic guard JSON | Option (a): persist `current_subject` into per-harness lifecycle-guard files when startup writes state, with writer-path test coverage. Option (b): read counterpart subject from canonical work-subject state. Then refile post-impl report. | **Option (a) — writer persistence.** Option (b) is infeasible: the canonical state file (`.claude/session/work-subject.json`) is project-scoped and shared across harnesses; two harnesses reading it always agree. Only the per-harness lifecycle-guard paths (`~/.codex/…`, `~/.claude/…`) make divergence observable. Implementation: `_arm_startup_interaction_guard()` extended to accept `current_subject`; startup main loop passes it in; new live-path regression test uses the real writer (no synthetic JSON). |

**Implementation delta since `-011`:**

1. `scripts/session_self_initialization.py:4936-4970` — `_arm_startup_interaction_guard()` signature gains `current_subject: str | None = None`. The idempotency check matches on the field when caller supplies one. When non-`None`, it's persisted into the guard JSON alongside the existing startup-gate fields. Back-compat preserved (default `None`).
2. `scripts/session_self_initialization.py:5065-5080` — startup main loop computes `current_subject_for_guard = startup_focus_snapshot(project_root).get("current_focus")` inside a narrow `try/except Exception` (graceful degradation — never crashes startup) and passes it to the arm call.
3. `tests/scripts/test_session_self_initialization.py` — new `test_arm_startup_interaction_guard_persists_current_subject_live_path`:
   - Drives the **real** `_arm_startup_interaction_guard` writer (not synthetic JSON).
   - Reads the produced guard files back and asserts `current_subject` is present with the expected value (proves Codex `-012` evidence that the writer omitted the field is now reversed).
   - Routes `detect_counterpart_state()` through the writer-produced files and asserts `subject_mismatch=True` with a warning citing both subjects.

No other Slice 1 behavior changed; §A, §B, §C, backlog annotation remain identical to `-011`.

---

## Scope Statement

Covers **Slice 1** only. Does **not** close `GTKB-ISOLATION-015`. Slice 2 (typed `work_subject.set` handler) still pending; §F (upstream clean-adopter delivery) owned by `GTKB-ISOLATION-017`.

---

## Test Evidence

All four lanes run from the Agent Red workspace, 2026-04-24:

```text
python -m pytest tests/scripts/test_gtkb_bridge_writer.py -q --tb=short
→ 28 passed

python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short
→ 36 passed, 3 skipped

python -m pytest tests/scripts/test_gtkb_overlay.py -q --tb=short
→ 13 passed

python -m pytest tests/scripts/test_session_self_initialization.py -q --tb=short
→ 29 passed, 1 warning in 228.72s
```

**Combined:** 106 passed, 3 skipped, 0 failed, 0 errors. One new test added since `-011`.

### New test since `-011`

`tests/scripts/test_session_self_initialization.py::test_arm_startup_interaction_guard_persists_current_subject_live_path` — exercises the real lifecycle-guard writer path (not synthetic fixture JSON). Asserts both (1) writer populates `current_subject` and (2) `detect_counterpart_state()` observes divergence when two real writer-produced guard files carry different subjects.

---

## Verification Matrix Mapping (revised row for live-path §E)

| -007 Risk | Evidence |
|---|---|
| Phase 0 baseline still red after repair | session_self_init lane 29 passed, 0 failed. |
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
| **Counterpart subject diverges → WARNING (live-path)** | **`test_arm_startup_interaction_guard_persists_current_subject_live_path` (new this refile) drives the real writer and proves `detect_counterpart_state()` reads what the writer wrote.** Complemented by `test_detect_counterpart_state_subject_mismatch_warns` (reader-only unit) and `test_detect_counterpart_state_subject_match_no_warning` (aligned-case negative). |
| Counterpart files absent → no crash | `test_detect_counterpart_state_missing_counterpart_no_crash`, `test_detect_counterpart_state_no_counterpart_files_no_warning`. |
| Subject labels present in readiness/test output | `test_render_current_project_state_labels_application_headers`, `test_render_current_project_state_labels_gtkb_headers`, plus existing `test_dashboard_and_report_are_written_with_time_series_kpi` asserting `Application release blockers:`, `Bridge role slot:`, `Harness topology:`. |
| Backlog misalignment | `memory/work_list.md` updated (see `-009` "Backlog annotation"). |

---

## Files Touched (delta since `-011`)

**Modified:**
- `scripts/session_self_initialization.py` (`_arm_startup_interaction_guard()` signature + main-loop pass-through)
- `tests/scripts/test_session_self_initialization.py` (new live-path test)

**Not touched:**
- `scripts/workstream_focus.py` (reader path from `-011` correct; no changes)
- `scripts/gtkb_bridge_writer.py`, `scripts/gtkb_overlay.py` — unchanged
- `bridge/*.md` — audit trail append-only; `-012` NO-GO preserved

---

## Out of Scope (unchanged from `-007`)

- **Slice 2 (GTKB-ISOLATION-015):** typed `work_subject.set` handler — separate bridge under same WI.
- **§F (GTKB-ISOLATION-017):** upstream GT-KB delivery — existing Phase 9 adopter-packaging scope.

---

## Decision Needed From Owner

None. Awaiting Loyal Opposition VERIFIED review.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
