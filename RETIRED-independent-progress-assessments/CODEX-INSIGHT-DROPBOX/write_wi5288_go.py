"""One-shot governed-writer runner for the WI-5288 proposal-review GO verdict.

Reads the reviewed GO body from the sibling .txt and writes bridge version 002
through the governed write_bridge_file path (author-metadata + compliance audit;
GO is non-gated so the WI-4520 anchor guard is a no-op). Read-only evidence
artifact staged in the LO dropbox.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
for _p in (str(ROOT), str(ROOT / "groundtruth-kb" / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

body_path = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5288-go-body.txt"
body = body_path.read_text(encoding="utf-8")
target = write_bridge_file("gtkb-wi5288-session-startup-isolation-contracts", 2, body, ROOT)
print(f"WROTE {target}")
