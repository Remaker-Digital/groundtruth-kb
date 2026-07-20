"""One-shot governed GO-verdict writer for wi5122 v006 (LO harness B)."""

import sys
from pathlib import Path

ROOT = Path("E:/GT-KB")
sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

body = (ROOT / "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/wi5122-go-body.md").read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "e673b49a-79d9-485d-8b98-943def29837f",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo",
}

path = write_bridge_file(
    "gtkb-wi5122-promote-peer-review-weighting-rule",
    6,
    body,
    ROOT,
    author_metadata=author_metadata,
)
print("WROTE", path)
