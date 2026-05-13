"""Tests for the bridge implementation-report filing helper."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "bridge" / "helpers" / "impl_report_bridge.py"


def _load_helper_module():
    sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
    spec = importlib.util.spec_from_file_location("bridge_impl_report_helper_under_test", HELPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["bridge_impl_report_helper_under_test"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def helper():
    return _load_helper_module()


def _stage_thread(tmp_path: Path, *, latest_status: str = "GO", slug: str = "test-impl-report") -> Path:
    bridge_dir = tmp_path / "bridge"
    bridge_dir.mkdir()
    (bridge_dir / f"{slug}-001.md").write_text(
        "NEW\n\n"
        "# Test Proposal\n\n"
        "## Specification Links\n\n"
        "- GOV-FILE-BRIDGE-AUTHORITY-001\n"
        "- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001\n\n"
        "## Acceptance Criteria\n\n"
        "- [ ] Helper files a post-implementation report.\n"
        "- [ ] Helper carries specification links forward.\n",
        encoding="utf-8",
    )
    (bridge_dir / f"{slug}-002.md").write_text(
        "GO\n\n# Loyal Opposition Review\n\nVerdict: GO\n",
        encoding="utf-8",
    )
    lines = [
        "# Bridge Index\n\n",
        f"Document: {slug}\n",
        f"{latest_status}: bridge/{slug}-002.md\n",
        f"NEW: bridge/{slug}-001.md\n",
        "\n",
        "Document: test-impl-report-extra\n",
        "GO: bridge/test-impl-report-extra-002.md\n",
        "NEW: bridge/test-impl-report-extra-001.md\n",
    ]
    (bridge_dir / "INDEX.md").write_text("".join(lines), encoding="utf-8")
    return bridge_dir


def _completed_report() -> str:
    return (
        "NEW\n\n"
        "# Test Implementation Report\n\n"
        "## Implementation Claim\n\n"
        "Implemented the helper.\n\n"
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001`\n"
        "- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`\n\n"
        "## Owner Decisions / Input\n\n"
        "No new owner decision is required.\n\n"
        "## Prior Deliberations\n\n"
        "- `bridge/test-impl-report-001.md` - approved proposal.\n\n"
        "## Specification-Derived Verification Plan\n\n"
        "| Spec / governing surface | Executed verification evidence |\n"
        "| --- | --- |\n"
        "| `GOV-FILE-BRIDGE-AUTHORITY-001` | helper unit test |\n\n"
        "## Commands Run\n\n"
        "- `python -m pytest platform_tests/skills/test_bridge_impl_report_helper.py -q --tb=short`\n\n"
        "## Observed Results\n\n"
        "- Passed.\n\n"
        "## Files Changed\n\n"
        "- `.claude/skills/bridge/helpers/impl_report_bridge.py`\n\n"
        "## Recommended Commit Type\n\n"
        "- Recommended commit type: `feat:`\n\n"
        "## Acceptance Criteria Status\n\n"
        "- [x] Helper files a post-implementation report.\n\n"
        "## Risk And Rollback\n\n"
        "Revert helper and tests; bridge audit files remain append-only.\n\n"
        "## Loyal Opposition Asks\n\n"
        "1. Verify this implementation report.\n"
    )


def test_latest_go_thread_produces_dry_run_plan(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)

    plan = helper.plan_report("test-impl-report", bridge_dir=bridge_dir, draft_dir=tmp_path / "drafts")

    assert plan.latest_status == "GO"
    assert plan.next_version == 3
    assert plan.proposal_path == "bridge/test-impl-report-001.md"
    assert plan.go_path == "bridge/test-impl-report-002.md"
    assert plan.report_path == "bridge/test-impl-report-003.md"
    assert plan.index_line == "NEW: bridge/test-impl-report-003.md"
    assert "GOV-FILE-BRIDGE-AUTHORITY-001" in plan.linked_specs


def test_write_mode_creates_report_and_inserts_new_line(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)

    live = helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)

    assert live == bridge_dir / "test-impl-report-003.md"
    assert live.exists()
    index = (bridge_dir / "INDEX.md").read_text(encoding="utf-8")
    assert (
        "Document: test-impl-report\n"
        "NEW: bridge/test-impl-report-003.md\n"
        "GO: bridge/test-impl-report-002.md\n"
        "NEW: bridge/test-impl-report-001.md\n"
    ) in index


def test_non_go_latest_status_refuses_write_mode(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path, latest_status="NO-GO")

    with pytest.raises(helper.BridgeLatestStatusError):
        helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)


def test_existing_target_file_causes_no_overwrite_error(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    (bridge_dir / "test-impl-report-003.md").write_text("existing", encoding="utf-8")

    with pytest.raises(helper.BridgeFileAlreadyExistsError):
        helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)


def test_exact_document_matching_avoids_slug_prefix_false_positive(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path, slug="test-impl-report-extra")

    with pytest.raises(helper.BridgeDocumentNotFoundError):
        helper.plan_report("test-impl-report", bridge_dir=bridge_dir)


def test_credential_content_aborts_before_live_mutation(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    content = _completed_report() + "\nsecret = 'abcdabcdabcdabcd'\n"

    with pytest.raises(RuntimeError, match="Credential-shaped content detected"):
        helper.file_report("test-impl-report", content=content, bridge_dir=bridge_dir)

    assert not (bridge_dir / "test-impl-report-003.md").exists()
    assert "NEW: bridge/test-impl-report-003.md" not in (bridge_dir / "INDEX.md").read_text(encoding="utf-8")


def test_index_changed_during_write_is_detected(helper, tmp_path, monkeypatch):
    bridge_dir = _stage_thread(tmp_path)
    original_insert = helper._insert_new_index_line

    def mutate_index_then_insert(index_text, slug, line_to_insert):
        (bridge_dir / "INDEX.md").write_text(
            index_text + "\nDocument: other\nNEW: bridge/other-001.md\n", encoding="utf-8"
        )
        return original_insert(index_text, slug, line_to_insert)

    monkeypatch.setattr(helper, "_insert_new_index_line", mutate_index_then_insert)

    with pytest.raises(helper.BridgeIndexConflictError):
        helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)


def test_proposal_spec_links_are_carried_forward_into_skeleton(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)

    skeleton = helper.build_report_skeleton("test-impl-report", bridge_dir=bridge_dir)

    assert "## Specification Links" in skeleton
    assert "- `GOV-FILE-BRIDGE-AUTHORITY-001`" in skeleton
    assert "- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`" in skeleton
    assert "| `GOV-FILE-BRIDGE-AUTHORITY-001` |" in skeleton


def test_files_changed_and_recommended_commit_type_sections_are_present(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)

    skeleton = helper.build_report_skeleton("test-impl-report", bridge_dir=bridge_dir)

    assert "## Files Changed" in skeleton
    assert "## Recommended Commit Type" in skeleton
    assert "Recommended commit type:" in skeleton
