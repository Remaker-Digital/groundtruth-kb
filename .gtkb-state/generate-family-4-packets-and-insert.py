"""Extract Family 4 (dispatch-envelope-adr-specs) bodies, generate body files,
and emit gt spec record commands for owner-approved batch insertion.

Per AUQ DECISION (2026-06-04, S408): author + insert in this session for
the 4 dispatch-envelope ADR/DCL/SPECs that are GO-terminal but absent from
MemBase. This unblocks WI-4296 and WI-4297.

This script:
1. Extracts each "## Artifact N — <ID> (type=X)" body section from
   bridge/gtkb-dispatch-envelope-adr-specs-001.md
2. Writes the body to .gtkb-state/family-4-bodies/<ID>.md
3. Emits `gt spec record` invocation strings (to stdout) for owner-approved
   insertion.

Owner runs the resulting commands (or this script's main also runs them
when --insert is passed). Per the earlier insertion pattern, gt spec
record auto-generates its own approval packet at the canonical path; we
do NOT pre-generate.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "bridge" / "gtkb-dispatch-envelope-adr-specs-001.md"

# (artifact_id, type, title, status, change_reason_suffix)
ARTIFACTS = [
    (
        "ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001",
        "architecture_decision",
        "Dispatch Envelope Architecture",
        "specified",
        "WI-4296 dispatch-envelope architecture decision per bridge/gtkb-dispatch-envelope-adr-specs-001.md GO -002.",
    ),
    (
        "DCL-DISPATCH-ENVELOPE-SCHEMA-001",
        "design_constraint",
        "Dispatch Envelope Schema Constraints",
        "specified",
        "WI-4296 dispatch-envelope schema constraints derived from ADR-DISPATCH-ENVELOPE-ARCHITECTURE-001.",
    ),
    (
        "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
        "requirement",
        "Centralized Dispatch Service",
        "specified",
        "WI-4296 centralized dispatch service requirement: single service consuming event-driven + schedule-driven triggers.",
    ),
    (
        "SPEC-PRIME-PROJECT-COMPLETION-ENVELOPE-001",
        "requirement",
        "Prime Builder Project-Completion Envelope",
        "specified",
        "WI-4297 Prime Builder project-completion envelope: drive an authorized project to VERIFIED via claim-gated proposals + event-driven verdict re-entry.",
    ),
]


def extract_artifact_bodies(text: str) -> dict[str, str]:
    """Extract bodies between '## Artifact N — <ID>' headings."""
    lines = text.splitlines(keepends=True)
    bodies = {}
    current_id = None
    current_lines: list[str] = []

    artifact_re = re.compile(r"^## Artifact \d+ — ([A-Z][A-Z0-9-]+)\s*\(type=")

    for line in lines:
        m = artifact_re.match(line.rstrip("\r\n"))
        if m:
            if current_id is not None:
                bodies[current_id] = "".join(current_lines).rstrip() + "\n"
            current_id = m.group(1)
            current_lines = []
        elif current_id is not None:
            if (line.startswith("## ") and not line.startswith("### ")) or line.startswith("---"):
                bodies[current_id] = "".join(current_lines).rstrip() + "\n"
                current_id = None
                current_lines = []
            else:
                current_lines.append(line)

    if current_id is not None:
        bodies[current_id] = "".join(current_lines).rstrip() + "\n"

    return bodies


def main(argv: list[str]) -> int:
    insert_mode = "--insert" in argv

    text = SOURCE.read_text(encoding="utf-8")
    bodies = extract_artifact_bodies(text)

    out_bodies = REPO / ".gtkb-state" / "family-4-bodies"
    out_bodies.mkdir(parents=True, exist_ok=True)

    results = []
    for artifact_id, type_, title, status, reason_suffix in ARTIFACTS:
        if artifact_id not in bodies:
            print(f"ERROR: body not found for {artifact_id}")
            return 1
        body = bodies[artifact_id]
        body_path = out_bodies / f"{artifact_id}.md"
        body_path.write_text(body, encoding="utf-8")

        cmd = [
            str(REPO / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"),
            "-m",
            "groundtruth_kb",
            "spec",
            "record",
            "--id",
            artifact_id,
            "--title",
            title,
            "--status",
            status,
            "--content-file",
            str(body_path.relative_to(REPO)).replace("\\", "/"),
            "--change-reason",
            f"Per S408 owner AUQ batch approval (Family 4 dispatch-envelope). {reason_suffix}",
            "--auq-id",
            f"S408-FAMILY-4-{artifact_id}-INSERT",
            "--auq-answer",
            "Author + insert in this session (S408 AUQ)",
            "--owner-presented",
            "--approved-by",
            "owner",
            "--type",
            type_,
        ]

        results.append(
            {
                "artifact_id": artifact_id,
                "type": type_,
                "body_path": str(body_path.relative_to(REPO)).replace("\\", "/"),
                "body_bytes": len(body.encode("utf-8")),
                "cmd": cmd,
            }
        )

    if insert_mode:
        for r in results:
            print(f"=== Inserting {r['artifact_id']} ===")
            proc = subprocess.run(r["cmd"], cwd=str(REPO), capture_output=True, text=True)
            print(proc.stdout.strip() or proc.stderr.strip())
            r["returncode"] = proc.returncode
            if proc.returncode != 0:
                print(f"FAILED for {r['artifact_id']}")
                break

    print(json.dumps([{k: v for k, v in r.items() if k != "cmd"} for r in results], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
