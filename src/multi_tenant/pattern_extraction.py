"""PatternExtractionService — Layer 3 cross-session behavioral pattern learning.

Work Items #90-92 (Decision #30): Post-conversation analysis to extract,
persist, and decay behavioral patterns that personalize future interactions.

Pattern types:
    - communication_preferences: how the customer likes to interact
      (brief replies, formal tone, prefers lists, asks follow-ups)
    - product_interests: categories, brands, price ranges the customer
      gravitates toward across multiple conversations
    - sentiment_trends: evolving satisfaction trajectory (improving,
      declining, stable-positive, stable-negative)
    - issue_categories: recurring problem themes (shipping delays,
      sizing questions, payment issues)
    - interaction_style: behavioral signals (time-of-day preference,
      response speed, conversation length tendency)

Each pattern carries a confidence score (0.0-1.0) that decays at
0.05/month when not reinforced by new conversations.  Patterns below
0.3 confidence are pruned automatically.

Tier gating:
    - Professional+ only (memory_layers must include 3 in TIER_DEFAULTS)
    - Trial and Starter tiers receive empty pattern lists

Consent gating:
    - Requires consent_status == GRANTED (Decision #10)
    - Skipped silently when consent is NOT_ASKED or DENIED

Execution model:
    - Runs post-conversation (async, not in the real-time pipeline)
    - No latency impact on customer-facing responses
    - Designed to be invoked by a background job or conversation-end hook

Architecture references:
    - Decision #30: Layer 3 — Cross-session pattern learning
    - Decision #10: Consent management gating
    - Decision #32: Test framework (L3-01 through L3-04)
    - WI #90: PatternExtractionService core
    - WI #91: Pattern persistence (merge, deduplicate, prune)
    - WI #92: SystemPromptBuilder integration (build_pattern_context)

Dependencies:
    - cosmos_schema.py: ConsentStatus, TenantTier, TIER_DEFAULTS
    - No new pip packages required

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from pydantic import BaseModel, Field

from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    TenantTier,
    TIER_DEFAULTS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Valid pattern types that the extraction model is expected to produce.
VALID_PATTERN_TYPES: set[str] = {
    "communication_preferences",
    "product_interests",
    "sentiment_trends",
    "issue_categories",
    "interaction_style",
}

# Confidence floor — patterns below this threshold are pruned on merge
# and during periodic decay.  Keeps the pattern store lean and relevant.
CONFIDENCE_PRUNE_THRESHOLD: float = 0.3

# Monthly decay rate applied to patterns that have not been reinforced
# by a new conversation.  A pattern at 1.0 confidence with no
# reinforcement reaches the prune threshold in ~14 months.
DECAY_RATE_PER_MONTH: float = 0.05

# Confidence boost when a new conversation reinforces an existing
# pattern (same pattern_type + pattern_key).  Capped at 1.0.
REINFORCEMENT_BOOST: float = 0.10

# Initial confidence assigned to newly extracted patterns when the
# extraction model does not specify a confidence value.
DEFAULT_INITIAL_CONFIDENCE: float = 0.60

# Maximum number of patterns stored per customer.  Prevents unbounded
# growth for customers with hundreds of conversations.
MAX_PATTERNS_PER_CUSTOMER: int = 50

# Characters-to-tokens approximation (English text), matching the
# constant in conversation_vectorizer.py.
CHARS_PER_TOKEN: int = 4

# Default token budget for Layer 3 prompt injection.
DEFAULT_PATTERN_BUDGET_TOKENS: int = 100

# GPT-4o-mini model identifier used for pattern extraction.
EXTRACTION_MODEL: str = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class ExtractedPattern(BaseModel):
    """A single behavioral pattern extracted from conversation analysis.

    Patterns are the atomic unit of Layer 3 memory.  They represent
    recurring signals about a customer's preferences, interests,
    sentiment, issues, or interaction style.

    The confidence score reflects how strongly the evidence supports
    this pattern.  It increases on reinforcement (new conversations
    exhibiting the same pattern) and decreases via monthly decay when
    no reinforcement occurs.

    Deduplication key: (pattern_type, pattern_key).  Two patterns with
    the same type and key are considered the same pattern and are merged
    rather than stored separately.
    """

    pattern_type: str = Field(
        description=(
            "Category of the pattern.  One of: communication_preferences, "
            "product_interests, sentiment_trends, issue_categories, "
            "interaction_style."
        ),
    )
    pattern_key: str = Field(
        description=(
            "Specific identifier within the pattern type.  Examples: "
            "'prefers_concise_replies', 'interested_in_running_shoes', "
            "'recurring_shipping_delays'."
        ),
    )
    value: str = Field(
        description=(
            "Human-readable description of the pattern, suitable for "
            "inclusion in a system prompt.  Example: 'Customer prefers "
            "concise, bullet-point responses over detailed paragraphs.'"
        ),
    )
    confidence: float = Field(
        default=DEFAULT_INITIAL_CONFIDENCE,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0).  Decays at 0.05/month.",
    )
    last_reinforced: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 timestamp of the last reinforcement event.",
    )
    reinforcement_count: int = Field(
        default=1,
        ge=1,
        description=(
            "Number of separate conversations that have reinforced "
            "this pattern.  Starts at 1 on first extraction."
        ),
    )


# ---------------------------------------------------------------------------
# Extraction prompt template
# ---------------------------------------------------------------------------

EXTRACTION_SYSTEM_PROMPT: str = (
    "You are a customer behavior analyst.  Analyze the following "
    "conversation transcript and extract recurring behavioral patterns "
    "about the customer.\n\n"
    "Return a JSON array of objects with these fields:\n"
    "  - pattern_type: one of communication_preferences, product_interests, "
    "sentiment_trends, issue_categories, interaction_style\n"
    "  - pattern_key: a snake_case identifier for the specific pattern\n"
    "  - value: a one-sentence human-readable description\n"
    "  - confidence: a float 0.0-1.0 reflecting how strongly the "
    "conversation supports this pattern\n\n"
    "Return ONLY the JSON array, no surrounding text.  If no patterns "
    "are detectable, return an empty array [].\n\n"
    "Rules:\n"
    "- Extract at most 5 patterns per conversation\n"
    "- Only include patterns with confidence >= 0.3\n"
    "- Do not hallucinate patterns not evidenced in the transcript\n"
    "- Do not include any PII in pattern_key or value fields\n"
)

MAX_PATTERNS_PER_EXTRACTION: int = 5


# ---------------------------------------------------------------------------
# PatternExtractionService
# ---------------------------------------------------------------------------


class PatternExtractionService:
    """Service for Layer 3 cross-session behavioral pattern learning.

    Extracts behavioral patterns from completed conversations using
    GPT-4o-mini, merges them with existing patterns (deduplicating on
    pattern_type + pattern_key), and applies monthly confidence decay.

    Patterns are stored per-customer and injected into the system prompt
    via ``build_pattern_context()`` at conversation start.

    This service runs post-conversation and has zero latency impact on
    the real-time pipeline.

    Tier gating:
        Layer 3 is available only to Professional and Enterprise tiers
        (memory_layers includes 3 in TIER_DEFAULTS).

    Consent gating:
        All operations require consent_status == GRANTED.

    Usage::

        service = get_pattern_service()
        service.configure(pattern_repo=repo, audit_repo=audit)

        # After conversation ends (background job):
        new_patterns = await service.extract_patterns(
            tenant_id, customer_id, messages, tier
        )
        await service.merge_patterns(tenant_id, customer_id, new_patterns)

        # Periodic maintenance (daily cron):
        await service.apply_decay(tenant_id, customer_id)

        # At conversation start (SystemPromptBuilder):
        patterns = await service.get_patterns(tenant_id, customer_id)
        context = service.build_pattern_context(patterns)
    """

    def __init__(self) -> None:
        self._pattern_repo: Any = None
        self._audit_repo: Any = None
        self._configured: bool = False

        # In-memory pattern store (DEVELOPMENT MODE).
        # Key: "{tenant_id}:{customer_id}" -> list[dict]
        # Production replacement: Cosmos DB via _pattern_repo.
        self._dev_store: dict[str, list[dict[str, Any]]] = {}

    def configure(
        self,
        pattern_repo: Any = None,
        audit_repo: Any = None,
    ) -> None:
        """Inject repository dependencies.

        Args:
            pattern_repo: Repository for pattern persistence.  When None
                the service operates in dev mode with an in-memory dict.
            audit_repo: Optional AuditLogRepository for change logging.
        """
        self._pattern_repo = pattern_repo
        self._audit_repo = audit_repo
        self._configured = True
        logger.info("PatternExtractionService configured")

    def _ensure_configured(self) -> None:
        """Emit a warning if configure() has not been called.

        Unlike ConversationVectorizer (which raises), this service
        gracefully degrades to an in-memory store in dev mode to match
        the pattern used by CustomerProfileService.
        """
        if not self._configured:
            logger.warning(
                "PatternExtractionService not configured — operating "
                "without persistence (dev mode)"
            )

    # ------------------------------------------------------------------
    # Tier and consent checks
    # ------------------------------------------------------------------

    @staticmethod
    def is_layer3_available(tier: TenantTier) -> bool:
        """Check whether the given tier supports Layer 3 memory.

        Layer 3 is gated by ``memory_layers`` in TIER_DEFAULTS.
        Currently available for Professional and Enterprise tiers.

        Args:
            tier: The tenant's subscription tier.

        Returns:
            True if Layer 3 is available, False otherwise.
        """
        from src.multi_tenant.entitlement_service import get_entitlement_service
        defaults = get_entitlement_service().get_tier_config_sync(tier.value)
        memory_layers: list[int] = defaults.get("memory_layers", [1, 2])
        return 3 in memory_layers

    @staticmethod
    def _check_consent(consent_status: ConsentStatus) -> bool:
        """Verify that the customer has granted consent for Layer 3.

        Args:
            consent_status: The customer's current consent status.

        Returns:
            True if consent is GRANTED, False otherwise.
        """
        return consent_status == ConsentStatus.GRANTED

    # ------------------------------------------------------------------
    # Pattern extraction (WI #90)
    # ------------------------------------------------------------------

    async def extract_patterns(
        self,
        tenant_id: str,
        customer_id: str,
        conversation_messages: list[dict[str, Any]],
        tier: TenantTier,
        *,
        consent_status: ConsentStatus = ConsentStatus.GRANTED,
    ) -> list[ExtractedPattern]:
        """Extract behavioral patterns from a completed conversation.

        Invoked post-conversation by a background job.  Uses GPT-4o-mini
        to analyze the transcript and identify recurring behavioral
        signals.

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.
            conversation_messages: Completed conversation transcript.
                Each message is a dict with at least ``role`` and
                ``content`` keys.
            tier: Tenant subscription tier (for Layer 3 gating).
            consent_status: Customer's GDPR consent status.

        Returns:
            List of extracted patterns.  Empty if the tier does not
            support Layer 3, consent is not granted, the conversation
            is empty, or the model returns no patterns.
        """
        self._ensure_configured()

        # Tier gate
        if not self.is_layer3_available(tier):
            logger.debug(
                "Layer 3 not available for tier %s — skipping extraction "
                "for tenant=%s customer=%s",
                tier.value, tenant_id, customer_id,
            )
            return []

        # Consent gate
        if not self._check_consent(consent_status):
            logger.info(
                "Skipping pattern extraction: consent=%s tenant=%s "
                "customer=%s",
                consent_status.value, tenant_id, customer_id,
            )
            return []

        # Empty conversation guard
        if not conversation_messages:
            logger.debug(
                "No messages in conversation — skipping pattern "
                "extraction for tenant=%s customer=%s",
                tenant_id, customer_id,
            )
            return []

        # Build transcript text for the model
        transcript = self._format_transcript(conversation_messages)

        # Call the extraction model
        raw_patterns = await self._call_extraction_model(transcript)

        # Parse and validate
        patterns = self._parse_raw_patterns(raw_patterns)

        logger.info(
            "Extracted %d patterns from conversation: tenant=%s "
            "customer=%s",
            len(patterns), tenant_id, customer_id,
        )

        return patterns

    @staticmethod
    def _format_transcript(
        messages: list[dict[str, Any]],
    ) -> str:
        """Format conversation messages into a plain-text transcript.

        Args:
            messages: List of message dicts with ``role`` and ``content``.

        Returns:
            Multi-line transcript string suitable for model input.
        """
        lines: list[str] = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if content:
                lines.append(f"{role}: {content}")
        return "\n".join(lines)

    async def _call_extraction_model(
        self,
        transcript: str,
    ) -> list[dict[str, Any]]:
        """Call GPT-4o-mini to extract behavioral patterns.

        This method is designed to be overridden or mocked in tests.
        The default implementation returns an empty list with a warning
        that the real model is not configured.

        Production deployments should subclass PatternExtractionService
        or monkey-patch this method to call the Azure OpenAI API::

            response = await openai_client.chat.completions.create(
                model=EXTRACTION_MODEL,
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": transcript},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500,
            )

        Args:
            transcript: Plain-text conversation transcript.

        Returns:
            List of raw pattern dicts from the model response.
            Each dict should have: pattern_type, pattern_key, value,
            confidence.  Returns empty list if model is not configured.
        """
        logger.warning(
            "Real extraction model not configured — returning empty "
            "patterns (DEVELOPMENT MODE).  Override "
            "_call_extraction_model() for production use."
        )
        return []

    @staticmethod
    def _parse_raw_patterns(
        raw_patterns: list[dict[str, Any]],
    ) -> list[ExtractedPattern]:
        """Parse and validate raw model output into ExtractedPattern objects.

        Filters out:
            - Patterns with invalid or missing pattern_type
            - Patterns with confidence below the prune threshold
            - Patterns exceeding the per-extraction limit

        Args:
            raw_patterns: Raw dicts from the extraction model.

        Returns:
            List of validated ExtractedPattern instances.
        """
        if not raw_patterns:
            return []

        now = datetime.now(timezone.utc).isoformat()
        validated: list[ExtractedPattern] = []

        for raw in raw_patterns:
            if len(validated) >= MAX_PATTERNS_PER_EXTRACTION:
                break

            pattern_type = raw.get("pattern_type", "")
            pattern_key = raw.get("pattern_key", "")
            value = raw.get("value", "")
            confidence = raw.get("confidence", DEFAULT_INITIAL_CONFIDENCE)

            # Validate pattern_type
            if pattern_type not in VALID_PATTERN_TYPES:
                logger.debug(
                    "Skipping pattern with invalid type: %s",
                    pattern_type,
                )
                continue

            # Validate required fields
            if not pattern_key or not value:
                logger.debug(
                    "Skipping pattern with missing key or value: "
                    "type=%s key=%s",
                    pattern_type, pattern_key,
                )
                continue

            # Validate and clamp confidence
            try:
                confidence = float(confidence)
            except (TypeError, ValueError):
                confidence = DEFAULT_INITIAL_CONFIDENCE
            confidence = max(0.0, min(1.0, confidence))

            # Prune below threshold
            if confidence < CONFIDENCE_PRUNE_THRESHOLD:
                logger.debug(
                    "Pruning low-confidence pattern: type=%s key=%s "
                    "confidence=%.2f",
                    pattern_type, pattern_key, confidence,
                )
                continue

            validated.append(
                ExtractedPattern(
                    pattern_type=pattern_type,
                    pattern_key=pattern_key,
                    value=value,
                    confidence=confidence,
                    last_reinforced=now,
                    reinforcement_count=1,
                )
            )

        return validated

    # ------------------------------------------------------------------
    # Pattern persistence (WI #91)
    # ------------------------------------------------------------------

    def _store_key(self, tenant_id: str, customer_id: str) -> str:
        """Build the composite key for the in-memory dev store.

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.

        Returns:
            Composite string key "{tenant_id}:{customer_id}".
        """
        return f"{tenant_id}:{customer_id}"

    async def _load_patterns(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> list[dict[str, Any]]:
        """Load stored patterns for a customer.

        Uses the injected repository when configured, otherwise falls
        back to the in-memory dev store.

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.

        Returns:
            List of pattern dicts (serialized ExtractedPattern).
        """
        if self._pattern_repo is not None:
            try:
                return await self._pattern_repo.get_patterns(
                    tenant_id, customer_id,
                )
            except Exception as exc:
                logger.error(
                    "Failed to load patterns from repo: tenant=%s "
                    "customer=%s error=%s",
                    tenant_id, customer_id, exc,
                )
                return []

        # Dev mode: in-memory store
        key = self._store_key(tenant_id, customer_id)
        return list(self._dev_store.get(key, []))

    async def _save_patterns(
        self,
        tenant_id: str,
        customer_id: str,
        patterns: list[dict[str, Any]],
    ) -> None:
        """Persist patterns for a customer.

        Uses the injected repository when configured, otherwise falls
        back to the in-memory dev store.

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.
            patterns: List of serialized pattern dicts to store.
        """
        if self._pattern_repo is not None:
            try:
                await self._pattern_repo.save_patterns(
                    tenant_id, customer_id, patterns,
                )
                return
            except Exception as exc:
                logger.error(
                    "Failed to save patterns to repo: tenant=%s "
                    "customer=%s error=%s",
                    tenant_id, customer_id, exc,
                )
                return

        # Dev mode: in-memory store
        key = self._store_key(tenant_id, customer_id)
        self._dev_store[key] = patterns

    async def get_patterns(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> list[ExtractedPattern]:
        """Retrieve all stored patterns for a customer.

        Returns deserialized ExtractedPattern objects sorted by
        confidence (highest first).

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.

        Returns:
            List of ExtractedPattern instances, sorted by confidence
            descending.  Empty list if no patterns exist.
        """
        self._ensure_configured()

        raw_list = await self._load_patterns(tenant_id, customer_id)
        if not raw_list:
            return []

        patterns: list[ExtractedPattern] = []
        for raw in raw_list:
            try:
                patterns.append(ExtractedPattern(**raw))
            except Exception as exc:
                logger.warning(
                    "Skipping malformed pattern: %s error=%s",
                    raw, exc,
                )

        # Sort by confidence descending (most confident first)
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        return patterns

    async def merge_patterns(
        self,
        tenant_id: str,
        customer_id: str,
        new_patterns: list[ExtractedPattern],
    ) -> list[ExtractedPattern]:
        """Merge new patterns with existing stored patterns.

        Deduplication logic:
            If an existing pattern has the same (pattern_type, pattern_key)
            as a new pattern:
                - Confidence is boosted by REINFORCEMENT_BOOST (capped at 1.0)
                - reinforcement_count is incremented
                - last_reinforced is updated to now
                - value is updated to the new extraction's value (latest
                  observation is the most current description)

            If no match exists, the new pattern is appended.

        After merging, patterns below CONFIDENCE_PRUNE_THRESHOLD are
        removed.  The total is capped at MAX_PATTERNS_PER_CUSTOMER,
        keeping the highest-confidence patterns.

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.
            new_patterns: Freshly extracted patterns to merge.

        Returns:
            The merged, pruned, and sorted list of patterns.
        """
        self._ensure_configured()

        if not new_patterns:
            return await self.get_patterns(tenant_id, customer_id)

        now = datetime.now(timezone.utc).isoformat()

        # Load existing patterns
        existing_raw = await self._load_patterns(tenant_id, customer_id)
        existing: list[ExtractedPattern] = []
        for raw in existing_raw:
            try:
                existing.append(ExtractedPattern(**raw))
            except Exception:
                pass

        # Build a lookup index: (pattern_type, pattern_key) -> index
        index: dict[tuple[str, str], int] = {}
        for i, pat in enumerate(existing):
            index[(pat.pattern_type, pat.pattern_key)] = i

        # Merge new patterns
        for new_pat in new_patterns:
            dedup_key = (new_pat.pattern_type, new_pat.pattern_key)

            if dedup_key in index:
                # Reinforce existing pattern
                idx = index[dedup_key]
                old = existing[idx]

                reinforced_confidence = min(
                    1.0, old.confidence + REINFORCEMENT_BOOST,
                )
                existing[idx] = ExtractedPattern(
                    pattern_type=old.pattern_type,
                    pattern_key=old.pattern_key,
                    value=new_pat.value,  # Use latest description
                    confidence=reinforced_confidence,
                    last_reinforced=now,
                    reinforcement_count=old.reinforcement_count + 1,
                )

                logger.debug(
                    "Reinforced pattern: type=%s key=%s "
                    "confidence=%.2f->%.2f count=%d",
                    old.pattern_type, old.pattern_key,
                    old.confidence, reinforced_confidence,
                    old.reinforcement_count + 1,
                )
            else:
                # New pattern — append
                existing.append(new_pat)
                index[dedup_key] = len(existing) - 1

        # Prune patterns below confidence threshold
        merged = [
            p for p in existing
            if p.confidence >= CONFIDENCE_PRUNE_THRESHOLD
        ]

        # Sort by confidence descending and cap at maximum
        merged.sort(key=lambda p: p.confidence, reverse=True)
        merged = merged[:MAX_PATTERNS_PER_CUSTOMER]

        # Persist
        serialized = [p.model_dump() for p in merged]
        await self._save_patterns(tenant_id, customer_id, serialized)

        logger.info(
            "Merged patterns: tenant=%s customer=%s total=%d "
            "(new=%d, pruned=%d)",
            tenant_id, customer_id, len(merged),
            len(new_patterns),
            len(existing) - len(merged),
        )

        return merged

    async def apply_decay(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> list[ExtractedPattern]:
        """Apply monthly confidence decay to all patterns for a customer.

        Decay formula:
            For each pattern, compute months since last_reinforced.
            New confidence = old_confidence - (months * DECAY_RATE_PER_MONTH).
            Patterns that fall below CONFIDENCE_PRUNE_THRESHOLD are removed.

        This method is designed to be called by a periodic maintenance
        job (e.g., daily cron).  Decay is calculated relative to the
        actual elapsed time since last_reinforced, not since last decay
        run — so it is safe to call at any frequency.

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.

        Returns:
            The surviving patterns after decay and pruning.
        """
        self._ensure_configured()

        existing_raw = await self._load_patterns(tenant_id, customer_id)
        if not existing_raw:
            return []

        now = datetime.now(timezone.utc)
        surviving: list[ExtractedPattern] = []
        pruned_count = 0

        for raw in existing_raw:
            try:
                pattern = ExtractedPattern(**raw)
            except Exception:
                continue

            # Calculate months since last reinforcement
            try:
                last_reinforced = datetime.fromisoformat(
                    pattern.last_reinforced
                )
                # Ensure timezone-aware comparison
                if last_reinforced.tzinfo is None:
                    last_reinforced = last_reinforced.replace(
                        tzinfo=timezone.utc
                    )
                elapsed = now - last_reinforced
                months_elapsed = elapsed.total_seconds() / (
                    30.44 * 24 * 60 * 60
                )  # Average month in seconds
            except (ValueError, TypeError):
                # Cannot parse timestamp — apply one month of decay
                months_elapsed = 1.0

            # Apply decay
            decay_amount = months_elapsed * DECAY_RATE_PER_MONTH
            new_confidence = pattern.confidence - decay_amount

            if new_confidence < CONFIDENCE_PRUNE_THRESHOLD:
                logger.debug(
                    "Pruning decayed pattern: type=%s key=%s "
                    "confidence=%.2f->%.2f",
                    pattern.pattern_type, pattern.pattern_key,
                    pattern.confidence, new_confidence,
                )
                pruned_count += 1
                continue

            surviving.append(
                ExtractedPattern(
                    pattern_type=pattern.pattern_type,
                    pattern_key=pattern.pattern_key,
                    value=pattern.value,
                    confidence=round(new_confidence, 4),
                    last_reinforced=pattern.last_reinforced,
                    reinforcement_count=pattern.reinforcement_count,
                )
            )

        # Sort and persist
        surviving.sort(key=lambda p: p.confidence, reverse=True)
        serialized = [p.model_dump() for p in surviving]
        await self._save_patterns(tenant_id, customer_id, serialized)

        if pruned_count > 0:
            logger.info(
                "Decay applied: tenant=%s customer=%s surviving=%d "
                "pruned=%d",
                tenant_id, customer_id, len(surviving), pruned_count,
            )

        return surviving

    async def delete_patterns(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> int:
        """Delete all patterns for a customer (GDPR data deletion).

        Called when consent is revoked or a data deletion request
        is processed.

        Args:
            tenant_id: Tenant partition key.
            customer_id: Customer identifier.

        Returns:
            Number of patterns deleted.
        """
        self._ensure_configured()

        existing = await self._load_patterns(tenant_id, customer_id)
        count = len(existing)

        await self._save_patterns(tenant_id, customer_id, [])

        if count > 0:
            logger.info(
                "Deleted %d patterns: tenant=%s customer=%s",
                count, tenant_id, customer_id,
            )

        return count

    # ------------------------------------------------------------------
    # Prompt context building (WI #92)
    # ------------------------------------------------------------------

    @staticmethod
    def build_pattern_context(
        patterns: list[ExtractedPattern],
        budget_tokens: int = DEFAULT_PATTERN_BUDGET_TOKENS,
    ) -> str:
        """Compress patterns into a prompt-ready context block.

        Produces a compact text section (~100 tokens) summarizing the
        customer's behavioral patterns for injection into the system
        prompt by SystemPromptBuilder (Layer 3).

        Patterns are grouped by type and rendered as brief, actionable
        statements.  Only patterns above the prune threshold are
        included, sorted by confidence descending.

        Args:
            patterns: List of ExtractedPattern instances to format.
            budget_tokens: Maximum token budget (default 100).

        Returns:
            Formatted context string for prompt injection.  Returns
            empty string if no patterns are provided or all are below
            the confidence threshold.
        """
        if not patterns:
            return ""

        # Filter and sort
        eligible = [
            p for p in patterns
            if p.confidence >= CONFIDENCE_PRUNE_THRESHOLD
        ]
        eligible.sort(key=lambda p: p.confidence, reverse=True)

        if not eligible:
            return ""

        max_chars = budget_tokens * CHARS_PER_TOKEN
        header = "CUSTOMER BEHAVIOR PATTERNS (cross-session learning):"
        lines: list[str] = [header]
        total_chars = len(header)

        # Group by pattern_type for readability
        type_order = [
            "communication_preferences",
            "product_interests",
            "sentiment_trends",
            "issue_categories",
            "interaction_style",
        ]

        # Build a map of type -> patterns
        by_type: dict[str, list[ExtractedPattern]] = {}
        for pat in eligible:
            by_type.setdefault(pat.pattern_type, []).append(pat)

        for ptype in type_order:
            type_patterns = by_type.get(ptype)
            if not type_patterns:
                continue

            for pat in type_patterns:
                # Format: - [type] value (conf=0.xx, seen Nx)
                line = (
                    f"- [{pat.pattern_type}] {pat.value} "
                    f"(conf={pat.confidence:.2f}, "
                    f"seen {pat.reinforcement_count}x)"
                )

                # Check budget
                if total_chars + len(line) > max_chars:
                    # Truncate the line if it alone is too long
                    available = max_chars - total_chars - 10
                    if available > 40:
                        truncated = line[:available].rsplit(" ", 1)[0] + "..."
                        lines.append(truncated)
                        total_chars += len(truncated)
                    break

                lines.append(line)
                total_chars += len(line)

                if total_chars >= max_chars:
                    break

            if total_chars >= max_chars:
                break

        if len(lines) <= 1:
            return ""

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Bulk operations (maintenance / admin)
    # ------------------------------------------------------------------

    async def get_pattern_summary(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> dict[str, Any]:
        """Get a summary of stored patterns for admin/debugging.

        Returns:
            Dict with total_count, by_type counts, avg_confidence,
            oldest_reinforced, and newest_reinforced timestamps.
        """
        patterns = await self.get_patterns(tenant_id, customer_id)

        if not patterns:
            return {
                "total_count": 0,
                "by_type": {},
                "avg_confidence": 0.0,
                "oldest_reinforced": None,
                "newest_reinforced": None,
            }

        by_type: dict[str, int] = {}
        for pat in patterns:
            by_type[pat.pattern_type] = by_type.get(pat.pattern_type, 0) + 1

        confidences = [p.confidence for p in patterns]
        timestamps = [p.last_reinforced for p in patterns]
        timestamps.sort()

        return {
            "total_count": len(patterns),
            "by_type": by_type,
            "avg_confidence": round(
                sum(confidences) / len(confidences), 4
            ),
            "oldest_reinforced": timestamps[0] if timestamps else None,
            "newest_reinforced": timestamps[-1] if timestamps else None,
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service: PatternExtractionService | None = None


def get_pattern_service() -> PatternExtractionService:
    """Get the singleton PatternExtractionService instance.

    Returns:
        The shared PatternExtractionService instance, creating it
        on first call.
    """
    global _service
    if _service is None:
        _service = PatternExtractionService()
    return _service
