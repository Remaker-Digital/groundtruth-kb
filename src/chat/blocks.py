# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Structured Answer Blocks — heuristic extraction from AI responses (SPEC-1867).

Detects structural patterns in AI response text and converts them to
typed blocks for rich widget rendering. Block types (v1):

    - steps: Numbered procedure lists (1. 2. 3. or Step 1: Step 2:)
    - faq: Q&A pairs (Q: / A: patterns, bold question headers)
    - action: CTA with URL (detected markdown links with action verbs)

Product cards are deferred to v2 (requires upstream structured-data plumbing).

Blocks are supplementary — the text content is always preserved as fallback.
Extraction is heuristic/regex only (no LLM call).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Block types
# ---------------------------------------------------------------------------

StepsBlock = dict  # {"type": "steps", "title": str|None, "items": list[str]}
FaqBlock = dict    # {"type": "faq", "items": list[{"question": str, "answer": str}]}
ActionBlock = dict # {"type": "action", "label": str, "url": str, "style": str}


# ---------------------------------------------------------------------------
# Extraction patterns
# ---------------------------------------------------------------------------

# Numbered list: "1. Do this\n2. Do that\n3. Do the other"
# Also matches "Step 1: ..." pattern
_NUMBERED_RE = re.compile(
    r"(?:^|\n)"                          # line start
    r"(?:(?:step\s+)?\d+[\.\):])\s+"     # "1. " or "Step 1: " or "1) "
    r"(.+)",                             # item text
    re.IGNORECASE | re.MULTILINE,
)

# Q&A pairs: "Q: What is...?\nA: It is..."
_QA_EXPLICIT_RE = re.compile(
    r"(?:^|\n)\s*"
    r"(?:Q:|Question:)\s*"                      # question marker
    r"(.+?)"                                    # question text
    r"\n\s*(?:A:|Answer:)\s*"                   # answer marker
    r"(.+?)(?=\n\s*(?:Q:|Question:)|$)",        # answer text
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)

# Bold-question format: "**What is your policy?**\nAnswer text here"
_QA_BOLD_RE = re.compile(
    r"\*\*([^*]+\??)\*\*\s*\n"                  # **question**
    r"(.+?)(?=\n\s*\*\*[^*]+\*\*|\Z)",         # answer until next bold or end
    re.DOTALL,
)

# Action CTA: markdown link with action verbs
_ACTION_RE = re.compile(
    r"\[([^\]]+)\]\((https?://[^)]+)\)",
    re.IGNORECASE,
)

_ACTION_VERBS = frozenset({
    "track", "order", "return", "exchange", "contact", "call", "visit",
    "learn", "view", "check", "start", "get", "find", "see", "browse",
    "shop", "buy", "download", "sign up", "subscribe", "book", "schedule",
})


# ---------------------------------------------------------------------------
# Extraction functions
# ---------------------------------------------------------------------------

def extract_steps(text: str) -> StepsBlock | None:
    """Extract a numbered step list from the response text."""
    matches = _NUMBERED_RE.findall(text)
    if len(matches) < 2:  # Need at least 2 steps to form a block
        return None

    # Check they're consecutive (not scattered random numbers)
    items = [m.strip() for m in matches if m.strip()]
    if len(items) < 2:
        return None

    # Try to extract a title (line before the first numbered item)
    lines = text.strip().split("\n")
    title = None
    for line in lines:
        stripped = line.strip()
        if stripped and not _NUMBERED_RE.match(stripped):
            # Potential title — check it's short and not a paragraph
            if len(stripped) < 100 and not stripped.endswith("."):
                title = stripped.rstrip(":")
            break
        elif _NUMBERED_RE.match(stripped):
            break

    return {"type": "steps", "title": title, "items": items}


def extract_faq(text: str) -> FaqBlock | None:
    """Extract Q&A pairs from the response text.

    Supports two formats:
      - Explicit: Q: ... / A: ... or Question: ... / Answer: ...
      - Bold: **question?**\\nanswer text
    """
    items: list[dict[str, str]] = []

    # Try explicit Q:/A: format first
    for q, a in _QA_EXPLICIT_RE.findall(text):
        question = q.strip().strip("*").strip()
        answer = a.strip()
        if question and answer:
            items.append({"question": question, "answer": answer})

    # Try bold-question format if no explicit matches
    if not items:
        for q, a in _QA_BOLD_RE.findall(text):
            question = q.strip()
            answer = a.strip()
            if question and answer:
                items.append({"question": question, "answer": answer})

    if not items:
        return None

    return {"type": "faq", "items": items}


def extract_actions(text: str) -> list[ActionBlock]:
    """Extract CTA action blocks from markdown links with action verbs."""
    actions: list[ActionBlock] = []
    for match in _ACTION_RE.finditer(text):
        label = match.group(1).strip()
        url = match.group(2).strip()
        # Only promote to action block if the label contains an action verb
        label_lower = label.lower()
        if any(verb in label_lower for verb in _ACTION_VERBS):
            actions.append({
                "type": "action",
                "label": label,
                "url": url,
                "style": "primary",
            })
    return actions


def extract_blocks(text: str) -> list[dict[str, Any]]:
    """Extract all structured blocks from AI response text.

    Returns a list of block dicts. Empty list if no blocks detected.
    Blocks are ordered: steps first, then faq, then actions.
    """
    blocks: list[dict[str, Any]] = []

    steps = extract_steps(text)
    if steps:
        blocks.append(steps)

    faq = extract_faq(text)
    if faq:
        blocks.append(faq)

    actions = extract_actions(text)
    for action in actions[:3]:  # Cap at 3 action buttons
        blocks.append(action)

    return blocks
