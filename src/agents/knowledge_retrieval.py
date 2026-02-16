# Agent Red Customer Experience — Knowledge Retrieval Agent
#
# Retrieves relevant knowledge base articles for a customer query using
# hybrid vector + BM25 search with Reciprocal Rank Fusion (RRF).
# Falls back to keyword search if the vectorizer is unavailable.
#
# Extracted from pipeline.py _call_knowledge_retrieval_direct().
#
# Input payload:
#   {"message": str, "intent": str, "system_prompt": str,
#    "tenant_id": str, "preferences": dict (optional)}
#
# Output payload:
#   {"context": str, "sources": [{"id": str, "title": str, ...}],
#    "model": str, "tokens_input": int, "tokens_output": int}
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import logging
import os
from typing import Any

from src.agents.base import AgentRedBaseAgent

logger = logging.getLogger(__name__)

AZURE_EMBEDDING_MODEL = os.environ.get(
    "AZURE_EMBEDDING_MODEL", "text-embedding-3-large"
)

# Stopwords for fallback keyword search
_STOP = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "shall",
    "of", "in", "to", "for", "with", "on", "at", "by", "from",
    "and", "or", "but", "not", "no", "so", "if", "as", "it",
    "its", "this", "that", "what", "which", "who", "how",
    "your", "you", "my", "me", "i", "we", "our", "they",
    "their", "them", "he", "she", "his", "her",
}


