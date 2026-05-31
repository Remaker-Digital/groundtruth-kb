# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Read-only bridge queue and automation status driver.

This module is intentionally side-effect free. It reads the live bridge index,
local hook configuration, and local dispatch state, then returns a deterministic
snapshot suitable for ``gt status`` and startup summaries.
"""

from __future__ import annotations

import json
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.bridge.detector import BridgeStatus, ParseResult, parse_index
from groundtruth_kb.bridge.notify import ActionablePending, compute_actionable_pending

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
NON_ACTIONABLE_STATUSES = {
    BridgeStatus.VERIFIED.value,
    BridgeStatus.WITHDRAWN.value,
    BridgeStatus.ADVISORY.value,
    BridgeStatus.DEFERRED.value,
}


@dataclass(frozen=True)
class BridgeQueueItem:
    """A currently actionable bridge item for one role."""

    document_name: str
    top_status: str
    top_file: str
    index_line_number: int
    dispatchable: bool
    classification: str

    @classmethod
    def from_pending(cls, item: ActionablePending) -> BridgeQueueItem:
        return cls(
            document_name=item.document_name,
            top_status=item.top_status,
            top_file=item.top_file,
            index_line_number=item.index_line_number,
            dispatchable=item.dispatchable,
            classification=item.classification,
        )

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "document_name": self.document_name,
            "top_status": self.top_status,
            "top_file": self.top_file,
            "index_line_number": self.index_line_number,
            "dispatchable": self.dispatchable,
            "classification": self.classification,
        }


@dataclass(frozen=True)
class BridgeQueueSnapshot:
    """Live bridge queue classification derived from bridge/INDEX.md."""

    index_path: Path
    threads: int
    status_counts: dict[str, int]
    prime_actionable: tuple[BridgeQueueItem, ...]
    loyal_opposition_actionable: tuple[BridgeQueueItem, ...]
    dispatchable_counts: dict[str, int]
    parse_warning_count: int
    parse_error_count: int
    parse_warnings: tuple[dict[str, Any], ...]
    parse_errors: tuple[dict[str, Any], ...]

    def to_json_dict(self, *, top_n: int | None = None) -> dict[str, Any]:
        prime = self.prime_actionable if top_n is None else self.prime_actionable[:top_n]
        loyal = self.loyal_opposition_actionable if top_n is None else self.loyal_opposition_actionable[:top_n]
        return {
            "index_path": str(self.index_path),
            "threads": self.threads,
            "status_counts": dict(self.status_counts),
            "prime_actionable_count": len(self.prime_actionable),
            "loyal_opposition_actionable_count": len(self.loyal_opposition_actionable),
            "dispatchable_counts": dict(self.dispatchable_counts),
            "prime_actionable": [item.to_json_dict() for item in prime],
            "loyal_opposition_actionable": [item.to_json_dict() for item in loyal],
            "parse_warning_count": self.parse_warning_count,
            "parse_error_count": self.parse_error_count,
            "parse_warnings": list(self.parse_warnings),
            "parse_errors": list(self.parse_errors),
        }


@dataclass(frozen=True)
class BridgeAutomationSnapshot:
    """Read-only local bridge automation health evidence."""

    trigger_script_exists: bool
    dispatch_state: dict[str, Any]
    active_session_locks: tuple[dict[str, Any], ...]
    hook_registrations: dict[str, dict[str, Any]]
    system_inventory: dict[str, Any]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "trigger_script_exists": self.trigger_script_exists,
            "dispatch_state": self.dispatch_state,
            "active_session_locks": list(self.active_session_locks),
            "hook_registrations": self.hook_registrations,
            "system_inventory": self.system_inventory,
        }


@dataclass(frozen=True)
class BridgeStatusSnapshot:
    """Combined queue and automation status snapshot."""

    queue: BridgeQueueSnapshot
    automation: BridgeAutomationSnapshot

    def to_json_dict(self, *, top_n: int | None = None) -> dict[str, Any]:
        return {
            "queue": self.queue.to_json_dict(top_n=top_n),
            "automation": self.automation.to_json_dict(),
        }


def collect_bridge_status(project_root: Path, *, top_n: int | None = 10) -> BridgeStatusSnapshot:
    """Collect bridge queue and automation status from local project files."""
    root = project_root.resolve()
    queue = _collect_queue_snapshot(root)
    automation = _collect_automation_snapshot(root)
    # top_n is accepted for API symmetry with to_json_dict callers. Collection
    # itself keeps the complete in-memory queue so callers can choose a view.
    _ = top_n
    return BridgeStatusSnapshot(queue=queue, automation=automation)


def _collect_queue_snapshot(root: Path) -> BridgeQueueSnapshot:
    index_path = root / "bridge" / "INDEX.md"
    parse_result = _parse_live_index(index_path, root)
    prime_pending, loyal_pending = compute_actionable_pending(parse_result, project_root=root)

    status_counts: dict[str, int] = {}
    dispatchable_counts = {
        "prime_dispatchable": 0,
        "prime_interactive": 0,
        "loyal_opposition_dispatchable": 0,
        "loyal_opposition_interactive": 0,
        "terminal_or_non_actionable": 0,
        "unknown_or_malformed": len(parse_result.errors),
    }

    for doc in parse_result.documents:
        top = doc.current_top
        if top is None:
            dispatchable_counts["unknown_or_malformed"] += 1
            continue
        status = top.status.value
        status_counts[status] = status_counts.get(status, 0) + 1
        if status in NON_ACTIONABLE_STATUSES:
            dispatchable_counts["terminal_or_non_actionable"] += 1

    prime_items = tuple(BridgeQueueItem.from_pending(item) for item in prime_pending)
    loyal_items = tuple(BridgeQueueItem.from_pending(item) for item in loyal_pending)
    for item in prime_items:
        key = "prime_dispatchable" if item.dispatchable else "prime_interactive"
        dispatchable_counts[key] += 1
    for item in loyal_items:
        key = "loyal_opposition_dispatchable" if item.dispatchable else "loyal_opposition_interactive"
        dispatchable_counts[key] += 1

    return BridgeQueueSnapshot(
        index_path=index_path,
        threads=len(parse_result.documents),
        status_counts=dict(sorted(status_counts.items())),
        prime_actionable=prime_items,
        loyal_opposition_actionable=loyal_items,
        dispatchable_counts=dispatchable_counts,
        parse_warning_count=len(parse_result.warnings),
        parse_error_count=len(parse_result.errors),
        parse_warnings=tuple(
            {
                "kind": warning.kind,
                "line_number": warning.line_number,
                "detail": warning.detail,
            }
            for warning in parse_result.warnings[:10]
        ),
        parse_errors=tuple(
            {
                "line_number": error.line_number,
                "content": error.content,
                "expected_state": error.expected_state,
            }
            for error in parse_result.errors[:10]
        ),
    )


def _parse_live_index(index_path: Path, root: Path) -> ParseResult:
    if not index_path.exists():
        return ParseResult(documents=())
    return parse_index(index_path.read_text(encoding="utf-8"), project_root=root)


def _collect_automation_snapshot(root: Path) -> BridgeAutomationSnapshot:
    state_dir = root / ".gtkb-state" / "bridge-poller"
    return BridgeAutomationSnapshot(
        trigger_script_exists=(root / "scripts" / "cross_harness_bridge_trigger.py").is_file(),
        dispatch_state=_read_dispatch_state(state_dir / "dispatch-state.json"),
        active_session_locks=_active_session_locks(state_dir),
        hook_registrations={
            ".claude/settings.json": _hook_registration_snapshot(root / ".claude" / "settings.json"),
            ".codex/hooks.json": _hook_registration_snapshot(root / ".codex" / "hooks.json"),
        },
        system_inventory=_system_inventory_snapshot(root / "config" / "agent-control" / "system-interface-map.toml"),
    )


def _read_dispatch_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "parseable": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"path": str(path), "exists": True, "parseable": False, "error": str(exc)}
    if not isinstance(payload, dict):
        return {"path": str(path), "exists": True, "parseable": False, "error": "payload is not an object"}
    recipients = payload.get("recipients", {})
    recipient_names = sorted(recipients.keys()) if isinstance(recipients, dict) else []
    return {
        "path": str(path),
        "exists": True,
        "parseable": True,
        "recipient_count": len(recipient_names),
        "recipients": recipient_names,
        "updated_at": payload.get("updated_at") or payload.get("written_at") or payload.get("last_updated"),
    }


def _active_session_locks(state_dir: Path) -> tuple[dict[str, Any], ...]:
    if not state_dir.exists():
        return ()
    now = time.time()
    locks: list[dict[str, Any]] = []
    for path in sorted(state_dir.glob("active-*-session*.lock")):
        try:
            stat = path.stat()
            age_seconds = round(now - stat.st_mtime, 3)
            raw = path.read_text(encoding="utf-8")
        except OSError as exc:
            locks.append({"path": str(path), "readable": False, "error": str(exc)})
            continue
        parsed: Any
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        locks.append(
            {
                "path": str(path),
                "readable": True,
                "age_seconds": age_seconds,
                "payload": parsed if isinstance(parsed, dict) else {},
            }
        )
    return tuple(locks)


def _hook_registration_snapshot(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "parseable": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"path": str(path), "exists": True, "parseable": False, "error": str(exc)}
    commands = _collect_command_strings(payload)
    return {
        "path": str(path),
        "exists": True,
        "parseable": True,
        "command_count": len(commands),
        "cross_harness_trigger_registered": any("cross_harness_bridge_trigger.py" in command for command in commands),
        "single_harness_automation_registered": any(
            "single_harness_bridge_automation.py" in command for command in commands
        ),
        "active_session_heartbeat_registered": any("active_session_heartbeat.py" in command for command in commands),
    }


def _collect_command_strings(value: Any) -> list[str]:
    commands: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "command" and isinstance(child, str):
                commands.append(child)
            else:
                commands.extend(_collect_command_strings(child))
    elif isinstance(value, list):
        for child in value:
            commands.extend(_collect_command_strings(child))
    return commands


def _system_inventory_snapshot(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "parseable": False}
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return {"path": str(path), "exists": True, "parseable": False, "error": str(exc)}

    systems = payload.get("systems", [])
    if not isinstance(systems, list):
        return {"path": str(path), "exists": True, "parseable": False, "error": "systems is not a list"}

    relevant: list[dict[str, Any]] = []
    for system in systems:
        if not isinstance(system, dict):
            continue
        haystack = " ".join(str(system.get(key, "")) for key in ("id", "canonical_name", "harness_caveats"))
        if any(token in haystack for token in ("bridge", "poller", "thread automation")):
            relevant.append(
                {
                    "id": system.get("id"),
                    "canonical_name": system.get("canonical_name"),
                    "lifecycle_state": system.get("lifecycle_state"),
                    "generated_or_authoritative": system.get("generated_or_authoritative"),
                }
            )

    retired = [row for row in relevant if row.get("lifecycle_state") == "retired"]
    external = [
        row
        for row in relevant
        if "thread automation" in str(row.get("canonical_name", "")).lower()
        or "external" in str(row.get("generated_or_authoritative", "")).lower()
    ]
    return {
        "path": str(path),
        "exists": True,
        "parseable": True,
        "relevant_system_count": len(relevant),
        "retired_systems": retired,
        "external_thread_automations": external,
    }
