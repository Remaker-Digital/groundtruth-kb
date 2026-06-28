"""Implementation for the high-level ``gt spec record`` command."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.governance.approval_packet import construct_approval_packet, validate_packet


class SpecRecordError(Exception):
    """Raised when ``gt spec record`` cannot safely proceed."""


SPEC_RECORD_TYPES = (
    "requirement",
    "governance",
    "protected_behavior",
    "architecture_decision",
    "design_constraint",
)

_PREFIX_TYPES = {
    "GOV-": "governance",
    "PB-": "protected_behavior",
    "ADR-": "architecture_decision",
    "DCL-": "design_constraint",
    "SPEC-": "requirement",
    "REQ-": "requirement",
}


@dataclass(frozen=True)
class SpecRecordRequest:
    spec_id: str
    title: str
    status: str
    content_file: Path
    change_reason: str
    auq_id: str
    auq_answer: str
    owner_presented: bool
    approved_by: str | None
    spec_type: str | None
    priority: str | None
    scope: str | None
    section: str | None
    handle: str | None
    tags_json: str | None
    assertions_json: str | None
    constraints_json: str | None
    affected_by_json: str | None
    testability: str | None
    source_paths_json: str | None
    application_scope: str | None
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


def _approval_packet_path(project_root: Path, artifact_id: str) -> Path:
    date_prefix = datetime.now(UTC).strftime("%Y-%m-%d")
    return project_root / ".groundtruth" / "formal-artifact-approvals" / f"{date_prefix}-{artifact_id}.json"


def _parse_json_option(raw: str | None, option_name: str, expected_type: type) -> Any:
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecRecordError(f"{option_name} must be valid JSON: {exc}") from exc
    if not isinstance(parsed, expected_type):
        raise SpecRecordError(f"{option_name} must decode to {expected_type.__name__}")
    return parsed


def _parse_json_list(raw: str | None, option_name: str) -> list[Any] | None:
    return cast(list[Any] | None, _parse_json_option(raw, option_name, list))


def _parse_json_dict(raw: str | None, option_name: str) -> dict[str, Any] | None:
    return cast(dict[str, Any] | None, _parse_json_option(raw, option_name, dict))


def _resolve_spec_type(spec_id: str, declared_type: str | None) -> str:
    for prefix, spec_type in _PREFIX_TYPES.items():
        if spec_id.startswith(prefix):
            if declared_type is not None and declared_type != spec_type:
                raise SpecRecordError(
                    f"--type {declared_type!r} does not match {spec_id!r} prefix-derived type {spec_type!r}"
                )
            return spec_type
    prefixes = ", ".join(sorted(_PREFIX_TYPES))
    raise SpecRecordError(f"--id must start with one of: {prefixes}")


def _validate_request_evidence(request: SpecRecordRequest) -> None:
    if not request.owner_presented:
        raise SpecRecordError("--owner-presented is required before recording a spec")
    if not request.auq_id.strip():
        raise SpecRecordError("--auq-id must be non-empty")
    if not request.auq_answer.strip():
        raise SpecRecordError("--auq-answer must be non-empty")
    if not request.change_reason.strip():
        raise SpecRecordError("--change-reason must be non-empty")


def _validate_string_list(value: list[Any] | None, option_name: str) -> list[str] | None:
    if value is None:
        return None
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise SpecRecordError(f"{option_name} must be a JSON list of non-empty strings")
    return list(value)


def _validate_assertions(value: list[Any] | None) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not all(isinstance(item, dict) for item in value):
        raise SpecRecordError("--assertions-json must be a JSON list of objects")
    return list(value)


def _validate_subtype(spec_id: str, spec_type: str, content: str, assertions: list[dict[str, Any]] | None) -> None:
    lowered = content.lower()
    if spec_type == "protected_behavior" and not assertions:
        raise SpecRecordError("PB-* specs require a non-empty --assertions-json list")
    if spec_type == "architecture_decision":
        required = ("## decision", "## rationale", "## consequences")
        missing = [section for section in required if section not in lowered]
        if "## alternatives considered" not in lowered and "## rejected alternatives" not in lowered:
            missing.append("## Alternatives Considered or ## Rejected Alternatives")
        if missing:
            raise SpecRecordError(f"{spec_id} ADR content missing required section(s): {', '.join(missing)}")
    if spec_type == "design_constraint" and "## constraint" not in lowered and "constraint statement" not in lowered:
        raise SpecRecordError("DCL-* specs require an explicit constraint section")


def _build_packet(
    *,
    request: SpecRecordRequest,
    resolved_type: str,
    full_content: str,
    changed_by: str,
) -> dict[str, object]:
    return construct_approval_packet(
        artifact_type=resolved_type,
        artifact_id=request.spec_id,
        action="create",
        source_ref=request.spec_id,
        full_content=full_content,
        approval_mode="approve",
        presented_to_user=request.owner_presented,
        transcript_captured=True,
        explicit_change_request=f"AUQ {request.auq_id}: {request.auq_answer}",
        approved_by=request.approved_by or "owner",
        changed_by=changed_by,
        change_reason=request.change_reason,
    )


def record_spec(config: GTConfig, request: SpecRecordRequest) -> dict[str, Any]:
    """Validate evidence, write an approval packet, and insert a new spec."""

    _validate_request_evidence(request)

    project_root = config.project_root.resolve()
    content_path = request.content_file.resolve()
    if not _is_relative_to(content_path, project_root):
        raise SpecRecordError(f"--content-file must be inside project root {project_root}")
    full_content = content_path.read_text(encoding="utf-8")
    if not full_content.strip():
        raise SpecRecordError("--content-file must not be empty")

    resolved_type = _resolve_spec_type(request.spec_id, request.spec_type)
    tags = _validate_string_list(_parse_json_list(request.tags_json, "--tags-json"), "--tags-json")
    assertions = _validate_assertions(_parse_json_list(request.assertions_json, "--assertions-json"))
    constraints = _parse_json_dict(request.constraints_json, "--constraints-json")
    affected_by = _validate_string_list(
        _parse_json_list(request.affected_by_json, "--affected-by-json"), "--affected-by-json"
    )
    source_paths = _validate_string_list(
        _parse_json_list(request.source_paths_json, "--source-paths-json"),
        "--source-paths-json",
    )
    _validate_subtype(request.spec_id, resolved_type, full_content, assertions)

    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    if db.get_spec(request.spec_id) is not None:
        raise SpecRecordError(f"spec {request.spec_id} already exists; Slice 2 record is create-only")

    changed_by = _changed_by()
    packet = _build_packet(
        request=request,
        resolved_type=resolved_type,
        full_content=full_content,
        changed_by=changed_by,
    )
    validation = validate_packet(packet)
    if not validation.is_valid:
        raise SpecRecordError("; ".join(validation.errors))

    packet_path = _approval_packet_path(project_root, request.spec_id)
    db_operation = {
        "method": "insert_spec",
        "id": request.spec_id,
        "type": resolved_type,
        "status": request.status,
    }
    if request.dry_run:
        return {
            "created": False,
            "dry_run": True,
            "id": request.spec_id,
            "row": None,
            "approval_packet_path": str(packet_path),
            "approval_packet": packet,
            "db_operation": db_operation,
        }

    if packet_path.exists():
        raise SpecRecordError(f"approval packet already exists: {packet_path}")
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    row = db.insert_spec(
        id=request.spec_id,
        title=request.title,
        description=full_content,
        status=request.status,
        changed_by=changed_by,
        change_reason=request.change_reason,
        priority=request.priority,
        scope=request.scope,
        section=request.section,
        handle=request.handle,
        tags=tags,
        assertions=assertions,
        type=resolved_type,
        constraints=constraints,
        affected_by=affected_by,
        testability=request.testability,
        source_paths=source_paths,
        application_scope=request.application_scope,
    )
    if row is None:
        raise SpecRecordError(f"Unexpected error: inserted spec {request.spec_id} not found on readback.")

    return {
        "created": True,
        "dry_run": False,
        "id": row["id"],
        "row": row,
        "approval_packet_path": str(packet_path),
        "approval_packet": packet,
        "db_operation": db_operation,
    }
