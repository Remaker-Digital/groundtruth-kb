#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Read-only audit for source citation anchors that no longer resolve."""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

ANCHOR_RE = re.compile(r"\b(?P<prefix>SPEC|GOV|DCL|ADR|PB|REQ|DELIB|WI|GTKB)-[A-Z0-9][A-Z0-9_-]*\b")
BRIDGE_RE = re.compile(r"\bbridge/[A-Za-z0-9_.-]+-\d{3}\.md\b")
SOURCE_EXTENSIONS = {".py", ".md"}
DEFAULT_SCAN_DIRS = (
    "scripts",
    "groundtruth-kb/src",
    "groundtruth-kb/tests",
    "platform_tests",
    "tests",
    ".claude/hooks",
    ".codex/gtkb-hooks",
)
EXCLUDED_DIRS = {
    ".git",
    ".gtkb-state",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


@dataclass(frozen=True)
class Citation:
    anchor: str
    kind: str
    path: str
    line: int


@dataclass(frozen=True)
class AuditResult:
    root: str
    db_path: str
    scanned_files: int
    resolved: dict[str, int]
    orphans: list[Citation]

    def to_jsonable(self) -> dict[str, object]:
        payload = asdict(self)
        payload["orphans"] = [asdict(orphan) for orphan in self.orphans]
        return payload


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    ).fetchone()
    return row is not None


def load_resolvable_ids(db_path: Path) -> dict[str, set[str]]:
    ids: dict[str, set[str]] = {"spec": set(), "deliberation": set(), "work_item": set()}
    if not db_path.exists():
        return ids
    conn = sqlite3.connect(str(db_path))
    try:
        table_map = {
            "specifications": "spec",
            "deliberations": "deliberation",
            "work_items": "work_item",
        }
        for table, kind in table_map.items():
            if not _table_exists(conn, table):
                continue
            ids[kind].update(row[0] for row in conn.execute(f"SELECT DISTINCT id FROM {table}"))
    finally:
        conn.close()
    return ids


def _citation_kind(anchor: str) -> str:
    prefix = anchor.split("-", 1)[0]
    if prefix == "DELIB":
        return "deliberation"
    if prefix in {"WI", "GTKB"}:
        return "work_item"
    return "spec"


def _scan_roots(root: Path, scan_dirs: Iterable[Path] | None) -> list[Path]:
    if scan_dirs:
        return [path if path.is_absolute() else root / path for path in scan_dirs]
    configured = [root / rel for rel in DEFAULT_SCAN_DIRS if (root / rel).exists()]
    return configured if configured else [root]


def iter_source_files(root: Path, scan_dirs: Iterable[Path] | None = None) -> Iterable[Path]:
    for scan_root in _scan_roots(root, scan_dirs):
        if scan_root.is_file():
            candidates = [scan_root]
        elif scan_root.is_dir():
            candidates = scan_root.rglob("*")
        else:
            continue
        for path in candidates:
            if not path.is_file() or path.suffix not in SOURCE_EXTENSIONS:
                continue
            if any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts):
                continue
            yield path


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _find_citations(path: Path, root: Path) -> Iterable[Citation]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")
    rel_path = _rel(path, root)
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in ANCHOR_RE.finditer(line):
            anchor = match.group(0)
            yield Citation(anchor=anchor, kind=_citation_kind(anchor), path=rel_path, line=line_no)
        for match in BRIDGE_RE.finditer(line):
            yield Citation(anchor=match.group(0), kind="bridge", path=rel_path, line=line_no)


def audit_root(root: Path, db_path: Path, scan_dirs: Iterable[Path] | None = None) -> AuditResult:
    root = root.resolve()
    db_path = db_path.resolve()
    resolvable = load_resolvable_ids(db_path)
    resolved: Counter[str] = Counter()
    orphans: list[Citation] = []
    scanned_files = 0

    for path in iter_source_files(root, scan_dirs):
        scanned_files += 1
        for citation in _find_citations(path, root):
            if citation.kind == "bridge":
                is_resolved = (root / citation.anchor).is_file()
            else:
                is_resolved = citation.anchor in resolvable[citation.kind]
            if is_resolved:
                resolved[citation.kind] += 1
            else:
                orphans.append(citation)

    return AuditResult(
        root=str(root),
        db_path=str(db_path),
        scanned_files=scanned_files,
        resolved={kind: resolved.get(kind, 0) for kind in ("spec", "deliberation", "work_item", "bridge")},
        orphans=orphans,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root to scan.")
    parser.add_argument("--db", type=Path, default=None, help="Knowledge DB path; defaults to <root>/groundtruth.db.")
    parser.add_argument(
        "--scan-dir",
        type=Path,
        action="append",
        default=None,
        help="Directory or file to scan, relative to --root. May be supplied more than once.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if not root.exists():
        print(json.dumps({"error": f"root not found: {root}"}), file=sys.stderr)
        return 2
    db_path = args.db.resolve() if args.db else root / "groundtruth.db"
    result = audit_root(root, db_path, args.scan_dir)
    print(json.dumps(result.to_jsonable(), indent=2, sort_keys=True))
    return 1 if result.orphans else 0


if __name__ == "__main__":
    raise SystemExit(main())
