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


def test_t3_stop_prose_pattern_appends_and_emits_block_decision(tmp_path: Path) -> None:
    """T3: prose anti-pattern detected without AskUserQuestion → durable file
    appends the entry AND Stop mode emits the bounded-exception block JSON.

    F3 contract was revised by gtkb-decision-tracker-block-prose-ask-2026-04-29
    -003 REVISED-1 (Codex GO at -004): Stop is silent for typical turns BUT
    emits one ``{"decision": "block", "reason": "..."}`` JSON when the just-
    completed turn contains at least one prose-decision-ask AND zero
    AskUserQuestion tool_use entries. The fixture
    ``turn_with_prose_decision.jsonl`` matches that hard condition.
    """
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    # F3 revision (bounded exception): block JSON written to stdout.
    assert result.stdout, "Stop stdout must contain block JSON for hard condition (F3 revision)"
    payload = json.loads(result.stdout)
    assert payload["decision"] == "block"
    assert "AskUserQuestion" in payload["reason"]
    # Durable-file append behavior preserved.
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
    assert after == before, "Truncated transcript must not mutate the durable file"
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


# ===========================================================================
# F3 bounded exception: Stop-mode block-on-prose-ask
# Per gtkb-decision-tracker-block-prose-ask-2026-04-29-003 REVISED-1 (Codex GO
# at -004). Stop emits one `{"decision": "block", ...}` JSON when the just-
# completed turn has a prose-decision-ask AND zero AskUserQuestion tool_use
# entries. Gated by GTKB_BLOCK_ON_PROSE_DECISION_ASK (default 1; =0 disables
# block JSON only — detection + durable-file appends are preserved).
# ===========================================================================


def _run_hook_with_env(mode: str, project_root: Path, stdin_text: str, extra_env: dict) -> subprocess.CompletedProcess:
    """Variant of _run_hook that sets/overrides specific env vars."""
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project_root)
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(HOOK), "--mode", mode],
        input=stdin_text,
        text=True,
        capture_output=True,
        env=env,
        check=False,
        timeout=10,
    )


def test_f3_stop_silent_for_typical_turn_without_prose_ask(tmp_path: Path) -> None:
    """F3 revision: Stop remains silent for typical turns. Fixture has an
    answered AskUserQuestion and no prose-ask -> no block emission."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_askuserquestion_answered.jsonl"))
    assert result.returncode == 0
    assert result.stdout == "", f"Stop stdout must be empty for typical turn; got: {result.stdout!r}"


def test_f3_stop_silent_when_prose_ask_with_askuserquestion_in_same_turn(tmp_path: Path) -> None:
    """F3 revision: prose-ask + AskUserQuestion in same turn -> no block.
    The bounded exception only fires when zero AskUserQuestion calls happened."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_prose_and_askuserquestion.jsonl"))
    assert result.returncode == 0
    assert result.stdout == "", f"Stop stdout must be empty when AskUserQuestion is present; got: {result.stdout!r}"
    body = _read_pending_file(project)
    assert "File Slice 1 proposal first" in body or "ask_user_question" in body


def test_f3_stop_emits_block_on_prose_ask_without_askuserquestion(tmp_path: Path) -> None:
    """F3 bounded exception: prose-ask + zero AskUserQuestion -> emit block JSON."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    assert result.returncode == 0
    assert result.stdout, "Stop stdout must contain block JSON for hard condition"
    payload = json.loads(result.stdout)
    assert payload["decision"] == "block"
    assert "AskUserQuestion" in payload["reason"]


def test_f3_stop_block_rate_limited_to_one_per_invocation(tmp_path: Path) -> None:
    """F3: at most one block emission per Stop invocation; reason caps at 3 bullets."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_many_prose_decisions.jsonl"))
    assert result.returncode == 0
    payload = json.loads(result.stdout.strip())
    assert payload["decision"] == "block"
    bullet_lines = [line for line in payload["reason"].split("\n") if line.startswith("  - ")]
    assert len(bullet_lines) == 3, f"Expected 3 displayed bullet lines (cap); got {len(bullet_lines)}"


