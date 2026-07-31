"""Publish the WI-5142 NO-GO verdict via the governed write_bridge_file path."""

from pathlib import Path

from scripts.gtkb_bridge_writer import write_bridge_file

ROOT = Path("E:/GT-KB")
DRAFT = ROOT / "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/verdict-body-gtkb-wi5142-hygiene-reclaim-cli-skill-002.md"

content = DRAFT.read_text(encoding="utf-8")

author_metadata = {
    "author_identity": "loyal-opposition/claude",
    "author_harness_id": "B",
    "author_session_context_id": "2026-07-16T03-10-57Z-loyal-opposition-B-9aa960",
    "author_model": "claude-opus-4-8",
    "author_model_version": "claude-opus-4-8",
    "author_model_configuration": "Claude Code headless bridge auto-dispatch; resolved role loyal-opposition via ::init gtkb lo",
}

path = write_bridge_file(
    "gtkb-wi5142-hygiene-reclaim-cli-skill",
    2,
    content,
    ROOT,
    author_metadata=author_metadata,
    require_author_metadata=True,
)
print(f"WROTE: {path}")