class KnowledgeRetrievalAgent(AgentRedBaseAgent):
    """Retrieve relevant knowledge for customer queries.

    Primary path: hybrid vector + BM25 via KnowledgeVectorizer.
    Fallback: keyword overlap search via KnowledgeBaseRepository.
    """

    agent_type = "knowledge-retrieval"

    def __init__(
        self,
        kb_repo: Any = None,
        knowledge_vectorizer: Any = None,
    ) -> None:
        super().__init__()
        self._kb_repo = kb_repo
        self._knowledge_vectorizer = knowledge_vectorizer

    def configure(
        self,
        kb_repo: Any = None,
        knowledge_vectorizer: Any = None,
    ) -> None:
        """Inject dependencies after construction."""
        if kb_repo is not None:
            self._kb_repo = kb_repo
        if knowledge_vectorizer is not None:
            self._knowledge_vectorizer = knowledge_vectorizer
        self._configured = True

    async def process(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Retrieve knowledge for a customer message.

        Tries hybrid vector search first; falls back to keyword search.

        Args:
            payload: {"message": str, "intent": str, "tenant_id": str,
                      "preferences": dict (optional)}
            headers: A2A headers.

        Returns:
            {"context": str, "sources": list, "model": str,
             "tokens_input": int, "tokens_output": int}
        """
        message = payload.get("message", "")
        intent = payload.get("intent", "general_inquiry")
        tenant_id = (
            headers.get("x-tenant-id")
            or payload.get("tenant_id", "")
        )
        prefs = payload.get("preferences", {})

        if not tenant_id:
            return self._empty_result()

        # Try hybrid vector search first
        result = await self._try_hybrid_search(
            tenant_id, message, intent, prefs,
        )
        if result is not None:
            return result

        # Fallback to keyword search
        return await self._keyword_fallback(tenant_id, message)

    async def _try_hybrid_search(
        self,
        tenant_id: str,
        message: str,
        intent: str,
        prefs: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Attempt hybrid vector + BM25 search via KnowledgeVectorizer.

        Returns None if vectorizer is unavailable or fails.
        """
        try:
            from src.multi_tenant.knowledge_vectorizer import (
                KnowledgeVectorizer,
                get_knowledge_vectorizer,
            )

            vectorizer = self._knowledge_vectorizer or get_knowledge_vectorizer()
            if not getattr(vectorizer, "_configured", False):
                raise RuntimeError("KnowledgeVectorizer not configured")

            # Read retrieval params from preferences
            top_k = max(1, min(prefs.get("retrieval_top_k", 5), 20))
            vector_weight = max(0.0, min(prefs.get("retrieval_vector_weight", 0.7), 1.0))
            bm25_weight = max(0.0, min(prefs.get("retrieval_bm25_weight", 0.3), 1.0))
            entry_type = None

            # Intent-to-source routing
            intent_mapping = prefs.get("intent_source_mapping", {})
            if intent_mapping and intent in intent_mapping:
                entry_type = intent_mapping[intent]

            results = await vectorizer.search(
                tenant_id=tenant_id,
                query=message,
                top_k=top_k,
                entry_type=entry_type,
                vector_weight=vector_weight,
                bm25_weight=bm25_weight,
            )

            # Apply minimum relevance score filter
            min_score = max(0.0, min(prefs.get("retrieval_min_score", 0.1), 1.0))
            results = [
                r for r in results
                if r.get("rrf_score", r.get("similarity", r.get("score", 0))) >= min_score
            ]

            formatted = KnowledgeVectorizer.format_for_pipeline(results)

            ctx = formatted.get("context", "")
            src = formatted.get("sources", [])
            logger.info(
                "KR hybrid: %d sources, context_len=%d",
                len(src), len(ctx),
            )

            formatted.setdefault("tokens_input", 0)
            formatted.setdefault("tokens_output", 0)
            formatted.setdefault("model", AZURE_EMBEDDING_MODEL)
            return formatted

        except Exception as exc:
            logger.warning(
                "Hybrid KB retrieval unavailable (%s) — falling back to keyword search",
                exc,
            )
            return None

    async def _keyword_fallback(
        self,
        tenant_id: str,
        message: str,
    ) -> dict[str, Any]:
        """Keyword overlap search using KnowledgeBaseRepository."""
        try:
            kb_repo = self._kb_repo
            if not kb_repo:
                logger.warning("No KnowledgeBaseRepository for fallback")
                return self._empty_result()

            articles = await kb_repo.list_active(tenant_id)
            if not articles:
                logger.info("No active KB articles for tenant %s", tenant_id)
                return self._empty_result()

            query_words = {
                w for w in message.lower().split()
                if w not in _STOP and len(w) > 1
            }
            if not query_words:
                query_words = set(message.lower().split())

            scored: list[tuple[float, dict[str, Any]]] = []
            for article in articles:
                title = (article.get("title") or "").lower()
                content = (article.get("content") or "").lower()
                title_words = {w for w in title.split() if w not in _STOP}
                content_words = set(content.split())

                title_overlap = len(query_words & title_words)
                content_overlap = len(query_words & content_words)
                score = (title_overlap * 3.0 + content_overlap) / max(len(query_words), 1)

                if score > 0:
                    scored.append((score, article))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_results = scored[:5]

            if not top_results:
                top_results = [(0.5, a) for a in articles[:5]]

            context_parts: list[str] = []
            sources: list[dict[str, str]] = []
            for _score, article in top_results:
                title = article.get("title", "Untitled")
                content = article.get("content", "")
                context_parts.append(f"### {title}\n{content}")
                sources.append({
                    "id": article.get("id", ""),
                    "title": title,
                    "entry_type": article.get("entry_type", ""),
                })

            context = "\n\n".join(context_parts)
            logger.info(
                "KR keyword fallback: %d results for tenant %s",
                len(top_results), tenant_id,
            )
            return {
                "context": context,
                "sources": sources,
                "model": "keyword-fallback",
                "tokens_input": 0,
                "tokens_output": 0,
            }

        except Exception as exc:
            logger.warning("KB keyword fallback failed (%s)", exc)
            return self._empty_result()

    @staticmethod
    def _empty_result() -> dict[str, Any]:
        """Return an empty knowledge result."""
        return {
            "context": "",
            "sources": [],
            "model": AZURE_EMBEDDING_MODEL,
            "tokens_input": 0,
            "tokens_output": 0,
        }
