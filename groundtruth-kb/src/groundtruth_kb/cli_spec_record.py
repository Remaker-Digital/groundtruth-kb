"""Implementation for the high-level ``gt spec record`` command."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB


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
    expected_version: int
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
    gap_state_capture: bool = False
    gap_state_bridge_id: str | None = None
    gap_state_reason: str | None = None
    dry_run: bool = False


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
    if request.expected_version != 0:
        raise SpecRecordError(
            "--expected-version must be 0 for record; a nonzero expected version addresses an "
            "existing specification and belongs to `spec update`"
        )
    if not request.change_reason.strip():
        raise SpecRecordError("--change-reason must be non-empty")
    if request.gap_state_capture:
        if not (request.gap_state_bridge_id and request.gap_state_bridge_id.strip()):
            raise SpecRecordError("--gap-state-bridge-id is required with --gap-state-capture")
        if not (request.gap_state_reason and request.gap_state_reason.strip()):
            raise SpecRecordError("--gap-state-reason is required with --gap-state-capture")


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


def _matches_postimage(row: dict[str, Any], full_content: str, postimage_fields: dict[str, Any]) -> bool:
    """Return True when the stored row already equals the requested postimage exactly.

    JSON-valued columns are compared against their parsed form when the reader
    supplies one, so an identical request is recognized regardless of stored
    serialization.
    """

    def _norm(value: Any) -> Any:
        # Storage normalizes an empty JSON container to NULL, so an identical
        # request round-trips to None. Comparing without this would report a
        # false difference and turn an exact replay into a spurious collision.
        if isinstance(value, (list, dict)) and not value:
            return None
        return value

    if (row.get("description") or "") != full_content:
        return False
    for name, value in postimage_fields.items():
        parsed_key = f"{name}_parsed"
        stored = row[parsed_key] if parsed_key in row else row.get(name)
        if _norm(stored) != _norm(value):
            return False
    return True


def record_spec(config: GTConfig, request: SpecRecordRequest) -> dict[str, Any]:
    """Validate the request under exact expected-version CAS and insert a new spec.

    Persistence is intrinsic: the canonical row is the record. No packet, receipt,
    approval field, or approvals-directory artifact is constructed, written, or read.
    """

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
    existing = db.get_spec(request.spec_id)

    changed_by = _changed_by()
    db_operation: dict[str, object] = {
        "method": "insert_spec",
        "id": request.spec_id,
        "type": resolved_type,
        "status": request.status,
    }
    postimage_fields: dict[str, Any] = {
        "title": request.title,
        "status": request.status,
        "priority": request.priority,
        "scope": request.scope,
        "section": request.section,
        "handle": request.handle,
        "tags": tags,
        "assertions": assertions,
        "constraints": constraints,
        "affected_by": affected_by,
        "testability": request.testability,
        "source_paths": source_paths,
        "application_scope": request.application_scope,
    }
    if existing is not None:
        # Exact replay is read-only: an identical request against an identical row
        # appends nothing and reports itself as a replay. A same-id request whose
        # content or postimage differs is a collision and leaves zero effect.
        if _matches_postimage(existing, full_content, postimage_fields):
            return {
                "created": False,
                "dry_run": request.dry_run,
                "replayed": True,
                "expected_version": request.expected_version,
                "gap_state_capture": request.gap_state_capture,
                "id": existing["id"],
                "row": existing,
                "db_operation": db_operation,
            }
        raise SpecRecordError(
            f"record_collision: {request.spec_id} already exists at version "
            f"{int(existing['version'])} with different content or postimage; no effect was applied"
        )

    if request.dry_run:
        return {
            "created": False,
            "dry_run": True,
            "replayed": False,
            "expected_version": request.expected_version,
            "gap_state_capture": request.gap_state_capture,
            "id": request.spec_id,
            "row": None,
            "db_operation": db_operation,
        }

    row = db.insert_spec(
        id=request.spec_id,
        description=full_content,
        changed_by=changed_by,
        change_reason=request.change_reason,
        type=resolved_type,
        **postimage_fields,
    )
    if row is None:
        raise SpecRecordError(f"Unexpected error: inserted spec {request.spec_id} not found on readback.")

    return {
        "created": True,
        "dry_run": False,
        "replayed": False,
        "expected_version": request.expected_version,
        "gap_state_capture": request.gap_state_capture,
        "id": row["id"],
        "row": row,
        "db_operation": db_operation,
    }
