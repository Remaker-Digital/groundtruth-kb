# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Knowledge Base vectorization and hybrid retrieval pipeline.

Work Items #209-213 (Decision RAG-1): Enterprise-grade RAG for the
merchant Knowledge Base. Extends the proven Layer 2 vectorization
pattern (conversation_vectorizer.py) to KB entries.

Capabilities:
    1. Embed KB entries on create/update (async, idempotent)
    2. Batch embedding for bulk imports
    3. Vector search via Cosmos DB DiskANN index
    4. BM25 keyword scoring for hybrid retrieval
    5. Reciprocal Rank Fusion (RRF) combining vector + BM25
    6. Retrieval quality metrics and logging
    7. Content hash tracking to detect changes needing re-embedding

Architecture references:
    - Decision RAG-1: Extend Layer 2 vectorization to KB
    - Decision #29: DiskANN, 3072 dimensions, cosine similarity
    - conversation_vectorizer.py: Proven embedding pattern
    - RAG-GAP-ANALYSIS.md: Full gap analysis and work items

Dependencies:
    - cosmos_schema.py: KnowledgeBaseDocument, VECTOR_DIMENSIONS
    - repository.py: KnowledgeBaseRepository (vector_search, list_unembedded)
    - openai: AsyncAzureOpenAI (text-embedding-3-large)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import math
