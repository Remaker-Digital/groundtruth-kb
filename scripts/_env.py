"""Shared .env.local loader for scripts and tests.

Consolidates the repeated env-loading boilerplate found across ~27 files
into a single importable utility. Three loading modes:

  - setdefault (default): Only set vars not already in os.environ.
    This is the correct behavior for scripts — shell env takes precedence.

  - override: Overwrite existing env vars with .env.local values.
    Use sparingly; matches python-dotenv's default load_dotenv() behavior.

  - check_only: Parse and return the dict without touching os.environ.
    Useful for tests that want to inspect .env.local contents.

Usage (from any script or test):

    from scripts._env import load_env_local
    load_env_local()                        # setdefault mode
    load_env_local(override=True)           # override mode
    values = load_env_local(check_only=True) # returns dict, no side effects

The project root is auto-detected relative to this file (scripts/../).

R7 refactoring — session 31.
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

# Suppress system-level configuration warnings
os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
if os.name == "nt":
    # Redirect global configuration lookup to a safe writeable temp directory on Windows
    os.environ["XDG_CONFIG_HOME"] = tempfile.gettempdir()

# Project root: scripts/../
PROJECT_ROOT = Path(__file__).resolve().parent.parent

_LOADED: bool = False


def _parse_env_file(env_path: Path) -> dict[str, str]:
    """Parse a .env file into a dict, skipping comments and blank lines."""
    result: dict[str, str] = {}
    if not env_path.is_file():
        return result
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key:
            result[key] = value
    return result


def _default_env_local_path(project_root: Path = PROJECT_ROOT) -> Path:
    """Return the authoritative env file for this checkout.

    Normal checkouts use their own ``.env.local``. Release worktrees under the
    in-root ``.tmp`` directory may omit credential files; in that case, read the
    primary checkout's ``.env.local`` without copying secrets into the worktree.
    """
    root = project_root.resolve()
    local = root / ".env.local"
    if local.is_file():
        return local
    tmp_parent = root.parent
    primary = tmp_parent.parent
    if tmp_parent.name == ".tmp" and (primary / "groundtruth.toml").is_file():
        primary_env = primary / ".env.local"
        if primary_env.is_file():
            return primary_env
    return local


def load_env_local(
    *,
    override: bool = False,
    check_only: bool = False,
    env_file: Path | None = None,
) -> dict[str, str]:
    """Load .env.local into os.environ.

    Args:
        override: If True, overwrite existing env vars. Default False
            (setdefault behavior — existing env takes precedence).
        check_only: If True, parse and return dict without modifying
            os.environ. Useful for inspection/tests.
        env_file: Explicit path to env file. Defaults to PROJECT_ROOT / ".env.local".

    Returns:
        Dict of key-value pairs parsed from the file (regardless of whether
        they were applied to os.environ).
    """
    global _LOADED
    path = env_file or _default_env_local_path()
    values = _parse_env_file(path)

    if check_only:
        return values

    for key, value in values.items():
        if override:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)

    _LOADED = True
    return values