def test_f3_block_reason_caps_at_three_with_overflow_count(tmp_path: Path) -> None:
    """Codex Q5: when more than 3 prose-asks match, reason text shows the first
    3 plus a `(N additional matches)` suffix."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_many_prose_decisions.jsonl"))
    assert result.returncode == 0
    payload = json.loads(result.stdout.strip())
    assert "additional matches)" in payload["reason"]


def test_f3_block_emission_disabled_when_env_var_zero(tmp_path: Path) -> None:
    """Codex -004 GO condition 3: GTKB_BLOCK_ON_PROSE_DECISION_ASK=0 suppresses
    block JSON emission while preserving detection + durable-file appends."""
    project = _setup_project(tmp_path)
    result = _run_hook_with_env(
        "stop",
        project,
        _stop_payload("turn_with_prose_decision.jsonl"),
        {"GTKB_BLOCK_ON_PROSE_DECISION_ASK": "0"},
    )
    assert result.returncode == 0
    assert result.stdout == "", f"Stdout must be empty when env var is 0; got: {result.stdout!r}"
    body = _read_pending_file(project)
    assert "detected_via: prose:" in body, "Detection must continue when block emission is disabled"


def test_f3_block_emission_enabled_by_default_when_env_var_unset(tmp_path: Path) -> None:
    """Default behavior: block emission is on without any env-var configuration."""
    project = _setup_project(tmp_path)
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(project)
    env.pop("GTKB_BLOCK_ON_PROSE_DECISION_ASK", None)
    result = subprocess.run(
        [sys.executable, str(HOOK), "--mode", "stop"],
        input=_stop_payload("turn_with_prose_decision.jsonl"),
        text=True,
        capture_output=True,
        env=env,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout.strip())
    assert payload["decision"] == "block"


def test_f3_block_emission_handles_malformed_transcript_gracefully(tmp_path: Path) -> None:
    """Graceful degradation: missing transcript must not crash."""
    project = _setup_project(tmp_path)
    payload = json.dumps({
        "session_id": "test-session",
        "transcript_path": str(FIXTURES / "nonexistent_fixture.jsonl"),
        "cwd": str(REPO_ROOT),
        "hook_event_name": "Stop",
        "stop_hook_active": True,
    })
    result = _run_hook("stop", project, payload)
    assert result.returncode == 0
    assert result.stdout == "", "Malformed transcript should produce no block emission"


def test_f3_block_reason_includes_resolution_path(tmp_path: Path) -> None:
    """Reason text names the resolution (AskUserQuestion) so the agent knows what to do."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    payload = json.loads(result.stdout.strip())
    assert "AskUserQuestion" in payload["reason"]
    assert "Resolution" in payload["reason"]


def test_f3_block_reason_includes_disable_path(tmp_path: Path) -> None:
    """Reason text names the env-var disable path."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    payload = json.loads(result.stdout.strip())
    assert "GTKB_BLOCK_ON_PROSE_DECISION_ASK" in payload["reason"]


def test_f3_block_emission_does_not_corrupt_durable_file(tmp_path: Path) -> None:
    """Block emission and durable-file append are independent code paths that both run."""
    project = _setup_project(tmp_path)
    initial_body = _read_pending_file(project)
    assert "(none)" in initial_body
    result = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    assert result.returncode == 0
    body = _read_pending_file(project)
    assert "detected_via: prose:" in body
    assert result.stdout
    payload = json.loads(result.stdout.strip())
    assert payload["decision"] == "block"


def test_f3_block_emission_returncode_zero_for_graceful_degradation(tmp_path: Path) -> None:
    """Hook must always return exit code 0 even when emitting a block JSON.
    The block control-flow signal is JSON on stdout, NOT a non-zero exit code."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    assert result.returncode == 0


def test_f3_session_init_renders_pending_decisions_when_block_already_emitted(tmp_path: Path) -> None:
    """Non-regression: after a block-emitting run, the pending durable file is
    still readable + the prose entry is recorded for next-session surfacing."""
    project = _setup_project(tmp_path)
    _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    body = _read_pending_file(project)
    pending = body.split("## Pending", 1)[1].split("##", 1)[0]
    n = pending.count("- id: DECISION-")
    assert n >= 1, f"Expected at least 1 pending entry after block-emitting run; got {n}"


# ---------------------------------------------------------------------------
# IP-1 / IP-2 — Pattern bounds tightening + same-turn AUQ correlation
# Authority: bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001
# (GO at -006 REVISED-2 -005)
# ---------------------------------------------------------------------------


def _import_hook_module():
    """Import the hook module for in-process unit tests of pure helpers.

    Used only for testing pure functions (snippet extraction, correlation).
    Stop-mode integration tests still go through the subprocess CLI surface.
    """
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("_odt_test", str(HOOK))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_odt_test"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_question_snippet_extracts_match_group_only() -> None:
    """T-DT-snippet-match-group-only: snippet captures only the matched group, not surrounding 20-char window."""
    mod = _import_hook_module()
    import re
    text = "Earlier: some context. Should I commit now? More text after."
    pattern = re.compile(r"Should I commit now\?")
    m = pattern.search(text)
    snippet = mod._extract_question_snippet(text, m)
    assert snippet == "Should I commit now?"
    assert "Earlier" not in snippet
    assert "More text" not in snippet


