# Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Focused tests for scripts/impl_start_target_paths_preflight.py (WI-3380).

Covers the test cases enumerated in
``bridge/gtkb-impl-start-target-paths-preflight-004.md`` § Proposed Scope:

- candidate paths that all match target globs
- one and multiple out-of-scope candidates
- glob patterns such as ``groundtruth-kb/src/**/*.py``
- informational unused targets
- authorization-packet fallback when candidates are omitted
- no-GO-file exit behavior
- missing-target-paths exit behavior
- JSON output schema
- ``--git-diff`` path collection through subprocess mocking
- hook-message enrichment remains advisory (regression: hook block/pass authority unchanged)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import impl_start_target_paths_preflight as preflight  # noqa: E402

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _write_bridge_thread(
    project_root: Path,
    bridge_id: str,
    *,
    target_paths: list[str] | None,
    version_chain: list[tuple[str, int]] | None = None,
) -> dict[str, Path]:
    """Write a synthetic bridge thread with INDEX entry + proposal + GO files.

    Returns a dict mapping each created file's role to its on-disk path. Each
    proposal file uses the canonical body shape so ``extract_target_paths``
    parses cleanly.
    """
    if version_chain is None:
        version_chain = [("GO", 2), ("NEW", 1)]

    bridge_dir = project_root / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)

    index_path = bridge_dir / "INDEX.md"
    index_lines = ["# Bridge Index", "", f"Document: {bridge_id}"]
    files: dict[str, Path] = {"index": index_path}
    for status, version in version_chain:
        rel = f"bridge/{bridge_id}-{version:03d}.md"
        index_lines.append(f"{status}: {rel}")
        body_lines = [
            status,
            "",
            f"# {status} {bridge_id} v{version}",
            "",
            f"Document: {bridge_id}",
            f"Version: {version:03d}",
        ]
        if status in {"NEW", "REVISED"}:
            if target_paths is None:
                body_lines.append("target_paths: []")
            else:
                body_lines.append(f"target_paths: {json.dumps(target_paths)}")
            body_lines.append("")
            body_lines.append("## Specification Links")
            body_lines.append("")
            body_lines.append("- `GOV-FILE-BRIDGE-AUTHORITY-001`")
        body_lines.append("")
        file_path = project_root / rel
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("\n".join(body_lines), encoding="utf-8")
        role = f"{status.lower()}-{version:03d}"
        files[role] = file_path
    index_lines.append("")
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return files


def _write_groundtruth_toml(project_root: Path) -> None:
    """Mark project_root as a canonical GT-KB root so resolver helpers accept it."""
    (project_root / "groundtruth.toml").write_text("# fixture\n", encoding="utf-8")


