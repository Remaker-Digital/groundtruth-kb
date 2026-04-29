# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for groundtruth_kb.bridge.paths.

Per ``bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md``
section 1.2, these tests verify strict-marker root resolution and fail-closed
state-directory semantics. No production-code bypass is exercised; tests that
need temporary state use a synthetic in-root GT-KB project under pytest
``tmp_path``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from groundtruth_kb.bridge.paths import (
    GROUNDTRUTH_MARKER,
    PROJECT_ROOT_ENV_VAR,
    STATE_DIR_ENV_VAR,
    ProjectRootNotFoundError,
    StateDirOutOfRootError,
    get_state_dir,
    resolve_project_root,
)


@pytest.fixture
def synthetic_gtkb_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a synthetic in-root GT-KB project at ``tmp_path/synth_gtkb/``.

    Sets ``GTKB_PROJECT_ROOT`` so ``resolve_project_root()`` returns the
    synthetic root for the duration of the test. State paths resolve under
    this synthetic root via the same in-root contract production uses.
    """
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / GROUNDTRUTH_MARKER).write_text("# synthetic GT-KB root for tests\n")
    monkeypatch.setenv(PROJECT_ROOT_ENV_VAR, str(synth))
    monkeypatch.delenv(STATE_DIR_ENV_VAR, raising=False)
    return synth


def test_resolve_project_root_from_groundtruth_toml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / GROUNDTRUTH_MARKER).write_text("")
    monkeypatch.setenv(PROJECT_ROOT_ENV_VAR, str(synth))
    assert resolve_project_root().resolve() == synth.resolve()


def test_resolve_project_root_from_git_toplevel_with_groundtruth_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Discovery via git rev-parse + validation by groundtruth.toml."""
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    synth = tmp_path / "synth_gtkb"
    synth.mkdir()
    (synth / GROUNDTRUTH_MARKER).write_text("")
    subprocess.run(["git", "init"], cwd=synth, check=True, capture_output=True)
    monkeypatch.delenv(PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(synth)
    assert resolve_project_root().resolve() == synth.resolve()


def test_resolve_project_root_walks_up_parents(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    synth = tmp_path / "synth_gtkb"
    nested = synth / "deep" / "nested"
    nested.mkdir(parents=True)
    (synth / GROUNDTRUTH_MARKER).write_text("")
    monkeypatch.delenv(PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(nested)
    # Disable git discovery so we test the parent-walk path directly.
    fake_path = tmp_path / "no-git"
    fake_path.mkdir()
    monkeypatch.setenv("PATH", str(fake_path))
    if os.name == "nt":
        monkeypatch.setenv("PATHEXT", "")
    assert resolve_project_root().resolve() == synth.resolve()


def test_resolve_project_root_raises_when_no_marker_found(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.delenv(PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(empty)
    fake_path = tmp_path / "no-git"
    fake_path.mkdir()
    monkeypatch.setenv("PATH", str(fake_path))
    if os.name == "nt":
        monkeypatch.setenv("PATHEXT", "")
    with pytest.raises(ProjectRootNotFoundError):
        resolve_project_root()


def test_resolve_project_root_via_env_var_validates_marker_presence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Env-var override missing groundtruth.toml raises immediately."""
    no_marker = tmp_path / "no_marker"
    no_marker.mkdir()
    monkeypatch.setenv(PROJECT_ROOT_ENV_VAR, str(no_marker))
    with pytest.raises(ProjectRootNotFoundError) as excinfo:
        resolve_project_root()
    assert GROUNDTRUTH_MARKER in str(excinfo.value)


def test_get_state_dir_default_under_synthetic_root(
    synthetic_gtkb_root: Path,
) -> None:
    state = get_state_dir()
    expected = synthetic_gtkb_root / ".gtkb-state" / "bridge-poller"
    assert state.resolve() == expected.resolve()
    assert state.is_relative_to(synthetic_gtkb_root)
    assert state.is_dir()


def test_get_state_dir_env_override_inside_synthetic_root(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    custom_state = synthetic_gtkb_root / "custom" / "state"
    monkeypatch.setenv(STATE_DIR_ENV_VAR, str(custom_state))
    state = get_state_dir()
    assert state.resolve() == custom_state.resolve()
    assert state.is_relative_to(synthetic_gtkb_root)


def test_get_state_dir_env_override_outside_synthetic_root_raises(
    synthetic_gtkb_root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    out_of_root = tmp_path / "outside" / "state"
    monkeypatch.setenv(STATE_DIR_ENV_VAR, str(out_of_root))
    with pytest.raises(StateDirOutOfRootError):
        get_state_dir()


def test_get_state_dir_env_override_at_home_dir_raises(
    synthetic_gtkb_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home_state = Path.home() / ".gtkb-state-test-leak"
    monkeypatch.setenv(STATE_DIR_ENV_VAR, str(home_state))
    with pytest.raises(StateDirOutOfRootError):
        get_state_dir()


def test_resolve_project_root_from_inside_groundtruth_kb_returns_parent_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolution from inside groundtruth-kb/ must return the GT-KB host root.

    Per Finding 2 of bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-004.md:
    the in-tree groundtruth.toml lives at the host root, not at the package
    root. Verify the resolver honors this when invoked from the package
    subdirectory.
    """
    host_root = Path(__file__).resolve().parents[2]
    package_dir = host_root / "groundtruth-kb"
    if not (host_root / GROUNDTRUTH_MARKER).is_file():
        pytest.skip(f"Test precondition: {GROUNDTRUTH_MARKER} must exist at {host_root}")
    if not (package_dir.exists() and package_dir.is_dir()):
        pytest.skip(f"Test precondition: package dir must exist at {package_dir}")

    monkeypatch.delenv(PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(package_dir)
    resolved = resolve_project_root()
    assert resolved.resolve() == host_root.resolve()


def test_resolve_project_root_rejects_git_repo_without_groundtruth_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A directory that is a Git repo but has no groundtruth.toml is NOT a valid GT-KB root.

    Per Finding 1 of bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-006.md:
    .git/ alone never qualifies a directory as a GT-KB host root.
    """
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    fake_repo = tmp_path / "not_gtkb"
    fake_repo.mkdir()
    subprocess.run(["git", "init"], cwd=fake_repo, check=True, capture_output=True)

    monkeypatch.delenv(PROJECT_ROOT_ENV_VAR, raising=False)
    monkeypatch.chdir(fake_repo)
    with pytest.raises(ProjectRootNotFoundError):
        resolve_project_root()


def test_resolve_project_root_via_env_var_pointing_at_git_repo_without_groundtruth_toml_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GTKB_PROJECT_ROOT pointing at a Git repo without groundtruth.toml is rejected."""
    if shutil.which("git") is None:
        pytest.skip("git not available on this system")
    fake_repo = tmp_path / "not_gtkb"
    fake_repo.mkdir()
    subprocess.run(["git", "init"], cwd=fake_repo, check=True, capture_output=True)

    monkeypatch.setenv(PROJECT_ROOT_ENV_VAR, str(fake_repo))
    with pytest.raises(ProjectRootNotFoundError) as excinfo:
        resolve_project_root()
    assert GROUNDTRUTH_MARKER in str(excinfo.value)
