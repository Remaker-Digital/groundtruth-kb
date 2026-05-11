# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""RAG Configuration — knowledge source management (SPEC-0617, SPEC-0823).

Manages RAG knowledge sources for each tenant, covering:
- Merchant-provided documents (knowledge articles, FAQ, product docs)
- Product documentation (admin guides, API docs)
- Persistent Customer Memory (conversation history, preferences)

Each source type can be independently enabled/disabled and configured
with its own vectorization parameters.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Knowledge source types
# ---------------------------------------------------------------------------

class KnowledgeSourceType(str, Enum):
    """Types of knowledge sources available for RAG."""

    MERCHANT_DOCS = "merchant_docs"        # FAQ, product descriptions, policies
    ADMIN_DOCS = "admin_docs"              # Product documentation for admin UI (SPEC-0617)
    CUSTOMER_MEMORY = "customer_memory"    # Persistent customer memory (SPEC-0823)
    CONVERSATION_HISTORY = "conversation_history"  # Past conversations
    EXTERNAL_INTEGRATION = "external_integration"  # Zendesk, Google Docs, etc.


class VectorIndexStatus(str, Enum):
    """Status of a vector index for a knowledge source."""

    NOT_CONFIGURED = "not_configured"
    INDEXING = "indexing"
    READY = "ready"
    ERROR = "error"
    STALE = "stale"


# ---------------------------------------------------------------------------
# Configuration models
# ---------------------------------------------------------------------------

@dataclass
class KnowledgeSourceConfig:
    """Configuration for a single knowledge source."""

    source_type: KnowledgeSourceType
    enabled: bool = False
    chunk_size: int = 512          # Tokens per chunk
    chunk_overlap: int = 64        # Overlap between chunks
    max_results: int = 5           # Max retrieval results
    similarity_threshold: float = 0.7
    index_status: VectorIndexStatus = VectorIndexStatus.NOT_CONFIGURED
    document_count: int = 0
    last_indexed_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGConfiguration:
    """Full RAG configuration for a tenant (SPEC-0617 + SPEC-0823)."""

    tenant_id: str
    sources: dict[str, KnowledgeSourceConfig] = field(default_factory=dict)
    global_max_context_tokens: int = 4096
    reranking_enabled: bool = True
    citation_enabled: bool = True

    @classmethod
    def default(cls, tenant_id: str) -> RAGConfiguration:
        """Create a default RAG configuration for a new tenant."""
        return cls(
            tenant_id=tenant_id,
            sources={
                KnowledgeSourceType.MERCHANT_DOCS.value: KnowledgeSourceConfig(
                    source_type=KnowledgeSourceType.MERCHANT_DOCS,
                    enabled=True,  # Enabled by default
                    max_results=5,
                ),
                KnowledgeSourceType.ADMIN_DOCS.value: KnowledgeSourceConfig(
                    source_type=KnowledgeSourceType.ADMIN_DOCS,
                    enabled=False,  # Opt-in (SPEC-0617)
                    max_results=3,
                ),
                KnowledgeSourceType.CUSTOMER_MEMORY.value: KnowledgeSourceConfig(
                    source_type=KnowledgeSourceType.CUSTOMER_MEMORY,
                    enabled=False,  # Opt-in (SPEC-0823)
                    max_results=3,
                    similarity_threshold=0.8,
                ),
                KnowledgeSourceType.CONVERSATION_HISTORY.value: KnowledgeSourceConfig(
                    source_type=KnowledgeSourceType.CONVERSATION_HISTORY,
                    enabled=True,
                    max_results=3,
                ),
                KnowledgeSourceType.EXTERNAL_INTEGRATION.value: KnowledgeSourceConfig(
                    source_type=KnowledgeSourceType.EXTERNAL_INTEGRATION,
                    enabled=False,
                    max_results=3,
                ),
            },
        )


# ---------------------------------------------------------------------------
# RAG Configuration Service
# ---------------------------------------------------------------------------

class RAGConfigService:
    """Service for managing per-tenant RAG configurations.

    Reads/writes RAG config as a Cosmos document in the tenant's
    preferences collection.
    """

    def __init__(self) -> None:
        self._cache: dict[str, RAGConfiguration] = {}

    def get_config(self, tenant_id: str) -> RAGConfiguration:
        """Get RAG config for a tenant (from cache or default)."""
        if tenant_id in self._cache:
            return self._cache[tenant_id]
        config = RAGConfiguration.default(tenant_id)
        self._cache[tenant_id] = config
        return config

    def update_source(
        self,
        tenant_id: str,
        source_type: str,
        *,
        enabled: bool | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        max_results: int | None = None,
        similarity_threshold: float | None = None,
    ) -> KnowledgeSourceConfig:
        """Update a specific knowledge source configuration."""
        config = self.get_config(tenant_id)

        if source_type not in config.sources:
            config.sources[source_type] = KnowledgeSourceConfig(
                source_type=KnowledgeSourceType(source_type),
            )

        source = config.sources[source_type]
        if enabled is not None:
            source.enabled = enabled
        if chunk_size is not None:
            source.chunk_size = max(64, min(2048, chunk_size))
        if chunk_overlap is not None:
            source.chunk_overlap = max(0, min(source.chunk_size // 2, chunk_overlap))
        if max_results is not None:
            source.max_results = max(1, min(20, max_results))
        if similarity_threshold is not None:
            source.similarity_threshold = max(0.0, min(1.0, similarity_threshold))

        logger.info(
            "RAG source updated: tenant=%s source=%s enabled=%s",
            tenant_id[:8], source_type, source.enabled,
        )
        return source

    def get_enabled_sources(self, tenant_id: str) -> list[KnowledgeSourceConfig]:
        """Get all enabled knowledge sources for a tenant."""
        config = self.get_config(tenant_id)
        return [s for s in config.sources.values() if s.enabled]

    def is_source_enabled(self, tenant_id: str, source_type: str) -> bool:
        """Check if a specific knowledge source is enabled."""
        config = self.get_config(tenant_id)
        source = config.sources.get(source_type)
        return source.enabled if source else False


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service: RAGConfigService | None = None


def get_rag_config_service() -> RAGConfigService:
    """Get or create the RAG config service singleton."""
    global _service
    if _service is None:
        _service = RAGConfigService()
    return _service
