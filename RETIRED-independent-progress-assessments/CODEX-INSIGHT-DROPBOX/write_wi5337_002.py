"""One-shot governed-writer driver for the WI-5337 NO-GO verdict (-002).

Reads the staged verdict body and publishes it via the governed
scripts.gtkb_bridge_writer.write_bridge_file path (which runs author-metadata,
compliance-audit, and WI-4520 anchor validation). Not a bridge artifact itself.
"""

import sys
import traceback
from pathlib import Path

ROOT = Path(r"E:/GT-KB")
for _p in (str(ROOT), str(ROOT / "groundtruth-kb" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

BODY = (
    ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "gtkb-wi5337-002-verdict-body.txt"
).read_text(encoding="utf-8")

SLUG = "gtkb-wi5337-latest-no-go-draft-claim-state"
VERSION = 2

try:
    target = write_bridge_file(SLUG, VERSION, BODY, ROOT)
    print("WROTE_OK:", target)
except Exception as exc:  # noqa: BLE001
    print("WRITE_ERROR:", type(exc).__name__, str(exc))
    traceback.print_exc()
    sys.exit(1)
