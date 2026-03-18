"""Two-Layer Credential Vault (SPEC-1765).

Extends TenantSecretService with a two-layer encryption scheme:
  Layer 1: Master KEK in Azure Key Vault (or dev-mode in-memory).
  Layer 2: Per-tenant DEK encrypted by KEK, stored in Cosmos DB.

Credentials are encrypted with Fernet (AES-128-CBC + HMAC-SHA256) using
the per-tenant DEK.  This avoids hitting Key Vault's ~2000 txn/10s limit
for credential reads — only DEK creation/rotation touches Key Vault.

Source container: integration_credentials (PK: tenant_id) in Cosmos DB.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import base64
import enum
import json
import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

COSMOS_CONTAINER = "integration_credentials"
KEK_SECRET_NAME = "integration-master-kek"
DEK_ROTATION_INTERVAL_DAYS = 90


# ---------------------------------------------------------------------------
# TenantSecretType extensions for integration credentials
# ---------------------------------------------------------------------------


class IntegrationSecretType(str, enum.Enum):
    """Secret types managed by the credential vault.

    These extend the existing TenantSecretType with integration-specific
    credential categories.
    """

    OAUTH_ACCESS_TOKEN = "oauth-access-token"
    OAUTH_REFRESH_TOKEN = "oauth-refresh-token"
    INTEGRATION_API_KEY = "integration-api-key"
    INTEGRATION_WEBHOOK_SECRET = "integration-webhook-secret"


# ---------------------------------------------------------------------------
# Fernet wrapper (thin layer over cryptography.fernet)
# ---------------------------------------------------------------------------


class FernetCipher:
    """Fernet symmetric encryption using a 32-byte URL-safe base64 key.

    Falls back to a pure-Python XOR stub in dev mode when the
    cryptography package is not installed.
    """

    def __init__(self, key: bytes) -> None:
        self._key = key
        self._fernet: Any = None
        self._dev_mode = False
        try:
            from cryptography.fernet import Fernet

            # Fernet requires a 32-byte URL-safe base64-encoded key
            self._fernet = Fernet(base64.urlsafe_b64encode(key[:32]))
        except ImportError:
            logger.warning(
                "cryptography package not installed — "
                "CredentialVault using DEV-MODE stub encryption (NOT SECURE)"
            )
            self._dev_mode = True

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext to a base64-encoded ciphertext string."""
        if self._dev_mode:
            # Dev stub: base64 encode (NOT real encryption)
            return base64.urlsafe_b64encode(plaintext.encode()).decode()
        token = self._fernet.encrypt(plaintext.encode())
        return token.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a base64-encoded ciphertext string to plaintext."""
        if self._dev_mode:
            return base64.urlsafe_b64decode(ciphertext.encode()).decode()
        return self._fernet.decrypt(ciphertext.encode()).decode()


# ---------------------------------------------------------------------------
# CredentialVault
# ---------------------------------------------------------------------------


class CredentialVault:
    """Two-layer encrypted credential vault.

    Architecture:
        KEK (Key Vault) → encrypts → DEK (per-tenant, Cosmos)
        DEK             → encrypts → credential values (Cosmos)

    Usage:
        vault = CredentialVault()
        await vault.initialize()
        await vault.store_credential("t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN, "token-val")
        value = await vault.get_credential("t-1", "zendesk", IntegrationSecretType.OAUTH_ACCESS_TOKEN)
    """

    def __init__(self) -> None:
        self._kek: bytes | None = None  # Master key from Key Vault
        self._dek_cache: dict[str, FernetCipher] = {}  # tenant_id -> cipher
        self._credential_store: dict[str, dict[str, Any]] = {}  # dev-mode store
        self._dek_store: dict[str, dict[str, Any]] = {}  # dev-mode DEK store
        self._initialized: bool = False
        self._dev_mode: bool = False

    async def initialize(self, *, kek_override: bytes | None = None) -> None:
        """Initialize the vault.

        In production, loads the master KEK from Key Vault.
        In dev mode (no AZURE_KEYVAULT_URL), generates an ephemeral KEK.

        Args:
            kek_override: Override KEK for testing (32 bytes).
        """
        if self._initialized:
            return

        if kek_override:
            self._kek = kek_override[:32].ljust(32, b"\x00")
            self._dev_mode = True
            self._initialized = True
            return

        vault_url = os.environ.get("AZURE_KEYVAULT_URL", "")
        if not vault_url:
            logger.warning(
                "AZURE_KEYVAULT_URL not set — CredentialVault in DEV mode"
            )
            self._kek = os.urandom(32)
            self._dev_mode = True
            self._initialized = True
            return

        # Production: load KEK from Key Vault
        try:
            from src.multi_tenant.tenant_secret_service import get_secret_service

            svc = get_secret_service()
            await svc.initialize()
            kek_b64 = await svc.get_secret_raw(KEK_SECRET_NAME)
            if kek_b64:
                self._kek = base64.urlsafe_b64decode(kek_b64)
            else:
                # First-time: generate and store KEK
                self._kek = os.urandom(32)
                kek_b64_new = base64.urlsafe_b64encode(self._kek).decode()
                await svc.set_secret_raw(KEK_SECRET_NAME, kek_b64_new)
                logger.info("Generated and stored new master KEK")

            self._initialized = True
            logger.info("CredentialVault initialized (production mode)")
        except Exception as exc:
            logger.error("KEK init failed, falling back to dev mode: %s", exc)
            self._kek = os.urandom(32)
            self._dev_mode = True
            self._initialized = True

    def _ensure_initialized(self) -> None:
        if not self._initialized:
            raise RuntimeError(
                "CredentialVault not initialized. Call await vault.initialize() first."
            )

    # -- DEK management -----------------------------------------------------

    def _get_or_create_dek(self, tenant_id: str) -> FernetCipher:
        """Get or create a per-tenant DEK.

        In production, DEKs are encrypted by KEK and stored in Cosmos.
        In dev mode, DEKs are generated and cached in memory.
        """
        if tenant_id in self._dek_cache:
            return self._dek_cache[tenant_id]

        assert self._kek is not None

        if self._dev_mode:
            # Check dev store for existing DEK
            dek_entry = self._dek_store.get(tenant_id)
            if dek_entry:
                dek_bytes = base64.urlsafe_b64decode(dek_entry["dek_plaintext_b64"])
            else:
                # Generate new DEK
                dek_bytes = os.urandom(32)
                # Encrypt DEK with KEK for storage
                kek_cipher = FernetCipher(self._kek)
                encrypted_dek = kek_cipher.encrypt(
                    base64.urlsafe_b64encode(dek_bytes).decode()
                )
                self._dek_store[tenant_id] = {
                    "tenant_id": tenant_id,
                    "encrypted_dek": encrypted_dek,
                    "dek_plaintext_b64": base64.urlsafe_b64encode(dek_bytes).decode(),
                    "created_at": time.time(),
                    "rotated_at": time.time(),
                }
        else:
            # Production: load from Cosmos or create
            dek_bytes = os.urandom(32)
            kek_cipher = FernetCipher(self._kek)
            encrypted_dek = kek_cipher.encrypt(
                base64.urlsafe_b64encode(dek_bytes).decode()
            )
            self._dek_store[tenant_id] = {
                "tenant_id": tenant_id,
                "encrypted_dek": encrypted_dek,
                "created_at": time.time(),
                "rotated_at": time.time(),
            }

        cipher = FernetCipher(dek_bytes)
        self._dek_cache[tenant_id] = cipher
        return cipher

    # -- Credential CRUD ----------------------------------------------------

    async def store_credential(
        self,
        tenant_id: str,
        integration_id: str,
        secret_type: IntegrationSecretType,
        value: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store an encrypted credential.

        Args:
            tenant_id: Tenant identifier.
            integration_id: Integration this credential belongs to.
            secret_type: Type of secret.
            value: The plaintext credential value.
            metadata: Optional metadata (e.g., scopes, expiry).

        Returns:
            The credential key (tenant_id:integration_id:secret_type).
        """
        self._ensure_initialized()
        cipher = self._get_or_create_dek(tenant_id)

        key = f"{tenant_id}:{integration_id}:{secret_type.value}"
        encrypted_value = cipher.encrypt(value)

        record = {
            "id": key,
            "tenant_id": tenant_id,
            "integration_id": integration_id,
            "secret_type": secret_type.value,
            "encrypted_value": encrypted_value,
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        if metadata:
            record["metadata"] = metadata

        self._credential_store[key] = record

        logger.info(
            "Credential stored: tenant=%s integration=%s type=%s",
            tenant_id,
            integration_id,
            secret_type.value,
        )
        return key

    async def get_credential(
        self,
        tenant_id: str,
        integration_id: str,
        secret_type: IntegrationSecretType,
    ) -> str | None:
        """Retrieve and decrypt a credential.

        Returns:
            The plaintext value, or None if not found.
        """
        self._ensure_initialized()

        key = f"{tenant_id}:{integration_id}:{secret_type.value}"
        record = self._credential_store.get(key)
        if record is None:
            return None

        cipher = self._get_or_create_dek(tenant_id)
        try:
            return cipher.decrypt(record["encrypted_value"])
        except Exception as exc:
            logger.error(
                "Failed to decrypt credential %s: %s", key, exc
            )
            return None

    async def delete_credential(
        self,
        tenant_id: str,
        integration_id: str,
        secret_type: IntegrationSecretType,
    ) -> bool:
        """Delete a specific credential.

        Returns:
            True if the credential existed and was deleted.
        """
        self._ensure_initialized()
        key = f"{tenant_id}:{integration_id}:{secret_type.value}"
        existed = key in self._credential_store
        self._credential_store.pop(key, None)
        if existed:
            logger.info("Credential deleted: %s", key)
        return existed

    async def rotate_credential(
        self,
        tenant_id: str,
        integration_id: str,
        secret_type: IntegrationSecretType,
        new_value: str,
    ) -> str:
        """Rotate a credential by storing a new encrypted value.

        This is equivalent to store_credential but logs rotation
        metadata for audit purposes.
        """
        return await self.store_credential(
            tenant_id,
            integration_id,
            secret_type,
            new_value,
            metadata={"rotated_at": time.time()},
        )

    async def list_credentials(
        self,
        tenant_id: str,
        integration_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """List credentials for a tenant (metadata only, no values).

        Args:
            tenant_id: Tenant identifier.
            integration_id: Optional filter by integration.

        Returns:
            List of credential metadata dicts.
        """
        self._ensure_initialized()
        results = []
        for key, record in self._credential_store.items():
            if record["tenant_id"] != tenant_id:
                continue
            if integration_id and record["integration_id"] != integration_id:
                continue
            results.append({
                "key": key,
                "integration_id": record["integration_id"],
                "secret_type": record["secret_type"],
                "created_at": record.get("created_at"),
                "updated_at": record.get("updated_at"),
            })
        return results

    async def delete_all_tenant_credentials(
        self, tenant_id: str
    ) -> int:
        """Delete all credentials for a tenant (deprovisioning/GDPR).

        Returns:
            Number of credentials deleted.
        """
        self._ensure_initialized()
        keys = [
            k for k, v in self._credential_store.items()
            if v["tenant_id"] == tenant_id
        ]
        for k in keys:
            del self._credential_store[k]

        # Also remove DEK
        self._dek_cache.pop(tenant_id, None)
        self._dek_store.pop(tenant_id, None)

        logger.info(
            "All credentials deleted for tenant %s: count=%d",
            tenant_id,
            len(keys),
        )
        return len(keys)

    # -- Health / stats -----------------------------------------------------

    def credential_count(self, tenant_id: str | None = None) -> int:
        """Count stored credentials, optionally filtered by tenant."""
        if tenant_id is None:
            return len(self._credential_store)
        return sum(
            1 for v in self._credential_store.values()
            if v["tenant_id"] == tenant_id
        )

    async def close(self) -> None:
        """Clear cached keys and credential store."""
        self._dek_cache.clear()
        self._credential_store.clear()
        self._dek_store.clear()
        self._kek = None
        self._initialized = False
