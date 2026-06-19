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
                'app_title = "Project Authorization Test"',
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


def _seed_project_authorization_inputs(tmp_path: Path) -> None:
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-TEST-PROJECT-AUTH",
            "owner_conversation",
            "Owner approved bounded project implementation",
            "Owner approved the test project for implementation.",
            "{}",
            "test",
            "seed owner decision",
            outcome="owner_decision",
        )
        db.insert_spec(
            "SPEC-SCOPED-IMPL",
            "Scoped spec",
            "specified",
            "test",
            "seed spec",
        )
        db.insert_work_item(
            "WI-PROJECT-AUTH-001",
            "Project authorization work item",
            "new",
            "platform",
            "open",
            "test",
            "seed work item",
            stage="backlogged",
        )
    finally:
        db.close()


def test_project_authorization_cli_is_append_only_and_visible(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _seed_project_authorization_inputs(tmp_path)

    project = _invoke_json(
        config_path,
        "projects",
        "create",
        "Scoped Implementation",
        "--id",
        "PROJECT-SCOPED-IMPL",
        "--change-reason",
        "create project",
    )
    assert project["id"] == "PROJECT-SCOPED-IMPL"

    _invoke_json(
        config_path,
        "projects",
        "add-item",
        "PROJECT-SCOPED-IMPL",
        "WI-PROJECT-AUTH-001",
        "--change-reason",
        "link work item",
    )
    authorization = _invoke_json(
        config_path,
        "projects",
        "authorize",
        "PROJECT-SCOPED-IMPL",
        "--id",
        "PAUTH-SCOPED-IMPL",
        "--owner-decision",
        "DELIB-TEST-PROJECT-AUTH",
        "--name",
        "Scoped implementation approval",
        "--scope",
        "Implement the project-scoped approved work items.",
        "--allowed-mutation",
        "source",
        "--allowed-mutation",
        "tests",
        "--forbid",
        "production-deploy",
        "--include-work-item",
        "WI-PROJECT-AUTH-001",
        "--include-spec",
        "SPEC-SCOPED-IMPL",
        "--change-reason",
        "authorize implementation project",
    )

    assert authorization["id"] == "PAUTH-SCOPED-IMPL"
    assert authorization["version"] == 1
    assert authorization["status"] == "active"
    assert authorization["allowed_mutation_classes_parsed"] == ["source", "tests"]
    assert authorization["forbidden_operations_parsed"] == ["production-deploy"]
    assert authorization["included_work_item_ids_parsed"] == ["WI-PROJECT-AUTH-001"]

    shown = _invoke_json(config_path, "projects", "show", "PROJECT-SCOPED-IMPL")
    assert [row["id"] for row in shown["authorizations"]] == ["PAUTH-SCOPED-IMPL"]

    listed = _invoke_json(config_path, "projects", "authorizations", "PROJECT-SCOPED-IMPL")
    assert [row["id"] for row in listed] == ["PAUTH-SCOPED-IMPL"]

    shown_authorization = _invoke_json(config_path, "projects", "show-authorization", "PAUTH-SCOPED-IMPL")
    assert shown_authorization["id"] == "PAUTH-SCOPED-IMPL"
    assert shown_authorization["project_id"] == "PROJECT-SCOPED-IMPL"
    assert shown_authorization["allowed_mutation_classes_parsed"] == ["source", "tests"]

    revoked = _invoke_json(
        config_path,
        "projects",
        "revoke-authorization",
        "PAUTH-SCOPED-IMPL",
        "--change-reason",
        "revoke implementation approval",
    )
    assert revoked["version"] == 2
    assert revoked["status"] == "revoked"

    assert _invoke_json(config_path, "projects", "authorizations", "PROJECT-SCOPED-IMPL") == []
    all_authorizations = _invoke_json(config_path, "projects", "authorizations", "PROJECT-SCOPED-IMPL", "--all")
    assert [(row["id"], row["status"], row["version"]) for row in all_authorizations] == [
        ("PAUTH-SCOPED-IMPL", "revoked", 2)
    ]
