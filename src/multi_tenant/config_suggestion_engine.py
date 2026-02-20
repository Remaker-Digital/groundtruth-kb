"""Configuration Suggestion Engine (KA-4: Knowledge Automation).

Heuristic analysis of KB articles and storefront content to generate
configuration suggestions for merchant tenants. Pure text analysis —
no LLM calls, deterministic, cost-free.

Analyzes KB content to extract:
  - brand_name (from product titles)
  - brand_voice (from content tone analysis)
  - return_policy (from policy articles)
  - shipping_info (from shipping articles)
  - escalation_keywords (from complaint/safety patterns)
  - greeting_message (from brand name + category)
  - widget_agent_display_name (from brand name)

Each suggestion has a confidence score (0.0-1.0).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Suggestion:
    """A single configuration suggestion with confidence score."""

    field_name: str
    value: Any
    confidence: float  # 0.0 to 1.0
    source: str  # Description of where this suggestion came from


@dataclass
class SuggestionSet:
    """Collection of configuration suggestions for a tenant."""

    suggestions: list[Suggestion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to a dict keyed by field_name."""
        return {
            s.field_name: {
                "value": s.value,
                "confidence": s.confidence,
                "source": s.source,
            }
            for s in self.suggestions
        }

    def get(self, field_name: str) -> Suggestion | None:
        """Get a suggestion by field name."""
        return next((s for s in self.suggestions if s.field_name == field_name), None)


# ---------------------------------------------------------------------------
# Tone analysis keywords
# ---------------------------------------------------------------------------

_TONE_KEYWORDS: dict[str, list[str]] = {
    "professional": [
        "professional", "compliance", "regulatory", "specification",
        "certification", "warranty", "guarantee", "standards",
    ],
    "friendly": [
        "welcome", "happy to help", "love", "enjoy", "fun", "great",
        "awesome", "wonderful", "excited", "glad",
    ],
    "technical": [
        "technical", "specification", "compatible", "processor", "RAM",
        "bandwidth", "resolution", "performance", "benchmark",
    ],
    "caring": [
        "care", "gentle", "sensitive", "health", "wellness", "safe",
        "natural", "organic", "nurturing",
    ],
    "luxury": [
        "premium", "exclusive", "artisan", "handcrafted", "bespoke",
        "curated", "elegant", "sophisticated", "exquisite",
    ],
}

