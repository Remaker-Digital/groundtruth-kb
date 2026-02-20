"""Tests for KA-3: Category Template Loader.

Validates template JSON files, registry, TemplateLoader class methods,
apply_template with mock repositories, and configuration suggestions.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from src.multi_tenant.template_loader import (
    TemplateLoader,
    get_template_loader,
    _TEMPLATES_DIR,
    _REGISTRY_FILE,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EXPECTED_CATEGORIES = [
    "apparel_fashion",
    "beauty_cosmetics",
    "electronics_gadgets",
    "home_garden",
    "food_beverage",
    "health_wellness",
    "jewelry_accessories",
    "sports_outdoors",
    "toys_games",
    "pet_supplies",
]

REQUIRED_ARTICLE_FIELDS = {"entry_type", "title", "content", "category", "tags"}
VALID_ENTRY_TYPES = {"faq", "policy", "glossary", "article"}
REQUIRED_CONFIG_SUGGESTION_FIELDS = {"brand_voice", "escalation_keywords", "greeting_message"}


@pytest.fixture
def loader():
    """Fresh TemplateLoader instance (no caching from prior tests)."""
    return TemplateLoader()


# ---------------------------------------------------------------------------
# Class 1: Registry validation
# ---------------------------------------------------------------------------

class TestRegistryValidation:
    """Validate _registry.json structure and contents."""

    def test_registry_file_exists(self):
        assert _REGISTRY_FILE.exists(), "_registry.json must exist"

    def test_registry_is_valid_json(self):
        data = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        assert isinstance(data, list)

    def test_registry_has_ten_categories(self):
        data = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        assert len(data) == 10

    def test_registry_category_ids_match_expected(self):
        data = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        ids = [entry["id"] for entry in data]
        assert sorted(ids) == sorted(EXPECTED_CATEGORIES)

    def test_registry_entries_have_required_fields(self):
        data = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        required = {"id", "name", "description", "article_count",
                     "suggested_brand_voice", "suggested_escalation_keywords"}
        for entry in data:
            missing = required - set(entry.keys())
            assert not missing, f"Registry entry {entry.get('id')} missing: {missing}"

    def test_registry_article_counts_are_positive(self):
        data = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        for entry in data:
            assert entry["article_count"] > 0, f"{entry['id']} has 0 articles"

    def test_registry_escalation_keywords_are_lists(self):
        data = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        for entry in data:
            assert isinstance(entry["suggested_escalation_keywords"], list)
            assert len(entry["suggested_escalation_keywords"]) >= 3, (
                f"{entry['id']} needs ≥3 escalation keywords"
            )


# ---------------------------------------------------------------------------
# Class 2: Template JSON file validation (per category)
# ---------------------------------------------------------------------------

class TestTemplateFiles:
    """Validate each category template JSON file."""

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_file_exists(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        assert path.exists(), f"Template file missing: {category_id}.json"

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_is_valid_json(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_has_matching_id(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["id"] == category_id

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_has_version(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "version" in data
        assert isinstance(data["version"], int)
        assert data["version"] >= 1

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_has_articles(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        articles = data.get("articles", [])
        assert len(articles) >= 10, f"{category_id} has {len(articles)} articles (need ≥10)"

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_articles_have_required_fields(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, article in enumerate(data["articles"]):
            missing = REQUIRED_ARTICLE_FIELDS - set(article.keys())
            assert not missing, (
                f"{category_id} article[{i}] ({article.get('title', '?')}) missing: {missing}"
            )

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_articles_have_valid_entry_types(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for article in data["articles"]:
            assert article["entry_type"] in VALID_ENTRY_TYPES, (
                f"{category_id}: invalid entry_type '{article['entry_type']}' "
                f"in article '{article['title']}'"
            )

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_articles_have_minimum_content_length(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for article in data["articles"]:
            assert len(article["content"]) >= 100, (
                f"{category_id}: article '{article['title']}' content too short "
                f"({len(article['content'])} chars, need ≥100)"
            )

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_articles_have_nonempty_tags(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for article in data["articles"]:
            assert isinstance(article["tags"], list)
            assert len(article["tags"]) >= 1, (
                f"{category_id}: article '{article['title']}' has no tags"
            )

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_has_config_suggestions(self, category_id: str):
        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        suggestions = data.get("config_suggestions", {})
        assert isinstance(suggestions, dict), f"{category_id} config_suggestions not a dict"
        missing = REQUIRED_CONFIG_SUGGESTION_FIELDS - set(suggestions.keys())
        assert not missing, f"{category_id} config_suggestions missing: {missing}"

    @pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
    def test_template_article_count_matches_registry(self, category_id: str):
        registry = json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        reg_entry = next((e for e in registry if e["id"] == category_id), None)
        assert reg_entry is not None

        path = _TEMPLATES_DIR / f"{category_id}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        actual_count = len(data.get("articles", []))
        assert actual_count == reg_entry["article_count"], (
            f"{category_id}: registry says {reg_entry['article_count']} articles "
            f"but template has {actual_count}"
        )


# ---------------------------------------------------------------------------
# Class 3: TemplateLoader.list_categories()
# ---------------------------------------------------------------------------

class TestListCategories:
    """Test the list_categories method."""

    def test_returns_list(self, loader: TemplateLoader):
        cats = loader.list_categories()
        assert isinstance(cats, list)

    def test_returns_ten_categories(self, loader: TemplateLoader):
        cats = loader.list_categories()
        assert len(cats) == 10

    def test_category_ids_match(self, loader: TemplateLoader):
        cats = loader.list_categories()
        ids = [c["id"] for c in cats]
        assert sorted(ids) == sorted(EXPECTED_CATEGORIES)

    def test_caches_after_first_load(self, loader: TemplateLoader):
        cats1 = loader.list_categories()
        cats2 = loader.list_categories()
        assert cats1 is cats2, "list_categories() should return cached list"


# ---------------------------------------------------------------------------
# Class 4: TemplateLoader.get_template()
# ---------------------------------------------------------------------------

class TestGetTemplate:
    """Test the get_template method."""

    def test_returns_dict_for_valid_category(self, loader: TemplateLoader):
        result = loader.get_template("apparel_fashion")
        assert isinstance(result, dict)
        assert result["id"] == "apparel_fashion"

    def test_returns_none_for_unknown_category(self, loader: TemplateLoader):
        result = loader.get_template("nonexistent_category")
        assert result is None

    def test_caches_template_after_first_load(self, loader: TemplateLoader):
        t1 = loader.get_template("apparel_fashion")
        t2 = loader.get_template("apparel_fashion")
        assert t1 is t2, "get_template() should return cached template"

    def test_template_contains_articles(self, loader: TemplateLoader):
        result = loader.get_template("electronics_gadgets")
        assert "articles" in result
        assert len(result["articles"]) >= 10


# ---------------------------------------------------------------------------
# Class 5: TemplateLoader.get_config_suggestions()
# ---------------------------------------------------------------------------

class TestGetConfigSuggestions:
    """Test the get_config_suggestions method."""

    def test_returns_dict_for_valid_category(self, loader: TemplateLoader):
        suggestions = loader.get_config_suggestions("apparel_fashion")
        assert isinstance(suggestions, dict)

    def test_contains_required_fields(self, loader: TemplateLoader):
        suggestions = loader.get_config_suggestions("beauty_cosmetics")
        for field in REQUIRED_CONFIG_SUGGESTION_FIELDS:
            assert field in suggestions, f"Missing config suggestion: {field}"

    def test_brand_voice_is_string(self, loader: TemplateLoader):
        suggestions = loader.get_config_suggestions("electronics_gadgets")
        assert isinstance(suggestions["brand_voice"], str)
        assert len(suggestions["brand_voice"]) > 0

    def test_escalation_keywords_is_list(self, loader: TemplateLoader):
        suggestions = loader.get_config_suggestions("home_garden")
        assert isinstance(suggestions["escalation_keywords"], list)
        assert len(suggestions["escalation_keywords"]) >= 3

    def test_greeting_message_is_string(self, loader: TemplateLoader):
        suggestions = loader.get_config_suggestions("food_beverage")
        assert isinstance(suggestions["greeting_message"], str)
        assert len(suggestions["greeting_message"]) > 10

    def test_returns_empty_dict_for_unknown_category(self, loader: TemplateLoader):
        suggestions = loader.get_config_suggestions("nonexistent")
        assert suggestions == {}


# ---------------------------------------------------------------------------
# Class 6: TemplateLoader.apply_template() (mocked repo)
# ---------------------------------------------------------------------------

class TestApplyTemplate:
    """Test apply_template with mocked KnowledgeBaseRepository and vectorizer."""

    @pytest.mark.asyncio
    async def test_apply_creates_articles(self, loader: TemplateLoader):
        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock()
        mock_repo.read = AsyncMock(return_value=MagicMock())

        mock_vectorizer = MagicMock()
        mock_vectorizer.embed_batch = AsyncMock()

        with patch(
            "src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            result = await loader.apply_template("tenant-1", "apparel_fashion")

        assert result["articles_created"] >= 10
        assert result["articles_failed"] == 0
        assert result["total_chars"] > 0
        assert len(result["entry_ids"]) == result["articles_created"]
        assert "config_suggestions" in result

    @pytest.mark.asyncio
    async def test_apply_raises_for_unknown_category(self, loader: TemplateLoader):
        with pytest.raises(ValueError, match="Template not found"):
            await loader.apply_template("tenant-1", "nonexistent")

    @pytest.mark.asyncio
    async def test_apply_handles_article_creation_failure(self, loader: TemplateLoader):
        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock(side_effect=Exception("Cosmos error"))

        with patch(
            "src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository",
            return_value=mock_repo,
        ):
            result = await loader.apply_template("tenant-1", "apparel_fashion")

        assert result["articles_created"] == 0
        assert result["articles_failed"] >= 10
        assert len(result["entry_ids"]) == 0

    @pytest.mark.asyncio
    async def test_apply_handles_vectorization_failure_gracefully(
        self, loader: TemplateLoader
    ):
        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock()
        mock_repo.read = AsyncMock(return_value=MagicMock())

        mock_vectorizer = MagicMock()
        mock_vectorizer.embed_batch = AsyncMock(side_effect=Exception("Embed error"))

        with patch(
            "src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            # Should NOT raise — vectorization failure is non-fatal
            result = await loader.apply_template("tenant-1", "apparel_fashion")

        assert result["articles_created"] >= 10

    @pytest.mark.asyncio
    async def test_apply_sets_template_metadata(self, loader: TemplateLoader):
        created_docs = []
        mock_repo = AsyncMock()

        async def capture_create(tid, doc):
            created_docs.append(doc)

        mock_repo.create = AsyncMock(side_effect=capture_create)
        mock_repo.read = AsyncMock(return_value=MagicMock())

        mock_vectorizer = MagicMock()
        mock_vectorizer.embed_batch = AsyncMock()

        with patch(
            "src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            await loader.apply_template("tenant-1", "apparel_fashion")

        assert len(created_docs) >= 10
        doc = created_docs[0]
        assert doc.tenant_id == "tenant-1"
        assert doc.metadata["template_source"] == "apparel_fashion"
        assert doc.metadata["template_version"] == 1
        assert doc.source_type == "template"
        assert doc.status == "published"
        assert doc.is_active is True
        assert doc.language == "en"

    @pytest.mark.asyncio
    async def test_apply_returns_config_suggestions(self, loader: TemplateLoader):
        mock_repo = AsyncMock()
        mock_repo.create = AsyncMock()
        mock_repo.read = AsyncMock(return_value=MagicMock())

        mock_vectorizer = MagicMock()
        mock_vectorizer.embed_batch = AsyncMock()

        with patch(
            "src.multi_tenant.repositories.knowledge.KnowledgeBaseRepository",
            return_value=mock_repo,
        ), patch(
            "src.multi_tenant.knowledge_vectorizer.get_knowledge_vectorizer",
            return_value=mock_vectorizer,
        ):
            result = await loader.apply_template("tenant-1", "beauty_cosmetics")

        suggestions = result["config_suggestions"]
        assert isinstance(suggestions, dict)
        assert "brand_voice" in suggestions


# ---------------------------------------------------------------------------
# Class 7: Singleton accessor
# ---------------------------------------------------------------------------

class TestSingleton:
    """Test get_template_loader singleton."""

    def test_returns_template_loader(self):
        loader = get_template_loader()
        assert isinstance(loader, TemplateLoader)

    def test_returns_same_instance(self):
        loader1 = get_template_loader()
        loader2 = get_template_loader()
        assert loader1 is loader2


# ---------------------------------------------------------------------------
# Class 8: Edge cases and content quality
# ---------------------------------------------------------------------------

class TestContentQuality:
    """Validate content quality across all templates."""

    def test_all_article_titles_are_unique_within_template(self, loader: TemplateLoader):
        for cat_id in EXPECTED_CATEGORIES:
            template = loader.get_template(cat_id)
            titles = [a["title"] for a in template["articles"]]
            assert len(titles) == len(set(titles)), (
                f"{cat_id}: duplicate article titles found"
            )

    def test_total_article_count_is_150(self, loader: TemplateLoader):
        """10 categories × 15 articles = 150 total."""
        total = 0
        for cat_id in EXPECTED_CATEGORIES:
            template = loader.get_template(cat_id)
            total += len(template["articles"])
        assert total == 150, f"Expected 150 total articles, got {total}"

    def test_all_categories_have_faq_articles(self, loader: TemplateLoader):
        for cat_id in EXPECTED_CATEGORIES:
            template = loader.get_template(cat_id)
            faq_count = sum(1 for a in template["articles"] if a["entry_type"] == "faq")
            assert faq_count >= 5, f"{cat_id} has only {faq_count} FAQ articles (need ≥5)"

    def test_all_categories_have_policy_articles(self, loader: TemplateLoader):
        for cat_id in EXPECTED_CATEGORIES:
            template = loader.get_template(cat_id)
            policy_count = sum(
                1 for a in template["articles"] if a["entry_type"] == "policy"
            )
            assert policy_count >= 2, (
                f"{cat_id} has only {policy_count} policy articles (need ≥2)"
            )

    def test_no_empty_tags(self, loader: TemplateLoader):
        for cat_id in EXPECTED_CATEGORIES:
            template = loader.get_template(cat_id)
            for article in template["articles"]:
                for tag in article["tags"]:
                    assert isinstance(tag, str)
                    assert len(tag.strip()) > 0, (
                        f"{cat_id}: empty tag in article '{article['title']}'"
                    )

    def test_categories_are_nonempty_strings(self, loader: TemplateLoader):
        for cat_id in EXPECTED_CATEGORIES:
            template = loader.get_template(cat_id)
            for article in template["articles"]:
                assert isinstance(article["category"], str)
                assert len(article["category"].strip()) > 0


# ---------------------------------------------------------------------------
# Class 9: _load_registry error handling
# ---------------------------------------------------------------------------

class TestRegistryErrorHandling:
    """Test error handling for registry loading."""

    def test_load_registry_with_missing_file(self, tmp_path):
        """If _registry.json doesn't exist, list_categories returns []."""
        loader = TemplateLoader()
        # Override the cached path to a non-existent file
        import src.multi_tenant.template_loader as mod

        original_file = mod._REGISTRY_FILE
        try:
            mod._REGISTRY_FILE = tmp_path / "missing.json"
            loader._registry_cache = None
            cats = loader.list_categories()
            assert cats == []
        finally:
            mod._REGISTRY_FILE = original_file

    def test_load_registry_with_invalid_json(self, tmp_path):
        """If _registry.json is invalid JSON, list_categories returns []."""
        bad_file = tmp_path / "_registry.json"
        bad_file.write_text("not valid json {{{", encoding="utf-8")

        loader = TemplateLoader()
        import src.multi_tenant.template_loader as mod

        original_file = mod._REGISTRY_FILE
        try:
            mod._REGISTRY_FILE = bad_file
            loader._registry_cache = None
            cats = loader.list_categories()
            assert cats == []
        finally:
            mod._REGISTRY_FILE = original_file

    def test_get_template_with_invalid_json(self, tmp_path):
        """If a template file is invalid JSON, get_template returns None."""
        import src.multi_tenant.template_loader as mod

        original_dir = mod._TEMPLATES_DIR
        try:
            mod._TEMPLATES_DIR = tmp_path
            bad_file = tmp_path / "bad_template.json"
            bad_file.write_text("{not valid", encoding="utf-8")

            loader = TemplateLoader()
            result = loader.get_template("bad_template")
            assert result is None
        finally:
            mod._TEMPLATES_DIR = original_dir
