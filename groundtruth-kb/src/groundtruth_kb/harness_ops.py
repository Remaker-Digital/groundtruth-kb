"""Harness registry operations: registration, lifecycle, and precedence.

``REQ-HARNESS-REGISTRY-001`` FR3: the ``gt harness`` command group's mutating
verbs perform their work through one deterministic transaction discipline —
validate first, then an atomic append-only write whose
``changed_by`` / ``changed_at`` / ``change_reason`` columns are the audit
trail. This module is that discipline for the ``harnesses``-table verbs
(``register`` / ``activate`` / ``suspend`` / ``resume`` / ``retire`` /
``set-precedence``).

It is pure DB logic: it imports only the standard library and
``groundtruth_kb.harness_lifecycle`` (the WI-3339 FSM), opens no file, and
writes no projection — the ``gt harness`` CLI refreshes the FR5 projection
after a successful mutation.

Direct active role assignment (``gt harness set-role``) is handled by the
operating mode transaction path. Lifecycle operations rebalance the active
harness set while preserving non-active role retention so role assignment and
dispatch eligibility remain orthogonal.

Authority: ``REQ-HARNESS-REGISTRY-001`` (FR3, FR1, FR2); ``DELIB-2079`` Q6
(unified ``gt harness`` command group); owner AskUserQuestion 2026-05-16
(retiring an active harness auto-suspends first).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
from typing import Any

from groundtruth_kb import harness_lifecycle

ROLE_PRIME_BUILDER = "prime-builder"
ROLE_LOYAL_OPPOSITION = "loyal-opposition"
VALID_OPERATING_ROLES = frozenset({ROLE_PRIME_BUILDER, ROLE_LOYAL_OPPOSITION})


class HarnessOperationError(RuntimeError):
    """Raised when a harness registry operation cannot be completed.

    Carries an operator-facing message; the ``gt harness`` CLI re-raises it as
    a ``click.ClickException`` so the command exits non-zero with a clear
    explanation and no traceback.
    """


# An operator who used the wrong lifecycle verb is pointed at the correct verb
# for the harness's actual status.
_STATUS_VERB_HINT: dict[str, str] = {
    harness_lifecycle.STATUS_REGISTERED: ("use 'gt harness activate' to bring a registered harness into service"),
    harness_lifecycle.STATUS_ACTIVE: ("use 'gt harness suspend' to suspend an active harness"),
    harness_lifecycle.STATUS_SUSPENDED: ("use 'gt harness resume' to return a suspended harness to service"),
    harness_lifecycle.STATUS_RETIRED: ("'retired' is terminal; the harness has no further transitions"),
}

# FR1 content fields carried forward verbatim when appending a new harness
# version, unless explicitly overridden by a verb.
_CARRY_FIELDS = (
    "harness_name",
    "harness_type",
    "status",
    "reviewer_precedence",
    "capabilities_ref",
)


def _role_tokens(raw: Any) -> list[str]:
    decoded = _decode_json_field(raw)
    if isinstance(decoded, str):
        decoded = [decoded]
    if isinstance(decoded, (tuple, set, frozenset)):
        decoded = list(decoded)
    if not isinstance(decoded, list):
        return []
    return sorted({str(token).strip() for token in decoded if str(token).strip() in VALID_OPERATING_ROLES})


def _record_id(record: dict[str, Any]) -> str:
    return str(record.get("id") or "")


def _sort_harnesses(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Stable deterministic ordering for automatic role repair.

    Lower reviewer_precedence wins when present; otherwise ids sort
    lexicographically. This keeps automatic fallback choices reproducible while
    still honoring the reviewer-precedence field when operators set it.
    """

    def key(record: dict[str, Any]) -> tuple[int, int, str]:
        precedence = record.get("reviewer_precedence")
        if isinstance(precedence, int):
            return (0, precedence, _record_id(record))
        return (1, 0, _record_id(record))

    return sorted(records, key=key)


def _active_harnesses(db: Any) -> list[dict[str, Any]]:
    return [
        row
        for row in db.list_harnesses()
        if isinstance(row, dict) and row.get("status") == harness_lifecycle.STATUS_ACTIVE
    ]


