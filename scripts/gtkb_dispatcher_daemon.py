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
import logging
import logging.handlers
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
PID_CREATE_TIME_FILENAME = "daemon.create_time_epoch"
PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS = 0.01
# WI-4882: persistent rotating daemon activity/error log. The daemon previously
# wrote only status.json + shadow-decisions.jsonl, so an unsupervised death left
# no diagnostic trail. This log records loop start/exit, per-tick completion, and
# crucially any fatal exception that breaks the loop, so the next death is
# diagnosable.
DAEMON_LOG_FILENAME = "daemon.log"
DAEMON_LOG_MAX_BYTES = 1_000_000
DAEMON_LOG_BACKUP_COUNT = 3
WATCHDOG_HEARTBEAT_RELPATH = ".gtkb-state/ops/storm-watchdog-heartbeat.txt"
WATCHDOG_TASK_NAME_DEFAULT = "GTKB-HarnessStormWatchdog"
LOCK_SANITY_TTL_ENV_VAR = "GTKB_DISPATCHER_DAEMON_LOCK_TTL_SECONDS"
LOCK_SANITY_TTL_DEFAULT_SECONDS = 120
TICK_SECONDS_ENV_VAR = "GTKB_DISPATCHER_DAEMON_TICK_SECONDS"
DEFAULT_TICK_SECONDS = 60
DEFAULT_MAX_ITEMS = 2
# WI-4856: heartbeat-freshness window for liveness-accurate status. A daemon
# whose newest heartbeat is older than this is treated as not-fresh; combined
# with PID-liveness it gates the reported ``running`` flag so a stale lock left
# by a dead daemon no longer reports running. ~3x the default 60s tick.
HEARTBEAT_STALE_SECONDS_ENV_VAR = "GTKB_DISPATCHER_DAEMON_HEARTBEAT_STALE_SECONDS"
HEARTBEAT_STALE_DEFAULT_SECONDS = 180


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def get_daemon_logger(state_dir: Path) -> logging.Logger:
    """Return the persistent rotating daemon logger (WI-4882).

    Idempotent: re-adds no handler if one already exists. Handler setup is
    fail-soft — an OSError creating the log directory/file never propagates, so
    logging can never break daemon startup.
    """
    logger = logging.getLogger("gtkb.dispatcher_daemon")
    if not logger.handlers:
        try:
            state_dir.mkdir(parents=True, exist_ok=True)
            handler = logging.handlers.RotatingFileHandler(
                state_dir / DAEMON_LOG_FILENAME,
                maxBytes=DAEMON_LOG_MAX_BYTES,
                backupCount=DAEMON_LOG_BACKUP_COUNT,
                encoding="utf-8",
            )
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            logger.propagate = False
        except OSError:
            # Fail-soft: a logging-setup failure must never break the daemon.
            pass
    return logger


def _safe_log(logger: logging.Logger, level: str, msg: str, *args: object) -> None:
    """Emit a log record fail-soft — a logging error never breaks a tick (WI-4882)."""
    try:
        getattr(logger, level)(msg, *args)
    except Exception:  # noqa: BLE001 - logging must never break a tick or the loop
        pass


def _heartbeat_stale_seconds() -> float:
    """Return the heartbeat-freshness window in seconds (env-overridable, WI-4856)."""
    raw = os.environ.get(HEARTBEAT_STALE_SECONDS_ENV_VAR)
    if raw is None:
        return float(HEARTBEAT_STALE_DEFAULT_SECONDS)
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return float(HEARTBEAT_STALE_DEFAULT_SECONDS)
    return value if value > 0 else float(HEARTBEAT_STALE_DEFAULT_SECONDS)


def daemon_state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*DAEMON_STATE_SUBDIR)


def _daemon_state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*DAEMON_STATE_SUBDIR)


def _trigger_state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*TRIGGER_STATE_SUBDIR)


def _bridge_poller_state_dir(project_root: Path) -> Path:
    return project_root.joinpath(*BRIDGE_POLLER_STATE_SUBDIR)


