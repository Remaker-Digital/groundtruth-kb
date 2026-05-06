"""Unified backlog helpers.

The canonical backlog is the current MemBase ``work_items`` view. This module
only exists to migrate older markdown work-list rows into that source of truth
and to keep the migration repeatable.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from groundtruth_kb.db import KnowledgeDB

_TABLE_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")
_BACKTICK_RE = re.compile(r"`([^`]+)`")
_BRIDGE_REF_RE = re.compile(r"\bbridge/[A-Za-z0-9._/-]+?\.md\b")
_DELIB_REF_RE = re.compile(r"\bDELIB-[A-Za-z0-9._-]+\b")
_SPEC_REF_RE = re.compile(r"\b(?:GOV|SPEC|PB|ADR|DCL|IPR|CVR|OM-DELTA)-[A-Za-z0-9._-]+\b")
_WORK_REF_RE = re.compile(r"\b[A-Z][A-Z0-9]+(?:-[A-Za-z0-9._]+)+\b")


@dataclass(frozen=True)
class WorkListItem:
    """One structured item parsed from the legacy markdown work list."""

    implementation_order: int
    work_item_id: str
    source_label_id: str
    title: str
    status_detail: str
    resolution_status: str
    stage: str
    priority: str | None
    project_name: str
    subproject_name: str | None
    blocks_or_blocked_by: str
    next_step: str
    description: str
    source_owner_directive: str
    related_deliberation_ids: tuple[str, ...]
    related_spec_ids_at_creation: tuple[str, ...]
    related_bridge_threads: tuple[str, ...]
    depends_on_work_items: tuple[str, ...]
    line_number: int

    def insert_kwargs(self, *, changed_by: str, change_reason: str) -> dict[str, Any]:
        """Return keyword arguments for ``KnowledgeDB.insert_work_item``."""
        return {
            "id": self.work_item_id,
            "title": self.title,
            "origin": "hygiene",
            "component": "backlog",
            "resolution_status": self.resolution_status,
            "changed_by": changed_by,
            "change_reason": change_reason,
            "description": self.description,
            "priority": self.priority,
            "stage": self.stage,
            "project_name": self.project_name,
            "subproject_name": self.subproject_name,
            "implementation_order": self.implementation_order,
            "status_detail": self.status_detail,
            "source_owner_directive": self.source_owner_directive,
            "related_deliberation_ids": _json_list(self.related_deliberation_ids),
            "related_spec_ids_at_creation": _json_list(self.related_spec_ids_at_creation),
            "related_bridge_threads": _json_list(self.related_bridge_threads),
            "depends_on_work_items": _json_list(self.depends_on_work_items),
        }


@dataclass(frozen=True)
class WorkListMigrationResult:
    """Summary of a legacy work-list migration run."""

    parsed: int
    inserted: tuple[str, ...]
    updated_existing: tuple[str, ...]
    skipped_existing: tuple[str, ...]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "parsed": self.parsed,
            "inserted_count": len(self.inserted),
            "inserted": list(self.inserted),
            "updated_existing_count": len(self.updated_existing),
            "updated_existing": list(self.updated_existing),
            "skipped_existing_count": len(self.skipped_existing),
            "skipped_existing": list(self.skipped_existing),
        }


def parse_work_list_markdown(text: str) -> list[WorkListItem]:
    """Parse the legacy ``memory/work_list.md`` table into work items."""
    return _dedupe_items([*_parse_work_list_table(text), *_parse_active_section_items(text)])


def _parse_work_list_table(text: str) -> list[WorkListItem]:
    """Parse the legacy numbered markdown table."""
    raw_rows: list[tuple[int, int, str, str, str, str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not _TABLE_ROW_RE.match(line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        try:
            implementation_order = int(cells[0])
        except ValueError:
            continue
        raw_id, suffix = _extract_id_and_suffix(cells[1])
        raw_rows.append((line_number, implementation_order, raw_id, suffix or "", cells[2], cells[3], cells[4]))

    id_counts = Counter(row[2] for row in raw_rows)
    items: list[WorkListItem] = []
    for line_number, implementation_order, source_label_id, suffix, status, blocks, next_step in raw_rows:
        work_item_id = source_label_id
        if id_counts[source_label_id] > 1:
            work_item_id = f"{source_label_id}-{_slugify(suffix)}"
        status_detail = _clean_markdown(status)
        blocks_or_blocked_by = _clean_markdown(blocks)
        cleaned_next_step = _clean_markdown(next_step)
        title = source_label_id if not suffix else f"{source_label_id} {suffix}"
        combined = "\n".join((source_label_id, suffix, status, blocks, next_step))
        related_work = tuple(
            ref for ref in _unique_refs(_WORK_REF_RE.findall(combined)) if ref not in {source_label_id, work_item_id}
        )
        description = (
            f"Migrated from memory/work_list.md row {implementation_order}.\n\n"
            f"Status: {status_detail}\n\n"
            f"Blocks / blocked by: {blocks_or_blocked_by}\n\n"
            f"Next step: {cleaned_next_step}"
        )
        items.append(
            WorkListItem(
                implementation_order=implementation_order,
                work_item_id=work_item_id,
                source_label_id=source_label_id,
                title=_clean_markdown(title),
                status_detail=status_detail,
                resolution_status=_coarse_resolution_status(status_detail),
                stage=_stage_from_status(status_detail),
                priority=_priority_from_status(status_detail, implementation_order),
                project_name=source_label_id,
                subproject_name=_clean_markdown(suffix) or None,
                blocks_or_blocked_by=blocks_or_blocked_by,
                next_step=cleaned_next_step,
                description=description,
                source_owner_directive=(
                    f"Migrated from memory/work_list.md line {line_number}; original table ID {source_label_id}."
                ),
                related_deliberation_ids=tuple(_unique_refs(_DELIB_REF_RE.findall(combined))),
                related_spec_ids_at_creation=tuple(_unique_refs(_SPEC_REF_RE.findall(combined))),
                related_bridge_threads=tuple(_unique_refs(_BRIDGE_REF_RE.findall(combined))),
                depends_on_work_items=related_work,
                line_number=line_number,
            )
        )
    return items


def _parse_active_section_items(text: str) -> list[WorkListItem]:
    """Parse the older ``## Active Items`` heading section."""
    items: list[WorkListItem] = []
    in_active = False
    current_heading: tuple[int, str, str, str | None] | None = None
    body_lines: list[str] = []
    sequence = 0

    def flush_current() -> None:
        nonlocal current_heading, body_lines, sequence
        if not current_heading:
            return
        line_number, source_label_id, title, subproject_name = current_heading
        body = "\n".join(body_lines).strip()
        work_item_id = _canonical_heading_item_id(source_label_id, title)
        combined = "\n".join((source_label_id, title, body))
        related_work = tuple(
            ref for ref in _unique_refs(_WORK_REF_RE.findall(combined)) if ref not in {source_label_id, work_item_id}
        )
        status_detail = "legacy active-section item"
        items.append(
            WorkListItem(
                implementation_order=1000 + sequence,
                work_item_id=work_item_id,
                source_label_id=source_label_id,
                title=_clean_markdown(title),
                status_detail=status_detail,
                resolution_status=_coarse_resolution_status(status_detail),
                stage=_stage_from_status(status_detail),
                priority=None,
                project_name=source_label_id,
                subproject_name=subproject_name,
                blocks_or_blocked_by="",
                next_step="",
                description=body or f"Migrated from memory/work_list.md heading {source_label_id}.",
                source_owner_directive=(
                    f"Migrated from memory/work_list.md line {line_number}; "
                    f"legacy Active Items heading {source_label_id}."
                ),
                related_deliberation_ids=tuple(_unique_refs(_DELIB_REF_RE.findall(combined))),
                related_spec_ids_at_creation=tuple(_unique_refs(_SPEC_REF_RE.findall(combined))),
                related_bridge_threads=tuple(_unique_refs(_BRIDGE_REF_RE.findall(combined))),
                depends_on_work_items=related_work,
                line_number=line_number,
            )
        )
        sequence += 1
        current_heading = None
        body_lines = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.startswith("## Active Items"):
            in_active = True
            continue
        if in_active and line.startswith("## "):
            flush_current()
            break
        if not in_active:
            continue
        if line.startswith("### "):
            flush_current()
            heading = _clean_markdown(line[4:])
            if re.search(r"\b(DONE|PAUSED|OBSOLETE|RETIRED)\b", heading, re.IGNORECASE):
                current_heading = None
                continue
            source_label_id, title = _extract_heading_id_and_title(heading)
            current_heading = (line_number, source_label_id, title, _heading_subproject_name(title))
            continue
        if current_heading:
            body_lines.append(line)
    if in_active:
        flush_current()
    return items


