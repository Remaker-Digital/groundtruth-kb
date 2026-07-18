#!/usr/bin/env python3
"""Check bridge proposals for cited work-item ID collisions.

The checker scans proposal text for GTKB-* and WI-* identifiers outside fenced
code blocks, then cross-references those IDs against the MemBase
``current_work_items`` view. A cited ID is a collision when it already exists in
MemBase, differs from the proposal's declared ``Work Item:`` metadata, and is
not validated by established related-work metadata.
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
CANONICAL_WI_RE = re.compile(r"^WI-\d+$")
RELATED_WORK_ITEMS_RE = re.compile(r"^Related Work Items:\s*(?P<value>.*)$", re.MULTILINE)
RELATED_WORK_ITEMS_JSON_RE = re.compile(r"^related_work_items:\s*(?P<value>.*)$", re.MULTILINE)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
PROPOSAL_STATUSES = {"NEW", "REVISED"}


@dataclass(frozen=True)
class RelationshipError:
    code: str
    message: str
    source: str
    work_item_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "source": self.source,
            "work_item_id": self.work_item_id,
        }


@dataclass(frozen=True)
class RelatedWorkItem:
    work_item_id: str
    sources: tuple[str, ...]
    exists_in_membase: bool
    title: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "work_item_id": self.work_item_id,
            "sources": list(self.sources),
            "exists_in_membase": self.exists_in_membase,
            "title": self.title,
        }


@dataclass(frozen=True)
class CitedId:
    cited_id: str
    exists_in_membase: bool
    matches_declared: bool
    related_work_item: bool
    collision: bool
    classification: str
    title: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "cited_id": self.cited_id,
            "exists_in_membase": self.exists_in_membase,
            "matches_declared": self.matches_declared,
            "related_work_item": self.related_work_item,
            "collision": self.collision,
            "classification": self.classification,
            "title": self.title,
        }


@dataclass(frozen=True)
class CollisionResult:
    declared_work_item: str | None
    cited_ids: tuple[CitedId, ...]
    related_work_items: tuple[RelatedWorkItem, ...] = ()
    relationship_errors: tuple[RelationshipError, ...] = ()

    @property
    def collisions(self) -> tuple[CitedId, ...]:
        return tuple(item for item in self.cited_ids if item.collision)

    @property
    def has_collisions(self) -> bool:
        """Return whether the advisory hook has an actionable finding.

        Existing foreign-ID collisions and invalid relationship metadata both
        require attention. The concrete collision records remain available
        separately through ``collisions``.
        """
        return bool(self.collisions or self.relationship_errors)

    @property
    def has_relationship_errors(self) -> bool:
        return bool(self.relationship_errors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "declared_work_item": self.declared_work_item,
            "has_collisions": self.has_collisions,
            "has_relationship_errors": self.has_relationship_errors,
            "cited_ids": [item.to_dict() for item in self.cited_ids],
            "collisions": [item.to_dict() for item in self.collisions],
            "validated_related_ids": [item.work_item_id for item in self.related_work_items],
            "related_work_items": [item.to_dict() for item in self.related_work_items],
            "relationship_errors": [item.to_dict() for item in self.relationship_errors],
        }


@dataclass(frozen=True)
class ParsedRelatedWorkItems:
    ordered_ids: tuple[str, ...]
    sources_by_id: dict[str, tuple[str, ...]]
    errors: tuple[RelationshipError, ...]


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


def _metadata_error(
    code: str,
    message: str,
    source: str,
    work_item_id: str | None = None,
) -> RelationshipError:
    return RelationshipError(
        code=code,
        message=message,
        source=source,
        work_item_id=work_item_id,
    )


def _parse_human_related_value(value: str) -> tuple[list[str], list[RelationshipError]]:
    source = "Related Work Items"
    if not value.strip():
        return [], [_metadata_error("empty_related_work_items", "Related Work Items must not be empty.", source)]

    ids: list[str] = []
    errors: list[RelationshipError] = []
    seen: set[str] = set()
    for raw_item in value.split(","):
        item_id = raw_item.strip().strip("`").strip()
        if not item_id or CANONICAL_WI_RE.fullmatch(item_id) is None:
            errors.append(
                _metadata_error(
                    "invalid_related_work_item",
                    f"Related Work Items member {raw_item.strip()!r} is not a canonical WI-[0-9]+ ID.",
                    source,
                    item_id or None,
                )
            )
            continue
        if item_id in seen:
            errors.append(
                _metadata_error(
                    "duplicate_related_work_item",
                    f"Related Work Items contains duplicate ID {item_id}.",
                    source,
                    item_id,
                )
            )
            continue
        seen.add(item_id)
        ids.append(item_id)
    return ids, errors


def _parse_json_related_value(value: str) -> tuple[list[str], list[RelationshipError]]:
    source = "related_work_items"
    if not value.strip():
        return [], [_metadata_error("empty_related_work_items", "related_work_items must not be empty.", source)]
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError as exc:
        return [], [
            _metadata_error(
                "malformed_related_work_items_json",
                f"related_work_items must contain valid JSON: {exc.msg}.",
                source,
            )
        ]
    if not isinstance(decoded, list):
        return [], [
            _metadata_error(
                "invalid_related_work_items_json_type",
                "related_work_items must decode to a JSON list.",
                source,
            )
        ]
    if not decoded:
        return [], [_metadata_error("empty_related_work_items", "related_work_items must not be empty.", source)]

    ids: list[str] = []
    errors: list[RelationshipError] = []
    seen: set[str] = set()
    for value_item in decoded:
        if not isinstance(value_item, str):
            errors.append(
                _metadata_error(
                    "non_string_related_work_item",
                    "Every related_work_items member must be a string.",
                    source,
                )
            )
            continue
        item_id = value_item.strip()
        if CANONICAL_WI_RE.fullmatch(item_id) is None:
            errors.append(
                _metadata_error(
                    "invalid_related_work_item",
                    f"related_work_items member {value_item!r} is not a canonical WI-[0-9]+ ID.",
                    source,
                    item_id or None,
                )
            )
            continue
        if item_id in seen:
            errors.append(
                _metadata_error(
                    "duplicate_related_work_item",
                    f"related_work_items contains duplicate ID {item_id}.",
                    source,
                    item_id,
                )
            )
            continue
        seen.add(item_id)
        ids.append(item_id)
    return ids, errors


def parse_related_work_items(text: str, declared_work_item: str | None) -> ParsedRelatedWorkItems:
    """Parse anchored related-work metadata without inferring from prose."""
    metadata_text = strip_fenced_code_blocks(text)
    human_matches = list(RELATED_WORK_ITEMS_RE.finditer(metadata_text))
    json_matches = list(RELATED_WORK_ITEMS_JSON_RE.finditer(metadata_text))
    if not human_matches and not json_matches:
        return ParsedRelatedWorkItems(ordered_ids=(), sources_by_id={}, errors=())

    errors: list[RelationshipError] = []
    human_ids: list[str] = []
    json_ids: list[str] = []
    structurally_invalid = False

    if len(human_matches) > 1:
        structurally_invalid = True
        errors.append(
            _metadata_error(
                "duplicate_related_work_items_metadata",
                "Related Work Items metadata may appear only once.",
                "Related Work Items",
            )
        )
    else:
        human_ids, human_errors = (
            _parse_human_related_value(human_matches[0].group("value")) if human_matches else ([], [])
        )
        errors.extend(human_errors)
        structurally_invalid = structurally_invalid or bool(human_errors)

    if len(json_matches) > 1:
        structurally_invalid = True
        errors.append(
            _metadata_error(
                "duplicate_related_work_items_metadata",
                "related_work_items metadata may appear only once.",
                "related_work_items",
            )
        )
    else:
        json_ids, json_errors = _parse_json_related_value(json_matches[0].group("value")) if json_matches else ([], [])
        errors.extend(json_errors)
        structurally_invalid = structurally_invalid or bool(json_errors)

    if human_matches and json_matches and not structurally_invalid and set(human_ids) != set(json_ids):
        structurally_invalid = True
        errors.append(
            _metadata_error(
                "contradictory_related_work_items",
                "Related Work Items and related_work_items must declare identical normalized sets.",
                "both",
            )
        )

    if structurally_invalid:
        return ParsedRelatedWorkItems(ordered_ids=(), sources_by_id={}, errors=tuple(errors))

    ordered_ids = list(human_ids)
    for item_id in json_ids:
        if item_id not in ordered_ids:
            ordered_ids.append(item_id)

    sources: dict[str, tuple[str, ...]] = {}
    for item_id in ordered_ids:
        item_sources: list[str] = []
        if item_id in human_ids:
            item_sources.append("Related Work Items")
        if item_id in json_ids:
            item_sources.append("related_work_items")
        sources[item_id] = tuple(item_sources)

    if declared_work_item and declared_work_item in ordered_ids:
        errors.append(
            _metadata_error(
                "self_related_work_item",
                f"Declared work item {declared_work_item} cannot also be related.",
                ",".join(sources[declared_work_item]),
                declared_work_item,
            )
        )
        ordered_ids.remove(declared_work_item)
        sources.pop(declared_work_item, None)

    return ParsedRelatedWorkItems(
        ordered_ids=tuple(ordered_ids),
        sources_by_id=sources,
        errors=tuple(errors),
    )


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


def _ensure_groundtruth_importable(project_root: Path) -> None:
    gt_src = project_root / "groundtruth-kb" / "src"
    if gt_src.is_dir() and str(gt_src) not in sys.path:
        sys.path.insert(0, str(gt_src))


def check_content(
    text: str,
    declared_wi: str | None = None,
    *,
    db_path: Path | str | None = None,
) -> CollisionResult:
    declared = declared_wi or parse_declared_work_item(text)
    cited_ids = extract_cited_ids(text)
    parsed_related = parse_related_work_items(text, declared)
    path = _db_path(db_path)
    if not path.is_file():
        raise FileNotFoundError(f"MemBase database not found: {path}")

    relationship_errors = list(parsed_related.errors)
    related_items: list[RelatedWorkItem] = []
    related_ids: set[str] = set()
    rows: list[CitedId] = []
    with sqlite3.connect(path) as conn:
        for item_id in parsed_related.ordered_ids:
            row = _lookup_work_item(conn, item_id)
            if row is None:
                relationship_errors.append(
                    _metadata_error(
                        "unknown_related_work_item",
                        f"Related work item {item_id} does not exist in current MemBase.",
                        ",".join(parsed_related.sources_by_id[item_id]),
                        item_id,
                    )
                )
                continue
            related_ids.add(item_id)
            related_items.append(
                RelatedWorkItem(
                    work_item_id=item_id,
                    sources=parsed_related.sources_by_id[item_id],
                    exists_in_membase=True,
                    title=row["title"],
                )
            )

        for cited_id in cited_ids:
            row = _lookup_work_item(conn, cited_id)
            exists = row is not None
            matches_declared = bool(declared) and cited_id == declared
            is_related = cited_id in related_ids
            collision = bool(declared) and exists and not matches_declared and not is_related
            if matches_declared:
                classification = "declared_work_item"
            elif is_related:
                classification = "related_work_item"
            elif collision:
                classification = "collision"
            else:
                classification = "unknown_reference"
            rows.append(
                CitedId(
                    cited_id=cited_id,
                    exists_in_membase=exists,
                    matches_declared=matches_declared,
                    related_work_item=is_related,
                    collision=collision,
                    classification=classification,
                    title=row["title"] if row is not None and "title" in row else None,
                )
            )
    return CollisionResult(
        declared_work_item=declared,
        cited_ids=tuple(rows),
        related_work_items=tuple(related_items),
        relationship_errors=tuple(relationship_errors),
    )


def format_markdown(result: CollisionResult) -> str:
    lines = [
        "## Collision Check",
        "",
        f"- declared_work_item: `{result.declared_work_item or '(unknown)'}`",
        f"- has_collisions: `{str(result.has_collisions).lower()}`",
        f"- has_relationship_errors: `{str(result.has_relationship_errors).lower()}`",
        "",
        "### Validated Related Work Items",
        "",
        "| work_item_id | sources | exists_in_membase |",
        "|---|---|---:|",
    ]
    if result.related_work_items:
        for item in result.related_work_items:
            lines.append(
                f"| `{item.work_item_id}` | `{', '.join(item.sources)}` | `{str(item.exists_in_membase).lower()}` |"
            )
    else:
        lines.append("| _(none)_ |  |  |")

    lines.extend(
        [
            "",
            "### Relationship Errors",
            "",
        ]
    )
    if result.relationship_errors:
        for error in result.relationship_errors:
            suffix = f" (`{error.work_item_id}`)" if error.work_item_id else ""
            lines.append(f"- `{error.code}` [{error.source}]{suffix}: {error.message}")
    else:
        lines.append("- _(none)_")

    lines.extend(
        [
            "",
            "### Cited Work Items",
            "",
            "| cited_id | classification | exists_in_membase | matches_declared | related_work_item | collision |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for item in result.cited_ids:
        lines.append(
            f"| `{item.cited_id}` | `{item.classification}` | `{str(item.exists_in_membase).lower()}` | "
            f"`{str(item.matches_declared).lower()}` | `{str(item.related_work_item).lower()}` | "
            f"`{str(item.collision).lower()}` |"
        )
    return "\n".join(lines) + "\n"


def _read_bridge_target(bridge_id: str, *, project_root: Path = PROJECT_ROOT) -> Path:
    _ensure_groundtruth_importable(project_root)
    from groundtruth_kb.bridge.versioned_files import scan_expected_documents, status_from_bridge_file

    document = scan_expected_documents(project_root).get(bridge_id)
    if document is None:
        raise FileNotFoundError(f"No numbered bridge document found for {bridge_id!r}")
    for rel_path in reversed(document.files):
        status = status_from_bridge_file(project_root / rel_path)
        if status in PROPOSAL_STATUSES:
            return project_root / rel_path
    return project_root / document.files[-1]


def _content_from_args(args: argparse.Namespace) -> str:
    if args.stdin:
        return sys.stdin.read()
    if args.content_file:
        return Path(args.content_file).read_text(encoding="utf-8")
    if args.bridge_id:
        return _read_bridge_target(args.bridge_id).read_text(encoding="utf-8")
    raise SystemExit("One of --bridge-id, --content-file, or --stdin is required.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-id", help="Bridge document slug from numbered bridge files.")
    parser.add_argument("--content-file", type=Path, help="Path to proposal content to scan.")
    parser.add_argument("--stdin", action="store_true", help="Read proposal content from stdin.")
    parser.add_argument("--declared-wi", help="Override the declared Work Item metadata.")
    parser.add_argument("--db-path", type=Path, default=None, help="MemBase SQLite database path.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of Markdown.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when collisions or relationship metadata errors exist.",
    )
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
