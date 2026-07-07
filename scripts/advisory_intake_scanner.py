#!/usr/bin/env python3
"""Advisory intake scanner tool.

Selects only live ADVISORY entries with adopt/adapt classification and
a Required Prime Builder Owner-Grilling Gate section, then summarizes them
for Prime intake.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

from scripts.advisory_backlog_router import (  # noqa: E402
    _candidate_store_path,
    _load_candidate_events,
    collect_advisories,
    current_candidate_status,
    is_live_advisory,
)
from scripts.advisory_grilling_gate_lint import (  # noqa: E402
    extract_classification,
    has_gate_heading,
)


@dataclass
class ScannedAdvisory:
    source_key: str
    source: str
    relative_path: str
    title: str
    description: str
    classification: str
    priority: str
    advisory_date: str | None
    has_grilling_gate: bool


def scan_intake_advisories(
    project_root: Path,
    source: str = "both",
    since: date | None = None,
    db_factory=None,
) -> list[ScannedAdvisory]:
    """Scan and filter advisories matching intake criteria."""
    advisories = collect_advisories(project_root, source=source, since=since)

    store_path = _candidate_store_path(project_root)
    status_map = current_candidate_status(_load_candidate_events(store_path))

    if db_factory is None:
        db = KnowledgeDB(str(project_root / "groundtruth.db"))
    else:
        db = db_factory()

    results: list[ScannedAdvisory] = []

    for advisory in advisories:
        # 1. Must be live (not promoted/rejected in candidate store, and not in DB)
        if not is_live_advisory(db, status_map, advisory.source_key):
            continue

        # Read the file to extract classification and gate heading presence
        file_path = project_root / advisory.relative_path
        if not file_path.is_file():
            continue

        try:
            text = file_path.read_text(encoding="utf-8-sig", errors="replace")
        except OSError:
            continue

        classification = extract_classification(text)

        # 2. Must be adopt or adapt
        if classification not in {"adopt", "adapt"}:
            continue

        # 3. Must contain the Owner-Grilling Gate heading
        if not has_gate_heading(text):
            continue

        results.append(
            ScannedAdvisory(
                source_key=advisory.source_key,
                source=advisory.source,
                relative_path=advisory.relative_path,
                title=advisory.title,
                description=advisory.description,
                classification=classification,
                priority=advisory.priority,
                advisory_date=advisory.advisory_date.isoformat() if advisory.advisory_date else None,
                has_grilling_gate=True,
            )
        )

    # Sort deterministically:
    # 1. Date (ascending, None last)
    # 2. Priority (high > medium > low)
    # 3. source_key (alphabetical)
    priority_order = {"high": 0, "medium": 1, "low": 2}

    def sort_key(adv: ScannedAdvisory):
        adv_date = date.fromisoformat(adv.advisory_date) if adv.advisory_date else date.max
        prio_val = priority_order.get(adv.priority, 3)
        return (adv_date, prio_val, adv.source_key)

    results.sort(key=sort_key)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        choices=("dropbox", "bridge", "both"),
        default="both",
        help="which advisory surface(s) to scan (default: both)",
    )
    parser.add_argument("--since", help="ISO date (YYYY-MM-DD); skip advisories dated before this")
    parser.add_argument("--project-root", default=None, help="override project root")
    parser.add_argument("--json", action="store_true", help="output JSON format")
    args = parser.parse_args(argv)

    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = PROJECT_ROOT

    since_date = None
    if args.since:
        try:
            since_date = datetime.strptime(args.since, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Invalid date format for --since: {args.since}", file=sys.stderr)
            return 1

    try:
        intake_ready = scan_intake_advisories(project_root, source=args.source, since=since_date)
    except Exception as exc:
        print(f"Error during scan: {exc}", file=sys.stderr)
        return 1

    if args.json:
        payload = {
            "intake_ready": [
                {
                    "source_key": adv.source_key,
                    "source": adv.source,
                    "relative_path": adv.relative_path,
                    "title": adv.title,
                    "description": adv.description,
                    "classification": adv.classification,
                    "priority": adv.priority,
                    "advisory_date": adv.advisory_date,
                    "has_grilling_gate": adv.has_grilling_gate,
                }
                for adv in intake_ready
            ],
            "scanned_count": len(collect_advisories(project_root, source=args.source, since=since_date)),
            "intake_ready_count": len(intake_ready),
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"Advisory Intake Scanner: Found {len(intake_ready)} live intake-ready adopt/adapt advisories:")
        for idx, adv in enumerate(intake_ready, 1):
            date_str = f" [{adv.advisory_date}]" if adv.advisory_date else ""
            print(f"{idx}. {adv.source_key}{date_str} ({adv.source}, {adv.priority}) - title: {adv.title}")
            print(f"   path: {adv.relative_path}")
            print(f"   classification: {adv.classification}")
            print(f"   description: {adv.description}")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
