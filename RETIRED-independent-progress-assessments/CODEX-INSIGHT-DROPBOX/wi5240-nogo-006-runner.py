"""One-shot governed bridge writer for the WI-5240 -006 NO-GO verdict.

Reads the staged NO-GO body, normalizes to LF, and writes
bridge/gtkb-wi5240-wi5236-pauth-registered-vocabulary-006.md through the
governed no-index writer (anchor + compliance gates enforced inside).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

SLUG = "gtkb-wi5240-wi5236-pauth-registered-vocabulary"
VERSION = 6
BODY_PATH = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5240-nogo-006-draft.txt"

body = BODY_PATH.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")

path = write_bridge_file(SLUG, VERSION, body, ROOT)
print("WROTE:", path)
