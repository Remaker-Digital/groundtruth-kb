#!/usr/bin/env python3
"""Claude Code Stop hook -- Advisory-to-Backlog Router scan.

Thin wrapper that invokes ``scripts/advisory_backlog_router.py`` on Stop
events. Reads the last-scan timestamp from
``.gtkb-state/advisory-router/last-scan.json`` and constrains the scan with
``--since <date>`` so per-Stop cost stays sub-second.

Failure modes are silent: the router is non-critical observability machinery,
and Stop-hook errors should never block the agent's turn from completing.

Stdin:  JSON (Stop hook payload; discarded)
Stdout: JSON ``{}`` (no block, no message)
Exit:   Always 0

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
LAST_SCAN_PATH = PROJECT_DIR / ".gtkb-state" / "advisory-router" / "last-scan.json"
ROUTER_SCRIPT = PROJECT_DIR / "scripts" / "advisory_backlog_router.py"
ROUTER_MODULE_NAME = "advisory_backlog_router_stop_hook"
DEFAULT_SCAN_HORIZON_DAYS = 7


def _emit_pass() -> None:
    sys.stdout.write(json.dumps({}))


def _load_router_module():
    """Load the router script as a module without triggering its main()."""
    spec = importlib.util.spec_from_file_location(ROUTER_MODULE_NAME, ROUTER_SCRIPT)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[ROUTER_MODULE_NAME] = module
    spec.loader.exec_module(module)
    return module


def _since_from_last_scan() -> date | None:
    """Pick a ``--since`` filter from last-scan.json's finished_at, with a
    safety horizon. Returns None when no prior scan exists (the first run
    sweeps the full history once).
    """
    if not LAST_SCAN_PATH.is_file():
        return None
    try:
        payload = json.loads(LAST_SCAN_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    raw = payload.get("last_scan_finished_at")
    if not isinstance(raw, str) or not raw:
        return None
    try:
        text = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    # Re-scan a small window so a backdated INSIGHTS file added retroactively
    # is not silently skipped.
    return (parsed.date() - timedelta(days=DEFAULT_SCAN_HORIZON_DAYS))


def main() -> None:
    # Discard stdin; we do not depend on the Stop payload.
    try:
        sys.stdin.read()
    except Exception:  # noqa: BLE001
        pass

    if not ROUTER_SCRIPT.is_file():
        _emit_pass()
        return

    try:
        module = _load_router_module()
    except Exception:  # noqa: BLE001
        _emit_pass()
        return
    if module is None:
        _emit_pass()
        return

    since = _since_from_last_scan()
    try:
        module.run(
            project_root=PROJECT_DIR,
            source="both",
            since=since,
            dry_run=False,
        )
    except Exception:  # noqa: BLE001 - never block the agent's turn
        pass
    _emit_pass()


if __name__ == "__main__":
    main()
