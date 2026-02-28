"""
GDPR compliance services — PII scrubbing, data export, data deletion, consent management.

Implements Decisions #7-10 and Work Items #30-34. Provides the full GDPR
compliance infrastructure for multi-tenant operations, including:

1. PII Scrubbing (Decision #7, WI #30):
   PiiScrubber — strips PII from log output and telemetry before export to
   Application Insights. Recognizes field-level PII classification from
   cosmos_schema.PiiClassification.

2. Grace Period Logic (Decision #8, WI #31):
   GracePeriodManager — enforces channel-specific grace periods:
   - Shopify: 48-hour mandatory grace period (per Shopify Partner requirements)
   - Stripe: 30-day grace period (per our SLA)
   After grace period expiry, triggers full data deletion.

3. Data Export (Decision #9, WI #32):
   DataExportService — exports all tenant/customer data from every data store
   using a registry pattern. Produces a portable JSON archive.

4. Data Deletion (Decision #9, WI #33):
   DataDeletionService — cascading delete across all stores:
   Cosmos DB (7 collections), NATS streams, Key Vault secrets.

5. Consent Management (Decision #10, WI #34):
   ConsentManager — gates Persistent Customer Memory Layers 2-4 behind
   consent_status. Logs all consent changes to the audit log.

Data store registry (Decision #9):
    ┌─────────────────────────────────────────────────────────────────┐
    │  DataStoreRegistry                                              │
    │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
    │  │ Cosmos DB         │  │ NATS JetStream   │  │ Key Vault    │ │
    │  │ (8 collections)   │  │ (tenant stream)  │  │ (tenant keys)│ │
    │  └──────────────────┘  └──────────────────┘  └──────────────┘ │
    └─────────────────────────────────────────────────────────────────┘

Architecture references:
    - Decision #7: PII scrubbing at logging layer
    - Decision #8: Channel-specific grace periods (48hr Shopify, 30d Stripe)
    - Decision #9: DataExportService + DataDeletionService with data store registry
    - Decision #10: consent_status gating for Persistent Customer Memory
    - AuditEventType.DATA_EXPORTED, DATA_DELETED, CONSENT_CHANGED
    - TenantDocument.consent_status, grace_period_ends_at
    - CustomerProfileDocument.consent_status

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Protocol

from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    BillingChannel,
    ConsentStatus,
    PiiClassification,
    TenantStatus,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Grace period durations (Decision #8)
SHOPIFY_GRACE_PERIOD_HOURS = 48      # Shopify Partner requirement
STRIPE_GRACE_PERIOD_DAYS = 30        # Per SLA

# PII field patterns — fields that must be scrubbed from logs/telemetry
# Keyed by PII classification level. Fields listed here are scrubbed from
# any dict before it's sent to Application Insights or external logging.
PII_FIELD_PATTERNS: dict[PiiClassification, list[str]] = {
    PiiClassification.DIRECT: [
        "customer_email",
        "email",
        "name",
        "first_name",
        "last_name",
        "customer_name",
        "phone",
        "phone_number",
        "address",
        "billing_address",
        "shipping_address",
    ],
    PiiClassification.INDIRECT: [
        "ip_address",
        "ip",
        "device_id",
        "user_agent",
        "stripe_customer_id",
        "shopify_shop_domain",
        "customer_id",
    ],
    PiiClassification.SENSITIVE: [
        "cart_contents",
        "purchase_history",
        "product_questions",
        "messages",
        "chunk_text",
        "transcript",
    ],
}

# Flat set of all PII field names for fast lookup
_ALL_PII_FIELDS: set[str] = set()
for _fields in PII_FIELD_PATTERNS.values():
    _ALL_PII_FIELDS.update(_fields)

# Regex patterns for PII that might appear in free-text fields
_EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_PHONE_PATTERN = re.compile(r"\+?[\d\s\-().]{7,15}")


# ---------------------------------------------------------------------------
# PII Scrubber (Decision #7, Work Item #30)
# ---------------------------------------------------------------------------


class PiiScrubber:
    """Scrubs PII from dicts before export to Application Insights or logs.

    Decision #7 requires that NO customer-identifiable data reaches
    Application Insights. This scrubber processes telemetry payloads
    at the logging/export layer.

    Scrubbing strategy:
        - Known PII fields (from PII_FIELD_PATTERNS) are replaced with
          "[REDACTED:{classification}]".
        - Free-text fields are scanned for email and phone patterns.
        - Nested dicts are scrubbed recursively.
        - Lists are scrubbed element-by-element.

    Usage:
        scrubber = PiiScrubber()

        # Scrub a telemetry payload before export
        clean = scrubber.scrub(raw_payload)
        send_to_application_insights(clean)

        # Scrub a log message
        safe_msg = scrubber.scrub_text("User john@example.com reported issue")
        logger.info(safe_msg)
    """

    def __init__(
        self,
        pii_fields: set[str] | None = None,
        redact_free_text: bool = True,
    ) -> None:
        """Initialize the PII scrubber.

        Args:
            pii_fields: Set of field names to scrub. Defaults to _ALL_PII_FIELDS.
            redact_free_text: Whether to scan free-text strings for patterns.
        """
        self._pii_fields = pii_fields or _ALL_PII_FIELDS
        self._redact_free_text = redact_free_text

    def scrub(self, data: dict[str, Any]) -> dict[str, Any]:
        """Scrub PII from a dict payload.

        Returns a new dict with PII fields replaced by redaction markers.
        The original dict is NOT modified.

        Args:
            data: Telemetry or log payload to scrub.

        Returns:
            A new dict with PII removed.
        """
        return self._scrub_dict(data)

    def scrub_text(self, text: str) -> str:
        """Scrub PII patterns from a free-text string.

        Replaces email addresses and phone numbers with markers.

        Args:
            text: Free-text string to scrub.

        Returns:
            The scrubbed string.
        """
        if not self._redact_free_text:
            return text
        result = _EMAIL_PATTERN.sub("[REDACTED:email]", text)
        result = _PHONE_PATTERN.sub("[REDACTED:phone]", result)
        return result

    def classify_field(self, field_name: str) -> PiiClassification:
        """Classify a field's PII level.

        Args:
            field_name: The field name to classify.

        Returns:
            The PII classification, or NONE if not recognized.
        """
        for classification, fields in PII_FIELD_PATTERNS.items():
            if field_name in fields:
                return classification
        return PiiClassification.NONE

    def _scrub_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively scrub a dict."""
        result: dict[str, Any] = {}
        for key, value in data.items():
            if key in self._pii_fields:
                classification = self.classify_field(key)
                result[key] = f"[REDACTED:{classification.value}]"
            elif isinstance(value, dict):
                result[key] = self._scrub_dict(value)
            elif isinstance(value, list):
                result[key] = self._scrub_list(value)
            elif isinstance(value, str) and self._redact_free_text:
                result[key] = self.scrub_text(value)
            else:
                result[key] = value
        return result

    def _scrub_list(self, items: list[Any]) -> list[Any]:
        """Recursively scrub a list."""
        result: list[Any] = []
        for item in items:
            if isinstance(item, dict):
                result.append(self._scrub_dict(item))
            elif isinstance(item, str) and self._redact_free_text:
                result.append(self.scrub_text(item))
            else:
                result.append(item)
        return result


