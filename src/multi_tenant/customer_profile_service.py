"""CustomerProfileService — Layer 1 customer context management.

Work Items #83-85 (Decision #28): CRUD operations for customer profiles,
Shopify data sync, and profile injection into SystemPromptBuilder.

Provides:
    - Profile CRUD with PII classification awareness
    - Shopify purchase/cart data sync adapter
    - Consent-gated operations (Layer 1 always available, Layers 2-4 gated)
    - Profile freshness tracking and stale profile detection
    - Profile summary for ~250 token prompt injection

Architecture references:
    - Decision #28: Layer 1 — Customer context profile (6 data sources)
    - Decision #10: Consent management (gates Layers 2-4, not Layer 1)
    - Decision #32: Test framework (L1-01 through L1-06)

Data sources:
    1. Purchase history (product ID, date, rating, review)
    2. Historical product questions
    3. Geographic region codes (shipping, availability, timezone, locale)
    4. Marketing segmentation codes
    5. Jurisdiction codes (regulatory compliance)
    6. Shopping cart contents (active + abandoned)

Dependencies:
    - cosmos_schema.py: CustomerProfileDocument, ConsentStatus, TenantTier
    - repository.py: CustomerProfileRepository
    - gdpr_services.py: PiiScrubber (for audit log sanitization)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import Any

from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    CustomerProfileDocument,
    TenantTier,
    TIER_DEFAULTS,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Profile older than this is flagged as stale (L1-06 test case)
STALE_PROFILE_DAYS = 90

# Maximum items per data source to keep profiles manageable
MAX_PURCHASE_HISTORY = 50
MAX_PRODUCT_QUESTIONS = 30
MAX_MARKETING_SEGMENTS = 20
MAX_CART_ITEMS = 25

# Patterns for extracting asserted name from customer messages (Issue #5b)
_NAME_PATTERNS = [
    re.compile(r"\bmy name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", re.IGNORECASE),
    re.compile(r"\bi'm\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", re.IGNORECASE),
    re.compile(r"\bthis is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", re.IGNORECASE),
    re.compile(r"\bcall me\s+([A-Z][a-z]+)\b", re.IGNORECASE),
    re.compile(r"\bname['s]*\s*(?:is|:)\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", re.IGNORECASE),
]

_EMAIL_PATTERN = re.compile(
    r"\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b"
)


def extract_identity_from_text(text: str) -> dict[str, str]:
    """Extract name and/or email from a customer message.

    Returns a dict with optional 'name' and 'email' keys.
    Only extracts values that look like genuine self-identification,
    not product names or other entities.
    """
    result: dict[str, str] = {}

    # Extract name
    for pattern in _NAME_PATTERNS:
        match = pattern.search(text)
        if match:
            name = match.group(1).strip()
            # Basic validation: 2-50 chars, not common words
            if 2 <= len(name) <= 50 and name.lower() not in (
                "here", "back", "sorry", "sure", "fine", "good", "great",
                "interested", "looking", "wondering", "having", "trying",
            ):
                result["name"] = name
                break

    # Extract email
    email_match = _EMAIL_PATTERN.search(text)
    if email_match:
        result["email"] = email_match.group(1)

    return result


# ---------------------------------------------------------------------------
# CustomerProfileService
# ---------------------------------------------------------------------------


class CustomerProfileService:
    """Service for managing Layer 1 customer profiles (Decision #28).

    Provides CRUD operations, data source updates, Shopify sync,
    consent management, and profile freshness tracking.

    Layer 1 is always available (all tiers, no consent gating).
    The profile is injected into SystemPromptBuilder as ~250 tokens
    of structured customer context.

    Usage:
        service = get_profile_service()
        profile = await service.get_or_create(tenant_id, customer_id)
        await service.update_purchase_history(tenant_id, customer_id, purchases)
        summary = service.build_prompt_summary(profile)
    """

    def __init__(self) -> None:
        self._repo: Any = None  # CustomerProfileRepository (injected)
        self._audit_repo: Any = None  # AuditLogRepository (optional)
        self._configured: bool = False

    def configure(
        self,
        profile_repo: Any,
        audit_repo: Any = None,
    ) -> None:
        """Inject repository dependencies.

        Args:
            profile_repo: CustomerProfileRepository instance.
            audit_repo: Optional AuditLogRepository for change logging.
        """
        self._repo = profile_repo
        self._audit_repo = audit_repo
        self._configured = True
        logger.info("CustomerProfileService configured")

    def _ensure_configured(self) -> None:
        if not self._configured:
            logger.warning(
                "CustomerProfileService not configured — operating without "
                "persistence (dev mode)"
            )

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    async def get_profile(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> CustomerProfileDocument | None:
        """Get a customer profile, or None if not found.

        Layer 1 profiles are not consent-gated — always returned
        when they exist.
        """
        if not self._configured:
            return None

        doc = await self._repo.get_by_customer_id(tenant_id, customer_id)
        if doc is None:
            return None

        return CustomerProfileDocument(**doc)

    async def get_or_create(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> CustomerProfileDocument:
        """Get an existing profile or create a new empty one.

        New profiles start with NOT_ASKED consent and empty data sources.
        """
        existing = await self.get_profile(tenant_id, customer_id)
        if existing is not None:
            return existing

        now = datetime.now(timezone.utc).isoformat()
        profile = CustomerProfileDocument(
            id=f"{tenant_id}:{customer_id}",
            tenant_id=tenant_id,
            customer_id=customer_id,
            consent_status=ConsentStatus.NOT_ASKED,
            created_at=now,
            updated_at=now,
        )

        if self._configured:
            await self._repo.upsert_profile(tenant_id, profile)
            logger.info(
                "Customer profile created: tenant=%s customer=%s",
                tenant_id, customer_id,
            )

        return profile

    async def delete_profile(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> bool:
        """Delete a customer profile (GDPR data deletion).

        Returns True if a profile was deleted, False if not found.
        """
        if not self._configured:
            return False

        doc_id = f"{tenant_id}:{customer_id}"
        try:
            await self._repo.delete(tenant_id, doc_id)
            logger.info(
                "Customer profile deleted: tenant=%s customer=%s",
                tenant_id, customer_id,
            )
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Data source updates
    # ------------------------------------------------------------------

    async def update_purchase_history(
        self,
        tenant_id: str,
        customer_id: str,
        purchases: list[dict[str, Any]],
    ) -> CustomerProfileDocument:
        """Append purchase records to the customer profile.

        Each purchase: {product_id, date, rating?, review_snippet?}
        Keeps the most recent MAX_PURCHASE_HISTORY entries.
        """
        profile = await self.get_or_create(tenant_id, customer_id)
        combined = profile.purchase_history + purchases
        # Keep most recent, sorted by date descending
        combined.sort(key=lambda p: p.get("date", ""), reverse=True)
        profile.purchase_history = combined[:MAX_PURCHASE_HISTORY]
        profile.updated_at = datetime.now(timezone.utc).isoformat()

        if self._configured:
            await self._repo.upsert_profile(tenant_id, profile)

        return profile

    async def update_product_questions(
        self,
        tenant_id: str,
        customer_id: str,
        questions: list[dict[str, Any]],
    ) -> CustomerProfileDocument:
        """Append product question records.

        Each question: {question, product_id, date, resolved}
        """
        profile = await self.get_or_create(tenant_id, customer_id)
        combined = profile.product_questions + questions
        combined.sort(key=lambda q: q.get("date", ""), reverse=True)
        profile.product_questions = combined[:MAX_PRODUCT_QUESTIONS]
        profile.updated_at = datetime.now(timezone.utc).isoformat()

        if self._configured:
            await self._repo.upsert_profile(tenant_id, profile)

        return profile

    async def update_region_codes(
        self,
        tenant_id: str,
        customer_id: str,
        region_codes: dict[str, str],
    ) -> CustomerProfileDocument:
        """Update geographic region codes.

        Expected keys: shipping_region, availability_zone, timezone, locale
        """
        profile = await self.get_or_create(tenant_id, customer_id)
        profile.region_codes.update(region_codes)
        profile.updated_at = datetime.now(timezone.utc).isoformat()

        if self._configured:
            await self._repo.upsert_profile(tenant_id, profile)

        return profile

    async def update_marketing_segments(
        self,
        tenant_id: str,
        customer_id: str,
        segments: list[str],
    ) -> CustomerProfileDocument:
        """Replace marketing segmentation codes."""
        profile = await self.get_or_create(tenant_id, customer_id)
        profile.marketing_segments = segments[:MAX_MARKETING_SEGMENTS]
        profile.updated_at = datetime.now(timezone.utc).isoformat()

        if self._configured:
            await self._repo.upsert_profile(tenant_id, profile)

        return profile

    async def update_jurisdiction_codes(
        self,
        tenant_id: str,
        customer_id: str,
        jurisdiction: dict[str, str],
    ) -> CustomerProfileDocument:
        """Update jurisdiction codes.

        Expected keys: country, state, tax_region, regulatory_framework
        """
        profile = await self.get_or_create(tenant_id, customer_id)
        profile.jurisdiction_codes.update(jurisdiction)
        profile.updated_at = datetime.now(timezone.utc).isoformat()

        if self._configured:
            await self._repo.upsert_profile(tenant_id, profile)

        return profile

    async def update_cart_contents(
        self,
        tenant_id: str,
        customer_id: str,
        active_cart: list[dict[str, Any]] | None = None,
        abandoned_cart: list[dict[str, Any]] | None = None,
    ) -> CustomerProfileDocument:
        """Update shopping cart contents.

        active_cart items: [{product_id, qty, ...}]
        abandoned_cart items: [{product_id, qty, abandoned_at, ...}]
        """
        profile = await self.get_or_create(tenant_id, customer_id)

        if active_cart is not None:
            profile.cart_contents["active"] = active_cart[:MAX_CART_ITEMS]
        if abandoned_cart is not None:
            profile.cart_contents["abandoned"] = abandoned_cart[:MAX_CART_ITEMS]

        profile.updated_at = datetime.now(timezone.utc).isoformat()

        if self._configured:
            await self._repo.upsert_profile(tenant_id, profile)

        return profile

    async def record_interaction(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> None:
        """Update the last_interaction_at timestamp.

        Called at the start of every conversation to track freshness.
        """
        if self._configured:
            try:
                await self._repo.update_last_interaction(tenant_id, customer_id)
            except Exception:
                # Non-fatal — profile may not exist yet
                logger.debug(
                    "Could not update interaction timestamp: tenant=%s customer=%s",
                    tenant_id, customer_id,
                )

    async def extract_and_store_identity(
        self,
        tenant_id: str,
        customer_id: str,
        message_text: str,
    ) -> dict[str, str] | None:
        """Extract asserted identity from a customer message and persist it.

        Called by the chat pipeline on each incoming customer message.
        Returns the extracted identity dict if new info was found, else None.
        """
        extracted = extract_identity_from_text(message_text)
        if not extracted:
            return None

        try:
            profile = await self.get_or_create(tenant_id, customer_id)
            existing = profile.asserted_identity or {}
            changed = False

            # Only update name if not already set or if new extraction is longer
            if "name" in extracted and (
                not existing.get("name")
                or len(extracted["name"]) > len(existing.get("name", ""))
            ):
                existing["name"] = extracted["name"]
                changed = True

            # Only update email if not already set
            if "email" in extracted and not existing.get("email"):
                existing["email"] = extracted["email"]
                changed = True

            if changed:
                existing["extracted_at"] = datetime.now(timezone.utc).isoformat()
                existing["source"] = "user_statement"
                profile.asserted_identity = existing
                profile.updated_at = datetime.now(timezone.utc).isoformat()
                if self._configured:
                    await self._repo.upsert_profile(tenant_id, profile)
                    logger.info(
                        "Asserted identity stored: tenant=%s customer=%s fields=%s",
                        tenant_id, customer_id, list(extracted.keys()),
                    )
                return extracted
        except Exception:
            logger.debug(
                "Could not store asserted identity: tenant=%s customer=%s",
                tenant_id, customer_id, exc_info=True,
            )
        return None

    # ------------------------------------------------------------------
    # Shopify sync adapter (WI #84)
    # ------------------------------------------------------------------

    async def sync_from_shopify(
        self,
        tenant_id: str,
        customer_id: str,
        shopify_data: dict[str, Any],
    ) -> CustomerProfileDocument:
        """Sync customer data from Shopify webhooks/API.

        Accepts a normalized dict with optional keys:
            - orders: [{product_id, date, ...}]
            - cart: {active: [...], abandoned: [...]}
            - customer: {region, locale, tags, ...}

        This is the primary data ingestion path for Shopify merchants.
        """
        profile = await self.get_or_create(tenant_id, customer_id)
        changed = False

        # Orders → purchase history
        if "orders" in shopify_data:
            orders = shopify_data["orders"]
            if orders:
                combined = profile.purchase_history + orders
                combined.sort(key=lambda p: p.get("date", ""), reverse=True)
                profile.purchase_history = combined[:MAX_PURCHASE_HISTORY]
                changed = True

        # Cart data
        if "cart" in shopify_data:
            cart = shopify_data["cart"]
            if "active" in cart:
                profile.cart_contents["active"] = cart["active"][:MAX_CART_ITEMS]
                changed = True
            if "abandoned" in cart:
                profile.cart_contents["abandoned"] = cart["abandoned"][:MAX_CART_ITEMS]
                changed = True

        # Customer metadata
        if "customer" in shopify_data:
            cust = shopify_data["customer"]

            # Region codes from Shopify address data
            region_update: dict[str, str] = {}
            if "country_code" in cust:
                region_update["shipping_region"] = cust["country_code"]
            if "province_code" in cust:
                region_update["availability_zone"] = cust["province_code"]
            if "locale" in cust:
                region_update["locale"] = cust["locale"]
            if region_update:
                profile.region_codes.update(region_update)
                changed = True

            # Marketing segments from Shopify tags
            if "tags" in cust and isinstance(cust["tags"], list):
                profile.marketing_segments = cust["tags"][:MAX_MARKETING_SEGMENTS]
                changed = True

        if changed:
            profile.updated_at = datetime.now(timezone.utc).isoformat()
            if self._configured:
                await self._repo.upsert_profile(tenant_id, profile)
                logger.info(
                    "Shopify sync complete: tenant=%s customer=%s",
                    tenant_id, customer_id,
                )

        return profile

    # ------------------------------------------------------------------
    # Profile freshness (L1-06 test case)
    # ------------------------------------------------------------------

    def is_stale(
        self,
        profile: CustomerProfileDocument,
        threshold_days: int = STALE_PROFILE_DAYS,
    ) -> bool:
        """Check if a profile is stale (no interaction in threshold_days).

        A stale profile should trigger a refresh from Shopify or
        other data sources.
        """
        if not profile.last_interaction_at:
            return True

        try:
            last = datetime.fromisoformat(profile.last_interaction_at)
            cutoff = datetime.now(timezone.utc) - timedelta(days=threshold_days)
            return last < cutoff
        except (ValueError, TypeError):
            return True

    def is_empty(self, profile: CustomerProfileDocument) -> bool:
        """Check if a profile has no meaningful data (L1-05 test case).

        Empty profiles should trigger graceful degradation — the
        prompt builder omits the customer context section entirely.
        """
        return (
            not profile.purchase_history
            and not profile.product_questions
            and not profile.region_codes
            and not profile.marketing_segments
            and not profile.jurisdiction_codes
            and not profile.cart_contents.get("active")
            and not profile.cart_contents.get("abandoned")
        )

    # ------------------------------------------------------------------
    # Consent management (per-customer level)
    # ------------------------------------------------------------------

    async def update_consent(
        self,
        tenant_id: str,
        customer_id: str,
        consent: ConsentStatus,
    ) -> CustomerProfileDocument:
        """Update customer-level consent for Persistent Customer Memory.

        Layer 1 is NOT gated by consent — it's always available.
        Consent gates Layers 2-4 (vectorization, patterns, fine-tuning).

        When consent is DENIED, this triggers deletion of Layer 2-4
        data via the ConsentManager in gdpr_services.py.
        """
        profile = await self.get_or_create(tenant_id, customer_id)
        profile.consent_status = consent
        profile.updated_at = datetime.now(timezone.utc).isoformat()

        if self._configured:
            await self._repo.upsert_profile(tenant_id, profile)
            logger.info(
                "Customer consent updated: tenant=%s customer=%s consent=%s",
                tenant_id, customer_id, consent.value,
            )

        return profile

    def is_consent_granted(self, profile: CustomerProfileDocument) -> bool:
        """Check if the customer has granted consent for Layers 2-4."""
        return profile.consent_status == ConsentStatus.GRANTED

    # ------------------------------------------------------------------
    # Tier-aware utilities
    # ------------------------------------------------------------------

    @staticmethod
    def get_available_layers(tier: TenantTier) -> list[int]:
        """Get available memory layers for a tier."""
        from src.multi_tenant.entitlement_service import get_entitlement_service
        defaults = get_entitlement_service().get_tier_config_sync(tier.value)
        return defaults.get("memory_layers", [1, 2])

    @staticmethod
    def get_history_depth_days(tier: TenantTier) -> int | None:
        """Get Layer 2 history depth in days for a tier.

        Returns None for unlimited (Enterprise).
        """
        from src.multi_tenant.entitlement_service import get_entitlement_service
        defaults = get_entitlement_service().get_tier_config_sync(tier.value)
        return defaults.get("history_depth_days", 90)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service: CustomerProfileService | None = None


def get_profile_service() -> CustomerProfileService:
    """Get the singleton CustomerProfileService instance."""
    global _service
    if _service is None:
        _service = CustomerProfileService()
    return _service
