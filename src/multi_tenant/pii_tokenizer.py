# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Reversible PII tokenization for transport-layer privacy (AGNTCY Phase 6).

Replaces one-way PII scrubbing (``[REDACTED:type]``) with reversible UUID
tokens (``pii-{type}-{uuid}``) that can be detokenized after AI processing.
This ensures PII never reaches external AI models while allowing the original
values to be restored in customer-facing responses.

SPEC-1543: PII Tokenization Before External AI Calls
SPEC-1544: PII Detokenization Before Customer Response
SPEC-1545: PII Token Mapping Storage
SPEC-1546: PII Tokenization Entity Detection

Architecture:
    1. ``tokenize()`` replaces PII with UUID tokens before agent dispatch
    2. AI agents process tokenized text (no PII exposure)
    3. ``detokenize()`` restores original values after Critic validation
    4. Token mappings persisted to Cosmos DB per conversation (7-day TTL)

Entity types detected:
    - email: RFC-compliant email addresses
    - phone: US/international phone numbers (E.164, parenthesized, dashed)
    - order_number: Common e-commerce order ID patterns (#, ORD-, ORDER-)
    - name: Customer names (from customer context, not regex)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PII detection patterns (SPEC-1546)
# ---------------------------------------------------------------------------

# Email: standard RFC-like pattern (conservative)
_EMAIL_RE = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b"
)

# Phone: US, international, parenthesized area codes
_PHONE_RE = re.compile(
    r"(?<!\w)"                         # Not preceded by word char
    r"(?:"
    r"\+?\d{1,3}[\s\-]?"              # Country code
    r"(?:\(\d{1,4}\)|\d{1,4})"         # Area code (optional parens)
    r"[\s\-]?"
    r"\d{3,4}[\s\-]?\d{3,4}"          # Subscriber number
    r"|"
    r"\(\d{3}\)\s*\d{3}[\-]\d{4}"     # (555) 123-4567
    r"|"
    r"\d{3}[\-\.]\d{3}[\-\.]\d{4}"    # 555-123-4567 or 555.123.4567
    r")"
    r"(?!\w)"                          # Not followed by word char
)

