#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Heartbeat watchdog for the GT-KB dispatcher daemon (WI-4787)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from gtkb_dispatcher_daemon import (  # noqa: E402
    HEARTBEAT_FILENAME,
    _daemon_state_dir,
    _resolve_project_root,
)

DEFAULT_STALE_SECONDS = 180
ALERTS_FILENAME = "heartbeat-alerts.jsonl"


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def evaluate_heartbeat(
    project_root: Path,
    *,
    stale_seconds: int = DEFAULT_STALE_SECONDS,
) -> dict[str, Any]:
    state_dir = _daemon_state_dir(project_root)
    heartbeat_path = state_dir / HEARTBEAT_FILENAME
    result: dict[str, Any] = {
        "evaluated_at": _now_iso(),
        "heartbeat_path": str(heartbeat_path),
        "stale_seconds_threshold": stale_seconds,
        "stale": True,
    }
    if not heartbeat_path.is_file():
        result["reason"] = "missing_heartbeat"
        return result
    try:
        heartbeat_text = heartbeat_path.read_text(encoding="utf-8").strip()
        result["heartbeat_at"] = heartbeat_text
        parsed = dt.datetime.fromisoformat(heartbeat_text.replace("Z", "+00:00"))
        age = (dt.datetime.now(dt.UTC) - parsed).total_seconds()
        result["heartbeat_age_seconds"] = age
        result["stale"] = age > stale_seconds
        if result["stale"]:
            result["reason"] = "daemon_stale"
        else:
            result["reason"] = "heartbeat_fresh"
    except (OSError, ValueError) as exc:
        result["reason"] = "heartbeat_unreadable"
        result["error_message"] = str(exc)
    return result


def append_alert(state_dir: Path, evaluation: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    alert_path = state_dir / ALERTS_FILENAME
    with alert_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(evaluation, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="GT-KB dispatcher daemon heartbeat watchdog.")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--stale-seconds", type=int, default=DEFAULT_STALE_SECONDS)
    parser.add_argument("--alert-on-stale", action="store_true")
    args = parser.parse_args(argv)
    project_root = _resolve_project_root(args.project_root)
    evaluation = evaluate_heartbeat(project_root, stale_seconds=args.stale_seconds)
    if args.alert_on_stale and evaluation.get("stale"):
        append_alert(_daemon_state_dir(project_root), evaluation)
    print(json.dumps(evaluation, indent=2, sort_keys=True))
    return 1 if evaluation.get("stale") else 0


if __name__ == "__main__":
    raise SystemExit(main())
