# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Google Docs/Drive Integration Manifest (SPEC-1777).

Declarative configuration for the Google Docs knowledge source adapter.
Auth: OAuth2.  Scopes: drive.readonly, documents.readonly.
Sync: Polling via Drive changes.list (incremental) with daily full sweep.

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

GOOGLE_DOCS_MANIFEST = IntegrationManifest(
    integration_id="google_docs",
    display_name="Google Docs",
    category=IntegrationCategory.KNOWLEDGE,
    description=(
        "Import knowledge from Google Docs and Drive.  Supports Docs, "
        "Sheets (as CSV), PDF, TXT, MD, and CSV files.  Incremental sync "
        "with content-hash deduplication."
    ),
    icon_url="/integration-logos/google-docs-logo-dark.svg",
    auth_type=AuthType.OAUTH2,
    auth_config=AuthConfig(
        scopes=[
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/documents.readonly",
        ],
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        revoke_url="https://oauth2.googleapis.com/revoke",
        client_id_env="GOOGLE_CLIENT_ID",
        client_secret_env="GOOGLE_CLIENT_SECRET",
    ),
    capabilities=frozenset([
        Capability.SOURCE_ARTICLES,
    ]),
    sync_strategy=SyncStrategy.POLLING,
    poll_interval_seconds=3600,  # 1 hour default
    rate_limit_rpm=60,  # Google API quota-friendly
    tier_gate="professional",
    status=IntegrationStatus.AVAILABLE,
)
