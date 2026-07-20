#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Idempotent ensure-alive entrypoint for the GT-KB dispatcher daemon (WI-4882).

Invoked by the ``GTKB-DispatcherDaemon`` Windows scheduled task on a fixed
interval. Unlike ``gt bridge dispatch daemon start`` (cli.py), which RAISES
"already running" (non-zero exit) when the daemon is alive, this entrypoint is
idempotent: it no-ops and exits 0 when the daemon is alive, and spawns a
detached daemon and exits 0 when it is dead. This is the D3 supervision
mechanism from the Daemon Resilience scope-lock (DELIB-20266276): a dedicated
scheduled task, separate from the storm-watchdog, that keeps the daemon alive
unattended.

The detached-spawn mirrors the cli ``daemon start`` path so the daemon survives
its launching task (WI-4855 true-detach semantics).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import gtkb_dispatcher_daemon as daemon  # noqa: E402
import dispatcher_generation_admission as admission  # noqa: E402

SUPERVISOR_LOCK_FILENAME = "generation-handoff-supervisor.lock"
HANDOFF_EXIT_TIMEOUT_SECONDS = 45.0
SUCCESSOR_ATTESTATION_TIMEOUT_SECONDS = 30.0
HANDOFF_POLL_SECONDS = 0.25


def _prefer_windows_gui_python(command: str) -> str:
    """Return sibling pythonw.exe for Windows python.exe commands when present."""
    if os.name != "nt":
        return command
    last_backslash = command.rfind("\\")
    last_slash = command.rfind("/")
    split_at = max(last_backslash, last_slash)
    executable_name = command[split_at + 1 :] if split_at >= 0 else command
    if executable_name.lower() != "python.exe":
        return command
    candidate = f"{command[: split_at + 1]}pythonw.exe" if split_at >= 0 else "pythonw.exe"
    return candidate if os.path.isfile(candidate) else command


def _resolve_daemon_spawn_source(
    project_root: Path,
) -> tuple[Path, str | None, dict[str, object]]:
    """Determine the daemon script path and PYTHONPATH from admission state.

    Returns (script_path, generation_id | None, spawn_meta).
    spawn_meta carries diagnostic fields for the result dict.
    """
    ad_status = admission.candidate_admission_status(project_root)

    # Preferred path: last admitted generation with intact materialization
    if (
        ad_status.get("last_admitted_generation")
        and ad_status.get("last_admitted_materialization_ok")
    ):
        last = admission.read_last_admitted(project_root)
        mat_dir = last.get("materialization_dir") if last else None
        if mat_dir:
            mat_path = Path(mat_dir)
            script = mat_path / "scripts" / "gtkb_dispatcher_daemon.py"
            if script.is_file():
                return (
                    script,
                    last["generation"],
                    {
                        "source": "admitted_generation",
                        "generation": last["generation"],
                        "materialization_dir": mat_dir,
                        "current_working_tree_generation": ad_status.get(
                            "current_working_tree_generation"
                        ),
                        "unfinalized_rejected": ad_status.get("current_unfinalized", False),
                    },
                )

    # Fallback: working-tree scripts (no admitted generation exists)
    script = _SCRIPTS_DIR / "gtkb_dispatcher_daemon.py"
    return (
        script,
        None,
        {
            "source": "working_tree",
            "reason": (
                "no_admitted_generation"
                if ad_status.get("no_admitted_generation_exists")
                else "admitted_materialization_corrupt"
            ),
        },
    )


