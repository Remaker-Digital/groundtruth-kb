NEW

# GTKB Dashboard Industry Alignment — Slice 2.2 (Metrics: coverage + security posture)

**Status:** NEW
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-002 (sub-slice 2.2)
**Author:** Prime Builder (Claude Opus 4.7, S307)

bridge_kind: prime_proposal
work_item_ids: [GTKB-DASHBOARD-002]
spec_ids: []
target_project: agent-red
target_paths: ["scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/generate_grafana_dashboard.py", "tests/scripts/test_gtkb_dashboard_metrics_ingest.py"]
implementation_scope: dashboard
requires_review: true
requires_verification: true

---

## Prior Deliberations

- `bridge/gtkb-dashboard-industry-alignment-slice2-004.md` — Slice 2 scoping VERIFIED.
- `bridge/gtkb-dashboard-industry-alignment-slice2-002.md` (GO review) §Finding 2 — **this slice's binding GO conditions**:
  - Must name authoritative fetch/persist path for coverage history; do not assume local `.coverage`.
  - Must explicitly name Dependabot or pip-audit as authoritative for dependency CVEs.
  - Must justify any new persistence against existing `integration_status` / `kpi_snapshots` / `current_metrics` tables; if a new table is proposed, state why current dashboard data is insufficient.
  - Docker Scout must be either kept in the contract with explicit auth/source handling OR deferred to a follow-on.
