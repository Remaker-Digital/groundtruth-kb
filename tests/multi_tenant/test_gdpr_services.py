"""GDPR services tests — P1 pre-launch (§5.2).

Test IDs: GDPR-01 through GDPR-30.

Validates:
    - PiiScrubber: field-level scrubbing, regex detection, recursive traversal,
      immutability, classification, free-text scrubbing
    - GracePeriodManager: Shopify 48hr, Stripe 30-day, expiry checks
    - DataStoreRegistry: adapter registration and retrieval
    - DataExportService: tenant + customer export, audit logging
    - DataDeletionService: tenant + customer deletion, grace period enforcement,
      audit logging, cascading order
    - ConsentManager: grant/deny, auto-deletion on denial, audit logging
    - CosmosDataStoreAdapter: export/delete across 7 collections
    - NATSDataStoreAdapter: stream purge/delete

Module under test: src/multi_tenant/gdpr_services.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.multi_tenant.cosmos_schema import (
    AuditEventType,
    BillingChannel,
    ConsentStatus,
    PiiClassification,
)
from src.multi_tenant.gdpr_services import (
    ConsentManager,
    CosmosDataStoreAdapter,
    DataDeletionService,
    DataExportService,
    DataStoreRegistry,
    DeletionResult,
    ExportResult,
    GracePeriodActiveError,
    GracePeriodManager,
    GracePeriodResult,
    NATSDataStoreAdapter,
    PiiScrubber,
    SHOPIFY_GRACE_PERIOD_HOURS,
    STRIPE_GRACE_PERIOD_DAYS,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

TENANT_ID = "t-gdpr-001"
CUSTOMER_ID = "cust-abc-123"


@pytest.fixture
def scrubber() -> PiiScrubber:
    """Default PII scrubber with all patterns enabled."""
    return PiiScrubber()


@pytest.fixture
def grace_mgr() -> GracePeriodManager:
    """Grace period manager instance."""
    return GracePeriodManager()


@pytest.fixture
def registry() -> DataStoreRegistry:
    """Empty data store registry."""
    return DataStoreRegistry()


@pytest.fixture
def mock_audit() -> AsyncMock:
    """Mock audit repository with log_event."""
    audit = AsyncMock()
    audit.log_event = AsyncMock()
    return audit


@pytest.fixture
def mock_store_adapter() -> MagicMock:
    """Mock data store adapter implementing the DataStoreAdapter protocol."""
    adapter = MagicMock()
    adapter.store_name = "mock_store"
    adapter.export_tenant_data = AsyncMock(return_value={"items": [{"id": "1"}]})
    adapter.export_customer_data = AsyncMock(return_value={"items": [{"id": "2"}]})
    adapter.delete_tenant_data = AsyncMock(return_value={"deleted": 1})
    adapter.delete_customer_data = AsyncMock(return_value={"deleted": 1})
    return adapter


def _make_mock_repo(name: str) -> AsyncMock:
    """Create a mock repo with standard CRUD methods."""
    repo = AsyncMock()
    repo.query = AsyncMock(return_value=[{"id": f"{name}-item-1", "tenant_id": TENANT_ID}])
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_cosmos_repos() -> dict[str, AsyncMock]:
    """Mock Cosmos DB repositories keyed by constructor parameter names."""
    repos: dict[str, AsyncMock] = {
        "tenant_repo": _make_mock_repo("tenants"),
        "conversation_repo": _make_mock_repo("conversations"),
        "usage_repo": _make_mock_repo("usage"),
        "customer_profile_repo": _make_mock_repo("customer_profiles"),
        "knowledge_base_repo": _make_mock_repo("knowledge_bases"),
        "memory_vector_repo": _make_mock_repo("memory_vectors"),
        "preferences_repo": _make_mock_repo("preferences"),
    }

    # Customer-specific methods
    repos["customer_profile_repo"].get_by_customer_id = AsyncMock(
        return_value={"id": f"{TENANT_ID}:{CUSTOMER_ID}", "tenant_id": TENANT_ID, "consent_status": "not_asked"},
    )
    repos["conversation_repo"].list_by_customer = AsyncMock(
        return_value=[{"id": "conv-1", "tenant_id": TENANT_ID}],
    )
    repos["memory_vector_repo"].delete_by_customer = AsyncMock(return_value=3)

    return repos


# ===========================================================================
# GDPR-01 to GDPR-09: PII Scrubber
# ===========================================================================


class TestPiiScrubber:
    """GDPR-01 through GDPR-09: PII detection and scrubbing."""

    def test_gdpr_01_email_detected_and_scrubbed(self, scrubber: PiiScrubber) -> None:
        """GDPR-01: Email addresses in free-text fields are scrubbed."""
        data = {"description": "Contact john@example.com for details"}
        result = scrubber.scrub(data)
        assert "john@example.com" not in result["description"]
        assert "[REDACTED:email]" in result["description"]

    def test_gdpr_02_phone_detected_and_scrubbed(self, scrubber: PiiScrubber) -> None:
        """GDPR-02: Phone numbers in free-text fields are scrubbed."""
        data = {"notes": "Call +1-555-123-4567 tomorrow"}
        result = scrubber.scrub(data)
        assert "+1-555-123-4567" not in result["notes"]
        assert "[REDACTED:phone]" in result["notes"]

    def test_gdpr_03_nested_dict_recursion(self, scrubber: PiiScrubber) -> None:
        """GDPR-03: PII in nested dicts is scrubbed recursively."""
        data = {
            "level1": {
                "level2": {
                    "email": "nested@example.com",
                    "safe_field": "no PII here",
                },
            },
        }
        result = scrubber.scrub(data)
        assert "[REDACTED:" in result["level1"]["level2"]["email"]
        assert result["level1"]["level2"]["safe_field"] == "no PII here"

    def test_gdpr_04_list_items_scrubbed(self, scrubber: PiiScrubber) -> None:
        """GDPR-04: PII in list items is scrubbed."""
        data = {
            "contacts": [
                {"email": "alice@test.com", "role": "admin"},
                {"email": "bob@test.com", "role": "user"},
            ],
        }
        result = scrubber.scrub(data)
        for contact in result["contacts"]:
            assert "[REDACTED:" in contact["email"]
            # Non-PII fields preserved
            assert contact["role"] in ("admin", "user")

    def test_gdpr_04_list_strings_scrubbed(self, scrubber: PiiScrubber) -> None:
        """GDPR-04 supplement: Free-text strings in lists are scrubbed."""
        # Use a non-PII field name to test list-of-strings scrubbing
        data = {"log_entries": ["Contact jane@example.com", "Normal text"]}
        result = scrubber.scrub(data)
        assert "[REDACTED:email]" in result["log_entries"][0]
        assert result["log_entries"][1] == "Normal text"

    def test_gdpr_05_direct_classification_scrubbed(self, scrubber: PiiScrubber) -> None:
        """GDPR-05: DIRECT PII fields are scrubbed with classification marker."""
        data = {
            "customer_email": "test@example.com",
            "name": "John Doe",
            "phone": "+1234567890",
            "billing_address": "123 Main St",
        }
        result = scrubber.scrub(data)
        for field in ("customer_email", "name", "phone", "billing_address"):
            assert result[field] == f"[REDACTED:{PiiClassification.DIRECT.value}]"

    def test_gdpr_06_indirect_classification_scrubbed(self, scrubber: PiiScrubber) -> None:
        """GDPR-06: INDIRECT PII fields are scrubbed with classification marker."""
        data = {
            "ip_address": "192.168.1.1",
            "device_id": "dev-abc",
            "stripe_customer_id": "cus_12345",
        }
        result = scrubber.scrub(data)
        for field in ("ip_address", "device_id", "stripe_customer_id"):
            assert result[field] == f"[REDACTED:{PiiClassification.INDIRECT.value}]"

    def test_gdpr_07_sensitive_classification_scrubbed(self, scrubber: PiiScrubber) -> None:
        """GDPR-07: SENSITIVE PII fields are scrubbed with classification marker."""
        data = {
            "purchase_history": [{"item": "widget"}],
            "transcript": "Hello, I need help",
            "messages": [{"text": "How do I..."}],
        }
        result = scrubber.scrub(data)
        for field in ("purchase_history", "transcript", "messages"):
            assert result[field] == f"[REDACTED:{PiiClassification.SENSITIVE.value}]"

    def test_gdpr_08_non_destructive(self, scrubber: PiiScrubber) -> None:
        """GDPR-08: scrub() returns new dict — original is unchanged."""
        original = {
            "email": "original@test.com",
            "nested": {"phone": "+1234567890"},
            "safe": "preserved",
        }
        # Deep copy reference values
        original_email = original["email"]
        original_phone = original["nested"]["phone"]

        result = scrubber.scrub(original)

        # Original unchanged
        assert original["email"] == original_email
        assert original["nested"]["phone"] == original_phone

        # Result is different object
        assert result is not original
        assert result["email"] != original_email

    def test_gdpr_09_scrub_text(self, scrubber: PiiScrubber) -> None:
        """GDPR-09: scrub_text() redacts email and phone from log messages."""
        text = "User john@example.com called from +1-555-0100"
        result = scrubber.scrub_text(text)
        assert "john@example.com" not in result
        assert "[REDACTED:email]" in result
        assert "[REDACTED:phone]" in result

    def test_gdpr_09_scrub_text_disabled(self) -> None:
        """GDPR-09 supplement: scrub_text respects redact_free_text=False."""
        scrubber = PiiScrubber(redact_free_text=False)
        text = "john@example.com"
        assert scrubber.scrub_text(text) == text

    def test_classify_field(self, scrubber: PiiScrubber) -> None:
        """Supplement: classify_field returns correct classification."""
        assert scrubber.classify_field("email") == PiiClassification.DIRECT
        assert scrubber.classify_field("ip_address") == PiiClassification.INDIRECT
        assert scrubber.classify_field("transcript") == PiiClassification.SENSITIVE
        assert scrubber.classify_field("unknown_field") == PiiClassification.NONE


# ===========================================================================
# GDPR-10 to GDPR-13: Grace Period Manager
# ===========================================================================


class TestGracePeriodManager:
    """GDPR-10 through GDPR-13: Channel-specific grace periods."""

    def test_gdpr_10_shopify_48hr_grace(self, grace_mgr: GracePeriodManager) -> None:
        """GDPR-10: Shopify tenants get 48-hour grace period."""
        now = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = grace_mgr.calculate_grace_period(BillingChannel.SHOPIFY, start_time=now)

        assert isinstance(result, GracePeriodResult)
        assert result.channel == BillingChannel.SHOPIFY
        assert result.grace_period_hours == SHOPIFY_GRACE_PERIOD_HOURS
        assert result.is_expired is False

        # Verify end time is 48 hours later
        expected_end = now + timedelta(hours=48)
        assert result.ends_at == expected_end.isoformat()

    def test_gdpr_11_stripe_30day_grace(self, grace_mgr: GracePeriodManager) -> None:
        """GDPR-11: Stripe tenants get 30-day grace period."""
        now = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = grace_mgr.calculate_grace_period(BillingChannel.STRIPE, start_time=now)

        assert result.channel == BillingChannel.STRIPE
        assert result.grace_period_hours == STRIPE_GRACE_PERIOD_DAYS * 24

        expected_end = now + timedelta(days=30)
        assert result.ends_at == expected_end.isoformat()

    def test_gdpr_12_not_expired(self, grace_mgr: GracePeriodManager) -> None:
        """GDPR-12: is_grace_expired returns False before expiry."""
        # Set grace end in the future
        future = datetime.now(timezone.utc) + timedelta(hours=24)
        assert grace_mgr.is_grace_expired(future.isoformat()) is False

    def test_gdpr_13_expired(self, grace_mgr: GracePeriodManager) -> None:
        """GDPR-13: is_grace_expired returns True after expiry."""
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        assert grace_mgr.is_grace_expired(past.isoformat()) is True

    def test_grace_expired_none(self, grace_mgr: GracePeriodManager) -> None:
        """Supplement: None grace_period_ends_at returns False."""
        assert grace_mgr.is_grace_expired(None) is False

    def test_grace_expired_invalid(self, grace_mgr: GracePeriodManager) -> None:
        """Supplement: Invalid date string returns False."""
        assert grace_mgr.is_grace_expired("not-a-date") is False

    def test_get_grace_hours(self, grace_mgr: GracePeriodManager) -> None:
        """Supplement: get_grace_hours returns correct values."""
        assert grace_mgr.get_grace_hours(BillingChannel.SHOPIFY) == 48
        assert grace_mgr.get_grace_hours(BillingChannel.STRIPE) == 30 * 24


# ===========================================================================
# GDPR-14: Data Store Registry
# ===========================================================================


class TestDataStoreRegistry:
    """GDPR-14: Registry pattern for data store adapters."""

    def test_gdpr_14_register_and_retrieve(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock,
    ) -> None:
        """GDPR-14: Register adapter and retrieve via store_names."""
        assert len(registry.store_names) == 0

        registry.register(mock_store_adapter)

        assert "mock_store" in registry.store_names
        assert len(registry.store_names) == 1

    def test_gdpr_14_multiple_adapters(self, registry: DataStoreRegistry) -> None:
        """GDPR-14 supplement: Multiple adapters can be registered."""
        for name in ("store_a", "store_b", "store_c"):
            adapter = MagicMock()
            adapter.store_name = name
            registry.register(adapter)

        assert len(registry.store_names) == 3
        assert set(registry.store_names) == {"store_a", "store_b", "store_c"}

    @pytest.mark.asyncio
    async def test_registry_export_all_tenant(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock,
    ) -> None:
        """Supplement: export_all_tenant_data delegates to all adapters."""
        registry.register(mock_store_adapter)
        result = await registry.export_all_tenant_data(TENANT_ID)

        assert "mock_store" in result
        mock_store_adapter.export_tenant_data.assert_awaited_once_with(TENANT_ID)

    @pytest.mark.asyncio
    async def test_registry_delete_all_tenant(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock,
    ) -> None:
        """Supplement: delete_all_tenant_data delegates to all adapters."""
        registry.register(mock_store_adapter)
        result = await registry.delete_all_tenant_data(TENANT_ID)

        assert "mock_store" in result
        mock_store_adapter.delete_tenant_data.assert_awaited_once_with(TENANT_ID)


# ===========================================================================
# GDPR-15 to GDPR-17: Data Export Service
# ===========================================================================


class TestDataExportService:
    """GDPR-15 through GDPR-17: Data export operations."""

    @pytest.mark.asyncio
    async def test_gdpr_15_tenant_export(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock, mock_audit: AsyncMock,
    ) -> None:
        """GDPR-15: Tenant-level export across all stores."""
        registry.register(mock_store_adapter)
        service = DataExportService(registry, audit_repo=mock_audit)

        result = await service.export_tenant(TENANT_ID)

        assert isinstance(result, ExportResult)
        assert result.tenant_id == TENANT_ID
        assert result.export_type == "tenant"
        assert result.customer_id is None
        assert "mock_store" in result.stores_exported
        assert len(result.errors) == 0
        assert result.export_id.startswith("export-")

    @pytest.mark.asyncio
    async def test_gdpr_16_customer_export(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock, mock_audit: AsyncMock,
    ) -> None:
        """GDPR-16: Customer-level export."""
        registry.register(mock_store_adapter)
        service = DataExportService(registry, audit_repo=mock_audit)

        result = await service.export_customer(TENANT_ID, CUSTOMER_ID)

        assert result.export_type == "customer"
        assert result.customer_id == CUSTOMER_ID
        assert result.tenant_id == TENANT_ID
        mock_store_adapter.export_customer_data.assert_awaited_once_with(TENANT_ID, CUSTOMER_ID)

    @pytest.mark.asyncio
    async def test_gdpr_17_export_audit_logged(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock, mock_audit: AsyncMock,
    ) -> None:
        """GDPR-17: DATA_EXPORTED audit event created on export."""
        registry.register(mock_store_adapter)
        service = DataExportService(registry, audit_repo=mock_audit)

        await service.export_tenant(TENANT_ID)

        mock_audit.log_event.assert_awaited_once()
        call_kwargs = mock_audit.log_event.call_args[1]
        assert call_kwargs["event_type"] == AuditEventType.DATA_EXPORTED
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["payload"]["export_type"] == "tenant"

    @pytest.mark.asyncio
    async def test_export_handles_store_error(
        self, registry: DataStoreRegistry, mock_audit: AsyncMock,
    ) -> None:
        """Supplement: Export captures errors from failing adapters."""
        failing_adapter = MagicMock()
        failing_adapter.store_name = "failing_store"
        failing_adapter.export_tenant_data = AsyncMock(side_effect=RuntimeError("boom"))
        registry.register(failing_adapter)

        service = DataExportService(registry, audit_repo=mock_audit)
        result = await service.export_tenant(TENANT_ID)

        assert "failing_store" not in result.stores_exported
        assert any("failing_store" in e for e in result.errors)


# ===========================================================================
# GDPR-18 to GDPR-21: Data Deletion Service
# ===========================================================================


class TestDataDeletionService:
    """GDPR-18 through GDPR-21: Data deletion operations."""

    @pytest.mark.asyncio
    async def test_gdpr_18_tenant_deletion_cascades(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock, mock_audit: AsyncMock,
    ) -> None:
        """GDPR-18: Tenant deletion cascades across all registered stores."""
        registry.register(mock_store_adapter)
        service = DataDeletionService(registry, audit_repo=mock_audit)

        result = await service.delete_tenant(TENANT_ID, force=True)

        assert isinstance(result, DeletionResult)
        assert result.deletion_type == "tenant"
        assert result.tenant_id == TENANT_ID
        assert "mock_store" in result.stores_deleted
        mock_store_adapter.delete_tenant_data.assert_awaited_once_with(TENANT_ID)

    @pytest.mark.asyncio
    async def test_gdpr_19_customer_deletion(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock, mock_audit: AsyncMock,
    ) -> None:
        """GDPR-19: Customer deletion across all stores (no grace period check)."""
        registry.register(mock_store_adapter)
        service = DataDeletionService(registry, audit_repo=mock_audit)

        result = await service.delete_customer(TENANT_ID, CUSTOMER_ID)

        assert result.deletion_type == "customer"
        assert result.customer_id == CUSTOMER_ID
        mock_store_adapter.delete_customer_data.assert_awaited_once_with(TENANT_ID, CUSTOMER_ID)

    @pytest.mark.asyncio
    async def test_gdpr_20_grace_period_enforced(self, mock_audit: AsyncMock) -> None:
        """GDPR-20: GracePeriodActiveError raised when grace period is active."""
        # Mock tenant repo returning a doc with future grace period
        future = datetime.now(timezone.utc) + timedelta(days=10)
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(return_value={
            "id": TENANT_ID,
            "tenant_id": TENANT_ID,
            "grace_period_ends_at": future.isoformat(),
            "billing_channel": "stripe",
        })

        registry = DataStoreRegistry()
        service = DataDeletionService(
            registry,
            audit_repo=mock_audit,
            tenant_repo=tenant_repo,
        )

        with pytest.raises(GracePeriodActiveError) as exc_info:
            await service.delete_tenant(TENANT_ID, force=False)

        assert exc_info.value.tenant_id == TENANT_ID

    @pytest.mark.asyncio
    async def test_gdpr_20_grace_period_bypassed_with_force(self, mock_audit: AsyncMock) -> None:
        """GDPR-20 supplement: force=True bypasses grace period check."""
        future = datetime.now(timezone.utc) + timedelta(days=10)
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(return_value={
            "id": TENANT_ID,
            "grace_period_ends_at": future.isoformat(),
            "billing_channel": "stripe",
        })

        registry = DataStoreRegistry()
        adapter = MagicMock()
        adapter.store_name = "test_store"
        adapter.delete_tenant_data = AsyncMock(return_value={"deleted": 1})
        registry.register(adapter)

        service = DataDeletionService(
            registry,
            audit_repo=mock_audit,
            tenant_repo=tenant_repo,
        )

        # Should NOT raise
        result = await service.delete_tenant(TENANT_ID, force=True)
        assert result.deletion_type == "tenant"

    @pytest.mark.asyncio
    async def test_gdpr_21_deletion_audit_logged(
        self, registry: DataStoreRegistry, mock_store_adapter: MagicMock, mock_audit: AsyncMock,
    ) -> None:
        """GDPR-21: DATA_DELETED audit event created on deletion."""
        registry.register(mock_store_adapter)
        service = DataDeletionService(registry, audit_repo=mock_audit)

        await service.delete_tenant(TENANT_ID, force=True)

        mock_audit.log_event.assert_awaited_once()
        call_kwargs = mock_audit.log_event.call_args[1]
        assert call_kwargs["event_type"] == AuditEventType.DATA_DELETED
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["payload"]["deletion_type"] == "tenant"


# ===========================================================================
# GDPR-22 to GDPR-25: Consent Manager
# ===========================================================================


class TestConsentManager:
    """GDPR-22 through GDPR-25: Consent management and auto-deletion."""

    @pytest.mark.asyncio
    async def test_gdpr_22_grant_consent(self, mock_audit: AsyncMock) -> None:
        """GDPR-22: Granting consent updates tenant record."""
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(return_value={
            "id": TENANT_ID, "tenant_id": TENANT_ID, "consent_status": "not_asked",
        })
        tenant_repo.patch = AsyncMock()

        mgr = ConsentManager(tenant_repo=tenant_repo, audit_repo=mock_audit)
        result = await mgr.update_tenant_consent(TENANT_ID, ConsentStatus.GRANTED, "user")

        assert result["new_status"] == "granted"
        assert result["previous_status"] == "not_asked"
        tenant_repo.patch.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_gdpr_23_deny_consent(self, mock_audit: AsyncMock) -> None:
        """GDPR-23: Denying consent updates tenant record."""
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(return_value={
            "id": TENANT_ID, "tenant_id": TENANT_ID, "consent_status": "granted",
        })
        tenant_repo.patch = AsyncMock()

        mgr = ConsentManager(tenant_repo=tenant_repo, audit_repo=mock_audit)
        result = await mgr.update_tenant_consent(TENANT_ID, ConsentStatus.DENIED, "user")

        assert result["new_status"] == "denied"
        assert result["previous_status"] == "granted"

    @pytest.mark.asyncio
    async def test_gdpr_24_deny_triggers_layer24_deletion(self, mock_audit: AsyncMock) -> None:
        """GDPR-24: Customer consent denial triggers Layer 2-4 data deletion."""
        profile_repo = AsyncMock()
        profile_repo.get_by_customer_id = AsyncMock(return_value={
            "id": f"{TENANT_ID}:{CUSTOMER_ID}",
            "tenant_id": TENANT_ID,
            "consent_status": "granted",
        })
        profile_repo.patch = AsyncMock()

        # Mock deletion service
        mock_deletion = AsyncMock(spec=DataDeletionService)
        mock_deletion.delete_customer = AsyncMock(return_value=DeletionResult(
            deletion_id="del-test",
            tenant_id=TENANT_ID,
            customer_id=CUSTOMER_ID,
            deletion_type="customer",
            stores_deleted=["cosmos_db"],
            details={},
            deleted_at="2026-01-15T00:00:00Z",
            errors=[],
        ))

        mgr = ConsentManager(
            customer_profile_repo=profile_repo,
            audit_repo=mock_audit,
            deletion_service=mock_deletion,
        )
        result = await mgr.update_customer_consent(
            TENANT_ID, CUSTOMER_ID, ConsentStatus.DENIED, "user",
        )

        assert result["new_status"] == "denied"
        assert "deletion" in result
        mock_deletion.delete_customer.assert_awaited_once_with(TENANT_ID, CUSTOMER_ID)

    @pytest.mark.asyncio
    async def test_gdpr_24_grant_no_deletion(self, mock_audit: AsyncMock) -> None:
        """GDPR-24 supplement: Granting consent does NOT trigger deletion."""
        profile_repo = AsyncMock()
        profile_repo.get_by_customer_id = AsyncMock(return_value={
            "id": f"{TENANT_ID}:{CUSTOMER_ID}",
            "tenant_id": TENANT_ID,
            "consent_status": "not_asked",
        })
        profile_repo.patch = AsyncMock()

        mock_deletion = AsyncMock(spec=DataDeletionService)

        mgr = ConsentManager(
            customer_profile_repo=profile_repo,
            audit_repo=mock_audit,
            deletion_service=mock_deletion,
        )
        result = await mgr.update_customer_consent(
            TENANT_ID, CUSTOMER_ID, ConsentStatus.GRANTED, "user",
        )

        assert result["new_status"] == "granted"
        assert "deletion" not in result
        mock_deletion.delete_customer.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_gdpr_25_consent_audit_logged(self, mock_audit: AsyncMock) -> None:
        """GDPR-25: CONSENT_CHANGED audit event on consent update."""
        tenant_repo = AsyncMock()
        tenant_repo.read = AsyncMock(return_value={
            "id": TENANT_ID, "tenant_id": TENANT_ID, "consent_status": "not_asked",
        })
        tenant_repo.patch = AsyncMock()

        mgr = ConsentManager(tenant_repo=tenant_repo, audit_repo=mock_audit)
        await mgr.update_tenant_consent(TENANT_ID, ConsentStatus.GRANTED, "admin_user")

        mock_audit.log_event.assert_awaited_once()
        call_kwargs = mock_audit.log_event.call_args[1]
        assert call_kwargs["event_type"] == AuditEventType.CONSENT_CHANGED
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["actor"] == "admin_user"
        assert call_kwargs["payload"]["new_status"] == "granted"

    def test_consent_layer_gating(self) -> None:
        """Supplement: is_layer_allowed enforces layer gating rules."""
        mgr = ConsentManager()

        # Layer 1 always allowed
        assert mgr.is_layer_allowed(ConsentStatus.NOT_ASKED, 1) is True
        assert mgr.is_layer_allowed(ConsentStatus.DENIED, 1) is True
        assert mgr.is_layer_allowed(ConsentStatus.GRANTED, 1) is True

        # Layers 2-4 require GRANTED
        for layer in (2, 3, 4):
            assert mgr.is_layer_allowed(ConsentStatus.GRANTED, layer) is True
            assert mgr.is_layer_allowed(ConsentStatus.DENIED, layer) is False
            assert mgr.is_layer_allowed(ConsentStatus.NOT_ASKED, layer) is False


# ===========================================================================
# GDPR-26 to GDPR-27: Cosmos Data Store Adapter
# ===========================================================================


class TestCosmosDataStoreAdapter:
    """GDPR-26 and GDPR-27: Cosmos DB adapter for export and deletion."""

    @pytest.mark.asyncio
    async def test_gdpr_26_export_7_collections(self, mock_cosmos_repos: dict[str, AsyncMock]) -> None:
        """GDPR-26: Export queries all 7 tenant-scoped collections."""
        adapter = CosmosDataStoreAdapter(**mock_cosmos_repos)
        result = await adapter.export_tenant_data(TENANT_ID)

        # All 7 internal collection names present in result
        expected_collections = {
            "tenants", "conversations", "usage", "customer_profiles",
            "knowledge_bases", "memory_vectors", "preferences",
        }
        assert set(result.keys()) == expected_collections
        for repo in mock_cosmos_repos.values():
            repo.query.assert_awaited()

    @pytest.mark.asyncio
    async def test_gdpr_26_customer_export(self, mock_cosmos_repos: dict[str, AsyncMock]) -> None:
        """GDPR-26 supplement: Customer export covers profile, conversations, vectors."""
        adapter = CosmosDataStoreAdapter(**mock_cosmos_repos)
        result = await adapter.export_customer_data(TENANT_ID, CUSTOMER_ID)

        assert "customer_profiles" in result
        assert "conversations" in result
        assert "memory_vectors" in result
        mock_cosmos_repos["customer_profile_repo"].get_by_customer_id.assert_awaited_once()
        mock_cosmos_repos["conversation_repo"].list_by_customer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_gdpr_27_delete_7_collections(self, mock_cosmos_repos: dict[str, AsyncMock]) -> None:
        """GDPR-27: Deletion cascades through all 7 collections."""
        adapter = CosmosDataStoreAdapter(**mock_cosmos_repos)
        result = await adapter.delete_tenant_data(TENANT_ID)

        # All 7 internal collection names processed
        expected_collections = {
            "tenants", "conversations", "usage", "customer_profiles",
            "knowledge_bases", "memory_vectors", "preferences",
        }
        assert set(result.keys()) == expected_collections
        for repo in mock_cosmos_repos.values():
            repo.query.assert_awaited()

    @pytest.mark.asyncio
    async def test_gdpr_27_customer_delete(self, mock_cosmos_repos: dict[str, AsyncMock]) -> None:
        """GDPR-27 supplement: Customer deletion removes profile, convos, vectors."""
        adapter = CosmosDataStoreAdapter(**mock_cosmos_repos)
        result = await adapter.delete_customer_data(TENANT_ID, CUSTOMER_ID)

        assert "memory_vectors" in result
        assert "conversations" in result
        assert "customer_profiles" in result
        mock_cosmos_repos["memory_vector_repo"].delete_by_customer.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_adapter_store_name(self, mock_cosmos_repos: dict[str, AsyncMock]) -> None:
        """Supplement: CosmosDataStoreAdapter.store_name is 'cosmos_db'."""
        adapter = CosmosDataStoreAdapter(**mock_cosmos_repos)
        assert adapter.store_name == "cosmos_db"


# ===========================================================================
# GDPR-28 to GDPR-29: NATS Data Store Adapter
# ===========================================================================


class TestNATSDataStoreAdapter:
    """GDPR-28 and GDPR-29: NATS JetStream adapter."""

    @pytest.mark.asyncio
    async def test_gdpr_28_stream_export(self) -> None:
        """GDPR-28: NATS export returns stream metadata (ephemeral data)."""
        mock_nats = AsyncMock()
        mock_nats.get_tenant_stream_info = AsyncMock(return_value={
            "stream_name": "tenant-t-gdpr-001",
            "messages": 42,
        })

        adapter = NATSDataStoreAdapter(mock_nats)
        result = await adapter.export_tenant_data(TENANT_ID)

        assert "stream_info" in result
        assert result["stream_info"]["messages"] == 42

    @pytest.mark.asyncio
    async def test_gdpr_29_stream_delete(self) -> None:
        """GDPR-29: NATS deletion calls deprovision_tenant_topics."""
        mock_nats = AsyncMock()
        mock_nats.deprovision_tenant_topics = AsyncMock(return_value={
            "deleted": True, "stream_name": "tenant-t-gdpr-001",
        })

        adapter = NATSDataStoreAdapter(mock_nats)
        result = await adapter.delete_tenant_data(TENANT_ID)

        assert result["deleted"] is True
        mock_nats.deprovision_tenant_topics.assert_awaited_once_with(TENANT_ID)

    @pytest.mark.asyncio
    async def test_nats_customer_operations_ephemeral(self) -> None:
        """Supplement: NATS per-customer operations return ephemeral note."""
        mock_nats = AsyncMock()
        adapter = NATSDataStoreAdapter(mock_nats)

        export = await adapter.export_customer_data(TENANT_ID, CUSTOMER_ID)
        assert "ephemeral" in export.get("note", "")

        delete = await adapter.delete_customer_data(TENANT_ID, CUSTOMER_ID)
        assert "ephemeral" in delete.get("note", "")

    @pytest.mark.asyncio
    async def test_nats_store_name(self) -> None:
        """Supplement: NATSDataStoreAdapter.store_name is 'nats_jetstream'."""
        adapter = NATSDataStoreAdapter(AsyncMock())
        assert adapter.store_name == "nats_jetstream"


# ===========================================================================
# GDPR-30: Cascading deletion order
# ===========================================================================


class TestCascadingDeletionOrder:
    """GDPR-30: Deletion order enforced (dependent data first, tenant last)."""

    @pytest.mark.asyncio
    async def test_gdpr_30_deletion_order(self, mock_cosmos_repos: dict[str, AsyncMock]) -> None:
        """GDPR-30: Cosmos adapter deletes in dependency order."""
        adapter = CosmosDataStoreAdapter(**mock_cosmos_repos)

        # Track deletion order by instrumenting the internal _repos dict
        deletion_order: list[str] = []

        for name, repo in adapter._repos.items():

            async def _tracking_query(
                *args: Any, _name: str = name, **kwargs: Any,
            ) -> list[dict[str, Any]]:
                deletion_order.append(_name)
                return [{"id": f"{_name}-1", "tenant_id": TENANT_ID}]

            repo.query = AsyncMock(side_effect=_tracking_query)

        await adapter.delete_tenant_data(TENANT_ID)

        # Expected order per gdpr_services.py: dependent data first, tenants last
        expected_order = [
            "memory_vectors",
            "customer_profiles",
            "conversations",
            "usage",
            "knowledge_bases",
            "preferences",
            "tenants",
        ]
        assert deletion_order == expected_order
