# GT-KB Package Integration Requirement

The dashboard runtime must not depend on Docker Desktop.

For the `groundtruth-kb` package, dashboard setup should be exposed through the GT-KB CLI, not a hidden pip
post-install side effect. The package should provide:

- `gtkb dashboard install`: installs local Grafana OSS into a user-local application data directory and installs
  the `frser-sqlite-datasource` plugin.
- `gtkb dashboard start`: initializes or refreshes the dedicated SQLite dashboard database, starts the refresh
  service, starts local Grafana, and opens `http://127.0.0.1:3000/d/gtkb/groundtruth-kb-dashboard`.
- `gtkb dashboard stop`: stops the local Grafana and refresh-service processes started by GT-KB.

The current source repository proves the required behavior with these repo-local scripts:

- `scripts/gtkb_dashboard/install_local_grafana.ps1`
- `scripts/gtkb_dashboard/start_local_dashboard.ps1`
- `scripts/gtkb_dashboard/stop_local_dashboard.ps1`
- `scripts/gtkb_dashboard/refresh_dashboard_db.py`
- `scripts/gtkb_dashboard/refresh_service.py`

Runtime artifacts are generated per environment and must remain uncommitted:

- `memory/gtkb-dashboard.sqlite`
- `memory/grafana/`
- `tools/grafana/`

The GT-KB package should vendor or generate equivalent provisioning files from
`docs/gtkb-dashboard/grafana/provisioning/` and should set:

- `GTKB_DASHBOARD_SQLITE_PATH`
- `GTKB_DASHBOARD_DASHBOARDS_PATH`
- `GTKB_DASHBOARD_REFRESH_TOKEN`
