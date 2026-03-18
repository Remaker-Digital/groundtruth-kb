"""Zendesk Integration Manifest (SPEC-1775).

Declarative configuration for the Zendesk full helpdesk adapter.
Auth: OAuth2.  Scopes: read, write, tickets:read, tickets:write.
API: REST v2, cursor pagination, 700 req/min.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from src.integrations.manifest import (
    AuthConfig,
    AuthType,
    Capability,
    IntegrationCategory,
    IntegrationManifest,
    IntegrationStatus,
    SyncStrategy,
)

ZENDESK_MANIFEST = IntegrationManifest(
    integration_id="zendesk",
    display_name="Zendesk",
    category=IntegrationCategory.HELPDESK,
    description=(
        "Full helpdesk integration: sync tickets, Guide articles, "
        "customer contacts.  Reply, update status, tag, and assign "
        "tickets directly from Agent Red."
    ),
    icon_url="/integration-logos/zendesk-logo-dark.svg",
    auth_type=AuthType.OAUTH2,
    auth_config=AuthConfig(
        scopes=["read", "write", "tickets:read", "tickets:write"],
        authorize_url="https://{subdomain}.zendesk.com/oauth/authorizations/new",
        token_url="https://{subdomain}.zendesk.com/oauth/tokens",
        revoke_url="https://{subdomain}.zendesk.com/oauth/tokens/{token_id}",
        client_id_env="ZENDESK_CLIENT_ID",
        client_secret_env="ZENDESK_CLIENT_SECRET",
    ),
    capabilities=frozenset([
        Capability.SOURCE_TICKETS,
        Capability.SOURCE_ARTICLES,
        Capability.SOURCE_CONTACTS,
        Capability.DEST_REPLY,
        Capability.DEST_DRAFT,
        Capability.DEST_NOTE,
        Capability.DEST_STATUS,
        Capability.DEST_TAG,
        Capability.DEST_ASSIGN,
        Capability.DEST_CREATE,
        Capability.ACTION_CUSTOMER_LOOKUP,
        Capability.WEBHOOK_RECEIVE,
    ]),
    sync_strategy=SyncStrategy.HYBRID,
    poll_interval_seconds=300,
    rate_limit_rpm=700,
    webhook_signature_header="x-zendesk-webhook-signature",
    webhook_signature_algo="hmac-sha256",
    tier_gate="professional",
    status=IntegrationStatus.AVAILABLE,
)
