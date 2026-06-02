#!/usr/bin/env python3
"""Read-only GT-KB isolation backstop.

Scans live platform-owned text surfaces for references to
``applications/<name>/``. Those references are allowed only on documented
historical, governance, migration, and test surfaces. Other occurrences are
reported as isolation regressions.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

APPLICATION_REF_RE = re.compile(r"applications/(?:<name>|[A-Za-z0-9_.-]+)(?:/[A-Za-z0-9_.:/@%+~#?&=,;!*'$()\\-]*)?")

TEXT_SUFFIXES = {
    ".cfg",
    ".cmd",
    ".ini",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

DEFAULT_SCAN_TARGETS = (
    "AGENTS.md",
    "CLAUDE.md",
    ".claude/rules",
    "config/governance",
    "groundtruth-kb/tests",
    "platform_tests",
    "scripts",
)

HISTORY_SCAN_TARGETS = (
    "bridge",
    "docs",
    "independent-progress-assessments",
    "memory",
)

SKIP_DIRS = {
    ".git",
    ".gtkb-state",
    ".hypothesis",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    ".agent",
    ".codex",
    "applications",
    "assets",
    "build",
    "dist",
    "gtkb-dashboard",
    "node_modules",
    "session-tmp",
    "worktrees",
}

SKIP_DIR_PREFIXES = (
    ".pytest-",
    ".ruff_cache",
    ".uv-",
    ".tmp",
    "GT-KB.tmp",
)

SKIP_FILE_PREFIXES = (
    "_temp_",
    "knowledge-export-",
)

ALLOWED_REFERENCE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("AGENTS.md", "root operating contract"),
    ("CLAUDE.md", "root operating contract"),
    (".claude/rules/*.md", "governance and operating-model rule"),
    ("bridge/**", "bridge history"),
    ("memory/**", "memory and decision history"),
    ("independent-progress-assessments/**", "review and assessment history"),
    ("docs/**", "documentation"),
    ("config/governance/**", "governance configuration"),
    ("groundtruth-kb/tests/**", "upstream test fixture"),
    ("platform_tests/**", "platform test fixture"),
    ("scripts/clean_adopter_validation.py", "adopter validation sandbox helper"),
    ("scripts/rehearse/**", "isolation rehearsal helper"),
    ("scripts/rollback_e1_write_set.py", "isolation migration rollback helper"),
    ("scripts/run_e1_step*.py", "isolation migration helper"),
    ("scripts/run_platform_tests_rename.py", "platform-test migration helper"),
    ("scripts/_capture_scaffold_golden.py", "scaffold golden capture helper"),
    ("scripts/_verify_slice8_closeout.py", "isolation closeout smoke helper"),
    ("scripts/release_candidate_gate.py", "release-gate application check inventory"),
)


@dataclass(frozen=True)
class Reference:
    path: str
    line: int
    column: int
    reference: str
    reason: str | None = None


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def _should_skip_dir(name: str) -> bool:
    return name in SKIP_DIRS or any(name.startswith(prefix) for prefix in SKIP_DIR_PREFIXES)


def _should_skip_file(name: str) -> bool:
    return any(name.startswith(prefix) for prefix in SKIP_FILE_PREFIXES)


def _iter_scan_targets(root: Path, *, include_history: bool = False) -> Iterable[Path]:
    target_names = DEFAULT_SCAN_TARGETS + (HISTORY_SCAN_TARGETS if include_history else ())
    for target_name in target_names:
        target = root / target_name
        if target.exists():
            yield target


def _iter_files(root: Path, *, include_history: bool = False) -> Iterable[Path]:
    self_path = Path(__file__).resolve()
    seen: set[Path] = set()
    for target in _iter_scan_targets(root, include_history=include_history):
        if target.is_file():
            candidates = [target]
        else:
            candidates = []
            for dirpath, dirnames, filenames in os.walk(target):
                dirnames[:] = sorted(name for name in dirnames if not _should_skip_dir(name))
                current_dir = Path(dirpath)
                candidates.extend(current_dir / filename for filename in sorted(filenames))
        for path in candidates:
            resolved = path.resolve()
            if resolved == self_path or resolved in seen or _should_skip_file(path.name):
                continue
            seen.add(resolved)
            if _is_text_file(path):
                yield path


def _allow_reason(rel_path: str) -> str | None:
    for pattern, reason in ALLOWED_REFERENCE_PATTERNS:
        if fnmatch.fnmatch(rel_path, pattern):
            return reason
    return None


def scan(root: Path = PROJECT_ROOT, *, include_history: bool = False) -> dict[str, object]:
    """Return the read-only isolation scan payload."""

    root = root.resolve()
    scanned_files: list[str] = []
    allowed: list[Reference] = []
    violations: list[Reference] = []

    for path in _iter_files(root, include_history=include_history):
        rel_path = _rel(path, root)
        scanned_files.append(rel_path)
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            violations.append(
                Reference(
                    path=rel_path,
                    line=0,
                    column=0,
                    reference="",
                    reason=f"unreadable file: {exc}",
                )
            )
            continue
        reason = _allow_reason(rel_path)
        for line_number, line in enumerate(lines, start=1):
            for match in APPLICATION_REF_RE.finditer(line):
                ref = Reference(
                    path=rel_path,
                    line=line_number,
                    column=match.start() + 1,
                    reference=match.group(0).rstrip(".,;:"),
                    reason=reason,
                )
                if reason:
                    allowed.append(ref)
                else:
                    violations.append(ref)

    return {
        "status": "fail" if violations else "pass",
        "project_root": str(root),
        "violations": [asdict(item) for item in violations],
        "allowed_references": [asdict(item) for item in allowed],
        "scanned_files": sorted(scanned_files),
    }


def _render_text(payload: dict[str, object]) -> str:
    lines = ["Isolation Program Backstop", "-" * 26]
    lines.append(f"status: {payload['status']}")
    lines.append(f"scanned_files: {len(payload['scanned_files'])}")
    lines.append(f"allowed_references: {len(payload['allowed_references'])}")
    lines.append(f"violations: {len(payload['violations'])}")
    for item in payload["violations"]:
        if not isinstance(item, dict):
            continue
        lines.append(f"- {item.get('path')}:{item.get('line')}:{item.get('column')} {item.get('reference')}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the read-only GT-KB isolation backstop.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--project-root", default=None, help="Override the project root to scan.")
    parser.add_argument(
        "--include-history",
        action="store_true",
        help="Also scan bridge, docs, memory, and assessment history surfaces.",
    )
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve() if args.project_root else PROJECT_ROOT
    payload = scan(root, include_history=args.include_history)
    if args.json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(_render_text(payload))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
