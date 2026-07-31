"""One-shot runner: publish the WI-5112 NO-GO verdict via the governed bridge writer.

Reads the reviewed draft body from the dropbox and writes bridge version 002
through scripts.gtkb_bridge_writer.write_bridge_file (write_bytes path), which
auto-injects author metadata and enforces the WI-4520 evidence-anchor guard.
"""

import sys
from pathlib import Path

ROOT = Path("E:/GT-KB")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

DRAFT = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5112-nogo-verdict-002-draft.md"
SLUG = "gtkb-wi5112-hunk-scoped-verified-finalization"

body = DRAFT.read_text(encoding="utf-8")
written = write_bridge_file(SLUG, 2, body, ROOT)
print("WROTE_BRIDGE:", written)
