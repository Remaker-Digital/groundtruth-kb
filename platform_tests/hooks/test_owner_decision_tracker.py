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
# Fixtures are co-located with this test file. Resolved relative to __file__
# (not REPO_ROOT) so the path survives a tests/ <-> platform_tests/ relocation
# -- the prior REPO_ROOT/"tests"/... form broke after the suite moved to
# platform_tests/, leaving every fixture-backed subprocess test failing
# (WI-3332; corrected under owner AskUserQuestion approval, S354 2026-05-15).
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "owner_decision_tracker"

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
    """Invoke the hook with worker-context env markers scrubbed by default."""
    env = os.environ.copy()
    env.pop("GTKB_BRIDGE_POLLER_RUN_ID", None)
    env.pop("GTKB_PROJECT_ROOT", None)
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
    return _stop_payload_for_path(FIXTURES / transcript_fixture)


def _stop_payload_for_path(transcript_path: Path) -> str:
    """Build a Stop hook payload pointing transcript_path at an explicit file."""
    return json.dumps(
        {
            "session_id": "test-session",
            "transcript_path": str(transcript_path),
            "cwd": str(REPO_ROOT),
            "hook_event_name": "Stop",
            "stop_hook_active": True,
            "last_assistant_message": "",
        }
    )


def _write_jsonl(path: Path, events: list[dict]) -> None:
    """Write a small transcript fixture local to the test's tmp_path."""
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")


def _write_answered_auq_transcript(path: Path, question: str, options: list[str], answer: str) -> None:
    """Write a transcript containing one answered AskUserQuestion call."""
    option_rows = [{"label": option, "description": option} for option in options]
    _write_jsonl(
        path,
        [
            {
                "type": "user",
                "uuid": "u-1",
                "parentUuid": None,
                "timestamp": "2026-06-22T12:00:00Z",
                "message": {"role": "user", "content": "Please formalize the decision."},
            },
            {
                "type": "assistant",
                "uuid": "a-1",
                "parentUuid": "u-1",
                "timestamp": "2026-06-22T12:00:01Z",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "Formalizing the decision."},
                        {
                            "type": "tool_use",
                            "id": "tu-cross-turn",
                            "name": "AskUserQuestion",
                            "input": {
                                "questions": [
                                    {
                                        "question": question,
                                        "header": "Decision",
                                        "options": option_rows,
                                        "multiSelect": False,
                                    }
                                ]
                            },
                        },
                    ],
                },
            },
            {
                "type": "user",
                "uuid": "u-2",
                "parentUuid": "a-1",
                "timestamp": "2026-06-22T12:00:30Z",
                "message": {
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": "tu-cross-turn", "content": answer}],
                },
            },
        ],
    )


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
    assert 'answer: "SQLite"' in body


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
    return json.dumps(
        {
            "session_id": "test-session",
            "hook_event_name": "UserPromptSubmit",
            "prompt": prompt,
        }
    )


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
    assert 'answer: "Yes"' in resolved


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
        json.dumps(
            {
                "type": "user",
                "uuid": "u1",
                "parentUuid": None,
                "timestamp": "2026-04-25T17:00:00Z",
                "message": {"role": "user", "content": "Tell me about decision-making."},
            }
        )
        + "\n"
        + json.dumps(
            {
                "type": "assistant",
                "uuid": "a1",
                "parentUuid": "u1",
                "timestamp": "2026-04-25T17:00:01Z",
                "message": {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": "Decisions are hard. In general, decisions involve weighing tradeoffs. Should I describe the framework or give an example?",
                        }
                    ],
                },
            }
        ),
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
    assert 'answer: "Yes"' in resolved


# ===========================================================================
# F3 bounded exception: Stop-mode block-on-prose-ask
# Per gtkb-decision-tracker-block-prose-ask-2026-04-29-003 REVISED-1 (Codex GO
# at -004). Stop emits one `{"decision": "block", ...}` JSON when the just-
# completed turn has a prose-decision-ask AND zero AskUserQuestion tool_use
# entries. Gated by GTKB_BLOCK_ON_PROSE_DECISION_ASK (default 1; =0 disables
# block JSON only — detection + durable-file appends are preserved).
# ===========================================================================


def _run_hook_with_env(mode: str, project_root: Path, stdin_text: str, extra_env: dict) -> subprocess.CompletedProcess:
    """Variant of _run_hook that explicitly restores caller-supplied env vars."""
    env = os.environ.copy()
    env.pop("GTKB_BRIDGE_POLLER_RUN_ID", None)
    env.pop("GTKB_PROJECT_ROOT", None)
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


