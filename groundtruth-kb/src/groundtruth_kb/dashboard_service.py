#!/usr/bin/env python3
"""Small companion service for scheduled and manual GT-KB dashboard refreshes."""

from __future__ import annotations

import argparse
import hmac
import html
import ipaddress
import json
import logging
import os
import threading
from collections.abc import Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from groundtruth_kb import dashboard_control_plane as registry
from groundtruth_kb.config import GTConfig
from groundtruth_kb.dashboard import initialize_dashboard, resolve_dashboard_paths

logger = logging.getLogger(__name__)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
DEFAULT_INTERVAL_MINUTES = 60
CONTROL_PLANE_SUBJECT = "dashboard"


class RefreshState:
    def __init__(
        self,
        db_path: Path,
        project_root: Path,
        interval_seconds: int,
        token: str,
        *,
        config: GTConfig | None = None,
        runtime_root: Path | None = None,
        config_path: Path | None = None,
        grafana_port: int = 3000,
        refresh_port: int = DEFAULT_PORT,
    ) -> None:
        self.config = config or GTConfig(project_root=project_root)
        self.paths = resolve_dashboard_paths(self.config, db_path=db_path, runtime_root=runtime_root)
        self.db_path = self.paths.db_path
        self.project_root = self.paths.project_root
        self.interval_seconds = interval_seconds
        self.token = token
        self.config_path = config_path.resolve() if config_path else None
        self.grafana_port = grafana_port
        self.refresh_port = refresh_port
        self.lock = threading.Lock()
        self.last_result: dict[str, Any] | None = None
        self.last_error = ""
        self.refreshing = False

    def refresh_now(self, trigger: str) -> dict[str, Any]:
        if not self.lock.acquire(blocking=False):
            return {"status": "already_running", "trigger": trigger}
        self.refreshing = True
        try:
            result = initialize_dashboard(
                self.paths, self.config, grafana_port=self.grafana_port, refresh_port=self.refresh_port
            )
            result["trigger"] = trigger
            self.last_result = result
            self.last_error = ""
            return result
        except Exception as exc:
            self.last_error = str(exc)
            self.last_result = {"status": "failed", "trigger": trigger, "error": str(exc)}
            raise
        finally:
            self.refreshing = False
            self.lock.release()


def _interval_seconds() -> int:
    raw_value = os.getenv("GTKB_DASHBOARD_REFRESH_INTERVAL_MINUTES", str(DEFAULT_INTERVAL_MINUTES))
    try:
        return max(60, int(raw_value) * 60)
    except ValueError:
        return DEFAULT_INTERVAL_MINUTES * 60


def _project_root() -> Path:
    return Path(os.getenv("GTKB_DASHBOARD_PROJECT_ROOT") or Path.cwd()).resolve()


def _dashboard_db_path() -> Path:
    root = _project_root()
    runtime = Path(os.getenv("GTKB_DASHBOARD_RUNTIME_ROOT") or root / ".groundtruth/dashboard")
    return Path(os.getenv("GTKB_DASHBOARD_DB") or runtime / "gtkb-dashboard.sqlite").resolve()


