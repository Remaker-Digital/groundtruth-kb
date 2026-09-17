"""Typed operational-event service (WI-6992).

``GOV-GTKB-EMERGENCY-BOOTSTRAP-001`` v4 states: *"The canonical service exposes
only typed* ``create``, ``inspect``, ``append``, ``show`` *and* ``verify``
*operations. Agents never access raw storage."* This module is that service.

The record it operates on is derived from the canon section 9 evidence list, not
from the legacy ``operational_events`` table. Per the owner ruling of 2026-08-31
authorization is a **value** on the project record and never an object, so the
three legacy ``project_authorization_*`` columns collapse to a single
``project_authorization_value``; ``execution_membership_id`` and
``execution_membership_version`` are dropped because section 9 states no
requirement they satisfy.

The legacy ``operational_events`` table is pre-definition history. No operation
here reads or writes it: a row lacking a declared authorization value cannot be
verified against a record that requires one, and returning it through this typed
surface would imply a conformance it does not have.

``verify`` is **integrity checking**, settled at
``bridge/gtkb-wi6992-five-operation-event-service-002.md`` and restated at
``-004``: digest agreement, gapless monotonic versions, and legal lifecycle
transitions. It is not independent-verification workflow state.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

__all__ = [
    "OperationalEventError",
    "SCHEMA_VERSION",
    "TABLE",
    "append",
    "create",
    "inspect",
    "show",
    "verify",
]

TABLE = "governed_operational_events"
SCHEMA_VERSION = 1

EVENT_TYPES = frozenset({"emergency_bootstrap", "foundational_bootstrap"})
AUTHORIZATION_VALUES = frozenset({"authorized", "not authorized"})

#: Lifecycle order. Canon section 9 records an operational event progressing from
#: open through independent verification to publication-confirmed closure.
LIFECYCLE_ORDER: tuple[str, ...] = (
    "open",
    "effects_recorded_pending_independent_verification",
    "independently_verified",
    "committed_pending_publication",
    "closed",
    "publication_confirmed_closed",
)
LIFECYCLE_STATES = frozenset(LIFECYCLE_ORDER)

#: The twelve elements canon section 9 requires an emergency-bootstrap event to
#: bind. Structural fields (work item, project, authorization value, actor) are
#: columns; the rest live in ``body_json`` under this declared shape and are
#: covered by ``body_sha256``.
BODY_ELEMENTS: tuple[str, ...] = (
    "applicable_formal_authority",
    "proof_of_foundational_deadlock",
    "exact_bypassed_control",
    "owner_approved_scope",
    "non_goals",
    "preimages",
    "postimages",
    "verifier_provenance",
    "tests_and_observed_results",
    "commit_identity",
    "owner_approval",
    "after_action_findings",
)


class OperationalEventError(RuntimeError):
    """Typed refusal. Carries a stable ``code`` for callers to branch on."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class EventRow:
    """One immutable version of one operational event."""

    id: str
    version: int
    schema_version: int
    event_type: str
    lifecycle_state: str
    work_item_id: str
    work_item_version: int
    project_id: str
    project_version: int
    project_authorization_value: str
    body: dict[str, Any]
    body_sha256: str
    recorder_session_context_id: str
    recorded_at: str


def _canonical_body_bytes(body: dict[str, Any]) -> bytes:
    """Deterministic encoding, so a digest is reproducible across processes."""
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _digest(body: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_body_bytes(body)).hexdigest()


def _row_to_event(row: sqlite3.Row) -> EventRow:
    return EventRow(
        id=row["id"],
        version=row["version"],
        schema_version=row["schema_version"],
        event_type=row["event_type"],
        lifecycle_state=row["lifecycle_state"],
        work_item_id=row["work_item_id"],
        work_item_version=row["work_item_version"],
        project_id=row["project_id"],
        project_version=row["project_version"],
        project_authorization_value=row["project_authorization_value"],
        body=json.loads(row["body_json"]),
        body_sha256=row["body_sha256"],
        recorder_session_context_id=row["recorder_session_context_id"],
        recorded_at=row["recorded_at"],
    )


def _validate_enums(*, event_type: str, lifecycle_state: str, authorization_value: str) -> None:
    if event_type not in EVENT_TYPES:
        raise OperationalEventError("invalid_event_type", f"event_type must be one of {sorted(EVENT_TYPES)}")
    if lifecycle_state not in LIFECYCLE_STATES:
        raise OperationalEventError(
            "invalid_lifecycle_state", f"lifecycle_state must be one of {list(LIFECYCLE_ORDER)}"
        )
    if authorization_value not in AUTHORIZATION_VALUES:
        raise OperationalEventError(
            "invalid_authorization_value",
            "project_authorization_value must be 'authorized' or 'not authorized'; "
            "authorization is a value on the project record, never an object reference",
        )


def _current(connection: sqlite3.Connection, event_id: str) -> sqlite3.Row | None:
    connection.row_factory = sqlite3.Row
    row: sqlite3.Row | None = connection.execute(
        f'SELECT * FROM "{TABLE}" WHERE id = ? ORDER BY version DESC LIMIT 1', (event_id,)
    ).fetchone()
    return row