def _current_roles(row: dict[str, Any]) -> list[str]:
    return _role_tokens(row.get("role"))


def _choose_existing_role_holder(
    active: list[dict[str, Any]],
    role: str,
    *,
    exclude_id: str | None = None,
) -> str | None:
    candidates = [
        row for row in _sort_harnesses(active) if _record_id(row) != exclude_id and role in _current_roles(row)
    ]
    return _record_id(candidates[0]) if candidates else None


def _choose_any_active(
    active: list[dict[str, Any]],
    *,
    exclude_id: str | None = None,
) -> str | None:
    candidates = [row for row in _sort_harnesses(active) if _record_id(row) != exclude_id]
    return _record_id(candidates[0]) if candidates else None


def _desired_role_assignments(
    rows: list[dict[str, Any]],
    *,
    preferred_prime_id: str | None = None,
    preferred_lo_id: str | None = None,
) -> dict[str, list[str]]:
    active = [row for row in rows if isinstance(row, dict) and row.get("status") == harness_lifecycle.STATUS_ACTIVE]
    active_by_id = {_record_id(row): row for row in active}
    if not active:
        raise HarnessOperationError("cannot satisfy operating-role invariant: no active harness remains")

    if len(active) == 1:
        only_id = _record_id(active[0])
        return {
            _record_id(row): (
                [ROLE_LOYAL_OPPOSITION, ROLE_PRIME_BUILDER] if _record_id(row) == only_id else _current_roles(row)
            )
            for row in rows
        }

    prime_id = (
        preferred_prime_id
        if preferred_prime_id in active_by_id
        else _choose_existing_role_holder(active, ROLE_PRIME_BUILDER)
    )
    if prime_id is None:
        prime_id = _choose_any_active(active)
    if prime_id is None:
        raise HarnessOperationError("cannot select an active prime-builder harness")

    lo_id = (
        preferred_lo_id
        if preferred_lo_id in active_by_id and preferred_lo_id != prime_id
        else _choose_existing_role_holder(active, ROLE_LOYAL_OPPOSITION, exclude_id=prime_id)
    )
    if lo_id is None:
        lo_id = _choose_any_active(active, exclude_id=prime_id)
    if lo_id is None or lo_id == prime_id:
        raise HarnessOperationError(
            "cannot satisfy operating-role invariant: PB and LO require distinct "
            "active harnesses when more than one active harness exists"
        )

    assignments: dict[str, list[str]] = {}
    for row in rows:
        harness_id = _record_id(row)
        roles: list[str] = []
        if harness_id not in active_by_id:
            roles = _current_roles(row)
        if harness_id == lo_id:
            roles.append(ROLE_LOYAL_OPPOSITION)
        if harness_id == prime_id:
            roles.append(ROLE_PRIME_BUILDER)
        assignments[harness_id] = roles
    return assignments


def _decode_json_field(raw: Any) -> Any:
    """Decode a JSON-text column value into a native object.

    The ``harnesses`` table stores ``role`` and ``invocation_surfaces`` as JSON
    text and ``get_harness`` returns them in that form. This mirrors
    ``harness_projection._decode_json_field`` so the encode/decode boundary is
    handled the same way on both the projection and the operations paths.
    """
    if raw is None or raw == "":
        return None
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw


def _append_version(
    db: Any,
    current_row: dict[str, Any],
    *,
    changed_by: str,
    change_reason: str,
    **overrides: Any,
) -> dict[str, Any]:
    """Append the next version of an existing harness, carrying FR1 fields forward.

    Every FR1 content field of ``current_row`` is carried forward unless named
    in ``overrides``. ``role`` and ``invocation_surfaces`` are decoded from the
    stored JSON text before being handed back to ``insert_harness`` (which
    re-encodes them). Raises ``HarnessOperationError`` on an unexpected override
    field name.
    """
    role = overrides.pop("role", _decode_json_field(current_row.get("role")))
    if not isinstance(role, list):
        role = []
    invocation_surfaces = overrides.pop(
        "invocation_surfaces",
        _decode_json_field(current_row.get("invocation_surfaces")),
    )
    fields: dict[str, Any] = {name: current_row.get(name) for name in _CARRY_FIELDS}
    for name in _CARRY_FIELDS:
        if name in overrides:
            fields[name] = overrides.pop(name)
    if overrides:
        raise HarnessOperationError(f"unexpected harness field override(s): {sorted(overrides)}")
    return db.insert_harness(
        id=current_row["id"],
        harness_name=fields["harness_name"],
        harness_type=fields["harness_type"],
        role=role,
        changed_by=changed_by,
        change_reason=change_reason,
        status=fields["status"],
        reviewer_precedence=fields["reviewer_precedence"],
        invocation_surfaces=invocation_surfaces,
        capabilities_ref=fields["capabilities_ref"],
    )


