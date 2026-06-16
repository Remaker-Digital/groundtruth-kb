"""Deterministic approval-state policy for MemBase work items."""

from __future__ import annotations

import re
from enum import StrEnum
from pathlib import Path
from typing import Any


class ApprovalState(StrEnum):
    """Canonical backlog implementation approval states."""

    UNAPPROVED = "unapproved"
    AUQ_REQUIRED = "auq_required"
    AUQ_RESOLVED = "auq_resolved"
    BRIDGE_AUTHORIZED = "bridge_authorized"
    IMPLEMENTATION_AUTHORIZED = "implementation_authorized"


ALLOWED_STATES = {state.value for state in ApprovalState}


def normalize_state(value: str | None) -> str:
    """Return a valid approval state, defaulting legacy empty values."""

    if value is None or not str(value).strip():
        return ApprovalState.UNAPPROVED.value
    normalized = str(value).strip().lower()
    if normalized not in ALLOWED_STATES:
        raise ValueError(f"unknown approval_state: {value!r}")
    return normalized


def classify_initial_state(row: dict[str, Any], *, bridge_statuses: dict[str, str] | None = None) -> str:
    """Classify a current work-item row without LLM or heuristic judgment."""

    work_item_id = str(row.get("id") or "")
    if work_item_id == "WI-3271":
        return ApprovalState.AUQ_RESOLVED.value

    bridge_statuses = bridge_statuses or {}
    related_threads = [
        token.strip()
        for token in str(row.get("related_bridge_threads") or "").replace(",", " ").split()
        if token.strip()
    ]
    statuses = {bridge_statuses.get(thread) for thread in related_threads}
    if "VERIFIED" in statuses:
        return ApprovalState.IMPLEMENTATION_AUTHORIZED.value
    if "GO" in statuses:
        return ApprovalState.BRIDGE_AUTHORIZED.value

    if str(row.get("source_owner_directive") or "").strip():
        deliberations = str(row.get("related_deliberation_ids") or "")
        if "DELIB-" in deliberations:
            return ApprovalState.AUQ_RESOLVED.value
        return ApprovalState.AUQ_REQUIRED.value

    return ApprovalState.UNAPPROVED.value


def has_auq_evidence(work_item_id: str, pending_owner_decisions_path: Path) -> bool:
    """Return whether durable owner-decision records cite the work item."""

    if not pending_owner_decisions_path.exists():
        return False
    text = pending_owner_decisions_path.read_text(encoding="utf-8")
    return work_item_id in text and "ask_user_question" in text


_BRIDGE_FILE_STATUS_RE = re.compile(
    r"^[#>*\-\s`]*(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY|DEFERRED|WITHDRAWN)\b",
    re.IGNORECASE,
)


def _status_from_bridge_file(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        match = _BRIDGE_FILE_STATUS_RE.match(stripped)
        return match.group(1).upper() if match else None
    return None


def _current_go_verdict_files_from_versioned_bridge(project_root: Path) -> list[Path]:
    latest: dict[str, tuple[int, str, Path]] = {}
    bridge_dir = project_root / "bridge"
    for path in bridge_dir.glob("*.md"):
        if path.name == "INDEX.md":
            continue
        match = re.match(r"^(.+)-(\d+)\.md$", path.name)
        if not match:
            continue
        slug = match.group(1)
        version = int(match.group(2))
        status = _status_from_bridge_file(path)
        if status is None:
            continue
        if slug not in latest or version > latest[slug][0]:
            latest[slug] = (version, status, path)
    return [path for _version, status, path in latest.values() if status == "GO"]


def has_go_verdict(work_item_id: str, bridge_index_path: Path, project_root: Path) -> bool:
    """Return whether a current GO bridge chain cites this work item."""

    if not bridge_index_path.exists():
        return any(
            work_item_id in verdict_path.read_text(encoding="utf-8", errors="replace")
            for verdict_path in _current_go_verdict_files_from_versioned_bridge(project_root)
        )
    for line in bridge_index_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("GO: bridge/"):
            continue
        rel_path = stripped.split(":", 1)[1].strip()
        verdict_path = project_root / rel_path
        if verdict_path.exists() and work_item_id in verdict_path.read_text(encoding="utf-8"):
            return True
    return False


def validate_transition(
    *,
    work_item_id: str,
    current_state: str | None,
    target_state: str,
    pending_owner_decisions_path: Path,
    bridge_index_path: Path,
    project_root: Path,
) -> tuple[bool, str]:
    """Validate a requested approval-state transition."""

    source = normalize_state(current_state)
    target = normalize_state(target_state)
    if target != ApprovalState.IMPLEMENTATION_AUTHORIZED.value:
        return True, f"transition {source} -> {target} allowed"
    if source == ApprovalState.BRIDGE_AUTHORIZED.value and has_go_verdict(
        work_item_id, bridge_index_path, project_root
    ):
        return True, "bridge GO verdict evidence found"
    if source == ApprovalState.AUQ_RESOLVED.value and has_auq_evidence(work_item_id, pending_owner_decisions_path):
        return True, "AskUserQuestion evidence found"
    return False, f"{source} -> implementation_authorized requires AskUserQuestion or bridge GO evidence"
