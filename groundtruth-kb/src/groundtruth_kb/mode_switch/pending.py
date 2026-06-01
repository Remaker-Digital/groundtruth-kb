"""Pending-transaction queue for next-session-effective mode switches.

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`` acceptance criterion #6:
"The implementation explicitly supports next-session effectiveness;
immediate mid-session state replacement is optional unless separately
specified."

Pending files live at ``.gtkb-state/mode-switches/pending/<timestamp>-<uuid>.json``.
On apply, successful entries move to ``.gtkb-state/mode-switches/applied/``;
failed entries remain in ``pending/`` with the error logged so the owner
can inspect.

The shared ``apply_pending(project_root)`` entry point is invoked from
multiple SessionStart-adjacent call sites BEFORE durable role resolution
(both SessionStart dispatch hooks, the cross-harness trigger, and
``scripts/session_self_initialization.py``) so that a deferred transaction
takes effect for the next session it can observe, regardless of which path
that session enters through. Each call site wraps the invocation
fail-soft.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights
reserved.
"""

from __future__ import annotations

import json
import shutil
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from groundtruth_kb.mode_switch.transaction import (
    TransactionResult,
    TransactionValidationError,
    apply_role_switch,
)

PENDING_SUBDIR = "pending"
APPLIED_SUBDIR = "applied"
MODE_SWITCHES_DIR = "mode-switches"


def _pending_dir(project_root: Path) -> Path:
    return project_root / ".gtkb-state" / MODE_SWITCHES_DIR / PENDING_SUBDIR


def _applied_dir(project_root: Path) -> Path:
    return project_root / ".gtkb-state" / MODE_SWITCHES_DIR / APPLIED_SUBDIR


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")


@dataclass(frozen=True)
class PendingTransaction:
    """A pending mode-switch transaction read from the queue."""

    path: Path
    harness_id_or_name: str
    role: str | None
    change_reason: str
    scheduled_at: datetime
    axis: str = "role"
    substrate: str | None = None


@dataclass(frozen=True)
class ApplyResult:
    """Result of applying a single pending transaction."""

    pending_path: Path
    applied: bool
    error: str | None = None
    applied_path: Path | None = None
    transaction_result: TransactionResult | None = None


def defer_role_switch(
    project_root: Path,
    harness_id_or_name: str,
    role: str,
    *,
    change_reason: str,
    scheduled_at: datetime | None = None,
) -> Path:
    """Write a pending mode-switch transaction to the queue.

    Returns the path to the new pending JSON file. The pending directory is
    runtime-created.
    """
    directory = _pending_dir(project_root)
    directory.mkdir(parents=True, exist_ok=True)
    when = scheduled_at if scheduled_at is not None else datetime.now(UTC)
    record_id = uuid.uuid4().hex[:8]
    filename = f"{_timestamp()}-{record_id}.json"
    target = directory / filename
    payload = {
        "schema_version": 1,
        "record_id": record_id,
        "harness_id_or_name": harness_id_or_name,
        "role": role,
        "change_reason": change_reason,
        "scheduled_at": when.isoformat().replace("+00:00", "Z"),
    }
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


def list_pending(project_root: Path) -> list[PendingTransaction]:
    """Return all pending transactions in chronological filename order."""
    directory = _pending_dir(project_root)
    if not directory.is_dir():
        return []
    result: list[PendingTransaction] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        scheduled_raw = str(data.get("scheduled_at", ""))
        try:
            scheduled_at = datetime.fromisoformat(scheduled_raw.replace("Z", "+00:00"))
        except ValueError:
            scheduled_at = datetime.now(UTC)
        axis = str(data.get("axis", "role"))
        result.append(
            PendingTransaction(
                path=path,
                harness_id_or_name=str(data.get("harness_id_or_name", "")),
                role=data.get("role"),
                change_reason=str(data.get("change_reason", "")),
                scheduled_at=scheduled_at,
                axis=axis,
                substrate=data.get("substrate"),
            )
        )
    return result


