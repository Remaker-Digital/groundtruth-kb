"""Implementation for the high-level ``gt deliberations record`` command."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.governance.approval_packet import (
    construct_approval_packet,
    content_hash,
    validate_packet,
)


class DeliberationRecordError(Exception):
    """Raised when ``gt deliberations record`` cannot safely proceed."""


@dataclass(frozen=True)
class DeliberationRecordRequest:
    source_type: str
    source_ref: str
    title: str
    summary: str
    content_file: Path
    change_reason: str
    auq_id: str
    auq_answer: str
    owner_presented: bool
    approved_by: str | None
    spec_id: str | None
    work_item_id: str | None
    participants: list[str] | None
    outcome: str | None
    session_id: str | None
    dry_run: bool


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _changed_by() -> str:
    for name in ("GTKB_HARNESS_ID", "GTKB_ACTIVE_HARNESS_ID", "CODEX_HARNESS_ID"):
        value = os.environ.get(name)
        if value and value.strip():
            return value.strip()
    return "gt-cli"


def _existing_by_source_hash(db: KnowledgeDB, source_ref: str, digest: str) -> dict[str, Any] | None:
    row = (
        db._get_conn()
        .execute(
            """SELECT id FROM current_deliberations
           WHERE source_ref = ? AND content_hash = ?""",
            (source_ref, digest),
        )
        .fetchone()
    )
    if not row:
        return None
    return db.get_deliberation(row["id"])


def _next_deliberation_id(db: KnowledgeDB) -> str:
    row = (
        db._get_conn()
        .execute("SELECT MAX(CAST(SUBSTR(id, 7) AS INTEGER)) FROM deliberations WHERE id LIKE 'DELIB-%'")
        .fetchone()
    )
    if row and row[0] is not None:
        return f"DELIB-{row[0] + 1:04d}"
    return "DELIB-0001"


def _approval_packet_path(project_root: Path, artifact_id: str) -> Path:
    date_prefix = datetime.now(UTC).strftime("%Y-%m-%d")
    return project_root / ".groundtruth" / "formal-artifact-approvals" / f"{date_prefix}-{artifact_id}.json"


def _build_packet(
    *,
    request: DeliberationRecordRequest,
    artifact_id: str,
    full_content: str,
    changed_by: str,
) -> dict[str, object]:
    return construct_approval_packet(
        artifact_type="deliberation",
        artifact_id=artifact_id,
        action="create",
        source_ref=request.source_ref,
        full_content=full_content,
        approval_mode="approve",
        presented_to_user=request.owner_presented,
        transcript_captured=True,
        explicit_change_request=f"AUQ {request.auq_id}: {request.auq_answer}",
        approved_by=request.approved_by or "owner",
        changed_by=changed_by,
        change_reason=request.change_reason,
    )


def _validate_request_evidence(request: DeliberationRecordRequest) -> None:
    if not request.owner_presented:
        raise DeliberationRecordError("--owner-presented is required before recording a deliberation")
    if not request.auq_id.strip():
        raise DeliberationRecordError("--auq-id must be non-empty")
    if not request.auq_answer.strip():
        raise DeliberationRecordError("--auq-answer must be non-empty")
    if not request.change_reason.strip():
        raise DeliberationRecordError("--change-reason must be non-empty")


def record_deliberation(config: GTConfig, request: DeliberationRecordRequest) -> dict[str, Any]:
    """Validate evidence, write an approval packet, and insert a deliberation."""

    _validate_request_evidence(request)

    project_root = config.project_root.resolve()
    content_path = request.content_file.resolve()
    if not _is_relative_to(content_path, project_root):
        raise DeliberationRecordError(f"--content-file must be inside project root {project_root}")
    full_content = content_path.read_text(encoding="utf-8")
    digest = content_hash(full_content)
    changed_by = _changed_by()

    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    existing = _existing_by_source_hash(db, request.source_ref, digest)
    if existing:
        return {
            "created": False,
            "dry_run": request.dry_run,
            "id": existing["id"],
            "row": existing,
            "approval_packet_path": None,
            "approval_packet": None,
        }

    planned_id = _next_deliberation_id(db)
    if db.get_deliberation(planned_id):
        planned_id = _next_deliberation_id(db)
        if db.get_deliberation(planned_id):
            raise DeliberationRecordError(f"could not allocate unused deliberation id after collision: {planned_id}")

    packet = _build_packet(
        request=request,
        artifact_id=planned_id,
        full_content=full_content,
        changed_by=changed_by,
    )
    validation = validate_packet(packet)
    if not validation.is_valid:
        raise DeliberationRecordError("; ".join(validation.errors))

    packet_path = _approval_packet_path(project_root, planned_id)
    if request.dry_run:
        return {
            "created": False,
            "dry_run": True,
            "id": planned_id,
            "row": None,
            "approval_packet_path": str(packet_path),
            "approval_packet": packet,
            "db_operation": {
                "method": "insert_deliberation",
                "source_type": request.source_type,
                "source_ref": request.source_ref,
                "content_hash": digest,
            },
        }

    if db.get_deliberation(planned_id):
        planned_id = _next_deliberation_id(db)
        packet = _build_packet(
            request=request,
            artifact_id=planned_id,
            full_content=full_content,
            changed_by=changed_by,
        )
        validation = validate_packet(packet)
        if not validation.is_valid:
            raise DeliberationRecordError("; ".join(validation.errors))
        packet_path = _approval_packet_path(project_root, planned_id)

    if packet_path.exists():
        raise DeliberationRecordError(f"approval packet already exists: {packet_path}")
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    row = db.insert_deliberation(
        id=planned_id,
        source_type=request.source_type,
        title=request.title,
        summary=request.summary,
        content=full_content,
        changed_by=changed_by,
        change_reason=request.change_reason,
        spec_id=request.spec_id,
        work_item_id=request.work_item_id,
        source_ref=request.source_ref,
        participants=request.participants,
        outcome=request.outcome,
        session_id=request.session_id,
    )
    if row is None:
        raise DeliberationRecordError(f"Unexpected error: inserted deliberation {planned_id} not found on readback.")

    return {
        "created": True,
        "dry_run": False,
        "id": row["id"],
        "row": row,
        "approval_packet_path": str(packet_path),
        "approval_packet": packet,
    }
