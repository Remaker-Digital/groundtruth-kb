#!/usr/bin/env python3
"""Deterministic obsolete-reference-purge check (WI-4795).

Operationalizes ``DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001``: for each
retirement-class artifact in the evaluation window, verify a linked
obsolete-reference-purge work item exists.

Phase 1 = WARN (advisory): the standalone CLI always exits 0; the doctor
surface (``_check_obsolete_reference_purge`` in
``groundtruth_kb.project.doctor``) returns ``warning`` -- never ``fail`` --
for unpaired retirements. Phase 2 (a blocking FAIL gate at the
cutover/verification boundary) is a separate future thread, gated on
Slice-1 feedback, mirroring ``gtkb-adr-dcl-clause-test-enforcement``.

Read-only. Performs no MemBase mutation.

Source: bridge thread ``gtkb-obsolete-reference-purge-deterministic-check``
(Loyal Opposition GO at -002); owner directive
``DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Forward-looking obligation effective date. The obligation is a STANDING
# completion obligation on significant changes going FORWARD (per
# ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001); retirement-class artifacts whose
# latest change predates this date are outside the Phase-1 window, because
# retroactively flagging the entire historical corpus of retired specs would
# flood WARN with un-actionable noise. Loyal Opposition confirmed this boundary
# as correct for Phase 1 (GO at -002, Positive Confirmations).
OBLIGATION_EFFECTIVE_DATE = "2026-06-24"

RETIRE_SPEC_PREFIX = "RETIRE-SPEC-"
RETIREMENT_STATUSES = ("retired", "superseded")
# Explicit, machine-readable supersession marker: a structured ``Supersedes:``
# (or ``Supersedes -``) field line in an ADR/DCL body that names a prior artifact.
# Phase 1 requires this structured field rather than matching the bare word
# "supersedes" in definitional prose -- otherwise the obligation DCL, whose own
# definition contains the word, would self-flag. A prose-only supersession is an
# intentional Phase-1 false-negative (advisory mode); tightening recall is gated
# on Slice-1 feedback before any Phase-2 FAIL gate.
SUPERSEDING_SPEC_TYPES = ("architecture_decision", "design_constraint")
_SUPERSEDES_FIELD_RE = re.compile(r"^\s*supersedes\s*[:\-]\s+\S", re.IGNORECASE | re.MULTILINE)
PURGE_PROJECT_MARKER = "OBSOLETE-REFERENCE-PURGE"


@dataclass
class Finding:
    """One retirement-class artifact and its pairing verdict."""

    artifact_id: str
    artifact_type: str
    status: str
    changed_at: str | None
    paired: bool
    pair_work_item: str | None
    reason: str


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if len(text) == 10:  # YYYY-MM-DD
            return datetime.fromisoformat(text).replace(tzinfo=UTC)
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _window_start(obligation_effective_date: str | None) -> datetime:
    date_text = obligation_effective_date or OBLIGATION_EFFECTIVE_DATE
    return datetime.fromisoformat(date_text).replace(tzinfo=UTC)


def in_window(changed_at: str | None, *, window_start: datetime) -> bool:
    """True when ``changed_at`` is at/after ``window_start``.

    An unparseable/absent timestamp is conservatively OUT of the window
    (favor no-noise; the obligation is forward-looking).
    """
    parsed = _parse_iso(changed_at)
    if parsed is None:
        return False
    return parsed >= window_start


def is_retirement_class(spec: dict[str, Any]) -> tuple[bool, str]:
    """Classify a spec as retirement-class per DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001."""
    spec_id = str(spec.get("id", ""))
    status = str(spec.get("status", "")).lower()
    spec_type = str(spec.get("type", "")).lower()
    if status in RETIREMENT_STATUSES:
        return True, f"status={status}"
    if spec_id.startswith(RETIRE_SPEC_PREFIX):
        return True, "RETIRE-SPEC-* id prefix"
    if spec_type in SUPERSEDING_SPEC_TYPES:
        body = str(spec.get("description", ""))
        if _SUPERSEDES_FIELD_RE.search(body):
            return True, f"{spec_type} with explicit Supersedes: field"
    return False, ""


def paired_work_item(spec_id: str, work_items: list[dict[str, Any]]) -> str | None:
    """Return a linked obsolete-reference-purge work item id, or ``None``.

    Detection is intentionally inclusive (favor PASS) so a Phase-1 advisory does
    not cry wolf on a genuinely-paired retirement. A work item pairs ``spec_id``
    when it (a) cites it as ``source_spec_id``, (b) carries an explicit
    ``purges: <spec_id>`` token, or (c) is a purge-project member referencing it.
    """
    for work_item in work_items:
        work_item_id = str(work_item.get("id", ""))
        if str(work_item.get("source_spec_id", "")) == spec_id:
            return work_item_id
        description = str(work_item.get("description", ""))
        description_lower = description.lower()
        if "purges:" in description_lower and spec_id.lower() in description_lower:
            return work_item_id
        project = str(work_item.get("project_name", "")).upper()
        if PURGE_PROJECT_MARKER in project and spec_id in description:
            return work_item_id
    return None


def _load_knowledge_db_cls(project_root: Path) -> Any:
    try:
        from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415
    except ImportError:
        src = project_root / "groundtruth-kb" / "src"
        if src.is_dir() and str(src) not in sys.path:
            sys.path.insert(0, str(src))
        from groundtruth_kb.db import KnowledgeDB  # noqa: PLC0415
    return KnowledgeDB


def evaluate(
    project_root: Path,
    *,
    obligation_effective_date: str | None = None,
) -> dict[str, Any]:
    """Evaluate retirement/purge pairing over the project's MemBase. Read-only."""
    knowledge_db_cls = _load_knowledge_db_cls(project_root)
    db = knowledge_db_cls(project_root / "groundtruth.db")
    window_start = _window_start(obligation_effective_date)

    specs = db.list_specs()
    work_items = db.list_work_items()

    findings: list[Finding] = []
    for spec in specs:
        is_retirement, reason = is_retirement_class(spec)
        if not is_retirement:
            continue
        changed_at = spec.get("changed_at") or spec.get("created_at")
        if not in_window(changed_at, window_start=window_start):
            continue
        spec_id = str(spec.get("id", ""))
        pair = paired_work_item(spec_id, work_items)
        findings.append(
            Finding(
                artifact_id=spec_id,
                artifact_type=str(spec.get("type", "")),
                status=str(spec.get("status", "")),
                changed_at=str(changed_at) if changed_at else None,
                paired=pair is not None,
                pair_work_item=pair,
                reason=reason,
            )
        )

    unpaired = [asdict(f) for f in findings if not f.paired]
    paired = [asdict(f) for f in findings if f.paired]
    return {
        "window_start": obligation_effective_date or OBLIGATION_EFFECTIVE_DATE,
        "evaluated": len(findings),
        "unpaired": unpaired,
        "paired": paired,
        "status": "warning" if unpaired else "pass",
    }


def unpaired_retirement_class_artifacts(
    project_root: Path,
    *,
    obligation_effective_date: str | None = None,
) -> list[dict[str, Any]]:
    """Doctor-surface helper: the unpaired retirement-class findings (may be empty)."""
    return evaluate(project_root, obligation_effective_date=obligation_effective_date)["unpaired"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args(argv)

    result = evaluate(args.project_root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        evaluated = result["evaluated"]
        unpaired = result["unpaired"]
        if unpaired:
            print(
                f"[WARN] {len(unpaired)}/{evaluated} in-window retirement-class "
                "artifact(s) lack a paired obsolete-reference-purge work item:"
            )
            for finding in unpaired:
                print(f"  - {finding['artifact_id']} ({finding['reason']}) -- no linked purge WI")
        else:
            print(
                f"[PASS] all {evaluated} in-window retirement-class artifact(s) "
                "have a paired obsolete-reference-purge work item"
            )
    # Phase 1 is advisory: always exit 0.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
