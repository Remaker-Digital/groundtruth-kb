"""One-shot driver: write the LO NO-GO verdict bridge file via the governed
write_bridge_file helper (write_bytes path; invisible to PreToolUse guards,
runs its own WI-4520 anchor audit + author-metadata injection).

Run: groundtruth-kb/.venv/Scripts/python.exe <this file>
"""

import sys
from pathlib import Path

ROOT = Path(".").resolve()
for candidate in (str(ROOT), str(ROOT / "groundtruth-kb" / "src")):
    if candidate not in sys.path:
        sys.path.insert(0, candidate)

from scripts.gtkb_bridge_writer import (  # noqa: E402
    BridgeConflictError,
    BridgeEvidenceAnchorError,
    BridgeTransitionError,
    write_bridge_file,
)

DRAFT = (
    ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "verdict-drafts"
    / "gtkb-sot-singleton-gov-foundation-004-draft.md"
)
SLUG = "gtkb-sot-singleton-gov-foundation"
VERSION = 4

body = DRAFT.read_text(encoding="utf-8")

try:
    target = write_bridge_file(SLUG, VERSION, body, ROOT)
    print("WROTE:", target.relative_to(ROOT).as_posix())
except BridgeConflictError as exc:
    print("CONFLICT (stand down; a peer may have filed the next version):", exc)
    raise SystemExit(2)
except BridgeEvidenceAnchorError as exc:
    print("ANCHOR-VIOLATION (fix citations in the draft):", exc)
    raise SystemExit(3)
except BridgeTransitionError as exc:
    print("TRANSITION-ERROR:", exc)
    raise SystemExit(4)