def _reap_dispatched_workers(project_root: Path) -> int:
    """Reap live dispatched workers that have no exit_code sidecar (WI-4857).

    Delegates to the trigger module's ``reap_inflight_dispatched_workers`` so
    the sidecar contract stays in one place.  Wraps the call to never raise so
    a reap failure cannot break daemon startup or shutdown.

    Returns the count of workers reaped (0 when the trigger cannot be loaded).
    """
    try:
        trigger = _load_trigger_module()
        runs_dir = _bridge_poller_state_dir(project_root) / trigger.DISPATCH_RUNS_SUBDIR
        return trigger.reap_inflight_dispatched_workers(runs_dir)
    except Exception:
        return 0


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


def _pid_create_time_epoch(pid: int) -> float | None:
    """Return the OS create-time epoch for ``pid`` when available."""
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return None
    if pid_int <= 0:
        return None
    try:
        import psutil  # noqa: PLC0415

        return float(psutil.Process(pid_int).create_time())
    except Exception:  # noqa: BLE001 - unavailable/vanished PIDs are not trusted
        return None


def _pid_create_time_matches(pid: int, expected_epoch: Any) -> bool:
    try:
        expected = float(expected_epoch)
    except (TypeError, ValueError):
        return False
    actual = _pid_create_time_epoch(pid)
    if actual is None:
        return False
    return abs(actual - expected) <= PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS


def _read_pid_create_time_sidecar(state_dir: Path) -> float | None:
    try:
        return float((state_dir / PID_CREATE_TIME_FILENAME).read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _write_daemon_pid_record(state_dir: Path, pid: int) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / PID_FILENAME).write_text(str(pid) + "\n", encoding="utf-8")
    create_time = _pid_create_time_epoch(pid)
    if create_time is not None:
        (state_dir / PID_CREATE_TIME_FILENAME).write_text(f"{create_time:.6f}", encoding="utf-8")


def _clear_daemon_pid_record(state_dir: Path) -> None:
    for filename in (PID_FILENAME, PID_CREATE_TIME_FILENAME):
        try:
            (state_dir / filename).unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass


def _pid_is_running(pid: int) -> bool:
    """Best-effort cross-platform liveness probe for a process id (WI-4855)."""
    if pid <= 0:
        return False
    try:
        import psutil  # noqa: PLC0415

        return bool(psutil.pid_exists(pid))
    except Exception:  # noqa: BLE001 - degrade to OS-native fallback
        pass
    import subprocess  # noqa: PLC0415

    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _project_root_from_state_dir(state_dir: Path) -> Path:
    """Resolve the project root implied by ``.gtkb-state/dispatcher-daemon``."""
    if state_dir.name == DAEMON_STATE_SUBDIR[-1] and state_dir.parent.name == DAEMON_STATE_SUBDIR[0]:
        return state_dir.parent.parent.resolve()
    return state_dir.resolve().parent.parent


def _process_command_line(pid: int) -> list[str]:
    """Return a process command line as argv tokens when the OS exposes it."""
    try:
        import psutil  # noqa: PLC0415

        return [str(part) for part in psutil.Process(int(pid)).cmdline()]
    except Exception:  # noqa: BLE001 - unavailable/vanished PIDs are not trusted
        return []


def _path_arg_matches(value: str, expected: Path) -> bool:
    raw = str(value).strip().strip('"').strip("'")
    if not raw:
        return False
    try:
        return Path(raw).resolve() == expected.resolve()
    except (OSError, RuntimeError, ValueError):
        return os.path.normcase(os.path.abspath(raw)) == os.path.normcase(str(expected.resolve()))


def _is_daemon_loop_command(cmdline: list[str], project_root: Path) -> bool:
    """Return True for a live dispatcher daemon loop command for this root.

    This is a legacy-liveness fallback, not provenance. It exists so a daemon
    that predates the create-time sidecar still blocks duplicate starts. The
    PID-reuse safety invariant remains: unrelated live PIDs are never trusted.
    """
    script_path = (project_root / "scripts" / "gtkb_dispatcher_daemon.py").resolve()
    has_script = any(_path_arg_matches(part, script_path) for part in cmdline)
    if not has_script:
        return False
    if "--loop" not in cmdline and "run" not in cmdline:
        return False
    if "--project-root" not in cmdline:
        return True
    try:
        root_arg = cmdline[cmdline.index("--project-root") + 1]
    except (IndexError, ValueError):
        return False
    return _path_arg_matches(root_arg, project_root)


