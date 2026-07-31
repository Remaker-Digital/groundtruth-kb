"""SQLite-backed journal for bounded, resumable platform operations."""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


class RuntimeRecoveryError(RuntimeError):
    """Base error for runtime recovery contract violations."""


class OperationCollision(RuntimeRecoveryError):
    """Raised when an operation ID is reused for different immutable inputs."""


class StaleOwnership(RuntimeRecoveryError):
    """Raised when a superseded or expired claimant attempts a mutation."""


class IllegalTransition(RuntimeRecoveryError):
    """Raised when an operation cannot perform the requested transition."""


class CompletionConflict(RuntimeRecoveryError):
    """Raised when a completed operation receives a different result."""


class RuntimeStatus(StrEnum):
    """Persisted operation states."""

    RUNNING = "running"
    RETRY_WAIT = "retry_wait"
    COMPLETED = "completed"
    QUARANTINED = "quarantined"


class ClaimOutcome(StrEnum):
    """Result of an atomic ownership claim."""

    ACQUIRED = "acquired"
    BUSY = "busy"
    RETRY_WAIT = "retry_wait"
    COMPLETED = "completed"
    QUARANTINED = "quarantined"


@dataclass(frozen=True)
class AttemptClaim:
    """Opaque ownership capability for one operation attempt."""

    operation_id: str
    owner_id: str
    token: str
    attempt_number: int
    lease_seconds: int
    lease_expires_at: float


@dataclass(frozen=True)
class OperationSnapshot:
    """Current durable state of an operation."""

    operation_id: str
    operation_kind: str
    input_fingerprint: str
    status: RuntimeStatus
    owner_id: str | None
    attempt_count: int
    max_attempts: int
    lease_seconds: int
    lease_expires_at: float | None
    next_retry_at: float | None
    checkpoint: dict[str, Any] | None
    result: dict[str, Any] | None
    last_error: str | None
    created_at: float
    updated_at: float
    completed_at: float | None
    version: int


@dataclass(frozen=True)
class ClaimDecision:
    """Atomic claim outcome and resulting operation state."""

    outcome: ClaimOutcome
    operation: OperationSnapshot
    claim: AttemptClaim | None = None


@dataclass(frozen=True)
class OperationEvent:
    """One ordered, append-only operation transition."""

    event_id: int
    operation_id: str
    event_type: str
    from_status: RuntimeStatus | None
    to_status: RuntimeStatus
    attempt_number: int
    owner_id: str | None
    detail: dict[str, Any]
    recorded_at: float


@dataclass(frozen=True)
class RecoveryObservation:
    """Read-only recovery recommendation derived from current durable state."""

    operation: OperationSnapshot
    recommended_action: str
    reason: str
    event_count: int
    last_event: OperationEvent


