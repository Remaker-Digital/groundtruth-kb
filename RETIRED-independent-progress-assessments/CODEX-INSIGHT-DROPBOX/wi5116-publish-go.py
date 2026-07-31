"""One-shot runner: inject fresh preflight output and publish the WI-5116 GO verdict.

Dispatched Loyal Opposition (harness B) verdict publication through the governed
gtkb_bridge_writer.write_bridge_file path. Read-only preflights are re-run here so
the embedded Applicability/Clause sections are byte-faithful to live tooling.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
SRC = ROOT / "groundtruth-kb" / "src"
VENV_PY = str(ROOT / "groundtruth-kb" / ".venv" / "Scripts" / "python.exe")
SLUG = "gtkb-wi5116-per-thread-finalization-repair"
VERSION = 2
BODY = (
    ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "wi5116-per-thread-finalization-repair-go-002-body.txt"
)

for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)


def _preflight(script: str) -> str:
    proc = subprocess.run(
        [VENV_PY, script, "--bridge-id", SLUG],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if not proc.stdout.strip():
        raise SystemExit(f"{script} produced no stdout (rc={proc.returncode}): {proc.stderr}")
    print(f"[preflight] {script} rc={proc.returncode}")
    return proc.stdout.strip()


appl = _preflight("scripts/bridge_applicability_preflight.py")
clause = _preflight("scripts/adr_dcl_clause_preflight.py")

body = BODY.read_text(encoding="utf-8")
body = body.replace("@@APPLICABILITY_PREFLIGHT@@", appl).replace("@@CLAUSE_PREFLIGHT@@", clause)
if "@@" in body:
    raise SystemExit("marker substitution incomplete; refusing to publish")

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "2026-07-16T18-04-07Z-loyal-opposition-B-367974",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code dispatched Loyal Opposition (harness B); ::init gtkb lo; PowerShell/Bash; project root E:\\GT-KB",
}

from scripts.gtkb_bridge_writer import write_bridge_file

written = write_bridge_file(SLUG, VERSION, body, ROOT, author_metadata=author_metadata)
print("WROTE", written)
