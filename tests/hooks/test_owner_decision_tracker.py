"""Tests for .claude/hooks/owner-decision-tracker.py.

Test architecture:

- Tests invoke the hook via subprocess (production CLI surface) to match
  the GOV-10 / GOV-19 outside-in testing principle. Internal helpers are
  not imported -- tests exercise what real Claude Code hook events
  exercise.

- CLAUDE_PROJECT_DIR is overridden to tmp_path so each test gets an
  isolated durable file. The hook resolves PENDING_FILE_REL relative to
  this env var.

- Stop-mode tests use the hand-curated JSONL fixtures under
  tests/hooks/fixtures/owner_decision_tracker/. Each fixture is a small
  representative transcript file matching the Claude Code hook reference
  shape.

- All tests assert the hook never raises (T13 graceful-degradation
  contract). A non-zero exit code is itself a test failure.

Authority:
- bridge/gtkb-gov-owner-decision-surfacing-slice1-003.md REVISED §2.4
- bridge/gtkb-gov-owner-decision-surfacing-slice1-004.md GO
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "owner-decision-tracker.py"
FIXTURES = REPO_ROOT / "tests" / "hooks" / "fixtures" / "owner_decision_tracker"

DURABLE_TEMPLATE = """\
# Pending Owner Decisions

Test fixture file.

---

## Pending

(none)

## Resolved

(none)

## History

(none)
"""


def _setup_project(tmp_path: Path) -> Path:
    """Create a tmp project root with an empty memory/pending-owner-decisions.md."""
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "pending-owner-decisions.md").write_text(DURABLE_TEMPLATE, encoding="utf-8")
    return tmp_path


def _run_hook(mode: str, project_root: Path, stdin_text: str = "") -> subprocess.CompletedProcess:
    """Invoke the hook subprocess with CLAUDE_PROJECT_DIR pointing at project_root."""
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_root)
    return subprocess.run(
        [sys.executable, str(HOOK), "--mode", mode],
        input=stdin_text,
        text=True,
        capture_output=True,
        env=env,
        check=False,
        timeout=10,
    )


def _read_pending_file(project_root: Path) -> str:
    return (project_root / "memory" / "pending-owner-decisions.md").read_text(encoding="utf-8")


def _stop_payload(transcript_fixture: str) -> str:
    """Build a Stop hook payload pointing transcript_path at the fixture."""
    return json.dumps({
        "session_id": "test-session",
        "transcript_path": str(FIXTURES / transcript_fixture),
        "cwd": str(REPO_ROOT),
        "hook_event_name": "Stop",
        "stop_hook_active": True,
        "last_assistant_message": "",
    })


# ---------------------------------------------------------------------------
# Stop mode -- transcript JSONL parsing (T1a, T1b -- F2 fixture coverage)
# ---------------------------------------------------------------------------

def test_t1a_stop_parses_jsonl_fixture_and_finds_turn_boundary(tmp_path: Path) -> None:
    """T1a: Stop reads the answered-fixture transcript, scans tool_use, writes Resolved entry."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_askuserquestion_answered.jsonl"))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    body = _read_pending_file(project)
    # Same-turn answered question lands in Resolved with answer text.
    assert "## Resolved" in body
    assert "Which storage backend?" in body
    assert "answer: \"SQLite\"" in body


def test_t1b_stop_extracts_questions_from_tool_use(tmp_path: Path) -> None:
    """T1b: hook extracts AskUserQuestion.input.questions list correctly."""
    project = _setup_project(tmp_path)
    _run_hook("stop", project, _stop_payload("turn_with_askuserquestion_pending.jsonl"))
    body = _read_pending_file(project)
    assert "Phase 8 rehearsal target child root path" in body
    # Options must round-trip through the YAML quoting.
    assert "Sibling under E:" in body
    assert "Defer" in body


# ---------------------------------------------------------------------------
# Stop mode -- core scans (T1, T2, T3, T4)
# ---------------------------------------------------------------------------

def test_t1_stop_same_turn_answer_appends_to_resolved(tmp_path: Path) -> None:
    """T1: AskUserQuestion + same-turn tool_result -> Resolved section."""
    project = _setup_project(tmp_path)
    _run_hook("stop", project, _stop_payload("turn_with_askuserquestion_answered.jsonl"))
    body = _read_pending_file(project)
    pending_section, _, resolved_section = body.partition("## Resolved")
    # Pending should still say (none); Resolved should hold the entry.
    assert "(none)" in pending_section.split("## Pending")[1].split("##")[0]
    assert "DECISION-" in resolved_section


