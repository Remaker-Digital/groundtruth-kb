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


def _index_lock_failure(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        ["git", *args],
        1,
        "",
        "fatal: Unable to create 'E:/GT-KB/.git/index.lock': Permission denied",
    )


def _init_verified_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    _git(repo, "config", "commit.gpgsign", "false")
    _write(repo / "bridge" / "sample-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "sample-002.md", "GO\n\n# GO\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 1\n")
    _git(repo, "add", "--", "bridge/sample-001.md", "bridge/sample-002.md", "scripts/feature.py")
    _git(repo, "commit", "-m", "chore: seed bridge thread")
    _write(repo / "bridge" / "sample-003.md", "NEW\n\n# Implementation report\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")
    return repo


def _verified_body() -> str:
    return """VERIFIED
author_identity: loyal-opposition/test
author_harness_id: T
author_session_context_id: test-session
author_model: test-model
author_model_version: test-version
author_model_configuration: test-config

bridge_kind: verification_verdict
Document: sample
Version: 004
Recommended commit type: fix:

## Prior Deliberations

_No prior deliberations: atomicity fixture._

## Specifications Carried Forward

- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py` | yes | PASS |

## Positive Confirmations

- The implementation report and changed source file were inspected.

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

    def fail_commit(args: list[str], *, cwd: Path, check: bool = False):
        if args and args[0] == "commit":
            return subprocess.CompletedProcess(["git", *args], 1, "", "simulated commit failure")
        return real_run_git(args, cwd=cwd, check=check)

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

    # The VERIFIED commit contains ONLY the verified path set + verdict; the
    # unrelated staged file is excluded via the explicit-pathspec commit.
    committed = set(_git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD").stdout.splitlines())
    assert committed == {"bridge/sample-003.md", "bridge/sample-004.md", "scripts/feature.py"}
    assert "scripts/unrelated.py" not in committed
    assert result.verdict_path == "bridge/sample-004.md"
    # The unrelated session's staged work is left untouched (still staged).
    staged = set(_git(repo, "diff", "--name-only", "--cached", "--").stdout.splitlines())
    assert "scripts/unrelated.py" in staged


def test_verified_finalization_retries_transient_index_lock_on_add(
    verify_helper,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _init_verified_repo(tmp_path)
    real_run_git = verify_helper._run_git
    add_attempts = 0
    sleeps: list[float] = []

    def transient_add_lock(args: list[str], *, cwd: Path, check: bool = False):
        nonlocal add_attempts
        if args and args[0] == "add":
            add_attempts += 1
            if add_attempts == 1:
                return _index_lock_failure(args)
        return real_run_git(args, cwd=cwd, check=check)

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

    def transient_commit_lock(args: list[str], *, cwd: Path, check: bool = False):
        nonlocal commit_attempts
        if args and args[0] == "commit":
            commit_attempts += 1
            if commit_attempts == 1:
                return _index_lock_failure(args)
        return real_run_git(args, cwd=cwd, check=check)

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

    def fail_add_without_lock(args: list[str], *, cwd: Path, check: bool = False):
        nonlocal add_attempts
        if args and args[0] == "add":
            add_attempts += 1
            return subprocess.CompletedProcess(["git", *args], 1, "", "pathspec error")
        return real_run_git(args, cwd=cwd, check=check)

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

    def always_lock_add(args: list[str], *, cwd: Path, check: bool = False):
        nonlocal add_attempts
        if args and args[0] == "add":
            add_attempts += 1
            return _index_lock_failure(args)
        return real_run_git(args, cwd=cwd, check=check)

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

    assert codex_bytes == claude_bytes
    assert b"def _run_git_with_lock_retry" in claude_bytes
    assert b"def _run_git_with_lock_retry" in codex_bytes


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

    _write(repo / "bridge" / "sample-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "sample-002.md", "GO\n\n# GO\n")
    _write(repo / "bridge" / "sample-003.md", "IMPLEMENTED\n\n# Old implementation report\n")
    _write(repo / "bridge" / "sample-004.md", "NO-GO\n\n# NO-GO\n")

    _git(
        repo,
        "add",
        "--",
        "bridge/sample-001.md",
        "bridge/sample-002.md",
        "bridge/sample-003.md",
        "bridge/sample-004.md",
    )
    _git(repo, "commit", "-m", "chore: seed bridge thread with historical IMPLEMENTED status")

    _write(repo / "bridge" / "sample-005.md", "REVISED\n\n# Revised implementation report\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")

    body = _verified_body().replace("Version: 004", "Version: 006")

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

    _write(repo / "bridge" / "sample-001.md", "NEW\n\n# Proposal\n")
    _write(repo / "bridge" / "sample-002.md", "GO\n\n# GO\n")
    _write(repo / "bridge" / "sample-003.md", "IMPLEMENTED\n\n# Old implementation report\n")
    _write(repo / "scripts" / "feature.py", "VALUE = 2\n")

    _git(
        repo, "add", "--", "bridge/sample-001.md", "bridge/sample-002.md", "bridge/sample-003.md", "scripts/feature.py"
    )
    _git(repo, "commit", "-m", "chore: seed bridge thread")

    body = _verified_body().replace("Version: 004", "Version: 004")

    with pytest.raises(verify_helper.VerifiedFinalizationError, match="latest status of NEW or REVISED"):
        verify_helper.finalize_verified_commit(
            "sample",
            body,
            include_paths=["bridge/sample-003.md", "scripts/feature.py"],
            commit_message="fix(gtkb): finalize verified sample work",
            project_root=repo,
            pre_populate=False,
        )
