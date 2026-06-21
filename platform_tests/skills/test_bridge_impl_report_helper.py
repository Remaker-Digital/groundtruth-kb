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


@pytest.fixture(autouse=True)
def author_metadata_env(monkeypatch):
    monkeypatch.setenv("GTKB_AUTHOR_IDENTITY", "Codex")
    monkeypatch.setenv("GTKB_AUTHOR_HARNESS_ID", "A")
    monkeypatch.setenv("GTKB_AUTHOR_SESSION_CONTEXT_ID", "session-123")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL", "GPT-5.5")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_VERSION", "5.5")
    monkeypatch.setenv("GTKB_AUTHOR_MODEL_CONFIGURATION", "Extra High")


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
    if latest_status != "GO":
        (bridge_dir / f"{slug}-002.md").write_text(
            f"{latest_status}\n\n# Loyal Opposition Review\n\nVerdict: {latest_status}\n",
            encoding="utf-8",
        )
    (bridge_dir / "test-impl-report-extra-001.md").write_text("NEW\n\n# Extra Proposal\n", encoding="utf-8")
    (bridge_dir / "test-impl-report-extra-002.md").write_text("GO\n\n# Extra Review\n", encoding="utf-8")
    return bridge_dir


def _completed_report() -> str:
    return (
        "NEW\n\n"
        "# Test Implementation Report\n\n"
        "bridge_kind: implementation_report\n\n"
        "## Implementation Claim\n\n"
        "Implemented the helper.\n\n"
        "## Specification Links\n\n"
        "- `GOV-FILE-BRIDGE-AUTHORITY-001`\n"
        "- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`\n\n"
        "## Owner Decisions / Input\n\n"
        "No new owner decision is required.\n\n"
        "## Prior Deliberations\n\n"
        "- `bridge/test-impl-report-001.md` - approved proposal.\n\n"
        "## Code Quality Baseline\n\n"
        "| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |\n"
        "|---|---|---|---|---|\n"
        "| CQ-TESTS-001 | Yes | Run focused helper tests. | pytest | |\n\n"
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


def test_write_mode_creates_report_without_index_mutation(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)

    live = helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)

    assert live == bridge_dir / "test-impl-report-003.md"
    assert live.exists()
    assert live.read_text(encoding="utf-8").lstrip().startswith("NEW")
    assert not (bridge_dir / "INDEX.md").exists()


