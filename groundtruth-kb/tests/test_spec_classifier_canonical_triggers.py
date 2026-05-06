"""Tests for Sub-slice E: regex-trigger AUQ gate.

Per bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04-007.md
GO at -008.

Verifies:
  - Canonical specification-language triggers fire the reminder.
  - Anti-patterns and short messages do NOT fire.
  - Reminder text contains the AUQ-only-spec-creation invariant.
  - Hook is registered in tracked .claude/settings.json (NOT settings.local.json).
  - Hook is registered in .codex/hooks.json (forward-compatible parity per
    ADR-CODEX-HOOK-PARITY-FALLBACK-001).
  - End-to-end subprocess invocation emits expected stdout JSON.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "spec-classifier.py"
TRACKED_SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"
CODEX_HOOKS_PATH = REPO_ROOT / ".codex" / "hooks.json"


def _run_hook(prompt: str) -> dict:
    """Invoke the hook via subprocess with the given prompt; return parsed stdout."""
    payload = json.dumps({
        "session_id": "test-spec-classifier-canonical",
        "transcript_path": "/tmp/transcript.jsonl",
        "cwd": str(REPO_ROOT),
        "hook_event_name": "UserPromptSubmit",
        "prompt": prompt,
    })
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=payload, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"Hook exit {result.returncode}; stderr: {result.stderr[-500:]}"
    out = result.stdout.strip()
    return json.loads(out) if out else {}


# ---- Canonical-trigger detection tests ----


def test_canonical_trigger_create_specification_fires():
    """`Create a specification for X` matches the imperative-creation pattern."""
    response = _run_hook("Create a specification for the API rate-limit policy.")
    assert "systemMessage" in response, f"Expected systemMessage; got {response}"


def test_canonical_trigger_track_as_requirement_fires():
    """`Track this as a requirement` matches the imperative-creation pattern."""
    response = _run_hook("Track this as a requirement for the upcoming release window.")
    assert "systemMessage" in response, f"Expected systemMessage; got {response}"


def test_canonical_trigger_this_is_a_protected_behavior_fires():
    """`This is a protected behavior` matches the declarative-classification pattern."""
    response = _run_hook(
        "This is a protected behavior of the system that must never be removed."
    )
    assert "systemMessage" in response, f"Expected systemMessage; got {response}"


def test_canonical_trigger_imperative_modal_fires():
    """`The system must include X` matches the imperative-modal pattern."""
    response = _run_hook(
        "The system must include retry-after handling for all 429 responses."
    )
    assert "systemMessage" in response, f"Expected systemMessage; got {response}"


# ---- Anti-pattern non-detection tests ----


def test_anti_pattern_show_does_not_fire():
    """`show me X` is a command, not a specification statement."""
    response = _run_hook("show me the rate limit configuration in the codebase please")
    assert response == {}, f"Expected empty; got {response}"


def test_anti_pattern_question_does_not_fire():
    """A question is not a specification statement."""
    response = _run_hook("what is the current rate limit configuration in the codebase?")
    assert response == {}, f"Expected empty; got {response}"


def test_anti_pattern_affirmative_does_not_fire():
    """An affirmative response is not a specification statement."""
    response = _run_hook("yes proceed with the implementation as you described above")
    assert response == {}, f"Expected empty; got {response}"


def test_short_message_does_not_fire():
    """Messages shorter than MIN_SPEC_LENGTH (40 chars) do not fire."""
    response = _run_hook("create a spec")  # 13 chars — too short
    assert response == {}, f"Expected empty; got {response}"


# ---- Reminder content tests ----


def test_reminder_text_contains_auq_invariant():
    """The reminder string must contain the AUQ-only-spec-creation invariant.

    Per GOV-REQUIREMENTS-COLLECTION-HOOK-001 v2: the reminder must direct
    the AI agent to use AskUserQuestion before any artifact creation.
    """
    response = _run_hook(
        "Create a specification for the new authentication flow with these constraints."
    )
    assert "systemMessage" in response
    msg = response["systemMessage"]
    assert "AskUserQuestion" in msg, f"Reminder missing 'AskUserQuestion': {msg[:200]}"
    assert "do NOT create" in msg, f"Reminder missing 'do NOT create' invariant: {msg[:200]}"


# ---- E2E subprocess smoke tests ----


def test_hook_subprocess_smoke_emits_systemMessage_on_match():
    """End-to-end subprocess invocation with a canonical trigger produces stdout JSON."""
    payload = json.dumps({
        "session_id": "test-e2e-match",
        "hook_event_name": "UserPromptSubmit",
        "prompt": "Create a specification for the cache invalidation policy described above.",
    })
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=payload, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
    parsed = json.loads(result.stdout.strip())
    assert "systemMessage" in parsed
    assert "SPECIFICATION TRIGGER" in parsed["systemMessage"]


def test_hook_subprocess_smoke_emits_empty_on_no_match():
    """End-to-end subprocess invocation with a non-trigger message produces empty JSON."""
    payload = json.dumps({
        "session_id": "test-e2e-nomatch",
        "hook_event_name": "UserPromptSubmit",
        "prompt": "show me the bridge index please",  # short + anti-pattern
    })
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=payload, capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
    parsed = json.loads(result.stdout.strip())
    assert parsed == {}, f"Expected empty dict; got {parsed}"


# ---- Hook registration tests ----


def test_hook_registered_in_claude_settings():
    """Tracked .claude/settings.json registers spec-classifier.py under UserPromptSubmit.

    NOT .claude/settings.local.json (workstation-local; doesn't propagate to
    fresh clones). Per Codex -004 F1 + REVISED-2 scope expansion.
    """
    config = json.loads(TRACKED_SETTINGS_PATH.read_text(encoding="utf-8"))
    user_prompt_hooks = config.get("hooks", {}).get("UserPromptSubmit", [])
    found = False
    for group in user_prompt_hooks:
        for h in group.get("hooks", []):
            cmd = h.get("command", "")
            if "spec-classifier.py" in cmd:
                found = True
                break
    assert found, (
        f"spec-classifier.py not registered under UserPromptSubmit in tracked "
        f"{TRACKED_SETTINGS_PATH}. Settings: {user_prompt_hooks}"
    )


def test_hook_registered_in_codex_hooks_json():
    """`.codex/hooks.json` registers spec-classifier.py under UserPromptSubmit.

    Forward-compatible parity per ADR-CODEX-HOOK-PARITY-FALLBACK-001 + Codex
    -006 F1. Currently disabled on Windows (Codex hook parity not yet live);
    active when parity activates.
    """
    config = json.loads(CODEX_HOOKS_PATH.read_text(encoding="utf-8"))
    user_prompt_hooks = config.get("hooks", {}).get("UserPromptSubmit", [])
    found = False
    for group in user_prompt_hooks:
        for h in group.get("hooks", []):
            cmd = h.get("command", "")
            if "spec-classifier.py" in cmd:
                found = True
                break
    assert found, (
        f"spec-classifier.py not registered under UserPromptSubmit in "
        f"{CODEX_HOOKS_PATH}. Settings: {user_prompt_hooks}"
    )
