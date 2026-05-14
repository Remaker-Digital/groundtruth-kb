#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Assertion Retirement Workflow (Slice 3 IP-2).

Per ``bridge/gtkb-self-diagnostic-leak-closure-slice-3-assertion-triage-007.md``
(Codex GO at -008). One-at-a-time owner-decision workflow for chronic_noise
assertions identified by ``scripts/assertion_categorize.py``.

Three modes:
- ``review-candidates``: read-only listing.
- ``ask <assertion_id>``: emit AUQ-ready question envelope.
- ``apply-decision <assertion_id> --decision <retire|accept|keep> --packet <path>``: apply.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path
from typing import Any

CATEGORY_CHRONIC_NOISE = "chronic_noise"
VALID_DECISIONS = {"retire", "accept", "keep"}


def _resolve_project_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    env_root = os.environ.get("GTKB_PROJECT_ROOT")
    if env_root:
        return Path(env_root).resolve()
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    raise SystemExit("Could not resolve GT-KB project root.")


def _load_categories(triage_dir: Path) -> list[dict[str, Any]]:
    categories_dir = triage_dir / "categories"
    if not categories_dir.is_dir():
        return []
    records = []
    for json_path in sorted(categories_dir.glob("*.json")):
        try:
            record = json.loads(json_path.read_text(encoding="utf-8"))
            record["_source_path"] = str(json_path)
            records.append(record)
        except (json.JSONDecodeError, OSError):
            continue
    return records


def _chronic_candidates(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [r for r in records if r.get("category") == CATEGORY_CHRONIC_NOISE],
        key=lambda r: (r.get("spec_id", ""), r.get("assertion_index", 0)),
    )


def review_candidates(triage_dir: Path, max_show: int = 50) -> dict[str, Any]:
    records = _load_categories(triage_dir)
    candidates = _chronic_candidates(records)
    lines = [
        "# Chronic Noise Retirement Candidates",
        "",
        f"Generated: {dt.datetime.now(dt.UTC).isoformat(timespec='seconds')}",
        f"Total chronic_noise candidates: {len(candidates)}",
        f"Showing top {min(max_show, len(candidates))}",
        "",
    ]
    for record in candidates[:max_show]:
        lines.append(f"## {record['assertion_id']}")
        lines.append(f"- spec_id: `{record['spec_id']}` (status: {record.get('spec_status', 'unknown')})")
        lines.append(f"- description: {record['description']}")
        lines.append(f"- rationale: {record['rationale']}")
        lines.append(f"- latest_detail: {(record.get('latest_detail') or '(none)')[:200]}")
        lines.append(f"- history_length: {record.get('history_length', 0)} runs")
        lines.append("")
    return {
        "total_candidates": len(candidates),
        "shown": min(max_show, len(candidates)),
        "markdown": "\n".join(lines),
        "candidates": candidates[:max_show],
    }


def build_question_envelope(assertion_id: str, triage_dir: Path) -> dict[str, Any]:
    records = _load_categories(triage_dir)
    target = next((r for r in records if r["assertion_id"] == assertion_id), None)
    if target is None:
        return {"error": f"assertion_id not found: {assertion_id}"}
    if target.get("category") != CATEGORY_CHRONIC_NOISE:
        return {"error": f"assertion {assertion_id} is category {target.get('category')}, not chronic_noise"}
    question_text = (
        f"Retirement decision for assertion {assertion_id}\n\n"
        f"Spec: {target['spec_id']} (status: {target.get('spec_status', 'unknown')})\n"
        f"Description: {target['description']}\n"
        f"Rationale: {target['rationale']}\n\n"
        f"How should this chronic-noise assertion be handled?"
    )
    return {
        "tool": "AskUserQuestion",
        "assertion_id": assertion_id,
        "spec_id": target["spec_id"],
        "question": {
            "question": question_text,
            "header": "Assertion triage",
            "multiSelect": False,
            "options": [
                {"label": "Retire the assertion",
                 "description": "Mark spec as retired in MemBase. Assertion no longer in failing-count rollup."},
                {"label": "Accept the failure as expected",
                 "description": "Record acceptance; spec status unchanged; assertion flagged expected_fail."},
                {"label": "Keep and schedule repair",
                 "description": "No retirement, no acceptance. Flagged for test-quality repair."},
            ],
        },
    }