def _spawn_detached_daemon(project_root: Path, interval: int) -> int:
    """Spawn the detached daemon loop, preferring an admitted generation.

    When an admitted generation exists with intact materialization, the daemon
    is spawned from those materialized Git-object bytes instead of the mutable
    working-tree source (WI-5429). When no admitted generation exists, falls
    back to the current working-tree scripts directory.
    """
    script_path, _generation_id, _spawn_meta = _resolve_daemon_spawn_source(
        project_root
    )
    mat_dir = _spawn_meta.get("materialization_dir")

    # Build PYTHONPATH: if spawning from admitted materialization, prepend the
    # materialized dirs so imports resolve to the admitted bytes, not working
    # tree. The canonical project root remains the data root for bridge, TAFE,
    # claims, leases, config, and audit state.
    env = os.environ.copy()
    if mat_dir:
        mat_path = Path(str(mat_dir))
        extra_paths = [
            str(mat_path / "scripts"),
            str(mat_path / "groundtruth-kb" / "src"),
        ]
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = os.pathsep.join(
            extra_paths + ([existing] if existing else [])
        )

    popen_kwargs: dict[str, object] = {
        "cwd": str(project_root),
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "env": env,
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = (
            getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
    else:
        popen_kwargs["start_new_session"] = True
    proc = subprocess.Popen(
        [
            _prefer_windows_gui_python(sys.executable),
            str(script_path),
            "--loop",
            "--project-root",
            str(project_root),
            "--tick-seconds",
            str(interval),
        ],
        **popen_kwargs,
    )
    return int(proc.pid)


def _supervisor_lock_path(state_dir: Path) -> Path:
    return state_dir / SUPERVISOR_LOCK_FILENAME


def _acquire_supervisor_lock(state_dir: Path) -> bool:
    """Serialize scheduled supervisor cycles and discard only dead-owner locks."""
    state_dir.mkdir(parents=True, exist_ok=True)
    path = _supervisor_lock_path(state_dir)
    payload = {
        "pid": os.getpid(),
        "pid_create_time_epoch": daemon._pid_create_time_epoch(os.getpid()),
        "acquired_at": daemon._now_iso(),
    }
    for attempt in range(2):
        try:
            descriptor = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            existing = daemon._read_json_object(path)
            if daemon._lock_owner_alive(existing):
                return False
            try:
                path.unlink()
            except OSError:
                return False
            if attempt == 0:
                continue
            return False
        except OSError:
            return False
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True))
        return True
    return False


def _release_supervisor_lock(state_dir: Path) -> None:
    path = _supervisor_lock_path(state_dir)
    payload = daemon._read_json_object(path)
    if not isinstance(payload, dict) or payload.get("pid") != os.getpid():
        return
    expected = payload.get("pid_create_time_epoch")
    if expected is not None and not daemon._pid_create_time_matches(os.getpid(), expected):
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _handoff_request_matches(
    request: dict[str, object],
    *,
    status: dict[str, object],
) -> bool:
    lock = status.get("lock")
    if not isinstance(lock, dict):
        return False
    return bool(
        request.get("daemon_pid") == lock.get("pid")
        and request.get("daemon_pid_create_time_epoch") == lock.get("pid_create_time_epoch")
        and request.get("observed_loaded_generation") == status.get("loaded_generation")
    )


def _new_handoff_request(status: dict[str, object], target_generation: str) -> dict[str, object] | None:
    lock = status.get("lock")
    if not isinstance(lock, dict):
        return None
    pid = lock.get("pid")
    create_time = lock.get("pid_create_time_epoch")
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0 or create_time is None:
        return None
    return {
        "schema_version": 1,
        "phase": "requested",
        "requested_at": daemon._now_iso(),
        "daemon_pid": pid,
        "daemon_pid_create_time_epoch": create_time,
        "observed_loaded_generation": status.get("loaded_generation"),
        "target_generation": target_generation,
    }


def _wait_for_daemon_exit(project_root: Path, state_dir: Path) -> bool:
    deadline = time.monotonic() + HANDOFF_EXIT_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if not daemon.daemon_process_alive(state_dir) and not (state_dir / daemon.LOCK_FILENAME).exists():
            return True
        time.sleep(HANDOFF_POLL_SECONDS)
    return False


def _wait_for_successor_generation(project_root: Path, expected_generation: str) -> dict[str, object] | None:
    deadline = time.monotonic() + SUCCESSOR_ATTESTATION_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        status = daemon.read_daemon_status(project_root)
        if (
            status.get("running") is True
            and status.get("pid_provenance_verified") is True
            and status.get("loaded_generation") == expected_generation
            and status.get("current_generation") == expected_generation
            and status.get("generation_match") is True
        ):
            return status
        time.sleep(HANDOFF_POLL_SECONDS)
    return None