def test_missing_bridge_kind_refuses_report(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    report_kind = "bridge_kind: " + "implementation_report"
    content = _completed_report().replace(f"{report_kind}\n\n", "")

    with pytest.raises(helper.BridgeImplReportError, match=report_kind):
        helper.file_report("test-impl-report", content=content, bridge_dir=bridge_dir)

    assert not (bridge_dir / "test-impl-report-003.md").exists()


def test_wrong_bridge_kind_refuses_report(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    report_kind = "bridge_kind: " + "implementation_report"
    proposal_kind = "bridge_kind: " + "implementation_" + "proposal"
    content = _completed_report().replace(report_kind, proposal_kind)
    expected_error = "got bridge_kind: " + "implementation_" + "proposal"

    with pytest.raises(helper.BridgeImplReportError, match=expected_error):
        helper.file_report("test-impl-report", content=content, bridge_dir=bridge_dir)

    assert not (bridge_dir / "test-impl-report-003.md").exists()


def test_missing_recommended_commit_type_refuses_report(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    commit_label = "Recommended commit " + "type:"
    content = _completed_report().replace(commit_label, "Commit type:")

    with pytest.raises(helper.BridgeImplReportError, match="Recommended commit type"):
        helper.file_report("test-impl-report", content=content, bridge_dir=bridge_dir)

    assert not (bridge_dir / "test-impl-report-003.md").exists()


def test_scaffold_content_is_compatible_with_report_validator(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    skeleton = helper.build_report_skeleton("test-impl-report", bridge_dir=bridge_dir)

    live = helper.file_report("test-impl-report", content=skeleton, bridge_dir=bridge_dir)

    assert live.exists()
    live_text = live.read_text(encoding="utf-8")
    assert ("bridge_kind: " + "implementation_report") in live_text
    assert ("Recommended commit " + "type:") in live_text


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
    assert not (bridge_dir / "INDEX.md").exists()


def test_unrelated_bridge_file_does_not_block_versioned_write(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    (bridge_dir / "other-001.md").write_text("NEW\n\n# Other thread\n", encoding="utf-8")

    helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)

    assert (bridge_dir / "test-impl-report-003.md").exists()
    assert (bridge_dir / "other-001.md").exists()
    assert not (bridge_dir / "INDEX.md").exists()


def test_latest_status_change_before_write_is_detected(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    (bridge_dir / "test-impl-report-003.md").write_text("NO-GO\n\n# Later review\n", encoding="utf-8")

    with pytest.raises(helper.BridgeLatestStatusError):
        helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)


def test_file_mode_uses_validated_bridge_writer(helper, tmp_path, monkeypatch):
    bridge_dir = _stage_thread(tmp_path)
    calls: list[tuple[str, object]] = []

    def fake_write(slug, version, content, project_root, *, require_author_metadata=True):
        calls.append(("write", (slug, version, require_author_metadata, content.startswith("NEW"), project_root)))
        return project_root / "bridge" / f"{slug}-{version:03d}.md"

    monkeypatch.setattr(helper, "write_bridge_file", fake_write)

    helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)

    assert [call[0] for call in calls] == ["write"]
    assert calls[0][1][1] == 3
    assert calls[0][1][2] is False
    assert calls[0][1][3] is True


def test_file_report_preserves_content_file_mtime(helper, tmp_path):
    bridge_dir = _stage_thread(tmp_path)
    content_path = tmp_path / "completed-report.md"
    content_path.write_text(_completed_report(), encoding="utf-8")
    old_time = 1_700_000_000
    helper.os.utime(content_path, (old_time, old_time))

    live = helper.file_report("test-impl-report", content_path=content_path, bridge_dir=bridge_dir)

    assert live.stat().st_mtime == pytest.approx(old_time, abs=1)


def test_file_report_does_not_preserve_mtime_for_direct_content(helper, tmp_path, monkeypatch):
    bridge_dir = _stage_thread(tmp_path)
    calls = []

    def fake_utime(*args, **kwargs):
        calls.append((args, kwargs))

    monkeypatch.setattr(helper.os, "utime", fake_utime)

    helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)

    assert calls == []


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


# ---------------------------------------------------------------------------
# WI-4468 acceptance assertions
# These two tests lock the WI-4522 fix at the impl_report_bridge.file_report
# boundary, verifying that author metadata provenance is per-harness and
# fail-closed (GOV-DOCUMENT-AUTHOR-PROVENANCE-001).
# ---------------------------------------------------------------------------


def test_wi4468_codex_env_stamps_loyal_opposition_codex_harness_a(helper, tmp_path, monkeypatch):
    """WI-4468 acceptance: file_report from Codex env stamps loyal-opposition/codex + harness A.

    Verifies the WI-4522 fix at the impl_report_bridge.file_report boundary.
    A metadata-less report body stamped from a Codex env envelope must carry
    the Codex-A identity, not a stale cross-harness Claude/B stamp.
    """
    import sys

    bridge_dir = _stage_thread(tmp_path)

    # Remove identity/harness_id env overrides so the durable resolver's
    # canonical form ("role/harness_name") is not masked by env values.
    # The four per-session runtime fields (session, model, etc.) remain from
    # the autouse author_metadata_env fixture so validate_author_metadata passes.
    monkeypatch.delenv("GTKB_AUTHOR_IDENTITY", raising=False)
    monkeypatch.delenv("GTKB_AUTHOR_HARNESS_ID", raising=False)

    # Patch the durable resolver to return canonical Codex LO identity.
    # In tests tmp_path has no harness-state/, so load_harness_identities /
    # load_role_assignments return {} — the resolver would otherwise return {}.
    bam = sys.modules["scripts.bridge_author_metadata"]
    monkeypatch.setattr(
        bam,
        "_resolve_durable_identity_fields",
        lambda root, *, env=None: {"author_identity": "loyal-opposition/codex", "author_harness_id": "A"},
    )

    live = helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)

    written = live.read_text(encoding="utf-8")
    assert "author_identity: loyal-opposition/codex" in written
    assert "author_harness_id: A" in written
    assert "author_harness_id: B" not in written  # no stale cross-harness stamp


def test_wi4468_absent_env_raises_before_writing(helper, tmp_path, monkeypatch):
    """WI-4468 acceptance: file_report fails closed before writing when env envelope is absent.

    Verifies the WI-4522 fix at the file_report boundary: when no env envelope
    supplies author metadata and the report body carries none, ensure_author_metadata
    raises BridgeAuthorMetadataError and the bridge file is never written.
    """
    import sys

    bridge_dir = _stage_thread(tmp_path)

    # Clear every env var that could supply author metadata, simulating the
    # absent-env-envelope case. FIELD_ENV_NAMES is the canonical catalog of
    # all env aliases the loader consults — using it avoids drift from the
    # production code's actual lookup table.
    bam = sys.modules["scripts.bridge_author_metadata"]
    for field_vars in bam.FIELD_ENV_NAMES.values():
        for var in field_vars:
            monkeypatch.delenv(var, raising=False)

    with pytest.raises(bam.BridgeAuthorMetadataError):
        helper.file_report("test-impl-report", content=_completed_report(), bridge_dir=bridge_dir)

    # Bridge file must not have been written before the error was raised.
    assert not (bridge_dir / "test-impl-report-003.md").exists()
