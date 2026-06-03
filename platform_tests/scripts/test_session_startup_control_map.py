# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structural tests for the Slice A startup-control inventory artifacts.

GTKB-STARTUP-REFRACTOR-001 Slice A (WI-4268) creates two role-neutral
documentation artifacts under ``config/agent-control/``:

- ``SESSION-STARTUP-CONTROL-MAP.md`` — the single source-of-truth inventory of
  startup control surfaces (advisory F2), with every surface row carrying a
  lifecycle classification (advisory F9-classify).
- ``ROLE-CAPABILITY-MANIFEST.md`` — the role-capability manifest (advisory F8),
  grouped into Prime Builder / Loyal Opposition / Shared / Owner-Gated sections.

These tests are *structural*: they assert the inventory enumerates the canonical
required startup files, that every inventory table row is classified with a
valid lifecycle token, and that the manifest carries the four role sections.
They do not assert the inventory is exhaustive (that would be brittle against
ongoing surface churn); they assert the load-bearing contract that the later
refactor slices depend on.

Authority: ``GOV-SESSION-SELF-INITIALIZATION-001``,
``DCL-SESSION-STARTUP-TOKEN-BUDGET-001``;
``bridge/gtkb-startup-refractor-slice-a-startup-control-inventory-002.md`` (GO).
"""

from __future__ import annotations

import re
from pathlib import Path

# Project root: this file is at platform_tests/scripts/, so two parents up.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CONTROL_MAP = _PROJECT_ROOT / "config" / "agent-control" / "SESSION-STARTUP-CONTROL-MAP.md"
_MANIFEST = _PROJECT_ROOT / "config" / "agent-control" / "ROLE-CAPABILITY-MANIFEST.md"

# Canonical required startup files the control-map MUST enumerate. This is the
# minimum load-bearing set both roles depend on at session start; it is not the
# exhaustive list.
REQUIRED_STARTUP_FILES = (
    "CLAUDE.md",
    "AGENTS.md",
    ".claude/rules/canonical-terminology.md",
    ".claude/rules/operating-role.md",
    ".claude/rules/file-bridge-protocol.md",
    ".claude/rules/deliberation-protocol.md",
    "scripts/session_self_initialization.py",
)

# Valid lifecycle classifications for a startup-control surface (advisory
# F9-classify; classify-only, no deletion in Slice A).
VALID_CLASSIFICATIONS = ("active", "deprecated", "archive", "generated")

# The four role sections the role-capability manifest must carry (advisory F8).
REQUIRED_MANIFEST_SECTIONS = (
    "Prime Builder",
    "Loyal Opposition",
    "Shared",
    "Owner-Gated",
)

# An inventory table data row: a markdown table row that is neither the header
# (contains "Surface" or "Capability") nor the separator (dashes only).
_TABLE_ROW = re.compile(r"^\|(?P<cells>.+)\|\s*$")
_SEPARATOR_ROW = re.compile(r"^\|[\s:|-]+\|\s*$")


def _read(path: Path) -> str:
    assert path.is_file(), f"required Slice A artifact missing: {path}"
    return path.read_text(encoding="utf-8")


def _inventory_rows(text: str) -> list[str]:
    """Return inventory table DATA rows (excluding header + separator rows).

    A row is considered an inventory data row when it is a markdown table row,
    is not a separator, and is not a header (header rows name a ``Surface`` or
    ``Capability`` column). Rows are collected only inside fenced inventory
    sections marked by an HTML comment ``<!-- inventory -->`` so prose tables
    elsewhere in the doc do not have to carry a classification column.
    """
    rows: list[str] = []
    in_inventory = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<!-- inventory -->"):
            in_inventory = True
            continue
        if stripped.startswith("<!-- /inventory -->"):
            in_inventory = False
            continue
        if not in_inventory:
            continue
        if _SEPARATOR_ROW.match(stripped):
            continue
        m = _TABLE_ROW.match(stripped)
        if not m:
            continue
        if "Surface" in stripped or "Capability" in stripped:
            continue
        rows.append(stripped)
    return rows


def test_control_map_exists_and_lists_required_startup_files() -> None:
    text = _read(_CONTROL_MAP)
    missing = [f for f in REQUIRED_STARTUP_FILES if f not in text]
    assert not missing, f"SESSION-STARTUP-CONTROL-MAP.md omits required startup files: {missing}"


def test_control_map_declares_lifecycle_legend() -> None:
    text = _read(_CONTROL_MAP).lower()
    missing = [c for c in VALID_CLASSIFICATIONS if c not in text]
    assert not missing, f"control-map lifecycle legend missing classifications: {missing}"


def test_every_inventory_row_is_classified() -> None:
    text = _read(_CONTROL_MAP)
    rows = _inventory_rows(text)
    assert rows, "control-map has no inventory rows inside <!-- inventory --> markers"
    unclassified = []
    for row in rows:
        lowered = row.lower()
        if not any(re.search(rf"\b{c}\b", lowered) for c in VALID_CLASSIFICATIONS):
            unclassified.append(row)
    assert not unclassified, f"inventory rows missing a valid lifecycle classification: {unclassified}"


def test_manifest_exists_and_has_role_sections() -> None:
    text = _read(_MANIFEST)
    missing = [s for s in REQUIRED_MANIFEST_SECTIONS if s not in text]
    assert not missing, f"ROLE-CAPABILITY-MANIFEST.md missing role sections: {missing}"
