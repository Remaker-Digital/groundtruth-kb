# Agent Red Customer Experience — Co-Pilot Agent (SPEC-1557)
#
# Dedicated handler for admin team member conversations. Retrieves product
# documentation from the shared admin_documentation_vectors collection and
# generates helpful responses about Agent Red administrative features.
#
# Unlike the customer-facing pipeline, the Co-pilot:
#   - Retrieves from a platform-level vector DB (not tenant-scoped KB)
#   - Uses an admin-specific system prompt (no payment disclaimers)
#   - Cites documentation sources in responses
#   - Does not invoke the Critic agent (admin context is trusted)
#
# Input payload:
#   {
#     "message": str,
#     "system_prompt": str,
#     "conversation_history": list[{"role": str, "content": str}],
#     "team_member_role": str,
#     "tenant_id": str
#   }
#
# Output payload:
#   {
#     "response": str,
#     "sources": list[{"id": str, "title": str, "category": str}],
#     "model": str,
#     "tokens_input": int,
#     "tokens_output": int
#   }
#
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from collections import Counter
from typing import Any

from src.agents.base import AgentRedBaseAgent

logger = logging.getLogger(__name__)

AZURE_RG_MODEL = os.environ.get("AZURE_RG_MODEL", "gpt-4o")

# BM25 parameters (matching knowledge_vectorizer.py)
BM25_K1 = 1.5
BM25_B = 0.75
DEFAULT_RRF_K = 60

# Retrieval defaults (used when no CopilotConfigDocument exists — SPEC-1576)
DEFAULT_TOP_K = 5
DEFAULT_VECTOR_WEIGHT = 0.7
DEFAULT_BM25_WEIGHT = 0.3
DEFAULT_MIN_SCORE = 0.1

# Mutable runtime config — populated by configure_copilot_retrieval()
_copilot_retrieval_config: dict[str, Any] = {}


def configure_copilot_retrieval(config: dict[str, Any] | None) -> None:
    """Update retrieval parameters at runtime (SPEC-1576).

    Called by the superadmin API when config is saved. Changes take
    effect on the next query without restart.
    """
    global _copilot_retrieval_config
    _copilot_retrieval_config = config or {}


def _get_retrieval_param(key: str, default: Any) -> Any:
    """Read a retrieval parameter from runtime config or fall back to default."""
    return _copilot_retrieval_config.get(key, default)

