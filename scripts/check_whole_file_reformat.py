#!/usr/bin/env python3
"""Detect whitespace-dominated whole-file reformat churn.

The detector compares normal git diff size with ``--ignore-all-space`` diff
size. A large raw diff with a tiny whitespace-ignored diff usually means an
editor or formatter rewrote most of a file while making little substantive
change. The check is read-only and can run in advisory mode or strict
pre-commit mode.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_MIN_RAW_CHANGES = 150
DEFAULT_MAX_IGNORED_CHANGES = 10
DEFAULT_MAX_IGNORED_RATIO = 0.15

DEFAULT_EXCLUDE_PATTERNS: tuple[str, ...] = (
    ".git/**",
    ".gtkb-state/**",
    ".venv/**",
    "groundtruth-kb/.venv/**",
    "node_modules/**",
    "dist/**",
    "build/**",
    "coverage/**",
    "htmlcov/**",
    "groundtruth-kb/site/**",
    "bridge/**",
    "memory/**",
    "independent-progress-assessments/**",
    "*.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Pipfile.lock",
    "poetry.lock",
    "*.min.js",
    "*.min.css",
    "*.map",
    "*.png",
    "*.jpg",
    "*.jpeg",
    "*.gif",
    "*.webp",
    "*.ico",
    "*.pdf",
    "*.zip",
    "*.gz",
    "*.db",
    "*.sqlite",
    "*.sqlite3",
)


@dataclass(frozen=True)
class NumstatEntry:
    path: str
    additions: int
    deletions: int
    binary: bool = False

    @property
    def changed_lines(self) -> int:
        return self.additions + self.deletions


@dataclass(frozen=True)
class DiffStats:
    path: str
    raw_additions: int
    raw_deletions: int
    ignored_additions: int = 0
    ignored_deletions: int = 0
    skipped_reason: str | None = None

    @property
    def raw_changes(self) -> int:
        return self.raw_additions + self.raw_deletions

    @property
    def ignored_changes(self) -> int:
        return self.ignored_additions + self.ignored_deletions

    @property
    def ignored_ratio(self) -> float:
        if self.raw_changes <= 0:
            return 0.0
        return self.ignored_changes / self.raw_changes


@dataclass(frozen=True)
class Finding:
    path: str
    raw_changes: int
    ignored_changes: int
    ignored_ratio: float
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "raw_changes": self.raw_changes,
            "whitespace_ignored_changes": self.ignored_changes,
            "whitespace_ignored_ratio": round(self.ignored_ratio, 4),
            "reason": self.reason,
        }


def _normalize_path(path: str | Path) -> str:
    return str(path).strip().replace("\\", "/")


def exclusion_reason(path: str, patterns: tuple[str, ...] = DEFAULT_EXCLUDE_PATTERNS) -> str | None:
    """Return the first generated/non-source exclusion reason for ``path``."""

    rel = _normalize_path(path)
    for pattern in patterns:
        if fnmatch.fnmatch(rel, pattern):
            return f"excluded_by_pattern:{pattern}"
    return None


def _parse_numstat(stdout: str) -> dict[str, NumstatEntry]:
    entries: dict[str, NumstatEntry] = {}
    for line in stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        additions_raw, deletions_raw, path_raw = parts
        path = _normalize_path(path_raw)
        if additions_raw == "-" or deletions_raw == "-":
            entries[path] = NumstatEntry(path=path, additions=0, deletions=0, binary=True)
            continue
        try:
            additions = int(additions_raw)
            deletions = int(deletions_raw)
        except ValueError:
            continue
        entries[path] = NumstatEntry(path=path, additions=additions, deletions=deletions)
    return entries


def _run_git_numstat(
    root: Path,
    *,
    staged: bool,
    ignore_whitespace: bool,
    paths: list[str] | None,
) -> dict[str, NumstatEntry]:
    cmd = ["git", "diff", "--numstat", "--diff-filter=ACMRT"]
    if staged:
        cmd.append("--cached")
    if ignore_whitespace:
        cmd.append("--ignore-all-space")
    if paths:
        cmd.extend(["--", *paths])

    completed = subprocess.run(
        cmd,
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    return _parse_numstat(completed.stdout)


def collect_diff_stats(
    root: Path,
    *,
    staged: bool = False,
    paths: list[str] | None = None,
    exclude_patterns: tuple[str, ...] = DEFAULT_EXCLUDE_PATTERNS,
) -> list[DiffStats]:
    raw_entries = _run_git_numstat(root, staged=staged, ignore_whitespace=False, paths=paths)
    ignored_entries = _run_git_numstat(root, staged=staged, ignore_whitespace=True, paths=paths)

    stats: list[DiffStats] = []
    for path in sorted(raw_entries):
        raw = raw_entries[path]
        if raw.binary:
            stats.append(DiffStats(path=path, raw_additions=0, raw_deletions=0, skipped_reason="binary_diff"))
            continue
        skip_reason = exclusion_reason(path, exclude_patterns)
        if skip_reason:
            stats.append(
                DiffStats(
                    path=path,
                    raw_additions=raw.additions,
                    raw_deletions=raw.deletions,
                    skipped_reason=skip_reason,
                )
            )
            continue
        ignored = ignored_entries.get(path)
        stats.append(
            DiffStats(
                path=path,
                raw_additions=raw.additions,
                raw_deletions=raw.deletions,
                ignored_additions=0 if ignored is None or ignored.binary else ignored.additions,
                ignored_deletions=0 if ignored is None or ignored.binary else ignored.deletions,
            )
        )
    return stats


def classify_finding(
    stats: DiffStats,
    *,
    min_raw_changes: int = DEFAULT_MIN_RAW_CHANGES,
    max_ignored_changes: int = DEFAULT_MAX_IGNORED_CHANGES,
    max_ignored_ratio: float = DEFAULT_MAX_IGNORED_RATIO,
) -> Finding | None:
    if stats.skipped_reason is not None or stats.raw_changes < min_raw_changes:
        return None

    if stats.ignored_changes <= max_ignored_changes:
        reason = f"raw_changes>={min_raw_changes} and whitespace_ignored_changes<={max_ignored_changes}"
        return Finding(
            path=stats.path,
            raw_changes=stats.raw_changes,
            ignored_changes=stats.ignored_changes,
            ignored_ratio=stats.ignored_ratio,
            reason=reason,
        )

    if stats.ignored_ratio <= max_ignored_ratio:
        reason = f"raw_changes>={min_raw_changes} and whitespace_ignored_ratio<={max_ignored_ratio:.3f}"
        return Finding(
            path=stats.path,
            raw_changes=stats.raw_changes,
            ignored_changes=stats.ignored_changes,
            ignored_ratio=stats.ignored_ratio,
            reason=reason,
        )

    return None


def evaluate(
    stats: list[DiffStats],
    *,
    min_raw_changes: int = DEFAULT_MIN_RAW_CHANGES,
    max_ignored_changes: int = DEFAULT_MAX_IGNORED_CHANGES,
    max_ignored_ratio: float = DEFAULT_MAX_IGNORED_RATIO,
) -> dict[str, Any]:
    findings = [
        finding
        for item in stats
        if (
            finding := classify_finding(
                item,
                min_raw_changes=min_raw_changes,
                max_ignored_changes=max_ignored_changes,
                max_ignored_ratio=max_ignored_ratio,
            )
        )
        is not None
    ]
    skipped = [{"path": item.path, "reason": item.skipped_reason} for item in stats if item.skipped_reason is not None]
    checked = [item for item in stats if item.skipped_reason is None]
    return {
        "status": "fail" if findings else "pass",
        "findings": [finding.as_dict() for finding in findings],
        "checked_count": len(checked),
        "skipped": skipped,
        "skipped_count": len(skipped),
        "thresholds": {
            "min_raw_changes": min_raw_changes,
            "max_ignored_changes": max_ignored_changes,
            "max_ignored_ratio": max_ignored_ratio,
        },
    }


def _format_human(result: dict[str, Any], *, strict: bool) -> str:
    if result["status"] == "pass":
        return (
            "[PASS] whole-file reformat check: no suspicious files "
            f"({result['checked_count']} checked, {result['skipped_count']} skipped)"
        )

    prefix = "[FAIL]" if strict else "[WARN]"
    lines = [
        f"{prefix} whole-file reformat check: suspicious whitespace-dominated diff(s)",
        "",
    ]
    for finding in result["findings"]:
        lines.append(
            "  - {path}: raw_changes={raw}, whitespace_ignored_changes={ignored}, "
            "ratio={ratio:.4f}, reason={reason}".format(
                path=finding["path"],
                raw=finding["raw_changes"],
                ignored=finding["whitespace_ignored_changes"],
                ratio=finding["whitespace_ignored_ratio"],
                reason=finding["reason"],
            )
        )
    if not strict:
        lines.extend(
            [
                "",
                "  Advisory mode only; pass --strict to make this a blocking pre-commit check.",
            ]
        )
    return "\n".join(lines)


def _repository_root(start: Path) -> Path:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=start,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return start.resolve()
    root = completed.stdout.strip()
    return Path(root).resolve() if root else start.resolve()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Inspect staged changes with git diff --cached.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when suspicious churn is detected.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--project-root", type=Path, default=None, help="Repository root; defaults to cwd git root.")
    parser.add_argument("--paths", nargs="*", default=None, help="Optional pathspecs to limit the diff.")
    parser.add_argument("--min-raw-changes", type=int, default=DEFAULT_MIN_RAW_CHANGES)
    parser.add_argument("--max-ignored-changes", type=int, default=DEFAULT_MAX_IGNORED_CHANGES)
    parser.add_argument("--max-ignored-ratio", type=float, default=DEFAULT_MAX_IGNORED_RATIO)
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional fnmatch-style path exclusion pattern. May be passed multiple times.",
    )
    parser.add_argument(
        "--no-default-excludes",
        action="store_true",
        help="Disable built-in generated/binary-adjacent path exclusions.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    cwd_root = _repository_root(Path.cwd())
    root = (args.project_root or cwd_root).resolve()
    patterns = tuple(args.exclude) if args.no_default_excludes else (*DEFAULT_EXCLUDE_PATTERNS, *args.exclude)

    try:
        stats = collect_diff_stats(
            root,
            staged=args.staged,
            paths=[_normalize_path(path) for path in args.paths] if args.paths else None,
            exclude_patterns=patterns,
        )
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f"whole-file reformat check error: git diff failed with exit {exc.returncode}\n")
        if exc.stderr:
            sys.stderr.write(exc.stderr)
        return 2

    result = evaluate(
        stats,
        min_raw_changes=args.min_raw_changes,
        max_ignored_changes=args.max_ignored_changes,
        max_ignored_ratio=args.max_ignored_ratio,
    )
    if args.json:
        sys.stdout.write(json.dumps(result, indent=2, sort_keys=True))
        sys.stdout.write("\n")
    else:
        stream = sys.stderr if result["status"] == "fail" and args.strict else sys.stdout
        stream.write(_format_human(result, strict=args.strict))
        stream.write("\n")

    if result["status"] == "fail" and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