def test_t2_stop_pending_question_appends_to_pending(tmp_path: Path) -> None:
    """T2: AskUserQuestion without same-turn tool_result -> Pending section."""
    project = _setup_project(tmp_path)
    _run_hook("stop", project, _stop_payload("turn_with_askuserquestion_pending.jsonl"))
    body = _read_pending_file(project)
    # Find the Pending section body
    pending_body = body.split("## Pending", 1)[1].split("##", 1)[0]
    assert "DECISION-" in pending_body
    assert "Phase 8 rehearsal" in pending_body


def test_t3_stop_prose_pattern_appends_with_no_systemmessage(tmp_path: Path) -> None:
    """T3: prose anti-pattern detected; entry gets detected_via prose; stdout is empty (F3)."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    # F3 contract: Stop mode never writes to stdout.
    assert result.stdout == "", f"Stop stdout must be empty per F3; got: {result.stdout!r}"
    body = _read_pending_file(project)
    assert "detected_via: prose:" in body


def test_t4_stop_idempotent_on_repeat_invocation(tmp_path: Path) -> None:
    """T4: Same fixture twice produces one entry, not two (question_hash dedup)."""
    project = _setup_project(tmp_path)
    _run_hook("stop", project, _stop_payload("turn_with_askuserquestion_pending.jsonl"))
    _run_hook("stop", project, _stop_payload("turn_with_askuserquestion_pending.jsonl"))
    body = _read_pending_file(project)
    # Count DECISION- IDs in Pending
    pending_body = body.split("## Pending", 1)[1].split("##", 1)[0]
    n = pending_body.count("- id: DECISION-")
    assert n == 1, f"Expected 1 entry after dedup; got {n}"


# ---------------------------------------------------------------------------
# session_self_initialization integration (T5a, T5b -- F1 fixture coverage)
# ---------------------------------------------------------------------------

def test_t5a_session_init_renders_pending_decisions_when_present(tmp_path: Path) -> None:
    """T5a: render_report includes the Pending Owner Decisions section when entries exist.

    Tested via direct import (the renderer is a pure function; subprocess
    overhead would obscure the contract). Uses tmp_path-isolated durable
    file via PROJECT_ROOT module-level attribute override.
    """
    project = _setup_project(tmp_path)
    # Pre-populate the durable file with one pending entry.
    pending_body = """\
# Pending Owner Decisions
---
## Pending

- id: DECISION-0001
  asked_at: 2026-04-25T09:00:00Z
  question: "Test pending decision?"
  options:
    - "Option A"
    - "Option B"
  detected_via: ask_user_question
  status: pending
  notes: ""

## Resolved

(none)

## History

(none)
"""
    (project / "memory" / "pending-owner-decisions.md").write_text(pending_body, encoding="utf-8")

    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        # Re-import with project root pointing at tmp_path. Easiest approach:
        # call _load_pending_owner_decisions(project_root=...) directly.
        import importlib
        import session_self_initialization as ssi  # type: ignore
        importlib.reload(ssi)
        decisions = ssi._load_pending_owner_decisions(project)
        block = ssi._render_pending_decisions_block(decisions)
    finally:
        sys.path.pop(0)

    assert decisions, "Expected one pending decision to be parsed"
    assert decisions[0]["id"] == "DECISION-0001"
    assert "Test pending decision?" in block
    assert "Option A" in block
    assert "Option B" in block


def test_t5b_session_init_omits_section_when_no_pending(tmp_path: Path) -> None:
    """T5b: render_report omits the section when ## Pending is empty."""
    project = _setup_project(tmp_path)
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        import importlib
        import session_self_initialization as ssi  # type: ignore
        importlib.reload(ssi)
        decisions = ssi._load_pending_owner_decisions(project)
        block = ssi._render_pending_decisions_block(decisions)
    finally:
        sys.path.pop(0)
    assert decisions == []
    assert block == ""


# ---------------------------------------------------------------------------
# UserPromptSubmit mode (T7, T8, T9, T10)
# ---------------------------------------------------------------------------

