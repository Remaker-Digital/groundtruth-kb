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

_EVENT_DRIVEN_HOOK_CAPABLE_TYPES = frozenset({"claude", "claude-code", "codex", "codex-cli"})


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


def _project_harness_record(row: dict[str, Any]) -> dict[str, Any]:
    """Project one ``current_harnesses`` row into a flat projection record."""
    record: dict[str, Any] = {field: row.get(field) for field in _PROJECTED_FIELDS}
    for field in _JSON_DECODED_FIELDS:
        record[field] = _decode_json_field(row.get(field))
    harness_type = str(record.get("harness_type") or "").strip().lower()
    record["event_driven_hooks"] = harness_type in _EVENT_DRIVEN_HOOK_CAPABLE_TYPES
    return record


def build_projection(harness_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the projection document from current-version harness rows.

    Pure function: given the rows returned by ``KnowledgeDB.list_harnesses()``
    it returns the projection dict. ``role`` and ``invocation_surfaces`` are
    decoded from JSON text to native types. No derived topology field is stored
    — topology is a derived pure function over the harness set (FR4), never a
    persisted value.
    """
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
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


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
    print(f"harness registry projection written: {written}")
    return 0


if __name__ == "__main__":  # pragma: no cover - module command-line entry
    raise SystemExit(main())