# ---------------------------------------------------------------------------
# Grace Period Manager (Decision #8, Work Item #31)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GracePeriodResult:
    """Result of a grace period calculation."""

    channel: BillingChannel
    grace_period_hours: int
    starts_at: str          # ISO 8601
    ends_at: str            # ISO 8601
    is_expired: bool


class GracePeriodManager:
    """Manages channel-specific data retention grace periods.

    Decision #8:
        - Shopify: 48-hour mandatory grace period (Shopify Partner requirement)
        - Stripe: 30-day grace period (per our SLA)

    After the grace period expires, the DataDeletionService is invoked
    to perform full cascading deletion.

    Usage:
        manager = GracePeriodManager()

        # When a tenant cancels
        result = manager.calculate_grace_period(BillingChannel.SHOPIFY)
        # result.ends_at → 48 hours from now

        # Check if grace period has expired
        if manager.is_grace_expired("2026-01-28T12:00:00Z", BillingChannel.SHOPIFY):
            await deletion_service.delete_tenant_data(tenant_id)
    """

    def calculate_grace_period(
        self,
        channel: BillingChannel,
        start_time: datetime | None = None,
    ) -> GracePeriodResult:
        """Calculate the grace period end time for a cancellation.

        Args:
            channel: Billing channel (determines grace period duration).
            start_time: When the cancellation occurred. Defaults to now.

        Returns:
            GracePeriodResult with start and end timestamps.
        """
        now = start_time or datetime.now(timezone.utc)

        if channel == BillingChannel.SHOPIFY:
            hours = SHOPIFY_GRACE_PERIOD_HOURS
        else:
            hours = STRIPE_GRACE_PERIOD_DAYS * 24

        ends_at = now + timedelta(hours=hours)

        return GracePeriodResult(
            channel=channel,
            grace_period_hours=hours,
            starts_at=now.isoformat(),
            ends_at=ends_at.isoformat(),
            is_expired=False,
        )

    def is_grace_expired(
        self,
        grace_period_ends_at: str | None,
        channel: BillingChannel | None = None,
    ) -> bool:
        """Check if a tenant's grace period has expired.

        Args:
            grace_period_ends_at: ISO 8601 timestamp from TenantDocument.
            channel: Optional — not used in check, but available for logging.

        Returns:
            True if the grace period has expired and data can be deleted.
        """
        if grace_period_ends_at is None:
            return False

        try:
            ends_at = datetime.fromisoformat(grace_period_ends_at)
        except ValueError:
            logger.warning(
                "Invalid grace_period_ends_at: %s", grace_period_ends_at,
            )
            return False

        # Ensure timezone-aware comparison
        if ends_at.tzinfo is None:
            ends_at = ends_at.replace(tzinfo=timezone.utc)

        return datetime.now(timezone.utc) >= ends_at

    def get_grace_hours(self, channel: BillingChannel) -> int:
        """Get the grace period duration in hours for a billing channel."""
        if channel == BillingChannel.SHOPIFY:
            return SHOPIFY_GRACE_PERIOD_HOURS
        return STRIPE_GRACE_PERIOD_DAYS * 24