def create(
    connection: sqlite3.Connection,
    *,
    event_id: str,
    event_type: str,
    work_item_id: str,
    work_item_version: int,
    project_id: str,
    project_version: int,
    project_authorization_value: str,
    body: dict[str, Any],
    recorder_session_context_id: str,
) -> EventRow:
    """Open a new event at version 1 in lifecycle state ``open``."""
    _validate_enums(
        event_type=event_type,
        lifecycle_state="open",
        authorization_value=project_authorization_value,
    )
    if _current(connection, event_id) is not None:
        raise OperationalEventError("event_exists", f"operational event {event_id} already exists; use append")

    digest = _digest(body)
    recorded_at = datetime.now(UTC).isoformat()
    connection.execute(
        f'INSERT INTO "{TABLE}" (id, version, schema_version, event_type, lifecycle_state,'
        " work_item_id, work_item_version, project_id, project_version,"
        " project_authorization_value, body_json, body_sha256,"
        " recorder_session_context_id, recorded_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            event_id,
            1,
            SCHEMA_VERSION,
            event_type,
            "open",
            work_item_id,
            work_item_version,
            project_id,
            project_version,
            project_authorization_value,
            _canonical_body_bytes(body).decode("utf-8"),
            digest,
            recorder_session_context_id,
            recorded_at,
        ),
    )
    connection.commit()
    return inspect(connection, event_id=event_id)


def append(
    connection: sqlite3.Connection,
    *,
    event_id: str,
    expected_current_version: int,
    lifecycle_state: str,
    body: dict[str, Any],
    recorder_session_context_id: str,
) -> EventRow:
    """Append the next version under compare-and-set.

    ``expected_current_version`` is the CAS token. A stale value writes nothing.
    """
    current = _current(connection, event_id)
    if current is None:
        raise OperationalEventError("event_absent", f"operational event {event_id} does not exist")
    if current["version"] != expected_current_version:
        raise OperationalEventError(
            "version_conflict",
            f"expected current version {expected_current_version}, found {current['version']}",
        )
    _validate_enums(
        event_type=current["event_type"],
        lifecycle_state=lifecycle_state,
        authorization_value=current["project_authorization_value"],
    )
    if LIFECYCLE_ORDER.index(lifecycle_state) < LIFECYCLE_ORDER.index(current["lifecycle_state"]):
        raise OperationalEventError(
            "illegal_transition",
            f"lifecycle cannot move backward from {current['lifecycle_state']} to {lifecycle_state}",
        )

    connection.execute(
        f'INSERT INTO "{TABLE}" (id, version, schema_version, event_type, lifecycle_state,'
        " work_item_id, work_item_version, project_id, project_version,"
        " project_authorization_value, body_json, body_sha256,"
        " recorder_session_context_id, recorded_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            event_id,
            current["version"] + 1,
            SCHEMA_VERSION,
            current["event_type"],
            lifecycle_state,
            current["work_item_id"],
            current["work_item_version"],
            current["project_id"],
            current["project_version"],
            current["project_authorization_value"],
            _canonical_body_bytes(body).decode("utf-8"),
            _digest(body),
            recorder_session_context_id,
            datetime.now(UTC).isoformat(),
        ),
    )
    connection.commit()
    return inspect(connection, event_id=event_id)


def inspect(connection: sqlite3.Connection, *, event_id: str) -> EventRow:
    """Return the current version of one event."""
    row = _current(connection, event_id)
    if row is None:
        raise OperationalEventError("event_absent", f"operational event {event_id} does not exist")
    return _row_to_event(row)


def show(connection: sqlite3.Connection, *, event_id: str) -> list[EventRow]:
    """Return the full append-only version history, oldest first."""
    connection.row_factory = sqlite3.Row
    rows = connection.execute(f'SELECT * FROM "{TABLE}" WHERE id = ? ORDER BY version ASC', (event_id,)).fetchall()
    if not rows:
        raise OperationalEventError("event_absent", f"operational event {event_id} does not exist")
    return [_row_to_event(r) for r in rows]


def verify(connection: sqlite3.Connection, *, event_id: str) -> dict[str, Any]:
    """Integrity-check one event.

    Checks digest agreement, gapless monotonic versions from 1, and legal
    lifecycle transitions. Returns a report rather than raising, so a caller can
    see every problem at once instead of only the first.
    """
    history = show(connection, event_id=event_id)
    problems: list[str] = []

    for index, event in enumerate(history, start=1):
        if event.version != index:
            problems.append(f"version sequence broken at position {index}: found version {event.version}")
        if _digest(event.body) != event.body_sha256:
            problems.append(f"body_sha256 mismatch at version {event.version}")
        if event.schema_version != SCHEMA_VERSION:
            problems.append(f"unexpected schema_version {event.schema_version} at version {event.version}")

    for earlier, later in zip(history, history[1:], strict=False):
        if LIFECYCLE_ORDER.index(later.lifecycle_state) < LIFECYCLE_ORDER.index(earlier.lifecycle_state):
            problems.append(
                f"illegal transition {earlier.lifecycle_state} -> {later.lifecycle_state} at version {later.version}"
            )

    return {
        "event_id": event_id,
        "versions": len(history),
        "current_lifecycle_state": history[-1].lifecycle_state,
        "ok": not problems,
        "problems": problems,
    }
