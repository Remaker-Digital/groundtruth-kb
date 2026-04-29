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

Stop the local dashboard:

```powershell
.\scripts\gtkb_dashboard\stop_local_dashboard.ps1
```

Package-level GT-KB integration requirements are captured in `PACKAGE-INTEGRATION.md`.
