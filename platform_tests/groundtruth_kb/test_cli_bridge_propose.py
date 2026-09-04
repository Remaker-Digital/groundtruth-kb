"""Platform tests for ``gt bridge file-implementation-proposal``."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
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
ALLOWED_MUTATION_CLASSES = [
    "bridge",
    "configuration",
    "governance_evidence",
    "metadata",
    "source",
    "test",
]


@pytest.fixture(autouse=True)
def _trusted_authorization_runtime(monkeypatch) -> None:
    canonical_load_operation_taxonomy = proposal_filing.load_operation_taxonomy
    monkeypatch.setattr(
        proposal_filing,
        "load_operation_taxonomy",
        lambda _project_root=None: canonical_load_operation_taxonomy(),
    )
    monkeypatch.setattr(
        proposal_filing,
        "_resolve_actor_context",
        lambda _project_root: {
            "session_context_id": "wi5458-test-session",
            "role": "prime-builder",
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
        db.insert_deliberation(
            id=DELIB_ID,
            source_type="owner_conversation",
            outcome="owner_decision",
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
    finally:
        db.close()


def _insert_authorization(
    root: Path,
    authorization_id: str,
    included_work_item_ids: list[str] | None,
    **kwargs: Any,
) -> None:
    """WI-7657: no-op. The record this seeded no longer exists.

    The call sites are left in place so the surrounding proposal-filing tests
    keep their shape, but there is nothing to seed: authorization is a field on
    the project row and the ``project_authorizations`` relation is gone.

    The tests that call this assert denial behaviour from a proposal-filing
    gate whose subject is retired. They are expected to fail until
    ``groundtruth_kb/bridge/proposal_filing.py`` is repointed, which is outside
    this work item's ``target_paths``. Stubbing the helper rather than deleting
    the calls keeps that gap visible at the call sites instead of erasing it.
    """


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
    assert [item["name"] for item in preflights] == [
        "applicability",
        "adr_dcl",
        "applicability",
        "adr_dcl",
    ]
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
    assert "No current project authorization covers" in result.output
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
        (
            candidate["project_authorization_id"],
            candidate["coverage"],
            candidate["specificity_rank"],
        )
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
    selected = payload["project_authorization_candidates"][0]
    assert selected["coverage"] == "explicit_list"
    assert selected["included_work_item_count"] == 2
    assert selected["project_authorization_id"] == "PAUTH-EXPLICIT-TWO-TEST"
    assert selected["selected"] is True
    assert selected["specificity_rank"] == [1, 2]


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


def test_file_implementation_proposal_rejects_source_create_missing_without_side_effects(
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

    assert result.exit_code == 1
    assert "target_mutation_class_not_allowed" in result.output
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")
    try:
        memberships = db.list_project_work_items(PROJECT_ID)
        authorizations = db.list_project_authorizations(PROJECT_ID, status="active")
    finally:
        db.close()
    assert memberships == []
    covering = [auth for auth in authorizations if WI_ID in (auth.get("included_work_item_ids_parsed") or [])]
    assert covering == []
    assert not (tmp_path / "bridge").exists()


def test_file_implementation_proposal_can_create_bridge_state_with_owner_decision(
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
        "bridge/gtkb-wi4567-test-001.md",
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
    assert len(covering) == 1
    assert covering[0]["allowed_mutation_classes_parsed"] == ["bridge", "metadata"]
    assert (tmp_path / "bridge" / "gtkb-wi4567-test-001.md").is_file()


@pytest.mark.parametrize(
    ("membership", "included", "excluded", "expected_code"),
    [
        (False, [WI_ID], [], None),
        (True, None, [], None),
        (False, None, [], "no_current_covering_authorization"),
        (True, ["WI-OTHER"], [], "no_current_covering_authorization"),
        (True, [WI_ID], [WI_ID], "work_item_excluded"),
    ],
)
def test_file_implementation_proposal_restrictive_work_item_coverage(
    tmp_path: Path,
    monkeypatch,
    membership: bool,
    included: list[str] | None,
    excluded: list[str],
    expected_code: str | None,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, membership=membership, authorization=False)
    _insert_authorization(
        tmp_path,
        "PAUTH-COVERAGE-TEST",
        included,
        excluded_work_item_ids=excluded,
    )
    writer, preflights = _install_fakes(monkeypatch)

    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--project",
        PROJECT_ID,
        "--slug",
        "gtkb-wi4567-coverage-test",
        "--target-path",
        "scripts/coverage_test.py",
        "--add-spec",
        SPEC_ID,
        "--dry-run",
        "--json",
    )

    if expected_code is None:
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["authorization_decision"]["allowed"] is True
        assert payload["project_authorization_id"] == "PAUTH-COVERAGE-TEST"
    else:
        assert result.exit_code == 1
        payload = json.loads(result.output)
        assert payload["authorization_decision"]["reason_code"] == expected_code
        assert writer.calls == []
        assert preflights == []


@pytest.mark.parametrize(
    ("membership", "included", "excluded", "expected_code"),
    [
        (False, [WI_ID], [], None),
        (True, ["WI-OTHER"], [], "no_current_covering_authorization"),
        (True, [], [], None),
        (False, [], [], "no_current_covering_authorization"),
        (True, [WI_ID], [WI_ID], "work_item_excluded"),
    ],
)
def test_file_implementation_proposal_explicit_selector_restrictive_work_item_coverage(
    tmp_path: Path,
    monkeypatch,
    membership: bool,
    included: list[str],
    excluded: list[str],
    expected_code: str | None,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, membership=membership, authorization=False)
    authorization_id = "PAUTH-EXPLICIT-COVERAGE-TEST"
    _insert_authorization(
        tmp_path,
        authorization_id,
        included,
        excluded_work_item_ids=excluded,
    )
    writer, preflights = _install_fakes(monkeypatch)

    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--project",
        PROJECT_ID,
        "--slug",
        "gtkb-wi4567-explicit-coverage-test",
        "--target-path",
        "scripts/explicit_coverage_test.py",
        "--add-spec",
        SPEC_ID,
        "--project-authorization",
        authorization_id,
        "--dry-run",
        "--json",
    )

    payload = json.loads(result.output)
    decision = payload["authorization_decision"]
    assert decision["selector_mode"] == "explicit"
    assert decision["requested_project_authorization_id"] == authorization_id
    assert decision["decision_id"].startswith("sha256:")
    assert writer.calls == []
    if expected_code is None:
        assert result.exit_code == 0, result.output
        assert decision["allowed"] is True
        assert payload["project_authorization_id"] == authorization_id
    else:
        assert result.exit_code == 1
        assert decision["reason_code"] == expected_code
        assert preflights == []


def test_file_implementation_proposal_explicit_selector_resolves_equal_best_only(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    _insert_authorization(tmp_path, "PAUTH-EXACT-A-TEST", [WI_ID])
    _insert_authorization(tmp_path, "PAUTH-EXACT-B-TEST", [WI_ID])
    _insert_authorization(tmp_path, "PAUTH-BROAD-TEST", None)
    _install_fakes(monkeypatch)

    allowed = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-selector-test",
        "--target-path",
        "scripts/selector_test.py",
        "--add-spec",
        SPEC_ID,
        "--project-authorization",
        "PAUTH-EXACT-B-TEST",
        "--dry-run",
        "--json",
    )
    assert allowed.exit_code == 0, allowed.output
    allowed_payload = json.loads(allowed.output)
    assert allowed_payload["authorization_decision"]["selector_mode"] == "explicit"
    assert allowed_payload["project_authorization_id"] == "PAUTH-EXACT-B-TEST"

    denied = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-selector-test-two",
        "--target-path",
        "scripts/selector_test.py",
        "--add-spec",
        SPEC_ID,
        "--project-authorization",
        "PAUTH-BROAD-TEST",
        "--dry-run",
        "--json",
    )
    assert denied.exit_code == 1
    denied_payload = json.loads(denied.output)
    assert denied_payload["authorization_decision"]["reason_code"] == (
        "selected_authorization_not_best_current_covering"
    )


@pytest.mark.parametrize(
    ("expires_at", "expected_code"),
    [
        ("2099-01-01T00:00:00Z", None),
        ("2099-01-01T01:00:00+01:00", None),
        ("2099-01-01T00:00:00", "malformed_authorization_expiry"),
        ("not-a-date", "malformed_authorization_expiry"),
        ("2000-01-01T00:00:00Z", "best_rank_cohort_stale"),
    ],
)
def test_file_implementation_proposal_authorization_expiry_is_fail_closed(
    tmp_path: Path,
    monkeypatch,
    expires_at: str,
    expected_code: str | None,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    _insert_authorization(tmp_path, "PAUTH-EXPIRY-TEST", [WI_ID], expires_at=expires_at)
    _install_fakes(monkeypatch)
    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-expiry-test",
        "--target-path",
        "scripts/expiry_test.py",
        "--add-spec",
        SPEC_ID,
        "--dry-run",
        "--json",
    )
    payload = json.loads(result.output)
    if expected_code is None:
        assert result.exit_code == 0, result.output
        assert payload["authorization_decision"]["authorization"]["normalized_expiry"] == ("2099-01-01T00:00:00Z")
    else:
        assert result.exit_code == 1
        assert payload["authorization_decision"]["reason_code"] == expected_code


@pytest.mark.parametrize(
    "stale_fields",
    [
        {"status": "superseded"},
        {"superseded_by": ["PAUTH-SUCCESSOR-TEST"]},
    ],
)
def test_file_implementation_proposal_does_not_fallback_from_stale_best_cohort(
    tmp_path: Path,
    monkeypatch,
    stale_fields: dict[str, Any],
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    _insert_authorization(tmp_path, "PAUTH-EXACT-STALE-TEST", [WI_ID], **stale_fields)
    _insert_authorization(tmp_path, "PAUTH-BROAD-CURRENT-TEST", None)
    _install_fakes(monkeypatch)
    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-stale-test",
        "--target-path",
        "scripts/stale_test.py",
        "--add-spec",
        SPEC_ID,
        "--dry-run",
        "--json",
    )
    assert result.exit_code == 1
    payload = json.loads(result.output)
    assert payload["authorization_decision"]["reason_code"] == "best_rank_cohort_stale"


def test_file_implementation_proposal_spec_exclusion_denies(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    _insert_authorization(
        tmp_path,
        "PAUTH-EXCLUDED-SPEC-TEST",
        [WI_ID],
        excluded_spec_ids=[SPEC_ID],
    )
    _install_fakes(monkeypatch)
    excluded = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-excluded-spec-test",
        "--target-path",
        "scripts/spec_test.py",
        "--add-spec",
        SPEC_ID,
        "--dry-run",
        "--json",
    )
    assert excluded.exit_code == 1
    assert json.loads(excluded.output)["authorization_decision"]["reason_code"] == ("linked_specification_excluded")


def test_file_implementation_proposal_forbidden_operation_denies(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    _insert_authorization(
        tmp_path,
        "PAUTH-FORBIDDEN-OPERATION-TEST",
        [WI_ID],
        forbidden_operations=["bridge_proposal_filing"],
    )
    _install_fakes(monkeypatch)
    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-forbidden-operation-test",
        "--target-path",
        "scripts/operation_test.py",
        "--add-spec",
        SPEC_ID,
        "--dry-run",
        "--json",
    )
    assert result.exit_code == 1
    assert json.loads(result.output)["authorization_decision"]["reason_code"] == "forbidden_operation"


def test_file_implementation_proposal_create_missing_rolls_back_membership_on_pauth_failure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, membership=False, authorization=False)
    db = KnowledgeDB(db_path=tmp_path / "groundtruth.db")

    def fail_insert(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("injected PAUTH insert failure")

    monkeypatch.setattr(db, "insert_project_authorization", fail_insert)
    try:
        with pytest.raises(proposal_filing.ProposalFilingError) as error:
            proposal_filing.file_implementation_proposal(
                db,
                tmp_path,
                proposal_filing.FilingRequest(
                    wi_id=WI_ID,
                    slug="gtkb-wi4567-rollback-test",
                    project_id=PROJECT_ID,
                    owner_decision=DELIB_ID,
                    create_missing_state=True,
                    target_paths=("bridge/gtkb-wi4567-rollback-test-001.md",),
                    add_specs=(SPEC_ID,),
                ),
                run_candidate_preflights=False,
                run_live_preflights=False,
            )
        assert error.value.decision["reason_code"] == "authorization_state_creation_failed"
        assert db.list_project_work_items(PROJECT_ID) == []
        assert db.list_project_authorizations(PROJECT_ID, include_terminal=True) == []
        assert not (tmp_path / "bridge").exists()
    finally:
        db.close()


def test_file_implementation_proposal_revalidates_after_candidate_preflight(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path)
    writer = _FakeWriter()
    changed = False

    def fake_preflight(project_root: Path, *, name: str, content_file=None, bridge_id=None):
        nonlocal changed
        if not changed:
            changed = True
            drift_db = KnowledgeDB(db_path=project_root / "groundtruth.db")
            try:
                drift_db.insert_project(
                    "Deterministic Services",
                    "test",
                    "inject project lifecycle drift",
                    id=PROJECT_ID,
                    status="retired",
                )
            finally:
                drift_db.close()
        return proposal_filing.PreflightResult(name=name, returncode=0, stdout="PASS", stderr="")

    monkeypatch.setattr(proposal_filing, "_load_bridge_writer", lambda _root: writer)
    monkeypatch.setattr(proposal_filing, "_run_preflight_command", fake_preflight)
    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-preflight-drift-test",
        "--target-path",
        "scripts/preflight_drift_test.py",
        "--add-spec",
        SPEC_ID,
        "--json",
    )
    assert result.exit_code == 1
    assert json.loads(result.output)["authorization_decision"]["reason_code"] == "project_not_active"
    assert writer.calls == []
    assert not (tmp_path / "bridge").exists()


def test_file_implementation_proposal_denies_expiry_during_candidate_preflight(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _write_config(tmp_path)
    _seed_db(tmp_path, authorization=False)
    initial_time = datetime(2026, 7, 29, 20, 0, tzinfo=UTC)
    _insert_authorization(
        tmp_path,
        "PAUTH-PREFLIGHT-EXPIRY-TEST",
        [WI_ID],
        expires_at=(initial_time + timedelta(seconds=30)).isoformat(),
    )
    writer, preflights = _install_fakes(monkeypatch)

    class _AdvancingDateTime(datetime):
        calls = iter((initial_time, initial_time, initial_time + timedelta(seconds=60)))

        @classmethod
        def now(cls, tz=None):
            value = next(cls.calls)
            return value if tz is None else value.astimezone(tz)

    monkeypatch.setattr(proposal_filing, "datetime", _AdvancingDateTime)
    result = _invoke(
        tmp_path,
        "bridge",
        "file-implementation-proposal",
        "--wi",
        WI_ID,
        "--slug",
        "gtkb-wi4567-preflight-expiry-test",
        "--target-path",
        "scripts/preflight_expiry_test.py",
        "--add-spec",
        SPEC_ID,
        "--json",
    )

    assert result.exit_code == 1
    assert result.output, repr(result.exception)
    payload = json.loads(result.output)
    assert payload["authorization_decision"]["reason_code"] == "best_rank_cohort_stale"
    assert payload["authorization_decision"]["decision_time"] == "2026-07-29T20:01:00Z"
    assert writer.calls == []
    assert [item["name"] for item in preflights] == ["applicability", "adr_dcl"]
    assert not (tmp_path / "bridge").exists()


def test_file_implementation_proposal_decision_identity_matches_content_and_result(
    tmp_path: Path,
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
                slug="gtkb-wi4567-decision-evidence-test",
                target_paths=("scripts/decision_evidence_test.py",),
                add_specs=(SPEC_ID,),
                dry_run=True,
            ),
            run_candidate_preflights=False,
            run_live_preflights=False,
        )
    finally:
        db.close()

    line = next(item for item in result.content.splitlines() if item.startswith("Project Authorization Decision: "))
    embedded = json.loads(line.split(": ", 1)[1])
    assert embedded == result.authorization_decision
    assert embedded["decision_id"].startswith("sha256:")
    assert embedded["actor"] == {
        "session_context_id": "wi5458-test-session",
        "role": "prime-builder",
    }
    assert embedded["invalidation_inputs"]["planned_bridge_status"] == "NEW"
    assert embedded["invalidation_inputs"]["planned_bridge_version"] == 1


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


def test_file_implementation_proposal_renders_parity_dispositions_and_passes_real_audit(
    tmp_path: Path,
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


def test_file_implementation_proposal_without_parity_disposition_remains_denied(
    tmp_path: Path,
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


# ---------------------------------------------------------------------------
# TEST-12341 (WI-7326): the generator must emit an artifact the real gate accepts.
#
# Authority: GOV-FILE-BRIDGE-AUTHORITY-001, ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001,
# DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001, GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001.
# GO conditions 2 and 4 of bridge/gtkb-wi7326-bridge-filing-path-repair-002.md require
# the kb-flag cross-check to fail closed and the end-to-end assertion to invoke the REAL
# baseline gate on generated content rather than a fixture approximation.
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
GATE_PROBE_SLUG = "gtkb-test12341-gate-probe"


def _minimal_proposal_body(*, slug: str, simplification: bool = True) -> str:
    """A body carrying every element the gate checks, so one element can be removed."""
    simplification_block = (
        "## Simplification Accounting\n\nConcepts minus one; no artifact added.\n\n" if simplification else ""
    )
    return (
        f"NEW\n{proposal_filing.PROPOSAL_RECIPIENT_INIT_MARKER}\n{proposal_filing.PROPOSAL_ACTIVITY_MARKER}\n\n"
        f"# Implementation Proposal - TEST-12341 probe\n\n"
        f"bridge_kind: prime_proposal\nDocument: {slug}\nVersion: 001\nDate: 2026-08-27 UTC\n\n"
        "author_identity: prime-builder/claude\nauthor_harness_id: B\n"
        "author_session_context_id: test-12341\nauthor_model: test-model\n"
        "author_model_version: test-model\nauthor_model_configuration: test\n\n"
        "Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-FILING-PATH-REPAIR-"
        "PROJECT-GTKB-BRIDGE-FILING-PATH-REPAIR-EXECUTION-AUTHORITY\n"
        "Project: PROJECT-GTKB-BRIDGE-FILING-PATH-REPAIR\nWork Item: WI-7326\n\n"
        'target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py"]\n\n'
        "## Requirement Sufficiency\n\nExisting requirements sufficient.\n\n"
        "## Specification Links\n\n- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority.\n"
        "- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete spec links.\n"
        "- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived verification.\n\n"
        "## Prior Deliberations\n\n_No prior deliberations: TEST-12341 probe body._\n\n"
        "## Owner Decisions / Input\n\n- `DELIB-20260827051707` - owner directive.\n\n"
        f"{simplification_block}"
        "## Proposed Scope\n\n- Probe body.\n\n"
        "## Specification-Derived Verification Plan\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001` - `python -m pytest` probe.\n\n"
        "## Acceptance Criteria\n\n- Probe.\n\n## Recommended Commit Type\n\n`test`\n"
    )


def test_12341_head_envelope_constants_name_the_recipient_role_and_activity() -> None:
    """Defect 2: a Prime-authored NEW proposal is dispatched to Loyal Opposition."""
    assert proposal_filing.PROPOSAL_RECIPIENT_INIT_MARKER == "::init gtkb lo"
    assert proposal_filing.PROPOSAL_ACTIVITY_MARKER == "::open build"


def test_12341_author_metadata_fields_match_the_audit_directive() -> None:
    """Defect 3: all six audit-metadata lines must be emitted."""
    assert proposal_filing.AUTHOR_METADATA_FIELDS == (
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "author_model_version",
        "author_model_configuration",
    )


def test_12341_kb_mutation_flag_is_derived_from_targets() -> None:
    """Defect 4: derived, not hard-coded false."""
    decision = {"classified_targets": [{"path": "groundtruth.db", "mutation_class": "metadata"}]}
    assert proposal_filing._derive_kb_mutation_in_scope(("groundtruth.db",), decision) is True
    assert proposal_filing._derive_kb_mutation_in_scope(("src/x.py",), decision) is False


def test_12341_kb_mutation_flag_fails_closed_on_decision_disagreement() -> None:
    """GO condition 2: cross-check against the authorization decision, fail closed."""
    with pytest.raises(proposal_filing.ProposalFilingError, match="disagrees with the authorization decision"):
        proposal_filing._derive_kb_mutation_in_scope(("groundtruth.db",), {"classified_targets": []})


def test_12341_candidate_preflight_scratch_is_not_under_forbidden_state_dir() -> None:
    """Defect 6: scratch belongs in the in-root scratchpad, session-scoped."""
    source = Path(proposal_filing.__file__).read_text(encoding="utf-8")
    assert '".gtkb-state" / "proposal-filing-preflight"' not in source
    assert '"scratchpad" / _session_scratch_dirname() / "proposal-filing-preflight"' in source
    assert proposal_filing._session_scratch_dirname()


def test_12341_gate_script_resolves_to_the_canonical_baseline_not_a_projection() -> None:
    """GO condition 4: the real baseline gate, never a projection copy."""
    script = proposal_filing._compliance_gate_script(REPO_ROOT)
    assert script.parts[-3:] == (".harness-baseline-configuration", "hooks", "bridge-compliance-gate.py")
    assert script.is_file(), f"baseline gate missing at {script}"


def test_12341_missing_gate_is_reported_not_raised(tmp_path: Path) -> None:
    """Parity: where no baseline gate exists the writer is not gated either."""
    result = proposal_filing._run_compliance_gate(tmp_path, "any-slug", "NEW\n")
    assert result.name == "compliance_gate"
    assert result.stdout.startswith("not_evaluated")


def test_12341_real_baseline_gate_rejects_content_missing_simplification_accounting() -> None:
    """End-to-end against the REAL gate: the very defect that blocked WI-7311 filing."""
    import subprocess as _sp
    import sys as _sys

    claim = [
        _sys.executable,
        str(REPO_ROOT / "scripts" / "bridge_claim_cli.py"),
        "claim",
        GATE_PROBE_SLUG,
        "--ttl-seconds",
        "300",
    ]
    if _sp.run(claim, cwd=REPO_ROOT, capture_output=True, text=True).returncode != 0:
        pytest.skip("probe slug claimed by another session; gate probe not runnable here")
    try:
        with pytest.raises(proposal_filing.ProposalFilingError, match="Simplification Accounting"):
            proposal_filing._run_compliance_gate(
                REPO_ROOT, GATE_PROBE_SLUG, _minimal_proposal_body(slug=GATE_PROBE_SLUG, simplification=False)
            )
        passing = proposal_filing._run_compliance_gate(
            REPO_ROOT, GATE_PROBE_SLUG, _minimal_proposal_body(slug=GATE_PROBE_SLUG, simplification=True)
        )
        assert passing.name == "compliance_gate"
    finally:
        _sp.run(
            [_sys.executable, str(REPO_ROOT / "scripts" / "bridge_claim_cli.py"), "release", GATE_PROBE_SLUG],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )


def test_12341_dry_run_and_write_paths_share_one_gate_call_site() -> None:
    """Defect 5: one call site, evaluated before the dry-run return, so verdicts agree."""
    source = Path(proposal_filing.__file__).read_text(encoding="utf-8")
    gate_call = source.index("preflight_results.append(_run_compliance_gate(")
    dry_run_return = source.index("if request.dry_run:", gate_call)
    writer_call = source.index("bridge_writer.propose_bridge_codex_non_bypass", gate_call)
    assert gate_call < dry_run_return < writer_call
    assert source.count("preflight_results.append(_run_compliance_gate(") == 1
