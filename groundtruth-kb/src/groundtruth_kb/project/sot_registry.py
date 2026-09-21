# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Typed current declarations for the platform artifact registry.

The canonical source is ``config/registry/sot-artifacts.toml``. Public reads
validate record fields, explicit lifecycle/coverage, locators and ambiguity.
Projections never supply current membership or gate a canonical read.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


def registry_path_observations(
    *,
    specifications: Iterable[Mapping[str, Any]],
    tests: Iterable[Mapping[str, Any]],
    documents: Iterable[Mapping[str, Any]],
    project_artifact_links: Iterable[Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Extract typed current path fields, without interpreting narrative prose."""
    observations: dict[tuple[str, str, str, str], dict[str, str]] = {}

    def append(source_kind: str, source_id: Any, field: str, value: Any) -> None:
        if value is None:
            return
        if not isinstance(value, str):
            raise ValueError(f"{source_kind}:{source_id}:{field} must contain a path string")
        path = value.strip().split("::", 1)[0]
        if path:
            row = {"path": path, "source_kind": source_kind, "source_id": str(source_id), "field": field}
            observations[(path.casefold(), source_kind, str(source_id), field)] = row

    for spec in specifications:
        values = spec.get("source_paths")
        if values is None:
            continue
        if isinstance(values, str):
            try:
                values = json.loads(values)
            except json.JSONDecodeError as exc:
                raise ValueError(f"specification:{spec['id']}:source_paths is not valid JSON") from exc
        if not isinstance(values, (list, tuple)):
            raise ValueError(f"specification:{spec['id']}:source_paths must be a list of paths")
        for value in values:
            if not isinstance(value, str):
                raise ValueError(f"specification:{spec['id']}:source_paths must be a list of paths")
            append("specification", spec["id"], "source_paths", value)
    for test in tests:
        append("test", test["id"], "test_file", test.get("test_file"))
    for document in documents:
        append("document", document["id"], "source_path", document.get("source_path"))
    path_types = {"configuration", "document", "file", "path", "source_file", "test"}
    for link in project_artifact_links:
        if link.get("status") == "active" and str(link.get("artifact_type") or "").casefold() in path_types:
            append("project_artifact_link", link["id"], "artifact_ref", link.get("artifact_ref"))
    return [observations[key] for key in sorted(observations)]


# ---------------------------------------------------------------------------
# Enum types
# ---------------------------------------------------------------------------

Domain = Literal[
    "specifications",
    "narrative_authority",
    "bridge_protocol",
    "harness_state",
    "control_surface",
    "governance_policy",
    "runtime_state",
    "scaffold_lifecycle",
    "operational_notepad",
    "retired",
]

Lifecycle = Literal["active", "deprecated", "archive", "generated"]

VersioningPolicy = Literal[
    "append_only_versioned",
    "overwrite_single_writer",
    "regenerated_from_source",
    "git_tracked",
    "immutable_archive",
]

BackupPolicy = Literal[
    "git_tracked",
    "membase_export",
    "regenerable_from_source",
    "gitignored_runtime",
    "external_backup",
]

RestoreAction = Literal[
    "manual",
    "visibility_only",
    "git_restore",
    "membase_export_restore",
    "regenerate_from_source",
    "ensure_alive",
    "noop",
]

CoverageMode = Literal["exact", "recursive", "glob", "opaque_container", "virtual"]

OwnerRole = Literal[
    "prime_builder",
    "loyal_opposition",
    "owner_only",
    "shared",
    "automated_only",
]

_VALID_DOMAINS: frozenset[str] = frozenset(
    {
        "specifications",
        "narrative_authority",
        "bridge_protocol",
        "harness_state",
        "control_surface",
        "governance_policy",
        "runtime_state",
        "scaffold_lifecycle",
        "operational_notepad",
        "retired",
    }
)

_VALID_LIFECYCLES: frozenset[str] = frozenset({"active", "deprecated", "archive", "generated"})

_VALID_VERSIONING: frozenset[str] = frozenset(
    {
        "append_only_versioned",
        "overwrite_single_writer",
        "regenerated_from_source",
        "git_tracked",
        "immutable_archive",
    }
)

_VALID_BACKUP: frozenset[str] = frozenset(
    {
        "git_tracked",
        "membase_export",
        "regenerable_from_source",
        "gitignored_runtime",
        "external_backup",
    }
)

_VALID_RESTORE_ACTIONS: frozenset[str] = frozenset(
    {
        "manual",
        "visibility_only",
        "git_restore",
        "membase_export_restore",
        "regenerate_from_source",
        "ensure_alive",
        "noop",
    }
)

_VALID_OWNER_ROLES: frozenset[str] = frozenset(
    {"prime_builder", "loyal_opposition", "owner_only", "shared", "automated_only"}
)

_VALID_COVERAGE_MODES: frozenset[str] = frozenset({"exact", "recursive", "glob", "opaque_container", "virtual"})

_DEFAULT_RESTORE_ACTION: RestoreAction = "manual"

_REQUIRED_FIELDS: frozenset[str] = frozenset(
    {
        "id",
        "domain",
        "lifecycle",
        "storage_path",
        "authority_spec_id",
        "mutation_api",
        "versioning_policy",
        "backup_policy",
        "health_check_function",
        "owner_role",
        "coverage_mode",
    }
)

_OPTIONAL_FIELDS: frozenset[str] = frozenset({"restore_action", "depends_on", "forbidden_substitutes", "notes"})

_ALL_KNOWN_FIELDS: frozenset[str] = _REQUIRED_FIELDS | _OPTIONAL_FIELDS


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class InvalidSoTRecord(ValueError):
    """Raised when a record in sot-artifacts.toml fails schema validation."""


class UnknownDomain(ValueError):
    """Raised when a domain value is outside the enum."""


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SoTArtifact:
    """One row of the SoT artifact registry per DCL-SOT-REGISTRY-RECORD-SCHEMA-001."""

    id: str
    domain: Domain
    lifecycle: Lifecycle
    storage_path: str
    authority_spec_id: str
    mutation_api: str
    versioning_policy: VersioningPolicy
    backup_policy: BackupPolicy
    health_check_function: str | None
    owner_role: OwnerRole
    restore_action: RestoreAction = _DEFAULT_RESTORE_ACTION
    depends_on: tuple[str, ...] = ()
    forbidden_substitutes: tuple[str, ...] = ()
    notes: str = ""
    coverage_mode: CoverageMode | None = None


@dataclass(frozen=True)
class ParityReport:
    """Result of comparing TOML-loaded records against MemBase projection."""

    in_sync: bool
    toml_count: int
    projection_count: int
    missing_in_projection: tuple[str, ...]
    missing_in_toml: tuple[str, ...]
    field_divergences: tuple[tuple[str, str], ...]  # (id, field_name) pairs


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _coerce_str_tuple(value: Any, record_id: str, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raise InvalidSoTRecord(f"record {record_id!r} field {field_name!r}: expected list of strings, got string")
    if not isinstance(value, list):
        raise InvalidSoTRecord(f"record {record_id!r} field {field_name!r}: expected list, got {type(value).__name__}")
    for item in value:
        if not isinstance(item, str):
            raise InvalidSoTRecord(f"record {record_id!r} field {field_name!r}: list item not a string: {item!r}")
    return tuple(value)


def _validate_required(record: dict[str, Any], record_id: str) -> None:
    missing = _REQUIRED_FIELDS - set(record.keys())
    if missing:
        raise InvalidSoTRecord(f"record {record_id!r}: missing required field(s): {sorted(missing)}")


def _validate_enum(record: dict[str, Any], field_name: str, valid_set: frozenset[str], record_id: str) -> None:
    value = record[field_name]
    if value not in valid_set:
        if field_name == "domain":
            raise UnknownDomain(f"record {record_id!r} field domain={value!r}: not in enum {sorted(valid_set)}")
        raise InvalidSoTRecord(f"record {record_id!r} field {field_name}={value!r}: not in enum {sorted(valid_set)}")


def _validate_unknown_fields(record: dict[str, Any], record_id: str) -> None:
    unknown = set(record.keys()) - _ALL_KNOWN_FIELDS
    if unknown:
        raise InvalidSoTRecord(f"record {record_id!r}: unknown field(s): {sorted(unknown)}")


def _parse_record(record: dict[str, Any], *, allow_missing_coverage: bool = False) -> SoTArtifact:
    record_id = str(record.get("id", "<missing-id>"))

    _validate_unknown_fields(record, record_id)
    if allow_missing_coverage and "coverage_mode" not in record:
        missing = (_REQUIRED_FIELDS - {"coverage_mode"}) - set(record)
        if missing:
            raise InvalidSoTRecord(f"record {record_id!r}: missing required field(s): {sorted(missing)}")
        record = {**record, "coverage_mode": None}
    else:
        _validate_required(record, record_id)
    for field in (_REQUIRED_FIELDS | {"restore_action", "notes"}) - {"health_check_function", "coverage_mode"}:
        if field in record and not isinstance(record[field], str):
            raise InvalidSoTRecord(f"record {record_id!r}: {field} must be a string")
    if record.get("coverage_mode") is not None and not isinstance(record["coverage_mode"], str):
        raise InvalidSoTRecord(f"record {record_id!r}: coverage_mode must be a string")
    _validate_enum(record, "domain", _VALID_DOMAINS, record_id)
    _validate_enum(record, "lifecycle", _VALID_LIFECYCLES, record_id)
    _validate_enum(record, "versioning_policy", _VALID_VERSIONING, record_id)
    _validate_enum(record, "backup_policy", _VALID_BACKUP, record_id)
    _validate_enum(record, "owner_role", _VALID_OWNER_ROLES, record_id)
    coverage_mode = record.get("coverage_mode")
    if coverage_mode is not None and coverage_mode not in _VALID_COVERAGE_MODES:
        raise InvalidSoTRecord(
            f"record {record_id!r} field coverage_mode={coverage_mode!r}: not in enum {sorted(_VALID_COVERAGE_MODES)}"
        )
    if coverage_mode is None and not allow_missing_coverage:
        raise InvalidSoTRecord(f"record {record_id!r}: coverage_mode is required")
    restore_action = record.get("restore_action", _DEFAULT_RESTORE_ACTION)
    if restore_action not in _VALID_RESTORE_ACTIONS:
        raise InvalidSoTRecord(
            f"record {record_id!r} field restore_action={restore_action!r}: "
            f"not in enum {sorted(_VALID_RESTORE_ACTIONS)}"
        )

    health_check = record["health_check_function"]
    if health_check is not None and not isinstance(health_check, str):
        raise InvalidSoTRecord(f"record {record_id!r}: health_check_function must be string or null")

    if record["lifecycle"] == "generated":
        mutation_api = record["mutation_api"]
        if not mutation_api or mutation_api.strip() == "":
            raise InvalidSoTRecord(
                f"record {record_id!r}: lifecycle=generated requires non-empty mutation_api (generator pointer)"
            )

    return SoTArtifact(
        id=record["id"],
        domain=record["domain"],
        lifecycle=record["lifecycle"],
        storage_path=record["storage_path"],
        authority_spec_id=record["authority_spec_id"],
        mutation_api=record["mutation_api"],
        versioning_policy=record["versioning_policy"],
        backup_policy=record["backup_policy"],
        health_check_function=health_check,
        owner_role=record["owner_role"],
        restore_action=restore_action,
        depends_on=_coerce_str_tuple(record.get("depends_on"), record_id, "depends_on"),
        forbidden_substitutes=_coerce_str_tuple(
            record.get("forbidden_substitutes"), record_id, "forbidden_substitutes"
        ),
        notes=str(record.get("notes", "")),
        coverage_mode=coverage_mode,
    )


def _load_toml_bytes(payload: bytes, *, allow_missing_coverage: bool = False) -> list[SoTArtifact]:
    """Parse one exact TOML byte payload into validated registry records."""

    try:
        data = tomllib.loads(payload.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise InvalidSoTRecord(f"Invalid registry TOML: {exc}") from exc
    raw_records = data.get("artifacts", [])
    if not isinstance(raw_records, list):
        raise InvalidSoTRecord(f"top-level 'artifacts' must be a list of tables, got {type(raw_records).__name__}")

    records: list[SoTArtifact] = []
    seen_ids: set[str] = set()
    for raw in raw_records:
        if not isinstance(raw, dict):
            raise InvalidSoTRecord(f"each artifacts entry must be a table, got {type(raw).__name__}")
        record = _parse_record(raw, allow_missing_coverage=allow_missing_coverage)
        if record.id in seen_ids:
            raise InvalidSoTRecord(f"duplicate id: {record.id!r}")
        seen_ids.add(record.id)
        records.append(record)

    return records


def _load_toml_unlocked(path: Path, *, allow_missing_coverage: bool = False) -> list[SoTArtifact]:
    """Load and validate the SoT artifact registry from a TOML file.

    Raises :class:`InvalidSoTRecord` or :class:`UnknownDomain` on schema
    violations. Raises :class:`FileNotFoundError` if path does not exist.
    Duplicate ids cause :class:`InvalidSoTRecord`.
    """

    if not path.exists():
        raise FileNotFoundError(f"sot-artifacts.toml not found at {path}")
    return _load_toml_bytes(path.read_bytes(), allow_missing_coverage=allow_missing_coverage)


def load_toml(path: Path) -> list[SoTArtifact]:
    """Read the canonical TOML declaration without consulting or changing replicas."""
    from groundtruth_kb.project.registry_control_plane import RegistryCoverageError, RegistryResolver

    records = _load_toml_unlocked(path)
    try:
        RegistryResolver(records)
    except RegistryCoverageError as exc:
        raise InvalidSoTRecord(str(exc)) from exc
    return records


# ---------------------------------------------------------------------------
# Default registry path
# ---------------------------------------------------------------------------


def default_registry_path(project_root: Path | None = None) -> Path:
    """Return the selected project's declaration, independent of package location."""
    if project_root is None:
        raise ValueError("project_root is required; the installed package location is not project authority")
    return Path(project_root).resolve() / "config" / "registry" / "sot-artifacts.toml"


# ---------------------------------------------------------------------------
# Parity validation
# ---------------------------------------------------------------------------


def _records_to_dict(records: list[SoTArtifact]) -> dict[str, SoTArtifact]:
    return {r.id: r for r in records}


def validate_projection_parity(
    toml_records: list[SoTArtifact],
    projection_records: list[SoTArtifact],
) -> ParityReport:
    """Compare TOML-loaded records against MemBase projection.

    Returns a :class:`ParityReport` describing membership and field-level
    divergences. ``in_sync`` is True iff no divergences are found.
    """

    toml_by_id = _records_to_dict(toml_records)
    proj_by_id = _records_to_dict(projection_records)

    missing_in_proj = tuple(sorted(set(toml_by_id) - set(proj_by_id)))
    missing_in_toml = tuple(sorted(set(proj_by_id) - set(toml_by_id)))

    common_ids = set(toml_by_id) & set(proj_by_id)
    divergences: list[tuple[str, str]] = []
    for artifact_id in sorted(common_ids):
        toml_rec = toml_by_id[artifact_id]
        proj_rec = proj_by_id[artifact_id]
        for fname in _REQUIRED_FIELDS | _OPTIONAL_FIELDS:
            tv = getattr(toml_rec, fname)
            pv = getattr(proj_rec, fname)
            if tv != pv:
                divergences.append((artifact_id, fname))

    return ParityReport(
        in_sync=(not missing_in_proj and not missing_in_toml and not divergences),
        toml_count=len(toml_records),
        projection_count=len(projection_records),
        missing_in_projection=missing_in_proj,
        missing_in_toml=missing_in_toml,
        field_divergences=tuple(divergences),
    )
