"""
Small local refresh service for the GroundTruth KB dashboard.

The service refreshes the generated dashboard SQLite database on a timer and
offers a manual refresh endpoint for evaluators running local Grafana.
"""

from __future__ import annotations

import argparse
import html
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from groundtruth_kb.config import GTConfig
from groundtruth_kb.dashboard import refresh_dashboard_db, resolve_dashboard_paths, write_grafana_assets


class RefreshState:
    """Shared refresh service state."""

    def __init__(self, config: GTConfig, db_path: Path, runtime_root: Path, interval_seconds: int) -> None:
        self.config = config
        self.paths = resolve_dashboard_paths(config, db_path=db_path, runtime_root=runtime_root)
        self.interval_seconds = interval_seconds
        self.lock = threading.Lock()
        self.last_status = "not-run"
        self.last_error = ""
        self.last_refreshed = ""

    def refresh(self) -> None:
        with self.lock:
            try:
                refresh_dashboard_db(self.paths, self.config)
                write_grafana_assets(self.paths, self.config)
            except Exception as exc:  # pragma: no cover - defensive service boundary
                self.last_status = "error"
                self.last_error = str(exc)
                raise
            else:
                self.last_status = "ok"
                self.last_error = ""
                self.last_refreshed = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class RefreshHandler(BaseHTTPRequestHandler):
    """HTTP handler for health and manual refresh."""

    state: RefreshState

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path == "/health":
            self._write_text(f"{self.state.last_status}\n")
            return
        self._write_html()

    def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
        if self.path != "/refresh":
            self.send_error(404)
            return
        try:
            self.state.refresh()
        except Exception as exc:  # intentional-catch: HTTP boundary returns refresh failure to caller.
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(exc).encode("utf-8"))
            return
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return

    def _write_text(self, body: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _write_html(self) -> None:
        status = html.escape(self.state.last_status)
        refreshed = html.escape(self.state.last_refreshed or "not yet")
        error = html.escape(self.state.last_error)
        body = f"""\
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>GroundTruth KB Dashboard Refresh</title></head>
<body>
  <h1>GroundTruth KB Dashboard Refresh</h1>
  <p>Status: {status}</p>
  <p>Last refreshed: {refreshed}</p>
  <p>{error}</p>
  <form method="post" action="/refresh"><button type="submit">Refresh now</button></form>
</body>
</html>
"""
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))


def run_service(
    config: GTConfig, db_path: Path, runtime_root: Path, host: str, port: int, interval_minutes: int
) -> None:
    """Run the refresh service until interrupted."""
    state = RefreshState(config, db_path, runtime_root, max(60, interval_minutes * 60))
    state.refresh()

    def scheduler() -> None:
        while True:
            time.sleep(state.interval_seconds)
            try:
                state.refresh()
            except Exception:  # intentional-catch: scheduler keeps serving after transient refresh failure.
                continue

    thread = threading.Thread(target=scheduler, daemon=True)
    thread.start()
    RefreshHandler.state = state
    server = ThreadingHTTPServer((host, port), RefreshHandler)
    server.serve_forever()


def main() -> None:
    """CLI entry point for ``python -m groundtruth_kb.dashboard_service``."""
    parser = argparse.ArgumentParser(description="GroundTruth KB dashboard refresh service")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--db-path", type=Path, required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--interval-minutes", type=int, default=60)
    args = parser.parse_args()
    config = GTConfig.load(config_path=args.config)
    run_service(config, args.db_path, args.runtime_root, args.host, args.port, args.interval_minutes)


if __name__ == "__main__":  # pragma: no cover
    main()
