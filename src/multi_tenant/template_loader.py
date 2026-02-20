"""Category Template Loader (KA-3: Knowledge Automation).

Loads industry-specific knowledge templates from JSON files and applies
them to a tenant's knowledge base. Templates provide starter KB content
(FAQ articles, policy documents, terminology glossaries) and configuration
suggestions tailored to common merchant categories.

Templates are stored as JSON files in src/multi_tenant/knowledge_templates/
and indexed by _registry.json.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import logging
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.multi_tenant.cosmos_schema import KnowledgeBaseDocument

logger = logging.getLogger(__name__)

# Path to the knowledge_templates directory (relative to this module)
_TEMPLATES_DIR = Path(__file__).parent / "knowledge_templates"
_REGISTRY_FILE = _TEMPLATES_DIR / "_registry.json"


class TemplateLoader:
    """Loads and applies industry category templates to merchant KBs.

    Templates are cached in memory after first load. Each template
    contains KB articles and configuration suggestions.

    Usage:
        loader = TemplateLoader()
        categories = loader.list_categories()
        template = loader.get_template("apparel_fashion")
        result = await loader.apply_template("tenant-id", "apparel_fashion")
    """

    def __init__(self) -> None:
        self._registry_cache: list[dict[str, Any]] | None = None
        self._template_cache: dict[str, dict[str, Any]] = {}

    def list_categories(self) -> list[dict[str, Any]]:
        """Return the template registry (category metadata without articles).

        Returns a list of dicts with: id, name, description, article_count,
        suggested_brand_voice, suggested_escalation_keywords.
        """
        if self._registry_cache is None:
            self._registry_cache = self._load_registry()
        return self._registry_cache

    def get_template(self, category_id: str) -> dict[str, Any] | None:
        """Load a full template by category ID (with articles).

        Returns the template dict or None if not found.
        """
        if category_id in self._template_cache:
            return self._template_cache[category_id]

        template_path = _TEMPLATES_DIR / f"{category_id}.json"
        if not template_path.exists():
            logger.warning("Template not found: %s", category_id)
            return None

        try:
            template = json.loads(template_path.read_text(encoding="utf-8"))
            self._template_cache[category_id] = template
            return template
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load template %s: %s", category_id, exc)
            return None

    async def apply_template(
        self,
        tenant_id: str,
        category_id: str,
        *,
        merge_mode: str = "append",
    ) -> dict[str, Any]:
        """Apply a category template to a tenant's knowledge base.

        Args:
            tenant_id: Target tenant ID.
            category_id: Template category to apply.
            merge_mode: "append" (add alongside existing) or "replace"
                        (clear existing articles of matching entry_types first).

        Returns:
            Dict with articles_created, articles_failed, config_suggestions.
        """
        template = self.get_template(category_id)
        if template is None:
            raise ValueError(f"Template not found: {category_id}")

        result = {
            "articles_created": 0,
            "articles_failed": 0,
            "total_chars": 0,
            "entry_ids": [],
            "config_suggestions": template.get("config_suggestions", {}),
        }

        articles = template.get("articles", [])
        if not articles:
            logger.warning("Template %s has no articles", category_id)
            return result

        # Import lazily to avoid circular dependencies
        from src.multi_tenant.repositories.knowledge import KnowledgeBaseRepository

        repo = KnowledgeBaseRepository()
        now = datetime.now(timezone.utc).isoformat()

        for article in articles:
            try:
                entry_id = str(uuid.uuid4())
                doc = KnowledgeBaseDocument(
                    id=entry_id,
                    tenant_id=tenant_id,
                    entry_type=article.get("entry_type", "article"),
                    title=article["title"],
                    content=article["content"],
                    metadata={
                        "template_source": category_id,
                        "template_version": template.get("version", 1),
                    },
                    tags=article.get("tags", []),
                    language="en",
                    category=article.get("category", "General"),
                    status="published",
                    is_active=True,
                    source_type="template",
                    created_at=now,
                    updated_at=now,
                )
                await repo.create(tenant_id, doc)
                result["entry_ids"].append(entry_id)
                result["articles_created"] += 1
                result["total_chars"] += len(article["content"])

            except Exception:
                result["articles_failed"] += 1
                logger.debug(
                    "Failed to create template article: %s",
                    article.get("title", "unknown")[:50],
                    exc_info=True,
                )

        # Vectorize created articles
        if result["entry_ids"]:
            try:
                from src.multi_tenant.knowledge_vectorizer import get_knowledge_vectorizer

                vectorizer = get_knowledge_vectorizer()
                entries = []
                for eid in result["entry_ids"]:
                    try:
                        entry = await repo.read(tenant_id, eid)
                        entries.append(entry)
                    except Exception:
                        pass
                if entries:
                    await vectorizer.embed_batch(tenant_id, entries)
            except Exception:
                logger.warning(
                    "Template vectorization failed for tenant %s (non-fatal)",
                    tenant_id[:8],
                    exc_info=True,
                )

        logger.info(
            "Applied template '%s' to tenant %s: %d articles created, %d failed",
            category_id, tenant_id[:8],
            result["articles_created"], result["articles_failed"],
        )

        return result

    def get_config_suggestions(self, category_id: str) -> dict[str, Any]:
        """Get configuration suggestions for a category without applying articles.

        Returns dict with brand_voice, escalation_keywords, greeting_message.
        """
        template = self.get_template(category_id)
        if template is None:
            return {}
        return template.get("config_suggestions", {})

    @staticmethod
    def _load_registry() -> list[dict[str, Any]]:
        """Load the template registry from _registry.json."""
        try:
            return json.loads(_REGISTRY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load template registry: %s", exc)
            return []


# ---------------------------------------------------------------------------
# Singleton access
# ---------------------------------------------------------------------------

_template_loader: TemplateLoader | None = None


def get_template_loader() -> TemplateLoader:
    """Get or create the singleton TemplateLoader."""
    global _template_loader  # noqa: PLW0603
    if _template_loader is None:
        _template_loader = TemplateLoader()
    return _template_loader
