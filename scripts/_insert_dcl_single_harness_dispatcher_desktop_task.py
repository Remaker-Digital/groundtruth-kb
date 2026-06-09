"""Insert DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 into MemBase."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("groundtruth-kb/src").resolve()))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

PACKET_PATH = Path(
    ".groundtruth/formal-artifact-approvals/2026-05-12-dcl-single-harness-dispatcher-desktop-task-001.json"
)


def main() -> None:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))
    db = KnowledgeDB("groundtruth.db")
    result = db.insert_spec(
        id=packet["artifact_id"],
        title="Single-Harness Dispatcher Wake Substrate Constraint",
        status="specified",
        changed_by=packet["changed_by"],
        change_reason=packet["change_reason"],
        description=packet["full_content"],
        type="design_constraint",
        source_paths=["bridge/gtkb-single-harness-bridge-dispatcher-001-013.md"],
        affected_by=[
            "ADR-SINGLE-HARNESS-OPERATING-MODE-001",
            "SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001",
        ],
    )
    print(f"inserted: {result['id']} v{result['version']} rowid={result['rowid']}")


if __name__ == "__main__":
    main()