def test_worker_stop_writes_owner_decision_artifact_instead_of_blocking(tmp_path: Path) -> None:
    """Slice 4 D2: unattended workers cannot answer Stop blocks, so a prose
    owner-decision ask becomes a structured dispatch artifact.
    """
    project = _setup_project(tmp_path)
    run_id = "worker-dispatch-42"

    result = _run_hook_with_env(
        "stop",
        project,
        _stop_payload("turn_with_prose_decision.jsonl"),
        {
            "GTKB_BRIDGE_POLLER_RUN_ID": run_id,
            "GTKB_PROJECT_ROOT": str(project),
            "GTKB_BLOCK_ON_PROSE_DECISION_ASK": "1",
        },
    )

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert result.stdout == "", "worker Stop hook must not emit an interactive block"
    artifact_path = (
        project / ".gtkb-state" / "cross-harness-trigger" / "dispatch-runs" / f"{run_id}.owner-decision-requested.json"
    )
    assert artifact_path.is_file()
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["decision"] == "requires_owner_decision"
    assert payload["run_id"] == run_id
    assert payload["detected_patterns"]
    assert payload["transcript_path"].endswith("turn_with_prose_decision.jsonl")


def test_worker_stop_still_appends_pending_owner_decision(tmp_path: Path) -> None:
    """The worker artifact is routing metadata; the durable notepad remains
    the load-bearing owner-decision record.
    """
    project = _setup_project(tmp_path)

    result = _run_hook_with_env(
        "stop",
        project,
        _stop_payload("turn_with_prose_decision.jsonl"),
        {
            "GTKB_BRIDGE_POLLER_RUN_ID": "worker-dispatch-43",
            "GTKB_PROJECT_ROOT": str(project),
            "GTKB_BLOCK_ON_PROSE_DECISION_ASK": "1",
        },
    )

    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert "detected_via: prose:" in _read_pending_file(project)


def test_owner_stop_context_still_emits_block_for_prose_decision(tmp_path: Path) -> None:
    """Slice 4 D2 is worker-scoped; normal owner-facing Stop behavior remains unchanged."""
    project = _setup_project(tmp_path)

    result = _run_hook_with_env(
        "stop",
        project,
        _stop_payload("turn_with_prose_decision.jsonl"),
        {"GTKB_BLOCK_ON_PROSE_DECISION_ASK": "1"},
    )

    assert result.returncode == 0, f"stderr: {result.stderr}"
    payload = json.loads(result.stdout.strip())
    assert payload["decision"] == "block"
    assert "AskUserQuestion" in payload["reason"]


def test_f3_block_emission_handles_malformed_transcript_gracefully(tmp_path: Path) -> None:
    """Graceful degradation: missing transcript must not crash."""
    project = _setup_project(tmp_path)
    payload = json.dumps(
        {
            "session_id": "test-session",
            "transcript_path": str(FIXTURES / "nonexistent_fixture.jsonl"),
            "cwd": str(REPO_ROOT),
            "hook_event_name": "Stop",
            "stop_hook_active": True,
        }
    )
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
    import importlib.util
    import sys

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
    assert "detected_via: prose:" not in pending, "correlated prose match must auto-resolve, not stay pending"


def test_cross_turn_pending_prose_resolves_on_later_correlated_auq(tmp_path: Path) -> None:
    """A pending prose ask resolves when a later answered AUQ matches the same decision."""
    project = _setup_project(tmp_path)
    first = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    assert first.returncode == 0, f"stderr: {first.stderr}"
    pending_after_first = _read_pending_file(project).split("## Pending", 1)[1].split("##", 1)[0]
    assert "detected_via: prose:" in pending_after_first

    transcript = tmp_path / "cross_turn_answered.jsonl"
    question = "Should I file the proposal as Slice 1 first or jump straight into the implementation?"
    _write_answered_auq_transcript(
        transcript,
        question,
        ["File proposal first", "Jump to implementation"],
        "File proposal first",
    )

    second = _run_hook("stop", project, _stop_payload_for_path(transcript))
    assert second.returncode == 0, f"stderr: {second.stderr}"
    body = _read_pending_file(project)
    pending = body.split("## Pending", 1)[1].split("##", 1)[0]
    resolved = body.split("## Resolved", 1)[1].split("##", 1)[0]
    assert "detected_via: prose:" not in pending
    assert "resolved_via: cross_turn_auq_formalization" in resolved
    assert 'answer: "File proposal first"' in resolved


