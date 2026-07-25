#!/usr/bin/env python3
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""GOV-09 owner-input classification capture (UserPromptSubmit).

Classifies the owner's prompt per GOV-09 (specification language triggers
spec-first workflow). When specification language is detected, emits an
additionalContext reminder so the agent applies the spec-first workflow and
archives the classification as a Deliberation Archive row.

Fail-open: any error silently exits 0 so the hook never blocks agent work.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _delib_common import insert_deliberation  # noqa: E402

GOV09_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(?:must|shall|should)\s+(?:be|have|include|support|provide|ensure|allow|require)", re.I),
    re.compile(r"\b(?:the\s+system|the\s+platform|the\s+application)\s+(?:must|shall|should)\b", re.I),
    re.compile(r"(?:^|\n)\s*\d+[\.\)]\s+\w", re.M),
    re.compile(r"\b(?:requirement|acceptance\s+criteria|success\s+criteria)\b", re.I),
]

ANTI_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^(?:git\s|cd\s|ls\s|cat\s|grep\s|ruff\s|pytest|python\s)", re.I),
    re.compile(r"^\s*(?:yes|no|ok|sure|approved?|confirm|go\s+ahead|looks?\s+good)\s*[.!]?\s*$", re.I),
    re.compile(r"^(?:what|how|why|when|where|who|which|can|does|is|are|do)\b.*\?\s*$", re.I | re.S),
    re.compile(r"^::init\s+gtkb\b", re.I),
    re.compile(r"^/\w+", re.I),
    re.compile(r"^\?$"),
]

MIN_LENGTH = 30

GOV09_CONTEXT = (
    "[GOV-09] Specification language detected in owner input. "
    "Before writing any code: (1) record or verify specifications in KB, "
    "(2) identify work items for any gaps, (3) add work items to the backlog, "
    "(4) present the backlog for prioritization. Only proceed to implementation "
    "after explicit prioritization approval."
)


def classify_gov09(prompt: str) -> bool:
    """Return True when the prompt looks like specification language."""
    if len(prompt.strip()) < MIN_LENGTH:
        return False
    for ap in ANTI_PATTERNS:
        if ap.search(prompt):
            return False
    for pat in GOV09_PATTERNS:
        if pat.search(prompt):
            return True
    return False


def main() -> int:
    """Hook entry point."""
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return 0

    prompt = payload.get("user_prompt", "") or payload.get("prompt", "")
    if not prompt:
        print(json.dumps({}))
        return 0

    if not classify_gov09(prompt):
        print(json.dumps({}))
        return 0

    session_id = payload.get("session_id", "")
    insert_deliberation(
        source_type="gov09_classification",
        content=f"GOV-09 spec-language detected:\n{prompt[:500]}",
        outcome="spec_language_detected",
        session_id=session_id,
        source_ref="hook/gov09-capture",
    )

    print(json.dumps({"additionalContext": GOV09_CONTEXT}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