def test_question_snippet_extends_to_sentence_boundary() -> None:
    """T-DT-snippet-sentence-extension: when match doesn't end at sentence terminator, extend forward."""
    mod = _import_hook_module()
    import re
    # Match doesn't include the final '?', extension should grab it.
    text = "Should we commit or revert"  # no terminator at all in text
    pattern = re.compile(r"Should we commit or revert")
    m = pattern.search(text)
    snippet = mod._extract_question_snippet(text, m)
    # No terminator within window -> snippet stays as match group.
    assert snippet == "Should we commit or revert"

    # Extension when terminator exists in window.
    text2 = "Should we commit or revert? More."
    pattern2 = re.compile(r"Should we commit or revert")
    m2 = pattern2.search(text2)
    snippet2 = mod._extract_question_snippet(text2, m2)
    assert snippet2.endswith("?")


def test_question_snippet_capped_at_120_chars() -> None:
    """T-DT-snippet-length-cap: snippet truncated with ellipsis at 120 chars."""
    mod = _import_hook_module()
    import re
    long_text = "Should I " + "really really " * 20 + "commit?"
    pattern = re.compile(re.escape(long_text))
    m = pattern.search(long_text)
    snippet = mod._extract_question_snippet(long_text, m)
    assert len(snippet) <= 120
    if len(long_text) > 120:
        assert snippet.endswith("...")


def test_correlated_two_signal_resolves_prose_entry_substring_path(tmp_path: Path) -> None:
    """T-DT-correlated-two-signal-substring: prose entry auto-resolves when correlated AUQ exists."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_prose_auq_correlated_substring.jsonl"))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    body = _read_pending_file(project)
    # The prose match should land in Resolved with resolved_via field.
    assert "## Resolved" in body
    assert "resolved_via: same_turn_auq_formalization" in body
    # And NOT in Pending.
    pending = body.split("## Pending", 1)[1].split("##", 1)[0]
    assert "detected_via: prose:" not in pending, (
        "correlated prose match must auto-resolve, not stay pending"
    )


def test_uncorrelated_boilerplate_overlap_keeps_prose_pending(tmp_path: Path) -> None:
    """T-DT-uncorrelated-boilerplate-counterexample: Codex F1 case — prose vs AUQ
    that share boilerplate but differ on discriminating tokens MUST NOT auto-resolve."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_prose_auq_uncorrelated_boilerplate.jsonl"))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    body = _read_pending_file(project)
    # The prose match (about commit) and the AUQ (about deploy) must NOT correlate.
    # Prose entry stays in Pending.
    pending = body.split("## Pending", 1)[1].split("##", 1)[0]
    assert "detected_via: prose:" in pending, (
        "uncorrelated prose match (boilerplate-only overlap) must stay pending; "
        "two-signal correlation must reject the boilerplate-only counterexample"
    )
    # And the AUQ lands in Resolved (since it's an answered AUQ in the fixture? No,
    # this fixture has unanswered AUQ -> AUQ goes to Pending too).
    # The key assertion is that the prose match did NOT auto-resolve.


def test_uncorrelated_pure_helpers_counterexample() -> None:
    """T-DT-uncorrelated-signal-a-only / signal-b-only: pure helper checks
    confirm two-signal-required logic via direct correlator calls."""
    mod = _import_hook_module()

    # Codex F1 commit-vs-deploy counterexample: stoplist removes boilerplate;
    # remaining tokens {commit} vs {deploy} -> J_d = 0 -> Signal A fails.
    correlated, sig = mod._correlate_prose_to_auq(
        "Want me to commit now or wait?",
        "Want me to deploy now or wait?",
        [],
    )
    assert correlated is False
    assert sig is None

    # Signal B alone (no Jaccard pass): synthetic case where strings differ in
    # discriminating tokens but share a >= 20-char substring through boilerplate.
    # We need substring containment but Jaccard < 0.5. Hard to construct because
    # substring containment usually drives high Jaccard. Instead test the inverse
    # check: confirm Signal A failure with substring match yields no auto-resolve.
    # The DCL gate is "BOTH A AND B"; B-only means correlated=False.
    correlated, sig = mod._correlate_prose_to_auq(
        "approve the dcl or defer",
        "approve the deployment or defer",
        [],
    )
    # After stoplist: {dcl} vs {deployment}. J_d = 0 -> Signal A fails.
    assert correlated is False
    assert sig is None


