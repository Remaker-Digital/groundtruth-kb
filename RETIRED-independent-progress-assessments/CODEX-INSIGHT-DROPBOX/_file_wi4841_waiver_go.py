# Transient LO verdict-writer driver (WI-4841 hunk-scoped finalization waiver GO v002).
import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "groundtruth-kb" / "src"))

from scripts.gtkb_bridge_writer import write_bridge_file

draft = (
    ROOT
    / "independent-progress-assessments"
    / "CODEX-INSIGHT-DROPBOX"
    / "wi4841-waiver-go-002-draft.txt"
)
content = draft.read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "7ebdb34c-d12d-4830-b37b-b783ff37fb78",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": (
        "Claude Code interactive session; resolved role loyal-opposition via ::init gtkb lo"
    ),
}

target = write_bridge_file(
    "gtkb-wi4841-hunk-scoped-finalization-waiver",
    2,
    content,
    ROOT,
    author_metadata=author_metadata,
)
print("WROTE", target)
