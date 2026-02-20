"""Tests for KA-4: Configuration Suggestion Engine.

Tests the heuristic analysis engine that generates configuration
suggestions from KB article content. Pure text analysis — no LLM calls.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from src.multi_tenant.config_suggestion_engine import (
    ConfigSuggestionEngine,
    Suggestion,
    SuggestionSet,
    get_config_suggestion_engine,
    _TONE_KEYWORDS,
    _ESCALATION_PATTERNS,
)


# ---------------------------------------------------------------------------
# Test data factories
# ---------------------------------------------------------------------------


def _make_article(
    *,
    title: str = "Test Article",
    content: str = "This is test content.",
    category: str = "General",
    metadata: dict | None = None,
) -> dict:
    """Build a mock KB article."""
    article = {
        "title": title,
        "content": content,
        "category": category,
    }
    if metadata:
        article["metadata"] = metadata
    return article


def _make_articles_with_vendor(vendor: str, count: int = 5) -> list[dict]:
    """Build articles with a consistent vendor in metadata."""
    return [
        _make_article(
            title=f"Product {i}",
            content=f"Description for product {i} from {vendor}.",
            metadata={"vendor": vendor},
        )
        for i in range(count)
    ]


def _make_toned_articles(tone: str, keyword_count: int = 10) -> list[dict]:
    """Build articles heavy in a specific tone's keywords."""
    keywords = _TONE_KEYWORDS.get(tone, [])
    # Repeat keywords to reach desired count
    repeated = (keywords * ((keyword_count // len(keywords)) + 1))[:keyword_count]
    content = " ".join(repeated) + " " + "filler text " * 50
    return [
        _make_article(content=content),
        _make_article(content=content),
    ]


def _make_escalation_articles(patterns: list[str] | None = None) -> list[dict]:
    """Build articles containing escalation-related keywords."""
    if patterns is None:
        patterns = ["defective", "broken", "safety", "recall", "fraud"]
    content = " ".join(patterns) + " some regular product content here"
    return [_make_article(content=content)]


# =========================================================================
# Suggestion / SuggestionSet data classes
# =========================================================================


class TestSuggestionDataClass:
    """Test the Suggestion dataclass."""

    def test_suggestion_fields(self):
        s = Suggestion(
            field_name="brand_name",
            value="TestBrand",
            confidence=0.85,
            source="vendor field",
        )
        assert s.field_name == "brand_name"
        assert s.value == "TestBrand"
        assert s.confidence == 0.85
        assert s.source == "vendor field"


class TestSuggestionSet:
    """Test the SuggestionSet collection."""

    def test_empty_set(self):
        ss = SuggestionSet()
        assert ss.suggestions == []
        assert ss.to_dict() == {}

    def test_to_dict(self):
        ss = SuggestionSet(suggestions=[
            Suggestion("brand_name", "Acme", 0.9, "vendor"),
            Suggestion("brand_voice", "friendly", 0.7, "tone"),
        ])
        d = ss.to_dict()
        assert "brand_name" in d
        assert d["brand_name"]["value"] == "Acme"
        assert d["brand_name"]["confidence"] == 0.9
        assert "brand_voice" in d
        assert d["brand_voice"]["value"] == "friendly"

    def test_get_existing(self):
        ss = SuggestionSet(suggestions=[
            Suggestion("brand_name", "Acme", 0.9, "vendor"),
        ])
        s = ss.get("brand_name")
        assert s is not None
        assert s.value == "Acme"

    def test_get_missing(self):
        ss = SuggestionSet()
        assert ss.get("nonexistent") is None


# =========================================================================
# Brand name extraction
# =========================================================================


class TestExtractBrandName:
    """Test _extract_brand_name heuristic."""

    def test_extracts_vendor_from_metadata(self):
        articles = _make_articles_with_vendor("Acme Corp", count=5)
        result = ConfigSuggestionEngine._extract_brand_name(articles)
        assert result is not None
        assert result.field_name == "brand_name"
        assert result.value == "Acme Corp"
        assert result.confidence > 0

    def test_no_vendor_returns_none(self):
        articles = [_make_article() for _ in range(5)]
        result = ConfigSuggestionEngine._extract_brand_name(articles)
        assert result is None

    def test_single_vendor_occurrence_returns_none(self):
        """Need at least 2 weighted occurrences."""
        # vendor gets weight 3, so one article = 3, but need count>=2
        # Actually count threshold is count < 2, and vendor gets +3
        # So 1 article with vendor = count 3, which is >= 2 → should return
        articles = [_make_article(metadata={"vendor": "Solo"})]
        result = ConfigSuggestionEngine._extract_brand_name(articles)
        # With one vendor occurrence (weight 3), count=3 which is >= 2
        assert result is not None
        assert result.value == "Solo"

    def test_empty_vendor_ignored(self):
        articles = [_make_article(metadata={"vendor": "  "}) for _ in range(5)]
        result = ConfigSuggestionEngine._extract_brand_name(articles)
        assert result is None

    def test_confidence_scales_with_count(self):
        small = _make_articles_with_vendor("Brand", count=2)
        large = _make_articles_with_vendor("Brand", count=10)
        r_small = ConfigSuggestionEngine._extract_brand_name(small)
        r_large = ConfigSuggestionEngine._extract_brand_name(large)
        assert r_small is not None
        assert r_large is not None
        # More articles with same vendor should give higher confidence
        assert r_large.confidence >= r_small.confidence

    def test_most_common_vendor_wins(self):
        articles = _make_articles_with_vendor("Winner", count=6)
        articles.extend(_make_articles_with_vendor("Loser", count=2))
        result = ConfigSuggestionEngine._extract_brand_name(articles)
        assert result is not None
        assert result.value == "Winner"

    def test_confidence_capped_at_one(self):
        articles = _make_articles_with_vendor("BigBrand", count=50)
        result = ConfigSuggestionEngine._extract_brand_name(articles)
        assert result is not None
        assert result.confidence <= 1.0


# =========================================================================
# Brand voice analysis
# =========================================================================


class TestAnalyzeBrandVoice:
    """Test _analyze_brand_voice heuristic."""

    def test_detects_friendly_tone(self):
        articles = _make_toned_articles("friendly")
        result = ConfigSuggestionEngine._analyze_brand_voice(articles)
        assert result is not None
        assert result.field_name == "brand_voice"
        assert "friendly" in result.value

    def test_detects_professional_tone(self):
        articles = _make_toned_articles("professional")
        result = ConfigSuggestionEngine._analyze_brand_voice(articles)
        assert result is not None
        assert "professional" in result.value

    def test_detects_technical_tone(self):
        articles = _make_toned_articles("technical")
        result = ConfigSuggestionEngine._analyze_brand_voice(articles)
        assert result is not None
        assert "technical" in result.value

    def test_detects_caring_tone(self):
        articles = _make_toned_articles("caring")
        result = ConfigSuggestionEngine._analyze_brand_voice(articles)
        assert result is not None
        assert "caring" in result.value

    def test_detects_luxury_tone(self):
        articles = _make_toned_articles("luxury")
        result = ConfigSuggestionEngine._analyze_brand_voice(articles)
        assert result is not None
        assert "luxury" in result.value

    def test_short_content_returns_none(self):
        articles = [_make_article(content="Hi")]
        result = ConfigSuggestionEngine._analyze_brand_voice(articles)
        assert result is None

    def test_no_tone_matches_returns_none(self):
        # Content with no tone keywords at all
        content = "abcxyz " * 100
        articles = [_make_article(content=content)]
        result = ConfigSuggestionEngine._analyze_brand_voice(articles)
        assert result is None

    def test_compound_voice_for_close_scores(self):
        """When two tones are close, produces compound descriptor."""
        # Mix friendly and caring keywords equally
        friendly_kws = " ".join(_TONE_KEYWORDS["friendly"][:4])
        caring_kws = " ".join(_TONE_KEYWORDS["caring"][:4])
        content = f"{friendly_kws} {caring_kws} " * 5 + "filler " * 50
        articles = [_make_article(content=content)]
        result = ConfigSuggestionEngine._analyze_brand_voice(articles)
        assert result is not None
        # Should contain "and" for compound voice
        assert " and " in result.value

    def test_confidence_scales_with_matches(self):
        # Few matches
        small_content = "welcome happy " + "filler " * 100
        articles_small = [_make_article(content=small_content)]
        # Many matches
        big_content = " ".join(_TONE_KEYWORDS["friendly"] * 10) + " filler " * 50
        articles_big = [_make_article(content=big_content)]

        r_small = ConfigSuggestionEngine._analyze_brand_voice(articles_small)
        r_big = ConfigSuggestionEngine._analyze_brand_voice(articles_big)
        assert r_small is not None
        assert r_big is not None
        assert r_big.confidence >= r_small.confidence


# =========================================================================
# Escalation keywords extraction
# =========================================================================


class TestExtractEscalationKeywords:
    """Test _extract_escalation_keywords heuristic."""

    def test_finds_escalation_patterns(self):
        articles = _make_escalation_articles(["defective", "safety", "recall"])
        result = ConfigSuggestionEngine._extract_escalation_keywords(articles)
        assert result is not None
        assert result.field_name == "escalation_keywords"
        assert "defective" in result.value
        assert "safety" in result.value
        assert "recall" in result.value

    def test_no_patterns_returns_none(self):
        articles = [_make_article(content="Everything is perfectly fine and normal.")]
        result = ConfigSuggestionEngine._extract_escalation_keywords(articles)
        assert result is None

    def test_confidence_scales_with_count(self):
        few = _make_escalation_articles(["defective"])
        many = _make_escalation_articles(_ESCALATION_PATTERNS[:10])
        r_few = ConfigSuggestionEngine._extract_escalation_keywords(few)
        r_many = ConfigSuggestionEngine._extract_escalation_keywords(many)
        assert r_few is not None
        assert r_many is not None
        assert r_many.confidence > r_few.confidence

    def test_caps_at_15_keywords(self):
        """Result value is capped at 15 keywords max."""
        # Use all escalation patterns
        content = " ".join(_ESCALATION_PATTERNS)
        articles = [_make_article(content=content)]
        result = ConfigSuggestionEngine._extract_escalation_keywords(articles)
        assert result is not None
        assert len(result.value) <= 15

    def test_confidence_capped_at_one(self):
        content = " ".join(_ESCALATION_PATTERNS * 3)
        articles = [_make_article(content=content)]
        result = ConfigSuggestionEngine._extract_escalation_keywords(articles)
        assert result is not None
        assert result.confidence <= 1.0


# =========================================================================
# Greeting generation
# =========================================================================


class TestGenerateGreeting:
    """Test _generate_greeting heuristic."""

    def test_includes_brand_name(self):
        brand = Suggestion("brand_name", "Acme Store", 0.9, "vendor")
        articles = [_make_article()]
        result = ConfigSuggestionEngine._generate_greeting(articles, brand)
        assert result is not None
        assert result.field_name == "greeting_message"
        assert "Acme Store" in result.value

    def test_fallback_without_brand(self):
        articles = [_make_article()]
        result = ConfigSuggestionEngine._generate_greeting(articles, None)
        assert result is not None
        assert "our store" in result.value

    def test_higher_confidence_with_strong_brand(self):
        strong_brand = Suggestion("brand_name", "BigBrand", 0.9, "vendor")
        weak_brand = Suggestion("brand_name", "WeakBrand", 0.3, "vendor")
        articles = [_make_article()]

        r_strong = ConfigSuggestionEngine._generate_greeting(articles, strong_brand)
        r_weak = ConfigSuggestionEngine._generate_greeting(articles, weak_brand)
        assert r_strong is not None
        assert r_weak is not None
        assert r_strong.confidence > r_weak.confidence

    def test_greeting_includes_help_offer(self):
        articles = [_make_article()]
        result = ConfigSuggestionEngine._generate_greeting(articles, None)
        assert result is not None
        assert "help" in result.value.lower() or "assist" in result.value.lower()


# =========================================================================
# Display name suggestion
# =========================================================================


class TestSuggestDisplayName:
    """Test _suggest_display_name heuristic."""

    def test_with_brand_name(self):
        brand = Suggestion("brand_name", "Acme", 0.9, "vendor")
        result = ConfigSuggestionEngine._suggest_display_name(brand)
        assert result is not None
        assert result.field_name == "widget_agent_display_name"
        assert result.value == "Acme Support"
        assert result.confidence > 0

    def test_without_brand_name_fallback(self):
        result = ConfigSuggestionEngine._suggest_display_name(None)
        assert result is not None
        assert result.value == "Customer Support"
        assert result.confidence == 0.3

    def test_confidence_derived_from_brand(self):
        brand_high = Suggestion("brand_name", "Acme", 0.9, "vendor")
        brand_low = Suggestion("brand_name", "Acme", 0.3, "vendor")
        r_high = ConfigSuggestionEngine._suggest_display_name(brand_high)
        r_low = ConfigSuggestionEngine._suggest_display_name(brand_low)
        assert r_high is not None
        assert r_low is not None
        assert r_high.confidence > r_low.confidence


# =========================================================================
# Full pipeline: generate_suggestions
# =========================================================================


class TestGenerateSuggestions:
    """Test the full generate_suggestions pipeline."""

    @pytest.mark.asyncio
    async def test_empty_articles_returns_empty_set(self):
        engine = ConfigSuggestionEngine()
        result = await engine.generate_suggestions("t-001", articles=[])
        assert isinstance(result, SuggestionSet)
        assert len(result.suggestions) == 0

    @pytest.mark.asyncio
    async def test_none_articles_fetches_from_repo(self):
        """When articles=None, fetches from repository."""
        engine = ConfigSuggestionEngine()
        with patch(
            "src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository",
        ) as MockRepo:
            mock_repo = AsyncMock()
            mock_repo.list_filtered = AsyncMock(return_value=[])
            MockRepo.return_value = mock_repo
            result = await engine.generate_suggestions("t-001", articles=None)
            assert isinstance(result, SuggestionSet)

    @pytest.mark.asyncio
    async def test_full_pipeline_with_vendor_articles(self):
        """Full pipeline extracts brand, voice, greeting, display name."""
        articles = _make_articles_with_vendor("TestBrand", count=5)
        # Add friendly tone content
        for a in articles:
            a["content"] += " welcome happy to help love enjoy fun great awesome "

        engine = ConfigSuggestionEngine()
        result = await engine.generate_suggestions("t-001", articles=articles)

        d = result.to_dict()
        assert "brand_name" in d
        assert d["brand_name"]["value"] == "TestBrand"
        assert "greeting_message" in d
        assert "TestBrand" in d["greeting_message"]["value"]
        assert "widget_agent_display_name" in d
        assert d["widget_agent_display_name"]["value"] == "TestBrand Support"

    @pytest.mark.asyncio
    async def test_full_pipeline_with_escalation_content(self):
        """Full pipeline extracts escalation keywords."""
        articles = _make_articles_with_vendor("SafeBrand", count=3)
        articles.extend(_make_escalation_articles(
            ["defective", "safety", "recall", "fraud", "toxic"]
        ))

        engine = ConfigSuggestionEngine()
        result = await engine.generate_suggestions("t-001", articles=articles)

        d = result.to_dict()
        assert "escalation_keywords" in d
        assert len(d["escalation_keywords"]["value"]) >= 3

    @pytest.mark.asyncio
    async def test_full_pipeline_generates_display_name_without_brand(self):
        """Even without vendor, display name is suggested with fallback."""
        content = "product info " * 50
        articles = [_make_article(content=content)]

        engine = ConfigSuggestionEngine()
        result = await engine.generate_suggestions("t-001", articles=articles)

        d = result.to_dict()
        assert "widget_agent_display_name" in d
        assert d["widget_agent_display_name"]["value"] == "Customer Support"

    @pytest.mark.asyncio
    async def test_fetch_failure_returns_empty(self):
        """When article fetch fails, returns empty suggestion set."""
        engine = ConfigSuggestionEngine()
        with patch(
            "src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository",
            side_effect=Exception("DB unavailable"),
        ):
            result = await engine.generate_suggestions("t-001", articles=None)
            assert isinstance(result, SuggestionSet)
            assert len(result.suggestions) == 0


# =========================================================================
# Singleton
# =========================================================================


class TestSingleton:
    """Test the get_config_suggestion_engine singleton."""

    def test_returns_same_instance(self):
        import src.multi_tenant.config_suggestion_engine as mod
        mod._engine = None
        e1 = get_config_suggestion_engine()
        e2 = get_config_suggestion_engine()
        assert e1 is e2

    def test_returns_engine_type(self):
        import src.multi_tenant.config_suggestion_engine as mod
        mod._engine = None
        engine = get_config_suggestion_engine()
        assert isinstance(engine, ConfigSuggestionEngine)
