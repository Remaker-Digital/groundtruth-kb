# Transient LO publisher for the WI-5142 -004 GO verdict. Reads the staged
# body and writes it through the governed gtkb_bridge_writer.write_bridge_file.
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

body_path = PROJECT_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5142-004-verdict-body.txt"
body = body_path.read_text(encoding="utf-8")

# Normalize to LF; the writer opens with newline="" and re-reads to verify.
body = body.replace("\r\n", "\n").replace("\r", "\n")

path = write_bridge_file(
    "gtkb-wi5142-bounded-readiness-repair",
    4,
    body,
    PROJECT_ROOT,
)
print("WROTE:", path)
