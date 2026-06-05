# Project Progress Dashboard Runbook

This dashboard pipeline is additive and local-only. It reads the Knowledge DB, local deployment/build logs, and the latest `run_results.json`, then writes visualization-ready artifacts under `independent-progress-assessments/artifacts/project-progress/`.

Run it with:

```powershell
python independent-progress-assessments\tools\project_progress_snapshot.py
```

Open the dashboard directly from disk:

- [dashboard.html](e:/Claude-Playground/CLAUDE-PROJECTS/Agent%20Red%20Customer%20Engagement/independent-progress-assessments/artifacts/project-progress/dashboard.html)

Or serve it over localhost:

```powershell
python independent-progress-assessments\tools\serve_project_progress_dashboard.py
```

Then open:

```text
http://127.0.0.1:8765/dashboard.html
```

Outputs:

- `independent-progress-assessments/artifacts/project-progress/dashboard.html`
- `independent-progress-assessments/artifacts/project-progress/latest.json`
- `independent-progress-assessments/artifacts/project-progress/history.json`
- `independent-progress-assessments/artifacts/project-progress/snapshots/progress-snapshot-<timestamp>.json`

What is included now:

- Delivery KPIs from the append-only Knowledge DB
- Quality KPIs from the Knowledge DB and assertion history
- Historical KB trend reconstruction from backlog snapshot timestamps
- Operational evidence from local build/deploy logs
- Latest verification/test-run summary from `run_results.json`
- A standalone HTML dashboard with embedded snapshot data for direct viewing

Important limits:

- Live SLA, latency, uptime, and tenant-usage metrics are not included in this local refresh path because those metrics are stored in runtime services, not in the local append-only artifact set.
- Coverage delta is neutralized to `0.0` in the quality composite because no durable line-coverage history is currently available in the local sources.
- Historical dashboard refresh history begins when this tool is first run; earlier trend points are reconstructed from Knowledge DB history and deployment logs rather than prior dashboard snapshots.

