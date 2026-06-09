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
                {
                    "label": "Retire the assertion",
                    "description": "Mark spec as retired in MemBase. Assertion no longer in failing-count rollup.",
                },
                {
                    "label": "Accept the failure as expected",
                    "description": "Record acceptance; spec status unchanged; assertion flagged expected_fail.",
                },
                {
                    "label": "Keep and schedule repair",
                    "description": "No retirement, no acceptance. Flagged for test-quality repair.",
                },
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


def _validate_formal_packet(packet_path: Path) -> dict[str, Any]:
    """Validate a formal-artifact approval packet via the shared schema validator.

    Delegates schema/hash/expiry validation to
    ``groundtruth_kb.governance.approval_packet.validate_packet`` and additionally
    enforces ``presented_to_user=True`` and ``transcript_captured=True``.

    Returns the parsed packet on success; raises ``SystemExit`` otherwise.
    """
    if not packet_path.is_file():
        raise SystemExit(f"Formal-approval packet file not found: {packet_path}")
    try:
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SystemExit(f"Formal-approval packet is not valid JSON: {e}") from e
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root / "groundtruth-kb" / "src"))
    from groundtruth_kb.governance.approval_packet import validate_packet

    result = validate_packet(packet)
    if not result.is_valid:
        raise SystemExit("Formal-approval packet invalid: " + "; ".join(result.errors))
    if packet.get("presented_to_user") is not True:
        raise SystemExit("Formal-approval packet requires presented_to_user=true")
    if packet.get("transcript_captured") is not True:
        raise SystemExit("Formal-approval packet requires transcript_captured=true")
    return packet


def apply_decision(
    project_root: Path,
    triage_dir: Path,
    assertion_id: str,
    decision: str,
    packet_path: Path,
    formal_packet_path: Path | None = None,
) -> dict[str, Any]:
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
    spec_update_result = None
    if decision == "retire":
        if formal_packet_path is None:
            raise SystemExit(
                "retire decision requires --formal-approval-packet pointing at a "
                "formal-artifact approval packet matching the spec's artifact_type"
            )
        formal_packet = _validate_formal_packet(formal_packet_path)
        spec_update_result = _retire_spec(project_root, target["spec_id"], assertion_id, packet, formal_packet)
    decisions_dir = triage_dir / "decisions"
    decisions_dir.mkdir(parents=True, exist_ok=True)
    decision_path = decisions_dir / f"{assertion_id}.json"
    decision_record = {
        "assertion_id": assertion_id,
        "spec_id": target["spec_id"],
        "decision": decision,
        "packet_path": str(packet_path),
        "formal_packet_path": str(formal_packet_path) if formal_packet_path else None,
        "applied_at": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
        "category_at_decision": target.get("category"),
        "description": target["description"],
        "spec_update_result": spec_update_result,
    }
    decision_path.write_text(json.dumps(decision_record, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "decision_path": str(decision_path),
        "decision": decision,
        "assertion_id": assertion_id,
        "spec_update_result": spec_update_result,
    }


def _retire_spec(
    project_root: Path, spec_id: str, assertion_id: str, auq_packet: dict[str, Any], formal_packet: dict[str, Any]
) -> dict[str, Any]:
    """Retire a spec via KnowledgeDB.update_spec, gated by tightly-bound formal packet.

    Tight binding (per REVISED-2 F1 fix at bridge/gtkb-governed-spec-retirement-005.md):
    - formal_packet["artifact_id"] == spec_id
    - formal_packet["action"] == "retire"
    - formal_packet["full_content"] matches the canonical transition marker
      f"spec_id={spec_id};from_status={current_status};to_status=retired;current_version={current_version}"
    - formal_packet["artifact_type"] == current spec's "type" field
    """
    sys.path.insert(0, str(project_root / "tools" / "knowledge-db"))
    from db import KnowledgeDB

    db = KnowledgeDB(str(project_root / "groundtruth.db"))
    try:
        current = db.get_spec(spec_id)
        if not current:
            raise SystemExit(f"Spec {spec_id} not found")
        if current["status"] == "retired":
            raise SystemExit(f"Spec {spec_id} is already retired")

        if formal_packet.get("artifact_id") != spec_id:
            raise SystemExit(
                f"Formal-artifact packet artifact_id mismatch: packet says "
                f"{formal_packet.get('artifact_id')!r} but retirement target is {spec_id!r}"
            )

        if formal_packet.get("action") != "retire":
            raise SystemExit(
                f"Formal-artifact packet action mismatch: packet says "
                f"{formal_packet.get('action')!r}, but governed retirement requires action='retire'"
            )

        expected_marker = (
            f"spec_id={spec_id};from_status={current['status']};to_status=retired;current_version={current['version']}"
        )
        full_content = formal_packet.get("full_content", "")
        if not (full_content == expected_marker or full_content.startswith(expected_marker + "\n")):
            raise SystemExit(
                f"Formal-artifact packet full_content does not match expected transition marker. "
                f"Expected: {expected_marker!r}. Got prefix: {full_content[:120]!r}"
            )

        expected_artifact_type = current["type"]
        if formal_packet.get("artifact_type") != expected_artifact_type:
            raise SystemExit(
                f"Formal-artifact packet artifact_type mismatch: packet says "
                f"{formal_packet.get('artifact_type')!r} but spec {spec_id} is type "
                f"{expected_artifact_type!r}"
            )

        new_row = db.update_spec(
            id=spec_id,
            changed_by="assertion-retirement-workflow@2.0",
            change_reason=(
                f"Retired via assertion_retirement_workflow.py for assertion {assertion_id} "
                f"(chronic_noise category, owner AUQ approved {auq_packet.get('approved_at', '?')}, "
                f"formal-artifact approval packet sha256:{str(formal_packet.get('full_content_sha256', '?'))[:12]}... "
                f"at {formal_packet.get('source_ref', '?')})"
            ),
            status="retired",
        )
        return {
            "spec_id": spec_id,
            "previous_version": current["version"],
            "new_version": new_row["version"],
            "new_status": "retired",
        }
    finally:
        db.close()


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
    sub_apply.add_argument("--packet", required=True, help="AUQ owner-decision packet path")
    sub_apply.add_argument("--formal-approval-packet", help="Formal-artifact approval packet; required for retire")
    args = parser.parse_args()
    project_root = _resolve_project_root(args.project_root)
    triage_dir = (
        Path(args.triage_dir).resolve() if args.triage_dir else project_root / ".gtkb-state" / "assertion-triage"
    )
    if args.mode == "review-candidates":
        result = review_candidates(triage_dir, max_show=args.max_show)
        print(result["markdown"])
        return 0
    if args.mode == "ask":
        envelope = build_question_envelope(args.assertion_id, triage_dir)
        print(json.dumps(envelope, indent=2, sort_keys=True))
        return 0 if "error" not in envelope else 1
    if args.mode == "apply-decision":
        formal_path = Path(args.formal_approval_packet).resolve() if args.formal_approval_packet else None
        result = apply_decision(
            project_root=project_root,
            triage_dir=triage_dir,
            assertion_id=args.assertion_id,
            decision=args.decision,
            packet_path=Path(args.packet).resolve(),
            formal_packet_path=formal_path,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