def _matching_daemon_loop_pids(state_dir: Path) -> list[int]:
    """Return live daemon-loop PIDs for this project root by command identity."""
    project_root = _project_root_from_state_dir(state_dir)
    try:
        import psutil  # noqa: PLC0415

        matches: list[int] = []
        for proc in psutil.process_iter(["pid", "cmdline"]):
            try:
                pid = int(proc.info.get("pid") or 0)
                cmdline = [str(part) for part in (proc.info.get("cmdline") or [])]
            except (TypeError, ValueError):
                continue
            if pid > 0 and _is_daemon_loop_command(cmdline, project_root):
                matches.append(pid)
        return sorted(set(matches))
    except Exception:  # noqa: BLE001 - fail closed: no scan evidence
        return []


matching_daemon_loop_pids = _matching_daemon_loop_pids


def daemon_pid_provenance_verified(state_dir: Path) -> bool:
    """Return True only when daemon.pid matches live create-time provenance."""
    pid_path = state_dir / PID_FILENAME
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return False
    if not _pid_is_running(pid):
        return False
    expected = _read_pid_create_time_sidecar(state_dir)
    if expected is None:
        try:
            lock_payload = json.loads((state_dir / LOCK_FILENAME).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        if lock_payload.get("pid") != pid:
            return False
        expected = lock_payload.get("pid_create_time_epoch")
    return _pid_create_time_matches(pid, expected)


def daemon_pid_matches_legacy_loop(state_dir: Path, pid: int) -> bool:
    """Return True when an unprovenanced recorded PID is a daemon loop command."""
    if pid <= 0 or not _pid_is_running(pid):
        return False
    return _is_daemon_loop_command(_process_command_line(pid), _project_root_from_state_dir(state_dir))


def daemon_process_alive(state_dir: Path) -> bool:
    """Return True when the PID recorded in daemon.pid is a live process.

    Single-instance enforcement (WI-4855 defect 2): detects a live-but-lockless
    daemon so ``start`` refuses to spawn a second instance even when the lock is
    stale or absent. Reads the PID file and create-time provenance written by
    ``run_loop``; PID-only evidence is not trusted because PID reuse can target
    an unrelated process.
    """
    if daemon_pid_provenance_verified(state_dir):
        return True
    pid_path = state_dir / PID_FILENAME
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        pid = 0
    if daemon_pid_matches_legacy_loop(state_dir, pid):
        return True
    matches = _matching_daemon_loop_pids(state_dir)
    excluded = {os.getpid(), os.getppid()}
    return bool([p for p in matches if p not in excluded])


def _lock_sanity_ttl_seconds() -> int:
    try:
        sanity_ttl = int(os.environ.get(LOCK_SANITY_TTL_ENV_VAR, LOCK_SANITY_TTL_DEFAULT_SECONDS))
    except (TypeError, ValueError):
        sanity_ttl = LOCK_SANITY_TTL_DEFAULT_SECONDS
    return sanity_ttl if sanity_ttl > 0 else LOCK_SANITY_TTL_DEFAULT_SECONDS


def _read_daemon_lock_payload(lock_path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _lock_owner_alive(payload: dict[str, Any] | None) -> bool:
    if not isinstance(payload, dict):
        return False
    try:
        pid = int(payload.get("pid"))
    except (TypeError, ValueError):
        return False
    if not _pid_is_running(pid):
        return False
    expected = payload.get("pid_create_time_epoch")
    if expected is None:
        return True
    return _pid_create_time_matches(pid, expected)


def acquire_daemon_lock(state_dir: Path) -> bool:
    """Return True when this process holds the single-instance daemon lock.

    Uses an atomic create to prevent two concurrent daemon starts from both
    deciding a missing/stale lock is claimable.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = state_dir / LOCK_FILENAME
    if daemon_process_alive(state_dir):
        return False
    sanity_ttl = _lock_sanity_ttl_seconds()
    payload = {
        "pid": os.getpid(),
        "pid_create_time_epoch": _pid_create_time_epoch(os.getpid()),
        "acquired_at": _now_iso(),
        "mode": "shadow",
    }
    for attempt in range(2):
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            lock_payload = _read_daemon_lock_payload(lock_path)
            try:
                age_seconds = time.time() - lock_path.stat().st_mtime
            except OSError:
                age_seconds = sanity_ttl + 1
            if age_seconds <= sanity_ttl or _lock_owner_alive(lock_payload):
                return False
            try:
                lock_path.unlink()
            except OSError:
                return False
            if attempt == 0:
                continue
            return False
        except OSError:
            return False
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True))
        return True
    return False


acquire_lock = acquire_daemon_lock


def release_daemon_lock(state_dir: Path, *, force: bool = False) -> None:
    lock_path = state_dir / LOCK_FILENAME
    if not force:
        payload = _read_daemon_lock_payload(lock_path)
        if not isinstance(payload, dict) or payload.get("pid") != os.getpid():
            return
        expected = payload.get("pid_create_time_epoch")
        if expected is not None and not _pid_create_time_matches(os.getpid(), expected):
            return
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
        poller_state_dir = _bridge_poller_state_dir(project_root)
        dispatch_state = trigger._load_dispatch_state(poller_state_dir, project_root)
        recipients_state = dispatch_state.get("recipients")
        if not isinstance(recipients_state, dict):
            recipients_state = {}
        role_map = trigger._read_role_assignments(project_root)
        harnesses = role_map.get("harnesses")
        if not isinstance(harnesses, dict):
            harnesses = {}
        remaining = list(items)
        for target in targets:
            selected, signature = trigger._target_selected_signature(target, remaining, max_items)
            h_info = harnesses.get(target.harness_id) or {}
            harness_type = str(h_info.get("harness_type") or "unknown").strip().lower()
            record: dict[str, Any] = {
                "timestamp": _now_iso(),
                "role": role_label,
                "recipient": target.dispatch_state_key,
                "harness_id": target.harness_id,
                "signature": signature,
                "would_dispatch": [getattr(item, "document_name", "") for item in selected],
                "shadow_mode": True,
                "spawned": False,
            }
            spawn_blocked_reason: str | None = None
            if not trigger._is_dispatch_ready(
                target.harness_id,
                h_info,
                project_root,
                poller_state_dir,
                role_label,
            ):
                spawn_blocked_reason = f"{harness_type}_dispatch_not_ready"
            else:
                prior = recipients_state.get(target.dispatch_state_key)
                if not isinstance(prior, dict):
                    prior = {}
                backoff_skip = trigger._provider_failure_backoff_skip(
                    prior=prior,
                    recipient=target.dispatch_state_key,
                    signature=signature,
                    state_dir=poller_state_dir,
                )
                if backoff_skip is not None:
                    spawn_blocked_reason = str(backoff_skip.get("reason") or "provider_failure_backoff_active")
            if spawn_blocked_reason is not None:
                record["reason"] = spawn_blocked_reason
            else:
                record["_spawn_target"] = target
                record["_spawn_selected"] = selected
            decisions.append(record)
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

        # Determine the recipient key to update liveness for
        recipient = None
        if target is not None:
            recipient = target.dispatch_state_key
        elif "recipient" in record:
            recipient = record["recipient"]
        elif "role" in record:
            role = record["role"]
            matching = [k for k in recipients_state if k.startswith(f"{role}:")]
            if matching:
                matching.sort(key=lambda k: str(recipients_state[k].get("updated_at") or ""), reverse=True)
                recipient = matching[0]
            else:
                recipient = role

        if recipient is not None:
            prior = recipients_state.get(recipient)
            recipient_state = dict(prior) if isinstance(prior, dict) else {}
            recipient_state["updated_at"] = _now_iso()
            recipients_state[recipient] = recipient_state
        else:
            recipient_state = None

        if target is None or not selected:
            if recipient_state is not None:
                recipient_state["last_result"] = record.get("reason") or "no_pending"
                recipient_state["pending_count"] = 0
                recipient_state["selected_count"] = 0
            continue

        signature = record.get("signature")
        if recipient_state is not None:
            prior_sig = recipient_state.get("last_dispatched_signature")
            if prior_sig is not None and prior_sig == signature:
                record["spawned"] = False
                record["spawn_reason"] = "unchanged"
                spawn_results.append({"recipient": recipient, "launched": False, "reason": "unchanged"})
                recipient_state["last_result"] = "unchanged"
                recipient_state["pending_count"] = len(selected)
                recipient_state["selected_count"] = 0
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
        if recipient_state is not None:
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
            recipient_state["pending_count"] = len(selected)
            recipient_state["selected_count"] = len(selected) if result.get("launched") else 0
        spawn_results.append(result)

    if not dry_run:
        state["updated_at"] = _now_iso()
        trigger._write_dispatch_state(state_dir, state)
    return spawn_results


def _read_watchdog_heartbeat_epoch(project_root: Path) -> float:
    """Read the storm watchdog heartbeat file; return epoch or 0.0 on failure.

    The storm watchdog writes a single line whose FIRST whitespace-delimited
    token is an ISO-8601 timestamp, followed by space-separated population
    fields (e.g. ``2026-06-26T14:21:02.09-07:00 codex=9 family=15 ... mode=...``).
    Only the leading timestamp token is parsed; the trailing fields are ignored.
    Feeding the whole line to ``datetime.fromisoformat`` raises ``ValueError`` on
    the trailing text, which would mis-read every fresh heartbeat as ``0.0``
    (dormant) and restart a healthy watchdog every tick.
    """
    hb_path = project_root / WATCHDOG_HEARTBEAT_RELPATH
    if not hb_path.is_file():
        return 0.0
    try:
        text = hb_path.read_text(encoding="utf-8").strip()
        token = text.split()[0]  # leading ISO timestamp; ignore trailing population fields
        return dt.datetime.fromisoformat(token.replace("Z", "+00:00")).timestamp()
    except (OSError, ValueError, IndexError):
        return 0.0


def _restart_storm_watchdog(task_name: str = WATCHDOG_TASK_NAME_DEFAULT) -> dict[str, Any]:
    """Fail-soft: re-run the storm watchdog scheduled task. Never raises."""
    import subprocess  # noqa: PLC0415

    try:
        run_kwargs: dict[str, object] = {
            "stdin": subprocess.DEVNULL,
            "capture_output": True,
            "timeout": 15,
        }
        if os.name == "nt":
            run_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        proc = subprocess.run(
            ["schtasks.exe", "/Run", "/TN", task_name],
            **run_kwargs,
        )
        return {"launched": proc.returncode == 0, "returncode": proc.returncode}
    except Exception as exc:  # noqa: BLE001
        return {"launched": False, "error": str(exc)}


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
    watchdog_verdict: dict[str, Any] | None = None
    watchdog_restart: dict[str, Any] | None = None
    watchdog_error: str | None = None
    try:
        monitor = _load_dispatch_monitor()
        hb_epoch = _read_watchdog_heartbeat_epoch(project_root)
        verdict = monitor.watchdog_dormancy(hb_epoch, time.time())
        watchdog_verdict = {
            "dormant": verdict.dormant,
            "age_seconds": verdict.age_seconds,
            "reason": verdict.reason,
        }
        if verdict.dormant:
            watchdog_verdict["remediation_hint"] = "restart_storm_watchdog"
            # Execute the restart only in LIVE mode. Shadow mode observes and
            # records the dormancy verdict + remediation_hint (like the
            # monitoring/health block above) but performs NO subprocess spawn,
            # per the committed shadow-never-spawns invariant
            # (test_daemon_shadow_mode_never_spawns). The daemon owns executing
            # remediation only when it is the live dispatch substrate.
            if not dry_run and mode == "live":
                watchdog_restart = _restart_storm_watchdog()
    except Exception as exc:  # noqa: BLE001 - fail-soft: never abort tick
        watchdog_error = str(exc)
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
    if watchdog_verdict is not None:
        result["watchdog_dormancy"] = watchdog_verdict
    if watchdog_restart is not None:
        result["watchdog_restart"] = watchdog_restart
    if watchdog_error is not None:
        result["watchdog_error"] = watchdog_error
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
        if watchdog_verdict is not None:
            status["watchdog_dormancy"] = watchdog_verdict
        if watchdog_restart is not None:
            status["watchdog_restart"] = watchdog_restart
        if watchdog_error is not None:
            status["watchdog_error"] = watchdog_error
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
    logger = get_daemon_logger(state_dir)
    _safe_log(logger, "info", "dispatcher daemon loop started pid=%s tick_seconds=%s", os.getpid(), tick_seconds)
    # WI-4857: holding the lock proves no prior daemon is alive — any live
    # dispatched worker at this point is an orphan from a crashed predecessor.
    _reap_dispatched_workers(project_root)
    _write_daemon_pid_record(state_dir, os.getpid())
    try:
        while True:
            try:
                run_tick(project_root, max_items=max_items)
            except Exception:  # noqa: BLE001 - WI-4882: log the fatal exception before the loop dies
                _safe_log(logger, "exception", "fatal exception in daemon tick; loop exiting pid=%s", os.getpid())
                raise
            _safe_log(logger, "info", "tick completed pid=%s", os.getpid())
            time.sleep(max(1, tick_seconds))
    finally:
        _safe_log(logger, "info", "dispatcher daemon loop exiting pid=%s", os.getpid())
        # WI-4857: reap in-flight workers before releasing the lock so a
        # graceful termination does not leave orphaned workers running.
        _reap_dispatched_workers(project_root)
        _clear_daemon_pid_record(state_dir)
        release_daemon_lock(state_dir)


def collect_daemon_status(project_root: Path) -> dict[str, Any]:
    state_dir = _daemon_state_dir(project_root)
    lock_path = state_dir / LOCK_FILENAME
    heartbeat_path = state_dir / HEARTBEAT_FILENAME
    # WI-4856 fix 2: mode/active_substrate derive from the active substrate
    # selection (mirrors run_tick), not a hardcoded "shadow".
    active_substrate = _active_substrate(project_root)
    status: dict[str, Any] = {
        "state_dir": str(state_dir),
        "running": False,
        "mode": "live" if active_substrate == DAEMON_SUBSTRATE else "shadow",
        "active_substrate": active_substrate,
        "heartbeat_path": str(heartbeat_path),
        "lock_path": str(lock_path),
    }
    lock_present = lock_path.is_file()
    if lock_present:
        try:
            status["lock"] = json.loads(lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    heartbeat_age: float | None = None
    if heartbeat_path.is_file():
        try:
            heartbeat_text = heartbeat_path.read_text(encoding="utf-8").strip()
            status["heartbeat_at"] = heartbeat_text
            parsed = dt.datetime.fromisoformat(heartbeat_text.replace("Z", "+00:00"))
            heartbeat_age = (dt.datetime.now(dt.UTC) - parsed).total_seconds()
            status["heartbeat_age_seconds"] = heartbeat_age
        except (OSError, ValueError):
            status["heartbeat_at"] = None
    # WI-4856 fix 1: derive running from process liveness + heartbeat freshness,
    # not lock presence alone. A stale lock left by a dead daemon (PID gone,
    # heartbeat aged out) no longer reports running; a cleanly stopped daemon
    # (lock released) reports not-running even if the heartbeat file lingers.
    pid_provenance_verified = daemon_pid_provenance_verified(state_dir)
    pid_alive = daemon_process_alive(state_dir)
    heartbeat_fresh = heartbeat_age is not None and heartbeat_age <= _heartbeat_stale_seconds()
    status["pid_provenance_verified"] = pid_provenance_verified
    status["running"] = bool(pid_alive or (lock_present and heartbeat_fresh))
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
