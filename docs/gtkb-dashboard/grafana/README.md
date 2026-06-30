# GT-KB Grafana Dashboard

This directory contains the committed Grafana provisioning assets for the GT-KB dashboard.

Dashboard design rule: default views should prioritize graphical summaries such as status cards, gauges,
charts, timelines, and diagrams. Long textual tables are drill-down detail and should be collapsed or placed
below the visual overview unless a user explicitly needs them first.

Runtime data is not committed. Each environment creates its own SQLite database at:

```text
memory/gtkb-dashboard.sqlite
```

Install Grafana locally:

```powershell
.\scripts\gtkb_dashboard\install_local_grafana.ps1
```

Start the local dashboard:

```powershell
.\scripts\gtkb_dashboard\start_local_dashboard.ps1
```

The dashboard is available at `http://127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard`.

The companion refresh service is available at `http://127.0.0.1:8766/` and requires
`GTKB_DASHBOARD_REFRESH_TOKEN` from `.env.local` for manual refreshes. The service also refreshes
the database on startup and every 60 minutes by default.

For release preparation, the refresh database must not report a false green. The
release readiness row surfaces:

- `release_blockers`
- `release_health_findings`
- `dirty_worktree_paths`
- `dispatcher_health_findings`
- `bridge_actionability_findings`
- `readme_wiki_drift`

Run a bounded one-off release-health refresh from the repository root with:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-health.sqlite --project-root E:\GT-KB
```

For release signoff, add `--probe-live` after confirming local dispatcher and
GitHub CLI probes are healthy; live probes are opt-in because they depend on
host-local process and authentication state.

Compare governed wiki source pages with a local wiki clone with:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/update_wiki_pages.py compare --wiki-dir .tmp/groundtruth-kb.wiki
```

Azure Container Apps reconciliation is an optional adopter diagnostic, not a
default GT-KB release-health dependency. Enable it only for an Azure-hosted
adopter check:

```powershell
$env:GTKB_DASHBOARD_AZURE_RECONCILE = "1"
```

Stop the local dashboard:

```powershell
.\scripts\gtkb_dashboard\stop_local_dashboard.ps1
```

Package-level GT-KB integration requirements are captured in `PACKAGE-INTEGRATION.md`.
