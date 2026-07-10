"""Regression tests for atomic Loyal Opposition VERIFIED finalization."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_HELPER_PATH = REPO_ROOT / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"
CODEX_VERIFY_HELPER_PATH = REPO_ROOT / ".codex" / "skills" / "verify" / "helpers" / "write_verdict.py"
CURSOR_VERIFY_HELPER_PATH = REPO_ROOT / ".cursor" / "skills" / "verify" / "helpers" / "write_verdict.py"


def _load_verify_helper():
    sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))
    spec = importlib.util.spec_from_file_location("verify_write_verdict_atomicity_under_test", VERIFY_HELPER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def verify_helper():
    return _load_verify_helper()


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def _write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _write_project_marker(repo: Path) -> None:
    _write(repo / "groundtruth.toml", "# test project root marker\n")


def _index_lock_failure(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        ["git", *args],
        1,
        "",
        "fatal: Unable to create 'E:/GT-KB/.git/index.lock': Permission denied",
    )


def _implementation_report_body(*, status: str = "NEW", title: str = "# Implementation report") -> str:
    return f"""{status}
author_identity: prime-builder/test
author_harness_id: P
author_session_context_id: 11111111-1111-4111-8111-111111111111
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

{title}
"""


def _init_verified_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.autocrlf", "false")
    _write_project_marker(repo)
    _write(repo / "bridge" / "sample-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "sample-002.md", "GO\n\n# GO\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 1\n")
    _git(repo, "add", "--", "groundtruth.toml", "bridge/sample-001.md", "bridge/sample-002.md", "scripts/feature.py")
    _git(repo, "commit", "-m", "chore: seed bridge thread")
    _write(repo / "bridge" / "sample-003.md", _implementation_report_body())
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")
    return repo


def _verified_body(*, version: int = 4, responds_to: str = "bridge/sample-003.md") -> str:
    return f"""VERIFIED
author_identity: loyal-opposition/test
author_harness_id: T
author_session_context_id: 22222222-2222-4222-8222-222222222222
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

bridge_kind: lo_verdict
Document: sample
Version: {version:03d}
Responds to: {responds_to}
Recommended commit type: fix:

## Prior Deliberations

_No prior deliberations: atomicity fixture._

## Specification Links

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Specifications Carried Forward

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/\
test_lo_verified_commit_atomicity.py` | yes | PASS |

## Positive Confirmations

- The implementation report and changed source file were inspected.

## Applicability Preflight

- packet_hash: `sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

- Blocking gaps: 0

## Commands Executed

