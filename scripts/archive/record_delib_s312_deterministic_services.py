"""Record DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE in the Knowledge DB.

Owner-stated guiding principle that repetitive AI work is a defect;
deterministic plumbing belongs in services, not in sessions. Extends
GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (DELIB-0874) with explicit
cost-and-error rationale and an active-pursuit mandate.

Approval packet at:

  .groundtruth/formal-artifact-approvals/2026-04-27-delib-s312-deterministic-services-principle.json

Run with:

  GTKB_FORMAL_APPROVAL_PACKET=<packet-path> python scripts/archive/record_delib_s312_deterministic_services.py

Note: this insertion is itself an instance of the principle being
recorded (~150 LOC of orchestration for a single DA entry). After
GTKB-ARTIFACT-RECORDER-CLI ships, future principle-captures will be a
single CLI call.

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

    if packet.get("artifact_id") != "DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE":
        print(
            f"ERROR: packet artifact_id mismatch: "
            f"{packet.get('artifact_id')!r} != "
            f"'DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE'",
            file=sys.stderr,
        )
        return 2

    content = packet["full_content"]
    summary = (
        "Owner-stated guiding principle (S312, 2026-04-27): repetitive AI "
        "work is a defect. Deterministic plumbing (structured records, "
        "hashes, parameter threading, boilerplate scripts) belongs in "
        "services, not in sessions. Justification: token cost (recurring "
        "tax) + error rate (AI procedures more error-prone than "
        "deterministic implementations) + project framing (collection of "
        "artifacts > dialog with activity). Operational mandate: when "
        "Prime Builder notices repetitive plumbing, surface it explicitly, "
        "file as backlog item, do not silently absorb friction. First "
        "manifestation: GTKB-ARTIFACT-RECORDER-CLI (work_list row 15). "
        "Extends GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / DELIB-0874 with "
        "operational-cost rationale and active-pursuit mandate; does NOT "
        "supersede GOV-ARTIFACT-APPROVAL-001."
    )

    kdb = db.KnowledgeDB()
    kdb.insert_deliberation(
        id=packet["artifact_id"],
        source_type="owner_conversation",
        title="Deterministic Services Principle (S312)",
        summary=summary,
        content=content,
        changed_by=packet["changed_by"],
        change_reason=packet["change_reason"],
        outcome="owner_decision",
        session_id="S312",
        source_ref=packet["source_ref"],
    )

    print(f"Inserted {packet['artifact_id']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
