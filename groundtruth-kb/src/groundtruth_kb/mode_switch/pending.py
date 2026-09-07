"""Pending-transaction queue for next-session-effective bridge-substrate switches.

Per ``SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`` v2, which supports next-session
effectiveness for the NON-ROLE axes of that requirement only.

THE ROLE AXIS WAS REMOVED (WI-7823). A session role resolves only from the
immutable init binding established for that session context, per
``DCL-SESSION-ROLE-RESOLUTION-001``. Nothing may create, persist, defer, or apply
at session initialization a result that resolves a session role, so this module
has no ``defer_role_switch`` writer and ``apply_pending`` refuses any entry whose
axis is not ``bridge_substrate``. ``apply_role_switch`` remains available in
``mode_switch.transaction`` for immediate harness-registry configuration; it is
simply unreachable from this queue.

Pending files live at ``.gtkb-state/mode-switches/pending/<timestamp>-<uuid>.json``.
On apply, successful entries move to ``.gtkb-state/mode-switches/applied/``;
failed entries remain in ``pending/`` with the error logged so the owner
can inspect. The forbidden-root placement of that queue is carried separately by
WI-7172 and is out of scope here.

``apply_pending(project_root)`` is an owner-invoked entry point, reached through
``gt mode apply-pending``. It is deliberately NOT called from any session-startup
path: automatic application at startup is what allowed one session to install
state for the next, which is the defect WI-7823 removed.

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
                raise TransactionValidationError(
                    f"Unsupported pending axis {entry.axis!r}. Role deferral was removed "
                    "under WI-7823: a session role resolves only from the immutable init "
                    "binding per DCL-SESSION-ROLE-RESOLUTION-001, so no pending entry may "
                    "resolve one. Only the 'bridge_substrate' axis is applied here.",
                    axis=entry.axis,
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
            except Exception:  # intentional-catch: quality gate waiver
                pass

            results.append(
                ApplyResult(
                    pending_path=entry.path,
                    applied=False,
                    error=str(exc),
                )
            )
            continue
        except Exception as exc:  # noqa: BLE001 - fail-soft per design  # intentional-catch: quality gate waiver
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
            except Exception:  # intentional-catch: quality gate waiver
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