- `pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q`
"""


def test_verified_finalization_commits_report_work_and_verdict_together(verify_helper, tmp_path: Path) -> None:
    repo = _init_verified_repo(tmp_path)

    result = verify_helper.finalize_verified_commit(
        "sample",
        _verified_body(),
        include_paths=["bridge/sample-003.md", "scripts/feature.py"],
        commit_message="fix(gtkb): finalize verified sample work",
        project_root=repo,
        pre_populate=False,
    )

    committed = set(_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines())
    assert committed == {"bridge/sample-003.md", "bridge/sample-004.md", "scripts/feature.py"}
    assert result.verdict_path == "bridge/sample-004.md"
    assert result.commit_sha == _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert "Final commit SHA is emitted by the helper" in (repo / "bridge" / "sample-004.md").read_text(
        encoding="utf-8"
    )
    assert _git(repo, "diff", "--name-only", "--cached", "--").stdout.strip() == ""


def test_commit_failure_removes_verified_verdict_and_unstages_helper_paths(
    verify_helper,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _init_verified_repo(tmp_path)
    real_run_git = verify_helper._run_git

    def fail_commit(
        args: list[str],
        *,
        cwd: Path,
        check: bool = False,
        env: dict[str, str] | None = None,
    ):
        if args and args[0] == "commit":
            return subprocess.CompletedProcess(["git", *args], 1, "", "simulated commit failure")
        return real_run_git(args, cwd=cwd, check=check, env=env)

    monkeypatch.setattr(verify_helper, "_run_git", fail_commit)

    with pytest.raises(verify_helper.VerifiedFinalizationError, match="git commit failed"):
        verify_helper.finalize_verified_commit(
            "sample",
            _verified_body(),
            include_paths=["bridge/sample-003.md", "scripts/feature.py"],
            commit_message="fix(gtkb): finalize verified sample work",
            project_root=repo,
            pre_populate=False,
        )

    assert not (repo / "bridge" / "sample-004.md").exists()
    assert _git(repo, "diff", "--name-only", "--cached", "--").stdout.strip() == ""
    assert "bridge/sample-003.md" in _git(repo, "status", "--short").stdout


def test_unrelated_staged_path_is_tolerated_and_excluded_from_commit(verify_helper, tmp_path: Path) -> None:
    repo = _init_verified_repo(tmp_path)
    # Another session left an unrelated file staged in the shared index.
    _write(repo / "scripts" / "unrelated.py", "VALUE = 99\n")
    _git(repo, "add", "--", "scripts/unrelated.py")

    result = verify_helper.finalize_verified_commit(
        "sample",
        _verified_body(),
        include_paths=["bridge/sample-003.md", "scripts/feature.py"],
        commit_message="fix(gtkb): finalize verified sample work",
        project_root=repo,
        pre_populate=False,
    )

    # The VERIFIED commit contains ONLY the disposable-index path set; the
    # unrelated staged file from the real index is excluded.
    committed = set(_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines())
    assert committed == {"bridge/sample-003.md", "bridge/sample-004.md", "scripts/feature.py"}
    assert "scripts/unrelated.py" not in committed
    assert result.verdict_path == "bridge/sample-004.md"
    # The unrelated session's staged work is left untouched (still staged).
    staged = set(_git(repo, "diff", "--name-only", "--cached", "--").stdout.splitlines())
    assert staged == {"scripts/unrelated.py"}


def test_hunk_patch_finalization_commits_selected_hunk_and_leaves_foreign_worktree_hunk(
    verify_helper,
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.autocrlf", "false")
    _write_project_marker(repo)
    _write(repo / "bridge" / "sample-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "sample-002.md", "GO\n\n# GO\n")
    _write(repo / "scripts" / "shared.py", "SELECTED = 1\nFOREIGN = 1\n")
    _git(repo, "add", "--", "groundtruth.toml", "bridge/sample-001.md", "bridge/sample-002.md", "scripts/shared.py")
    _git(repo, "commit", "-m", "chore: seed shared file")
    _write(repo / "bridge" / "sample-003.md", _implementation_report_body())
    _write(repo / "scripts" / "shared.py", "SELECTED = 2\nFOREIGN = 2\n")
    _write(
        repo / "selected.patch",
        """diff --git a/scripts/shared.py b/scripts/shared.py
--- a/scripts/shared.py
+++ b/scripts/shared.py
@@ -1,2 +1,2 @@
-SELECTED = 1
+SELECTED = 2
 FOREIGN = 1
""",
    )

    result = verify_helper.finalize_verified_commit(
        "sample",
        _verified_body(),
        include_paths=["bridge/sample-003.md", "scripts/shared.py"],
        hunk_patch_paths=["selected.patch"],
        commit_message="fix(gtkb): finalize selected shared hunk",
        project_root=repo,
        pre_populate=False,
    )

    committed = set(_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines())
    assert committed == {"bridge/sample-003.md", "bridge/sample-004.md", "scripts/shared.py"}
    assert result.verdict_path == "bridge/sample-004.md"
    assert _git(repo, "show", "HEAD:scripts/shared.py").stdout == "SELECTED = 2\nFOREIGN = 1\n"
    assert (repo / "scripts" / "shared.py").read_text(encoding="utf-8") == "SELECTED = 2\nFOREIGN = 2\n"
    assert _git(repo, "diff", "--name-only", "--cached", "--").stdout.strip() == ""
    assert _git(repo, "diff", "--", "scripts/shared.py").stdout.count("+FOREIGN = 2") == 1


def test_hunk_patch_finalization_preserves_unrelated_real_index_entry(
    verify_helper,
    tmp_path: Path,
) -> None:
    repo = _init_verified_repo(tmp_path)
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n# foreign working tree\n")
    _write(repo / "feature.patch", "diff --git a/scripts/feature.py b/scripts/feature.py\n")
    _write(
        repo / "feature.patch",
        """diff --git a/scripts/feature.py b/scripts/feature.py
--- a/scripts/feature.py
+++ b/scripts/feature.py
@@ -1 +1 @@
-VALUE = 1
+VALUE = 2
""",
    )
    _write(repo / "scripts" / "unrelated.py", "VALUE = 99\n")
    _git(repo, "add", "--", "scripts/unrelated.py")
    staged_before = _git(repo, "diff", "--cached", "--", "scripts/unrelated.py").stdout

    verify_helper.finalize_verified_commit(
        "sample",
        _verified_body(),
        include_paths=["bridge/sample-003.md", "scripts/feature.py"],
        hunk_patch_paths=["feature.patch"],
        commit_message="fix(gtkb): finalize verified sample work",
        project_root=repo,
        pre_populate=False,
    )

    assert _git(repo, "diff", "--cached", "--", "scripts/unrelated.py").stdout == staged_before
    assert set(_git(repo, "diff", "--name-only", "--cached", "--").stdout.splitlines()) == {"scripts/unrelated.py"}
    assert "# foreign working tree" in _git(repo, "diff", "--", "scripts/feature.py").stdout


def test_hunk_patch_outside_include_set_fails_without_verdict(verify_helper, tmp_path: Path) -> None:
    repo = _init_verified_repo(tmp_path)
    _write(
        repo / "outside.patch",
        """diff --git a/scripts/outside.py b/scripts/outside.py
