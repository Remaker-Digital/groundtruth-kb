"""Bridge substrate transaction component (Slice 1).

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`` and bridge thread
``gtkb-bridge-mode-config-transactions-slice-1``. Provides a deterministic
component for bridge dispatch substrate switch requests.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from groundtruth_kb.mode_switch.audit import write_bridge_substrate_record
from groundtruth_kb.mode_switch.derive import topology_from_role_map
from groundtruth_kb.mode_switch.transaction import TransactionValidationError, _atomic_write_json
from groundtruth_kb.mode_switch.validation import (
    validate_bridge_artifact,
    validate_bridge_substrate,
    validate_role_artifact,
    validate_session_state_artifact,
)


def _resolve_prime_harness_id(project_root: Path) -> str:
    """Resolve the active event-capable prime-builder harness ID from projection."""
    from groundtruth_kb.harness_projection import harness_registry_path

    def has_prime_role(record: dict[str, object]) -> bool:
        role = record.get("role", [])
        if isinstance(role, list):
            roles = {str(item).strip().lower() for item in role if str(item).strip()}
        elif isinstance(role, str) and role.strip():
            roles = {role.strip().lower()}
        else:
            return False
        if "acting-prime-builder" in roles:
            roles.discard("acting-prime-builder")
            roles.add("prime-builder")
        return "prime-builder" in roles

    registry_path = harness_registry_path(project_root)
    if registry_path.is_file():
        try:
            projection = json.loads(registry_path.read_text(encoding="utf-8"))
            harnesses = projection.get("harnesses", [])
            for rec in harnesses:
                if not isinstance(rec, dict):
                    continue
                if rec.get("status") == "active" and rec.get("event_driven_hooks") is True and has_prime_role(rec):
                    return str(rec.get("id", "C"))
        except Exception:
            pass
    return "C"


def apply_bridge_substrate_switch(
    project_root: Path,
    new_substrate: str,
    *,
    change_reason: str | None = None,
    applied_at: datetime | None = None,
) -> Path:
    """Validate and atomically apply a bridge-substrate switch.

    Per SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001:
    1. Validate role, bridge, and session-state artifacts.
    2. Read DB-backed harness registry projection to derive active topology.
    3. Validate substrate against topology and registrations.
    4. Write audit record (write_bridge_substrate_record) in .gtkb-state/mode-switches/
    5. Atomically write harness-state/bridge-substrate.json.
    """
    # 1. Standard artifact validators
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

    # 2. Derive topology
    from groundtruth_kb.harness_projection import harness_registry_path

    registry_path = harness_registry_path(project_root)
    projection = json.loads(registry_path.read_text(encoding="utf-8"))
    projection_harnesses = projection.get("harnesses", []) if isinstance(projection, dict) else []
    role_map = {
        "harnesses": {str(rec["id"]): rec for rec in projection_harnesses if isinstance(rec, dict) and rec.get("id")}
    }
    topology = topology_from_role_map(role_map)

    # 3. Substrate validation
    sub_result = validate_bridge_substrate(project_root, new_substrate, topology)
    if not sub_result.is_valid:
        raise TransactionValidationError(
            f"bridge substrate validation failed: {'; '.join(sub_result.errors)}",
            axis=sub_result.axis,
            errors=sub_result.errors,
        )

    # Get previous substrate if any
    prev_substrate: str | None = None
    sub_path = project_root / "harness-state" / "bridge-substrate.json"
    if sub_path.exists():
        try:
            prev_data = json.loads(sub_path.read_text(encoding="utf-8"))
            if isinstance(prev_data, dict):
                prev_substrate = prev_data.get("substrate")
        except Exception:
            pass

    harness_id = _resolve_prime_harness_id(project_root)
    when = applied_at if applied_at is not None else datetime.now(UTC)
    reason_str = change_reason or f"Bridge substrate switch to {new_substrate}"

    # 4. Write audit record (applied)
    audit_path = write_bridge_substrate_record(
        project_root,
        harness_id=harness_id,
        previous_substrate=prev_substrate,
        new_substrate=new_substrate,
        change_reason=reason_str,
        applied_at=when,
        deferred=False,
    )

    # 5. Atomic state write to harness-state/bridge-substrate.json
    payload = {
        "substrate": new_substrate,
        "applied_at": when.isoformat().replace("+00:00", "Z"),
        "applied_by": harness_id,
    }
    _atomic_write_json(sub_path, payload)

    return audit_path


def defer_bridge_substrate_switch(
    project_root: Path,
    new_substrate: str,
    *,
    change_reason: str | None = None,
    scheduled_at: datetime | None = None,
) -> Path:
    """Queue a bridge-substrate switch for next-session application."""
    directory = project_root / ".gtkb-state" / "mode-switches" / "pending"
    directory.mkdir(parents=True, exist_ok=True)
    when = scheduled_at if scheduled_at is not None else datetime.now(UTC)
    record_id = uuid.uuid4().hex[:8]
    filename = f"{when.strftime('%Y%m%dT%H%M%SZ')}-{record_id}.json"
    target = directory / filename
    harness_id = _resolve_prime_harness_id(project_root)
    reason_str = change_reason or f"Deferred bridge substrate switch to {new_substrate}"
    payload = {
        "schema_version": 1,
        "record_id": record_id,
        "axis": "bridge_substrate",
        "substrate": new_substrate,
        "change_reason": reason_str,
        "scheduled_at": when.isoformat().replace("+00:00", "Z"),
        "harness_id_or_name": harness_id,
    }
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target