@pytest.fixture
def fixture_project(tmp_path: Path) -> Path:
    """A self-contained fixture project root with groundtruth.toml + bridge/."""
    _write_groundtruth_toml(tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# T1: All candidates in scope -> exit 0
# ---------------------------------------------------------------------------


def test_all_candidates_in_scope_returns_exit_ok(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py", "groundtruth-kb/tests/test_foo.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/foo.py", "groundtruth-kb/tests/test_foo.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_OK
    assert result[preflight.KEY_VERDICT] == preflight.VERDICT_OK
    assert result[preflight.KEY_OUT_OF_SCOPE] == []
    assert sorted(result[preflight.KEY_IN_SCOPE]) == sorted(["scripts/foo.py", "groundtruth-kb/tests/test_foo.py"])


# ---------------------------------------------------------------------------
# T2 + T3: out-of-scope candidates -> exit 5
# ---------------------------------------------------------------------------


def test_single_out_of_scope_candidate_returns_exit_drift(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/bar.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_SCOPE_DRIFT
    assert result[preflight.KEY_VERDICT] == preflight.VERDICT_SCOPE_DRIFT
    assert result[preflight.KEY_OUT_OF_SCOPE] == ["scripts/bar.py"]
    assert result[preflight.KEY_IN_SCOPE] == []


def test_multiple_out_of_scope_candidates_returns_exit_drift(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/bar.py", "applications/agent_red/main.py", "docs/x.md"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_SCOPE_DRIFT
    assert sorted(result[preflight.KEY_OUT_OF_SCOPE]) == sorted(
        ["scripts/bar.py", "applications/agent_red/main.py", "docs/x.md"]
    )


def test_mixed_in_and_out_of_scope_returns_exit_drift(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/foo.py", "scripts/bar.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_SCOPE_DRIFT
    assert result[preflight.KEY_IN_SCOPE] == ["scripts/foo.py"]
    assert result[preflight.KEY_OUT_OF_SCOPE] == ["scripts/bar.py"]


# ---------------------------------------------------------------------------
# T3a: root-boundary candidates stay out of scope
# ---------------------------------------------------------------------------


def test_root_escape_candidate_does_not_normalize_to_in_scope(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/impl_start_target_paths_preflight.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["../scripts/impl_start_target_paths_preflight.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_SCOPE_DRIFT
    assert result[preflight.KEY_IN_SCOPE] == []
    assert result[preflight.KEY_OUT_OF_SCOPE] == ["../scripts/impl_start_target_paths_preflight.py"]


def test_absolute_outside_root_candidate_is_out_of_scope(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/impl_start_target_paths_preflight.py"],
    )
    outside_path = fixture_project.parent / "outside" / "scripts" / "impl_start_target_paths_preflight.py"
    expected_display = str(outside_path).replace("\\", "/")
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=[str(outside_path)],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_SCOPE_DRIFT
    assert result[preflight.KEY_IN_SCOPE] == []
    assert result[preflight.KEY_OUT_OF_SCOPE] == [expected_display]


def test_in_root_non_existing_relative_path_still_normalizes(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/new_tool.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/new_tool.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_OK
    assert result[preflight.KEY_IN_SCOPE] == ["scripts/new_tool.py"]
    assert result[preflight.KEY_OUT_OF_SCOPE] == []


# ---------------------------------------------------------------------------
# T4: glob patterns like groundtruth-kb/src/**/*.py
# ---------------------------------------------------------------------------


def test_recursive_glob_matches_nested_paths(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["groundtruth-kb/src/**/*.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=[
            "groundtruth-kb/src/groundtruth_kb/project/doctor.py",
            "groundtruth-kb/src/groundtruth_kb/__init__.py",
        ],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_OK
    assert result[preflight.KEY_OUT_OF_SCOPE] == []
    assert len(result[preflight.KEY_IN_SCOPE]) == 2


def test_recursive_glob_rejects_out_of_subtree(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["groundtruth-kb/src/**/*.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/foo.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_SCOPE_DRIFT
    assert result[preflight.KEY_OUT_OF_SCOPE] == ["scripts/foo.py"]


# ---------------------------------------------------------------------------
# T5: informational unused targets
# ---------------------------------------------------------------------------


def test_unused_targets_reported_but_do_not_fail(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py", "scripts/bar.py", "scripts/baz.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/foo.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_OK
    assert sorted(result[preflight.KEY_UNUSED_TARGETS]) == sorted(["scripts/bar.py", "scripts/baz.py"])


# ---------------------------------------------------------------------------
# T6: authorization-packet fallback when candidates omitted
# ---------------------------------------------------------------------------


def test_falls_back_to_named_packet_when_no_explicit_candidates(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    # Write a named-cache packet so the fallback collector picks it up.
    state_dir = fixture_project / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    state_dir.mkdir(parents=True, exist_ok=True)
    packet = {
        "bridge_id": "gtkb-fixture-thread",
        "target_path_globs": ["scripts/foo.py"],
    }
    (state_dir / "gtkb-fixture-thread.json").write_text(json.dumps(packet), encoding="utf-8")
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=None,
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_OK
    assert result[preflight.KEY_CANDIDATE_SOURCE] == preflight.CANDIDATE_SOURCE_PACKET
    assert result[preflight.KEY_CANDIDATE_PATHS] == ["scripts/foo.py"]


def test_no_candidates_and_no_packet_reports_none_source(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=None,
        use_git_diff=False,
    )
    # No candidates -> trivially OK, but source label is "none" and message is informational.
    assert exit_code == preflight.EXIT_OK
    assert result[preflight.KEY_CANDIDATE_SOURCE] == preflight.CANDIDATE_SOURCE_NONE
    assert result[preflight.KEY_CANDIDATE_PATHS] == []


# ---------------------------------------------------------------------------
# T7: no-GO-file exit (3)
# ---------------------------------------------------------------------------


def test_no_go_file_returns_exit_3(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
        version_chain=[("NEW", 1)],  # NEW only - no GO
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/foo.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_NO_GO_FILE
    assert result[preflight.KEY_VERDICT] == preflight.VERDICT_NO_GO_FILE


def test_unknown_bridge_id_returns_exit_3(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-nonexistent-thread",
        explicit_candidates=["scripts/foo.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_NO_GO_FILE


# ---------------------------------------------------------------------------
# T8: missing target_paths exit (4)
# ---------------------------------------------------------------------------


def test_missing_target_paths_returns_exit_4(fixture_project: Path) -> None:
    # Write a thread whose approved proposal has no target_paths metadata line.
    bridge_dir = fixture_project / "bridge"
    bridge_dir.mkdir(parents=True, exist_ok=True)
    (bridge_dir / "INDEX.md").write_text(
        "# Bridge Index\n\nDocument: gtkb-fixture-thread\n"
        "GO: bridge/gtkb-fixture-thread-002.md\n"
        "NEW: bridge/gtkb-fixture-thread-001.md\n",
        encoding="utf-8",
    )
    (bridge_dir / "gtkb-fixture-thread-001.md").write_text(
        "NEW\n\n# Proposal\n\n## Specification Links\n- `GOV-FILE-BRIDGE-AUTHORITY-001`\n",
        encoding="utf-8",
    )
    (bridge_dir / "gtkb-fixture-thread-002.md").write_text("GO\n\n# Verdict\n", encoding="utf-8")
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/foo.py"],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_MISSING_TARGETS
    assert result[preflight.KEY_VERDICT] == preflight.VERDICT_MISSING_TARGETS


def test_empty_target_paths_returns_exit_4(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=[],
    )
    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/foo.py"],
        use_git_diff=False,
    )
    # extract_target_paths raises on empty list, mapping to EXIT_MISSING_TARGETS.
    assert exit_code == preflight.EXIT_MISSING_TARGETS


# ---------------------------------------------------------------------------
# T9: JSON output schema
# ---------------------------------------------------------------------------


def test_json_output_schema(fixture_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    rc = preflight.main(
        [
            "--bridge-id",
            "gtkb-fixture-thread",
            "--candidate-paths",
            "scripts/foo.py",
            "--json",
            "--project-root",
            str(fixture_project),
        ]
    )
    captured = capsys.readouterr()
    assert rc == preflight.EXIT_OK
    payload = json.loads(captured.out)
    expected_keys = {
        preflight.KEY_BRIDGE_ID,
        preflight.KEY_VERDICT,
        preflight.KEY_EXIT_CODE,
        preflight.KEY_MESSAGE,
        preflight.KEY_GO_FILE,
        preflight.KEY_APPROVED_PROPOSAL_FILE,
        preflight.KEY_TARGET_PATHS,
        preflight.KEY_CANDIDATE_PATHS,
        preflight.KEY_CANDIDATE_SOURCE,
        preflight.KEY_IN_SCOPE,
        preflight.KEY_OUT_OF_SCOPE,
        preflight.KEY_UNUSED_TARGETS,
    }
    assert set(payload.keys()) == expected_keys
    assert payload[preflight.KEY_VERDICT] == preflight.VERDICT_OK
    assert payload[preflight.KEY_EXIT_CODE] == preflight.EXIT_OK


def test_human_output_includes_expected_lines(fixture_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    rc = preflight.main(
        [
            "--bridge-id",
            "gtkb-fixture-thread",
            "--candidate-paths",
            "scripts/foo.py",
            "--project-root",
            str(fixture_project),
        ]
    )
    captured = capsys.readouterr()
    assert rc == preflight.EXIT_OK
    assert "Bridge: gtkb-fixture-thread" in captured.out
    assert "Verdict: in_scope" in captured.out


# ---------------------------------------------------------------------------
# T10: --git-diff via subprocess mocking
# ---------------------------------------------------------------------------


def test_git_diff_collects_candidates_via_subprocess(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py", "scripts/bar.py"],
    )
    with patch(
        "impl_start_target_paths_preflight.subprocess.check_output",
        return_value="scripts/foo.py\nscripts/bar.py\n\n",
    ) as mocked:
        result, exit_code = preflight.run_preflight(
            fixture_project,
            "gtkb-fixture-thread",
            explicit_candidates=None,
            use_git_diff=True,
        )
    assert mocked.called
    assert exit_code == preflight.EXIT_OK
    assert result[preflight.KEY_CANDIDATE_SOURCE] == preflight.CANDIDATE_SOURCE_GIT_DIFF
    assert sorted(result[preflight.KEY_CANDIDATE_PATHS]) == sorted(["scripts/foo.py", "scripts/bar.py"])


def test_git_diff_subprocess_error_yields_empty_candidates(fixture_project: Path) -> None:
    _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=["scripts/foo.py"],
    )
    with patch(
        "impl_start_target_paths_preflight.subprocess.check_output",
        side_effect=subprocess.SubprocessError("git failed"),
    ):
        result, exit_code = preflight.run_preflight(
            fixture_project,
            "gtkb-fixture-thread",
            explicit_candidates=None,
            use_git_diff=True,
        )
    # No candidates -> trivially OK with git_diff source label.
    assert exit_code == preflight.EXIT_OK
    assert result[preflight.KEY_CANDIDATE_SOURCE] == preflight.CANDIDATE_SOURCE_GIT_DIFF
    assert result[preflight.KEY_CANDIDATE_PATHS] == []


# ---------------------------------------------------------------------------
# T11: Hook advisory regression -- existing bridge-compliance-gate authority
#       must remain block/pass-unchanged for non-preflight code paths.
# ---------------------------------------------------------------------------


def test_hook_existing_required_fields_constant_unchanged() -> None:
    """The hook's REQUIRED_AUTHOR_METADATA_FIELDS is the load-bearing contract
    against ``scripts/bridge_author_metadata.py``. Adding the advisory call
    must NOT mutate that frozenset / tuple.
    """
    sys.path.insert(0, str(_REPO_ROOT))
    from scripts.bridge_author_metadata import REQUIRED_AUTHOR_METADATA_FIELDS

    assert REQUIRED_AUTHOR_METADATA_FIELDS == (
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "author_model_version",
        "author_model_configuration",
    )


def test_hook_module_imports_cleanly_after_advisory_change() -> None:
    """Lock that the hook module still imports cleanly with the added advisory
    call path. If a syntax/import regression slips in during the advisory edit
    this test catches it immediately.
    """
    sys.path.insert(0, str(_REPO_ROOT / ".claude" / "hooks"))
    import importlib

    # Lazy-import the hook by file path so it can be re-imported after edits.
    spec = importlib.util.spec_from_file_location(
        "bridge_compliance_gate_under_test",
        _REPO_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The hook keeps PENDING_PREFLIGHT_STATUSES + WRITE_TOOLS as load-bearing constants.
    assert "WRITE_TOOLS" in module.__dict__
    assert {"Write", "Edit"} == module.WRITE_TOOLS


# ---------------------------------------------------------------------------
# Smoke: importable + constants stable
# ---------------------------------------------------------------------------


def test_exit_codes_stable() -> None:
    assert preflight.EXIT_OK == 0
    assert preflight.EXIT_NO_GO_FILE == 3
    assert preflight.EXIT_MISSING_TARGETS == 4
    assert preflight.EXIT_SCOPE_DRIFT == 5


def test_verdict_labels_stable() -> None:
    assert preflight.VERDICT_OK == "in_scope"
    assert preflight.VERDICT_NO_GO_FILE == "no_go_file"
    assert preflight.VERDICT_MISSING_TARGETS == "missing_target_paths"
    assert preflight.VERDICT_SCOPE_DRIFT == "out_of_scope_drift"


def test_design_only_empty_target_paths_returns_exit_ok(fixture_project: Path) -> None:
    files = _write_bridge_thread(
        fixture_project,
        "gtkb-fixture-thread",
        target_paths=[],
    )
    proposal_path = files["new-001"]
    content = proposal_path.read_text(encoding="utf-8")
    content = content.replace("target_paths: []", "target_paths: []\nimplementation_scope: design-only\n")
    proposal_path.write_text(content, encoding="utf-8")

    result, exit_code = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=[],
        use_git_diff=False,
    )
    assert exit_code == preflight.EXIT_OK
    assert result[preflight.KEY_VERDICT] == preflight.VERDICT_OK

    result2, exit_code2 = preflight.run_preflight(
        fixture_project,
        "gtkb-fixture-thread",
        explicit_candidates=["scripts/foo.py"],
        use_git_diff=False,
    )
    assert exit_code2 == preflight.EXIT_SCOPE_DRIFT
    assert result2[preflight.KEY_VERDICT] == preflight.VERDICT_SCOPE_DRIFT
