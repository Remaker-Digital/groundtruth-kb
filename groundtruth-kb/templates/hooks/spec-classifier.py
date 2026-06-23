#!/usr/bin/env python3
"""Claude Code UserPromptSubmit hook — Specification Classifier (regex gate).

Enforces: GOV-REQUIREMENTS-COLLECTION-HOOK-001 v2;
DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001 v2.
See bridge/gtkb-gov-auq-enforcement-stack-slice-e-requirements-collector-2026-05-04 for approved scope.
Source rationale: DELIB-S332-NO-LLM-API-PARALLEL-USE-DIRECTIVE;
DELIB-S332-CANONICAL-TRIGGER-SET-INTUITIVE-CLARIFICATION.

Detects owner input that contains canonical specification-language triggers
and emits a reminder directing the AI agent to use AskUserQuestion to
confirm any specification creation BEFORE proceeding. The hook is a regex
gate, not an LLM classifier — owner uses explicit language to invoke it.

Stdin:  JSON {"prompt": "...", "session_id": "...", "transcript_path": "...", ...}
Stdout: JSON {"systemMessage": "..."} when a canonical trigger fires; "{}" otherwise
Exit:   Always 0

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import re
import sys

# Canonical specification-language triggers. Owner-intuitive phrasings that
# invoke the AUQ-only-spec-creation invariant. Pattern set is intentionally
# small so the owner can remember + use them as a contract.
SPEC_PATTERNS = [
    # Imperative artifact-creation triggers
    r"\bcreate (?:a |the )?(?:spec|specification|requirement|GOV|ADR|DCL|PB|protected behavior)\b",
    r"\b(?:specify|track|capture) (?:that|this|it)\b",
    r"\b(?:make|add) (?:a |an )?(?:requirement|specification|spec|GOV|ADR|DCL)\b",
    # Declarative artifact-classification triggers
    r"\b(?:this|that) is (?:a |an )?(?:requirement|specification|spec|protected behavior)\b",
    # Imperative modal verb triggers (preserved from prior pattern set)
    r"\bthe (?:system|product|feature) (?:must|shall|should)\b",
    # Standing-rule triggers (preserved from prior pattern set)
    r"\b(?:from now on|always|never)\s+\S+(?:\s+\S+){0,4}\s+(?:use|do|require|include|ensure|allow|skip|omit)\b",
]

# Anti-patterns: phrasings that look spec-like but are commands, questions,
# or affirmations and should NOT fire the reminder.
ANTI_PATTERNS = [
    r"^(?:stop|wait|pause|hold|cancel)\b",
    r"^(?:what|how|why|where|when|who|can you|do you|is there|are there)\b",
    r"^(?:show|list|read|open|check|look|find|search|grep|run|execute|deploy|commit)\b",
    r"^(?:fix|debug|investigate|explain|describe|summarize)\b",
    r"^(?:yes|no|ok|sure|agreed|approved|proceed|continue|go ahead)\b",
]

# Minimum prompt length filter — short prompts are typically commands or
# affirmations, not specification statements.
MIN_SPEC_LENGTH = 40


def detect_specification_language(prompt: str) -> bool:
    """Return True if the prompt matches a canonical specification-language trigger."""
    stripped = prompt.strip()
    if len(stripped) < MIN_SPEC_LENGTH:
        return False
    first_line = stripped.split("\n")[0].strip().lower()
    for pattern in ANTI_PATTERNS:
        if re.search(pattern, first_line, re.IGNORECASE):
            return False
    return any(re.search(pattern, stripped, re.IGNORECASE | re.MULTILINE) for pattern in SPEC_PATTERNS)


# AUQ-only-spec-creation invariant reminder. Cited rules:
# - GOV-REQUIREMENTS-COLLECTION-HOOK-001 v2 (this hook's mandate)
# - GOV-SPEC-CAPTURE-TRANSPARENCY-001 (surfacing transparency)
# Per S332 owner directive: "no requirements specifications are created
# without my explicit choice from an AskUserQuestion."
REMINDER = (
    "SPECIFICATION TRIGGER — Your message contains a canonical specification-language trigger.\n\n"
    "Per GOV-REQUIREMENTS-COLLECTION-HOOK-001 v2: do NOT create or promote any formal artifact "
    "(SPEC / REQ / GOV / ADR / DCL / PB / DELIB) without first issuing an AskUserQuestion to confirm "
    "the artifact's existence, scope, and approval.\n\n"
    "Per GOV-SPEC-CAPTURE-TRANSPARENCY-001: surface the candidate to the owner immediately with "
    "classification, interpretation, and the artifact that would be created if approved. Wait for the "
    "AskUserQuestion answer before any KB mutation."
)


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
        # Accept both legacy "user_prompt" and current "prompt" field names
        # per Claude Code UserPromptSubmit hook contract evolution.
        prompt = data.get("prompt") or data.get("user_prompt") or ""
        if detect_specification_language(prompt):
            json.dump({"systemMessage": REMINDER}, sys.stdout)
        else:
            json.dump({}, sys.stdout)
    except Exception:
        # Non-fatal — never block the user prompt submission.
        json.dump({}, sys.stdout)


if __name__ == "__main__":
    main()