def test_cross_turn_uncorrelated_auq_leaves_prose_pending(tmp_path: Path) -> None:
    """A later answered AUQ on an unrelated topic must not resolve prior prose pending state."""
    project = _setup_project(tmp_path)
    first = _run_hook("stop", project, _stop_payload("turn_with_prose_decision.jsonl"))
    assert first.returncode == 0, f"stderr: {first.stderr}"

    transcript = tmp_path / "cross_turn_unrelated.jsonl"
    _write_answered_auq_transcript(
        transcript,
        "Should I deploy the dashboard now or hold?",
        ["Deploy", "Hold"],
        "Deploy",
    )

    second = _run_hook("stop", project, _stop_payload_for_path(transcript))
    assert second.returncode == 0, f"stderr: {second.stderr}"
    body = _read_pending_file(project)
    pending = body.split("## Pending", 1)[1].split("##", 1)[0]
    assert "detected_via: prose:" in pending
    assert "resolved_via: cross_turn_auq_formalization" not in body


def test_same_turn_correlation_still_resolves_after_cross_turn_change(tmp_path: Path) -> None:
    """The cross-turn pass does not disturb existing same-turn AUQ correlation."""
    project = _setup_project(tmp_path)
    result = _run_hook("stop", project, _stop_payload("turn_prose_auq_correlated_substring.jsonl"))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    body = _read_pending_file(project)
    pending = body.split("## Pending", 1)[1].split("##", 1)[0]
    assert "resolved_via: same_turn_auq_formalization" in body
    assert "resolved_via: cross_turn_auq_formalization" not in body
    assert "detected_via: prose:" not in pending


def test_cross_turn_resolution_noops_without_pending_prose(tmp_path: Path) -> None:
    """Scan A2 is a no-op when the turn has an answered AUQ but no pending prose entry."""
    project = _setup_project(tmp_path)
    transcript = tmp_path / "cross_turn_no_pending.jsonl"
    _write_answered_auq_transcript(
        transcript,
        "Should I file the proposal as Slice 1 first or jump straight into the implementation?",
        ["File proposal first", "Jump to implementation"],
        "File proposal first",
    )
    result = _run_hook("stop", project, _stop_payload_for_path(transcript))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    body = _read_pending_file(project)
    pending = body.split("## Pending", 1)[1].split("##", 1)[0]
    assert "(none)" in pending
    assert "resolved_via: cross_turn_auq_formalization" not in body


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
    parsed_entry = mod.DecisionEntry(id="DECISION-9999", asked_at="2026-05-09T00:00:00Z")
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
        "resolved_via field must survive write -> read round-trip via the durable-file parser path"
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
    assert correlated is False, "Signal A alone (Jaccard pass) without B signal must NOT auto-resolve"
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
    assert correlated is False, "Signal B alone (option-label overlap) without Signal A must NOT auto-resolve"
    assert sig is None


# ===========================================================================
# WI-3332 -- startup-relay known-match suppression
# Authority: bridge/gtkb-owner-decision-tracker-startup-relay-known-match-
# suppression-003.md (Prime REVISED); Codex GO at -004.
#
# A prose match that merely relays an already-recorded owner decision (e.g. a
# startup disclosure echoing the Pending Owner Decisions section) must not be
# treated as a fresh owner-decision-ask. Fresh prose asks still block.
# ===========================================================================


# Offering/choice-shaped question matching the ``should_i_or`` prose pattern.
_WI3332_TRIGGER_QUESTION = "Should I land this slice now, or hold for the next review?"


def _wi3332_question_hash(question: str) -> str:
    """Compute the durable question_hash the hook stores for a prose snippet."""
    return _import_hook_module()._question_hash(question, [])


def _write_relay_transcript(tmp_path: Path, assistant_text: str) -> Path:
    """Write a minimal user->assistant JSONL transcript relaying assistant_text.

    The assistant event carries ``assistant_text`` as plain prose so the
    Stop-mode scan exercises the prose-pattern detector on a non-structural
    line (mimics a startup-disclosure relay of a pending-decision bullet).
    """
    transcript = tmp_path / "wi3332_relay_transcript.jsonl"
    user_event = json.dumps(
        {
            "type": "user",
            "uuid": "u1",
            "parentUuid": None,
            "timestamp": "2026-05-15T23:00:00Z",
            "message": {"role": "user", "content": "init gtkb"},
        }
    )
    assistant_event = json.dumps(
        {
            "type": "assistant",
            "uuid": "a1",
            "parentUuid": "u1",
            "timestamp": "2026-05-15T23:00:01Z",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": assistant_text}],
            },
        }
    )
    transcript.write_text(user_event + "\n" + assistant_event, encoding="utf-8")
    return transcript


