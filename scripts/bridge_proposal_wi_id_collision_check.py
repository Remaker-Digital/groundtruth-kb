#!/usr/bin/env python3
"""Check bridge proposals for cited work-item ID collisions.

The checker scans proposal text for GTKB-* and WI-* identifiers outside fenced
code blocks, then cross-references those IDs against the MemBase
``current_work_items`` view. A cited ID is a collision when it already exists in
MemBase and differs from the proposal's declared ``Work Item:`` metadata.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "groundtruth.db"
DB_ENV_VAR = "GTKB_WI_COLLISION_DB_PATH"

WORK_ITEM_RE = re.compile(r"(?im)^Work Item:\s*`?(?P<work_item>[^`\n]+?)`?\s*$")
ID_RE = re.compile(r"\b(?:GTKB-[A-Z]+-\d+|WI-\d+)\b")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INDEX_STATUS_RE = re.compile(r"^(?:NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY):\s*(bridge/.+\.md)$")


@dataclass(frozen=True)
class CitedId:
    cited_id: str
    exists_in_membase: bool
    matches_declared: bool
    collision: bool
    title: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "cited_id": self.cited_id,
            "exists_in_membase": self.exists_in_membase,
            "matches_declared": self.matches_declared,
            "collision": self.collision,
            "title": self.title,
        }


@dataclass(frozen=True)
class CollisionResult:
    declared_work_item: str | None
    cited_ids: tuple[CitedId, ...]

    @property
    def collisions(self) -> tuple[CitedId, ...]:
        return tuple(item for item in self.cited_ids if item.collision)

    @property
    def has_collisions(self) -> bool:
        return bool(self.collisions)

    def to_dict(self) -> dict[str, Any]:
        return {
            "declared_work_item": self.declared_work_item,
            "has_collisions": self.has_collisions,
            "cited_ids": [item.to_dict() for item in self.cited_ids],
            "collisions": [item.to_dict() for item in self.collisions],
        }


def strip_fenced_code_blocks(text: str) -> str:
    """Return text with fenced code blocks removed."""
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def parse_declared_work_item(text: str) -> str | None:
    match = WORK_ITEM_RE.search(text)
    if not match:
        return None
    return match.group("work_item").strip()


def extract_cited_ids(text: str) -> list[str]:
    seen: set[str] = set()
    ids: list[str] = []
    for match in ID_RE.finditer(strip_fenced_code_blocks(text)):
        item_id = match.group(0)
        if item_id not in seen:
            ids.append(item_id)
            seen.add(item_id)
    return ids


def _db_path(db_path: Path | str | None = None) -> Path:
    if db_path is not None:
        return Path(db_path)
    env_value = os.environ.get(DB_ENV_VAR)
    return Path(env_value) if env_value else DEFAULT_DB_PATH


def _lookup_work_item(conn: sqlite3.Connection, item_id: str) -> sqlite3.Row | None:
    conn.row_factory = sqlite3.Row
    return conn.execute(
        "SELECT id, title FROM current_work_items WHERE id = ? LIMIT 1",
        (item_id,),
    ).fetchone()


def check_content(
    text: str,
    declared_wi: str | None = None,
    *,
    db_path: Path | str | None = None,
) -> CollisionResult:
    declared = declared_wi or parse_declared_work_item(text)
    cited_ids = extract_cited_ids(text)
    path = _db_path(db_path)
    if not path.is_file():
        raise FileNotFoundError(f"MemBase database not found: {path}")

    rows: list[CitedId] = []
    with sqlite3.connect(path) as conn:
        for cited_id in cited_ids:
            row = _lookup_work_item(conn, cited_id)
            exists = row is not None
            matches_declared = bool(declared) and cited_id == declared
            rows.append(
                CitedId(
                    cited_id=cited_id,
                    exists_in_membase=exists,
                    matches_declared=matches_declared,
                    collision=bool(declared) and exists and not matches_declared,
                    title=row["title"] if row is not None and "title" in row else None,
                )
            )
    return CollisionResult(declared_work_item=declared, cited_ids=tuple(rows))


def format_markdown(result: CollisionResult) -> str:
    lines = [
        "## Collision Check",
        "",
        f"- declared_work_item: `{result.declared_work_item or '(unknown)'}`",
        f"- has_collisions: `{str(result.has_collisions).lower()}`",
        "",
        "| cited_id | exists_in_membase | matches_declared | collision |",
        "|---|---:|---:|---:|",
    ]
    for item in result.cited_ids:
        lines.append(
            f"| `{item.cited_id}` | `{str(item.exists_in_membase).lower()}` | "
            f"`{str(item.matches_declared).lower()}` | `{str(item.collision).lower()}` |"
        )
    return "\n".join(lines) + "\n"


def _read_index_target(bridge_id: str, *, project_root: Path = PROJECT_ROOT) -> Path:
    index_path = project_root / "bridge" / "INDEX.md"
    text = index_path.read_text(encoding="utf-8")
    in_doc = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("Document:"):
            in_doc = line.removeprefix("Document:").strip() == bridge_id
            continue
        if not in_doc:
            continue
        if not line:
            break
        match = INDEX_STATUS_RE.match(line)
        if match:
            return project_root / match.group(1)
    raise FileNotFoundError(f"No bridge document found in INDEX for {bridge_id!r}")


def _content_from_args(args: argparse.Namespace) -> str:
    if args.stdin:
        return sys.stdin.read()
    if args.content_file:
        return Path(args.content_file).read_text(encoding="utf-8")
    if args.bridge_id:
        return _read_index_target(args.bridge_id).read_text(encoding="utf-8")
    raise SystemExit("One of --bridge-id, --content-file, or --stdin is required.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-id", help="Bridge document name from bridge/INDEX.md.")
    parser.add_argument("--content-file", type=Path, help="Path to proposal content to scan.")
    parser.add_argument("--stdin", action="store_true", help="Read proposal content from stdin.")
    parser.add_argument("--declared-wi", help="Override the declared Work Item metadata.")
    parser.add_argument("--db-path", type=Path, default=None, help="MemBase SQLite database path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when collisions exist.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    content = _content_from_args(args)
    result = check_content(content, args.declared_wi, db_path=args.db_path)
    if args.json:
        sys.stdout.write(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n")
    else:
        sys.stdout.write(format_markdown(result))
    return 3 if args.strict and result.has_collisions else 0


if __name__ == "__main__":
    raise SystemExit(main())
