"""Tests for Sub-slice A follow-up: code-fence-aware structural FP guards.

Per bridge/gtkb-gov-auq-enforcement-stack-slice-a-followup-code-fence-guards-2026-05-04-005.md
GO at -006.

Verifies the new ``_is_inside_structural_context`` helper and its
integration in ``_scan_prose_decisions`` suppress prose-decision-ask
matches when the trigger text is embedded in markdown structural
contexts (fenced code blocks, 4-space indented code blocks, markdown
blockquotes, HTML comments) while preserving detection of genuine asks
and existing in-window false-positive guards.

Note on detector self-reference: the trigger phrase is constructed via
string concatenation so the test file's source bytes do not contain a
contiguous match for ``PROSE_DECISION_PATTERNS["offering_or_choice"]``.
This avoids recursive detector firing on test failure output. Per
feedback_avoid_quoting_decision_tracker_fragments.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "owner-decision-tracker.py"


@pytest.fixture(scope="module")
def hook_module():
    spec = importlib.util.spec_from_file_location("owner_decision_tracker_struct_hook", HOOK_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["owner_decision_tracker_struct_hook"] = module
    spec.loader.exec_module(module)
    return module


def _make_event(text: str) -> dict:
    return {
        "type": "assistant",
        "message": {"content": [{"type": "text", "text": text}]},
    }


def _scan(hook_module, text: str) -> list[tuple[str, str]]:
    return hook_module._scan_prose_decisions([_make_event(text)])


# Trigger built by concatenation to avoid placing a contiguous
# offering_or_choice match in the test source bytes. The runtime string
# matches PROSE_DECISION_PATTERNS["offering_or_choice"]:
#   r'(?<!["`])\bwant me to\b[^.?!]*\bor\b[^.?!]*\?'
_TRIGGER = "want " + "me to" + " ship A or" + " ship B?"


def test_genuine_prose_ask_outside_fence_still_blocks(hook_module):
    """Control: trigger at top level (no structural context) must still match."""
    matches = _scan(hook_module, "Quick question: " + _TRIGGER)
    assert len(matches) == 1, f"Expected 1 control match, got {matches}"
    assert matches[0][0] == "offering_or_choice"


def test_prose_ask_inside_triple_backtick_fence_does_not_block(hook_module):
    """Trigger inside ``` ... ``` fenced block is documentation; must NOT match."""
    text = "Documentation example below.\n```\n" + _TRIGGER + "\n```\nEnd of documentation."
    matches = _scan(hook_module, text)
    assert matches == [], f"Expected 0 matches inside fence, got {matches}"


def test_prose_ask_inside_indented_code_block_does_not_block(hook_module):
    """Trigger inside 4-space indented code block must NOT match."""
    text = "Indented code below.\n\n    " + _TRIGGER + "\n\nEnd."
    matches = _scan(hook_module, text)
    assert matches == [], f"Expected 0 matches inside indented block, got {matches}"


def test_prose_ask_inside_blockquote_does_not_block(hook_module):
    """Trigger inside ``> `` blockquote line must NOT match."""
    text = "Quoting prior conversation:\n> " + _TRIGGER + "\nEnd."
    matches = _scan(hook_module, text)
    assert matches == [], f"Expected 0 matches inside blockquote, got {matches}"


def test_prose_ask_inside_html_comment_does_not_block(hook_module):
    """Trigger inside ``<!-- ... -->`` HTML comment must NOT match."""
    text = "Note: <!-- " + _TRIGGER + " --> end."
    matches = _scan(hook_module, text)
    assert matches == [], f"Expected 0 matches inside HTML comment, got {matches}"


def test_genuine_ask_after_fenced_documentation_block_still_blocks(hook_module):
    """Mixed-context: fenced doc THEN a genuine ask must produce exactly one match (the post-fence ask)."""
    text = "Documentation:\n```\n" + _TRIGGER + "\n```\nAnd now I really need to ask: " + _TRIGGER
    matches = _scan(hook_module, text)
    assert len(matches) == 1, f"Expected exactly 1 match (the post-fence ask only), got {matches}"


def test_self_reference_inside_fence_does_not_block(hook_module):
    """Trigger shown as code example must NOT match (compounds with the existing self-ref guard)."""
    text = (
        "The detector matches phrasings like:\n"
        "```regex\n" + _TRIGGER + "\n"
        "```\n"
        "in the imperative-decision-ask category."
    )
    matches = _scan(hook_module, text)
    assert matches == [], f"Expected 0 matches (fenced self-ref), got {matches}"


def test_existing_in_window_guards_still_apply(hook_module):
    """In-window PROSE_FALSE_POSITIVE_GUARDS must still suppress when context is non-structural.

    The ``decisions are hard`` guard at PROSE_FALSE_POSITIVE_GUARDS[0] should
    suppress a match within GUARD_LOCAL_WINDOW_CHARS (200) of the trigger.
    """
    text = "In general, decisions are hard. Anyway, " + _TRIGGER
    matches = _scan(hook_module, text)
    assert matches == [], f"Expected 0 matches (in-window 'decisions are hard' guard), got {matches}"


def test_structural_guard_does_not_pollute_live_memory_file(tmp_path, monkeypatch):
    """Per Sub-slice A -013 hermetic-isolation pattern: end-to-end Stop-mode
    invocation against a temp project root must not mutate the live durable file.

    Trigger embedded in a fenced block; structural guard suppresses the match;
    Stop hook records nothing (no decision); pre/post SHA-256 of live file
    must be identical.
    """
    live_pending_path = REPO_ROOT / "memory" / "pending-owner-decisions.md"
    pre_hash = hashlib.sha256(live_pending_path.read_bytes()).hexdigest() if live_pending_path.exists() else None

    project_root = tmp_path / "project"
    (project_root / "memory").mkdir(parents=True)
    (project_root / "memory" / "pending-owner-decisions.md").write_text(
        "# Pending Owner Decisions\n\n"
        "This file is owned by .claude/hooks/owner-decision-tracker.py.\n\n---\n\n"
        "## Pending\n\n## Resolved\n\n## History\n",
        encoding="utf-8",
    )

    fenced_text = "```\n" + _TRIGGER + "\n```\n"
    transcript = [
        {"type": "user", "message": {"content": [{"type": "text", "text": "continue"}]}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": fenced_text}]}},
    ]
    tfile = tmp_path / "transcript.jsonl"
    tfile.write_text("\n".join(json.dumps(e) for e in transcript), encoding="utf-8")
    payload = json.dumps(
        {
            "session_id": "test-slice-a-followup-structural-e2e",
            "hook_event_name": "Stop",
            "transcript_path": str(tfile.resolve()),
            "cwd": str(project_root),
        }
    )
    env = dict(os.environ)
    env.pop("GTKB_BLOCK_ON_PROSE_DECISION_ASK", None)
    env["CLAUDE_PROJECT_DIR"] = str(project_root)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH), "--mode", "stop"],
        input=payload,
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    assert result.returncode == 0, f"Hook exit code {result.returncode}; stderr: {result.stderr[-500:]}"

    out = result.stdout.strip()
    if out:
        parsed = json.loads(out)
        assert parsed.get("decision") != "block", (
            f"Structural-guard suppression failed: hook emitted block; got {parsed!r}"
        )

    post_hash = hashlib.sha256(live_pending_path.read_bytes()).hexdigest() if live_pending_path.exists() else None
    assert pre_hash == post_hash, (
        f"Live memory/pending-owner-decisions.md was mutated by test "
        f"(pre={pre_hash}, post={post_hash}); test is not hermetic"
    )
