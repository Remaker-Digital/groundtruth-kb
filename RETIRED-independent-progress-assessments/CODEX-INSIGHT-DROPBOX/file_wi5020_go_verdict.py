"""One-shot driver: file the WI-5020 GO verdict (-004) through the governed
bridge helper (propose_bridge_codex_non_bypass). LO cannot raw-Write bridge
files post-WI-4967; this driver runs the sanctioned write_bytes path with an
in-process bridge-compliance audit. Staged in the LO-allow-listed dropbox."""

import sys
import traceback
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "bridge-propose" / "helpers"))

import write_bridge as wb  # noqa: E402

SLUG = "gtkb-wi5020-retire-event-source-config"
BODY_FILE = (
    ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "VERDICT-BODY-gtkb-wi5020-retire-event-source-config-004.md"
)

body = BODY_FILE.read_text(encoding="utf-8")

try:
    written = wb.propose_bridge_codex_non_bypass(
        SLUG,
        body,
        version=4,
        status="GO",
        bridge_dir=ROOT / "bridge",
        pre_populate_prior_deliberations=False,
        mode="abort",
    )
    print("WROTE:", written)
except Exception as exc:  # noqa: BLE001 - surface full error for the operator
    print("FAILED:", type(exc).__name__, str(exc))
    traceback.print_exc()
    sys.exit(1)
