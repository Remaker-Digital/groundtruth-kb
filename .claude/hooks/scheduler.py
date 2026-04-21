#!/usr/bin/env python3
"""
Claude Code UserPromptSubmit hook — Session Scheduler.

Reads .claude/SCHEDULE.md and injects scheduled prompts based on trigger
conditions. Groups are processed FIFO (first group evaluated each prompt).
Each user prompt triggers at most one scheduled task.

Stdin:  JSON {"user_prompt": "...", "session_id": "...", ...}
Stdout: JSON {"systemMessage": "..."} or {}
Exit:   Always 0

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import json
import re
import os
import traceback
import msvcrt  # Windows file locking
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
CLAUDE_DIR = PROJECT_DIR / ".claude"
AGENTS_FILE = PROJECT_DIR / "AGENTS.md"
SCHEDULE_FILE = CLAUDE_DIR / "SCHEDULE.md"
STATE_FILE = CLAUDE_DIR / "hooks" / ".scheduler-state.json"
LOYAL_OPPOSITION_SENTINEL = "This project is in Loyal Opposition mode until the owner revokes it."

def _env_flag(name: str) -> bool | None:
    """Parse an environment flag as a boolean when explicitly set."""
    value = os.environ.get(name)
    if value is None:
        return None

    value = value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return None


def _workspace_loyal_opposition_mode() -> bool:
    """Infer review mode from the tracked workspace contract when flags are unset."""
    try:
        return LOYAL_OPPOSITION_SENTINEL in AGENTS_FILE.read_text(encoding="utf-8")
    except OSError:
        return False


def _review_readonly_mode() -> bool:
    """Return True when the session should avoid mutating local scheduler state."""
    for name in ("LOYAL_OPPOSITION_READONLY", "CODEX_REVIEW_MODE"):
        parsed = _env_flag(name)
        if parsed is not None:
            return parsed
    return _workspace_loyal_opposition_mode()


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------
def load_state(session_id: str) -> dict:
    """Load prompt counter state. Resets when session_id changes."""
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if state.get("session_id") != session_id:
            return {"session_id": session_id, "prompt_count": 0}
        return state
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"session_id": session_id, "prompt_count": 0}


def save_state(state: dict) -> None:
    try:
        STATE_FILE.write_text(json.dumps(state), encoding="utf-8")
    except OSError:
        pass  # Non-fatal — counter just won't persist


# ---------------------------------------------------------------------------
# Schedule parsing
# ---------------------------------------------------------------------------
def parse_groups(content: str) -> list[dict]:
    """Parse SCHEDULE.md into a list of group dicts."""
    groups = []
    # Split on --- separator lines
    sections = re.split(r"\n---\n", content)

    for section in sections:
        heading = re.search(r"^## Group:\s*(.+)$", section, re.MULTILINE)
        if not heading:
            continue

        group = {
            "name": heading.group(1).strip(),
            "trigger": "always",
            "keywords": [],
            "count": 0,
            "prompts": [],
        }

        # Parse trigger line
        trigger_match = re.search(r"^trigger:\s*(.+)$", section, re.MULTILINE)
        if trigger_match:
            raw_trigger = trigger_match.group(1).strip()
            after_match = re.match(r"after:(\d+)", raw_trigger)
            if after_match:
                group["trigger"] = "after_n"
                group["count"] = int(after_match.group(1))
            else:
                group["trigger"] = raw_trigger

        # Parse keywords (for session_end trigger)
        kw_match = re.search(r"^keywords:\s*(.+)$", section, re.MULTILINE)
        if kw_match:
            group["keywords"] = [
                k.strip().lower() for k in kw_match.group(1).split(",")
            ]

        # Parse checkbox prompts
        for m in re.finditer(r"^- \[([ x])\] (.+)$", section, re.MULTILINE):
            group["prompts"].append(
                {"done": m.group(1) == "x", "text": m.group(2).strip()}
            )

        if group["prompts"]:
            groups.append(group)

    return groups


# ---------------------------------------------------------------------------
# Trigger evaluation
# ---------------------------------------------------------------------------
def _keyword_matches(user_prompt: str, keyword: str) -> bool:
    """Return True only when the keyword appears as its own phrase."""
    normalized_prompt = re.sub(r"\s+", " ", user_prompt.lower()).strip()
    normalized_keyword = re.sub(r"\s+", " ", keyword.lower()).strip()
    if not normalized_keyword:
        return False

    return re.search(rf"(?<![\w-]){re.escape(normalized_keyword)}(?![\w-])", normalized_prompt) is not None


def should_trigger(group: dict, user_prompt: str, state: dict) -> bool:
    trigger = group["trigger"]

    if trigger == "always":
        return True

    if trigger == "session_end":
        return any(_keyword_matches(user_prompt, kw) for kw in group["keywords"])

    if trigger == "after_n":
        return state["prompt_count"] >= group["count"]

    return False


# ---------------------------------------------------------------------------
# File locking (prevents TOCTOU race if multiple hooks fire simultaneously)
# ---------------------------------------------------------------------------
LOCK_FILE = CLAUDE_DIR / "hooks" / ".scheduler.lock"


class _FileLock:
    """Simple advisory file lock using msvcrt (Windows)."""

    def __init__(self, path: Path):
        self.path = path
        self._fh = None

    def __enter__(self):
        self._fh = open(self.path, "w")
        try:
            msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
        except (OSError, IOError):
            # Lock contention — wait briefly and retry once
            import time
            time.sleep(0.1)
            try:
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
            except (OSError, IOError):
                pass  # Proceed unlocked rather than fail the hook
        return self

    def __exit__(self, *args):
        if self._fh:
            try:
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
            except (OSError, IOError):
                pass
            self._fh.close()
            self._fh = None


# ---------------------------------------------------------------------------
# Schedule mutation
# ---------------------------------------------------------------------------
def mark_done(content: str, prompt_text: str) -> str:
    """Mark a specific prompt checkbox as [x]."""
    escaped = re.escape(prompt_text)
    return re.sub(
        rf"^- \[ \] {escaped}$",
        f"- [x] {prompt_text}",
        content,
        count=1,
        flags=re.MULTILINE,
    )


def remove_group(content: str, group_name: str) -> str:
    """Remove a completed group block from the schedule file."""
    # Match from ## Group: <name> to next --- or end of file
    escaped_name = re.escape(group_name)
    pattern = rf"## Group:\s*{escaped_name}.*?(?=\n---\n|\Z)"
    content = re.sub(pattern, "", content, flags=re.DOTALL)
    # Clean up consecutive --- separators
    content = re.sub(r"\n---\n(\s*\n---\n)+", "\n---\n", content)
    # Clean up trailing ---
    content = re.sub(r"\n---\s*$", "\n", content)
    # Clean up excessive blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    # Read hook payload from stdin
    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError) as e:
        print(f"scheduler.py: Failed to parse stdin: {e}", file=sys.stderr)
        json.dump({}, sys.stdout)
        sys.exit(0)

    user_prompt = payload.get("user_prompt", "")
    session_id = payload.get("session_id", "unknown")

    if _review_readonly_mode():
        json.dump({}, sys.stdout)
        sys.exit(0)

    # Update prompt counter
    state = load_state(session_id)
    state["prompt_count"] += 1

    # Check schedule file
    if not SCHEDULE_FILE.exists():
        save_state(state)
        json.dump({}, sys.stdout)
        sys.exit(0)

    # Lock to prevent TOCTOU race on read-modify-write of SCHEDULE.md
    with _FileLock(LOCK_FILE):
        try:
            # Read inside lock to ensure we have the latest content
            try:
                content = SCHEDULE_FILE.read_text(encoding="utf-8")
            except OSError as e:
                print(f"scheduler.py: Failed to read {SCHEDULE_FILE}: {e}", file=sys.stderr)
                save_state(state)
                json.dump({}, sys.stdout)
                sys.exit(0)

            groups = parse_groups(content)
            if not groups:
                save_state(state)
                json.dump({}, sys.stdout)
                sys.exit(0)

            # Evaluate first group only (FIFO — groups are processed top-to-bottom,
            # one at a time. The first group must be exhausted before the second is evaluated.)
            group = groups[0]

            if not should_trigger(group, user_prompt, state):
                save_state(state)
                json.dump({}, sys.stdout)
                sys.exit(0)

            # Find next pending prompt
            pending = [p for p in group["prompts"] if not p["done"]]
            if not pending:
                # All done — remove group
                content = remove_group(content, group["name"])
                SCHEDULE_FILE.write_text(content, encoding="utf-8")
                save_state(state)
                json.dump({}, sys.stdout)
                sys.exit(0)

            prompt = pending[0]

            # Mark this prompt as done in the file
            content = mark_done(content, prompt["text"])

            # If this was the last pending prompt, remove the entire group
            if len(pending) == 1:
                content = remove_group(content, group["name"])

            SCHEDULE_FILE.write_text(content, encoding="utf-8")
            save_state(state)

            # Output the scheduled task as a system message
            result = {
                "systemMessage": (
                    f"SCHEDULED TASK (group: {group['name']}): {prompt['text']}"
                )
            }
            json.dump(result, sys.stdout)
            sys.exit(0)

        except Exception as e:
            traceback.print_exc(file=sys.stderr)
            save_state(state)
            json.dump({}, sys.stdout)
            sys.exit(0)


if __name__ == "__main__":
    main()
