# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Managed artifact registry — single source of truth for scaffold, upgrade, and doctor.

The registry lives at ``templates/managed-artifacts.toml`` and is parsed at runtime
into a typed dataclass structure. Three independent lifecycle axes per record:

- ``initial_profiles``         — scaffold copies the artifact for these profiles
- ``managed_profiles``         — upgrade enforces drift/missing-file repair
- ``doctor_required_profiles`` — doctor enforces presence as a simple required check

Invariants (loader-enforced, :class:`InvalidArtifactRecord` on violation):

- ``managed_profiles ⊆ initial_profiles``
- ``doctor_required_profiles ⊆ initial_profiles``
- each class has its own required/forbidden key schema

This module is a pure reader — it does not mutate filesystems. Consumers use the
``artifacts_for_*`` helpers to obtain a filtered view for a given profile and
(optional) class.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

from groundtruth_kb import get_templates_dir

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


ArtifactClass = Literal[
    "hook",
    "rule",
    "skill",
    "settings-hook-registration",
    "gitignore-pattern",
    "ownership-glob",
]

SettingsEvent = Literal[
    "SessionStart",
    "UserPromptSubmit",
    "PostToolUse",
    "PreToolUse",
]

# Ownership-matrix enum literals (bridge/gtkb-artifact-ownership-matrix-003.md §1.3).
OwnershipEnum = Literal[
    "gt-kb-managed",
    "gt-kb-scaffolded",
    "shared-structured",
    "adopter-owned",
    "legacy-exception",
]

UpgradePolicyEnum = Literal[
    "overwrite",
    "structured-merge",
    "adopter-opt-in",
    "preserve",
    "transient",
]

DivergencePolicyEnum = Literal[
    "warn",
    "error",
    "force-merge-on-upgrade",
]

_VALID_ARTIFACT_CLASSES: frozenset[str] = frozenset(
    {
        "hook",
        "rule",
        "skill",
        "settings-hook-registration",
        "gitignore-pattern",
        "ownership-glob",
    }
)

_VALID_SETTINGS_EVENTS: frozenset[str] = frozenset({"SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"})

_FILE_CLASSES: frozenset[str] = frozenset({"hook", "rule", "skill"})

_VALID_OWNERSHIP_VALUES: frozenset[str] = frozenset(
    {"gt-kb-managed", "gt-kb-scaffolded", "shared-structured", "adopter-owned", "legacy-exception"}
)

_VALID_UPGRADE_POLICIES: frozenset[str] = frozenset(
    {"overwrite", "structured-merge", "adopter-opt-in", "preserve", "transient"}
)

_VALID_DIVERGENCE_POLICIES: frozenset[str] = frozenset({"warn", "error", "force-merge-on-upgrade"})

# Upgrade policies that require adopter_divergence_policy to be explicitly set.
# Rows with ``upgrade_policy`` in {preserve, transient} MUST omit divergence policy.
_UPGRADE_POLICIES_REQUIRING_DIVERGENCE: frozenset[str] = frozenset({"overwrite", "structured-merge", "adopter-opt-in"})

# The 3 ownership keys that define an ownership block. C1: defaults apply iff
# ALL three are absent. If any of the three are present, the block is treated
# as explicitly declared and fully validated.
_OWNERSHIP_BLOCK_KEYS: frozenset[str] = frozenset({"ownership", "upgrade_policy", "adopter_divergence_policy"})


# Per-class defaults applied when the entire ownership block is absent from a
# legacy row (GO Condition C1). All-or-none: partial blocks raise.
_CLASS_OWNERSHIP_DEFAULTS: dict[str, tuple[str, str, str]] = {
    "hook": ("gt-kb-managed", "overwrite", "warn"),
    "rule": ("gt-kb-managed", "overwrite", "warn"),
    "skill": ("gt-kb-managed", "overwrite", "warn"),
    "settings-hook-registration": ("gt-kb-managed", "structured-merge", "warn"),
    "gitignore-pattern": ("gt-kb-managed", "structured-merge", "warn"),
}


