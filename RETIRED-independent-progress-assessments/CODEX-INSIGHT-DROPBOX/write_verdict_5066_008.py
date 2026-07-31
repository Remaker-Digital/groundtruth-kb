import sys
from pathlib import Path

root = Path(r"E:\GT-KB")
sys.path.insert(0, str(root / "groundtruth-kb" / "src"))
sys.path.insert(0, str(root))

from scripts.gtkb_bridge_writer import write_bridge_file

body_path = root / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "verdict-body-gtkb-wi5066-008.md"
body = body_path.read_text(encoding="utf-8")

target = write_bridge_file(
    "gtkb-wi5066-dispatch-wrapper-commandline-redaction",
    8,
    body,
    root,
)
print("WROTE", target)
