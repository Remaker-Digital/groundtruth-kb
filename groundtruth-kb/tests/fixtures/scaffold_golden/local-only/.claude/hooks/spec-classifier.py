#!/usr/bin/env python3
"""
UserPromptSubmit hook — Specification Classifier.

Detects owner input that contains specification-like language (requirements,
business rules, "must/should/shall" directives) and injects a system message
reminding the assistant to follow the spec-first workflow:

  1. Record or verify specifications in the knowledge database
  2. Create work items for gaps
  3. Add work items to backlog
  4. Present backlog for owner prioritization
  5. Only then proceed to implementation

This is a mechanical guardrail — it fires BEFORE the assistant sees the
message, ensuring the classification step cannot be skipped.

Hook type: UserPromptSubmit
Stdin:  JSON {"user_prompt": "...", "session_id": "...", ...}
Stdout: JSON {"systemMessage": "..."} or {}
Exit:   Always 0

Customize: adjust SPEC_PATTERNS for your project's domain language.
"""

import json
import re
import sys

# Phrases that signal the owner is stating requirements/specifications
SPEC_PATTERNS = [
    # Modal verbs indicating requirements
    r"\bmust\s+(include|have|support|provide|implement|ensure|validate|contain)\b",
    r"\bshould\s+(include|have|support|provide|implement|ensure|validate|contain)\b",
    r"\bshall\s+(include|have|support|provide|implement|ensure|validate|contain)\b",
    # Numbered criteria or acceptance conditions
    r"(?:^|\n)\s*\d+[\.\)]\s+.{10,}",
    # Explicit spec language
    r"\b(?:specification|requirement|acceptance\s+criter|business\s+rule)\b",
    # "The system must/should..."
    r"\bthe\s+system\s+(must|should|shall|will)\b",
]

SPEC_REMINDER = """SPEC-FIRST WORKFLOW TRIGGERED — the owner's message appears to contain specification language.

Before writing any code:
1. Record or verify specifications in the knowledge database
2. Identify work items for any gaps
3. Add work items to the backlog
4. Present the backlog for prioritization approval
5. Only proceed to implementation after explicit approval"""


def _contains_spec_language(text: str) -> bool:
    """Check if the text contains specification-like patterns."""
    text_lower = text.lower()
    return any(re.search(pattern, text_lower, re.MULTILINE) for pattern in SPEC_PATTERNS)


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        print(json.dumps({}))
        return

    user_prompt = payload.get("user_prompt", "")

    if _contains_spec_language(user_prompt):
        print(json.dumps({"systemMessage": SPEC_REMINDER}))
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
