from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.db import KnowledgeDB


def _write_config(tmp_path: Path) -> Path:
    config_path = tmp_path / "groundtruth.toml"
    config_path.write_text(
        "\n".join(
            [
                "[groundtruth]",
                f'db_path = "{(tmp_path / "groundtruth.db").as_posix()}"',
                f'project_root = "{tmp_path.as_posix()}"',
                'app_title = "CLI Artifact Read Verb Test"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def _invoke_json(config_path: Path, *args: str):
    result = CliRunner().invoke(cli_main, ["--config", str(config_path), *args, "--json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def _seed_artifacts(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_spec(
            "SPEC-READ-001",
            "Readable spec",
            "specified",
            "test",
            "seed spec",
            description="Initial description",
            priority="P2",
            section="cli",
            handle="readable-spec",
            tags=["cli-read"],
            testability="automatable",
        )
        db.insert_spec(
            "SPEC-READ-001",
            "Readable spec",
            "verified",
            "test",
            "verify spec",
            description="Verified description",
            priority="P2",
            section="cli",
            handle="readable-spec",
            tags=["cli-read"],
            testability="automatable",
        )
        db.insert_spec(
            "SPEC-OTHER-001",
            "Other spec",
            "specified",
            "test",
            "seed other spec",
            description="Other description",
            priority="P3",
        )
        db.insert_deliberation(
            "DELIB-READ-001",
            "owner_conversation",
            "Read deliberation",
            "Summary for readback",
            "Deliberation body",
            "test",
            "seed deliberation",
            outcome="owner_decision",
            spec_id="SPEC-READ-001",
        )
        db.insert_test(
            "TEST-READ-001",
            "Readable test",
            "SPEC-READ-001",
            "unit",
            "Command exits 0",
            "test",
            "seed test",
            test_file="platform_tests/scripts/test_cli_artifact_read_verbs.py",
            test_function="test_tests_show_and_list_read_artifacts",
            last_result="pass",
            last_executed_at="2026-06-18T00:00:00Z",
        )
        db.insert_test(
            "TEST-READ-001",
            "Readable test",
            "SPEC-READ-001",
            "unit",
            "Command exits 0",
            "test",
            "update test",
            test_file="platform_tests/scripts/test_cli_artifact_read_verbs.py",
            test_function="test_tests_show_and_list_read_artifacts",
            last_result="fail",
            last_executed_at="2026-06-18T01:00:00Z",
        )
        db.insert_test(
            "TEST-OTHER-001",
            "Other test",
            "SPEC-OTHER-001",
            "integration",
            "Other command exits 0",
            "test",
            "seed other test",
            last_result="pass",
        )
    finally:
        db.close()


def test_spec_show_and_list_read_artifacts(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _seed_artifacts(tmp_path)

    shown = _invoke_json(config_path, "spec", "show", "SPEC-READ-001")
    assert shown["id"] == "SPEC-READ-001"
    assert shown["version"] == 2
    assert shown["status"] == "verified"

    history = _invoke_json(config_path, "spec", "show", "SPEC-READ-001", "--history")
    assert [row["version"] for row in history] == [2, 1]

    listed = _invoke_json(config_path, "spec", "list", "--status", "verified", "--tag", "cli-read")
    assert [row["id"] for row in listed] == ["SPEC-READ-001"]


def test_deliberations_show_alias_matches_get(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _seed_artifacts(tmp_path)

    shown = _invoke_json(config_path, "deliberations", "show", "DELIB-READ-001")
    got = _invoke_json(config_path, "deliberations", "get", "DELIB-READ-001")

    assert shown == got
    assert shown["id"] == "DELIB-READ-001"
    assert shown["spec_id"] == "SPEC-READ-001"


def test_tests_show_and_list_read_artifacts(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _seed_artifacts(tmp_path)

    shown = _invoke_json(config_path, "tests", "show", "TEST-READ-001")
    assert shown["id"] == "TEST-READ-001"
    assert shown["version"] == 2
    assert shown["last_result"] == "fail"

    history = _invoke_json(config_path, "tests", "show", "TEST-READ-001", "--history")
    assert [row["version"] for row in history] == [2, 1]

    listed = _invoke_json(config_path, "tests", "list", "--spec-id", "SPEC-READ-001", "--test-type", "unit")
    assert [row["id"] for row in listed] == ["TEST-READ-001"]
