"""One-shot governed GO-verdict writer for WI-5204 v002 (LO harness B, auto-dispatched)."""

import sys
from pathlib import Path

ROOT = Path("E:/GT-KB")
sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

body = (
    ROOT / "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/wi5204-go-body.txt"
).read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "94c9c26b-f0dd-43e9-aac0-87147bf1e18f",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": (
        "Claude Code auto-dispatched loyal-opposition worker (::init gtkb lo); "
        "dispatch 2026-07-12T01-37-34Z-loyal-opposition-B-1efffa"
    ),
}

path = write_bridge_file(
    "gtkb-wi5204-h-stop-hook-completion-preservation",
    2,
    body,
    ROOT,
    author_metadata=author_metadata,
)
print("WROTE", path)
