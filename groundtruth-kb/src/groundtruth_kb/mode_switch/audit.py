"""Transaction-record audit-trail writer.

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`` acceptance criterion #3:
"The component records enough transaction evidence to audit who requested
the switch, what changed, when it was requested, and when it becomes
effective."

Records are written to ``.gtkb-state/mode-switches/<timestamp>-<uuid>.json``
for immediate-apply transactions. The audit directory is runtime-created
(no tracked placeholder files); ``.gtkb-state/`` is ignored by
``.gitignore`` per the runtime-state policy.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

AUDIT_DIR_NAME = "mode-switches"


def _audit_dir(project_root: Path) -> Path:
    return project_root / ".gtkb-state" / AUDIT_DIR_NAME


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


def write_transaction_record(
    project_root: Path,
    *,
    harness_id: str,
    requested_role: str,
    previous_role_set: list[str] | None,
    new_role_set: list[str],
    derived_topology: str,
    change_reason: str,
    applied_at: datetime | None = None,
    deferred: bool = False,
) -> Path:
    """Write an audit-trail record for an applied or deferred mode-switch.

    Returns the path to the JSON record. The audit directory is created if
    missing. Filename pattern: ``<timestamp>-<uuid8>.json``.
    """
    directory = _audit_dir(project_root)
    directory.mkdir(parents=True, exist_ok=True)
    when = applied_at if applied_at is not None else datetime.now(UTC)
    record_id = uuid.uuid4().hex[:8]
    filename = f"{_timestamp()}-{record_id}.json"
    record_path = directory / filename
    payload: dict[str, Any] = {
        "schema_version": 1,
        "record_id": record_id,
        "harness_id": harness_id,
        "requested_role": requested_role,
        "previous_role_set": previous_role_set,
        "new_role_set": new_role_set,
        "derived_topology": derived_topology,
        "change_reason": change_reason,
        "requested_at": when.isoformat().replace("+00:00", "Z"),
        "effective_at": when.isoformat().replace("+00:00", "Z"),
        "deferred": deferred,
    }
    record_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return record_path


def write_bridge_substrate_record(
    project_root: Path,
    *,
    harness_id: str,
    previous_substrate: str | None,
    new_substrate: str,
    change_reason: str,
    applied_at: datetime | None = None,
    deferred: bool = False,
) -> Path:
    """Write an audit-trail record for an applied or deferred bridge-substrate switch.

    Returns the path to the JSON record. Axis is 'bridge_substrate'.
    """
    directory = _audit_dir(project_root)
    directory.mkdir(parents=True, exist_ok=True)
    when = applied_at if applied_at is not None else datetime.now(UTC)
    record_id = uuid.uuid4().hex[:8]
    filename = f"{_timestamp()}-{record_id}.json"
    record_path = directory / filename
    payload: dict[str, Any] = {
        "schema_version": 1,
        "record_id": record_id,
        "axis": "bridge_substrate",
        "harness_id": harness_id,
        "previous_substrate": previous_substrate,
        "new_substrate": new_substrate,
        "change_reason": change_reason,
        "requested_at": when.isoformat().replace("+00:00", "Z"),
        "effective_at": when.isoformat().replace("+00:00", "Z"),
        "deferred": deferred,
    }
    record_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return record_path