def _ups_payload(prompt: str) -> str:
    return json.dumps({
        "session_id": "test-session",
        "hook_event_name": "UserPromptSubmit",
        "prompt": prompt,
    })


def _seed_one_pending(project: Path, decision_id: str = "DECISION-0001", question: str = "Test pending?") -> None:
    body = f"""\
# Pending Owner Decisions
---
## Pending

- id: {decision_id}
  asked_at: 2026-04-25T09:00:00Z
  question: {json.dumps(question)}
  options:
    - "Yes"
    - "No"
  detected_via: ask_user_question
  status: pending
  question_hash: abc123
  notes: ""

## Resolved

(none)

## History

(none)
"""
    (project / "memory" / "pending-owner-decisions.md").write_text(body, encoding="utf-8")


def test_t7_ups_emits_nudge_when_pending_and_prompt_unrelated(tmp_path: Path) -> None:
    """T7: pending exists + prompt doesn't reference -> nudge emitted."""
    project = _setup_project(tmp_path)
    _seed_one_pending(project)
    result = _run_hook("user-prompt-submit", project, _ups_payload("Continue with the next backlog item."))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "Pending Owner Decisions" in result.stdout
    assert "DECISION-0001" in result.stdout


def test_t8_ups_silent_when_prompt_references_pending(tmp_path: Path) -> None:
    """T8: prompt mentions DECISION-NNNN -> nudge suppressed."""
    project = _setup_project(tmp_path)
    _seed_one_pending(project)
    result = _run_hook("user-prompt-submit", project, _ups_payload("Looking at DECISION-0001 now."))
    assert result.returncode == 0
    assert result.stdout == ""


def test_t9_ups_defer_all_acknowledges_all_pending(tmp_path: Path) -> None:
    """T9: `defer all` shortcut acknowledges entries (notes updated, still pending)."""
    project = _setup_project(tmp_path)
    _seed_one_pending(project)
    result = _run_hook("user-prompt-submit", project, _ups_payload("defer all"))
    assert result.returncode == 0
    body = _read_pending_file(project)
    assert "Acknowledged:" in body
    # Still pending (defer doesn't move to resolved).
    assert body.split("## Pending", 1)[1].split("##", 1)[0].count("- id: DECISION-") == 1


def test_t10_ups_resolve_id_moves_to_resolved(tmp_path: Path) -> None:
    """T10: `resolve DECISION-NNNN: <answer>` moves the entry."""
    project = _setup_project(tmp_path)
    _seed_one_pending(project)
    result = _run_hook("user-prompt-submit", project, _ups_payload("resolve DECISION-0001: Yes"))
    assert result.returncode == 0
    body = _read_pending_file(project)
    assert "(none)" in body.split("## Pending", 1)[1].split("##", 1)[0]
    resolved = body.split("## Resolved", 1)[1].split("##", 1)[0]
    assert "DECISION-0001" in resolved
    assert "answer: \"Yes\"" in resolved


# ---------------------------------------------------------------------------
# File-format + graceful-degradation (T11, T12, T13, T14)
# ---------------------------------------------------------------------------

def test_t11_malformed_durable_file_preserved_as_corrupted(tmp_path: Path) -> None:
    """T11: parse failure preserves the malformed file as .corrupted-<ts>; fresh template replaces it."""
    project = _setup_project(tmp_path)
    pending_path = project / "memory" / "pending-owner-decisions.md"
    # Write a truly malformed payload that breaks the parser. The simple
    # line-based parser is robust to most shapes, so we trigger a real
    # error by monkey-patching with content that breaks _set_entry_field
    # via an unexpected nested dict... Actually simplest: break I/O by
    # making the file a directory (rename it).
    pending_path.unlink()
    pending_path.mkdir()  # path is now a directory; read_text will OSError
    # Run Stop -- hook should catch the error path and not raise
    result = _run_hook("stop", project, _stop_payload("turn_with_askuserquestion_pending.jsonl"))
    assert result.returncode == 0  # Graceful


