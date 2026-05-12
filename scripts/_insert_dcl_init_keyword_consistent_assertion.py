"""Insert DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001 into MemBase.

Reads the approval packet. Requires GTKB_FORMAL_APPROVAL_PACKET env var for the
formal-artifact-approval-gate hook.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("groundtruth-kb/src").resolve()))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

PACKET_PATH = Path(".groundtruth/formal-artifact-approvals/2026-05-12-dcl-init-keyword-consistent-assertion-001.json")


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    db = KnowledgeDB("groundtruth.db")
    result = db.insert_spec(
        id=packet["artifact_id"],
        title=(
            "Init-Keyword Emitter Must Derive From Durable Records; "
            "Receiver Must Check Set-Membership Against Durable Role"
        ),
        status="specified",
        changed_by=packet["changed_by"],
        change_reason=packet["change_reason"],
        description=packet["full_content"],
        source_paths=["bridge/gtkb-canonical-init-keyword-syntax-001-007.md"],
    )
    print(f"inserted: id={result['id']} version={result['version']} type={result['type']}")


if __name__ == "__main__":
    main()