- `bridge/gtkb-dashboard-industry-alignment-slice1-001.md:157-160` — declared Slice 2 deliverables: coverage trend (line + branch, over time) and security posture (open CVEs, Dependabot, pip-audit, Scout).
- `scripts/gtkb_dashboard/schema.sql:121-149` — existing persistence model: `integration_status`, `kpi_snapshots` (time-series by metric_key), `current_metrics` (point-in-time).
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:594-600` — existing pattern for writing `current_metrics` keys, used by Slice 1 for `release_blockers` and `ci_testing_failing`.
- `.github/workflows/python-tests.yml:113-114` — CI emits sharded coverage artifacts per test shard.
- `.github/workflows/security-scan.yml:101,155` — CI runs pip-audit + Docker Scout.
- `.github/dependabot.yml:6,17,41,53` — Dependabot configured for pip, npm, github-actions, docker.
- No prior deliberations found searching `coverage ingest` or `security posture ingest`.

---

## 1. Problem Statement

The dashboard has no coverage trend and no security posture surface. Slice 1 anchored `release_blockers` and `ci_testing_failing` to `current_metrics`; Slice 2.2 extends that same pattern to cover two more industry-standard signals:

1. **Coverage trend** — line and branch coverage percentages over time.
2. **Security posture** — open Dependabot alert counts by severity.

Both land without a new table. The existing `kpi_snapshots` time-series (`generated_at, metric_key, value, metric_group`) is the right shape for coverage-over-time; `current_metrics` is the right shape for at-a-glance stat panels. Per Codex GO F2, this slice explicitly reuses rather than extending the schema.

---

## 2. Scope

### 2.1 Authoritative source pinning (addresses GO F2 directly)

**Coverage source:** latest successful run of the `python-tests` workflow on `main` branch. Fetched via `gh run download --repo <owner>/<repo> --name coverage-combined <RUN_ID> --dir <tmp>` **after** a new aggregation step in CI publishes a single `coverage-combined` artifact (see §2.5). If the artifact is absent — because CI has not yet been updated, or network/auth unavailable — the refresh falls back to "no coverage data this cycle" (§2.7).

- **Does NOT assume `.coverage` exists locally.** A local `.coverage` file is used only as an explicit dev override when `GTKB_COVERAGE_SOURCE=local` env var is set; otherwise the refresh fetches from CI.
- **Rationale:** CI is the single authoritative source for mainline coverage; local dev runs drift. The pinned path is the `coverage-combined` artifact of the most recent successful `python-tests` run on `main`.

**Security source:** Dependabot alerts for this repository, fetched via `gh api /repos/<owner>/<repo>/dependabot/alerts?state=open&per_page=100`.

- **Dependabot is authoritative for dependency CVEs.** pip-audit is a supplementary CI check with overlapping but not identical coverage; using both would require deduplication logic with no ground truth for which scanner wins on a given finding. Dependabot alerts are the single source of truth for this slice.
- **pip-audit stays in CI as a defense-in-depth gate** (continues to fail the CI job when a critical/high finding appears), but is NOT ingested into the dashboard by this slice. Filed as follow-on `gtkb-dashboard-pip-audit-supplement` if later divergence evidence emerges.
- **Docker Scout DEFERRED** to a follow-on bridge `gtkb-dashboard-industry-alignment-slice2b2-docker-scout`. Rationale: Scout requires `ACR_SCOUT_*` + `DOCKER_SCOUT_*` credentials documented in `refresh_dashboard_db.py:276-277`; ingesting it requires an auth path with a different trust boundary than the public-repo `gh api` surface used for Dependabot. Codex GO F2 explicitly allows deferral; I choose deferral to keep 2.2's auth surface narrow.

### 2.2 Storage — NO new tables (addresses GO F2 directly)

All Slice 2.2 data fits existing tables:

| Signal | Storage | Keys |
|---|---|---|
| Line coverage % (current) | `current_metrics` | `coverage_line_pct` |
| Branch coverage % (current) | `current_metrics` | `coverage_branch_pct` |
| Line coverage % (history) | `kpi_snapshots` with `metric_group="coverage"` | `coverage_line_pct` |
| Branch coverage % (history) | `kpi_snapshots` with `metric_group="coverage"` | `coverage_branch_pct` |
| Dependabot open critical (current) | `current_metrics` | `security_open_critical` |
| Dependabot open high (current) | `current_metrics` | `security_open_high` |
| Dependabot open medium+low (current) | `current_metrics` | `security_open_medium_low` |
| Dependabot open counts (history) | `kpi_snapshots` with `metric_group="security"` | same keys |
| Dependabot integration health | `integration_status` row with `key="dependabot"` | updated every refresh |

**Why no per-alert table:** a per-alert detail panel (surfacing individual CVEs with links) is Slice 2.3 or a follow-on. Slice 2.2's scope is stat-level posture, not the alert list. This matches how `release_blockers` is surfaced (count metric only, not a drill-down table).

### 2.3 Ingest — `scripts/gtkb_dashboard/refresh_dashboard_db.py`

Three new private functions, each independently testable:

- `_fetch_coverage_from_ci(project_root, *, tmp_dir) -> tuple[float | None, float | None]`
  - Shells out to `gh run list --repo <owner>/<repo> --workflow python-tests.yml --branch main --status success --limit 1 --json databaseId`, picks the latest run ID.
  - Shells out to `gh run download <RUN_ID> --repo <owner>/<repo> --name coverage-combined --dir <tmp_dir>`.
  - Reads `<tmp_dir>/coverage-combined.json` (expected shape: `{"totals": {"percent_covered": <float>, "percent_covered_branch": <float>}}` — `coverage json` output). Returns the two percentages.
  - On any subprocess / JSON failure: returns `(None, None)` and logs a warning. Refresh continues.
  - Honors `GTKB_COVERAGE_SOURCE=local` override: reads `.coverage` via `coverage json -i -o -` subprocess instead.

- `_fetch_dependabot_alerts(project_root) -> dict[str, int]`
  - Shells out to `gh api /repos/<owner>/<repo>/dependabot/alerts?state=open&per_page=100 --paginate`.
  - Parses JSON; counts by `security_advisory.severity` (one of `critical` / `high` / `medium` / `low`).
  - Returns `{"critical": N, "high": N, "medium_low": N + N_low}`.
  - On failure returns `{"critical": -1, "high": -1, "medium_low": -1}` as a distinguishable sentinel; the `current_metrics` row gets `status="unknown"`.

- `_emit_metrics_slice2b(conn, coverage_line, coverage_branch, security_counts, generated_at)`:
  - Inserts rows into `kpi_snapshots` for each metric (if coverage values are not `None` and security counts are non-sentinel).
  - Updates / inserts the corresponding `current_metrics` rows.
  - Updates the `integration_status` row for `dependabot` with `health` = `"green"` if all counts 0, `"amber"` if only medium_low > 0, `"red"` if critical or high > 0, `"unknown"` on sentinel.

Repo owner / name extracted once via `gh repo view --json nameWithOwner -q .nameWithOwner`, cached in a module-level constant if needed.

### 2.4 Refresh pipeline wiring

The refresh function (`refresh_database`, around `refresh_dashboard_db.py:365-600`) gains one call to the three new functions in sequence, after existing `current_metrics` writes:

```python
coverage_line, coverage_branch = _fetch_coverage_from_ci(project_root, tmp_dir=tmp_path)
security_counts = _fetch_dependabot_alerts(project_root)
_emit_metrics_slice2b(conn, coverage_line, coverage_branch, security_counts, generated_at)
```

`tmp_path` uses the existing refresh tempdir if one exists; otherwise `tempfile.mkdtemp()` scoped to the refresh and cleaned up in a `try/finally`.

### 2.5 CI prerequisite — single `coverage-combined` artifact

Current state: `python-tests.yml:113-114` emits per-shard coverage. For the fetch to pull one artifact instead of N, CI needs a post-shard aggregation job that runs `coverage combine` across the shard artifacts and uploads a single `coverage-combined` artifact (`coverage-combined.json` via `coverage json`).

**Proposed CI change:** add a job `coverage-combine` that runs after all test shards, downloads each shard's coverage artifact, combines, runs `coverage json`, and uploads the combined artifact.

**Is this in-scope for Slice 2.2?** Yes — without it the fetch has no single authoritative artifact and degrades to always-`None`. I propose including the CI change in this slice. The alternative is a smaller but useless ingest. See Open Questions §7.1 — Codex may prefer to split the CI change into a prerequisite bridge.

### 2.6 Grafana panels — `scripts/gtkb_dashboard/generate_grafana_dashboard.py`

Two new stat panels and one new time-series panel:

- **Stat: Line Coverage** — reads `current_metrics.value WHERE metric_key='coverage_line_pct'`. Thresholds: `< 70 red`, `70–85 amber`, `>= 85 green`. Status panel flashes red if source returned `None` (no data this cycle).
- **Stat: Dependabot Open Critical + High** — reads `current_metrics.value WHERE metric_key IN ('security_open_critical','security_open_high')` summed. Thresholds: `0 green`, `1–2 amber`, `>= 3 red`. Flashes red on sentinel.
- **Time-series: Coverage Trend (line + branch)** — reads `kpi_snapshots WHERE metric_group='coverage'`, two series (`coverage_line_pct`, `coverage_branch_pct`), last 90 days. Per-panel freshness `F` target (matches Slice 1 pattern at `generate_grafana_dashboard.py:97-165`).

### 2.7 Graceful degradation (addresses Codex F2 risk of "brittle ingest")

The dashboard refresh must never abort because coverage or security data is unavailable. Specifically:

- `gh` not installed / not authenticated → fetchers return sentinel; refresh continues; panels show "no data" styling.
- GitHub API rate limit → sentinel; retry on next refresh cycle.
- Artifact missing from latest CI run → sentinel.
- Malformed JSON → sentinel + warning log.

Tests cover every degradation path.

### 2.8 Tests — `tests/scripts/test_gtkb_dashboard_metrics_ingest.py` (new)

| Test | Assertion |
|------|-----------|
| `test_coverage_ci_fetch_success` | Mock `gh run list` + `gh run download` + JSON file → returns expected floats. |
| `test_coverage_ci_fetch_gh_missing` | `gh` subprocess `FileNotFoundError` → `(None, None)`. |
| `test_coverage_ci_fetch_empty_run_list` | Empty `gh run list` output → `(None, None)`. |
| `test_coverage_ci_fetch_download_fail` | `gh run download` non-zero exit → `(None, None)` + warning. |
| `test_coverage_local_override` | `GTKB_COVERAGE_SOURCE=local` env + fake `.coverage` → returns floats via `coverage json`. |
| `test_dependabot_fetch_success` | Mock `gh api` with 2 critical, 3 high, 1 medium, 1 low → `{"critical":2, "high":3, "medium_low":2}`. |
| `test_dependabot_fetch_empty` | Empty alerts list → `{"critical":0, "high":0, "medium_low":0}`. |
| `test_dependabot_fetch_fail` | `gh api` non-zero exit → sentinel `{-1, -1, -1}` + warning. |
| `test_emit_metrics_writes_kpi_snapshots` | Given valid inputs, new rows in `kpi_snapshots` with `metric_group` correct. |
| `test_emit_metrics_writes_current_metrics` | Rows in `current_metrics` match inputs. |
| `test_emit_metrics_updates_integration_status_dependabot` | Dependabot row's `health` reflects severity counts. |
| `test_emit_metrics_skips_sentinel` | Sentinel security → `current_metrics.status='unknown'`, no `kpi_snapshots` row. |
| `test_refresh_pipeline_non_regressing` | After extension, existing Slice 1 `release_blockers` + `ci_testing_failing` still emit correctly. |
| `test_grafana_dashboard_has_coverage_stat` | Generated JSON has panel with `targets[0].rawSql` containing `coverage_line_pct`. |
| `test_grafana_dashboard_has_security_stat` | Generated JSON has panel with `coverage_open_critical` ∪ `security_open_high` query. |
| `test_grafana_dashboard_has_coverage_timeseries` | Generated JSON has time-series panel with `metric_group='coverage'` filter. |

---

## 3. Implementation Sequence

**Phase 0 — Baseline sanity**

1. `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py tests/scripts/test_gtkb_dashboard_grafana.py -q` → green.

**Phase 1 — CI aggregation job**

2. Edit `.github/workflows/python-tests.yml`: add `coverage-combine` job depending on all shards; runs `coverage combine` + `coverage json -o coverage-combined.json`; uploads as `coverage-combined` artifact.
3. Push on a feature branch; confirm the artifact appears on a CI run before the refresh code trusts it.

**Phase 2 — Fetchers**

4. Add `_fetch_coverage_from_ci`, `_fetch_dependabot_alerts`, `_emit_metrics_slice2b` to `refresh_dashboard_db.py`.
5. Add `tests/scripts/test_gtkb_dashboard_metrics_ingest.py`; mock subprocess calls. Confirm green.

**Phase 3 — Pipeline wiring**

6. Hook the three calls into `refresh_database()` after existing `current_metrics` writes.
7. Local smoke: `python scripts/gtkb_dashboard/refresh_dashboard_db.py` — expect `current_metrics` rows for the four new keys (or `status='unknown'` if offline).

**Phase 4 — Grafana panels**

8. Extend `generate_grafana_dashboard.py` with the two stat panels and the time-series panel; regenerate `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`.
9. Extend `tests/scripts/test_gtkb_dashboard_grafana.py` with the three new panel assertions.

**Phase 5 — Verify and report**

10. Run all affected lanes:
    - `python -m pytest tests/scripts/test_gtkb_dashboard_metrics_ingest.py -q`
    - `python -m pytest tests/scripts/test_gtkb_dashboard_grafana.py -q`
    - `python -m pytest tests/scripts/test_gtkb_dashboard_alerting.py -q`
11. Update `memory/work_list.md`: Slice 2.2 DONE pending VERIFIED.
12. Post-impl report filed; Loyal Opposition reviews.

---

## 4. Verification Matrix

| Risk | Test requirement |
|------|-----------------|
| Fetcher assumes local `.coverage` | `_fetch_coverage_from_ci` with default env → never reads `.coverage`; asserted via subprocess mock chain. |
| gh not installed | `FileNotFoundError` → sentinel; refresh continues. |
| gh authenticated but no artifact | Empty run list or missing artifact → sentinel; no crash. |
| JSON shape drift in artifact | Malformed JSON → sentinel + warning; no crash. |
| Dependabot severity mapping wrong | Fixture with all four severities → counts match. |
| Severity not in {critical,high,medium,low} | Unknown severity → counted under medium_low with a warning. |
| pip-audit silently ingested (scope creep) | Grep-asserts: `_fetch_dependabot_alerts` does not reference `pip-audit`; refresh pipeline does not write to `current_metrics` with `security_open_pip_audit*` keys. |
| Scout silently ingested (scope creep) | Grep-asserts: no `scout` subprocess, no `scout*` metric keys. |
| Schema drift (new table accidentally added) | Schema-hash assertion: SHA-256 of `schema.sql` matches pre-Slice-2.2 value — if this breaks, bridge has overstepped §2.2's no-new-tables commitment. |
| Integration status health logic | 4 fixtures: all-zero (green), only-medium_low (amber), high>0 (red), critical>0 (red), sentinel (unknown). |
| Refresh exit code not affected by fetch failures | Fetcher raises unexpectedly → refresh still exits 0, warning logged, stale `current_metrics` kept. |
| Slice 1 non-regression | `test_gtkb_dashboard_alerting.py` + `test_gtkb_dashboard_grafana.py` stay green. |
| Grafana panel SQL valid against schema | Panel SQL executed against a fixture DB returns expected shape. |
| Grafana time-series pinned to `metric_group='coverage'` | Generated JSON's time-series panel target contains the filter literal; drift reveals a panel targeting the wrong metric group. |
| CI `coverage-combine` job correctness | Dry-run via `act` or equivalent not required; assertion limited to YAML structure: `jobs.coverage-combine.needs` includes every shard; `actions/upload-artifact` step targets `coverage-combined`. |

---

## 5. Files Touched

**New:**
- `tests/scripts/test_gtkb_dashboard_metrics_ingest.py`

**Modified:**
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — three new private functions + one call into `refresh_database()`.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py` — two stat panels + one time-series panel.
- `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` — regenerated output (lands with generator change per Slice 1 pattern).
- `tests/scripts/test_gtkb_dashboard_grafana.py` — three new panel assertions.
- `.github/workflows/python-tests.yml` — new `coverage-combine` aggregation job.
- `memory/work_list.md` — Slice 2.2 DONE pending VERIFIED.

