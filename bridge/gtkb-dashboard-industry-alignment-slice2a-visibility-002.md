NO-GO

# Loyal Opposition Review - GTKB Dashboard Industry Alignment Slice 2.1 (Visibility)

**Date:** 2026-04-24
**Document:** `gtkb-dashboard-industry-alignment-slice2a-visibility`
**Reviewed file:** `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-001.md`
**Verdict:** NO-GO

## Prior Deliberations

No prior deliberations found for `GTKB-DASHBOARD-002`, `bridge swimlane`, `subject selector`, or `dashboard industry alignment` in the Deliberation Archive search against `groundtruth.db`.

## Claim

The proposed Slice 2.1 split is directionally correct, but the current design does not yet carry the work-subject selector through the actual static-dashboard data path. As written, the landing page will not receive the canonical subject value under the normal `dashboard-data.json` shape, and the verification sequence is pointed at the wrong producer for that JSON.

## Findings

### Finding 1 (HIGH) - The proposed `current_work_subject` field is attached to the wrong payload layer for the current landing-page reader

**Evidence**

- The proposal says the snapshot writer should add `current_work_subject` as a top-level sibling of `model` and `history` in `dashboard-data.json`: `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-001.md:121-132`.
- The same proposal says the landing page script will read `current_work_subject` from the "snapshot payload": `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-001.md:171-173`.
- The current landing page does not render the top-level payload. `selectLatest(payload)` returns the last `history` row whenever `history` exists: `docs/gtkb-dashboard/index.html:168-173`.
- The rendered object is therefore a snapshot row, not the root JSON object: `docs/gtkb-dashboard/index.html:236-239`.
- Snapshot rows come from `_snapshot_from_model()`, and that function currently emits only KPI/timestamp fields; it does not carry any work-subject field: `scripts/session_self_initialization.py:2647-2665`.

**Risk / impact**

The primary "subject selector defaults to canonical subject" behavior will not work in the normal case where `dashboard-data.json` includes history. A raw-file assertion can still pass while the UI silently falls back to the wrong default state, which makes the feature look implemented while failing its actual operator-facing contract.

**Required action**

Pick one durable contract and wire all three layers to it:

1. Add the subject field to the snapshot/history shape emitted by `_snapshot_from_model()`, or
2. Change the landing page to read the root payload instead of only the selected history snapshot.

Then add a verification that exercises the same object the page actually renders, not just the raw root JSON.

### Finding 2 (MEDIUM) - The verification sequence is wired to the wrong producer for `dashboard-data.json`

**Evidence**

- The implementation sequence says to extend the snapshot writer with `current_work_subject`, then run `python scripts/gtkb_dashboard/refresh_dashboard_db.py` and expect both the swimlane JSON and the subject field to be present in output: `bridge/gtkb-dashboard-industry-alignment-slice2a-visibility-001.md:241-243`.
- `refresh_dashboard_db.py` is the SQLite refresh path; the loaded implementation evidence here shows it populates dashboard tables such as `delivery_timeline_events`, `release_blockers`, `quality_rollup`, `risk_register`, and `current_metrics`: `scripts/gtkb_dashboard/refresh_dashboard_db.py:516-626`.
- The actual writer for `docs/gtkb-dashboard/dashboard-data.json` is `write_dashboard_and_report()` in `session_self_initialization.py`: `scripts/session_self_initialization.py:4645-4664`.

**Risk / impact**

The bridge can appear green after a DB refresh even if the static landing-page JSON was never regenerated with the new subject field. That creates a false verification path and invites stale `dashboard-data.json` drift between the SQLite-backed Grafana surfaces and the static landing page this slice is explicitly modifying.

**Required action**

Pin the owner/writer contract in the implementation bridge:

1. Name the exact function/module that must emit the subject field for the static page.
2. Update the verification commands so they regenerate the same artifact the page fetches.
3. Add a test that proves the page-facing JSON changes after the intended writer runs.

## Recommended Action

Revise the bridge so the subject-selector data path is end-to-end coherent:

- define whether `current_work_subject` lives in the snapshot rows or the root payload,
- make the landing page read that exact contract,
- verify through the page-facing artifact writer rather than the SQLite refresh alone.

The swimlane portion can remain in this slice, but the selector path needs this contract correction before GO.

## Decision Needed From Owner

None.
