"""Harness registry hot-path projection generator.

``REQ-HARNESS-REGISTRY-001`` FR5: a generated flat projection file serves the
SessionStart hot path so harness identity and role resolution never depend on
DB availability, schema currency, or lock contention. This module is the
DB-side generator — it reads the authoritative ``harnesses`` table (via the
``current_harnesses`` view) and writes ``harness-state/harness-registry.json``.

The DB-independent reader counterpart is ``scripts/harness_projection_reader.py``;
that module imports only the Python standard library and is safe to call at
SessionStart before any DB connection exists.

Per FR4, harness topology (single- vs multi-harness) is a derived pure function
over the harness set and is never persisted; the projection stores only the
raw harness records.

Authority: ``REQ-HARNESS-REGISTRY-001`` (FR5, FR1, FR4); ``DELIB-2079`` Q4
(DB-authoritative table plus a generated flat projection for the hot path).

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECTION_SCHEMA_VERSION = 1

HARNESS_REGISTRY_RELATIVE_PATH = Path("harness-state") / "harness-registry.json"
HARNESS_IDENTITIES_RELATIVE_PATH = Path("harness-state") / "harness-identities.json"
HARNESS_CAPABILITIES_RELATIVE_PATH = Path("config") / "agent-control" / "harness-capability-registry.toml"


class HarnessStateError(Exception):
    """Raised when a harness-state SoT file is missing or malformed.

    Per the WI-4327 canonical reader-entrypoint contract
    (``DCL-HARNESS-STATE-SOT-READER-CONTRACT-001``): all reads of the 3
    harness-state SoT surfaces (roles via ``harness-registry.json``;
    identities via ``harness-identities.json``; capabilities via
    ``harness-capability-registry.toml``) MUST go through the canonical
    entrypoint functions in this module. Direct file reads in committed
    code outside ``groundtruth_kb.harness_projection`` are doctor findings.

    The exception subclasses :class:`Exception` so callers can distinguish
    SoT contract failures from generic ``OSError`` / ``json.JSONDecodeError``
    while still allowing a broad ``except Exception:`` to swallow them at
    fail-soft boundaries (e.g. SessionStart).
    """


_PROJECTION_SOURCE_OF_TRUTH = "MemBase harnesses table (groundtruth.db)"
_PROJECTION_DESCRIPTION = (
    "Generated hot-path projection of the MemBase harnesses registry table "
    "(REQ-HARNESS-REGISTRY-001 FR5). SessionStart harness identity and role "
    "resolution reads this flat file so it never depends on DB availability. "
    "Do not hand-edit; regenerate from the harnesses table via "
    "groundtruth_kb.harness_projection."
)

# Harness-record fields carried verbatim into the projection.
_PROJECTED_FIELDS = (
    "id",
    "version",
    "harness_name",
    "harness_type",
    "status",
    "reviewer_precedence",
    "capabilities_ref",
)
# Fields stored as JSON text in the DB, decoded to native objects here.
_JSON_DECODED_FIELDS = ("role", "invocation_surfaces")

# --- Capability axes (FAB-01 / HYG-004) ----------------------------------
#
# The single ``event_driven_hooks`` flag historically conflated two distinct
# capabilities, and once every registered harness type was added to its capable
# set the flag became always-true — it encoded "is a valid dispatch target",
# not "can fire bridge dispatch hooks". That conflation masked the dispatch
# deadlock at the eligibility check (a hook-less harness was a valid dispatch
# TARGET but could never fire the event that drives a counterpart spawn).
#
# The two axes are now derived separately:
#
# - ``can_fire_events``: retained compatibility field for historical
#   event-firing hook surfaces. The dispatcher daemon is now the only live
#   dispatch event source, so current projections neutralize this axis even
#   when legacy registry metadata says otherwise.
# - ``can_receive_dispatch``: the harness can be spawned headless as a dispatch
#   target. All registered launchable harness types qualify.
#
# ``event_driven_hooks`` is retained as a DEPRECATED back-compat alias for the
# neutralized event-source axis. New code MUST read ``can_fire_events`` /
# ``can_receive_dispatch``.
_EVENT_FIRING_CAPABLE_TYPES: frozenset[str] = frozenset()

_DISPATCH_RECEIVE_CAPABLE_TYPES = frozenset(
    {"claude", "claude-code", "codex", "codex-cli", "cursor", "ollama", "openrouter", "antigravity"}
)
_PROVIDER_HARNESS_TYPES = frozenset({"ollama", "openrouter"})

# Deprecated alias preserved for back-compat readers; equals the neutralized
# event-source axis.
_EVENT_DRIVEN_HOOK_CAPABLE_TYPES = _EVENT_FIRING_CAPABLE_TYPES


def _now_iso() -> str:
    """UTC ISO-8601 timestamp with a ``Z`` suffix (harness-state convention)."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _decode_json_field(raw: Any) -> Any:
    """Decode a JSON-text column value into a native object.

    The ``harnesses`` table stores ``role`` and ``invocation_surfaces`` as JSON
    text. A NULL column or empty string projects as ``None``. An already-decoded
    (non-string) value is returned unchanged; malformed JSON is returned as-is
    so the generator never raises on a single bad row.
    """
    if raw is None or raw == "":
        return None
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw


