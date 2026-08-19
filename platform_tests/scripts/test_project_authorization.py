from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from groundtruth_kb.cli import main as cli_main
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.project.lifecycle import (
    ProjectLifecycleError,
    ProjectLifecycleService,
)


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
    result = CliRunner().invoke(
        cli_main, ["--config", str(config_path), *args, "--json"]
    )
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


def _write_bridge(
    project_root: Path, slug: str, status: str, work_item_id: str | None = None
) -> None:
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
        "\n".join(
            [
                "# Bridge Index",
                "",
                f"Document: {slug}",
                f"VERIFIED: bridge/{slug}-001.md",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _write_open_project_authorization_thread(
    project_root: Path,
    *,
    project_id: str,
    authorization_id: str,
    slug: str = "gtkb-project-authorization-open-go",
) -> None:
    bridge = project_root / "bridge"
    bridge.mkdir(parents=True, exist_ok=True)
    (bridge / f"{slug}-001.md").write_text(
        "\n".join(
            [
                "NEW",
                "",
                "# Fixture open PAUTH proposal",
                "",
                f"Project Authorization: {authorization_id}",
                f"Project: {project_id}",
                "Work Item: WI-OPEN-PAUTH",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (bridge / f"{slug}-002.md").write_text(
        "GO\n\n# Fixture GO verdict\n", encoding="utf-8"
    )


def _seed_completion_cli_env(
    tmp_path: Path, *, project_id: str, authorization_id: str, work_item_id: str
) -> None:
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
        db.insert_project(
            "Completion Authorization",
            "test",
            "create project",
            id=project_id,
            status="active",
        )
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


def _add_completion_guard(
    project_root: Path, *, project_id: str, authorization_id: str
) -> None:
    db = KnowledgeDB(project_root / "groundtruth.db")
    try:
        db.add_project_artifact_link(
            project_id,
            "completion_guard",
            f"{authorization_id}-keepopen",
            "test",
            "seed plan-incomplete keep-open guard",
            relationship="plan_incomplete",
            notes="Fixture keep-open guard",
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

    listed = _invoke_json(
        config_path, "projects", "authorizations", "PROJECT-SCOPED-IMPL"
    )
    assert [row["id"] for row in listed] == ["PAUTH-SCOPED-IMPL"]

    shown_authorization = _invoke_json(
        config_path, "projects", "show-authorization", "PAUTH-SCOPED-IMPL"
    )
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

    assert (
        _invoke_json(config_path, "projects", "authorizations", "PROJECT-SCOPED-IMPL")
        == []
    )
    all_authorizations = _invoke_json(
        config_path, "projects", "authorizations", "PROJECT-SCOPED-IMPL", "--all"
    )
    assert [
        (row["id"], row["status"], row["version"]) for row in all_authorizations
    ] == [("PAUTH-SCOPED-IMPL", "revoked", 2)]


def test_project_authorization_cli_plan_incomplete_records_keep_open_guard(
    tmp_path: Path,
) -> None:
    config_path = _write_config(tmp_path)
    _seed_project_authorization_inputs(tmp_path)

    _invoke_json(
        config_path,
        "projects",
        "create",
        "Scoped Implementation",
        "--id",
        "PROJECT-SCOPED-IMPL",
        "--change-reason",
        "create project",
    )
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
        "Implement one slice and keep the project open.",
        "--include-work-item",
        "WI-PROJECT-AUTH-001",
        "--include-spec",
        "SPEC-SCOPED-IMPL",
        "--plan-incomplete",
        "--change-reason",
        "authorize implementation project",
    )

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        links = db.list_project_artifact_links("PROJECT-SCOPED-IMPL")
    finally:
        db.close()

    assert authorization["id"] == "PAUTH-SCOPED-IMPL"
    guard = next(
        link
        for link in links
        if link["artifact_type"] == "completion_guard"
        and link["relationship"] == "plan_incomplete"
        and link["artifact_ref"] == "PAUTH-SCOPED-IMPL-keepopen"
    )
    assert guard["status"] == "active"


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
        assert (
            db.get_project_authorization("PAUTH-COMPLETE-KEEP")["status"] == "completed"
        )
        assert db.get_project("PROJECT-COMPLETE-KEEP")["status"] == "active"
    finally:
        db.close()


def test_complete_authorization_cli_plan_incomplete_guard_keeps_project_open(
    tmp_path: Path,
) -> None:
    config_path = _write_config(tmp_path)
    _seed_completion_cli_env(
        tmp_path,
        project_id="PROJECT-COMPLETE-GUARD",
        authorization_id="PAUTH-COMPLETE-GUARD",
        work_item_id="WI-9001",
    )
    _add_completion_guard(
        tmp_path,
        project_id="PROJECT-COMPLETE-GUARD",
        authorization_id="PAUTH-COMPLETE-GUARD",
    )

    result = CliRunner().invoke(
        cli_main,
        [
            "--config",
            str(config_path),
            "projects",
            "complete-authorization",
            "PAUTH-COMPLETE-GUARD",
            "--change-reason",
            "complete authorization",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Completed project authorization PAUTH-COMPLETE-GUARD." in result.output
    assert "Project retired." not in result.output

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        assert (
            db.get_project_authorization("PAUTH-COMPLETE-GUARD")["status"]
            == "completed"
        )
        assert db.get_project("PROJECT-COMPLETE-GUARD")["status"] == "active"
        guard = next(
            link
            for link in db.list_project_artifact_links(
                "PROJECT-COMPLETE-GUARD", include_inactive=True
            )
            if link["artifact_ref"] == "PAUTH-COMPLETE-GUARD-keepopen"
        )
        assert guard["status"] == "inactive"
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
    assert (
        "Completed project authorization PAUTH-COMPLETE-RETIRE. Project retired."
        in result.output
    )

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        assert (
            db.get_project_authorization("PAUTH-COMPLETE-RETIRE")["status"]
            == "completed"
        )
        assert db.get_project("PROJECT-COMPLETE-RETIRE")["status"] == "retired"
    finally:
        db.close()


def test_autocomplete_withheld_when_addressing_thread_not_verified(
    tmp_path: Path,
) -> None:
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
        assert (
            db.get_project_authorization("PAUTH-AUTOCOMPLETE-WITHHELD")["status"]
            == "active"
        )
        assert db.get_project("PROJECT-AUTOCOMPLETE-WITHHELD")["status"] == "active"
    finally:
        db.close()


def test_complete_authorization_withheld_when_project_authorization_thread_open(
    tmp_path: Path,
) -> None:
    _seed_completion_cli_env(
        tmp_path,
        project_id="PROJECT-COMPLETE-OPEN-GO",
        authorization_id="PAUTH-COMPLETE-OPEN-GO",
        work_item_id="WI-9006",
    )

    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        _write_open_project_authorization_thread(
            tmp_path,
            project_id="PROJECT-COMPLETE-OPEN-GO",
            authorization_id="PAUTH-COMPLETE-OPEN-GO",
        )
        service = ProjectLifecycleService(db)

        with pytest.raises(
            ProjectLifecycleError, match="active project-authorization bridge thread"
        ):
            service.complete_project_authorization(
                "PAUTH-COMPLETE-OPEN-GO",
                project_root=tmp_path,
                change_reason="complete authorization",
            )
        assert (
            db.get_project_authorization("PAUTH-COMPLETE-OPEN-GO")["status"] == "active"
        )
        assert db.get_project("PROJECT-COMPLETE-OPEN-GO")["status"] == "active"
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
        assert (
            db.get_project_authorization("PAUTH-AUTOCOMPLETE-VERIFIED")["status"]
            == "completed"
        )
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
        assert (
            db.get_project_authorization("PAUTH-AUTOCOMPLETE-MEMBERSHIP-ONLY")["status"]
            == "completed"
        )
        assert (
            db.get_project("PROJECT-AUTOCOMPLETE-MEMBERSHIP-ONLY")["status"]
            == "retired"
        )
    finally:
        db.close()


def test_restrictive_included_list_authorizes_only_listed_wi(tmp_path: Path) -> None:
    import importlib.util
    import sys

    auth_path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "implementation_authorization.py"
    )
    spec = importlib.util.spec_from_file_location(
        "implementation_authorization_proj_auth", auth_path
    )
    assert spec and spec.loader
    auth = importlib.util.module_from_spec(spec)
    sys.modules["implementation_authorization_proj_auth"] = auth
    spec.loader.exec_module(auth)

    _seed_project_authorization_inputs(tmp_path)
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    try:
        db.insert_project(
            "Restrictive Auth Project",
            "test",
            "seed",
            id="PROJECT-RESTRICT",
            status="active",
        )
        db.insert_work_item(
            "WI-9001",
            "Listed WI",
            "new",
            "platform",
            "open",
            "test",
            "seed",
            stage="backlogged",
        )
        db.insert_work_item(
            "WI-MEMBER-ONLY",
            "Member only WI",
            "new",
            "platform",
            "open",
            "test",
            "seed",
            stage="backlogged",
        )
        db.link_project_work_item(
            "PROJECT-RESTRICT", "WI-MEMBER-ONLY", "test", "link member"
        )
        db.insert_project_authorization(
            "PROJECT-RESTRICT",
            "Restrictive included list",
            "DELIB-TEST-PROJECT-AUTH",
            "Restrictive scope test.",
            "test",
            "seed auth",
            id="PAUTH-RESTRICT",
            included_work_item_ids=["WI-LISTED"],
            included_spec_ids=["SPEC-SCOPED-IMPL"],
        )
    finally:
        db.close()

    row = auth._project_authorization_row(tmp_path, "PAUTH-RESTRICT")
    auth.validate_project_authorization_row(tmp_path, row, work_item_id="WI-LISTED")

    with pytest.raises(
        auth.AuthorizationError,
        match="not in the authorizing included_work_item_ids list",
    ):
        auth.validate_project_authorization_row(
            tmp_path, row, work_item_id="WI-MEMBER-ONLY"
        )

    with pytest.raises(
        auth.AuthorizationError,
        match="not in the authorizing included_work_item_ids list",
    ):
        auth.validate_project_authorization_row(
            tmp_path, row, work_item_id="WI-NOT-ANYWHERE"
        )


# --- WI-6505: bounded project-authorization amendment -----------------------
#
# The defect: authorize_project is a whole-envelope write, so amending by
# re-issue silently revokes scope for anything the caller fails to restate, and
# on a large include list the equivalent CLI invocation exceeds the Windows
# command-line limit (WI-6480). These tests pin the delta path.

_AMEND_AUTH_ID = "PAUTH-AMEND-TEST"
_AMEND_PROJECT_ID = "PROJECT-AMEND-TEST"


def _seed_amendable_authorization(
    tmp_path: Path, *, include_count: int = 400
) -> ProjectLifecycleService:
    """Create an active authorization with a deliberately large include list."""
    db = KnowledgeDB(tmp_path / "groundtruth.db")
    db.insert_deliberation(
        "DELIB-AMEND-TEST",
        "owner_conversation",
        "Owner approved the amendable test authorization",
        "Owner approval.",
        "{}",
        "test",
        "seed owner decision",
        outcome="owner_decision",
    )
    db.insert_spec("SPEC-AMEND-TEST", "Amend spec", "specified", "test", "seed spec")
    service = ProjectLifecycleService(db)
    service.create_project(
        "Amend Test", project_id=_AMEND_PROJECT_ID, change_reason="seed project"
    )
    service.authorize_project(
        _AMEND_PROJECT_ID,
        authorization_id=_AMEND_AUTH_ID,
        owner_decision="DELIB-AMEND-TEST",
        name="Amend test authorization",
        scope="Bounded scope for amendment tests.",
        change_reason="seed authorization",
        allowed_mutation_classes=["source", "test"],
        forbidden_operations=["git_commit"],
        included_work_item_ids=[f"WI-{6000 + n}" for n in range(include_count)],
        included_spec_ids=["SPEC-AMEND-TEST"],
    )
    return service


def test_amend_adds_item_and_preserves_all_others(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path)
    try:
        before = service.db.get_project_authorization(_AMEND_AUTH_ID)
        before_items = json.loads(before["included_work_item_ids"])

        result = service.amend_authorization(
            _AMEND_AUTH_ID,
            owner_decision="DELIB-AMEND-TEST",
            add_work_items=["WI-NEWLY-ADDED"],
            change_reason="add one work item",
        )

        after_items = json.loads(result["authorization"]["included_work_item_ids"])
        assert "WI-NEWLY-ADDED" in after_items
        assert len(after_items) == len(before_items) + 1
        # The whole point: nothing that was present went missing.
        assert set(before_items).issubset(set(after_items))
        assert result["delta"]["work_items_added"] == ["WI-NEWLY-ADDED"]
        assert result["delta"]["work_items_removed"] == []
        assert result["delta"]["dropped"] == []
    finally:
        service.db.close()


def test_amend_carries_unspecified_fields_forward(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path)
    try:
        before = service.db.get_project_authorization(_AMEND_AUTH_ID)
        service.amend_authorization(
            _AMEND_AUTH_ID,
            owner_decision="DELIB-AMEND-TEST",
            add_work_items=["WI-CARRY-FORWARD"],
            change_reason="add one work item",
        )
        after = service.db.get_project_authorization(_AMEND_AUTH_ID)

        # Every field the caller did not name must be identical, by construction
        # rather than because the caller restated it correctly.
        for field in (
            "authorization_name",
            "scope_summary",
            "allowed_mutation_classes",
            "forbidden_operations",
            "included_spec_ids",
            "excluded_work_item_ids",
            "excluded_spec_ids",
            "expires_at",
            "project_id",
        ):
            assert after[field] == before[field], field
    finally:
        service.db.close()


def test_amend_is_append_only(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path)
    try:
        before = service.db.get_project_authorization(_AMEND_AUTH_ID)
        result = service.amend_authorization(
            _AMEND_AUTH_ID,
            owner_decision="DELIB-AMEND-TEST",
            add_work_items=["WI-APPEND-ONLY"],
            change_reason="add one work item",
        )
        assert result["authorization"]["version"] == before["version"] + 1

        rows = (
            service.db._get_conn()
            .execute(
                "SELECT version, included_work_item_ids FROM project_authorizations WHERE id = ? ORDER BY version",
                (_AMEND_AUTH_ID,),
            )
            .fetchall()
        )
        assert len(rows) >= 2
        # The prior version is still readable and still lacks the new entry.
        assert "WI-APPEND-ONLY" not in json.loads(rows[0][1])
    finally:
        service.db.close()


def test_amend_refuses_non_active_authorization(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path)
    try:
        service.revoke_project_authorization(
            _AMEND_AUTH_ID, change_reason="revoke for test"
        )
        with pytest.raises(
            ProjectLifecycleError, match="only an active authorization may be amended"
        ):
            service.amend_authorization(
                _AMEND_AUTH_ID,
                owner_decision="DELIB-AMEND-TEST",
                add_work_items=["WI-SHOULD-NOT-LAND"],
                change_reason="amend a revoked authorization",
            )
    finally:
        service.db.close()


def test_amend_refuses_missing_authorization(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path)
    try:
        with pytest.raises(ProjectLifecycleError, match="not found"):
            service.amend_authorization(
                "PAUTH-DOES-NOT-EXIST",
                owner_decision="DELIB-AMEND-TEST",
                add_work_items=["WI-X"],
                change_reason="amend a missing authorization",
            )
    finally:
        service.db.close()


def test_amend_requires_owner_decision(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path)
    try:
        with pytest.raises((ProjectLifecycleError, ValueError)):
            service.amend_authorization(
                _AMEND_AUTH_ID,
                owner_decision="",
                add_work_items=["WI-NO-OWNER-DECISION"],
                change_reason="amend without owner decision",
            )
    finally:
        service.db.close()


def test_amend_refuses_to_empty_include_list(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path, include_count=2)
    try:
        with pytest.raises(
            ProjectLifecycleError, match="would empty included_work_item_ids"
        ):
            service.amend_authorization(
                _AMEND_AUTH_ID,
                owner_decision="DELIB-AMEND-TEST",
                remove_work_items=["WI-6000", "WI-6001"],
                change_reason="empty the include list",
            )
    finally:
        service.db.close()


def test_amend_removal_is_explicit_only(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path, include_count=5)
    try:
        result = service.amend_authorization(
            _AMEND_AUTH_ID,
            owner_decision="DELIB-AMEND-TEST",
            remove_work_items=["WI-6002"],
            change_reason="remove exactly one",
        )
        after = json.loads(result["authorization"]["included_work_item_ids"])
        assert "WI-6002" not in after
        assert len(after) == 4
        assert result["delta"]["work_items_removed"] == ["WI-6002"]
        # Nothing else left, and the unrequested-drop guard stayed empty.
        assert result["delta"]["dropped"] == []
    finally:
        service.db.close()


def test_amend_dry_run_writes_nothing(tmp_path: Path) -> None:
    service = _seed_amendable_authorization(tmp_path)
    try:
        before = service.db.get_project_authorization(_AMEND_AUTH_ID)
        result = service.amend_authorization(
            _AMEND_AUTH_ID,
            owner_decision="DELIB-AMEND-TEST",
            add_work_items=["WI-DRY-RUN"],
            change_reason="dry run",
            dry_run=True,
        )
        after = service.db.get_project_authorization(_AMEND_AUTH_ID)

        assert result["dry_run"] is True
        assert result["authorization"] is None
        assert result["delta"]["work_items_added"] == ["WI-DRY-RUN"]
        assert after["version"] == before["version"]
        assert "WI-DRY-RUN" not in json.loads(after["included_work_item_ids"])
    finally:
        service.db.close()


def test_amend_cli_argv_stays_bounded_for_large_include_list(tmp_path: Path) -> None:
    """WI-6480 regression guard: argv scales with the delta, not the envelope."""
    config_path = _write_config(tmp_path)
    service = _seed_amendable_authorization(tmp_path)
    service.db.close()

    argv = [
        "projects",
        "amend-authorization",
        _AMEND_AUTH_ID,
        "--owner-decision",
        "DELIB-AMEND-TEST",
        "--add-work-item",
        "WI-CLI-ADDED",
        "--change-reason",
        "add one work item through the CLI",
    ]
    # The equivalent re-issue would have to restate all 400 includes; this must
    # not, so the rendered command line stays far below the 8191-char limit.
    assert len(" ".join(argv)) < 2000

    payload = _invoke_json(config_path, *argv)
    assert payload["delta"]["work_items_added"] == ["WI-CLI-ADDED"]
    assert (
        payload["delta"]["work_items_after"]
        == payload["delta"]["work_items_before"] + 1
    )
    assert payload["delta"]["dropped"] == []
