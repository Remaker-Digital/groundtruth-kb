# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Bridge harness registry: static-record-only registration layer.

RETIRED (2026-05-09): The smart-poller runtime that was the primary consumer
of this registry has been archived to ``archive/smart-poller-2026-05-09/``.
The cross-harness event-driven trigger
(``scripts/cross_harness_bridge_trigger.py``) does not require static harness
registration; it reads recipient signatures from ``bridge/INDEX.md`` directly
on each fire. This module is retained for compatibility with adopters that
still consume the ``register`` CLI subcommand from a SessionStart hook.

Per ``bridge/gtkb-bridge-poller-p2-registry-005.md`` (REVISED-2, GO at -006)
and ``bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-004.md``
(REVISED-1 GO), this module owns the static registration record schema, the
atomic JSON write/read, and the ``register`` CLI subcommand invoked by
SessionStart hooks.

Out of scope (per design): heartbeat writing, PID-based liveness checks,
process-name allowlists, stale/live classification. ``recording_pid`` and
``recording_ppid`` are diagnostic-only — they are NOT claimed to be the
harness PID. Consumers must NOT treat registry records as live/stale
authoritative.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from groundtruth_kb.bridge.paths import get_state_dir, resolve_project_root

REGISTRY_SUBDIR: Final[str] = "registry"
REGISTRY_SCHEMA_VERSION: Final[int] = 1
HARNESS_KINDS: Final[frozenset[str]] = frozenset({"claude-code", "codex"})

# Path-traversal guard: reject these characters in harness_id.
_FORBIDDEN_HARNESS_ID_CHARS = re.compile(r"[/\\\x00]|\.\.")

_ACTIVE_ROLE_RE = re.compile(r"^active_role:\s*(?P<role>[\w-]+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class HarnessRegistration:
    """A single harness registration record.

    Schema version 1. ``recording_pid`` and ``recording_ppid`` are diagnostic
    fields capturing the PID of the registry-child process that wrote this
    record. Neither is claimed to be the harness PID.
    """

    schema_version: int
    harness_id: str
    harness_kind: str
    workspace_root: str
    active_role: str
    recorded_at: str
    recording_pid: int
    recording_ppid: int
    invoke_command_template: tuple[str, ...]
    invoke_template_notes: str
    role_record_source: str


def _now_iso() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def _slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s).strip("_")


def _make_harness_id(harness_kind: str, workspace_root: Path, pid: int) -> str:
    workspace_slug = _slugify(workspace_root.name or workspace_root.as_posix())
    iso_z = (
        dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H-%M-%SZ")  # path-safe ISO-8601
    )
    return f"{harness_kind}-{workspace_slug}-{iso_z}-pid{pid}"


def _validate_harness_id(harness_id: str) -> None:
    """Path-traversal guard: reject harness_id containing forbidden characters."""
    if _FORBIDDEN_HARNESS_ID_CHARS.search(harness_id):
        raise ValueError(f"harness_id contains forbidden characters (path-traversal guard): {harness_id!r}")


def _validate_harness_kind(harness_kind: str) -> None:
    if harness_kind not in HARNESS_KINDS:
        raise ValueError(f"harness_kind must be one of {sorted(HARNESS_KINDS)}; got {harness_kind!r}")


def _read_active_role(role_record_path: Path) -> str:
    if not role_record_path.is_file():
        return "unknown"
    text = role_record_path.read_text(encoding="utf-8")
    m = _ACTIVE_ROLE_RE.search(text)
    return m.group("role") if m else "unknown"


def _default_role_record_path(project_root: Path, harness_kind: str) -> Path:
    """Return the per-harness durable role record path."""
    if harness_kind == "claude-code":
        return project_root / "harness-state" / "claude" / "operating-role.md"
    if harness_kind == "codex":
        return project_root / "harness-state" / "codex" / "operating-role.md"
    return project_root / ".claude" / "rules" / "operating-role.md"


def _registry_dir() -> Path:
    base = get_state_dir()
    out = base / REGISTRY_SUBDIR
    out.mkdir(parents=True, exist_ok=True)
    return out


def _atomic_write(target: Path, content: str) -> None:
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(target)


def _default_invoke_command_template(harness_kind: str) -> tuple[str, ...]:
    if harness_kind == "claude-code":
        return (
            "claude",
            "-p",
            "{prompt}",
            "--add-dir",
            "{workspace_root}",
            "--output-format",
            "json",
        )
    if harness_kind == "codex":
        return (
            "codex",
            "exec",
            "{prompt}",
            "--cd",
            "{workspace_root}",
        )
    return ()