def _bool_or_none(value: Any) -> bool | None:
    """Normalize an explicit boolean-ish metadata value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return None


def _float_or_none(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (list, tuple, set, frozenset)):
        return []
    return sorted({str(item).strip() for item in value if str(item).strip()})


def _without_event_source_tag(tags: list[str]) -> list[str]:
    return sorted({tag for tag in tags if tag != "event-source"})


def _neutralize_event_source_metadata(surfaces: Any) -> Any:
    if not isinstance(surfaces, dict):
        return surfaces
    neutralized = {key: dict(value) if isinstance(value, dict) else value for key, value in surfaces.items()}

    for source in (neutralized, *(value for value in neutralized.values() if isinstance(value, dict))):
        for key in ("can_fire_events", "fire_events", "event_source", "event_driven_hooks"):
            if key in source:
                source[key] = False
        for key in ("dispatch_tags", "tags"):
            tags = _string_list(source.get(key))
            if tags:
                source[key] = _without_event_source_tag(tags)

    return neutralized


def _dispatch_metadata(record: dict[str, Any]) -> dict[str, Any]:
    """Extract explicit dispatch capability metadata from invocation surfaces.

    ``harnesses`` has no dedicated dispatchability columns, and this bridge
    slice deliberately avoids a schema migration. The append-only registry can
    still carry explicit metadata inside the existing ``invocation_surfaces``
    JSON field. Supported shapes are intentionally tolerant:

    - top-level ``can_fire_events`` / ``can_receive_dispatch``;
    - ``dispatch`` or ``dispatchability`` subtable with those keys;
    - ``headless.can_receive_dispatch`` for target-only overrides.
    """

    surfaces = record.get("invocation_surfaces")
    if not isinstance(surfaces, dict):
        return {}
    sources = [surfaces]
    for key in ("dispatch", "dispatchability"):
        value = surfaces.get(key)
        if isinstance(value, dict):
            sources.append(value)
    headless = surfaces.get("headless")
    if isinstance(headless, dict):
        sources.append(headless)

    aliases = {
        "can_fire_events": ("can_fire_events", "fire_events", "event_source"),
        "can_receive_dispatch": ("can_receive_dispatch", "receive_dispatch", "dispatch_target"),
        "event_driven_hooks": ("event_driven_hooks",),
    }
    result: dict[str, Any] = {}
    for canonical, names in aliases.items():
        for source in sources:
            for name in names:
                parsed = _bool_or_none(source.get(name))
                if parsed is not None:
                    result[canonical] = parsed
                    break
            if canonical in result:
                break
    numeric_aliases = {
        "dispatch_quality": ("dispatch_quality", "quality"),
        "dispatch_cost": ("dispatch_cost", "cost"),
        "dispatch_availability": ("dispatch_availability", "availability"),
    }
    for canonical, names in numeric_aliases.items():
        for source in sources:
            for name in names:
                parsed_float = _float_or_none(source.get(name))
                if parsed_float is not None:
                    result[canonical] = parsed_float
                    break
            if canonical in result:
                break
    for source in sources:
        parsed_int = _int_or_none(source.get("dispatch_max_items", source.get("max_items")))
        if parsed_int is not None:
            result["dispatch_max_items"] = parsed_int
            break
    for source in sources:
        tags = _string_list(source.get("dispatch_tags", source.get("tags")))
        if tags:
            result["dispatch_tags"] = tags
            break
    return result


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _envelope_metadata(record: dict[str, Any]) -> dict[str, Any]:
    """Extract activity/result/session envelope metadata from invocation surfaces."""
    surfaces = record.get("invocation_surfaces")
    if not isinstance(surfaces, dict):
        return {}
    sources = [surfaces]
    for key in ("activity_envelope", "result_envelope", "session_envelope", "envelope_projection"):
        value = surfaces.get(key)
        if isinstance(value, dict):
            sources.append(value)

    aliases = {
        "activity_envelope_projection_mode": (
            "activity_envelope_projection_mode",
            "activity_projection_mode",
            "activity_envelope_mode",
        ),
        "compact_result_envelope_mode": (
            "compact_result_envelope_mode",
            "result_envelope_mode",
            "result_envelope",
        ),
        "compact_session_envelope_mode": (
            "compact_session_envelope_mode",
            "session_envelope_mode",
            "session_envelope",
        ),
    }
    result: dict[str, Any] = {}
    for canonical, names in aliases.items():
        for source in sources:
            for name in names:
                parsed = _string_or_none(source.get(name))
                if parsed is not None:
                    result[canonical] = parsed
                    break
            if canonical in result:
                break
    for source in sources:
        parsed_bool = _bool_or_none(source.get("full_transcript_archive_required"))
        if parsed_bool is not None:
            result["full_transcript_archive_required"] = parsed_bool
            break
    return result


def _project_harness_record(row: dict[str, Any], dispatch_config: Any | None = None) -> dict[str, Any]:
    """Project one ``current_harnesses`` row into a flat projection record."""
    record: dict[str, Any] = {field: row.get(field) for field in _PROJECTED_FIELDS}
    for field in _JSON_DECODED_FIELDS:
        record[field] = _decode_json_field(row.get(field))
    record["invocation_surfaces"] = _neutralize_event_source_metadata(record.get("invocation_surfaces"))
    harness_type = str(record.get("harness_type") or "").strip().lower()
    explicit = _dispatch_metadata(record)
    # Honest split axes (FAB-01 / HYG-004). Event firing is schema-retained
    # but daemon-owned after WI-5020, so legacy explicit metadata is ignored.
    record["can_fire_events"] = False
    record["can_receive_dispatch"] = explicit.get(
        "can_receive_dispatch",
        harness_type in _DISPATCH_RECEIVE_CAPABLE_TYPES,
    )
    # Deprecated back-compat alias for the neutralized event-source capability.
    record["event_driven_hooks"] = False
    for field in ("dispatch_quality", "dispatch_cost", "dispatch_availability", "dispatch_max_items"):
        if field in explicit:
            record[field] = explicit[field]
    tags = explicit.get("dispatch_tags")
    filtered_tags = _without_event_source_tag(tags) if isinstance(tags, list) else []
    if filtered_tags:
        record["dispatch_tags"] = filtered_tags
    else:
        derived_tags = _string_list(record.get("role"))
        if record["can_fire_events"]:
            derived_tags.append("event-source")
        if harness_type in _PROVIDER_HARNESS_TYPES:
            derived_tags.append("low-cost")
        record["dispatch_tags"] = sorted(set(derived_tags))
    envelope = _envelope_metadata(record)
    provider_harness = harness_type in _PROVIDER_HARNESS_TYPES
    default_mode = "compact-provider" if provider_harness else "native"
    record["activity_envelope_projection_mode"] = envelope.get("activity_envelope_projection_mode", default_mode)
    record["compact_result_envelope_mode"] = envelope.get("compact_result_envelope_mode", default_mode)
    record["compact_session_envelope_mode"] = envelope.get("compact_session_envelope_mode", default_mode)
    record["full_transcript_archive_required"] = envelope.get("full_transcript_archive_required", False)
    _ = dispatch_config  # Back-compat parameter; WI-5012 forbids config-derived dispatch authority.
    return record


def build_projection(harness_rows: list[dict[str, Any]], *, dispatch_config: Any | None = None) -> dict[str, Any]:
    """Build the projection document from current-version harness rows.

    Pure function: given the rows returned by ``KnowledgeDB.list_harnesses()``
    it returns the projection dict. ``role`` and ``invocation_surfaces`` are
    decoded from JSON text to native types. No derived topology field is stored
    — topology is a derived pure function over the harness set (FR4), never a
    persisted value.
    """
    _ = dispatch_config  # Back-compat parameter; projection authority is MemBase-only after WI-5012.
    records = [_project_harness_record(row) for row in harness_rows]
    records.sort(key=lambda r: str(r.get("id") or ""))
    return {
        "schema_version": PROJECTION_SCHEMA_VERSION,
        "source_of_truth": _PROJECTION_SOURCE_OF_TRUTH,
        "description": _PROJECTION_DESCRIPTION,
        "generated_at": _now_iso(),
        "harnesses": records,
    }


def harness_registry_path(project_root: Path, override: Path | None = None) -> Path:
    """Resolve the projection file path.

    Resolution order: explicit ``override`` > the ``GTKB_HARNESS_REGISTRY_PATH``
    environment variable > ``<project_root>/harness-state/harness-registry.json``.
    Mirrors ``scripts/harness_roles.py:role_assignments_path``.
    """
    if override is not None:
        return override.expanduser().resolve()
    env_override = os.environ.get("GTKB_HARNESS_REGISTRY_PATH")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return project_root.resolve() / HARNESS_REGISTRY_RELATIVE_PATH


def _write_projection(path: Path, document: dict[str, Any]) -> Path:
    """Atomically write the projection document as JSON.

    Uses the temp-file + ``os.replace`` pattern with ``sort_keys=True`` so the
    generated file diffs cleanly in git, matching
    ``scripts/harness_roles.py:write_role_assignments``.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if _projection_matches_existing_except_generated_at(path, document):
        return path
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def _projection_matches_existing_except_generated_at(path: Path, document: dict[str, Any]) -> bool:
    """True when writing would only advance the projection timestamp."""
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return False
    if not isinstance(existing, dict):
        return False
    existing_without_timestamp = dict(existing)
    document_without_timestamp = dict(document)
    existing_without_timestamp.pop("generated_at", None)
    document_without_timestamp.pop("generated_at", None)
    return existing_without_timestamp == document_without_timestamp


