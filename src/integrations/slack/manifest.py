# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Slack Integration Manifest (SPEC-1776).

Declarative configuration for the Slack channel adapter.
Auth: OAuth2.  Bot scopes: chat:write, channels:history/read, etc.
Webhooks: Events API with x-slack-signature HMAC-SHA256.

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

SLACK_MANIFEST = IntegrationManifest(
    integration_id="slack",
    display_name="Slack",
    category=IntegrationCategory.CHANNEL,
    description=(
        "Slack channel adapter: @mention-triggered AI bot with threaded "
        "responses, source citations, escalation, and Block Kit formatting."
    ),
    icon_url="/integration-logos/slack-logo-dark.svg",
    auth_type=AuthType.OAUTH2,
    auth_config=AuthConfig(
        scopes=[
            "chat:write",
            "channels:history",
            "channels:read",
            "groups:read",
            "im:read",
            "im:write",
            "app_mentions:read",
            "users:read",
        ],
        authorize_url="https://slack.com/oauth/v2/authorize",
        token_url="https://slack.com/api/oauth.v2.access",
        revoke_url="https://slack.com/api/auth.revoke",
        client_id_env="SLACK_CLIENT_ID",
        client_secret_env="SLACK_CLIENT_SECRET",
    ),
    capabilities=frozenset([
        Capability.DEST_REPLY,
        Capability.WEBHOOK_RECEIVE,
    ]),
    sync_strategy=SyncStrategy.WEBHOOK,
    poll_interval_seconds=0,  # Webhook-only
    rate_limit_rpm=60,  # Slack Tier 3 ≈ 50/min
    webhook_signature_header="x-slack-signature",
    webhook_signature_algo="hmac-sha256",
    tier_gate="professional",
    status=IntegrationStatus.AVAILABLE,
)