@dataclass(frozen=True)
class OwnershipMeta:
    """Typed ownership metadata attached to every parsed artifact (GO C2).

    ``adopter_divergence_policy`` is ``None`` iff ``upgrade_policy`` is one of
    ``preserve`` / ``transient``. Enforced by :func:`_extract_ownership_block`.
    """

    ownership: OwnershipEnum
    upgrade_policy: UpgradePolicyEnum
    adopter_divergence_policy: DivergencePolicyEnum | None
    workflow_targets: tuple[str, ...] = ()


@dataclass(frozen=True)
class FileArtifact:
    """Managed hook, rule, or skill file.

    Class value is stored in ``class_`` because ``class`` is a Python keyword.
    """

    class_: Literal["hook", "rule", "skill"]
    id: str
    template_path: str
    target_path: str
    initial_profiles: tuple[str, ...]
    managed_profiles: tuple[str, ...]
    doctor_required_profiles: tuple[str, ...]
    ownership: OwnershipMeta | None = None


@dataclass(frozen=True)
class SettingsHookRegistration:
    """Managed hook registration inside ``.claude/settings.json``."""

    class_: Literal["settings-hook-registration"]
    id: str
    event: SettingsEvent
    hook_filename: str
    target_settings_path: str
    initial_profiles: tuple[str, ...]
    managed_profiles: tuple[str, ...]
    doctor_required_profiles: tuple[str, ...]
    ownership: OwnershipMeta | None = None


@dataclass(frozen=True)
class GitignorePattern:
    """Managed ``.gitignore`` pattern."""

    class_: Literal["gitignore-pattern"]
    id: str
    pattern: str
    comment: str
    initial_profiles: tuple[str, ...]
    managed_profiles: tuple[str, ...]
    doctor_required_profiles: tuple[str, ...]
    ownership: OwnershipMeta | None = None


@dataclass(frozen=True)
class OwnershipGlobArtifact:
    """Sibling ownership-map record keyed by ``path_glob`` rather than ``target_path``.

    Loaded from ``templates/scaffold-ownership.toml``. The ``ownership`` block
    is REQUIRED (never default-derived) — ownership-glob rows exist solely to
    carry ownership metadata. The ``priority`` integer (higher wins) drives
    glob-conflict resolution in :class:`OwnershipResolver`.
    """

    class_: Literal["ownership-glob"]
    id: str
    path_glob: str
    priority: int
    initial_profiles: tuple[str, ...]
    managed_profiles: tuple[str, ...]
    doctor_required_profiles: tuple[str, ...]
    ownership: OwnershipMeta
    notes: str = ""


ManagedArtifact = FileArtifact | SettingsHookRegistration | GitignorePattern | OwnershipGlobArtifact


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class UnknownArtifactClass(ValueError):
    """Raised when an artifact record has an unrecognised ``class`` value."""


class InvalidArtifactRecord(ValueError):
    """Raised on required/forbidden key violations OR lifecycle invariant violations.

    Lifecycle invariants:

    - ``managed_profiles ⊆ initial_profiles``
    - ``doctor_required_profiles ⊆ initial_profiles``
    """


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


_REQUIRED_COMMON_KEYS: frozenset[str] = frozenset(
    {"class", "id", "initial_profiles", "managed_profiles", "doctor_required_profiles"}
)