def _spawn_when_quiescent(project_root: Path, state_dir: Path, interval: int) -> dict[str, object]:
    quiescence = daemon.dispatch_quiescence(project_root)
    if not quiescence.get("known"):
        return {
            "action": "generation_handoff_failed",
            "running": False,
            "reason": "dispatch_quiescence_unknown",
            "quiescence": quiescence,
        }
    if quiescence.get("live_worker_count") or quiescence.get("live_document_lease_count"):
        return {
            "action": "generation_handoff_deferred",
            "running": False,
            "reason": "dispatch_work_active",
            "quiescence": quiescence,
        }
    request = daemon.read_generation_handoff_request(project_root)
    if request is not None:
        daemon.clear_generation_handoff_request(project_root)

    # WI-5429: compute admission status before spawn for diagnostics
    ad_status = admission.candidate_admission_status(project_root)

    pid = _spawn_detached_daemon(project_root, interval)
    expected = daemon.current_runtime_generation(project_root).get("generation")
    if not isinstance(expected, str):
        return {
            "action": "generation_handoff_failed",
            "running": True,
            "pid": pid,
            "reason": "current_generation_unavailable_after_spawn",
        }
    successor = _wait_for_successor_generation(project_root, expected)
    if successor is None:
        return {
            "action": "generation_handoff_failed",
            "running": True,
            "pid": pid,
            "reason": "successor_generation_attestation_timeout",
            "expected_generation": expected,
        }
    result: dict[str, object] = {
        "action": "spawned",
        "running": True,
        "pid": successor.get("lock", {}).get("pid", pid),
        "loaded_generation": expected,
    }
    if ad_status.get("current_unfinalized"):
        result["unfinalized_generation_rejected"] = True
        result["last_admitted_generation"] = ad_status.get("last_admitted_generation")
    if ad_status.get("last_admitted_generation"):
        result["last_admitted_generation"] = ad_status.get("last_admitted_generation")
    return result


