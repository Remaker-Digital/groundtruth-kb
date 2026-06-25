"""Regression tests for WI-4763 foreign-session staged verdict commit guard."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PATHSPEC_SCRIPT = PROJECT_ROOT / "scripts" / "check_commit_pathspec_safety.py"
SCOPE_SCRIPT = PROJECT_ROOT / "scripts" / "check_commit_scope_bundling.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pathspec_checker = _load_module(PATHSPEC_SCRIPT, "check_commit_pathspec_safety_foreign_guard")
scope_checker = _load_module(SCOPE_SCRIPT, "check_commit_scope_bundling_foreign_guard")


def _write_verdict(
    repo: Path,
    rel_path: str,
    *,
    status: str,
    author_session_context_id: str | None,
) -> None:
    path = repo / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [status, ""]
    if author_session_context_id is not None:
        lines.append(f"author_session_context_id: {author_session_context_id}")
    lines.append("")
    lines.append("# Fixture verdict")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo, check=True, capture_output=True)
    return repo


def test_blocks_foreign_session_staged_verdict_outside_pathspec(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_verdict(
        repo,
        "bridge/gtkb-foreign-fixture-008.md",
        status="NO-GO",
        author_session_context_id="foreign-session-abc",
    )

    result = pathspec_checker.detect_foreign_staged_verdicts(
        repo,
        ["bridge/gtkb-foreign-fixture-008.md", "scripts/feature.py"],
        "committing-session-xyz",
        pathspec_names=set(),
    )

    assert result["foreign_blocked"] is True
    assert result["foreign_verdicts"][0]["path"] == "bridge/gtkb-foreign-fixture-008.md"
    assert result["foreign_verdicts"][0]["reason"] == "foreign_session"


def test_allows_owned_verdict_in_explicit_pathspec(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    rel = "bridge/gtkb-foreign-fixture-008.md"
    _write_verdict(repo, rel, status="VERIFIED", author_session_context_id="foreign-session-abc")

    result = pathspec_checker.detect_foreign_staged_verdicts(
        repo,
        [rel, "scripts/feature.py"],
        "committing-session-xyz",
        pathspec_names={rel},
    )

    assert result["foreign_blocked"] is False
    assert result["foreign_verdicts"] == []


def test_allows_same_session_authored_verdict(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    rel = "bridge/gtkb-foreign-fixture-008.md"
    session = "shared-session-123"
    _write_verdict(repo, rel, status="GO", author_session_context_id=session)

    result = pathspec_checker.detect_foreign_staged_verdicts(
        repo,
        [rel],
        session,
        pathspec_names=set(),
    )

    assert result["foreign_blocked"] is False


def test_strict_exit_nonzero_for_foreign_verdict(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _init_repo(tmp_path)
    rel = "bridge/gtkb-foreign-fixture-008.md"
    _write_verdict(repo, rel, status="NO-GO", author_session_context_id="foreign-session")

    monkeypatch.chdir(repo)
    monkeypatch.setattr(pathspec_checker, "_staged_names", lambda: [rel, "scripts/feature.py"])
    monkeypatch.setattr(pathspec_checker, "_repository_root", lambda: repo)

    rc = pathspec_checker.main(
        [
            "--staged",
            "--strict",
            "--check-foreign-verdicts",
            "--committing-session-id",
            "committing-session-xyz",
        ]
    )
    assert rc == pathspec_checker.STRICT_CONTAMINATION_EXIT


def test_scope_bundling_warns_on_foreign_staged_verdict(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    config_path = repo / "config" / "governance" / "narrative-artifact-approval.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        '[[protected_artifacts]]\npatterns = ["docs/*.md"]\n',
        encoding="utf-8",
    )
    rel = "bridge/gtkb-foreign-fixture-008.md"
    _write_verdict(repo, rel, status="NO-GO", author_session_context_id="foreign-session")

    result = scope_checker.evaluate(
        repo,
        paths=[rel, "scripts/feature.py"],
        committing_session_id="committing-session-xyz",
        pathspec_names=set(),
    )

    assert result["status"] == "warn"
    assert any(finding["kind"] == "foreign_staged_verdict" for finding in result["findings"])
