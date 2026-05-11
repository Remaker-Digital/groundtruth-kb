# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Knowledge Base staleness detection and refresh service (WI #219-222).

Tracks content freshness, computes staleness scores, and triggers
automatic re-embedding for stale entries. Integrates with the
KnowledgeVectorizer for re-embedding operations.

Staleness scoring model:
    - Age factor: days since last update or verification (0.0-0.5)
    - Embedding drift: content changed since last embedding (0.0-0.3)
    - Type weight: products stale faster than policies (multiplier)
    - Verification recency: recent human verification reduces score (0.0-0.2)

Score interpretation:
    - 0.0-0.3: Fresh (no action needed)
    - 0.3-0.6: Aging (review recommended)
    - 0.6-0.8: Stale (refresh recommended)
    - 0.8-1.0: Very stale (auto-refresh triggered if enabled)

Architecture references:
    - RAG-GAP-ANALYSIS.md: WI #219-222 specifications
    - knowledge_vectorizer.py: Re-embedding integration
    - cosmos_schema.py: KnowledgeBaseDocument staleness fields
    - Zendesk AI: Competitive reference for staleness detection

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Staleness thresholds (days)
FRESH_THRESHOLD = 0.3  # Below this score = fresh
AGING_THRESHOLD = 0.6  # Below this score = aging
STALE_THRESHOLD = 0.8  # Below this score = stale, above = very stale

# Default freshness windows by entry type (days).
# Products change frequently (pricing, availability); policies are stable.
DEFAULT_FRESHNESS_WINDOWS: dict[str, int] = {
    "product": 30,   # Products stale after 30 days without verification
    "faq": 60,       # FAQs stale after 60 days
    "policy": 90,    # Policies stale after 90 days
    "custom": 45,    # Custom entries after 45 days
}

# Default freshness window for unknown entry types
DEFAULT_FRESHNESS_DAYS = 60

# Auto re-embedding threshold — entries above this score are re-embedded
AUTO_REEMBED_THRESHOLD = 0.7

# Max entries to re-embed in one batch run
MAX_REEMBED_BATCH = 100


# ---------------------------------------------------------------------------
# Staleness score computation (WI #220)
# ---------------------------------------------------------------------------


def compute_staleness_score(
    entry: dict[str, Any],
    *,
    now: datetime | None = None,
    freshness_windows: dict[str, int] | None = None,
) -> float:
    """Compute a staleness score for a KB entry.

    Score ranges from 0.0 (fresh) to 1.0 (very stale).

    Factors:
        1. Age factor (0.0-0.5): How old is the content relative to its
           type-specific freshness window?
        2. Embedding drift (0.0-0.3): Has content changed since last embedding?
        3. Verification recency (0.0-0.2): How recently was this verified by
           a human?

    Args:
        entry: KB entry dict with standard fields.
        now: Current time (defaults to UTC now).
        freshness_windows: Custom freshness windows per entry type.

    Returns:
        Staleness score between 0.0 and 1.0.
    """
    if now is None:
        now = datetime.now(UTC)
    if freshness_windows is None:
        freshness_windows = DEFAULT_FRESHNESS_WINDOWS

    entry_type = entry.get("entry_type", "custom")
    window_days = freshness_windows.get(entry_type, DEFAULT_FRESHNESS_DAYS)

    score = 0.0

    # Factor 1: Age (0.0 - 0.5)
    # Uses the most recent of: updated_at, last_verified_at
    reference_date = _get_reference_date(entry, now)
    days_old = (now - reference_date).total_seconds() / 86400
    age_ratio = min(days_old / window_days, 1.0) if window_days > 0 else 0.0
    score += age_ratio * 0.5

    # Factor 2: Embedding drift (0.0 - 0.3)
    # Content hash mismatch or missing embedding indicates drift
    has_embedding = entry.get("embedding") is not None
    content_hash = entry.get("content_hash")
    entry.get("embedded_at")

    if not has_embedding:
        # Never embedded — maximum drift
        score += 0.3
    elif not content_hash:
        # Embedded but no hash — cannot verify, moderate drift
        score += 0.15
    else:
        # Check if content has changed since embedding
        from src.multi_tenant.knowledge_vectorizer import compute_content_hash
        title = entry.get("title", "")
        content = entry.get("content", "")
        current_hash = compute_content_hash(title, content)
        if current_hash != content_hash:
            score += 0.3  # Content changed, needs re-embedding

    # Factor 3: Verification recency (0.0 - 0.2)
    last_verified = entry.get("last_verified_at")
    if not last_verified:
        # Never verified — maximum verification staleness
        score += 0.2
    else:
        try:
            verified_dt = datetime.fromisoformat(last_verified.replace("Z", "+00:00"))
            if verified_dt.tzinfo is None:
                verified_dt = verified_dt.replace(tzinfo=UTC)
            days_since_verified = (now - verified_dt).total_seconds() / 86400
            verification_ratio = min(days_since_verified / window_days, 1.0)
            score += verification_ratio * 0.2
        except (ValueError, AttributeError):
            score += 0.2

    return min(score, 1.0)


