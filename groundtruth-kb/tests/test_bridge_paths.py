# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Strict-marker, environment and linked-worktree project-root resolution.

Bridge imports stay lazy to preserve the bridge import-hygiene contract.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest


def _paths() -> SimpleNamespace:
    """Lazy-import bridge.paths per test_bridge_import_hygiene rule."""
    from groundtruth_kb.bridge.paths import (
        GROUNDTRUTH_MARKER,
        PROJECT_ROOT_ENV_VAR,
        ProjectRootNotFoundError,
        resolve_project_root,
    )

    return SimpleNamespace(
        GROUNDTRUTH_MARKER=GROUNDTRUTH_MARKER,
        PROJECT_ROOT_ENV_VAR=PROJECT_ROOT_ENV_VAR,
        ProjectRootNotFoundError=ProjectRootNotFoundError,
        resolve_project_root=resolve_project_root,
    )


def _confine_marker_lookup_to_fixture(monkeypatch: pytest.MonkeyPatch, fixture_root: Path) -> None:
    """Hide real host markers above a synthetic negative-test boundary."""
    from groundtruth_kb.bridge import paths

    boundary = fixture_root.resolve()
    has_marker = paths._has_marker

    def _has_fixture_marker(candidate: Path) -> bool:
        resolved = candidate.resolve()
        if resolved != boundary and boundary not in resolved.parents:
            return False
        return has_marker(candidate)

    monkeypatch.setattr(paths, "_has_marker", _has_fixture_marker)


