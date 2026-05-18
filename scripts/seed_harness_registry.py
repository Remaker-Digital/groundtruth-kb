"""Seed the harnesses registry table from the legacy harness-state JSON.

WI-3342 Slice A. Per the owner's 2026-05-16 decision ("Seed the harnesses
table first"), this migration imports the live AI coding harnesses into the
DB-backed ``harnesses`` registry table (``REQ-HARNESS-REGISTRY-001`` FR1) from
``harness-state/harness-identities.json`` and
``harness-state/role-assignments.json``, then regenerates the FR5 hot-path
projection.

The harnesses are seeded at ``status = active`` -- they are already-live,
in-service harnesses being imported, not newly registered ones; the FR2
lifecycle FSM governs future transitions from the seeded state. The migration
is idempotent: a harness id already present in the table is skipped, so a
re-run is a no-op.

This slice populates the table; it does NOT make the table the authoritative
role/identity substrate. ``harness-state/role-assignments.json`` and
``harness-state/harness-identities.json`` remain authoritative until the
WI-3342 Slice B reader migration.

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
_IDENTITIES_FILE = "harness-identities.json"
_ROLE_ASSIGNMENTS_FILE = "role-assignments.json"

SEED_STATUS = "active"
SEED_CHANGED_BY = "harness-registry-seed"
SEED_CHANGE_REASON = (
    "Seed harness registry from legacy harness-state JSON per owner decision "
    "2026-05-16 (WI-3342 Slice A)."
)

# WI-3344 IP-3: a fresh install must seed invocation_surfaces so the
# registry-driven cross-harness trigger can dispatch the seeded harnesses
# without any code-side fallback. Keyed by resolved harness type; the headless
# argv template uses the {{PROMPT}} / {{PROJECT_ROOT}} placeholder tokens that
# cross_harness_bridge_trigger._harness_command substitutes as individual argv
# elements. Unknown harness types seed with no invocation_surfaces.
_SEED_INVOCATION_SURFACES: dict[str, dict[str, Any]] = {
    "codex": {"headless": {"argv": ["codex", "exec", "{{PROMPT}}", "--cd", "{{PROJECT_ROOT}}"]}},
    "claude": {
        "headless": {
            "argv": ["claude", "-p", "{{PROMPT}}", "--add-dir", "{{PROJECT_ROOT}}", "--output-format", "json"]
        }
    },
}


def _load_json_object(path: Path) -> dict[str, Any]:
    """Load a JSON object from ``path``; return an empty dict on any failure."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _normalize_role(raw: Any) -> list[str]:
    """Normalize a legacy role field (list or scalar) into a list of tokens."""
    if isinstance(raw, list):
        return [str(token).strip() for token in raw if str(token).strip()]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def read_legacy_harnesses(project_root: Path) -> list[dict[str, Any]]:
    """Join the legacy identity and role-assignment JSON into harness descriptors.

    Returns one descriptor per harness id in ``role-assignments.json``, each
    carrying ``id``, ``harness_name``, ``harness_type``, and ``role``. The
    descriptors are ordered by harness id for deterministic seeding.
    """
    state_dir = project_root / _HARNESS_STATE_DIR
    identities = _load_json_object(state_dir / _IDENTITIES_FILE).get("harnesses", {})
    role_map = _load_json_object(state_dir / _ROLE_ASSIGNMENTS_FILE).get("harnesses", {})

    id_to_name: dict[str, str] = {}
    if isinstance(identities, dict):
        for name, record in identities.items():
            if isinstance(record, dict):
                harness_id = str(record.get("id") or "").strip()
                if harness_id:
                    id_to_name[harness_id] = str(name)

    descriptors: list[dict[str, Any]] = []
    if isinstance(role_map, dict):
        for raw_id, record in sorted(role_map.items()):
            if not isinstance(record, dict):
                continue
            hid = str(raw_id).strip()
            if not hid:
                continue
            harness_type = str(record.get("harness_type") or "").strip()
            harness_name = id_to_name.get(hid) or harness_type or hid
            resolved_type = harness_type or harness_name
            descriptors.append(
                {
                    "id": hid,
                    "harness_name": harness_name,
                    "harness_type": resolved_type,
                    "role": _normalize_role(record.get("role")),
                    "invocation_surfaces": _SEED_INVOCATION_SURFACES.get(resolved_type.strip().lower()),
                }
            )
    return descriptors


def seed_harness_registry(
    db: Any,
    project_root: Path,
    *,
    changed_by: str = SEED_CHANGED_BY,
) -> dict[str, Any]:
    """Seed the ``harnesses`` table from the legacy harness-state JSON.

    For each legacy harness not already present in the table, appends a row at
    ``status = active`` carrying its id, name, type, and role-set. Idempotent:
    a harness id already present is skipped. After any inserts the FR5
    projection is regenerated. Returns a summary dict with the seeded ids, the
    skipped ids, and the projection path.
    """
    from groundtruth_kb.harness_projection import generate_harness_projection

    seeded: list[str] = []
    skipped: list[str] = []
    for descriptor in read_legacy_harnesses(project_root):
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
            status=SEED_STATUS,
            invocation_surfaces=descriptor.get("invocation_surfaces"),
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
