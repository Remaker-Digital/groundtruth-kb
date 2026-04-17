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
]

SettingsEvent = Literal[
    "SessionStart",
    "UserPromptSubmit",
    "PostToolUse",
    "PreToolUse",
]

_VALID_ARTIFACT_CLASSES: frozenset[str] = frozenset(
    {
        "hook",
        "rule",
        "skill",
        "settings-hook-registration",
        "gitignore-pattern",
    }
)

_VALID_SETTINGS_EVENTS: frozenset[str] = frozenset({"SessionStart", "UserPromptSubmit", "PostToolUse", "PreToolUse"})

_FILE_CLASSES: frozenset[str] = frozenset({"hook", "rule", "skill"})


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


ManagedArtifact = FileArtifact | SettingsHookRegistration | GitignorePattern


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
}

_CLASS_FORBIDDEN_KEYS: dict[str, frozenset[str]] = {
    "hook": frozenset({"profiles", "event", "hook_filename", "target_settings_path", "pattern", "comment"}),
    "rule": frozenset({"profiles", "event", "hook_filename", "target_settings_path", "pattern", "comment"}),
    "skill": frozenset({"profiles", "event", "hook_filename", "target_settings_path", "pattern", "comment"}),
    "settings-hook-registration": frozenset({"profiles", "template_path", "target_path", "pattern", "comment"}),
    "gitignore-pattern": frozenset(
        {"profiles", "template_path", "target_path", "event", "hook_filename", "target_settings_path"}
    ),
}


def _registry_path() -> Path:
    """Return the filesystem path to the registry TOML."""
    return get_templates_dir() / "managed-artifacts.toml"


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
    return GitignorePattern(
        class_="gitignore-pattern",
        id=record_id,
        pattern=pattern,
        comment=comment,
        initial_profiles=initial,
        managed_profiles=managed,
        doctor_required_profiles=doctor_required,
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
    # Only remaining branch.
    return _build_gitignore_pattern(record)


# ---------------------------------------------------------------------------
# Public loading helpers
# ---------------------------------------------------------------------------


def _load_all_artifacts() -> list[ManagedArtifact]:
    """Parse the TOML registry and return every record.

    No profile filter; no ID uniqueness check at this layer — that is enforced by
    dedicated tests (see ``tests/test_managed_registry.py``). Validation of
    per-record schemas and lifecycle invariants IS performed here so that the
    loader itself is the point at which ``InvalidArtifactRecord`` is raised.
    """
    path = _registry_path()
    with open(path, "rb") as f:
        data = tomllib.load(f)

    raw_records = data.get("artifacts", [])
    if not isinstance(raw_records, list):
        raise InvalidArtifactRecord(f"registry root 'artifacts' must be a list, got {type(raw_records).__name__}")

    results: list[ManagedArtifact] = []
    for raw in raw_records:
        if not isinstance(raw, dict):
            raise InvalidArtifactRecord(f"artifacts[] entries must be tables, got {type(raw).__name__}")
        results.append(_parse_record(raw))
    return results


def load_managed_artifacts(profile: str) -> list[ManagedArtifact]:
    """Return every registry record touching *profile* in any axis.

    A record appears in the result if *profile* is a member of at least one of
    ``initial_profiles``, ``managed_profiles``, or ``doctor_required_profiles``.

    This is a broad query helper; filters for a specific lifecycle step should
    use :func:`artifacts_for_scaffold`, :func:`artifacts_for_upgrade`, or
    :func:`artifacts_for_doctor`.
    """
    return [
        a
        for a in _load_all_artifacts()
        if profile in a.initial_profiles or profile in a.managed_profiles or profile in a.doctor_required_profiles
    ]


def artifacts_for_scaffold(
    profile: str,
    class_: ArtifactClass | None = None,
) -> list[ManagedArtifact]:
    """Return artifacts to be copied by ``scaffold_project`` for *profile*.

    Filters by ``initial_profiles`` membership. Optional ``class_`` argument
    narrows the result to one class.
    """
    return [
        a for a in _load_all_artifacts() if profile in a.initial_profiles and (class_ is None or a.class_ == class_)
    ]


def artifacts_for_upgrade(
    profile: str,
    class_: ArtifactClass | None = None,
) -> list[ManagedArtifact]:
    """Return artifacts for which ``plan_upgrade`` enforces drift/missing-file repair.

    Filters by ``managed_profiles`` membership.
    """
    return [
        a for a in _load_all_artifacts() if profile in a.managed_profiles and (class_ is None or a.class_ == class_)
    ]


def artifacts_for_doctor(
    profile: str,
    class_: ArtifactClass | None = None,
) -> list[ManagedArtifact]:
    """Return artifacts enforced by ``run_doctor`` as simple required checks.

    Filters by ``doctor_required_profiles`` membership.
    """
    return [
        a
        for a in _load_all_artifacts()
        if profile in a.doctor_required_profiles and (class_ is None or a.class_ == class_)
    ]


def find_artifact_by_id(artifact_id: str) -> ManagedArtifact:
    """Return the registry record whose ``id`` matches *artifact_id*.

    Used by ``doctor.py``'s composite checks (scanner-safe-writer) to
    resolve the canonical hook / settings-registration / gitignore-pattern
    triple by ID rather than by hardcoded string.

    Raises:
        KeyError: if no record has the given id.
    """
    for a in _load_all_artifacts():
        if a.id == artifact_id:
            return a
    raise KeyError(f"no managed artifact with id {artifact_id!r}")
