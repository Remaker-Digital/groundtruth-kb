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
from copy import deepcopy
from typing import Any

from groundtruth_kb.db import KnowledgeDB

_SOURCE_SPEC_IDS = ["SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA", "SPEC-TAFE-R1", "SPEC-TAFE-R7"]
_WORKSPACE_ISOLATION = {
    "project_root": "E:\\GT-KB",
    "scope": "gtkb-platform",
    "requires_separate_worktree_for_parallel_harnesses": True,
}
_DETERMINISTIC_CARVE_OUTS = [
    "generated_bridge_view",
    "read_only_status_render",
]

CANONICAL_REVIEWED_TASK_FLOW_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "implementation",
        "flow_type": "implementation",
        "title": "Implementation Flow",
        "description": "Reviewed task flow for proposed source, test, data, or governance implementation work.",
        "stage_sequence": ["propose", "review", "implement", "verify", "complete"],
        "required_roles_by_stage": {
            "propose": "prime-builder",
            "review": "loyal-opposition",
            "implement": "prime-builder",
            "verify": "loyal-opposition",
            "complete": "prime-builder",
        },
        "auq_gate_positions": ["after:propose", "after:review", "after:verify"],
        "never_self_review_stages": ["review", "verify"],
    },
    {
        "id": "operation",
        "flow_type": "operation",
        "title": "Operation Flow",
        "description": "Reviewed task flow for bounded operational work that executes an approved procedure.",
        "stage_sequence": ["plan", "execute", "verify", "complete"],
        "required_roles_by_stage": {
            "plan": "prime-builder",
            "execute": "prime-builder",
            "verify": "loyal-opposition",
            "complete": "prime-builder",
        },
        "auq_gate_positions": ["after:plan"],
        "never_self_review_stages": ["verify"],
    },
    {
        "id": "remediation",
        "flow_type": "remediation",
        "title": "Remediation Flow",
        "description": "Reviewed task flow for diagnosing and correcting defects, drift, or failed verification.",
        "stage_sequence": ["diagnose", "propose_fix", "review", "implement", "verify", "complete"],
        "required_roles_by_stage": {
            "diagnose": "loyal-opposition",
            "propose_fix": "prime-builder",
            "review": "loyal-opposition",
            "implement": "prime-builder",
            "verify": "loyal-opposition",
            "complete": "prime-builder",
        },
        "auq_gate_positions": ["after:diagnose"],
        "never_self_review_stages": ["review", "verify"],
    },
    {
        "id": "deliberation",
        "flow_type": "deliberation",
        "title": "Deliberation Flow",
        "description": "Reviewed task flow for surfacing, investigating, deciding, and recording owner decisions.",
        "stage_sequence": ["surface", "investigate", "decide", "record", "complete"],
        "required_roles_by_stage": {
            "surface": "prime-builder",
            "investigate": "loyal-opposition",
            "decide": "owner",
            "record": "prime-builder",
            "complete": "prime-builder",
        },
        "auq_gate_positions": ["before:decide"],
        "never_self_review_stages": ["investigate", "record"],
    },
    {
        "id": "report",
        "flow_type": "report",
        "title": "Report Flow",
        "description": "Reviewed task flow for investigation reports, audit reports, and finalization work.",
        "stage_sequence": ["investigate", "draft", "review", "finalize", "complete"],
        "required_roles_by_stage": {
            "investigate": "loyal-opposition",
            "draft": "loyal-opposition",
            "review": "prime-builder",
            "finalize": "loyal-opposition",
            "complete": "loyal-opposition",
        },
        "auq_gate_positions": ["after:review"],
        "never_self_review_stages": ["review"],
    },
)