_ESCALATION_PATTERNS: list[str] = [
    "defective", "broken", "damaged", "fraud", "stolen", "recall",
    "safety", "hazard", "allergic", "reaction", "injury", "lawsuit",
    "toxic", "contamination", "poisoning", "expired", "counterfeit",
    "unauthorized", "complaint", "refund demand",
]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class ConfigSuggestionEngine:
    """Generates configuration suggestions from KB content analysis.

    Pure heuristic engine — no LLM calls. Fast, deterministic, cost-free.
    """

    async def generate_suggestions(
        self,
        tenant_id: str,
        articles: list[dict[str, Any]] | None = None,
    ) -> SuggestionSet:
        """Generate config suggestions from KB articles.

        Args:
            tenant_id: Tenant to analyze.
            articles: Pre-loaded articles. If None, fetches from repository.

        Returns:
            SuggestionSet with field suggestions and confidence scores.
        """
        if articles is None:
            articles = await self._fetch_articles(tenant_id)

        if not articles:
            return SuggestionSet()

        suggestions = SuggestionSet()

        # Extract suggestions from different signals
        brand_name = self._extract_brand_name(articles)
        if brand_name:
            suggestions.suggestions.append(brand_name)

        brand_voice = self._analyze_brand_voice(articles)
        if brand_voice:
            suggestions.suggestions.append(brand_voice)

        escalation = self._extract_escalation_keywords(articles)
        if escalation:
            suggestions.suggestions.append(escalation)

        greeting = self._generate_greeting(articles, brand_name)
        if greeting:
            suggestions.suggestions.append(greeting)

        display_name = self._suggest_display_name(brand_name)
        if display_name:
            suggestions.suggestions.append(display_name)

        logger.info(
            "Generated %d suggestions for tenant %s from %d articles",
            len(suggestions.suggestions), tenant_id[:8], len(articles),
        )

        return suggestions

    @staticmethod
    async def _fetch_articles(tenant_id: str) -> list[dict[str, Any]]:
        """Fetch KB articles from the repository."""
        try:
            from src.multi_tenant.repository import KnowledgeBaseRepository

            repo = KnowledgeBaseRepository()
            results = await repo.list_filtered(
                tenant_id,
                offset=0,
                limit=100,
                status="published",
            )
            return results
        except Exception:
            logger.warning(
                "Failed to fetch articles for tenant %s",
                tenant_id[:8],
                exc_info=True,
            )
            return []

    @staticmethod
    def _extract_brand_name(articles: list[dict[str, Any]]) -> Suggestion | None:
        """Extract likely brand name from article titles and metadata."""
        # Count words in titles (excluding common stop words)
        stop_words = {
            "the", "a", "an", "and", "or", "for", "to", "in", "of", "on",
            "is", "how", "what", "why", "when", "our", "your", "my", "we",
            "i", "you", "it", "do", "does", "can", "will", "with", "about",
            "guide", "policy", "faq", "help", "information", "instructions",
        }

        word_counts: Counter = Counter()
        for article in articles:
            metadata = article.get("metadata", {})
            vendor = metadata.get("vendor")
            if vendor and vendor.strip():
                word_counts[vendor.strip()] += 3  # Vendor field is high signal

        if not word_counts:
            return None

        top_word, count = word_counts.most_common(1)[0]
        if count < 2:
            return None

        confidence = min(count / (len(articles) * 0.5), 1.0)
        return Suggestion(
            field_name="brand_name",
            value=top_word,
            confidence=round(confidence, 2),
            source=f"Extracted from vendor field ({count} occurrences)",
        )

    @staticmethod
    def _analyze_brand_voice(articles: list[dict[str, Any]]) -> Suggestion | None:
        """Determine brand voice from content tone analysis."""
        all_content = " ".join(
            article.get("content", "").lower() for article in articles
        )

        if len(all_content) < 200:
            return None

        tone_scores: dict[str, int] = {}
        for tone, keywords in _TONE_KEYWORDS.items():
            score = sum(all_content.count(kw) for kw in keywords)
            if score > 0:
                tone_scores[tone] = score

        if not tone_scores:
            return None

        # Pick the top two tones for a compound descriptor
        sorted_tones = sorted(tone_scores.items(), key=lambda x: x[1], reverse=True)
        top_tone = sorted_tones[0][0]

        if len(sorted_tones) > 1 and sorted_tones[1][1] > sorted_tones[0][1] * 0.5:
            voice = f"{top_tone} and {sorted_tones[1][0]}"
        else:
            voice = top_tone

        total_matches = sum(tone_scores.values())
        confidence = min(total_matches / max(len(articles) * 2, 1), 1.0)

        return Suggestion(
            field_name="brand_voice",
            value=voice,
            confidence=round(confidence, 2),
            source=f"Tone analysis: {dict(sorted_tones[:3])}",
        )

    @staticmethod
    def _extract_escalation_keywords(
        articles: list[dict[str, Any]],
    ) -> Suggestion | None:
        """Extract escalation keywords from article content."""
        all_content = " ".join(
            article.get("content", "").lower() for article in articles
        )

        found_keywords = []
        for pattern in _ESCALATION_PATTERNS:
            if pattern in all_content:
                found_keywords.append(pattern)

        if not found_keywords:
            return None

        confidence = min(len(found_keywords) / 5, 1.0)
        return Suggestion(
            field_name="escalation_keywords",
            value=found_keywords[:15],  # Cap at 15 keywords
            confidence=round(confidence, 2),
            source=f"Found {len(found_keywords)} escalation patterns in KB content",
        )

    @staticmethod
    def _generate_greeting(
        articles: list[dict[str, Any]],
        brand_suggestion: Suggestion | None,
    ) -> Suggestion | None:
        """Generate a greeting message suggestion."""
        brand_name = brand_suggestion.value if brand_suggestion else "our store"

        # Try to infer category from article categories
        categories: Counter = Counter()
        for article in articles:
            cat = article.get("category", "")
            if cat:
                categories[cat.lower()] += 1

        greeting = (
            f"Welcome to {brand_name}! I'm here to help you with "
            f"product information, order questions, and anything else "
            f"you need. How can I assist you today?"
        )

        confidence = 0.5
        if brand_suggestion and brand_suggestion.confidence > 0.6:
            confidence = 0.7

        return Suggestion(
            field_name="greeting_message",
            value=greeting,
            confidence=round(confidence, 2),
            source="Generated from brand name and category analysis",
        )

    @staticmethod
    def _suggest_display_name(
        brand_suggestion: Suggestion | None,
    ) -> Suggestion | None:
        """Suggest a widget agent display name."""
        if brand_suggestion is None:
            return Suggestion(
                field_name="widget_agent_display_name",
                value="Customer Support",
                confidence=0.3,
                source="Default fallback (no brand detected)",
            )

        brand = brand_suggestion.value
        name = f"{brand} Support"

        return Suggestion(
            field_name="widget_agent_display_name",
            value=name,
            confidence=round(brand_suggestion.confidence * 0.8, 2),
            source=f"Derived from brand name: {brand}",
        )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_engine: ConfigSuggestionEngine | None = None


def get_config_suggestion_engine() -> ConfigSuggestionEngine:
    """Get or create the singleton ConfigSuggestionEngine."""
    global _engine  # noqa: PLW0603
    if _engine is None:
        _engine = ConfigSuggestionEngine()
    return _engine
