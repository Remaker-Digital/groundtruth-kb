"""Legacy approval-state compatibility for MemBase work items.

The ``approval_state`` column is historical metadata only. Project-level
authorization, a live bridge ``GO``, and an implementation-start packet are the
only implementation authority chain.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any


class ApprovalState(StrEnum):
    """Legacy labels retained so historical rows can still deserialize."""

    UNAPPROVED = "unapproved"
    AUQ_REQUIRED = "auq_required"
    AUQ_RESOLVED = "auq_resolved"
    BRIDGE_AUTHORIZED = "bridge_authorized"
    IMPLEMENTATION_AUTHORIZED = "implementation_authorized"


ALLOWED_STATES = {state.value for state in ApprovalState}


def normalize_state(value: str | None) -> str:
    """Return a normalized legacy approval-state label."""

    if value is None or not str(value).strip():
        return ApprovalState.UNAPPROVED.value
    normalized = str(value).strip().lower()
    return normalized


def classify_initial_state(row: dict[str, Any], *, bridge_statuses: dict[str, str] | None = None) -> str:
    """Return the stored legacy label without deriving implementation authority."""

    _ = bridge_statuses
    return normalize_state(str(row.get("approval_state") or ""))


def validate_transition(
    *,
    work_item_id: str,
    current_state: str | None,
    target_state: str,
    pending_owner_decisions_path: Path,
    bridge_state_path: Path,
    project_root: Path,
) -> tuple[bool, str]:
    """Compatibility shim for the retired approval-state transition gate."""

    source = normalize_state(current_state)
    target = normalize_state(target_state)
    _ = work_item_id, pending_owner_decisions_path, bridge_state_path, project_root
    return (
        True,
        f"approval_state is legacy metadata only; transition {source} -> {target} "
        "does not grant or block implementation authority",
    )
