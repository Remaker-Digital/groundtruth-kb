"""One-off governed-writer wrapper: file the WI-5555/WI-5556 NO-GO verdict (version 002)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

DOCUMENT_NAME = "gtkb-wi5555-wi5556-codex-no-window-evidence-strictness"
VERSION = 2
BODY_PATH = ROOT / ".claude" / "skills" / "verify" / "helpers" / "draft-gtkb-wi5555-wi5556-002-body.md"


def main() -> int:
    content = BODY_PATH.read_text(encoding="utf-8")
    target = write_bridge_file(
        DOCUMENT_NAME,
        VERSION,
        content,
        ROOT,
        require_author_metadata=False,
    )
    print(f"WROTE: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
