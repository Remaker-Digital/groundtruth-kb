"""Tests for scripts/batch_archive_terminal_verdicts.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import batch_archive_terminal_verdicts as batch_mod  # noqa: E402


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Batch Archive Test")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "bridge").mkdir(parents=True, exist_ok=True)
    (repo / "src").mkdir(parents=True, exist_ok=True)
    (repo / "src" / "foreign.py").write_text("foreign = True\n", encoding="utf-8")
    _git(repo, "add", "src/foreign.py")
    _git(repo, "commit", "-q", "-m", "base")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _init_repo(root)
    return root


_REPORT = """NEW
author_identity: prime-builder/codex
author_session_context_id: pb-session

bridge_kind: implementation_report
Document: {slug}
Version: 001
target_paths: ["src/foreign.py"]
"""

_VALID_VERIFIED = """VERIFIED
author_identity: loyal-opposition/cursor
author_session_context_id: lo-session

bridge_kind: implementation_verification
Document: {slug}
Version: 002
Responds to: bridge/{slug}-001.md
Recommended commit type: chore

## Verdict
VERIFIED.

## Spec-to-Test Mapping

| Spec | Verification | Executed | Result |
| --- | --- | --- | --- |
| GOV-WORK-TREE-HYGIENE-001 | python -m pytest tests/test_{slug}.py -q | yes | passed |

## Commands Executed

- `python -m pytest tests/test_{slug}.py -q` -> passed

## Commit Finalization Evidence

Same-transaction path set:

- `bridge/{slug}-001.md`
- `bridge/{slug}-002.md`
"""

_INVALID_VERIFIED = """VERIFIED
author_identity: loyal-opposition/cursor
author_session_context_id: lo-session

bridge_kind: implementation_verification
Document: {slug}
Version: 002
Responds to: bridge/{slug}-001.md

## Verdict
VERIFIED.
"""

_WITHDRAWN = """WITHDRAWN
author_identity: prime-builder/codex
author_session_context_id: pb-session

bridge_kind: withdrawal
Document: {slug}
Version: 002
"""

_ADVISORY = """ADVISORY
author_identity: loyal-opposition/codex
author_session_context_id: lo-session

bridge_kind: loyal_opposition_advisory
Document: {slug}
Version: 002
"""

_RETIRED = """RETIRED
author_identity: prime-builder/codex
author_session_context_id: pb-session

bridge_kind: retirement
Document: {slug}
Version: 002
"""

_SUPERSEDED = """SUPERSEDED
author_identity: prime-builder/codex
author_session_context_id: pb-session