def parse_work_list_file(path: Path) -> list[WorkListItem]:
    """Parse the legacy work-list markdown file."""
    return parse_work_list_markdown(path.read_text(encoding="utf-8"))


def migrate_work_list_items(
    db: KnowledgeDB,
    items: list[WorkListItem],
    *,
    changed_by: str,
    change_reason: str,
    dry_run: bool = False,
) -> WorkListMigrationResult:
    """Migrate parsed work-list rows into MemBase ``work_items``."""
    inserted: list[str] = []
    updated_existing: list[str] = []
    skipped_existing: list[str] = []
    for item in items:
        existing = db.get_work_item(item.work_item_id)
        if existing:
            update_fields = _missing_metadata_update_fields(existing, item)
            if update_fields:
                updated_existing.append(item.work_item_id)
                if not dry_run:
                    db.update_work_item(
                        item.work_item_id,
                        changed_by=changed_by,
                        change_reason=change_reason,
                        **update_fields,
                    )
            else:
                skipped_existing.append(item.work_item_id)
            continue
        inserted.append(item.work_item_id)
        if not dry_run:
            db.insert_work_item(**item.insert_kwargs(changed_by=changed_by, change_reason=change_reason))
    return WorkListMigrationResult(
        parsed=len(items),
        inserted=tuple(inserted),
        updated_existing=tuple(updated_existing),
        skipped_existing=tuple(skipped_existing),
    )


