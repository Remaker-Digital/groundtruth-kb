#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Read-only dispatch monitoring detector for the GT-KB dispatcher daemon (WI-4790 slice 1).

Active-monitoring slice 1 of WI-4790 (Phase 3). This module is the DETECTION
foundation the daemon's health and the later remediation slices (liveness
probing; hold->auto-remediate->escalate) consume. It is pure and read-only: it
observes dispatch evidence and emits a structured ``DispatchMonitorSnapshot``;
it mutates no dispatch state and changes no dispatch behavior.

Mirrors the gather-vs-pure-decision split used by
``scripts/ops/storm_watchdog_reap.py``: ``classify_outcome`` and
``compute_snapshot`` are pure functions of their inputs (no clock / IO /
randomness inside), so they are fully unit-testable; the thin gather + JSON emit
live in ``main``.

State-dir roots scanned by ``main`` (per the -002 GO review note): BOTH
``.gtkb-state/cross-harness-trigger`` and ``.gtkb-state/bridge-poller`` -- the two
dispatch-state directories the cross-harness trigger uses -- so the snapshot
reflects all dispatch evidence regardless of which substrate produced it.

``classify_outcome`` defines the CANONICAL run-outcome error-class taxonomy for
monitoring. It is intentionally NOT byte-for-byte parity with the trigger's
``_classify_failure_record`` / ``_classify_invocation_outcome`` helpers (those
classify WinError messages and per-invocation ``last_result`` diagnostics, a
different question). This taxonomy classifies the *outcome of a dispatched
worker*.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

DEFAULT_STATE_DIRS = (
    ".gtkb-state/cross-harness-trigger",
    ".gtkb-state/bridge-poller",
)
DISPATCH_RUNS_SUBDIR = "dispatch-runs"
DISPATCH_FAILURES_FILENAME = "dispatch-failures.jsonl"

DEFAULT_WINDOW_SECONDS = 3600
# Backstop matching the storm-watchdog max-lifetime (WI-4828) and the
# run_with_status worker-lifetime timeout (WI-4806 / WI-4845): a record believed
# in-flight (no exit) older than this is a stale/phantom record, not a healthy
# in-flight worker.
DEFAULT_MAX_LIFETIME_SECONDS = 900
# run_with_status.py TIMEOUT_EXIT_CODE (WI-4806) and the Windows
# process-terminated-abruptly code observed in WI-4674 dispatch evidence.
WORKER_KILL_EXIT_CODES = frozenset({124, 4294967295})
DEFAULT_PER_ROLE_CAP = 3

# Canonical run-outcome monitoring taxonomy.
CLASS_SUCCESS = "success"
CLASS_IN_FLIGHT = "in_flight"
CLASS_WORKER_TIMEOUT = "worker_timeout"
CLASS_CORRUPT_OUTPUT = "corrupt_output"
CLASS_PROVIDER_FAILURE = "provider_failure"
CLASS_CAP_REACHED = "cap_reached"
CLASS_NO_ACTIVE_TARGET = "no_active_target"
CLASS_SUBPROCESS_FAILED = "subprocess_failed"
CLASS_OTHER = "other"

ERROR_CLASSES = (
    CLASS_SUCCESS,
    CLASS_IN_FLIGHT,
    CLASS_WORKER_TIMEOUT,
    CLASS_CORRUPT_OUTPUT,
    CLASS_PROVIDER_FAILURE,
    CLASS_CAP_REACHED,
    CLASS_NO_ACTIVE_TARGET,
    CLASS_SUBPROCESS_FAILED,
    CLASS_OTHER,
)

_ROLE_TOKENS = ("loyal-opposition", "prime-builder")


@dataclass(frozen=True)
class DispatchOutcome:
    """One parsed dispatch outcome (a dispatch-run sidecar set or a failure record)."""

    role: str
    harness_id: str | None
    launched: bool
    exit_code: int | None  # None = no exit recorded (believed in-flight)
    has_verdict: bool
    stdout_bytes: int
    error_message: str
    created_epoch: float
    pid_alive: bool


@dataclass(frozen=True)
class RoleMonitorSnapshot:
    role: str
    total: int
    error_class_counts: dict[str, int]
    corrupt_output_count: int
    in_flight_count: int
    saturation_ratio: float
    stale_live_count: int
    healthy: bool


