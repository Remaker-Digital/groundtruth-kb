"""One-shot governed-writer runner for the WI-5237 -008 NO-GO verdict.

Writes bridge/gtkb-wi5237-wi5229-pauth-configuration-coverage-008.md via the
governed writer (no finalizer contact, no commit). Race-safe: write_bridge_file
raises BridgeConflictError if a peer already wrote -008.
"""

import sys
import traceback
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

draft = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5237-008-nogo-draft.txt"
body = draft.read_text(encoding="utf-8")

try:
    path = write_bridge_file(
        "gtkb-wi5237-wi5229-pauth-configuration-coverage",
        8,
        body,
        ROOT,
    )
    print("WROTE:", path)
except Exception as exc:  # noqa: BLE001 - surface the exact guard that fired
    traceback.print_exc()
    print("WRITE_FAILED:", type(exc).__name__, exc)
    sys.exit(1)
