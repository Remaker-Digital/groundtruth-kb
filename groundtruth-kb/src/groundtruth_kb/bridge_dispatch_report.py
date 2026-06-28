"""Read-only bridge dispatcher reporting helpers."""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections import Counter, deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge_dispatch_config import DISPATCH_ROLES, collect_bridge_dispatch_status

STATE_DIR_RELATIVE_PATH = Path(".gtkb-state") / "bridge-poller"
RUNS_RELATIVE_PATH = STATE_DIR_RELATIVE_PATH / "dispatch-runs"
RUN_TIMESTAMP_RE = re.compile(r"^(?P<stamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)")
PID_CREATE_TIME_SUFFIX = ".create_time_epoch"
PID_CREATE_TIME_MATCH_TOLERANCE_SECONDS = 0.01


def build_bridge_dispatch_report(
    project_root: Path,
    *,
    max_records: int = 50,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Build a bounded, read-only dispatcher operations report."""
    root = project_root.resolve()
    status = collect_bridge_dispatch_status(root)
    status_payload = status.to_json_dict()
    now_utc = now or datetime.now(UTC)

    state, state_warnings = _read_json(root / STATE_DIR_RELATIVE_PATH / "dispatch-state.json")
    recipients = state.get("recipients") if isinstance(state.get("recipients"), dict) else {}
    if not isinstance(recipients, dict):
        recipients = {}

    dispatch_failures, failure_warnings = _read_jsonl_glob(root, "dispatch-failures.jsonl*", max_records)
    dispatch_suppressions, suppression_warnings = _read_jsonl_glob(root, "dispatch-suppressions.jsonl*", max_records)
    trigger_diagnostics, diagnostic_warnings = _read_jsonl_glob(root, "trigger-diagnostic.jsonl*", max_records)
    starvation_telemetry, starvation_warnings = _read_json(root / STATE_DIR_RELATIVE_PATH / "starvation-telemetry.json")
    recent_runs = _collect_recent_runs(root, max_records=max_records, now=now_utc)

    selected_by_role = status_payload["selected_by_role"]
    effective_ceiling = _effective_per_cycle_ceiling(selected_by_role)
    live_runs = [run for run in recent_runs if run["state"] == "live"]
    run_counts = Counter(str(run["state"]) for run in recent_runs)
    success_count = run_counts.get("exit_0", 0)
    completed_count = success_count + run_counts.get("exit_nonzero", 0)
    success_rate = None if completed_count == 0 else success_count / completed_count

    failure_taxonomy = _failure_taxonomy(recipients, dispatch_failures, dispatch_suppressions)
    circuit_breakers = [
        {
            "recipient": key,
            "failure_class": row.get("failure_class"),
            "last_result": row.get("last_result"),
            "pending_count": row.get("pending_count"),
        }
        for key, row in sorted(recipients.items())
        if isinstance(row, dict) and row.get("circuit_breaker_tripped") is True
    ]

    warnings = state_warnings + failure_warnings + suppression_warnings + diagnostic_warnings + starvation_warnings
    runtime_failure_count = sum(1 for finding in status.health_findings if "dispatch runtime failure" in finding)
    runtime_warning_count = sum(1 for finding in status.health_findings if "dispatch runtime warning" in finding)

    return {
        "summary": {
            "health_status": status.health_status,
            "health_finding_count": len(status.health_findings),
            "runtime_failure_count": runtime_failure_count,
            "runtime_warning_count": runtime_warning_count,
            "selected_candidate_count": {role: len(selected_by_role.get(role, [])) for role in DISPATCH_ROLES},
            "effective_per_cycle_ceiling": effective_ceiling,
            "live_worker_count": len(live_runs),
            "recent_run_count": len(recent_runs),
            "warning_count": len(warnings),
        },
        "configuration": status_payload["config"],
        "topology": {
            "harnesses": status_payload["harnesses"],
            "selected_by_role": selected_by_role,
            "effective_per_cycle_ceiling": effective_ceiling,
        },
        "performance": {
            "recent_run_counts": dict(sorted(run_counts.items())),
            "success_rate": success_rate,
            "per_recipient": _recipient_performance(recipients),
        },
        "reliability": {
            "health_status": status.health_status,
            "findings": list(status.health_findings),
            "consistency_findings": list(status.consistency_findings),
            "runtime_classifications": list(status.runtime_classifications),
            "failure_taxonomy": failure_taxonomy,
            "circuit_breakers": circuit_breakers,
            "dispatch_failures_tail": dispatch_failures,
            "dispatch_suppressions_tail": dispatch_suppressions,
            "warnings": warnings,
        },
        "live_state": {
            "updated_at": state.get("updated_at"),
            "recipients": recipients,
            "live_worker_count": len(live_runs),
            "live_workers": live_runs,
            "starvation_telemetry": starvation_telemetry,
        },
        "history": {
            "recent_runs": recent_runs,
            "trigger_diagnostics_tail": trigger_diagnostics,
        },
    }


def format_bridge_dispatch_report(report: dict[str, Any]) -> str:
    """Render a compact human-readable dispatch operations report."""
    summary = report["summary"]
    lines = [
        f"Bridge dispatch report: {summary['health_status']}",
        f"Effective per-cycle ceiling: {summary['effective_per_cycle_ceiling']}",
        f"Live workers: {summary['live_worker_count']}",
        "",
        "Selected candidates:",
    ]
    for role in DISPATCH_ROLES:
        rows = report["topology"]["selected_by_role"].get(role, [])
        ids = [str(row.get("id")) for row in rows]
        lines.append(f"- {role}: {', '.join(ids) if ids else '(none)'}")
    lines.append("")
    lines.append("Recent runs:")
    for state, count in report["performance"]["recent_run_counts"].items():
        lines.append(f"- {state}: {count}")
    if report["reliability"]["findings"]:
        lines.append("")
        lines.append("Reliability findings:")
        for finding in report["reliability"]["findings"]:
            lines.append(f"- {finding}")
    return "\n".join(lines)


def _read_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.exists():
        return {}, []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"unable to read {path}: {exc}"]
    if not isinstance(payload, dict):
        return {}, [f"{path} is not a JSON object"]
    return payload, []


def _read_jsonl_glob(root: Path, pattern: str, max_records: int) -> tuple[list[dict[str, Any]], list[str]]:
    state_dir = root / STATE_DIR_RELATIVE_PATH
    paths = sorted(state_dir.glob(pattern), key=lambda path: path.stat().st_mtime if path.exists() else 0)
    records: deque[dict[str, Any]] = deque(maxlen=max_records)
    warnings: list[str] = []
    for path in paths:
        file_records, file_warnings = _read_jsonl_tail(path, max_records)
        warnings.extend(file_warnings)
        records.extend(file_records)
    return list(records), warnings


def _read_jsonl_tail(path: Path, max_records: int) -> tuple[list[dict[str, Any]], list[str]]:
    records: deque[dict[str, Any]] = deque(maxlen=max_records)
    warnings: list[str] = []
    if not path.exists():
        return [], []
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:
                    warnings.append(f"unable to parse {path}:{line_number}: {exc}")
                    continue
                if isinstance(payload, dict):
                    records.append(payload)
    except OSError as exc:
        warnings.append(f"unable to read {path}: {exc}")
    return list(records), warnings


def _collect_recent_runs(root: Path, *, max_records: int, now: datetime) -> list[dict[str, Any]]:
    runs_dir = root / RUNS_RELATIVE_PATH
    if not runs_dir.exists():
        return []
    runs: dict[str, dict[str, Any]] = {}
    for path in runs_dir.iterdir():
        dispatch_id = _dispatch_id_from_run_file(path)
        if dispatch_id is None:
            continue
        row = runs.setdefault(dispatch_id, {"dispatch_id": dispatch_id})
        row["last_modified_at"] = datetime.fromtimestamp(path.stat().st_mtime, UTC).isoformat()
        if path.name.endswith(".stdout.log"):
            row["stdout_bytes"] = path.stat().st_size
        elif path.name.endswith(".stderr.log"):
            row["stderr_bytes"] = path.stat().st_size
        elif path.name.endswith(".exit_code"):
            row["exit_code"] = _read_exit_code(path)
        elif path.name.endswith(".pid"):
            row["pid"] = _read_int(path)
        elif path.name.endswith(PID_CREATE_TIME_SUFFIX):
            row["pid_create_time_epoch"] = _read_float(path)
    for row in runs.values():
        started = _parse_dispatch_started_at(row["dispatch_id"])
        row["started_at"] = started.isoformat() if started is not None else None
        if "exit_code" not in row and _recent_run_live(runs_dir, row):
            row["state"] = "live"
            row["age_seconds"] = None if started is None else max(0.0, (now - started).total_seconds())
        elif "exit_code" not in row:
            row["state"] = "stale"
            row["age_seconds"] = None if started is None else max(0.0, (now - started).total_seconds())
        elif row["exit_code"] == 0:
            row["state"] = "exit_0"
        elif row["exit_code"] is None:
            row["state"] = "unknown"
        else:
            row["state"] = "exit_nonzero"
    return sorted(
        runs.values(),
        key=lambda row: str(row.get("started_at") or row.get("last_modified_at") or ""),
        reverse=True,
    )[:max_records]


def _dispatch_id_from_run_file(path: Path) -> str | None:
    for suffix in (".stdout.log", ".stderr.log", ".exit_code", ".pid", PID_CREATE_TIME_SUFFIX):
        if path.name.endswith(suffix):
            return path.name[: -len(suffix)]
    return None


def _read_int(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _read_float(path: Path) -> float | None:
    try:
        return float(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _read_exit_code(path: Path) -> int | None:
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def _pid_alive(pid: int) -> bool:
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return False
    if pid_int <= 0:
        return False
    try:
        import psutil  # noqa: PLC0415

        return bool(psutil.pid_exists(pid_int))
    except Exception:  # noqa: BLE001
        pass
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid_int}", "/NH"],
                capture_output=True,
                text=True,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return False
        return str(pid_int) in result.stdout
    try:
        os.kill(pid_int, 0)
    except OSError:
        return False
    return True


def _pid_create_time_epoch(pid: int) -> float | None:
    try:
        pid_int = int(pid)
    except (TypeError, ValueError):
        return None
    if pid_int <= 0:
        return None
    try:
        import psutil  # noqa: PLC0415

        return float(psutil.Process(pid_int).create_time())
    except Exception:  # noqa: BLE001
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


def _recent_run_live(runs_dir: Path, row: dict[str, Any]) -> bool:
    pid = row.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool):
        return False
    if not _pid_alive(pid):
        return False
    expected = row.get("pid_create_time_epoch")
    if expected is None:
        expected = _read_float(runs_dir / f"{row['dispatch_id']}{PID_CREATE_TIME_SUFFIX}")
    return _pid_create_time_matches(pid, expected)


def _parse_dispatch_started_at(dispatch_id: str) -> datetime | None:
    match = RUN_TIMESTAMP_RE.match(dispatch_id)
    if match is None:
        return None
    try:
        return datetime.strptime(match.group("stamp"), "%Y-%m-%dT%H-%M-%SZ").replace(tzinfo=UTC)
    except ValueError:
        return None


def _effective_per_cycle_ceiling(selected_by_role: dict[str, list[dict[str, Any]]]) -> dict[str, int | None]:
    ceilings: dict[str, int | None] = {}
    for role in DISPATCH_ROLES:
        rows = selected_by_role.get(role, [])
        values = [row.get("dispatch_max_items") for row in rows if isinstance(row.get("dispatch_max_items"), int)]
        ceilings[role] = sum(values) if values else None
    return ceilings


def _recipient_performance(recipients: dict[str, Any]) -> dict[str, dict[str, Any]]:
    performance: dict[str, dict[str, Any]] = {}
    for key, row in sorted(recipients.items()):
        if not isinstance(row, dict):
            continue
        performance[key] = {
            "pending_count": row.get("pending_count"),
            "raw_pending_count": row.get("raw_pending_count"),
            "selected_count": row.get("selected_count"),
            "last_result": row.get("last_result"),
            "updated_at": row.get("updated_at"),
        }
    return performance


def _failure_taxonomy(
    recipients: dict[str, Any],
    dispatch_failures: list[dict[str, Any]],
    dispatch_suppressions: list[dict[str, Any]],
) -> dict[str, dict[str, int]]:
    taxonomy: dict[str, Counter[str]] = {
        "last_result": Counter(),
        "failure_class": Counter(),
        "last_launch.reason": Counter(),
        "last_launch.exit_failure_reason": Counter(),
        "jsonl.reason": Counter(),
        "suppression.reason": Counter(),
    }
    for row in recipients.values():
        if not isinstance(row, dict):
            continue
        _count_value(taxonomy["last_result"], row.get("last_result"))
        _count_value(taxonomy["failure_class"], row.get("failure_class"))
        launch = row.get("last_launch") if isinstance(row.get("last_launch"), dict) else {}
        _count_value(taxonomy["last_launch.reason"], launch.get("reason"))
        _count_value(taxonomy["last_launch.exit_failure_reason"], launch.get("exit_failure_reason"))
    for row in dispatch_failures:
        _count_value(taxonomy["jsonl.reason"], row.get("reason") or row.get("failure_reason") or row.get("last_result"))
        _count_value(taxonomy["failure_class"], row.get("failure_class"))
    for row in dispatch_suppressions:
        _count_value(taxonomy["suppression.reason"], row.get("reason") or row.get("suppression_reason"))
    return {field: dict(sorted(counter.items())) for field, counter in taxonomy.items()}


def _count_value(counter: Counter[str], value: Any) -> None:
    if value is None:
        return
    text = str(value).strip()
    if text:
        counter[text] += 1