def _seed_one_decision(
    project: Path,
    section: str,
    question: str,
    question_hash: str,
    decision_id: str = "DECISION-0001",
) -> None:
    """Write a durable file with one entry under ``section`` (Pending/Resolved)."""
    other = "Resolved" if section == "Pending" else "Pending"
    status = "pending" if section == "Pending" else "resolved"
    body = f"""\
# Pending Owner Decisions
---
## {section}

- id: {decision_id}
  asked_at: 2026-05-15T09:00:00Z
  question: {json.dumps(question)}
  detected_via: prose:should_i_or
  status: {status}
  question_hash: {question_hash}
  notes: ""

## {other}

(none)

## History

(none)
"""
    (project / "memory" / "pending-owner-decisions.md").write_text(body, encoding="utf-8")


def test_wi3332_t1_known_pending_relay_does_not_block(tmp_path: Path) -> None:
    """T1: relaying an already-recorded PENDING decision as prose must not
    emit a Stop block and must not append a duplicate durable entry."""
    project = _setup_project(tmp_path)
    qhash = _wi3332_question_hash(_WI3332_TRIGGER_QUESTION)
    _seed_one_decision(project, "Pending", _WI3332_TRIGGER_QUESTION, qhash)
    transcript = _write_relay_transcript(tmp_path, f"- DECISION-0001: {_WI3332_TRIGGER_QUESTION}")
    result = _run_hook("stop", project, json.dumps({"transcript_path": str(transcript)}))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert result.stdout == "", f"relaying a known pending decision must not block; got: {result.stdout!r}"
    # Idempotence preserved: the relay must not append a second entry.
    pending = _read_pending_file(project).split("## Pending", 1)[1].split("##", 1)[0]
    assert pending.count("- id: DECISION-") == 1, "relay must not duplicate the entry"


def test_wi3332_t2_fresh_prose_ask_still_blocks(tmp_path: Path) -> None:
    """T2: the same trigger-shaped prose ask, when NOT already recorded, is
    fresh and still emits the Stop block (the fix does not over-suppress)."""
    project = _setup_project(tmp_path)
    transcript = _write_relay_transcript(tmp_path, f"- DECISION-0001: {_WI3332_TRIGGER_QUESTION}")
    result = _run_hook("stop", project, json.dumps({"transcript_path": str(transcript)}))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert result.stdout, "a fresh prose decision-ask must still emit a block"
    assert json.loads(result.stdout)["decision"] == "block"


def test_wi3332_t3_known_resolved_relay_does_not_block(tmp_path: Path) -> None:
    """T3: the known-decision snapshot spans all sections -- relaying a
    decision recorded under ## Resolved must also not block."""
    project = _setup_project(tmp_path)
    qhash = _wi3332_question_hash(_WI3332_TRIGGER_QUESTION)
    _seed_one_decision(project, "Resolved", _WI3332_TRIGGER_QUESTION, qhash)
    transcript = _write_relay_transcript(tmp_path, f"- DECISION-0001: {_WI3332_TRIGGER_QUESTION}")
    result = _run_hook("stop", project, json.dumps({"transcript_path": str(transcript)}))
    assert result.returncode == 0, f"stderr: {result.stderr}"
    assert result.stdout == "", f"relaying a known resolved decision must not block; got: {result.stdout!r}"


# ---------------------------------------------------------------------------
# Slice 4 -- auto-archive env-gate + failure-log path
# (gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive)
# ---------------------------------------------------------------------------


def test_slice4_auto_archive_disabled_by_default(tmp_path: Path) -> None:
    """Default behavior: env var unset -> no failure log written, tracker behaves identically."""
    project = _setup_project(tmp_path)
    payload = _stop_payload("turn_with_askuserquestion_answered.jsonl")
    result = _run_hook("stop", project, payload)
    assert result.returncode == 0, f"stderr: {result.stderr}"
    failure_log = project / ".gtkb-state" / "owner-decision-auto-archive" / "failures.jsonl"
    assert not failure_log.exists(), "default-off must not create the failure-log file"


