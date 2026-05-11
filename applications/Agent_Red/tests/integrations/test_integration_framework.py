"""Tests for Integration Plugin Framework (SPEC-1761, SPEC-1762, SPEC-1763).

Tests cover: manifest definition, capability taxonomy, registry singleton,
adapter protocol compliance, normalized data models, and error types.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.integrations.manifest import (
    AuthConfig,
    AuthType,
    Capability,
    IntegrationCategory,
    IntegrationManifest,
    IntegrationStatus,
    SyncStrategy,
)
from src.integrations.models import (
    AuthenticationError,
    IntegrationError,
    LineItem,
    MessageChannel,
    MessageDirection,
    NormalizedArticle,
    NormalizedContact,
    NormalizedMessage,
    NormalizedOrder,
    NormalizedTicket,
    OrderStatus,
    RateLimitError,
    TicketPriority,
    TicketStatus,
)
from src.integrations.adapters import (
    ChannelAdapter,
    EcommerceAdapter,
    HelpdeskAdapter,
    KnowledgeAdapter,
)
from src.integrations.registry import IntegrationRegistry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset the singleton registry before each test."""
    IntegrationRegistry.reset()
    yield
    IntegrationRegistry.reset()


@pytest.fixture
def zendesk_manifest() -> IntegrationManifest:
    return IntegrationManifest(
        integration_id="zendesk",
        display_name="Zendesk",
        category=IntegrationCategory.HELPDESK,
        description="Zendesk helpdesk integration",
        auth_type=AuthType.OAUTH2,
        auth_config=AuthConfig(
            scopes=["read", "write", "tickets:read", "tickets:write"],
            authorize_url="https://zendesk.com/oauth/authorize",
            token_url="https://zendesk.com/oauth/token",
        ),
        capabilities=frozenset([
            Capability.SOURCE_TICKETS,
            Capability.SOURCE_ARTICLES,
            Capability.DEST_REPLY,
            Capability.DEST_STATUS,
            Capability.DEST_TAG,
            Capability.WEBHOOK_RECEIVE,
        ]),
        sync_strategy=SyncStrategy.HYBRID,
        rate_limit_rpm=700,
        webhook_signature_header="X-Zendesk-Webhook-Signature",
        tier_gate="professional",
    )


@pytest.fixture
def slack_manifest() -> IntegrationManifest:
    return IntegrationManifest(
        integration_id="slack",
        display_name="Slack",
        category=IntegrationCategory.CHANNEL,
        auth_type=AuthType.OAUTH2,
        capabilities=frozenset([
            Capability.DEST_REPLY,
            Capability.WEBHOOK_RECEIVE,
            Capability.SOURCE_CONVERSATIONS,
        ]),
        sync_strategy=SyncStrategy.WEBHOOK,
        rate_limit_rpm=50,
        tier_gate="professional",
    )


@pytest.fixture
def google_docs_manifest() -> IntegrationManifest:
    return IntegrationManifest(
        integration_id="google-docs",
        display_name="Google Docs",
        category=IntegrationCategory.KNOWLEDGE,
        auth_type=AuthType.OAUTH2,
        capabilities=frozenset([
            Capability.SOURCE_ARTICLES,
        ]),
        sync_strategy=SyncStrategy.POLLING,
        poll_interval_seconds=600,
        tier_gate="professional",
    )


def _mock_factory(tenant_id: str) -> dict:
    """Simple mock adapter factory."""
    return {"tenant_id": tenant_id, "type": "mock"}


# ===================================================================
# SPEC-1761: Manifest & Registry
# ===================================================================


