"""Tests for the bridge REVISED filing helper."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "revise_bridge.py"


def _load_helper_module():
    sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
    spec = importlib.util.spec_from_file_location("bridge_revise_helper_under_test", HELPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["bridge_revise_helper_under_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def helper():
    return _load_helper_module()


@pytest.fixture(autouse=True)
def author_metadata_env(monkeypatch):
    monkeypatch.setenv("GTKB_AUTHOR_IDENTITY", "Codex")
    monkeypatch.setenv("GTKB_AUTHOR_HARNESS_ID", "A")
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", "session-123")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL", "GPT-5.5")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_VERSION", "5.5")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_CONFIGURATION", "Extra High")


def _stage_thread(tmp_path: Path, *, latest_status: str = "NO-GO", slug: str = "test-revision") -> Path:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / f"{slug}-001.md").write_text(
        "NEW\n\n"
        "# Test Proposal\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n\n"
        "## Owner Decisions / Input\n\n"
        "- Carry this section forward.\n",
        encoding="utf-8",
    )
    (bridge_dir / f"{slug}-002.md").write_text(
        "NO-GO\n\n"
        "# Loyal Opposition Review\n\n"
        "## Findings\n\n"
        "### F1 - P1 - Missing concrete correction\n\n"
        "### F2 - P2 - Missing gate ordering\n",
        encoding="utf-8",
    )
    lines = [
        "# Bridge Index\n\n",
        f"Document: {slug}\n",
        f"{latest_status}: bridge/{slug}-002.md\n",
        f"NEW: bridge/{slug}-001.md\n",
    ]
    (bridge_dir / "INDEX.md").write_text("".join(lines), encoding="utf-8")
    return bridge_dir


def _completed_revision() -> str:
    return (
        "REVISED\n\n"
        "# Test Revision\n\n"
        "## Revision Claim\n\n"
        "This completed revision addresses the findings while preserving bridge/INDEX.md as canonical.\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
        "- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001\n"
        "- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001\n\n"
        "## Prior Deliberations\n\n"
        "- bridge/test-revision-002.md - prior review finding.\n\n"
        "## Owner Decisions / Input\n\n"
        "- Carried forward from the prior proposal; no new owner decision.\n\n"
        "## Findings Addressed\n\n"
        "### F1 - P1 - Missing concrete correction\n\n"
        "Completed correction is documented here.\n\n"
        "### F2 - P2 - Missing gate ordering\n\n"
        "Completed gate ordering is documented here.\n\n"
        "## Pre-Filing Preflight Subsection\n\n"
        "The helper inserts the REVISED line at the top of the existing INDEX entry after gates pass.\n\n"
        "## Check Plan\n\n"
        "Run `python -m pytest platform_tests/skills/test_bridge_revise_helper.py` after filing.\n\n"
        "## Risk And Rollback\n\n"
        "Rollback removes helper output only; bridge audit files remain append-only.\n"
    )


def test_latest_no_go_thread_produces_plan_and_findings(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)

    plan = helper.plan_revision("test-revision", bridge_dir=bridge_dir, draft_dir=tmp_path / "drafts")

    assert plan.latest_status == "NO-GO"
    assert plan.next_version == 3
    assert plan.live_path == "bridge/test-revision-003.md"
    assert plan.index_line == "REVISED: bridge/test-revision-003.md"
    assert any("F1" in finding for finding in plan.findings)
    assert any("F2" in finding for finding in plan.findings)


def test_scaffold_mode_creates_non_dispatchable_draft(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    draft_dir = tmp_path / ".gtkb-state" / "bridge-revisions" / "drafts"

    draft = helper.scaffold_revision("test-revision", bridge_dir=bridge_dir, draft_dir=draft_dir)

    index = (bridge_dir / "INDEX.md").read_text(encoding="utf-8")
    assert draft == draft_dir / "test-revision-003.md"
    assert draft.exists()
    assert "draft_only: true" in draft.read_text(encoding="utf-8")
    assert "Owner Decisions / Input" in draft.read_text(encoding="utf-8")
    assert "REVISED: bridge/test-revision-003.md" not in index
    assert not (bridge_dir / "test-revision-003.md").exists()


def test_file_mode_creates_live_revised_after_gates(helper, tmp_path, monkeypatch):
    bridge_dir = _stage_thread(tmp_path)
    calls: list[tuple[str, Path]] = []

    def fake_preflights(slug, candidate_path, *, project_root=helper.PROJECT_ROOT):
        calls.append((slug, candidate_path))

    monkeypatch.setattr(helper, "_run_candidate_preflights", fake_preflights)

    live = helper.file_revision("test-revision", content=_completed_revision(), bridge_dir=bridge_dir)

    assert live == bridge_dir / "test-revision-003.md"
    assert live.exists()
    assert calls and calls[0][0] == "test-revision"
    index = (bridge_dir / "INDEX.md").read_text(encoding="utf-8")
    assert (
        "Document: test-revision\n"
        "REVISED: bridge/test-revision-003.md\n"
        "NO-GO: bridge/test-revision-002.md\n"
        "NEW: bridge/test-revision-001.md\n"
    ) in index


def test_existing_target_file_causes_no_overwrite_error(helper, tmp_path, monkeypatch):
    bridge_dir = _stage_thread(tmp_path)
    (bridge_dir / "test-revision-003.md").write_text("existing", encoding="utf-8")
    monkeypatch.setattr(helper, "_run_candidate_preflights", lambda *_args, **_kwargs: None)

    with pytest.raises(helper.BridgeFileAlreadyExistsError):
        helper.file_revision("test-revision", content=_completed_revision(), bridge_dir=bridge_dir)


def test_non_no_go_latest_status_refuses_write_mode(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path, latest_status="GO")

    with pytest.raises(helper.BridgeLatestStatusError):
        helper.file_revision(
            "test-revision", content=_completed_revision(), bridge_dir=bridge_dir, run_preflights=False
        )


def test_exact_document_matching_avoids_slug_prefix_false_positive(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path, slug="test-revision-extra")

    with pytest.raises(helper.BridgeDocumentNotFoundError):
        helper.plan_revision("test-revision", bridge_dir=bridge_dir)


def test_credential_content_aborts_before_live_mutation(helper, tmp_path, monkeypatch):
    bridge_dir = _stage_thread(tmp_path)
    monkeypatch.setattr(helper, "_run_candidate_preflights", lambda *_args, **_kwargs: None)
    content = _completed_revision() + "\nsecret = 'abcdabcdabcdabcd'\n"
    with pytest.raises(RuntimeError, match="Credential-shaped content detected"):
        helper.file_revision("test-revision", content=content, bridge_dir=bridge_dir)

    assert not (bridge_dir / "test-revision-003.md").exists()
    assert "REVISED: bridge/test-revision-003.md" not in (bridge_dir / "INDEX.md").read_text(encoding="utf-8")


def test_incomplete_placeholders_cannot_become_live_revised_row(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    content = _completed_revision().replace("Completed correction is documented here.", "TODO")

    with pytest.raises(helper.BridgeRevisionPlaceholderError):
        helper.file_revision("test-revision", content=content, bridge_dir=bridge_dir, run_preflights=False)

    assert not (bridge_dir / "test-revision-003.md").exists()


def test_preflight_failure_aborts_before_index_mutation(helper, tmp_path, monkeypatch):
    bridge_dir = _stage_thread(tmp_path)

    def fail_preflight(*_args, **_kwargs):
        raise helper.BridgePreflightError("simulated gate failure")

    monkeypatch.setattr(helper, "_run_candidate_preflights", fail_preflight)

    with pytest.raises(helper.BridgePreflightError):
        helper.file_revision("test-revision", content=_completed_revision(), bridge_dir=bridge_dir)

    assert not (bridge_dir / "test-revision-003.md").exists()
    assert "REVISED: bridge/test-revision-003.md" not in (bridge_dir / "INDEX.md").read_text(encoding="utf-8")


def test_index_changed_during_write_is_detected(helper, tmp_path, monkeypatch):
    bridge_dir = _stage_thread(tmp_path)
    original_insert = helper._insert_revised_index_line

    def mutate_index_then_insert(index_text, slug, line_to_insert):
        (bridge_dir / "INDEX.md").write_text(
            index_text + "\nDocument: other\nNEW: bridge/other-001.md\n", encoding="utf-8"
        )
        return original_insert(index_text, slug, line_to_insert)

    monkeypatch.setattr(helper, "_run_candidate_preflights", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(helper, "_insert_revised_index_line", mutate_index_then_insert)

    with pytest.raises(helper.BridgeIndexConflictError):
        helper.file_revision("test-revision", content=_completed_revision(), bridge_dir=bridge_dir)


def test_real_candidate_content_preflights_pass(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)

    live = helper.file_revision("test-revision", content=_completed_revision(), bridge_dir=bridge_dir)

    assert live.exists()
