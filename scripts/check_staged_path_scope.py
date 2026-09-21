#!/usr/bin/env python3
"""Check that git staged files do not exceed the declared scope (WI-6690).

Prevents cross-session index contamination during concurrent multi-agent operation.
Compares staged paths with explicitly supplied paths. Reports exact matches,
valid subsets and excess paths; warns when no comparison scope is supplied.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import sys
from pathlib import Path


def _normalize_path(p: str) -> str:
    norm = p.strip().replace("\\", "/")
    while norm.startswith("./"):
        norm = norm[2:]
    return norm


def get_staged_paths(project_root: Path) -> list[str]:
    """Return list of repository-relative paths currently staged in git."""
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        return [_normalize_path(line) for line in lines]
    except Exception as exc:
        print(f"WARN [check_staged_path_scope]: Unable to read git staged paths: {exc}", file=sys.stderr)
        return []


def resolve_declared_scope(
    project_root: Path,
    explicit_paths: list[str] | None = None,
) -> tuple[list[str] | None, str]:
    """Resolve declared scope paths and source description."""
    if explicit_paths is not None:
        normalized = [_normalize_path(p) for p in explicit_paths]
        return normalized, "explicit argument (--expect-paths)"

    return None, "none"


def matches_declared_pattern(staged_path: str, declared_pattern: str) -> bool:
    """Check if staged path matches declared path or glob."""
    if staged_path == declared_pattern:
        return True
    if os.name == "nt" and staged_path.lower() == declared_pattern.lower():
        return True
    if fnmatch.fnmatch(staged_path, declared_pattern):
        return True
    return bool(os.name == "nt" and fnmatch.fnmatch(staged_path.lower(), declared_pattern.lower()))


def check_staged_scope(
    project_root: Path,
    explicit_paths: list[str] | None = None,
    staged_paths_override: list[str] | None = None,
) -> tuple[int, str]:
    """Evaluate staged paths against declared scope.

    Returns (exit_code, message).
    """
    declared_paths, source_desc = resolve_declared_scope(project_root, explicit_paths)
    if staged_paths_override is not None:
        staged_paths = [_normalize_path(p) for p in staged_paths_override]
    else:
        staged_paths = get_staged_paths(project_root)

    if not staged_paths:
        return 0, "PASS staged-path scope: no files staged in git index."

    if declared_paths is None:
        return 0, (
            f"WARN staged-path scope: {len(staged_paths)} file(s) staged, but no explicit paths supplied; "
            "comparison not performed."
        )

    extra_paths: list[str] = []
    for sp in staged_paths:
        if not any(matches_declared_pattern(sp, dp) for dp in declared_paths):
            extra_paths.append(sp)

    if not extra_paths:
        if len(staged_paths) < len(declared_paths):
            return 0, (
                f"PASS staged-path scope: {len(staged_paths)} of {len(declared_paths)} declared path(s) "
                f"staged (valid subset; source: {source_desc})."
            )
        return (
            0,
            f"PASS staged-path scope: all {len(staged_paths)} staged file(s) match declared scope ({source_desc}).",
        )

    lines = [
        f"FAIL staged-path scope: {len(extra_paths)} staged path(s) exceed declared scope ({source_desc}).",
        "Declared scope:",
    ]
    for dp in declared_paths:
        lines.append(f"  + {dp}")
    lines.append("Staged paths outside declared scope (cross-session contamination risk):")
    for ep in extra_paths:
        lines.append(f"  - {ep}")
    lines.append("Remedy: Unstage extra files using 'git restore --staged <file>' before committing.")

    return 1, "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check staged git paths against declared scope (WI-6690).")
    parser.add_argument(
        "--expect-paths",
        nargs="*",
        default=None,
        help="Explicit expected file paths for comparison.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the GT-KB project.",
    )

    args = parser.parse_args()
    code, message = check_staged_scope(args.project_root, args.expect_paths)
    if code != 0:
        print(message, file=sys.stderr)
    else:
        print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
