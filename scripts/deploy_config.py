"""Shared deployment configuration — single source of truth.

All deployment scripts (deploy_pipeline.py, upgrade_verification.py, deploy.py)
MUST read environment config from this module. No hardcoded tenant IDs, FQDNs,
or credential env var names anywhere else.

SPEC-1882 / Codex WP2: Unify production verification config to prevent
snapshot-tenant / verify-tenant drift.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure .env.local is loaded before reading env vars
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from scripts._env import load_env_local  # noqa: E402

load_env_local()


# ---------------------------------------------------------------------------
# Environment configurations
# ---------------------------------------------------------------------------

ENVIRONMENTS: dict[str, dict[str, str]] = {
    "staging": {
        "fqdn": "agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
        "container_app": "agent-red-staging",
        "tenant_id": os.environ.get("STAGING_REMAKER_TENANT_ID", "remaker-digital-001"),
        "api_key": os.environ.get("STAGING_REMAKER_TENANT_KEY", ""),
        "widget_key": os.environ.get("STAGING_REMAKER_WIDGET_KEY", ""),
        "spa_api_key": os.environ.get("STAGING_SPA_KEY", "") or os.environ.get("SPA_CONSOLE_API_KEY", ""),
        "resource_group": "Agent-Red",
        "cosmos_db_database": "agentred-staging",
    },
    "production": {
        "fqdn": "agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
        "container_app": "agent-red-api-gateway",
        "tenant_id": os.environ.get("PRODUCTION_REMAKER_TENANT_ID", ""),
        "api_key": os.environ.get("PRODUCTION_REMAKER_TENANT_KEY", ""),
        "widget_key": os.environ.get("PRODUCTION_REMAKER_WIDGET_KEY", ""),
        "spa_api_key": os.environ.get("PRODUCTION_SPA_KEY", ""),
        "resource_group": "Agent-Red",
        "cosmos_db_database": "agentred",
    },
}

# Additional tenants for multi-tenant upgrade verification (staging only).
TENANTS: dict[str, dict[str, str]] = {
    "staging:staging-001": {
        "tenant_id": "staging-001",
        "api_key": os.environ.get("STAGING_001_TENANT_KEY", ""),
        "widget_key": os.environ.get("STAGING_001_WIDGET_KEY", ""),
    },
    "staging:staging-002": {
        "tenant_id": "staging-002",
        "api_key": os.environ.get("STAGING_002_TENANT_KEY", ""),
        "widget_key": os.environ.get("STAGING_002_WIDGET_KEY", ""),
    },
}


# ---------------------------------------------------------------------------
# Production deploy gates
# ---------------------------------------------------------------------------


def check_owner_approval() -> bool:
    """Check if owner has approved production deployment (GOV-16).

    Returns True if DEPLOY_APPROVED=1 is set in environment.
    This is a code-enforced gate, not policy text.
    """
    return os.environ.get("DEPLOY_APPROVED") == "1"


def get_environment(env_name: str) -> dict[str, str]:
    """Get environment config by name. Raises KeyError if not found."""
    if env_name not in ENVIRONMENTS:
        raise KeyError(f"Unknown environment '{env_name}' (valid: {list(ENVIRONMENTS.keys())})")
    return ENVIRONMENTS[env_name]


# ---------------------------------------------------------------------------
# Azure helpers (used by rollback)
# ---------------------------------------------------------------------------

ACR_REGISTRY = "acragentredeastus"
ACR_REPO = "api-gateway"


def get_current_image(env_name: str) -> str | None:
    """Get the currently deployed container image tag.

    Uses az containerapp show to query the running image.
    Returns the full image reference or None on failure.
    """
    import subprocess

    config = get_environment(env_name)
    try:
        result = subprocess.run(
            [
                "az",
                "containerapp",
                "show",
                "--name",
                config["container_app"],
                "--resource-group",
                config["resource_group"],
                "--query",
                "properties.template.containers[0].image",
                "--output",
                "tsv",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


def rollback_to_image(env_name: str, image: str) -> bool:
    """Roll back a container app to a previous image.

    Returns True if the az containerapp update succeeded.
    """
    import subprocess

    config = get_environment(env_name)
    try:
        result = subprocess.run(
            [
                "az",
                "containerapp",
                "update",
                "--name",
                config["container_app"],
                "--resource-group",
                config["resource_group"],
                "--image",
                image,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.returncode == 0
    except Exception:
        return False
