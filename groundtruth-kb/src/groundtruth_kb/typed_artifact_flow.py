"""Service surface for Typed Artifact-Flow Engine definitions.

This module is the Phase 0 access point for TAFE flow templates. It stores
append-only definition versions in MemBase while bridge markdown remains the
authoritative coordination surface until a later governed cutover.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from groundtruth_kb.db import KnowledgeDB


class FlowDefinitionService:
    """Canonical source API for TAFE flow-definition records."""

    def __init__(self, db: KnowledgeDB):
        self.db = db

    def define(
        self,
        *,
        id: str,
        flow_type: str,
        title: str,
        stage_sequence: Sequence[str],
        required_roles_by_stage: Mapping[str, str],
        changed_by: str,
        change_reason: str,
        description: str | None = None,
        status: str = "active",
        auq_gate_positions: Sequence[str] | None = None,
        never_self_review_stages: Sequence[str] | None = None,
        deterministic_carve_outs: list[str] | dict[str, Any] | None = None,
        workspace_isolation: dict[str, Any] | None = None,
        source_spec_ids: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Append a flow-definition version and return its current row."""

        normalized_stages = _normalize_stage_sequence(stage_sequence)
        normalized_roles = _normalize_required_roles(required_roles_by_stage, normalized_stages)
        row = self.db.insert_flow_definition(
            id=_require_non_empty("id", id),
            flow_type=_require_non_empty("flow_type", flow_type),
            title=_require_non_empty("title", title),
            stage_sequence=normalized_stages,
            required_roles_by_stage=normalized_roles,
            changed_by=_require_non_empty("changed_by", changed_by),
            change_reason=_require_non_empty("change_reason", change_reason),
            description=description,
            status=_require_non_empty("status", status),
            auq_gate_positions=_list_or_none(auq_gate_positions),
            never_self_review_stages=_list_or_none(never_self_review_stages),
            deterministic_carve_outs=deterministic_carve_outs,
            workspace_isolation=workspace_isolation,
            source_spec_ids=list(source_spec_ids) if source_spec_ids is not None else None,
        )
        if row is None:
            raise RuntimeError(f"Inserted flow definition {id!r} but could not read it back")
        return _service_row(row)

    def get(self, flow_definition_id: str) -> dict[str, Any] | None:
        """Return the current version of a flow definition."""

        row = self.db.get_flow_definition(flow_definition_id)
        return _service_row(row) if row else None

    def history(self, flow_definition_id: str) -> list[dict[str, Any]]:
        """Return all versions of a flow definition, newest first."""

        return [_service_row(row) for row in self.db.get_flow_definition_history(flow_definition_id)]

    def list(
        self,
        *,
        flow_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List current flow definitions with optional filters."""

        return [
            _service_row(row)
            for row in self.db.list_flow_definitions(
                flow_type=flow_type,
                status=status,
            )
        ]


class TypedArtifactFlowService(FlowDefinitionService):
    """Backward-compatible friendly facade over ``FlowDefinitionService``."""

    def create_flow_definition(
        self,
        *,
        id: str,
        flow_type: str,
        name: str,
        stages: Sequence[str | Mapping[str, Any]],
        required_roles: Mapping[str, str],
        changed_by: str,
        change_reason: str,
        description: str | None = None,
        lifecycle_status: str = "active",
        auq_gate_positions: Sequence[str] | None = None,
        never_self_review_points: Sequence[str] | None = None,
        deterministic_carveouts: list[str] | dict[str, Any] | None = None,
        workspace_isolation: dict[str, Any] | None = None,
        source_spec_ids: Sequence[str] | None = None,
    ) -> dict[str, Any]:
        """Append a flow definition using the friendlier alias names."""

        return self.define(
            id=id,
            flow_type=flow_type,
            title=name,
            stage_sequence=_stage_sequence_from_aliases(stages),
            required_roles_by_stage=required_roles,
            changed_by=changed_by,
            change_reason=change_reason,
            description=description,
            status=lifecycle_status,
            auq_gate_positions=auq_gate_positions,
            never_self_review_stages=never_self_review_points,
            deterministic_carve_outs=deterministic_carveouts,
            workspace_isolation=workspace_isolation,
            source_spec_ids=source_spec_ids,
        )

    def get_flow_definition(self, flow_definition_id: str) -> dict[str, Any] | None:
        return self.get(flow_definition_id)

    def get_flow_definition_history(self, flow_definition_id: str) -> list[dict[str, Any]]:
        return self.history(flow_definition_id)

    def list_flow_definitions(
        self,
        *,
        flow_type: str | None = None,
        lifecycle_status: str | None = None,
    ) -> list[dict[str, Any]]:
        return self.list(flow_type=flow_type, status=lifecycle_status)


def _service_row(row: dict[str, Any]) -> dict[str, Any]:
    result = dict(row)
    result["name"] = result.get("name") or result.get("title")
    result["lifecycle_status"] = result.get("lifecycle_status") or result.get("status")
    result["stages_parsed"] = result.get("stages_parsed") or result.get("stage_sequence_parsed", [])
    result["required_roles_parsed"] = result.get("required_roles_parsed") or result.get(
        "required_roles_by_stage_parsed", {}
    )
    result["never_self_review_points_parsed"] = result.get("never_self_review_points_parsed") or result.get(
        "never_self_review_stages_parsed", []
    )
    result["deterministic_carveouts_parsed"] = result.get("deterministic_carveouts_parsed") or result.get(
        "deterministic_carve_outs_parsed", []
    )
    return result


def _normalize_stage_sequence(stage_sequence: Sequence[str]) -> list[str]:
    if isinstance(stage_sequence, (str, bytes)) or not isinstance(stage_sequence, Sequence):
        raise ValueError("stage_sequence must be a non-string sequence")
    normalized = [_require_non_empty("stage", str(stage)) for stage in stage_sequence]
    if not normalized:
        raise ValueError("stage_sequence must contain at least one stage")
    duplicates = sorted({stage for stage in normalized if normalized.count(stage) > 1})
    if duplicates:
        raise ValueError(f"duplicate stages: {duplicates}")
    return normalized


def _normalize_required_roles(required_roles: Mapping[str, str], stage_sequence: Sequence[str]) -> dict[str, str]:
    normalized = {
        _require_non_empty("required role stage", str(stage)): _require_non_empty("required role", str(role))
        for stage, role in required_roles.items()
    }
    known = set(stage_sequence)
    missing = [stage for stage in stage_sequence if stage not in normalized]
    if missing:
        raise ValueError(f"required_roles_by_stage missing stages: {missing}")
    unknown = sorted(set(normalized) - known)
    if unknown:
        raise ValueError(f"required_roles_by_stage includes unknown stages: {unknown}")
    return normalized


def _stage_sequence_from_aliases(stages: Sequence[str | Mapping[str, Any]]) -> list[str]:
    if isinstance(stages, (str, bytes)) or not isinstance(stages, Sequence):
        raise ValueError("stages must be a non-string sequence")
    normalized = []
    for stage in stages:
        stage_id = stage.get("id") if isinstance(stage, Mapping) else stage
        normalized.append(_require_non_empty("stage id", str(stage_id or "")))
    return _normalize_stage_sequence(normalized)


def _list_or_none(value: Sequence[Any] | None) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError("value must be a non-string sequence")
    return list(value)


def _require_non_empty(field_name: str, value: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError(f"{field_name} must be a non-empty string")
    return text


__all__ = ["FlowDefinitionService", "TypedArtifactFlowService"]
