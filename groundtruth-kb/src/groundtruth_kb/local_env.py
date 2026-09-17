"""Explicit local environment loading shared by installed code and standalone scripts.

Importing this standard-library module does not read files or change the
environment. Callers select an environment file or a checkout root; the package
installation directory is never used as a credential root. Values retain the
existing simple parser's literal quoting and last-assignment behavior.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

from __future__ import annotations

import os
from pathlib import Path


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


def _default_env_local_path(project_root: Path) -> Path:
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
    project_root: Path | None = None,
) -> dict[str, str]:
    """Load .env.local into os.environ.

    Args:
        override: If True, overwrite existing env vars. Default False
            (setdefault behavior — existing env takes precedence).
        check_only: If True, parse and return dict without modifying
            os.environ. Useful for inspection/tests.
        env_file: Explicit file, taking precedence over project_root.
        project_root: Explicit checkout root when env_file is omitted.

    Returns:
        Dict of key-value pairs parsed from the file (regardless of whether
        they were applied to os.environ).
    """
    if env_file is None:
        if project_root is None:
            raise ValueError("Select env_file or project_root explicitly")
        env_file = _default_env_local_path(project_root)
    path = env_file
    values = _parse_env_file(path)

    if check_only:
        return values

    for key, value in values.items():
        if override:
            os.environ[key] = value
        else:
            os.environ.setdefault(key, value)

    return values
