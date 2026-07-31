"""One-shot driver: publish the WI-5298 finalization-scoped NO-GO (-004)."""

import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

draft = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5298-nogo-draft-004.txt"
body = draft.read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "2026-07-16T00-17-30Z-loyal-opposition-B-a3e6dd",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code dispatcher-spawned headless; resolved_role=loyal-opposition",
}

path = write_bridge_file(
    "gtkb-wi5298-codex-snapshot-git-window-containment",
    4,
    body,
    ROOT,
    author_metadata=author_metadata,
)
print("WROTE:", path)
