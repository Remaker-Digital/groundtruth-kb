"""One-shot runner: file the WI-5171 NO-GO verdict via the governed bridge writer.

The verify helper only writes VERIFIED; a NO-GO must go through the low-level
governed writer. Claude dispatch env does not inject the three author_model_*
fields, so we pass explicit author_metadata.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402
SLUG = "gtkb-wi5171-document-authoritative-backlog-writer"
VERSION = 4
DRAFT = (
    PROJECT_ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "draft-wi5171-nogo-004.txt"
)

body = DRAFT.read_text(encoding="utf-8")

session_ctx = os.environ.get(
    "GTKB_BRIDGE_POLLER_RUN_ID", "2026-07-10T19-20-38Z-loyal-opposition-B-fd1c16"
)

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": session_ctx,
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": (
        "Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition"
    ),
}

written = write_bridge_file(
    SLUG,
    VERSION,
    body,
    PROJECT_ROOT,
    author_metadata=author_metadata,
)
print(f"WROTE: {written}")