def canonical_reviewed_task_flow_definitions() -> tuple[dict[str, Any], ...]:
    """Return copy-safe canonical seed definitions for the five TAFE flow families."""

    return tuple(_canonical_seed_payload(seed) for seed in CANONICAL_REVIEWED_TASK_FLOW_DEFINITIONS)


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

    def seed_reviewed_task_flow_definitions(
        self,
        *,
        changed_by: str,
        change_reason: str,
    ) -> dict[str, Any]:
        """Idempotently seed the five canonical reviewed-task flow definitions."""

        inserted: list[str] = []
        updated: list[str] = []
        unchanged: list[str] = []
        definitions: list[dict[str, Any]] = []

        for seed in canonical_reviewed_task_flow_definitions():
            current = self.get(seed["id"])
            if current is None:
                row = self._define_seed(seed, changed_by=changed_by, change_reason=change_reason)
                inserted.append(seed["id"])
            elif _flow_definition_matches_seed(current, seed):
                row = current
                unchanged.append(seed["id"])
            else:
                row = self._define_seed(seed, changed_by=changed_by, change_reason=change_reason)
                updated.append(seed["id"])
            definitions.append(row)

        return {
            "inserted": inserted,
            "updated": updated,
            "unchanged": unchanged,
            "definitions": definitions,
        }

    def _define_seed(
        self,
        seed: Mapping[str, Any],
        *,
        changed_by: str,
        change_reason: str,
    ) -> dict[str, Any]:
        return self.define(
            id=str(seed["id"]),
            flow_type=str(seed["flow_type"]),
            title=str(seed["title"]),
            description=str(seed["description"]),
            stage_sequence=seed["stage_sequence"],
            required_roles_by_stage=seed["required_roles_by_stage"],
            auq_gate_positions=seed["auq_gate_positions"],
            never_self_review_stages=seed["never_self_review_stages"],
            deterministic_carve_outs=seed["deterministic_carve_outs"],
            workspace_isolation=seed["workspace_isolation"],
            source_spec_ids=seed["source_spec_ids"],
            changed_by=changed_by,
            change_reason=change_reason,
        )


