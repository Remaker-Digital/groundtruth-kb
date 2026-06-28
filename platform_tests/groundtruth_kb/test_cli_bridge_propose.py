"""Platform tests for ``gt bridge file-implementation-proposal``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from click.testing import CliRunner
import groundtruth_kb.db
from groundtruth_kb.bridge import proposal_filing
from groundtruth_kb.cli import main
from groundtruth_kb.db import KnowledgeDB

# Eagerly disable ChromaDB in unit test runtime to avoid hangs during semantic search queries
groundtruth_kb.db.HAS_CHROMADB = False

WI_ID = "WI-4567"
PROJECT_ID = "PROJECT-GTKB-DETERMINISTIC-SERVICES-TEST"
AUTH_ID = "PAUTH-WI-4567-TEST"
DELIB_ID = "DELIB-WI-4567-TEST"
SPEC_ID = "SPEC-WI-4567-TEST"


class _FakeWriter:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def propose_bridge_codex_non_bypass(self, topic_slug: str, body: str, **kwargs: Any) -> Path:
        bridge_dir = Path(kwargs["bridge_dir"])
        bridge_dir.mkdir(parents=True, exist_ok=True)
        path = bridge_dir / f"{topic_slug}-{int(kwargs.get('version', 1)):03d}.md"
        path.write_text(body, encoding="utf-8")
        self.calls.append({"topic_slug": topic_slug, "body": body, **kwargs})
        return path


def _config_path(root: Path) -> Path:
    return root / "groundtruth.toml"


def _write_config(root: Path) -> Path:
    config = _config_path(root)
    config.write_text(
        f'[groundtruth]\ndb_path = "{(root / "groundtruth.db").as_posix()}"\n'
        f'project_root = "{root.as_posix()}"\napp_title = "Test Project"\n',
        encoding="utf-8",
    )
    return config


def _seed_db(root: Path, *, membership: bool = True, authorization: bool = True) -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_spec(
            id=SPEC_ID,
            title="WI-4567 test spec",
            status="specified",
            changed_by="test",
            change_reason="seed spec",
        )
        db.insert_deliberation(
            id=DELIB_ID,
            source_type="owner_conversation",
            title="Owner decision for WI-4567",
            summary="Owner approved bounded proposal-filing state creation.",
            content="Owner approved bounded proposal-filing state creation.",
            changed_by="test",
            change_reason="seed owner decision",
        )
        db.insert_project("Deterministic Services", "test", "seed project", id=PROJECT_ID)
        db.insert_work_item(
            id=WI_ID,
            title="Bridge proposal filing service",
            description="One command files a gate-passing bridge implementation proposal.",
            origin="improvement",
            component="bridge-tooling",
            source_spec_id=SPEC_ID,
            resolution_status="open",
            priority="P3",
            changed_by="test",
            change_reason="seed work item",
        )
        if membership:
            db.link_project_work_item(PROJECT_ID, WI_ID, "test", "seed membership")
        if authorization:
            db.insert_project_authorization(
                PROJECT_ID,
                "WI-4567 test authorization",
                DELIB_ID,
                "Bounded authorization for WI-4567 tests.",
                "test",
                "seed authorization",
                id=AUTH_ID,
                included_work_item_ids=[WI_ID],
                included_spec_ids=[SPEC_ID],
            )
    finally:
        db.close()


def _install_fakes(monkeypatch) -> tuple[_FakeWriter, list[dict[str, Any]]]:
    writer = _FakeWriter()
    preflights: list[dict[str, Any]] = []

    def fake_load_writer(_project_root: Path) -> _FakeWriter:
        return writer

    def fake_preflight(project_root: Path, *, name: str, content_file=None, bridge_id=None):
        preflights.append(
            {
                "project_root": project_root,
                "name": name,
                "content_file": content_file,
                "bridge_id": bridge_id,
            }
        )
        return proposal_filing.PreflightResult(name=name, returncode=0, stdout="PASS", stderr="")

    monkeypatch.setattr(proposal_filing, "_load_bridge_writer", fake_load_writer)
    monkeypatch.setattr(proposal_filing, "_run_preflight_command", fake_preflight)
    return writer, preflights


def _invoke(root: Path, *args: str):
    return CliRunner().invoke(main, ["--config", str(_config_path(root)), *args])


def test_file_implementation_proposal_reuses_active_state_and_writes_new(tmp_path: Path, monkeypatch) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path)
    writer, preflights = _install_fakes(monkeypatch)

    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-test",
        "--target-path",
        "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py",
        "--add-spec",
        SPEC_ID,
    )

    assert result.exit_code == 0, result.output
    bridge_file = tmp_path / "bridge" / "gtkb-wi4567-test-001.md"
    assert bridge_file.is_file()
    content = bridge_file.read_text(encoding="utf-8")
    assert "Version: 001\n" in content
    assert "DRAFT" not in content
    assert f"Project Authorization: {AUTH_ID}" in content
    assert f"Project: {PROJECT_ID}" in content
    assert f"Work Item: {WI_ID}" in content
    assert 'target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py"]' in content
    assert "## Specification-Derived Verification Plan" in content
    assert writer.calls[0]["topic_slug"] == "gtkb-wi4567-test"
    assert [item["name"] for item in preflights] == ["applicability", "adr_dcl", "applicability", "adr_dcl"]
    assert preflights[0]["content_file"] is not None
    assert preflights[-1]["bridge_id"] == "gtkb-wi4567-test"


def test_file_implementation_proposal_fails_closed_without_active_authorization(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    _install_fakes(monkeypatch)

    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-test",
        "--target-path",
        "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py",
        "--add-spec",
        SPEC_ID,
    )

    assert result.exit_code == 1
    assert "No active project authorization covers" in result.output
    assert not (tmp_path / "bridge").exists()


def test_file_implementation_proposal_can_create_missing_state_with_owner_decision(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, membership=False, authorization=False)
    _install_fakes(monkeypatch)

    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-test",
        "--project",
        PROJECT_ID,
        "--owner-decision",
        DELIB_ID,
        "--create-missing-state",
        "--target-path",
        "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py",
        "--add-spec",
        SPEC_ID,
    )

    assert result.exit_code == 0, result.output
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    try:
        memberships = db.list_project_work_items(PROJECT_ID)
        authorizations = db.list_project_authorizations(PROJECT_ID, status="active")
    finally:
        db.close()
    assert [item["work_item_id"] for item in memberships] == [WI_ID]
    covering = [auth for auth in authorizations if WI_ID in (auth.get("included_work_item_ids_parsed") or [])]
    assert covering
    assert (tmp_path / "bridge" / "gtkb-wi4567-test-001.md").is_file()


def test_file_implementation_proposal_rejects_agent_red_target(tmp_path: Path, monkeypatch) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path)
    _install_fakes(monkeypatch)

    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-test",
        "--target-path",
        "applications/Agent_Red/src/main.py",
        "--add-spec",
        SPEC_ID,
    )

    assert result.exit_code == 1
    assert "Agent Red targets are out of scope" in result.output


def test_file_implementation_proposal_help_resolves() -> None:
    result = CliRunner().invoke(main, ["bridge", "file-implementation-proposal", "--help"])
    assert result.exit_code == 0, result.output
    assert "File a dispatchable NEW implementation proposal" in result.output
