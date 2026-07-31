#!/usr/bin/env python3
"""One-shot capture of preflight stdout/stderr for parent agent."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
OUT = ROOT / "bridge" / "_preflight_capture_wi4943_wi4944.txt"

COMMANDS = [
    [
        str(PY),
        str(ROOT / "scripts" / "bridge_applicability_preflight.py"),
        "--bridge-id",
        "gtkb-wi4944-release-dispatcher-lo-dispatch-unblock",
    ],
    [
        str(PY),
        str(ROOT / "scripts" / "adr_dcl_clause_preflight.py"),
        "--bridge-id",
        "gtkb-wi4944-release-dispatcher-lo-dispatch-unblock",
    ],
    [
        str(PY),
        str(ROOT / "scripts" / "bridge_applicability_preflight.py"),
        "--bridge-id",
        "gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation",
    ],
    [
        str(PY),
        str(ROOT / "scripts" / "adr_dcl_clause_preflight.py"),
        "--bridge-id",
        "gtkb-wi4943-release-branch-dispatcher-substrate-reconciliation",
    ],
]


def main() -> int:
    chunks: list[str] = []
    for idx, cmd in enumerate(COMMANDS, start=1):
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        chunks.append(f"=== COMMAND {idx} ===")
        chunks.append(f"command: {' '.join(cmd[2:]) if len(cmd) > 2 else ' '.join(cmd)}")
        chunks.append(f"exit_code: {proc.returncode}")
        chunks.append("--- stdout ---")
        chunks.append(proc.stdout if proc.stdout else "")
        chunks.append("--- stderr ---")
        chunks.append(proc.stderr if proc.stderr else "")
        chunks.append("")
    OUT.write_text("\n".join(chunks), encoding="utf-8", newline="\n")
    sys.stdout.write(OUT.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
