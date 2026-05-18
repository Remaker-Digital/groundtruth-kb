"""DB-independent reader for the harness registry hot-path projection.

``REQ-HARNESS-REGISTRY-001`` FR5: harness identity and role resolution at
SessionStart must never depend on DB availability. This module is the
hot-path reader counterpart of the ``groundtruth_kb.harness_projection``
generator. It imports ONLY the Python standard library — no ``groundtruth_kb``
import, no DB connection — so it is safe to call at SessionStart before any DB
connection exists, exactly like ``scripts/harness_roles.py``.

A missing, malformed, or unreadable projection file yields a normalized empty
document rather than raising, mirroring
``scripts/harness_roles.py:load_role_assignments``.

Authority: ``REQ-HARNESS-REGISTRY-001`` (FR5); ``DELIB-2079`` Q4.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

HARNESS_REGISTRY_RELATIVE_PATH = Path("harness-state") / "harness-registry.json"

_EMPTY_SOURCE_OF_TRUTH = "MemBase harnesses table (groundtruth.db)"


def harness_registry_path(project_root: Path, override: Path | None = None) -> Path:
    """Resolve the projection file path.

    Resolution order: explicit ``override`` > the ``GTKB_HARNESS_REGISTRY_PATH``
    environment variable > ``<project_root>/harness-state/harness-registry.json``.
    Consistent with ``groundtruth_kb.harness_projection.harness_registry_path``.
    """
    if override is not None:
        return override.expanduser().resolve()
    env_override = os.environ.get("GTKB_HARNESS_REGISTRY_PATH")
    if env_override:
        return Path(env_override).expanduser().resolve()
    return project_root.resolve() / HARNESS_REGISTRY_RELATIVE_PATH


def _empty_document() -> dict[str, Any]:
    """Return a normalized empty projection document."""
    return {
        "schema_version": 1,
        "source_of_truth": _EMPTY_SOURCE_OF_TRUTH,
        "harnesses": [],
    }


def _normalize_document(raw: Any) -> dict[str, Any]:
    """Normalize a parsed projection into a document with a ``harnesses`` list.

    A non-dict payload yields the empty document. A ``harnesses`` value that is
    not a list is replaced with an empty list; non-dict entries within the list
    are dropped.
    """
    if not isinstance(raw, dict):
        return _empty_document()
    document = dict(raw)
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, list):
        document["harnesses"] = []
    else:
        document["harnesses"] = [h for h in harnesses if isinstance(h, dict)]
    return document


def load_harness_projection(
    project_root: Path,
    *,
    projection_path: Path | None = None,
) -> dict[str, Any]:
    """Load the harness registry projection.

    Reads and JSON-parses the projection file. A missing file, a malformed
    file, or an unreadable file yields a normalized empty document — never an
    exception — so a SessionStart caller can resolve a sensible default before
    the projection has been generated.
    """
    path = harness_registry_path(project_root, projection_path)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return _empty_document()
    return _normalize_document(raw)


# --- Keyed accessors (WI-3342 Slice B, IP-1) -------------------------------
#
# ``load_harness_projection`` returns a ``harnesses`` LIST, while the legacy
# JSON readers being migrated (``harness-state/role-assignments.json`` keyed by
# harness id, ``harness-state/harness-identities.json`` keyed by harness name)
# expect dict-shaped lookups. These accessors provide the list-to-keyed
# adaptation once, so each migrating reader queries the projection without
# re-implementing it. All are stdlib-only and fail-soft (never raise).


def _harness_records(document: Any) -> list[dict[str, Any]]:
    """Return the projection's harness records as a list of dicts.

    Tolerant of a non-dict ``document`` or a missing/malformed ``harnesses``
    value (yields an empty list), so callers cannot raise by passing an
    unnormalized payload."""
    if not isinstance(document, dict):
        return []
    harnesses = document.get("harnesses")
    if not isinstance(harnesses, list):
        return []
    return [h for h in harnesses if isinstance(h, dict)]


def _role_set(value: Any) -> set[str]:
    """Normalize a record's ``role`` field into a set of role strings.

    Accepts the canonical list wire form (``["prime-builder"]``) and the
    legacy scalar form (``"prime-builder"``); any other shape yields an empty
    set. Mirrors the READ-side tolerance of
    ``scripts/harness_roles.py::_normalize_role_field``."""
    if isinstance(value, str):
        return {value} if value else set()
    if isinstance(value, list):
        return {r for r in value if isinstance(r, str) and r}
    return set()


def harness_by_id(document: dict[str, Any], harness_id: str) -> dict[str, Any] | None:
    """Return the harness record whose ``id`` equals ``harness_id``.

    ``document`` is a projection document as returned by
    ``load_harness_projection``. Yields ``None`` when no record matches."""
    for record in _harness_records(document):
        if record.get("id") == harness_id:
            return record
    return None


def role_set_for_id(document: dict[str, Any], harness_id: str) -> set[str]:
    """Return the role set recorded for the harness with the given ``id``.

    Yields an empty set when the id is absent or the record carries no
    recognizable ``role`` field — fail-soft, consistent with the module's
    never-raise contract."""
    record = harness_by_id(document, harness_id)
    if record is None:
        return set()
    return _role_set(record.get("role"))


def id_for_name(document: dict[str, Any], harness_name: str) -> str | None:
    """Return the ``id`` of the harness whose ``harness_name`` equals
    ``harness_name``, or ``None`` when no record matches."""
    for record in _harness_records(document):
        if record.get("harness_name") == harness_name:
            value = record.get("id")
            return value if isinstance(value, str) else None
    return None
