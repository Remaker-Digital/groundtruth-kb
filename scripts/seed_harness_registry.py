"""Seed the harnesses registry table from the harness-registry projection.

WI-3342 Slice A. Per the owner's 2026-05-16 decision ("Seed the harnesses
table first"), this migration imports the live AI coding harnesses into the
DB-backed ``harnesses`` registry table (``REQ-HARNESS-REGISTRY-001`` FR1) from
the tracked ``harness-state/harness-registry.json`` hot-path projection, then
regenerates that FR5 projection from the DB.

The migration is idempotent: a harness id already present in the table is
skipped, so a re-run is a no-op. Fresh-install seeding preserves each
projection record's status rather than coercing every harness to ``active``.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
Licensed under AGPL-3.0-or-later.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Make the in-repo groundtruth_kb package importable regardless of which
# interpreter runs this migration (a system python or a project venv).
_REPO_ROOT = Path(__file__).resolve().parent.parent
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if _PACKAGE_SRC.is_dir() and str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

_HARNESS_STATE_DIR = "harness-state"
_HARNESS_REGISTRY_FILE = "harness-registry.json"

DEFAULT_SEED_STATUS = "registered"
SEED_CHANGED_BY = "harness-registry-seed"
SEED_CHANGE_REASON = "Seed harness registry from tracked harness-registry projection per WI-4214 Slice 1 seed repoint."


def _load_json_object(path: Path) -> dict[str, Any]:
    """Load a JSON object from ``path``; raise with a clear seed-source error."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"required harness registry projection not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"required harness registry projection is invalid JSON: {path}") from exc
    except OSError as exc:
        raise OSError(f"required harness registry projection is unreadable: {path}: {exc}") from exc
    return data if isinstance(data, dict) else {}


def _normalize_role(raw: Any) -> list[str]:
    """Normalize a role field (list or scalar) into a list of tokens."""
    if isinstance(raw, list):
        return [str(token).strip() for token in raw if str(token).strip()]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def read_projected_harnesses(project_root: Path) -> list[dict[str, Any]]:
    """Read harness descriptors from ``harness-state/harness-registry.json``.

    Returns one descriptor per projected harness, ordered by harness id for
    deterministic seeding. Missing ``status`` values default to ``registered``
    so incomplete records fail closed instead of becoming dispatch-active.
    """
    state_dir = project_root / _HARNESS_STATE_DIR
    projection = _load_json_object(state_dir / _HARNESS_REGISTRY_FILE)
    records = projection.get("harnesses", [])
    descriptors: list[dict[str, Any]] = []
    if isinstance(records, list):
        for record in records:
            if not isinstance(record, dict):
                continue
            hid = str(record.get("id") or "").strip()
            if not hid:
                continue
            harness_type = str(record.get("harness_type") or hid).strip() or hid
            harness_name = str(record.get("harness_name") or harness_type or hid).strip()
            resolved_type = harness_type or harness_name
            raw_invocation_surfaces = record.get("invocation_surfaces")
            invocation_surfaces = raw_invocation_surfaces if isinstance(raw_invocation_surfaces, dict) else None
            descriptors.append(
                {
                    "id": hid,
                    "harness_name": harness_name,
                    "harness_type": resolved_type,
                    "role": _normalize_role(record.get("role")),
                    "status": str(record.get("status") or DEFAULT_SEED_STATUS).strip() or DEFAULT_SEED_STATUS,
                    "reviewer_precedence": record.get("reviewer_precedence"),
                    "invocation_surfaces": invocation_surfaces,
                    "capabilities_ref": record.get("capabilities_ref"),
                }
            )
    return sorted(descriptors, key=lambda descriptor: descriptor["id"])


def seed_harness_registry(
    db: Any,
    project_root: Path,
    *,
    changed_by: str = SEED_CHANGED_BY,
) -> dict[str, Any]:
    """Seed the ``harnesses`` table from the tracked harness-registry projection.

    For each legacy harness not already present in the table, appends a row at
    the projection's recorded status carrying its id, name, type, role-set, and
    invocation surfaces. Idempotent: a harness id already present is skipped.
    After any inserts the FR5 projection is regenerated. Returns a summary dict
    with the seeded ids, skipped ids, and projection path.
    """
    from groundtruth_kb.harness_projection import generate_harness_projection

    seeded: list[str] = []
    skipped: list[str] = []
    for descriptor in read_projected_harnesses(project_root):
        harness_id = descriptor["id"]
        if db.get_harness(harness_id) is not None:
            skipped.append(harness_id)
            continue
        db.insert_harness(
            id=harness_id,
            harness_name=descriptor["harness_name"],
            harness_type=descriptor["harness_type"],
            role=descriptor["role"],
            changed_by=changed_by,
            change_reason=SEED_CHANGE_REASON,
            status=descriptor["status"],
            reviewer_precedence=descriptor.get("reviewer_precedence"),
            invocation_surfaces=descriptor.get("invocation_surfaces"),
            capabilities_ref=descriptor.get("capabilities_ref"),
        )
        seeded.append(harness_id)
    projection_path = generate_harness_projection(db, project_root)
    return {
        "seeded": sorted(seeded),
        "skipped": sorted(skipped),
        "projection_path": str(projection_path),
    }


def main() -> int:
    """Run the seed migration against the configured MemBase; return an exit code."""
    from groundtruth_kb.config import GTConfig
    from groundtruth_kb.db import KnowledgeDB

    config = GTConfig.load()
    db = KnowledgeDB(db_path=config.db_path)
    summary = seed_harness_registry(db, config.project_root)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - module command-line entry
    raise SystemExit(main())
