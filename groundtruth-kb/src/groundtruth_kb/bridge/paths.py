# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Resolve the marked GT-KB project root from an explicit setting or Git context.

A valid root contains ``groundtruth.toml``. Linked worktrees resolve through
Git's common directory; ``.git`` alone is not enough to select a root.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

GROUNDTRUTH_MARKER = "groundtruth.toml"
PROJECT_ROOT_ENV_VAR = "GTKB_PROJECT_ROOT"


class ProjectRootNotFoundError(Exception):
    """Raised when no GT-KB host root can be resolved.

    A valid host root must contain ``groundtruth.toml``. Per
    ``.harness-baseline-configuration/rules/project-root-boundary.md``, ``.git/`` alone is not
    sufficient.
    """


def _has_marker(path: Path) -> bool:
    return (path / GROUNDTRUTH_MARKER).is_file()


def _resolve_via_env_var() -> Path | None:
    override = os.environ.get(PROJECT_ROOT_ENV_VAR)
    if not override:
        return None
    candidate = Path(override).resolve()
    if _has_marker(candidate):
        return candidate
    raise ProjectRootNotFoundError(
        f"{PROJECT_ROOT_ENV_VAR}={override} resolves to {candidate}, "
        f"which does not contain {GROUNDTRUTH_MARKER}. "
        f"A valid GT-KB host root must contain {GROUNDTRUTH_MARKER}."
    )


_WORKTREE_DIR_SEGMENTS = (".claude", "worktrees")


def _is_under_worktrees(path: Path) -> bool:
    """Return True when ``path`` is at or below a ``.claude/worktrees/`` directory.

    A linked worktree scaffolded under ``.claude/worktrees/<name>/`` carries its
    own committed copy of ``groundtruth.toml``; a parent walk must not stop on
    that copy. The canonical root sits above the ``.claude/worktrees/`` segment.
    """
    parts = path.parts
    return any(pair == _WORKTREE_DIR_SEGMENTS for pair in zip(parts, parts[1:], strict=False))


def _git_common_dir() -> Path | None:
    """Return the absolute path of the shared git directory, or None.

    ``git rev-parse --git-common-dir`` reports the *shared* git directory: in a
    linked worktree that is the main worktree's ``.git``; in the main worktree
    it is ``.git`` itself. Its parent is the canonical main-worktree root from
    either location -- unlike ``--show-toplevel``, which reports the current
    (possibly worktree-local) checkout.

    Prefers ``--path-format=absolute`` (git >= 2.31); for older git, resolves
    the bare ``--git-common-dir`` output relative to cwd.
    """
    try:
        absolute = subprocess.check_output(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        absolute = ""
    if absolute and Path(absolute).is_absolute():
        return Path(absolute).resolve()

    try:
        bare = subprocess.check_output(
            ["git", "rev-parse", "--git-common-dir"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    if not bare:
        return None
    return (Path.cwd() / bare).resolve()


def _resolve_via_git_common_dir() -> Path | None:
    """Resolve the canonical main-worktree root via the shared git directory.

    Worktree-correct: the shared git directory's parent is the canonical root
    in both the main worktree and a linked worktree, validated by the
    ``groundtruth.toml`` marker.
    """
    common_dir = _git_common_dir()
    if common_dir is None:
        return None
    candidate = common_dir.parent
    if _has_marker(candidate):
        return candidate
    return None


def _resolve_via_parent_walk() -> Path | None:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if _has_marker(candidate) and not _is_under_worktrees(candidate):
            return candidate
    return None


def resolve_project_root() -> Path:
    """Resolve the GT-KB host root, fail-closed.

    Resolution order:

    1. ``GTKB_PROJECT_ROOT`` env var (must contain ``groundtruth.toml``).
    2. ``git rev-parse --git-common-dir`` from cwd: the shared git directory's
       parent is the canonical main-worktree root, validated by
       ``groundtruth.toml``. Worktree-correct -- a linked worktree resolves to
       the canonical root, not to itself.
    3. Walk parents from cwd looking for ``groundtruth.toml``, skipping any
       candidate at or below a ``.claude/worktrees/`` segment.

    Raises:
        ProjectRootNotFoundError: when no path yields a validated host root,
            or when ``GTKB_PROJECT_ROOT`` is set but the configured path
            lacks ``groundtruth.toml``.
    """
    env_root = _resolve_via_env_var()
    if env_root is not None:
        return env_root

    git_root = _resolve_via_git_common_dir()
    if git_root is not None:
        return git_root

    walk_root = _resolve_via_parent_walk()
    if walk_root is not None:
        return walk_root

    raise ProjectRootNotFoundError(
        f"No GT-KB host root found from cwd={Path.cwd().resolve()}. "
        f"A valid host root must contain {GROUNDTRUTH_MARKER}. "
        f"Set {PROJECT_ROOT_ENV_VAR} or run from inside a GT-KB checkout."
    )
