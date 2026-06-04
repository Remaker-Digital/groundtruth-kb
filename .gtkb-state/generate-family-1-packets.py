"""Generate formal-artifact-approval packets for Family 1 (envelope-program core).

Per AUQ DECISION (2026-06-04): batch-by-family approval of 7 GO-terminal
governance_review spec bodies. Each spec body is extracted from its
GO-endorsed bridge operative_file (NOT necessarily the -001 NEW), hashed,
and emitted as a packet JSON at
.groundtruth/formal-artifact-approvals/2026-06-04-<artifact-id>.json.

This helper extracts the section between a body-marker heading and the next
`## ` heading. It does NOT mutate MemBase; that's a separate authorized step.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# (artifact_id, artifact_type, source_bridge_file, body_marker_heading, source_proposal_id)
PACKETS = [
    (
        "SPEC-CANONICAL-WRAP-KEYWORD-SYNTAX-001",
        "specification",
        "bridge/gtkb-canonical-wrap-keyword-syntax-001-003.md",
        "## Spec Body — Canonical Wrap-Keyword Syntax Spec (REVISED-2 draft)",
        "gtkb-canonical-wrap-keyword-syntax-001 GO at -004",
    ),
    (
        "DCL-SESSION-ENVELOPE-DURABILITY-001",
        "design_constraint",
        "bridge/gtkb-session-envelope-durability-001-005.md",
        "## Revised DCL Body",
        "gtkb-session-envelope-durability-001 GO at -006",
    ),
    (
        "SPEC-DISPATCH-ENVELOPE-ELEMENT-001",
        "specification",
        "bridge/gtkb-envelope-dispatch-element-001-001.md",
        "## Spec Body — SPEC-DISPATCH-ENVELOPE-ELEMENT-001 (draft)",
        "gtkb-envelope-dispatch-element-001 GO at -002",
    ),
    (
        "DCL-DISPATCH-ENVELOPE-RULES-001",
        "design_constraint",
        "bridge/gtkb-envelope-dispatch-element-001-001.md",
        "## Spec Body — DCL-DISPATCH-ENVELOPE-RULES-001 (draft)",
        "gtkb-envelope-dispatch-element-001 GO at -002",
    ),
    (
        "SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001",
        "specification",
        "bridge/gtkb-session-wrap-procedure-001-003.md",
        "## Spec Body — SPEC-SESSION-WRAP-PROCEDURE-DETERMINISTIC-TRIGGER-001 (REVISED-2 draft)",
        "gtkb-session-wrap-procedure-001 GO at -004",
    ),
    (
        "SPEC-PROJECT-COMPLETION-DRIVE-PAYLOAD-001",
        "specification",
        "bridge/gtkb-project-completion-drive-payload-001-001.md",
        "## Spec Body — SPEC-PROJECT-COMPLETION-DRIVE-PAYLOAD-001 (draft)",
        "gtkb-project-completion-drive-payload-001 GO at -002",
    ),
    (
        "DCL-BRIDGE-VERDICT-AUQ-CLASS-MARKER-001",
        "design_constraint",
        "bridge/gtkb-project-completion-drive-payload-001-001.md",
        "## Spec Body — DCL-BRIDGE-VERDICT-AUQ-CLASS-MARKER-001 (draft)",
        "gtkb-project-completion-drive-payload-001 GO at -002",
    ),
]


def extract_body(text: str, marker: str) -> str:
    """Extract the section starting at marker line through the next `## ` heading.

    Returns the body without the marker heading itself.
    """
    lines = text.splitlines(keepends=True)
    start_idx = None
    for i, line in enumerate(lines):
        if line.rstrip("\r\n") == marker:
            start_idx = i + 1
            break
    if start_idx is None:
        raise ValueError(f"Marker not found: {marker!r}")
    end_idx = len(lines)
    for j in range(start_idx, len(lines)):
        if lines[j].startswith("## ") and not lines[j].startswith("### "):
            end_idx = j
            break
    body = "".join(lines[start_idx:end_idx])
    # Trim trailing blank lines but keep a terminal newline if non-empty.
    body = body.rstrip() + "\n"
    return body


def make_packet(
    artifact_id: str,
    artifact_type: str,
    full_content: str,
    source_proposal_id: str,
) -> dict:
    sha = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    return {
        "action": "create",
        "approval_mode": "approve",
        "approved_by": "owner",
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "change_reason": (
            f"Per owner AUQ DECISION (2026-06-04, S407+ session): "
            f"approve Family 1 envelope-program core packet generation against "
            f"bridge-GO-endorsed bodies. Source proposal: {source_proposal_id}. "
            f"Body extracted from operative_file cited by the GO verdict."
        ),
        "changed_by": "gt-cli",
        "explicit_change_request": (
            "AUQ batch approval (Family 1): approve all 7 envelope-program core "
            "specs for packet generation; insertion deferred to a separate authorized step."
        ),
        "full_content": full_content,
        "full_content_sha256": sha,
        "presented_to_user": True,
        "source_ref": artifact_id,
        "transcript_captured": True,
    }


def main() -> int:
    out_dir = REPO / ".groundtruth" / "formal-artifact-approvals"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for artifact_id, artifact_type, source_path, marker, source_proposal_id in PACKETS:
        source = REPO / source_path
        text = source.read_text(encoding="utf-8")
        body = extract_body(text, marker)
        packet = make_packet(artifact_id, artifact_type, body, source_proposal_id)
        out_path = out_dir / f"2026-06-04-{artifact_id}.json"
        out_path.write_text(
            json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        results.append(
            {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "packet_path": str(out_path.relative_to(REPO)).replace("\\", "/"),
                "sha256": packet["full_content_sha256"],
                "body_bytes": len(body.encode("utf-8")),
                "source_file": source_path,
            }
        )

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
