# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""CQ-1: Runtime conversation quality scoring (SPEC-0180).

Evaluates every AI response on a 1-5 scale across three dimensions:
faithfulness (40%), relevancy (40%), tone (20%).  Uses the Phase 0
heuristic engine from the Quality Pilot (evaluation/pilots/quality_pilot.py)
adapted for runtime use — no golden dataset required.

The scorer is invoked asynchronously after each AI turn so it does NOT
add latency to the user experience.  Scores are stored in the conversation
document's message metadata under ``quality_score``.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging

from src.chat.models import QualityScore

logger = logging.getLogger(__name__)

# Profanity markers that reduce the tone score.
_PROFANITY_MARKERS = frozenset({"damn", "hell", "crap", "wtf", "shit", "fuck"})

# Smart-quote normalization table (same as quality_pilot.py).
_SMART_QUOTES = str.maketrans({
    "\u2018": "'",
    "\u2019": "'",
    "\u201C": '"',
    "\u201D": '"',
})


class ConversationQualityScorer:
    """Stateless scorer — one instance per application, called per-turn."""

    def score_turn(
        self,
        ai_response: str,
        customer_message: str = "",
        knowledge_context: str = "",
        *,
        expected_contains: list[str] | None = None,
        expected_excludes: list[str] | None = None,
        is_jailbreak_block: bool = False,
    ) -> QualityScore:
        """Score a single AI response turn.

        Args:
            ai_response: The AI-generated response text.
            customer_message: The customer's question (for relevancy context).
            knowledge_context: The knowledge base context that was provided.
            expected_contains: Optional phrases the response should include.
            expected_excludes: Optional phrases the response must avoid.
            is_jailbreak_block: If True and response is empty, treat as
                correct Critic blocking (perfect 5.0).

        Returns:
            QualityScore with per-dimension and overall scores.
        """
        issues: list[str] = []
        response_lower = ai_response.translate(_SMART_QUOTES).lower()

        # --- Jailbreak fast-path ---
        if is_jailbreak_block and len(ai_response.strip()) == 0:
            return QualityScore(
                faithfulness=5.0,
                relevancy=5.0,
                tone=5.0,
                overall=5.0,
                issues=[],
            )

        # --- Faithfulness (1-5) ---
        # Based on excluded-phrase compliance + response sanity.
        excludes = expected_excludes or []
        excludes_violations = 0
        for phrase in excludes:
            if phrase.lower() in response_lower:
                excludes_violations += 1
                issues.append(f"Contains excluded phrase: '{phrase}'")

        if excludes:
            excludes_ratio = 1.0 - (excludes_violations / len(excludes))
        else:
            excludes_ratio = 1.0

        faith_base = excludes_ratio * 4.0 + 1.0
        if len(ai_response.strip()) < 10 and len(ai_response.strip()) > 0:
            faith_base = max(1.0, faith_base - 1.0)
            issues.append("Response suspiciously short")
        elif len(ai_response.strip()) == 0:
            faith_base = 1.0
            issues.append("Empty response")
        faithfulness = round(min(5.0, faith_base), 1)

        # --- Relevancy (1-5) ---
        # Based on expected-phrase inclusion.
        contains = expected_contains or []
        if contains:
            hits = sum(1 for p in contains if p.lower() in response_lower)
            contains_ratio = hits / len(contains)
        else:
            # Without golden-data, use heuristic: non-empty response to
            # non-empty question = baseline 4.0.  Short or empty = penalized.
            if customer_message.strip() and ai_response.strip():
                contains_ratio = 0.75  # baseline relevancy
            elif ai_response.strip():
                contains_ratio = 0.5
            else:
                contains_ratio = 0.0

        relevancy = round(min(5.0, contains_ratio * 4.0 + 1.0), 1)

        # --- Tone (1-5) ---
        tone_score = 5.0
        for marker in _PROFANITY_MARKERS:
            if marker in response_lower:
                tone_score -= 1.0
                issues.append(f"Profanity detected: '{marker}'")
        # Excessive capitalization
        if len(ai_response) > 20:
            caps_ratio = sum(1 for c in ai_response if c.isupper()) / len(ai_response)
            if caps_ratio > 0.5:
                tone_score -= 1.0
                issues.append("Excessive capitalization")
        tone = round(max(1.0, tone_score), 1)

        # --- Overall (weighted) ---
        overall = round(faithfulness * 0.4 + relevancy * 0.4 + tone * 0.2, 1)

        return QualityScore(
            faithfulness=faithfulness,
            relevancy=relevancy,
            tone=tone,
            overall=overall,
            issues=issues,
        )

    def aggregate_conversation_quality(
        self,
        turn_scores: list[QualityScore],
    ) -> QualityScore | None:
        """Compute aggregate quality score for an entire conversation.

        Returns None if no turns were scored.
        """
        if not turn_scores:
            return None

        n = len(turn_scores)
        avg_faith = round(sum(s.faithfulness for s in turn_scores) / n, 1)
        avg_rel = round(sum(s.relevancy for s in turn_scores) / n, 1)
        avg_tone = round(sum(s.tone for s in turn_scores) / n, 1)
        avg_overall = round(avg_faith * 0.4 + avg_rel * 0.4 + avg_tone * 0.2, 1)

        # Collect unique issues across all turns
        all_issues: list[str] = []
        seen: set[str] = set()
        for s in turn_scores:
            for issue in s.issues:
                if issue not in seen:
                    seen.add(issue)
                    all_issues.append(issue)

        return QualityScore(
            faithfulness=avg_faith,
            relevancy=avg_rel,
            tone=avg_tone,
            overall=avg_overall,
            issues=all_issues,
        )


# Module-level singleton — import and use directly.
quality_scorer = ConversationQualityScorer()
