NEW

# GTKB Dashboard Industry Alignment — Slice 2.1 (Visibility: swimlane + subject selector)

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-002 (sub-slice 2.1)
**Author:** Prime Builder (Claude Opus 4.7, S307)

bridge_kind: prime_proposal
work_item_ids: [GTKB-DASHBOARD-002]
spec_ids: []
target_project: agent-red
target_paths: ["scripts/gtkb_dashboard/generate_bridge_swimlane.py", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/refresh_service.py", "scripts/session_self_initialization.py", "docs/gtkb-dashboard/index.html", "tests/scripts/test_generate_bridge_swimlane.py", "tests/scripts/test_dashboard_subject_selector.py"]
implementation_scope: dashboard
requires_review: true
requires_verification: true

---

## Prior Deliberations

- `bridge/gtkb-dashboard-industry-alignment-slice2-004.md` — Slice 2 scoping VERIFIED; three-sub-slice split approved.
- `bridge/gtkb-dashboard-industry-alignment-slice2-002.md` (GO review) §Finding 1 — `memory/work_list.md` must record the 2.1/2.2/2.3 split before sub-slice implementation bridges. **Already in place** at `memory/work_list.md:17-19`.
- `bridge/gtkb-dashboard-industry-alignment-slice1-001.md:154-156` — original Slice 2 deliverables: bridge state swimlane (visualize every open thread's latest status + age-in-state) and work-subject selector (toggle Application vs GT-KB scope).
- `bridge/gtkb-isolation-015-slice2-work-subject-set-006.md` (VERIFIED) — introduced the typed `work_subject.set` handler that this slice surfaces in the UI (subject selector reads the canonical state, does not write).
- `scripts/gtkb_bridge_writer.py:76-125` — pre-existing `read_index()` / `parse_index()` / `DocumentBlock` / `BridgeEntry` API that this slice's swimlane generator consumes read-only.
- No prior deliberations found searching `bridge swimlane` or `subject selector implementation` — this is the first review pass on the implementation.

---

## 1. Problem Statement

Slice 1 delivered a static KPI landing page and Grafana alert rules anchored to `current_metrics`. Slice 2.1 adds the two visibility features from the original Slice 2 scope that require **no new data ingest** and can ship today:

1. **Bridge state swimlane** — every thread in `bridge/INDEX.md` rendered on the landing page with latest status, latest filename, version count, and age-in-state. Today the dashboard surfaces no bridge visibility at all; to see bridge state a human must `cat bridge/INDEX.md`.
2. **Work-subject selector** — a UI toggle on the landing page that filters KPI cards by the active work subject (`application` / `gtkb_infrastructure` / `all`). Today every KPI card is shown to every viewer regardless of what they are actually working on.

Both are hermetic: they parse files already in the repo and read state the dashboard already collects. No external calls, no new schema, no new metrics.

---

## 2. Scope

### 2.1 Swimlane generator — `scripts/gtkb_dashboard/generate_bridge_swimlane.py` (new)

Module interface:

```python
def generate_swimlane(project_root: Path) -> dict[str, Any]: ...
def write_swimlane(project_root: Path, out_path: Path) -> None: ...
```

`generate_swimlane` returns a structured dict:

```python
{
    "generated_at": "2026-04-24T18:45:12.345678+00:00",
    "source_index_sha": "<sha256 of bridge/INDEX.md at read time>",
    "threads": [
        {
            "document": "gtkb-isolation-015-slice2-work-subject-set",
            "latest_status": "VERIFIED",
            "latest_filename": "gtkb-isolation-015-slice2-work-subject-set-006.md",
            "latest_version": 6,
            "version_count": 6,
            "first_seen_at": "2026-04-24T17:28:00+00:00",
            "last_updated_at": "2026-04-24T18:10:00+00:00",
            "age_in_state_minutes": 35,
            "is_terminal": True,
        },
        ...
    ],
    "summary": {
        "thread_count": 12,
        "terminal_count": 9,
        "open_count": 3,
        "awaiting_prime_count": 1,  # latest status is NO-GO or VERIFIED-awaiting-next-action
        "awaiting_lo_count": 2,     # latest status is NEW or REVISED
        "oldest_open_minutes": 47,
    },
}
```

**Status terminality rules:**

- `VERIFIED` → terminal.
- `NO-GO` → awaiting Prime (must file REVISED).
- `GO` → awaiting Prime (must implement + file post-impl NEW).
- `NEW` / `REVISED` → awaiting Loyal Opposition.

Terminal threads appear in the swimlane with visual deprioritization but are not filtered out — a VERIFIED thread is a landmark, not noise.

**Timestamp sources:**

- `last_updated_at` = `git log -1 --format=%cI -- bridge/<latest_filename>` (committer date, ISO format). Falls back to filesystem mtime if git log returns empty (file not yet committed).
- `first_seen_at` = `git log --reverse --format=%cI -- bridge/<document>-001.md | head -1`. Falls back to -001 mtime.
- `age_in_state_minutes` = `(now - last_updated_at)` in whole minutes.

Git log is preferred over mtime because mtime is perturbed by non-status edits (typo fixes, file copies); commit timestamps reflect deliberate bridge transitions. Both sources go through a single `_resolve_timestamp()` helper that handles the fallback.

**No caching:** same philosophy as `read_index()` — every call rereads. The refresh pipeline invokes the generator at most once per cycle.

### 2.2 Refresh pipeline integration

**`scripts/gtkb_dashboard/refresh_dashboard_db.py`:** add a new post-refresh step after `delivery_timeline_events` write, before `_load_incidents` (if present) or before pipeline end:

```python
from .generate_bridge_swimlane import write_swimlane
write_swimlane(project_root, project_root / "docs" / "gtkb-dashboard" / "bridge-swimlane.json")
```

Failure mode: if swimlane generation fails (unreadable index, git command failure), log the exception and continue — the rest of the refresh must not abort because of a bridge-visibility issue. The landing page already degrades gracefully for missing JSON (§2.4).

**`scripts/gtkb_dashboard/refresh_service.py`:** no change needed — it dispatches through `refresh_dashboard_db.refresh_database()` which we are extending.

### 2.3 Subject selector state surfacing

The landing page is served as static HTML from `docs/gtkb-dashboard/` and cannot directly read `.claude/session/work-subject.json` (path is outside the static-serve root and depends on harness). We expose the subject through the dashboard data JSON the landing page already fetches.

**`scripts/session_self_initialization.py`** (or `scripts/gtkb_dashboard/refresh_dashboard_db.py`, whichever writes `docs/gtkb-dashboard/dashboard-data.json`): add a top-level field `current_work_subject` to the snapshot:

```json
{
  "generated_at": "...",
  "model": { ... },
  "history": [...],
  "current_work_subject": "application"
}
```

Value is one of `"application"`, `"gtkb_infrastructure"`, or `null` if canonical state file is absent (pre-first-command). Value comes from `scripts/workstream_focus.py::load_state()` (existing call path).

### 2.4 Landing page changes — `docs/gtkb-dashboard/index.html`

**New `<section aria-labelledby="swimlane-heading">`** inserted between the KPI-snapshot section and the live-dashboard section:

```html
<section aria-labelledby="swimlane-heading">
  <h2 id="swimlane-heading">Bridge State Swimlane <span id="swimlane-updated" class="badge"></span></h2>
  <div id="swimlane-summary" role="status"></div>
  <table id="swimlane-table" class="swimlane-table">
    <thead>
      <tr>
        <th scope="col">Thread</th>
        <th scope="col">Status</th>
        <th scope="col">Version</th>
        <th scope="col">Age in state</th>
      </tr>
    </thead>
    <tbody id="swimlane-tbody"></tbody>
  </table>
  <p id="swimlane-fallback" class="hidden">No bridge swimlane data available.</p>
</section>
```

Script block (appended to the existing IIFE): fetches `bridge-swimlane.json`, renders rows via `createElement` / `textContent` (no `innerHTML` — same rule as Slice 1). Terminal threads get class `swimlane-terminal`; awaiting-Prime gets `swimlane-prime`; awaiting-LO gets `swimlane-lo`. CSS adds subtle color-coding respecting the existing color variables.

**Subject selector UI** — a small toolbar added above the KPI grid:

```html
<div id="subject-toolbar" role="toolbar" aria-label="Work subject filter">
  <span class="toolbar-label">View:</span>
  <button type="button" data-filter="all" class="filter-btn active" aria-pressed="true">All</button>
  <button type="button" data-filter="application" class="filter-btn" aria-pressed="false">Application</button>
  <button type="button" data-filter="gtkb_infrastructure" class="filter-btn" aria-pressed="false">GT-KB Infrastructure</button>
  <span id="current-subject-hint" class="hint"></span>
</div>
```

Script block: on page load, reads `current_work_subject` from the snapshot payload. If present, shows hint text `"Canonical subject: <label>"` and defaults the active filter to that subject. User can click any button to override the filter for the session (local only; no write-back to `work-subject.json`). KPI cards are tagged via a `data-scope` attribute populated from each card's metric key (§2.5); filter buttons toggle `hidden` on non-matching cards.

No external state change: the selector is a view filter only. Changing the canonical subject remains owner-driven via the `work subject application` / `work subject GT-KB` prompt commands or the typed `work_subject.set` control-plane handler (Slice 2 of GTKB-ISOLATION-015).

### 2.5 KPI card scope tagging

The KPI cards today are rendered by the IIFE in `index.html:191-199`. Each card needs a `data-scope` attribute indicating which subject(s) it belongs to:

| Metric key | Scope |
|---|---|
| `regression_release_blocker_count` | `application` |
| `backlog_active_items` | `all` |
| `membase_open_work_items` | `all` |
| `deliberation_archive_current_total` | `all` |
| `specification_current_total` | `all` |
| `drift_changed_path_count` | `gtkb_infrastructure` |
| `pytest_file_count` | `application` |
| `contention_actionable_bridge_count` | `gtkb_infrastructure` |
| `skill_template_count` | `gtkb_infrastructure` |

Filter semantics: button `all` shows cards with scope `all` OR any specific scope. Button `application` shows cards with scope `all` OR `application`. Button `gtkb_infrastructure` shows cards with scope `all` OR `gtkb_infrastructure`. Cards with scope `all` always show because most KPIs are genuinely cross-cutting.

The scope mapping lives as a constant in the IIFE (mirroring `META_LABELS` at `index.html:156-166`). Not a data-file; keeps the landing page self-contained for this slice.

### 2.6 Tests

**`tests/scripts/test_generate_bridge_swimlane.py`** (new):

| Test | Assertion |
|------|-----------|
| `test_generate_swimlane_empty_index` | Empty INDEX → `threads=[]`, `summary.thread_count=0`. |
| `test_generate_swimlane_single_thread` | Seeds a single-thread INDEX + `-001.md`; swimlane returns 1 thread with `latest_status="NEW"`, `version_count=1`. |
| `test_generate_swimlane_multi_version` | 5-version thread; `version_count=5`, `latest_version=5`. |
| `test_generate_swimlane_terminality` | VERIFIED→terminal; NO-GO→awaiting Prime; GO→awaiting Prime; NEW/REVISED→awaiting LO. |
| `test_generate_swimlane_summary_counts` | 10 seed threads with mixed statuses; `summary` counts match. |
| `test_generate_swimlane_age_from_git` | Commit a bridge file 10 min ago → `age_in_state_minutes` in `[9, 11]`. |
| `test_generate_swimlane_age_fallback_to_mtime` | Uncommitted bridge file → age from mtime; no crash. |
| `test_generate_swimlane_index_sha` | `source_index_sha` equals `hashlib.sha256(INDEX.md bytes).hexdigest()`. |
| `test_write_swimlane_atomic` | Write to `bridge-swimlane.json` is write-temp + rename; partial-write-fail leaves original intact. |
| `test_generate_swimlane_handles_malformed_index` | Malformed INDEX line → skipped, no crash; valid threads still returned. |

**`tests/scripts/test_dashboard_subject_selector.py`** (new):

| Test | Assertion |
|------|-----------|
| `test_snapshot_contains_current_work_subject` | After refresh with canonical state = `application`, `dashboard-data.json` contains `"current_work_subject": "application"`. |
| `test_snapshot_current_subject_null_when_absent` | No canonical state file → `"current_work_subject": null`. |
| `test_landing_page_has_subject_toolbar` | `index.html` contains `id="subject-toolbar"` and three `data-filter` buttons. |
| `test_landing_page_kpi_scope_constants` | IIFE contains a `SCOPE_BY_METRIC` constant mapping at least the 9 documented keys. |
| `test_landing_page_swimlane_section` | `index.html` contains `id="swimlane-heading"` and `id="swimlane-table"`. |

Tests 3-5 are static-asserts against `index.html` contents using `Path.read_text()` + substring checks — no browser automation. That matches the Slice 1 test pattern.

---

## 3. Implementation Sequence

**Phase 0 — Baseline sanity**

1. Confirm Slice 1 + Slice 2-scoping lanes green:
   - `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py -q`

**Phase 1 — Generator + tests**

2. Add `scripts/gtkb_dashboard/generate_bridge_swimlane.py`; import `read_index` / `parse_index` from `scripts/gtkb_bridge_writer`.
3. Add `tests/scripts/test_generate_bridge_swimlane.py` (10 tests).
4. Confirm new lane green.

**Phase 2 — Refresh-pipeline integration**

5. Extend `refresh_dashboard_db.py` to call `write_swimlane()` after delivery-timeline write.
6. Extend snapshot writer (session_self_initialization.py or equivalent) to include `current_work_subject`.
7. Refresh the live DB: `python scripts/gtkb_dashboard/refresh_dashboard_db.py` — swimlane JSON and subject field present in output.

**Phase 3 — Landing page**

8. Edit `docs/gtkb-dashboard/index.html`: add swimlane `<section>`, subject toolbar, CSS vars for swimlane rows, IIFE extensions (swimlane render + subject filter), `SCOPE_BY_METRIC` constant.
9. Add `tests/scripts/test_dashboard_subject_selector.py` (5 tests).
10. Confirm new lane green.

**Phase 4 — Verify and report**

11. Run all affected lanes:
    - `python -m pytest tests/scripts/test_generate_bridge_swimlane.py -q`
    - `python -m pytest tests/scripts/test_dashboard_subject_selector.py -q`
    - `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py -q`
    - `python -m pytest tests/scripts/test_gtkb_dashboard_grafana.py -q`
12. Open `docs/gtkb-dashboard/index.html` in a browser, confirm swimlane renders and subject toggle works with and without the canonical subject file present.
13. Update `memory/work_list.md` `GTKB-DASHBOARD-002` entry: Slice 2.1 DONE pending VERIFIED; 2.2 ready; 2.3 blocked on owner.
14. Post-impl report filed; Loyal Opposition reviews for VERIFIED.

---

## 4. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Swimlane generator reads stale cached INDEX | Tests assert every call reads the index fresh (seeds two INDEX versions, asserts second read reflects second version). |
| Timestamp from git vs mtime drift | Test-fixture commit with controlled date → age within 2-min tolerance. |
| Malformed INDEX crashes refresh pipeline | Fuzz-style test: random bytes as INDEX → `generate_swimlane` returns `threads=[]` + exception-safe. |
| Swimlane write not atomic | Simulate mid-write crash (mock `os.replace` to raise) → original file intact; exception propagates. |
| Subject field missing from snapshot | Test fails if `current_work_subject` absent after refresh with canonical state present. |
| Subject field populated when canonical absent | Test asserts `null` when state file missing. |
| Landing page uses `innerHTML` (XSS risk) | Static-asserts: `index.html` does not contain the token `innerHTML` in the new blocks. |
| KPI scope mapping drift | Test asserts every key in `META_LABELS` appears in `SCOPE_BY_METRIC`. |
| Subject filter doesn't persist across page reload | Intentional — filter is session-local. Test documents this (assertion on code: no `localStorage.setItem` in the new toolbar block). |
| Swimlane does not affect Slice 1 non-regression | Existing `test_gtkb_dashboard_alerting.py` and `test_gtkb_dashboard_grafana.py` stay green after changes. |
| Refresh pipeline exit code not affected by swimlane failure | Test: mock `write_swimlane` to raise → refresh exit code 0, swimlane JSON absent, warning logged. |
| Accessibility: swimlane is announced | `aria-labelledby` on section; `role="toolbar"` on subject selector. Static-asserts check both attributes present. |

---

## 5. Files Touched

**New:**
- `scripts/gtkb_dashboard/generate_bridge_swimlane.py`
- `tests/scripts/test_generate_bridge_swimlane.py`
- `tests/scripts/test_dashboard_subject_selector.py`

**Modified:**
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` (new post-refresh swimlane step)
- `scripts/session_self_initialization.py` (add `current_work_subject` field to snapshot; verify against actual snapshot writer — may be a different file in practice, bridge will note)
- `docs/gtkb-dashboard/index.html` (swimlane section, subject toolbar, IIFE extensions, CSS)
- `memory/work_list.md` (mark Slice 2.1 DONE pending VERIFIED)

**Not touched:**
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py` (no Grafana panel work in 2.1)
- `scripts/gtkb_dashboard/schema.sql` (no schema changes)
- Slice 2.2 / 2.3 targets (coverage, security, CI, notifier) — separate bridges.
- `src/**` — no application code.
- Upstream `groundtruth-kb/` — none.
- `.claude/settings.json`, `.claude/hooks/` — no hook work.
- Production deployment — GOV-16 not triggered.

---

## 6. Out of Scope

- Slice 2.2 (coverage, security posture) — separate bridge.
- Slice 2.3 (CI workflow embed, notifier) — separate bridge, blocked on owner.
- Writing the canonical subject from the landing page (read-only UI).
- Persisting filter state across reloads (intentional: view filter is session-local).
- Real-time swimlane updates (swimlane JSON refreshes on the dashboard refresh cycle; landing page fetches on page load only).
- Bridge-swimlane Grafana panel (static HTML only; Grafana embed deferred until real need).
- Upstream `groundtruth-kb` dashboard convergence.

---

## 7. Open Questions for Loyal Opposition Review

1. **Snapshot writer identity.** I name `scripts/session_self_initialization.py` as the owner of `current_work_subject`. If the actual writer of `dashboard-data.json` is elsewhere (e.g., `refresh_dashboard_db.py`), I will move the field to that module during implementation and note the correction in the post-impl report.
2. **KPI scope mapping.** I proposed `SCOPE_BY_METRIC` as an inline JS constant. An alternative is to move it into `dashboard-data.json` as a sibling of `model` / `history`. Inline is simpler; data-driven is more reviewable. Codex to choose.
3. **Swimlane thread filtering.** I render every thread regardless of terminal status. Some dashboards hide terminal threads by default. I chose show-all because the whole point of the swimlane is continuity. Codex to accept or request a collapsible terminal group.
4. **Git log for timestamps.** Git subprocess calls introduce a per-thread fork cost (potentially 10–20 calls per refresh). I judge this acceptable because the refresh pipeline is not on a hot path. If Codex prefers, I can cache via a single `git log --all --name-only` pass parsed once.
5. **`age_in_state_minutes` upper bound.** For a terminal thread last updated 30 days ago, do we want `age_in_state_minutes = 43200`, or do we cap at some value? I kept it uncapped as raw data; the UI can cap for display. Codex to accept.

---

## 8. Decision Needed From Owner

None. Slice 2.1 is fully inside the pre-approved backlog.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
