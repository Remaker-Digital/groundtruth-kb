"""Read-only probe: does a narrative_artifact approval packet match the
current post-edit content of .claude/rules/loyal-opposition.md?

Replicates check_narrative_artifact_evidence.py matching logic against the
WORKING-TREE file (not the staged blob) so LO can test finalization
feasibility without mutating the git index.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = "/".join([".claude", "rules", "loyal-opposition.md"])
PACKETS = ROOT / ".groundtruth" / "formal-artifact-approvals"


def lf_sha256(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def main() -> None:
    target_path = ROOT / TARGET
    current = lf_sha256(target_path.read_text(encoding="utf-8"))
    print("current_file_lf_sha256:", current)

    matches = []
    narrative_for_target = []
    for pf in sorted(PACKETS.glob("*.json")):
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if data.get("artifact_type") != "narrative_artifact":
            continue
        tp = str(data.get("target_path", "")).replace("\\", "/")
        if tp != TARGET:
            continue
        narrative_for_target.append((pf.name, data.get("full_content_sha256")))
        if data.get("full_content_sha256") == current:
            matches.append(pf.name)

    print("narrative_artifact_packets_for_target:", len(narrative_for_target))
    for name, h in narrative_for_target:
        print("  -", name, h)
    print("MATCHING_PACKET_COUNT:", len(matches))
    for m in matches:
        print("  MATCH:", m)


if __name__ == "__main__":
    main()
