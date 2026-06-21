from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import ProjectLifecycleService


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


def _write_bridge(project_root: Path, slug: str, status: str, work_item_id: str | None = None) -> None:
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    body = f"{status}\n\n# Proposal {slug}\n"
    if work_item_id:
        body += f"\nWork Item: {work_item_id}\n"
    (bridge / f"{slug}-001.md").write_text(
        body,
        encoding="utf-8",
    )


def _write_verified_bridge(project_root: Path, work_item_id: str) -> None:
    slug = "gtkb-project-authorization-cli-completion"
    _write_bridge(project_root, slug, "VERIFIED", work_item_id)
    bridge = project_root / "bridge"
    (bridge / "INDEX.md").write_text(
        "\n".join(["# Bridge Index", "", f"Document: {slug}", f"VERIFIED: bridge/{slug}-001.md", ""]),
        encoding="utf-8",
    )


def _seed_completion_cli_env(tmp_path: Path, *, project_id: str, authorization_id: str, work_item_id: str) -> None:
    _write_verified_bridge(tmp_path, work_item_id)
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_deliberation(
            "DELIB-TEST-COMPLETE-AUTH",
            "owner_conversation",
            "Owner approved completion test authorization",
            "Owner approved the completion test project for implementation.",
            "{}",
            "test",
            "seed owner decision",
            outcome="owner_decision",
        )
        db.insert_spec(
            "SPEC-COMPLETE-AUTH",
            "Completion authorization spec",
            "verified",
            "test",
            "seed spec",
        )
        db.insert_work_item(
            work_item_id,
            "Completion authorization work item",
            "new",
            "platform",
            "open",
            "test",
            "seed work item",
        )
        db.insert_project("Completion Authorization", "test", "create project", id=project_id, status="active")
        db.link_project_work_item(project_id, work_item_id, "test", "link work item")
        db.insert_project_authorization(
            project_id,
            "Completion authorization approval",
            "DELIB-TEST-COMPLETE-AUTH",
            "Implement completion authorization behavior.",
            "test",
            "authorize implementation project",
            id=authorization_id,
            included_work_item_ids=[work_item_id],
            included_spec_ids=["SPEC-COMPLETE-AUTH"],
        )
        db.add_project_artifact_link(
            project_id,
            "bridge_thread",
            "gtkb-project-authorization-cli-completion",
            "test",
            "seed implements link",
            relationship="implements",
        )
    finally:
        db.close()


def _add_implements_bridge(
    db: KnowledgeDB,
    project_root: Path,
    *,
    project_id: str,
    slug: str,
    status: str,
    work_item_id: str | None = None,
) -> None:
    _write_bridge(project_root, slug, status, work_item_id)
    db.add_project_artifact_link(
        project_id,
        "bridge_thread",
        slug,
        "test",
        f"seed {status.lower()} implements link",
        relationship="implements",
    )


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