class FlowRuntimeService(FlowDefinitionService):
    """Service API for TAFE runtime substrate records."""

    def create_flow_instance(
        self,
        *,
        id: str,
        flow_definition_id: str,
        subject_type: str,
        subject_id: str,
        changed_by: str,
        change_reason: str,
        flow_definition_version: int | None = None,
        flow_type: str | None = None,
        status: str = "created",
        current_stage_instance_id: str | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Append a flow-instance version and return the current row."""

        if self.get(flow_definition_id) is None:
            raise ValueError(f"unknown flow_definition_id: {flow_definition_id}")
        row = self.db.insert_flow_instance(
            id=_require_non_empty("id", id),
            flow_definition_id=_require_non_empty("flow_definition_id", flow_definition_id),
            subject_type=_require_non_empty("subject_type", subject_type),
            subject_id=_require_non_empty("subject_id", subject_id),
            changed_by=_require_non_empty("changed_by", changed_by),
            change_reason=_require_non_empty("change_reason", change_reason),
            flow_definition_version=flow_definition_version,
            flow_type=flow_type,
            status=_require_non_empty("status", status),
            current_stage_instance_id=current_stage_instance_id,
            started_at=started_at,
            completed_at=completed_at,
            metadata=dict(metadata) if metadata is not None else None,
        )
        if row is None:
            raise RuntimeError(f"Inserted flow instance {id!r} but could not read it back")
        return dict(row)

    def start_flow(self, **kwargs: Any) -> dict[str, Any]:
        """Alias for ``create_flow_instance``; no dispatch execution occurs."""

        return self.create_flow_instance(**kwargs)

    def get_flow_instance(self, flow_instance_id: str) -> dict[str, Any] | None:
        row = self.db.get_flow_instance(flow_instance_id)
        return dict(row) if row else None

    def get_flow_instance_history(self, flow_instance_id: str) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.get_flow_instance_history(flow_instance_id)]

    def list_flow_instances(
        self,
        *,
        flow_definition_id: str | None = None,
        flow_type: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.list_flow_instances(
                flow_definition_id=flow_definition_id,
                flow_type=flow_type,
                status=status,
            )
        ]

    def create_stage_instance(
        self,
        *,
        id: str,
        flow_instance_id: str,
        stage_id: str,
        stage_index: int,
        required_role: str,
        changed_by: str,
        change_reason: str,
        status: str = "pending",
        claim_status: str = "unclaimed",
        claimed_by_harness_id: str | None = None,
        claimed_by_session_id: str | None = None,
        started_at: str | None = None,
        completed_at: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Append a stage-instance version and return the current row."""

        if stage_index < 0:
            raise ValueError("stage_index must be non-negative")
        row = self.db.insert_stage_instance(
            id=_require_non_empty("id", id),
            flow_instance_id=_require_non_empty("flow_instance_id", flow_instance_id),
            stage_id=_require_non_empty("stage_id", stage_id),
            stage_index=stage_index,
            required_role=_require_non_empty("required_role", required_role),
            changed_by=_require_non_empty("changed_by", changed_by),
            change_reason=_require_non_empty("change_reason", change_reason),
            status=_require_non_empty("status", status),
            claim_status=_require_non_empty("claim_status", claim_status),
            claimed_by_harness_id=claimed_by_harness_id,
            claimed_by_session_id=claimed_by_session_id,
            started_at=started_at,
            completed_at=completed_at,
            metadata=dict(metadata) if metadata is not None else None,
        )
        if row is None:
            raise RuntimeError(f"Inserted stage instance {id!r} but could not read it back")
        return dict(row)

    def get_stage_instance(self, stage_instance_id: str) -> dict[str, Any] | None:
        row = self.db.get_stage_instance(stage_instance_id)
        return dict(row) if row else None

    def get_stage_instance_history(self, stage_instance_id: str) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.get_stage_instance_history(stage_instance_id)]

    def list_stage_instances(
        self,
        *,
        flow_instance_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.list_stage_instances(
                flow_instance_id=flow_instance_id,
                status=status,
            )
        ]

    def create_stage_lease(
        self,
        *,
        id: str,
        stage_instance_id: str,
        holder_harness_id: str,
        holder_session_id: str,
        ttl_seconds: int,
        changed_by: str,
        change_reason: str,
        lease_status: str = "active",
        acquired_at: str | None = None,
        heartbeat_at: str | None = None,
        expires_at: str | None = None,
        released_at: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Append a stage-lease version without implementing claim/release policy."""

        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        row = self.db.insert_stage_lease(
            id=_require_non_empty("id", id),
            stage_instance_id=_require_non_empty("stage_instance_id", stage_instance_id),
            holder_harness_id=_require_non_empty("holder_harness_id", holder_harness_id),
            holder_session_id=_require_non_empty("holder_session_id", holder_session_id),
            ttl_seconds=ttl_seconds,
            changed_by=_require_non_empty("changed_by", changed_by),
            change_reason=_require_non_empty("change_reason", change_reason),
            lease_status=_require_non_empty("lease_status", lease_status),
            acquired_at=acquired_at,
            heartbeat_at=heartbeat_at,
            expires_at=expires_at,
            released_at=released_at,
            metadata=dict(metadata) if metadata is not None else None,
        )
        if row is None:
            raise RuntimeError(f"Inserted stage lease {id!r} but could not read it back")
        return dict(row)

    def get_stage_lease(self, lease_id: str) -> dict[str, Any] | None:
        row = self.db.get_stage_lease(lease_id)
        return dict(row) if row else None

    def get_stage_lease_history(self, lease_id: str) -> list[dict[str, Any]]:
        return [dict(row) for row in self.db.get_stage_lease_history(lease_id)]

    def list_stage_leases(
        self,
        *,
        stage_instance_id: str | None = None,
        lease_status: str | None = None,
        holder_harness_id: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.list_stage_leases(
                stage_instance_id=stage_instance_id,
                lease_status=lease_status,
                holder_harness_id=holder_harness_id,
            )
        ]

    def record_flow_event(
        self,
        *,
        id: str,
        flow_instance_id: str,
        event_type: str,
        changed_by: str,
        change_reason: str,
        stage_instance_id: str | None = None,
        event_at: str | None = None,
        event_payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Insert an append-only flow event."""

        row = self.db.insert_flow_event(
            id=_require_non_empty("id", id),
            flow_instance_id=_require_non_empty("flow_instance_id", flow_instance_id),
            event_type=_require_non_empty("event_type", event_type),
            changed_by=_require_non_empty("changed_by", changed_by),
            change_reason=_require_non_empty("change_reason", change_reason),
            stage_instance_id=stage_instance_id,
            event_at=event_at,
            event_payload=dict(event_payload) if event_payload is not None else None,
        )
        if row is None:
            raise RuntimeError(f"Inserted flow event {id!r} but could not read it back")
        return dict(row)

    def get_flow_event(self, event_id: str) -> dict[str, Any] | None:
        row = self.db.get_flow_event(event_id)
        return dict(row) if row else None

    def list_flow_events(
        self,
        *,
        flow_instance_id: str | None = None,
        stage_instance_id: str | None = None,
        event_type: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.list_flow_events(
                flow_instance_id=flow_instance_id,
                stage_instance_id=stage_instance_id,
                event_type=event_type,
            )
        ]

    def link_flow_artifact(
        self,
        *,
        id: str,
        flow_instance_id: str,
        artifact_type: str,
        artifact_ref: str,
        changed_by: str,
        change_reason: str,
        stage_instance_id: str | None = None,
        relationship: str = "related",
        status: str = "active",
        metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Insert an append-only flow-artifact reference."""

        row = self.db.insert_flow_artifact(
            id=_require_non_empty("id", id),
            flow_instance_id=_require_non_empty("flow_instance_id", flow_instance_id),
            artifact_type=_require_non_empty("artifact_type", artifact_type),
            artifact_ref=_require_non_empty("artifact_ref", artifact_ref),
            changed_by=_require_non_empty("changed_by", changed_by),
            change_reason=_require_non_empty("change_reason", change_reason),
            stage_instance_id=stage_instance_id,
            relationship=_require_non_empty("relationship", relationship),
            status=_require_non_empty("status", status),
            metadata=dict(metadata) if metadata is not None else None,
        )
        if row is None:
            raise RuntimeError(f"Inserted flow artifact {id!r} but could not read it back")
        return dict(row)

    def get_flow_artifact(self, artifact_id: str) -> dict[str, Any] | None:
        row = self.db.get_flow_artifact(artifact_id)
        return dict(row) if row else None

    def list_flow_artifacts(
        self,
        *,
        flow_instance_id: str | None = None,
        stage_instance_id: str | None = None,
        artifact_type: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            dict(row)
            for row in self.db.list_flow_artifacts(
                flow_instance_id=flow_instance_id,
                stage_instance_id=stage_instance_id,
                artifact_type=artifact_type,
            )
        ]


class TypedArtifactFlowService(FlowRuntimeService):
    """Friendly facade over TAFE definition and runtime services."""

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


def _canonical_seed_payload(seed: Mapping[str, Any]) -> dict[str, Any]:
    payload = dict(seed)
    payload["stage_sequence"] = list(seed["stage_sequence"])
    payload["required_roles_by_stage"] = dict(seed["required_roles_by_stage"])
    payload["auq_gate_positions"] = list(seed["auq_gate_positions"])
    payload["never_self_review_stages"] = list(seed["never_self_review_stages"])
    payload["deterministic_carve_outs"] = list(_DETERMINISTIC_CARVE_OUTS)
    payload["workspace_isolation"] = deepcopy(_WORKSPACE_ISOLATION)
    payload["source_spec_ids"] = list(_SOURCE_SPEC_IDS)
    return payload


def _flow_definition_matches_seed(row: Mapping[str, Any], seed: Mapping[str, Any]) -> bool:
    return (
        row.get("flow_type") == seed["flow_type"]
        and row.get("title") == seed["title"]
        and row.get("description") == seed["description"]
        and row.get("status") == "active"
        and _parsed_or_raw(row, "stage_sequence", []) == seed["stage_sequence"]
        and _parsed_or_raw(row, "required_roles_by_stage", {}) == seed["required_roles_by_stage"]
        and _parsed_or_raw(row, "auq_gate_positions", []) == seed["auq_gate_positions"]
        and _parsed_or_raw(row, "never_self_review_stages", []) == seed["never_self_review_stages"]
        and _parsed_or_raw(row, "deterministic_carve_outs", []) == seed["deterministic_carve_outs"]
        and _parsed_or_raw(row, "workspace_isolation", {}) == seed["workspace_isolation"]
        and _parsed_or_raw(row, "source_spec_ids", []) == seed["source_spec_ids"]
    )


def _parsed_or_raw(row: Mapping[str, Any], key: str, default: Any) -> Any:
    parsed_key = f"{key}_parsed"
    if parsed_key in row:
        return row[parsed_key]
    return row.get(key, default)


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


__all__ = [
    "CANONICAL_REVIEWED_TASK_FLOW_DEFINITIONS",
    "FlowDefinitionService",
    "FlowRuntimeService",
    "TypedArtifactFlowService",
    "canonical_reviewed_task_flow_definitions",
]
