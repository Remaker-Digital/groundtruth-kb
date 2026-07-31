"""One-shot driver: file the WI-5330 -006 finalization-scoped NO-GO verdict.

Headless Claude LO-B dispatch. Uses the governed low-level writer
(scripts.gtkb_bridge_writer.write_bridge_file) because write_verdict.py only
writes VERIFIED, and raw Write of bridge files is blocked. Race-safe: the writer
raises BridgeConflictError if -006 already exists (peer LO filed first).
"""

import pathlib
import sys

ROOT = pathlib.Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

BODY_PATH = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5330-006-nogo-body.txt"
body = BODY_PATH.read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude/B",
    "author_harness_id": "B",
    "author_session_context_id": "2026-07-16T18-23-54Z-loyal-opposition-B-a036ed",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition",
}

written = write_bridge_file(
    "gtkb-wi5330-spec-link-heading-hyphen-false-positive",
    6,
    body,
    ROOT,
    author_metadata=author_metadata,
)
print("WROTE_BRIDGE_FILE", written)
