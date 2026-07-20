"""Platform tests for ``gt bridge file-implementation-proposal``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import groundtruth_kb.db
import pytest
from click.testing import CliRunner
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


def _nonimpairment_disposition(content: str) -> dict[str, Any]:
    section = content.split("## Intuitiveness / Non-Impairment Disposition", 1)[1]
    fenced = section.split("```json", 1)[1].split("```", 1)[0]
    return json.loads(fenced)


def _replace_nonimpairment_disposition(content: str, disposition: dict[str, Any]) -> str:
    heading, remainder = content.split("## Intuitiveness / Non-Impairment Disposition", 1)
    _, after = remainder.split("```json", 1)
    _, suffix = after.split("```", 1)
    rendered = json.dumps(disposition, ensure_ascii=True, indent=2)
    return f"{heading}## Intuitiveness / Non-Impairment Disposition\n\n```json\n{rendered}\n```{suffix}"


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


def _insert_authorization(
    root: Path,
    authorization_id: str,
    included_work_item_ids: list[str] | None,
) -> None:
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        db.insert_project_authorization(
            PROJECT_ID,
            f"{authorization_id} test authorization",
            DELIB_ID,
            "Bounded authorization for proposal selection tests.",
            "test",
            "seed authorization candidate",
            id=authorization_id,
            included_work_item_ids=included_work_item_ids,
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


def _with_test_author_metadata(content: str) -> str:
    metadata = (
        "author_identity: prime-builder/codex/A\n"
        "author_harness_id: A\n"
        "author_session_context_id: wi5420-test-session\n"
        "author_model: OpenAI Codex\n"
        "author_model_version: test\n"
        "author_model_configuration: platform test\n\n"
    )
    return content.replace("NEW\n\n", f"NEW\n\n{metadata}", 1)


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
    assert "Project Authorization Candidates:" in content
    assert f'"project_authorization_id":"{AUTH_ID}"' in content
    assert '"coverage":"exact_singleton"' in content
    assert "Project Authorization Candidates:" in result.output
    assert f"Project: {PROJECT_ID}" in content
    assert f"Work Item: {WI_ID}" in content
    assert 'target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py"]' in content
    assert "## Specification-Derived Verification Plan" in content
    assert "## Intuitiveness / Non-Impairment Disposition" in content
    disposition = _nonimpairment_disposition(content)
    assert set(proposal_filing.NONIMPAIRMENT_REQUIRED_FIELDS) <= set(disposition)
    assert disposition["schema_version"] == 1
    assert disposition["applicability"] == "applicable"
    assert content.index("## Intuitiveness / Non-Impairment Disposition") < content.index(
        "## Specification-Derived Verification Plan"
    )
    assert "## Cross-Harness Disposition" not in content
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


@pytest.mark.parametrize(
    "authorization_rows",
    [
        [
            ("PAUTH-FALLBACK-TEST", None),
            ("PAUTH-EXPLICIT-TEST", [WI_ID, "WI-4568"]),
            ("PAUTH-EXACT-TEST", [WI_ID]),
        ],
        [
            ("PAUTH-EXACT-TEST", [WI_ID]),
            ("PAUTH-EXPLICIT-TEST", [WI_ID, "WI-4568"]),
            ("PAUTH-FALLBACK-TEST", None),
        ],
    ],
)
def test_file_implementation_proposal_selects_exact_authorization_independent_of_insertion_order(
    tmp_path: Path,
    monkeypatch,
    authorization_rows: list[tuple[str, list[str] | None]],
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    for authorization_id, included_work_item_ids in authorization_rows:
        _insert_authorization(tmp_path, authorization_id, included_work_item_ids)
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
        "--dry-run",
        "--json",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["project_authorization_id"] == "PAUTH-EXACT-TEST"
    assert [
        (candidate["project_authorization_id"], candidate["coverage"], candidate["specificity_rank"])
        for candidate in payload["project_authorization_candidates"]
    ] == [
        ("PAUTH-EXACT-TEST", "exact_singleton", [0, 1]),
        ("PAUTH-EXPLICIT-TEST", "explicit_list", [1, 2]),
        ("PAUTH-FALLBACK-TEST", "project_membership_fallback", [2, 0]),
    ]
    assert [candidate["selected"] for candidate in payload["project_authorization_candidates"]] == [
        True,
        False,
        False,
    ]


def test_file_implementation_proposal_prefers_smaller_explicit_authorization(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    _insert_authorization(tmp_path, "PAUTH-EXPLICIT-THREE-TEST", [WI_ID, "WI-4568", "WI-4569"])
    _insert_authorization(tmp_path, "PAUTH-EXPLICIT-TWO-TEST", [WI_ID, "WI-4568"])
    _insert_authorization(tmp_path, "PAUTH-FALLBACK-TEST", None)
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
        "--dry-run",
        "--json",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["project_authorization_id"] == "PAUTH-EXPLICIT-TWO-TEST"
    assert payload["project_authorization_candidates"][0] == {
        "coverage": "explicit_list",
        "included_work_item_count": 2,
        "project_authorization_id": "PAUTH-EXPLICIT-TWO-TEST",
        "selected": True,
        "specificity_rank": [1, 2],
    }


def test_file_implementation_proposal_fails_before_publication_on_equal_rank_ambiguity(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    _insert_authorization(tmp_path, "PAUTH-EXACT-A-TEST", [WI_ID])
    _insert_authorization(tmp_path, "PAUTH-EXACT-B-TEST", [WI_ID])
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

    assert result.exit_code == 1
    assert "Ambiguous active project authorizations cover WI-4567 at specificity rank [0, 1]" in result.output
    assert "PAUTH-EXACT-A-TEST, PAUTH-EXACT-B-TEST" in result.output
    assert writer.calls == []
    assert preflights == []
    assert not (tmp_path / "bridge").exists()


def test_file_implementation_proposal_dry_run_text_discloses_candidate_ranks(
    tmp_path: Path,
    monkeypatch,
) -> None:
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
        "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py",
        "--add-spec",
        SPEC_ID,
        "--dry-run",
    )

    assert result.exit_code == 0, result.output
    assert f"Project Authorization: {AUTH_ID}" in result.output
    assert "Project Authorization Candidates:" in result.output
    assert '"specificity_rank":[0,1]' in result.output
    assert '"selected":true' in result.output


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


def test_file_implementation_proposal_renders_parity_dispositions_and_passes_real_audit(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path)
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    try:
        result = proposal_filing.file_implementation_proposal(
            db,
            tmp_path,
            proposal_filing.FilingRequest(
                wi_id=WI_ID,
                slug="gtkb-wi4567-parity-test",
                target_paths=(".claude/skills/example/SKILL.md",),
                add_specs=(SPEC_ID,),
                cross_harness_dispositions=(
                    "Claude=Canonical managed-skill source.",
                    "Codex=Generated adapter with equivalent behavior.",
                ),
                dry_run=True,
            ),
            run_candidate_preflights=False,
            run_live_preflights=False,
        )
    finally:
        db.close()

    assert (
        "## Cross-Harness Disposition\n\n"
        "- **Claude**: Canonical managed-skill source.\n"
        "- **Codex**: Generated adapter with equivalent behavior.\n"
    ) in result.content
    assert result.content.count("## Intuitiveness / Non-Impairment Disposition") == 1
    assert (
        result.content.index("## Cross-Harness Disposition")
        < result.content.index("## Intuitiveness / Non-Impairment Disposition")
        < result.content.index("## Specification-Derived Verification Plan")
    )

    writer = proposal_filing._load_bridge_writer(tmp_path)
    content = writer.normalize_bridge_envelope_head(_with_test_author_metadata(result.content))
    audit = writer._run_bridge_compliance_audit(
        file_path=tmp_path / "bridge" / "gtkb-wi4567-parity-test-001.md",
        content=content,
        project_root=tmp_path,
    )
    assert audit["decision"] == "pass"


@pytest.mark.parametrize("invalid_value", [None, "", "TODO"])
def test_file_implementation_proposal_nonimpairment_remains_fail_closed(
    tmp_path: Path,
    invalid_value: str | None,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path)
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    try:
        result = proposal_filing.file_implementation_proposal(
            db,
            tmp_path,
            proposal_filing.FilingRequest(
                wi_id=WI_ID,
                slug="gtkb-wi4567-parity-test",
                target_paths=(".claude/skills/example/SKILL.md",),
                add_specs=(SPEC_ID,),
                cross_harness_dispositions=(
                    "Claude=Canonical managed-skill source.",
                    "Codex=Generated adapter with equivalent behavior.",
                ),
                dry_run=True,
            ),
            run_candidate_preflights=False,
            run_live_preflights=False,
        )
    finally:
        db.close()

    disposition = _nonimpairment_disposition(result.content)
    if invalid_value is None:
        disposition.pop("before_behavior")
    else:
        disposition["before_behavior"] = invalid_value
    invalid_content = _replace_nonimpairment_disposition(result.content, disposition)
    writer = proposal_filing._load_bridge_writer(tmp_path)
    normalized = writer.normalize_bridge_envelope_head(_with_test_author_metadata(invalid_content))
    with pytest.raises(writer.BridgeComplianceError, match="Intuitiveness/Non-Impairment Disposition"):
        writer._run_bridge_compliance_audit(
            file_path=tmp_path / "bridge" / "gtkb-wi4567-parity-test-001.md",
            content=normalized,
            project_root=tmp_path,
        )


def test_file_implementation_proposal_without_parity_disposition_remains_denied(tmp_path: Path) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path)
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    try:
        result = proposal_filing.file_implementation_proposal(
            db,
            tmp_path,
            proposal_filing.FilingRequest(
                wi_id=WI_ID,
                slug="gtkb-wi4567-parity-test",
                target_paths=(".claude/skills/example/SKILL.md",),
                add_specs=(SPEC_ID,),
                dry_run=True,
            ),
            run_candidate_preflights=False,
            run_live_preflights=False,
        )
    finally:
        db.close()

    writer = proposal_filing._load_bridge_writer(tmp_path)
    content = writer.normalize_bridge_envelope_head(_with_test_author_metadata(result.content))
    with pytest.raises(writer.BridgeComplianceError, match="Cross-Harness Disposition"):
        writer._run_bridge_compliance_audit(
            file_path=tmp_path / "bridge" / "gtkb-wi4567-parity-test-001.md",
            content=content,
            project_root=tmp_path,
        )


@pytest.mark.parametrize(
    "entry",
    [
        "missing-equals",
        "=disposition",
        "Claude=",
        "Claude=first\nCodex=second",
    ],
)
def test_file_implementation_proposal_rejects_malformed_parity_disposition(
    tmp_path: Path,
    monkeypatch,
    entry: str,
) -> None:
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
        ".claude/skills/example/SKILL.md",
        "--add-spec",
        SPEC_ID,
        "--cross-harness-disposition",
        entry,
    )

    assert result.exit_code == 1
    assert "--cross-harness-disposition" in result.output
    assert not (tmp_path / "bridge").exists()


def test_file_implementation_proposal_rejects_duplicate_parity_disposition_key(
    tmp_path: Path,
    monkeypatch,
) -> None:
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
        ".claude/skills/example/SKILL.md",
        "--add-spec",
        SPEC_ID,
        "--cross-harness-disposition",
        "Claude=first",
        "--cross-harness-disposition",
        "claude=second",
    )

    assert result.exit_code == 1
    assert "Duplicate --cross-harness-disposition key: claude" in result.output
    assert not (tmp_path / "bridge").exists()


def test_file_implementation_proposal_help_resolves() -> None:
    result = CliRunner().invoke(main, ["bridge", "file-implementation-proposal", "--help"])
    assert result.exit_code == 0, result.output
    assert "File a dispatchable NEW implementation proposal" in result.output
    assert "--cross-harness-disposition" in result.output
