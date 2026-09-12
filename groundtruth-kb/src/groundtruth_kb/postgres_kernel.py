"""Native PostgreSQL domain transactions and current-state migration boundary.

This module has no import-time database effects. Operator initialization and
migration use ``gt db postgres``. Ordinary clients use the typed domain service;
they do not receive these internal storage primitives or database credentials.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import sqlite3
import tempfile
from collections.abc import Callable, Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal, DecimalException
from importlib.resources import files
from pathlib import Path
from typing import Any

import psycopg
from psycopg import sql
from psycopg.errors import (
    CheckViolation,
    DataError,
    DeadlockDetected,
    ForeignKeyViolation,
    LockNotAvailable,
    NotNullViolation,
    SerializationFailure,
    UniqueViolation,
)
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from groundtruth_kb.config import PostgreSQLConfig

SCHEMA_VERSION = 1
SCHEMA_FORMAT = "gtkb.postgresql.schema.v1"
# PostgreSQL ships this exact comment on the stock ``public`` schema of a freshly created
# database. It is the absence of kernel metadata, not drift from it, so a table-free ``public``
# schema carrying exactly this string is an uninitialized target (WI-7690). The match is exact:
# no stripping, case folding, JSON fallback, or wildcard, and it applies to no other schema.
STOCK_PUBLIC_SCHEMA_COMMENT = "standard public schema"
TRANSFORM_FORMAT = "gtkb.postgresql.transform.v1"
CURRENT_FORMAT = "gtkb.postgresql.current.v1"
SQLITE_INVENTORY_FORMAT = "gtkb.sqlite.table-inventory.v1"
PG_INTEGER_MIN = -(2**31)
PG_INTEGER_MAX = 2**31 - 1

CURRENT_TABLES = (
    "specifications",
    "specification_deliberation_sources",
    "test_procedures",
    "operational_procedures",
    "environment_config",
    "documents",
    "tests",
    "test_plans",
    "test_plan_phases",
    "work_items",
    "projects",
    "project_work_item_memberships",
    "project_dependencies",
    "project_artifact_links",
    "testable_elements",
    "deliberations",
    "deliberation_specs",
    "deliberation_work_items",
    "canonical_terms",
    "harnesses",
)
COORDINATION_TABLES = ("session_init_bindings", "bridge_attempts", "bridge_items", "work_intent_claims")
MIGRATION_TABLES = (*CURRENT_TABLES, "session_init_bindings")
BINDING_COLUMNS = (
    "native_context_id",
    "session_context_id",
    "subject",
    "role",
    "created_at",
    "minimum_idempotency_identity",
)
ALL_TABLES = (*CURRENT_TABLES, "record_history", *COORDINATION_TABLES)

REBUILT_LATER_TABLES = frozenset(
    {
        "assertion_runs",
        "pipeline_events",
        "sot_quarantine_receipts",
        "work_intent_claims",
    }
)
RETIRED_TABLES = frozenset(
    {
        "session_prompts",
        "dispatch_events",
        "test_coverage",
        "project_authorizations",
        "flow_definitions",
        "flow_instances",
        "stage_instances",
        "flow_events",
        "flow_artifacts",
        "stage_leases",
        "stage_attempt_telemetry",
        "agent_capability_snapshots",
        "dispatch_lanes",
        "dispatch_lane_score_dimensions",
        "dispatch_lane_scoring_evidence",
        "dispatch_lane_score_snapshots",
        "dispatch_lane_projection_snapshots",
        "backlog_snapshots",
        "quality_scores",
        "spec_quality_scores",
        "session_snapshots",
        "sot_registry_observation_capabilities",
        # Obsolete dispatcher projections/metrics; no worker role survives in a lane.
        "dispatch_default_metric_events",
        "dispatch_default_metrics_snapshots",
        "dispatch_lane_matrix",
        "dispatch_lane_projection_metadata",
        # Historical bootstrap permission/effect bundles. Current formal, project,
        # work and test facts migrate through their domain tables; backups retain history.
        "emergency_bootstrap_operational_event_tombstones",
        "emergency_bootstrap_operational_events",
        "governed_operational_events",
        "operational_event_tombstones",
        "operational_event_versions",
        "operational_events",
        # Mutable session containers and duplicate role provenance are not bindings.
        "session_context_envelope_terminal_facts",
        "session_context_envelopes",
        "session_role_attestations",
        # Canonical registry declarations stay in TOML; no projection or
        # observation journal is rebuilt in PostgreSQL.
        "sot_artifacts",
        "sot_artifact_revisions",
        "sot_registry_transaction_journal",
        # Retired per-effect permission and recovery receipts.
        "sot_registry_bridge_publication_capabilities",
        "sot_registry_bridge_recovery_receipts",
        "sot_registry_transition_requests",
        "test_artifact_update_requests",
    }
)
SOURCE_TABLES = frozenset(MIGRATION_TABLES) | REBUILT_LATER_TABLES | RETIRED_TABLES
FORBIDDEN_TABLES = (
    REBUILT_LATER_TABLES | RETIRED_TABLES | frozenset({"authorization_packets", "approval_receipts", "record_heads"})
) - frozenset(COORDINATION_TABLES)
FORBIDDEN_COLUMNS = frozenset(
    {
        "approval_state",
        "membership_role",
        "reviewer_precedence",
        "authorization_name",
        "owner_decision_deliberation_id",
        "related_bridge_threads",
    }
)
_CHANGE_COLUMNS = ("changed_by", "changed_at", "change_reason")
_TIMESTAMP_COLUMNS = frozenset(
    {
        "added_at",
        "changed_at",
        "completed_at",
        "implementation_verified_at",
        "last_corrected_at",
        "last_executed_at",
        "last_verified_at",
        "retired_at",
    }
)
_DATE_COLUMNS = frozenset({"start_date", "target_date", "last_executed_on", "last_verified_on", "last_corrected_on"})
_DATE_PRECISION_FIELDS = {
    "tests": (("last_executed_at", "last_executed_on"),),
    "test_procedures": (("last_executed_at", "last_executed_on"),),
    "test_plan_phases": (("last_executed_at", "last_executed_on"),),
    "operational_procedures": (
        ("last_verified_at", "last_verified_on"),
        ("last_corrected_at", "last_corrected_on"),
    ),
}
_INTEGER_COLUMNS = frozenset(
    {
        "assertion_count",
        "implementation_order",
        "membership_order",
        "phase_order",
        "rank",
        "registry_version",
        "version",
    }
)
_REQUIRED_COLUMNS: dict[str, frozenset[str]] = {
    "specifications": frozenset({"id", "version", "title", "status", *_CHANGE_COLUMNS}),
    "specification_deliberation_sources": frozenset({"spec_id", "deliberation_id", "version", "added_at", "added_by"}),
    "test_procedures": frozenset({"id", "version", "title", *_CHANGE_COLUMNS}),
    "operational_procedures": frozenset({"id", "version", "title", *_CHANGE_COLUMNS}),
    "environment_config": frozenset(
        {"id", "version", "environment", "category", "key", "value", "sensitive", *_CHANGE_COLUMNS}
    ),
    "documents": frozenset({"id", "version", "title", "category", "status", *_CHANGE_COLUMNS}),
    "tests": frozenset({"id", "version", "title", "spec_id", "test_type", "expected_outcome", *_CHANGE_COLUMNS}),
    "test_plans": frozenset({"id", "version", "title", "status", *_CHANGE_COLUMNS}),
    "test_plan_phases": frozenset(
        {"id", "version", "plan_id", "phase_order", "title", "gate_criteria", *_CHANGE_COLUMNS}
    ),
    "work_items": frozenset(
        {"id", "version", "title", "origin", "component", "resolution_status", "stage", *_CHANGE_COLUMNS}
    ),
    "projects": frozenset({"id", "version", "name", "kind", "status", *_CHANGE_COLUMNS}),
    "project_work_item_memberships": frozenset(
        {"id", "version", "project_id", "work_item_id", "status", *_CHANGE_COLUMNS}
    ),
    "project_dependencies": frozenset(
        {
            "id",
            "version",
            "dependent_project_id",
            "prerequisite_project_id",
            "dependency_kind",
            "required_prerequisite_state",
            "affected_gate",
            "provenance",
            "registry_version",
            "blocking_status",
            "status",
            *_CHANGE_COLUMNS,
        }
    ),
    "project_artifact_links": frozenset(
        {
            "id",
            "version",
            "project_id",
            "artifact_type",
            "artifact_ref",
            "relationship",
            "status",
            *_CHANGE_COLUMNS,
        }
    ),
    "testable_elements": frozenset(
        {
            "id",
            "version",
            "subsystem",
            "page_or_module",
            "name",
            "element_type",
            "expected_behavior",
            "applicable_dimensions",
            "status",
            *_CHANGE_COLUMNS,
        }
    ),
    "deliberations": frozenset({"id", "version", "source_type", "title", "summary", "content", *_CHANGE_COLUMNS}),
    "deliberation_specs": frozenset({"deliberation_id", "spec_id", "version"}),
    "deliberation_work_items": frozenset({"deliberation_id", "work_item_id", "version"}),
    "canonical_terms": frozenset(
        {
            "id",
            "version",
            "canonical_term",
            "definition",
            "authority_level",
            "scope",
            "lifecycle_status",
            "source_authority",
            *_CHANGE_COLUMNS,
        }
    ),
    "harnesses": frozenset({"id", "version", "harness_name", "harness_type", "status", *_CHANGE_COLUMNS}),
}


@dataclass(frozen=True)
class TableSpec:
    name: str
    identity_columns: tuple[str, ...]
    columns: tuple[str, ...]
    json_columns: frozenset[str] = frozenset()
    boolean_columns: frozenset[str] = frozenset()


def _table(
    name: str,
    identity: Sequence[str],
    columns: Sequence[str],
    *,
    json_columns: Iterable[str] = (),
    boolean_columns: Iterable[str] = (),
) -> TableSpec:
    return TableSpec(
        name=name,
        identity_columns=tuple(identity),
        columns=tuple(columns),
        json_columns=frozenset(json_columns),
        boolean_columns=frozenset(boolean_columns),
    )


TABLE_SPECS: dict[str, TableSpec] = {
    "specifications": _table(
        "specifications",
        ("id",),
        (
            "id",
            "version",
            "title",
            "description",
            "priority",
            "scope",
            "section",
            "handle",
            "tags",
            "status",
            "assertions",
            "type",
            "authority",
            "provisional_until",
            "constraints",
            "affected_by",
            "testability",
            "source_paths",
            "implementation_verified_at",
            "retired_at",
            "parent",
            "application_scope",
            *_CHANGE_COLUMNS,
        ),
        json_columns=("tags", "assertions", "constraints", "affected_by", "source_paths"),
    ),
    "specification_deliberation_sources": _table(
        "specification_deliberation_sources",
        ("spec_id", "deliberation_id"),
        ("spec_id", "deliberation_id", "version", "source_role", "added_at", "added_by"),
    ),
    "test_procedures": _table(
        "test_procedures",
        ("id",),
        (
            "id",
            "version",
            "title",
            "type",
            "content",
            "assertion_count",
            "last_execution_status",
            "last_executed_at",
            "last_executed_on",
            *_CHANGE_COLUMNS,
        ),
    ),
    "operational_procedures": _table(
        "operational_procedures",
        ("id",),
        (
            "id",
            "version",
            "title",
            "type",
            "variables",
            "steps",
            "known_failure_modes",
            "last_verified_at",
            "last_verified_on",
            "last_corrected_at",
            "last_corrected_on",
            *_CHANGE_COLUMNS,
        ),
        json_columns=("variables", "steps", "known_failure_modes"),
    ),
    "environment_config": _table(
        "environment_config",
        ("id",),
        ("id", "version", "environment", "category", "key", "value", "sensitive", "notes", *_CHANGE_COLUMNS),
        boolean_columns=("sensitive",),
    ),
    "documents": _table(
        "documents",
        ("id",),
        ("id", "version", "title", "category", "content", "tags", "status", "source_path", *_CHANGE_COLUMNS),
        json_columns=("tags",),
    ),
    "tests": _table(
        "tests",
        ("id",),
        (
            "id",
            "version",
            "title",
            "spec_id",
            "test_type",
            "test_file",
            "test_class",
            "test_function",
            "description",
            "expected_outcome",
            "last_result",
            "last_executed_at",
            "last_executed_on",
            "application_scope",
            *_CHANGE_COLUMNS,
        ),
    ),
    "test_plans": _table(
        "test_plans",
        ("id",),
        ("id", "version", "title", "description", "status", *_CHANGE_COLUMNS),
    ),
    "test_plan_phases": _table(
        "test_plan_phases",
        ("id",),
        (
            "id",
            "version",
            "plan_id",
            "phase_order",
            "title",
            "description",
            "gate_criteria",
            "test_ids",
            "last_result",
            "last_executed_at",
            "last_executed_on",
            *_CHANGE_COLUMNS,
        ),
        json_columns=("test_ids",),
    ),
    "work_items": _table(
        "work_items",
        ("id",),
        (
            "id",
            "version",
            "title",
            "description",
            "origin",
            "component",
            "source_spec_id",
            "source_test_id",
            "failure_description",
            "resolution_status",
            "priority",
            "stage",
            "implementation_order",
            "status_detail",
            "source_owner_directive",
            "source_deliberation_query",
            "related_deliberation_ids",
            "related_spec_ids_at_creation",
            "depends_on_work_items",
            "blocks_work_items",
            "acceptance_summary",
            "regression_visibility",
            "completion_evidence",
            "supersedes",
            "superseded_by",
            *_CHANGE_COLUMNS,
        ),
        json_columns=(
            "related_deliberation_ids",
            "related_spec_ids_at_creation",
            "depends_on_work_items",
            "blocks_work_items",
            "supersedes",
            "superseded_by",
        ),
    ),
    "projects": _table(
        "projects",
        ("id",),
        (
            "id",
            "version",
            "name",
            "kind",
            "status",
            "authorization",
            "rank",
            "parent_project_id",
            "purpose",
            "target_outcome",
            "scope_note",
            "start_date",
            "target_date",
            "completed_at",
            "notes",
            "source_project_name",
            "source_subproject_name",
            *_CHANGE_COLUMNS,
        ),
    ),
    "project_work_item_memberships": _table(
        "project_work_item_memberships",
        ("id",),
        (
            "id",
            "version",
            "project_id",
            "work_item_id",
            "membership_order",
            "status",
            "source",
            *_CHANGE_COLUMNS,
        ),
    ),
    "project_dependencies": _table(
        "project_dependencies",
        ("id",),
        (
            "id",
            "version",
            "dependent_project_id",
            "prerequisite_project_id",
            "dependency_kind",
            "required_prerequisite_state",
            "affected_gate",
            "provenance",
            "registry_version",
            "rationale",
            "blocking_status",
            "related_work_item_id",
            "status",
            *_CHANGE_COLUMNS,
        ),
    ),
    "project_artifact_links": _table(
        "project_artifact_links",
        ("id",),
        (
            "id",
            "version",
            "project_id",
            "artifact_type",
            "artifact_ref",
            "relationship",
            "status",
            "notes",
            *_CHANGE_COLUMNS,
        ),
    ),
    "testable_elements": _table(
        "testable_elements",
        ("id",),
        (
            "id",
            "version",
            "subsystem",
            "page_or_module",
            "name",
            "element_type",
            "expected_behavior",
            "spec_id",
            "applicable_dimensions",
            "status",
            *_CHANGE_COLUMNS,
        ),
        json_columns=("applicable_dimensions",),
    ),
    "deliberations": _table(
        "deliberations",
        ("id",),
        (
            "id",
            "version",
            "spec_id",
            "work_item_id",
            "source_type",
            "source_ref",
            "title",
            "summary",
            "content",
            "content_hash",
            "participants",
            "outcome",
            "session_id",
            "sensitivity",
            "redaction_state",
            "redaction_notes",
            "origin_project",
            "origin_repo",
            *_CHANGE_COLUMNS,
        ),
        json_columns=("participants",),
    ),
    "deliberation_specs": _table(
        "deliberation_specs",
        ("deliberation_id", "spec_id"),
        ("deliberation_id", "spec_id", "version", "role"),
    ),
    "deliberation_work_items": _table(
        "deliberation_work_items",
        ("deliberation_id", "work_item_id"),
        ("deliberation_id", "work_item_id", "version", "role"),
    ),
    "canonical_terms": _table(
        "canonical_terms",
        ("id",),
        (
            "id",
            "version",
            "canonical_term",
            "definition",
            "authority_level",
            "scope",
            "accepted_synonyms",
            "discouraged_synonyms",
            "linked_artifacts",
            "linked_services",
            "usage_examples",
            "forbidden_uses",
            "lifecycle_status",
            "source_authority",
            *_CHANGE_COLUMNS,
        ),
        json_columns=(
            "accepted_synonyms",
            "discouraged_synonyms",
            "linked_artifacts",
            "linked_services",
            "usage_examples",
            "forbidden_uses",
        ),
    ),
    "harnesses": _table(
        "harnesses",
        ("id",),
        (
            "id",
            "version",
            "harness_name",
            "harness_type",
            "status",
            "invocation_surfaces",
            "capabilities_ref",
            *_CHANGE_COLUMNS,
        ),
        json_columns=("invocation_surfaces",),
    ),
}


class PostgresKernelError(Exception):
    """Credential-free, stable operational error returned by the public CLI."""

    def __init__(self, code: str, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_json_dict(self) -> dict[str, Any]:
        error: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details:
            error["details"] = self.details
        return {"error": error}


def canonical_json_bytes(value: object) -> bytes:
    """Return compact, key-sorted RFC 8259 JSON followed by exactly one LF."""
    try:
        _validate_json_value(value)
        rendered = _render_canonical_json(value)
    except (RecursionError, TypeError, ValueError) as exc:
        raise PostgresKernelError("invalid_json", "Value cannot be represented as canonical JSON") from exc
    return (rendered + "\n").encode("utf-8")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _validate_text(value: str, *, label: str = "text") -> None:
    if "\x00" in value:
        raise PostgresKernelError("invalid_text", f"{label} contains NUL")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise PostgresKernelError("invalid_text", f"{label} contains an unpaired surrogate") from exc


def _validate_json_value(value: object) -> None:
    pending: list[tuple[object, int]] = [(value, 0)]
    while pending:
        item, depth = pending.pop()
        if depth > 512:
            raise PostgresKernelError("invalid_json", "JSON nesting exceeds the supported limit")
        if item is None or isinstance(item, bool):
            continue
        if isinstance(item, int):
            _canonical_number_text(item)
            continue
        if isinstance(item, (Decimal, float)):
            is_finite = item.is_finite() if isinstance(item, Decimal) else math.isfinite(item)
            if not is_finite:
                raise PostgresKernelError("invalid_json", "NaN and Infinity are not valid RFC 8259 numbers")
            _canonical_number_text(item)
            continue
        if isinstance(item, str):
            _validate_text(item)
            continue
        if isinstance(item, list):
            pending.extend((child, depth + 1) for child in item)
            continue
        if isinstance(item, dict):
            for key, child in item.items():
                if not isinstance(key, str):
                    raise PostgresKernelError("invalid_json", "JSON object keys must be strings")
                _validate_text(key, label="JSON object key")
                pending.append((child, depth + 1))
            continue
        raise PostgresKernelError("invalid_json", f"Unsupported JSON value type: {type(item).__name__}")


def _canonical_number_text(value: int | float | Decimal) -> str:
    if isinstance(value, int):
        rendered = _integer_text(value)
        if len(rendered.removeprefix("-")) > 131_072:
            raise PostgresKernelError("invalid_json", "JSON number exceeds PostgreSQL numeric range")
        return rendered
    decimal_value = value if isinstance(value, Decimal) else Decimal(repr(value))
    if not decimal_value.is_finite():
        raise PostgresKernelError("invalid_json", "NaN and Infinity are not valid RFC 8259 numbers")
    sign, digits_tuple, exponent = decimal_value.as_tuple()
    if not isinstance(exponent, int):
        raise PostgresKernelError("invalid_json", "NaN and Infinity are not valid RFC 8259 numbers")
    digits = "".join(str(digit) for digit in digits_tuple) or "0"
    if not any(digits_tuple):
        if exponent < 0:
            fractional_digits = -exponent
            if fractional_digits > 16_383:
                raise PostgresKernelError("invalid_json", "JSON number exceeds PostgreSQL numeric range")
            return "0." + ("0" * fractional_digits)
        return "0"
    digits_before = len(digits) + exponent
    fractional_digits = max(-exponent, 0)
    if max(digits_before, 0) > 131_072 or fractional_digits > 16_383:
        raise PostgresKernelError("invalid_json", "JSON number exceeds PostgreSQL numeric range")
    if exponent >= 0:
        rendered = digits + ("0" * exponent)
    elif digits_before > 0:
        rendered = digits[:digits_before] + "." + digits[digits_before:]
    else:
        rendered = "0." + ("0" * -digits_before) + digits
    return ("-" if sign else "") + rendered


def _integer_text(value: int) -> str:
    """Render an integer without Python's process-configurable digit limit."""
    if value == 0:
        return "0"
    negative = value < 0
    remaining = -value if negative else value
    chunks: list[int] = []
    while remaining:
        remaining, chunk = divmod(remaining, 1_000_000_000)
        chunks.append(chunk)
    rendered = str(chunks.pop())
    rendered += "".join(f"{chunk:09d}" for chunk in reversed(chunks))
    return "-" + rendered if negative else rendered


