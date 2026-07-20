#!/usr/bin/env python3
"""Run WI-5172 -008 LO review preflights, seed deliberations, and file GO verdict."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYTHON = PROJECT_ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe"
SLUG = "gtkb-wi5172-canonical-carrier-nonauthority-evaluator"
VERSION = 8
DRAFT = PROJECT_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "verdict-body-wi5172-008-draft.md"
PREFLIGHT_OUT = PROJECT_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5172-008-preflight.txt"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run(cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, check=False)


def main() -> int:
    app = run([
        str(PYTHON),
        str(PROJECT_ROOT / "scripts" / "bridge_applicability_preflight.py"),
        "--bridge-id",
        SLUG,
    ])
    clause = run([
        str(PYTHON),
        str(PROJECT_ROOT / "scripts" / "adr_dcl_clause_preflight.py"),
        "--bridge-id",
        SLUG,
    ])
    PREFLIGHT_OUT.write_text(
        f"=== applicability exit {app.returncode} ===\n{app.stdout}\n{app.stderr}\n"
        f"=== clause exit {clause.returncode} ===\n{clause.stdout}\n{clause.stderr}\n",
        encoding="utf-8",
    )
    print(PREFLIGHT_OUT.read_text(encoding="utf-8"))
    if app.returncode != 0 or clause.returncode != 0:
        print("PREFLIGHT_FAILED", file=sys.stderr)
        return 1

    body = DRAFT.read_text(encoding="utf-8")
    seeded = run([
        str(PYTHON),
        str(PROJECT_ROOT / ".cursor" / "skills" / "verify" / "helpers" / "write_verdict.py"),
        "--slug",
        SLUG,
        "--body-file",
        str(DRAFT),
    ])
    if seeded.returncode != 0:
        print(seeded.stdout)
        print(seeded.stderr, file=sys.stderr)
        return seeded.returncode
    if seeded.stdout.strip():
        body_path = Path(seeded.stdout.strip().splitlines()[-1])
        if body_path.is_file():
            body = body_path.read_text(encoding="utf-8")

    sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.gtkb_bridge_writer import write_bridge_file

    target = write_bridge_file(
        SLUG,
        VERSION,
        body,
        PROJECT_ROOT,
        author_metadata={
            "author_identity": "loyal-opposition/cursor",
            "author_harness_id": "E",
            "author_session_context_id": "2026-07-16T09-10-29Z-loyal-opposition-E-8f5b70",
            "author_model": "composer",
            "author_model_version": "composer-2.5-fast",
            "author_model_configuration": "Cursor dispatcher-spawned Loyal Opposition (harness E); resolved role loyal-opposition via bridge auto-dispatch",
        },
    )
    print(f"FILED:{target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
