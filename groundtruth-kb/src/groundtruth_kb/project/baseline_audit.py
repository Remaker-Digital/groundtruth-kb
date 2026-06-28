# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Baseline-audit skill contract: trigger detection and evidence-class validation."""

from __future__ import annotations

import re

BASELINE_AUDIT_TRIGGER_PHRASES: tuple[str, ...] = (
    "baseline status",
    "release readiness",
    "production readiness",
    "project handoff",
    "baseline audit",
    "where do we stand",
    "full status",
)

EVIDENCE_CLASSES: frozenset[str] = frozenset(
    {
        "command_output",
        "bridge_status",
        "DA_row",
        "CI_result",
        "release_tag",
        "doc_inference",
    }
)

BASELINE_AUDIT_ITEM_COUNT = 29

EVIDENCE_CLASS_TAG_RE = re.compile(
    r"\[(?:evidence[_-]class|class):\s*(" + "|".join(sorted(EVIDENCE_CLASSES, key=len, reverse=True)) + r")\]",
    re.IGNORECASE,
)

BASELINE_AUDIT_ROW_RE = re.compile(
    r"^\|\s*\d+\s*\|",
    re.MULTILINE,
)


def matches_baseline_audit_trigger(text: str) -> bool:
    """Return True when *text* contains a documented trigger phrase (substring match)."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in BASELINE_AUDIT_TRIGGER_PHRASES)


def extract_baseline_audit_table_rows(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if BASELINE_AUDIT_ROW_RE.match(line.strip())]


def normalize_evidence_class(raw: str) -> str | None:
    normalized = raw.strip().lower()
    mapping = {
        "command_output": "command_output",
        "bridge_status": "bridge_status",
        "da_row": "DA_row",
        "ci_result": "CI_result",
        "release_tag": "release_tag",
        "doc_inference": "doc_inference",
    }
    return mapping.get(normalized)


def validate_baseline_audit_output(text: str) -> tuple[bool, str]:
    rows = extract_baseline_audit_table_rows(text)
    if len(rows) != BASELINE_AUDIT_ITEM_COUNT:
        return False, f"expected {BASELINE_AUDIT_ITEM_COUNT} table rows, found {len(rows)}"

    for index, row in enumerate(rows, start=1):
        match = EVIDENCE_CLASS_TAG_RE.search(row)
        if not match:
            return False, f"row {index} missing evidence-class tag"
        evidence_class = normalize_evidence_class(match.group(1))
        if evidence_class not in EVIDENCE_CLASSES:
            return False, f"row {index} has invalid evidence class {match.group(1)!r}"
    return True, "baseline audit output valid"
