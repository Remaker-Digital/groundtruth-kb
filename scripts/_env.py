"""Standalone script interface to the canonical standard-library environment loader.

The fixed neighboring source file is loaded directly so setup scripts remain
usable before GT-KB or its dependencies are installed. Installed package callers
import groundtruth_kb.local_env normally. Both routes execute the same authored
implementation; this adapter does not search other checkouts or alter sys.path.
Importing either route leaves the environment unchanged.
"""

from __future__ import annotations

import runpy
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_LOADER = runpy.run_path(str(PROJECT_ROOT / "groundtruth-kb/src/groundtruth_kb/local_env.py"))
_LOADED: bool = False
_parse_env_file = _LOADER["_parse_env_file"]


def _default_env_local_path(project_root: Path = PROJECT_ROOT) -> Path:
    """Preserve the script interface's explicit-root and release-worktree routing."""
    return _LOADER["_default_env_local_path"](project_root)


def load_env_local(
    *,
    override: bool = False,
    check_only: bool = False,
    env_file: Path | None = None,
) -> dict[str, str]:
    """Load the selected file, defaulting only this script interface to its checkout."""
    global _LOADED
    values = _LOADER["load_env_local"](
        override=override, check_only=check_only, env_file=env_file, project_root=PROJECT_ROOT
    )
    if not check_only:
        _LOADED = True
    return values
