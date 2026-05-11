from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.harness_identity import resolved_harness_id, set_harness_identity, validate_unique_harness_ids


def _write_identity_map(path: Path, identities: dict[str, str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "harnesses": {
                    harness_name: {"id": harness_id, "assigned_by": "test"}
                    for harness_name, harness_id in identities.items()
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def test_resolves_existing_persistent_identity_without_rewriting(tmp_path: Path) -> None:
    identity_path = _write_identity_map(tmp_path / "harness-identities.json", {"codex": "A"})
    before = identity_path.read_text(encoding="utf-8")

    harness_id = resolved_harness_id(
        tmp_path,
        harness_name="codex",
        identity_path=identity_path,
    )

    assert harness_id == "A"
    assert identity_path.read_text(encoding="utf-8") == before


def test_startup_asserted_id_must_match_persistent_identity(tmp_path: Path) -> None:
    identity_path = _write_identity_map(tmp_path / "harness-identities.json", {"codex": "A"})

    with pytest.raises(ValueError, match="persistently identified as A"):
        resolved_harness_id(
            tmp_path,
            harness_name="codex",
            harness_id="C",
            identity_path=identity_path,
        )


def test_identity_ids_must_be_unique(tmp_path: Path) -> None:
    identity_path = _write_identity_map(tmp_path / "harness-identities.json", {"codex": "A", "claude": "A"})
    document = json.loads(identity_path.read_text(encoding="utf-8"))

    assert validate_unique_harness_ids(document) == ["harness ID A is assigned to both codex and claude"]
    with pytest.raises(ValueError, match="assigned to both"):
        resolved_harness_id(tmp_path, harness_name="codex", identity_path=identity_path)


def test_identity_change_requires_owner_requested_operation(tmp_path: Path) -> None:
    identity_path = _write_identity_map(tmp_path / "harness-identities.json", {"codex": "A", "claude": "B"})

    with pytest.raises(ValueError, match="explicit owner-requested"):
        set_harness_identity(
            tmp_path,
            harness_name="codex",
            harness_id="C",
            identity_path=identity_path,
        )

    changed_id, document, _path = set_harness_identity(
        tmp_path,
        harness_name="codex",
        harness_id="C",
        owner_requested=True,
        identity_path=identity_path,
    )

    assert changed_id == "C"
    assert document["harnesses"]["codex"]["id"] == "C"
    assert document["harnesses"]["codex"]["previous_id"] == "A"
    assert document["harnesses"]["codex"]["assigned_by"] == "explicit-owner-requested-identity-change"


def test_identity_change_rejects_duplicate_target_id(tmp_path: Path) -> None:
    identity_path = _write_identity_map(tmp_path / "harness-identities.json", {"codex": "A", "claude": "B"})

    with pytest.raises(ValueError, match="already assigned to claude"):
        set_harness_identity(
            tmp_path,
            harness_name="codex",
            harness_id="B",
            owner_requested=True,
            identity_path=identity_path,
        )