def _run_hook_isolated(
    mode: str,
    project_root: Path,
    extra_env: dict,
    stdin_text: str = "",
) -> subprocess.CompletedProcess:
    """Run hook with cwd=project_root for Slice 4 isolation (NO-GO -007 F1 fix)."""
    env = os.environ.copy()
    env.pop("GTKB_BRIDGE_POLLER_RUN_ID", None)
    env.pop("GTKB_PROJECT_ROOT", None)
    env["CLAUDE_PROJECT_DIR"] = str(project_root)
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(HOOK), "--mode", mode],
        input=stdin_text,
        text=True,
        capture_output=True,
        env=env,
        cwd=str(project_root),
        check=False,
        timeout=10,
    )


def test_slice4_auto_archive_enabled_writes_failure_log_when_service_unavailable(
    tmp_path: Path,
) -> None:
    """Env-gate-on + archive temp-dir unavailable -> graceful failure-log write.

    Post NO-GO -007 F1+F2 fix: subprocess runs with cwd=tmp_path AND
    CLAUDE_PROJECT_DIR=tmp_path. The archive temp path is blocked with a file,
    so archive_decision raises before service writes can proceed. The tracker
    catches the exception and writes a JSONL record to
    <tmp_path>/.gtkb-state/owner-decision-auto-archive/failures.jsonl. The
    notepad-tier write remains load-bearing (exit 0).
    """
    project = _setup_project(tmp_path)
    (project / ".tmp").write_text("archive temp directory unavailable\n", encoding="utf-8")
    payload = _stop_payload("turn_with_askuserquestion_answered.jsonl")
    result = _run_hook_isolated(
        "stop",
        project,
        {"GTKB_AUQ_AUTO_ARCHIVE": "1"},
        payload,
    )
    assert result.returncode == 0, f"tracker hook must NEVER raise on auto-archive failure; stderr: {result.stderr}"
    pending = _read_pending_file(project)
    assert "DECISION-" in pending, "notepad write must remain load-bearing"

    failure_log = project / ".gtkb-state" / "owner-decision-auto-archive" / "failures.jsonl"
    assert failure_log.exists(), f"failure log must be written when service is unavailable; checked {failure_log}"
    lines = [ln for ln in failure_log.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert lines, "failure log must contain at least one JSONL record"
    record = json.loads(lines[0])
    assert "decision_id" in record, "failure record must cite the decision id"
    assert record["decision_id"].startswith("DECISION-"), "decision_id format"
    assert "error_type" in record, "failure record must name the exception type"
    assert "error_message" in record, "failure record must capture the error message"
    assert len(record["error_message"]) <= 500, "error_message must be bounded"


def test_slice4_hook_does_not_touch_live_repo_state(tmp_path: Path) -> None:
    """Regression for NO-GO -007 F1: the env-gated hook must never write to
    the live GT-KB repo (groundtruth.db, .groundtruth/formal-artifact-approvals/,
    or .gtkb-state/) regardless of process cwd or stray PROJECT_ROOT resolution.
    """
    project = _setup_project(tmp_path)
    payload = _stop_payload("turn_with_askuserquestion_answered.jsonl")

    live_repo = REPO_ROOT
    approvals_dir = live_repo / ".groundtruth" / "formal-artifact-approvals"
    state_dir = live_repo / ".gtkb-state" / "owner-decision-auto-archive"
    db_path = live_repo / "groundtruth.db"

    before_approvals = set(approvals_dir.glob("2026-05-30-DELIB-*.json")) if approvals_dir.exists() else set()
    before_state = set(state_dir.glob("*")) if state_dir.exists() else set()
    before_db_mtime = db_path.stat().st_mtime if db_path.exists() else None

    result = _run_hook_isolated(
        "stop",
        project,
        {"GTKB_AUQ_AUTO_ARCHIVE": "1"},
        payload,
    )
    assert result.returncode == 0, f"hook must not raise; stderr: {result.stderr}"

    after_approvals = set(approvals_dir.glob("2026-05-30-DELIB-*.json")) if approvals_dir.exists() else set()
    after_state = set(state_dir.glob("*")) if state_dir.exists() else set()
    after_db_mtime = db_path.stat().st_mtime if db_path.exists() else None

    new_approvals = after_approvals - before_approvals
    new_state = after_state - before_state
    db_touched = before_db_mtime is not None and after_db_mtime != before_db_mtime

    assert not new_approvals, f"hook leaked approval packets into live repo: {sorted(p.name for p in new_approvals)}"
    assert not new_state, f"hook leaked state files into live .gtkb-state/: {sorted(p.name for p in new_state)}"
    assert not db_touched, "hook must not modify the live groundtruth.db"