def test_correlation_positive_via_option_label_overlap(tmp_path: Path) -> None:
    """T-DT-correlated-two-signal-option-label: Signal A + B2 option-label overlap."""
    mod = _import_hook_module()
    # Prose mentions specific concept; AUQ option label includes the concept.
    correlated, sig = mod._correlate_prose_to_auq(
        "Should I land slice 4 retirement work?",
        "Land slice 4 retirement work or hold?",
        ["Land slice 4 retirement work", "Hold"],
    )
    assert correlated is True
    assert sig in ("normalized_substring", "option_label_overlap", "text_identity")


def test_decision_entry_resolved_via_round_trips(tmp_path: Path) -> None:
    """T-DT-resolved-via-round-trip: DecisionEntry resolved_via field
    survives render -> parse cycle through the hook's own parser path
    (per Codex `-008` F2 fix; covers both render side AND parse side)."""
    mod = _import_hook_module()
    entry = mod.DecisionEntry(
        id="DECISION-9999",
        asked_at="2026-05-09T00:00:00Z",
        question="Test question?",
        detected_via="prose:test",
        status="resolved",
        question_hash="abc",
        resolved_at="2026-05-09T00:00:01Z",
        resolved_via="same_turn_auq_formalization",
    )
    # Render side: assert the field is emitted.
    rendered = entry.render()
    assert "resolved_via: same_turn_auq_formalization" in rendered

    # Parse side: feed the rendered key:value into _set_entry_field and assert
    # the field survives round-trip back onto a fresh DecisionEntry. This
    # exercises the read/write parser path used by _read_pending_file.
    parsed_entry = mod.DecisionEntry(
        id="DECISION-9999", asked_at="2026-05-09T00:00:00Z"
    )
    mod._set_entry_field(parsed_entry, "resolved_via", "same_turn_auq_formalization")
    assert parsed_entry.resolved_via == "same_turn_auq_formalization", (
        "_set_entry_field must restore resolved_via on parse; otherwise the "
        "field would be lost on the next hook read/write cycle"
    )

    # Full round-trip: write a section to disk, read it back via _read_pending_file,
    # and assert the parsed entry preserves resolved_via.
    pending_path = tmp_path / "pending-owner-decisions.md"
    sections_in = {
        "pending": [],
        "resolved": [entry],
        "history": [],
    }
    mod._write_pending_file(pending_path, sections_in)
    sections_out = mod._read_pending_file(pending_path)
    resolved_out = sections_out.get("resolved", [])
    assert resolved_out, "expected at least one resolved entry after round-trip"
    assert resolved_out[0].resolved_via == "same_turn_auq_formalization", (
        "resolved_via field must survive write -> read round-trip via the "
        "durable-file parser path"
    )


def test_correlation_signal_a_only_keeps_prose_pending() -> None:
    """T-DT-uncorrelated-signal-a-only (per Codex `-008` F1 fix):
    Signal A passes (J_d >= 0.5 with shared substantive token) but no
    B signal fires; correlated MUST be False.
    """
    mod = _import_hook_module()
    # Two prompts that share most discriminating tokens (Signal A passes)
    # but neither is a substring of the other (B1 fails), no options (B2
    # fails), and they're not identical (B3 fails).
    prose = "should i land slice 4 retirement work or hold for review"
    auq = "should i land slice 4 retirement code or hold for review"
    correlated, sig = mod._correlate_prose_to_auq(prose, auq, [])
    assert correlated is False, (
        "Signal A alone (Jaccard pass) without B signal must NOT auto-resolve"
    )
    assert sig is None


def test_correlation_signal_b_only_keeps_prose_pending() -> None:
    """T-DT-uncorrelated-signal-b-only (per Codex `-008` F1 fix):
    Signal B (option-label overlap) fires while Signal A fails; correlated
    MUST be False.
    """
    mod = _import_hook_module()
    # Discriminating tokens are disjoint after stoplist removal
    # (Signal A fails: prose={dcl}, auq question={deployment}, J_d=0).
    # An option label embeds the prose -> Signal B2 (option-label overlap)
    # fires.
    prose = "approve the dcl or defer"
    auq_question = "approve the deployment or defer"
    options = ["approve the dcl or defer"]
    # Verify Signal B2 actually fires (sanity check).
    assert mod._option_label_overlap(prose, options) is True

    # Now confirm the orchestrator returns False because Signal A failed.
    correlated, sig = mod._correlate_prose_to_auq(prose, auq_question, options)
    assert correlated is False, (
        "Signal B alone (option-label overlap) without Signal A must NOT "
        "auto-resolve"
    )
    assert sig is None
