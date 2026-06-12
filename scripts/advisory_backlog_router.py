#!/usr/bin/env python3
"""Advisory-to-backlog router service.

Scans Loyal Opposition advisories under
``independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`` and
bridge ``ADVISORY`` entries listed in ``bridge/INDEX.md``, and STAGES one
candidate per unhandled advisory on an append-only candidate surface
(``.gtkb-state/advisory-candidates/candidates.jsonl``) under
``GOV-STANDING-BACKLOG-001`` authority.

Stage 3 (WI-4469, ``DELIB-20261667`` D5, owner AUQ 2026-06-11 = approval-staged
intake) stops the backlog leak at the source: the router no longer auto-promotes
advisories to OPEN ``work_items`` rows. Staged candidates enter the active
backlog only via the owner-batch-AUQ promotion path in
``scripts/hygiene/advisory_candidate_promote.py``. The service is idempotent on
rerun: an advisory is "already handled" when its source identifier is present on
the candidate surface (any status) OR already references an existing
``work_items`` row via ``related_deliberation_ids``.

Per ``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE``, this replaces the
repetitive per-session plumbing of manually opening the dropbox and
hand-creating backlog rows; the only marginal human judgment is the owner's
per-batch promotion APPROVE / REFINE / REJECT decision.

CLI:
    python scripts/advisory_backlog_router.py
        [--dry-run]
        [--source dropbox|bridge|both]
        [--since YYYY-MM-DD]
        [--project-root PATH]

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

ROUTER_ID = "advisory-backlog-router/1.0"
SOURCE_SPEC_ID = "GOV-STANDING-BACKLOG-001"
WORK_ITEM_COMPONENT = "backlog"
ORIGIN = "hygiene"
RESOLUTION_STATUS = "open"

DROPBOX_RELATIVE = Path("independent-progress-assessments/CODEX-INSIGHT-DROPBOX")
INSIGHTS_GLOB = "INSIGHTS-*.md"
LAST_SCAN_RELATIVE = Path(".gtkb-state/advisory-router/last-scan.json")
BRIDGE_INDEX_RELATIVE = Path("bridge/INDEX.md")

# Stage 3 (WI-4469, DELIB-20261667 D5): the router no longer auto-promotes
# advisories to OPEN work_items rows. It stages each advisory on an append-only
# candidate surface; entry into the active backlog happens only via the
# owner-batch-AUQ promotion path in scripts/hygiene/advisory_candidate_promote.py.
# The store is an append-only JSONL event log; the current status of a candidate
# is the ``event`` of its latest record (staged -> promoted/rejected), so status
# transitions preserve full provenance instead of rewriting prior records.
CANDIDATE_STORE_RELATIVE = Path(".gtkb-state/advisory-candidates/candidates.jsonl")

# Severity tokens P0-P4 in advisory bodies. The strictest match wins; we look
# for "Severity: P<n>" and "**Severity:** P<n>" patterns in both Finding-block
# headers and report frontmatter.
SEVERITY_RE = re.compile(r"\*?\*?Severity\*?\*?\s*:\s*P\s*([0-4])", re.IGNORECASE)
HIGH_SEVERITY = {"0", "1"}
MEDIUM_SEVERITY = {"2"}

INSIGHTS_DATE_RE = re.compile(r"INSIGHTS-(\d{4})-(\d{2})-(\d{2})")


@dataclass
class Advisory:
    """One advisory item the router considers for backlog routing."""

    source: str  # "dropbox" or "bridge"
    source_key: str  # idempotency key (filename or bridge slug)
    relative_path: str  # path under project root, forward-slash form
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    advisory_date: date | None = None
    related_bridge_threads: str | None = None
    severity_token: str | None = None  # raw P0..P4 string when found, else None

    def proposed_wi_title(self) -> str:
        if self.source == "dropbox":
            return f"Route LO advisory: {Path(self.relative_path).name}"
        return f"Route bridge ADVISORY: {self.source_key}"


@dataclass
class RouterResult:
    # ``staged``: advisories appended to the candidate surface this run (or, in
    # dry-run, the advisories that WOULD be staged). The router no longer creates
    # work_items rows; promotion to the active backlog is a separate owner-gated
    # step (scripts/hygiene/advisory_candidate_promote.py).
    staged: list[dict[str, Any]] = field(default_factory=list)
    skipped_existing: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    scanned: int = 0
    scan_started_at: str = ""
    scan_finished_at: str = ""
    dry_run: bool = False

    def as_json(self, *, compact: bool = False) -> str:
        if compact:
            payload = {
                "staged_count": len(self.staged),
                "skipped_existing_count": len(self.skipped_existing),
                "errors": self.errors,
                "scanned": self.scanned,
                "scan_started_at": self.scan_started_at,
                "scan_finished_at": self.scan_finished_at,
                "dry_run": self.dry_run,
            }
        else:
            payload = {
                "staged": self.staged,
                "skipped_existing": self.skipped_existing,
                "errors": self.errors,
                "scanned": self.scanned,
                "scan_started_at": self.scan_started_at,
                "scan_finished_at": self.scan_finished_at,
                "dry_run": self.dry_run,
            }
        return json.dumps(payload, indent=2, sort_keys=True)


def _project_root_from_arg(value: str | None) -> Path:
    if value:
        return Path(value).resolve()
    return Path(__file__).resolve().parent.parent


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _severity_to_priority(severity_token: str | None) -> str:
    if severity_token is None:
        return "low"
    digit = severity_token.strip().upper().removeprefix("P")
    if digit in HIGH_SEVERITY:
        return "high"
    if digit in MEDIUM_SEVERITY:
        return "medium"
    return "low"


def _extract_severity(text: str) -> str | None:
    """Return the strictest severity digit (P0..P4) found in the advisory body.

    "Strictest" = lowest digit (P0 > P1 > P2 ...). Returns None when no
    Severity header is present.
    """
    matches = SEVERITY_RE.findall(text)
    if not matches:
        return None
    digits = [m.strip() for m in matches if m.strip().isdigit()]
    if not digits:
        return None
    return f"P{min(digits)}"


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.lstrip("# ").strip() or fallback
    return fallback


def _extract_first_paragraph(text: str) -> str:
    """Return the first non-empty prose paragraph after the H1, capped to ~600 chars."""
    lines = text.splitlines()
    in_first_para = False
    buffer: list[str] = []
    past_h1 = False
    for raw in lines:
        line = raw.rstrip()
        if not past_h1:
            if line.startswith("# "):
                past_h1 = True
            continue
        stripped = line.strip()
        if not stripped:
            if in_first_para:
                break
            continue
        if stripped.startswith("#"):
            if in_first_para:
                break
            continue
        if stripped.startswith(
            (
                "**Date:",
                "**Author:",
                "**Scope:",
                "**Objective:",
                "**Disposition:",
                "Date:",
                "Author:",
                "Scope:",
                "Audience:",
                "Role:",
                "Objective:",
                "Disposition:",
            )
        ):
            continue
        in_first_para = True
        buffer.append(stripped)
    paragraph = " ".join(buffer).strip()
    if len(paragraph) > 600:
        paragraph = paragraph[:597].rstrip() + "..."
    return paragraph


def _parse_insights_date(filename: str) -> date | None:
    match = INSIGHTS_DATE_RE.match(filename)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def collect_dropbox_advisories(project_root: Path, *, since: date | None) -> list[Advisory]:
    """Scan INSIGHTS-*.md files in the dropbox; return one Advisory per file."""
    advisories: list[Advisory] = []
    dropbox = project_root / DROPBOX_RELATIVE
    if not dropbox.is_dir():
        return advisories
    for path in sorted(dropbox.glob(INSIGHTS_GLOB)):
        filename = path.name
        adv_date = _parse_insights_date(filename)
        if since is not None and adv_date is not None and adv_date < since:
            continue
        try:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        title = _extract_title(text, filename)
        description = _extract_first_paragraph(text)
        severity = _extract_severity(text)
        priority = _severity_to_priority(severity)
        rel = path.relative_to(project_root).as_posix()
        advisories.append(
            Advisory(
                source="dropbox",
                source_key=filename,
                relative_path=rel,
                title=title,
                description=description or f"LO advisory at {rel} (no first paragraph extracted).",
                priority=priority,
                advisory_date=adv_date,
                severity_token=severity,
            )
        )
    return advisories


def _iter_bridge_documents(text: str) -> Iterable[tuple[str, list[tuple[str, str]]]]:
    """Yield (doc_id, [(status, path), ...]) for every Document block in INDEX text."""
    status_re = re.compile(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|ADVISORY):\s+(bridge/.+\.md)$")
    current_id: str | None = None
    current_versions: list[tuple[str, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("Document: "):
            if current_id is not None:
                yield current_id, current_versions
            current_id = line.removeprefix("Document: ").strip()
            current_versions = []
            continue
        match = status_re.match(line)
        if current_id and match:
            current_versions.append((match.group(1), match.group(2)))
    if current_id is not None:
        yield current_id, current_versions


def collect_bridge_advisories(project_root: Path, *, since: date | None) -> list[Advisory]:
    """Scan bridge/INDEX.md for Document blocks whose latest status is ADVISORY."""
    advisories: list[Advisory] = []
    index_path = project_root / BRIDGE_INDEX_RELATIVE
    if not index_path.is_file():
        return advisories
    text = index_path.read_text(encoding="utf-8-sig", errors="replace")
    for doc_id, versions in _iter_bridge_documents(text):
        if not versions:
            continue
        latest_status, latest_path = versions[0]
        if latest_status != "ADVISORY":
            continue
        file_path = project_root / latest_path
        if not file_path.is_file():
            continue
        try:
            body = file_path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue
        title = _extract_title(body, doc_id)
        description = _extract_first_paragraph(body)
        severity = _extract_severity(body)
        priority = _severity_to_priority(severity)
        adv_date: date | None = None
        match = re.search(r"^Date:\s*(\d{4}-\d{2}-\d{2})", body, re.MULTILINE)
        if match:
            try:
                adv_date = _parse_iso_date(match.group(1))
            except ValueError:
                adv_date = None
        if since is not None and adv_date is not None and adv_date < since:
            continue
        advisories.append(
            Advisory(
                source="bridge",
                source_key=doc_id,
                relative_path=latest_path.replace("\\", "/"),
                title=title,
                description=description or f"Bridge advisory document {doc_id} at {latest_path}.",
                priority=priority,
                advisory_date=adv_date,
                related_bridge_threads=doc_id,
                severity_token=severity,
            )
        )
    return advisories


def collect_advisories(project_root: Path, *, source: str, since: date | None) -> list[Advisory]:
    items: list[Advisory] = []
    if source in {"dropbox", "both"}:
        items.extend(collect_dropbox_advisories(project_root, since=since))
    if source in {"bridge", "both"}:
        items.extend(collect_bridge_advisories(project_root, since=since))
    return items


def _existing_wi_for(db, source_key: str) -> str | None:
    """Return the WI id whose related_deliberation_ids contains ``source_key``.

    Idempotency is detected via the ``related_deliberation_ids`` field, which
    we always populate with the advisory's source_key on insert. Substring
    match keeps the check robust even when other deliberation ids share the
    field as a comma-separated list.
    """
    conn = db._get_conn()
    row = conn.execute(
        "SELECT id FROM current_work_items "
        "WHERE related_deliberation_ids IS NOT NULL "
        "AND related_deliberation_ids LIKE ? "
        "ORDER BY id LIMIT 1",
        (f"%{source_key}%",),
    ).fetchone()
    return None if row is None else row[0]


def _candidate_store_path(project_root: Path) -> Path:
    return project_root / CANDIDATE_STORE_RELATIVE


def _load_candidate_events(store_path: Path) -> list[dict[str, Any]]:
    """Read the append-only candidate event log (one JSON object per line)."""
    if not store_path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for raw_line in store_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and record.get("source_key"):
            events.append(record)
    return events


def load_candidate_events(project_root: Path) -> list[dict[str, Any]]:
    """Read candidate events from the project-rooted advisory candidate store."""
    return _load_candidate_events(_candidate_store_path(project_root))


def _record_status(record: dict[str, Any]) -> str:
    return str(record.get("status") or record.get("event") or "")


def current_candidate_status(events: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Fold the append-only event log into the latest record per source_key.

    The current status of a candidate is the ``event`` of its most recent record
    (``staged`` -> ``promoted`` / ``rejected``). Later records never rewrite
    earlier ones; provenance is preserved by append, so the log is a literal
    successor-record audit trail.
    """
    status: dict[str, dict[str, Any]] = {}
    for record in events:
        folded = dict(record)
        folded["status"] = _record_status(record)
        status[str(record["source_key"])] = folded
    return status