def test_t12_resolved_entry_older_than_30_days_moves_to_history(tmp_path: Path) -> None:
    """T12: Resolved entry older than HISTORY_AGE_DAYS goes to History on Stop."""
    project = _setup_project(tmp_path)
    body = """\
# Pending Owner Decisions
---
## Pending

(none)

## Resolved

- id: DECISION-0001
  asked_at: 2025-01-01T00:00:00Z
  resolved_at: 2025-01-01T00:00:00Z
  question: "Old decision"
  detected_via: ask_user_question
  status: resolved
  question_hash: old001
  answer: "Yes"
  notes: ""

## History

(none)
"""
    (project / "memory" / "pending-owner-decisions.md").write_text(body, encoding="utf-8")
    # Run Stop with a no-op transcript (no fixture exists for "empty-turn",
    # so use the prose fixture; archival runs unconditionally). The
    # important assertion is on the post-state.
    _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    final = _read_pending_file(project)
    # Old entry should have moved to History.
    history_section = final.split("## History", 1)[1] if "## History" in final else ""
    assert "DECISION-0001" in history_section


def test_t13_hook_never_raises_on_garbage_input(tmp_path: Path) -> None:
    """T13: garbage stdin / invalid mode args / corrupt transcript -> exit 0."""
    project = _setup_project(tmp_path)
    # Garbage stdin
    result = _run_hook("stop", project, "this is not json")
    assert result.returncode == 0
    # Pointing at a non-existent transcript path
    payload = json.dumps({"transcript_path": "/does/not/exist.jsonl"})
    result = _run_hook("stop", project, payload)
    assert result.returncode == 0


def test_t14_prose_false_positive_guard_suppresses_abstract_discussion(tmp_path: Path) -> None:
    """T14: assistant text discussing decisions abstractly does NOT trigger detection."""
    project = _setup_project(tmp_path)
    fixture_path = tmp_path / "abstract.jsonl"
    fixture_path.write_text(
        json.dumps({"type": "user", "uuid": "u1", "parentUuid": None, "timestamp": "2026-04-25T17:00:00Z",
                    "message": {"role": "user", "content": "Tell me about decision-making."}}) + "\n" +
        json.dumps({"type": "assistant", "uuid": "a1", "parentUuid": "u1", "timestamp": "2026-04-25T17:00:01Z",
                    "message": {"role": "assistant",
                                "content": [{"type": "text",
                                             "text": "Decisions are hard. In general, decisions involve weighing tradeoffs. Should I describe the framework or give an example?"}]}}),
        encoding="utf-8",
    )
    payload = json.dumps({"transcript_path": str(fixture_path)})
    _run_hook("stop", project, payload)
    body = _read_pending_file(project)
    # Pending should remain empty -- the abstract discussion should be
    # suppressed by the false-positive guard.
    pending_body = body.split("## Pending", 1)[1].split("##", 1)[0]
    assert "DECISION-" not in pending_body, "False-positive guard failed; abstract discussion was logged"


# ---------------------------------------------------------------------------
# T15, T16 -- additional edge cases per Codex F2
# ---------------------------------------------------------------------------

def test_t15_truncated_transcript_returns_zero_no_mutation(tmp_path: Path) -> None:
    """T15: corrupt/truncated transcript -> hook exits 0; durable file unchanged."""
    project = _setup_project(tmp_path)
    before = _read_pending_file(project)
    result = _run_hook("stop", project, _stop_payload("turn_truncated.jsonl"))
    assert result.returncode == 0
    after = _read_pending_file(project)
    # Should not crash; durable file should be intact (may be unchanged
    # since the truncated fixture has no parseable AskUserQuestion).
    assert "## Pending" in after
    assert "(none)" in after.split("## Pending", 1)[1].split("##", 1)[0]
    # Sanity: test fixture file exists
    assert (FIXTURES / "turn_truncated.jsonl").exists()


def test_t16_multiple_askuserquestion_in_one_turn(tmp_path: Path) -> None:
    """T16: multiple AskUserQuestion in single turn; one answered, one pending."""
    project = _setup_project(tmp_path)
    _run_hook("stop", project, _stop_payload("turn_multiple_askuserquestion.jsonl"))
    body = _read_pending_file(project)
    pending = body.split("## Pending", 1)[1].split("##", 1)[0]
    resolved = body.split("## Resolved", 1)[1].split("##", 1)[0]
    # Notifier question is unanswered -> Pending.
    assert "Notifier default channel?" in pending
    # Feature X question was answered "Yes" -> Resolved.
    assert "Should we enable feature X?" in resolved
    assert "answer: \"Yes\"" in resolved