def reconcile_role_assignments(
    db: Any,
    *,
    changed_by: str,
    change_reason: str,
    preferred_prime_id: str | None = None,
    preferred_lo_id: str | None = None,
) -> None:
    """Repair active operating-role assignments to match the active harness set.

    The registrar invariant is:

    - non-active harnesses may retain PB/LO role assignment for interactive or
      owner-directed work, but do not participate in active role partitioning;
    - with one active harness, that harness carries PB+LO;
    - with multiple active harnesses, exactly one active harness carries PB and
      exactly one different active harness carries LO.

    The function appends only rows whose role set actually changes. Non-active
    rows carry their current role set forward unchanged.
    """
    rows = [row for row in db.list_harnesses() if isinstance(row, dict)]
    assignments = _desired_role_assignments(
        rows,
        preferred_prime_id=preferred_prime_id,
        preferred_lo_id=preferred_lo_id,
    )
    for row in rows:
        harness_id = _record_id(row)
        desired = assignments.get(harness_id, _current_roles(row))
        if _current_roles(row) == desired:
            continue
        _append_version(
            db,
            row,
            changed_by=changed_by,
            change_reason=change_reason,
            role=desired,
        )


def register_harness(
    db: Any,
    *,
    id: str,
    harness_name: str,
    harness_type: str,
    role: Any = (),
    reviewer_precedence: int | None = None,
    invocation_surfaces: dict[str, Any] | None = None,
    capabilities_ref: str | None = None,
    changed_by: str,
    change_reason: str,
) -> dict[str, Any]:
    """Register a new harness at status ``registered`` (FR3 ``register``, FR1).

    Raises ``HarnessOperationError`` if a harness with ``id`` already exists:
    ``register`` is for new harness identities; an existing harness is changed
    through the lifecycle and precedence verbs.
    """
    if _role_tokens(role):
        raise HarnessOperationError(
            "registration is separate from operating-role assignment; register "
            "the harness with no role, activate it, then use 'gt harness set-role'"
        )
    existing = db.get_harness(id)
    if existing is not None:
        raise HarnessOperationError(
            f"harness {id!r} is already registered (current status: "
            f"{existing.get('status')!r}); use the lifecycle verbs to change it"
        )
    try:
        return db.insert_harness(
            id=id,
            harness_name=harness_name,
            harness_type=harness_type,
            role=[],
            changed_by=changed_by,
            change_reason=change_reason,
            status=harness_lifecycle.STATUS_REGISTERED,
            reviewer_precedence=reviewer_precedence,
            invocation_surfaces=invocation_surfaces,
            capabilities_ref=capabilities_ref,
        )
    except ValueError as exc:
        raise HarnessOperationError(str(exc)) from exc


