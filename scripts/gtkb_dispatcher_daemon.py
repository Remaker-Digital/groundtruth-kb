#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GT-KB dispatcher daemon — shadow by default; substrate-gated live (WI-4787/WI-4848).

Persistent always-on loop that owns the dispatch decision path. Default substrate
stays shadow (records, never spawns). When ``bridge-substrate.json`` names the
daemon substrate, live ticks reuse ``cross_harness_bridge_trigger._spawn_harness``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

_PACKAGE_SRC = _SCRIPTS_DIR.parent / "groundtruth-kb" / "src"
if _PACKAGE_SRC.is_dir() and str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

DAEMON_STATE_SUBDIR = (".gtkb-state", "dispatcher-daemon")
TRIGGER_STATE_SUBDIR = (".gtkb-state", "cross-harness-trigger")
BRIDGE_POLLER_STATE_SUBDIR = (".gtkb-state", "bridge-poller")
DAEMON_SUBSTRATE = "dispatcher_daemon"
DEFAULT_SUBSTRATE = "cross_harness_trigger"
LOCK_FILENAME = "daemon.lock"
HEARTBEAT_FILENAME = "heartbeat.txt"
SHADOW_LOG_FILENAME = "shadow-decisions.jsonl"
STATUS_FILENAME = "status.json"
PID_FILENAME = "daemon.pid"
LOCK_SANITY_TTL_ENV_VAR = "GTKB_DISPATCHER_DAEMON_LOCK_TTL_SECONDS"
LOCK_SANITY_TTL_DEFAULT_SECONDS = 120
TICK_SECONDS_ENV_VAR = "GTKB_DISPATCHER_DAEMON_TICK_SECONDS"
DEFAULT_TICK_SECONDS = 60
DEFAULT_MAX_ITEMS = 2


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def daemon_state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*DAEMON_STATE_SUBDIR)


def _daemon_state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*DAEMON_STATE_SUBDIR)


def _trigger_state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*TRIGGER_STATE_SUBDIR)


def _bridge_poller_state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*BRIDGE_POLLER_STATE_SUBDIR)


def _active_substrate(project_root: Path) -> str:
    """Read harness-state/bridge-substrate.json substrate; fail-soft default."""
    path = project_root / "harness-state" / "bridge-substrate.json"
    if not path.is_file():
        return DEFAULT_SUBSTRATE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            substrate = data.get("substrate")
            if isinstance(substrate, str) and substrate.strip():
                return substrate.strip()
    except Exception:
        pass
    return DEFAULT_SUBSTRATE


