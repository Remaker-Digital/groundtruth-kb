"""Filing uses existing project state, never authorization records or state creation.

Retired envelope ranking/expiry tests are replaced by project-field and membership
tests. All publication and denial probes use temporary roots, never live claims.
"""

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
from groundtruth_kb.session.attestation import bind_exact_init

# Eagerly disable ChromaDB in unit test runtime to avoid hangs during semantic search queries
groundtruth_kb.db.HAS_CHROMADB = False

WI_ID = "WI-4567"
PROJECT_ID = "PROJECT-GTKB-DETERMINISTIC-SERVICES-TEST"
SPEC_ID = "SPEC-WI-4567-TEST"
#: Session identifiers this module authors as, mapped to their binding role
#: (WI-6095). See the sibling fixture in ``test_gtkb_bridge_writer.py``.
_AUTHORED_SESSIONS = {
    "wi5420-test-session": "pb",
    "wi5458-test-session": "pb",
    "test-12341": "pb",
}


@pytest.fixture(autouse=True)
def _bind_authored_sessions(tmp_path: Path) -> None:
    """Give every session this module authors as a real exact-init binding.

    Same defect and same repair as the writer module: these tests wrote as bare
    placeholder identifiers that no session-init binding backed, and the filing
    path now resolves author provenance through that binding per
    ``DCL-INIT-BOUND-SESSION-IDENTITY-001``.

    This runs before ``_seed_db``; both create the database if absent, so the
    ordering is harmless.
    """
    for session_id, role in _AUTHORED_SESSIONS.items():
        bind_exact_init(
            tmp_path / "groundtruth.db",
            native_context_id=session_id,
            init_command=f"::init gtkb {role}",
        )


@pytest.fixture(autouse=True)
def _trusted_authorization_runtime(monkeypatch) -> None:
    monkeypatch.setattr(
        proposal_filing,
        "_resolve_actor_context",
        lambda _project_root: {
            "session_context_id": "wi5458-test-session",
            "role": "prime-builder",
            **{key: "test-author" for key in proposal_filing.AUTHOR_METADATA_FIELDS},
            "author_identity": "prime-builder/codex/A",
            "author_harness_id": "A",
            "author_session_context_id": "wi5458-test-session",
        },
    )


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
        db.insert_project("Deterministic Services", "test", "seed project", id=PROJECT_ID)
        db.insert_test(
            "TEST-4567", "Filing test", SPEC_ID, "unit", "PASS", "test", "seed", test_file="tests/test_filing.py"
        )
        db.insert_work_item(
            id=WI_ID,
            title="Bridge proposal filing service",
            description="One command files a gate-passing bridge implementation proposal.",
            origin="improvement",
            component="bridge-tooling",
            source_spec_id=SPEC_ID,
            source_test_id="TEST-4567",
            resolution_status="open",
            priority="P3",
            changed_by="test",
            change_reason="seed work item",
        )
        if membership:
            db.link_project_work_item(PROJECT_ID, WI_ID, "test", "seed membership")
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


