"""Atomic multi-dimensional capacity accounting for the Dispatcher Next spike.

The ledger is intentionally isolated from the live dispatcher and its
configuration. Each instance owns a caller-supplied SQLite database and applies
one immutable in-memory policy to every acquisition decision.
"""

from __future__ import annotations

import json
import math
import sqlite3
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final

SCHEMA_VERSION: Final[int] = 1
DEFAULT_BUSY_TIMEOUT_SECONDS: Final[float] = 30.0
_MAX_SQLITE_INTEGER: Final[int] = (1 << 63) - 1
_DIMENSION_PREFIXES: Final[tuple[str, ...]] = (
    "role",
    "provider",
    "model",
    "harness",
)
_OWNED_TABLES: Final[frozenset[str]] = frozenset(
    {
        "capacity_metadata",
        "capacity_lease_history",
        "capacity_leases",
        "capacity_audit_events",
    }
)

JsonObject = dict[str, Any]


class CapacityLedgerError(RuntimeError):
    """Base error for capacity-ledger failures."""


class InvalidCapacityPolicy(ValueError):
    """Raised when a capacity policy cannot be enforced safely."""


class InvalidCapacityRequest(ValueError):
    """Raised when an acquisition request is malformed."""


class DuplicateLeaseError(InvalidCapacityRequest):
    """Raised when a previously granted lease ID is reused."""


@dataclass(frozen=True, slots=True)
class CapacityRequest:
    """One immutable request that consumes all five capacity dimensions."""

    role: str
    provider: str
    model: str
    harness: str
    amount: int = 1

    def __post_init__(self) -> None:
        for field_name in _DIMENSION_PREFIXES:
            _validate_name(
                getattr(self, field_name),
                field_name=field_name,
                error_type=InvalidCapacityRequest,
            )
        _validate_positive_integer(
            self.amount,
            field_name="amount",
            error_type=InvalidCapacityRequest,
        )

    @property
    def dimension_keys(self) -> tuple[str, str, str, str, str]:
        """Return the exact policy keys consumed by this request."""

        return (
            "global",
            f"role:{self.role}",
            f"provider:{self.provider}",
            f"model:{self.model}",
            f"harness:{self.harness}",
        )

    def to_dict(self) -> JsonObject:
        """Return a deterministic JSON-friendly representation."""

        return {
            "role": self.role,
            "provider": self.provider,
            "model": self.model,
            "harness": self.harness,
            "amount": self.amount,
        }


@dataclass(frozen=True, slots=True)
class CapacityPolicy:
    """Immutable limits keyed by ``global`` or ``<dimension>:<value>``."""

    limits: Mapping[str, int]

    def __post_init__(self) -> None:
        if not isinstance(self.limits, Mapping):
            raise InvalidCapacityPolicy("limits must be a mapping")

        normalized: dict[str, int] = {}
        for key, limit in self.limits.items():
            if not isinstance(key, str):
                raise InvalidCapacityPolicy("capacity dimension keys must be strings")
            _validate_policy_key(key)
            _validate_limit(limit, key=key)
            normalized[key] = limit

        if "global" not in normalized:
            raise InvalidCapacityPolicy("a global capacity limit is required")
        object.__setattr__(
            self,
            "limits",
            MappingProxyType(dict(sorted(normalized.items()))),
        )

    def limit_for(self, dimension: str) -> int | None:
        """Return the configured limit for a canonical dimension key."""

        return self.limits.get(dimension)

    def to_dict(self) -> dict[str, int]:
        """Return a deterministic JSON-friendly copy of the limits."""

        return dict(self.limits)


