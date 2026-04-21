"""Tests for hook scripts — 2 OPS specs (SPEC-1487..1488).

Covers:
  SPEC-1487: Hook 'assertion-check.py' for session automation
  SPEC-1488: Hook 'scheduler.py' for session automation

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
HOOKS_DIR = PROJECT_ROOT / ".claude" / "hooks"


# ---------------------------------------------------------------------------
# SPEC-1487: Hook 'assertion-check.py' for session automation
# ---------------------------------------------------------------------------
class TestAssertionCheckHook:
    """SPEC-1487: assertion-check.py exists and works as a session hook."""

    def test_assertion_check_file_exists(self):
        assert (HOOKS_DIR / "assertion-check.py").exists()

    def test_assertion_check_reads_stdin_json(self):
        """The hook reads JSON from stdin (SessionStart payload)."""
        source = (HOOKS_DIR / "assertion-check.py").read_text(encoding="utf-8")
        assert "sys.stdin.read()" in source
        assert "json.loads" in source

    def test_assertion_check_outputs_json(self):
        """The hook outputs JSON to stdout."""
        source = (HOOKS_DIR / "assertion-check.py").read_text(encoding="utf-8")
        assert "json.dump" in source
        assert "sys.stdout" in source

    def test_assertion_check_exits_zero(self):
        """The hook always exits 0."""
        source = (HOOKS_DIR / "assertion-check.py").read_text(encoding="utf-8")
        assert "sys.exit(0)" in source

    def test_run_assertions_classifies_regressions(self):
        """_run_assertions differentiates regressions from expected failures."""
        source = (HOOKS_DIR / "assertion-check.py").read_text(encoding="utf-8")
        assert "regressions" in source
        assert "expected" in source
        assert "implemented" in source
        assert "verified" in source

    def test_read_handoff_prompt_function_exists(self):
        """_read_handoff_prompt reads and consumes session handoff."""
        source = (HOOKS_DIR / "assertion-check.py").read_text(encoding="utf-8")
        assert "def _read_handoff_prompt" in source
        assert "consume_session_prompt" in source

    def test_assertion_check_has_additional_context_key(self):
        """Output uses 'additionalContext' key per hook protocol."""
        source = (HOOKS_DIR / "assertion-check.py").read_text(encoding="utf-8")
        assert "additionalContext" in source


# ---------------------------------------------------------------------------
# SPEC-1488: Hook 'scheduler.py' for session automation
# ---------------------------------------------------------------------------

# Import scheduler functions directly (it's on Windows so msvcrt is available)
sys.path.insert(0, str(HOOKS_DIR))
from scheduler import (  # noqa: E402
    _FileLock,
    _keyword_matches,
    load_state,
    mark_done,
    parse_groups,
    remove_group,
    should_trigger,
)


class TestSchedulerHook:
    """SPEC-1488: scheduler.py provides session scheduling automation."""

    def test_scheduler_file_exists(self):
        assert (HOOKS_DIR / "scheduler.py").exists()

    def test_scheduler_reads_stdin_json(self):
        """The hook reads JSON from stdin (UserPromptSubmit payload)."""
        source = (HOOKS_DIR / "scheduler.py").read_text(encoding="utf-8")
        assert "sys.stdin.read()" in source
        assert "json.loads" in source

    def test_scheduler_outputs_system_message(self):
        """The hook outputs systemMessage JSON to stdout."""
        source = (HOOKS_DIR / "scheduler.py").read_text(encoding="utf-8")
        assert "systemMessage" in source


class TestParseGroups:
    """Test parse_groups function from scheduler.py."""

    SAMPLE_SCHEDULE = """# Session Schedule

---

## Group: Wrap-Up Tasks
trigger: session_end
keywords: wrap up, end session, done for today

- [ ] Execute session wrap-up procedure
- [ ] Update MEMORY.md
- [x] Already completed task

---

## Group: Always Run
trigger: always

- [ ] Check test status
- [ ] Review backlog

---

## Group: After Five
trigger: after:5