@dataclass(frozen=True)
class DispatchMonitorSnapshot:
    per_role: dict[str, RoleMonitorSnapshot]
    generated_at: str
    window_seconds: int

    def to_json_dict(self) -> dict[str, object]:
        return {
            "generated_at": self.generated_at,
            "window_seconds": self.window_seconds,
            "per_role": {
                role: {
                    "role": snap.role,
                    "total": snap.total,
                    "error_class_counts": snap.error_class_counts,
                    "corrupt_output_count": snap.corrupt_output_count,
                    "in_flight_count": snap.in_flight_count,
                    "saturation_ratio": snap.saturation_ratio,
                    "stale_live_count": snap.stale_live_count,
                    "healthy": snap.healthy,
                }
                for role, snap in self.per_role.items()
            },
        }


def classify_outcome(outcome: DispatchOutcome) -> str:
    """Classify one dispatch outcome into the canonical monitoring taxonomy.

    Order matters: the zero-output-no-verdict ``corrupt_output`` signature takes
    precedence over a bare timeout exit code, because a worker that produced
    nothing usable is the more actionable (and worse) condition.
    """
    msg = (outcome.error_message or "").lower()
    if not outcome.launched:
        if "no_active_target" in msg or "no active" in msg:
            return CLASS_NO_ACTIVE_TARGET
        if "concurrency_cap" in msg or "cap_reached" in msg or "per_role_concurrency" in msg:
            return CLASS_CAP_REACHED
        return CLASS_OTHER
    if outcome.exit_code is None:
        return CLASS_IN_FLIGHT
    if outcome.exit_code == 0:
        return CLASS_SUCCESS
    # Nonzero exit: a launched worker that failed.
    if outcome.stdout_bytes == 0 and not outcome.has_verdict:
        # Produced nothing usable -- the killed-mid-output signature.
        return CLASS_CORRUPT_OUTPUT
    if outcome.exit_code in WORKER_KILL_EXIT_CODES:
        return CLASS_WORKER_TIMEOUT
    if "provider" in msg:
        return CLASS_PROVIDER_FAILURE
    if "subprocess" in msg:
        return CLASS_SUBPROCESS_FAILED
    return CLASS_OTHER


def is_stale_live(outcome: DispatchOutcome, now: float, max_lifetime_seconds: int) -> bool:
    """A record believed in-flight (no exit) that is actually dead or over-lifetime."""
    if not outcome.launched or outcome.exit_code is not None:
        return False
    if not outcome.pid_alive:
        return True
    return (now - outcome.created_epoch) > max_lifetime_seconds


def compute_snapshot(
    outcomes: list[DispatchOutcome],
    caps: dict[str, int],
    now: float,
    *,
    window_seconds: int = DEFAULT_WINDOW_SECONDS,
    max_lifetime_seconds: int = DEFAULT_MAX_LIFETIME_SECONDS,
) -> DispatchMonitorSnapshot:
    """Pure: fold dispatch outcomes into a per-role monitoring snapshot."""
    cutoff = now - window_seconds
    per_role_outcomes: dict[str, list[DispatchOutcome]] = {}
    for outcome in outcomes:
        if outcome.created_epoch < cutoff:
            continue
        per_role_outcomes.setdefault(outcome.role, []).append(outcome)

    per_role: dict[str, RoleMonitorSnapshot] = {}
    for role, role_outcomes in per_role_outcomes.items():
        counts = {cls: 0 for cls in ERROR_CLASSES}
        corrupt = 0
        in_flight = 0
        stale = 0
        for outcome in role_outcomes:
            cls = classify_outcome(outcome)
            counts[cls] = counts.get(cls, 0) + 1
            if cls == CLASS_CORRUPT_OUTPUT:
                corrupt += 1
            if cls == CLASS_IN_FLIGHT:
                in_flight += 1
            if is_stale_live(outcome, now, max_lifetime_seconds):
                stale += 1
        # Genuinely-live workers exclude the stale (phantom) ones for saturation.
        live = max(in_flight - stale, 0)
        cap = caps.get(role, DEFAULT_PER_ROLE_CAP)
        saturation = (live / cap) if cap > 0 else 0.0
        healthy = saturation < 1.0 and corrupt == 0 and stale == 0
        per_role[role] = RoleMonitorSnapshot(
            role=role,
            total=len(role_outcomes),
            error_class_counts=counts,
            corrupt_output_count=corrupt,
            in_flight_count=in_flight,
            saturation_ratio=round(saturation, 4),
            stale_live_count=stale,
            healthy=healthy,
        )
    return DispatchMonitorSnapshot(
        per_role=per_role,
        generated_at=_iso(now),
        window_seconds=window_seconds,
    )


def _iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _epoch_from_dispatch_id(dispatch_id: str) -> float:
    """Best-effort parse of the leading ISO timestamp from a dispatch_id.

    Failure records use a ``dispatch_id`` like
    ``2026-06-25T23:30:17+00:00-no-active-target``; the leading ISO timestamp is
    the dispatch time. Returns ``0.0`` when no timestamp can be parsed.
    """
    match = re.match(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)?)", dispatch_id)
    if not match:
        return 0.0
    text = match.group(1).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return 0.0