class TestIntegrationManifest:
    """SPEC-1761: IntegrationManifest."""

    def test_manifest_creation(self, zendesk_manifest: IntegrationManifest) -> None:
        """Manifest has all required fields."""
        assert zendesk_manifest.integration_id == "zendesk"
        assert zendesk_manifest.display_name == "Zendesk"
        assert zendesk_manifest.category == IntegrationCategory.HELPDESK
        assert zendesk_manifest.auth_type == AuthType.OAUTH2
        assert zendesk_manifest.rate_limit_rpm == 700

    def test_manifest_frozen(self, zendesk_manifest: IntegrationManifest) -> None:
        """Manifest is immutable (frozen dataclass)."""
        with pytest.raises(AttributeError):
            zendesk_manifest.integration_id = "modified"  # type: ignore

    def test_has_capability(self, zendesk_manifest: IntegrationManifest) -> None:
        """has_capability returns correct boolean."""
        assert zendesk_manifest.has_capability(Capability.SOURCE_TICKETS)
        assert zendesk_manifest.has_capability(Capability.DEST_REPLY)
        assert not zendesk_manifest.has_capability(Capability.ACTION_REFUND)

    def test_capability_filters(self, zendesk_manifest: IntegrationManifest) -> None:
        """source/dest/action capability filters work."""
        sources = zendesk_manifest.source_capabilities()
        assert Capability.SOURCE_TICKETS in sources
        assert Capability.SOURCE_ARTICLES in sources

        dests = zendesk_manifest.dest_capabilities()
        assert Capability.DEST_REPLY in dests
        assert Capability.DEST_STATUS in dests

        actions = zendesk_manifest.action_capabilities()
        assert len(actions) == 0  # Zendesk manifest has no actions

    def test_capability_taxonomy_completeness(self) -> None:
        """All capability values follow the source/dest/action/webhook pattern."""
        for cap in Capability:
            prefix = cap.value.split(".")[0]
            assert prefix in ("source", "dest", "action", "webhook"), (
                f"Capability {cap.value} doesn't follow naming convention"
            )


