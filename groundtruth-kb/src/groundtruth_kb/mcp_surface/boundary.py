"""Root-boundary helpers for the GT-KB MCP surface.

Enforces ``ADR-ISOLATION-APPLICATION-PLACEMENT-001`` (the project-root
boundary) at the MCP tool layer. Every tool that accepts a filesystem path
MUST route it through ``assert_in_root`` or ``resolve_safe_path`` before
opening, reading, listing, or otherwise dereferencing the path.

Resolution always happens before the in-root check so traversal sequences
(``..``) cannot escape the root by lexical trick.
"""

from __future__ import annotations

import os
from pathlib import Path


class MCPBoundaryError(ValueError):
    """Raised when an MCP tool is asked to act on a path outside the GT-KB root."""


def _resolve_root() -> Path:
    """Resolve the GT-KB project root for boundary checks.

    Order:
      1. ``groundtruth_kb.bridge.paths.resolve_project_root`` if importable
         (the canonical resolver shared with the cross-harness trigger).
      2. ``GTKB_PROJECT_ROOT`` env var fallback for environments where the
         package self-import path is not yet active.

    Fail-closed: raises ``MCPBoundaryError`` if no root can be resolved.
    """

    try:
        from groundtruth_kb.bridge.paths import resolve_project_root

        return Path(resolve_project_root()).resolve()
    except Exception:  # intentional-catch: quality gate waiver
        pass
    env_root = os.environ.get("GTKB_PROJECT_ROOT")
    if env_root:
        candidate = Path(env_root).resolve()
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    raise MCPBoundaryError(
        "Cannot resolve GT-KB project root; set GTKB_PROJECT_ROOT or run from a directory containing groundtruth.toml."
    )


def assert_in_root(path: str | os.PathLike[str], *, root: Path | None = None) -> Path:
    """Assert ``path`` resolves to a location under the GT-KB root.

    Returns the resolved absolute path on success. Raises
    ``MCPBoundaryError`` otherwise.

    Parameters
    ----------
    path:
        The path to validate. May be absolute or relative; relative paths are
        resolved against the current working directory then checked against
        the root.
    root:
        Optional explicit root override. Primarily for testing; production
        callers should rely on the default resolution.
    """

    project_root = (root or _resolve_root()).resolve()
    candidate = Path(path).resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError as exc:
        raise MCPBoundaryError(f"Path '{candidate}' is outside the GT-KB root '{project_root}'.") from exc
    return candidate


def resolve_safe_path(path: str | os.PathLike[str], *, root: Path | None = None) -> Path:
    """Resolve a (possibly relative) path against the GT-KB root and bound-check it.

    Relative paths are joined to the resolved root before resolution, so a
    callsite that says ``resolve_safe_path("bridge/INDEX.md")`` always lands
    inside the root regardless of the current working directory.
    """

    project_root = (root or _resolve_root()).resolve()
    raw = Path(path)
    if not raw.is_absolute():
        raw = project_root / raw
    return assert_in_root(raw, root=project_root)