def register_harness(
    *,
    harness_kind: str,
    workspace_root: Path | None = None,
    role_record_source: Path | None = None,
) -> HarnessRegistration:
    """Write an atomic static registration record for the active harness.

    Args:
        harness_kind: one of ``claude-code`` or ``codex``.
        workspace_root: project root override; defaults to ``resolve_project_root()``.
        role_record_source: durable role record path; defaults per-harness-kind.

    Returns:
        The HarnessRegistration written.

    Raises:
        ValueError: invalid ``harness_kind`` or unsafe ``harness_id``.
    """
    _validate_harness_kind(harness_kind)
    project_root = workspace_root or resolve_project_root()
    role_record_path = role_record_source or _default_role_record_path(project_root, harness_kind)
    pid = os.getpid()
    ppid = os.getppid()
    harness_id = _make_harness_id(harness_kind, project_root, pid)
    _validate_harness_id(harness_id)

    record = HarnessRegistration(
        schema_version=REGISTRY_SCHEMA_VERSION,
        harness_id=harness_id,
        harness_kind=harness_kind,
        workspace_root=str(project_root),
        active_role=_read_active_role(role_record_path),
        recorded_at=_now_iso(),
        recording_pid=pid,
        recording_ppid=ppid,
        invoke_command_template=_default_invoke_command_template(harness_kind),
        invoke_template_notes=(
            "Defaults exclude --bare pending P2.5 spike outcome per bridge/gtkb-bridge-poller-001-smart-poller-007.md"
        ),
        role_record_source=str(role_record_path),
    )

    target = _registry_dir() / f"{harness_id}.json"
    _atomic_write(
        target,
        json.dumps(
            {
                **asdict(record),
                "invoke_command_template": list(record.invoke_command_template),
            },
            indent=2,
        ),
    )
    return record


def list_all_registrations(*, since_days: int | None = 7) -> list[HarnessRegistration]:
    """Return all registration records sorted by ``recorded_at`` descending.

    Does NOT classify records as live or stale. Consumers must handle that
    interpretation themselves.

    Args:
        since_days: optional age filter (default 7). When set, records older
            than this many days are omitted. Pass ``None`` to disable filtering.
    """
    out: list[HarnessRegistration] = []
    cutoff: dt.datetime | None = None
    if since_days is not None:
        cutoff = dt.datetime.now(dt.UTC) - dt.timedelta(days=since_days)

    try:
        registry_dir = _registry_dir()
    except Exception:  # intentional-catch: registry-dir resolution may raise on missing config; degrade to empty list
        return []

    for path in registry_dir.glob("*.json"):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            recorded_at = raw["recorded_at"]
            if cutoff is not None:
                rec_dt = dt.datetime.fromisoformat(recorded_at)
                if rec_dt.tzinfo is None:
                    rec_dt = rec_dt.replace(tzinfo=dt.UTC)
                if rec_dt < cutoff:
                    continue
            template = tuple(raw.get("invoke_command_template", ()))
            out.append(
                HarnessRegistration(
                    schema_version=int(raw["schema_version"]),
                    harness_id=str(raw["harness_id"]),
                    harness_kind=str(raw["harness_kind"]),
                    workspace_root=str(raw["workspace_root"]),
                    active_role=str(raw.get("active_role", "unknown")),
                    recorded_at=str(recorded_at),
                    recording_pid=int(raw.get("recording_pid", 0)),
                    recording_ppid=int(raw.get("recording_ppid", 0)),
                    invoke_command_template=template,
                    invoke_template_notes=str(raw.get("invoke_template_notes", "")),
                    role_record_source=str(raw.get("role_record_source", "")),
                )
            )
        except (KeyError, ValueError, json.JSONDecodeError):
            continue
    out.sort(key=lambda r: r.recorded_at, reverse=True)
    return out


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m groundtruth_kb.bridge.registry",
        description="Smart-poller harness static registry CLI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    register_p = sub.add_parser("register", help="Write a static registration record for this harness.")
    register_p.add_argument(
        "--harness-kind",
        required=True,
        choices=sorted(HARNESS_KINDS),
        help="Identifier of the harness this record describes.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``python -m groundtruth_kb.bridge.registry``."""
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    if args.command == "register":
        record = register_harness(harness_kind=args.harness_kind)
        sys.stdout.write(record.harness_id + "\n")
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
