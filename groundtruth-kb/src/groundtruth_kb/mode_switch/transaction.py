"""Operating-mode transaction component: ``apply_role_switch``.

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001``. Validators run FIRST
(role artifact, bridge artifact, session-state artifact); on any validation
failure ``TransactionValidationError`` is raised and no state mutation
occurs. On all-pass, the role-map is updated atomically, the derived
topology is written to the session-state artifact, and an audit-trail
record is emitted.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.mode_switch.audit import write_transaction_record
from groundtruth_kb.mode_switch.derive import topology_from_role_map
from groundtruth_kb.mode_switch.validation import (
    validate_bridge_artifact,
    validate_role_artifact,
    validate_session_state_artifact,
)

VALID_ROLES_FOR_WRITE = frozenset({"prime-builder", "loyal-opposition"})


class TransactionValidationError(RuntimeError):
    """Raised when one or more pre-write validators fail."""

    def __init__(self, message: str, axis: str, errors: tuple[str, ...] = ()) -> None:
        super().__init__(message)
        self.axis = axis
        self.errors = errors


@dataclass(frozen=True)
class TransactionResult:
    """Result of a successful role-switch transaction."""

    harness_id: str
    previous_role_set: tuple[str, ...]
    new_role_set: tuple[str, ...]
    derived_topology: str
    audit_record_path: Path
    applied_at: datetime


def _resolve_harness_id(
    role_map: dict[str, Any], harness_id_or_name: str
) -> str:
    """Resolve a harness id-or-name to its harness id in the role map.

    Direct id match takes priority; falls back to name match within harness
    records.
    """
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict):
        raise TransactionValidationError(
            "role map has no 'harnesses' dict", axis="role"
        )
    if harness_id_or_name in harnesses:
        return harness_id_or_name
    for hid, record in harnesses.items():
        if isinstance(record, dict) and record.get("name") == harness_id_or_name:
            return hid
    raise TransactionValidationError(
        f"unknown harness id-or-name: {harness_id_or_name!r}", axis="role"
    )


def _atomic_write_json(path: Path, payload: Any) -> None:
    """Write JSON atomically via tempfile + rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def apply_role_switch(
    project_root: Path,
    harness_id_or_name: str,
    role: str,
    *,
    change_reason: str,
    applied_at: datetime | None = None,
) -> TransactionResult:
    """Apply an immediate role-switch transaction.

    Order of operations (fail-closed before any state mutation):

    1. Validate role artifact (``harness-state/role-assignments.json``).
    2. Validate bridge artifact (``bridge/INDEX.md``).
    3. Validate session-state artifact (``.claude/session/work-subject.json``).
    4. Validate role token against ``VALID_ROLES_FOR_WRITE`` (SET-rejects
       ``acting-prime-builder``).
    5. Resolve harness id-or-name to harness id.
    6. Read role map; compute new role set (singleton list for multi-harness
       case; multi-element only via separate single-harness path).
    7. Write audit-trail record FIRST (per failure-leaves-no-state-mutation
       invariant).
    8. Atomically write role-assignments.json with derived topology.
    9. Atomically write work-subject.json with derived topology if file
       exists.

    Raises ``TransactionValidationError`` on any validation failure;
    no state mutation occurs in that case.
    """
    # Step 1-3: Validators (fail-closed on any axis).
    role_result = validate_role_artifact(project_root)
    bridge_result = validate_bridge_artifact(project_root)
    session_result = validate_session_state_artifact(project_root)
    for result in (role_result, bridge_result, session_result):
        if not result.is_valid:
            raise TransactionValidationError(
                f"{result.axis} artifact validation failed: {'; '.join(result.errors)}",
                axis=result.axis,
                errors=result.errors,
            )

    # Step 4: Role-token validation.
    if role not in VALID_ROLES_FOR_WRITE:
        raise TransactionValidationError(
            f"requested role {role!r} not in {sorted(VALID_ROLES_FOR_WRITE)}; "
            f"acting-prime-builder is SET-rejected per GOV-ACTING-PRIME-BUILDER-001",
            axis="role",
        )

    # Step 5-6: Resolve harness, compute new role set.
    role_map_path = project_root / "harness-state" / "role-assignments.json"
    role_map = json.loads(role_map_path.read_text(encoding="utf-8"))
    harness_id = _resolve_harness_id(role_map, harness_id_or_name)
    harnesses = role_map["harnesses"]
    record = harnesses[harness_id]
    previous_role_value = record.get("role", [])
    if isinstance(previous_role_value, list):
        previous_role_set: tuple[str, ...] = tuple(previous_role_value)
    elif isinstance(previous_role_value, str):
        previous_role_set = (previous_role_value,) if previous_role_value else ()
    else:
        previous_role_set = ()

    # Multi-harness assignment: this harness gets the singleton role; all
    # OTHER harnesses are demoted to the opposite singleton role. The
    # single-harness multi-element case is handled by a separate code path
    # not in scope for this slice.
    new_role_set: tuple[str, ...] = (role,)
    opposite = "loyal-opposition" if role == "prime-builder" else "prime-builder"
    record["role"] = list(new_role_set)
    for other_id, other_record in harnesses.items():
        if other_id == harness_id or not isinstance(other_record, dict):
            continue
        other_role = other_record.get("role")
        other_set = []
        if isinstance(other_role, list):
            other_set = list(other_role)
        elif isinstance(other_role, str) and other_role.strip():
            other_set = [other_role.strip()]
        if role in other_set:
            other_record["role"] = [opposite]

    # Derive new topology.
    derived_topology = topology_from_role_map(role_map)

    # Step 7: Audit-trail record FIRST.
    when = applied_at if applied_at is not None else datetime.now(UTC)
    audit_path = write_transaction_record(
        project_root,
        harness_id=harness_id,
        requested_role=role,
        previous_role_set=list(previous_role_set),
        new_role_set=list(new_role_set),
        derived_topology=derived_topology,
        change_reason=change_reason,
        applied_at=when,
        deferred=False,
    )

    # Step 8: Atomic write role-assignments.json.
    _atomic_write_json(role_map_path, role_map)

    # Step 9: Atomic write work-subject.json with derived topology (if it
    # exists).
    session_path = project_root / ".claude" / "session" / "work-subject.json"
    if session_path.exists():
        session_data = json.loads(session_path.read_text(encoding="utf-8"))
        if isinstance(session_data, dict):
            session_data["topology_mode"] = derived_topology
            _atomic_write_json(session_path, session_data)

    return TransactionResult(
        harness_id=harness_id,
        previous_role_set=previous_role_set,
        new_role_set=new_role_set,
        derived_topology=derived_topology,
        audit_record_path=audit_path,
        applied_at=when,
    )
