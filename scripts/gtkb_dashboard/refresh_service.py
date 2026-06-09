#!/usr/bin/env python3
"""Small companion service for scheduled and manual GT-KB dashboard refreshes."""

from __future__ import annotations

import html
import json
import os
import sys
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Mapping
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.gtkb_dashboard import control_plane_registry as registry  # noqa: E402
from scripts.gtkb_dashboard.refresh_dashboard_db import (  # noqa: E402
    DEFAULT_DB_PATH,
    PROJECT_ROOT,
    initialize_database,
    refresh_database,
)

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8766
DEFAULT_INTERVAL_MINUTES = 60
CONTROL_PLANE_SUBJECT = "dashboard"


class RefreshState:
    def __init__(self, db_path: Path, project_root: Path, interval_seconds: int, token: str) -> None:
        self.db_path = db_path
        self.project_root = project_root
        self.interval_seconds = interval_seconds
        self.token = token
        self.lock = threading.Lock()
        self.last_result: dict[str, Any] | None = None
        self.last_error = ""
        self.refreshing = False

    def refresh_now(self, trigger: str) -> dict[str, Any]:
        if not self.lock.acquire(blocking=False):
            return {"status": "already_running", "trigger": trigger}
        self.refreshing = True
        try:
            result = refresh_database(self.db_path, self.project_root)
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


def _dashboard_db_path() -> Path:
    return Path(os.getenv("GTKB_DASHBOARD_DB", str(DEFAULT_DB_PATH))).resolve()


def _project_root() -> Path:
    return Path(os.getenv("GTKB_DASHBOARD_PROJECT_ROOT", str(PROJECT_ROOT))).resolve()


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
    body {{ font-family: system-ui, -apple-system, Segoe UI, sans-serif; margin: 0; color: #102027; background: #f6f8fa; }}
    header {{ background: #103f3a; color: #fff; padding: 24px 32px; }}
    main {{ max-width: 980px; margin: 32px auto; padding: 0 20px; }}
    section {{ background: #fff; border: 1px solid #d5dde3; border-radius: 6px; padding: 20px; margin-bottom: 18px; }}
    label {{ display: block; font-weight: 650; margin-bottom: 8px; }}
    input {{ width: min(480px, 100%); padding: 10px; border: 1px solid #b8c2cc; border-radius: 4px; }}
    button {{ margin-top: 12px; padding: 10px 14px; border: 0; border-radius: 4px; background: #0b6b61; color: #fff; cursor: pointer; }}
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
    operation declares a role slot and ``dry_run`` is not set. Read-only
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
    requires_token = descriptor is not None and bool(descriptor.required_role_slots) and not dry_run

    if requires_token:
        if not state.token:
            return HTTPStatus.SERVICE_UNAVAILABLE, {
                "status": "error",
                "error": "GTKB_DASHBOARD_REFRESH_TOKEN is not configured",
            }
        if supplied_token != state.token:
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
    except Exception as exc:  # pragma: no cover - handler failure safety net
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
                    }
                )
                return
            if parsed.path == "/":
                self._send_html(_render_home(state))
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:  # noqa: N802
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
                self.send_header("Location", "/")
                self.end_headers()
                return
            # Preserve the legacy JSON shape (the underlying refresh result)
            # so existing clients of POST /refresh keep working.
            self._send_json(dict(response.get("details", {})))

        def _read_json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8") if length else ""
            if not raw:
                return {}
            try:
                parsed_body = json.loads(raw)
            except json.JSONDecodeError:
                return {}
            return parsed_body if isinstance(parsed_body, dict) else {}

        def log_message(self, format: str, *args: Any) -> None:
            print(f"{self.address_string()} - {format % args}")

        def _read_form(self) -> dict[str, list[str]]:
            length = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(length).decode("utf-8") if length else ""
            content_type = self.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    payload = json.loads(body or "{}")
                except json.JSONDecodeError:
                    return {}
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
    except Exception as exc:
        print(f"Startup dashboard refresh failed: {exc}")
    while not stop_event.wait(state.interval_seconds):
        try:
            state.refresh_now("scheduled")
        except Exception as exc:
            print(f"Scheduled dashboard refresh failed: {exc}")


def main() -> int:
    db_path = _dashboard_db_path()
    project_root = _project_root()
    token = os.getenv("GTKB_DASHBOARD_REFRESH_TOKEN", "")
    state = RefreshState(db_path, project_root, _interval_seconds(), token)
    initialize_database(db_path)

    stop_event = threading.Event()
    scheduler = threading.Thread(target=_run_scheduler, args=(state, stop_event), daemon=True)
    scheduler.start()

    host = os.getenv("GTKB_DASHBOARD_REFRESH_HOST", DEFAULT_HOST)
    port = int(os.getenv("GTKB_DASHBOARD_REFRESH_PORT", str(DEFAULT_PORT)))
    server = ThreadingHTTPServer((host, port), _make_handler(state))
    print(f"GT-KB dashboard refresh service listening on http://{host}:{port}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        stop_event.set()
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
