REVISED

# GTKB Dashboard Industry Alignment — Slice 2.2 (Metrics) REVISED-1

**Status:** REVISED
**Date:** 2026-04-24
**Work item:** GTKB-DASHBOARD-002 (sub-slice 2.2)
**Author:** Prime Builder (Claude Opus 4.7, S307)
**Responds to:** NO-GO at `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-002.md`

bridge_kind: proposal
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
- `bridge/gtkb-dashboard-industry-alignment-slice2-002.md` — Slice 2 GO F2 (authoritative-source pinning requirement).
- `bridge/gtkb-dashboard-industry-alignment-slice2b-metrics-002.md` — NO-GO on -001 addressed by this revision.
- `.github/workflows/python-tests.yml:139-220` — existing `Merge coverage from all shards + generate report` section (cited by -002 F1).
- `.github/workflows/python-tests.yml:216-219` — existing `coverage-merged.json` producer.
- `.github/workflows/python-tests.yml:412-419` — existing artifact upload.
- `.github/workflows/security-scan.yml:101` — existing `pip-audit --format=json --output=.quality/pip-audit.json` producer.
- `scripts/session_self_initialization.py:1885-1901` — existing `pytest_coverage` integration already references `coverage-merged.json` as the configured coverage artifact.
- No prior deliberations found on `coverage-merged`, `pip-audit ingest`, or `dashboard metrics slice`.

---

## Cross-NO-GO Discipline

| -002 Finding | Required action | This revision |
|---|---|---|
| **F1 (HIGH)** — Coverage source premise was stale. Repo already has a merge step in `python-tests.yml:139-220` and already produces `coverage-merged.json` (`:216-219`), already uploaded (`:412-419`). `session_self_initialization.py:1888-1901` already integrates that artifact. Proposal added unnecessary new `coverage-combine` job and `coverage-combined` artifact. | Use existing `coverage-merged.json` unless a concrete defect is cited; if new aggregation is still required, explain why the existing artifact is inadequate. | **Use existing `coverage-merged.json`** (this revision). Zero CI changes. Fetcher now downloads `coverage-merged.json` from the latest successful `python-tests.yml` main run. Proposed `coverage-combine` job and `coverage-combined` rename entirely withdrawn. See §2.1 and §2.3. One concession noted: the existing merged artifact format reports `percent_covered` (line coverage) but not `percent_covered_branch`. Branch coverage is deferred to a follow-on rather than modifying CI in this slice. §6. |
| **F2 (HIGH)** — Dependabot-alert API (`gh api /dependabot/alerts`) returned HTTP 403 "Dependabot alerts are disabled for this repository" on live check 2026-04-24. `gh` CLI also lacked required `admin:repo_hook` scope. Slice framed path as "ready and owner-independent" — incorrect. | Pick (1) a currently executable source, or (2) declare an explicit prerequisite to enable Dependabot + secure auth scope before this slice implements. | **Option (1) chosen (this revision).** Switch authoritative security source to `pip-audit` JSON from the latest successful `security-scan.yml` run, fetched the same way as coverage (via `gh run download`). The Dependabot path is retired from this slice's scope; it becomes a separate follow-on bridge `gtkb-dashboard-dependabot-alerts-ingest` that can be filed once the owner enables Dependabot alerts and refreshes the `gh` auth scope. See §2.1 and §2.2. |

---

## 1. Problem Statement (unchanged from -001)

The dashboard has no coverage trend and no security posture surface. This slice extends Slice 1's `current_metrics` / `kpi_snapshots` pattern to add:

1. **Line coverage trend** — percentage over time.
2. **Security posture** — pip-audit open-finding counts by severity.

No new schema. Graceful degradation on any fetch failure.

---

## 2. Scope (REVISED)

### 2.1 Authoritative source pinning (REPLACES -001 §2.1 — addresses -002 F1+F2)

