"""Regression guard for WI-5114 tree-stabilization scratch ignores."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

IGNORED_SCRATCH_PATHS = (
    ".harness-tmp/wi5114/sentinel.txt",
    "work_area/wi5114/sentinel.txt",
    ".loyal-opposition/wi5114/sentinel.txt",
    "bridge/example-draft.txt",
    "bridge/.draft-example.txt",
    "bridge/draft-verdict-example.txt",
    ".claude/skills/verify/helpers/_temp_verdict_example.md",
    ".claude/skills/verify/helpers/example-draft-body.md",
    ".codex/skills/verify/helpers/_tmp_example.md",
    ".codex/skills/verify/helpers/draft-example.md",
    ".codex/skills/verify/helpers/writer_script.py",
    "__TEMP_DRAFT_example.md",
    ".temp_verdict_example.md",
    ".tmp_verdict_example.md",
    "_temp_wi5114.md",
    "_temp_draft_example.txt",
    "wi5114-review-package.md",
    "backlog_status_utf8.txt",
    "bridge-scan.json",
)

WI5299_IGNORED_SCRATCH_PATHS = (
    ".harness-tmp-unique-1234/test_case/bridge/INDEX.md",
    ".tmp_lo_diff_filter.py",
    ".tmp_lo_hunk_example.patch",
    "CON",
    "strftime",
    "temp-direct.txt",
    "temp-direct3.txt",
    "temp-test.txt",
    "test-auth-root/bridge/x.md",
    "test-auth-root/harness-state/harness-identities.json",
    ".claude/skills/verify/helpers/tmp_gtkb-wi5061-draft.md",
    ".claude/skills/verify/helpers/write_bridge_5171.py",
    ".codex/skills/verify/helpers/tmp_gtkb-wi5061-draft.md",
    ".codex/skills/verify/helpers/gtkb-wi5069-draft-body.md",
)

VISIBLE_CONTROL_PATHS = (
    ".gitignore",
    ".gitattributes",
    "bridge/gtkb-wi5114-scratch-ignore-hygiene-004.md",
    "bridge/gtkb-wi5299-deterministic-scratch-ignore-closure-002.md",
    ".codex/skills/verify/helpers/write_verdict.py",
    ".claude/skills/verify/helpers/write_bridge.py",
    ".codex/skills/verify/helpers/gtkb-wi5069-final.md",
    "nested/.tmp_lo_keep.py",
    "test-auth-root-canonical/groundtruth.toml",
)


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_tree_stabilization_scratch_paths_are_gitignored() -> None:
    for test_path in IGNORED_SCRATCH_PATHS:
        result = _git("check-ignore", "-v", test_path)

        assert result.returncode == 0, (
            f"Expected {test_path!r} to be gitignored. stdout: {result.stdout!r} stderr: {result.stderr!r}"
        )


def test_wi5299_residue_classes_are_gitignored() -> None:
    for test_path in WI5299_IGNORED_SCRATCH_PATHS:
        result = _git("check-ignore", "-v", test_path)

        assert result.returncode == 0, (
            f"Expected {test_path!r} to be gitignored. stdout: {result.stdout!r} stderr: {result.stderr!r}"
        )


def test_control_paths_are_not_hidden_by_scratch_ignores() -> None:
    for test_path in VISIBLE_CONTROL_PATHS:
        result = _git("check-ignore", "-q", test_path)

        assert result.returncode == 1, (
            f"Expected {test_path!r} to remain visible to git. stdout: {result.stdout!r} stderr: {result.stderr!r}"
        )


def test_gitignore_is_lf_pinned_and_has_no_cr_bytes() -> None:
    gitignore_bytes = (ROOT / ".gitignore").read_bytes()
    assert b"\r" not in gitignore_bytes, ".gitignore must stay LF-only"

    attr_result = _git("check-attr", "text", "eol", "--", ".gitignore")
    assert attr_result.returncode == 0, attr_result.stderr
    assert ".gitignore: text: set" in attr_result.stdout
    assert ".gitignore: eol: lf" in attr_result.stdout

    eol_result = _git("ls-files", "--eol", ".gitignore")
    assert eol_result.returncode == 0, eol_result.stderr
    assert eol_result.stdout.startswith("i/lf"), eol_result.stdout
    assert "w/lf" in eol_result.stdout, eol_result.stdout
