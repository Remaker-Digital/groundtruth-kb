#!/usr/bin/env python3
"""
UserPromptSubmit hook: session scheduler.

Reads .claude/SCHEDULE.md and injects the next unexecuted prompt as
additional context for the current user prompt. Unchecked items
(lines starting with "- [ ]") are candidates; the first one found
is injected.

Hook type: UserPromptSubmit

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import os
import sys


SCHEDULE_PATH = os.path.join(".claude", "SCHEDULE.md")


def find_next_scheduled_prompt():
    """Find the first unchecked item in SCHEDULE.md."""
    if not os.path.isfile(SCHEDULE_PATH):
        return None

    try:
        with open(SCHEDULE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped.startswith("- [ ]"):
                    # Extract the prompt text after the checkbox.
                    prompt_text = stripped[len("- [ ]"):].strip()
                    if prompt_text:
                        return prompt_text
    except (IOError, OSError):
        return None

    return None


def main():
    scheduled_prompt = find_next_scheduled_prompt()

    if scheduled_prompt:
        # Output the scheduled prompt as additional context.
        # The hook system will append this to the user's prompt.
        print(
            f"[Scheduled task from .claude/SCHEDULE.md]\n"
            f"{scheduled_prompt}"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
