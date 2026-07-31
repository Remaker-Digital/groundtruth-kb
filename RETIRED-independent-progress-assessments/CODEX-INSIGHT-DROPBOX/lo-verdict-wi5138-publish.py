import sys
from pathlib import Path

sys.path.insert(0, ".")
from scripts import gtkb_bridge_writer

root = Path("E:/GT-KB")
body_path = Path(
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/lo-verdict-wi5138-008-draft.md"
)
content = body_path.read_text(encoding="utf-8")

written = gtkb_bridge_writer.write_bridge_file(
    "gtkb-modernization-wi5138-pauth-activation",
    8,
    content,
    root,
)
print("WROTE:", written)
