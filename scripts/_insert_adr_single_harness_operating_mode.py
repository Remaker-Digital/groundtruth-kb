"""Insert ADR-SINGLE-HARNESS-OPERATING-MODE-001 into MemBase.

Reads the approval packet to source the body, changed_by, and change_reason.
Requires GTKB_FORMAL_APPROVAL_PACKET env var (or --formal-approval-packet flag)
for the formal-artifact-approval-gate hook to authorize this insert_spec call.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("groundtruth-kb/src").resolve()))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

PACKET_PATH = Path(".groundtruth/formal-artifact-approvals/2026-05-12-adr-single-harness-operating-mode-001.json")


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    db = KnowledgeDB("groundtruth.db")
    result = db.insert_spec(
        id=packet["artifact_id"],
        title="GT-KB Operating Mode Topology: Single-Harness And Multi-Harness Both First-Class",
        status="specified",
        changed_by=packet["changed_by"],
        change_reason=packet["change_reason"],
        description=packet["full_content"],
        type="architecture_decision",
        source_paths=["bridge/gtkb-single-harness-bridge-dispatcher-001-013.md"],
    )
    print(f"inserted: {result}")


if __name__ == "__main__":
    main()
