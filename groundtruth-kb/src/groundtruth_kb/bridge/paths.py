# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GT-KB project root and bridge-state directory resolution.

RETIRED (2026-05-09): The smart-poller runtime that was the primary consumer of
``state_dir`` has been archived to ``archive/smart-poller-2026-05-09/``. The
cross-harness event-driven trigger
(``scripts/cross_harness_bridge_trigger.py``) reuses the same directory layout
under ``.gtkb-state/bridge-poller/`` for its dispatch-state file. This
module's project-root and state-dir resolution helpers remain valid for both
the retired smart-poller substrate and the current trigger.

Per ``.claude/rules/project-root-boundary.md`` and DELIB-S319 owner directives,
all live GT-KB bridge state must remain under the GT-KB host root.
Resolution is fail-closed: paths outside the validated host root raise
``StateDirOutOfRootError``; candidates without ``groundtruth.toml`` raise
``ProjectRootNotFoundError``. ``.git/`` is never sufficient on its own.

Authority: ``bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-008.md``
GO at REVISED-3.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

GROUNDTRUTH_MARKER = "groundtruth.toml"
PROJECT_ROOT_ENV_VAR = "GTKB_PROJECT_ROOT"
STATE_DIR_ENV_VAR = "GTKB_STATE_DIR"
DEFAULT_STATE_SUBDIR = (".gtkb-state", "bridge-poller")


class ProjectRootNotFoundError(Exception):
    """Raised when no GT-KB host root can be resolved.

    A valid host root must contain ``groundtruth.toml``. Per
    ``.claude/rules/project-root-boundary.md``, ``.git/`` alone is not
    sufficient.
    """


class StateDirOutOfRootError(Exception):
    """Raised when ``GTKB_STATE_DIR`` resolves outside the GT-KB host root.

    Per ``.claude/rules/project-root-boundary.md``, GT-KB state must remain
    in-root. Production code does not allow naming-convention bypasses for
    test-temp paths; tests use synthetic in-root projects under pytest
    ``tmp_path`` instead.
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


def _resolve_via_git_toplevel() -> Path | None:
    try:
        toplevel = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    if not toplevel:
        return None
    candidate = Path(toplevel).resolve()
    if _has_marker(candidate):
        return candidate
    return None


def _resolve_via_parent_walk() -> Path | None:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if _has_marker(candidate):
            return candidate
    return None


def resolve_project_root() -> Path:
    """Resolve the GT-KB host root, fail-closed.

    Resolution order:

    1. ``GTKB_PROJECT_ROOT`` env var (must contain ``groundtruth.toml``).
    2. ``git rev-parse --show-toplevel`` from cwd, validated by ``groundtruth.toml``.
    3. Walk parents from cwd looking for ``groundtruth.toml``.

    Raises:
        ProjectRootNotFoundError: when no path yields a validated host root,
            or when ``GTKB_PROJECT_ROOT`` is set but the configured path
            lacks ``groundtruth.toml``.
    """
    env_root = _resolve_via_env_var()
    if env_root is not None:
        return env_root

    git_root = _resolve_via_git_toplevel()
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


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_state_dir() -> Path:
    """Get the smart-poller state directory, fail-closed against out-of-root paths.

    Default: ``<project_root>/.gtkb-state/bridge-poller/``.

    Override: ``GTKB_STATE_DIR`` env var. Accepted only when its resolved path
    is relative to the validated project root. Out-of-root values raise
    ``StateDirOutOfRootError``.

    Raises:
        ProjectRootNotFoundError: when the project root cannot be resolved.
        StateDirOutOfRootError: when ``GTKB_STATE_DIR`` resolves outside root.
    """
    root = resolve_project_root()
    override = os.environ.get(STATE_DIR_ENV_VAR)
    if override:
        path = Path(override).resolve()
        if path.is_relative_to(root):
            return _ensure_dir(path)
        raise StateDirOutOfRootError(
            f"{STATE_DIR_ENV_VAR}={override} resolves to {path}, "
            f"which is outside project root {root}. "
            f"Per .claude/rules/project-root-boundary.md, GT-KB state "
            f"must remain in-root."
        )
    return _ensure_dir(root.joinpath(*DEFAULT_STATE_SUBDIR))