_CLASS_REQUIRED_KEYS: dict[str, frozenset[str]] = {
    "hook": frozenset(_REQUIRED_COMMON_KEYS | {"template_path", "target_path"}),
    "rule": frozenset(_REQUIRED_COMMON_KEYS | {"template_path", "target_path"}),
    "skill": frozenset(_REQUIRED_COMMON_KEYS | {"template_path", "target_path"}),
    "settings-hook-registration": frozenset(_REQUIRED_COMMON_KEYS | {"event", "hook_filename", "target_settings_path"}),
    "gitignore-pattern": frozenset(_REQUIRED_COMMON_KEYS | {"pattern", "comment"}),
    # ownership-glob rows must carry the full ownership triple inline (no defaults).
    "ownership-glob": frozenset(_REQUIRED_COMMON_KEYS | {"path_glob", "priority", "ownership", "upgrade_policy"}),
}

_CLASS_FORBIDDEN_KEYS: dict[str, frozenset[str]] = {
    "hook": frozenset(
        {"profiles", "event", "hook_filename", "target_settings_path", "pattern", "comment", "path_glob", "priority"}
    ),
    "rule": frozenset(
        {"profiles", "event", "hook_filename", "target_settings_path", "pattern", "comment", "path_glob", "priority"}
    ),
    "skill": frozenset(
        {"profiles", "event", "hook_filename", "target_settings_path", "pattern", "comment", "path_glob", "priority"}
    ),
    "settings-hook-registration": frozenset(
        {"profiles", "template_path", "target_path", "pattern", "comment", "path_glob", "priority"}
    ),
    "gitignore-pattern": frozenset(
        {
            "profiles",
            "template_path",
            "target_path",
            "event",
            "hook_filename",
            "target_settings_path",
            "path_glob",
            "priority",
        }
    ),
    "ownership-glob": frozenset(
        {
            "profiles",
            "template_path",
            "target_path",
            "event",
            "hook_filename",
            "target_settings_path",
            "pattern",
            "comment",
        }
    ),
}


def _registry_path() -> Path:
    """Return the filesystem path to the registry TOML."""
    return get_templates_dir() / "managed-artifacts.toml"


def _ownership_glob_path() -> Path:
    """Return the filesystem path to the sibling ownership-glob TOML.

    File may be absent (older GT-KB installs); loader handles absence
    gracefully by returning an empty record list.
    """
    return get_templates_dir() / "scaffold-ownership.toml"


def _coerce_profile_tuple(value: Any, record_id: str, field_name: str) -> tuple[str, ...]:
    """Coerce a TOML profile array into a ``tuple[str, ...]``.

    Raises :class:`InvalidArtifactRecord` on malformed input.
    """
    if not isinstance(value, list):
        raise InvalidArtifactRecord(
            f"record {record_id!r}: {field_name} must be a list of strings, got {type(value).__name__}"
        )
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise InvalidArtifactRecord(
                f"record {record_id!r}: {field_name} item must be str, got {type(item).__name__}"
            )
        result.append(item)
    return tuple(result)


def _validate_schema_keys(record: dict[str, Any], class_: str, record_id: str) -> None:
    """Validate required/forbidden key presence for the record's class."""
    required = _CLASS_REQUIRED_KEYS[class_]
    forbidden = _CLASS_FORBIDDEN_KEYS[class_]
    present = set(record.keys())

    missing = required - present
    if missing:
        raise InvalidArtifactRecord(f"record {record_id!r} (class={class_!r}): missing required keys {sorted(missing)}")

    illegal = forbidden & present
    if illegal:
        raise InvalidArtifactRecord(
            f"record {record_id!r} (class={class_!r}): forbidden keys present {sorted(illegal)}"
        )


def _validate_lifecycle_invariants(
    record_id: str,
    initial: tuple[str, ...],
    managed: tuple[str, ...],
    doctor_required: tuple[str, ...],
) -> None:
    """Enforce ``managed ⊆ initial`` and ``doctor_required ⊆ initial``."""
    initial_set = set(initial)
    managed_extra = set(managed) - initial_set
    if managed_extra:
        raise InvalidArtifactRecord(
            f"record {record_id!r}: managed_profiles {sorted(managed_extra)} "
            f"not a subset of initial_profiles {sorted(initial_set)}"
        )
    doctor_extra = set(doctor_required) - initial_set
    if doctor_extra:
        raise InvalidArtifactRecord(
            f"record {record_id!r}: doctor_required_profiles {sorted(doctor_extra)} "
            f"not a subset of initial_profiles {sorted(initial_set)}"
        )


