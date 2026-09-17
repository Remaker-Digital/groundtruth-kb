"""The project dashboard link as configuration states it (SPEC-PROJECT-DASHBOARD-KPI-LINK-001).

One derivation serves two readers: `gt dashboard start` reports the URLs of the processes it launched, and
`gt status` states the link at session startup without contacting anything. The Grafana dashboard uid, the loopback
host, the port defaults and the runtime directory default are fixed by the installed package; a launch may choose
other ports on its command line, and the service it starts reports them on its own health route.
"""

from __future__ import annotations

from pathlib import Path

LOOPBACK_HOST = "127.0.0.1"
GRAFANA_DASHBOARD_UID = "groundtruth-kb-dashboard"
GRAFANA_DASHBOARD_SLUG = "groundtruth-kb-dashboard"
DEFAULT_GRAFANA_PORT = 3000
DEFAULT_REFRESH_PORT = 8766
DASHBOARD_RUNTIME_RELATIVE_PATH = Path(".groundtruth") / "dashboard"


def grafana_dashboard_url(grafana_port: int = DEFAULT_GRAFANA_PORT) -> str:
    """The Grafana dashboard page on the local loopback listener."""
    return f"http://{LOOPBACK_HOST}:{grafana_port}/d/{GRAFANA_DASHBOARD_UID}/{GRAFANA_DASHBOARD_SLUG}"


def refresh_service_url(refresh_port: int = DEFAULT_REFRESH_PORT) -> str:
    """The landing page served by the refresh service on the local loopback listener."""
    return f"http://{LOOPBACK_HOST}:{refresh_port}/"


def default_dashboard_runtime_root(project_root: Path) -> Path:
    """Where the installed dashboard materializes its derived view unless a runtime root is selected."""
    return (project_root / DASHBOARD_RUNTIME_RELATIVE_PATH).resolve()