class CapacityLedger:
    """SQLite-backed atomic capacity ledger with expiring leases."""

    def __init__(
        self,
        path: str | Path,
        policy: CapacityPolicy,
        *,
        clock: Callable[[], float] = time.time,
        busy_timeout_seconds: float = DEFAULT_BUSY_TIMEOUT_SECONDS,
    ) -> None:
        if not isinstance(policy, CapacityPolicy):
            raise InvalidCapacityPolicy("policy must be a CapacityPolicy")
        if not callable(clock):
            raise ValueError("clock must be callable")
        if (
            isinstance(busy_timeout_seconds, bool)
            or not isinstance(busy_timeout_seconds, (int, float))
            or not math.isfinite(float(busy_timeout_seconds))
            or busy_timeout_seconds <= 0
        ):
            raise ValueError("busy_timeout_seconds must be a positive finite number")

        database_path = Path(path)
        if str(database_path).strip() in {"", ":memory:"}:
            raise ValueError("path must name a durable SQLite database")
        if database_path.exists() and database_path.is_dir():
            raise ValueError(f"capacity database path is a directory: {database_path}")

        self.path = database_path.resolve()
        self.policy = policy
        self._clock = clock
        self._busy_timeout_seconds = float(busy_timeout_seconds)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def acquire(
        self,
        request: CapacityRequest,
        lease_id: str,
        ttl_seconds: float,
    ) -> JsonObject:
        """Atomically acquire every requested dimension or none of them."""

        if not isinstance(request, CapacityRequest):
            raise InvalidCapacityRequest("request must be a CapacityRequest")
        _validate_lease_id(lease_id)
        ttl = _validate_ttl(ttl_seconds)
        now = self._now()
        expires_at = now + ttl
        if not math.isfinite(expires_at):
            raise InvalidCapacityRequest("ttl_seconds produces a non-finite expiry")

        connection = self._connect()
        duplicate = False
        try:
            connection.execute("BEGIN IMMEDIATE")
            reaped = self._reap_expired_locked(connection, now=now)

            prior = connection.execute(
                "SELECT 1 FROM capacity_lease_history WHERE lease_id = ?",
                (lease_id,),
            ).fetchone()
            if prior is not None:
                self._append_event(
                    connection,
                    event_type="acquire_duplicate_rejected",
                    lease_id=lease_id,
                    detail={"request": request.to_dict()},
                    recorded_at=now,
                )
                connection.commit()
                duplicate = True
            else:
                result = self._acquire_locked(
                    connection,
                    request=request,
                    lease_id=lease_id,
                    now=now,
                    expires_at=expires_at,
                    reaped_lease_ids=reaped,
                )
                connection.commit()
                return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

        if duplicate:
            raise DuplicateLeaseError(f"lease_id {lease_id!r} has already been used")
        raise CapacityLedgerError("duplicate lease handling did not produce a decision")

    def release(self, lease_id: str) -> JsonObject:
        """Release an active lease, returning an idempotent no-op otherwise."""

        _validate_lease_id(lease_id)
        now = self._now()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            reaped = self._reap_expired_locked(connection, now=now)
            row = connection.execute(
                """
                SELECT lease_id, role, provider, model, harness, amount,
                       acquired_at, expires_at
                FROM capacity_leases
                WHERE lease_id = ?
                """,
                (lease_id,),
            ).fetchone()
            if row is None:
                known = connection.execute(
                    "SELECT 1 FROM capacity_lease_history WHERE lease_id = ?",
                    (lease_id,),
                ).fetchone()
                result = {
                    "schema_version": SCHEMA_VERSION,
                    "released": False,
                    "lease_id": lease_id,
                    "reason": "already_inactive" if known is not None else "not_found",
                    "reaped_lease_ids": reaped,
                }
            else:
                connection.execute(
                    "DELETE FROM capacity_leases WHERE lease_id = ?",
                    (lease_id,),
                )
                event_id = self._append_event(
                    connection,
                    event_type="lease_released",
                    lease_id=lease_id,
                    detail={"lease": self._lease_dict(row)},
                    recorded_at=now,
                )
                result = {
                    "schema_version": SCHEMA_VERSION,
                    "released": True,
                    "lease_id": lease_id,
                    "reason": "released",
                    "event_id": event_id,
                    "reaped_lease_ids": reaped,
                }
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def recover_expired(self) -> JsonObject:
        """Reap all expired active leases and record durable audit events."""

        now = self._now()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            reaped = self._reap_expired_locked(connection, now=now)
            snapshot = self._snapshot_locked(connection, observed_at=now)
            connection.commit()
            return {
                "schema_version": SCHEMA_VERSION,
                "recovered_count": len(reaped),
                "recovered_lease_ids": reaped,
                "snapshot": snapshot,
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def snapshot(self) -> JsonObject:
        """Return current counts and leases after atomically reaping expiry."""

        now = self._now()
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            reaped = self._reap_expired_locked(connection, now=now)
            result = self._snapshot_locked(connection, observed_at=now)
            result["reaped_lease_ids"] = reaped
            connection.commit()
            return result
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def current_counts(self) -> dict[str, int]:
        """Return only the current per-dimension counts."""

        snapshot = self.snapshot()
        return dict(snapshot["counts"])

    def audit_events(
        self,
        *,
        after_event_id: int = 0,
        limit: int | None = None,
    ) -> list[JsonObject]:
        """Read append-only audit events in deterministic event order."""

        if isinstance(after_event_id, bool) or not isinstance(after_event_id, int):
            raise ValueError("after_event_id must be a non-negative integer")
        if after_event_id < 0:
            raise ValueError("after_event_id must be a non-negative integer")
        if limit is not None:
            _validate_positive_integer(limit, field_name="limit", error_type=ValueError)

        query = """
            SELECT event_id, event_type, lease_id, detail_json, recorded_at
            FROM capacity_audit_events
            WHERE event_id > ?
            ORDER BY event_id
        """
        parameters: list[int] = [after_event_id]
        if limit is not None:
            query += " LIMIT ?"
            parameters.append(limit)

        connection = self._connect()
        try:
            rows = connection.execute(query, parameters).fetchall()
        finally:
            connection.close()

        events: list[JsonObject] = []
        for row in rows:
            detail = json.loads(str(row["detail_json"]))
            if not isinstance(detail, dict):
                raise CapacityLedgerError(f"audit event {row['event_id']} has invalid detail JSON")
            events.append(
                {
                    "event_id": int(row["event_id"]),
                    "event_type": str(row["event_type"]),
                    "lease_id": row["lease_id"],
                    "detail": detail,
                    "recorded_at": float(row["recorded_at"]),
                }
            )
        return events

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=self._busy_timeout_seconds,
            isolation_level=None,
        )
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(f"PRAGMA busy_timeout = {int(self._busy_timeout_seconds * 1000)}")
            journal_mode = connection.execute("PRAGMA journal_mode").fetchone()
            if journal_mode is None or str(journal_mode[0]).lower() != "wal":
                raise CapacityLedgerError("capacity database is not in WAL mode")
            return connection
        except Exception:
            connection.close()
            raise

    def _initialize(self) -> None:
        connection = sqlite3.connect(
            self.path,
            timeout=self._busy_timeout_seconds,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        try:
            connection.execute(f"PRAGMA busy_timeout = {int(self._busy_timeout_seconds * 1000)}")
            existing_tables = {
                str(row["name"])
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    """
                ).fetchall()
            }
            if existing_tables and not existing_tables.issubset(_OWNED_TABLES):
                foreign_tables = sorted(existing_tables - _OWNED_TABLES)
                raise CapacityLedgerError("capacity database contains non-ledger tables: " + ", ".join(foreign_tables))

            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute("PRAGMA synchronous = FULL")
            connection.execute("BEGIN IMMEDIATE")
            schema_statements = (
                """
                CREATE TABLE IF NOT EXISTS capacity_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS capacity_lease_history (
                    lease_id TEXT PRIMARY KEY,
                    request_json TEXT NOT NULL,
                    first_acquired_at REAL NOT NULL
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS capacity_leases (
                    lease_id TEXT PRIMARY KEY
                        REFERENCES capacity_lease_history(lease_id),
                    role TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    harness TEXT NOT NULL,
                    amount INTEGER NOT NULL CHECK (amount > 0),
                    acquired_at REAL NOT NULL,
                    expires_at REAL NOT NULL CHECK (expires_at > acquired_at)
                )
                """,
                """
                CREATE INDEX IF NOT EXISTS capacity_leases_expiry
                    ON capacity_leases(expires_at, lease_id)
                """,
                """
                CREATE TABLE IF NOT EXISTS capacity_audit_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    lease_id TEXT,
                    detail_json TEXT NOT NULL,
                    recorded_at REAL NOT NULL
                )
                """,
                """
                CREATE INDEX IF NOT EXISTS capacity_audit_events_lease
                    ON capacity_audit_events(lease_id, event_id)
                """,
            )
            for statement in schema_statements:
                connection.execute(statement)
            row = connection.execute("SELECT value FROM capacity_metadata WHERE key = 'schema_version'").fetchone()
            if row is None:
                connection.execute(
                    """
                    INSERT INTO capacity_metadata(key, value)
                    VALUES ('schema_version', ?)
                    """,
                    (str(SCHEMA_VERSION),),
                )
            elif str(row["value"]) != str(SCHEMA_VERSION):
                raise CapacityLedgerError(
                    f"unsupported capacity ledger schema version {row['value']!r}; expected {SCHEMA_VERSION}"
                )

            policy_json = _canonical_json(self.policy.to_dict())
            policy_row = connection.execute("SELECT value FROM capacity_metadata WHERE key = 'policy_json'").fetchone()
            if policy_row is None:
                connection.execute(
                    """
                    INSERT INTO capacity_metadata(key, value)
                    VALUES ('policy_json', ?)
                    """,
                    (policy_json,),
                )
            elif str(policy_row["value"]) != policy_json:
                raise InvalidCapacityPolicy("capacity database was initialized with a different policy")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _acquire_locked(
        self,
        connection: sqlite3.Connection,
        *,
        request: CapacityRequest,
        lease_id: str,
        now: float,
        expires_at: float,
        reaped_lease_ids: list[str],
    ) -> JsonObject:
        counts = self._counts_locked(connection)
        blockers: list[JsonObject] = []
        checked: list[JsonObject] = []

        for dimension in request.dimension_keys:
            current = counts.get(dimension, 0)
            limit = self.policy.limit_for(dimension)
            projected = current + request.amount
            check = {
                "dimension": dimension,
                "current": current,
                "requested": request.amount,
                "projected": projected,
                "limit": limit,
            }
            checked.append(check)
            if limit is None:
                blockers.append({**check, "reason": "missing_policy_limit"})
            elif projected > limit:
                blockers.append({**check, "reason": "capacity_exceeded"})

        if blockers:
            reason = (
                "missing_policy_limits"
                if any(item["reason"] == "missing_policy_limit" for item in blockers)
                else "capacity_exceeded"
            )
            event_id = self._append_event(
                connection,
                event_type="acquire_denied",
                lease_id=lease_id,
                detail={
                    "reason": reason,
                    "request": request.to_dict(),
                    "checked_dimensions": checked,
                    "blockers": blockers,
                },
                recorded_at=now,
            )
            return {
                "schema_version": SCHEMA_VERSION,
                "acquired": False,
                "lease_id": lease_id,
                "reason": reason,
                "request": request.to_dict(),
                "checked_dimensions": checked,
                "blockers": blockers,
                "event_id": event_id,
                "reaped_lease_ids": reaped_lease_ids,
            }

        request_json = _canonical_json(request.to_dict())
        connection.execute(
            """
            INSERT INTO capacity_lease_history(
                lease_id, request_json, first_acquired_at
            )
            VALUES (?, ?, ?)
            """,
            (lease_id, request_json, now),
        )
        connection.execute(
            """
            INSERT INTO capacity_leases(
                lease_id, role, provider, model, harness, amount,
                acquired_at, expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                lease_id,
                request.role,
                request.provider,
                request.model,
                request.harness,
                request.amount,
                now,
                expires_at,
            ),
        )
        event_id = self._append_event(
            connection,
            event_type="lease_acquired",
            lease_id=lease_id,
            detail={
                "request": request.to_dict(),
                "expires_at": expires_at,
                "checked_dimensions": checked,
            },
            recorded_at=now,
        )
        return {
            "schema_version": SCHEMA_VERSION,
            "acquired": True,
            "lease_id": lease_id,
            "reason": "acquired",
            "request": request.to_dict(),
            "acquired_at": now,
            "expires_at": expires_at,
            "checked_dimensions": checked,
            "blockers": [],
            "event_id": event_id,
            "reaped_lease_ids": reaped_lease_ids,
        }

    def _reap_expired_locked(
        self,
        connection: sqlite3.Connection,
        *,
        now: float,
    ) -> list[str]:
        rows = connection.execute(
            """
            SELECT lease_id, role, provider, model, harness, amount,
                   acquired_at, expires_at
            FROM capacity_leases
            WHERE expires_at <= ?
            ORDER BY lease_id
            """,
            (now,),
        ).fetchall()
        for row in rows:
            connection.execute(
                "DELETE FROM capacity_leases WHERE lease_id = ?",
                (row["lease_id"],),
            )
            self._append_event(
                connection,
                event_type="lease_expired",
                lease_id=str(row["lease_id"]),
                detail={"lease": self._lease_dict(row)},
                recorded_at=now,
            )
        return [str(row["lease_id"]) for row in rows]

    def _counts_locked(self, connection: sqlite3.Connection) -> dict[str, int]:
        rows = connection.execute(
            """
            SELECT role, provider, model, harness, amount
            FROM capacity_leases
            ORDER BY lease_id
            """
        ).fetchall()
        counts = {dimension: 0 for dimension in self.policy.limits}
        for row in rows:
            amount = int(row["amount"])
            dimensions = (
                "global",
                f"role:{row['role']}",
                f"provider:{row['provider']}",
                f"model:{row['model']}",
                f"harness:{row['harness']}",
            )
            for dimension in dimensions:
                counts[dimension] = counts.get(dimension, 0) + amount
        return dict(sorted(counts.items()))

    def _snapshot_locked(
        self,
        connection: sqlite3.Connection,
        *,
        observed_at: float,
    ) -> JsonObject:
        rows = connection.execute(
            """
            SELECT lease_id, role, provider, model, harness, amount,
                   acquired_at, expires_at
            FROM capacity_leases
            ORDER BY lease_id
            """
        ).fetchall()
        return {
            "schema_version": SCHEMA_VERSION,
            "observed_at": observed_at,
            "policy": self.policy.to_dict(),
            "counts": self._counts_locked(connection),
            "active_lease_count": len(rows),
            "active_leases": [self._lease_dict(row) for row in rows],
        }

    def _append_event(
        self,
        connection: sqlite3.Connection,
        *,
        event_type: str,
        lease_id: str | None,
        detail: Mapping[str, Any],
        recorded_at: float,
    ) -> int:
        cursor = connection.execute(
            """
            INSERT INTO capacity_audit_events(
                event_type, lease_id, detail_json, recorded_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (event_type, lease_id, _canonical_json(detail), recorded_at),
        )
        if cursor.lastrowid is None:
            raise CapacityLedgerError("capacity audit event did not receive an ID")
        return int(cursor.lastrowid)

    @staticmethod
    def _lease_dict(row: sqlite3.Row) -> JsonObject:
        return {
            "lease_id": str(row["lease_id"]),
            "request": {
                "role": str(row["role"]),
                "provider": str(row["provider"]),
                "model": str(row["model"]),
                "harness": str(row["harness"]),
                "amount": int(row["amount"]),
            },
            "acquired_at": float(row["acquired_at"]),
            "expires_at": float(row["expires_at"]),
        }

    def _now(self) -> float:
        now = self._clock()
        if isinstance(now, bool) or not isinstance(now, (int, float)):
            raise CapacityLedgerError("clock must return a finite number")
        normalized = float(now)
        if not math.isfinite(normalized):
            raise CapacityLedgerError("clock must return a finite number")
        return normalized


def _validate_policy_key(key: str) -> None:
    if key != key.strip() or "\x00" in key:
        raise InvalidCapacityPolicy(f"invalid capacity dimension key {key!r}")
    if key == "global":
        return
    prefix, separator, value = key.partition(":")
    if separator != ":" or prefix not in _DIMENSION_PREFIXES or not value or value != value.strip():
        raise InvalidCapacityPolicy(f"invalid capacity dimension key {key!r}")


def _validate_limit(limit: object, *, key: str) -> None:
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise InvalidCapacityPolicy(f"limit for {key!r} must be an integer")
    if limit < 0 or limit > _MAX_SQLITE_INTEGER:
        raise InvalidCapacityPolicy(f"limit for {key!r} must be between 0 and {_MAX_SQLITE_INTEGER}")


def _validate_name(
    value: object,
    *,
    field_name: str,
    error_type: type[ValueError],
) -> None:
    if not isinstance(value, str):
        raise error_type(f"{field_name} must be a string")
    if not value or value != value.strip() or "\x00" in value:
        raise error_type(f"{field_name} must be a non-empty canonical string")


def _validate_positive_integer(
    value: object,
    *,
    field_name: str,
    error_type: type[ValueError],
) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise error_type(f"{field_name} must be a positive integer")
    if value < 1 or value > _MAX_SQLITE_INTEGER:
        raise error_type(f"{field_name} must be between 1 and {_MAX_SQLITE_INTEGER}")


def _validate_lease_id(lease_id: object) -> None:
    _validate_name(
        lease_id,
        field_name="lease_id",
        error_type=InvalidCapacityRequest,
    )
    if len(lease_id) > 512:
        raise InvalidCapacityRequest("lease_id must not exceed 512 characters")


def _validate_ttl(ttl_seconds: object) -> float:
    if (
        isinstance(ttl_seconds, bool)
        or not isinstance(ttl_seconds, (int, float))
        or not math.isfinite(float(ttl_seconds))
        or ttl_seconds <= 0
    ):
        raise InvalidCapacityRequest("ttl_seconds must be a positive finite number")
    return float(ttl_seconds)


def _canonical_json(value: Mapping[str, Any]) -> str:
    try:
        return json.dumps(
            dict(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise CapacityLedgerError("audit detail is not JSON-serializable") from exc