- [ ] Run audit checks
"""

    def test_parse_groups_returns_list(self):
        groups = parse_groups(self.SAMPLE_SCHEDULE)
        assert isinstance(groups, list)

    def test_parse_groups_finds_three_groups(self):
        groups = parse_groups(self.SAMPLE_SCHEDULE)
        assert len(groups) == 3

    def test_parse_groups_names(self):
        groups = parse_groups(self.SAMPLE_SCHEDULE)
        names = [g["name"] for g in groups]
        assert "Wrap-Up Tasks" in names
        assert "Always Run" in names
        assert "After Five" in names

    def test_parse_groups_trigger_types(self):
        groups = parse_groups(self.SAMPLE_SCHEDULE)
        triggers = {g["name"]: g["trigger"] for g in groups}
        assert triggers["Wrap-Up Tasks"] == "session_end"
        assert triggers["Always Run"] == "always"
        assert triggers["After Five"] == "after_n"

    def test_parse_groups_keywords(self):
        groups = parse_groups(self.SAMPLE_SCHEDULE)
        wrap_up = [g for g in groups if g["name"] == "Wrap-Up Tasks"][0]
        assert "wrap up" in wrap_up["keywords"]
        assert "end session" in wrap_up["keywords"]
        assert "done for today" in wrap_up["keywords"]

    def test_parse_groups_after_n_count(self):
        groups = parse_groups(self.SAMPLE_SCHEDULE)
        after_five = [g for g in groups if g["name"] == "After Five"][0]
        assert after_five["count"] == 5

    def test_parse_groups_prompts(self):
        groups = parse_groups(self.SAMPLE_SCHEDULE)
        wrap_up = [g for g in groups if g["name"] == "Wrap-Up Tasks"][0]
        assert len(wrap_up["prompts"]) == 3
        assert wrap_up["prompts"][0]["done"] is False
        assert wrap_up["prompts"][2]["done"] is True

    def test_parse_groups_empty_content(self):
        groups = parse_groups("")
        assert groups == []


class TestShouldTrigger:
    """Test should_trigger function from scheduler.py."""

    def test_keyword_matches_exact_phrase_boundary(self):
        assert _keyword_matches("Let's wrap up the session.", "wrap up") is True
        assert _keyword_matches("The done-state check is unrelated.", "done") is False

    def test_always_trigger_returns_true(self):
        group = {"trigger": "always", "keywords": [], "count": 0}
        state = {"prompt_count": 1}
        assert should_trigger(group, "anything", state) is True

    def test_session_end_trigger_with_matching_keyword(self):
        group = {
            "trigger": "session_end",
            "keywords": ["wrap up", "end session"],
            "count": 0,
        }
        state = {"prompt_count": 1}
        assert should_trigger(group, "Let's wrap up the session", state) is True

    def test_session_end_trigger_no_match(self):
        group = {
            "trigger": "session_end",
            "keywords": ["wrap up", "end session"],
            "count": 0,
        }
        state = {"prompt_count": 1}
        assert should_trigger(group, "Continue working on tests", state) is False

    def test_after_n_trigger_when_count_reached(self):
        group = {"trigger": "after_n", "keywords": [], "count": 5}
        state = {"prompt_count": 5}
        assert should_trigger(group, "anything", state) is True

    def test_after_n_trigger_when_count_not_reached(self):
        group = {"trigger": "after_n", "keywords": [], "count": 5}
        state = {"prompt_count": 3}
        assert should_trigger(group, "anything", state) is False

    def test_after_n_trigger_when_count_exceeded(self):
        group = {"trigger": "after_n", "keywords": [], "count": 5}
        state = {"prompt_count": 10}
        assert should_trigger(group, "anything", state) is True

    def test_unknown_trigger_returns_false(self):
        group = {"trigger": "unknown_trigger", "keywords": [], "count": 0}
        state = {"prompt_count": 1}
        assert should_trigger(group, "anything", state) is False


class TestMarkDone:
    """Test mark_done function from scheduler.py."""

    def test_marks_unchecked_as_checked(self):
        content = "- [ ] Execute session wrap-up procedure\n- [ ] Update MEMORY.md"
        result = mark_done(content, "Execute session wrap-up procedure")
        assert "- [x] Execute session wrap-up procedure" in result
        # Second item should remain unchecked
        assert "- [ ] Update MEMORY.md" in result

    def test_does_not_change_already_checked(self):
        content = "- [x] Already done\n- [ ] Not done"
        result = mark_done(content, "Not done")
        assert "- [x] Already done" in result
        assert "- [x] Not done" in result

    def test_no_match_leaves_content_unchanged(self):
        content = "- [ ] Task A\n- [ ] Task B"
        result = mark_done(content, "Task C")
        assert result == content


class TestRemoveGroup:
    """Test remove_group function from scheduler.py."""

    SAMPLE = """# Schedule

---

## Group: First Group
trigger: always

- [x] Task 1

---

## Group: Second Group
trigger: always

- [ ] Task 2
"""

    def test_removes_named_group(self):
        result = remove_group(self.SAMPLE, "First Group")
        assert "First Group" not in result
        assert "Second Group" in result

    def test_keeps_other_groups(self):
        result = remove_group(self.SAMPLE, "First Group")
        assert "Task 2" in result

    def test_removes_only_targeted_group(self):
        result = remove_group(self.SAMPLE, "Second Group")
        assert "First Group" in result
        assert "Task 1" in result


class TestLoadState:
    """Test load_state function from scheduler.py."""

    def test_returns_fresh_state_for_new_session(self):
        state = load_state("new-session-id")
        assert state["session_id"] == "new-session-id"
        assert state["prompt_count"] == 0

    @patch("scheduler.STATE_FILE")
    def test_resets_on_session_change(self, mock_state_file):
        """State resets when session_id changes."""
        mock_state_file.read_text.return_value = json.dumps({
            "session_id": "old-session",
            "prompt_count": 42,
        })
        state = load_state("new-session")
        assert state["session_id"] == "new-session"
        assert state["prompt_count"] == 0

    @patch("scheduler.STATE_FILE")
    def test_preserves_state_for_same_session(self, mock_state_file):
        """State is preserved when session_id matches."""
        mock_state_file.read_text.return_value = json.dumps({
            "session_id": "current",
            "prompt_count": 7,
        })
        state = load_state("current")
        assert state["session_id"] == "current"
        assert state["prompt_count"] == 7


class TestFileLock:
    """Test _FileLock context manager from scheduler.py."""

    def test_filelock_is_context_manager(self):
        """_FileLock supports with statement."""
        assert hasattr(_FileLock, "__enter__")
        assert hasattr(_FileLock, "__exit__")

    def test_filelock_init_stores_path(self):
        lock = _FileLock(Path("/tmp/test.lock"))
        assert lock.path == Path("/tmp/test.lock")
