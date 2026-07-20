"""One-shot governed writer for the WI-5166 proposal-review NO-GO verdict.

Loyal Opposition (harness B) authoring aid: reads the reviewed verdict body from
the LO dropbox and publishes bridge/gtkb-wi5166-modernization-nonimpairment-enforcement-002.md
through the governed no-index writer (scripts.gtkb_bridge_writer.write_bridge_file),
which runs the bridge-compliance audit and the WI-4520 evidence-anchor preflight
in-process. This is an ephemeral helper, not a canonical artifact.
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
SRC = ROOT / "groundtruth-kb" / "src"
for entry in (str(ROOT), str(SRC)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

BODY_PATH = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5166-nogo-verdict-body.txt"
SLUG = "gtkb-wi5166-modernization-nonimpairment-enforcement"
VERSION = 2

body = BODY_PATH.read_text(encoding="utf-8")

try:
    written = write_bridge_file(SLUG, VERSION, body, ROOT)
    print("WROTE:", written)
except Exception:
    traceback.print_exc()
    raise SystemExit(1)
