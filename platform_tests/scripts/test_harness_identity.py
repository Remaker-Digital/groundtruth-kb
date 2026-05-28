from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_SRC = _REPO_ROOT / "groundtruth-kb" / "src"
if str(_PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(_PACKAGE_SRC))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from groundtruth_kb.harness_projection import (  # noqa: E402
    generate_harness_projection,
)

from scripts.harness_identity import (  # noqa: E402
    load_harness_identities,
    resolved_harness_id,
    set_harness_identity,
    validate_unique_harness_ids,
)

# ---------------------------------------------------------------------------
# WI-3342 IP-6 — registry-backed identity reader/writer fixtures.
#
# scripts/harness_identity.py was migrated off the legacy
# harness-state/harness-identities.json. load_harness_identities reads the
# DB-backed registry projection (harness-state/harness-registry.json), and the
# identity writers (set_harness_identity, the resolve_harness_identity
# bootstrap path) mutate the DB ``harnesses`` table via
# _mirror_identities_to_registry, then regenerate the projection.
# _mirror_identities_to_registry skips a harness whose current DB row carries
# no role set, so fixtures seed each harness with a role.
# ---------------------------------------------------------------------------


def _seed_registry(root: Path, identities: dict[str, str]) -> None:
    """Seed a groundtruth.db ``harnesses`` table + generated projection.

    ``identities`` maps each harness_name to its durable harness id. Each
    seeded harness carries a role set so the identity-write mirror does not
    skip it.
    """
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    for harness_name, harness_id in identities.items():
        db.insert_harness(
            id=harness_id,
            harness_name=harness_name,
            harness_type=harness_name,
            role=["loyal-opposition"],
            changed_by="test",
            change_reason="WI-3342 IP-6 harness_identity fixture",
            status="active",
        )
    generate_harness_projection(db, root)


def _identity_id(root: Path, harness_name: str) -> str | None:
    """Return the durable id recorded for ``harness_name`` in the registry."""
    document = load_harness_identities(root)
    record = document["harnesses"].get(harness_name)
    return record.get("id") if isinstance(record, dict) else None


def test_resolves_existing_persistent_identity_without_rewriting(tmp_path: Path) -> None:
    _seed_registry(tmp_path, {"codex": "A"})
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    version_before = db.get_harness("A")["version"]

    harness_id = resolved_harness_id(tmp_path, harness_name="codex")

    assert harness_id == "A"
    # WI-3342 IP-6: resolving an already-recorded identity must not append a
    # new registry version (the "without rewriting" contract).
    db_after = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    assert db_after.get_harness("A")["version"] == version_before


def test_startup_asserted_id_must_match_persistent_identity(tmp_path: Path) -> None:
    _seed_registry(tmp_path, {"codex": "A"})

    with pytest.raises(ValueError, match="persistently identified as A"):
        resolved_harness_id(tmp_path, harness_name="codex", harness_id="C")


def test_identity_ids_must_be_unique(tmp_path: Path) -> None:
    # A duplicate-id document is a validation-helper input; build it directly
    # rather than via the registry (the registry keys by unique harness id).
    document = {
        "harnesses": {
            "codex": {"id": "A"},
            "claude": {"id": "A"},
        }
    }
    assert validate_unique_harness_ids(document) == ["harness ID A is assigned to both codex and claude"]

    # A registry projection cannot itself encode the same id twice (id is the
    # record key), so the resolve-path uniqueness assertion is exercised by
    # loading a projection whose two records share an id.
    registry = tmp_path / "harness-state" / "harness-registry.json"
    registry.parent.mkdir(parents=True, exist_ok=True)
    registry.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": [
                    {"id": "A", "harness_name": "codex", "role": ["loyal-opposition"]},
                    {"id": "A", "harness_name": "claude", "role": ["prime-builder"]},
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="assigned to both"):
        resolved_harness_id(tmp_path, harness_name="codex")


def test_identity_change_requires_owner_requested_operation(tmp_path: Path) -> None:
    _seed_registry(tmp_path, {"codex": "A", "claude": "B"})

    with pytest.raises(ValueError, match="explicit owner-requested"):
        set_harness_identity(tmp_path, harness_name="codex", harness_id="C")

    changed_id, document, _path = set_harness_identity(
        tmp_path,
        harness_name="codex",
        harness_id="C",
        owner_requested=True,
    )

    assert changed_id == "C"
    assert document["harnesses"]["codex"]["id"] == "C"
    assert document["harnesses"]["codex"]["previous_id"] == "A"
    assert document["harnesses"]["codex"]["assigned_by"] == "explicit-owner-requested-identity-change"


def test_identity_change_rejects_duplicate_target_id(tmp_path: Path) -> None:
    _seed_registry(tmp_path, {"codex": "A", "claude": "B"})

    with pytest.raises(ValueError, match="already assigned to claude"):
        set_harness_identity(
            tmp_path,
            harness_name="codex",
            harness_id="B",
            owner_requested=True,
        )