def test_complete_authorization_cli_keep_project_open(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _seed_completion_cli_env(
        tmp_path,
        project_id="PROJECT-COMPLETE-KEEP",
        authorization_id="PAUTH-COMPLETE-KEEP",
        work_item_id="WI-9001",
    )

    result = CliRunner().invoke(
        cli_main,
        [
            "--config",
            str(config_path),
            "projects",
            "complete-authorization",
            "PAUTH-COMPLETE-KEEP",
            "--change-reason",
            "complete authorization",
            "--keep-project-open",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Completed project authorization PAUTH-COMPLETE-KEEP." in result.output
    assert "Project retired." not in result.output

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        assert db.get_project_authorization("PAUTH-COMPLETE-KEEP")["status"] == "completed"
        assert db.get_project("PROJECT-COMPLETE-KEEP")["status"] == "active"
    finally:
        db.close()


def test_complete_authorization_cli_default_retires_project(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _seed_completion_cli_env(
        tmp_path,
        project_id="PROJECT-COMPLETE-RETIRE",
        authorization_id="PAUTH-COMPLETE-RETIRE",
        work_item_id="WI-9002",
    )

    result = CliRunner().invoke(
        cli_main,
        [
            "--config",
            str(config_path),
            "projects",
            "complete-authorization",
            "PAUTH-COMPLETE-RETIRE",
            "--change-reason",
            "complete authorization",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Completed project authorization PAUTH-COMPLETE-RETIRE. Project retired." in result.output

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        assert db.get_project_authorization("PAUTH-COMPLETE-RETIRE")["status"] == "completed"
        assert db.get_project("PROJECT-COMPLETE-RETIRE")["status"] == "retired"
    finally:
        db.close()


def test_autocomplete_withheld_when_addressing_thread_not_verified(tmp_path: Path) -> None:
    _seed_completion_cli_env(
        tmp_path,
        project_id="PROJECT-AUTOCOMPLETE-WITHHELD",
        authorization_id="PAUTH-AUTOCOMPLETE-WITHHELD",
        work_item_id="WI-9003",
    )

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _add_implements_bridge(
            db,
            tmp_path,
            project_id="PROJECT-AUTOCOMPLETE-WITHHELD",
            slug="gtkb-project-authorization-addressing-pending",
            status="NEW",
        )
        service = ProjectLifecycleService(db)

        assert service.auto_complete_ready_authorizations(project_root=tmp_path) == []
        assert db.get_project_authorization("PAUTH-AUTOCOMPLETE-WITHHELD")["status"] == "active"
        assert db.get_project("PROJECT-AUTOCOMPLETE-WITHHELD")["status"] == "active"
    finally:
        db.close()


def test_autocomplete_proceeds_when_addressing_thread_verified(tmp_path: Path) -> None:
    _seed_completion_cli_env(
        tmp_path,
        project_id="PROJECT-AUTOCOMPLETE-VERIFIED",
        authorization_id="PAUTH-AUTOCOMPLETE-VERIFIED",
        work_item_id="WI-9004",
    )

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _add_implements_bridge(
            db,
            tmp_path,
            project_id="PROJECT-AUTOCOMPLETE-VERIFIED",
            slug="gtkb-project-authorization-addressing-verified",
            status="VERIFIED",
        )
        service = ProjectLifecycleService(db)

        records = service.auto_complete_ready_authorizations(project_root=tmp_path)

        assert records == [
            {
                "outcome": "completed",
                "authorization_id": "PAUTH-AUTOCOMPLETE-VERIFIED",
                "project_id": "PROJECT-AUTOCOMPLETE-VERIFIED",
                "project_retired": True,
                "retired_work_items": ["WI-9004"],
            }
        ]
        assert db.get_project_authorization("PAUTH-AUTOCOMPLETE-VERIFIED")["status"] == "completed"
        assert db.get_project("PROJECT-AUTOCOMPLETE-VERIFIED")["status"] == "retired"
    finally:
        db.close()


def test_autocomplete_membership_only_project_unaffected(tmp_path: Path) -> None:
    _seed_completion_cli_env(
        tmp_path,
        project_id="PROJECT-AUTOCOMPLETE-MEMBERSHIP-ONLY",
        authorization_id="PAUTH-AUTOCOMPLETE-MEMBERSHIP-ONLY",
        work_item_id="WI-9005",
    )

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        service = ProjectLifecycleService(db)

        records = service.auto_complete_ready_authorizations(project_root=tmp_path)

        assert records == [
            {
                "outcome": "completed",
                "authorization_id": "PAUTH-AUTOCOMPLETE-MEMBERSHIP-ONLY",
                "project_id": "PROJECT-AUTOCOMPLETE-MEMBERSHIP-ONLY",
                "project_retired": True,
                "retired_work_items": ["WI-9005"],
            }
        ]
        assert db.get_project_authorization("PAUTH-AUTOCOMPLETE-MEMBERSHIP-ONLY")["status"] == "completed"
        assert db.get_project("PROJECT-AUTOCOMPLETE-MEMBERSHIP-ONLY")["status"] == "retired"
    finally:
        db.close()