def _canonical_json(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(dict(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:
        raise ValueError("value must be a JSON-serializable object") from exc


def _json_object(value: str | None) -> dict[str, Any] | None:
    if value is None:
        return None
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise RuntimeRecoveryError("persisted runtime recovery JSON is not an object")
    return parsed


class RecoveryStore:
    """Transactional operation journal with leases, retries, and recovery views."""

    def __init__(
        self,
        db_path: Path,
        *,
        clock: Callable[[], float] = time.time,
        token_factory: Callable[[], str] | None = None,
        busy_timeout_seconds: float = 5.0,
    ) -> None:
        self.db_path = Path(db_path)
        self._clock = clock
        self._token_factory = token_factory or (lambda: uuid.uuid4().hex)
        self._busy_timeout_seconds = busy_timeout_seconds
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.db_path,
            timeout=self._busy_timeout_seconds,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute(f"PRAGMA busy_timeout={int(self._busy_timeout_seconds * 1000)}")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("PRAGMA wal_autocheckpoint=1000")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS runtime_recovery_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS runtime_operations (
                    operation_id TEXT PRIMARY KEY,
                    operation_kind TEXT NOT NULL,
                    input_fingerprint TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('running', 'retry_wait', 'completed', 'quarantined')
                    ),
                    owner_id TEXT,
                    owner_token TEXT,
                    attempt_count INTEGER NOT NULL CHECK (attempt_count >= 1),
                    max_attempts INTEGER NOT NULL CHECK (max_attempts >= 1),
                    lease_seconds INTEGER NOT NULL CHECK (lease_seconds >= 1),
                    lease_expires_at REAL,
                    next_retry_at REAL,
                    checkpoint_json TEXT,
                    result_json TEXT,
                    last_error TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    completed_at REAL,
                    version INTEGER NOT NULL CHECK (version >= 1)
                );

                CREATE TABLE IF NOT EXISTS runtime_operation_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_id TEXT NOT NULL REFERENCES runtime_operations(operation_id),
                    event_type TEXT NOT NULL,
                    from_status TEXT,
                    to_status TEXT NOT NULL,
                    attempt_number INTEGER NOT NULL,
                    owner_id TEXT,
                    detail_json TEXT NOT NULL,
                    recorded_at REAL NOT NULL
                );

                CREATE INDEX IF NOT EXISTS runtime_operation_events_operation
                    ON runtime_operation_events(operation_id, event_id);
                """
            )
            row = connection.execute(
                "SELECT value FROM runtime_recovery_metadata WHERE key = 'schema_version'"
            ).fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO runtime_recovery_metadata(key, value) VALUES ('schema_version', ?)",
                    (str(SCHEMA_VERSION),),
                )
            elif row["value"] != str(SCHEMA_VERSION):
                raise RuntimeRecoveryError(
                    f"unsupported runtime recovery schema version {row['value']}; expected {SCHEMA_VERSION}"
                )

    def claim(
        self,
        operation_id: str,
        *,
        operation_kind: str,
        input_fingerprint: str,
        owner_id: str,
        max_attempts: int = 3,
        lease_seconds: int = 300,
    ) -> ClaimDecision:
        """Atomically claim a new, retryable, or interrupted operation."""
        self._validate_identity(
            operation_id=operation_id,
            operation_kind=operation_kind,
            input_fingerprint=input_fingerprint,
            owner_id=owner_id,
            max_attempts=max_attempts,
            lease_seconds=lease_seconds,
        )
        now = self._clock()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = self._operation_row(connection, operation_id)
            if row is None:
                decision = self._create_operation(
                    connection,
                    operation_id=operation_id,
                    operation_kind=operation_kind,
                    input_fingerprint=input_fingerprint,
                    owner_id=owner_id,
                    max_attempts=max_attempts,
                    lease_seconds=lease_seconds,
                    now=now,
                )
            else:
                self._assert_same_operation(
                    row,
                    operation_kind=operation_kind,
                    input_fingerprint=input_fingerprint,
                    max_attempts=max_attempts,
                    lease_seconds=lease_seconds,
                )
                decision = self._claim_existing(connection, row=row, owner_id=owner_id, now=now)
            connection.commit()
            return decision
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def checkpoint(self, claim: AttemptClaim, value: Mapping[str, Any]) -> OperationSnapshot:
        """Persist a resumable checkpoint and renew the current claimant's lease."""
        encoded = _canonical_json(value)
        now = self._clock()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = self._require_live_owner(connection, claim, now=now)
            lease_expires_at = now + row["lease_seconds"]
            connection.execute(
                """
                UPDATE runtime_operations
                SET checkpoint_json = ?, lease_expires_at = ?, updated_at = ?, version = version + 1
                WHERE operation_id = ?
                """,
                (encoded, lease_expires_at, now, claim.operation_id),
            )
            self._append_event(
                connection,
                operation_id=claim.operation_id,
                event_type="checkpoint_recorded",
                from_status=RuntimeStatus.RUNNING,
                to_status=RuntimeStatus.RUNNING,
                attempt_number=claim.attempt_number,
                owner_id=claim.owner_id,
                detail={"checkpoint": dict(value), "lease_expires_at": lease_expires_at},
                recorded_at=now,
            )
            snapshot = self._snapshot(self._operation_row_required(connection, claim.operation_id))
            connection.commit()
            return snapshot
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def heartbeat(self, claim: AttemptClaim) -> OperationSnapshot:
        """Renew ownership without changing operation progress."""
        now = self._clock()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = self._require_live_owner(connection, claim, now=now)
            lease_expires_at = now + row["lease_seconds"]
            connection.execute(
                """
                UPDATE runtime_operations
                SET lease_expires_at = ?, updated_at = ?, version = version + 1
                WHERE operation_id = ?
                """,
                (lease_expires_at, now, claim.operation_id),
            )
            self._append_event(
                connection,
                operation_id=claim.operation_id,
                event_type="lease_renewed",
                from_status=RuntimeStatus.RUNNING,
                to_status=RuntimeStatus.RUNNING,
                attempt_number=claim.attempt_number,
                owner_id=claim.owner_id,
                detail={"lease_expires_at": lease_expires_at},
                recorded_at=now,
            )
            snapshot = self._snapshot(self._operation_row_required(connection, claim.operation_id))
            connection.commit()
            return snapshot
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def complete(self, claim: AttemptClaim, result: Mapping[str, Any]) -> OperationSnapshot:
        """Complete once; an identical repeated completion is a read-only success."""
        encoded = _canonical_json(result)
        now = self._clock()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = self._operation_row_required(connection, claim.operation_id)
            if row["status"] == RuntimeStatus.COMPLETED:
                if row["result_json"] != encoded:
                    raise CompletionConflict(f"operation {claim.operation_id!r} already has a different result")
                snapshot = self._snapshot(row)
                connection.commit()
                return snapshot
            self._assert_live_owner(row, claim, now=now)
            connection.execute(
                """
                UPDATE runtime_operations
                SET status = 'completed', owner_id = NULL, owner_token = NULL,
                    lease_expires_at = NULL, next_retry_at = NULL, result_json = ?,
                    updated_at = ?, completed_at = ?, version = version + 1
                WHERE operation_id = ?
                """,
                (encoded, now, now, claim.operation_id),
            )
            self._append_event(
                connection,
                operation_id=claim.operation_id,
                event_type="operation_completed",
                from_status=RuntimeStatus.RUNNING,
                to_status=RuntimeStatus.COMPLETED,
                attempt_number=claim.attempt_number,
                owner_id=claim.owner_id,
                detail={"result": dict(result)},
                recorded_at=now,
            )
            snapshot = self._snapshot(self._operation_row_required(connection, claim.operation_id))
            connection.commit()
            return snapshot
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def fail(
        self,
        claim: AttemptClaim,
        error: str,
        *,
        retryable: bool = True,
        retry_delay_seconds: float = 0,
    ) -> OperationSnapshot:
        """Record failure, scheduling a bounded retry or quarantining terminally."""
        error = error.strip()
        if not error:
            raise ValueError("error must not be empty")
        if retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must be non-negative")
        now = self._clock()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = self._require_live_owner(connection, claim, now=now)
            exhausted = row["attempt_count"] >= row["max_attempts"]
            if not retryable or exhausted:
                status = RuntimeStatus.QUARANTINED
                next_retry_at = None
                event_type = "operation_quarantined"
                reason = "non_retryable_failure" if not retryable else "attempt_limit_exhausted"
            else:
                status = RuntimeStatus.RETRY_WAIT
                next_retry_at = now + retry_delay_seconds
                event_type = "retry_scheduled"
                reason = "retryable_failure"
            connection.execute(
                """
                UPDATE runtime_operations
                SET status = ?, owner_id = NULL, owner_token = NULL, lease_expires_at = NULL,
                    next_retry_at = ?, last_error = ?, updated_at = ?, version = version + 1
                WHERE operation_id = ?
                """,
                (status.value, next_retry_at, error, now, claim.operation_id),
            )
            self._append_event(
                connection,
                operation_id=claim.operation_id,
                event_type=event_type,
                from_status=RuntimeStatus.RUNNING,
                to_status=status,
                attempt_number=claim.attempt_number,
                owner_id=claim.owner_id,
                detail={"error": error, "reason": reason, "next_retry_at": next_retry_at},
                recorded_at=now,
            )
            snapshot = self._snapshot(self._operation_row_required(connection, claim.operation_id))
            connection.commit()
            return snapshot
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def get(self, operation_id: str) -> OperationSnapshot | None:
        """Return current operation state without mutation."""
        with self._connect() as connection:
            row = self._operation_row(connection, operation_id)
            return None if row is None else self._snapshot(row)

    def events(self, operation_id: str) -> tuple[OperationEvent, ...]:
        """Return the operation's ordered, append-only event history."""
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM runtime_operation_events
                WHERE operation_id = ? ORDER BY event_id
                """,
                (operation_id,),
            ).fetchall()
            return tuple(self._event(row) for row in rows)

    def observe(self, operation_id: str) -> RecoveryObservation | None:
        """Describe the next recovery action without changing durable state."""
        now = self._clock()
        with self._connect() as connection:
            connection.execute("BEGIN")
            row = self._operation_row(connection, operation_id)
            if row is None:
                connection.commit()
                return None
            event_rows = connection.execute(
                """
                SELECT * FROM runtime_operation_events
                WHERE operation_id = ? ORDER BY event_id
                """,
                (operation_id,),
            ).fetchall()
            snapshot = self._snapshot(row)
            events = tuple(self._event(event_row) for event_row in event_rows)
            connection.commit()
        action, reason = self._recovery_action(snapshot, now=now)
        return RecoveryObservation(
            operation=snapshot,
            recommended_action=action,
            reason=reason,
            event_count=len(events),
            last_event=events[-1],
        )

    def _create_operation(
        self,
        connection: sqlite3.Connection,
        *,
        operation_id: str,
        operation_kind: str,
        input_fingerprint: str,
        owner_id: str,
        max_attempts: int,
        lease_seconds: int,
        now: float,
    ) -> ClaimDecision:
        token = self._token_factory()
        lease_expires_at = now + lease_seconds
        connection.execute(
            """
            INSERT INTO runtime_operations(
                operation_id, operation_kind, input_fingerprint, status, owner_id, owner_token,
                attempt_count, max_attempts, lease_seconds, lease_expires_at,
                created_at, updated_at, version
            ) VALUES (?, ?, ?, 'running', ?, ?, 1, ?, ?, ?, ?, ?, 1)
            """,
            (
                operation_id,
                operation_kind,
                input_fingerprint,
                owner_id,
                token,
                max_attempts,
                lease_seconds,
                lease_expires_at,
                now,
                now,
            ),
        )
        self._append_event(
            connection,
            operation_id=operation_id,
            event_type="operation_started",
            from_status=None,
            to_status=RuntimeStatus.RUNNING,
            attempt_number=1,
            owner_id=owner_id,
            detail={"max_attempts": max_attempts, "lease_expires_at": lease_expires_at},
            recorded_at=now,
        )
        claim = AttemptClaim(operation_id, owner_id, token, 1, lease_seconds, lease_expires_at)
        return ClaimDecision(
            ClaimOutcome.ACQUIRED,
            self._snapshot(self._operation_row_required(connection, operation_id)),
            claim,
        )

    def _claim_existing(
        self,
        connection: sqlite3.Connection,
        *,
        row: sqlite3.Row,
        owner_id: str,
        now: float,
    ) -> ClaimDecision:
        status = RuntimeStatus(row["status"])
        if status in {RuntimeStatus.COMPLETED, RuntimeStatus.QUARANTINED}:
            return ClaimDecision(ClaimOutcome(status.value), self._snapshot(row))
        if status is RuntimeStatus.RUNNING and row["lease_expires_at"] > now:
            return ClaimDecision(ClaimOutcome.BUSY, self._snapshot(row))
        if status is RuntimeStatus.RETRY_WAIT and row["next_retry_at"] > now:
            return ClaimDecision(ClaimOutcome.RETRY_WAIT, self._snapshot(row))
        if row["attempt_count"] >= row["max_attempts"]:
            connection.execute(
                """
                UPDATE runtime_operations
                SET status = 'quarantined', owner_id = NULL, owner_token = NULL,
                    lease_expires_at = NULL, next_retry_at = NULL, updated_at = ?, version = version + 1
                WHERE operation_id = ?
                """,
                (now, row["operation_id"]),
            )
            self._append_event(
                connection,
                operation_id=row["operation_id"],
                event_type="operation_quarantined",
                from_status=status,
                to_status=RuntimeStatus.QUARANTINED,
                attempt_number=row["attempt_count"],
                owner_id=None,
                detail={"reason": "attempt_limit_exhausted_during_recovery"},
                recorded_at=now,
            )
            updated = self._operation_row_required(connection, row["operation_id"])
            return ClaimDecision(ClaimOutcome.QUARANTINED, self._snapshot(updated))

        token = self._token_factory()
        attempt_number = row["attempt_count"] + 1
        lease_expires_at = now + row["lease_seconds"]
        event_type = "ownership_reclaimed" if status is RuntimeStatus.RUNNING else "retry_started"
        connection.execute(
            """
            UPDATE runtime_operations
            SET status = 'running', owner_id = ?, owner_token = ?, attempt_count = ?,
                lease_expires_at = ?, next_retry_at = NULL, updated_at = ?, version = version + 1
            WHERE operation_id = ?
            """,
            (owner_id, token, attempt_number, lease_expires_at, now, row["operation_id"]),
        )
        self._append_event(
            connection,
            operation_id=row["operation_id"],
            event_type=event_type,
            from_status=status,
            to_status=RuntimeStatus.RUNNING,
            attempt_number=attempt_number,
            owner_id=owner_id,
            detail={"lease_expires_at": lease_expires_at, "previous_owner_id": row["owner_id"]},
            recorded_at=now,
        )
        updated = self._operation_row_required(connection, row["operation_id"])
        claim = AttemptClaim(
            row["operation_id"], owner_id, token, attempt_number, row["lease_seconds"], lease_expires_at
        )
        return ClaimDecision(ClaimOutcome.ACQUIRED, self._snapshot(updated), claim)

    @staticmethod
    def _validate_identity(
        *,
        operation_id: str,
        operation_kind: str,
        input_fingerprint: str,
        owner_id: str,
        max_attempts: int,
        lease_seconds: int,
    ) -> None:
        for name, value in (
            ("operation_id", operation_id),
            ("operation_kind", operation_kind),
            ("input_fingerprint", input_fingerprint),
            ("owner_id", owner_id),
        ):
            if not value or value.strip() != value:
                raise ValueError(f"{name} must be a non-empty, trimmed string")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if lease_seconds < 1:
            raise ValueError("lease_seconds must be at least 1")

    @staticmethod
    def _assert_same_operation(
        row: sqlite3.Row,
        *,
        operation_kind: str,
        input_fingerprint: str,
        max_attempts: int,
        lease_seconds: int,
    ) -> None:
        actual = (
            row["operation_kind"],
            row["input_fingerprint"],
            row["max_attempts"],
            row["lease_seconds"],
        )
        expected = (operation_kind, input_fingerprint, max_attempts, lease_seconds)
        if actual != expected:
            raise OperationCollision(f"operation ID {row['operation_id']!r} was reused with different immutable inputs")

    def _require_live_owner(
        self,
        connection: sqlite3.Connection,
        claim: AttemptClaim,
        *,
        now: float,
    ) -> sqlite3.Row:
        row = self._operation_row_required(connection, claim.operation_id)
        self._assert_live_owner(row, claim, now=now)
        return row

    @staticmethod
    def _assert_live_owner(row: sqlite3.Row, claim: AttemptClaim, *, now: float) -> None:
        if row["status"] != RuntimeStatus.RUNNING:
            raise IllegalTransition(
                f"operation {claim.operation_id!r} is {row['status']}, not {RuntimeStatus.RUNNING.value}"
            )
        if row["owner_token"] != claim.token or row["owner_id"] != claim.owner_id:
            raise StaleOwnership(f"claim for operation {claim.operation_id!r} is no longer the owner")
        if row["lease_expires_at"] <= now:
            raise StaleOwnership(f"claim for operation {claim.operation_id!r} has expired")

    @staticmethod
    def _operation_row(connection: sqlite3.Connection, operation_id: str) -> sqlite3.Row | None:
        return connection.execute(
            "SELECT * FROM runtime_operations WHERE operation_id = ?",
            (operation_id,),
        ).fetchone()

    def _operation_row_required(self, connection: sqlite3.Connection, operation_id: str) -> sqlite3.Row:
        row = self._operation_row(connection, operation_id)
        if row is None:
            raise RuntimeRecoveryError(f"unknown operation {operation_id!r}")
        return row

    @staticmethod
    def _append_event(
        connection: sqlite3.Connection,
        *,
        operation_id: str,
        event_type: str,
        from_status: RuntimeStatus | None,
        to_status: RuntimeStatus,
        attempt_number: int,
        owner_id: str | None,
        detail: Mapping[str, Any],
        recorded_at: float,
    ) -> None:
        connection.execute(
            """
            INSERT INTO runtime_operation_events(
                operation_id, event_type, from_status, to_status, attempt_number,
                owner_id, detail_json, recorded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                operation_id,
                event_type,
                None if from_status is None else from_status.value,
                to_status.value,
                attempt_number,
                owner_id,
                _canonical_json(detail),
                recorded_at,
            ),
        )

    @staticmethod
    def _snapshot(row: sqlite3.Row) -> OperationSnapshot:
        return OperationSnapshot(
            operation_id=row["operation_id"],
            operation_kind=row["operation_kind"],
            input_fingerprint=row["input_fingerprint"],
            status=RuntimeStatus(row["status"]),
            owner_id=row["owner_id"],
            attempt_count=row["attempt_count"],
            max_attempts=row["max_attempts"],
            lease_seconds=row["lease_seconds"],
            lease_expires_at=row["lease_expires_at"],
            next_retry_at=row["next_retry_at"],
            checkpoint=_json_object(row["checkpoint_json"]),
            result=_json_object(row["result_json"]),
            last_error=row["last_error"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            completed_at=row["completed_at"],
            version=row["version"],
        )

    @staticmethod
    def _event(row: sqlite3.Row) -> OperationEvent:
        detail = _json_object(row["detail_json"])
        if detail is None:
            raise RuntimeRecoveryError("runtime recovery event detail is missing")
        return OperationEvent(
            event_id=row["event_id"],
            operation_id=row["operation_id"],
            event_type=row["event_type"],
            from_status=None if row["from_status"] is None else RuntimeStatus(row["from_status"]),
            to_status=RuntimeStatus(row["to_status"]),
            attempt_number=row["attempt_number"],
            owner_id=row["owner_id"],
            detail=detail,
            recorded_at=row["recorded_at"],
        )

    @staticmethod
    def _recovery_action(snapshot: OperationSnapshot, *, now: float) -> tuple[str, str]:
        if snapshot.status is RuntimeStatus.COMPLETED:
            return "return_result", "operation completed successfully"
        if snapshot.status is RuntimeStatus.QUARANTINED:
            return "manual_intervention", "operation is quarantined"
        if snapshot.status is RuntimeStatus.RETRY_WAIT:
            if snapshot.next_retry_at is not None and snapshot.next_retry_at <= now:
                return "claim_retry", "retry delay elapsed"
            return "wait", "retry delay has not elapsed"
        if snapshot.lease_expires_at is not None and snapshot.lease_expires_at <= now:
            return "reclaim_interrupted", "ownership lease expired"
        return "wait", "operation has an active owner"
