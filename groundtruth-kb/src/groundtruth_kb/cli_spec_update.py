"""Implementation for the high-level ``gt spec update`` command.

``gt spec update`` is the governed companion to ``gt spec record``. Where
``record`` is create-only, ``update`` produces a NEW VERSION of an existing
spec via :meth:`KnowledgeDB.update_spec`. Like ``record`` it is an in-process
deterministic service: the caller supplies the exact expected current version and
the mutation proceeds only when that version still holds. Persistence is
intrinsic, so no packet, receipt, approval field, or approvals-directory artifact
is constructed, written, or read. A stale expected version leaves zero effect.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from groundtruth_kb.config import GTConfig
from groundtruth_kb.db import KnowledgeDB

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
    expected_version: int
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
    if request.expected_version < 1:
        raise SpecUpdateError(
            "--expected-version must be the exact current version, which is at least 1 for an "
            "existing specification; use `gt spec record --expected-version 0` to create one"
        )
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


def _matches_postimage(row: dict[str, Any], full_content: str, postimage_fields: dict[str, Any]) -> bool:
    """Return True when the stored row already equals the requested postimage exactly."""

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


def update_spec(config: GTConfig, request: SpecUpdateRequest) -> dict[str, Any]:
    """Version an existing spec under exact expected-version CAS.

    Persistence is intrinsic: the canonical row is the record. A stale expected
    version leaves zero effect, and no packet or approvals artifact is involved.
    """

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

    # artifact_type is the live spec row's stored type, NOT a value derived from
    # the id prefix. This preserves the canonical type assignment made at create time.
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

    if current_version != request.expected_version:
        # Exact replay is read-only: when the requested postimage is already the
        # current row and the expected version names the version it replaced, the
        # update has already succeeded and nothing is appended.
        if current_version == request.expected_version + 1 and _matches_postimage(
            current, full_content, postimage_fields
        ):
            return {
                "updated": False,
                "dry_run": request.dry_run,
                "replayed": True,
                "id": current["id"],
                "row": current,
                "from_version": request.expected_version,
                "to_version": current_version,
                "expected_version": request.expected_version,
                "merged_fields": sorted(merged_fields),
                "db_operation": {
                    "method": "update_spec",
                    "id": request.spec_id,
                    "type": artifact_type,
                    "from_version": request.expected_version,
                    "to_version": current_version,
                },
            }
        raise SpecUpdateError(
            f"stale_expected_version: {request.spec_id} is at version {current_version}, "
            f"but --expected-version was {request.expected_version}; re-read the "
            "specification and retry. No effect was applied."
        )

    changed_by = _changed_by()
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
            "replayed": False,
            "id": request.spec_id,
            "row": None,
            "from_version": current_version,
            "to_version": new_version,
            "expected_version": request.expected_version,
            "merged_fields": sorted(merged_fields),
            "db_operation": db_operation,
        }

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
        "replayed": False,
        "id": row["id"],
        "row": row,
        "from_version": current_version,
        "to_version": int(row["version"]),
        "expected_version": request.expected_version,
        "merged_fields": sorted(merged_fields),
        "db_operation": db_operation,
    }
