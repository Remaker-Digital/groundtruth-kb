"""Conversation vectorization pipeline — Layer 2 memory.

Work Items #87-88 (Decision #29): Post-conversation vectorization and
semantic search over customer conversation history.

Pipeline:
    1. Transcript → chunking (200-300 tokens)
    2. PII tokenization (via PiiScrubber)
    3. Embedding (text-embedding-3-large, 3072 dimensions)
    4. Storage in Cosmos DB with DiskANN vector index
    5. Semantic search at conversation start (parallel query, top-K)
    6. Result compression for ~300 token prompt injection

Tier gating:
    - Starter:      90-day history
    - Professional:  365-day history
    - Enterprise:    unlimited

Consent gating:
    - Layer 2 requires consent_status = GRANTED
    - Denied consent triggers deletion of all vectors for that customer

Architecture references:
    - Decision #29: Layer 2 — Conversation memory (vectorized search)
    - Decision #10: Consent management gating
    - Test cases L2-01 through L2-06

Dependencies:
    - cosmos_schema.py: MemoryVectorDocument, ConsentStatus, TIER_DEFAULTS
    - repository.py: MemoryVectorRepository (vector_search, list_by_conversation)
    - gdpr_services.py: PiiScrubber
    - openai: AsyncAzureOpenAI (text-embedding-3-large)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    MemoryVectorDocument,
    TenantTier,
    TIER_DEFAULTS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Embedding model (Decision #29)
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072

# Chunking parameters
CHUNK_TARGET_TOKENS = 250  # Target tokens per chunk (200-300 range)
CHUNK_MIN_TOKENS = 50  # Minimum chunk size (avoid tiny fragments)
CHUNK_OVERLAP_TOKENS = 30  # Overlap between adjacent chunks for continuity

# Characters-to-tokens approximation (English text)
CHARS_PER_TOKEN = 4

# Search defaults
DEFAULT_TOP_K = 5
MAX_TOP_K = 20

# Prompt injection budget
MAX_HISTORY_TOKENS = 300  # ~300 token budget for Layer 2 injection


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_transcript(
    messages: list[dict[str, Any]],
    target_tokens: int = CHUNK_TARGET_TOKENS,
    min_tokens: int = CHUNK_MIN_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
) -> list[str]:
    """Split a conversation transcript into chunks of ~200-300 tokens.

    Respects message boundaries — never splits mid-message.
    Overlap ensures context continuity between adjacent chunks.

    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        target_tokens: Target chunk size in tokens.
        min_tokens: Minimum chunk size (fragments below this are merged).
        overlap_tokens: Token overlap between consecutive chunks.

    Returns:
        List of chunk text strings, each ~200-300 tokens.
    """
    if not messages:
        return []

    # Build text lines from messages
    lines: list[str] = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if content:
            lines.append(f"{role}: {content}")

    if not lines:
        return []

    target_chars = target_tokens * CHARS_PER_TOKEN
    min_chars = min_tokens * CHARS_PER_TOKEN
    overlap_chars = overlap_tokens * CHARS_PER_TOKEN

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_len = 0

    for line in lines:
        line_len = len(line)

        # If adding this line would exceed target, flush current chunk
        if current_len + line_len > target_chars and current_chunk:
            chunk_text = "\n".join(current_chunk)
            if len(chunk_text) >= min_chars:
                chunks.append(chunk_text)

            # Overlap: carry forward the last portion
            overlap_text = chunk_text[-overlap_chars:] if overlap_chars else ""
            current_chunk = [overlap_text] if overlap_text else []
            current_len = len(overlap_text)

        current_chunk.append(line)
        current_len += line_len

    # Flush remaining
    if current_chunk:
        chunk_text = "\n".join(current_chunk)
        if len(chunk_text) >= min_chars:
            chunks.append(chunk_text)
        elif chunks:
            # Merge tiny remainder into last chunk
            chunks[-1] = chunks[-1] + "\n" + chunk_text

    return chunks


# ---------------------------------------------------------------------------
# ConversationVectorizer
# ---------------------------------------------------------------------------


class ConversationVectorizer:
    """Post-conversation vectorization pipeline (Decision #29).

    Processes completed conversations into searchable vector embeddings
    stored in Cosmos DB with DiskANN index.

    Usage:
        vectorizer = get_vectorizer()
        # After conversation ends:
        await vectorizer.vectorize_conversation(
            tenant_id, customer_id, conversation_id, messages
        )
        # At conversation start:
        results = await vectorizer.search_history(
            tenant_id, customer_id, query, tier
        )
        summary = vectorizer.compress_for_prompt(results)
    """

    def __init__(self) -> None:
        self._vector_repo: Any = None  # MemoryVectorRepository
        self._openai_client: Any = None  # AsyncAzureOpenAI or AsyncOpenAI
        self._pii_scrubber: Any = None  # PiiScrubber
        self._configured: bool = False

    def configure(
        self,
        vector_repo: Any,
        openai_client: Any = None,
        pii_scrubber: Any = None,
    ) -> None:
        """Inject dependencies.

        Args:
            vector_repo: MemoryVectorRepository instance.
            openai_client: AsyncAzureOpenAI or AsyncOpenAI for embeddings.
            pii_scrubber: PiiScrubber for transcript sanitization.
        """
        self._vector_repo = vector_repo
        self._openai_client = openai_client
        self._pii_scrubber = pii_scrubber
        self._configured = True
        logger.info("ConversationVectorizer configured")

    def _ensure_configured(self) -> None:
        if not self._configured:
            raise RuntimeError(
                "ConversationVectorizer not configured. "
                "Call vectorizer.configure() first."
            )

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    async def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Uses text-embedding-3-large (3072 dimensions) via Azure OpenAI
        or OpenAI API.

        Falls back to zero vectors in dev mode when no client is
        configured (allows testing pipeline without API calls).
        """
        if not self._openai_client:
            logger.warning(
                "No OpenAI client configured — returning zero vectors "
                "(DEVELOPMENT MODE)"
            )
            return [[0.0] * EMBEDDING_DIMENSIONS for _ in texts]

        try:
            response = await self._openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts,
                dimensions=EMBEDDING_DIMENSIONS,
            )
            return [item.embedding for item in response.data]
        except Exception as exc:
            logger.error("Embedding API call failed: %s", exc)
            raise

    async def _embed_single(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        results = await self._embed_texts([text])
        return results[0]

    # ------------------------------------------------------------------
    # Vectorization pipeline (WI #87)
    # ------------------------------------------------------------------

    async def vectorize_conversation(
        self,
        tenant_id: str,
        customer_id: str,
        conversation_id: str,
        messages: list[dict[str, Any]],
        *,
        language: str = "en",
        topics: list[str] | None = None,
        consent_status: ConsentStatus = ConsentStatus.GRANTED,
    ) -> list[str]:
        """Vectorize a completed conversation transcript.

        Pipeline:
            1. Check consent (must be GRANTED)
            2. Chunk transcript (200-300 tokens per chunk)
            3. PII-scrub each chunk
            4. Generate embeddings (text-embedding-3-large, 3072d)
            5. Store MemoryVectorDocuments in Cosmos DB

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.
            conversation_id: Source conversation ID.
            messages: Conversation messages [{role, content, timestamp}].
            language: Transcript language (ISO 639-1).
            topics: Optional pre-extracted topics for filtering.
            consent_status: Customer consent (must be GRANTED).

        Returns:
            List of stored chunk IDs.

        Raises:
            ValueError: If consent is not GRANTED.
        """
        self._ensure_configured()

        # Consent gate (Decision #10)
        if consent_status != ConsentStatus.GRANTED:
            logger.info(
                "Skipping vectorization: consent=%s tenant=%s customer=%s",
                consent_status.value, tenant_id, customer_id,
            )
            return []

        # Step 1: Chunk
        chunks = chunk_transcript(messages)
        if not chunks:
            logger.debug(
                "No chunks produced from conversation %s", conversation_id,
            )
            return []

        # Step 2: PII scrub
        if self._pii_scrubber:
            chunks = [self._pii_scrubber.scrub_text(chunk) for chunk in chunks]

        # Step 3: Embed
        embeddings = await self._embed_texts(chunks)

        # Step 4: Store
        now = datetime.now(timezone.utc).isoformat()
        conversation_date = now  # Use current time as conversation date
        # Try to extract from first message timestamp
        if messages and messages[0].get("timestamp"):
            conversation_date = messages[0]["timestamp"]

        chunk_ids: list[str] = []
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{conversation_id}:chunk-{idx}"
            # ADR-004: Populate canonical_customer_id for new vectors.
            canonical_cid = customer_id if customer_id.startswith("cid_") else None
            doc = MemoryVectorDocument(
                id=chunk_id,
                tenant_id=tenant_id,
                customer_id=customer_id,
                canonical_customer_id=canonical_cid,
                conversation_id=conversation_id,
                chunk_text=chunk_text,
                chunk_index=idx,
                embedding=embedding,
                language=language,
                topics=topics or [],
                created_at=now,
                conversation_date=conversation_date,
            )

            await self._vector_repo.upsert(tenant_id, doc)
            chunk_ids.append(chunk_id)

        logger.info(
            "Vectorized conversation: %s (%d chunks) tenant=%s customer=%s",
            conversation_id, len(chunk_ids), tenant_id, customer_id,
        )

        return chunk_ids

    async def delete_conversation_vectors(
        self,
        tenant_id: str,
        conversation_id: str,
    ) -> int:
        """Delete all vector chunks for a conversation.

        Used by GDPR deletion and consent revocation.
        """
        self._ensure_configured()
        count = await self._vector_repo.delete_by_conversation(
            tenant_id, conversation_id,
        )
        logger.info(
            "Deleted %d vectors for conversation %s", count, conversation_id,
        )
        return count

    # ------------------------------------------------------------------
    # Semantic search (WI #88)
    # ------------------------------------------------------------------

    async def search_history(
        self,
        tenant_id: str,
        customer_id: str,
        query: str,
        tier: TenantTier,
        *,
        top_k: int = DEFAULT_TOP_K,
        consent_status: ConsentStatus = ConsentStatus.GRANTED,
    ) -> list[dict[str, Any]]:
        """Search customer conversation history via vector similarity.

        Called at conversation start to retrieve relevant prior context.
        Results are tier-gated by history depth (Starter 90d,
        Professional 365d, Enterprise unlimited).

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.
            query: The customer's initial message or query text.
            tier: Tenant tier (for history depth gating).
            top_k: Number of results (default 5, max 20).
            consent_status: Customer consent (must be GRANTED).

        Returns:
            List of matching chunks with similarity scores.
        """
        self._ensure_configured()

        # Consent gate
        if consent_status != ConsentStatus.GRANTED:
            return []

        # Enforce top_k bounds
        top_k = min(max(top_k, 1), MAX_TOP_K)

        # Compute history depth cutoff
        since = self._compute_since_date(tier)

        # Embed query
        query_embedding = await self._embed_single(query)

        # Vector search
        results = await self._vector_repo.vector_search(
            tenant_id=tenant_id,
            embedding=query_embedding,
            customer_id=customer_id,
            top_k=top_k,
            since=since,
        )

        logger.debug(
            "History search: tenant=%s customer=%s results=%d tier=%s",
            tenant_id, customer_id, len(results), tier.value,
        )

        return results

    # ------------------------------------------------------------------
    # Prompt compression (WI #88 — result formatting)
    # ------------------------------------------------------------------

    @staticmethod
    def compress_for_prompt(
        results: list[dict[str, Any]],
        max_tokens: int = MAX_HISTORY_TOKENS,
    ) -> str:
        """Compress search results into a ~300 token prompt section.

        Takes the top-K results from vector search and formats them
        into a concise context block for SystemPromptBuilder injection.

        Args:
            results: Vector search results with chunk_text and similarity.
            max_tokens: Maximum token budget for the section.

        Returns:
            Formatted string for prompt injection, or empty string
            if no results.
        """
        if not results:
            return ""

        max_chars = max_tokens * CHARS_PER_TOKEN
        lines = ["CONVERSATION HISTORY (relevant prior interactions):"]
        total_chars = len(lines[0])

        for result in results:
            chunk_text = result.get("chunk_text", "")
            conv_date = result.get("conversation_date", "")
            similarity = result.get("similarity", 0)

            # Format: [date] (sim=0.xx) summary_text
            date_prefix = f"[{conv_date[:10]}]" if conv_date else ""
            sim_prefix = f"(rel={similarity:.2f})" if similarity else ""

            # Truncate chunk text to fit budget
            available = max_chars - total_chars - 50  # Reserve for prefix
            if available <= 0:
                break

            truncated = chunk_text[:available]
            if len(chunk_text) > available:
                truncated = truncated.rsplit(" ", 1)[0] + "..."

            line = f"- {date_prefix} {sim_prefix} {truncated}".strip()
            lines.append(line)
            total_chars += len(line)

            if total_chars >= max_chars:
                break

        if len(lines) <= 1:
            return ""

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Tier-based history depth
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_since_date(tier: TenantTier) -> str | None:
        """Compute the history depth cutoff date for a tier.

        Returns:
            ISO 8601 date string, or None for unlimited (Enterprise).
        """
        from src.multi_tenant.entitlement_service import get_entitlement_service
        defaults = get_entitlement_service().get_tier_config_sync(tier.value)
        depth_days = defaults.get("history_depth_days")

        if depth_days is None:
            return None  # Unlimited

        cutoff = datetime.now(timezone.utc) - timedelta(days=depth_days)
        return cutoff.isoformat()


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_vectorizer: ConversationVectorizer | None = None


def get_vectorizer() -> ConversationVectorizer:
    """Get the singleton ConversationVectorizer instance."""
    global _vectorizer
    if _vectorizer is None:
        _vectorizer = ConversationVectorizer()
    return _vectorizer
