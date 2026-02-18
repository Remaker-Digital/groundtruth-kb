"""Tenant secret management — per-tenant secrets in Azure Key Vault.

Work Item #29 (Decision #6): Enum-based access to per-tenant secrets
stored in Azure Key Vault with `tenant-{id}-{type}` naming convention.

Provides:
    - TenantSecretType enum for type-safe secret access
    - TenantSecretService with store/get/delete/list/rotate operations
    - KeyVaultDataStoreAdapter for GDPR export/deletion (Decision #9)
    - Health check for /ready endpoint integration
    - Dev-mode in-memory fallback when Key Vault is unavailable

Configuration (environment variables):
    AZURE_KEYVAULT_URL       — Key Vault endpoint URL
                                (e.g., https://kv-agntcy-cs-prod-rc6vcp.vault.azure.net/)
    KEYVAULT_USE_MANAGED_ID  — "true" to use Managed Identity (default: true)

Architecture references:
    - Decision #4: API keys hashed, stored in Key Vault
    - Decision #6: Per-tenant secrets, enum-based access, naming convention
    - Decision #9: DataStoreAdapter protocol for GDPR data stores

Dependencies:
    - azure-keyvault-secrets>=4.8.0 (in requirements.txt)
    - azure-identity>=1.19.0 (in requirements.txt)
    - gdpr_services.py: DataStoreAdapter protocol

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import enum
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# TenantSecretType — enum-based access (Decision #6)
# ---------------------------------------------------------------------------


class TenantSecretType(str, enum.Enum):
    """Types of per-tenant secrets stored in Key Vault.

    Each type maps to a specific credential or sensitive value that
    a tenant may provision. The enum enforces a closed set of allowed
    secret types — arbitrary strings cannot be used.

    Naming convention: tenant-{tenant_id}-{type_value}
    Example: tenant-abc123-shopify-token
    """

    # E-commerce platform credentials
    SHOPIFY_TOKEN = "shopify-token"
    SHOPIFY_WEBHOOK_SECRET = "shopify-webhook-secret"
    STRIPE_API_KEY = "stripe-api-key"
    STRIPE_WEBHOOK_SECRET = "stripe-webhook-secret"

    # Agent Red API key (hashed, per Decision #4)
    API_KEY_HASH = "api-key-hash"

    # Azure OpenAI (for tenants with dedicated resource)
    OPENAI_API_KEY = "openai-api-key"

    # External integrations
    ZENDESK_API_TOKEN = "zendesk-api-token"
    MAILCHIMP_API_KEY = "mailchimp-api-key"

    # Encryption (per-tenant Customer-Managed Key reference)
    CMK_KEY_ID = "cmk-key-id"

    # Custom webhook/integration secrets
    WEBHOOK_SIGNING_SECRET = "webhook-signing-secret"

    # MFA/TOTP seed (per-user, naming: user-{team_member_id}-totp-seed)
    TOTP_SEED = "totp-seed"


# ---------------------------------------------------------------------------
# Secret name construction
# ---------------------------------------------------------------------------


def build_secret_name(tenant_id: str, secret_type: TenantSecretType) -> str:
    """Build the Key Vault secret name from tenant ID and type.

    Format: tenant-{tenant_id}-{type_value}
    Example: tenant-abc123-shopify-token

    Key Vault secret names must be 1-127 characters, alphanumeric + hyphens.
    Tenant IDs are UUIDs (36 chars with hyphens), type values use hyphens.
    """
    return f"tenant-{tenant_id}-{secret_type.value}"


def parse_secret_name(name: str) -> tuple[str, str] | None:
    """Parse a Key Vault secret name into (tenant_id, type_suffix).

    Returns None if the name doesn't match the tenant secret pattern.
    """
    if not name.startswith("tenant-"):
        return None

    # Remove "tenant-" prefix
    remainder = name[7:]

    # Try to match against known secret types (longest match first)
    for secret_type in sorted(TenantSecretType, key=lambda t: -len(t.value)):
        suffix = f"-{secret_type.value}"
        if remainder.endswith(suffix):
            tenant_id = remainder[: -len(suffix)]
            if tenant_id:
                return (tenant_id, secret_type.value)

    return None


# ---------------------------------------------------------------------------
# TenantSecretService
# ---------------------------------------------------------------------------


class TenantSecretService:
    """Per-tenant secret management backed by Azure Key Vault.

    Provides enum-based access to secrets with the naming convention
    ``tenant-{id}-{type}`` per Decision #6.

    Features:
        - Type-safe access via TenantSecretType enum
        - Managed Identity authentication (default) or client secret
        - In-memory dev fallback when Key Vault is unavailable
        - GDPR-aware: list and delete all secrets for a tenant
        - Secret versioning (Key Vault native)
        - Health check for /ready integration

    Usage:
        service = get_secret_service()
        await service.store_secret("tenant-123", TenantSecretType.SHOPIFY_TOKEN, "shpat_xxx")
        value = await service.get_secret("tenant-123", TenantSecretType.SHOPIFY_TOKEN)
    """

    def __init__(self) -> None:
        self._client: Any = None  # azure.keyvault.secrets.aio.SecretClient
        self._vault_url: str = ""
        self._initialized: bool = False
        self._dev_mode: bool = False
        self._dev_store: dict[str, str] = {}  # In-memory fallback for dev

    async def initialize(self) -> None:
        """Initialize the Key Vault client.

        Reads configuration from environment and creates the async
        SecretClient. Falls back to in-memory mode if AZURE_KEYVAULT_URL
        is not set (development).
        """
        if self._initialized:
            return

        self._vault_url = os.environ.get("AZURE_KEYVAULT_URL", "")

        if not self._vault_url:
            logger.warning(
                "AZURE_KEYVAULT_URL not set — TenantSecretService running in "
                "DEVELOPMENT in-memory mode. Secrets are NOT persisted."
            )
            self._dev_mode = True
            self._initialized = True
            return

        try:
            from azure.identity.aio import DefaultAzureCredential
            from azure.keyvault.secrets.aio import SecretClient

            credential = DefaultAzureCredential()
            self._client = SecretClient(
                vault_url=self._vault_url,
                credential=credential,
            )
            self._initialized = True
            logger.info(
                "TenantSecretService initialized: vault=%s",
                self._vault_url,
            )
        except ImportError:
            logger.warning(
                "azure-keyvault-secrets or azure-identity not installed — "
                "TenantSecretService running in DEVELOPMENT in-memory mode."
            )
            self._dev_mode = True
            self._initialized = True
        except Exception as exc:
            logger.error(
                "Failed to initialize Key Vault client: %s — "
                "falling back to in-memory mode",
                exc,
            )
            self._dev_mode = True
            self._initialized = True

    def _ensure_initialized(self) -> None:
        """Raise if the service hasn't been initialized."""
        if not self._initialized:
            raise RuntimeError(
                "TenantSecretService not initialized. "
                "Call await service.initialize() first."
            )

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    async def store_secret(
        self,
        tenant_id: str,
        secret_type: TenantSecretType,
        value: str,
        *,
        tags: dict[str, str] | None = None,
    ) -> str:
        """Store a secret for a tenant.

        Args:
            tenant_id: Tenant identifier.
            secret_type: Type of secret (enum).
            value: The secret value to store.
            tags: Optional Key Vault tags (e.g., {"created_by": "provisioning"}).

        Returns:
            The secret name that was stored.
        """
        self._ensure_initialized()
        name = build_secret_name(tenant_id, secret_type)

        # Default tags for tracking
        all_tags = {
            "tenant_id": tenant_id,
            "secret_type": secret_type.value,
        }
        if tags:
            all_tags.update(tags)

        if self._dev_mode:
            self._dev_store[name] = value
            logger.debug(
                "DEV store_secret: %s (tenant=%s type=%s)",
                name, tenant_id, secret_type.value,
            )
            return name

        try:
            await self._client.set_secret(
                name,
                value,
                tags=all_tags,
            )
            logger.info(
                "Secret stored: %s (tenant=%s type=%s)",
                name, tenant_id, secret_type.value,
            )
        except Exception as exc:
            logger.error(
                "Failed to store secret %s: %s",
                name, exc,
            )
            raise

        return name

    async def get_secret(
        self,
        tenant_id: str,
        secret_type: TenantSecretType,
    ) -> str | None:
        """Retrieve a secret for a tenant.

        Args:
            tenant_id: Tenant identifier.
            secret_type: Type of secret (enum).

        Returns:
            The secret value, or None if not found.
        """
        self._ensure_initialized()
        name = build_secret_name(tenant_id, secret_type)

        if self._dev_mode:
            return self._dev_store.get(name)

        try:
            secret = await self._client.get_secret(name)
            return secret.value
        except Exception as exc:
            # ResourceNotFoundError from azure.core.exceptions
            exc_type = type(exc).__name__
            if "NotFound" in exc_type or "ResourceNotFound" in exc_type:
                return None
            logger.error("Failed to get secret %s: %s", name, exc)
            raise

    async def delete_secret(
        self,
        tenant_id: str,
        secret_type: TenantSecretType,
    ) -> bool:
        """Delete a specific secret for a tenant.

        Key Vault soft-deletes by default. The secret enters a
        "deleted" state and can be purged after the retention period.

        Args:
            tenant_id: Tenant identifier.
            secret_type: Type of secret (enum).

        Returns:
            True if the secret was deleted, False if it didn't exist.
        """
        self._ensure_initialized()
        name = build_secret_name(tenant_id, secret_type)

        if self._dev_mode:
            existed = name in self._dev_store
            self._dev_store.pop(name, None)
            return existed

        try:
            poller = await self._client.begin_delete_secret(name)
            await poller.wait()
            logger.info("Secret deleted: %s", name)
            return True
        except Exception as exc:
            exc_type = type(exc).__name__
            if "NotFound" in exc_type or "ResourceNotFound" in exc_type:
                return False
            logger.error("Failed to delete secret %s: %s", name, exc)
            raise

    # ------------------------------------------------------------------
    # Raw name access (for non-tenant-scoped secrets, e.g. MFA TOTP seeds)
    # ------------------------------------------------------------------

    async def get_secret_raw(self, name: str) -> str | None:
        """Retrieve a secret by raw Key Vault name (no tenant prefix)."""
        self._ensure_initialized()
        if self._dev_mode:
            return self._dev_store.get(name)
        try:
            secret = await self._client.get_secret(name)
            return secret.value
        except Exception as exc:
            exc_type = type(exc).__name__
            if "NotFound" in exc_type or "ResourceNotFound" in exc_type:
                return None
            logger.error("Failed to get raw secret %s: %s", name, exc)
            raise

    async def set_secret_raw(self, name: str, value: str) -> None:
        """Store a secret by raw Key Vault name (no tenant prefix)."""
        self._ensure_initialized()
        if self._dev_mode:
            self._dev_store[name] = value
            return
        await self._client.set_secret(name, value)

    async def delete_secret_raw(self, name: str) -> bool:
        """Delete a secret by raw Key Vault name (no tenant prefix)."""
        self._ensure_initialized()
        if self._dev_mode:
            existed = name in self._dev_store
            self._dev_store.pop(name, None)
            return existed
        try:
            poller = await self._client.begin_delete_secret(name)
            await poller.wait()
            return True
        except Exception as exc:
            exc_type = type(exc).__name__
            if "NotFound" in exc_type or "ResourceNotFound" in exc_type:
                return False
            logger.error("Failed to delete raw secret %s: %s", name, exc)
            raise

    async def delete_all_tenant_secrets(
        self,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Delete ALL secrets for a tenant (GDPR / deprovisioning).

        Iterates all known secret types and attempts deletion for each.
        Key Vault list_properties_of_secrets is used to find any
        additional secrets matching the tenant prefix.

        Returns:
            Dict with deletion results: {"deleted": [...], "not_found": [...], "errors": [...]}.
        """
        self._ensure_initialized()
        prefix = f"tenant-{tenant_id}-"
        deleted: list[str] = []
        not_found: list[str] = []
        errors: list[dict[str, str]] = []

        if self._dev_mode:
            # Find all matching dev secrets
            to_delete = [k for k in self._dev_store if k.startswith(prefix)]
            for key in to_delete:
                del self._dev_store[key]
                deleted.append(key)
            return {"deleted": deleted, "not_found": not_found, "errors": errors}

        # Strategy: iterate enum types + scan for any extra secrets
        # matching the tenant prefix that may not be in the enum
        # (future-proofing for secret types added later).

        # 1. Delete all known enum types
        for secret_type in TenantSecretType:
            name = build_secret_name(tenant_id, secret_type)
            try:
                poller = await self._client.begin_delete_secret(name)
                await poller.wait()
                deleted.append(name)
            except Exception as exc:
                exc_type = type(exc).__name__
                if "NotFound" in exc_type or "ResourceNotFound" in exc_type:
                    not_found.append(name)
                else:
                    errors.append({"name": name, "error": str(exc)})
                    logger.error("Error deleting secret %s: %s", name, exc)

        # 2. Scan for any additional secrets with this tenant prefix
        try:
            async for secret_props in self._client.list_properties_of_secrets():
                if (
                    secret_props.name
                    and secret_props.name.startswith(prefix)
                    and secret_props.name not in deleted
                    and secret_props.name not in not_found
                ):
                    try:
                        poller = await self._client.begin_delete_secret(
                            secret_props.name,
                        )
                        await poller.wait()
                        deleted.append(secret_props.name)
                    except Exception as inner_exc:
                        errors.append({
                            "name": secret_props.name,
                            "error": str(inner_exc),
                        })
        except Exception as exc:
            logger.warning(
                "Could not scan Key Vault for extra tenant secrets: %s", exc,
            )

        logger.info(
            "Tenant secrets deleted: tenant=%s deleted=%d not_found=%d errors=%d",
            tenant_id, len(deleted), len(not_found), len(errors),
        )

        return {"deleted": deleted, "not_found": not_found, "errors": errors}

    async def list_tenant_secrets(
        self,
        tenant_id: str,
    ) -> list[dict[str, Any]]:
        """List all secrets for a tenant (metadata only, no values).

        Returns:
            List of dicts with secret metadata:
            [{"name": "...", "type": "...", "created": "...", "updated": "..."}]
        """
        self._ensure_initialized()
        prefix = f"tenant-{tenant_id}-"
        results: list[dict[str, Any]] = []

        if self._dev_mode:
            for key in self._dev_store:
                if key.startswith(prefix):
                    parsed = parse_secret_name(key)
                    results.append({
                        "name": key,
                        "type": parsed[1] if parsed else "unknown",
                    })
            return results

        try:
            async for secret_props in self._client.list_properties_of_secrets():
                if secret_props.name and secret_props.name.startswith(prefix):
                    parsed = parse_secret_name(secret_props.name)
                    results.append({
                        "name": secret_props.name,
                        "type": parsed[1] if parsed else "unknown",
                        "created": (
                            secret_props.created_on.isoformat()
                            if secret_props.created_on
                            else None
                        ),
                        "updated": (
                            secret_props.updated_on.isoformat()
                            if secret_props.updated_on
                            else None
                        ),
                        "enabled": secret_props.enabled,
                    })
        except Exception as exc:
            logger.error("Failed to list secrets for tenant %s: %s", tenant_id, exc)
            raise

        return results

    async def rotate_secret(
        self,
        tenant_id: str,
        secret_type: TenantSecretType,
        new_value: str,
    ) -> str:
        """Rotate a secret by storing a new version.

        Key Vault automatically versions secrets — setting a new value
        creates a new version while preserving the old one. The latest
        version is always returned by get_secret().

        Args:
            tenant_id: Tenant identifier.
            secret_type: Type of secret (enum).
            new_value: The new secret value.

        Returns:
            The secret name.
        """
        # store_secret creates a new version in Key Vault
        return await self.store_secret(
            tenant_id,
            secret_type,
            new_value,
            tags={"rotated_at": str(int(time.time()))},
        )

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    async def health_check(self) -> dict[str, Any]:
        """Check Key Vault connectivity for readiness probes.

        Returns:
            Dict with health status and detail.
        """
        if not self._initialized:
            return {"status": "not_initialized", "detail": "Service not initialized"}

        if self._dev_mode:
            return {
                "status": "dev_mode",
                "detail": "In-memory mode (no Key Vault)",
                "secret_count": len(self._dev_store),
            }

        try:
            # List one secret as a lightweight connectivity check
            async for _ in self._client.list_properties_of_secrets():
                break
            return {"status": "healthy", "detail": "Key Vault connection OK"}
        except Exception as exc:
            logger.warning("Key Vault health check failed: %s", exc)
            return {"status": "unhealthy", "detail": str(exc)}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def close(self) -> None:
        """Close the Key Vault client and release resources."""
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("TenantSecretService closed")
        self._initialized = False
        self._dev_store.clear()


# ---------------------------------------------------------------------------
# KeyVaultDataStoreAdapter — GDPR integration (Decision #9)
# ---------------------------------------------------------------------------


class KeyVaultDataStoreAdapter:
    """DataStoreAdapter for Key Vault — enables GDPR export/deletion.

    Implements the DataStoreAdapter protocol from gdpr_services.py
    so that Key Vault secrets are included in tenant data export
    and deletion operations.
    """

    def __init__(self, secret_service: TenantSecretService) -> None:
        self._service = secret_service

    @property
    def store_name(self) -> str:
        """Human-readable store name for logging and audit."""
        return "key_vault"

    async def export_tenant_data(
        self,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Export secret metadata for a tenant (values excluded).

        Per GDPR export requirements, we export the existence and
        types of secrets — never the secret values themselves.
        """
        secrets = await self._service.list_tenant_secrets(tenant_id)
        return {
            "store": self.store_name,
            "secret_count": len(secrets),
            "secrets": [
                {k: v for k, v in s.items() if k != "value"}
                for s in secrets
            ],
        }

    async def export_customer_data(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> dict[str, Any]:
        """Customers don't have individual secrets in Key Vault."""
        return {"store": self.store_name, "data": {}}

    async def delete_tenant_data(
        self,
        tenant_id: str,
    ) -> dict[str, Any]:
        """Delete all secrets for a tenant from Key Vault."""
        result = await self._service.delete_all_tenant_secrets(tenant_id)
        return {
            "store": self.store_name,
            "deleted_count": len(result["deleted"]),
            "errors": result["errors"],
        }

    async def delete_customer_data(
        self,
        tenant_id: str,
        customer_id: str,
    ) -> dict[str, Any]:
        """Customers don't have individual secrets in Key Vault."""
        return {"store": self.store_name, "deleted_count": 0}


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service: TenantSecretService | None = None


def get_secret_service() -> TenantSecretService:
    """Get the singleton TenantSecretService instance.

    Returns:
        The global TenantSecretService. Call await service.initialize()
        before first use.
    """
    global _service
    if _service is None:
        _service = TenantSecretService()
    return _service