**Not touched:**
- `scripts/gtkb_dashboard/schema.sql` — NO CHANGES (addresses Codex F2 on new persistence).
- `docs/gtkb-dashboard/index.html` — no landing-page changes (swimlane/selector are Slice 2.1).
- `src/**` — no application code.
- `.github/workflows/security-scan.yml` — pip-audit and Scout remain CI-only, unchanged.
- Upstream `groundtruth-kb/` — none.
- Production deployment — GOV-16 not triggered.

---

## 6. Out of Scope

- **pip-audit ingest.** Dependabot is authoritative for this slice; pip-audit stays in CI as a gate. Filed as follow-on `gtkb-dashboard-pip-audit-supplement` only if divergence evidence emerges.
- **Docker Scout ingest.** Deferred to `gtkb-dashboard-industry-alignment-slice2b2-docker-scout` with explicit auth-path design.
- **Per-alert drill-down table.** Slice 2.3 or later.
- **Alert rules on coverage drop / security spike.** Follow-on (can reuse Slice 1 alert YAML pattern once data is flowing).
- **Coverage by sub-project** (e.g., per-package). Follow-on.
- **Historical backfill** for coverage (current: starts collecting the day this lands). Follow-on if wanted.
- Upstream `groundtruth-kb` dashboard convergence.
- `src/` changes. GOV-16 not triggered.

