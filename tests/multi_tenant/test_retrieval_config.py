"""
Tests for RAG Phase 1: retrieval tuning, intent-to-source routing,
and source citation in responses.

Covers:
  - PreferencesDocument retrieval fields (schema)
  - Config processor passthrough (_PREFS_DIRECT_FIELDS)
  - Pipeline retrieval parameter wiring
  - Intent-to-source routing (entry_type filter)
  - Minimum relevance score filtering
  - Cite sources in response toggle
  - Config field definitions in tenant_config_schema.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.multi_tenant.cosmos_schema import PreferencesDocument


# ---------------------------------------------------------------------------
# Schema tests: PreferencesDocument retrieval fields
# ---------------------------------------------------------------------------


class TestPreferencesDocumentRetrievalFields:
    """Verify retrieval tuning fields exist on PreferencesDocument."""

    def test_retrieval_top_k_default_none(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01"
        )
        assert doc.retrieval_top_k is None

    def test_retrieval_top_k_set(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            retrieval_top_k=10,
        )
        assert doc.retrieval_top_k == 10

    def test_retrieval_vector_weight_default_none(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01"
        )
        assert doc.retrieval_vector_weight is None

    def test_retrieval_vector_weight_set(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            retrieval_vector_weight=0.5,
        )
        assert doc.retrieval_vector_weight == 0.5

    def test_retrieval_bm25_weight_default_none(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01"
        )
        assert doc.retrieval_bm25_weight is None

    def test_retrieval_min_score_default_none(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01"
        )
        assert doc.retrieval_min_score is None

    def test_retrieval_min_score_set(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            retrieval_min_score=0.3,
        )
        assert doc.retrieval_min_score == 0.3

    def test_intent_source_mapping_default_none(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01"
        )
        assert doc.intent_source_mapping is None

    def test_intent_source_mapping_set(self):
        mapping = {"refund": "policy", "product_info": "product"}
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            intent_source_mapping=mapping,
        )
        assert doc.intent_source_mapping == mapping

    def test_cite_sources_default_false(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01"
        )
        assert doc.cite_sources_in_response is False

    def test_cite_sources_set_true(self):
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            cite_sources_in_response=True,
        )
        assert doc.cite_sources_in_response is True

    def test_all_retrieval_fields_in_serialization(self):
        """All new fields survive dict roundtrip."""
        doc = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            retrieval_top_k=8,
            retrieval_vector_weight=0.6,
            retrieval_bm25_weight=0.4,
            retrieval_min_score=0.2,
            intent_source_mapping={"shipping": "faq"},
            cite_sources_in_response=True,
        )
        data = doc.model_dump()
        assert data["retrieval_top_k"] == 8
        assert data["retrieval_vector_weight"] == 0.6
        assert data["retrieval_bm25_weight"] == 0.4
        assert data["retrieval_min_score"] == 0.2
        assert data["intent_source_mapping"] == {"shipping": "faq"}
        assert data["cite_sources_in_response"] is True


# ---------------------------------------------------------------------------
# Config processor tests: passthrough fields
# ---------------------------------------------------------------------------


class TestConfigProcessorPassthrough:
    """Verify retrieval fields are in _PREFS_DIRECT_FIELDS."""

    def test_retrieval_fields_in_direct_fields(self):
        from src.multi_tenant.tenant_config_processor import _PREFS_DIRECT_FIELDS

        expected = {
            "retrieval_top_k",
            "retrieval_vector_weight",
            "retrieval_bm25_weight",
            "retrieval_min_score",
            "intent_source_mapping",
            "cite_sources_in_response",
        }
        assert expected.issubset(_PREFS_DIRECT_FIELDS)


# ---------------------------------------------------------------------------
# Config schema tests: field definitions
# ---------------------------------------------------------------------------


class TestConfigSchemaRetrievalFields:
    """Verify retrieval tuning fields are defined in the config schema."""

    def test_retrieval_fields_exist_in_schema(self):
        from src.multi_tenant.tenant_config_schema import (
            get_field_registry,
            OnboardingStep,
        )

        fields = list(get_field_registry().values())
        field_names = {f.field_name for f in fields}

        expected = {
            "retrieval_top_k",
            "retrieval_vector_weight",
            "retrieval_bm25_weight",
            "retrieval_min_score",
            "cite_sources_in_response",
            "intent_source_mapping",
        }
        assert expected.issubset(field_names)

    def test_retrieval_fields_in_knowledge_base_step(self):
        from src.multi_tenant.tenant_config_schema import (
            get_field_registry,
            OnboardingStep,
        )

        fields = list(get_field_registry().values())
        kb_fields = [f for f in fields if f.onboarding_step == OnboardingStep.KNOWLEDGE_BASE]
        kb_names = {f.field_name for f in kb_fields}

        assert "retrieval_top_k" in kb_names
        assert "retrieval_vector_weight" in kb_names
        assert "retrieval_bm25_weight" in kb_names
        assert "retrieval_min_score" in kb_names
        assert "cite_sources_in_response" in kb_names
        assert "intent_source_mapping" in kb_names

    def test_intent_source_mapping_professional_tier_gate(self):
        from src.multi_tenant.tenant_config_schema import (
            get_field_registry,
            TierGate,
        )

        fields = list(get_field_registry().values())
        ism = next(f for f in fields if f.field_name == "intent_source_mapping")
        assert ism.tier_gate == TierGate.PROFESSIONAL_PLUS

    def test_retrieval_top_k_validation_range(self):
        from src.multi_tenant.tenant_config_schema import get_field_registry

        fields = list(get_field_registry().values())
        topk = next(f for f in fields if f.field_name == "retrieval_top_k")
        assert topk.validation.min_value == 1
        assert topk.validation.max_value == 20

    def test_weight_fields_validation_range(self):
        from src.multi_tenant.tenant_config_schema import get_field_registry

        fields = list(get_field_registry().values())

        for fname in ("retrieval_vector_weight", "retrieval_bm25_weight", "retrieval_min_score"):
            f = next(fd for fd in fields if fd.field_name == fname)
            assert f.validation.min_value == 0.0, f"{fname} min_value"
            assert f.validation.max_value == 1.0, f"{fname} max_value"


# ---------------------------------------------------------------------------
# Pipeline tests: retrieval param wiring
# ---------------------------------------------------------------------------


class TestPipelineRetrievalParams:
    """Test that pipeline reads retrieval params from preferences."""

    def _make_prefs(self, **overrides):
        defaults = dict(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
        )
        defaults.update(overrides)
        return PreferencesDocument(**defaults)

    @pytest.mark.asyncio
    async def test_pipeline_uses_config_top_k(self):
        """Pipeline passes configured top_k to vectorizer.search()."""
        from src.chat.pipeline import ChatPipeline

        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs(retrieval_top_k=12)

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            result = await pipeline._call_knowledge_retrieval_direct("hello", "general_inquiry", "system")

        mock_vectorizer.search.assert_awaited_once()
        call_kwargs = mock_vectorizer.search.call_args[1]
        assert call_kwargs["top_k"] == 12

    @pytest.mark.asyncio
    async def test_pipeline_uses_config_weights(self):
        """Pipeline passes configured vector/bm25 weights to vectorizer."""
        from src.chat.pipeline import ChatPipeline

        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs(
            retrieval_vector_weight=0.5,
            retrieval_bm25_weight=0.5,
        )

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            result = await pipeline._call_knowledge_retrieval_direct("hello", "general_inquiry", "system")

        call_kwargs = mock_vectorizer.search.call_args[1]
        assert call_kwargs["vector_weight"] == 0.5
        assert call_kwargs["bm25_weight"] == 0.5

    @pytest.mark.asyncio
    async def test_pipeline_clamps_top_k(self):
        """Top K clamped to valid range [1, 20]."""
        from src.chat.pipeline import ChatPipeline

        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs(retrieval_top_k=50)

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            await pipeline._call_knowledge_retrieval_direct("hello", "general_inquiry", "system")

        call_kwargs = mock_vectorizer.search.call_args[1]
        assert call_kwargs["top_k"] == 20

    @pytest.mark.asyncio
    async def test_pipeline_clamps_weight_to_valid_range(self):
        """Weights clamped to [0.0, 1.0]."""
        from src.chat.pipeline import ChatPipeline

        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs(
            retrieval_vector_weight=1.5,
            retrieval_bm25_weight=-0.3,
        )

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            await pipeline._call_knowledge_retrieval_direct("hello", "general_inquiry", "system")

        call_kwargs = mock_vectorizer.search.call_args[1]
        assert call_kwargs["vector_weight"] == 1.0
        assert call_kwargs["bm25_weight"] == 0.0

    @pytest.mark.asyncio
    async def test_pipeline_defaults_when_prefs_none(self):
        """Falls back to hardcoded defaults when no preferences."""
        from src.chat.pipeline import ChatPipeline

        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = None

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            await pipeline._call_knowledge_retrieval_direct("hello", "general_inquiry", "system")

        call_kwargs = mock_vectorizer.search.call_args[1]
        assert call_kwargs["top_k"] == 5
        assert call_kwargs["vector_weight"] == 0.7
        assert call_kwargs["bm25_weight"] == 0.3
        assert call_kwargs.get("entry_type") is None


# ---------------------------------------------------------------------------
# Pipeline tests: intent-to-source routing
# ---------------------------------------------------------------------------


class TestPipelineIntentRouting:
    """Test intent-to-source mapping routes to correct entry_type."""

    def _make_prefs(self, **overrides):
        defaults = dict(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
        )
        defaults.update(overrides)
        return PreferencesDocument(**defaults)

    @pytest.mark.asyncio
    async def test_intent_maps_to_entry_type(self):
        """Known intent maps to configured entry_type filter."""
        from src.chat.pipeline import ChatPipeline

        mapping = {"refund": "policy", "product_info": "product"}
        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs(
            intent_source_mapping=mapping,
        )

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            await pipeline._call_knowledge_retrieval_direct("I want a refund", "refund", "system")

        call_kwargs = mock_vectorizer.search.call_args[1]
        assert call_kwargs["entry_type"] == "policy"

    @pytest.mark.asyncio
    async def test_unknown_intent_no_filter(self):
        """Intent not in mapping → no entry_type filter."""
        from src.chat.pipeline import ChatPipeline

        mapping = {"refund": "policy"}
        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs(
            intent_source_mapping=mapping,
        )

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            await pipeline._call_knowledge_retrieval_direct("hello", "greeting", "system")

        call_kwargs = mock_vectorizer.search.call_args[1]
        assert call_kwargs.get("entry_type") is None

    @pytest.mark.asyncio
    async def test_no_mapping_no_filter(self):
        """No intent_source_mapping → no entry_type filter."""
        from src.chat.pipeline import ChatPipeline

        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs()

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=[])

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            await pipeline._call_knowledge_retrieval_direct("hello", "general_inquiry", "system")

        call_kwargs = mock_vectorizer.search.call_args[1]
        assert call_kwargs.get("entry_type") is None


# ---------------------------------------------------------------------------
# Pipeline tests: minimum score filtering
# ---------------------------------------------------------------------------


class TestPipelineMinScoreFilter:
    """Test that results below min_score are filtered out."""

    def _make_prefs(self, **overrides):
        defaults = dict(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
        )
        defaults.update(overrides)
        return PreferencesDocument(**defaults)

    @pytest.mark.asyncio
    async def test_results_filtered_by_min_score(self):
        """Results below min_score are excluded."""
        from src.chat.pipeline import ChatPipeline

        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs(retrieval_min_score=0.5)

        results = [
            {"title": "High", "content": "good match", "score": 0.8},
            {"title": "Low", "content": "bad match", "score": 0.2},
            {"title": "Medium", "content": "ok match", "score": 0.5},
        ]

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=results)

        captured_results = []

        def mock_format(r):
            captured_results.extend(r)
            return {
                "context": "\n".join(item["content"] for item in r),
                "sources": [{"title": item["title"]} for item in r],
            }

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ), patch(
            "src.multi_tenant.knowledge_vectorizer.KnowledgeVectorizer.format_for_pipeline",
            side_effect=mock_format,
        ):
            result = await pipeline._call_knowledge_retrieval_direct("test", "general", "system")

        # format_for_pipeline receives filtered results (only score >= 0.5)
        assert len(captured_results) == 2  # High (0.8) and Medium (0.5), not Low (0.2)
        titles = [r["title"] for r in captured_results]
        assert "High" in titles
        assert "Medium" in titles
        assert "Low" not in titles

    @pytest.mark.asyncio
    async def test_default_min_score_0_1(self):
        """Default min_score is 0.1 when not configured."""
        from src.chat.pipeline import ChatPipeline

        pipeline = ChatPipeline.__new__(ChatPipeline)
        pipeline._current_tenant_id = "t1"
        pipeline._current_preferences = self._make_prefs()  # no min_score set

        results = [
            {"title": "OK", "content": "match", "score": 0.15},
            {"title": "Bad", "content": "no match", "score": 0.05},
        ]

        mock_vectorizer = MagicMock()
        mock_vectorizer._configured = True
        mock_vectorizer.search = AsyncMock(return_value=results)

        captured_results = []

        def mock_format(r):
            captured_results.extend(r)
            return {"context": "", "sources": []}

        with patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ), patch(
            "src.multi_tenant.knowledge_vectorizer.KnowledgeVectorizer.format_for_pipeline",
            side_effect=mock_format,
        ):
            await pipeline._call_knowledge_retrieval_direct("test", "general", "system")

        assert len(captured_results) == 1  # Only OK (0.15), not Bad (0.05)


# ---------------------------------------------------------------------------
# Source citation tests
# ---------------------------------------------------------------------------


class TestSourceCitation:
    """Test cite_sources_in_response toggle."""

    def test_citation_appended_to_response(self):
        """When cite_sources=True and sources exist, citation line appended."""
        prefs = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            cite_sources_in_response=True,
        )
        safe_text = "Here is your answer about returns."
        sources = [
            {"title": "Return Policy"},
            {"title": "FAQ: Returns"},
        ]

        # Simulate the pipeline logic
        if prefs.cite_sources_in_response and sources:
            source_titles = [s.get("title", "") for s in sources if s.get("title")]
            if source_titles:
                citation_line = "\n\nSources: " + ", ".join(source_titles)
                safe_text = safe_text + citation_line

        assert "Sources: Return Policy, FAQ: Returns" in safe_text
        assert safe_text.startswith("Here is your answer")

    def test_no_citation_when_disabled(self):
        """When cite_sources=False, response unchanged."""
        prefs = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            cite_sources_in_response=False,
        )
        safe_text = "Here is your answer."
        sources = [{"title": "Return Policy"}]

        if prefs.cite_sources_in_response and sources:
            source_titles = [s.get("title", "") for s in sources if s.get("title")]
            if source_titles:
                safe_text = safe_text + "\n\nSources: " + ", ".join(source_titles)

        assert safe_text == "Here is your answer."

    def test_no_citation_when_no_sources(self):
        """When cite_sources=True but no sources, response unchanged."""
        prefs = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            cite_sources_in_response=True,
        )
        safe_text = "Here is your answer."
        sources = []

        if prefs.cite_sources_in_response and sources:
            source_titles = [s.get("title", "") for s in sources if s.get("title")]
            if source_titles:
                safe_text = safe_text + "\n\nSources: " + ", ".join(source_titles)

        assert safe_text == "Here is your answer."

    def test_citation_skips_empty_titles(self):
        """Sources with empty/missing titles are excluded from citation."""
        prefs = PreferencesDocument(
            id="test", tenant_id="t1", version=1, created_at="2026-01-01",
            cite_sources_in_response=True,
        )
        safe_text = "Answer."
        sources = [
            {"title": "Return Policy"},
            {"title": ""},
            {"content": "no title field"},
            {"title": "Shipping FAQ"},
        ]

        if prefs.cite_sources_in_response and sources:
            source_titles = [s.get("title", "") for s in sources if s.get("title")]
            if source_titles:
                safe_text = safe_text + "\n\nSources: " + ", ".join(source_titles)

        assert "Sources: Return Policy, Shipping FAQ" in safe_text
        assert safe_text.count(",") == 1  # Only one comma between two titles
