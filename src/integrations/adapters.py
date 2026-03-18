"""Adapter Protocol Interfaces — typed contracts for integrations (SPEC-1763).

Four Protocol-based adapter interfaces that all integration adapters must
implement.  All methods are async and return normalized models (SPEC-1762).
Vendor errors are wrapped in IntegrationError.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from src.integrations.models import (
    NormalizedArticle,
    NormalizedContact,
    NormalizedMessage,
    NormalizedOrder,
    NormalizedTicket,
)


# ---------------------------------------------------------------------------
# Helpdesk Adapter
# ---------------------------------------------------------------------------


@runtime_checkable
class HelpdeskAdapter(Protocol):
    """Protocol for helpdesk integrations (Zendesk, Freshdesk, Intercom, etc.)."""

    async def list_tickets(
        self,
        tenant_id: str,
        *,
        cursor: str | None = None,
        limit: int = 100,
        status: str | None = None,
    ) -> tuple[list[NormalizedTicket], str | None]:
        """List tickets with pagination cursor."""
        ...

    async def get_ticket(
        self, tenant_id: str, ticket_id: str
    ) -> NormalizedTicket | None:
        """Get a single ticket by external ID."""
        ...

    async def add_reply(
        self,
        tenant_id: str,
        ticket_id: str,
        body: str,
        *,
        html_body: str | None = None,
        internal: bool = False,
    ) -> NormalizedMessage:
        """Add a reply to a ticket."""
        ...

    async def update_status(
        self, tenant_id: str, ticket_id: str, status: str
    ) -> NormalizedTicket:
        """Update a ticket's status."""
        ...

    async def add_tags(
        self, tenant_id: str, ticket_id: str, tags: list[str]
    ) -> NormalizedTicket:
        """Add tags to a ticket."""
        ...

    async def assign_ticket(
        self, tenant_id: str, ticket_id: str, assignee_id: str
    ) -> NormalizedTicket:
        """Assign a ticket to an agent."""
        ...

    async def create_ticket(
        self,
        tenant_id: str,
        subject: str,
        body: str,
        *,
        requester_email: str | None = None,
        priority: str = "normal",
        tags: list[str] | None = None,
    ) -> NormalizedTicket:
        """Create a new ticket."""
        ...

    async def search_tickets(
        self, tenant_id: str, query: str, *, limit: int = 25
    ) -> list[NormalizedTicket]:
        """Search tickets by query string."""
        ...

    async def register_webhook(
        self, tenant_id: str, target_url: str, events: list[str]
    ) -> dict[str, Any]:
        """Register a webhook for ticket events."""
        ...

    async def verify_webhook(
        self, headers: dict[str, str], body: bytes, secret: str
    ) -> bool:
        """Verify webhook signature."""
        ...

    async def health_check(self, tenant_id: str) -> bool:
        """Check if the integration is healthy/connected."""
        ...


# ---------------------------------------------------------------------------
# Knowledge Adapter
# ---------------------------------------------------------------------------


@runtime_checkable
class KnowledgeAdapter(Protocol):
    """Protocol for knowledge source integrations (Zendesk Guide, Google Docs, Notion)."""

    async def list_articles(
        self,
        tenant_id: str,
        *,
        cursor: str | None = None,
        limit: int = 100,
        category: str | None = None,
    ) -> tuple[list[NormalizedArticle], str | None]:
        """List articles with pagination cursor."""
        ...

    async def get_article(
        self, tenant_id: str, article_id: str
    ) -> NormalizedArticle | None:
        """Get a single article by external ID."""
        ...

    async def search_articles(
        self, tenant_id: str, query: str, *, limit: int = 25
    ) -> list[NormalizedArticle]:
        """Search articles by query string."""
        ...

    async def health_check(self, tenant_id: str) -> bool:
        """Check if the integration is healthy/connected."""
        ...


# ---------------------------------------------------------------------------
# Channel Adapter
# ---------------------------------------------------------------------------


@runtime_checkable
class ChannelAdapter(Protocol):
    """Protocol for channel integrations (Slack, Teams, SMS gateways)."""

    async def send_message(
        self,
        tenant_id: str,
        channel_id: str,
        body: str,
        *,
        thread_id: str | None = None,
        blocks: list[dict[str, Any]] | None = None,
    ) -> NormalizedMessage:
        """Send a message to a channel or thread."""
        ...

    async def receive_messages(
        self,
        tenant_id: str,
        channel_id: str,
        *,
        cursor: str | None = None,
        limit: int = 100,
    ) -> tuple[list[NormalizedMessage], str | None]:
        """Fetch recent messages from a channel."""
        ...

    async def register_webhook(
        self, tenant_id: str, target_url: str, events: list[str]
    ) -> dict[str, Any]:
        """Register a webhook for channel events."""
        ...

    async def verify_webhook(
        self, headers: dict[str, str], body: bytes, secret: str
    ) -> bool:
        """Verify webhook signature."""
        ...

    async def format_message(
        self, text: str, *, rich: bool = False
    ) -> dict[str, Any]:
        """Format a message for this channel (e.g., Block Kit for Slack)."""
        ...

    async def health_check(self, tenant_id: str) -> bool:
        """Check if the integration is healthy/connected."""
        ...


# ---------------------------------------------------------------------------
# E-commerce Adapter
# ---------------------------------------------------------------------------


@runtime_checkable
class EcommerceAdapter(Protocol):
    """Protocol for e-commerce integrations (Shopify, Stripe, WooCommerce)."""

    async def lookup_customer(
        self, tenant_id: str, *, email: str | None = None, customer_id: str | None = None
    ) -> NormalizedContact | None:
        """Look up a customer by email or ID."""
        ...

    async def lookup_order(
        self, tenant_id: str, order_id: str
    ) -> NormalizedOrder | None:
        """Look up an order by ID."""
        ...

    async def search_orders(
        self, tenant_id: str, query: str, *, limit: int = 25
    ) -> list[NormalizedOrder]:
        """Search orders by query string."""
        ...

    async def get_product(
        self, tenant_id: str, product_id: str
    ) -> dict[str, Any] | None:
        """Get product details."""
        ...

    async def search_products(
        self, tenant_id: str, query: str, *, limit: int = 25
    ) -> list[dict[str, Any]]:
        """Search products by query string."""
        ...

    async def process_refund(
        self,
        tenant_id: str,
        order_id: str,
        *,
        amount: float | None = None,
        reason: str = "",
    ) -> dict[str, Any]:
        """Process a refund for an order."""
        ...

    async def health_check(self, tenant_id: str) -> bool:
        """Check if the integration is healthy/connected."""
        ...
