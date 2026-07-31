"""One-shot governed GO-verdict writer for gtkb-wi5114-scratch-ignore-hygiene v004 (LO harness B)."""

import sys
from pathlib import Path

ROOT = Path("E:/GT-KB")
sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

body = (
    ROOT / "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/wi5114-go-body.md"
).read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "2026-07-10T08-27-30Z-loyal-opposition-B-25a84c",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code headless bridge auto-dispatch; resolved role loyal-opposition via ::init gtkb lo",
}

path = write_bridge_file(
    "gtkb-wi5114-scratch-ignore-hygiene",
    4,
    body,
    ROOT,
    author_metadata=author_metadata,
)
print("WROTE", path)
