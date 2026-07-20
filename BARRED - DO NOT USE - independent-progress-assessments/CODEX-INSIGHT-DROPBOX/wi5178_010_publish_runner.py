import sys
from pathlib import Path

ROOT = Path(r"E:\GT-KB")
sys.path.insert(0, str(ROOT))  # noqa: E402
from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

DRAFT = ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "wi5178-010-verdict-body.txt"
body = DRAFT.read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "2026-07-17T13-11-01Z-loyal-opposition-B-dde84b",
    "author_model": "claude-sonnet-5",
    "author_model_version": "claude-sonnet-5",
    "author_model_configuration": "Claude Code dispatcher-spawned headless worker; resolved_role=loyal-opposition; explanatory output style",
}

written = write_bridge_file(
    "gtkb-wi5178-operation-time-authority-enforcement",
    10,
    body,
    ROOT,
    author_metadata=author_metadata,
)
print("WROTE:", written)

DRAFT.unlink()
print("CLEANED UP DRAFT")