def _ensure_daemon_running_locked(project_root: Path, state_dir: Path, interval: int) -> dict[str, object]:
    status = daemon.read_daemon_status(project_root)
    alive = bool(status.get("running")) or daemon.daemon_process_alive(state_dir)
    if not alive:
        # WI-5429: when daemon is dead, surface admission status for
        # diagnostics. Recovery will prefer the last admitted generation;
        # unfinalized working-tree changes are rejected as executable authority.
        ad_status = admission.candidate_admission_status(project_root)
        spawn_result = _spawn_when_quiescent(project_root, state_dir, interval)
        if ad_status.get("no_admitted_generation_exists"):
            spawn_result["admission"] = "no_admitted_generation_exists"
        elif ad_status.get("current_already_admitted"):
            spawn_result["admission"] = "current_already_admitted"
        elif ad_status.get("current_unfinalized"):
            spawn_result["admission"] = "unfinalized_generation_rejected"
            spawn_result["last_admitted_generation"] = ad_status.get(
                "last_admitted_generation"
            )
        return spawn_result
    if status.get("generation_match") is True:
        return {
            "action": "noop",
            "running": True,
            "loaded_generation": status.get("loaded_generation"),
        }

    loaded_generation = status.get("loaded_generation")
    current_generation = status.get("current_generation")
    if not isinstance(loaded_generation, str) or not isinstance(current_generation, str):
        return {
            "action": "generation_handoff_failed",
            "running": True,
            "reason": "runtime_generation_unknown",
            "loaded_generation": loaded_generation,
            "current_generation": current_generation,
        }
    if status.get("pid_provenance_verified") is not True:
        return {
            "action": "generation_handoff_failed",
            "running": True,
            "reason": "daemon_pid_provenance_unverified",
            "loaded_generation": loaded_generation,
            "current_generation": current_generation,
        }

    request = daemon.read_generation_handoff_request(project_root)
    if request is None:
        request = _new_handoff_request(status, current_generation)
        if request is None:
            return {
                "action": "generation_handoff_failed",
                "running": True,
                "reason": "daemon_identity_unavailable",
            }
        daemon.write_generation_handoff_request(project_root, request)
        return {
            "action": "generation_handoff_deferred",
            "running": True,
            "reason": "handoff_requested",
            "loaded_generation": loaded_generation,
            "current_generation": current_generation,
        }
    if not _handoff_request_matches(request, status=status):
        return {
            "action": "generation_handoff_failed",
            "running": True,
            "reason": "handoff_request_identity_mismatch",
        }
    if request.get("target_generation") != current_generation:
        retargeted_request = _new_handoff_request(status, current_generation)
        if retargeted_request is None:
            return {
                "action": "generation_handoff_failed",
                "running": True,
                "reason": "daemon_identity_unavailable",
            }
        retargeted_request["supersedes_target_generation"] = request.get("target_generation")
        daemon.write_generation_handoff_request(project_root, retargeted_request)
        return {
            "action": "generation_handoff_deferred",
            "running": True,
            "reason": "handoff_retargeted",
            "loaded_generation": loaded_generation,
            "current_generation": current_generation,
        }

    handoff = status.get("generation_handoff")
    handoff_state = handoff.get("state") if isinstance(handoff, dict) else None
    if handoff_state == "generation_handoff_failed":
        return {
            "action": "generation_handoff_failed",
            "running": True,
            "reason": handoff.get("reason", "daemon_handoff_failed"),
        }
    if handoff_state != "generation_handoff_ready" and request.get("phase") != "commit":
        return {
            "action": "generation_handoff_deferred",
            "running": True,
            "reason": "daemon_draining",
            "handoff_state": handoff_state,
        }

    quiescence = daemon.dispatch_quiescence(project_root)
    if not quiescence.get("known"):
        return {
            "action": "generation_handoff_failed",
            "running": True,
            "reason": "dispatch_quiescence_unknown",
            "quiescence": quiescence,
        }
    if quiescence.get("live_worker_count") or quiescence.get("live_document_lease_count"):
        return {
            "action": "generation_handoff_deferred",
            "running": True,
            "reason": "dispatch_work_active",
            "quiescence": quiescence,
        }

    old_pid = request["daemon_pid"]
    if request.get("phase") != "commit":
        committed_request = dict(request)
        committed_request["phase"] = "commit"
        committed_request["committed_at"] = daemon._now_iso()
        daemon.write_generation_handoff_request(project_root, committed_request)
    if not _wait_for_daemon_exit(project_root, state_dir):
        return {
            "action": "generation_handoff_deferred",
            "running": True,
            "reason": "daemon_exit_pending",
            "old_pid": old_pid,
        }

    daemon.clear_generation_handoff_request(project_root)
    pid = _spawn_detached_daemon(project_root, interval)
    successor = _wait_for_successor_generation(project_root, current_generation)
    if successor is None:
        return {
            "action": "generation_handoff_failed",
            "running": True,
            "reason": "successor_generation_attestation_timeout",
            "old_pid": old_pid,
            "pid": pid,
            "expected_generation": current_generation,
        }
    return {
        "action": "generation_handoff_completed",
        "running": True,
        "old_pid": old_pid,
        "pid": successor.get("lock", {}).get("pid", pid),
        "loaded_generation": current_generation,
    }


def ensure_daemon_running(project_root: Path, interval: int) -> dict[str, object]:
    """Idempotently ensure the current dispatcher daemon generation is running.

    Returns a result dict describing the action taken. Never raises on the
    already-running current-generation path.
    """
    state_dir = daemon.daemon_state_dir(project_root)
    if not _acquire_supervisor_lock(state_dir):
        return {
            "action": "generation_handoff_deferred",
            "running": bool(daemon.read_daemon_status(project_root).get("running")),
            "reason": "supervisor_cycle_already_active",
        }
    try:
        return _ensure_daemon_running_locked(project_root, state_dir, interval)
    finally:
        _release_supervisor_lock(state_dir)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Idempotently ensure the GT-KB dispatcher daemon is running (WI-4882 supervisor)."
    )
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--interval", type=int, default=30, help="Daemon tick interval seconds.")
    args = parser.parse_args(argv)
    result = ensure_daemon_running(args.project_root.resolve(), args.interval)
    suffix = f" pid={result['pid']}" if "pid" in result else ""
    print(f"ensure-dispatcher-daemon: {result['action']} running={result['running']}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