def _extract_ownership_block(record: dict[str, Any], class_: str) -> OwnershipMeta:
    """Validate + extract ownership metadata for any artifact record (GO C2).

    Called from all four build helpers. Enforces:

    - **C1 all-or-none defaults**: if NONE of the 3 ownership keys
      (``ownership``, ``upgrade_policy``, ``adopter_divergence_policy``) are
      present, class defaults apply. If ANY are present, the block is treated
      as explicitly declared and fully validated.
    - **Enum membership**: all three values must be in the canonical sets.
    - **Divergence invariant**: ``adopter_divergence_policy`` present iff
      ``upgrade_policy ∈ {overwrite, structured-merge, adopter-opt-in}``.

    ``ownership-glob`` rows always require an explicit block (no defaults);
    this is enforced by required-key validation before this function is
    called.
    """
    record_id = record["id"]
    present_keys = _OWNERSHIP_BLOCK_KEYS & record.keys()

    if not present_keys:
        # C1: entire block absent → class defaults apply. ownership-glob
        # never reaches this branch because "ownership" is in its required
        # key set and _validate_schema_keys will have already raised.
        if class_ not in _CLASS_OWNERSHIP_DEFAULTS:
            raise InvalidArtifactRecord(
                f"record {record_id!r} (class={class_!r}): no class default ownership block defined"
            )
        default_ownership, default_upgrade, default_divergence = _CLASS_OWNERSHIP_DEFAULTS[class_]
        return OwnershipMeta(
            ownership=cast(OwnershipEnum, default_ownership),
            upgrade_policy=cast(UpgradePolicyEnum, default_upgrade),
            adopter_divergence_policy=cast(DivergencePolicyEnum, default_divergence),
            workflow_targets=_coerce_workflow_targets(record.get("workflow_targets"), record_id),
        )

    # C1: at least one ownership key is present → validate the whole block.
    ownership_val = record.get("ownership")
    upgrade_policy_val = record.get("upgrade_policy")
    divergence_val = record.get("adopter_divergence_policy")

    if not isinstance(ownership_val, str):
        raise InvalidArtifactRecord(
            f"record {record_id!r}: ownership must be a string (one of "
            f"{sorted(_VALID_OWNERSHIP_VALUES)}); got {type(ownership_val).__name__}"
        )
    if ownership_val not in _VALID_OWNERSHIP_VALUES:
        raise InvalidArtifactRecord(
            f"record {record_id!r}: ownership {ownership_val!r} is not in {sorted(_VALID_OWNERSHIP_VALUES)}"
        )

    if not isinstance(upgrade_policy_val, str):
        raise InvalidArtifactRecord(
            f"record {record_id!r}: upgrade_policy must be a string (one of "
            f"{sorted(_VALID_UPGRADE_POLICIES)}); got {type(upgrade_policy_val).__name__}"
        )
    if upgrade_policy_val not in _VALID_UPGRADE_POLICIES:
        raise InvalidArtifactRecord(
            f"record {record_id!r}: upgrade_policy {upgrade_policy_val!r} is not in {sorted(_VALID_UPGRADE_POLICIES)}"
        )

    divergence_required = upgrade_policy_val in _UPGRADE_POLICIES_REQUIRING_DIVERGENCE
    if divergence_required:
        if divergence_val is None:
            raise InvalidArtifactRecord(
                f"record {record_id!r}: upgrade_policy={upgrade_policy_val!r} requires "
                f"adopter_divergence_policy (one of {sorted(_VALID_DIVERGENCE_POLICIES)})"
            )
        if not isinstance(divergence_val, str):
            raise InvalidArtifactRecord(
                f"record {record_id!r}: adopter_divergence_policy must be a string; got {type(divergence_val).__name__}"
            )
        if divergence_val not in _VALID_DIVERGENCE_POLICIES:
            raise InvalidArtifactRecord(
                f"record {record_id!r}: adopter_divergence_policy {divergence_val!r} "
                f"is not in {sorted(_VALID_DIVERGENCE_POLICIES)}"
            )
    else:
        # preserve / transient — divergence policy must be absent.
        if divergence_val is not None:
            raise InvalidArtifactRecord(
                f"record {record_id!r}: upgrade_policy={upgrade_policy_val!r} forbids "
                f"adopter_divergence_policy (present: {divergence_val!r})"
            )

    return OwnershipMeta(
        ownership=cast(OwnershipEnum, ownership_val),
        upgrade_policy=cast(UpgradePolicyEnum, upgrade_policy_val),
        adopter_divergence_policy=(cast(DivergencePolicyEnum, divergence_val) if divergence_val is not None else None),
        workflow_targets=_coerce_workflow_targets(record.get("workflow_targets"), record_id),
    )