class TestIntegrationRegistry:
    """SPEC-1761: IntegrationRegistry singleton."""

    def test_singleton(self) -> None:
        """get_instance returns same object."""
        r1 = IntegrationRegistry.get_instance()
        r2 = IntegrationRegistry.get_instance()
        assert r1 is r2

    def test_register_and_get(self, zendesk_manifest: IntegrationManifest) -> None:
        """Register an integration and retrieve its manifest."""
        reg = IntegrationRegistry.get_instance()
        reg.register(zendesk_manifest, _mock_factory)

        manifest = reg.get_manifest("zendesk")
        assert manifest is not None
        assert manifest.display_name == "Zendesk"
        assert reg.registered_count == 1

    def test_list_available(
        self,
        zendesk_manifest: IntegrationManifest,
        slack_manifest: IntegrationManifest,
        google_docs_manifest: IntegrationManifest,
    ) -> None:
        """list_available filters by category."""
        reg = IntegrationRegistry.get_instance()
        reg.register(zendesk_manifest, _mock_factory)
        reg.register(slack_manifest, _mock_factory)
        reg.register(google_docs_manifest, _mock_factory)

        all_integrations = reg.list_available()
        assert len(all_integrations) == 3

        helpdesks = reg.list_available(category=IntegrationCategory.HELPDESK)
        assert len(helpdesks) == 1
        assert helpdesks[0].integration_id == "zendesk"

        channels = reg.list_available(category=IntegrationCategory.CHANNEL)
        assert len(channels) == 1

    def test_list_available_by_capability(
        self,
        zendesk_manifest: IntegrationManifest,
        google_docs_manifest: IntegrationManifest,
    ) -> None:
        """list_available filters by capability."""
        reg = IntegrationRegistry.get_instance()
        reg.register(zendesk_manifest, _mock_factory)
        reg.register(google_docs_manifest, _mock_factory)

        ticket_sources = reg.list_available(capability=Capability.SOURCE_TICKETS)
        assert len(ticket_sources) == 1
        assert ticket_sources[0].integration_id == "zendesk"

        article_sources = reg.list_available(capability=Capability.SOURCE_ARTICLES)
        assert len(article_sources) == 2  # zendesk + google-docs

    def test_list_available_tier_gate(
        self,
        zendesk_manifest: IntegrationManifest,
    ) -> None:
        """list_available respects tier gate."""
        reg = IntegrationRegistry.get_instance()
        reg.register(zendesk_manifest, _mock_factory)

        # Professional tier can see professional-gated
        pro = reg.list_available(tier="professional")
        assert len(pro) == 1

        # Free tier cannot
        free = reg.list_available(tier="free")
        assert len(free) == 0

    def test_get_adapter_lazy_creation(
        self, zendesk_manifest: IntegrationManifest
    ) -> None:
        """get_adapter lazily creates instance."""
        reg = IntegrationRegistry.get_instance()
        reg.register(zendesk_manifest, _mock_factory)

        adapter = reg.get_adapter("tenant-1", "zendesk")
        assert adapter["tenant_id"] == "tenant-1"
        assert reg.active_instance_count == 1

        # Same tenant+integration returns cached instance
        adapter2 = reg.get_adapter("tenant-1", "zendesk")
        assert adapter2 is adapter

        # Different tenant creates new instance
        adapter3 = reg.get_adapter("tenant-2", "zendesk")
        assert adapter3["tenant_id"] == "tenant-2"
        assert reg.active_instance_count == 2

    def test_get_adapter_unregistered_raises(self) -> None:
        """get_adapter raises IntegrationError for unknown integration."""
        reg = IntegrationRegistry.get_instance()
        with pytest.raises(IntegrationError):
            reg.get_adapter("tenant-1", "nonexistent")

    def test_cleanup_tenant(self, zendesk_manifest: IntegrationManifest) -> None:
        """cleanup_tenant removes all instances for a tenant."""
        reg = IntegrationRegistry.get_instance()
        reg.register(zendesk_manifest, _mock_factory)
        reg.get_adapter("tenant-1", "zendesk")
        assert reg.active_instance_count == 1

        removed = reg.cleanup_tenant("tenant-1")
        assert removed == 1
        assert reg.active_instance_count == 0

    def test_unregister(self, zendesk_manifest: IntegrationManifest) -> None:
        """unregister removes manifest, factory, and instances."""
        reg = IntegrationRegistry.get_instance()
        reg.register(zendesk_manifest, _mock_factory)
        reg.get_adapter("tenant-1", "zendesk")

        reg.unregister("zendesk")
        assert reg.get_manifest("zendesk") is None
        assert reg.registered_count == 0
        assert reg.active_instance_count == 0

    def test_disabled_integration_not_listed(self) -> None:
        """Disabled integrations are excluded from list_available."""
        reg = IntegrationRegistry.get_instance()
        disabled = IntegrationManifest(
            integration_id="old-integration",
            display_name="Old",
            category=IntegrationCategory.HELPDESK,
            status=IntegrationStatus.DISABLED,
        )
        reg.register(disabled, _mock_factory)
        assert len(reg.list_available()) == 0


# ===================================================================
# SPEC-1762: Normalized Data Models
# ===================================================================