def _parse_integer_token(token: str) -> int:
    negative = token.startswith("-")
    digits = token[1:] if negative else token
    if len(digits) > 131_072:
        raise PostgresKernelError("invalid_json", "JSON number exceeds PostgreSQL numeric range")
    first_width = len(digits) % 9 or 9
    value = int(digits[:first_width])
    for offset in range(first_width, len(digits), 9):
        value = value * 1_000_000_000 + int(digits[offset : offset + 9])
    return -value if negative else value


def _parse_decimal_token(token: str) -> Decimal:
    try:
        return Decimal(token)
    except (DecimalException, ValueError) as exc:
        raise PostgresKernelError("invalid_json", "JSON number exceeds the supported decimal range") from exc


def _render_canonical_json(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float, Decimal)):
        return _canonical_number_text(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)
    if isinstance(value, list):
        return "[" + ",".join(_render_canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        return (
            "{"
            + ",".join(
                f"{json.dumps(key, ensure_ascii=False, allow_nan=False)}:{_render_canonical_json(value[key])}"
                for key in sorted(value)
            )
            + "}"
        )
    raise PostgresKernelError("invalid_json", f"Unsupported JSON value type: {type(value).__name__}")


def _reject_constant(value: str) -> None:
    raise PostgresKernelError("invalid_json", f"Non-RFC-8259 number is forbidden: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PostgresKernelError("duplicate_json_key", f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_bytes(raw: bytes) -> Any:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise PostgresKernelError("invalid_json", "UTF-8 BOM is forbidden")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PostgresKernelError("invalid_json", "Input is not valid UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_parse_decimal_token,
            parse_int=_parse_integer_token,
        )
        _validate_json_value(value)
    except PostgresKernelError:
        raise
    except (ValueError, RecursionError) as exc:
        raise PostgresKernelError("invalid_json", "Input is not valid JSON") from exc
    return value


def _postgres_json_dumps(value: object) -> str:
    """Serialize JSONB inputs with the same exact numeric contract as manifests."""
    return canonical_json_bytes(value).decode("utf-8").removesuffix("\n")


def _canonical_sql_resource_bytes(raw: bytes) -> bytes:
    if raw.startswith(b"\xef\xbb\xbf"):
        raise PostgresKernelError("schema_resource_invalid", "Packaged PostgreSQL schema has a UTF-8 BOM")
    normalized = raw.replace(b"\r\n", b"\n")
    if b"\r" in normalized:
        raise PostgresKernelError("schema_resource_invalid", "Packaged PostgreSQL schema has a bare CR")
    return normalized


def schema_sql_bytes() -> bytes:
    return _canonical_sql_resource_bytes(files("groundtruth_kb").joinpath("postgresql_v1.sql").read_bytes())


def schema_sql_sha256() -> str:
    return hashlib.sha256(schema_sql_bytes()).hexdigest()


def _schema_metadata(*, catalog_sha256: str) -> dict[str, Any]:
    return {
        "catalog_sha256": catalog_sha256,
        "format": SCHEMA_FORMAT,
        "schema_sha256": schema_sql_sha256(),
        "schema_version": SCHEMA_VERSION,
    }


def _ascii_lower(value: str) -> str:
    return "".join(chr(ord(char) + 32) if "A" <= char <= "Z" else char for char in value)


def _strict_bool(value: object, *, label: str) -> bool:
    if type(value) is not int or value not in (0, 1):
        raise PostgresKernelError("invalid_sqlite_inventory", f"{label} must be SQLite boolean 0 or 1")
    return bool(value)


def normalize_table_inventory(
    table_list_rows: Sequence[Mapping[str, Any]],
    column_rows: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    """Validate and normalize already-read SQLite inventory rows without I/O."""
    seen_exact: set[str] = set()
    seen_folded: set[str] = set()
    tables: list[dict[str, Any]] = []
    for raw_table in table_list_rows:
        name = raw_table.get("name")
        kind = raw_table.get("type")
        if not isinstance(name, str) or not name or not isinstance(kind, str):
            raise PostgresKernelError("invalid_sqlite_inventory", "SQLite table name and kind must be text")
        _validate_text(name, label="SQLite table name")
        if name in seen_exact or _ascii_lower(name) in seen_folded:
            raise PostgresKernelError("invalid_sqlite_inventory", f"Duplicate SQLite table name: {name}")
        if kind not in {"table", "virtual", "shadow"}:
            raise PostgresKernelError("invalid_sqlite_inventory", f"Unsupported SQLite table kind: {kind}")
        seen_exact.add(name)
        seen_folded.add(_ascii_lower(name))

        raw_columns = list(column_rows.get(name, ()))
        expected_count = raw_table.get("ncol")
        if (
            not isinstance(expected_count, int)
            or isinstance(expected_count, bool)
            or expected_count != len(raw_columns)
        ):
            raise PostgresKernelError("invalid_sqlite_inventory", f"Column-count disagreement for SQLite table: {name}")
        normalized_columns: list[dict[str, Any]] = []
        seen_column_exact: set[str] = set()
        seen_column_folded: set[str] = set()
        cids: list[int] = []
        for raw_column in raw_columns:
            cid = raw_column.get("cid")
            column_name = raw_column.get("name")
            declared_type = raw_column.get("type")
            default_sql = raw_column.get("dflt_value")
            hidden = raw_column.get("hidden")
            primary_key = raw_column.get("pk")
            if not isinstance(cid, int) or isinstance(cid, bool) or cid < 0:
                raise PostgresKernelError("invalid_sqlite_inventory", f"Invalid column id in SQLite table: {name}")
            if not isinstance(column_name, str) or not isinstance(declared_type, str):
                raise PostgresKernelError("invalid_sqlite_inventory", f"Invalid column text in SQLite table: {name}")
            _validate_text(column_name, label="SQLite column name")
            _validate_text(declared_type, label="SQLite declared type")
            if default_sql is not None:
                if not isinstance(default_sql, str):
                    raise PostgresKernelError(
                        "invalid_sqlite_inventory", f"Invalid default SQL in SQLite table: {name}"
                    )
                _validate_text(default_sql, label="SQLite default SQL")
            if column_name in seen_column_exact or _ascii_lower(column_name) in seen_column_folded:
                raise PostgresKernelError("invalid_sqlite_inventory", f"Duplicate SQLite column name in table: {name}")
            if not isinstance(hidden, int) or isinstance(hidden, bool) or hidden not in range(4):
                raise PostgresKernelError("invalid_sqlite_inventory", f"Invalid hidden flag in SQLite table: {name}")
            if not isinstance(primary_key, int) or isinstance(primary_key, bool) or primary_key < 0:
                raise PostgresKernelError(
                    "invalid_sqlite_inventory", f"Invalid primary-key ordinal in SQLite table: {name}"
                )
            seen_column_exact.add(column_name)
            seen_column_folded.add(_ascii_lower(column_name))
            cids.append(cid)
            normalized_columns.append(
                {
                    "cid": cid,
                    "declared_type": declared_type,
                    "default_sql": default_sql,
                    "hidden": hidden,
                    "name": column_name,
                    "not_null": _strict_bool(raw_column.get("notnull"), label="not_null"),
                    "primary_key_ordinal": primary_key,
                }
            )
        if sorted(cids) != list(range(len(raw_columns))):
            raise PostgresKernelError("invalid_sqlite_inventory", f"Noncontiguous column ids in SQLite table: {name}")
        normalized_columns.sort(key=lambda row: row["cid"])
        tables.append(
            {
                "columns": normalized_columns,
                "kind": kind,
                "name": name,
                "strict": _strict_bool(raw_table.get("strict"), label="strict"),
                "without_rowid": _strict_bool(raw_table.get("wr"), label="without_rowid"),
            }
        )
    tables.sort(key=lambda row: (str(row["name"]).encode("utf-8"), str(row["kind"])))
    return {"format": SQLITE_INVENTORY_FORMAT, "tables": tables}


_LOWER_SHA_RE = re.compile(r"[0-9a-f]{64}\Z")


def _exact_keys(value: object, expected: set[str], *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PostgresKernelError("invalid_contract", f"{label} must be an object")
    actual = set(value)
    if actual != expected:
        raise PostgresKernelError(
            "invalid_contract",
            f"{label} has missing or unknown keys",
            details={"missing": sorted(expected - actual), "unknown": sorted(actual - expected)},
        )
    return value


def _nonnegative_int(value: object, *, label: str, positive: bool = False) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < (1 if positive else 0):
        qualifier = "positive" if positive else "nonnegative"
        raise PostgresKernelError("invalid_contract", f"{label} must be a {qualifier} integer")
    return value


def _opaque_id(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise PostgresKernelError("invalid_contract", f"{label} must be a non-empty opaque string")
    _validate_text(value, label=label)
    return value


def validate_transform_plan(value: object) -> dict[str, Any]:
    plan = _exact_keys(value, {"format", "schema_version", "source", "projects", "project_dependencies"}, label="plan")
    if (
        plan["format"] != TRANSFORM_FORMAT
        or type(plan["schema_version"]) is not int
        or plan["schema_version"] != SCHEMA_VERSION
    ):
        raise PostgresKernelError("invalid_transform_plan", "Unsupported transform-plan format or schema version")

    source = _exact_keys(
        plan["source"],
        {
            "sqlite_snapshot_sha256",
            "sqlite_snapshot_size_bytes",
            "expected_pragma_user_version",
            "expected_table_inventory_sha256",
        },
        label="plan.source",
    )
    for key in ("sqlite_snapshot_sha256", "expected_table_inventory_sha256"):
        if not isinstance(source[key], str) or not _LOWER_SHA_RE.fullmatch(source[key]):
            raise PostgresKernelError("invalid_transform_plan", f"plan.source.{key} must be lowercase SHA-256")
    _nonnegative_int(source["sqlite_snapshot_size_bytes"], label="snapshot size", positive=True)
    _nonnegative_int(source["expected_pragma_user_version"], label="PRAGMA user_version")

    projects = _exact_keys(
        plan["projects"],
        {
            "expected_total",
            "expected_programs",
            "expected_authorized",
            "expected_not_authorized",
        },
        label="plan.projects",
    )
    expected_total = _nonnegative_int(projects["expected_total"], label="project total")
    expected_authorized = _nonnegative_int(projects["expected_authorized"], label="authorized project count")
    expected_not_authorized = _nonnegative_int(
        projects["expected_not_authorized"], label="not-authorized project count"
    )
    expected_programs = _nonnegative_int(projects["expected_programs"], label="program count")
    if expected_authorized + expected_not_authorized + expected_programs != expected_total:
        raise PostgresKernelError("invalid_transform_plan", "Project authorization counts do not sum to expected_total")

    dependencies = _exact_keys(
        plan["project_dependencies"],
        {
            "expected_source_count",
            "affected_gate_from",
            "affected_gate_to",
            "expected_gate_transition_count",
            "retire_dependency_ids",
            "preserve_dependency_ids",
            "expected_active_after",
            "expected_retired_after",
        },
        label="plan.project_dependencies",
    )
    expected_source_count = _nonnegative_int(dependencies["expected_source_count"], label="dependency source count")
    expected_active = _nonnegative_int(dependencies["expected_active_after"], label="active dependency count")
    expected_retired = _nonnegative_int(dependencies["expected_retired_after"], label="retired dependency count")
    expected_gate = _nonnegative_int(
        dependencies["expected_gate_transition_count"], label="dependency gate-transition count"
    )
    if dependencies["affected_gate_from"] != "authorization" or dependencies["affected_gate_to"] != "readiness":
        raise PostgresKernelError(
            "invalid_transform_plan", "Dependency gate transition must be authorization to readiness"
        )
    if expected_active + expected_retired != expected_source_count or expected_gate > expected_source_count:
        raise PostgresKernelError("invalid_transform_plan", "Dependency counts are inconsistent")
    all_dependency_ids: set[str] = set()
    for list_name in ("retire_dependency_ids", "preserve_dependency_ids"):
        values = dependencies[list_name]
        if not isinstance(values, list):
            raise PostgresKernelError("invalid_transform_plan", f"{list_name} must be an array")
        for raw_id in values:
            dependency_id = _opaque_id(raw_id, label=list_name)
            if dependency_id in all_dependency_ids:
                raise PostgresKernelError("invalid_transform_plan", f"Duplicate dependency id: {dependency_id}")
            all_dependency_ids.add(dependency_id)
    if len(all_dependency_ids) != expected_source_count:
        raise PostgresKernelError("invalid_transform_plan", "Dependency lists do not account for expected_source_count")
    return plan


def _identity_key(spec: TableSpec, row: Mapping[str, Any]) -> tuple[bytes, ...]:
    values: list[bytes] = []
    for column in spec.identity_columns:
        value = row.get(column)
        if not isinstance(value, str) or not value:
            raise PostgresKernelError("invalid_manifest", f"{spec.name}.{column} must be non-empty text")
        _validate_text(value, label=f"{spec.name}.{column}")
        values.append(value.encode("utf-8"))
    return tuple(values)


def _canonical_timestamp(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        _validate_text(value, label=label)
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise PostgresKernelError("invalid_timestamp", f"{label} must be RFC 3339") from exc
    else:
        raise PostgresKernelError("invalid_timestamp", f"{label} must be RFC 3339 text")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise PostgresKernelError("invalid_timestamp", f"{label} must include an offset")
    try:
        return parsed.astimezone(UTC).isoformat()
    except (OverflowError, ValueError) as exc:
        raise PostgresKernelError("invalid_timestamp", f"{label} is outside the UTC timestamp range") from exc


def _canonical_date(value: object, *, label: str) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        raise PostgresKernelError("invalid_date", f"{label} must be an ISO date")
    if isinstance(value, date):
        parsed = value
    elif isinstance(value, str):
        _validate_text(value, label=label)
        try:
            parsed = date.fromisoformat(value)
        except ValueError as exc:
            raise PostgresKernelError("invalid_date", f"{label} must be an ISO date") from exc
    else:
        raise PostgresKernelError("invalid_date", f"{label} must be an ISO date")
    return parsed.isoformat()


def _require_reference(value: object, allowed: set[str], *, label: str) -> None:
    if value is not None and value not in allowed:
        raise PostgresKernelError("invalid_manifest", f"{label} references a missing current record")


def dependency_shape(record: Mapping[str, Any]) -> bool:
    """The native dependency contract has exact states, never completion aliases."""
    return (
        record.get("dependency_kind") == "requires_project_state"
        and record.get("required_prerequisite_state") in {"active", "verified", "retired", "cancelled"}
        and record.get("affected_gate") in {"readiness", "closure"}
        and isinstance(record.get("rationale"), str)
        and bool(record["rationale"].strip())
    )


def validate_project_dependencies(records: list[dict[str, Any]], projects: dict[str, dict[str, Any]]) -> None:
    """Validate the same current graph for native writes and migration input."""
    edges, semantic = {}, set()
    for record in records:
        if record["status"] != "active":
            continue
        if not dependency_shape(record):
            raise PostgresKernelError(
                "invalid_dependency_contract",
                "Reconcile the dependency kind, exact state, gate and rationale",
                details={"id": record["id"]},
            )
        dependent, prerequisite = record["dependent_project_id"], record["prerequisite_project_id"]
        for key in (dependent, prerequisite):
            if key not in projects or projects[key]["kind"] != "project":
                raise PostgresKernelError(
                    "invalid_dependency_endpoint", "Dependencies sequence execution projects", details={"id": key}
                )
        key = (dependent, prerequisite, record["affected_gate"])
        if key in semantic:
            raise PostgresKernelError(
                "duplicate_dependency", "One prerequisite state per project pair and gate is sufficient"
            )
        semantic.add(key)
        edges.setdefault(dependent, set()).add(prerequisite)
        edges.setdefault(prerequisite, set())
    # Closed outcomes remain in the graph; readiness evaluates their state.
    # Iterative cycle detection does not depend on the Python recursion limit.
    pending = {key: set(value) for key, value in edges.items()}
    while pending:
        leaves = {key for key, values in pending.items() if not values}
        if not leaves:
            raise PostgresKernelError(
                "dependency_cycle",
                "The active project dependency graph contains a cycle",
                details={"projects": sorted(pending)},
            )
        pending = {key: values - leaves for key, values in pending.items() if key not in leaves}


def validate_work_item_dependencies(records: list[dict[str, Any]]) -> None:
    """Require the same executable predecessor graph on import and ordinary writes."""
    rows = {row["id"]: row for row in records}
    edges = {}
    for key, row in rows.items():
        dependencies = row.get("depends_on_work_items")
        if dependencies is None:
            dependencies = []
        if not isinstance(dependencies, list) or any(
            not isinstance(value, str)
            or len(value) > 256
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", value) is None
            for value in dependencies
        ):
            raise PostgresKernelError(
                "invalid_work_item_dependencies",
                "Work-item predecessors must be identifier strings; "
                "reconcile legacy predicates and non-work references",
                details={"work_item_id": key},
            )
        if len(set(dependencies)) != len(dependencies):
            raise PostgresKernelError(
                "duplicate_work_item_dependency",
                "A work item names each predecessor once",
                details={"work_item_id": key},
            )
        missing = sorted(set(dependencies) - rows.keys())
        if missing:
            raise PostgresKernelError(
                "missing_work_item_dependency",
                "Every predecessor must resolve to a current work item",
                details={"work_item_id": key, "missing_work_item_ids": missing},
            )
        edges[key] = dependencies

    # An iterative DFS reports the actual cycle, not unrelated nodes waiting on it.
    # Closed source labels do not make an invalid current graph safe to migrate.
    complete = set()
    for root in edges:
        if root in complete:
            continue
        path, positions = [root], {root: 0}
        stack = [iter(edges[root])]
        while stack:
            predecessor = next(stack[-1], None)
            if predecessor is None:
                finished = path.pop()
                complete.add(finished)
                positions.pop(finished)
                stack.pop()
            elif predecessor in positions:
                raise PostgresKernelError(
                    "dependency_cycle",
                    "The current work-item predecessor graph contains a cycle",
                    details={"work_item_ids": path[positions[predecessor] :] + [predecessor]},
                )
            elif predecessor not in complete:
                positions[predecessor] = len(path)
                path.append(predecessor)
                stack.append(iter(edges[predecessor]))


def _validate_manifest_relationships(tables: Mapping[str, list[dict[str, Any]]]) -> None:
    ids = {
        table_name: {str(row["id"]) for row in tables[table_name]}
        for table_name in ("specifications", "tests", "test_plans", "work_items", "projects", "deliberations")
    }

    for row in tables["specifications"]:
        _require_reference(row["parent"], ids["specifications"], label="specifications.parent")
        _require_reference(row["provisional_until"], ids["specifications"], label="specifications.provisional_until")
    for row in tables["specification_deliberation_sources"]:
        _require_reference(row["spec_id"], ids["specifications"], label="source.spec_id")
        _require_reference(row["deliberation_id"], ids["deliberations"], label="source.deliberation_id")
    for row in tables["tests"]:
        _require_reference(row["spec_id"], ids["specifications"], label="tests.spec_id")
    for row in tables["test_plan_phases"]:
        _require_reference(row["plan_id"], ids["test_plans"], label="test_plan_phases.plan_id")
    for row in tables["work_items"]:
        _require_reference(row["source_spec_id"], ids["specifications"], label="work_items.source_spec_id")
        _require_reference(row["source_test_id"], ids["tests"], label="work_items.source_test_id")
    validate_work_item_dependencies(tables["work_items"])
    projects = {row["id"]: row for row in tables["projects"]}
    for row in tables["projects"]:
        _require_reference(row["parent_project_id"], ids["projects"], label="projects.parent_project_id")
        parent_id = row["parent_project_id"]
        if parent_id is not None and (row["kind"] != "project" or projects[parent_id]["kind"] != "program"):
            raise PostgresKernelError("invalid_manifest", "Only a program can contain execution projects")

    membership_pairs: set[tuple[str, str]] = set()
    active_parent_counts: dict[str, int] = {}
    for row in tables["project_work_item_memberships"]:
        _require_reference(row["project_id"], ids["projects"], label="membership.project_id")
        _require_reference(row["work_item_id"], ids["work_items"], label="membership.work_item_id")
        pair = (row["project_id"], row["work_item_id"])
        if pair in membership_pairs:
            raise PostgresKernelError("invalid_manifest", "Duplicate current project/work-item relationship")
        membership_pairs.add(pair)
        if row["status"] == "active":
            if projects[row["project_id"]]["kind"] != "project":
                raise PostgresKernelError("invalid_manifest", "A program cannot contain work items")
            active_parent_counts[row["work_item_id"]] = active_parent_counts.get(row["work_item_id"], 0) + 1

    # Open work is constituted under exactly one execution project; intake and
    # every native membership write keep that rule. Closed work migrates with
    # its recorded membership history exactly: zero or several active rows are
    # historical facts that are neither repaired nor fabricated here.
    open_items = {str(row["id"]) for row in tables["work_items"] if row.get("resolution_status") == "open"}
    multiple_parents = sorted(item for item in open_items if active_parent_counts.get(item, 0) > 1)
    if multiple_parents:
        raise PostgresKernelError(
            "invalid_manifest",
            "An open work item cannot have multiple active parent projects",
            details={"work_item_ids": multiple_parents[:20]},
        )
    missing_parents = sorted(item for item in open_items if active_parent_counts.get(item, 0) == 0)
    if missing_parents:
        raise PostgresKernelError(
            "invalid_manifest",
            "Every open work item requires one active parent project",
            details={"missing_parent_count": len(missing_parents), "work_item_ids": missing_parents[:20]},
        )

    for row in tables["project_dependencies"]:
        _require_reference(row["dependent_project_id"], ids["projects"], label="dependency.dependent_project_id")
        _require_reference(
            row["prerequisite_project_id"],
            ids["projects"],
            label="dependency.prerequisite_project_id",
        )
        _require_reference(row["related_work_item_id"], ids["work_items"], label="dependency.related_work_item_id")
    validate_project_dependencies(tables["project_dependencies"], projects)
    for row in tables["project_artifact_links"]:
        _require_reference(row["project_id"], ids["projects"], label="artifact_link.project_id")
    for row in tables["testable_elements"]:
        _require_reference(row["spec_id"], ids["specifications"], label="testable_element.spec_id")
    for row in tables["deliberations"]:
        _require_reference(row["spec_id"], ids["specifications"], label="deliberation.spec_id")
        _require_reference(row["work_item_id"], ids["work_items"], label="deliberation.work_item_id")
    for row in tables["deliberation_specs"]:
        _require_reference(row["deliberation_id"], ids["deliberations"], label="deliberation_specs.deliberation_id")
        _require_reference(row["spec_id"], ids["specifications"], label="deliberation_specs.spec_id")
    for row in tables["deliberation_work_items"]:
        _require_reference(
            row["deliberation_id"],
            ids["deliberations"],
            label="deliberation_work_items.deliberation_id",
        )
        _require_reference(row["work_item_id"], ids["work_items"], label="deliberation_work_items.work_item_id")

    environment_keys: set[tuple[str, str, str]] = set()
    for row in tables["environment_config"]:
        key = (row["environment"], row["category"], row["key"])
        if key in environment_keys:
            raise PostgresKernelError("invalid_manifest", "Duplicate current environment configuration key")
        environment_keys.add(key)


def _normalize_manifest_row(
    table_name: str,
    raw_row: object,
    *,
    require_version_one: bool,
) -> dict[str, Any]:
    spec = TABLE_SPECS[table_name]
    row = dict(_exact_keys(raw_row, set(spec.columns), label=f"manifest row {table_name}"))
    _identity_key(spec, row)
    version = row.get("version")
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise PostgresKernelError("invalid_manifest", f"Invalid version in {table_name}")
    if version > PG_INTEGER_MAX:
        raise PostgresKernelError("invalid_manifest", f"Version is outside PostgreSQL range in {table_name}")
    if require_version_one and version != 1:
        raise PostgresKernelError("invalid_manifest", f"Imported version must restart at 1 in {table_name}")
    for timestamp, calendar_date in _DATE_PRECISION_FIELDS.get(table_name, ()):
        if row[timestamp] is not None and row[calendar_date] is not None:
            raise PostgresKernelError(
                "invalid_manifest", f"{table_name} must supply either {timestamp} or {calendar_date}, not both"
            )
    if table_name in {"specifications", "tests"} and row["application_scope"] not in (
        None,
        "gtkb_platform",
        "agent_red_application",
    ):
        raise PostgresKernelError("invalid_manifest", f"Invalid {table_name}.application_scope")
    if table_name == "work_items":
        # Predecessor shape and graph diagnostics stay with their domain validator.
        for column in spec.json_columns - {"depends_on_work_items"}:
            value = row[column]
            if value is not None and (
                not isinstance(value, list)
                or any(not isinstance(reference, str) or not reference.strip() for reference in value)
            ):
                raise PostgresKernelError(
                    "invalid_manifest",
                    f"work_items.{column} must be an array of nonempty references or null",
                )
    if table_name == "projects":
        if row.get("kind") not in {"program", "project"}:
            raise PostgresKernelError("invalid_manifest", "Invalid projects.kind")
        if row["kind"] == "program" and row.get("authorization") is not None:
            raise PostgresKernelError("invalid_manifest", "Programs have no authorization")
        if row["kind"] == "project" and row.get("authorization") not in {"authorized", "not authorized"}:
            raise PostgresKernelError("invalid_manifest", "Invalid projects.authorization")
        if row["id"] == "PROJECT-GTKB-NEW-WORK-INTAKE" and row.get("authorization") != "not authorized":
            raise PostgresKernelError("invalid_manifest", "Standing intake must remain not authorized")
    if table_name == "project_dependencies" and row.get("affected_gate") == "authorization":
        raise PostgresKernelError("invalid_manifest", "Project dependency affected_gate was not transformed")
    if table_name == "canonical_terms":
        if row.get("authority_level") not in {"platform_core", "adopter_extension", "project_local"}:
            raise PostgresKernelError("invalid_manifest", "Invalid canonical_terms.authority_level")
        if row.get("lifecycle_status") not in {"candidate", "active", "deprecated", "retired"}:
            raise PostgresKernelError("invalid_manifest", "Invalid canonical_terms.lifecycle_status")
    for column in spec.columns:
        value = row[column]
        if column in _REQUIRED_COLUMNS[table_name] and value is None:
            raise PostgresKernelError("invalid_manifest", f"{table_name}.{column} must not be null")
        if column in _TIMESTAMP_COLUMNS:
            row[column] = _canonical_timestamp(value, label=f"{table_name}.{column}")
        elif column in _DATE_COLUMNS:
            row[column] = _canonical_date(value, label=f"{table_name}.{column}")
        elif value is None or column in spec.json_columns:
            continue
        elif column in spec.boolean_columns:
            if type(value) is not bool:
                raise PostgresKernelError("invalid_manifest", f"{table_name}.{column} must be boolean")
        elif column in _INTEGER_COLUMNS:
            if type(value) is not int or not PG_INTEGER_MIN <= value <= PG_INTEGER_MAX:
                raise PostgresKernelError(
                    "invalid_manifest",
                    f"{table_name}.{column} must fit a PostgreSQL integer",
                )
        elif not isinstance(value, str):
            raise PostgresKernelError("invalid_manifest", f"{table_name}.{column} must be text or null")
    _validate_json_value(row)
    return row


def normalize_bindings(value: object) -> list[dict[str, Any]]:
    """Preserve immutable attribution without inventing versions or change history."""
    if not isinstance(value, list):
        raise PostgresKernelError("invalid_manifest", "Session bindings must be an array")
    result = []
    native_ids, context_ids = set(), set()
    for raw in value:
        row = dict(_exact_keys(raw, set(BINDING_COLUMNS), label="session_init_bindings"))
        for column in BINDING_COLUMNS:
            if column != "created_at":
                _opaque_id(row[column], label=f"session_init_bindings.{column}")
        if row["subject"] not in {"gtkb", "application"} or row["role"] not in {"prime-builder", "loyal-opposition"}:
            raise PostgresKernelError("invalid_manifest", "Invalid immutable session subject or role")
        row["created_at"] = _canonical_timestamp(row["created_at"], label="session_init_bindings.created_at")
        if row["created_at"] is None:
            raise PostgresKernelError("invalid_manifest", "An immutable binding requires its actual creation time")
        if row["native_context_id"] in native_ids or row["session_context_id"] in context_ids:
            raise PostgresKernelError("invalid_manifest", "Session binding identities must be unique")
        native_ids.add(row["native_context_id"])
        context_ids.add(row["session_context_id"])
        result.append(row)
    return sorted(result, key=lambda row: row["native_context_id"].encode("utf-8"))


def normalize_manifest(value: object, *, require_version_one: bool = True) -> dict[str, Any]:
    manifest = _exact_keys(value, {"format", "schema_version", "tables"}, label="manifest")
    if (
        manifest["format"] != CURRENT_FORMAT
        or type(manifest["schema_version"]) is not int
        or manifest["schema_version"] != SCHEMA_VERSION
    ):
        raise PostgresKernelError("invalid_manifest", "Unsupported migration-manifest format or schema version")
    tables = _exact_keys(manifest["tables"], set(MIGRATION_TABLES), label="manifest.tables")
    normalized_tables: dict[str, list[dict[str, Any]]] = {}
    for table_name in CURRENT_TABLES:
        rows = tables[table_name]
        if not isinstance(rows, list):
            raise PostgresKernelError("invalid_manifest", f"Manifest table {table_name} must be an array")
        spec = TABLE_SPECS[table_name]
        seen: set[tuple[bytes, ...]] = set()
        normalized_rows: list[dict[str, Any]] = []
        for raw_row in rows:
            row = _normalize_manifest_row(
                table_name,
                raw_row,
                require_version_one=require_version_one,
            )
            identity = _identity_key(spec, row)
            if identity in seen:
                raise PostgresKernelError("invalid_manifest", f"Duplicate manifest identity in {table_name}")
            seen.add(identity)
            normalized_rows.append(row)
        normalized_rows.sort(key=lambda row: _identity_key(spec, row))
        normalized_tables[table_name] = normalized_rows
    normalized_tables["session_init_bindings"] = normalize_bindings(tables["session_init_bindings"])
    _validate_manifest_relationships(normalized_tables)
    return {"format": CURRENT_FORMAT, "schema_version": SCHEMA_VERSION, "tables": normalized_tables}


def _hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _publish_bytes(path: Path, payload: bytes) -> str:
    def existing_status() -> str:
        if path.is_file() and not path.is_symlink() and path.read_bytes() == payload:
            return "already_current"
        raise PostgresKernelError("output_exists", "Output exists with different content")

    try:
        if path.exists():
            return existing_status()
        if not path.parent.is_dir():
            raise PostgresKernelError("output_parent_missing", "Output parent directory does not exist")
        descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(temporary_name)
        publication_status: str | None = None
        publication_error: PostgresKernelError | OSError | None = None
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, path)
                publication_status = "ok"
            except FileExistsError:
                publication_status = existing_status()
        except (PostgresKernelError, OSError) as exc:
            publication_error = exc
        try:
            if temporary.exists():
                try:
                    temporary.unlink()
                except OSError:
                    os.unlink(temporary)
        except OSError as cleanup_error:
            if publication_error is None and publication_status is None:
                publication_error = cleanup_error
        if publication_error is not None:
            raise publication_error
        if publication_status is None:
            raise OSError("Canonical output publication produced no result")
        return publication_status
    except PostgresKernelError:
        raise
    except OSError as exc:
        raise PostgresKernelError("output_write_failed", "Canonical output could not be published") from exc


def _json_from_sqlite(value: object, *, table: str, column: str) -> object:
    if value is None or isinstance(value, (dict, list, bool, int, float)):
        _validate_json_value(value)
        return value
    if not isinstance(value, str):
        raise PostgresKernelError("invalid_source", f"{table}.{column} is not JSON text")
    try:
        parsed = parse_json_bytes(value.encode("utf-8"))
    except PostgresKernelError as exc:
        raise PostgresKernelError("invalid_source", f"{table}.{column} contains invalid JSON") from exc
    return parsed


def _sqlite_inventory(connection: sqlite3.Connection) -> dict[str, Any]:
    names = [
        row[0]
        for row in connection.execute(
            "SELECT name FROM main.sqlite_schema WHERE type='table' AND substr(name,1,7) <> 'sqlite_' ORDER BY name"
        ).fetchall()
    ]
    table_list_all = connection.execute(
        "SELECT schema,name,type,ncol,wr,strict FROM pragma_table_list WHERE schema='main'"
    ).fetchall()
    table_list_by_name: dict[str, list[sqlite3.Row]] = {}
    for row in table_list_all:
        table_list_by_name.setdefault(str(row["name"]), []).append(row)
    table_rows: list[dict[str, Any]] = []
    column_rows: dict[str, list[dict[str, Any]]] = {}
    for name in names:
        matches = table_list_by_name.get(str(name), [])
        if len(matches) != 1:
            raise PostgresKernelError("invalid_sqlite_inventory", f"Expected one table_list row for: {name}")
        table_rows.append(dict(matches[0]))
        rows = connection.execute(
            'SELECT cid,name,type,"notnull",dflt_value,pk,hidden FROM pragma_table_xinfo(?)',
            (name,),
        ).fetchall()
        column_rows[str(name)] = [dict(row) for row in rows]
    return normalize_table_inventory(table_rows, column_rows)


def _current_sqlite_rows(connection: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    quoted = '"' + table_name.replace('"', '""') + '"'
    columns = {row["name"] for row in connection.execute(f"PRAGMA table_info({quoted})")}
    if "version" not in columns:
        return [dict(row) for row in connection.execute(f"SELECT * FROM {quoted}")]
    spec = TABLE_SPECS[table_name]
    keys = ",".join('"' + key.replace('"', '""') + '"' for key in spec.identity_columns)
    invalid = connection.execute(
        f"SELECT 1 FROM {quoted} WHERE typeof(version) <> 'integer' OR version < 1 LIMIT 1"
    ).fetchone()
    if invalid is not None:
        raise PostgresKernelError("invalid_source", f"Invalid source version in {table_name}")
    duplicate = connection.execute(
        f"SELECT 1 FROM {quoted} GROUP BY {keys},version HAVING COUNT(*) > 1 LIMIT 1"
    ).fetchone()
    if duplicate is not None:
        raise PostgresKernelError("invalid_source", f"Duplicate source identity/version in {table_name}")
    # Select current payloads in SQLite. Historical bodies can dominate the
    # source size and are not migration input; never materialize them in Python.
    rows = [
        dict(row)
        for row in connection.execute(
            f"SELECT t.* FROM {quoted} t JOIN "
            f"(SELECT {keys},MAX(version) version FROM {quoted} GROUP BY {keys}) h USING ({keys},version)"
        )
    ]
    for row in rows:
        _identity_key(spec, row)
    return rows


def _transform_source_rows(
    source_rows: Mapping[str, list[dict[str, Any]]], plan: Mapping[str, Any]
) -> dict[str, list[dict[str, Any]]]:
    output: dict[str, list[dict[str, Any]]] = {}
    current_spec_versions = {str(row["id"]): int(row["version"]) for row in source_rows["specifications"]}
    dependency_plan = plan["project_dependencies"]
    retire_ids = set(dependency_plan["retire_dependency_ids"])
    preserve_ids = set(dependency_plan["preserve_dependency_ids"])
    source_dependency_ids = {str(row["id"]) for row in source_rows["project_dependencies"]}
    if source_dependency_ids != retire_ids | preserve_ids:
        raise PostgresKernelError(
            "transform_precondition_failed", "Dependency plan does not exactly account for source IDs"
        )
    dependency_rows_by_id = {str(row["id"]): row for row in source_rows["project_dependencies"]}
    if any(dependency_rows_by_id[dependency_id].get("status") != "active" for dependency_id in retire_ids):
        raise PostgresKernelError(
            "transform_precondition_failed",
            "Every planned dependency retirement must name a current active row",
        )

    gate_transition_count = 0
    for table_name in CURRENT_TABLES:
        spec = TABLE_SPECS[table_name]
        source_table_rows = source_rows[table_name]
        if table_name == "project_work_item_memberships":
            # Migration restarts current state. Inactive links describe former
            # associations, preserved in the source/backup, not extra parents.
            historical_statuses = {"removed", "retired", "moved", "superseded", "completed", "excluded", "rehomed"}
            for source_row in source_table_rows:
                if source_row.get("status") not in historical_statuses | {"active"}:
                    raise PostgresKernelError(
                        "invalid_source",
                        "Unknown project membership status",
                        details={"membership_id": source_row.get("id"), "status": source_row.get("status")},
                    )
            source_table_rows = [row for row in source_table_rows if row["status"] == "active"]
        if table_name == "specification_deliberation_sources":
            for source_row in source_table_rows:
                source_spec_id = str(source_row.get("spec_id"))
                source_spec_version = source_row.get("spec_version")
                if source_spec_id not in current_spec_versions:
                    raise PostgresKernelError(
                        "transform_precondition_failed",
                        "Specification source link names an unknown current specification",
                    )
                if (
                    not isinstance(source_spec_version, int)
                    or isinstance(source_spec_version, bool)
                    or source_spec_version < 1
                ):
                    raise PostgresKernelError(
                        "transform_precondition_failed",
                        "Specification source link has an invalid source version",
                    )
            source_table_rows = [
                row
                for row in source_table_rows
                if current_spec_versions[str(row.get("spec_id"))] == row.get("spec_version")
            ]
        transformed: list[dict[str, Any]] = []
        seen: set[tuple[bytes, ...]] = set()
        for source in source_table_rows:
            row: dict[str, Any] = {column: source.get(column) for column in spec.columns}
            row["version"] = 1
            for timestamp, calendar_date in _DATE_PRECISION_FIELDS.get(table_name, ()):
                value = row[timestamp]
                if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                    if row[calendar_date] is not None:
                        raise PostgresKernelError(
                            "invalid_source", f"Ambiguous date precision in {table_name}.{timestamp}"
                        )
                    row[calendar_date] = _canonical_date(value, label=f"{table_name}.{calendar_date}")
                    row[timestamp] = None
            for column in spec.json_columns:
                row[column] = _json_from_sqlite(row[column], table=table_name, column=column)
            for column in spec.boolean_columns:
                value = row[column]
                if type(value) is not int or value not in (0, 1):
                    raise PostgresKernelError("invalid_source", f"{table_name}.{column} is not boolean")
                row[column] = bool(value)
            for column in spec.columns:
                if column in _TIMESTAMP_COLUMNS:
                    row[column] = _canonical_timestamp(row[column], label=f"{table_name}.{column}")
                elif column in _DATE_COLUMNS:
                    row[column] = _canonical_date(row[column], label=f"{table_name}.{column}")
            if table_name == "project_dependencies":
                if source.get("affected_gate") == dependency_plan["affected_gate_from"]:
                    row["affected_gate"] = dependency_plan["affected_gate_to"]
                    gate_transition_count += 1
                if str(row["id"]) in retire_ids:
                    row["status"] = "retired"
            identity = _identity_key(spec, row)
            if identity in seen:
                raise PostgresKernelError(
                    "transform_precondition_failed", f"Duplicate current relationship in {table_name}"
                )
            seen.add(identity)
            transformed.append(row)
        transformed.sort(key=lambda row: _identity_key(spec, row))
        output[table_name] = transformed

    projects = output["projects"]
    authorized_count = sum(row["authorization"] == "authorized" for row in projects)
    not_authorized_count = sum(row["authorization"] == "not authorized" for row in projects)
    program_count = sum(row["kind"] == "program" for row in projects)
    project_plan = plan["projects"]
    if (
        len(projects) != project_plan["expected_total"]
        or authorized_count != project_plan["expected_authorized"]
        or not_authorized_count != project_plan["expected_not_authorized"]
        or program_count != project_plan["expected_programs"]
    ):
        raise PostgresKernelError("transform_precondition_failed", "Project count or authorization result drifted")

    dependencies = output["project_dependencies"]
    active_count = sum(row["status"] == "active" for row in dependencies)
    retired_count = sum(row["status"] == "retired" for row in dependencies)
    if (
        len(dependencies) != dependency_plan["expected_source_count"]
        or gate_transition_count != dependency_plan["expected_gate_transition_count"]
        or active_count != dependency_plan["expected_active_after"]
        or retired_count != dependency_plan["expected_retired_after"]
    ):
        raise PostgresKernelError("transform_precondition_failed", "Dependency transform counts drifted")
    output["session_init_bindings"] = normalize_bindings(source_rows["session_init_bindings"])
    return output


def _normalize_pg_value(value: object) -> object:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise PostgresKernelError("invalid_timestamp", "PostgreSQL returned a timestamp without an offset")
        return value.astimezone(UTC).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_normalize_pg_value(item) for item in value]
    if isinstance(value, list):
        return [_normalize_pg_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _normalize_pg_value(item) for key, item in value.items()}
    return value


def _select_columns(spec: TableSpec) -> Any:
    """Select JSONB as text so psycopg cannot round precise numbers through float."""
    expressions: list[Any] = []
    for column in spec.columns:
        if column in spec.json_columns:
            expressions.append(sql.SQL("{}::text AS {}").format(sql.Identifier(column), sql.Identifier(column)))
        else:
            expressions.append(sql.Identifier(column))
    return sql.SQL(",").join(expressions)


def _decode_pg_json(value: object, *, label: str) -> object:
    if isinstance(value, str):
        raw = value.encode("utf-8")
    elif isinstance(value, bytes):
        raw = value
    else:
        raise PostgresKernelError(
            "postgres_readback_invalid",
            f"PostgreSQL returned non-text JSON for {label}",
        )
    try:
        return parse_json_bytes(raw)
    except PostgresKernelError as exc:
        raise PostgresKernelError(
            "postgres_readback_invalid",
            f"PostgreSQL returned invalid JSON for {label}",
        ) from exc


def _normalize_pg_row(raw: Mapping[str, object], spec: TableSpec) -> dict[str, Any]:
    row: dict[str, Any] = {}
    for column in spec.columns:
        if column not in raw:
            raise PostgresKernelError(
                "postgres_readback_invalid",
                f"PostgreSQL omitted {spec.name}.{column}",
            )
        value = raw[column]
        if column in spec.json_columns and value is not None:
            row[column] = _decode_pg_json(value, label=f"{spec.name}.{column}")
        else:
            row[column] = _normalize_pg_value(value)
    return row


class PostgresKernel:
    """PostgreSQL kernel service with injectable connectors for database-free tests."""

    def __init__(
        self,
        settings: PostgreSQLConfig,
        *,
        connector: Callable[..., Any] | None = None,
        sqlite_connector: Callable[..., sqlite3.Connection] | None = None,
    ) -> None:
        self.settings = settings
        self._connector = connector
        self._sqlite_connector = sqlite_connector

    def _connect(self) -> Any:
        connector = self._connector or psycopg.connect
        try:
            return connector(
                service=self.settings.service,
                connect_timeout=self.settings.connect_timeout_seconds,
                autocommit=False,
                row_factory=dict_row,
            )
        except PostgresKernelError:
            raise
        except Exception as exc:  # intentional-catch: driver failures surface as PostgresKernelError
            raise PostgresKernelError("postgres_unavailable", "PostgreSQL service is unavailable") from exc

    def _configure_transaction(self, cursor: Any) -> None:
        cursor.execute("SELECT set_config('lock_timeout', %s, true)", (f"{self.settings.lock_timeout_ms}ms",))
        cursor.execute(
            "SELECT set_config('statement_timeout', %s, true)",
            (f"{self.settings.statement_timeout_ms}ms",),
        )

    @staticmethod
    def _current_schema(cursor: Any) -> str:
        cursor.execute("SELECT current_schema() AS schema_name")
        row = cursor.fetchone()
        schema_name = row.get("schema_name") if isinstance(row, Mapping) else row[0]
        if not isinstance(schema_name, str) or not schema_name:
            raise PostgresKernelError("schema_unavailable", "libpq service does not select a current schema")
        _validate_text(schema_name, label="PostgreSQL schema name")
        return schema_name

    @staticmethod
    def _table_names(cursor: Any, schema_name: str) -> set[str]:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema=%s AND table_type='BASE TABLE'",
            (schema_name,),
        )
        return {str(row.get("table_name") if isinstance(row, Mapping) else row[0]) for row in cursor.fetchall()}

    @staticmethod
    def _schema_has_relations(cursor: Any, schema_name: str) -> bool:
        cursor.execute(
            "SELECT EXISTS ("
            "SELECT 1 FROM pg_catalog.pg_depend d "
            "WHERE d.refclassid='pg_catalog.pg_namespace'::regclass "
            "AND d.refobjid=(SELECT oid FROM pg_catalog.pg_namespace WHERE nspname=%s) "
            "AND d.deptype='n'"
            ") AS has_relations",
            (schema_name,),
        )
        row = cursor.fetchone()
        return bool(row.get("has_relations") if isinstance(row, Mapping) else row[0])

    @staticmethod
    def _schema_comment(cursor: Any, schema_name: str) -> object:
        cursor.execute(
            "SELECT obj_description(oid, 'pg_namespace') AS comment FROM pg_catalog.pg_namespace WHERE nspname=%s",
            (schema_name,),
        )
        row = cursor.fetchone()
        if row is None:
            raise PostgresKernelError("schema_unavailable", "PostgreSQL current schema does not exist")
        return row.get("comment") if isinstance(row, Mapping) else row[0]

    @staticmethod
    def _decode_schema_comment(comment: object) -> dict[str, Any] | None:
        if comment is None:
            return None
        try:
            if not isinstance(comment, str):
                raise PostgresKernelError("schema_metadata_drift", "PostgreSQL schema comment is not text")
            value = parse_json_bytes(comment.encode("utf-8"))
            metadata = _exact_keys(
                value,
                {"catalog_sha256", "format", "schema_sha256", "schema_version"},
                label="schema metadata",
            )
        except PostgresKernelError as exc:
            raise PostgresKernelError(
                "schema_metadata_drift",
                "PostgreSQL schema metadata is invalid",
            ) from exc
        if (
            metadata["format"] != SCHEMA_FORMAT
            or type(metadata["schema_version"]) is not int
            or metadata["schema_version"] != SCHEMA_VERSION
            or not isinstance(metadata["schema_sha256"], str)
            or not _LOWER_SHA_RE.fullmatch(metadata["schema_sha256"])
            or not isinstance(metadata["catalog_sha256"], str)
            or not _LOWER_SHA_RE.fullmatch(metadata["catalog_sha256"])
        ):
            raise PostgresKernelError("schema_metadata_drift", "PostgreSQL schema metadata is invalid")
        return metadata

    @staticmethod
    def _catalog_snapshot(cursor: Any, schema_name: str) -> dict[str, Any]:
        queries = {
            "columns": (
                "SELECT table_name,ordinal_position,column_name,data_type,udt_name,is_nullable,"
                "column_default,is_identity,identity_generation,collation_name,"
                "character_maximum_length,numeric_precision,numeric_scale,datetime_precision,"
                "is_generated,generation_expression "
                "FROM information_schema.columns WHERE table_schema=%s "
                "ORDER BY table_name,ordinal_position"
            ),
            "constraints": (
                "SELECT r.relname AS table_name,c.conname AS constraint_name,c.contype AS constraint_type,"
                "c.condeferrable AS is_deferrable,c.condeferred AS initially_deferred,"
                "c.convalidated AS is_validated,pg_get_constraintdef(c.oid,false) AS definition "
                "FROM pg_catalog.pg_constraint c "
                "JOIN pg_catalog.pg_class r ON r.oid=c.conrelid "
                "JOIN pg_catalog.pg_namespace n ON n.oid=r.relnamespace "
                "WHERE n.nspname=%s ORDER BY r.relname,c.conname"
            ),
            "indexes": (
                "SELECT tablename AS table_name,indexname AS index_name,indexdef AS definition "
                "FROM pg_catalog.pg_indexes WHERE schemaname=%s ORDER BY tablename,indexname"
            ),
            "namespace_object_counts": (
                "SELECT d.classid::regclass::text AS catalog_name,count(*)::bigint AS object_count "
                "FROM pg_catalog.pg_depend d "
                "WHERE d.refclassid='pg_catalog.pg_namespace'::regclass "
                "AND d.refobjid=(SELECT oid FROM pg_catalog.pg_namespace WHERE nspname=%s) "
                "AND d.deptype='n' "
                "GROUP BY d.classid ORDER BY catalog_name"
            ),
            "relations": (
                "SELECT c.relname AS relation_name,c.relkind AS relation_kind,"
                "c.relpersistence AS persistence,c.relreplident AS replica_identity,"
                "c.relrowsecurity AS row_security,c.relforcerowsecurity AS force_row_security,"
                "c.reloptions AS relation_options,am.amname AS access_method "
                "FROM pg_catalog.pg_class c "
                "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
                "LEFT JOIN pg_catalog.pg_am am ON am.oid=c.relam "
                "WHERE n.nspname=%s AND c.relkind IN ('r','p','v','m','S','f') "
                "ORDER BY c.relname,c.relkind"
            ),
            "attributes": (
                "SELECT c.relname AS relation_name,a.attnum AS ordinal_position,a.attname AS column_name,"
                "pg_catalog.format_type(a.atttypid,a.atttypmod) AS formatted_type,"
                "a.attnotnull AS is_not_null,a.atthasdef AS has_default,a.attidentity AS identity_kind,"
                "a.attgenerated AS generated_kind,a.attstorage AS storage_kind,a.attcompression AS compression_kind,"
                "a.attstattarget AS statistics_target,a.attoptions AS attribute_options,"
                "coll.collname AS collation_name "
                "FROM pg_catalog.pg_attribute a "
                "JOIN pg_catalog.pg_class c ON c.oid=a.attrelid "
                "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
                "LEFT JOIN pg_catalog.pg_collation coll ON coll.oid=a.attcollation "
                "WHERE n.nspname=%s AND a.attnum>0 AND NOT a.attisdropped "
                "ORDER BY c.relname,a.attnum"
            ),
            "routines": (
                "SELECT p.proname AS routine_name,p.prokind AS routine_kind,"
                "pg_get_function_identity_arguments(p.oid) AS identity_arguments "
                "FROM pg_catalog.pg_proc p "
                "JOIN pg_catalog.pg_namespace n ON n.oid=p.pronamespace "
                "WHERE n.nspname=%s ORDER BY p.proname,identity_arguments"
            ),
            "sequences": (
                "SELECT c.relname AS sequence_name,s.seqtypid::regtype::text AS data_type,"
                "s.seqstart AS start_value,s.seqincrement AS increment_by,"
                "s.seqmax AS maximum_value,s.seqmin AS minimum_value,"
                "s.seqcache AS cache_size,s.seqcycle AS cycles "
                "FROM pg_catalog.pg_sequence s "
                "JOIN pg_catalog.pg_class c ON c.oid=s.seqrelid "
                "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
                "WHERE n.nspname=%s ORDER BY c.relname"
            ),
            "triggers": (
                "SELECT c.relname AS table_name,t.tgname AS trigger_name,"
                "pg_get_triggerdef(t.oid,false) AS definition "
                "FROM pg_catalog.pg_trigger t "
                "JOIN pg_catalog.pg_class c ON c.oid=t.tgrelid "
                "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
                "WHERE n.nspname=%s AND NOT t.tgisinternal ORDER BY c.relname,t.tgname"
            ),
            "policies": (
                "SELECT tablename AS table_name,policyname AS policy_name,permissive,roles,cmd,qual,with_check "
                "FROM pg_catalog.pg_policies WHERE schemaname=%s ORDER BY tablename,policyname"
            ),
            "rules": (
                "SELECT c.relname AS relation_name,r.rulename AS rule_name,"
                "pg_get_ruledef(r.oid,false) AS definition "
                "FROM pg_catalog.pg_rewrite r "
                "JOIN pg_catalog.pg_class c ON c.oid=r.ev_class "
                "JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace "
                "WHERE n.nspname=%s AND r.rulename <> '_RETURN' ORDER BY c.relname,r.rulename"
            ),
            "types": (
                "SELECT t.typname AS type_name,t.typtype AS type_kind,t.typcategory AS category,"
                "t.typispreferred AS is_preferred,t.typnotnull AS is_not_null,t.typdefault AS default_value,"
                "base.typname AS base_type,element.typname AS element_type,relation.relname AS relation_name "
                "FROM pg_catalog.pg_type t "
                "JOIN pg_catalog.pg_namespace n ON n.oid=t.typnamespace "
                "LEFT JOIN pg_catalog.pg_type base ON base.oid=t.typbasetype "
                "LEFT JOIN pg_catalog.pg_type element ON element.oid=t.typelem "
                "LEFT JOIN pg_catalog.pg_class relation ON relation.oid=t.typrelid "
                "WHERE n.nspname=%s ORDER BY t.typname"
            ),
        }
        snapshot: dict[str, Any] = {}
        for key, query in queries.items():
            cursor.execute(query, (schema_name,))
            rows: list[dict[str, Any]] = []
            for raw_row in cursor.fetchall():
                if not isinstance(raw_row, Mapping):
                    raise PostgresKernelError(
                        "schema_catalog_unreadable",
                        "PostgreSQL catalog did not return named columns",
                    )
                rows.append({str(column): _normalize_pg_value(value) for column, value in raw_row.items()})
            snapshot[key] = rows
        return snapshot

    @classmethod
    def _catalog_sha256(cls, cursor: Any, schema_name: str) -> str:
        return canonical_sha256(cls._catalog_snapshot(cursor, schema_name))

    @classmethod
    def _require_exact_schema(cls, cursor: Any, schema_name: str) -> None:
        tables = cls._table_names(cursor, schema_name)
        actual_catalog_sha256 = cls._catalog_sha256(cursor, schema_name)
        try:
            metadata = cls._decode_schema_comment(cls._schema_comment(cursor, schema_name))
        except PostgresKernelError as exc:
            raise PostgresKernelError(
                "schema_drift",
                "PostgreSQL target schema metadata does not match kernel v1",
                details={"actual_catalog_sha256": actual_catalog_sha256},
            ) from exc
        if (
            tables != set(ALL_TABLES)
            or metadata is None
            or metadata.get("format") != SCHEMA_FORMAT
            or metadata.get("schema_version") != SCHEMA_VERSION
            or metadata.get("schema_sha256") != schema_sql_sha256()
            or metadata.get("catalog_sha256") != actual_catalog_sha256
        ):
            raise PostgresKernelError(
                "schema_drift",
                "PostgreSQL target schema is not the exact kernel v1 catalog",
                details={"actual_catalog_sha256": actual_catalog_sha256},
            )

    def initialize(self) -> dict[str, Any]:
        connection = self._connect()
        try:
            with connection, connection.transaction():
                cursor = connection.cursor()
                self._configure_transaction(cursor)
                schema_name = self._current_schema(cursor)
                table_names = self._table_names(cursor, schema_name)
                schema_comment = self._schema_comment(cursor, schema_name)
                stock_public_default = schema_name == "public" and schema_comment == STOCK_PUBLIC_SCHEMA_COMMENT
                if table_names or (schema_comment is not None and not stock_public_default):
                    self._require_exact_schema(cursor, schema_name)
                    return {
                        "schema_sha256": schema_sql_sha256(),
                        "schema_version": SCHEMA_VERSION,
                        "status": "already_current",
                        "table_count": len(ALL_TABLES),
                    }

                if self._schema_has_relations(cursor, schema_name):
                    raise PostgresKernelError(
                        "schema_not_empty",
                        "PostgreSQL target schema contains pre-existing relations",
                    )

                try:
                    template = schema_sql_bytes().decode("utf-8")
                except UnicodeDecodeError as exc:
                    raise PostgresKernelError(
                        "schema_resource_invalid", "Packaged PostgreSQL schema is not UTF-8"
                    ) from exc
                cursor.execute(sql.SQL(template).format(schema=sql.Identifier(schema_name)))
                catalog_sha256 = self._catalog_sha256(cursor, schema_name)
                expected_metadata = _schema_metadata(catalog_sha256=catalog_sha256)
                comment = canonical_json_bytes(expected_metadata).decode("utf-8").removesuffix("\n")
                cursor.execute(
                    sql.SQL("COMMENT ON SCHEMA {} IS {}").format(
                        sql.Identifier(schema_name),
                        sql.Literal(comment),
                    )
                )
                self._require_exact_schema(cursor, schema_name)
                return {
                    "schema_sha256": expected_metadata["schema_sha256"],
                    "schema_version": SCHEMA_VERSION,
                    "status": "initialized",
                    "table_count": len(ALL_TABLES),
                }
        except PostgresKernelError:
            raise
        except Exception as exc:  # intentional-catch: driver failures surface as PostgresKernelError
            raise PostgresKernelError("postgres_operation_failed", "PostgreSQL initialization failed") from exc

    def status(self) -> dict[str, Any]:
        connection = self._connect()
        try:
            with connection, connection.transaction():
                cursor = connection.cursor()
                cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                self._configure_transaction(cursor)
                schema_name = self._current_schema(cursor)
                cursor.execute("SHOW server_version_num")
                version_row = cursor.fetchone()
                version_text = (
                    version_row.get("server_version_num") if isinstance(version_row, Mapping) else version_row[0]
                )
                server_major = int(str(version_text)) // 10000
                tables = self._table_names(cursor, schema_name)
                schema_comment = self._schema_comment(cursor, schema_name)
                # A table-free public schema carrying only PostgreSQL's stock comment is an
                # uninitialized target, exactly as initialize() classifies it. Report it as
                # not ready with every table missing instead of raising metadata drift.
                stock_public_default = (
                    schema_name == "public" and not tables and schema_comment == STOCK_PUBLIC_SCHEMA_COMMENT
                )
                metadata = None if stock_public_default else self._decode_schema_comment(schema_comment)
                actual_catalog_sha256 = self._catalog_sha256(cursor, schema_name)
                cursor.execute(
                    "SELECT table_name,column_name FROM information_schema.columns WHERE table_schema=%s",
                    (schema_name,),
                )
                forbidden_columns = sorted(
                    f"{row['table_name']}.{row['column_name']}"
                    for row in cursor.fetchall()
                    if row["column_name"] in FORBIDDEN_COLUMNS
                )
                missing_tables = sorted(set(ALL_TABLES) - tables)
                unexpected_tables = sorted(tables - set(ALL_TABLES))
                forbidden_tables = sorted(tables & FORBIDDEN_TABLES)
                ready = (
                    metadata is not None
                    and metadata.get("format") == SCHEMA_FORMAT
                    and metadata.get("schema_version") == SCHEMA_VERSION
                    and metadata.get("schema_sha256") == schema_sql_sha256()
                    and metadata.get("catalog_sha256") == actual_catalog_sha256
                    and not missing_tables
                    and not unexpected_tables
                    and not forbidden_tables
                    and not forbidden_columns
                )
                return {
                    "forbidden_columns": forbidden_columns,
                    "forbidden_tables": forbidden_tables,
                    "missing_tables": missing_tables,
                    "postgresql_major_version": server_major,
                    "reachable": True,
                    "ready": ready,
                    "schema_catalog_matches": bool(
                        metadata and metadata.get("catalog_sha256") == actual_catalog_sha256
                    ),
                    "schema_catalog_sha256": actual_catalog_sha256,
                    "schema_sha256": metadata.get("schema_sha256") if metadata else None,
                    "schema_version": metadata.get("schema_version") if metadata else None,
                    "timeout_posture": {
                        "connect_timeout_seconds": self.settings.connect_timeout_seconds,
                        "lock_timeout_ms": self.settings.lock_timeout_ms,
                        "statement_timeout_ms": self.settings.statement_timeout_ms,
                    },
                    "unexpected_tables": unexpected_tables,
                }
        except PostgresKernelError:
            raise
        except Exception as exc:  # intentional-catch: driver failures surface as PostgresKernelError
            raise PostgresKernelError("postgres_operation_failed", "PostgreSQL status failed") from exc

    @contextmanager
    def _inspect_sqlite_snapshot(
        self,
        *,
        sqlite_snapshot: Path,
        live_sqlite_source: Path | None,
    ) -> Iterator[tuple[sqlite3.Connection, dict[str, Any]]]:
        try:
            if sqlite_snapshot.is_symlink():
                raise PostgresKernelError("invalid_snapshot", "SQLite snapshot must not be a symbolic link")
            snapshot = sqlite_snapshot.resolve(strict=True)
            if not snapshot.is_file():
                raise PostgresKernelError("invalid_snapshot", "SQLite snapshot must be one regular non-symlink file")
            if live_sqlite_source is not None:
                live_source = live_sqlite_source.resolve(strict=False)
                same_file = snapshot == live_source
                if live_source.exists():
                    same_file = same_file or os.path.samefile(snapshot, live_source)
                if same_file:
                    raise PostgresKernelError(
                        "live_source_forbidden",
                        "The live SQLite source cannot be exported directly",
                    )
            for suffix in ("-wal", "-shm"):
                if snapshot.with_name(snapshot.name + suffix).exists():
                    raise PostgresKernelError(
                        "snapshot_sidecar_present",
                        "SQLite snapshot has an adjacent WAL or SHM sidecar",
                    )
            initial_size = snapshot.stat().st_size
            if initial_size <= 0:
                raise PostgresKernelError("invalid_snapshot", "SQLite snapshot must have a positive byte size")
            initial_hash = _hash_file(snapshot)
        except PostgresKernelError:
            raise
        except OSError as exc:
            raise PostgresKernelError(
                "snapshot_preflight_failed",
                "SQLite snapshot filesystem preflight failed",
            ) from exc

        connector = self._sqlite_connector or sqlite3.connect
        uri = snapshot.as_uri() + "?mode=ro&immutable=1"
        connection: sqlite3.Connection | None = None
        primary_read_failed = False
        try:
            connection = connector(uri, uri=True)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only=ON")
            if connection.execute("PRAGMA query_only").fetchone()[0] != 1:
                raise PostgresKernelError("snapshot_read_failed", "SQLite query_only could not be enabled")
            integrity_rows = connection.execute("PRAGMA integrity_check").fetchall()
            if [row[0] for row in integrity_rows] != ["ok"]:
                raise PostgresKernelError(
                    "snapshot_integrity_failed", "SQLite snapshot integrity_check did not return ok"
                )
            user_version = connection.execute("PRAGMA user_version").fetchone()[0]
            if isinstance(user_version, bool) or not isinstance(user_version, int) or user_version < 0:
                raise PostgresKernelError(
                    "snapshot_read_failed",
                    "SQLite snapshot user_version must be a nonnegative integer",
                )
            inventory = _sqlite_inventory(connection)
            inventory_names = {row["name"] for row in inventory["tables"]}
            missing = set(MIGRATION_TABLES) - inventory_names
            unclassified = inventory_names - SOURCE_TABLES
            if missing or unclassified:
                raise PostgresKernelError(
                    "snapshot_table_set_mismatch",
                    "SQLite source contains missing or unclassified tables",
                    details={
                        "missing": sorted(missing),
                        "unclassified": sorted(unclassified),
                    },
                )
            source = {
                "expected_pragma_user_version": user_version,
                "expected_table_inventory_sha256": canonical_sha256(inventory),
                "sqlite_snapshot_sha256": initial_hash,
                "sqlite_snapshot_size_bytes": initial_size,
            }
            yield connection, source
        except PostgresKernelError:
            primary_read_failed = True
            raise
        except sqlite3.Error as exc:
            primary_read_failed = True
            raise PostgresKernelError("snapshot_read_failed", "Immutable SQLite snapshot read failed") from exc
        except Exception:
            primary_read_failed = True
            raise
        finally:
            if connection is not None:
                try:
                    connection.close()
                except (sqlite3.Error, OSError) as exc:
                    if not primary_read_failed:
                        raise PostgresKernelError(
                            "snapshot_read_failed",
                            "Immutable SQLite snapshot close failed",
                        ) from exc
        try:
            for suffix in ("-wal", "-shm"):
                if snapshot.with_name(snapshot.name + suffix).exists():
                    raise PostgresKernelError(
                        "snapshot_sidecar_present",
                        "SQLite snapshot gained a WAL or SHM sidecar",
                    )
            if snapshot.stat().st_size != initial_size or _hash_file(snapshot) != initial_hash:
                raise PostgresKernelError("snapshot_changed", "SQLite snapshot changed during immutable read")
        except PostgresKernelError:
            raise
        except OSError as exc:
            raise PostgresKernelError(
                "snapshot_postflight_failed",
                "SQLite snapshot filesystem postflight failed",
            ) from exc

    def preflight_export_current(
        self,
        *,
        sqlite_snapshot: Path,
        live_sqlite_source: Path | None,
    ) -> dict[str, Any]:
        source: dict[str, Any]
        with self._inspect_sqlite_snapshot(
            sqlite_snapshot=sqlite_snapshot,
            live_sqlite_source=live_sqlite_source,
        ) as (_connection, inspected_source):
            source = dict(inspected_source)
        return source

    def export_current(
        self,
        *,
        sqlite_snapshot: Path,
        transform_plan: Path,
        output: Path,
        live_sqlite_source: Path | None,
    ) -> dict[str, Any]:
        try:
            plan_raw = transform_plan.read_bytes()
            plan_value = parse_json_bytes(plan_raw)
        except OSError as exc:
            raise PostgresKernelError("transform_plan_unreadable", "Transform plan cannot be read") from exc
        plan = validate_transform_plan(plan_value)
        if plan_raw != canonical_json_bytes(plan):
            raise PostgresKernelError("transform_plan_not_canonical", "Transform plan bytes are not canonical")

        expected_source = plan["source"]
        with self._inspect_sqlite_snapshot(
            sqlite_snapshot=sqlite_snapshot,
            live_sqlite_source=live_sqlite_source,
        ) as (connection, actual_source):
            if (
                actual_source["sqlite_snapshot_size_bytes"] != expected_source["sqlite_snapshot_size_bytes"]
                or actual_source["sqlite_snapshot_sha256"] != expected_source["sqlite_snapshot_sha256"]
            ):
                raise PostgresKernelError(
                    "snapshot_preimage_mismatch",
                    "SQLite snapshot size or SHA-256 does not match plan",
                )
            if actual_source["expected_pragma_user_version"] != expected_source["expected_pragma_user_version"]:
                raise PostgresKernelError(
                    "snapshot_user_version_mismatch",
                    "SQLite snapshot user_version drifted",
                )
            if actual_source["expected_table_inventory_sha256"] != expected_source["expected_table_inventory_sha256"]:
                raise PostgresKernelError(
                    "snapshot_inventory_mismatch",
                    "SQLite table inventory drifted",
                )
            source_rows = {name: _current_sqlite_rows(connection, name) for name in MIGRATION_TABLES}
            transformed = _transform_source_rows(source_rows, plan)
            manifest = normalize_manifest(
                {"format": CURRENT_FORMAT, "schema_version": SCHEMA_VERSION, "tables": transformed}
            )
            payload = canonical_json_bytes(manifest)

        publication = _publish_bytes(output, payload)
        return {
            "manifest_sha256": hashlib.sha256(payload).hexdigest(),
            "row_count": sum(len(rows) for rows in manifest["tables"].values()),
            "status": publication,
        }

    @staticmethod
    def _adapt_value(column: str, value: object, spec: TableSpec) -> object:
        if column in spec.json_columns:
            return Jsonb(value, dumps=_postgres_json_dumps) if value is not None else None
        return value

    @staticmethod
    def _readback_with_cursor(cursor: Any, schema_name: str) -> dict[str, Any]:
        tables: dict[str, list[dict[str, Any]]] = {}
        for table_name in CURRENT_TABLES:
            spec = TABLE_SPECS[table_name]
            query = sql.SQL("SELECT {} FROM {}.{}").format(
                _select_columns(spec),
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            )
            cursor.execute(query)
            rows = []
            for raw_row in cursor.fetchall():
                rows.append(_normalize_pg_row(dict(raw_row), spec))
            rows.sort(key=lambda row: _identity_key(spec, row))
            tables[table_name] = rows
        cursor.execute(
            sql.SQL("SELECT {} FROM {}.session_init_bindings").format(
                sql.SQL(",").join(sql.Identifier(column) for column in BINDING_COLUMNS), sql.Identifier(schema_name)
            )
        )
        tables["session_init_bindings"] = normalize_bindings([dict(row) for row in cursor.fetchall()])
        return normalize_manifest(
            {"format": CURRENT_FORMAT, "schema_version": SCHEMA_VERSION, "tables": tables}, require_version_one=False
        )

    @staticmethod
    def _row_count(manifest: Mapping[str, Any]) -> int:
        return sum(len(rows) for rows in manifest["tables"].values())

    @staticmethod
    def _history_matches_manifest(cursor: Any, schema_name: str, manifest: Mapping[str, Any]) -> bool:
        cursor.execute(
            sql.SQL(
                "SELECT record_type,record_id::text AS record_id,prior_version,new_version,"
                "prior_state::text AS prior_state,new_state::text AS new_state "
                "FROM {}.record_history ORDER BY history_id"
            ).format(sql.Identifier(schema_name))
        )
        actual_rows = [dict(row) for row in cursor.fetchall()]
        expected: dict[tuple[str, bytes], bytes] = {}
        for table_name in CURRENT_TABLES:
            spec = TABLE_SPECS[table_name]
            for row in manifest["tables"][table_name]:
                identity = {column: row[column] for column in spec.identity_columns}
                key = (table_name, canonical_json_bytes(identity))
                expected[key] = canonical_json_bytes(row)
        if len(actual_rows) != len(expected):
            return False
        observed: set[tuple[str, bytes]] = set()
        for history in actual_rows:
            record_type = history.get("record_type")
            if not isinstance(record_type, str):
                return False
            try:
                record_id = _decode_pg_json(history.get("record_id"), label="record_history.record_id")
                new_state = _decode_pg_json(history.get("new_state"), label="record_history.new_state")
                key = (record_type, canonical_json_bytes(record_id))
                state_bytes = canonical_json_bytes(new_state)
            except PostgresKernelError:
                return False
            if (
                key in observed
                or expected.get(key) != state_bytes
                or history.get("prior_version") is not None
                or history.get("new_version") != 1
                or history.get("prior_state") is not None
            ):
                return False
            observed.add(key)
        return observed == set(expected)

    def import_current(self, *, input_path: Path, actor: str, reason: str) -> dict[str, Any]:
        _opaque_id(actor, label="actor")
        _opaque_id(reason, label="reason")
        try:
            raw = input_path.read_bytes()
        except OSError as exc:
            raise PostgresKernelError("manifest_unreadable", "Migration manifest cannot be read") from exc
        manifest = normalize_manifest(parse_json_bytes(raw))
        canonical = canonical_json_bytes(manifest)
        if raw != canonical:
            raise PostgresKernelError("manifest_not_canonical", "Migration manifest bytes are not canonical")

        connection = self._connect()
        try:
            with connection, connection.transaction():
                cursor = connection.cursor()
                cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                self._configure_transaction(cursor)
                schema_name = self._current_schema(cursor)
                self._require_exact_schema(cursor, schema_name)
                # A migration owns one bounded target transaction, not live
                # agent work. After these locks, READ COMMITTED sees any writer
                # that finished while we waited; no stale snapshot can hide it.
                cursor.execute(
                    sql.SQL("LOCK TABLE {} IN SHARE ROW EXCLUSIVE MODE").format(
                        sql.SQL(",").join(
                            sql.SQL("{}.{}").format(sql.Identifier(schema_name), sql.Identifier(table))
                            for table in ALL_TABLES
                        )
                    )
                )
                for table in COORDINATION_TABLES:
                    if table == "session_init_bindings":
                        continue  # Immutable attribution is part of this import, not disposable bridge state.
                    cursor.execute(
                        sql.SQL("SELECT 1 FROM {}.{} LIMIT 1").format(
                            sql.Identifier(schema_name), sql.Identifier(table)
                        )
                    )
                    if cursor.fetchone() is not None:
                        raise PostgresKernelError(
                            "target_coordination_not_empty",
                            "Migration requires an empty target without existing coordination state",
                            details={"table": table},
                        )
                cursor.execute(
                    sql.SQL("SELECT count(*) AS count FROM {}.record_history").format(sql.Identifier(schema_name))
                )
                history_count = int(cursor.fetchone()["count"])
                current = self._readback_with_cursor(cursor, schema_name)
                if (
                    current["tables"]["session_init_bindings"]
                    and current["tables"]["session_init_bindings"] != manifest["tables"]["session_init_bindings"]
                ):
                    raise PostgresKernelError(
                        "target_coordination_not_empty",
                        "The target contains different immutable session bindings",
                        details={"table": "session_init_bindings"},
                    )
                current_count = self._row_count(current)
                expected_count = self._row_count(manifest)
                if canonical_json_bytes(current) == canonical and self._history_matches_manifest(
                    cursor,
                    schema_name,
                    manifest,
                ):
                    return {
                        "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
                        "row_count": expected_count,
                        "status": "already_current",
                    }
                if current_count or history_count:
                    raise PostgresKernelError(
                        "target_not_empty", "PostgreSQL target is partial or differs from manifest"
                    )

                for row in manifest["tables"]["session_init_bindings"]:
                    cursor.execute(
                        sql.SQL("INSERT INTO {}.session_init_bindings ({}) VALUES ({})").format(
                            sql.Identifier(schema_name),
                            sql.SQL(",").join(sql.Identifier(column) for column in BINDING_COLUMNS),
                            sql.SQL(",").join(sql.Placeholder() for _ in BINDING_COLUMNS),
                        ),
                        [row[column] for column in BINDING_COLUMNS],
                    )
                for table_name in CURRENT_TABLES:
                    spec = TABLE_SPECS[table_name]
                    for row in manifest["tables"][table_name]:
                        insert = sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
                            sql.Identifier(schema_name),
                            sql.Identifier(table_name),
                            sql.SQL(",").join(sql.Identifier(column) for column in spec.columns),
                            sql.SQL(",").join(sql.Placeholder() for _ in spec.columns),
                        )
                        values = [self._adapt_value(column, row[column], spec) for column in spec.columns]
                        cursor.execute(insert, values)
                        identity = {column: row[column] for column in spec.identity_columns}
                        cursor.execute(
                            sql.SQL(
                                "INSERT INTO {}.record_history "
                                "(record_type,record_id,prior_version,new_version,prior_state,new_state,actor,reason) "
                                "VALUES (%s,%s,NULL,1,NULL,%s,%s,%s)"
                            ).format(sql.Identifier(schema_name)),
                            (
                                table_name,
                                Jsonb(identity, dumps=_postgres_json_dumps),
                                Jsonb(row, dumps=_postgres_json_dumps),
                                actor,
                                reason,
                            ),
                        )
                readback = self._readback_with_cursor(cursor, schema_name)
                if canonical_json_bytes(readback) != canonical:
                    raise PostgresKernelError("import_readback_mismatch", "In-transaction PostgreSQL readback differs")
                return {
                    "manifest_sha256": hashlib.sha256(canonical).hexdigest(),
                    "row_count": expected_count,
                    "status": "imported",
                }
        except PostgresKernelError:
            raise
        except (SerializationFailure, DeadlockDetected, LockNotAvailable, UniqueViolation) as exc:
            raise PostgresKernelError(
                "retryable_conflict", "PostgreSQL import encountered a retryable conflict"
            ) from exc
        except Exception as exc:  # intentional-catch: driver failures surface as PostgresKernelError
            raise PostgresKernelError("postgres_operation_failed", "PostgreSQL import failed") from exc

    def readback_current(self, *, output: Path) -> dict[str, Any]:
        connection = self._connect()
        try:
            with connection, connection.transaction():
                cursor = connection.cursor()
                cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                self._configure_transaction(cursor)
                schema_name = self._current_schema(cursor)
                self._require_exact_schema(cursor, schema_name)
                manifest = self._readback_with_cursor(cursor, schema_name)
                payload = canonical_json_bytes(manifest)
        except PostgresKernelError:
            raise
        except Exception as exc:  # intentional-catch: driver failures surface as PostgresKernelError
            raise PostgresKernelError("postgres_operation_failed", "PostgreSQL readback failed") from exc
        publication = _publish_bytes(output, payload)
        return {
            "manifest_sha256": hashlib.sha256(payload).hexdigest(),
            "row_count": self._row_count(manifest),
            "status": publication,
        }

    def mutate_current(
        self,
        *,
        table: str,
        identity: Mapping[str, str],
        expected_version: int,
        new_state: Mapping[str, Any],
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        """Apply one trusted-service current-row CAS with literal row locking."""
        self._validate_mutation(table, identity, expected_version, new_state, actor, reason)
        with self.transaction(serializable=False) as transaction:
            return transaction.mutate(
                table=table,
                identity=identity,
                expected_version=expected_version,
                new_state=new_state,
                actor=actor,
                reason=reason,
            )

    @contextmanager
    def transaction(self, *, read_only: bool = False, serializable: bool = True) -> Iterator[PostgresTransaction]:
        """Group a domain operation and its readback in one native transaction.

        Serializable writes prevent write skew between membership and project
        operations. Read-only requests see one repeatable canonical snapshot.
        Conflicts are returned to the caller; effects are never retried blindly.
        """
        connection = self._connect()
        try:
            with connection, connection.transaction():
                cursor = connection.cursor()
                if read_only:
                    cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
                elif serializable:
                    cursor.execute("SET TRANSACTION ISOLATION LEVEL SERIALIZABLE")
                else:
                    # A single-row CAS waits on that row and compares its latest
                    # version. Multi-record domain operations use serializable.
                    cursor.execute("SET TRANSACTION ISOLATION LEVEL READ COMMITTED")
                self._configure_transaction(cursor)
                schema_name = self._current_schema(cursor)
                self._require_exact_schema(cursor, schema_name)
                yield PostgresTransaction(self, cursor, schema_name)
        except PostgresKernelError:
            raise
        except (SerializationFailure, DeadlockDetected, LockNotAvailable, UniqueViolation) as exc:
            raise PostgresKernelError(
                "retryable_conflict", "Concurrent canonical state changed; read current state before retrying"
            ) from exc
        except (CheckViolation, ForeignKeyViolation, NotNullViolation, DataError) as exc:
            raise PostgresKernelError("invalid_state", "PostgreSQL rejected the domain state") from exc
        except Exception as exc:  # intentional-catch: driver failures surface as PostgresKernelError
            raise PostgresKernelError("postgres_operation_failed", "PostgreSQL domain operation failed") from exc

    @staticmethod
    def _validate_mutation(
        table: str,
        identity: Mapping[str, str],
        expected_version: int,
        new_state: Mapping[str, Any],
        actor: str,
        reason: str,
    ) -> tuple[TableSpec, dict[str, str], dict[str, Any]]:
        if table not in TABLE_SPECS:
            raise PostgresKernelError("unknown_record_type", "Record type is not part of the PostgreSQL kernel")
        spec = TABLE_SPECS[table]
        if set(identity) != set(spec.identity_columns):
            raise PostgresKernelError("invalid_identity", "Record identity does not match its table")
        if (
            not isinstance(expected_version, int)
            or isinstance(expected_version, bool)
            or expected_version < 0
            or expected_version >= PG_INTEGER_MAX
        ):
            raise PostgresKernelError(
                "invalid_expected_version",
                "expected_version must permit a PostgreSQL integer successor",
            )
        try:
            normalized_identity = {
                column: _opaque_id(identity[column], label=f"{table}.{column}") for column in spec.identity_columns
            }
        except PostgresKernelError as exc:
            raise PostgresKernelError("invalid_identity", "Record identity values are invalid") from exc
        candidate = dict(new_state)
        if set(candidate) != set(spec.columns):
            raise PostgresKernelError("invalid_state", "Complete current-row state is required")
        candidate["version"] = expected_version + 1
        try:
            candidate = _normalize_manifest_row(table, candidate, require_version_one=False)
        except PostgresKernelError as exc:
            raise PostgresKernelError("invalid_state", "Current-row state is invalid") from exc
        for column, value in normalized_identity.items():
            if candidate.get(column) != value:
                raise PostgresKernelError("invalid_state", "State identity differs from requested identity")
        _opaque_id(actor, label="actor")
        _opaque_id(reason, label="reason")

        return spec, normalized_identity, candidate

    def _mutate_with_cursor(
        self,
        cursor: Any,
        schema_name: str,
        *,
        table: str,
        identity: Mapping[str, str],
        expected_version: int,
        new_state: Mapping[str, Any],
        actor: str,
        reason: str,
    ) -> dict[str, Any]:
        """Write and verify a current row inside the caller's transaction."""
        spec, normalized_identity, candidate = self._validate_mutation(
            table,
            identity,
            expected_version,
            new_state,
            actor,
            reason,
        )
        where = sql.SQL(" AND ").join(
            sql.SQL("{}=%s").format(sql.Identifier(column)) for column in spec.identity_columns
        )
        identity_values = [normalized_identity[column] for column in spec.identity_columns]
        cursor.execute(
            sql.SQL("SELECT {} FROM {}.{} WHERE {} FOR UPDATE").format(
                _select_columns(spec),
                sql.Identifier(schema_name),
                sql.Identifier(table),
                where,
            ),
            identity_values,
        )
        existing_raw = cursor.fetchone()
        if existing_raw is None:
            if expected_version != 0:
                raise PostgresKernelError("cas_conflict", "Current record does not match expected version")
            cursor.execute(
                sql.SQL("INSERT INTO {}.{} ({}) VALUES ({})").format(
                    sql.Identifier(schema_name),
                    sql.Identifier(table),
                    sql.SQL(",").join(sql.Identifier(column) for column in spec.columns),
                    sql.SQL(",").join(sql.Placeholder() for _ in spec.columns),
                ),
                [self._adapt_value(column, candidate[column], spec) for column in spec.columns],
            )
            prior: dict[str, Any] | None = None
            cursor.execute(
                sql.SQL(
                    "INSERT INTO {}.record_history "
                    "(record_type,record_id,prior_version,new_version,prior_state,new_state,actor,reason) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                ).format(sql.Identifier(schema_name)),
                (
                    table,
                    Jsonb(normalized_identity, dumps=_postgres_json_dumps),
                    None,
                    candidate["version"],
                    None,
                    Jsonb(candidate, dumps=_postgres_json_dumps),
                    actor,
                    reason,
                ),
            )
        else:
            prior = _normalize_pg_row(dict(existing_raw), spec)
            if prior.get("version") != expected_version:
                raise PostgresKernelError("cas_conflict", "Current record does not match expected version")
            cursor.execute(
                sql.SQL(
                    "INSERT INTO {}.record_history "
                    "(record_type,record_id,prior_version,new_version,prior_state,new_state,actor,reason) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                ).format(sql.Identifier(schema_name)),
                (
                    table,
                    Jsonb(normalized_identity, dumps=_postgres_json_dumps),
                    prior["version"],
                    candidate["version"],
                    Jsonb(prior, dumps=_postgres_json_dumps),
                    Jsonb(candidate, dumps=_postgres_json_dumps),
                    actor,
                    reason,
                ),
            )
            assignments = [column for column in spec.columns if column not in spec.identity_columns]
            cursor.execute(
                sql.SQL("UPDATE {}.{} SET {} WHERE {}").format(
                    sql.Identifier(schema_name),
                    sql.Identifier(table),
                    sql.SQL(",").join(sql.SQL("{}=%s").format(sql.Identifier(column)) for column in assignments),
                    where,
                ),
                [self._adapt_value(column, candidate[column], spec) for column in assignments] + identity_values,
            )
        cursor.execute(
            sql.SQL("SELECT {} FROM {}.{} WHERE {}").format(
                _select_columns(spec),
                sql.Identifier(schema_name),
                sql.Identifier(table),
                where,
            ),
            identity_values,
        )
        readback = cursor.fetchone()
        if readback is None:
            raise PostgresKernelError(
                "mutation_readback_mismatch",
                "PostgreSQL current-row readback is missing",
            )
        normalized_readback = _normalize_pg_row(dict(readback), spec)
        if canonical_json_bytes(normalized_readback) != canonical_json_bytes(candidate):
            raise PostgresKernelError(
                "mutation_readback_mismatch",
                "PostgreSQL current-row readback differs from requested state",
            )
        return {"record": normalized_readback, "status": "updated" if prior else "created"}


class PostgresTransaction:
    """Internal row primitives; public callers use typed domain services."""

    def __init__(self, kernel: PostgresKernel, cursor: Any, schema: str) -> None:
        self.kernel = kernel
        self.cursor = cursor
        self.schema = schema

    def get(self, table: str, identity: Mapping[str, str], *, lock: bool = False) -> dict[str, Any] | None:
        spec = TABLE_SPECS[table]
        if set(identity) != set(spec.identity_columns):
            raise PostgresKernelError("invalid_identity", "Record identity does not match its domain")
        where = sql.SQL(" AND ").join(sql.SQL("{}=%s").format(sql.Identifier(c)) for c in identity)
        self.cursor.execute(
            sql.SQL("SELECT {} FROM {}.{} WHERE {}{}").format(
                _select_columns(spec),
                sql.Identifier(self.schema),
                sql.Identifier(table),
                where,
                sql.SQL(" FOR UPDATE" if lock else ""),
            ),
            list(identity.values()),
        )
        row = self.cursor.fetchone()
        return _normalize_pg_row(dict(row), spec) if row else None

    def list(
        self,
        table: str,
        *,
        filters: Mapping[str, Any] | None = None,
        after: str | None = None,
        limit: int = 200,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        spec = TABLE_SPECS[table]
        if spec.identity_columns != ("id",) or not 1 <= limit <= 1000:
            raise PostgresKernelError("invalid_query", "This query requires an id domain and a limit from 1 to 1000")
        terms, values = [], []
        for column, value in (filters or {}).items():
            if column not in spec.columns or column in spec.json_columns:
                raise PostgresKernelError("invalid_query", "Unsupported domain filter")
            terms.append(sql.SQL("{} IS NOT DISTINCT FROM %s").format(sql.Identifier(column)))
            values.append(value)
        if after is not None:
            terms.append(sql.SQL('id COLLATE "C" > %s'))
            values.append(after)
        if search is not None:
            search_columns = [
                c
                for c in ("title", "name", "description", "purpose", "canonical_term", "definition")
                if c in spec.columns
            ]
            if not search_columns:
                raise PostgresKernelError("invalid_query", "Search is unavailable for this domain")
            terms.append(
                sql.SQL("({})").format(
                    sql.SQL(" OR ").join(
                        sql.SQL("strpos(lower(coalesce({},'')),lower(%s)) > 0").format(sql.Identifier(c))
                        for c in search_columns
                    )
                )
            )
            values.extend([search] * len(search_columns))
        self.cursor.execute(
            sql.SQL('SELECT {} FROM {}.{} WHERE {} ORDER BY id COLLATE "C" LIMIT %s').format(
                _select_columns(spec),
                sql.Identifier(self.schema),
                sql.Identifier(table),
                sql.SQL(" AND ").join(terms) if terms else sql.SQL("true"),
            ),
            [*values, limit],
        )
        return [_normalize_pg_row(dict(row), spec) for row in self.cursor.fetchall()]

    def mutate(self, **request: Any) -> dict[str, Any]:
        return self.kernel._mutate_with_cursor(self.cursor, self.schema, **request)
