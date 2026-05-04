"""Tests for Sub-slice A regex tightening of owner-decision-tracker.

Verifies the changes specified in
bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-007.md
(Codex GO at -008):

1. Tightened PROSE_DECISION_PATTERNS (negative lookbehind + split _q/_first_person variants)
2. Per-match local-window guard scope in _scan_prose_decisions()
3. Extended PROSE_FALSE_POSITIVE_GUARDS (self-reference + bridge-metadata)
4. GTKB_BLOCK_ON_PROSE_DECISION_ASK env override removed
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "owner-decision-tracker.py"
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "owner_decision_tracker"
SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.local.json"


@pytest.fixture(scope="module")
def hook_module():
    spec = importlib.util.spec_from_file_location("owner_decision_tracker_hook", HOOK_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # Required so @dataclass inside the hook can resolve cls.__module__.
    sys.modules["owner_decision_tracker_hook"] = module
    spec.loader.exec_module(module)
    return module


def _make_event(text: str) -> dict:
    return {
        "type": "assistant",
        "message": {"content": [{"type": "text", "text": text}]},
    }


def _scan(hook_module, text: str) -> list[tuple[str, str]]:
    return hook_module._scan_prose_decisions([_make_event(text)])


def _read_fixture(name: str) -> list[str]:
    path = FIXTURE_DIR / name
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        lines.append(stripped)
    return lines


def test_negative_fixtures_no_match(hook_module):
    """Each negative fixture line returns empty match list."""
    for line in _read_fixture("regex_negative_fixtures.txt"):
        matches = _scan(hook_module, line)
        assert matches == [], f"Expected NO match for negative fixture: {line!r}; got {matches!r}"


def test_positive_fixtures_match(hook_module):
    """Each positive fixture line returns at least one match.

    Also asserts that every one of the 7 prose patterns has at least one
    positive-fixture line that matches it.
    """
    pattern_names_seen: set[str] = set()
    for line in _read_fixture("regex_positive_fixtures.txt"):
        matches = _scan(hook_module, line)
        assert len(matches) >= 1, f"Expected ≥1 match for positive fixture: {line!r}"
        for name, _snippet in matches:
            pattern_names_seen.add(name)
    expected_patterns = {
        "offering_or_choice",
        "should_i_or",
        "awaiting_input_q",
        "awaiting_input_first_person",
        "standing_by_for_q",
        "standing_by_for_first_person",
        "your_decision_q",
    }
    missing = expected_patterns - pattern_names_seen
    assert not missing, f"Positive fixtures missing coverage for patterns: {missing}"


def test_self_reference_guard_suppresses(hook_module):
    """Self-reference guard suppresses a match when local window mentions detector internals."""
    text = "I am awaiting your direction on the regex tightening for PROSE_DECISION_PATTERNS."
    matches = _scan(hook_module, text)
    assert matches == [], f"Self-reference guard should suppress; got {matches!r}"


def test_bridge_metadata_guard_suppresses(hook_module):
    """Bridge-metadata guard suppresses when local window mentions Codex GO/NO-GO/etc."""
    text = "Codex GO at -004 confirms we are awaiting your direction on next steps."
    matches = _scan(hook_module, text)
    assert matches == [], f"Bridge-metadata guard should suppress; got {matches!r}"


def test_mixed_event_genuine_ask_still_matches(hook_module):
    """Per Codex -002 F1: guards apply per-match; a genuine ask far from a guard region still matches."""
    # Two paragraphs separated by 600+ chars of neutral text. Paragraph 1 contains
    # bridge-metadata guard region; paragraph 2 contains a genuine ask far away.
    para1 = "The umbrella -004 Codex GO confirmed scope. The PROSE_DECISION_PATTERNS regex tightening was approved."
    neutral = " filler. " * 100  # ~900 chars
    para2 = "I am awaiting your direction on Sub-slice B priority."
    text = para1 + "\n\n" + neutral + "\n\n" + para2
    matches = _scan(hook_module, text)
    pattern_names = {name for name, _ in matches}
    assert "awaiting_input_first_person" in pattern_names, (
        f"Genuine ask far from guard region should still match; got {matches!r}"
    )


def test_mixed_event_two_genuine_asks_both_match(hook_module):
    """Per Codex -002 F1: pattern.finditer() switch detects multiple matches per event."""
    text = (
        "I am awaiting your direction on the next priority.\n\n"
        + ("filler. " * 50)
        + "\n\nWe are awaiting owner approval on the deferred items."
    )
    matches = _scan(hook_module, text)
    # Both should match awaiting_input_first_person
    awaiting_matches = [m for m in matches if m[0] == "awaiting_input_first_person"]
    assert len(awaiting_matches) >= 2, (
        f"Expected ≥2 awaiting_input_first_person matches via finditer; got {matches!r}"
    )


def test_quoted_fp_1_decision0001(hook_module):
    """DECISION-0001 doc-paragraph FP suppression via negative lookbehind."""
    text = 'ose anti-patterns ("want me to X or Y?") and logs them.'
    matches = _scan(hook_module, text)
    assert matches == [], f"DECISION-0001 quoted FP should be suppressed; got {matches!r}"


def test_quoted_fp_2_decision0002(hook_module):
    """DECISION-0002 backtick-literal FP suppression via negative lookbehind."""
    text = 'The detector saw `"want me to X or Y?"` as a literal string.'
    matches = _scan(hook_module, text)
    assert matches == [], f"DECISION-0002 backtick-literal FP should be suppressed; got {matches!r}"


def test_quoted_fp_other_patterns(hook_module):
    """Lookbehind suppresses quoted instances of other patterns; positive control matches sentence-start forms."""
    quoted_should_i = 'The detector saw "should I X or Y?" as a literal example.'
    quoted_awaiting_q = 'The hook flagged "awaiting your direction?" as a match.'
    sentence_start_should_i = "Should I file -005 or wait for the umbrella?"
    sentence_start_awaiting = "Awaiting your direction?"

    assert _scan(hook_module, quoted_should_i) == [], "Quoted should_i_or should suppress"
    assert _scan(hook_module, quoted_awaiting_q) == [], "Quoted awaiting_input_q should suppress"
    # Positive controls
    assert any(name == "should_i_or" for name, _ in _scan(hook_module, sentence_start_should_i)), (
        "Sentence-start should_i_or should still match"
    )
    assert any(name == "awaiting_input_q" for name, _ in _scan(hook_module, sentence_start_awaiting)), (
        "Sentence-start awaiting_input_q should still match"
    )


def test_block_emission_enabled_when_env_unset(hook_module, monkeypatch):
    """_block_emission_enabled() returns True when env var is absent."""
    monkeypatch.delenv("GTKB_BLOCK_ON_PROSE_DECISION_ASK", raising=False)
    assert hook_module._block_emission_enabled() is True


def test_offering_or_choice_negative(hook_module):
    """offering_or_choice does not match factual statements without binary-question form."""
    text = "Want me to start the implementation."  # no "or", no "?"
    assert _scan(hook_module, text) == []


def test_offering_or_choice_positive(hook_module):
    """offering_or_choice matches genuine binary-choice asks."""
    text = "Want me to file -005 or wait for review?"
    matches = _scan(hook_module, text)
    assert any(name == "offering_or_choice" for name, _ in matches)


def test_should_i_or_negative(hook_module):
    """should_i_or does not match factual statements without binary-question form."""
    text = "Should I implement the change."  # no "or", no "?"
    assert _scan(hook_module, text) == []


def test_should_i_or_positive(hook_module):
    """should_i_or matches genuine binary-choice asks."""
    text = "Should I commit and push now or wait for review?"
    matches = _scan(hook_module, text)
    assert any(name == "should_i_or" for name, _ in matches)


def test_your_decision_q_negative(hook_module):
    """your_decision_q does not match statements without ?."""
    text = "Your decision was recorded in the deliberation archive."
    assert _scan(hook_module, text) == []


def test_your_decision_q_positive(hook_module):
    """your_decision_q matches genuine asks."""
    text = "Your decision on the next sub-slice priority?"
    matches = _scan(hook_module, text)
    assert any(name == "your_decision_q" for name, _ in matches)


def test_env_override_absent_in_settings():
    """GTKB_BLOCK_ON_PROSE_DECISION_ASK no longer present in .claude/settings.local.json env."""
    config = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    assert "GTKB_BLOCK_ON_PROSE_DECISION_ASK" not in config.get("env", {})


def test_block_emission_end_to_end_stop_mode(tmp_path, monkeypatch):
    """T-block-emission-end-to-end: Stop-mode invocation with valid transcript emits block JSON.

    Per Codex -010 F1: this proves the actual re-enabled blocking behavior end-to-end.
    Per Codex -010 hint: transcript needs at least one real user event (type=user with
    non-tool_result content) followed by the assistant text event, because
    _find_just_completed_turn() looks backward for a real user boundary.
    """
    import subprocess
    monkeypatch.delenv("GTKB_BLOCK_ON_PROSE_DECISION_ASK", raising=False)
    transcript = [
        {"type": "user", "message": {"content": [{"type": "text", "text": "continue"}]}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "Should I commit the changes or wait for review?"}]}},
    ]
    tfile = tmp_path / "transcript.jsonl"
    tfile.write_text("\n".join(json.dumps(e) for e in transcript), encoding="utf-8")
    payload = json.dumps({
        "session_id": "test-slice-a-e2e",
        "hook_event_name": "Stop",
        "transcript_path": str(tfile.resolve()),
        "cwd": str(REPO_ROOT),
    })
    env = dict(os.environ)
    env.pop("GTKB_BLOCK_ON_PROSE_DECISION_ASK", None)
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH), "--mode", "stop"],
        input=payload, capture_output=True, text=True, env=env, timeout=10,
    )
    assert result.returncode == 0, f"Hook exit code {result.returncode}; stderr: {result.stderr[-500:]}"
    out = result.stdout.strip()
    assert out, f"Hook produced empty stdout; stderr: {result.stderr[-500:]}"
    parsed = json.loads(out)
    assert parsed.get("decision") == "block", f"Expected decision=block; got {parsed!r}"
    assert "reason" in parsed
    assert "should_i_or" in parsed["reason"], f"Expected pattern name in reason; got {parsed['reason'][:200]!r}"