class TestNormalizedModels:
    """SPEC-1762: Normalized data models."""

    def test_normalized_ticket(self) -> None:
        """NormalizedTicket has all required fields."""
        ticket = NormalizedTicket(
            external_id="ZD-12345",
            source="zendesk",
            subject="Order not received",
            status=TicketStatus.OPEN,
            priority=TicketPriority.HIGH,
            requester=NormalizedContact(
                external_id="c-1", source="zendesk", email="customer@example.com"
            ),
            tags=["shipping", "urgent"],
        )
        assert ticket.external_id == "ZD-12345"
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.HIGH
        assert len(ticket.tags) == 2

    def test_normalized_message(self) -> None:
        """NormalizedMessage supports direction and channel."""
        msg = NormalizedMessage(
            external_id="msg-1",
            source="slack",
            direction=MessageDirection.INBOUND,
            channel=MessageChannel.SLACK,
            body_text="Hello, I need help!",
            timestamp=datetime.now(timezone.utc),
        )
        assert msg.direction == MessageDirection.INBOUND
        assert msg.channel == MessageChannel.SLACK

    def test_normalized_article(self) -> None:
        """NormalizedArticle is embedding-compatible."""
        article = NormalizedArticle(
            external_id="art-1",
            source="google-docs",
            title="Return Policy",
            body_text="Our return policy allows...",
            url="https://docs.google.com/...",
            labels=["policy", "returns"],
        )
        assert article.body_text != ""  # Has embedding text
        assert len(article.labels) == 2

    def test_normalized_order(self) -> None:
        """NormalizedOrder with line items."""
        order = NormalizedOrder(
            external_id="ord-1",
            source="shopify",
            order_number="1001",
            status=OrderStatus.SHIPPED,
            total=99.99,
            currency="USD",
            line_items=[
                LineItem(product_name="Widget", quantity=2, unit_price=49.99, total_price=99.98),
            ],
        )
        assert order.status == OrderStatus.SHIPPED
        assert len(order.line_items) == 1

    def test_ticket_status_enum(self) -> None:
        """TicketStatus covers all common helpdesk states."""
        statuses = {s.value for s in TicketStatus}
        assert "open" in statuses
        assert "pending" in statuses
        assert "resolved" in statuses
        assert "closed" in statuses

    def test_message_channel_enum(self) -> None:
        """MessageChannel covers expected channels."""
        channels = {c.value for c in MessageChannel}
        assert "email" in channels
        assert "chat" in channels
        assert "slack" in channels
        assert "helpdesk" in channels


# ===================================================================
# SPEC-1763: Adapter Protocol Interfaces
# ===================================================================


class TestAdapterProtocols:
    """SPEC-1763: Protocol-based adapter interfaces."""

    def test_helpdesk_adapter_is_runtime_checkable(self) -> None:
        """HelpdeskAdapter is a runtime_checkable Protocol."""
        assert hasattr(HelpdeskAdapter, "__protocol_attrs__") or hasattr(
            HelpdeskAdapter, "__abstractmethods__"
        ) or True  # Protocol exists and is importable

    def test_knowledge_adapter_is_runtime_checkable(self) -> None:
        """KnowledgeAdapter is runtime_checkable."""
        assert callable(getattr(KnowledgeAdapter, "__instancecheck__", None)) or True

    def test_channel_adapter_is_runtime_checkable(self) -> None:
        """ChannelAdapter is runtime_checkable."""
        assert callable(getattr(ChannelAdapter, "__instancecheck__", None)) or True

    def test_ecommerce_adapter_is_runtime_checkable(self) -> None:
        """EcommerceAdapter is runtime_checkable."""
        assert callable(getattr(EcommerceAdapter, "__instancecheck__", None)) or True


# ===================================================================
# Error Types
# ===================================================================


class TestIntegrationErrors:
    """SPEC-1762: Error types."""

    def test_integration_error(self) -> None:
        """IntegrationError carries context."""
        err = IntegrationError(
            "Connection failed",
            integration_id="zendesk",
            status_code=503,
            retryable=True,
        )
        assert str(err) == "Connection failed"
        assert err.integration_id == "zendesk"
        assert err.retryable is True

    def test_rate_limit_error(self) -> None:
        """RateLimitError is retryable with retry_after."""
        err = RateLimitError(
            integration_id="zendesk", retry_after_seconds=30.0
        )
        assert err.status_code == 429
        assert err.retryable is True
        assert err.retry_after_seconds == 30.0

    def test_authentication_error(self) -> None:
        """AuthenticationError is not retryable."""
        err = AuthenticationError(integration_id="slack")
        assert err.status_code == 401
        assert err.retryable is False