def test_harness_surface_proposal_passes_without_peer_knowledge(tmp_path):
    _write_config(tmp_path)
    _seed_db(tmp_path)
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    try:
        result = proposal_filing.file_implementation_proposal(
            db,
            tmp_path,
            proposal_filing.FilingRequest(
                wi_id=WI_ID, slug="harness-change", target_paths=(".claude/skills/example/SKILL.md",), dry_run=True
            ),
            run_candidate_preflights=False,
            run_live_preflights=False,
        )
    finally:
        db.close()
    assert "Cross-Harness Disposition" not in result.content
    writer = proposal_filing._load_bridge_writer(tmp_path)
    audit = writer._run_bridge_compliance_audit(
        file_path=tmp_path / "bridge/harness-change-001.md", content=result.content, project_root=tmp_path
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


def test_file_implementation_proposal_help_resolves() -> None:
    result = CliRunner().invoke(main, ["bridge", "file-implementation-proposal", "--help"])
    assert result.exit_code == 0, result.output
    assert "File a dispatchable NEW implementation proposal" in result.output
    assert "--cross-harness-disposition" not in result.output
    assert "--project-authorization" not in result.output
    assert "--owner-decision" not in result.output
    assert "--create-missing-state" not in result.output


def _file(root, monkeypatch, *, dry_run=False, **overrides):
    writer, preflights = _install_fakes(monkeypatch)
    db = KnowledgeDB(db_path=root / "groundtruth.db")
    try:
        result = proposal_filing.file_implementation_proposal(
            db,
            root,
            proposal_filing.FilingRequest(
                **{
                    "wi_id": WI_ID,
                    "slug": "filing-test",
                    "target_paths": ("src/x.py",),
                    "add_specs": (SPEC_ID,),
                    "dry_run": dry_run,
                    **overrides,
                }
            ),
        )
    finally:
        db.close()
    return result, writer, preflights


@pytest.mark.parametrize("dry_run", [False, True])
def test_existing_authorized_project_files_without_carriers(tmp_path, monkeypatch, dry_run):
    _seed_db(tmp_path)
    result, writer, preflights = _file(tmp_path, monkeypatch, dry_run=dry_run)
    assert len(writer.calls) == (0 if dry_run else 1)
    assert len(preflights) == (2 if dry_run else 4)
    assert result.content.splitlines()[:3] == ["NEW", "::init gtkb lo", "::open build"]
    assert "recipient_role: loyal-opposition" in result.content
    assert 'test_artifact_targets: ["TEST-4567"]' in result.content
    assert f"Project: {PROJECT_ID}" in result.content
    for obsolete in ("PAUTH", "Project Authorization:", "Owner Decisions", "Prior Deliberations"):
        assert obsolete not in result.content
    assert not (tmp_path / ".gtkb-state").exists()


@pytest.mark.parametrize("value", ["not authorized", "", None, "active"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_only_authorized_project_value_permits_new(tmp_path, monkeypatch, value, dry_run):
    _seed_db(tmp_path)
    original = KnowledgeDB.get_project

    def read(db, project_id):
        return {**original(db, project_id), "authorization": value, "activation_status": "authorized"}

    monkeypatch.setattr(KnowledgeDB, "get_project", read)
    with pytest.raises(proposal_filing.ProposalFilingError, match="requires 'authorized'"):
        _file(tmp_path, monkeypatch, dry_run=dry_run)
    assert not (tmp_path / "bridge").exists()


@pytest.mark.parametrize("count", [0, 2])
@pytest.mark.parametrize("explicit", [None, PROJECT_ID])
def test_single_membership_cannot_be_bypassed(tmp_path, monkeypatch, count, explicit):
    _seed_db(tmp_path)
    monkeypatch.setattr(
        proposal_filing,
        "_active_memberships_for_work_item",
        lambda *a: [{"project_id": PROJECT_ID, "id": str(i)} for i in range(count)],
    )
    with pytest.raises(proposal_filing.ProposalFilingError, match="exactly one"):
        _file(tmp_path, monkeypatch, project_id=explicit)
    assert not (tmp_path / "bridge").exists()


def test_explicit_project_is_an_assertion_not_a_membership_override(tmp_path, monkeypatch):
    _seed_db(tmp_path)
    with pytest.raises(proposal_filing.ProposalFilingError, match="belongs to"):
        _file(tmp_path, monkeypatch, project_id="PROJECT-OTHER")


@pytest.mark.parametrize("test", [None, {"test_file": ""}])
def test_missing_executable_test_denies_before_publication(tmp_path, monkeypatch, test):
    _seed_db(tmp_path)
    monkeypatch.setattr(KnowledgeDB, "get_test", lambda *a: test)
    with pytest.raises(proposal_filing.ProposalFilingError, match="linked executable test"):
        _file(tmp_path, monkeypatch)
    assert not (tmp_path / "bridge").exists()


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("surface", ["project", "membership", "work_item", "test"])
def test_changes_during_preflight_prevent_publication(tmp_path, monkeypatch, dry_run, surface):
    _seed_db(tmp_path)
    original = proposal_filing._resolve_project_state
    calls = 0

    def read(*args, **kwargs):
        nonlocal calls
        state = original(*args, **kwargs)
        calls += 1
        if calls == 2:
            state.inputs[surface]["version"] = 999
        return state

    monkeypatch.setattr(proposal_filing, "_resolve_project_state", read)
    with pytest.raises(proposal_filing.ProposalFilingError, match="changed before filing"):
        _file(tmp_path, monkeypatch, dry_run=dry_run)
    assert not (tmp_path / "bridge").exists()


@pytest.mark.parametrize("dry_run", [False, True])
def test_preflight_failure_never_publishes(tmp_path, monkeypatch, dry_run):
    _seed_db(tmp_path)

    def refuse(*args):
        raise proposal_filing.ProposalFilingError("candidate rejected")

    monkeypatch.setattr(proposal_filing, "_run_candidate_preflights", refuse)
    with pytest.raises(proposal_filing.ProposalFilingError, match="candidate rejected"):
        _file(tmp_path, monkeypatch, dry_run=dry_run)
    assert not (tmp_path / "bridge").exists()


def test_existing_chain_is_not_overwritten(tmp_path, monkeypatch):
    _seed_db(tmp_path)
    bridge = tmp_path / "bridge"
    bridge.mkdir()
    head = bridge / "filing-test-001.md"
    head.write_text("NEW\n", encoding="utf-8")
    with pytest.raises(proposal_filing.ProposalFilingError, match="already exists"):
        _file(tmp_path, monkeypatch)
    assert head.read_text() == "NEW\n"


@pytest.mark.parametrize("target", ["../escape.py", "../../escape.py"])
def test_target_escape_denied(tmp_path, monkeypatch, target):
    _seed_db(tmp_path)
    with pytest.raises(proposal_filing.ProposalFilingError, match="outside the project root"):
        _file(tmp_path, monkeypatch, target_paths=(target,))


@pytest.mark.parametrize("slug", ["../escape", "UPPER", "foo/bar", "foo\nbar"])
def test_invalid_slug_denied(tmp_path, monkeypatch, slug):
    _seed_db(tmp_path)
    with pytest.raises(proposal_filing.ProposalFilingError, match="kebab-case"):
        _file(tmp_path, monkeypatch, slug=slug)


@pytest.mark.parametrize(
    "target,expected",
    [("src/x.py", False), ("groundtruth.db", True), ("nested/groundtruth.db", True), ("nested\\groundtruth.db", True)],
)
def test_database_scope_comes_from_targets(target, expected):
    assert proposal_filing._derive_kb_mutation_in_scope((target,)) is expected


def test_cli_json_has_only_filing_results(tmp_path, monkeypatch):
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
        "cli-test",
        "--target-path",
        "src/x.py",
        "--dry-run",
        "--json",
    )
    assert result.exit_code == 0, result.output
    assert set(json.loads(result.output)) == {"bridge_path", "project_id", "preflights"}
    assert not (tmp_path / "bridge").exists()


@pytest.mark.parametrize("status", ["resolved", "retired", "wont_fix", "not_a_defect", "verified"])
def test_completed_work_item_cannot_start_new(tmp_path, monkeypatch, status):
    _seed_db(tmp_path)
    original = proposal_filing.get_work_item_or_raise
    monkeypatch.setattr(
        proposal_filing,
        "get_work_item_or_raise",
        lambda *a: {
            **original(*a),
            "resolution_status": status,
        },
    )
    with pytest.raises(proposal_filing.ProposalFilingError, match="cannot start NEW"):
        _file(tmp_path, monkeypatch)


@pytest.mark.parametrize("output", ["", '{"hookSpecificOutput":{"permissionDecision":"allow"}}'])
def test_crashed_gate_cannot_approve(tmp_path, monkeypatch, output):
    from types import SimpleNamespace

    script = proposal_filing._compliance_gate_script(tmp_path)
    script.parent.mkdir(parents=True)
    script.touch()
    monkeypatch.setattr(
        proposal_filing.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(
            returncode=1,
            stdout=output,
            stderr="crashed",
        ),
    )
    with pytest.raises(proposal_filing.ProposalFilingError, match="failed with exit 1"):
        proposal_filing._run_compliance_gate(tmp_path, "test", "NEW\n")