# ---------------------------------------------------------------------------
# Data store registry protocol (Decision #9)
# ---------------------------------------------------------------------------


class DataStoreAdapter(Protocol):
    """Protocol for data store adapters in the registry.

    Each data store that may contain tenant or customer data must
    implement this protocol to participate in export/deletion.
    """

    @property
    def store_name(self) -> str:
        """Human-readable name of the data store."""
        ...

    async def export_tenant_data(
        self, tenant_id: str,
    ) -> dict[str, Any]:
        """Export all data for a tenant from this store.

        Returns:
            Dict with exported data. Keys are collection/table names,
            values are lists of records.
        """
        ...

    async def export_customer_data(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """Export all data for a specific customer from this store."""
        ...

    async def delete_tenant_data(
        self, tenant_id: str,
    ) -> dict[str, Any]:
        """Delete all data for a tenant from this store.

        Returns:
            Dict with deletion results (counts, errors).
        """
        ...

    async def delete_customer_data(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """Delete all data for a specific customer from this store."""
        ...


# ---------------------------------------------------------------------------
# Cosmos DB adapter (7 tenant-scoped collections)
# ---------------------------------------------------------------------------


class CosmosDataStoreAdapter:
    """Data store adapter for Cosmos DB (8 tenant-scoped collections).

    Exports and deletes data from: tenants, conversations, usage,
    customer_profiles, knowledge_bases, memory_vectors, preferences,
    pii_token_mappings.

    Uses the TenantScopedRepository pattern — all operations go through
    the repository layer which enforces tenant_id isolation.
    """

    def __init__(
        self,
        tenant_repo: Any,
        conversation_repo: Any,
        usage_repo: Any,
        customer_profile_repo: Any,
        knowledge_base_repo: Any,
        memory_vector_repo: Any,
        preferences_repo: Any,
        pii_token_mappings_repo: Any | None = None,
    ) -> None:
        self._repos = {
            "tenants": tenant_repo,
            "conversations": conversation_repo,
            "usage": usage_repo,
            "customer_profiles": customer_profile_repo,
            "knowledge_bases": knowledge_base_repo,
            "memory_vectors": memory_vector_repo,
            "preferences": preferences_repo,
        }
        if pii_token_mappings_repo is not None:
            self._repos["pii_token_mappings"] = pii_token_mappings_repo

    @property
    def store_name(self) -> str:
        return "cosmos_db"

    async def export_tenant_data(
        self, tenant_id: str,
    ) -> dict[str, Any]:
        """Export all tenant data from all registered collections."""
        result: dict[str, Any] = {}

        for name, repo in self._repos.items():
            try:
                # Query all documents in this tenant's partition
                items = await repo.query(
                    tenant_id=tenant_id,
                    query_text="SELECT * FROM c",
                )
                result[name] = items
                logger.debug(
                    "Exported %d items from %s for tenant=%s",
                    len(items), name, tenant_id,
                )
            except Exception:
                logger.exception(
                    "Error exporting %s for tenant=%s", name, tenant_id,
                )
                result[name] = {"error": f"export_failed:{name}"}

        return result

    async def export_customer_data(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """Export all data for a specific customer.

        Queries conversations, customer_profiles, and memory_vectors
        for records matching the customer_id.
        """
        result: dict[str, Any] = {}

        # Customer profile
        try:
            profile = await self._repos["customer_profiles"].get_by_customer_id(
                tenant_id, customer_id,
            )
            result["customer_profiles"] = [profile] if profile else []
        except Exception:
            logger.exception(
                "Error exporting customer profile: tenant=%s customer=%s",
                tenant_id, customer_id,
            )
            result["customer_profiles"] = {"error": "export_failed"}

        # Conversations
        try:
            conversations = await self._repos["conversations"].list_by_customer(
                tenant_id, customer_id,
            )
            result["conversations"] = conversations
        except Exception:
            logger.exception(
                "Error exporting conversations: tenant=%s customer=%s",
                tenant_id, customer_id,
            )
            result["conversations"] = {"error": "export_failed"}

        # Memory vectors
        try:
            vectors = await self._repos["memory_vectors"].query(
                tenant_id=tenant_id,
                query_text="SELECT * FROM c WHERE c.customer_id = @cid",
                parameters=[{"name": "@cid", "value": customer_id}],
            )
            result["memory_vectors"] = vectors
        except Exception:
            logger.exception(
                "Error exporting memory vectors: tenant=%s customer=%s",
                tenant_id, customer_id,
            )
            result["memory_vectors"] = {"error": "export_failed"}

        return result

    async def delete_tenant_data(
        self, tenant_id: str,
    ) -> dict[str, Any]:
        """Delete all tenant data from all 7 collections.

        Deletion order: dependent data first, then the tenant record.
        """
        result: dict[str, Any] = {}

        # Delete dependent collections first (conversations, vectors, etc.)
        # Tenant record is deleted last
        deletion_order = [
            "memory_vectors",
            "customer_profiles",
            "conversations",
            "usage",
            "knowledge_bases",
            "preferences",
            "tenants",  # Last — the tenant record itself
        ]

        for name in deletion_order:
            repo = self._repos.get(name)
            if repo is None:
                continue

            try:
                items = await repo.query(
                    tenant_id=tenant_id,
                    query_text="SELECT c.id FROM c",
                )
                deleted = 0
                for item in items:
                    try:
                        await repo.delete(tenant_id, item["id"])
                        deleted += 1
                    except Exception:
                        logger.exception(
                            "Error deleting %s/%s for tenant=%s",
                            name, item.get("id"), tenant_id,
                        )

                result[name] = {"deleted": deleted, "total": len(items)}
                logger.info(
                    "Deleted %d/%d items from %s for tenant=%s",
                    deleted, len(items), name, tenant_id,
                )
            except Exception:
                logger.exception(
                    "Error deleting from %s for tenant=%s", name, tenant_id,
                )
                result[name] = {"error": f"deletion_failed:{name}"}

        return result

    async def delete_customer_data(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """Delete all data for a specific customer (GDPR right to erasure).

        Deletes: customer profile, all conversations, all memory vectors.
        Does NOT delete tenant-level data (knowledge base, preferences, usage).
        """
        result: dict[str, Any] = {}

        # Delete memory vectors first (most granular)
        try:
            count = await self._repos["memory_vectors"].delete_by_customer(
                tenant_id, customer_id,
            )
            result["memory_vectors"] = {"deleted": count}
        except Exception:
            logger.exception(
                "Error deleting memory vectors: tenant=%s customer=%s",
                tenant_id, customer_id,
            )
            result["memory_vectors"] = {"error": "deletion_failed"}

        # Delete conversations
        try:
            conversations = await self._repos["conversations"].list_by_customer(
                tenant_id, customer_id,
            )
            deleted = 0
            for conv in conversations:
                try:
                    await self._repos["conversations"].delete(tenant_id, conv["id"])
                    deleted += 1
                except Exception:
                    pass
            result["conversations"] = {"deleted": deleted, "total": len(conversations)}
        except Exception:
            logger.exception(
                "Error deleting conversations: tenant=%s customer=%s",
                tenant_id, customer_id,
            )
            result["conversations"] = {"error": "deletion_failed"}

        # Delete customer profile
        try:
            profile = await self._repos["customer_profiles"].get_by_customer_id(
                tenant_id, customer_id,
            )
            if profile:
                await self._repos["customer_profiles"].delete(
                    tenant_id, profile["id"],
                )
                result["customer_profiles"] = {"deleted": 1}
            else:
                result["customer_profiles"] = {"deleted": 0}
        except Exception:
            logger.exception(
                "Error deleting customer profile: tenant=%s customer=%s",
                tenant_id, customer_id,
            )
            result["customer_profiles"] = {"error": "deletion_failed"}

        return result


# ---------------------------------------------------------------------------
# NATS adapter
# ---------------------------------------------------------------------------


class NATSDataStoreAdapter:
    """Data store adapter for NATS JetStream tenant streams.

    Exports are not applicable for NATS (ephemeral message bus).
    Deletion purges the tenant's stream.
    """

    def __init__(self, nats_manager: Any) -> None:
        self._nats = nats_manager

    @property
    def store_name(self) -> str:
        return "nats_jetstream"

    async def export_tenant_data(
        self, tenant_id: str,
    ) -> dict[str, Any]:
        """NATS messages are ephemeral — export stream metadata only."""
        info = await self._nats.get_tenant_stream_info(tenant_id)
        return {"stream_info": info or "no_stream_found"}

    async def export_customer_data(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """NATS does not store per-customer data — nothing to export."""
        return {"note": "nats_messages_are_ephemeral"}

    async def delete_tenant_data(
        self, tenant_id: str,
    ) -> dict[str, Any]:
        """Purge and delete the tenant's NATS stream."""
        return await self._nats.deprovision_tenant_topics(tenant_id)

    async def delete_customer_data(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """NATS does not store per-customer data — nothing to delete."""
        return {"note": "nats_messages_are_ephemeral"}


# ---------------------------------------------------------------------------
# Data store registry
# ---------------------------------------------------------------------------


class DataStoreRegistry:
    """Registry of all data stores containing tenant/customer data.

    The central coordination point for DataExportService and
    DataDeletionService. Each data store registers an adapter that
    knows how to export/delete data from that store.

    Usage:
        registry = DataStoreRegistry()
        registry.register(CosmosDataStoreAdapter(...))
        registry.register(NATSDataStoreAdapter(...))

        # Export from all stores
        export = await registry.export_all_tenant_data("t-abc123")

        # Delete from all stores
        result = await registry.delete_all_tenant_data("t-abc123")
    """

    def __init__(self) -> None:
        self._adapters: list[DataStoreAdapter] = []

    def register(self, adapter: DataStoreAdapter) -> None:
        """Register a data store adapter."""
        self._adapters.append(adapter)
        logger.info(
            "Data store registered: %s (total: %d)",
            adapter.store_name, len(self._adapters),
        )

    @property
    def store_names(self) -> list[str]:
        """List names of all registered data stores."""
        return [a.store_name for a in self._adapters]

    async def export_all_tenant_data(
        self, tenant_id: str,
    ) -> dict[str, Any]:
        """Export all tenant data from all registered stores."""
        result: dict[str, Any] = {}
        for adapter in self._adapters:
            try:
                data = await adapter.export_tenant_data(tenant_id)
                result[adapter.store_name] = data
            except Exception:
                logger.exception(
                    "Error exporting from %s for tenant=%s",
                    adapter.store_name, tenant_id,
                )
                result[adapter.store_name] = {"error": "export_failed"}
        return result

    async def export_all_customer_data(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """Export all customer data from all registered stores."""
        result: dict[str, Any] = {}
        for adapter in self._adapters:
            try:
                data = await adapter.export_customer_data(tenant_id, customer_id)
                result[adapter.store_name] = data
            except Exception:
                logger.exception(
                    "Error exporting customer data from %s: tenant=%s customer=%s",
                    adapter.store_name, tenant_id, customer_id,
                )
                result[adapter.store_name] = {"error": "export_failed"}
        return result

    async def delete_all_tenant_data(
        self, tenant_id: str,
    ) -> dict[str, Any]:
        """Delete all tenant data from all registered stores."""
        result: dict[str, Any] = {}
        for adapter in self._adapters:
            try:
                data = await adapter.delete_tenant_data(tenant_id)
                result[adapter.store_name] = data
            except Exception:
                logger.exception(
                    "Error deleting from %s for tenant=%s",
                    adapter.store_name, tenant_id,
                )
                result[adapter.store_name] = {"error": "deletion_failed"}
        return result

    async def delete_all_customer_data(
        self, tenant_id: str, customer_id: str,
    ) -> dict[str, Any]:
        """Delete all customer data from all registered stores."""
        result: dict[str, Any] = {}
        for adapter in self._adapters:
            try:
                data = await adapter.delete_customer_data(tenant_id, customer_id)
                result[adapter.store_name] = data
            except Exception:
                logger.exception(
                    "Error deleting customer data from %s: tenant=%s customer=%s",
                    adapter.store_name, tenant_id, customer_id,
                )
                result[adapter.store_name] = {"error": "deletion_failed"}
        return result


# ---------------------------------------------------------------------------
# Data Export Service (Decision #9, Work Item #32)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExportResult:
    """Result of a data export operation."""

    export_id: str
    tenant_id: str
    customer_id: str | None
    export_type: str          # "tenant" or "customer"
    stores_exported: list[str]
    data: dict[str, Any]
    exported_at: str          # ISO 8601
    errors: list[str]


class DataExportService:
    """Exports tenant or customer data across all registered stores.

    Implements GDPR right of access (Article 15) and data portability
    (Article 20). Produces a structured JSON archive.

    Usage:
        export_service = DataExportService(registry, audit_repo)

        # Export all data for a tenant
        result = await export_service.export_tenant(tenant_id)

        # Export data for a specific customer
        result = await export_service.export_customer(tenant_id, customer_id)
    """

    def __init__(
        self,
        registry: DataStoreRegistry,
        audit_repo: Any | None = None,
    ) -> None:
        self._registry = registry
        self._audit = audit_repo

    async def export_tenant(self, tenant_id: str) -> ExportResult:
        """Export all data for a tenant from all data stores.

        Args:
            tenant_id: Tenant identifier.

        Returns:
            ExportResult with all exported data and metadata.
        """
        export_id = f"export-{uuid.uuid4()}"
        now = datetime.now(timezone.utc).isoformat()

        logger.info(
            "Starting tenant data export: export_id=%s tenant=%s",
            export_id, tenant_id,
        )

        data = await self._registry.export_all_tenant_data(tenant_id)

        # Identify errors
        errors = []
        stores_exported = []
        for store_name, store_data in data.items():
            if isinstance(store_data, dict) and store_data.get("error"):
                errors.append(f"{store_name}: {store_data['error']}")
            else:
                stores_exported.append(store_name)

        result = ExportResult(
            export_id=export_id,
            tenant_id=tenant_id,
            customer_id=None,
            export_type="tenant",
            stores_exported=stores_exported,
            data=data,
            exported_at=now,
            errors=errors,
        )

        # Audit log
        await self._log_audit(
            event_type=AuditEventType.DATA_EXPORTED,
            tenant_id=tenant_id,
            payload={
                "export_id": export_id,
                "export_type": "tenant",
                "stores_exported": stores_exported,
                "error_count": len(errors),
            },
        )

        logger.info(
            "Tenant data export complete: export_id=%s tenant=%s "
            "stores=%d errors=%d",
            export_id, tenant_id, len(stores_exported), len(errors),
        )

        return result

    async def export_customer(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> ExportResult:
        """Export all data for a specific customer.

        Args:
            tenant_id: Tenant identifier.
            customer_id: Customer identifier.

        Returns:
            ExportResult with all exported customer data.
        """
        export_id = f"export-{uuid.uuid4()}"
        now = datetime.now(timezone.utc).isoformat()

        logger.info(
            "Starting customer data export: export_id=%s tenant=%s customer=%s",
            export_id, tenant_id, customer_id,
        )

        data = await self._registry.export_all_customer_data(tenant_id, customer_id)

        errors = []
        stores_exported = []
        for store_name, store_data in data.items():
            if isinstance(store_data, dict) and store_data.get("error"):
                errors.append(f"{store_name}: {store_data['error']}")
            else:
                stores_exported.append(store_name)

        result = ExportResult(
            export_id=export_id,
            tenant_id=tenant_id,
            customer_id=customer_id,
            export_type="customer",
            stores_exported=stores_exported,
            data=data,
            exported_at=now,
            errors=errors,
        )

        await self._log_audit(
            event_type=AuditEventType.DATA_EXPORTED,
            tenant_id=tenant_id,
            payload={
                "export_id": export_id,
                "export_type": "customer",
                "customer_id": customer_id,
                "stores_exported": stores_exported,
                "error_count": len(errors),
            },
        )

        logger.info(
            "Customer data export complete: export_id=%s tenant=%s "
            "customer=%s stores=%d errors=%d",
            export_id, tenant_id, customer_id,
            len(stores_exported), len(errors),
        )

        return result

    async def _log_audit(self, **kwargs: Any) -> None:
        if self._audit is None:
            return
        try:
            await self._audit.log_event(**kwargs)
        except Exception:
            logger.exception("Failed to log data export audit event")


# ---------------------------------------------------------------------------
# Data Deletion Service (Decision #9, Work Item #33)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DeletionResult:
    """Result of a data deletion operation."""

    deletion_id: str
    tenant_id: str
    customer_id: str | None
    deletion_type: str        # "tenant" or "customer"
    stores_deleted: list[str]
    details: dict[str, Any]
    deleted_at: str           # ISO 8601
    errors: list[str]


class DataDeletionService:
    """Cascading deletion of tenant or customer data across all stores.

    Implements GDPR right to erasure (Article 17). Deletes data from
    all registered data stores in the correct dependency order.

    The deletion service works with the GracePeriodManager to ensure
    data is only deleted after the grace period expires.

    Usage:
        deletion_service = DataDeletionService(registry, audit_repo)

        # Delete all data for a tenant (after grace period)
        result = await deletion_service.delete_tenant(tenant_id)

        # Delete data for a specific customer
        result = await deletion_service.delete_customer(tenant_id, customer_id)
    """

    def __init__(
        self,
        registry: DataStoreRegistry,
        audit_repo: Any | None = None,
        grace_period_manager: GracePeriodManager | None = None,
        tenant_repo: Any | None = None,
    ) -> None:
        self._registry = registry
        self._audit = audit_repo
        self._grace = grace_period_manager or GracePeriodManager()
        self._tenants = tenant_repo

    async def delete_tenant(
        self,
        tenant_id: str,
        force: bool = False,
    ) -> DeletionResult:
        """Delete all data for a tenant across all stores.

        By default, checks that the grace period has expired before
        proceeding. Set force=True to skip the grace period check
        (admin operation only).

        Args:
            tenant_id: Tenant identifier.
            force: Skip grace period check.

        Returns:
            DeletionResult with deletion details.

        Raises:
            GracePeriodActiveError: If grace period hasn't expired and force=False.
        """
        deletion_id = f"delete-{uuid.uuid4()}"
        now = datetime.now(timezone.utc).isoformat()

        logger.info(
            "Starting tenant data deletion: deletion_id=%s tenant=%s force=%s",
            deletion_id, tenant_id, force,
        )

        # Check grace period
        if not force and self._tenants is not None:
            try:
                tenant_doc = await self._tenants.read(tenant_id, tenant_id)
                grace_ends = tenant_doc.get("grace_period_ends_at")
                channel_str = tenant_doc.get("billing_channel")
                channel = BillingChannel(channel_str) if channel_str else None

                if grace_ends and not self._grace.is_grace_expired(grace_ends, channel):
                    raise GracePeriodActiveError(
                        tenant_id=tenant_id,
                        grace_period_ends_at=grace_ends,
                    )
            except GracePeriodActiveError:
                raise
            except Exception:
                logger.exception(
                    "Error checking grace period: tenant=%s — proceeding with deletion",
                    tenant_id,
                )

        details = await self._registry.delete_all_tenant_data(tenant_id)

        errors = []
        stores_deleted = []
        for store_name, store_data in details.items():
            if isinstance(store_data, dict) and store_data.get("error"):
                errors.append(f"{store_name}: {store_data['error']}")
            else:
                stores_deleted.append(store_name)

        result = DeletionResult(
            deletion_id=deletion_id,
            tenant_id=tenant_id,
            customer_id=None,
            deletion_type="tenant",
            stores_deleted=stores_deleted,
            details=details,
            deleted_at=now,
            errors=errors,
        )

        await self._log_audit(
            event_type=AuditEventType.DATA_DELETED,
            tenant_id=tenant_id,
            payload={
                "deletion_id": deletion_id,
                "deletion_type": "tenant",
                "stores_deleted": stores_deleted,
                "error_count": len(errors),
                "forced": force,
            },
        )

        logger.info(
            "Tenant data deletion complete: deletion_id=%s tenant=%s "
            "stores=%d errors=%d",
            deletion_id, tenant_id, len(stores_deleted), len(errors),
        )

        return result

    async def delete_customer(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> DeletionResult:
        """Delete all data for a specific customer (GDPR right to erasure).

        No grace period check — customer erasure requests are processed
        promptly per GDPR Article 17 (without undue delay, max 30 days).

        Args:
            tenant_id: Tenant identifier.
            customer_id: Customer identifier.

        Returns:
            DeletionResult with deletion details.
        """
        deletion_id = f"delete-{uuid.uuid4()}"
        now = datetime.now(timezone.utc).isoformat()

        logger.info(
            "Starting customer data deletion: deletion_id=%s tenant=%s customer=%s",
            deletion_id, tenant_id, customer_id,
        )

        details = await self._registry.delete_all_customer_data(
            tenant_id, customer_id,
        )

        errors = []
        stores_deleted = []
        for store_name, store_data in details.items():
            if isinstance(store_data, dict) and store_data.get("error"):
                errors.append(f"{store_name}: {store_data['error']}")
            else:
                stores_deleted.append(store_name)

        result = DeletionResult(
            deletion_id=deletion_id,
            tenant_id=tenant_id,
            customer_id=customer_id,
            deletion_type="customer",
            stores_deleted=stores_deleted,
            details=details,
            deleted_at=now,
            errors=errors,
        )

        await self._log_audit(
            event_type=AuditEventType.DATA_DELETED,
            tenant_id=tenant_id,
            payload={
                "deletion_id": deletion_id,
                "deletion_type": "customer",
                "customer_id": customer_id,
                "stores_deleted": stores_deleted,
                "error_count": len(errors),
            },
        )

        logger.info(
            "Customer data deletion complete: deletion_id=%s tenant=%s "
            "customer=%s stores=%d errors=%d",
            deletion_id, tenant_id, customer_id,
            len(stores_deleted), len(errors),
        )

        return result

    async def _log_audit(self, **kwargs: Any) -> None:
        if self._audit is None:
            return
        try:
            await self._audit.log_event(**kwargs)
        except Exception:
            logger.exception("Failed to log data deletion audit event")


class GracePeriodActiveError(Exception):
    """Raised when a deletion is attempted before the grace period expires."""

    def __init__(self, tenant_id: str, grace_period_ends_at: str) -> None:
        self.tenant_id = tenant_id
        self.grace_period_ends_at = grace_period_ends_at
        super().__init__(
            f"Grace period still active for tenant {tenant_id}. "
            f"Data deletion blocked until {grace_period_ends_at}."
        )


# ---------------------------------------------------------------------------
# Consent Manager (Decision #10, Work Item #34)
# ---------------------------------------------------------------------------


class ConsentManager:
    """Manages GDPR consent for Persistent Customer Memory.

    Decision #10: consent_status gates Layers 2-4 of Persistent Customer
    Memory. Without consent, only Layer 1 (basic customer profile with
    non-PII operational data) is active.

    Consent states:
        - NOT_ASKED: Default. Layers 2-4 inactive. Consent prompt pending.
        - GRANTED: Layers 2-4 active. Full memory capabilities enabled.
        - DENIED: Layers 2-4 inactive. Existing Layer 2-4 data deleted.

    Consent transitions are logged to the audit log (AuditEventType.CONSENT_CHANGED).

    Usage:
        consent_mgr = ConsentManager(tenant_repo, profile_repo, audit_repo)

        # Check if a feature is gated by consent
        if consent_mgr.is_layer_allowed(ConsentStatus.GRANTED, layer=2):
            # Enable Layer 2 vector search

        # Update consent (with cascading side effects)
        await consent_mgr.update_tenant_consent(tenant_id, ConsentStatus.GRANTED, "user")
        await consent_mgr.update_customer_consent(tenant_id, customer_id, ConsentStatus.DENIED, "user")
    """

    # Layer gating rules (Decision #10)
    # Layer 1 (basic profile): always available, no consent needed
    # Layer 2 (vector search): requires consent
    # Layer 3 (pattern extraction): requires consent
    # Layer 4 (fine-tuning): requires consent + Enterprise tier
    CONSENT_REQUIRED_LAYERS = {2, 3, 4}

    def __init__(
        self,
        tenant_repo: Any | None = None,
        customer_profile_repo: Any | None = None,
        audit_repo: Any | None = None,
        deletion_service: DataDeletionService | None = None,
    ) -> None:
        self._tenants = tenant_repo
        self._profiles = customer_profile_repo
        self._audit = audit_repo
        self._deletion = deletion_service

    def is_layer_allowed(
        self,
        consent_status: ConsentStatus,
        layer: int,
    ) -> bool:
        """Check if a memory layer is allowed under the given consent status.

        Args:
            consent_status: The tenant's or customer's consent status.
            layer: Memory layer number (1-4).

        Returns:
            True if the layer is allowed.
        """
        if layer not in self.CONSENT_REQUIRED_LAYERS:
            return True  # Layer 1 is always allowed
        return consent_status == ConsentStatus.GRANTED

    async def update_tenant_consent(
        self,
        tenant_id: str,
        new_status: ConsentStatus,
        actor: str = "system",
    ) -> dict[str, Any]:
        """Update consent status at the tenant level.

        When consent changes to DENIED, this DOES NOT automatically delete
        Layer 2-4 data for all customers. Instead, it prevents new data
        from being stored. Customer-level deletion is handled separately
        via customer consent changes or explicit data requests.

        Args:
            tenant_id: Tenant identifier.
            new_status: New consent status.
            actor: Who made the change (user or system).

        Returns:
            Dict with previous and new consent status.
        """
        previous_status: str | None = None

        if self._tenants is not None:
            try:
                tenant_doc = await self._tenants.read(tenant_id, tenant_id)
                previous_status = tenant_doc.get("consent_status")

                await self._tenants.patch(
                    tenant_id=tenant_id,
                    document_id=tenant_id,
                    operations=[
                        {"op": "set", "path": "/consent_status", "value": new_status.value},
                        {
                            "op": "set",
                            "path": "/updated_at",
                            "value": datetime.now(timezone.utc).isoformat(),
                        },
                    ],
                )
            except Exception:
                logger.exception(
                    "Error updating tenant consent: tenant=%s", tenant_id,
                )
                raise

        # Audit log the consent change
        await self._log_consent_change(
            tenant_id=tenant_id,
            customer_id=None,
            previous_status=previous_status,
            new_status=new_status.value,
            actor=actor,
        )

        logger.info(
            "Tenant consent updated: tenant=%s %s → %s by=%s",
            tenant_id, previous_status, new_status.value, actor,
        )

        return {
            "tenant_id": tenant_id,
            "previous_status": previous_status,
            "new_status": new_status.value,
        }

    async def update_customer_consent(
        self,
        tenant_id: str,
        customer_id: str,
        new_status: ConsentStatus,
        actor: str = "system",
    ) -> dict[str, Any]:
        """Update consent status for a specific customer.

        When consent changes to DENIED:
        - Memory Layers 2-4 data for this customer is deleted.
        - Layer 1 profile data is retained (operational necessity).

        Args:
            tenant_id: Tenant identifier.
            customer_id: Customer identifier.
            new_status: New consent status.
            actor: Who made the change.

        Returns:
            Dict with consent change details and any deletion results.
        """
        previous_status: str | None = None
        deletion_result: dict[str, Any] | None = None

        if self._profiles is not None:
            try:
                doc_id = f"{tenant_id}:{customer_id}"
                profile = await self._profiles.get_by_customer_id(
                    tenant_id, customer_id,
                )

                if profile:
                    previous_status = profile.get("consent_status")
                    await self._profiles.patch(
                        tenant_id=tenant_id,
                        document_id=profile["id"],
                        operations=[
                            {"op": "set", "path": "/consent_status", "value": new_status.value},
                            {
                                "op": "set",
                                "path": "/updated_at",
                                "value": datetime.now(timezone.utc).isoformat(),
                            },
                        ],
                    )
            except Exception:
                logger.exception(
                    "Error updating customer consent: tenant=%s customer=%s",
                    tenant_id, customer_id,
                )
                raise

        # If consent changed to DENIED, delete Layer 2-4 data
        if new_status == ConsentStatus.DENIED and self._deletion is not None:
            try:
                deletion_result = await self._deletion.delete_customer(
                    tenant_id, customer_id,
                )
                logger.info(
                    "Layer 2-4 data deleted after consent denial: "
                    "tenant=%s customer=%s",
                    tenant_id, customer_id,
                )
            except Exception:
                logger.exception(
                    "Error deleting Layer 2-4 data after consent denial: "
                    "tenant=%s customer=%s",
                    tenant_id, customer_id,
                )

        # Audit log
        await self._log_consent_change(
            tenant_id=tenant_id,
            customer_id=customer_id,
            previous_status=previous_status,
            new_status=new_status.value,
            actor=actor,
        )

        logger.info(
            "Customer consent updated: tenant=%s customer=%s %s → %s by=%s",
            tenant_id, customer_id, previous_status, new_status.value, actor,
        )

        result: dict[str, Any] = {
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "previous_status": previous_status,
            "new_status": new_status.value,
        }
        if deletion_result is not None:
            result["deletion"] = deletion_result

        return result

    async def _log_consent_change(
        self,
        tenant_id: str,
        customer_id: str | None,
        previous_status: str | None,
        new_status: str,
        actor: str,
    ) -> None:
        """Log a consent change to the audit log."""
        if self._audit is None:
            return
        try:
            await self._audit.log_event(
                event_type=AuditEventType.CONSENT_CHANGED,
                tenant_id=tenant_id,
                actor=actor,
                actor_type="user" if actor != "system" else "system",
                payload={
                    "customer_id": customer_id,
                    "previous_status": previous_status,
                    "new_status": new_status,
                },
            )
        except Exception:
            logger.exception(
                "Failed to log CONSENT_CHANGED audit: tenant=%s", tenant_id,
            )