def _coerce_workflow_targets(raw: Any, record_id: str) -> tuple[str, ...]:
    """Coerce optional ``workflow_targets`` list into a tuple of str."""
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise InvalidArtifactRecord(
            f"record {record_id!r}: workflow_targets must be a list of strings; got {type(raw).__name__}"
        )
    result: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise InvalidArtifactRecord(
                f"record {record_id!r}: workflow_targets item must be str; got {type(item).__name__}"
            )
        result.append(item)
    return tuple(result)


def _build_file_artifact(record: dict[str, Any]) -> FileArtifact:
    """Construct a :class:`FileArtifact` from a validated record dict."""
    class_raw = record["class"]
    record_id = record["id"]
    template_path = record["template_path"]
    target_path = record["target_path"]
    if not isinstance(class_raw, str) or class_raw not in _FILE_CLASSES:
        raise UnknownArtifactClass(f"record {record_id!r}: class {class_raw!r} is not a file class")
    if not isinstance(template_path, str):
        raise InvalidArtifactRecord(
            f"record {record_id!r}: template_path must be str, got {type(template_path).__name__}"
        )
    if not isinstance(target_path, str):
        raise InvalidArtifactRecord(f"record {record_id!r}: target_path must be str, got {type(target_path).__name__}")
    initial = _coerce_profile_tuple(record["initial_profiles"], record_id, "initial_profiles")
    managed = _coerce_profile_tuple(record["managed_profiles"], record_id, "managed_profiles")
    doctor_required = _coerce_profile_tuple(record["doctor_required_profiles"], record_id, "doctor_required_profiles")
    _validate_lifecycle_invariants(record_id, initial, managed, doctor_required)
    ownership_meta = _extract_ownership_block(record, class_raw)
    # Narrow class_raw for mypy via cast — schema validation above guarantees the value.
    class_literal = cast(Literal["hook", "rule", "skill"], class_raw)
    return FileArtifact(
        class_=class_literal,
        id=record_id,
        template_path=template_path,
        target_path=target_path,
        initial_profiles=initial,
        managed_profiles=managed,
        doctor_required_profiles=doctor_required,
        ownership=ownership_meta,
    )


