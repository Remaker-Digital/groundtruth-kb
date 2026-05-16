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