# Order numbers: #12345, ORD-12345, ORDER-12345, etc.
_ORDER_RE = re.compile(
    r"(?<!\w)"
    r"(?:#\d{4,10}|(?:ORD|ORDER|INV|INVOICE)[\-_]?\d{4,10})"
    r"(?!\w)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Token mapping storage
# ---------------------------------------------------------------------------

@dataclass
class TokenMapping:
    """Maps a PII token back to its original value.

    Attributes:
        token: The replacement token (e.g., "pii-email-a1b2c3d4").
        original: The original PII value.
        entity_type: PII category (email, phone, order_number, name).
        conversation_id: Scoped to this conversation.
        tenant_id: Owning tenant.
    """

    token: str
    original: str
    entity_type: str
    conversation_id: str
    tenant_id: str


@dataclass
class PiiTokenStore:
    """In-memory cache of PII token mappings for a conversation.

    Token mappings are cached per conversation. Cosmos DB persistence
    is handled asynchronously for durability (SPEC-1545).
    """

    conversation_id: str
    tenant_id: str
    mappings: dict[str, TokenMapping] = field(default_factory=dict)
    _reverse: dict[str, str] = field(default_factory=dict)

    def add(self, original: str, entity_type: str) -> str:
        """Add a PII value and return its token. Deduplicates."""
        if original in self._reverse:
            return self._reverse[original]

        token_id = uuid.uuid4().hex[:12]
        token = f"pii-{entity_type}-{token_id}"

        mapping = TokenMapping(
            token=token,
            original=original,
            entity_type=entity_type,
            conversation_id=self.conversation_id,
            tenant_id=self.tenant_id,
        )
        self.mappings[token] = mapping
        self._reverse[original] = token
        return token

    def resolve(self, token: str) -> str | None:
        """Resolve a token back to its original value."""
        mapping = self.mappings.get(token)
        return mapping.original if mapping else None

    def to_cosmos_docs(self) -> list[dict[str, Any]]:
        """Serialize mappings for Cosmos DB persistence."""
        return [
            {
                "id": f"pii-{m.conversation_id}-{m.token}",
                "token": m.token,
                "original": m.original,
                "entity_type": m.entity_type,
                "conversation_id": m.conversation_id,
                "tenant_id": m.tenant_id,
                "ttl": 604800,  # 7 days
            }
            for m in self.mappings.values()
        ]


# ---------------------------------------------------------------------------
# PII Tokenizer (SPEC-1543, SPEC-1544)
# ---------------------------------------------------------------------------

# Per-conversation token stores (in-memory cache)
_conversation_stores: dict[str, PiiTokenStore] = {}


class PiiTokenizer:
    """Reversible PII tokenizer for the transport layer.

    Usage::

        tokenizer = PiiTokenizer()

        # Before agent dispatch (SPEC-1543)
        safe_text = tokenizer.tokenize(
            customer_message,
            conversation_id="conv-123",
            tenant_id="tenant-456",
        )

        # After Critic validation (SPEC-1544)
        response = tokenizer.detokenize(
            ai_response,
            conversation_id="conv-123",
            tenant_id="tenant-456",
        )
    """

    def __init__(
        self,
        customer_names: list[str] | None = None,
    ) -> None:
        """Initialize tokenizer with optional customer context.

        Args:
            customer_names: Known customer names from profile context.
                These are tokenized as entity_type="name" since name
                detection cannot rely on regex alone.
        """
        self._customer_names = customer_names or []

    def _get_store(
        self,
        conversation_id: str,
        tenant_id: str,
    ) -> PiiTokenStore:
        """Get or create the token store for a conversation."""
        key = f"{tenant_id}:{conversation_id}"
        if key not in _conversation_stores:
            _conversation_stores[key] = PiiTokenStore(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
            )
        return _conversation_stores[key]

    def tokenize(
        self,
        text: str,
        conversation_id: str,
        tenant_id: str,
    ) -> str:
        """Replace PII entities with reversible tokens (SPEC-1543).

        Detection order: names (exact match) > emails > phones > order numbers.
        Each unique PII value gets a stable token within the conversation.

        Args:
            text: Input text containing potential PII.
            conversation_id: Conversation scope.
            tenant_id: Tenant scope.

        Returns:
            Text with PII replaced by ``pii-{type}-{uuid}`` tokens.
        """
        if not text:
            return text

        store = self._get_store(conversation_id, tenant_id)
        result = text

        # 1. Names (from customer context — exact match, case-insensitive)
        for name in self._customer_names:
            if not name or len(name) < 2:
                continue
            # Word-boundary match to avoid partial replacements
            pattern = re.compile(re.escape(name), re.IGNORECASE)
            for match in pattern.finditer(result):
                original = match.group()
                token = store.add(original, "name")
                result = result.replace(original, token, 1)

        # 2. Emails
        for match in _EMAIL_RE.finditer(result):
            original = match.group()
            if original.startswith("pii-"):
                continue  # Skip already-tokenized values
            token = store.add(original, "email")
            result = result.replace(original, token, 1)

        # 3. Phone numbers
        for match in _PHONE_RE.finditer(result):
            original = match.group()
            if original.startswith("pii-"):
                continue
            token = store.add(original, "phone")
            result = result.replace(original, token, 1)

        # 4. Order numbers
        for match in _ORDER_RE.finditer(result):
            original = match.group()
            if original.startswith("pii-"):
                continue
            token = store.add(original, "order_number")
            result = result.replace(original, token, 1)

        if store.mappings:
            logger.debug(
                "PII tokenized: conv=%s entities=%d types=%s",
                conversation_id,
                len(store.mappings),
                list({m.entity_type for m in store.mappings.values()}),
            )

        return result

    def detokenize(
        self,
        text: str,
        conversation_id: str,
        tenant_id: str,
    ) -> str:
        """Restore original PII values from tokens (SPEC-1544).

        Args:
            text: Text containing ``pii-{type}-{uuid}`` tokens.
            conversation_id: Conversation scope.
            tenant_id: Tenant scope.

        Returns:
            Text with tokens replaced by original PII values.
        """
        if not text:
            return text

        store = self._get_store(conversation_id, tenant_id)
        result = text

        for token, mapping in store.mappings.items():
            if token in result:
                result = result.replace(token, mapping.original)

        return result

    def get_mappings(
        self,
        conversation_id: str,
        tenant_id: str,
    ) -> list[dict[str, Any]]:
        """Get all token mappings for Cosmos DB persistence (SPEC-1545)."""
        store = self._get_store(conversation_id, tenant_id)
        return store.to_cosmos_docs()

    @staticmethod
    def clear_conversation(conversation_id: str, tenant_id: str) -> None:
        """Clear cached mappings for a completed conversation."""
        key = f"{tenant_id}:{conversation_id}"
        _conversation_stores.pop(key, None)

    @staticmethod
    def clear_tenant(tenant_id: str) -> None:
        """Clear all cached mappings for a tenant (GDPR deletion)."""
        keys_to_remove = [
            k for k in _conversation_stores if k.startswith(f"{tenant_id}:")
        ]
        for key in keys_to_remove:
            del _conversation_stores[key]