def _get_reference_date(entry: dict[str, Any], now: datetime) -> datetime:
    """Get the most recent reference date for age calculation.

    Uses the latest of: updated_at, last_verified_at.
    Falls back to created_at, then current time.
    """
    candidates: list[datetime] = []

    for field in ("updated_at", "last_verified_at"):
        value = entry.get(field)
        if value:
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=UTC)
                candidates.append(dt)
            except (ValueError, AttributeError):
                pass

    if not candidates:
        created = entry.get("created_at")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=UTC)
                candidates.append(dt)
            except (ValueError, AttributeError):
                pass

    return max(candidates) if candidates else now


def classify_staleness(score: float) -> str:
    """Classify a staleness score into a human-readable category.

    Returns:
        "fresh", "aging", "stale", or "very_stale"
    """
    if score < FRESH_THRESHOLD:
        return "fresh"
    if score < AGING_THRESHOLD:
        return "aging"
    if score < STALE_THRESHOLD:
        return "stale"
    return "very_stale"


# ---------------------------------------------------------------------------
# StalenessService (WI #220 + #222)
# ---------------------------------------------------------------------------


class StalenessService:
    """Knowledge Base staleness detection and refresh management.

    Provides:
        1. score_entry() — Compute staleness for a single entry
        2. score_all() — Compute staleness for all tenant entries
        3. list_stale() — Get entries above staleness threshold
        4. verify_entry() — Mark an entry as verified (human confirmation)
        5. refresh_stale() — Re-embed stale entries (auto-refresh)
        6. refresh_changed() — Re-embed entries with content changes

    Usage:
        service = get_staleness_service()
        service.configure(kb_repo=repo, vectorizer=vectorizer)

        # Compute staleness for all entries:
        stale_entries = await service.list_stale(tenant_id)

        # Mark entry as verified:
        await service.verify_entry(tenant_id, entry_id)

        # Scheduled job: refresh stale entries:
        count = await service.refresh_stale(tenant_id)
    """

    def __init__(self) -> None:
        self._kb_repo: Any = None  # KnowledgeBaseRepository
        self._vectorizer: Any = None  # KnowledgeVectorizer
        self._configured: bool = False

    def configure(
        self,
        kb_repo: Any,
        vectorizer: Any = None,
    ) -> None:
        """Inject dependencies.

        Args:
            kb_repo: KnowledgeBaseRepository instance.
            vectorizer: KnowledgeVectorizer for re-embedding (optional).
        """
        self._kb_repo = kb_repo
        self._vectorizer = vectorizer
        self._configured = True
        logger.info("StalenessService configured (vectorizer=%s)", "enabled" if vectorizer else "disabled")

    def _ensure_configured(self) -> None:
        if not self._configured:
            raise RuntimeError("StalenessService not configured. Call configure() first.")

    # ------------------------------------------------------------------
    # Score computation
    # ------------------------------------------------------------------

    async def score_entry(
        self,
        tenant_id: str,
        entry_id: str,
        *,
        update: bool = True,
    ) -> dict[str, Any]:
        """Compute and optionally persist staleness score for an entry.

        Args:
            tenant_id: Tenant partition key.
            entry_id: Entry document ID.
            update: If True, persist the score to Cosmos DB.

        Returns:
            Dict with 'id', 'staleness_score', 'staleness_category',
            'last_verified_at', 'embedded_at'.
        """
        self._ensure_configured()

        entry = await self._kb_repo.read(tenant_id, entry_id)
        score = compute_staleness_score(entry)
        category = classify_staleness(score)

        if update:
            await self._kb_repo.patch(
                tenant_id=tenant_id,
                document_id=entry_id,
                operations=[
                    {"op": "set", "path": "/staleness_score", "value": round(score, 4)},
                ],
            )

        return {
            "id": entry_id,
            "staleness_score": round(score, 4),
            "staleness_category": category,
            "last_verified_at": entry.get("last_verified_at"),
            "embedded_at": entry.get("embedded_at"),
        }

    async def score_all(
        self,
        tenant_id: str,
        *,
        update: bool = True,
    ) -> list[dict[str, Any]]:
        """Compute staleness scores for all active entries.

        Args:
            tenant_id: Tenant partition key.
            update: If True, persist scores to Cosmos DB.

        Returns:
            List of score dicts sorted by score descending.
        """
        self._ensure_configured()

        entries = await self._kb_repo.list_filtered(
            tenant_id=tenant_id,
            is_active=True,
            offset=0,
            limit=10000,
        )

        results: list[dict[str, Any]] = []
        for entry in entries:
            entry_id = entry.get("id", "")
            score = compute_staleness_score(entry)
            category = classify_staleness(score)

            if update:
                try:
                    await self._kb_repo.patch(
                        tenant_id=tenant_id,
                        document_id=entry_id,
                        operations=[
                            {"op": "set", "path": "/staleness_score", "value": round(score, 4)},
                        ],
                    )
                except Exception as exc:
                    logger.warning(
                        "Failed to update staleness score for %s: %s", entry_id, exc
                    )

            results.append({
                "id": entry_id,
                "title": entry.get("title", ""),
                "entry_type": entry.get("entry_type", ""),
                "staleness_score": round(score, 4),
                "staleness_category": category,
                "last_verified_at": entry.get("last_verified_at"),
                "embedded_at": entry.get("embedded_at"),
                "updated_at": entry.get("updated_at"),
            })

        results.sort(key=lambda x: x["staleness_score"], reverse=True)
        return results

    async def list_stale(
        self,
        tenant_id: str,
        *,
        threshold: float = STALE_THRESHOLD,
    ) -> list[dict[str, Any]]:
        """List entries above the staleness threshold.

        Args:
            tenant_id: Tenant partition key.
            threshold: Minimum staleness score to include.

        Returns:
            List of stale entry dicts.
        """
        all_scores = await self.score_all(tenant_id, update=True)
        return [e for e in all_scores if e["staleness_score"] >= threshold]

    # ------------------------------------------------------------------
    # Verification (WI #221)
    # ------------------------------------------------------------------

    async def verify_entry(
        self,
        tenant_id: str,
        entry_id: str,
    ) -> dict[str, Any]:
        """Mark an entry as verified by a human.

        Updates `last_verified_at` to now and recalculates staleness score.

        Args:
            tenant_id: Tenant partition key.
            entry_id: Entry document ID.

        Returns:
            Updated score dict.
        """
        self._ensure_configured()

        now = datetime.now(UTC).isoformat()

        await self._kb_repo.patch(
            tenant_id=tenant_id,
            document_id=entry_id,
            operations=[
                {"op": "set", "path": "/last_verified_at", "value": now},
            ],
        )

        # Re-read and recompute score
        entry = await self._kb_repo.read(tenant_id, entry_id)
        score = compute_staleness_score(entry)
        category = classify_staleness(score)

        # Persist updated score
        await self._kb_repo.patch(
            tenant_id=tenant_id,
            document_id=entry_id,
            operations=[
                {"op": "set", "path": "/staleness_score", "value": round(score, 4)},
            ],
        )

        logger.info(
            "KB entry verified: id=%s tenant=%s new_score=%.4f",
            entry_id, tenant_id[:8], score,
        )

        return {
            "id": entry_id,
            "staleness_score": round(score, 4),
            "staleness_category": category,
            "last_verified_at": now,
            "embedded_at": entry.get("embedded_at"),
        }

    # ------------------------------------------------------------------
    # Auto re-embedding (WI #222)
    # ------------------------------------------------------------------

    async def refresh_stale(
        self,
        tenant_id: str,
        *,
        threshold: float = AUTO_REEMBED_THRESHOLD,
        max_entries: int = MAX_REEMBED_BATCH,
    ) -> int:
        """Re-embed stale entries that need refreshing.

        Targets entries where:
            1. Content has changed since last embedding (content_hash mismatch)
            2. Entry has never been embedded
            3. Staleness score exceeds threshold

        Only re-embeds if content has actually changed or embedding is missing.
        Re-embedding unchanged content would produce identical vectors.

        Args:
            tenant_id: Tenant partition key.
            threshold: Minimum staleness score to consider.
            max_entries: Maximum entries to re-embed per batch.

        Returns:
            Number of entries re-embedded.
        """
        self._ensure_configured()

        if not self._vectorizer:
            logger.warning("No vectorizer configured — cannot refresh stale entries")
            return 0

        entries = await self._kb_repo.list_filtered(
            tenant_id=tenant_id,
            is_active=True,
            offset=0,
            limit=10000,
        )

        # Filter to entries that need re-embedding
        to_reembed: list[dict[str, Any]] = []
        for entry in entries:
            score = compute_staleness_score(entry)

            # Only consider entries above threshold
            if score < threshold:
                continue

            # Only re-embed if content changed or embedding is missing
            if self._vectorizer.needs_reembedding(entry):
                to_reembed.append(entry)

        if not to_reembed:
            logger.info("No stale entries need re-embedding for tenant=%s", tenant_id[:8])
            return 0

        # Limit batch size
        to_reembed = to_reembed[:max_entries]

        count = await self._vectorizer.embed_batch(tenant_id, to_reembed)

        logger.info(
            "Stale entry refresh: re-embedded %d/%d entries for tenant=%s",
            count, len(to_reembed), tenant_id[:8],
        )

        return count

    async def refresh_changed(
        self,
        tenant_id: str,
        *,
        max_entries: int = MAX_REEMBED_BATCH,
    ) -> int:
        """Re-embed entries where content has changed since last embedding.

        Unlike refresh_stale(), this targets ALL entries with content
        changes regardless of staleness score. Suitable for scheduled
        jobs that ensure embeddings stay in sync.

        Args:
            tenant_id: Tenant partition key.
            max_entries: Maximum entries to re-embed per batch.

        Returns:
            Number of entries re-embedded.
        """
        self._ensure_configured()

        if not self._vectorizer:
            logger.warning("No vectorizer configured — cannot refresh changed entries")
            return 0

        # embed_unembedded handles entries without embeddings
        unembedded_count = await self._vectorizer.embed_unembedded(tenant_id)

        # Also check for content hash mismatches
        entries = await self._kb_repo.list_filtered(
            tenant_id=tenant_id,
            is_active=True,
            offset=0,
            limit=10000,
        )

        changed: list[dict[str, Any]] = []
        for entry in entries:
            if entry.get("embedding") and self._vectorizer.needs_reembedding(entry):
                changed.append(entry)

        changed_count = 0
        if changed:
            changed = changed[:max_entries]
            changed_count = await self._vectorizer.embed_batch(tenant_id, changed)

        total = unembedded_count + changed_count

        if total > 0:
            logger.info(
                "Content-change refresh: %d new + %d changed = %d total for tenant=%s",
                unembedded_count, changed_count, total, tenant_id[:8],
            )

        return total

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    async def get_summary(self, tenant_id: str) -> dict[str, Any]:
        """Get a summary of staleness across the tenant's KB.

        Returns:
            Dict with counts per category and overall statistics.
        """
        all_scores = await self.score_all(tenant_id, update=False)

        total = len(all_scores)
        categories = {"fresh": 0, "aging": 0, "stale": 0, "very_stale": 0}
        total_score = 0.0

        for entry in all_scores:
            cat = entry["staleness_category"]
            categories[cat] = categories.get(cat, 0) + 1
            total_score += entry["staleness_score"]

        avg_score = total_score / total if total > 0 else 0.0

        return {
            "total_entries": total,
            "avg_staleness_score": round(avg_score, 4),
            "fresh_count": categories["fresh"],
            "aging_count": categories["aging"],
            "stale_count": categories["stale"],
            "very_stale_count": categories["very_stale"],
            "needs_attention": categories["stale"] + categories["very_stale"],
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_staleness_service: StalenessService | None = None


def get_staleness_service() -> StalenessService:
    """Get the singleton StalenessService instance."""
    global _staleness_service
    if _staleness_service is None:
        _staleness_service = StalenessService()
    return _staleness_service