def _validate_packet(packet_path: Path) -> dict[str, Any]:
    if not packet_path.is_file():
        raise SystemExit(f"Packet file not found: {packet_path}")
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Packet is not valid JSON: {e}") from e
    required = ["tool", "assertion_id", "decision", "approved_by", "approved_at"]
    missing = [k for k in required if k not in packet]
    if missing:
        raise SystemExit(f"Packet missing required fields: {missing}")
    if packet["tool"] != "AskUserQuestion":
        raise SystemExit(f"Packet tool must be 'AskUserQuestion', got: {packet['tool']!r}")
    if packet["approved_by"] != "owner":
        raise SystemExit(f"Packet approved_by must be 'owner', got: {packet['approved_by']!r}")
    if packet["decision"] not in VALID_DECISIONS:
        raise SystemExit(f"Packet decision must be one of {VALID_DECISIONS}, got: {packet['decision']!r}")
    return packet


def apply_decision(project_root: Path, triage_dir: Path, assertion_id: str,
                   decision: str, packet_path: Path) -> dict[str, Any]:
    if decision not in VALID_DECISIONS:
        raise SystemExit(f"Invalid decision: {decision!r}")
    packet = _validate_packet(packet_path)
    if packet["assertion_id"] != assertion_id:
        raise SystemExit(f"Packet assertion_id mismatch: {packet['assertion_id']} != {assertion_id}")
    if packet["decision"] != decision:
        raise SystemExit(f"Packet decision mismatch: {packet['decision']} != {decision}")
    records = _load_categories(triage_dir)
    target = next((r for r in records if r["assertion_id"] == assertion_id), None)
    if target is None:
        raise SystemExit(f"assertion_id not found: {assertion_id}")
    if decision == "retire":
        raise SystemExit(
            "Refusing retire decision: governed spec retirement requires the "
            "follow-on bridge gtkb-governed-spec-retirement-001 to land first. "
            "Use `accept` or `keep` for this assertion, or wait for the follow-on bridge."
        )
    decisions_dir = triage_dir / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    decision_path = decisions_dir / f"{assertion_id}.json"
    decision_record = {
        "assertion_id": assertion_id,
        "spec_id": target["spec_id"],
        "decision": decision,
        "packet_path": str(packet_path),
        "applied_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "category_at_decision": target.get("category"),
        "description": target["description"],
        "spec_update_result": None,
    }
    decision_path.write_text(json.dumps(decision_record, indent=2, sort_keys=True), encoding="utf-8")
    return {"decision_path": str(decision_path), "decision": decision,
            "assertion_id": assertion_id, "spec_update_result": None}


def main() -> int:
    parser = argparse.ArgumentParser(description="One-at-a-time retirement workflow for chronic_noise assertions.")
    parser.add_argument("--project-root")
    parser.add_argument("--triage-dir")
    sub = parser.add_subparsers(dest="mode", required=True)
    sub_review = sub.add_parser("review-candidates")
    sub_review.add_argument("--max-show", type=int, default=50)
    sub_ask = sub.add_parser("ask")
    sub_ask.add_argument("assertion_id")
    sub_apply = sub.add_parser("apply-decision")
    sub_apply.add_argument("assertion_id")
    sub_apply.add_argument("--decision", choices=sorted(VALID_DECISIONS), required=True)
    sub_apply.add_argument("--packet", required=True)
    args = parser.parse_args()
    project_root = _resolve_project_root(args.project_root)
    triage_dir = (Path(args.triage_dir).resolve() if args.triage_dir
                  else project_root / ".gtkb-state" / "assertion-triage")
    if args.mode == "review-candidates":
        result = review_candidates(triage_dir, max_show=args.max_show)
        print(result["markdown"])
        return 0
    if args.mode == "ask":
        envelope = build_question_envelope(args.assertion_id, triage_dir)
        print(json.dumps(envelope, indent=2, sort_keys=True))
        return 0 if "error" not in envelope else 1
    if args.mode == "apply-decision":
        result = apply_decision(project_root=project_root, triage_dir=triage_dir,
                                assertion_id=args.assertion_id, decision=args.decision,
                                packet_path=Path(args.packet).resolve())
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
