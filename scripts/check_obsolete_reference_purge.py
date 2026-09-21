#!/usr/bin/env python3
"""Read-only native obsolete-reference-purge diagnostics (WI-4795).

DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001 retains the Phase-1 advisory:
unpaired in-window retirement-class artifacts warn. Current specifications,
work items and project memberships come from native service GETs. Project-name
fields on work items and historical bridge messages establish no relationship.
The CLI exits 0 for a completed advisory evaluation, and an unavailable native
inspection is an error. This module makes no canonical writes.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

from groundtruth_kb.authority_client import (
    AuthorityClient,
    AuthorityClientError,
    configured_authority_client,
    page_records,
)

# Forward-looking obligation effective date. The obligation is a STANDING
# completion obligation on significant changes going FORWARD (per
# ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001); retirement-class artifacts whose
# latest change predates this date are outside the Phase-1 window, because
# retroactively flagging the entire historical corpus of retired specs would
# flood WARN with un-actionable noise. The retained Phase-1 window is advisory.
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


def paired_work_item(
    spec_id: str, work_items: list[dict[str, Any]], *, purge_member_ids: set[str] | None = None
) -> str | None:
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
        if work_item_id in (purge_member_ids or set()) and spec_id in description:
            return work_item_id
    return None


def evaluate(
    project_root: Path,
    *,
    obligation_effective_date: str | None = None,
    client: AuthorityClient | None = None,
) -> dict[str, Any]:
    """Evaluate retirement/purge pairing over current native records. Read-only."""
    reader = client if client is not None else configured_authority_client(project_root)
    window_start = _window_start(obligation_effective_date)

    specs = page_records(reader, "/v1/specifications")
    work_items = page_records(reader, "/v1/work-items")
    purge_member_ids: set[str] = set()
    for project in page_records(reader, "/v1/projects"):
        if project.get("kind") != "project" or not any(
            PURGE_PROJECT_MARKER in str(project.get(key) or "").upper() for key in ("id", "name")
        ):
            continue
        project_id = project["id"]
        detail = reader.request("GET", "/v1/projects/" + quote(project_id, safe=""))
        members = detail.get("memberships") if isinstance(detail, dict) else None
        if not isinstance(members, list) or any(
            not isinstance(member, dict)
            or member.get("project_id") != project_id
            or member.get("status") != "active"
            or not isinstance(member.get("work_item_id"), str)
            or not member["work_item_id"].strip()
            for member in members
        ):
            raise AuthorityClientError("invalid_response", f"Project {project_id} memberships are malformed")
        purge_member_ids.update(member["work_item_id"] for member in members)

    findings: list[Finding] = []
    for spec in specs:
        is_retirement, reason = is_retirement_class(spec)
        if not is_retirement:
            continue
        changed_at = spec.get("changed_at") or spec.get("created_at")
        if not in_window(changed_at, window_start=window_start):
            continue
        spec_id = str(spec.get("id", ""))
        pair = paired_work_item(spec_id, work_items, purge_member_ids=purge_member_ids)
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
    client: AuthorityClient | None = None,
) -> list[dict[str, Any]]:
    """Doctor-surface helper: the unpaired retirement-class findings (may be empty)."""
    return evaluate(project_root, obligation_effective_date=obligation_effective_date, client=client)["unpaired"]


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