bridge_kind: supersession
Document: {slug}
Version: 002
"""


def _write_untracked_thread(repo: Path, slug: str, verdict: str) -> None:
    (repo / "bridge" / f"{slug}-001.md").write_text(_REPORT.format(slug=slug), encoding="utf-8")
    (repo / "bridge" / f"{slug}-002.md").write_text(verdict.format(slug=slug), encoding="utf-8")


def _head_files(repo: Path) -> set[str]:
    out = _git(repo, "show", "--name-only", "--format=", "HEAD").stdout
    return {line.strip().replace("\\", "/") for line in out.splitlines() if line.strip()}


def test_discover_selects_terminal_non_finalizable_only(repo: Path) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)
    _write_untracked_thread(repo, "thread-valid", _VALID_VERIFIED)
    _write_untracked_thread(repo, "thread-withdrawn", _WITHDRAWN)
    (repo / "bridge" / "thread-go-001.md").write_text("GO\n", encoding="utf-8")

    candidates, skipped = batch_mod.discover_candidates(repo, limit=None)

    assert {candidate.source for candidate in candidates} == {
        "bridge/thread-invalid-002.md",
        "bridge/thread-withdrawn-002.md",
    }
    assert any(skip.source == "bridge/thread-valid-002.md" and "finalizable" in skip.reason for skip in skipped)
    assert any(skip.source == "bridge/thread-go-001.md" and "not terminal" in skip.reason for skip in skipped)


def test_discover_uses_governing_terminal_status_taxonomy(repo: Path) -> None:
    _write_untracked_thread(repo, "thread-advisory", _ADVISORY)
    _write_untracked_thread(repo, "thread-retired", _RETIRED)
    _write_untracked_thread(repo, "thread-superseded", _SUPERSEDED)

    candidates, skipped = batch_mod.discover_candidates(repo, limit=None)

    assert {candidate.source for candidate in candidates} == {"bridge/thread-advisory-002.md"}
    assert any(skip.source == "bridge/thread-retired-002.md" and "not terminal" in skip.reason for skip in skipped)
    assert any(skip.source == "bridge/thread-superseded-002.md" and "not terminal" in skip.reason for skip in skipped)


def test_dry_run_mutates_nothing(repo: Path) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)

    result = batch_mod.run_batch(repo, dry_run=True)

    assert len(result["candidates"]) == 1
    assert result["archived"] == []
    assert (repo / "bridge" / "thread-invalid-002.md").exists()
    assert not (repo / "archive" / "bridge-terminal-verdicts" / "thread-invalid-002.md").exists()
    assert "bridge/thread-invalid-002.md" in _git(repo, "ls-files", "--others", "--exclude-standard").stdout
    assert not (repo / ".gtkb-state" / "batch-archive").exists()


def test_byte_mismatch_aborts_with_source_intact(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)
    candidate = batch_mod.discover_candidates(repo, limit=None)[0][0]

    def corrupt_copy(source: Path, archive: Path) -> None:
        archive.parent.mkdir(parents=True, exist_ok=True)
        archive.write_bytes(source.read_bytes() + b"corrupt")

    monkeypatch.setattr(batch_mod, "_copy_bytes", corrupt_copy)

    with pytest.raises(RuntimeError, match="byte length mismatch"):
        batch_mod.copy_and_verify(candidate, repo)

    assert (repo / candidate.source).exists()
    assert not (repo / candidate.archive).exists()


def test_real_run_commits_only_archive_and_preserves_foreign_index(repo: Path) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)
    (repo / "src" / "foreign.py").write_text("foreign = False\n", encoding="utf-8")
    _git(repo, "add", "src/foreign.py")

    result = batch_mod.run_batch(repo, limit=None)

    assert result["errors"] == []
    assert len(result["archived"]) == 1
    assert not (repo / "bridge" / "thread-invalid-002.md").exists()
    archive = repo / "archive" / "bridge-terminal-verdicts" / "thread-invalid-002.md"
    assert archive.exists()
    assert _head_files(repo) == {"archive/bridge-terminal-verdicts/thread-invalid-002.md"}
    status = _git(repo, "status", "--short", "--", "src/foreign.py").stdout.strip()
    assert status.startswith("M "), status


def test_archive_target_is_not_ignored(repo: Path) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)

    result = batch_mod.run_batch(repo, limit=None)

    assert result["errors"] == []
    ignored = _git(repo, "check-ignore", "archive/bridge-terminal-verdicts/thread-invalid-002.md")
    assert ignored.returncode == 1


def test_index_lock_fails_closed_with_source_intact(repo: Path) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)
    (repo / ".git" / "index.lock").write_text("locked\n", encoding="utf-8")

    result = batch_mod.run_batch(repo, limit=None)

    assert result["errors"]
    assert ".git/index.lock present" in result["errors"][0]["reason"]
    assert (repo / "bridge" / "thread-invalid-002.md").exists()
    assert not (repo / "archive" / "bridge-terminal-verdicts" / "thread-invalid-002.md").exists()
    assert result["cleanup"]["removed"] == ["archive/bridge-terminal-verdicts/thread-invalid-002.md"]

    (repo / ".git" / "index.lock").unlink()
    retry = batch_mod.run_batch(repo, limit=None)

    assert retry["errors"] == []
    assert not (repo / "bridge" / "thread-invalid-002.md").exists()
    assert (repo / "archive" / "bridge-terminal-verdicts" / "thread-invalid-002.md").exists()


def test_commit_failure_unstages_and_removes_only_same_attempt_copy(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)
    (repo / "src" / "foreign.py").write_text("foreign = False\n", encoding="utf-8")
    _git(repo, "add", "src/foreign.py")
    original_commit = batch_mod._commit_archives

    def stage_then_fail(project_root: Path, archive_paths: list[str]) -> tuple[bool, str]:
        staged = _git(project_root, "add", "--", *archive_paths)
        assert staged.returncode == 0
        return False, "forced commit failure"

    monkeypatch.setattr(batch_mod, "_commit_archives", stage_then_fail)

    result = batch_mod.run_batch(repo, limit=None)

    archive_rel = "archive/bridge-terminal-verdicts/thread-invalid-002.md"
    assert result["errors"][0] == {"stage": "commit", "reason": "forced commit failure"}
    assert result["cleanup"] == {"removed": [archive_rel], "errors": []}
    assert (repo / "bridge" / "thread-invalid-002.md").exists()
    assert not (repo / archive_rel).exists()
    assert archive_rel not in _git(repo, "diff", "--cached", "--name-only").stdout
    assert _git(repo, "status", "--short", "--", "src/foreign.py").stdout.strip().startswith("M ")

    monkeypatch.setattr(batch_mod, "_commit_archives", original_commit)
    retry = batch_mod.run_batch(repo, limit=None)

    assert retry["errors"] == []
    assert not (repo / "bridge" / "thread-invalid-002.md").exists()
    assert (repo / archive_rel).exists()


def test_commit_failure_preserves_changed_same_attempt_copy(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)

    def change_then_fail(project_root: Path, archive_paths: list[str]) -> tuple[bool, str]:
        archive = project_root / archive_paths[0]
        archive.write_bytes(archive.read_bytes() + b"changed")
        return False, "forced commit failure after external change"

    monkeypatch.setattr(batch_mod, "_commit_archives", change_then_fail)

    result = batch_mod.run_batch(repo, limit=None)

    archive_rel = "archive/bridge-terminal-verdicts/thread-invalid-002.md"
    assert (repo / "bridge" / "thread-invalid-002.md").exists()
    assert (repo / archive_rel).exists()
    assert result["cleanup"]["removed"] == []
    assert result["cleanup"]["errors"] == [f"preserved changed failed archive copy: {archive_rel}"]
    assert {"stage": "cleanup", "reason": f"preserved changed failed archive copy: {archive_rel}"} in result["errors"]


def test_limit_bounds_candidate_set(repo: Path) -> None:
    _write_untracked_thread(repo, "thread-a", _INVALID_VERIFIED)
    _write_untracked_thread(repo, "thread-b", _INVALID_VERIFIED)

    result = batch_mod.run_batch(repo, limit=1, dry_run=True)

    assert len(result["candidates"]) == 1


def test_audit_log_written(repo: Path) -> None:
    _write_untracked_thread(repo, "thread-invalid", _INVALID_VERIFIED)

    batch_mod.run_batch(repo, limit=None)

    logs = list((repo / ".gtkb-state" / "batch-archive").glob("*.jsonl"))
    assert len(logs) == 1
    events = [json.loads(line) for line in logs[0].read_text(encoding="utf-8").splitlines()]
    assert events[0]["action"] == "archive"