def _render_home(state: RefreshState) -> str:
    last_result = state.last_result or {"status": "not_run"}
    token_status = "configured" if state.token else "missing"
    refresh_status = "running" if state.refreshing else str(last_result.get("status", "not_run"))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GT-KB Dashboard Refresh</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 0;
           color: #102027; background: #f6f8fa; }}
    header {{ background: #103f3a; color: #fff; padding: 24px 32px; }}
    main {{ max-width: 980px; margin: 32px auto; padding: 0 20px; }}
    section {{ background: #fff; border: 1px solid #d5dde3; border-radius: 6px; padding: 20px; margin-bottom: 18px; }}
    label {{ display: block; font-weight: 650; margin-bottom: 8px; }}
    input {{ width: min(480px, 100%); padding: 10px; border: 1px solid #b8c2cc; border-radius: 4px; }}
    button {{ margin-top: 12px; padding: 10px 14px; border: 0; border-radius: 4px; background: #0b6b61;
             color: #fff; cursor: pointer; }}
    code {{ background: #edf1f4; padding: 2px 5px; border-radius: 3px; }}
    pre {{ white-space: pre-wrap; background: #edf1f4; padding: 12px; border-radius: 4px; overflow: auto; }}
  </style>
</head>
<body>
  <header>
    <h1>GT-KB Dashboard Refresh</h1>
    <p>Manual and scheduled refresh control for the SQLite-backed Grafana dashboard.</p>
  </header>
  <main>
    <section>
      <h2>Status</h2>
      <p>Refresh status: <strong>{html.escape(refresh_status)}</strong></p>
      <p>Shared token: <strong>{html.escape(token_status)}</strong></p>
      <p>SQLite database: <code>{html.escape(str(state.db_path))}</code></p>
      <p>Scheduled interval: <code>{state.interval_seconds // 60} minutes</code></p>
    </section>
    <section>
      <h2>Manual Refresh</h2>
      <form method="post" action="/refresh">
        <label for="token">Refresh token</label>
        <input id="token" name="token" type="password" autocomplete="off">
        <br>
        <button type="submit">Refresh now</button>
      </form>
    </section>
    <section>
      <h2>Last Result</h2>
      <pre>{html.escape(json.dumps(last_result, indent=2, sort_keys=True))}</pre>
    </section>
  </main>
</body>
</html>"""


def _make_context(state: RefreshState) -> registry.OperationContext:
    """Build a registry context that reads/writes through the given state.

    Paths come from the service, never from caller input."""

    def apply_op(operation_id: str) -> Mapping[str, Any]:
        return state.refresh_now(operation_id)

    def read_state() -> Mapping[str, Any]:
        return {
            "last_result": state.last_result,
            "last_error": state.last_error,
            "refreshing": state.refreshing,
            "token_configured": bool(state.token),
            "interval_seconds": state.interval_seconds,
        }

    return registry.OperationContext(
        project_root=state.project_root,
        dashboard_db=state.db_path,
        subject=CONTROL_PLANE_SUBJECT,
        apply_operation=apply_op,
        read_state=read_state,
    )


def handle_control_plane_request(
    request: Mapping[str, Any],
    state: RefreshState,
    supplied_token: str,
) -> tuple[HTTPStatus, dict[str, Any]]:
    """Route a control-plane request through the registry.

    Returns ``(status, body)``. Token enforcement applies only when the
    operation requires the refresh token and ``dry_run`` is not set. Read-only
    operations and dry-run previews do not require the token.
    """
    operation_id = request.get("operation_id")
    descriptor: registry.OperationDescriptor | None = None
    if isinstance(operation_id, str) and operation_id:
        try:
            descriptor = registry.get_descriptor(operation_id)
        except registry.UnknownOperationError:
            descriptor = None

    dry_run = bool(request.get("dry_run", False))
    requires_token = descriptor is not None and descriptor.requires_token and not dry_run

    if requires_token:
        if not state.token:
            return HTTPStatus.SERVICE_UNAVAILABLE, {
                "status": "error",
                "error": "GTKB_DASHBOARD_REFRESH_TOKEN is not configured",
            }
        if not hmac.compare_digest(supplied_token.encode("utf-8"), state.token.encode("utf-8")):
            return HTTPStatus.UNAUTHORIZED, {
                "status": "error",
                "error": "invalid refresh token",
            }

    context = _make_context(state)
    try:
        response = registry.dispatch(request, context)
    except registry.UnknownOperationError as exc:
        return HTTPStatus.NOT_FOUND, {"status": "error", "error": str(exc)}
    except registry.InvalidRequestError as exc:
        return HTTPStatus.BAD_REQUEST, {"status": "error", "error": str(exc)}
    except Exception as exc:  # pragma: no cover  # intentional-catch: handler safety net returns a structured 500
        return HTTPStatus.INTERNAL_SERVER_ERROR, {
            "status": "failed",
            "error": str(exc),
        }
    return HTTPStatus.OK, response


def _make_handler(state: RefreshState) -> type[BaseHTTPRequestHandler]:
    class RefreshHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._send_json(
                    {
                        "status": "ok",
                        "refreshing": state.refreshing,
                        "last_result": state.last_result,
                        "last_error": state.last_error,
                        "project_root": str(state.project_root),
                        "runtime_root": str(state.paths.runtime_root),
                        "dashboard_db": str(state.db_path),
                        "config_path": str(state.config_path) if state.config_path else None,
                        "interval_seconds": state.interval_seconds,
                        "grafana_port": state.grafana_port,
                    }
                )
                return
            if parsed.path == "/control":
                self._send_html(_render_home(state))
                return
            display_files = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/dashboard-data.json": ("dashboard-data.json", "application/json; charset=utf-8"),
                "/bridge-swimlane.json": ("bridge-swimlane.json", "application/json; charset=utf-8"),
            }
            if parsed.path in display_files:
                name, content_type = display_files[parsed.path]
                try:
                    encoded = (state.paths.runtime_root / name).read_bytes()
                except OSError:
                    self._send_json({"status": "unavailable"}, HTTPStatus.SERVICE_UNAVAILABLE)
                    return
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
            try:
                self._handle_post()
            except (ValueError, UnicodeError, TimeoutError):
                self._send_json(
                    {"status": "invalid_request", "error": "Malformed request body"}, HTTPStatus.BAD_REQUEST
                )

        def _handle_post(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/control_plane":
                self._handle_control_plane_post()
                return
            if parsed.path == "/refresh":
                self._handle_legacy_refresh()
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def _handle_control_plane_post(self) -> None:
            body = self._read_json_body()
            supplied_token = (str(body.get("token", "")) if isinstance(body, dict) else "") or self.headers.get(
                "X-Refresh-Token", ""
            )
            # Do not forward the token field into the registry — it is a
            # transport-layer credential, not a handler parameter.
            request = {k: v for k, v in body.items() if k != "token"}
            status, response = handle_control_plane_request(request, state, supplied_token)
            self._send_json(response, status)

        def _handle_legacy_refresh(self) -> None:
            form = self._read_form()
            supplied_token = form.get("token", [""])[0] or self.headers.get("X-Refresh-Token", "")
            status, response = handle_control_plane_request(
                {"operation_id": "dashboard.refresh"}, state, supplied_token
            )
            if status != HTTPStatus.OK:
                self._send_json(response, status)
                return
            accept = self.headers.get("Accept", "")
            if "text/html" in accept:
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/control")
                self.end_headers()
                return
            # Preserve the legacy JSON shape (the underlying refresh result)
            # so existing clients of POST /refresh keep working.
            self._send_json(dict(response.get("details", {})))

        def _read_body(self) -> str:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if not 0 <= length <= 65536:
                raise ValueError("Invalid body size")
            self.connection.settimeout(10)
            body = self.rfile.read(length)
            if len(body) != length:
                raise ValueError("Incomplete body")
            return body.decode("utf-8")

        def _read_json_body(self) -> dict[str, Any]:
            raw = self._read_body()
            if not raw:
                return {}
            try:
                parsed_body = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return parsed_body if isinstance(parsed_body, dict) else {}

        def log_message(self, format: str, *args: Any) -> None:
            logger.info("%s - %s", self.address_string(), format % args)

        def _read_form(self) -> dict[str, list[str]]:
            body = self._read_body()
            content_type = self.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    payload = json.loads(body or "{}")
                except json.JSONDecodeError:
                    return {}
                if not isinstance(payload, dict):
                    raise ValueError("Expected an object")
                return {key: [str(value)] for key, value in payload.items()}
            return parse_qs(body)

        def _send_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _send_json(self, body: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
            encoded = json.dumps(body, indent=2, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

    return RefreshHandler


def _run_scheduler(state: RefreshState, stop_event: threading.Event) -> None:
    try:
        state.refresh_now("startup")
    except Exception as exc:  # intentional-catch: a failed startup refresh is logged; the scheduler keeps its interval
        logger.error("Startup dashboard refresh failed: %s", exc)
    while not stop_event.wait(state.interval_seconds):
        try:
            state.refresh_now("scheduled")
        except Exception as exc:  # intentional-catch: a failed scheduled refresh is logged; the next interval retries
            logger.error("Scheduled dashboard refresh failed: %s", exc)


def _loopback_host(host: str) -> str:
    """Resolve the numeric IPv4 loopback address supported by this local server."""
    try:
        address = ipaddress.IPv4Address(host)
        if address.is_loopback:
            return str(address)
    except ipaddress.AddressValueError:
        pass
    raise ValueError("dashboard_host_must_be_ipv4_loopback: use 127.0.0.1")


def run_service(
    config: GTConfig,
    db_path: Path,
    runtime_root: Path,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    interval_minutes: int = DEFAULT_INTERVAL_MINUTES,
    *,
    config_path: Path | None = None,
    grafana_port: int = 3000,
) -> None:
    """Serve only the installed display and fixed control operations for this root."""
    host = _loopback_host(host)
    # The service entry point supplies default stderr logging without replacing configured handlers.
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    state = RefreshState(
        db_path,
        config.project_root,
        max(60, interval_minutes * 60),
        os.getenv("GTKB_DASHBOARD_REFRESH_TOKEN", ""),
        config=config,
        runtime_root=runtime_root,
        config_path=config_path,
        grafana_port=grafana_port,
        refresh_port=port,
    )
    # Refuse an occupied address before starting refresh effects.
    server = ThreadingHTTPServer((host, port), _make_handler(state))
    stop_event = threading.Event()
    scheduler = threading.Thread(target=_run_scheduler, args=(state, stop_event), daemon=True)
    scheduler.start()
    logger.info("GT-KB dashboard service listening on http://%s:%s/", host, server.server_port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        server.server_close()
        scheduler.join(timeout=5)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--db-path", type=Path)
    parser.add_argument("--runtime-root", type=Path)
    parser.add_argument("--host", default=DEFAULT_HOST, help="Numeric IPv4 loopback bind address (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=int(os.getenv("GTKB_DASHBOARD_REFRESH_PORT", DEFAULT_PORT)))
    parser.add_argument("--interval-minutes", type=int, default=_interval_seconds() // 60)
    parser.add_argument("--grafana-port", type=int, default=3000)
    args = parser.parse_args(argv)
    try:
        args.host = _loopback_host(args.host)
    except ValueError as exc:
        parser.error(str(exc))
    project_root = (args.project_root or _project_root()).resolve()
    config_path = (args.config or project_root / "groundtruth.toml").resolve()
    config = GTConfig.load(config_path=config_path, discover=False)
    paths = resolve_dashboard_paths(
        config,
        db_path=args.db_path or (Path(os.environ["GTKB_DASHBOARD_DB"]) if os.getenv("GTKB_DASHBOARD_DB") else None),
        runtime_root=args.runtime_root
        or (Path(os.environ["GTKB_DASHBOARD_RUNTIME_ROOT"]) if os.getenv("GTKB_DASHBOARD_RUNTIME_ROOT") else None),
    )
    if not all(0 < p < 65536 for p in (args.port, args.grafana_port)) or args.interval_minutes < 1:
        parser.error("port must be 1..65535 and interval-minutes must be positive")
    run_service(
        config,
        paths.db_path,
        paths.runtime_root,
        args.host,
        args.port,
        args.interval_minutes,
        config_path=config_path,
        grafana_port=args.grafana_port,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
