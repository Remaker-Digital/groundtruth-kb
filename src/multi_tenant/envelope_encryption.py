# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Envelope Encryption Service — SPEC-1843 / WI-1624.

Provides application-level envelope encryption for tenant data using
AES-256-GCM with per-tenant Data Encryption Keys (DEKs).

Architecture:
  - Master KEK stored in Azure Key Vault (HSM-backed RSA-2048)
  - Per-tenant DEK: AES-256 key, wrapped by KEK, stored in Key Vault
  - Field-level encryption: AES-256-GCM with 96-bit random nonce
  - AAD (Additional Authenticated Data) = tenant_id + doc_id (tamper proof)

Dev mode: Uses in-memory KEK for local development without Key Vault.
"""
from __future__ import annotations

import base64
import hashlib
import logging
import os
import secrets
from typing import Any

logger = logging.getLogger(__name__)

# AES-256-GCM constants
_KEY_SIZE = 32          # 256 bits
_NONCE_SIZE = 12        # 96 bits (GCM standard)
_TAG_SIZE = 16          # 128-bit authentication tag

# Module-level singleton
_service: EnvelopeEncryptionService | None = None


def get_envelope_encryption_service() -> EnvelopeEncryptionService | None:
    """Return the singleton EnvelopeEncryptionService (or None if not initialized)."""
    return _service


def set_envelope_encryption_service(svc: EnvelopeEncryptionService) -> None:
    """Set the module-level singleton."""
    global _service
    _service = svc


class EnvelopeEncryptionService:
    """Envelope encryption: KEK wraps per-tenant DEKs, DEKs encrypt data.

    In production, the KEK is an RSA-2048 key in Azure Key Vault.
    In dev mode, a local AES-256 key is used for wrapping.
    """

    def __init__(self, *, dev_mode: bool = False, kek_key_id: str | None = None) -> None:
        self._dev_mode = dev_mode
        self._kek_key_id = kek_key_id
        self._dev_kek: bytes | None = None

        if dev_mode:
            # In-memory KEK for local development
            self._dev_kek = hashlib.sha256(b"dev-mode-kek-not-for-production").digest()
            logger.warning(
                "EnvelopeEncryptionService running in DEV MODE — "
                "using in-memory KEK (NOT SECURE FOR PRODUCTION)"
            )
        else:
            if not kek_key_id:
                raise ValueError(
                    "kek_key_id required in production mode. "
                    "Set MASTER_KEK_KEY_ID env var or pass explicitly."
                )
            logger.info("EnvelopeEncryptionService initialized with KEK: %s", kek_key_id)

    # -- KEK operations (wrap/unwrap DEK) -----------------------------------

    def create_tenant_dek(self, tenant_id: str) -> bytes:
        """Generate a new DEK for a tenant and return it wrapped by KEK.

        The wrapped DEK should be stored in Key Vault as
        ``tenant-{tenant_id}-dek``.

        Args:
            tenant_id: Tenant identifier (used as context for wrapping).

        Returns:
            Wrapped (encrypted) DEK bytes.
        """
        raw_dek = secrets.token_bytes(_KEY_SIZE)  # 256-bit random key
        wrapped = self._wrap_key(raw_dek, tenant_id)
        logger.info("DEK created for tenant %s (%d bytes wrapped)", tenant_id, len(wrapped))
        return wrapped

    def _wrap_key(self, raw_key: bytes, context: str) -> bytes:
        """Wrap (encrypt) a DEK using the KEK."""
        if self._dev_mode:
            return self._dev_wrap(raw_key, context)
        return self._kv_wrap(raw_key, context)

    def _unwrap_key(self, wrapped_key: bytes, context: str) -> bytes:
        """Unwrap (decrypt) a DEK using the KEK."""
        if self._dev_mode:
            return self._dev_unwrap(wrapped_key, context)
        return self._kv_unwrap(wrapped_key, context)

    # -- Dev-mode wrap/unwrap (AES-256-GCM with static KEK) -----------------

    def _dev_wrap(self, raw_key: bytes, context: str) -> bytes:
        """Dev-mode: wrap DEK with in-memory KEK using AES-256-GCM."""
        assert self._dev_kek is not None
        nonce = secrets.token_bytes(_NONCE_SIZE)
        aad = f"dek-wrap:{context}".encode()

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            cipher = AESGCM(self._dev_kek)
            ct = cipher.encrypt(nonce, raw_key, aad)
        except ImportError:
            # Fallback: XOR stub for environments without cryptography
            ct = self._xor_stub(raw_key, self._dev_kek, nonce)

        return nonce + ct  # nonce || ciphertext+tag

    def _dev_unwrap(self, wrapped: bytes, context: str) -> bytes:
        """Dev-mode: unwrap DEK with in-memory KEK."""
        assert self._dev_kek is not None
        nonce = wrapped[:_NONCE_SIZE]
        ct = wrapped[_NONCE_SIZE:]
        aad = f"dek-wrap:{context}".encode()

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            cipher = AESGCM(self._dev_kek)
            return cipher.decrypt(nonce, ct, aad)
        except ImportError:
            return self._xor_stub(ct, self._dev_kek, nonce)

    # -- Production Key Vault wrap/unwrap (placeholder) ---------------------

    def _kv_wrap(self, raw_key: bytes, context: str) -> bytes:
        """Production: wrap DEK using Azure Key Vault RSA-OAEP."""
        raise NotImplementedError(
            "Production KEK wrapping requires Azure Key Vault client. "
            "Set MASTER_KEK_KEY_ID and ensure managed identity has wrap permissions."
        )

    def _kv_unwrap(self, wrapped: bytes, context: str) -> bytes:
        """Production: unwrap DEK using Azure Key Vault RSA-OAEP."""
        raise NotImplementedError(
            "Production KEK unwrapping requires Azure Key Vault client. "
            "Set MASTER_KEK_KEY_ID and ensure managed identity has unwrap permissions."
        )

    # -- Field-level encrypt/decrypt (AES-256-GCM) --------------------------

    def encrypt_field(
        self,
        wrapped_dek: bytes,
        plaintext: str | None,
        *,
        tenant_id: str,
        doc_id: str,
    ) -> str | None:
        """Encrypt a single field value.

        Uses AES-256-GCM with AAD = tenant_id + doc_id for tamper detection.

        Args:
            wrapped_dek: KEK-wrapped DEK for this tenant.
            plaintext: Value to encrypt (None passes through).
            tenant_id: Tenant identifier (AAD component).
            doc_id: Document identifier (AAD component).

        Returns:
            Base64-encoded ciphertext string, or None if plaintext is None.
        """
        if plaintext is None:
            return None
        if plaintext == "":
            return ""  # Empty string is a valid non-sensitive value

        dek = self._unwrap_key(wrapped_dek, tenant_id)
        nonce = secrets.token_bytes(_NONCE_SIZE)
        aad = f"{tenant_id}:{doc_id}".encode()
        data = plaintext.encode("utf-8")

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            cipher = AESGCM(dek)
            ct = cipher.encrypt(nonce, data, aad)
        except ImportError:
            ct = self._xor_stub(data, dek, nonce)

        # Format: base64(nonce || ciphertext || tag)
        return base64.b64encode(nonce + ct).decode("ascii")

    def decrypt_field(
        self,
        wrapped_dek: bytes,
        ciphertext: str | None,
        *,
        tenant_id: str,
        doc_id: str,
    ) -> str | None:
        """Decrypt a single field value.

        Args:
            wrapped_dek: KEK-wrapped DEK for this tenant.
            ciphertext: Base64-encoded ciphertext (None passes through).
            tenant_id: Tenant identifier (AAD component).
            doc_id: Document identifier (AAD component).

        Returns:
            Decrypted plaintext string, or None if ciphertext is None.
        """
        if ciphertext is None:
            return None
        if ciphertext == "":
            return ""

        dek = self._unwrap_key(wrapped_dek, tenant_id)
        raw = base64.b64decode(ciphertext)
        nonce = raw[:_NONCE_SIZE]
        ct = raw[_NONCE_SIZE:]
        aad = f"{tenant_id}:{doc_id}".encode()

        try:
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            cipher = AESGCM(dek)
            plaintext_bytes = cipher.decrypt(nonce, ct, aad)
        except ImportError:
            plaintext_bytes = self._xor_stub(ct, dek, nonce)

        return plaintext_bytes.decode("utf-8")

    # -- XOR stub for dev environments without cryptography -----------------

    @staticmethod
    def _xor_stub(data: bytes, key: bytes, nonce: bytes) -> bytes:
        """Simple XOR cipher — NOT SECURE, dev fallback only."""
        expanded = (key * ((len(data) // len(key)) + 1))[:len(data)]
        return bytes(a ^ b for a, b in zip(data, expanded))