def _missing_metadata_update_fields(existing: dict[str, Any], item: WorkListItem) -> dict[str, Any]:
    metadata = item.insert_kwargs(changed_by="", change_reason="")
    fields = (
        "description",
        "project_name",
        "subproject_name",
        "implementation_order",
        "status_detail",
        "source_owner_directive",
        "related_deliberation_ids",
        "related_spec_ids_at_creation",
        "related_bridge_threads",
        "depends_on_work_items",
    )
    return {
        field: metadata[field]
        for field in fields
        if metadata.get(field) is not None and existing.get(field) in (None, "")
    }


def _extract_id_and_suffix(id_cell: str) -> tuple[str, str | None]:
    match = _BACKTICK_RE.search(id_cell)
    if match:
        source_id = match.group(1).strip()
        suffix = id_cell[: match.start()] + id_cell[match.end() :]
        suffix = suffix.strip(" -")
        return source_id, _clean_markdown(suffix) or None
    parts = _clean_markdown(id_cell).split(maxsplit=1)
    if not parts:
        raise ValueError("work-list row has no ID")
    suffix_text = parts[1] if len(parts) > 1 else None
    return parts[0], suffix_text


def _extract_heading_id_and_title(heading: str) -> tuple[str, str]:
    separator_match = re.match(r"(?P<id>\S+)\s+(?:--|-|\u2014)\s+(?P<title>.+)", heading)
    if separator_match:
        return separator_match.group("id"), separator_match.group("title")
    parts = heading.split(maxsplit=1)
    if len(parts) == 1:
        return parts[0], heading
    return parts[0], parts[1]


def _canonical_heading_item_id(source_label_id: str, title: str) -> str:
    if re.match(r"^[A-Z][A-Z0-9]*(?:-[A-Za-z0-9._]+)+$", source_label_id):
        return source_label_id
    return f"WORKLIST-{_slugify(f'{source_label_id} {title}')}"


def _heading_subproject_name(title: str) -> str | None:
    match = re.search(r"\b(Slice\s+[A-Za-z0-9.]+|Phase\s+[A-Za-z0-9.]+|Tier\s+[A-Za-z0-9.]+)\b", title)
    return match.group(1) if match else None


def _clean_markdown(value: str | None) -> str:
    if not value:
        return ""
    cleaned = re.sub(r"<br\s*/?>", " ", value)
    cleaned = cleaned.replace("**", "").replace("~~", "")
    cleaned = cleaned.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", cleaned).strip()


def _coarse_resolution_status(status_detail: str) -> str:
    status = status_detail.lower()
    if any(token in status for token in ("verified", "done", "closed", "complete")):
        return "verified"
    if any(token in status for token in ("implemented", "in progress", "post-implementation", "go;")):
        return "in_progress"
    if "resolved" in status:
        return "resolved"
    return "open"


def _stage_from_status(status_detail: str) -> str:
    status = status_detail.lower()
    if any(token in status for token in ("verified", "done", "closed", "complete", "resolved")):
        return "resolved"
    if any(token in status for token in ("implemented", "in progress", "post-implementation", "go;")):
        return "implementing"
    return "backlogged"


def _priority_from_status(status_detail: str, implementation_order: int) -> str | None:
    match = re.search(r"\bP\d+\b", status_detail, flags=re.IGNORECASE)
    if match:
        return match.group(0).upper()
    if implementation_order == 0:
        return "P0"
    return None


def _slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.upper()).strip("-")
    return slug or "ITEM"


def _unique_refs(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        cleaned = value.strip(".,;:()[]")
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        unique.append(cleaned)
    return unique


def _json_list(values: tuple[str, ...]) -> str | None:
    if not values:
        return None
    return json.dumps(list(values))


def _dedupe_items(items: list[WorkListItem]) -> list[WorkListItem]:
    seen: set[str] = set()
    deduped: list[WorkListItem] = []
    for item in items:
        if item.work_item_id in seen:
            continue
        seen.add(item.work_item_id)
        deduped.append(item)
    return deduped
