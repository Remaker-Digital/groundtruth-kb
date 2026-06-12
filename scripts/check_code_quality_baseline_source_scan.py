#!/usr/bin/env python3
"""Tier-3 source/diff scanner for mechanical Code Quality Baseline rules."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

SECRET_RE = re.compile(r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]")
ABS_PATH_RE = re.compile(r"[A-Za-z]:\\|/Users/|/home/")
COMPLEXITY_THRESHOLD = 10


def _diff(project_root: Path, since: str, paths: list[str]) -> str:
    command = ["git", "diff", "--unified=0", since, "--", *paths]
    result = subprocess.run(
        command,
        cwd=project_root,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    return result.stdout


def _changed_python_files(project_root: Path, since: str, paths: list[str]) -> list[Path]:
    command = ["git", "diff", "--name-only", since, "--", "*.py", *paths]
    result = subprocess.run(
        command,
        cwd=project_root,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    files: list[Path] = []
    for line in result.stdout.splitlines():
        path = project_root / line
        if path.exists():
            files.append(path)
    return files


def _complexity_violations(project_root: Path, since: str, paths: list[str]) -> list[str]:
    try:
        from radon.complexity import cc_visit
    except ModuleNotFoundError:
        return ["CQ-COMPLEXITY-001: radon not installed; complexity scan skipped"]

    violations: list[str] = []
    for file_path in _changed_python_files(project_root, since, paths):
        try:
            blocks = cc_visit(file_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            violations.append(f"CQ-COMPLEXITY-001: unable to parse {file_path.relative_to(project_root)}: {exc}")
            continue
        for block in blocks:
            if block.complexity > COMPLEXITY_THRESHOLD:
                violations.append(
                    "CQ-COMPLEXITY-001: "
                    f"{file_path.relative_to(project_root)}:{block.lineno} "
                    f"{block.name} complexity {block.complexity} exceeds {COMPLEXITY_THRESHOLD}"
                )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", required=True)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("paths", nargs="*", help="Optional git pathspecs limiting the scanned diff.")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    diff = _diff(project_root, args.since, args.paths)
    violations: list[str] = []
    for line in diff.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        if SECRET_RE.search(line):
            violations.append(f"CQ-SECRETS-001: {line[:120]}")
        if ABS_PATH_RE.search(line):
            violations.append(f"CQ-PATHS-001: {line[:120]}")
        if re.search(r"(?<![A-Za-z_])\d{4,}(?![A-Za-z_])", line):
            violations.append(f"CQ-CONSTANTS-001: {line[:120]}")
    violations.extend(_complexity_violations(project_root, args.since, args.paths))
    if violations:
        print("\n".join(violations))
        return 0 if all("radon not installed" in violation for violation in violations) else 1
    print("Code Quality Baseline source scan clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