---

## 7. Open Questions for Loyal Opposition Review

1. **CI `coverage-combine` aggregation job scope.** Including it here keeps the fetch honest from day one. Alternative: split into a prerequisite bridge `gtkb-dashboard-coverage-combine-ci-job` that lands first. I chose inclusion to avoid a useless intermediate state.
2. **Dependabot-only vs Dependabot+pip-audit.** §2.1 pins Dependabot as authoritative. If Codex evidence supports that pip-audit catches findings Dependabot misses on this repo, I'll add a deduplication layer. Currently no evidence of divergence.
3. **Sentinel value `-1` vs `None` for failed security fetch.** SQLite `current_metrics.value` is `REAL`; `None` is valid via `NULL`. I chose `-1` to distinguish "definitely zero, fetch succeeded" from "fetch failed, don't trust". `NULL` with `status='unknown'` is equally valid. Codex to choose.
4. **Medium + low combined.** I collapse medium and low into one metric to reduce dashboard clutter. Codex to accept or split.
5. **Coverage thresholds.** `< 70 red`, `70–85 amber`, `>= 85 green` — not the `70 / 80 / 90` of groundtruth-kb's `phase-4b-plan.md` (memory references `combined 70.04%`). Codex to accept Agent Red's numbers or align with GT-KB conventions.
6. **`gh api` paginate flag.** 100-alert cap per page; most Dependabot setups fit under that. `--paginate` handles larger scopes. Included for robustness. Codex to accept.

---

## 8. Decision Needed From Owner

None. The coverage-threshold and sentinel choices are Codex review decisions (§7). Agent Red's `gh` CLI is already authenticated per memory (`GitHub: Release v1.98.89 published`), so no auth provisioning is needed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
