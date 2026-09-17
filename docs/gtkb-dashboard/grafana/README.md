# GT-KB Grafana dashboard

The installed package owns dashboard collection, templates and process control.
Run the ordinary CLI with the configuration for the intended project:

```powershell
gt --config E:\GT-KB\groundtruth.toml dashboard install
gt --config E:\GT-KB\groundtruth.toml dashboard start
gt --config E:\GT-KB\groundtruth.toml dashboard refresh --json
gt --config E:\GT-KB\groundtruth.toml dashboard stop
```

`start` returns the actual local URLs after checking readiness. Default ports are
3000 for Grafana and 8766 for the refresh service. Both listeners bind to loopback;
children run without visible windows. The refresh service collects on startup
and every 60 minutes by default. Manual refresh requires
`GTKB_DASHBOARD_REFRESH_TOKEN` in the service's environment.

Generated data and display assets default to `<project_root>/.groundtruth/dashboard`;
Grafana defaults to `<project_root>/.groundtruth/tools/grafana`. These runtime
files are uncommitted. Source templates live in the installed package's
`templates/dashboard` directory. `--runtime-root`, `--db-path`, port and interval
options select a particular runtime; use the same runtime when stopping it.

`dashboard init` collects current native observations and materializes the display
without starting processes. `dashboard init --schema-only` creates or migrates
only the derived reporting schema. `dashboard refresh --probe-live` additionally
reads native service/bridge and GitHub workflow observations using the selected
configuration. Probes are read-only; unavailable measurements remain unavailable.
A completed refresh is not release signoff or full telemetry qualification.

Display record counts and queue eligibility do not establish execution success,
readiness or context ownership. Prefer graphical summaries and provide detailed
tables below the overview. Live application connectors and external alert delivery
remain explicit application/operator choices; dashboard setup does not activate
them. The default notifier retains local alert-list behavior.

The source-tree Python and PowerShell entry points have been consolidated into
these installed commands. No Docker Desktop or pip post-install operation is
required. See [package integration](PACKAGE-INTEGRATION.md) for replacement details.
