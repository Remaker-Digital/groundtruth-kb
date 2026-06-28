"""Tests for the Agent Red partition-in-place migration helper."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from groundtruth_kb.db import KnowledgeDB

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "agent_red_partition_in_place.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("agent_red_partition_in_place", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["agent_red_partition_in_place"] = module
    spec.loader.exec_module(module)
    return module


def _seed_partition_fixture(db: KnowledgeDB) -> None:
    db.insert_spec(
        id="SPEC-LEGACY-APP",
        title="Legacy Agent Red application path",
        status="specified",
        changed_by="test",
        change_reason="seed",
        source_paths=["Agent_Red/app/main.py"],
    )
    db.insert_spec(
        id="SPEC-AMBIGUOUS-APP",
        title="Agent Red generic test path",
        status="specified",
        changed_by="test",
        change_reason="seed",
        source_paths=["tests/test_widget.py"],
    )
    db.insert_spec(
        id="SPEC-MIXED-APP",
        title="Mixed platform and app evidence",
        status="specified",
        changed_by="test",
        change_reason="seed",
        source_paths=["bridge/thread-001.md", "applications/Agent_Red/.gtkb-app-isolation.json"],
    )
    db.insert_test(
        id="TEST-LEGACY-APP",
        title="Legacy Agent Red application test path",
        spec_id="SPEC-LEGACY-APP",
        test_type="unit",
        test_file="agent-red/tests/test_widget.py",
        expected_outcome="passes",
        changed_by="test",
        change_reason="seed",
    )


def test_partition_manifest_separates_updates_from_ambiguous_rows(tmp_path) -> None:
    module = _load_script_module()
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    _seed_partition_fixture(db)

    manifest = module.build_manifest(db)

    db.close()
    assert manifest["action_count"] == 2
    assert {row["id"] for row in manifest["actions"]} == {"SPEC-LEGACY-APP", "TEST-LEGACY-APP"}
    assert {row["id"] for row in manifest["ambiguous"]} == {"SPEC-AMBIGUOUS-APP", "SPEC-MIXED-APP"}
    spec_action = next(row for row in manifest["actions"] if row["id"] == "SPEC-LEGACY-APP")
    assert spec_action["proposed_scope"] == "agent_red_application"
    assert spec_action["proposed_paths"] == ["applications/Agent_Red/app/main.py"]


def test_partition_execute_uses_append_only_db_updates(tmp_path) -> None:
    module = _load_script_module()
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    _seed_partition_fixture(db)
    manifest = module.build_manifest(db)

    applied = module.apply_manifest(
        db,
        manifest,
        changed_by="test",
        change_reason="apply partition fixture",
        max_mutations=50,
    )
    spec = db.get_spec("SPEC-LEGACY-APP")
    test = db.get_test("TEST-LEGACY-APP")
    db.close()

    assert {row["id"] for row in applied} == {"SPEC-LEGACY-APP", "TEST-LEGACY-APP"}
    assert spec is not None
    assert spec["version"] == 2
    assert spec["application_scope"] == "agent_red_application"
    assert spec["source_paths_parsed"] == ["applications/Agent_Red/app/main.py"]
    assert test is not None
    assert test["version"] == 2
    assert test["application_scope"] == "agent_red_application"
    assert test["test_file"] == "applications/Agent_Red/tests/test_widget.py"