def _public_decision(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def _load_trigger_module():
    name = "_cross_harness_bridge_trigger_for_daemon"
    if name in sys.modules:
        return sys.modules[name]
    trigger_path = _SCRIPTS_DIR / "cross_harness_bridge_trigger.py"
    spec = importlib.util.spec_from_file_location(name, trigger_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load cross-harness trigger from {trigger_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_dispatch_monitor():
    name = "_dispatch_monitor_for_daemon"
    if name in sys.modules:
        return sys.modules[name]
    monitor_path = _SCRIPTS_DIR / "ops" / "dispatch_monitor.py"
    spec = importlib.util.spec_from_file_location(name, monitor_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load dispatch monitor from {monitor_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _health_response_to_json(health: dict) -> dict[str, dict]:
    return {
        role: {
            "action": action.action,
            "reasons": list(action.reasons),
            "remediation_hint": action.remediation_hint,
        }
        for role, action in health.items()
    }


def _resolve_project_root(explicit: Path | None) -> Path:
    if explicit is not None:
        candidate = explicit.resolve()
        if not (candidate / "groundtruth.toml").is_file():
            raise SystemExit(f"--project-root {candidate} lacks groundtruth.toml")
        return candidate
    try:
        from groundtruth_kb.bridge.paths import resolve_project_root

        return resolve_project_root()
    except Exception:
        pass
    env_root = os.environ.get("GTKB_PROJECT_ROOT")
    if env_root:
        candidate = Path(env_root).resolve()
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    raise SystemExit("Could not resolve GT-KB project root.")


def acquire_daemon_lock(state_dir: Path) -> bool:
    """Return True when this process holds the single-instance daemon lock."""
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = state_dir / LOCK_FILENAME
    try:
        sanity_ttl = int(os.environ.get(LOCK_SANITY_TTL_ENV_VAR, LOCK_SANITY_TTL_DEFAULT_SECONDS))
    except (TypeError, ValueError):
        sanity_ttl = LOCK_SANITY_TTL_DEFAULT_SECONDS
    if sanity_ttl <= 0:
        sanity_ttl = LOCK_SANITY_TTL_DEFAULT_SECONDS
    if lock_path.is_file():
        try:
            age_seconds = time.time() - lock_path.stat().st_mtime
        except OSError:
            age_seconds = sanity_ttl + 1
        if age_seconds <= sanity_ttl:
            return False
    payload = {"pid": os.getpid(), "acquired_at": _now_iso(), "mode": "shadow"}
    try:
        lock_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    except OSError:
        return False
    return True


acquire_lock = acquire_daemon_lock


def release_daemon_lock(state_dir: Path) -> None:
    lock_path = state_dir / LOCK_FILENAME
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


release_lock = release_daemon_lock


def write_heartbeat(state_dir: Path) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / HEARTBEAT_FILENAME).write_text(_now_iso() + "\n", encoding="utf-8")


def _append_shadow_decision(state_dir: Path, record: dict[str, Any]) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / SHADOW_LOG_FILENAME
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def compute_shadow_decisions(
    project_root: Path,
    *,
    max_items: int = DEFAULT_MAX_ITEMS,
) -> list[dict[str, Any]]:
    """Compute per-role shadow dispatch decisions without spawning."""
    trigger = _load_trigger_module()
    index_text = trigger._read_bridge_state_live(project_root)
    actionable_for_prime, actionable_for_codex = trigger._compute_actionable(index_text, project_root)
    trigger_state_dir = _trigger_state_dir(project_root)
    decisions: list[dict[str, Any]] = []
    for role_label, items in (
        ("prime-builder", actionable_for_prime),
        ("loyal-opposition", actionable_for_codex),
    ):
        try:
            targets = trigger._resolve_dispatch_targets(
                role_label,
                project_root,
                trigger_state_dir,
                items=items,
            )
        except ValueError as exc:
            decisions.append(
                {
                    "timestamp": _now_iso(),
                    "role": role_label,
                    "reason": "dispatch_target_resolution_failed",
                    "error_message": str(exc),
                    "shadow_mode": True,
                    "spawned": False,
                }
            )
            continue
        if not targets:
            decisions.append(
                {
                    "timestamp": _now_iso(),
                    "role": role_label,
                    "reason": "no_active_target_for_role",
                    "signature": trigger._signature(items),
                    "shadow_mode": True,
                    "spawned": False,
                }
            )
            continue
        remaining = list(items)
        for target in targets:
            selected, signature = trigger._target_selected_signature(target, remaining, max_items)
            decisions.append(
                {
                    "timestamp": _now_iso(),
                    "role": role_label,
                    "recipient": target.dispatch_state_key,
                    "harness_id": target.harness_id,
                    "signature": signature,
                    "would_dispatch": [getattr(item, "document_name", "") for item in selected],
                    "shadow_mode": True,
                    "spawned": False,
                    "_spawn_target": target,
                    "_spawn_selected": selected,
                }
            )
            if not selected:
                break
            remaining = trigger._without_selected_dispatch_items(remaining, selected)
            if not any(getattr(item, "dispatchable", True) for item in remaining):
                break
    return decisions


def _execute_live_spawns(
    project_root: Path,
    decision_records: list[dict[str, Any]],
    *,
    max_items: int,
    dry_run: bool,
) -> list[dict[str, Any]]:
    """Spawn workers for daemon-substrate ticks via trigger _spawn_harness."""
    trigger = _load_trigger_module()
    state_dir = _bridge_poller_state_dir(project_root)
    state = trigger._load_dispatch_state(state_dir, project_root)
    recipients_state = state.get("recipients")
    if not isinstance(recipients_state, dict):
        recipients_state = {}
        state["recipients"] = recipients_state

    spawn_results: list[dict[str, Any]] = []
    for record in decision_records:
        target = record.get("_spawn_target")
        selected = record.get("_spawn_selected") or []
        if target is None or not selected:
            continue
        recipient = target.dispatch_state_key
        signature = record.get("signature")
        prior = recipients_state.get(recipient, {})
        if isinstance(prior, dict):
            prior_sig = prior.get("last_dispatched_signature")
            if prior_sig is not None and prior_sig == signature:
                record["spawned"] = False
                record["spawn_reason"] = "unchanged"
                spawn_results.append({"recipient": recipient, "launched": False, "reason": "unchanged"})
                continue

        spawn_items = list(reversed(selected))
        result = trigger._spawn_harness(
            target=target,
            items=spawn_items,
            project_root=project_root,
            state_dir=state_dir,
            max_items=max_items,
            dry_run=dry_run,
        )
        recipient_state = recipients_state.get(recipient)
        if not isinstance(recipient_state, dict):
            recipient_state = {}
        recipient_state["updated_at"] = _now_iso()
        if result.get("launched"):
            recipient_state["last_dispatched_signature"] = signature
            recipient_state["signature"] = signature
            record["spawned"] = True
        else:
            record["spawned"] = False
            record["spawn_reason"] = result.get("reason")
        recipient_state["last_result"] = result.get("reason") or (
            "launched" if result.get("launched") else "not_launched"
        )
        recipients_state[recipient] = recipient_state
        spawn_results.append(result)

    if not dry_run:
        state["updated_at"] = _now_iso()
        trigger._write_dispatch_state(state_dir, state)
    return spawn_results


def run_tick(
    project_root: Path,
    *,
    max_items: int = DEFAULT_MAX_ITEMS,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Execute one tick: substrate-gated shadow or live dispatch."""
    state_dir = _daemon_state_dir(project_root)
    active_substrate = _active_substrate(project_root)
    mode = "live" if active_substrate == DAEMON_SUBSTRATE else "shadow"
    raw_decisions = compute_shadow_decisions(project_root, max_items=max_items)
    for record in raw_decisions:
        record["shadow_mode"] = mode == "shadow"
        if mode == "live" and "spawned" not in record:
            record["spawned"] = False

    spawn_results: list[dict[str, Any]] = []
    if mode == "live":
        spawn_results = _execute_live_spawns(
            project_root,
            raw_decisions,
            max_items=max_items,
            dry_run=dry_run,
        )

    decisions = [_public_decision(record) for record in raw_decisions]
    monitoring: dict[str, Any] | None = None
    health: dict[str, dict] | None = None
    monitoring_error: str | None = None
    try:
        monitor = _load_dispatch_monitor()
        outcomes = monitor.gather_outcomes(project_root)
        snapshot = monitor.compute_snapshot(outcomes, caps={}, now=time.time())
        response = monitor.health_response(snapshot)
        monitoring = snapshot.to_json_dict()
        health = _health_response_to_json(response)
    except Exception as exc:  # noqa: BLE001 - fail-soft monitoring must not break tick
        monitoring_error = str(exc)
    tick_at = _now_iso()
    result: dict[str, Any] = {
        "tick_at": tick_at,
        "mode": mode,
        "active_substrate": active_substrate,
        "decisions": decisions,
        "dry_run": dry_run,
    }
    if spawn_results:
        result["spawn_results"] = spawn_results
    if monitoring is not None:
        result["monitoring"] = monitoring
    if health is not None:
        result["health"] = health
    if monitoring_error is not None:
        result["monitoring_error"] = monitoring_error
    if not dry_run:
        for record in decisions:
            _append_shadow_decision(state_dir, record)
        write_heartbeat(state_dir)
        status: dict[str, Any] = {
            "updated_at": tick_at,
            "mode": mode,
            "active_substrate": active_substrate,
            "decision_count": len(decisions),
            "pid": os.getpid(),
        }
        if spawn_results:
            status["spawn_count"] = sum(1 for item in spawn_results if item.get("launched"))
        if monitoring is not None:
            status["monitoring"] = monitoring
        if health is not None:
            status["health"] = health
        if monitoring_error is not None:
            status["monitoring_error"] = monitoring_error
        (state_dir / STATUS_FILENAME).write_text(json.dumps(status, indent=2), encoding="utf-8")
    return result


def run_loop(
    project_root: Path,
    *,
    max_items: int = DEFAULT_MAX_ITEMS,
    tick_seconds: int = DEFAULT_TICK_SECONDS,
) -> None:
    state_dir = _daemon_state_dir(project_root)
    if not acquire_daemon_lock(state_dir):
        raise SystemExit("another dispatcher daemon instance is running")
    (state_dir / PID_FILENAME).write_text(str(os.getpid()) + "\n", encoding="utf-8")
    try:
        while True:
            run_tick(project_root, max_items=max_items)
            time.sleep(max(1, tick_seconds))
    finally:
        try:
            (state_dir / PID_FILENAME).unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass
        release_daemon_lock(state_dir)


def collect_daemon_status(project_root: Path) -> dict[str, Any]:
    state_dir = _daemon_state_dir(project_root)
    lock_path = state_dir / LOCK_FILENAME
    heartbeat_path = state_dir / HEARTBEAT_FILENAME
    status: dict[str, Any] = {
        "state_dir": str(state_dir),
        "running": False,
        "mode": "shadow",
        "heartbeat_path": str(heartbeat_path),
        "lock_path": str(lock_path),
    }
    if lock_path.is_file():
        try:
            lock_payload = json.loads(lock_path.read_text(encoding="utf-8"))
            status["lock"] = lock_payload
            status["running"] = True
        except (OSError, json.JSONDecodeError):
            status["running"] = lock_path.is_file()
    if heartbeat_path.is_file():
        try:
            heartbeat_text = heartbeat_path.read_text(encoding="utf-8").strip()
            status["heartbeat_at"] = heartbeat_text
            parsed = dt.datetime.fromisoformat(heartbeat_text.replace("Z", "+00:00"))
            age = (dt.datetime.now(dt.UTC) - parsed).total_seconds()
            status["heartbeat_age_seconds"] = age
        except (OSError, ValueError):
            status["heartbeat_at"] = None
    log_path = state_dir / SHADOW_LOG_FILENAME
    if log_path.is_file():
        try:
            lines = log_path.read_text(encoding="utf-8").splitlines()
            if lines:
                last = json.loads(lines[-1])
                status["last_decision"] = last
                status["last_shadow_decision"] = last
        except (OSError, json.JSONDecodeError):
            pass
    return status


read_daemon_status = collect_daemon_status


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GT-KB dispatcher daemon (shadow mode).")
    subparsers = parser.add_subparsers(dest="command")
    run_parser = subparsers.add_parser("run", help="Run the daemon loop until interrupted.")
    run_parser.add_argument("--project-root", type=Path, default=None)
    run_parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS)
    run_parser.add_argument("--interval", type=int, default=None, help="Tick interval in seconds.")
    run_parser.add_argument("--tick-seconds", type=int, default=None, help="Alias for --interval.")
    tick_parser = subparsers.add_parser("tick", help="Run one shadow tick and exit.")
    tick_parser.add_argument("--project-root", type=Path, default=None)
    tick_parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS)
    tick_parser.add_argument("--dry-run", action="store_true")
    status_parser = subparsers.add_parser("status", help="Print daemon status JSON and exit.")
    status_parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS)
    parser.add_argument("--once", action="store_true", help="Run one tick and exit.")
    parser.add_argument("--loop", action="store_true", help="Run until interrupted.")
    parser.add_argument("--tick-seconds", type=int, default=None)
    parser.add_argument("--interval", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true", help="Print daemon status JSON and exit.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "status" or getattr(args, "status", False):
        project_root = _resolve_project_root(args.project_root)
        print(json.dumps(collect_daemon_status(project_root), indent=2, sort_keys=True))
        return 0
    if args.command == "tick" or getattr(args, "once", False):
        project_root = _resolve_project_root(args.project_root)
        dry_run = getattr(args, "dry_run", False)
        result = run_tick(project_root, max_items=args.max_items, dry_run=dry_run)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "run" or getattr(args, "loop", False):
        project_root = _resolve_project_root(args.project_root)
        tick_seconds = getattr(args, "interval", None) or getattr(args, "tick_seconds", None)
        if tick_seconds is None:
            try:
                tick_seconds = int(os.environ.get(TICK_SECONDS_ENV_VAR, DEFAULT_TICK_SECONDS))
            except (TypeError, ValueError):
                tick_seconds = DEFAULT_TICK_SECONDS
        run_loop(project_root, max_items=args.max_items, tick_seconds=tick_seconds)
        return 0
    project_root = _resolve_project_root(getattr(args, "project_root", None))
    result = run_tick(project_root, max_items=getattr(args, "max_items", DEFAULT_MAX_ITEMS))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
