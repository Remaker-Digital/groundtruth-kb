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

Role assignment (``gt harness set-role``) is NOT handled here. Its DB-coherent
behavior is ``REQ-HARNESS-REGISTRY-001`` FR9, delivered by WI-3341; WI-3340
registers ``set-role`` only as a guarded command.

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


class HarnessOperationError(RuntimeError):
    """Raised when a harness registry operation cannot be completed.

    Carries an operator-facing message; the ``gt harness`` CLI re-raises it as
    a ``click.ClickException`` so the command exits non-zero with a clear
    explanation and no traceback.
    """


# An operator who used the wrong lifecycle verb is pointed at the correct verb
# for the harness's actual status.
_STATUS_VERB_HINT: dict[str, str] = {
    harness_lifecycle.STATUS_REGISTERED: (
        "use 'gt harness activate' to bring a registered harness into service"
    ),
    harness_lifecycle.STATUS_ACTIVE: (
        "use 'gt harness suspend' to suspend an active harness"
    ),
    harness_lifecycle.STATUS_SUSPENDED: (
        "use 'gt harness resume' to return a suspended harness to service"
    ),
    harness_lifecycle.STATUS_RETIRED: (
        "'retired' is terminal; the harness has no further transitions"
    ),
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
        raise HarnessOperationError(
            f"unexpected harness field override(s): {sorted(overrides)}"
        )
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
            role=list(role),
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
    graph. Raises ``HarnessOperationError`` on an unknown harness, a
    wrong-source-state verb use, or an FSM-invalid transition.
    """
    current = db.get_harness(harness_id)
    if current is None:
        raise HarnessOperationError(
            f"unknown harness {harness_id!r}; no such harness in the registry"
        )
    current_status = current["status"]
    if expected_source is not None and current_status != expected_source:
        hint = _STATUS_VERB_HINT.get(current_status, "")
        raise HarnessOperationError(
            f"harness {harness_id!r} has status {current_status!r}, not "
            f"{expected_source!r}" + (f"; {hint}" if hint else "")
        )
    if (
        target_status == harness_lifecycle.STATUS_RETIRED
        and current_status == harness_lifecycle.STATUS_ACTIVE
    ):
        harness_lifecycle.validate_transition(
            harness_lifecycle.STATUS_ACTIVE, harness_lifecycle.STATUS_SUSPENDED
        )
        suspended = _append_version(
            db,
            current,
            changed_by=changed_by,
            change_reason=f"{change_reason} [auto-suspend before retire]",
            status=harness_lifecycle.STATUS_SUSPENDED,
        )
        harness_lifecycle.validate_transition(
            harness_lifecycle.STATUS_SUSPENDED, harness_lifecycle.STATUS_RETIRED
        )
        return _append_version(
            db,
            suspended,
            changed_by=changed_by,
            change_reason=change_reason,
            status=harness_lifecycle.STATUS_RETIRED,
        )
    try:
        harness_lifecycle.validate_transition(current_status, target_status)
    except ValueError as exc:
        raise HarnessOperationError(str(exc)) from exc
    return _append_version(
        db,
        current,
        changed_by=changed_by,
        change_reason=change_reason,
        status=target_status,
    )


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
        raise HarnessOperationError(
            f"unknown harness {harness_id!r}; no such harness in the registry"
        )
    return _append_version(
        db,
        current,
        changed_by=changed_by,
        change_reason=change_reason,
        reviewer_precedence=reviewer_precedence,
    )