def apply_pending(project_root: Path) -> list[ApplyResult]:
    """Apply every pending transaction in chronological order.

    Each pending file is applied independently. Successful applications
    move the file to ``.gtkb-state/mode-switches/applied/``; failed
    applications leave the file in ``pending/`` with the error returned in
    the corresponding ``ApplyResult.error``.

    This function is idempotent against an empty queue (returns ``[]``).
    """
    pending = list_pending(project_root)
    if not pending:
        return []
    applied_root = _applied_dir(project_root)
    applied_root.mkdir(parents=True, exist_ok=True)
    results: list[ApplyResult] = []
    for entry in pending:
        try:
            if entry.axis == "bridge_substrate":
                from groundtruth_kb.mode_switch.bridge_substrate import apply_bridge_substrate_switch

                if not entry.substrate:
                    raise TransactionValidationError(
                        "Missing 'substrate' in bridge_substrate pending transaction",
                        axis="bridge_substrate",
                    )
                apply_bridge_substrate_switch(
                    project_root,
                    entry.substrate,
                    change_reason=entry.change_reason,
                )
                tx_result = None
            else:
                if not entry.role:
                    raise TransactionValidationError(
                        "Missing 'role' in role pending transaction",
                        axis="role",
                    )
                tx_result = apply_role_switch(
                    project_root,
                    entry.harness_id_or_name,
                    entry.role,
                    change_reason=entry.change_reason,
                )
        except TransactionValidationError as exc:
            # Write a failed record to .gtkb-state/mode-switches/failed/
            try:
                failed_dir = project_root / ".gtkb-state" / "mode-switches" / "failed"
                failed_dir.mkdir(parents=True, exist_ok=True)
                rec_id = uuid.uuid4().hex[:8]
                failed_path = failed_dir / f"{_timestamp()}-{rec_id}.json"
                failed_payload = {
                    "schema_version": 1,
                    "record_id": rec_id,
                    "axis": entry.axis,
                    "harness_id_or_name": entry.harness_id_or_name,
                    "role": entry.role,
                    "substrate": entry.substrate,
                    "change_reason": entry.change_reason,
                    "scheduled_at": entry.scheduled_at.isoformat().replace("+00:00", "Z"),
                    "failed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    "error": str(exc),
                }
                failed_path.write_text(json.dumps(failed_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            except Exception:
                pass

            results.append(
                ApplyResult(
                    pending_path=entry.path,
                    applied=False,
                    error=str(exc),
                )
            )
            continue
        except Exception as exc:  # noqa: BLE001 - fail-soft per design
            # Write a failed record to .gtkb-state/mode-switches/failed/
            try:
                failed_dir = project_root / ".gtkb-state" / "mode-switches" / "failed"
                failed_dir.mkdir(parents=True, exist_ok=True)
                rec_id = uuid.uuid4().hex[:8]
                failed_path = failed_dir / f"{_timestamp()}-{rec_id}.json"
                failed_payload = {
                    "schema_version": 1,
                    "record_id": rec_id,
                    "axis": entry.axis,
                    "harness_id_or_name": entry.harness_id_or_name,
                    "role": entry.role,
                    "substrate": entry.substrate,
                    "change_reason": entry.change_reason,
                    "scheduled_at": entry.scheduled_at.isoformat().replace("+00:00", "Z"),
                    "failed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    "error": f"unexpected error: {exc}",
                }
                failed_path.write_text(json.dumps(failed_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            except Exception:
                pass

            results.append(
                ApplyResult(
                    pending_path=entry.path,
                    applied=False,
                    error=f"unexpected error: {exc}",
                )
            )
            continue
        applied_target = applied_root / entry.path.name
        try:
            shutil.move(str(entry.path), str(applied_target))
        except OSError as exc:
            results.append(
                ApplyResult(
                    pending_path=entry.path,
                    applied=True,
                    error=f"applied but archive move failed: {exc}",
                    transaction_result=tx_result,
                )
            )
            continue
        results.append(
            ApplyResult(
                pending_path=entry.path,
                applied=True,
                applied_path=applied_target,
                transaction_result=tx_result,
            )
        )
    return results
