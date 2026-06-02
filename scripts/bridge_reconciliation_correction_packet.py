#!/usr/bin/env python3
"""Generate dry-run bridge reconciliation correction packets.

Consumes read-only audit JSON from the bridge reconciliation detectors and
emits a single-class correction packet. The generator never mutates MemBase,
bridge files, project rows, or deliberation state.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

WORK_ITEM_RE = re.compile(r"^WI-\d+$")
HIGH_PRIORITY = {"P0", "P1", "P2"}
TERMINAL_STATUSES = {
    "resolved",
    "retired",
    "withdrawn",
    "obsolete",
    "obsoleted",
    "duplicate",
    "closed",
    "not_planned",
    "not-planned",
}

MUTATION_TYPES = {
    "bridge_index_chain_deviation": "bridge_index_correction_packet",
    "bridge_index_drift": "bridge_index_correction_packet",
    "missing_or_incorrect_related_bridge_threads": "related_bridge_threads_update",
    "stale_backlog_status": "backlog_terminal_status_update",
    "terminal_backlog_without_evidence": "completion_evidence_or_reopen_review",
    "verified_bridge_missing_terminal_backlog_state": "backlog_terminal_status_update",
    "verified_bridge_without_backlog_match": "backlog_linkage_intake",
}

REQUIRED_GATES = [
    "single triage class only",
    "owner decision recorded one at a time before mutation",
    "bridge GO for any mutation proposal",
    "implementation-start packet before file or MemBase mutation",
    "post-implementation report after mutation",
    "Loyal Opposition verification before terminal closure",
]

FORBIDDEN_ACTIONS = [
    "no backlog update",
    "no project update",
    "no bridge/INDEX.md edit",
    "no bridge writer helper invocation",
    "no deliberation mutation",
]


def validate_triage_class(triage_class: str) -> str:
    cleaned = triage_class.strip()
    if not cleaned:
        raise ValueError("A non-empty triage class is required.")
    if any(separator in cleaned for separator in [",", ";", "+"]):
        raise ValueError("Specify exactly one triage class; combined classes are refused.")
    if len(cleaned.split()) > 1:
        raise ValueError("Specify exactly one triage class; whitespace-separated classes are refused.")
    return cleaned


def load_audit_input(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _selected(issue: dict[str, Any], triage_class: str) -> bool:
    return issue.get("class") == triage_class or issue.get("type") == triage_class


def _mutation_type(issue: dict[str, Any], triage_class: str) -> str:
    return (
        MUTATION_TYPES.get(str(issue.get("class") or ""))
        or MUTATION_TYPES.get(str(issue.get("type") or ""))
        or MUTATION_TYPES.get(triage_class)
        or "manual_reconciliation_review"
    )


def _priority(evidence: dict[str, Any]) -> str:
    return str(evidence.get("priority") or evidence.get("work_item_priority") or "unknown")


def _nonterminal(evidence: dict[str, Any]) -> bool:
    status = str(evidence.get("resolution_status") or "").lower()
    return bool(status) and status not in TERMINAL_STATUSES


def _verified_metadata(issue: dict[str, Any]) -> bool:
    text = json.dumps(issue.get("evidence", {}), sort_keys=True).upper()
    return "VERIFIED" in text or str(issue.get("class", "")).startswith("verified_bridge")


def _bridge_evidence_paths(value: Any) -> list[str]:
    paths: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            for key, item in node.items():
                lowered = str(key).lower()
                if (
                    "path" in lowered
                    or "bridge" in lowered
                    or "thread" in lowered
                    or isinstance(item, (dict, list, tuple))
                ):
                    visit(item)
        elif isinstance(node, (list, tuple)):
            for item in node:
                visit(item)
        elif isinstance(node, str):
            if node.startswith("bridge/") or node.startswith("gtkb-"):
                paths.append(node)

    visit(value)
    return sorted(dict.fromkeys(paths))


def _candidate(issue: dict[str, Any], triage_class: str) -> dict[str, Any]:
    evidence = issue.get("evidence") if isinstance(issue.get("evidence"), dict) else {}
    subject = str(issue.get("subject") or "")
    priority = _priority(evidence)
    nonterminal = _nonterminal(evidence)
    verified = _verified_metadata(issue)
    return {
        "subject": subject,
        "work_item_id": subject if WORK_ITEM_RE.match(subject) else evidence.get("work_item_id"),
        "issue_class": issue.get("class"),
        "issue_type": issue.get("type"),
        "severity": issue.get("severity", "P3"),
        "priority": priority,
        "stage": evidence.get("stage"),
        "resolution_status": evidence.get("resolution_status"),
        "verified_bridge_metadata": verified,
        "proposed_mutation_type": _mutation_type(issue, triage_class),
        "evidence": evidence,
        "bridge_evidence_paths": _bridge_evidence_paths(evidence),
        "risk_notes": list(issue.get("risk_notes") or [])
        + ["dry-run packet only; no correction is approved by this output"],
        "recommended_action": issue.get("recommended_action"),
        "confidence": "high" if priority in HIGH_PRIORITY and nonterminal and verified else "medium",
        "required_gates": REQUIRED_GATES,
    }


def _candidate_sort_key(candidate: dict[str, Any]) -> tuple[int, int, int, str]:
    priority = str(candidate.get("priority") or "unknown")
    high_priority_rank = 0 if priority in HIGH_PRIORITY else 1
    terminal_rank = (
        0
        if candidate.get("resolution_status") and str(candidate["resolution_status"]).lower() not in TERMINAL_STATUSES
        else 1
    )
    verified_rank = 0 if candidate.get("verified_bridge_metadata") else 1
    return (high_priority_rank, terminal_rank, verified_rank, str(candidate.get("subject") or ""))


def build_packet(audit: dict[str, Any], *, triage_class: str, limit: int | None = None) -> dict[str, Any]:
    selected_class = validate_triage_class(triage_class)
    issues = audit.get("issues")
    if not isinstance(issues, list):
        raise ValueError("Audit JSON must contain an issues list.")
    selected_issues = [issue for issue in issues if isinstance(issue, dict) and _selected(issue, selected_class)]
    candidates = [_candidate(issue, selected_class) for issue in selected_issues]
    candidates.sort(key=_candidate_sort_key)
    if limit is not None:
        candidates = candidates[:limit]
    excluded = [issue for issue in issues if isinstance(issue, dict) and not _selected(issue, selected_class)]
    exclusion_counts = Counter(str(issue.get("class") or issue.get("type") or "unknown") for issue in excluded)
    return {
        "schema_version": 1,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "dry_run": True,
        "triage_class": selected_class,
        "source_audit": {
            "generated_at": audit.get("generated_at"),
            "bridge_index": audit.get("bridge_index"),
            "db_path": audit.get("db_path"),
            "issue_count": audit.get("issue_count"),
        },
        "candidate_count": len(candidates),
        "candidates": candidates,
        "exclusions": {
            "excluded_count": len(excluded),
            "reason": "different triage class",
            "counts_by_class_or_type": dict(sorted(exclusion_counts.items())),
        },
        "owner_decision_slots": [
            {
                "id": "owner-approval",
                "required": bool(candidates),
                "prompt": f"Approve one governed correction packet for `{selected_class}` after bridge review.",
            }
        ],
        "required_gates": REQUIRED_GATES,
        "forbidden_actions": FORBIDDEN_ACTIONS,
    }


def render_markdown_packet(packet: dict[str, Any]) -> str:
    lines = [
        "# Bridge Reconciliation Correction Packet",
        "",
        f"- generated_at: `{packet['generated_at']}`",
        f"- dry_run: `{str(packet['dry_run']).lower()}`",
        f"- triage_class: `{packet['triage_class']}`",
        f"- candidate_count: {packet['candidate_count']}",
        "",
        "## Required Gates",
    ]
    lines.extend(f"- {gate}" for gate in packet["required_gates"])
    lines.extend(["", "## Forbidden Actions"])
    lines.extend(f"- {action}" for action in packet["forbidden_actions"])
    lines.extend(["", "## Candidates"])
    for candidate in packet["candidates"][:20]:
        lines.append(
            "- "
            f"{candidate['subject']} "
            f"[{candidate['priority']}, {candidate['resolution_status']}, {candidate['proposed_mutation_type']}]"
        )
    if not packet["candidates"]:
        lines.append("- none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Audit JSON file to consume.")
    parser.add_argument("--class", dest="triage_class", required=True, help="Single triage class to packetize.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum candidate count.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)
    try:
        packet = build_packet(load_audit_input(args.input), triage_class=args.triage_class, limit=args.limit)
    except ValueError as exc:
        parser.error(str(exc))
    if args.json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(render_markdown_packet(packet))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
