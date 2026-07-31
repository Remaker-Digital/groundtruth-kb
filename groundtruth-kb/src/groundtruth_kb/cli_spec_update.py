"""Implementation for the high-level ``gt spec update`` command.

``gt spec update`` is the governed companion to ``gt spec record``. Where
``record`` is create-only, ``update`` produces a NEW VERSION of an existing
spec via :meth:`KnowledgeDB.update_spec`. Like ``record`` it is an in-process
deterministic service: owner/AUQ evidence is validated and a formal-artifact
approval packet is written before any DB mutation. The raw ``update_spec(...)``
mutation pattern remains protected by the existing PreToolUse hook for
direct-API callers; this governed CLI path writes its own approval packet.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

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

_POSTIMAGE_FIELD_NAMES = (
    "title",
    "status",
    "priority",
    "scope",
    "section",
    "handle",
    "tags",
    "assertions",
    "constraints",
    "affected_by",
    "testability",
    "source_paths",
    "application_scope",
)
_JSON_POSTIMAGE_FIELDS = ("tags", "assertions", "constraints", "affected_by", "source_paths")


class SpecUpdateError(Exception):
    """Raised when ``gt spec update`` cannot safely proceed."""


@dataclass(frozen=True)
class SpecUpdateRequest:
    spec_id: str
    content_file: Path
    change_reason: str
    auq_id: str
    auq_answer: str
    owner_presented: bool
    approved_by: str | None
    title: str | None
    status: str | None
    priority: str | None
    scope: str | None
    section: str | None
    handle: str | None
    testability: str | None
    tags_json: str | None
    assertions_json: str | None
    constraints_json: str | None
    affected_by_json: str | None
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


def _approval_packet_path(project_root: Path, artifact_id: str, new_version: int) -> Path:
    """Return the update-time approval-packet path.

    The ``-v<new_version>`` suffix avoids collision with the Slice-2
    create-time packet (``<date>-<artifact_id>.json``) for the same spec id.
    """
    date_prefix = datetime.now(UTC).strftime("%Y-%m-%d")
    return (
        project_root / ".groundtruth" / "formal-artifact-approvals" / f"{date_prefix}-{artifact_id}-v{new_version}.json"
    )


def _parse_json_option(raw: str | None, option_name: str, expected_type: type) -> Any:
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SpecUpdateError(f"{option_name} must be valid JSON: {exc}") from exc
    if not isinstance(parsed, expected_type):
        raise SpecUpdateError(f"{option_name} must decode to {expected_type.__name__}")
    return parsed


def _parse_json_list(raw: str | None, option_name: str) -> list[Any] | None:
    return cast(list[Any] | None, _parse_json_option(raw, option_name, list))


def _parse_json_dict(raw: str | None, option_name: str) -> dict[str, Any] | None:
    return cast(dict[str, Any] | None, _parse_json_option(raw, option_name, dict))


def _validate_request_evidence(request: SpecUpdateRequest) -> None:
    if not request.owner_presented:
        raise SpecUpdateError("--owner-presented is required before updating a spec")
    if not request.auq_id.strip():
        raise SpecUpdateError("--auq-id must be non-empty")
    if not request.auq_answer.strip():
        raise SpecUpdateError("--auq-answer must be non-empty")
    if not request.change_reason.strip():
        raise SpecUpdateError("--change-reason must be non-empty")


def _validate_string_list(value: list[Any] | None, option_name: str) -> list[str] | None:
    if value is None:
        return None
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise SpecUpdateError(f"{option_name} must be a JSON list of non-empty strings")
    return list(value)


def _validate_assertions(value: list[Any] | None) -> list[dict[str, Any]] | None:
    if value is None:
        return None
    if not all(isinstance(item, dict) for item in value):
        raise SpecUpdateError("--assertions-json must be a JSON list of objects")
    return list(value)


def _build_packet(
    *,
    request: SpecUpdateRequest,
    artifact_type: str,
    current_version: int,
    full_content: str,
    changed_by: str,
    postimage_fields: dict[str, Any],
) -> dict[str, object]:
    return construct_approval_packet(
        artifact_type=artifact_type,
        artifact_id=request.spec_id,
        action="update",
        source_ref=f"{request.spec_id}@v{current_version}",
        full_content=full_content,
        approval_mode="approve",
        presented_to_user=request.owner_presented,
        transcript_captured=True,
        explicit_change_request=f"AUQ {request.auq_id}: {request.auq_answer}",
        approved_by=request.approved_by or "owner",
        changed_by=changed_by,
        change_reason=request.change_reason,
        postimage_fields=postimage_fields,
    )


def _normalized_postimage_fields(
    request: SpecUpdateRequest,
    current: dict[str, Any],
    *,
    tags: list[str] | None,
    assertions: list[dict[str, Any]] | None,
    constraints: dict[str, Any] | None,
    affected_by: list[str] | None,
    source_paths: list[str] | None,
) -> dict[str, Any]:
    """Return the complete normalized non-description row postimage."""

    supplied_json = {
        "tags": (request.tags_json, tags),
        "assertions": (request.assertions_json, assertions),
        "constraints": (request.constraints_json, constraints),
        "affected_by": (request.affected_by_json, affected_by),
        "source_paths": (request.source_paths_json, source_paths),
    }
    fields: dict[str, Any] = {}
    for name in _POSTIMAGE_FIELD_NAMES:
        if name in _JSON_POSTIMAGE_FIELDS:
            raw_option, parsed_option = supplied_json[name]
            if raw_option is not None:
                fields[name] = parsed_option
                continue
            if current.get(name) is None:
                fields[name] = None
                continue
            parsed_name = f"{name}_parsed"
            if parsed_name not in current:
                raise SpecUpdateError(f"stored {name} for {request.spec_id} is not valid JSON")
            fields[name] = current[parsed_name]
            continue

        supplied_value = getattr(request, name)
        fields[name] = supplied_value if supplied_value is not None else current.get(name)
    return fields


def update_spec(config: GTConfig, request: SpecUpdateRequest) -> dict[str, Any]:
    """Validate evidence, write an approval packet, and version an existing spec."""

    _validate_request_evidence(request)

    project_root = config.project_root.resolve()
    content_path = request.content_file.resolve()
    if not _is_relative_to(content_path, project_root):
        raise SpecUpdateError(f"--content-file must be inside project root {project_root}")
    full_content = content_path.read_text(encoding="utf-8")
    if not full_content.strip():
        raise SpecUpdateError("--content-file must not be empty")

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

    db = KnowledgeDB(db_path=config.db_path, chroma_path=config.chroma_path)
    current = db.get_spec(request.spec_id)
    if current is None:
        raise SpecUpdateError(f"spec {request.spec_id} does not exist; use 'gt spec record' to create a new spec")

    # The packet's artifact_type is the live spec row's stored type, NOT a
    # value derived from the id prefix. This preserves the canonical type
    # assignment made at create time.
    artifact_type = current["type"]
    current_version = int(current["version"])
    new_version = current_version + 1

    postimage_fields = _normalized_postimage_fields(
        request,
        current,
        tags=tags,
        assertions=assertions,
        constraints=constraints,
        affected_by=affected_by,
        source_paths=source_paths,
    )
    merged_fields = {"description": full_content, **postimage_fields}

    changed_by = _changed_by()
    packet = _build_packet(
        request=request,
        artifact_type=artifact_type,
        current_version=current_version,
        full_content=full_content,
        changed_by=changed_by,
        postimage_fields=postimage_fields,
    )
    validation = validate_packet(packet)
    if not validation.is_valid:
        raise SpecUpdateError("; ".join(validation.errors))

    packet_path = _approval_packet_path(project_root, request.spec_id, new_version)
    db_operation = {
        "method": "update_spec",
        "id": request.spec_id,
        "type": artifact_type,
        "from_version": current_version,
        "to_version": new_version,
    }
    if request.dry_run:
        return {
            "updated": False,
            "dry_run": True,
            "id": request.spec_id,
            "row": None,
            "from_version": current_version,
            "to_version": new_version,
            "approval_packet_path": str(packet_path),
            "approval_packet": packet,
            "merged_fields": sorted(merged_fields),
            "db_operation": db_operation,
        }

    if packet_path.exists():
        raise SpecUpdateError(f"approval packet already exists: {packet_path}")
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    try:
        row = db.update_spec(
            request.spec_id,
            changed_by,
            request.change_reason,
            **merged_fields,
        )
    except ValueError as exc:
        raise SpecUpdateError(str(exc)) from exc
    if row is None:
        raise SpecUpdateError(f"Unexpected error: updated spec {request.spec_id} not found on readback.")

    return {
        "updated": True,
        "dry_run": False,
        "id": row["id"],
        "row": row,
        "from_version": current_version,
        "to_version": int(row["version"]),
        "approval_packet_path": str(packet_path),
        "approval_packet": packet,
        "merged_fields": sorted(merged_fields),
        "db_operation": db_operation,
    }