def _build_settings_registration(record: dict[str, Any]) -> SettingsHookRegistration:
    """Construct a :class:`SettingsHookRegistration` from a validated record dict."""
    record_id = record["id"]
    event_raw = record["event"]
    hook_filename = record["hook_filename"]
    target_settings_path = record["target_settings_path"]
    if not isinstance(event_raw, str) or event_raw not in _VALID_SETTINGS_EVENTS:
        raise InvalidArtifactRecord(
            f"record {record_id!r}: event {event_raw!r} is not one of {sorted(_VALID_SETTINGS_EVENTS)}"
        )
    if not isinstance(hook_filename, str):
        raise InvalidArtifactRecord(
            f"record {record_id!r}: hook_filename must be str, got {type(hook_filename).__name__}"
        )
    if not isinstance(target_settings_path, str):
        raise InvalidArtifactRecord(
            f"record {record_id!r}: target_settings_path must be str, got {type(target_settings_path).__name__}"
        )
    initial = _coerce_profile_tuple(record["initial_profiles"], record_id, "initial_profiles")
    managed = _coerce_profile_tuple(record["managed_profiles"], record_id, "managed_profiles")
    doctor_required = _coerce_profile_tuple(record["doctor_required_profiles"], record_id, "doctor_required_profiles")
    _validate_lifecycle_invariants(record_id, initial, managed, doctor_required)
    ownership_meta = _extract_ownership_block(record, "settings-hook-registration")
    event_literal = cast(SettingsEvent, event_raw)
    return SettingsHookRegistration(
        class_="settings-hook-registration",
        id=record_id,
        event=event_literal,
        hook_filename=hook_filename,
        target_settings_path=target_settings_path,
        initial_profiles=initial,
        managed_profiles=managed,
        doctor_required_profiles=doctor_required,
        ownership=ownership_meta,
    )


def _build_gitignore_pattern(record: dict[str, Any]) -> GitignorePattern:
    """Construct a :class:`GitignorePattern` from a validated record dict."""
    record_id = record["id"]
    pattern = record["pattern"]
    comment = record["comment"]
    if not isinstance(pattern, str):
        raise InvalidArtifactRecord(f"record {record_id!r}: pattern must be str, got {type(pattern).__name__}")
    if not isinstance(comment, str):
        raise InvalidArtifactRecord(f"record {record_id!r}: comment must be str, got {type(comment).__name__}")
    initial = _coerce_profile_tuple(record["initial_profiles"], record_id, "initial_profiles")
    managed = _coerce_profile_tuple(record["managed_profiles"], record_id, "managed_profiles")
    doctor_required = _coerce_profile_tuple(record["doctor_required_profiles"], record_id, "doctor_required_profiles")
    _validate_lifecycle_invariants(record_id, initial, managed, doctor_required)
    ownership_meta = _extract_ownership_block(record, "gitignore-pattern")
    return GitignorePattern(
        class_="gitignore-pattern",
        id=record_id,
        pattern=pattern,
        comment=comment,
        initial_profiles=initial,
        managed_profiles=managed,
        doctor_required_profiles=doctor_required,
        ownership=ownership_meta,
    )


def _build_ownership_glob(record: dict[str, Any]) -> OwnershipGlobArtifact:
    """Construct an :class:`OwnershipGlobArtifact` from a validated record dict.

    ``ownership-glob`` rows carry their ownership block inline (no defaults);
    :func:`_extract_ownership_block` will validate it as explicitly-declared.
    """
    record_id = record["id"]
    path_glob = record["path_glob"]
    priority_raw = record["priority"]
    notes_raw = record.get("notes", "")

    if not isinstance(path_glob, str):
        raise InvalidArtifactRecord(f"record {record_id!r}: path_glob must be str; got {type(path_glob).__name__}")
    if not isinstance(priority_raw, int) or isinstance(priority_raw, bool):
        # bool is a subclass of int; reject True/False as accidental values.
        raise InvalidArtifactRecord(f"record {record_id!r}: priority must be int; got {type(priority_raw).__name__}")
    if not isinstance(notes_raw, str):
        raise InvalidArtifactRecord(f"record {record_id!r}: notes must be str; got {type(notes_raw).__name__}")

    initial = _coerce_profile_tuple(record["initial_profiles"], record_id, "initial_profiles")
    managed = _coerce_profile_tuple(record["managed_profiles"], record_id, "managed_profiles")
    doctor_required = _coerce_profile_tuple(record["doctor_required_profiles"], record_id, "doctor_required_profiles")
    _validate_lifecycle_invariants(record_id, initial, managed, doctor_required)

    ownership_meta = _extract_ownership_block(record, "ownership-glob")

    return OwnershipGlobArtifact(
        class_="ownership-glob",
        id=record_id,
        path_glob=path_glob,
        priority=priority_raw,
        initial_profiles=initial,
        managed_profiles=managed,
        doctor_required_profiles=doctor_required,
        ownership=ownership_meta,
        notes=notes_raw,
    )


