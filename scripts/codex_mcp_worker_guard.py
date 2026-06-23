#!/usr/bin/env python3
"""Report and explicitly clean up stale Codex MCP worker processes."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

KNOWN_MCP_FAMILY_TOKENS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "playwright",
        (
            "@playwright/mcp",
            "@modelcontextprotocol/server-playwright",
            "mcp-server-playwright",
            "playwright-mcp",
        ),
    ),
    (
        "browser",
        (
            "@modelcontextprotocol/server-browser",
            "mcp-server-browser",
            "browser-mcp",
        ),
    ),
    (
        "context7",
        (
            "@upstash/context7-mcp",
            "context7-mcp",
        ),
    ),
)
CODEX_PARENT_TOKENS = ("codex", "openai codex")
DEFAULT_MIN_AGE_SECONDS = 300
COMMAND_PREVIEW_CHARS = 220


@dataclass(frozen=True)
class ProcessRecord:
    pid: int
    ppid: int | None
    name: str
    command_line: str
    created_at: datetime | None = None


@dataclass(frozen=True)
class WorkerFinding:
    pid: int
    ppid: int | None
    family: str
    state: str
    reason: str
    age_seconds: int | None
    command_preview: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "pid": self.pid,
            "ppid": self.ppid,
            "family": self.family,
            "state": self.state,
            "reason": self.reason,
            "age_seconds": self.age_seconds,
            "command_preview": self.command_preview,
        }


def utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed.astimezone(UTC) if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _coerce_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _normalize_command(command_line: str) -> str:
    return command_line.replace("\\", "/").lower()


def mcp_family_for(command_line: str) -> str | None:
    normalized = _normalize_command(command_line)
    for family, tokens in KNOWN_MCP_FAMILY_TOKENS:
        if any(token in normalized for token in tokens):
            return family
    if "context7" in normalized and "mcp" in normalized:
        return "context7"
    if "playwright" in normalized and "mcp" in normalized:
        return "playwright"
    return None


def is_node_process(record: ProcessRecord) -> bool:
    name = Path(record.name).name.lower()
    command = _normalize_command(record.command_line)
    return name in {"node", "node.exe"} or "/node " in command or command.endswith("/node")


def _process_text(record: ProcessRecord) -> str:
    return f"{record.name} {record.command_line}".lower()


def _ancestor_has_codex_parent(record: ProcessRecord, by_pid: dict[int, ProcessRecord]) -> bool:
    seen: set[int] = set()
    current = record
    while current.ppid and current.ppid > 0 and current.ppid not in seen:
        seen.add(current.ppid)
        parent = by_pid.get(current.ppid)
        if parent is None:
            return False
        parent_text = _process_text(parent)
        if any(token in parent_text for token in CODEX_PARENT_TOKENS):
            return True
        current = parent
    return False


def _detached_reason(record: ProcessRecord, by_pid: dict[int, ProcessRecord]) -> str | None:
    if not record.ppid or record.ppid <= 0:
        return "missing_parent_pid"
    parent = by_pid.get(record.ppid)
    if parent is None:
        return "parent_process_not_running"
    if record.created_at and parent.created_at and parent.created_at > record.created_at:
        return "parent_pid_reused_after_worker_start"
    return None


def _age_seconds(record: ProcessRecord, now: datetime) -> int | None:
    if record.created_at is None:
        return None
    return max(0, int((now - record.created_at).total_seconds()))


def _command_preview(command_line: str) -> str:
    compact = " ".join(command_line.split())
    if len(compact) <= COMMAND_PREVIEW_CHARS:
        return compact
    return compact[: COMMAND_PREVIEW_CHARS - 3] + "..."


def classify_processes(
    records: list[ProcessRecord],
    *,
    now: datetime | None = None,
    min_age_seconds: int = DEFAULT_MIN_AGE_SECONDS,
) -> dict[str, Any]:
    checked_at = now or utc_now()
    by_pid = {record.pid: record for record in records}
    stale: list[WorkerFinding] = []
    suspect: list[WorkerFinding] = []
    live: list[WorkerFinding] = []
    unrelated_node_count = 0

    for record in records:
        if not is_node_process(record):
            continue
        family = mcp_family_for(record.command_line)
        if family is None:
            unrelated_node_count += 1
            continue

        age = _age_seconds(record, checked_at)
        preview = _command_preview(record.command_line)
        detached = _detached_reason(record, by_pid)
        if _ancestor_has_codex_parent(record, by_pid):
            live.append(
                WorkerFinding(record.pid, record.ppid, family, "live", "codex_parent_chain_running", age, preview)
            )
            continue
        if detached and (age is None or age >= min_age_seconds):
            stale.append(WorkerFinding(record.pid, record.ppid, family, "stale", detached, age, preview))
            continue
        if detached:
            suspect.append(
                WorkerFinding(record.pid, record.ppid, family, "suspect", "detached_but_below_min_age", age, preview)
            )
            continue
        live.append(WorkerFinding(record.pid, record.ppid, family, "attached", "parent_process_running", age, preview))

    return {
        "checked_at": checked_at.isoformat().replace("+00:00", "Z"),
        "process_count": len(records),
        "known_mcp_worker_count": len(stale) + len(suspect) + len(live),
        "unrelated_node_count": unrelated_node_count,
        "stale_workers": [finding.as_dict() for finding in stale],
        "suspect_workers": [finding.as_dict() for finding in suspect],
        "live_workers": [finding.as_dict() for finding in live],
    }


def _record_from_windows_row(row: dict[str, Any]) -> ProcessRecord | None:
    pid = _coerce_int(row.get("ProcessId"))
    if pid is None:
        return None
    return ProcessRecord(
        pid=pid,
        ppid=_coerce_int(row.get("ParentProcessId")),
        name=str(row.get("Name") or ""),
        command_line=str(row.get("CommandLine") or ""),
        created_at=parse_datetime(row.get("CreationDateUtc")),
    )


def collect_windows_processes() -> list[ProcessRecord]:
    powershell = (
        "$rows = Get-CimInstance Win32_Process | "
        "Select-Object ProcessId,ParentProcessId,Name,CommandLine,"
        "@{Name='CreationDateUtc';Expression={if ($_.CreationDate) "
        "{$_.CreationDate.ToUniversalTime().ToString('o')} else {$null}}}; "
        "$rows | ConvertTo-Json -Compress -Depth 3"
    )
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", powershell],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    raw = json.loads(result.stdout or "[]")
    rows = raw if isinstance(raw, list) else [raw]
    return [record for row in rows if isinstance(row, dict) and (record := _record_from_windows_row(row))]


def collect_posix_processes() -> list[ProcessRecord]:
    result = subprocess.run(
        ["ps", "-eo", "pid=,ppid=,comm=,args="],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    records: list[ProcessRecord] = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 3)
        if len(parts) < 3:
            continue
        pid = _coerce_int(parts[0])
        ppid = _coerce_int(parts[1])
        if pid is None:
            continue
        name = parts[2]
        command = parts[3] if len(parts) > 3 else name
        records.append(ProcessRecord(pid=pid, ppid=ppid, name=name, command_line=command))
    return records


def collect_processes() -> list[ProcessRecord]:
    if os.name == "nt":
        return collect_windows_processes()
    return collect_posix_processes()


def terminate_process(pid: int) -> tuple[bool, str]:
    if os.name == "nt":
        result = subprocess.run(
            ["taskkill.exe", "/PID", str(pid), "/F"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0, (result.stdout + result.stderr).strip()
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as exc:
        return False, str(exc)
    return True, "SIGTERM sent"


def cleanup_stale_workers(
    report: dict[str, Any],
    *,
    dry_run: bool,
    terminator: Callable[[int], tuple[bool, str]] = terminate_process,
) -> dict[str, Any]:
    planned = report["stale_workers"]
    terminated: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    if not dry_run:
        for worker in planned:
            ok, detail = terminator(int(worker["pid"]))
            row = {"pid": worker["pid"], "family": worker["family"], "detail": detail}
            if ok:
                terminated.append(row)
            else:
                failed.append(row)
    return {
        "requested": True,
        "dry_run": dry_run,
        "planned": planned,
        "terminated": terminated,
        "failed": failed,
    }


def render_text(report: dict[str, Any]) -> str:
    stale_count = len(report["stale_workers"])
    suspect_count = len(report["suspect_workers"])
    live_count = len(report["live_workers"])
    if stale_count == 0 and suspect_count == 0:
        return f"Codex MCP worker guard: clean ({live_count} live/attached Codex MCP worker(s), no stale/detached workers)."
    lines = [
        "Codex MCP worker guard: attention needed",
        f"- stale/detached cleanup-eligible workers: {stale_count}",
        f"- suspect known MCP workers not eligible for cleanup: {suspect_count}",
        f"- live/attached Codex MCP workers: {live_count}",
    ]
    for worker in report["stale_workers"]:
        lines.append(
            f"- stale pid={worker['pid']} family={worker['family']} reason={worker['reason']} "
            f"age={worker['age_seconds']}s cmd={worker['command_preview']}"
        )
    for worker in report["suspect_workers"]:
        lines.append(
            f"- suspect pid={worker['pid']} family={worker['family']} reason={worker['reason']} "
            f"age={worker['age_seconds']}s"
        )
    return "\n".join(lines)


def run(
    argv: list[str] | None = None,
    *,
    collector: Callable[[], list[ProcessRecord]] = collect_processes,
    terminator: Callable[[int], tuple[bool, str]] = terminate_process,
    now: datetime | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true", help="Report current Codex MCP worker state")
    mode.add_argument("--cleanup", action="store_true", help="Clean up stale/detached workers")
    parser.add_argument("--dry-run", action="store_true", help="Plan cleanup without terminating processes")
    parser.add_argument("--yes", action="store_true", help="Confirm live cleanup termination")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument("--quiet-when-clean", action="store_true", help="Emit no output when report mode is clean")
    parser.add_argument("--min-age-seconds", type=int, default=DEFAULT_MIN_AGE_SECONDS)
    args = parser.parse_args(argv)

    cleanup_requested = args.cleanup
    if cleanup_requested and args.dry_run == args.yes:
        parser.error("--cleanup requires exactly one of --dry-run or --yes")
    if not cleanup_requested and (args.dry_run or args.yes):
        parser.error("--dry-run/--yes are only valid with --cleanup")

    records = collector()
    report = classify_processes(records, now=now, min_age_seconds=args.min_age_seconds)
    if cleanup_requested:
        report["cleanup"] = cleanup_stale_workers(report, dry_run=args.dry_run, terminator=terminator)
    else:
        report["cleanup"] = {"requested": False, "dry_run": None, "planned": [], "terminated": [], "failed": []}

    clean = not report["stale_workers"] and not report["suspect_workers"]
    if args.quiet_when_clean and clean and not cleanup_requested:
        return 0
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
        if cleanup_requested and args.dry_run:
            print(f"Cleanup dry-run: {len(report['cleanup']['planned'])} process(es) would be terminated.")
        elif cleanup_requested:
            print(
                "Cleanup result: "
                f"{len(report['cleanup']['terminated'])} terminated, {len(report['cleanup']['failed'])} failed."
            )
    return 1 if cleanup_requested and report["cleanup"]["failed"] else 0


def main() -> int:
    return run(sys.argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
