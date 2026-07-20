"""One-shot runner: write the WI-5144 HP08 NO-GO verdict via the governed writer."""

import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))
sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

DRAFT = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5144-hp08-nogo-006-draft.txt"
body = DRAFT.read_text(encoding="utf-8")

target = write_bridge_file(
    "gtkb-wi5144-hp08-semantic-adapter-drift",
    6,
    body,
    ROOT,
)
print("WROTE:", target)
