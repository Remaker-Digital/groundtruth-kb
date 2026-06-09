#!/usr/bin/env python3
"""Agent-scoped GT-KB service client (Phase 4 baseline slice).

This module is the Phase 4 single-operation scoped-service boundary for
Agent Red (GTKB-ISOLATION-012). It exposes one read operation,
``dashboard.summary.read``, and owns the raw ``groundtruth.db`` connection
for that operation. Callers must go through the client rather than opening
their own SQLite connections on the summary path.

Design constraints for this slice:

- Only the operations declared in ``[scoped_service].allowed_read_operations``
  in the root ``groundtruth.toml`` are accepted. The first slice declares a
  single operation: ``dashboard.summary.read``.
- Any mutating ("write"/"request"/"emit"/"refresh") operation class is
  rejected at the client boundary regardless of configuration.
- Subject labels other than the configured default subject are rejected.
- Project-root confinement is enforced: the effective project root resolved
  against the TOML must match the caller-supplied project root.
- Responses carry source/freshness metadata so consumers never treat the
  read model as canonical state.

Deferred to later Phase 4 sub-slices: ``dashboard.history.read``,
``dashboard.refresh.request``, DA/MemBase mutation, bridge write/read
authority, deployment/release request queues, hosted service or auth token
issuance, dashboard control-plane registry, overlay storage, and promotion
behavior.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tomllib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE_NAME = "groundtruth.toml"
CONFIG_SECTION = "scoped_service"

DASHBOARD_SUMMARY_READ = "dashboard.summary.read"
SUPPORTED_READ_OPERATIONS: frozenset[str] = frozenset({DASHBOARD_SUMMARY_READ})

MUTATING_OPERATION_MARKERS: tuple[str, ...] = (
    ".write",
    ".upsert",
    ".append",
    ".emit",
    ".request",
    ".refresh",
    ".delete",
    ".mutate",
    ".promote",
    ".schedule",
)

_DASHBOARD_SUMMARY_TABLES: tuple[str, ...] = (
    "current_specifications",
    "current_work_items",
    "current_tests",
    "current_deliberations",
)


class ScopedServiceConfigError(RuntimeError):
    """Raised when the scoped service configuration is malformed or missing."""


class ScopedOperationError(RuntimeError):
    """Raised when the client is asked for an operation it must refuse."""


@dataclass(frozen=True)
class ScopedServiceConfig:
    """Parsed ``[scoped_service]`` configuration from ``groundtruth.toml``."""

    default_subject: str
    application_id: str
    project_root: Path
    allowed_read_operations: tuple[str, ...]
    runtime_root: Path
    dashboard_db: Path
    allowed_request_operations: tuple[str, ...] = field(default_factory=tuple)
    source_path: Path | None = None


def load_scoped_service_config(project_root: Path | None = None) -> ScopedServiceConfig:
    """Load and validate the ``[scoped_service]`` section of ``groundtruth.toml``."""

    resolved_root = (project_root or DEFAULT_PROJECT_ROOT).resolve()
    config_path = resolved_root / CONFIG_FILE_NAME
    if not config_path.is_file():
        raise ScopedServiceConfigError(f"scoped-service config file not found at {config_path}")

    with config_path.open("rb") as handle:
        data = tomllib.load(handle)

    section = data.get(CONFIG_SECTION)
    if not isinstance(section, dict):
        raise ScopedServiceConfigError(f"[{CONFIG_SECTION}] section missing or not a table in {config_path}")

    missing: list[str] = []
    for required in (
        "default_subject",
        "application_id",
        "project_root",
        "allowed_read_operations",
        "runtime_root",
    ):
        if required not in section:
            missing.append(required)
    if missing:
        raise ScopedServiceConfigError(f"[{CONFIG_SECTION}] missing required fields: {', '.join(missing)}")

    default_subject = str(section["default_subject"]).strip()
    if not default_subject:
        raise ScopedServiceConfigError("default_subject must be a non-empty string")

    application_id = str(section["application_id"]).strip()
    if not application_id:
        raise ScopedServiceConfigError("application_id must be a non-empty string")

    config_project_root_raw = str(section["project_root"]).strip()
    if not config_project_root_raw:
        raise ScopedServiceConfigError("project_root must be a non-empty string")
    effective_root = (resolved_root / config_project_root_raw).resolve()

    allowed_read = section["allowed_read_operations"]
    if not isinstance(allowed_read, list) or not allowed_read:
        raise ScopedServiceConfigError("allowed_read_operations must be a non-empty list of operation names")
    normalized_read = tuple(str(op).strip() for op in allowed_read)
    for op in normalized_read:
        if not op:
            raise ScopedServiceConfigError("allowed_read_operations entries must be non-empty")
        if _is_mutating_operation_name(op):
            raise ScopedServiceConfigError(
                f"operation {op!r} is mutating/request-class and cannot appear in allowed_read_operations"
            )
        if op not in SUPPORTED_READ_OPERATIONS:
            raise ScopedServiceConfigError(
                f"operation {op!r} is not supported in this slice (supported: {sorted(SUPPORTED_READ_OPERATIONS)})"
            )

    allowed_request_raw = section.get("allowed_request_operations", [])
    if not isinstance(allowed_request_raw, list):
        raise ScopedServiceConfigError("allowed_request_operations must be a list when present")
    allowed_request = tuple(str(op).strip() for op in allowed_request_raw)
    if allowed_request:
        raise ScopedServiceConfigError("allowed_request_operations must be empty in the Phase 4 baseline slice")

    runtime_root_raw = str(section["runtime_root"]).strip()
    if not runtime_root_raw:
        raise ScopedServiceConfigError("runtime_root must be a non-empty string")
    runtime_root = (effective_root / runtime_root_raw).resolve()

    dashboard_db_raw = str(section.get("dashboard_db", "")).strip()
    dashboard_db = (
        (effective_root / dashboard_db_raw).resolve()
        if dashboard_db_raw
        else effective_root / "memory" / "gtkb-dashboard.sqlite"
    )

    return ScopedServiceConfig(
        default_subject=default_subject,
        application_id=application_id,
        project_root=effective_root,
        allowed_read_operations=normalized_read,
        runtime_root=runtime_root,
        dashboard_db=dashboard_db,
        allowed_request_operations=allowed_request,
        source_path=config_path,
    )


def _is_mutating_operation_name(operation: str) -> bool:
    lowered = operation.lower()
    return any(marker in lowered for marker in MUTATING_OPERATION_MARKERS)


class GtkbScopedClient:
    """Narrow typed client for the Phase 4 scoped-service boundary."""

    def __init__(self, config: ScopedServiceConfig) -> None:
        self._config = config

    @classmethod
    def from_project_root(cls, project_root: Path | None = None) -> "GtkbScopedClient":
        config = load_scoped_service_config(project_root)
        return cls(config)

    @property
    def config(self) -> ScopedServiceConfig:
        return self._config

    def invoke(
        self,
        operation: str,
        *,
        subject: str | None = None,
        project_root: Path | None = None,
    ) -> dict[str, Any]:
        """Invoke a scoped operation, fail-closed on unsupported inputs."""

        normalized = operation.strip()
        if _is_mutating_operation_name(normalized):
            raise ScopedOperationError(
                f"operation {normalized!r} is mutating/request-class and is not allowed on the read client"
            )
        if normalized not in self._config.allowed_read_operations:
            raise ScopedOperationError(
                f"operation {normalized!r} is not allowed in this slice "
                f"(allowed: {list(self._config.allowed_read_operations)})"
            )

        requested_subject = (subject or self._config.default_subject).strip()
        if requested_subject != self._config.default_subject:
            raise ScopedOperationError(
                f"subject {requested_subject!r} not allowed; this slice only "
                f"serves subject {self._config.default_subject!r}"
            )

        if project_root is not None:
            requested_root = Path(project_root).resolve()
            if requested_root != self._config.project_root:
                raise ScopedOperationError(
                    f"project_root {requested_root} does not match configured "
                    f"scoped-service root {self._config.project_root}"
                )

        if normalized == DASHBOARD_SUMMARY_READ:
            return self._dashboard_summary_read()

        # Defensive: allowlist already rejected unknown ops above.
        raise ScopedOperationError(f"operation {normalized!r} has no handler in this slice")

    def _dashboard_summary_read(self) -> dict[str, Any]:
        db_path = self._config.project_root / "groundtruth.db"
        envelope: dict[str, Any] = {
            "available": False,
            "subject": self._config.default_subject,
            "application_id": self._config.application_id,
            "operation": DASHBOARD_SUMMARY_READ,
            "project_root": str(self._config.project_root),
            "source": "groundtruth.db",
            "source_path": str(db_path),
            "freshness": {
                "retrieved_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                "mtime_utc": None,
            },
            "payload": None,
            "error": None,
        }

        if not db_path.is_file():
            envelope["error"] = f"missing {db_path.name}"
            return envelope

        stat = db_path.stat()
        envelope["freshness"]["mtime_utc"] = (
            datetime.fromtimestamp(stat.st_mtime, tz=UTC).isoformat().replace("+00:00", "Z")
        )
        envelope["freshness"]["size_bytes"] = int(stat.st_size)

        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        try:
            rows_by_table: dict[str, list[dict[str, Any]]] = {}
            for table in _DASHBOARD_SUMMARY_TABLES:
                rows_by_table[table] = [dict(row) for row in connection.execute(f"SELECT * FROM {table}")]
            test_procedures_count = int(connection.execute("SELECT COUNT(*) FROM test_procedures").fetchone()[0])
        finally:
            connection.close()

        envelope["available"] = True
        envelope["payload"] = {
            "specifications": rows_by_table["current_specifications"],
            "work_items": rows_by_table["current_work_items"],
            "tests": rows_by_table["current_tests"],
            "deliberations": rows_by_table["current_deliberations"],
            "test_procedures_count": test_procedures_count,
        }
        return envelope


def _cli_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="gtkb_scoped_client",
        description="Agent-scoped GT-KB service client (Phase 4 baseline).",
    )
    parser.add_argument("operation", help="Scoped operation name, e.g. dashboard.summary.read")
    parser.add_argument("--subject", default=None, help="Override the default subject (normally unnecessary)")
    parser.add_argument(
        "--project-root",
        default=None,
        help="Path to the Agent Red project root (defaults to the client's configured root)",
    )
    parser.add_argument("--json", action="store_true", help="Emit the full response envelope as JSON")
    args = parser.parse_args(argv)

    project_root = Path(args.project_root).resolve() if args.project_root else None
    try:
        client = GtkbScopedClient.from_project_root(project_root)
        response = client.invoke(args.operation, subject=args.subject, project_root=project_root)
    except (ScopedServiceConfigError, ScopedOperationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        # Payload includes full row dicts; those are large. Trim to counts for the CLI default-safe JSON
        # unless the caller explicitly asks for payload via the subcommand (future slice).
        trimmed = dict(response)
        payload = trimmed.get("payload")
        if isinstance(payload, dict):
            trimmed["payload"] = {
                "specification_count": len(payload.get("specifications", [])),
                "work_item_count": len(payload.get("work_items", [])),
                "test_count": len(payload.get("tests", [])),
                "deliberation_count": len(payload.get("deliberations", [])),
                "test_procedures_count": int(payload.get("test_procedures_count", 0)),
            }
        json.dump(trimmed, sys.stdout, indent=2, default=str)
        sys.stdout.write("\n")
    else:
        print(f"operation={response.get('operation')} available={response.get('available')}")
        if response.get("error"):
            print(f"error={response['error']}")
        freshness = response.get("freshness", {})
        print(f"retrieved_at={freshness.get('retrieved_at')} mtime_utc={freshness.get('mtime_utc')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli_main(sys.argv[1:]))
