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

import contextlib
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
ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
STATUS_ACTIVE = "active"


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


def _resolve_harness_id(role_map: dict[str, Any], harness_id_or_name: str) -> str:
    """Resolve a harness id-or-name to its harness id in the role map.

    Direct id match takes priority; falls back to name match within harness
    records.
    """
    harnesses = role_map.get("harnesses", {})
    if not isinstance(harnesses, dict):
        raise TransactionValidationError("role map has no 'harnesses' dict", axis="role")
    if harness_id_or_name in harnesses:
        return harness_id_or_name
    for hid, record in harnesses.items():
        if isinstance(record, dict) and record.get("name") == harness_id_or_name:
            return hid
        if isinstance(record, dict) and record.get("harness_name") == harness_id_or_name:
            return hid
    raise TransactionValidationError(f"unknown harness id-or-name: {harness_id_or_name!r}", axis="role")


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
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def _decode_harness_json_field(raw: Any) -> Any:
    """Decode a harnesses-table JSON-text column value (role / invocation_surfaces).

    ``KnowledgeDB.get_harness`` returns these columns as raw JSON text (or
    ``None``). Decoding is required before the value is round-tripped back
    through ``insert_harness``, which JSON-encodes its inputs — passing the raw
    text straight through would double-encode it."""
    if raw is None or raw == "":
        return None
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None
    return raw


def _role_tokens(raw: Any) -> list[str]:
    if isinstance(raw, str):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    return sorted({str(token).strip() for token in raw if str(token).strip() in VALID_ROLES_FOR_WRITE})


def _sort_harness_ids(harnesses: dict[str, Any]) -> list[str]:
    def key(harness_id: str) -> tuple[int, int, str]:
        record = harnesses.get(harness_id)
        precedence = record.get("reviewer_precedence") if isinstance(record, dict) else None
        if isinstance(precedence, int):
            return (0, precedence, harness_id)
        return (1, 0, harness_id)

    return sorted(harnesses, key=key)


def _active_ids(harnesses: dict[str, Any]) -> list[str]:
    return [
        harness_id
        for harness_id in _sort_harness_ids(harnesses)
        if isinstance(harnesses.get(harness_id), dict) and harnesses[harness_id].get("status") == STATUS_ACTIVE
    ]


def _existing_holder(
    harnesses: dict[str, Any],
    active_ids: list[str],
    role: str,
    *,
    exclude_id: str | None = None,
) -> str | None:
    for harness_id in active_ids:
        if harness_id == exclude_id:
            continue
        record = harnesses.get(harness_id)
        if isinstance(record, dict) and role in _role_tokens(record.get("role")):
            return harness_id
    return None


def _first_active(active_ids: list[str], *, exclude_id: str | None = None) -> str | None:
    for harness_id in active_ids:
        if harness_id != exclude_id:
            return harness_id
    return None


def _apply_active_role_assignment(
    harnesses: dict[str, Any],
    *,
    target_id: str,
    requested_role: str,
) -> tuple[str, ...]:
    """Mutate ``harnesses`` to the clarified active-role invariant."""
    record = harnesses.get(target_id)
    if not isinstance(record, dict):
        raise TransactionValidationError(f"unknown harness id: {target_id!r}", axis="role")
    if record.get("status") != STATUS_ACTIVE:
        raise TransactionValidationError(
            f"harness {target_id!r} has status {record.get('status')!r}; "
            "role assignment requires a registered and active harness",
            axis="role",
        )
    active_ids = _active_ids(harnesses)
    if not active_ids:
        raise TransactionValidationError("role assignment requires at least one active harness", axis="role")

    if len(active_ids) == 1:
        prime_id = lo_id = active_ids[0]
    elif requested_role == ROLE_PRIME_BUILDER:
        prime_id = target_id
        lo_id = _existing_holder(harnesses, active_ids, ROLE_LOYAL_OPPOSITION, exclude_id=prime_id)
        if lo_id is None:
            lo_id = _first_active(active_ids, exclude_id=prime_id)
    else:
        lo_id = target_id
        prime_id = _existing_holder(harnesses, active_ids, ROLE_PRIME_BUILDER, exclude_id=lo_id)
        if prime_id is None:
            prime_id = _first_active(active_ids, exclude_id=lo_id)

    if not prime_id or not lo_id:
        raise TransactionValidationError("could not derive PB/LO assignment from active harness set", axis="role")
    if len(active_ids) > 1 and prime_id == lo_id:
        raise TransactionValidationError(
            "PB and LO must be assigned to different active harnesses when more than one active harness exists",
            axis="role",
        )

    for harness_id, item in harnesses.items():
        if not isinstance(item, dict):
            continue
        if item.get("status") != STATUS_ACTIVE:
            continue
        roles: list[str] = []
        if harness_id == lo_id:
            roles.append(ROLE_LOYAL_OPPOSITION)
        if harness_id == prime_id:
            roles.append(ROLE_PRIME_BUILDER)
        if not roles:
            item["status"] = "suspended"
        item["role"] = roles
    return tuple(harnesses[target_id].get("role") or [])