def _role_from_text(text: str) -> str:
    for token in _ROLE_TOKENS:
        if token in text:
            return token
    return "unknown"


def _harness_from_stem(stem: str) -> str | None:
    # Dispatch ids look like 2026-06-25T21-36-26Z-loyal-opposition-F-3a7528.
    match = re.search(r"-(?:loyal-opposition|prime-builder)-([A-Za-z0-9]+)-[0-9a-f]+$", stem)
    return match.group(1) if match else None


def _read_int(path: Path | None) -> int | None:
    if path is None or not path.is_file():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _pid_alive(pid: int | None) -> bool:
    if not pid or pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes

        process_query = 0x1000  # PROCESS_QUERY_LIMITED_INFORMATION
        still_active = 259
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(process_query, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            if kernel32.GetExitCodeProcess(handle, ctypes.byref(code)):
                return code.value == still_active
            return True
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _gather_dispatch_runs(runs_dir: Path) -> list[DispatchOutcome]:
    """Parse dispatch-run sidecar sets into outcomes. Read-only, best-effort."""
    outcomes: list[DispatchOutcome] = []
    if not runs_dir.is_dir():
        return outcomes
    stems: dict[str, dict[str, Path]] = {}
    for path in runs_dir.iterdir():
        if not path.is_file():
            continue
        for suffix in (".exit_code", ".stdout.log", ".stderr.log", ".pid"):
            if path.name.endswith(suffix):
                stems.setdefault(path.name[: -len(suffix)], {})[suffix] = path
                break
    for stem, parts in stems.items():
        exit_code = _read_int(parts.get(".exit_code"))
        stdout_path = parts.get(".stdout.log")
        stdout_bytes = stdout_path.stat().st_size if stdout_path and stdout_path.is_file() else 0
        pid = _read_int(parts.get(".pid"))
        pid_alive = _pid_alive(pid) if exit_code is None else False
        newest = max((p.stat().st_mtime for p in parts.values()), default=0.0)
        outcomes.append(
            DispatchOutcome(
                role=_role_from_text(stem),
                harness_id=_harness_from_stem(stem),
                launched=True,
                exit_code=exit_code,
                has_verdict=stdout_bytes > 0,
                stdout_bytes=stdout_bytes,
                error_message="",
                created_epoch=newest,
                pid_alive=pid_alive,
            )
        )
    return outcomes


def _gather_failures(failures_path: Path) -> list[DispatchOutcome]:
    """Parse dispatch-failures.jsonl into outcomes (mostly not-launched records)."""
    outcomes: list[DispatchOutcome] = []
    if not failures_path.is_file():
        return outcomes
    try:
        lines = failures_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return outcomes
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        recipient = str(record.get("recipient") or "")
        message = str(record.get("error_message") or record.get("reason") or "")
        outcomes.append(
            DispatchOutcome(
                role=_role_from_text(recipient) if recipient else _role_from_text(message),
                harness_id=None,
                launched=bool(record.get("launched", False)),
                exit_code=None,
                has_verdict=False,
                stdout_bytes=0,
                error_message=message,
                created_epoch=_epoch_from_dispatch_id(str(record.get("dispatch_id") or "")),
                pid_alive=False,
            )
        )
    return outcomes


def gather_outcomes(project_root: Path, state_dirs: tuple[str, ...] = DEFAULT_STATE_DIRS) -> list[DispatchOutcome]:
    """Read-only gather of dispatch outcomes from both dispatch state-dir roots."""
    outcomes: list[DispatchOutcome] = []
    for rel in state_dirs:
        base = project_root / rel
        outcomes.extend(_gather_dispatch_runs(base / DISPATCH_RUNS_SUBDIR))
        outcomes.extend(_gather_failures(base / DISPATCH_FAILURES_FILENAME))
    return outcomes


def _resolve_project_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    env_root = os.environ.get("GTKB_PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path.cwd().resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only GT-KB dispatch monitoring snapshot (WI-4790 slice 1).")
    parser.add_argument("--project-root", type=Path, default=None)
    parser.add_argument("--window-seconds", type=int, default=DEFAULT_WINDOW_SECONDS)
    args = parser.parse_args(argv)
    root = _resolve_project_root(args.project_root)
    import time

    now = time.time()
    outcomes = gather_outcomes(root)
    snapshot = compute_snapshot(outcomes, caps={}, now=now, window_seconds=args.window_seconds)
    print(json.dumps(snapshot.to_json_dict(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
