# Headless LO governed verdict writer for gtkb-modernization-gate-1-25-execution-design-002.
# Runs write_bridge_file (governed no-index writer) which executes the bridge-compliance
# audit in-process. Not a canonical artifact; scratch runner in the LO dropbox.
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DRAFT = PROJECT_ROOT / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX" / "draft-gate-1-25-execution-design-verdict-002.txt"

for p in (str(PROJECT_ROOT), str(PROJECT_ROOT / "groundtruth-kb" / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.gtkb_bridge_writer import write_bridge_file

body = DRAFT.read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude/B",
    "author_harness_id": "B",
    "author_session_context_id": "118141b5-25ff-4aa3-b6d3-7691f64b4f8c",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code headless bridge auto-dispatch worker; resolved role loyal-opposition",
}

target = write_bridge_file(
    "gtkb-modernization-gate-1-25-execution-design",
    2,
    body,
    PROJECT_ROOT,
    author_metadata=author_metadata,
)
print("WROTE:", target)