import re
import time
from collections import Counter
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Embedding model (same as Layer 2 — Decision #29)
EMBEDDING_MODEL = "text-embedding-3-large"
EMBEDDING_DIMENSIONS = 3072

# Characters-to-tokens approximation (English text)
CHARS_PER_TOKEN = 4

# Retrieval defaults
DEFAULT_TOP_K = 5
MAX_TOP_K = 20

# Hybrid retrieval parameters
DEFAULT_RRF_K = 60  # RRF smoothing constant (standard value)
DEFAULT_VECTOR_WEIGHT = 0.7  # Weight for vector results in hybrid
DEFAULT_BM25_WEIGHT = 0.3  # Weight for BM25 results in hybrid

# BM25 parameters
BM25_K1 = 1.5  # Term frequency saturation
BM25_B = 0.75  # Document length normalization

# Batch embedding limits
MAX_BATCH_SIZE = 50  # Max entries per embedding API call
MAX_CONTENT_CHARS = 8000  # Max chars per entry for embedding (avoid token limits)

# Retrieval quality thresholds
MIN_RELEVANCE_SCORE = 0.1  # Minimum score to include in results
HIGH_RELEVANCE_SCORE = 0.7  # Score indicating strong match


# ---------------------------------------------------------------------------
# Content hashing
# ---------------------------------------------------------------------------


def compute_content_hash(title: str, content: str) -> str:
    """Compute SHA-256 hash of title+content for change detection.

    Used to determine if an entry's content has changed since last
    embedding, avoiding unnecessary re-embedding API calls.
    """
    combined = f"{title}\n---\n{content}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# BM25 scoring (WI #212)
# ---------------------------------------------------------------------------


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for BM25.

    Lowercase, strip punctuation, filter tokens < 2 chars.
    """
    text = text.lower()
    tokens = re.findall(r"\b[a-z0-9]+\b", text)
    return [t for t in tokens if len(t) >= 2]


def _compute_idf(
    term: str,
    doc_frequencies: dict[str, int],
    total_docs: int,
) -> float:
    """Compute Inverse Document Frequency for a term.

    Uses smoothed IDF: log((N - df + 0.5) / (df + 0.5) + 1)
    """
    df = doc_frequencies.get(term, 0)
    return math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)


def bm25_score(
    query_tokens: list[str],
    doc_tokens: list[str],
    doc_frequencies: dict[str, int],
    total_docs: int,
    avg_doc_len: float,
    k1: float = BM25_K1,
    b: float = BM25_B,
) -> float:
    """Compute BM25 relevance score for a document given a query.

    Args:
        query_tokens: Tokenized query.
        doc_tokens: Tokenized document.
        doc_frequencies: Term -> document count mapping.
        total_docs: Total number of documents.
        avg_doc_len: Average document length in tokens.
        k1: Term frequency saturation parameter.
        b: Document length normalization parameter.

    Returns:
        BM25 score (higher = more relevant).
    """
    if not query_tokens or not doc_tokens or avg_doc_len == 0:
        return 0.0

    doc_len = len(doc_tokens)
    tf_map = Counter(doc_tokens)
    score = 0.0

    for term in query_tokens:
        if term not in tf_map:
            continue

        tf = tf_map[term]
        idf = _compute_idf(term, doc_frequencies, total_docs)

        # BM25 TF component with length normalization
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * doc_len / avg_doc_len)
        score += idf * numerator / denominator

    return score


def compute_bm25_scores(
    query: str,
    entries: list[dict[str, Any]],
) -> list[tuple[str, float]]:
    """Compute BM25 scores for all entries against a query.

    Args:
        query: Search query string.
        entries: List of KB entry dicts with 'id', 'title', 'content', 'tags'.

    Returns:
        List of (entry_id, bm25_score) tuples, sorted by score descending.
    """
    if not entries:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    # Tokenize all documents (title + tags + content)
    doc_token_lists: list[list[str]] = []
    for entry in entries:
        title = entry.get("title", "")
        content = entry.get("content", "")
        tags = " ".join(entry.get("tags", []))
        # Weight title 3x by repeating tokens (simple title boosting)
        doc_text = f"{title} {title} {title} {tags} {tags} {content}"
        doc_token_lists.append(_tokenize(doc_text))

    # Compute document frequencies
    doc_frequencies: dict[str, int] = Counter()
    for tokens in doc_token_lists:
        unique_terms = set(tokens)
        for term in unique_terms:
            doc_frequencies[term] += 1

    total_docs = len(entries)
    avg_doc_len = sum(len(t) for t in doc_token_lists) / total_docs if total_docs > 0 else 0

    # Score each document
    results: list[tuple[str, float]] = []
    for i, entry in enumerate(entries):
        score = bm25_score(
            query_tokens=query_tokens,
            doc_tokens=doc_token_lists[i],
            doc_frequencies=doc_frequencies,
            total_docs=total_docs,
            avg_doc_len=avg_doc_len,
        )
        results.append((entry.get("id", ""), score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Reciprocal Rank Fusion (WI #212)
# ---------------------------------------------------------------------------


def reciprocal_rank_fusion(
    vector_results: list[dict[str, Any]],
    bm25_results: list[tuple[str, float]],
    *,
    k: int = DEFAULT_RRF_K,
    vector_weight: float = DEFAULT_VECTOR_WEIGHT,
    bm25_weight: float = DEFAULT_BM25_WEIGHT,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """Combine vector and BM25 results using Reciprocal Rank Fusion.

    RRF formula: score(d) = sum(weight / (k + rank_i(d)))

    Args:
        vector_results: Results from vector search with 'id' and 'similarity'.
        bm25_results: Results from BM25 as (id, score) tuples.
        k: Smoothing constant (standard: 60).
        vector_weight: Weight for vector search ranks.
        bm25_weight: Weight for BM25 ranks.
        top_k: Number of results to return.

    Returns:
        Fused results sorted by combined RRF score, each dict containing
        the original entry data plus 'rrf_score', 'vector_rank',
        'bm25_rank', 'vector_similarity', and 'bm25_score'.
    """
    # Build lookup maps
    rrf_scores: dict[str, float] = {}
    entry_data: dict[str, dict[str, Any]] = {}
    vector_ranks: dict[str, int] = {}
    vector_similarities: dict[str, float] = {}
    bm25_ranks: dict[str, int] = {}
    bm25_scores_map: dict[str, float] = {}

    # Vector search RRF contribution
    for rank, result in enumerate(vector_results, start=1):
        entry_id = result.get("id", "")
        if not entry_id:
            continue
        rrf_scores[entry_id] = rrf_scores.get(entry_id, 0.0) + vector_weight / (k + rank)
        entry_data[entry_id] = result
        vector_ranks[entry_id] = rank
        vector_similarities[entry_id] = result.get("similarity", 0.0)

    # BM25 RRF contribution
    for rank, (entry_id, score) in enumerate(bm25_results, start=1):
        if not entry_id or score <= 0:
            continue
        rrf_scores[entry_id] = rrf_scores.get(entry_id, 0.0) + bm25_weight / (k + rank)
        bm25_ranks[entry_id] = rank
        bm25_scores_map[entry_id] = score

    # Normalize RRF scores to [0, 1] by dividing by theoretical maximum.
    # The maximum raw RRF score occurs when a document is ranked #1 in both
    # systems: max_rrf = (vector_weight + bm25_weight) / (k + 1).
    # After normalization, rank 1 in both → 1.0, rank 1 in vector only → ~0.7.
    max_rrf = (vector_weight + bm25_weight) / (k + 1)
    if max_rrf > 0:
        for entry_id in rrf_scores:
            rrf_scores[entry_id] /= max_rrf

    # Sort by RRF score
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)

    # Build output
    fused: list[dict[str, Any]] = []
    for entry_id in sorted_ids[:top_k]:
        result = dict(entry_data.get(entry_id, {"id": entry_id}))
        result["rrf_score"] = round(rrf_scores[entry_id], 6)
        result["vector_rank"] = vector_ranks.get(entry_id)
        result["bm25_rank"] = bm25_ranks.get(entry_id)
        result["vector_similarity"] = vector_similarities.get(entry_id)
        result["bm25_score"] = bm25_scores_map.get(entry_id)
        fused.append(result)

    return fused


# ---------------------------------------------------------------------------
# KnowledgeVectorizer
# ---------------------------------------------------------------------------


class KnowledgeVectorizer:
    """Knowledge Base vectorization and hybrid retrieval service.

    Provides:
        1. embed_entry() — Vectorize a single KB entry
        2. embed_batch() — Vectorize multiple entries
        3. search() — Hybrid search (vector + BM25 with RRF)
        4. search_vector_only() — Pure vector search
        5. needs_reembedding() — Check if content changed
        6. embed_unembedded() — Background job: embed entries missing vectors

    Usage:
        vectorizer = get_knowledge_vectorizer()
        vectorizer.configure(kb_repo=repo, openai_client=client)

        # On KB entry create/update:
        await vectorizer.embed_entry(tenant_id, entry_doc)

        # During conversation pipeline:
        results = await vectorizer.search(tenant_id, query)
    """

    def __init__(self) -> None:
        self._kb_repo: Any = None  # KnowledgeBaseRepository
        self._openai_client: Any = None  # AsyncAzureOpenAI
        self._configured: bool = False
        self._metrics: RetrievalMetrics = RetrievalMetrics()
        self._cache: Any = None  # SemanticCache (lazy import)

    def configure(
        self,
        kb_repo: Any,
        openai_client: Any = None,
    ) -> None:
        """Inject dependencies.

        Args:
            kb_repo: KnowledgeBaseRepository instance.
            openai_client: AsyncAzureOpenAI for embeddings.
        """
        self._kb_repo = kb_repo
        self._openai_client = openai_client
        self._configured = True
        logger.info("KnowledgeVectorizer configured")

    def _get_cache(self) -> Any:
        """Lazy-load the SemanticCache singleton."""
        if self._cache is None:
            from src.multi_tenant.semantic_cache import get_semantic_cache
            self._cache = get_semantic_cache()
        return self._cache

    def _ensure_configured(self) -> None:
        if not self._configured:
            raise RuntimeError(
                "KnowledgeVectorizer not configured. "
                "Call vectorizer.configure() first."
            )

    @property
    def metrics(self) -> RetrievalMetrics:
        """Access retrieval quality metrics."""
        return self._metrics

    # ------------------------------------------------------------------
    # Embedding
    # ------------------------------------------------------------------

    async def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts.

        Falls back to zero vectors in dev mode when no client is
        configured (allows testing without API calls).
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
            logger.error("KB embedding API call failed: %s", exc)
            raise

    def _prepare_embedding_text(self, entry: dict[str, Any]) -> str:
        """Prepare text for embedding from a KB entry.

        Combines title, tags, and content into a single string
        optimized for semantic search. Title is weighted by
        appearing first (positional importance in embeddings).
        """
        title = entry.get("title", "")
        tags = ", ".join(entry.get("tags", []))
        content = entry.get("content", "")
        entry_type = entry.get("entry_type", "")

        parts = [f"[{entry_type.upper()}] {title}"]
        if tags:
            parts.append(f"Tags: {tags}")
        if content:
            # Truncate content to avoid token limit issues
            truncated = content[:MAX_CONTENT_CHARS]
            if len(content) > MAX_CONTENT_CHARS:
                truncated = truncated.rsplit(" ", 1)[0] + "..."
            parts.append(truncated)

        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Entry embedding (WI #210)
    # ------------------------------------------------------------------

    async def embed_entry(
        self,
        tenant_id: str,
        entry: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Embed a single KB entry and update it in Cosmos DB.

        Skips embedding if:
            - Entry is not active
            - Content has not changed since last embedding (content_hash match)

        Args:
            tenant_id: Tenant partition key.
            entry: KB entry dict (from repository).

        Returns:
            Updated entry dict, or None if skipped.
        """
        self._ensure_configured()

        entry_id = entry.get("id", "")

        # Skip inactive entries
        if not entry.get("is_active", True):
            logger.debug("Skipping embedding for inactive entry %s", entry_id)
            return None

        # Check content hash — skip if unchanged
        title = entry.get("title", "")
        content = entry.get("content", "")
        current_hash = compute_content_hash(title, content)
        stored_hash = entry.get("content_hash")

        if stored_hash == current_hash and entry.get("embedding"):
            logger.debug(
                "Skipping embedding for entry %s — content unchanged", entry_id,
            )
            return None

        # Prepare and embed
        embed_text = self._prepare_embedding_text(entry)
        embeddings = await self._embed_texts([embed_text])
        embedding = embeddings[0]

        # Update entry with embedding
        now = datetime.now(UTC).isoformat()
        operations = [
            {"op": "set", "path": "/embedding", "value": embedding},
            {"op": "set", "path": "/embedding_model", "value": EMBEDDING_MODEL},
            {"op": "set", "path": "/embedded_at", "value": now},
            {"op": "set", "path": "/content_hash", "value": current_hash},
        ]

        result = await self._kb_repo.patch(
            tenant_id=tenant_id,
            document_id=entry_id,
            operations=operations,
        )

        logger.info(
            "Embedded KB entry: id=%s tenant=%s model=%s",
            entry_id, tenant_id[:8], EMBEDDING_MODEL,
        )

        # Invalidate search/response caches for this tenant (WI #223)
        cache = self._get_cache()
        cache.invalidate_tenant(tenant_id)

        return result

    async def embed_batch(
        self,
        tenant_id: str,
        entries: list[dict[str, Any]],
    ) -> int:
        """Embed multiple KB entries in batches.

        Args:
            tenant_id: Tenant partition key.
            entries: List of KB entry dicts to embed.

        Returns:
            Number of entries successfully embedded.
        """
        self._ensure_configured()

        if not entries:
            return 0

        # Filter to entries that need embedding
        to_embed: list[dict[str, Any]] = []
        for entry in entries:
            if not entry.get("is_active", True):
                continue
            title = entry.get("title", "")
            content = entry.get("content", "")
            current_hash = compute_content_hash(title, content)
            if entry.get("content_hash") == current_hash and entry.get("embedding"):
                continue
            to_embed.append(entry)

        if not to_embed:
            logger.info("No entries need embedding for tenant=%s", tenant_id[:8])
            return 0

        embedded_count = 0

        # Process in batches
        for batch_start in range(0, len(to_embed), MAX_BATCH_SIZE):
            batch = to_embed[batch_start:batch_start + MAX_BATCH_SIZE]

            # Prepare texts
            texts = [self._prepare_embedding_text(e) for e in batch]

            try:
                embeddings = await self._embed_texts(texts)
            except Exception as exc:
                logger.error(
                    "Batch embedding failed at offset %d: %s",
                    batch_start, exc,
                )
                continue

            # Update each entry
            now = datetime.now(UTC).isoformat()
            for entry, embedding in zip(batch, embeddings):
                entry_id = entry.get("id", "")
                title = entry.get("title", "")
                content = entry.get("content", "")
                content_hash = compute_content_hash(title, content)

                try:
                    await self._kb_repo.patch(
                        tenant_id=tenant_id,
                        document_id=entry_id,
                        operations=[
                            {"op": "set", "path": "/embedding", "value": embedding},
                            {"op": "set", "path": "/embedding_model", "value": EMBEDDING_MODEL},
                            {"op": "set", "path": "/embedded_at", "value": now},
                            {"op": "set", "path": "/content_hash", "value": content_hash},
                        ],
                    )
                    embedded_count += 1
                except Exception as exc:
                    logger.error(
                        "Failed to update entry %s with embedding: %s",
                        entry_id, exc,
                    )

        logger.info(
            "Batch embedding complete: %d/%d entries for tenant=%s",
            embedded_count, len(to_embed), tenant_id[:8],
        )

        return embedded_count

    async def embed_unembedded(self, tenant_id: str) -> int:
        """Background job: embed all entries that lack embeddings.

        Queries for active entries without embeddings and processes
        them in batches. Suitable for scheduled execution.

        Args:
            tenant_id: Tenant partition key.

        Returns:
            Number of entries embedded.
        """
        self._ensure_configured()

        entries = await self._kb_repo.list_unembedded(tenant_id)
        if not entries:
            return 0

        logger.info(
            "Found %d unembedded entries for tenant=%s",
            len(entries), tenant_id[:8],
        )

        return await self.embed_batch(tenant_id, entries)

    # ------------------------------------------------------------------
    # Change detection
    # ------------------------------------------------------------------

    def needs_reembedding(self, entry: dict[str, Any]) -> bool:
        """Check if a KB entry's content has changed since last embedding.

        Args:
            entry: KB entry dict.

        Returns:
            True if the entry needs re-embedding.
        """
        if not entry.get("embedding"):
            return True

        stored_hash = entry.get("content_hash")
        if not stored_hash:
            return True

        title = entry.get("title", "")
        content = entry.get("content", "")
        current_hash = compute_content_hash(title, content)

        return current_hash != stored_hash

    # ------------------------------------------------------------------
    # Hybrid search (WI #211 + #212)
    # ------------------------------------------------------------------

    async def search(
        self,
        tenant_id: str,
        query: str,
        *,
        top_k: int = DEFAULT_TOP_K,
        entry_type: str | None = None,
        language: str | None = None,
        vector_weight: float = DEFAULT_VECTOR_WEIGHT,
        bm25_weight: float = DEFAULT_BM25_WEIGHT,
    ) -> list[dict[str, Any]]:
        """Hybrid search combining vector similarity and BM25 via RRF.

        This is the primary retrieval method used by the chat pipeline.
        Combines semantic understanding (vector search) with lexical
        matching (BM25) using Reciprocal Rank Fusion.

        Args:
            tenant_id: Tenant partition key.
            query: Search query (customer message).
            top_k: Number of results to return.
            entry_type: Optional filter by entry type.
            language: Optional filter by language.
            vector_weight: RRF weight for vector results (default 0.7).
            bm25_weight: RRF weight for BM25 results (default 0.3).

        Returns:
            List of KB entries with retrieval metadata (rrf_score,
            vector_similarity, bm25_score, vector_rank, bm25_rank).
        """
        self._ensure_configured()

        start_time = time.monotonic()
        top_k = min(max(top_k, 1), MAX_TOP_K)
        cache = self._get_cache()

        # Cache check: exact-match search results (WI #224)
        cached_results = cache.get_search_results(
            tenant_id, query, top_k, entry_type, language,
        )
        if cached_results is not None:
            elapsed_ms = (time.monotonic() - start_time) * 1000
            self._metrics.record_search(
                tenant_id=tenant_id,
                query=query,
                result_count=len(cached_results),
                latency_ms=elapsed_ms,
                mode="cache_hit",
                top_score=cached_results[0]["rrf_score"] if cached_results else 0.0,
            )
            logger.debug(
                "KB search cache hit: tenant=%s latency=%.0fms query='%s'",
                tenant_id[:8], elapsed_ms, query[:80],
            )
            return cached_results

        # Parallel: vector search + BM25 scoring
        # Vector search needs embedding, BM25 needs document list
        # We fetch a wider candidate set for both to improve fusion quality
        candidate_k = min(top_k * 3, MAX_TOP_K)

        # Step 1: Embed query (check embedding cache first — WI #223)
        query_embedding: list[float] | None = None
        try:
            cached_emb = cache.get_embedding(tenant_id, query)
            if cached_emb is not None:
                query_embedding = cached_emb
            else:
                query_embedding = (await self._embed_texts([query]))[0]
                cache.put_embedding(tenant_id, query, query_embedding)
        except Exception as exc:
            logger.warning(
                "Query embedding failed, falling back to BM25-only: %s", exc,
            )
            query_embedding = None

        # Semantic cache check: find similar queries with cached results
        if query_embedding is not None:
            semantic_results = cache.get_semantic_search_results(
                tenant_id, query_embedding, top_k,
            )
            if semantic_results is not None:
                elapsed_ms = (time.monotonic() - start_time) * 1000
                self._metrics.record_search(
                    tenant_id=tenant_id,
                    query=query,
                    result_count=len(semantic_results),
                    latency_ms=elapsed_ms,
                    mode="semantic_cache_hit",
                    top_score=semantic_results[0]["rrf_score"] if semantic_results else 0.0,
                )
                logger.debug(
                    "KB semantic cache hit: tenant=%s latency=%.0fms query='%s'",
                    tenant_id[:8], elapsed_ms, query[:80],
                )
                return semantic_results

        # Steps 2+3: Vector search and BM25 scoring run in PARALLEL
        # (they are independent — vector needs embedding, BM25 needs doc list)

        async def _do_vector_search() -> list[dict[str, Any]]:
            if not query_embedding:
                return []
            try:
                return await self._kb_repo.vector_search(
                    tenant_id=tenant_id,
                    embedding=query_embedding,
                    top_k=candidate_k,
                    entry_type=entry_type,
                    language=language,
                )
            except Exception as exc:
                logger.warning("Vector search failed: %s", exc)
                return []

        async def _do_bm25_search() -> tuple[list[tuple[str, float]], list[dict]]:
            try:
                entries = await self._kb_repo.list_active_lightweight(
                    tenant_id=tenant_id,
                    entry_type=entry_type,
                    language=language,
                )
                if entries:
                    scores = compute_bm25_scores(query, entries)
                    return scores[:candidate_k], entries
                return [], entries or []
            except Exception as exc:
                logger.warning("BM25 scoring failed: %s", exc)
                return [], []

        vector_results, (bm25_results, all_entries) = await asyncio.gather(
            _do_vector_search(),
            _do_bm25_search(),
        )

        # Step 4: Fuse results via RRF
        if vector_results and bm25_results:
            fused = reciprocal_rank_fusion(
                vector_results=vector_results,
                bm25_results=bm25_results,
                vector_weight=vector_weight,
                bm25_weight=bm25_weight,
                top_k=top_k,
            )
        elif vector_results:
            # Vector-only fallback
            fused = vector_results[:top_k]
            for i, r in enumerate(fused):
                r["rrf_score"] = r.get("similarity", 0.0)
                r["vector_rank"] = i + 1
                r["bm25_rank"] = None
                r["vector_similarity"] = r.get("similarity", 0.0)
                r["bm25_score"] = None
        elif bm25_results:
            # BM25-only fallback (when vector search is unavailable)
            # Normalize BM25 scores to [0, 1] relative to the top score
            # so that MIN_RELEVANCE_SCORE threshold works consistently.
            entry_map = {e.get("id", ""): e for e in (all_entries or [])}
            max_bm25 = bm25_results[0][1] if bm25_results else 1.0
            if max_bm25 <= 0:
                max_bm25 = 1.0
            fused = []
            for entry_id, score in bm25_results[:top_k]:
                entry = entry_map.get(entry_id, {"id": entry_id})
                entry["rrf_score"] = score / max_bm25
                entry["vector_rank"] = None
                entry["bm25_rank"] = bm25_results.index((entry_id, score)) + 1
                entry["vector_similarity"] = None
                entry["bm25_score"] = score
                fused.append(entry)
        else:
            fused = []

        # Step 5: Record metrics
        elapsed_ms = (time.monotonic() - start_time) * 1000
        self._metrics.record_search(
            tenant_id=tenant_id,
            query=query,
            result_count=len(fused),
            latency_ms=elapsed_ms,
            mode="hybrid" if (vector_results and bm25_results) else
                  "vector" if vector_results else
                  "bm25" if bm25_results else "empty",
            top_score=fused[0]["rrf_score"] if fused else 0.0,
        )

        logger.info(
            "KB search: tenant=%s results=%d latency=%.0fms mode=%s "
            "top_score=%.4f query='%s'",
            tenant_id[:8],
            len(fused),
            elapsed_ms,
            "hybrid" if (vector_results and bm25_results) else "vector-only" if vector_results else "bm25-only",
            fused[0]["rrf_score"] if fused else 0.0,
            query[:80],
        )

        # Step 6: Cache results for future queries (WI #223-224)
        if fused:
            cache.put_search_results(
                tenant_id, query, fused, top_k, entry_type, language,
            )
            if query_embedding is not None:
                cache.put_semantic_search_results(
                    tenant_id, query, query_embedding, fused,
                    top_k, entry_type, language,
                )

        return fused

    async def search_vector_only(
        self,
        tenant_id: str,
        query: str,
        *,
        top_k: int = DEFAULT_TOP_K,
        entry_type: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """Pure vector search without BM25 fusion.

        Useful when lexical matching is less important (e.g., semantic
        similarity for recommendation or clustering).

        Args:
            tenant_id: Tenant partition key.
            query: Search query.
            top_k: Number of results.
            entry_type: Optional filter.
            language: Optional filter.

        Returns:
            List of entries with similarity scores.
        """
        self._ensure_configured()

        top_k = min(max(top_k, 1), MAX_TOP_K)

        query_embedding = (await self._embed_texts([query]))[0]

        results = await self._kb_repo.vector_search(
            tenant_id=tenant_id,
            embedding=query_embedding,
            top_k=top_k,
            entry_type=entry_type,
            language=language,
        )

        return results

    # ------------------------------------------------------------------
    # Pipeline context formatting
    # ------------------------------------------------------------------

    @staticmethod
    def format_for_pipeline(
        results: list[dict[str, Any]],
        max_chars: int = 4000,
    ) -> dict[str, Any]:
        """Format search results for the chat pipeline.

        Produces the same output structure as
        _call_knowledge_retrieval_direct() in pipeline.py.

        Args:
            results: Search results from search() or search_vector_only().
            max_chars: Max total characters for context string.

        Returns:
            Dict with 'context', 'sources', 'model', 'retrieval_mode'.
        """
        if not results:
            return {
                "context": "",
                "sources": [],
                "model": EMBEDDING_MODEL,
                "retrieval_mode": "none",
            }

        context_parts: list[str] = []
        sources: list[dict[str, Any]] = []
        total_chars = 0

        for result in results:
            title = result.get("title", "Untitled")
            content = result.get("content", "")
            entry_type = result.get("entry_type", "")
            rrf_score = result.get("rrf_score", result.get("similarity", 0.0))

            # Skip low-relevance results
            if rrf_score < MIN_RELEVANCE_SCORE:
                continue

            # Truncate content to fit budget
            available = max_chars - total_chars - 50
            if available <= 0:
                break

            truncated = content[:available]
            if len(content) > available:
                truncated = truncated.rsplit(" ", 1)[0] + "..."

            source_url = result.get("source_url", "")
            url_line = f"\nSource: {source_url}" if source_url else ""
            part = f"[{entry_type.upper()}] {title}{url_line}\n{truncated}"
            context_parts.append(part)
            total_chars += len(part)

            sources.append({
                "id": result.get("id", ""),
                "title": title,
                "score": round(float(rrf_score), 4),
                "type": entry_type,
                "retrieval_mode": _get_result_mode(result),
                "source_url": source_url,
            })

        retrieval_mode = "hybrid"
        if results and results[0].get("bm25_rank") is None:
            retrieval_mode = "vector"
        elif results and results[0].get("vector_rank") is None:
            retrieval_mode = "bm25"

        return {
            "context": "\n\n---\n\n".join(context_parts),
            "sources": sources,
            "model": EMBEDDING_MODEL,
            "retrieval_mode": retrieval_mode,
        }


def _get_result_mode(result: dict[str, Any]) -> str:
    """Determine retrieval mode for a single result."""
    has_vector = result.get("vector_rank") is not None
    has_bm25 = result.get("bm25_rank") is not None
    if has_vector and has_bm25:
        return "hybrid"
    if has_vector:
        return "vector"
    if has_bm25:
        return "bm25"
    return "unknown"


# ---------------------------------------------------------------------------
# Retrieval quality metrics (WI #213)
# ---------------------------------------------------------------------------


class RetrievalMetrics:
    """In-memory retrieval quality metrics collector.

    Tracks search performance for the /ready health endpoint and
    operational dashboards. Metrics are per-process (reset on restart).

    For persistent metrics, use the audit log or Application Insights.
    """

    def __init__(self) -> None:
        self.total_searches: int = 0
        self.total_results: int = 0
        self.empty_searches: int = 0
        self.hybrid_searches: int = 0
        self.vector_only_searches: int = 0
        self.bm25_only_searches: int = 0
        self.total_latency_ms: float = 0.0
        self.max_latency_ms: float = 0.0
        self.high_relevance_count: int = 0  # Results with score > HIGH_RELEVANCE_SCORE
        self._recent_queries: list[dict[str, Any]] = []  # Last 100 queries for debugging
        self._max_recent = 100

    def record_search(
        self,
        tenant_id: str,
        query: str,
        result_count: int,
        latency_ms: float,
        mode: str,
        top_score: float,
    ) -> None:
        """Record metrics for a single search operation.

        mode values: 'hybrid', 'vector', 'bm25', 'empty',
                     'cache_hit', 'semantic_cache_hit'
        """
        self.total_searches += 1
        self.total_results += result_count
        self.total_latency_ms += latency_ms
        self.max_latency_ms = max(self.max_latency_ms, latency_ms)

        if result_count == 0:
            self.empty_searches += 1
        if mode == "hybrid":
            self.hybrid_searches += 1
        elif mode == "vector":
            self.vector_only_searches += 1
        elif mode == "bm25":
            self.bm25_only_searches += 1

        if top_score >= HIGH_RELEVANCE_SCORE:
            self.high_relevance_count += 1

        # Keep recent queries for debugging
        self._recent_queries.append({
            "tenant_id": tenant_id[:8],
            "query": query[:100],
            "result_count": result_count,
            "latency_ms": round(latency_ms, 1),
            "mode": mode,
            "top_score": round(top_score, 4),
            "timestamp": datetime.now(UTC).isoformat(),
        })
        if len(self._recent_queries) > self._max_recent:
            self._recent_queries = self._recent_queries[-self._max_recent:]

    def summary(self) -> dict[str, Any]:
        """Return a summary of retrieval metrics."""
        avg_latency = (
            self.total_latency_ms / self.total_searches
            if self.total_searches > 0 else 0.0
        )
        avg_results = (
            self.total_results / self.total_searches
            if self.total_searches > 0 else 0.0
        )
        empty_rate = (
            self.empty_searches / self.total_searches
            if self.total_searches > 0 else 0.0
        )
        high_relevance_rate = (
            self.high_relevance_count / self.total_searches
            if self.total_searches > 0 else 0.0
        )

        return {
            "total_searches": self.total_searches,
            "avg_results_per_search": round(avg_results, 1),
            "avg_latency_ms": round(avg_latency, 1),
            "max_latency_ms": round(self.max_latency_ms, 1),
            "empty_search_rate": round(empty_rate, 3),
            "high_relevance_rate": round(high_relevance_rate, 3),
            "hybrid_searches": self.hybrid_searches,
            "vector_only_searches": self.vector_only_searches,
            "bm25_only_searches": self.bm25_only_searches,
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_knowledge_vectorizer: KnowledgeVectorizer | None = None


def get_knowledge_vectorizer() -> KnowledgeVectorizer:
    """Get the singleton KnowledgeVectorizer instance."""
    global _knowledge_vectorizer
    if _knowledge_vectorizer is None:
        _knowledge_vectorizer = KnowledgeVectorizer()
    return _knowledge_vectorizer
