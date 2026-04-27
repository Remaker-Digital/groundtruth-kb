"""Record DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE in the Knowledge DB.

Owner-approved S312 update to DELIB-S310-ROLE-DEFINITION-ASSESSMENT. Extends
the 9-gap role-contract analysis with new empirical evidence from the
GTKB-ISOLATION-016 Wave 2 Slice 4 lifecycle (4 NO-GOs across proposal +
post-impl review). Approval packet at:

  .groundtruth/formal-artifact-approvals/2026-04-27-delib-s312-role-contract-effectiveness-update.json

Run with:

  GTKB_FORMAL_APPROVAL_PACKET=<packet-path> python scripts/archive/record_delib_s312_role_contract.py

The formal-artifact-approval-gate hook reads the env var, validates the
packet, and allows the insert_deliberation call only if the packet metadata
matches the expected shape (deliberation artifact_type, owner-approved
mode, sha256 verification, etc.).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "tools/knowledge-db")
import db  # noqa: E402


def main() -> int:
    packet_path = os.environ.get("GTKB_FORMAL_APPROVAL_PACKET")
    if not packet_path:
        print(
            "ERROR: GTKB_FORMAL_APPROVAL_PACKET env var not set. "
            "This script is gated by the formal-artifact-approval hook.",
            file=sys.stderr,
        )
        return 2

    packet = json.loads(Path(packet_path).read_text(encoding="utf-8"))

    if packet.get("artifact_id") != "DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE":
        print(
            f"ERROR: packet artifact_id mismatch: "
            f"{packet.get('artifact_id')!r} != "
            f"'DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE'",
            file=sys.stderr,
        )
        return 2

    content = packet["full_content"]
    summary = (
        "S312 update to the Prime Builder / Loyal Opposition role-contract "
        "effectiveness assessment. Confirms the 9-gap analysis from "
        "DELIB-S310 with new empirical evidence from the GTKB-ISOLATION-016 "
        "Wave 2 Slice 4 lifecycle (4 distinct NO-GOs across proposal and "
        "post-impl review). Concludes: (1) LO evaluation scope spans "
        "technology choices, design patterns, scope drift, completeness "
        "interpretation, and test/error-handling semantics — well beyond "
        "the floor described in .claude/rules/loyal-opposition.md; (2) the "
        "role contract is sufficient for current single-owner two-harness "
        "work but the 9 gaps from DELIB-S310 remain real; (3) one near-term "
        "low-cost clause would mitigate the most expensive gap surfaced "
        "this session: a review-depth heuristic specifying that LO walks "
        "proposal §4 output contracts against returned output_files lists "
        "at proposal review (not just post-impl). Continued deferral of "
        "the formal GTKB-ROLE-ENHANCEMENT implementation until "
        "post-isolation remains defensible."
    )

    kdb = db.KnowledgeDB()
    kdb.insert_deliberation(
        id=packet["artifact_id"],
        source_type="owner_conversation",
        title="Role-Contract Effectiveness Update (S312)",
        summary=summary,
        content=content,
        changed_by=packet["changed_by"],
        change_reason=packet["change_reason"],
        outcome="informational",
        session_id="S312",
        source_ref=packet["source_ref"],
    )

    print(f"Inserted {packet['artifact_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