def _mirror_role_map_to_registry(
    project_root: Path,
    role_map: dict[str, Any],
    change_reason: str,
) -> None:
    """Write the post-switch role map to the DB ``harnesses`` registry table
    and regenerate the hot-path projection.

    WI-3342 IP-5: this is now the AUTHORITATIVE role write for the role-switch
    transaction — the transitional ``role-assignments.json`` write was removed,
    so the DB-backed registry and its projection are the sole authoritative
    role surface.

    For each harness in the role map whose role set differs from its current
    DB row, an append-only ``insert_harness`` version is written carrying the
    new role and every other field forwarded from the current row. A harness
    with no current DB row is skipped — the registry seed owns first-version
    creation. After the inserts the projection is regenerated.

    A missing ``groundtruth.db`` (e.g. a DB-less test fixture) is a graceful
    no-op. Any other registry/DB failure is raised, failing the transaction —
    a registry-write failure must not silently lose the role switch."""
    db_path = project_root / "groundtruth.db"
    if not db_path.is_file():
        return
    try:
        from groundtruth_kb.db import KnowledgeDB
        from groundtruth_kb.harness_projection import generate_harness_projection
    except Exception:
        return
    harnesses = role_map.get("harnesses")
    if not isinstance(harnesses, dict):
        return
    try:
        db = KnowledgeDB(db_path=db_path)
        changed = False
        for harness_id, record in harnesses.items():
            if not isinstance(record, dict):
                continue
            raw_role = record.get("role")
            if isinstance(raw_role, list):
                new_role = [str(r) for r in raw_role if str(r).strip()]
            elif isinstance(raw_role, str) and raw_role.strip():
                new_role = [raw_role.strip()]
            else:
                new_role = []
            current = db.get_harness(str(harness_id))
            if current is None:
                continue
            current_role = _decode_harness_json_field(current.get("role"))
            current_role_list = current_role if isinstance(current_role, list) else []
            current_status = str(current.get("status") or "registered")
            new_status = str(record.get("status") or "registered")
            if sorted(str(r) for r in current_role_list) == sorted(new_role) and current_status == new_status:
                continue
            db.insert_harness(
                id=str(harness_id),
                harness_name=str(current.get("harness_name") or harness_id),
                harness_type=str(current.get("harness_type") or harness_id),
                role=new_role,
                changed_by="mode-switch-transaction",
                change_reason=change_reason,
                status=new_status,
                reviewer_precedence=current.get("reviewer_precedence"),
                invocation_surfaces=_decode_harness_json_field(current.get("invocation_surfaces")),
                capabilities_ref=current.get("capabilities_ref"),
            )
            changed = True
        if changed:
            generate_harness_projection(db, project_root)
    except Exception as exc:
        # WI-3342 IP-5: the DB-backed registry is now the sole authoritative
        # role surface (the transitional role-assignments.json write was
        # removed), so a registry-write failure must fail the transaction
        # rather than silently lose the role switch.
        raise RuntimeError(f"harness registry write failed during role-switch transaction: {exc}") from exc


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

    1. Validate role artifact (the harness registry projection).
    2. Validate bridge artifact (``bridge/INDEX.md``).
    3. Validate session-state artifact (``.claude/session/work-subject.json``).
    4. Validate role token against ``VALID_ROLES_FOR_WRITE`` (SET-rejects
       ``acting-prime-builder``).
    5. Resolve harness id-or-name to harness id.
    6. Read the role map from the DB-backed registry projection; compute the
       new active-role assignments. Non-active harness role sets are preserved;
       one active harness carries PB+LO in single-active mode; PB and LO are
       distinct in multi-active mode.
    7. Write audit-trail record FIRST (per failure-leaves-no-state-mutation
       invariant).
    8. WI-3342 IP-5: the transitional ``role-assignments.json`` write is
       removed — the DB registry and projection (Step 10) are the sole
       authoritative role surface.
    9. Atomically write work-subject.json with derived topology if file
       exists.
    10. Write the post-switch role map to the DB harnesses registry and
       regenerate the hot-path projection — the authoritative role write.

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
    # WI-3342 IP-5: the current role map is read from the DB-backed registry
    # projection (harness-state/harness-registry.json), not the retired
    # harness-state/role-assignments.json. The projection stores harnesses as a
    # LIST; convert to the {harness_id: record} dict shape the role-switch
    # logic below mutates.
    from groundtruth_kb.harness_projection import harness_registry_path

    registry_path = harness_registry_path(project_root)
    projection = json.loads(registry_path.read_text(encoding="utf-8"))
    projection_harnesses = projection.get("harnesses", []) if isinstance(projection, dict) else []
    role_map: dict[str, Any] = {
        "harnesses": {str(rec["id"]): rec for rec in projection_harnesses if isinstance(rec, dict) and rec.get("id")}
    }
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

    # Active-harness assignment: the target receives the requested role, the
    # complementary role is preserved or assigned to a different active harness
    # when possible. Non-active harness role sets are preserved because
    # role/status/capability are orthogonal; an active harness demoted out of
    # the active assignment is suspended and cleared intentionally.
    new_role_set = _apply_active_role_assignment(
        harnesses,
        target_id=harness_id,
        requested_role=role,
    )

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

    # Step 8: WI-3342 IP-5 — the transitional legacy-JSON write of
    # harness-state/role-assignments.json is removed. The DB-backed registry
    # and its projection (written authoritatively by Step 10) are now the sole
    # authoritative role surface.

    # Step 9: Atomic write work-subject.json with derived topology (if it
    # exists).
    session_path = project_root / ".claude" / "session" / "work-subject.json"
    if session_path.exists():
        session_data = json.loads(session_path.read_text(encoding="utf-8"))
        if isinstance(session_data, dict):
            session_data["topology_mode"] = derived_topology
            _atomic_write_json(session_path, session_data)

    # Step 10: WI-3342 IP-5 — write the post-switch role map to the DB
    # harnesses registry and regenerate the hot-path projection. This is the
    # authoritative role write (the legacy-JSON write was removed at Step 8).
    _mirror_role_map_to_registry(project_root, role_map, change_reason)

    return TransactionResult(
        harness_id=harness_id,
        previous_role_set=previous_role_set,
        new_role_set=new_role_set,
        derived_topology=derived_topology,
        audit_record_path=audit_path,
        applied_at=when,
    )