def generate_harness_projection(
    db: Any,
    project_root: Path,
    *,
    projection_path: Path | None = None,
) -> Path:
    """Regenerate the harness registry projection file from the DB.

    Reads the current-version harness rows via ``db.list_harnesses()``, builds
    the projection document, and atomically writes it to the resolved path.
    ``db`` only needs to expose ``list_harnesses()`` (it is duck-typed so this
    function does not force a ``groundtruth_kb.db`` import). Returns the written
    path.
    """
    document = build_projection(db.list_harnesses())
    path = harness_registry_path(project_root, projection_path)
    return _write_projection(path, document)


def _resolve_project_root(project_root: Path | None) -> Path:
    """Resolve project_root for the canonical reader entrypoints.

    Order: explicit argument > ``GTKB_PROJECT_ROOT`` env var > current
    working directory's resolved absolute path. Mirrors the resolution
    pattern used by sibling generator surfaces.
    """
    if project_root is not None:
        return project_root.expanduser().resolve()
    env_root = os.environ.get("GTKB_PROJECT_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path.cwd().resolve()


def read_roles(project_root: Path | None = None) -> dict[str, Any]:
    """Read the harness roles SoT (``harness-state/harness-registry.json``).

    This is the canonical reader entrypoint for harness roles per
    ``DCL-HARNESS-STATE-SOT-READER-CONTRACT-001``. Direct ``json.load`` /
    ``json.loads`` reads of the registry file in committed code outside
    this module are doctor findings.

    Raises :class:`HarnessStateError` when the SoT file is missing,
    unreadable, malformed JSON, or non-mapping at the top level.
    """
    root = _resolve_project_root(project_root)
    path = harness_registry_path(root)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise HarnessStateError(f"harness-state SoT file missing: {path}") from exc
    except OSError as exc:
        raise HarnessStateError(f"harness-state SoT file unreadable ({path}): {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HarnessStateError(f"harness-state SoT file malformed JSON ({path}): {exc}") from exc
    if not isinstance(data, dict):
        raise HarnessStateError(
            f"harness-state SoT file expected a JSON object at top level ({path}); got {type(data).__name__}"
        )
    return data


def read_identity(project_root: Path | None = None) -> dict[str, Any]:
    """Read the harness identities SoT (``harness-state/harness-identities.json``).

    Canonical reader entrypoint per
    ``DCL-HARNESS-STATE-SOT-READER-CONTRACT-001``. Direct file reads
    of the identities file in committed code outside this module are
    doctor findings.

    Raises :class:`HarnessStateError` when the SoT file is missing,
    unreadable, malformed JSON, or non-mapping at the top level.
    """
    root = _resolve_project_root(project_root)
    path = root / HARNESS_IDENTITIES_RELATIVE_PATH
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise HarnessStateError(f"harness-state SoT file missing: {path}") from exc
    except OSError as exc:
        raise HarnessStateError(f"harness-state SoT file unreadable ({path}): {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise HarnessStateError(f"harness-state SoT file malformed JSON ({path}): {exc}") from exc
    if not isinstance(data, dict):
        raise HarnessStateError(
            f"harness-state SoT file expected a JSON object at top level ({path}); got {type(data).__name__}"
        )
    return data


def read_capabilities(project_root: Path | None = None) -> dict[str, Any]:
    """Read the harness capabilities SoT (``config/agent-control/harness-capability-registry.toml``).

    Canonical reader entrypoint per
    ``DCL-HARNESS-STATE-SOT-READER-CONTRACT-001``. Direct TOML reads
    of the capability registry in committed code outside this module
    are doctor findings.

    Raises :class:`HarnessStateError` when the SoT file is missing,
    unreadable, malformed TOML, or non-mapping at the top level.
    """
    try:
        import tomllib  # Python 3.11+ standard library
    except ImportError as exc:  # pragma: no cover - <3.11 unsupported
        raise HarnessStateError(f"tomllib unavailable on this Python build: {exc}") from exc

    root = _resolve_project_root(project_root)
    path = root / HARNESS_CAPABILITIES_RELATIVE_PATH
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except FileNotFoundError as exc:
        raise HarnessStateError(f"harness-state SoT file missing: {path}") from exc
    except OSError as exc:
        raise HarnessStateError(f"harness-state SoT file unreadable ({path}): {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise HarnessStateError(f"harness-state SoT file malformed TOML ({path}): {exc}") from exc
    if not isinstance(data, dict):
        raise HarnessStateError(
            f"harness-state SoT file expected a TOML table at top level ({path}); got {type(data).__name__}"
        )
    return data


def main() -> int:
    """Regenerate the projection from the configured DB. Returns an exit code.

    The DB path and project root are resolved through the package config
    (``GTConfig.load()`` — ``groundtruth.toml`` + ``GT_*`` env vars + defaults),
    so the generator honours a non-default configuration rather than a literal
    path.
    """
    from groundtruth_kb.config import GTConfig
    from groundtruth_kb.db import KnowledgeDB

    config = GTConfig.load()
    db = KnowledgeDB(db_path=config.db_path)
    written = generate_harness_projection(db, config.project_root)
    print(f"harness registry projection written: {written}")  # print-ok
    return 0


if __name__ == "__main__":  # pragma: no cover - module command-line entry
    raise SystemExit(main())
