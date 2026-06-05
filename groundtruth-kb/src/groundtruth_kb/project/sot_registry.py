# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""SoT (Source-of-Truth) artifact registry — single platform-wide inventory.

Implements DCL-SOT-REGISTRY-PROJECTION-PARITY-001 (TOML/MemBase parity) and
DCL-SOT-REGISTRY-RECORD-SCHEMA-001 (per-record schema), in service of
GOV-PLATFORM-SOT-REGISTRY-001 (every SoT class MUST be registered).

The registry lives at ``config/registry/sot-artifacts.toml`` and is parsed
into typed dataclasses. The registry projection in MemBase
(``sot_artifacts`` table) is regenerated from TOML via :func:`sync_projection`.

Loader-enforced invariants (:class:`InvalidSoTRecord` on violation):

- All 10 required fields present.
- ``domain``, ``lifecycle``, ``versioning_policy``, ``backup_policy``,
  ``owner_role`` values are in their respective enums.
- ``lifecycle='generated'`` rows have a non-trivial ``mutation_api`` (acts as
  generator pointer).
- ``id`` is unique across the file.

This module is a pure reader/projector — it does not mutate the filesystem
or MemBase except through explicit :func:`sync_projection` calls.

Reference precedent: ``groundtruth_kb.project.managed_registry``.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

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

_VALID_OWNER_ROLES: frozenset[str] = frozenset(
    {"prime_builder", "loyal_opposition", "owner_only", "shared", "automated_only"}
)

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
    }
)

_OPTIONAL_FIELDS: frozenset[str] = frozenset({"depends_on", "forbidden_substitutes", "notes"})

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
    depends_on: tuple[str, ...] = ()
    forbidden_substitutes: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class ParityReport:
    """Result of comparing TOML-loaded records against MemBase projection."""

    in_sync: bool
    toml_count: int
    projection_count: int
    missing_in_projection: tuple[str, ...]
    missing_in_toml: tuple[str, ...]
    field_divergences: tuple[tuple[str, str], ...]  # (id, field_name) pairs


@dataclass(frozen=True)
class SyncReport:
    """Result of regenerating MemBase projection from TOML."""

    inserted: tuple[str, ...]
    updated: tuple[str, ...]
    unchanged: tuple[str, ...]


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


def _parse_record(record: dict[str, Any]) -> SoTArtifact:
    record_id = str(record.get("id", "<missing-id>"))

    _validate_unknown_fields(record, record_id)
    _validate_required(record, record_id)
    _validate_enum(record, "domain", _VALID_DOMAINS, record_id)
    _validate_enum(record, "lifecycle", _VALID_LIFECYCLES, record_id)
    _validate_enum(record, "versioning_policy", _VALID_VERSIONING, record_id)
    _validate_enum(record, "backup_policy", _VALID_BACKUP, record_id)
    _validate_enum(record, "owner_role", _VALID_OWNER_ROLES, record_id)

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
        depends_on=_coerce_str_tuple(record.get("depends_on"), record_id, "depends_on"),
        forbidden_substitutes=_coerce_str_tuple(
            record.get("forbidden_substitutes"), record_id, "forbidden_substitutes"
        ),
        notes=str(record.get("notes", "")),
    )


def load_toml(path: Path) -> list[SoTArtifact]:
    """Load and validate the SoT artifact registry from a TOML file.

    Raises :class:`InvalidSoTRecord` or :class:`UnknownDomain` on schema
    violations. Raises :class:`FileNotFoundError` if path does not exist.
    Duplicate ids cause :class:`InvalidSoTRecord`.
    """

    if not path.exists():
        raise FileNotFoundError(f"sot-artifacts.toml not found at {path}")

    with path.open("rb") as fh:
        data = tomllib.load(fh)

    raw_records = data.get("artifacts", [])
    if not isinstance(raw_records, list):
        raise InvalidSoTRecord(f"top-level 'artifacts' must be a list of tables, got {type(raw_records).__name__}")

    records: list[SoTArtifact] = []
    seen_ids: set[str] = set()
    for raw in raw_records:
        if not isinstance(raw, dict):
            raise InvalidSoTRecord(f"each artifacts entry must be a table, got {type(raw).__name__}")
        record = _parse_record(raw)
        if record.id in seen_ids:
            raise InvalidSoTRecord(f"duplicate id: {record.id!r}")
        seen_ids.add(record.id)
        records.append(record)

    return records


# ---------------------------------------------------------------------------
# Default registry path
# ---------------------------------------------------------------------------