def transition_harness(
    db: Any,
    harness_id: str,
    target_status: str,
    *,
    changed_by: str,
    change_reason: str,
    expected_source: str | None = None,
) -> dict[str, Any]:
    """Transition a harness to ``target_status`` through the FR2 FSM.

    Backs the FR3 lifecycle verbs ``activate`` / ``suspend`` / ``resume`` /
    ``retire``. ``expected_source`` lets a verb assert the harness's current
    status so a misused verb (e.g. ``activate`` on a suspended harness) fails
    with a hint naming the correct verb. Retiring an ``active`` harness
    auto-suspends it first (``active -> suspended -> retired``) per the owner's
    2026-05-16 AskUserQuestion decision; the FSM keeps its literal four-edge
    graph. Role metadata is carried forward across non-active lifecycle states
    because role membership, lifecycle status, and dispatch capability are
    orthogonal. Raises ``HarnessOperationError`` on an unknown harness, a
    wrong-source-state verb use, or an FSM-invalid transition.
    """
    current = db.get_harness(harness_id)
    if current is None:
        raise HarnessOperationError(f"unknown harness {harness_id!r}; no such harness in the registry")
    current_status = current["status"]
    if expected_source is not None and current_status != expected_source:
        hint = _STATUS_VERB_HINT.get(current_status, "")
        raise HarnessOperationError(
            f"harness {harness_id!r} has status {current_status!r}, not "
            f"{expected_source!r}" + (f"; {hint}" if hint else "")
        )
    if target_status in {
        harness_lifecycle.STATUS_SUSPENDED,
        harness_lifecycle.STATUS_RETIRED,
    }:
        active_count = len(_active_harnesses(db))
        if current_status == harness_lifecycle.STATUS_ACTIVE and active_count <= 1:
            raise HarnessOperationError(
                f"cannot {target_status} harness {harness_id!r}; it is the last "
                "active harness, and GT-KB must always retain one active PB and "
                "one active LO assignment"
            )
        if current_status != harness_lifecycle.STATUS_ACTIVE and active_count == 0:
            raise HarnessOperationError(
                f"cannot {target_status} harness {harness_id!r}; no active "
                "harness exists to carry PB/LO after the transition"
            )
    if target_status == harness_lifecycle.STATUS_RETIRED and current_status == harness_lifecycle.STATUS_ACTIVE:
        current_role = _decode_json_field(current.get("role"))
        retained_role = current_role if isinstance(current_role, list) else []
        harness_lifecycle.validate_transition(harness_lifecycle.STATUS_ACTIVE, harness_lifecycle.STATUS_SUSPENDED)
        suspended = _append_version(
            db,
            current,
            changed_by=changed_by,
            change_reason=f"{change_reason} [auto-suspend before retire]",
            status=harness_lifecycle.STATUS_SUSPENDED,
            role=retained_role,
        )
        harness_lifecycle.validate_transition(harness_lifecycle.STATUS_SUSPENDED, harness_lifecycle.STATUS_RETIRED)
        _append_version(
            db,
            suspended,
            changed_by=changed_by,
            change_reason=change_reason,
            status=harness_lifecycle.STATUS_RETIRED,
            role=retained_role,
        )
        reconcile_role_assignments(
            db,
            changed_by=changed_by,
            change_reason=f"{change_reason} [role invariant reconciliation]",
        )
        return db.get_harness(harness_id)
    try:
        harness_lifecycle.validate_transition(current_status, target_status)
    except ValueError as exc:
        raise HarnessOperationError(str(exc)) from exc
    current_role = _decode_json_field(current.get("role"))
    retained_role = current_role if isinstance(current_role, list) else []
    _append_version(
        db,
        current,
        changed_by=changed_by,
        change_reason=change_reason,
        status=target_status,
        role=retained_role,
    )
    reconcile_role_assignments(
        db,
        changed_by=changed_by,
        change_reason=f"{change_reason} [role invariant reconciliation]",
    )
    return db.get_harness(harness_id)


def set_harness_precedence(
    db: Any,
    harness_id: str,
    reviewer_precedence: int | None,
    *,
    changed_by: str,
    change_reason: str,
) -> dict[str, Any]:
    """Set a harness's ``reviewer_precedence`` (FR3 ``set-precedence``).

    Appends a new harness version with the updated precedence; all other FR1
    fields, including ``status``, carry forward unchanged. Precedence is
    independent of the lifecycle FSM. Raises ``HarnessOperationError`` for an
    unknown harness.
    """
    current = db.get_harness(harness_id)
    if current is None:
        raise HarnessOperationError(f"unknown harness {harness_id!r}; no such harness in the registry")
    return _append_version(
        db,
        current,
        changed_by=changed_by,
        change_reason=change_reason,
        reviewer_precedence=reviewer_precedence,
    )