@pytest.fixture
def synthetic_gtkb_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a synthetic in-root GT-KB project at ``tmp_path/synth_gtkb/``."""
    p = _paths()
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / p.GROUNDTRUTH_MARKER).write_text("# synthetic GT-KB root for tests\n")
    monkeypatch.setenv(p.PROJECT_ROOT_ENV_VAR, str(synth))
    return synth


def test_resolve_project_root_from_groundtruth_toml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = _paths()
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / p.GROUNDTRUTH_MARKER).write_text("")
    monkeypatch.setenv(p.PROJECT_ROOT_ENV_VAR, str(synth))
    assert p.resolve_project_root().resolve() == synth.resolve()


def test_resolve_project_root_from_git_toplevel_with_groundtruth_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Discovery via git rev-parse + validation by groundtruth.toml."""
    p = _paths()
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / p.GROUNDTRUTH_MARKER).write_text("")
    subprocess.run(["git", "init"], cwd=synth, check=True, capture_output=True)
    monkeypatch.delenv(p.PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(synth)
    assert p.resolve_project_root().resolve() == synth.resolve()


def test_resolve_project_root_walks_up_parents(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = _paths()
    synth = tmp_path / "synth_gtkb"
    nested = synth / "deep" / "nested"
    nested.mkdir(parents=True)
    (synth / p.GROUNDTRUTH_MARKER).write_text("")
    monkeypatch.delenv(p.PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(nested)
    fake_path = tmp_path / "no-git"
    fake_path.mkdir()
    monkeypatch.setenv("PATH", str(fake_path))
    if os.name == "nt":
        monkeypatch.setenv("PATHEXT", "")
    assert p.resolve_project_root().resolve() == synth.resolve()


def test_resolve_project_root_raises_when_no_marker_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    p = _paths()
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.delenv(p.PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(empty)
    fake_path = tmp_path / "no-git"
    fake_path.mkdir()
    monkeypatch.setenv("PATH", str(fake_path))
    if os.name == "nt":
        monkeypatch.setenv("PATHEXT", "")
    _confine_marker_lookup_to_fixture(monkeypatch, empty)
    with pytest.raises(p.ProjectRootNotFoundError):
        p.resolve_project_root()


def test_resolve_project_root_via_env_var_validates_marker_presence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Env-var override missing groundtruth.toml raises immediately."""
    p = _paths()
    no_marker = tmp_path / "no_marker"
    no_marker.mkdir()
    monkeypatch.setenv(p.PROJECT_ROOT_ENV_VAR, str(no_marker))
    with pytest.raises(p.ProjectRootNotFoundError) as excinfo:
        p.resolve_project_root()
    assert p.GROUNDTRUTH_MARKER in str(excinfo.value)


def test_resolve_project_root_from_inside_groundtruth_kb_returns_parent_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolution from inside groundtruth-kb/ must return the GT-KB host root.

    A linked worktree checkout (``.git`` is a gitfile) resolves to the canonical
    main-worktree root by the resolver's contract, so the expected root is read
    from the gitfile rather than assumed to be this checkout.
    """
    p = _paths()
    host_root = Path(__file__).resolve().parents[2]
    package_dir = host_root / "groundtruth-kb"
    if not (host_root / p.GROUNDTRUTH_MARKER).is_file():
        pytest.skip(f"Test precondition: {p.GROUNDTRUTH_MARKER} must exist at {host_root}")
    if not (package_dir.exists() and package_dir.is_dir()):
        pytest.skip(f"Test precondition: package dir must exist at {package_dir}")
    expected_root = host_root
    gitfile = host_root / ".git"
    if gitfile.is_file():
        gitdir = gitfile.read_text(encoding="utf-8").strip().removeprefix("gitdir:").strip()
        # <main>/.git/worktrees/<name> -> <main>
        expected_root = Path(gitdir).resolve().parents[2]

    monkeypatch.delenv(p.PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(package_dir)
    resolved = p.resolve_project_root()
    assert resolved.resolve() == expected_root.resolve()


def test_resolve_project_root_rejects_git_repo_without_groundtruth_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Git repo without groundtruth.toml is NOT a valid GT-KB root."""
    p = _paths()
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    fake_repo = tmp_path / "not_gtkb"
    fake_repo.mkdir()
    subprocess.run(["git", "init"], cwd=fake_repo, check=True, capture_output=True)

    monkeypatch.delenv(p.PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(fake_repo)
    _confine_marker_lookup_to_fixture(monkeypatch, fake_repo)
    with pytest.raises(p.ProjectRootNotFoundError):
        p.resolve_project_root()


def test_resolve_project_root_via_env_var_pointing_at_git_repo_without_groundtruth_toml_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GTKB_PROJECT_ROOT pointing at a Git repo without groundtruth.toml is rejected."""
    p = _paths()
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    fake_repo = tmp_path / "not_gtkb"
    fake_repo.mkdir()
    subprocess.run(["git", "init"], cwd=fake_repo, check=True, capture_output=True)

    monkeypatch.setenv(p.PROJECT_ROOT_ENV_VAR, str(fake_repo))
    with pytest.raises(p.ProjectRootNotFoundError) as excinfo:
        p.resolve_project_root()
    assert p.GROUNDTRUTH_MARKER in str(excinfo.value)


# WI-3353 IP-1: worktree-aware canonical-root resolution via --git-common-dir.


def _build_worktree_project(tmp_path: Path) -> tuple[Path, Path]:
    """Build a synthetic GT-KB canonical checkout with a linked worktree under
    .claude/worktrees/test-wt. Returns (canonical_root, worktree_root). The
    worktree carries its own committed groundtruth.toml. Requires git.
    """
    ident = [
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=test",
        "-c",
        "commit.gpgsign=false",
    ]
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    (canonical / "groundtruth.toml").write_text("# synthetic GT-KB root\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "add", "groundtruth.toml"], cwd=canonical, check=True, capture_output=True)
    subprocess.run(["git", *ident, "commit", "-m", "init"], cwd=canonical, check=True, capture_output=True)
    worktree = canonical / ".claude" / "worktrees" / "test-wt"
    worktree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", *ident, "worktree", "add", "--detach", str(worktree)],
        cwd=canonical,
        check=True,
        capture_output=True,
    )
    return canonical, worktree


def test_resolve_project_root_worktree_returns_canonical(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-3353 IP-1: resolve_project_root() from inside a linked worktree returns
    the canonical main-worktree root, not the worktree itself.

    ``git rev-parse --git-common-dir`` reports the shared git directory (the main
    worktree's .git); its parent is the canonical root from either checkout.
    """
    p = _paths()
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    canonical, worktree = _build_worktree_project(tmp_path)
    monkeypatch.delenv(p.PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(worktree)
    assert p.resolve_project_root().resolve() == canonical.resolve()


def test_resolve_project_root_env_override_and_parent_walk(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """WI-3353 IP-1: the GTKB_PROJECT_ROOT override still wins from a worktree
    cwd, and the no-git parent walk skips a .claude/worktrees/ segment to reach
    the canonical root rather than stopping on the worktree's marker copy.
    """
    p = _paths()
    canonical = tmp_path / "canonical"
    worktree = canonical / ".claude" / "worktrees" / "wt"
    worktree.mkdir(parents=True)
    (canonical / p.GROUNDTRUTH_MARKER).write_text("# canonical root\n")
    # The worktree carries its own committed copy of the marker.
    (worktree / p.GROUNDTRUTH_MARKER).write_text("# worktree marker copy\n")

    # 1. The env-var override wins regardless of cwd.
    monkeypatch.chdir(worktree)
    monkeypatch.setenv(p.PROJECT_ROOT_ENV_VAR, str(canonical))
    assert p.resolve_project_root().resolve() == canonical.resolve()

    # 2. With no env var and no git on PATH, the parent walk skips the
    #    worktree's marker copy and resolves the canonical root above
    #    .claude/worktrees/.
    monkeypatch.delenv(p.PROJECT_ROOT_ENV_VAR, raising=False)
    no_git = tmp_path / "no-git-dir"
    no_git.mkdir()
    monkeypatch.setenv("PATH", str(no_git))
    if os.name == "nt":
        monkeypatch.setenv("PATHEXT", "")
    assert p.resolve_project_root().resolve() == canonical.resolve()
