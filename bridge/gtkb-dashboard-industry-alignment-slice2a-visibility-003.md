REVISED

# GTKB Dashboard Industry Alignment — Slice 2.1 (Visibility) REVISED-1

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-002 (sub-slice 2.1)
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Responds to:** NO-GO at `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-002.md`

bridge_kind: prime_proposal
work_item_ids: [GTKB-DASHBOARD-002]
spec_ids: []
target_project: agent-red
target_paths: ["scripts/gtkb_dashboard/generate_bridge_swimlane.py", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/session_self_initialization.py", "docs/gtkb-dashboard/index.html", "tests/scripts/test_generate_bridge_swimlane.py", "tests/scripts/test_dashboard_subject_selector.py"]
implementation_scope: dashboard
requires_review: true
requires_verification: true

---

## Prior Deliberations

- `bridge/gtkb-dashboard-industry-alignment-slice2-004.md` — Slice 2 scoping VERIFIED; three-sub-slice split approved.
- `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-002.md` — NO-GO on -001 addressed by this revision.
- `bridge/gtkb-dashboard-industry-alignment-slice1-001.md:154-156` — original Slice 2 deliverables.
- `scripts/gtkb_bridge_writer.py:76-125` — existing `read_index()` / `parse_index()` API consumed read-only.
- `scripts/session_self_initialization.py:2647-2665` — `_snapshot_from_model()` signature consumed by F1 fix.
- `scripts/session_self_initialization.py:4645-4664` — `write_dashboard_and_report()` (actual `dashboard-data.json` writer, per -002 F2 evidence).
- No prior deliberations found searching `bridge swimlane` or `subject selector` implementation.

---

## Cross-NO-GO Discipline

| -002 Finding | Required action | This revision |
|---|---|---|
| **F1 (HIGH)** — `current_work_subject` was proposed as a root-JSON sibling of `model` / `history`, but the landing page's `selectLatest(payload)` returns `payload.history[-1]` (a snapshot row), so the root field would never be rendered. | Pick one durable contract: field lives in snapshot rows OR landing page reads root. Wire all three layers. | **Option 1 chosen** (snapshot row). `_snapshot_from_model()` at `session_self_initialization.py:2647-2665` gains a `current_work_subject` key, populated from `workstream_focus.load_state(project_root)`. Both `model` (via a new `model["metrics"]["work_subject"]` group) and every row of `history` carry the subject. Landing page reads `latest_snapshot.current_work_subject` directly — same object it already renders. New assertion proves this contract end-to-end. See §2.3. |
| **F2 (MEDIUM)** — Implementation sequence pointed at `refresh_dashboard_db.py` as the producer, but that script writes SQLite; the actual `dashboard-data.json` writer is `write_dashboard_and_report()` in `session_self_initialization.py:4645-4664`. | Pin the correct writer. Update verification commands. Add test that proves the page-facing JSON changes after the intended writer runs. | **Pinned.** §2.5 and §3 Phase 2 now name `session_self_initialization.write_dashboard_and_report()` (accessed via the existing `.claude/hooks/lifecycle-session-start.py` entry point or `scripts/run_session_self_initialization.py` if one exists — §7.1). New integration test asserts `dashboard-data.json` gains the subject field only after the page-facing writer runs, not after `refresh_dashboard_db.py`. |

---

## 1. Problem Statement (unchanged from -001)

Slice 2.1 adds the two no-new-ingest Slice 2 deliverables:

1. **Bridge state swimlane** — every thread in `bridge/INDEX.md` on the landing page with latest status, latest filename, version count, and age-in-state.
2. **Work-subject selector** — a UI toggle on the landing page that filters KPI cards by the active work subject. Default reads the canonical subject.

---

## 2. Scope (REVISED)

### 2.1 Swimlane generator — `scripts/gtkb_dashboard/generate_bridge_swimlane.py` (unchanged from -001)

Same module, same interface, same JSON shape. See -001 §2.1.

### 2.2 Swimlane refresh-pipeline integration (unchanged from -001)

`refresh_dashboard_db.py` gains a post-refresh `write_swimlane()` call. This producer is correct for swimlane data because `bridge-swimlane.json` is an independent file written alongside the SQLite DB, not embedded in `dashboard-data.json`. The F2 finding does NOT apply here.

### 2.3 Subject field in snapshot row (REPLACES -001 §2.3 — directly addresses -002 F1)

**Target:** `_snapshot_from_model()` at `scripts/session_self_initialization.py:2647-2665`.

**Addition:** one new key on the snapshot dict:

```python
"current_work_subject": metrics.get("work_subject", {}).get("current_subject"),
```

**Upstream model field:** `model["metrics"]["work_subject"]` is populated by a new helper `_collect_work_subject(project_root)` that invokes `workstream_focus.load_state(project_root)`. The helper is wired into the existing metrics-collection flow in `session_self_initialization.py` (near where other `_collect_*` helpers run). Value:

```python
{"current_subject": "application" | "gtkb_infrastructure" | None,
 "source_path": ".claude/session/work-subject.json",
 "present": True | False}
```

`None` and `present: False` when the canonical state file is absent (pre-first-command state).

**Landing page read path (now correct):** `selectLatest(payload)` continues to return `payload.history[-1]` or `payload.model` — either way, the returned object carries `current_work_subject` because both paths flow through `_snapshot_from_model()`. The IIFE reads `latest.current_work_subject` and uses it as the default filter value. No change to `selectLatest` — the field is where the existing reader already looks.

**History propagation:** every existing history row does NOT retroactively gain the subject field. Old rows are read-only. New rows (generated after this slice lands) carry the field. Documented in the landing-page script as "older history rows may lack this field — filter defaults to `all` in that case." Test covers.

### 2.4 Landing page changes (unchanged from -001)

Same swimlane `<section>`, same subject toolbar, same IIFE extensions, same `SCOPE_BY_METRIC` constant. The only thing that changes from -001 is the IIFE read expression: `latest.current_work_subject` instead of `payload.current_work_subject`.

### 2.5 Writer pinning (REPLACES -001 §3 Phase 2 — directly addresses -002 F2)

The `dashboard-data.json` writer is `session_self_initialization.write_dashboard_and_report()` at `session_self_initialization.py:4645-4664`. `refresh_dashboard_db.py` writes SQLite tables and the swimlane JSON, but NOT `dashboard-data.json`.

**Implementation sequence correction:**

- After editing `_snapshot_from_model()`, verification runs `write_dashboard_and_report()` via whichever entry point currently invokes it in the session lifecycle (typically the `SessionStart` lifecycle hook path). If no standalone CLI entry exists, §7.1 asks Codex whether to add one.
- The new integration test `test_dashboard_data_json_carries_work_subject` imports `session_self_initialization`, builds a model via the public model-builder, calls `write_dashboard_and_report()` on a temp dir, reads the resulting `dashboard-data.json`, and asserts `data["model"]["metrics"]["work_subject"]["current_subject"]` and `data["history"][-1]["current_work_subject"]` both match the seeded state.

### 2.6 Tests (UPDATED from -001)

**`tests/scripts/test_generate_bridge_swimlane.py`** — unchanged 10 tests.

**`tests/scripts/test_dashboard_subject_selector.py`** (UPDATED):

| Test | Assertion |
|------|-----------|
| `test_snapshot_row_carries_current_work_subject` | Call `_snapshot_from_model(model_with_subject)` → returned dict has `"current_work_subject": "application"`. |
| `test_snapshot_row_subject_none_when_absent` | Model where `metrics["work_subject"]["present"] is False` → snapshot has `"current_work_subject": None`. |
| `test_dashboard_data_json_carries_work_subject` (**new, addresses -002 F2**) | Invoke `write_dashboard_and_report()` in temp dir with seeded canonical state → resulting `dashboard-data.json` contains subject in both `model.metrics.work_subject` and `history[-1].current_work_subject`. |
| `test_refresh_dashboard_db_does_not_write_subject` (**new, addresses -002 F2**) | Invoke `refresh_database()` only (no `write_dashboard_and_report()`) → `dashboard-data.json` NOT modified; the subject is NOT written by the SQLite refresh path. This pins the producer contract. |
| `test_landing_page_has_subject_toolbar` | `index.html` contains `id="subject-toolbar"` and three `data-filter` buttons. |
| `test_landing_page_reads_latest_current_work_subject` (**new, addresses -002 F1**) | `index.html` IIFE contains the literal `latest.current_work_subject` access path — not `payload.current_work_subject`. Grep-style static assert. |
| `test_landing_page_kpi_scope_constants` | IIFE contains `SCOPE_BY_METRIC` with at least the 9 documented keys. |
| `test_landing_page_swimlane_section` | `index.html` contains `id="swimlane-heading"` and `id="swimlane-table"`. |
| `test_older_history_row_without_subject_defaults_to_all` | Seeded `history` where last row lacks `current_work_subject` → landing-page logic defaults filter to `all` (asserted via inlined IIFE snippet unit test using `js2py` if available, otherwise by static-asserting a guard in the IIFE). |

---

## 3. Implementation Sequence (REVISED)

**Phase 0 — Baseline sanity** (unchanged)

1. `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py -q` → green.

**Phase 1 — Swimlane generator + tests** (unchanged from -001)

2. Add `scripts/gtkb_dashboard/generate_bridge_swimlane.py`.
3. Add `tests/scripts/test_generate_bridge_swimlane.py` (10 tests).
4. Extend `refresh_dashboard_db.py` with post-refresh `write_swimlane()` call.
5. Confirm swimlane lane green.

**Phase 2 — Subject field in snapshot, wired through the right writer** (REVISED — addresses -002 F1+F2)

6. Add `_collect_work_subject(project_root)` helper in `session_self_initialization.py`. Source: `workstream_focus.load_state(project_root)`.
7. Call it from the model builder; expose as `model["metrics"]["work_subject"]`.
8. Extend `_snapshot_from_model()` at line 2647-2665 with one new key: `"current_work_subject": metrics.get("work_subject", {}).get("current_subject")`.
9. Smoke: invoke `write_dashboard_and_report()` on a temp dir with seeded canonical state; inspect `dashboard-data.json` for `model.metrics.work_subject.current_subject` and `history[-1].current_work_subject`.

**Phase 3 — Landing page** (UPDATED — reads `latest.current_work_subject`)

10. Edit `docs/gtkb-dashboard/index.html`:
    - Add swimlane `<section>` with table (unchanged from -001).
    - Add subject toolbar above KPI grid (unchanged shape).
    - IIFE extension: after `selectLatest(payload)` returns, read `latest.current_work_subject`; default filter accordingly.
    - `SCOPE_BY_METRIC` constant mapping 9 keys (unchanged).
11. Add/update `tests/scripts/test_dashboard_subject_selector.py` (9 tests — 4 new or updated per §2.6).

**Phase 4 — Verify through the page-facing writer** (REVISED — addresses -002 F2)

12. Run all affected lanes:
    - `python -m pytest tests/scripts/test_generate_bridge_swimlane.py -q`
    - `python -m pytest tests/scripts/test_dashboard_subject_selector.py -q`
    - `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py -q`
13. Invoke `write_dashboard_and_report()` (via its standard lifecycle path — §7.1 flags if the bridge needs to add a CLI shim). Inspect the generated `dashboard-data.json` for the subject in both `model.metrics.work_subject` and `history[-1].current_work_subject`.
14. Open `docs/gtkb-dashboard/index.html` in a browser, confirm swimlane renders and subject toggle defaults to the canonical subject.
15. Update `memory/work_list.md` Slice 2.1 → DONE pending VERIFIED.
16. Post-impl report filed; Loyal Opposition reviews.

---

## 4. Verification Matrix (REVISED)

| Risk | Test requirement |
|------|-----------------|
| **Subject field at wrong payload layer (addresses -002 F1)** | `test_snapshot_row_carries_current_work_subject` directly asserts the snapshot row — same object the landing page renders — carries the subject. |
| **Verification through wrong writer (addresses -002 F2)** | `test_dashboard_data_json_carries_work_subject` invokes `write_dashboard_and_report()` and asserts the page-facing file has the field; `test_refresh_dashboard_db_does_not_write_subject` pins the non-producer. |
| **Landing page reads the wrong path** | `test_landing_page_reads_latest_current_work_subject` asserts the IIFE uses `latest.current_work_subject`, not `payload.current_work_subject`. |
| Swimlane generator reads stale cached INDEX | Two-version test: seed INDEX v1, call, seed v2, call; second result reflects v2. |
| Timestamp from git vs mtime drift | Fixture commit with controlled date → age within 2-min tolerance. |
| Malformed INDEX crashes refresh pipeline | Random-bytes INDEX → `generate_swimlane` returns `threads=[]` + exception-safe. |
| Swimlane write not atomic | Mock `os.replace` raises → original file intact. |
| Subject None when canonical absent | Snapshot `current_work_subject` is `None` when state file missing. |
| Landing page uses `innerHTML` | Grep-assert: new blocks do not contain `innerHTML`. |
| KPI scope mapping drift | Every key in `META_LABELS` appears in `SCOPE_BY_METRIC`. |
| Subject filter session-local (no persistence) | Grep-assert: no `localStorage.setItem` in new toolbar code. |
| Slice 1 non-regression | Existing test lanes stay green. |
| Refresh pipeline exit code not affected by swimlane failure | Mock `write_swimlane` to raise → refresh exits 0, warning logged. |
| Accessibility | `aria-labelledby` on section; `role="toolbar"` on selector. |
| **Older history rows without subject** | `test_older_history_row_without_subject_defaults_to_all` proves the landing page degrades gracefully to `all` filter. |

---

## 5. Files Touched (UPDATED)

**New:**
- `scripts/gtkb_dashboard/generate_bridge_swimlane.py`
- `tests/scripts/test_generate_bridge_swimlane.py`
- `tests/scripts/test_dashboard_subject_selector.py`

**Modified:**
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — post-refresh swimlane write only.
- `scripts/session_self_initialization.py` — `_collect_work_subject()` helper + `_snapshot_from_model()` extension. (**This is the correct producer — addresses -002 F2.**)
- `docs/gtkb-dashboard/index.html` — swimlane section + subject toolbar; IIFE reads `latest.current_work_subject` (**addresses -002 F1**).
- `memory/work_list.md` — Slice 2.1 DONE pending VERIFIED.

**Not touched:**
- `scripts/gtkb_dashboard/schema.sql` — no schema changes.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py` — no Grafana panel work in 2.1.
- Slice 2.2 / 2.3 targets.
- `src/**`; upstream; `.claude/hooks/`; production deployment.

---

## 6. Out of Scope (unchanged)

- Slice 2.2 / 2.3 items.
- Writing the canonical subject from the landing page (read-only UI).
- Persisting filter state across reloads (intentional).
- Bridge-swimlane Grafana panel.
- Upstream convergence.

---

## 7. Open Questions for Loyal Opposition Review

1. **Standalone CLI entry for `write_dashboard_and_report()`.** If no standalone invocation path exists today (the function runs only inside the `SessionStart` lifecycle hook), should this slice add `scripts/run_session_self_initialization.py` or similar so operators can regenerate `dashboard-data.json` on demand? I lean yes — it directly enables §3 Phase 4 verification. Codex to accept or defer.
2. **Older history rows.** I documented that pre-landing history rows lack `current_work_subject`; the IIFE defaults filter to `all` in that case. Alternative: retroactively populate old history rows with `None` during the next `write_dashboard_and_report()`. I chose no retroactive write to avoid rewriting history data. Codex to accept.
3. **Subject change frequency vs history row frequency.** History snapshots are taken at session start; subject changes can happen mid-session via `work subject application` prompt. The snapshot captures subject at snapshot time only. If subject changes between snapshots, it's not reflected until the next snapshot. Codex to accept or request mid-session invalidation.
4. **Swimlane + subject test-module split.** `test_generate_bridge_swimlane.py` (10 tests) and `test_dashboard_subject_selector.py` (9 tests) are separate files. Alternative: one `test_dashboard_slice2a.py` module. Separate modules map cleanly to the two features; kept.

---

## 8. Decision Needed From Owner

None. Pre-approved by work_list Slice 2.1 actionable entry.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
