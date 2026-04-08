"""Integration Plugin Manifest — declarative integration configuration (SPEC-1761).

Each integration declares its capabilities, authentication requirements,
sync strategy, and tier gate through an IntegrationManifest.  The manifest
is the single source of truth for what an integration can do and how it
connects.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class IntegrationCategory(str, Enum):
    """Categories of integrations."""

    HELPDESK = "helpdesk"
    ECOMMERCE = "ecommerce"
    CHANNEL = "channel"
    KNOWLEDGE = "knowledge"
    CRM = "crm"
    ANALYTICS = "analytics"


class AuthType(str, Enum):
    """Supported authentication methods."""

    OAUTH2 = "oauth2"
    OAUTH2_PKCE = "oauth2_pkce"
    API_KEY = "api_key"
    BASIC = "basic"
    WEBHOOK_ONLY = "webhook_only"
    NONE = "none"


class SyncStrategy(str, Enum):
    """How the integration synchronizes data."""

    WEBHOOK = "webhook"
    POLLING = "polling"
    HYBRID = "hybrid"  # webhook + polling fallback
    ON_DEMAND = "on_demand"


class IntegrationStatus(str, Enum):
    """Lifecycle status of an integration."""

    AVAILABLE = "available"
    BETA = "beta"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"


# ---------------------------------------------------------------------------
# Capability Taxonomy
# ---------------------------------------------------------------------------


class Capability(str, Enum):
    """Standardized integration capability identifiers.

    Organized by direction: source (read from), dest (write to),
    action (execute), webhook (receive events).
    """

    # Source capabilities (read)
    SOURCE_TICKETS = "source.tickets"
    SOURCE_ARTICLES = "source.articles"
    SOURCE_CONTACTS = "source.contacts"
    SOURCE_CONVERSATIONS = "source.conversations"
    SOURCE_ORDERS = "source.orders"
    SOURCE_PRODUCTS = "source.products"

    # Destination capabilities (write)
    DEST_REPLY = "dest.reply"
    DEST_DRAFT = "dest.draft"
    DEST_NOTE = "dest.note"
    DEST_STATUS = "dest.status"
    DEST_TAG = "dest.tag"
    DEST_ASSIGN = "dest.assign"
    DEST_CREATE = "dest.create"

    # Action capabilities (execute)
    ACTION_ORDER_LOOKUP = "action.order_lookup"
    ACTION_REFUND = "action.refund"
    ACTION_CUSTOMER_LOOKUP = "action.customer_lookup"
    ACTION_PRODUCT_SEARCH = "action.product_search"

    # Webhook capabilities
    WEBHOOK_RECEIVE = "webhook.receive"


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuthConfig:
    """Authentication configuration for an integration."""

    scopes: list[str] = field(default_factory=list)
    authorize_url: str = ""
    token_url: str = ""
    revoke_url: str = ""
    client_id_env: str = ""
    client_secret_env: str = ""
    api_key_header: str = ""
    api_key_prefix: str = ""


@dataclass(frozen=True)
class IntegrationManifest:
    """Declarative configuration for an integration plugin.

    This is the core registry entry — it describes what the integration
    can do, how it authenticates, and how it syncs data.
    """

    integration_id: str
    display_name: str
    category: IntegrationCategory
    description: str = ""
    icon_url: str = ""

    # Authentication
    auth_type: AuthType = AuthType.NONE
    auth_config: AuthConfig = field(default_factory=AuthConfig)

    # Capabilities
    capabilities: frozenset[Capability] = field(default_factory=frozenset)

    # Sync
    sync_strategy: SyncStrategy = SyncStrategy.ON_DEMAND
    poll_interval_seconds: int = 300  # 5 min default
    rate_limit_rpm: int = 60

    # Webhook
    webhook_signature_header: str = ""
    webhook_signature_algo: str = "hmac-sha256"

    # Access control
    tier_gate: str = "professional"  # minimum tier required

    # Status
    status: IntegrationStatus = IntegrationStatus.AVAILABLE

    def has_capability(self, cap: Capability) -> bool:
        """Check if this integration supports a given capability."""
        return cap in self.capabilities

    def source_capabilities(self) -> frozenset[Capability]:
        """Return all source.* capabilities."""
        return frozenset(c for c in self.capabilities if c.value.startswith("source."))

    def dest_capabilities(self) -> frozenset[Capability]:
        """Return all dest.* capabilities."""
        return frozenset(c for c in self.capabilities if c.value.startswith("dest."))

    def action_capabilities(self) -> frozenset[Capability]:
        """Return all action.* capabilities."""
        return frozenset(c for c in self.capabilities if c.value.startswith("action."))
