# Dashboard package integration

The ordinary `gt dashboard` commands use installed Python modules and templates.
Setup is explicit; installing the Python package does not install Grafana or
start processes, and the runtime does not require Docker Desktop.

| Former source entry point | Installed behavior |
| --- | --- |
| `refresh_dashboard_db.py` | `gt dashboard refresh`; `--probe-live` preserves explicit optional probes. Former `--init-only` is `gt dashboard init --schema-only`. |
| `generate_grafana_dashboard.py` | `gt dashboard init` or `refresh` generates the Grafana display and provisioning as part of the selected runtime. |
| `generate_bridge_swimlane.py` | `init` or `refresh` publishes the swimlane in that runtime. Unavailable bridge observations are explicit in its payload; refresh completion does not assert an observed queue. |
| `refresh_service.py` | `gt dashboard serve` runs the installed service with selected configuration, paths, ports and interval. |
| `install_local_grafana.ps1` | `gt dashboard install` uses pinned Grafana and SQLite plugin versions, verifies downloads and records observed installed identities. Select an existing home with `--grafana-home`; skip flags remain explicit. Arbitrary unverified version downloads are not retained. |
| `start_local_dashboard.ps1` | `gt dashboard start` starts hidden children and returns URLs after readiness. No headless switch or automatic browser launch is needed. |
| `stop_local_dashboard.ps1` | `gt dashboard stop` checks recorded process creation identity and stops only that runtime's recorded process trees. No global executable-path process sweep remains. |

The collector, control registry, Grafana generator and swimlane generator are
package modules; schema, HTML and alerting YAML are package templates. Generated
copies under documentation paths are removed. Default runtime locations are
`.groundtruth/dashboard` and `.groundtruth/tools/grafana` under the selected
project. A source database cannot be selected as reporting output.

There is no standalone arbitrary output path for only the old generators: select
`--runtime-root` for the complete derived display. API/module generation helpers
remain within the package. A legacy bare-PID record cannot authorize process
termination and requires inspection. Existing source-tree runtime installations
are not moved, stopped or replaced by source consolidation.

The refresh token is read from `GTKB_DASHBOARD_REFRESH_TOKEN` in the selected
service environment. Grafana paths and loopback binding are supplied by the
launcher. External notification and application connectors remain opt-in.
Builder tests of isolated inputs do not establish actual-host startup behavior,
independent verification or permission to resume ordinary operation.