# Stop words for BM25 tokenization
_STOP = frozenset(
    "a an the is are was were be been being have has had do does did "
    "will would shall should may might can could of in to for with on "
    "at by from as into through during before after above below between "
    "i me my we our you your he him his she her it its they them their "
    "this that these those and but or nor not so yet".split()
)


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for BM25."""
    tokens = re.findall(r"\b[a-z0-9]+\b", text.lower())
    return [t for t in tokens if len(t) >= 2 and t not in _STOP]


def _bm25_score(
    query_tokens: list[str],
    doc_tokens: list[str],
    doc_frequencies: dict[str, int],
    total_docs: int,
    avg_doc_len: float,
) -> float:
    """Compute BM25 relevance score."""
    if not query_tokens or not doc_tokens or avg_doc_len == 0:
        return 0.0

    import math

    doc_len = len(doc_tokens)
    tf_map = Counter(doc_tokens)
    score = 0.0

    for token in query_tokens:
        if token not in tf_map:
            continue
        tf = tf_map[token]
        df = doc_frequencies.get(token, 0)
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
        numerator = tf * (BM25_K1 + 1)
        denominator = tf + BM25_K1 * (1 - BM25_B + BM25_B * doc_len / avg_doc_len)
        score += idf * numerator / denominator

    return score


class CoPilotAgent(AgentRedBaseAgent):
    """Admin documentation assistant — Co-pilot agent.

    Retrieves from the shared admin_documentation_vectors collection
    and generates responses about Agent Red administrative features.
    Follows the same hybrid vector + BM25 retrieval pattern as the
    KnowledgeRetrievalAgent but operates on platform-level docs.
    """

    agent_type = "co-pilot"

    def __init__(
        self,
        openai_client: Any = None,
        admin_doc_repo: Any = None,
    ) -> None:
        super().__init__()
        self._openai_client = openai_client
        self._admin_doc_repo = admin_doc_repo

    def configure(
        self,
        openai_client: Any,
        admin_doc_repo: Any | None = None,
    ) -> None:
        """Inject dependencies after construction."""
        self._openai_client = openai_client
        if admin_doc_repo is not None:
            self._admin_doc_repo = admin_doc_repo
        self._configured = True

    async def process(
        self,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """Handle an admin documentation query.

        1. Retrieve relevant documentation (hybrid vector + BM25)
        2. Build context from top-K results
        3. Generate a helpful response with source citations

        Args:
            payload: {message, system_prompt, conversation_history,
                      team_member_role, tenant_id}
            headers: A2A headers.

        Returns:
            {response, sources, model, tokens_input, tokens_output}
        """
        message = payload.get("message", "")
        system_prompt = payload.get("system_prompt", "")
        history = payload.get("conversation_history", [])
        role = payload.get("team_member_role", "admin")

        # ── Step 1: Retrieve documentation context ───────────────
        doc_context, sources = await self._retrieve_documentation(message)

        # ── Step 2: Build prompt with documentation context ──────
        effective_prompt = self._build_effective_prompt(
            system_prompt, doc_context, sources, role,
        )

        # ── Step 3: Generate response ────────────────────────────
        if not self._openai_client:
            return {
                "response": (
                    "I'm the Agent Red Co-pilot, but I'm currently unable to "
                    "process your request. Please try again in a moment."
                ),
                "sources": sources,
                "model": AZURE_RG_MODEL,
                "tokens_input": 0,
                "tokens_output": 0,
            }

        # Build messages array with conversation history
        messages: list[dict[str, str]] = [
            {"role": "system", "content": effective_prompt},
        ]
        # Include up to last 10 turns of history for context
        for turn in history[-10:]:
            messages.append({
                "role": turn.get("role", "user"),
                "content": turn.get("content", ""),
            })
        messages.append({"role": "user", "content": message})

        try:
            response = await self._openai_client.chat.completions.create(
                model=AZURE_RG_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )

            content = response.choices[0].message.content or ""
            usage = response.usage

            return {
                "response": content,
                "sources": sources,
                "model": AZURE_RG_MODEL,
                "tokens_input": usage.prompt_tokens if usage else 0,
                "tokens_output": usage.completion_tokens if usage else 0,
            }
        except Exception as exc:
            logger.warning("Co-pilot response generation failed: %s", exc)
            return {
                "response": (
                    "I encountered an issue generating a response. "
                    "Please try rephrasing your question."
                ),
                "sources": sources,
                "model": AZURE_RG_MODEL,
                "tokens_input": 0,
                "tokens_output": 0,
            }

    async def _retrieve_documentation(
        self, query: str,
    ) -> tuple[str, list[dict[str, str]]]:
        """Retrieve relevant documentation using hybrid search.

        Returns (formatted_context, sources_list).
        Falls back to keyword search if vector search is unavailable.
        """
        if not self._admin_doc_repo:
            return "", []

        sources: list[dict[str, str]] = []
        results: list[dict[str, Any]] = []

        # ── Primary: Vector search (cross-partition) ─────────────
        try:
            if self._openai_client:
                embedding_response = await self._openai_client.embeddings.create(
                    model="text-embedding-3-large",
                    input=query,
                    dimensions=3072,
                )
                query_embedding = embedding_response.data[0].embedding

                top_k = _get_retrieval_param("top_k", DEFAULT_TOP_K)
                vector_results = await self._admin_doc_repo.vector_search_all_categories(
                    embedding=query_embedding,
                    top_k=top_k * 2,  # Over-fetch for RRF merge
                )

                # Also do BM25 for hybrid merge
                bm25_results = await self._bm25_search(query, top_k=top_k * 2)

                # Merge via Reciprocal Rank Fusion
                results = self._rrf_merge(vector_results, bm25_results, top_k=top_k)
            else:
                # Keyword-only fallback
                top_k = _get_retrieval_param("top_k", DEFAULT_TOP_K)
                results = await self._bm25_search(query, top_k=top_k)
        except Exception as exc:
            logger.warning("Co-pilot vector search failed, trying keyword: %s", exc)
            try:
                results = await self._bm25_search(
                    query,
                    top_k=_get_retrieval_param("top_k", DEFAULT_TOP_K),
                )
            except Exception:
                return "", []

        if not results:
            return "", []

        # ── Format context ───────────────────────────────────────
        context_parts: list[str] = []
        for i, doc in enumerate(results, 1):
            title = doc.get("title", "Untitled")
            content = doc.get("content", "")
            category = doc.get("document_category", "general")
            section = doc.get("section", "")

            source_label = f"{category}/{section}" if section else category
            context_parts.append(
                f"═══ Source {i}: {title} ({source_label}) ═══\n{content}"
            )
            sources.append({
                "id": doc.get("id", ""),
                "title": title,
                "category": category,
            })

        formatted = "\n\n".join(context_parts)
        return formatted, sources

    async def _bm25_search(
        self, query: str, top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Keyword-based BM25 search across all documentation."""
        all_docs = await self._admin_doc_repo.list_all_lightweight()
        if not all_docs:
            return []

        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        # Build document frequency map
        doc_token_lists = []
        for doc in all_docs:
            tokens = _tokenize(
                f"{doc.get('title', '')} {doc.get('content', '')}"
            )
            doc_token_lists.append(tokens)

        total_docs = len(all_docs)
        avg_doc_len = sum(len(t) for t in doc_token_lists) / max(total_docs, 1)

        # Count document frequencies
        df: dict[str, int] = {}
        for tokens in doc_token_lists:
            for token in set(tokens):
                df[token] = df.get(token, 0) + 1

        # Score each document
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc, tokens in zip(all_docs, doc_token_lists):
            score = _bm25_score(query_tokens, tokens, df, total_docs, avg_doc_len)
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    def _rrf_merge(
        self,
        vector_results: list[dict[str, Any]],
        bm25_results: list[dict[str, Any]],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Merge vector and BM25 results using Reciprocal Rank Fusion."""
        vector_weight = _get_retrieval_param("vector_weight", DEFAULT_VECTOR_WEIGHT)
        bm25_weight = _get_retrieval_param("bm25_weight", DEFAULT_BM25_WEIGHT)
        rrf_k = _get_retrieval_param("rrf_k", DEFAULT_RRF_K)

        scores: dict[str, float] = {}
        doc_map: dict[str, dict[str, Any]] = {}

        for rank, doc in enumerate(vector_results):
            doc_id = doc.get("id", "")
            if not doc_id:
                continue
            scores[doc_id] = scores.get(doc_id, 0) + (
                vector_weight / (rrf_k + rank + 1)
            )
            doc_map[doc_id] = doc

        for rank, doc in enumerate(bm25_results):
            doc_id = doc.get("id", "")
            if not doc_id:
                continue
            scores[doc_id] = scores.get(doc_id, 0) + (
                bm25_weight / (rrf_k + rank + 1)
            )
            if doc_id not in doc_map:
                doc_map[doc_id] = doc

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [doc_map[doc_id] for doc_id, _ in ranked[:top_k] if doc_id in doc_map]

    def _build_effective_prompt(
        self,
        base_prompt: str,
        doc_context: str,
        sources: list[dict[str, str]],
        team_member_role: str,
    ) -> str:
        """Build the effective system prompt with documentation context."""
        parts = [base_prompt]

        if doc_context:
            parts.append(
                "\n\n═══ AGENT RED DOCUMENTATION ═══\n"
                "Use the following documentation to answer the team member's question. "
                "Reference specific sections and provide actionable guidance. "
                "If the documentation doesn't cover their question, say so clearly "
                "and suggest where they might find the answer.\n\n"
                f"{doc_context}"
            )

        parts.append(
            f"\n\nThe team member has the role: {team_member_role}. "
            "Tailor your response to their access level."
        )

        return "\n".join(parts)
