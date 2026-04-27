"""Wave 2 lane 8 (Stage B): backlog row classification by subject.

Per ``bridge/gtkb-isolation-016-phase8-wave2-slice5-005.md`` (REVISED-2)
and ``-006`` (Codex GO).

Reads ``memory/work_list.md`` scoped to the **"Next Actionable Items"**
table only (per Codex ``-002`` non-blocking note 3); historical /
completed sections are out of scope.

Classification per Codex ``-004`` F1 fix (Option 2: content-based
override + conflict→unclassified):

- ``AR-*`` prefix → adopter.
- ``GTKB-*`` prefix + adopter content marker (e.g., "agent red
  migration") → unclassified with signal
  ``gtkb_prefix_with_adopter_content``. Per ``-006`` GO condition 1:
  surface the conflict, do NOT silently land in framework.
- ``GTKB-*`` prefix + no adopter content → framework.
- Other prefix → unclassified with signal ``unknown_prefix``.

Per ``-006`` non-blocking note: scan ``blocks_blocked_by`` field as
well as ``status`` and ``next_step`` for adopter content markers
(broader detection without changing approved behavior).

Authority: ADR-ISOLATION-APPLICATION-PLACEMENT-001; Wave 2 GO at
``bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md``.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from rehearse._common import LEGACY_ROOT
from rehearse._split_helper import (
    build_split_summary,
    emit_result,
    partition_items,
)

# Markers that strongly suggest a backlog row is adopter-targeted
# regardless of its ID prefix. Keep the list small + explicit; expand
# only with documented evidence in the test suite. Per Codex Slice 5
# `-006` non-blocking note: scanning blocks_blocked_by alongside status
# and next_step is more robust without changing approved behavior.
_ADOPTER_CONTENT_MARKERS: tuple[str, ...] = (
    "agent red migration",
    "agent red customer",
    "agent red staging",
    "agent red production",
    "adopter migration",
    "adopter rehearsal",
)

_NEXT_ACTIONABLE_HEADER = re.compile(r"^##\s+Next Actionable Items.*$", re.MULTILINE)
# Stop at the next H2 heading or the "Completed" marker, whichever
# comes first.
_TABLE_TERMINATOR = re.compile(r"^(##\s+|\*\*Completed\b)", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\|\s*(?P<index>\d+)\s*\|\s*(?P<rest>.+)\|\s*$")
_BACKTICKED_ID = re.compile(r"`([A-Za-z0-9_-]+)`")


def _extract_actionable_table(text: str) -> str:
    """Return the slice of ``work_list.md`` between the H2 heading and the next terminator."""
    header_match = _NEXT_ACTIONABLE_HEADER.search(text)
    if not header_match:
        return ""
    start = header_match.end()
    rest = text[start:]
    terminator_match = _TABLE_TERMINATOR.search(rest)
    end = terminator_match.start() if terminator_match else len(rest)
    return rest[:end]


def _parse_actionable_rows(table_text: str) -> list[dict[str, str]]:
    """Parse the Next Actionable Items markdown table into row dicts."""
    rows: list[dict[str, str]] = []
    for line in table_text.splitlines():
        stripped = line.strip()
        if not stripped or not stripped.startswith("|"):
            continue
        row_match = _TABLE_ROW.match(stripped)
        if not row_match:
            continue
        cells = [c.strip() for c in row_match.group("rest").split("|")]
        if len(cells) < 4:
            continue
        id_cell, status_cell, blocks_cell, next_step_cell = (
            cells[0],
            cells[1],
            cells[2],
            cells[3],
        )
        id_match = _BACKTICKED_ID.search(id_cell) or re.search(r"([A-Za-z0-9_-]+)", id_cell)
        if not id_match:
            continue
        rows.append(
            {
                "row_index": row_match.group("index"),
                "id": id_match.group(1),
                "status": status_cell,
                "blocks_blocked_by": blocks_cell,
                "next_step": next_step_cell,
            }
        )
    return rows


def _has_adopter_content(row: dict[str, str]) -> bool:
    """Return True if any marker appears in status, blocks_blocked_by, or next_step."""
    blob = (row.get("status", "") + " " + row.get("blocks_blocked_by", "") + " " + row.get("next_step", "")).lower()
    return any(marker in blob for marker in _ADOPTER_CONTENT_MARKERS)


def _classify_row(row: dict[str, str]) -> tuple[str, str]:
    """Return (classification, signal) for a backlog row.

    Per Slice 5 ``-005`` §1.1 (Option 2 fix from ``-004`` F1):
    - AR-* prefix → adopter (signal: ``ar_prefix``).
    - GTKB-* + adopter content → unclassified (signal:
      ``gtkb_prefix_with_adopter_content``).
    - GTKB-* + no adopter content → framework (signal: ``gtkb_prefix``).
    - Unknown prefix → unclassified (signal: ``unknown_prefix``).
    """
    row_id = row.get("id", "")
    if row_id.startswith("AR-"):
        return ("adopter", "ar_prefix")
    if row_id.startswith("GTKB-"):
        if _has_adopter_content(row):
            return ("unclassified", "gtkb_prefix_with_adopter_content")
        return ("framework", "gtkb_prefix")
    return ("unclassified", "unknown_prefix")


def run(
    manifest: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool = False,
    work_list_path: Path | None = None,
) -> dict[str, Any]:
    """Wave 2 Stage B leaf lane. Per common contract Wave 2 -003 §4.1.

    ``work_list_path`` (default ``LEGACY_ROOT/memory/work_list.md``)
    lets tests pass a fixture file per Codex Slice 5 ``-002``
    non-blocking note 4.
    """
    if dry_run:
        return {
            "status": "skipped",
            "output_files": [],
            "metrics": {"reason": "dry_run"},
            "warnings": [],
        }

    lane_dir = output_dir / "backlog_split"
    lane_dir.mkdir(parents=True, exist_ok=True)
    source_path = work_list_path if work_list_path is not None else LEGACY_ROOT / "memory" / "work_list.md"

    if not source_path.exists():
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"work_list_missing: {source_path}"],
            },
        )

    try:
        text = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": [f"work_list_unreadable: {exc}"],
            },
        )

    table_text = _extract_actionable_table(text)
    if not table_text.strip():
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": ["next_actionable_items_section_not_found_or_empty"],
            },
        )

    rows = _parse_actionable_rows(table_text)
    if not rows:
        return emit_result(
            lane_dir,
            {
                "status": "error",
                "output_files": [],
                "metrics": {},
                "warnings": ["work_list_table_no_rows_parsed"],
            },
        )

    buckets = partition_items(rows, _classify_row)

    warnings: list[str] = []
    conflict_count = sum(
        1 for r in buckets["unclassified"] if r["classification_signal"] == "gtkb_prefix_with_adopter_content"
    )
    if conflict_count:
        warnings.append(
            f"gtkb_prefix_with_adopter_content_conflicts: {conflict_count} "
            f"row(s) — surface for Wave 3 owner decision (per Slice 5 -006 "
            f"GO condition 2)"
        )
    unknown_prefix_count = sum(1 for r in buckets["unclassified"] if r["classification_signal"] == "unknown_prefix")
    if unknown_prefix_count:
        warnings.append(
            f"unknown_prefix_rows: {unknown_prefix_count} row(s) had prefixes outside GTKB-/AR-; surface for Wave 3"
        )

    backlog_split_doc = {
        "schema_version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_path": str(source_path).replace("\\", "/"),
        "summary": build_split_summary(buckets),
        "framework_rows": buckets["framework"],
        "adopter_rows": buckets["adopter"],
        "unclassified_rows": buckets["unclassified"],
    }

    backlog_split_path = lane_dir / "backlog_split.json"
    backlog_split_path.write_text(json.dumps(backlog_split_doc, indent=2), encoding="utf-8")

    return emit_result(
        lane_dir,
        {
            "status": "ok",
            "output_files": [str(backlog_split_path)],
            "metrics": {
                "framework_count": backlog_split_doc["summary"]["framework_count"],
                "adopter_count": backlog_split_doc["summary"]["adopter_count"],
                "unclassified_count": backlog_split_doc["summary"]["unclassified_count"],
                "total_rows": backlog_split_doc["summary"]["total"],
            },
            "warnings": warnings,
        },
    )
