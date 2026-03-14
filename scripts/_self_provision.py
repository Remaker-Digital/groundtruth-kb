"""Self-provisioning helper for test infrastructure (WI-1107).

Creates ephemeral test tenants via the SPA platform admin API and returns
raw keys for automated test use. This eliminates the need for provider-held
tenant keys in .env.local, satisfying SPEC-1673 compliance.

The test provisioning endpoint (POST /api/superadmin/test/provision-tenant)
is only available in non-production environments.

Usage:
    from scripts._self_provision import provision_test_tenant, cleanup_test_tenant

    result = provision_test_tenant(base_url, spa_key, tier="starter")
    # result.tenant_id, result.user_api_key, result.widget_key
    ...
    cleanup_test_tenant(base_url, spa_key, result.tenant_id)

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

import httpx


@dataclass
class ProvisionedTenant:
    """Credentials for a self-provisioned test tenant."""

    tenant_id: str
    user_api_key: str
    widget_key: str
    tier: str
    email: str
    warnings: list[str] = field(default_factory=list)


def provision_test_tenant(
    base_url: str,
    spa_key: str,
    *,
    tier: str = "starter",
    merchant_name: str | None = None,
    email: str | None = None,
    expires_at: str | None = None,
    timeout: float = 30.0,
) -> ProvisionedTenant:
    """Create an ephemeral test tenant via the test provisioning endpoint.

    Args:
        base_url: Target environment URL (e.g., https://agent-red-staging...).
        spa_key: SPA platform admin key (ar_spa_plat_*).
        tier: Subscription tier for the test tenant.
        merchant_name: Display name (auto-generated if omitted).
        email: Superadmin email (auto-generated if omitted).
        expires_at: Optional ISO 8601 expiry for auto-cleanup.
        timeout: HTTP request timeout in seconds.

    Returns:
        ProvisionedTenant with tenant_id, user_api_key, and widget_key.

    Raises:
        RuntimeError: If provisioning fails or keys are not returned.
    """
    run_id = uuid.uuid4().hex[:8]
    if not merchant_name:
        merchant_name = f"Test Tenant {run_id}"
    if not email:
        email = f"test-{run_id}@pipeline.agentredcx.com"

    body = {
        "merchantName": merchant_name,
        "superadminEmail": email,
        "tier": tier,
    }
    if expires_at:
        body["expiresAt"] = expires_at

    with httpx.Client(timeout=timeout) as client:
        resp = client.post(
            f"{base_url}/api/superadmin/test/provision-tenant",
            json=body,
            headers={
                "X-API-Key": spa_key,
                "Content-Type": "application/json",
            },
        )

    if resp.status_code == 403:
        raise RuntimeError(
            "Test provisioning endpoint returned 403 — blocked in production. "
            "This endpoint is only available in staging/development environments."
        )

    if resp.status_code != 201:
        raise RuntimeError(
            f"Test provisioning failed: HTTP {resp.status_code} — {resp.text[:500]}"
        )

    data = resp.json()
    user_key = data.get("userApiKey", "")
    widget_key = data.get("widgetKey", "")

    if not user_key:
        raise RuntimeError(
            f"Test provisioning returned no user API key for tenant {data.get('tenantId')}. "
            f"Warnings: {data.get('warnings', [])}"
        )

    return ProvisionedTenant(
        tenant_id=data["tenantId"],
        user_api_key=user_key,
        widget_key=widget_key or "",
        tier=tier,
        email=email,
        warnings=data.get("warnings", []),
    )


def cleanup_test_tenant(
    base_url: str,
    spa_key: str,
    tenant_id: str,
    *,
    timeout: float = 15.0,
) -> bool:
    """Deactivate an ephemeral test tenant after test run.

    Uses the tier override endpoint to set status indicators that
    mark the tenant as a test artifact. Returns True on success.
    """
    try:
        with httpx.Client(timeout=timeout) as client:
            # Set expiry to now to block further access
            from datetime import datetime, timezone
            now_iso = datetime.now(timezone.utc).isoformat()
            resp = client.patch(
                f"{base_url}/api/superadmin/tenants/{tenant_id}/expiry",
                json={"expiresAt": now_iso},
                headers={
                    "X-API-Key": spa_key,
                    "Content-Type": "application/json",
                },
            )
            return resp.status_code == 200
    except Exception:
        return False


def provision_test_tenants(
    base_url: str,
    spa_key: str,
    *,
    count: int = 1,
    tier: str = "starter",
    expires_at: str | None = None,
) -> list[ProvisionedTenant]:
    """Provision multiple ephemeral test tenants.

    Returns a list of ProvisionedTenant objects. If any provisioning
    fails, the already-provisioned tenants are still returned (partial
    success is acceptable for multi-tenant test scenarios).
    """
    tenants: list[ProvisionedTenant] = []
    for i in range(count):
        try:
            t = provision_test_tenant(
                base_url, spa_key,
                tier=tier,
                expires_at=expires_at,
            )
            tenants.append(t)
        except RuntimeError as e:
            # Log but continue — partial provisioning is acceptable
            print(f"WARNING: Failed to provision test tenant {i+1}/{count}: {e}")
    return tenants