def default_registry_path(project_root: Path | None = None) -> Path:
    """Return the canonical path to ``config/registry/sot-artifacts.toml``.

    If ``project_root`` is None, derives from the location of this module
    (assumes installed-package layout).
    """

    if project_root is None:
        # This module lives at:
        # <project_root>/groundtruth-kb/src/groundtruth_kb/project/sot_registry.py
        # so project_root is 4 parents up.
        project_root = Path(__file__).resolve().parents[4]
    return project_root / "config" / "registry" / "sot-artifacts.toml"


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


# ---------------------------------------------------------------------------
# MemBase projection (DB read/write)
# ---------------------------------------------------------------------------


def load_projection(db_path: Path | str) -> list[SoTArtifact]:
    """Load all ``current_sot_artifacts`` rows from MemBase as SoTArtifact records.

    Returns an empty list if the table or view doesn't exist yet (fresh DB).
    """
    import json
    import sqlite3

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        # Tolerate fresh DBs where the view doesn't yet exist.
        try:
            cur.execute(
                "SELECT id, domain, lifecycle, storage_path, authority_spec_id, "
                "mutation_api, versioning_policy, backup_policy, "
                "health_check_function, owner_role, depends_on, "
                "forbidden_substitutes, notes "
                "FROM current_sot_artifacts ORDER BY id"
            )
        except sqlite3.OperationalError:
            return []
        rows = cur.fetchall()
    finally:
        conn.close()
    records: list[SoTArtifact] = []
    for row in rows:
        depends_on = tuple(json.loads(row[10])) if row[10] else ()
        forbidden = tuple(json.loads(row[11])) if row[11] else ()
        records.append(
            SoTArtifact(
                id=row[0],
                domain=row[1],
                lifecycle=row[2],
                storage_path=row[3],
                authority_spec_id=row[4],
                mutation_api=row[5],
                versioning_policy=row[6],
                backup_policy=row[7],
                health_check_function=row[8],
                owner_role=row[9],
                depends_on=depends_on,
                forbidden_substitutes=forbidden,
                notes=row[12] or "",
            )
        )
    return records


def sync_projection(
    toml_records: list[SoTArtifact],
    db_path: Path | str,
    *,
    changed_by: str = "gt-registry-sync",
    change_reason: str = "gt registry sync",
) -> SyncReport:
    """Regenerate the ``sot_artifacts`` projection from TOML records.

    Inserts a new version row for each TOML record whose declared fields differ
    from the latest projection row (or whose ID has no projection row yet).
    Returns a :class:`SyncReport` enumerating inserted / updated / unchanged IDs.
    """
    import json
    import sqlite3
    from datetime import UTC, datetime

    proj_by_id = {r.id: r for r in load_projection(db_path)}
    inserted: list[str] = []
    updated: list[str] = []
    unchanged: list[str] = []
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        for rec in toml_records:
            existing = proj_by_id.get(rec.id)
            if existing is not None:
                # Compare all schema fields.
                same = all(getattr(existing, f) == getattr(rec, f) for f in (_REQUIRED_FIELDS | _OPTIONAL_FIELDS))
                if same:
                    unchanged.append(rec.id)
                    continue
            cur.execute(
                "SELECT COALESCE(MAX(version), 0) FROM sot_artifacts WHERE id = ?",
                (rec.id,),
            )
            current_version = cur.fetchone()[0]
            next_version = current_version + 1
            cur.execute(
                """
                INSERT INTO sot_artifacts (
                    id, version, domain, lifecycle, storage_path,
                    authority_spec_id, mutation_api, versioning_policy,
                    backup_policy, health_check_function, owner_role,
                    depends_on, forbidden_substitutes, notes,
                    changed_by, changed_at, change_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec.id,
                    next_version,
                    rec.domain,
                    rec.lifecycle,
                    rec.storage_path,
                    rec.authority_spec_id,
                    rec.mutation_api,
                    rec.versioning_policy,
                    rec.backup_policy,
                    rec.health_check_function,
                    rec.owner_role,
                    json.dumps(list(rec.depends_on)) if rec.depends_on else None,
                    json.dumps(list(rec.forbidden_substitutes)) if rec.forbidden_substitutes else None,
                    rec.notes or None,
                    changed_by,
                    now,
                    change_reason,
                ),
            )
            if existing is None:
                inserted.append(rec.id)
            else:
                updated.append(rec.id)
        conn.commit()
    finally:
        conn.close()

    return SyncReport(
        inserted=tuple(inserted),
        updated=tuple(updated),
        unchanged=tuple(unchanged),
    )
