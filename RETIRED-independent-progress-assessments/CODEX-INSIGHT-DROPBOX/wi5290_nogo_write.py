"""One-shot governed writer for the WI-5290 -004 NO-GO verdict (headless LO-B).

Reads the reviewed NO-GO body from the dropbox .txt draft and publishes it as
bridge/gtkb-wi5290-isolation-backstop-deploy-disposition-004.md through the
governed low-level writer (no work-intent claim required; race-safe via
BridgeConflictError). The body already carries a complete 6-field author block,
so ensure_author_metadata returns it unchanged.
"""

from __future__ import annotations

import traceback
from pathlib import Path

from scripts.gtkb_bridge_writer import write_bridge_file

SLUG = "gtkb-wi5290-isolation-backstop-deploy-disposition"
VERSION = 4
BODY = Path(
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/wi5290-nogo-004-body.txt"
).read_text(encoding="utf-8")

AUTHOR_METADATA = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "2026-07-16T07-41-33Z-loyal-opposition-B-681989",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code headless bridge auto-dispatch; explanatory output style; resolved role loyal-opposition",
}


def main() -> int:
    try:
        target = write_bridge_file(
            SLUG,
            VERSION,
            BODY,
            Path("."),
            author_metadata=AUTHOR_METADATA,
        )
    except Exception as exc:  # noqa: BLE001 - surface the exact gate error headlessly
        print("WRITE_FAILED", type(exc).__name__, str(exc))
        traceback.print_exc()
        return 1
    print("WROTE", target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