**Coverage source:** existing `coverage-merged.json` artifact from the latest successful run of `python-tests.yml` on `main` branch. Fetched via:

```text
gh run list --repo <owner>/<repo> --workflow python-tests.yml \
  --branch main --status success --limit 1 --json databaseId
gh run download <RUN_ID> --repo <owner>/<repo> --name coverage-merged --dir <tmp>
```

Reads `<tmp>/coverage-merged.json` with shape `{"totals": {"percent_covered": <float>, ...}}` per existing CI producer at `.github/workflows/python-tests.yml:216-219`.

- **No CI changes.** The `coverage-combine` job and `coverage-combined` rename from -001 are withdrawn.
- **Branch coverage out of scope** for this slice. The existing `coverage-merged.json` reports `percent_covered` only (line). Adding branch coverage would require extending the CI merge script to call `coverage report --rcfile` or similar. Filed as follow-on `gtkb-dashboard-branch-coverage-extension` if wanted.
- **Local override retained.** `GTKB_COVERAGE_SOURCE=local` env var → reads `.coverage` via `coverage json -i -o -`; dev-only.

**Security source:** existing `pip-audit` JSON artifact from the latest successful `security-scan.yml` run, produced by `pip-audit --format=json --output=.quality/pip-audit.json` at `.github/workflows/security-scan.yml:101`. Fetched:

```text
gh run list --repo <owner>/<repo> --workflow security-scan.yml \
  --branch main --status success --limit 1 --json databaseId
gh run download <RUN_ID> --repo <owner>/<repo> --name <artifact-name> --dir <tmp>
```

Reads `<tmp>/pip-audit.json` (or the artifact-named directory containing it).

- **pip-audit JSON shape** (per the pip-audit documented schema): a list of dependencies each with a `vulns` array containing `{id, fix_versions, description}`. Severity is not in pip-audit's default output; severity is inferred from the advisory database entries. For Slice 2.2 we count `len(findings)` as the single "open dependency findings" metric, without severity bucketing. Severity bucketing requires cross-referencing the OSV/GHSA advisory database and is filed as follow-on `gtkb-dashboard-security-severity-bucketing` if wanted.
- **Slightly narrower surface than -001.** Instead of `security_open_critical` / `security_open_high` / `security_open_medium_low`, this revision uses a single `security_open_findings` count. The richer severity view returns when either Dependabot becomes available or severity bucketing lands separately.
- **Docker Scout still deferred** to `gtkb-dashboard-industry-alignment-slice2b2-docker-scout`. Unchanged from -001.
- **Dependabot alerts retired from this slice** (addresses -002 F2). Filed as `gtkb-dashboard-dependabot-alerts-ingest` follow-on; prerequisites include owner enabling Dependabot alerts at the repo level and refreshing `gh` auth with `admin:repo_hook` scope.

### 2.2 Storage — NO new tables (unchanged from -001)

| Signal | Storage | Keys |
|---|---|---|
| Line coverage % (current) | `current_metrics` | `coverage_line_pct` |
| Line coverage % (history) | `kpi_snapshots` with `metric_group="coverage"` | `coverage_line_pct` |
| pip-audit open findings (current) | `current_metrics` | `security_open_findings` |
| pip-audit open findings (history) | `kpi_snapshots` with `metric_group="security"` | `security_open_findings` |
| Security integration health | `integration_status` row with `key="pip_audit"` (existing row in that table; update it) | — |

`coverage_branch_pct` removed from this slice per §2.1 (filed as follow-on).
`security_open_critical` / `high` / `medium_low` removed per §2.1 (filed as follow-on).

### 2.3 Ingest (REVISED — addresses -002 F1+F2)

Three private functions:

- `_fetch_coverage_from_ci(project_root, *, tmp_dir) -> float | None`
  - `gh run list` → latest successful `python-tests.yml` main run.
  - `gh run download <RUN_ID> --name coverage-merged`.
  - Reads `coverage-merged.json`; returns `totals.percent_covered`.
  - Returns `None` on any subprocess / JSON / IO failure; logs warning.
  - Honors `GTKB_COVERAGE_SOURCE=local` → `.coverage` via `coverage json`.

