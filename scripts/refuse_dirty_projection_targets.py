#!/usr/bin/env python3
"""Refuse projection writes when any named target is git-dirty (WI-5999).

Callers pass the exact relative paths a run would write. This helper asks git
porcelain, including untracked files, and exits non-zero without writing
anything when any of those paths is dirty.

``--force-dirty PATH[,PATH...]`` must name every dirty path being overridden.
A bare ``--force`` is forbidden.

This slice is the shared preflight only. It does not write projection bytes
and does not wrap generators.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    from windows_subprocess import no_window_subprocess_kwargs
except ModuleNotFoundError:  # pragma: no cover - package-style test import
    from scripts.windows_subprocess import no_window_subprocess_kwargs

DIRTY_REFUSE_EXIT = 1
USAGE_REFUSE_EXIT = 2


class DirtyTargetError(RuntimeError):
    """Raised when git status cannot be collected fail-closed."""


def normalize_relative_path(project_root: Path, raw: str) -> str:
    """Return a posix-relative path inside *project_root*."""

    text = raw.strip().replace("\\", "/")
    if not text:
        raise DirtyTargetError("empty path is not a valid projection target")
    root = project_root.resolve()
    candidate = Path(text)
    path = candidate if candidate.is_absolute() else root / candidate
    try:
        relative = path.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise DirtyTargetError(f"path escapes project root: {raw}") from exc
    return relative.as_posix()


def parse_force_dirty_values(values: list[str] | None) -> list[str]:
    """Split repeatable ``--force-dirty PATH[,PATH...]`` values."""

    names: list[str] = []
    for raw in values or []:
        for part in raw.split(","):
            name = part.strip()
            if name:
                names.append(name)
    return names


def parse_porcelain_z(output: str) -> list[str]:
    """Return dirty paths from ``git status --porcelain=v1 -z`` output."""

    paths: list[str] = []
    tokens = output.split("\0")
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token or len(token) < 4:
            continue
        status = token[:2]
        first = token[3:].replace("\\", "/")
        if first:
            paths.append(first)
        if "R" in status or "C" in status:
            if index < len(tokens):
                second = tokens[index].replace("\\", "/")
                index += 1
                if second:
                    paths.append(second)
    return paths


def _run_git(project_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        **no_window_subprocess_kwargs(),
    )


def resolve_project_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    result = _run_git(Path.cwd(), ["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git rev-parse failed").strip()
        raise DirtyTargetError(detail)
    top = result.stdout.strip()
    if not top:
        raise DirtyTargetError("git rev-parse returned an empty toplevel")
    return Path(top)


def collect_dirty_target_paths(project_root: Path, targets: list[str]) -> list[str]:
    """Return the normalized targets that git porcelain reports as dirty."""

    if not targets:
        raise DirtyTargetError("at least one target path is required")
    normalized = [normalize_relative_path(project_root, target) for target in targets]
    result = _run_git(
        project_root,
        ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--", *normalized],
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "git status failed").strip()
        raise DirtyTargetError(detail)
    dirty = {normalize_relative_path(project_root, path) for path in parse_porcelain_z(result.stdout)}
    return sorted(path for path in normalized if path in dirty)


def unnamed_dirty_paths(dirty_paths: list[str], force_dirty: list[str], project_root: Path) -> list[str]:
    allowed = {normalize_relative_path(project_root, path) for path in force_dirty}
    return [path for path in dirty_paths if path not in allowed]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refuse when any named projection target is git-dirty.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "targets",
        nargs="+",
        help="Exact relative paths the caller would write.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Repository root. Defaults to `git rev-parse --show-toplevel`.",
    )
    parser.add_argument(
        "--force-dirty",
        action="append",
        default=[],
        metavar="PATH[,PATH...]",
        help="Named dirty-path override. Every dirty target must be listed.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.force:
        sys.stderr.write(
            "refuse-dirty-projection-targets: bare --force is forbidden; "
            "name every overridden dirty path with --force-dirty PATH[,PATH...]\n"
        )
        return USAGE_REFUSE_EXIT
    try:
        project_root = resolve_project_root(args.project_root)
        dirty_paths = collect_dirty_target_paths(project_root, args.targets)
        unnamed = unnamed_dirty_paths(
            dirty_paths,
            parse_force_dirty_values(args.force_dirty),
            project_root,
        )
    except DirtyTargetError as exc:
        sys.stderr.write(f"refuse-dirty-projection-targets: {exc}\n")
        return DIRTY_REFUSE_EXIT
    if not unnamed:
        return 0
    sys.stderr.write(
        "refuse-dirty-projection-targets: dirty targets "
        "(use --force-dirty PATH[,PATH...] to override named paths only):\n"
    )
    for path in unnamed:
        sys.stderr.write(f"  {path}\n")
    return DIRTY_REFUSE_EXIT


if __name__ == "__main__":
    sys.exit(main())