def _parse_record(record: dict[str, Any]) -> ManagedArtifact:
    """Dispatch a raw record dict to the right class constructor."""
    class_raw = record.get("class")
    record_id_raw = record.get("id", "<unknown>")
    if not isinstance(record_id_raw, str):
        raise InvalidArtifactRecord(f"record id must be str, got {type(record_id_raw).__name__}")
    if not isinstance(class_raw, str):
        raise InvalidArtifactRecord(f"record {record_id_raw!r}: class must be str, got {type(class_raw).__name__}")
    if class_raw not in _VALID_ARTIFACT_CLASSES:
        raise UnknownArtifactClass(
            f"record {record_id_raw!r}: unknown class {class_raw!r} (valid: {sorted(_VALID_ARTIFACT_CLASSES)})"
        )
    _validate_schema_keys(record, class_raw, record_id_raw)

    if class_raw in _FILE_CLASSES:
        return _build_file_artifact(record)
    if class_raw == "settings-hook-registration":
        return _build_settings_registration(record)
    if class_raw == "gitignore-pattern":
        return _build_gitignore_pattern(record)
    # Only remaining branch.
    return _build_ownership_glob(record)


# ---------------------------------------------------------------------------
# Public loading helpers
# ---------------------------------------------------------------------------


def _load_raw_artifacts_from(path: Path, source_label: str) -> list[ManagedArtifact]:
    """Parse a single artifact-table TOML file and return its records.

    Returns an empty list if the file is absent. Raises on malformed root.
    """
    if not path.exists():
        return []
    with open(path, "rb") as f:
        data = tomllib.load(f)
    raw_records = data.get("artifacts", [])
    if not isinstance(raw_records, list):
        raise InvalidArtifactRecord(
            f"registry root 'artifacts' in {source_label} must be a list, got {type(raw_records).__name__}"
        )
    results: list[ManagedArtifact] = []
    for raw in raw_records:
        if not isinstance(raw, dict):
            raise InvalidArtifactRecord(
                f"artifacts[] entries in {source_label} must be tables, got {type(raw).__name__}"
            )
        results.append(_parse_record(raw))
    return results


def _load_all_artifacts() -> list[ManagedArtifact]:
    """Parse BOTH artifact TOML files and return every record.

    Sources in order:

    1. ``templates/managed-artifacts.toml`` (the registry, ~40 records)
    2. ``templates/scaffold-ownership.toml`` (sibling ownership map; optional)

    Records are merged into a single list. Cross-file ``id`` uniqueness IS
    enforced here: a collision raises :class:`InvalidArtifactRecord` naming
    the two offending files. Validation of per-record schemas and lifecycle
    invariants is performed inside :func:`_parse_record`.
    """
    registry_path = _registry_path()
    ownership_path = _ownership_glob_path()

    registry_records = _load_raw_artifacts_from(registry_path, source_label="managed-artifacts.toml")
    ownership_records = _load_raw_artifacts_from(ownership_path, source_label="scaffold-ownership.toml")

    # Cross-file ``id`` uniqueness (records within a single file are allowed
    # to collide — the test suite enforces that separately — but a collision
    # across files is surfaced here because the offending file pair is
    # known).
    registry_ids = {r.id for r in registry_records}
    for r in ownership_records:
        if r.id in registry_ids:
            raise InvalidArtifactRecord(
                f"artifact id {r.id!r} is defined in both "
                f"'templates/managed-artifacts.toml' and 'templates/scaffold-ownership.toml'"
            )

    return [*registry_records, *ownership_records]


