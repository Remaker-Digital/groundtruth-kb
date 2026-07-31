# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""One-shot governed writer for the WI-4978 NO-GO verdict (-004).

Reads the reviewed body from the dropbox and files it through the governed
``write_bridge_file`` chokepoint. Fails closed on version conflict (peer race).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
for p in (ROOT / "groundtruth-kb" / "src", ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

SLUG = "gtkb-wi4978-helper-compliance-audit-chokepoint"
VERSION = 4
BODY = (
    ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "wi4978-verify-nogo-004-body.txt"
).read_text(encoding="utf-8")

target = write_bridge_file(SLUG, VERSION, BODY, ROOT)
print(f"WROTE {target}")
