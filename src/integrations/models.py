"""Normalized data models — integration boundary types (SPEC-1762).

All adapters produce and consume these normalized models.  Vendor-specific
data is mapped to these types at the adapter boundary, ensuring the core
system never deals with vendor-specific structures.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TicketStatus(str, Enum):
    """Normalized ticket status (superset of common helpdesk states)."""

    OPEN = "open"
    PENDING = "pending"
    WAITING_ON_AGENT = "waiting_on_agent"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, Enum):
    """Normalized ticket priority."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageDirection(str, Enum):
    """Direction of a message."""

    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"


class MessageChannel(str, Enum):
    """Channel the message was sent through."""

    EMAIL = "email"
    CHAT = "chat"
    SLACK = "slack"
    SMS = "sms"
    SOCIAL = "social"
    HELPDESK = "helpdesk"
    PHONE = "phone"


class OrderStatus(str, Enum):
    """Normalized order status."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


# ---------------------------------------------------------------------------
# Normalized Models
# ---------------------------------------------------------------------------


class NormalizedAttachment(BaseModel):
    """File attachment."""

    filename: str
    content_type: str = ""
    url: str = ""
    size_bytes: int = 0


class NormalizedContact(BaseModel):
    """Normalized contact/customer record."""

    external_id: str
    source: str = Field(description="Integration that produced this record")
    email: str = ""
    name: str = ""
    phone: str = ""
    company: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedMessage(BaseModel):
    """Normalized message within a ticket or conversation."""

    external_id: str
    source: str
    direction: MessageDirection
    channel: MessageChannel = MessageChannel.HELPDESK
    body_text: str = ""
    body_html: str = ""
    sender: NormalizedContact | None = None
    attachments: list[NormalizedAttachment] = Field(default_factory=list)
    timestamp: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizedTicket(BaseModel):
    """Normalized helpdesk ticket."""

    external_id: str
    source: str
    subject: str = ""
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.NORMAL
    channel: MessageChannel = MessageChannel.HELPDESK
    requester: NormalizedContact | None = None
    assignee: NormalizedContact | None = None
    messages: list[NormalizedMessage] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    raw: dict[str, Any] = Field(
        default_factory=dict,
        description="Original vendor payload for debugging",
    )


class NormalizedArticle(BaseModel):
    """Normalized knowledge base article.

    Compatible with KnowledgeBaseDocument for embedding.
    """

    external_id: str
    source: str
    title: str = ""
    body_text: str = Field(default="", description="Plaintext for embedding")
    body_html: str = ""
    url: str = ""
    category: str = ""
    labels: list[str] = Field(default_factory=list)
    last_modified: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class LineItem(BaseModel):
    """Order line item."""

    product_id: str = ""
    product_name: str = ""
    variant_id: str = ""
    variant_name: str = ""
    quantity: int = 0
    unit_price: float = 0.0
    total_price: float = 0.0


class NormalizedOrder(BaseModel):
    """Normalized e-commerce order."""

    external_id: str
    source: str
    order_number: str = ""
    status: OrderStatus = OrderStatus.PENDING
    customer: NormalizedContact | None = None
    line_items: list[LineItem] = Field(default_factory=list)
    total: float = 0.0
    currency: str = "USD"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------


class IntegrationError(Exception):
    """Base error for integration operations."""

    def __init__(
        self,
        message: str,
        integration_id: str = "",
        status_code: int | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.integration_id = integration_id
        self.status_code = status_code
        self.retryable = retryable


class RateLimitError(IntegrationError):
    """Rate limit exceeded on external API."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        integration_id: str = "",
        retry_after_seconds: float = 60.0,
    ):
        super().__init__(
            message, integration_id=integration_id, status_code=429, retryable=True
        )
        self.retry_after_seconds = retry_after_seconds


class AuthenticationError(IntegrationError):
    """Authentication failed (expired token, invalid credentials)."""

    def __init__(
        self,
        message: str = "Authentication failed",
        integration_id: str = "",
    ):
        super().__init__(
            message, integration_id=integration_id, status_code=401, retryable=False
        )