def load_managed_artifacts(profile: str) -> list[ManagedArtifact]:
    """Return every registry record touching *profile* in any axis.

    A record appears in the result if *profile* is a member of at least one of
    ``initial_profiles``, ``managed_profiles``, or ``doctor_required_profiles``.

    ``ownership-glob`` rows are excluded because they are not lifecycle
    participants for scaffold/upgrade/doctor — they carry ownership metadata
    only. Callers needing every record (including ownership-glob) should use
    :func:`_load_all_artifacts` directly (private) or the
    :class:`~groundtruth_kb.project.ownership.OwnershipResolver` query API.

    This is a broad query helper; filters for a specific lifecycle step should
    use :func:`artifacts_for_scaffold`, :func:`artifacts_for_upgrade`, or
    :func:`artifacts_for_doctor`.
    """
    return [
        a
        for a in _load_all_artifacts()
        if a.class_ != "ownership-glob"
        and (profile in a.initial_profiles or profile in a.managed_profiles or profile in a.doctor_required_profiles)
    ]


def artifacts_for_scaffold(
    profile: str,
    class_: ArtifactClass | None = None,
) -> list[ManagedArtifact]:
    """Return artifacts to be copied by ``scaffold_project`` for *profile*.

    Filters by ``initial_profiles`` membership. Optional ``class_`` argument
    narrows the result to one class. ``ownership-glob`` records are always
    excluded — they carry ownership metadata only and never trigger a file
    copy at scaffold time (sub-bridge ``gtkb-artifact-ownership-matrix-003``).
    """
    return [
        a
        for a in _load_all_artifacts()
        if a.class_ != "ownership-glob" and profile in a.initial_profiles and (class_ is None or a.class_ == class_)
    ]


def artifacts_for_upgrade(
    profile: str,
    class_: ArtifactClass | None = None,
) -> list[ManagedArtifact]:
    """Return artifacts for which ``plan_upgrade`` enforces drift/missing-file repair.

    Filters by ``managed_profiles`` membership. ``ownership-glob`` records
    are always excluded — upgrade policy is derived from the resolved
    :class:`~groundtruth_kb.project.ownership.OwnershipMeta` on registry
    rows, not directly from glob entries.
    """
    return [
        a
        for a in _load_all_artifacts()
        if a.class_ != "ownership-glob" and profile in a.managed_profiles and (class_ is None or a.class_ == class_)
    ]


def artifacts_for_doctor(
    profile: str,
    class_: ArtifactClass | None = None,
) -> list[ManagedArtifact]:
    """Return artifacts enforced by ``run_doctor`` as simple required checks.

    Filters by ``doctor_required_profiles`` membership. ``ownership-glob``
    records are always excluded.
    """
    return [
        a
        for a in _load_all_artifacts()
        if a.class_ != "ownership-glob"
        and profile in a.doctor_required_profiles
        and (class_ is None or a.class_ == class_)
    ]


def find_artifact_by_id(artifact_id: str) -> ManagedArtifact:
    """Return the registry record whose ``id`` matches *artifact_id*.

    Searches across both the registry and the sibling ownership-glob file;
    ``id`` uniqueness is enforced globally at load time.

    Used by ``doctor.py``'s composite checks (scanner-safe-writer) to
    resolve the canonical hook / settings-registration / gitignore-pattern
    triple by ID rather than by hardcoded string, and by
    :class:`~groundtruth_kb.project.ownership.OwnershipResolver` to look up
    ownership-glob records.

    Raises:
        KeyError: if no record has the given id.
    """
    for a in _load_all_artifacts():
        if a.id == artifact_id:
            return a
    raise KeyError(f"no managed artifact with id {artifact_id!r}")