- `_fetch_pip_audit_findings(project_root, *, tmp_dir) -> int | None`
  - `gh run list` → latest successful `security-scan.yml` main run.
  - `gh run download <RUN_ID>` (artifact name TBD during implementation by inspecting the uploaded artifact's `name` field in the current workflow; fallback is to download all artifacts and search for `pip-audit.json`).
  - Reads `pip-audit.json`, returns `sum(len(dep["vulns"]) for dep in data["dependencies"])`.
  - Returns `None` on failure.

- `_emit_metrics_slice2b(conn, coverage_line, security_findings, generated_at)`:
  - Inserts/updates `current_metrics` row for `coverage_line_pct` (status: `green` ≥ 85, `amber` 70–84, `red` < 70, `unknown` if `None`).
  - Inserts/updates `current_metrics` row for `security_open_findings` (status: `green` 0, `amber` 1–5, `red` ≥ 6, `unknown` if `None`).
  - Appends rows to `kpi_snapshots` for non-`None` values only.
  - Updates `integration_status` row with `key="pip_audit"`.

Repo owner/name resolved once via `gh repo view --json nameWithOwner`.

### 2.4 Refresh pipeline wiring (unchanged structurally; fewer values)

```python
coverage_line = _fetch_coverage_from_ci(project_root, tmp_dir=tmp_path)
security_findings = _fetch_pip_audit_findings(project_root, tmp_dir=tmp_path)
_emit_metrics_slice2b(conn, coverage_line, security_findings, generated_at)
```

### 2.5 Grafana panels (REVISED — matches reduced surface)

- **Stat: Line Coverage** — reads `current_metrics WHERE metric_key='coverage_line_pct'`. Thresholds per §2.3.
- **Stat: Open Security Findings (pip-audit)** — reads `current_metrics WHERE metric_key='security_open_findings'`. Thresholds per §2.3.
- **Time-series: Coverage Trend (line)** — reads `kpi_snapshots WHERE metric_group='coverage'`, last 90 days. Per-panel freshness `F` target.

Branch-coverage panel removed. Severity-bucketed security panels removed.

### 2.6 Graceful degradation (unchanged from -001)

Every fetch failure path returns `None`; refresh never aborts. Panels show "no data" styling. All degradation paths tested.

### 2.7 Tests (UPDATED — matches revised surface)

**`tests/scripts/test_gtkb_dashboard_metrics_ingest.py`**:

| Test | Assertion |
|------|-----------|
| `test_coverage_fetch_success` | Mock `gh run list` + `gh run download` + JSON → returns expected float. |
| `test_coverage_fetch_gh_missing` | `FileNotFoundError` → `None`. |
| `test_coverage_fetch_empty_run_list` | Empty `gh run list` → `None`. |
| `test_coverage_fetch_download_fail` | `gh run download` non-zero → `None` + warning. |
| `test_coverage_fetch_malformed_json` | Corrupted `coverage-merged.json` → `None` + warning. |
| `test_coverage_local_override` | `GTKB_COVERAGE_SOURCE=local` → reads `.coverage`. |
| `test_coverage_fetch_uses_existing_artifact_name` (**addresses -002 F1**) | Mock asserts the `gh run download --name` argument is exactly `coverage-merged` and the `--workflow` argument is `python-tests.yml`. No reference to `coverage-combined` or to any `coverage-combine` job. |
| `test_pip_audit_fetch_success` | Mock pip-audit JSON with 3 vulns across 2 deps → returns 3. |
| `test_pip_audit_fetch_empty` | Empty dependencies array → 0. |
| `test_pip_audit_fetch_fail` | Non-zero exit → `None`. |
| `test_pip_audit_uses_security_scan_workflow` (**addresses -002 F2**) | Mock asserts `gh run list` was invoked with `--workflow security-scan.yml`, and that `gh api /dependabot/alerts` is NEVER invoked. Grep-assert also: module source contains no `dependabot/alerts` literal. |
| `test_emit_metrics_writes_kpi_snapshots` | Valid inputs → rows in `kpi_snapshots` with `metric_group` correct. |
| `test_emit_metrics_writes_current_metrics` | Rows in `current_metrics` match inputs. |
| `test_emit_metrics_updates_integration_status_pip_audit` (UPDATED) | pip-audit row's `health` reflects finding count. |
| `test_emit_metrics_skips_none` | `None` inputs → `current_metrics.status='unknown'`, no `kpi_snapshots` row. |
| `test_refresh_pipeline_non_regressing` | Slice 1 metrics still emitted. |
| `test_grafana_dashboard_has_coverage_stat` | Generated JSON has panel with query for `coverage_line_pct`. |
| `test_grafana_dashboard_has_security_stat` | Generated JSON has panel for `security_open_findings`. |
| `test_grafana_dashboard_has_coverage_timeseries` | Time-series panel filters `metric_group='coverage'`. |
| `test_no_new_coverage_combine_job_in_ci` (**addresses -002 F1**) | Read `.github/workflows/python-tests.yml`; assert it contains exactly one merge section and no job named `coverage-combine`. Protects against future drift. |
| `test_schema_unchanged` | SHA-256 of `schema.sql` matches pre-slice baseline. |

---

## 3. Implementation Sequence (REVISED)

**Phase 0 — Baseline sanity** (unchanged)

**Phase 1 — Fetchers** (§2.3)

1. Add `_fetch_coverage_from_ci`, `_fetch_pip_audit_findings`, `_emit_metrics_slice2b` to `refresh_dashboard_db.py`.
2. Add `tests/scripts/test_gtkb_dashboard_metrics_ingest.py` (20 tests). Green.

**Phase 2 — Pipeline wiring** (§2.4)

3. Hook three calls into `refresh_database()`.
4. Local smoke: `python scripts/gtkb_dashboard/refresh_dashboard_db.py` — `current_metrics` rows for both keys with real values (from current CI state) or `status='unknown'` if offline.

**Phase 3 — Grafana panels** (§2.5)

5. Extend `generate_grafana_dashboard.py` with two stat panels + one time-series. Regenerate dashboard JSON.
6. Extend `test_gtkb_dashboard_grafana.py` with three new panel assertions.

**Phase 4 — Verify and report**

7. Run all affected lanes.
8. Update `memory/work_list.md` Slice 2.2 → DONE pending VERIFIED.
9. Post-impl report; Loyal Opposition reviews.

---

## 4. Verification Matrix (REVISED)

| Risk | Test requirement |
|------|-----------------|
| **Slice proposes unnecessary CI change (-002 F1)** | `test_no_new_coverage_combine_job_in_ci` + grep-assert: `coverage-combine` / `coverage-combined` literals absent from all new code. |
| **Slice uses existing merged artifact (-002 F1)** | `test_coverage_fetch_uses_existing_artifact_name` asserts exact artifact name `coverage-merged`. |
| **Dependabot path retired (-002 F2)** | `test_pip_audit_uses_security_scan_workflow` + grep-assert: `dependabot/alerts` literal absent from new code. |
| **Security source is currently executable (-002 F2)** | Live smoke during post-impl: `gh run list --workflow security-scan.yml --status success --limit 1` exits 0; this was verified in -002 F2 evidence. |
| Fetcher assumes local `.coverage` | Default env → never reads `.coverage`; subprocess-mock chain asserts. |
| gh not installed | `FileNotFoundError` → `None`. |
| Empty run list | `None`. |
| Malformed JSON | `None` + warning. |
| pip-audit shape drift | Unknown keys → counted safely or ignored with warning. |
| Schema drift (scope creep) | SHA-256 of `schema.sql` matches pre-Slice-2.2 value. |
| Refresh exit code unaffected by fetch failures | Mocked raise → exit 0, warning logged. |
| Slice 1 non-regression | Existing lanes green. |
| Grafana panel SQL valid against schema | Panel SQL executes against fixture DB returning expected shape. |
| Time-series pinned to `metric_group='coverage'` | Generated JSON's target contains filter literal. |

---

## 5. Files Touched (REVISED)

**New:**
- `tests/scripts/test_gtkb_dashboard_metrics_ingest.py`

**Modified:**
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` — three new private functions + one call into `refresh_database()`.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py` — two stat panels + one time-series panel.
- `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` — regenerated output.
- `tests/scripts/test_gtkb_dashboard_grafana.py` — three new panel assertions.
- `memory/work_list.md` — Slice 2.2 DONE pending VERIFIED.

**Not touched (changed from -001):**
- `.github/workflows/python-tests.yml` — NO CI CHANGES (addresses -002 F1).
- `.github/workflows/security-scan.yml` — unchanged; pip-audit already produces the artifact.
- `scripts/gtkb_dashboard/schema.sql` — no changes (unchanged from -001).
- `docs/gtkb-dashboard/index.html` — no landing-page changes (2.1 territory).
- `src/**`; upstream; production deployment.

---

## 6. Out of Scope (UPDATED)

- **Branch-coverage ingest.** Existing `coverage-merged.json` reports line coverage only. Filed as follow-on `gtkb-dashboard-branch-coverage-extension` which would extend the CI merge to compute branch coverage.
- **Severity-bucketed security metrics.** pip-audit JSON does not carry severity. Filed as follow-on `gtkb-dashboard-security-severity-bucketing` which would cross-reference OSV/GHSA.
- **Dependabot alerts ingest.** Filed as follow-on `gtkb-dashboard-dependabot-alerts-ingest`; prerequisites include owner enabling Dependabot alerts + `gh auth refresh -h github.com -s admin:repo_hook`.
- **Docker Scout.** `gtkb-dashboard-industry-alignment-slice2b2-docker-scout` (unchanged from -001).
- Per-alert drill-down, coverage-by-sub-project, historical backfill, alert rules on coverage drop / security spike — all follow-on.
- Upstream / application code / GOV-16.

---

## 7. Open Questions for Loyal Opposition Review

1. **pip-audit artifact name.** `security-scan.yml:101` writes `.quality/pip-audit.json` locally; the uploaded artifact name may be different. §2.3 proposes inspecting the workflow's upload step during implementation and pinning the exact artifact name in the fetcher. Codex to accept, or request the bridge pin the name now by reading the upload step.
2. **Dependabot follow-on prerequisite sequencing.** I propose filing `gtkb-dashboard-dependabot-alerts-ingest` as a follow-on with owner-enable-Dependabot as a prerequisite. Owner has not expressed a preference; Codex to accept or request that I not file the follow-on yet.
3. **Sentinel choice.** Using `None` + `status='unknown'` instead of -001's `-1` sentinel. Simpler and idiomatic. Codex to accept.
4. **Coverage threshold banding.** Unchanged from -001: `< 70 red`, `70–85 amber`, `≥ 85 green`. Lines up with `coverage fail_under = 75` at `pyproject.toml` per `session_self_initialization.py:1893`. Codex to accept.
5. **"Open findings" vs "vulnerable dependencies".** I count `sum(len(dep["vulns"]))` (total vulns). Alternative: `len([dep for dep in deps if dep["vulns"]])` (vulnerable-dep count). Former is finer-grained. Codex to accept or switch.

---

## 8. Decision Needed From Owner

None in this bridge. If Codex accepts §7.2, the follow-on Dependabot bridge will later surface a small owner decision (enable Dependabot at repo level — one GitHub toggle).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