--- a/scripts/outside.py
+++ b/scripts/outside.py
@@ -0,0 +1 @@
+VALUE = 1
""",
    )

    with pytest.raises(verify_helper.VerifiedFinalizationError, match="outside the VERIFIED include set"):
        verify_helper.finalize_verified_commit(
            "sample",
            _verified_body(),
            include_paths=["bridge/sample-003.md", "scripts/feature.py"],
            hunk_patch_paths=["outside.patch"],
            commit_message="fix(gtkb): finalize verified sample work",
            project_root=repo,
            pre_populate=False,
        )

    assert not (repo / "bridge" / "sample-004.md").exists()
    assert _git(repo, "diff", "--name-only", "--cached", "--").stdout.strip() == ""


def test_hunk_patch_apply_failure_removes_verdict_and_preserves_real_index(verify_helper, tmp_path: Path) -> None:
    repo = _init_verified_repo(tmp_path)
    _write(
        repo / "bad.patch",
        """diff --git a/scripts/feature.py b/scripts/feature.py
--- a/scripts/feature.py
+++ b/scripts/feature.py
@@ -1 +1 @@
-MISSING = 1
+VALUE = 2
""",
    )
    _write(repo / "scripts" / "unrelated.py", "VALUE = 99\n")
    _git(repo, "add", "--", "scripts/unrelated.py")
    staged_before = _git(repo, "diff", "--cached", "--", "scripts/unrelated.py").stdout

    with pytest.raises(verify_helper.VerifiedFinalizationError, match="failed to apply"):
        verify_helper.finalize_verified_commit(
            "sample",
            _verified_body(),
            include_paths=["bridge/sample-003.md", "scripts/feature.py"],
            hunk_patch_paths=["bad.patch"],
            commit_message="fix(gtkb): finalize verified sample work",
            project_root=repo,
            pre_populate=False,
        )

    assert not (repo / "bridge" / "sample-004.md").exists()
    assert _git(repo, "diff", "--cached", "--", "scripts/unrelated.py").stdout == staged_before


def test_hunk_patch_with_crlf_context_applies_to_disposable_index(verify_helper, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _git(repo, "config", "core.autocrlf", "false")
    _write_project_marker(repo)
    _write(repo / "bridge" / "sample-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "sample-002.md", "GO\n\n# GO\n")
    _write_bytes(repo / "scripts" / "crlf.txt", b"alpha\r\nbeta\r\n")
    _git(repo, "add", "--", "groundtruth.toml", "bridge/sample-001.md", "bridge/sample-002.md", "scripts/crlf.txt")
    _git(repo, "commit", "-m", "chore: seed crlf fixture")
    _write(repo / "bridge" / "sample-003.md", _implementation_report_body())
    _write_bytes(repo / "scripts" / "crlf.txt", b"alpha\r\nbeta selected\r\n")
    patch_text = _git(repo, "diff", "--", "scripts/crlf.txt").stdout
    _write(repo / "crlf.patch", patch_text)
    _write_bytes(repo / "scripts" / "crlf.txt", b"alpha\r\nbeta selected\r\nforeign\r\n")

    verify_helper.finalize_verified_commit(
        "sample",
        _verified_body(),
        include_paths=["bridge/sample-003.md", "scripts/crlf.txt"],
        hunk_patch_paths=["crlf.patch"],
        commit_message="fix(gtkb): finalize crlf hunk",
        project_root=repo,
        pre_populate=False,
    )

    assert _git(repo, "show", "HEAD:scripts/crlf.txt").stdout == "alpha\nbeta selected\n"
    assert "foreign" in (repo / "scripts" / "crlf.txt").read_text(encoding="utf-8")


def test_verified_finalization_retries_transient_index_lock_on_add(
    verify_helper,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _init_verified_repo(tmp_path)
    real_run_git = verify_helper._run_git
    add_attempts = 0
    sleeps: list[float] = []

    def transient_add_lock(
        args: list[str],
        *,
        cwd: Path,
        check: bool = False,
        env: dict[str, str] | None = None,
    ):
        nonlocal add_attempts
        if args and args[0] == "add":
            add_attempts += 1
            if add_attempts == 1:
                return _index_lock_failure(args)
        return real_run_git(args, cwd=cwd, check=check, env=env)

    monkeypatch.setattr(verify_helper, "_run_git", transient_add_lock)
    monkeypatch.setattr(verify_helper.time, "sleep", sleeps.append)

    result = verify_helper.finalize_verified_commit(
        "sample",
        _verified_body(),
        include_paths=["bridge/sample-003.md", "scripts/feature.py"],
        commit_message="fix(gtkb): finalize verified sample work",
        project_root=repo,
        pre_populate=False,
    )

    committed = set(_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines())
    assert committed == {"bridge/sample-003.md", "bridge/sample-004.md", "scripts/feature.py"}
    assert result.verdict_path == "bridge/sample-004.md"
    assert add_attempts == 2
    assert sleeps == [0.5]
    assert _git(repo, "diff", "--name-only", "--cached", "--").stdout.strip() == ""


def test_verified_finalization_retries_transient_index_lock_on_commit(
    verify_helper,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _init_verified_repo(tmp_path)
    real_run_git = verify_helper._run_git
    commit_attempts = 0
    sleeps: list[float] = []

    def transient_commit_lock(
        args: list[str],
        *,
        cwd: Path,
        check: bool = False,
        env: dict[str, str] | None = None,
    ):
        nonlocal commit_attempts
        if args and args[0] == "commit":
            commit_attempts += 1
            if commit_attempts == 1:
                return _index_lock_failure(args)
        return real_run_git(args, cwd=cwd, check=check, env=env)

    monkeypatch.setattr(verify_helper, "_run_git", transient_commit_lock)
    monkeypatch.setattr(verify_helper.time, "sleep", sleeps.append)

    result = verify_helper.finalize_verified_commit(
        "sample",
        _verified_body(),
        include_paths=["bridge/sample-003.md", "scripts/feature.py"],
        commit_message="fix(gtkb): finalize verified sample work",
        project_root=repo,
        pre_populate=False,
    )

    assert result.commit_sha == _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert commit_attempts == 2
    assert sleeps == [0.5]
    assert _git(repo, "diff", "--name-only", "--cached", "--").stdout.strip() == ""


def test_verified_finalization_does_not_retry_non_lock_git_failure(
    verify_helper,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _init_verified_repo(tmp_path)
    real_run_git = verify_helper._run_git
    add_attempts = 0

    def fail_add_without_lock(
        args: list[str],
        *,
        cwd: Path,
        check: bool = False,
        env: dict[str, str] | None = None,
    ):
        nonlocal add_attempts
        if args and args[0] == "add":
            add_attempts += 1
            return subprocess.CompletedProcess(["git", *args], 1, "", "pathspec error")
        return real_run_git(args, cwd=cwd, check=check, env=env)

    monkeypatch.setattr(verify_helper, "_run_git", fail_add_without_lock)

    with pytest.raises(verify_helper.VerifiedFinalizationError, match="pathspec error"):
        verify_helper.finalize_verified_commit(
            "sample",
            _verified_body(),
            include_paths=["bridge/sample-003.md", "scripts/feature.py"],
            commit_message="fix(gtkb): finalize verified sample work",
            project_root=repo,
            pre_populate=False,
        )

    assert add_attempts == 1
    assert not (repo / "bridge" / "sample-004.md").exists()
    assert _git(repo, "diff", "--name-only", "--cached", "--").stdout.strip() == ""


def test_verified_finalization_exhausts_lock_retries(
    verify_helper,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _init_verified_repo(tmp_path)
    real_run_git = verify_helper._run_git
    add_attempts = 0
    sleeps: list[float] = []

    def always_lock_add(
        args: list[str],
        *,
        cwd: Path,
        check: bool = False,
        env: dict[str, str] | None = None,
    ):
        nonlocal add_attempts
        if args and args[0] == "add":
            add_attempts += 1
            return _index_lock_failure(args)
        return real_run_git(args, cwd=cwd, check=check, env=env)

    monkeypatch.setattr(verify_helper, "_run_git", always_lock_add)
    monkeypatch.setattr(verify_helper.time, "sleep", sleeps.append)
    monkeypatch.setenv("GTKB_VERIFIED_COMMIT_LOCK_RETRIES", "3")
    monkeypatch.setenv("GTKB_VERIFIED_COMMIT_LOCK_BASE_DELAY", "0.25")

    with pytest.raises(verify_helper.VerifiedFinalizationError, match="index.lock"):
        verify_helper.finalize_verified_commit(
            "sample",
            _verified_body(),
            include_paths=["bridge/sample-003.md", "scripts/feature.py"],
            commit_message="fix(gtkb): finalize verified sample work",
            project_root=repo,
            pre_populate=False,
        )

    assert add_attempts == 3
    assert sleeps == [0.25, 0.5]
    assert not (repo / "bridge" / "sample-004.md").exists()
    assert _git(repo, "diff", "--name-only", "--cached", "--").stdout.strip() == ""


def test_verify_helper_codex_twin_matches_claude_and_has_retry() -> None:
    claude_bytes = VERIFY_HELPER_PATH.read_bytes()
    codex_bytes = CODEX_VERIFY_HELPER_PATH.read_bytes()
    cursor_bytes = CURSOR_VERIFY_HELPER_PATH.read_bytes()

    assert codex_bytes == claude_bytes
    assert cursor_bytes == claude_bytes
    assert b"def _run_git_with_lock_retry" in claude_bytes
    assert b"def _run_git_with_lock_retry" in codex_bytes
    assert b"def _run_git_with_lock_retry" in cursor_bytes
    assert b"def _assert_verdict_evidence_anchors" in claude_bytes
    assert b"def _assert_verdict_evidence_anchors" in codex_bytes
    assert b"def _assert_verdict_evidence_anchors" in cursor_bytes


def test_verified_body_requires_executed_spec_to_test_mapping(verify_helper, tmp_path: Path) -> None:
    repo = _init_verified_repo(tmp_path)
    body = _verified_body().replace("## Spec-to-Test Mapping", "## Missing Mapping")

    with pytest.raises(verify_helper.VerifiedFinalizationError, match="Spec-to-Test Mapping"):
        verify_helper.finalize_verified_commit(
            "sample",
            body,
            include_paths=["bridge/sample-003.md", "scripts/feature.py"],
            commit_message="fix(gtkb): finalize verified sample work",
            project_root=repo,
            pre_populate=False,
        )

    assert not (repo / "bridge" / "sample-004.md").exists()


def test_verified_finalization_tolerates_historical_implemented_status(verify_helper, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _write_project_marker(repo)

    _write(repo / "bridge" / "sample-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "sample-002.md", "GO\n\n# GO\n")
    _write(repo / "bridge" / "sample-003.md", "IMPLEMENTED\n\n# Old implementation report\n")
    _write(repo / "bridge" / "sample-004.md", "NO-GO\n\n# NO-GO\n")

    _git(
        repo,
        "add",
        "--",
        "groundtruth.toml",
        "bridge/sample-001.md",
        "bridge/sample-002.md",
        "bridge/sample-003.md",
        "bridge/sample-004.md",
    )
    _git(repo, "commit", "-m", "chore: seed bridge thread with historical IMPLEMENTED status")

    _write(
        repo / "bridge" / "sample-005.md",
        _implementation_report_body(status="REVISED", title="# Revised implementation report"),
    )
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")

    body = _verified_body(version=6, responds_to="bridge/sample-005.md")

    result = verify_helper.finalize_verified_commit(
        "sample",
        body,
        include_paths=["bridge/sample-005.md", "scripts/feature.py"],
        commit_message="fix(gtkb): finalize verified sample work",
        project_root=repo,
        pre_populate=False,
    )

    committed = set(_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines())
    assert committed == {"bridge/sample-005.md", "bridge/sample-006.md", "scripts/feature.py"}
    assert result.verdict_path == "bridge/sample-006.md"


def test_verified_finalization_rejects_latest_implemented_status(verify_helper, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _write_project_marker(repo)

    _write(repo / "bridge" / "sample-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "sample-002.md", "GO\n\n# GO\n")
    _write(
        repo / "bridge" / "sample-003.md",
        _implementation_report_body(status="IMPLEMENTED", title="# Old implementation report"),
    )
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")

    _git(
        repo,
        "add",
        "--",
        "groundtruth.toml",
        "bridge/sample-001.md",
        "bridge/sample-002.md",
        "bridge/sample-003.md",
        "scripts/feature.py",
    )
    _git(repo, "commit", "-m", "chore: seed bridge thread")

    body = _verified_body()

    with pytest.raises(verify_helper.VerifiedFinalizationError, match="latest status of NEW, REVISED, or NO-ACTION"):
        verify_helper.finalize_verified_commit(
            "sample",
            body,
            include_paths=["bridge/sample-003.md", "scripts/feature.py"],
            commit_message="fix(gtkb): finalize verified sample work",
            project_root=repo,
            pre_populate=False,
        )