def stage_advisory_candidate(store_path: Path, advisory: Advisory) -> dict[str, Any]:
    """Append one ``staged`` event for ``advisory`` to the candidate store.

    Carries the advisory metadata the promotion tool needs to mint a real
    ``work_items`` row on owner-batch approval (origin/component/source_spec_id,
    title, description, priority, provenance), without creating any backlog row.
    """
    record = {
        "event": "staged",
        "status": "staged",
        "source": advisory.source,
        "source_key": advisory.source_key,
        "relative_path": advisory.relative_path,
        "proposed_title": advisory.proposed_wi_title(),
        "title": advisory.title,
        "description": advisory.description,
        "priority": advisory.priority,
        "severity_token": advisory.severity_token,
        "related_bridge_threads": advisory.related_bridge_threads,
        "advisory_date": advisory.advisory_date.isoformat() if advisory.advisory_date else None,
        "origin": ORIGIN,
        "component": WORK_ITEM_COMPONENT,
        "source_spec_id": SOURCE_SPEC_ID,
        "recorded_at": _now_iso(),
    }
    store_path.parent.mkdir(parents=True, exist_ok=True)
    with store_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")
    return record


def _write_last_scan(project_root: Path, result: RouterResult, source: str, since: date | None) -> None:
    path = project_root / LAST_SCAN_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "last_scan_started_at": result.scan_started_at,
        "last_scan_finished_at": result.scan_finished_at,
        "source": source,
        "since": since.isoformat() if since else None,
        "dry_run": result.dry_run,
        "scanned": result.scanned,
        "staged_count": len(result.staged),
        "skipped_existing_count": len(result.skipped_existing),
        "errors_count": len(result.errors),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(
    *,
    project_root: Path,
    source: str = "both",
    since: date | None = None,
    dry_run: bool = False,
    db_factory=None,
) -> RouterResult:
    """Run one router pass: stage unhandled advisories on the candidate surface.

    The router never writes work_items rows; promotion to the active backlog is
    the owner-batch-AUQ step in scripts/hygiene/advisory_candidate_promote.py.
    ``db_factory`` is for test injection and is used only for the promoted-row
    idempotency read.
    """
    result = RouterResult(dry_run=dry_run)
    result.scan_started_at = _now_iso()
    advisories = collect_advisories(project_root, source=source, since=since)
    result.scanned = len(advisories)

    store_path = _candidate_store_path(project_root)
    status_map = current_candidate_status(_load_candidate_events(store_path))

    if db_factory is None:
        from groundtruth_kb.db import KnowledgeDB

        db = KnowledgeDB(str(project_root / "groundtruth.db"))
    else:
        db = db_factory()

    for advisory in advisories:
        try:
            # Idempotency #1: already on the candidate surface (any status).
            if advisory.source_key in status_map:
                result.skipped_existing.append(
                    {
                        "source_key": advisory.source_key,
                        "source": advisory.source,
                        "matched_in": "candidate_store",
                        "matched_status": status_map[advisory.source_key].get("status"),
                    }
                )
                continue
            # Idempotency #2: already promoted to a work_items row (or a legacy
            # auto-created row from the pre-Stage-3 router).
            existing = _existing_wi_for(db, advisory.source_key)
            if existing is not None:
                result.skipped_existing.append(
                    {
                        "source_key": advisory.source_key,
                        "source": advisory.source,
                        "matched_in": "work_items",
                        "matched_wi": existing,
                    }
                )
                continue
            if dry_run:
                result.staged.append(
                    {
                        "status": "staged",
                        "source": advisory.source,
                        "source_key": advisory.source_key,
                        "proposed_title": advisory.proposed_wi_title(),
                        "priority": advisory.priority,
                    }
                )
                continue
            record = stage_advisory_candidate(store_path, advisory)
            status_map[advisory.source_key] = record
            result.staged.append(
                {
                    "status": record["status"],
                    "source": advisory.source,
                    "source_key": advisory.source_key,
                    "proposed_title": record["proposed_title"],
                    "priority": advisory.priority,
                }
            )
        except Exception as exc:  # noqa: BLE001 - any failure becomes a row in result.errors
            result.errors.append(
                {
                    "source_key": advisory.source_key,
                    "source": advisory.source,
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )

    result.scan_finished_at = _now_iso()
    if not dry_run:
        _write_last_scan(project_root, result, source=source, since=since)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report what would be staged without writing")
    parser.add_argument(
        "--source",
        choices=("dropbox", "bridge", "both"),
        default="both",
        help="which advisory surface(s) to scan (default: both)",
    )
    parser.add_argument("--since", help="ISO date (YYYY-MM-DD); skip advisories dated before this")
    parser.add_argument("--project-root", default=None, help="override project root (defaults to script parent)")
    parser.add_argument("--compact", action="store_true", help="suppress full staged and skipped lists in output JSON")
    args = parser.parse_args(argv)

    since = _parse_iso_date(args.since) if args.since else None
    root = _project_root_from_arg(args.project_root)
    result = run(project_root=root, source=args.source, since=since, dry_run=args.dry_run)
    print(result.as_json(compact=args.compact))
    return 0 if not result.errors else 1


if __name__ == "__main__":
    sys.exit(main())
