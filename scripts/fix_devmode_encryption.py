#!/usr/bin/env python3
"""Fix dev-mode encryption: decrypt fields that were encrypted with dev-mode KEK.

The S263 encryption migration ran without MASTER_KEK_KEY_ID, causing data to be
encrypted with the dev-mode in-memory test KEK. This script decrypts those fields
back to plaintext so the migration can be re-run with the correct production KEK.

Usage:
    # Dry run (preview only):
    COSMOS_DB_DATABASE=agentred python scripts/fix_devmode_encryption.py --dry-run --force

    # Fix production:
    COSMOS_DB_DATABASE=agentred python scripts/fix_devmode_encryption.py --force

Safety:
    - Requires --force for production database (same gate as migration)
    - Supports --dry-run to preview without writing
    - Logs every field change for audit trail

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import hashlib
import logging
import os
import secrets
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env.local if present
_env_local = os.path.join(os.path.dirname(__file__), "..", ".env.local")
if os.path.exists(_env_local):
    with open(_env_local, "rb") as _f:
        for _line in _f:
            _line = _line.decode("utf-8", errors="replace").strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

logger = logging.getLogger("fix_devmode_encryption")

# Dev-mode KEK (same as envelope_encryption.py:79)
DEV_KEK = hashlib.sha256(b"dev-mode-kek-not-for-production").digest()
NONCE_SIZE = 12  # 96-bit nonce for AES-GCM

# Collections and their encrypted fields (must match repository declarations)
ENCRYPTED_COLLECTIONS: dict[str, list[str]] = {
    "tenants": ["customer_email", "shopify_shop_domain", "brand_name"],
    "team_members": ["email", "display_name"],
    "conversations": ["messages", "customer_intent", "escalation_reason", "transcript"],
    "customer_profiles": [
        "email", "phone", "display_name", "contact_attributes",
        "first_seen_channel", "last_seen_channel",
    ],
    "preferences": ["whatsapp_business_phone"],
    "knowledge_bases": ["content", "source_url", "title"],
    "memory_vectors": ["text", "metadata_json"],
}


def _looks_encrypted(value: str) -> bool:
    """Heuristic: base64-encoded ciphertext is all printable and not natural text."""
    if not value or len(value) < 20:
        return False
    try:
        raw = base64.b64decode(value)
        # AES-GCM ciphertext: nonce (12) + ct + tag (16) = at least 29 bytes
        return len(raw) >= 29
    except Exception:
        return False


def _decrypt_dev_field(ciphertext_b64: str, tenant_id: str, doc_id: str) -> str | None:
    """Decrypt a field that was encrypted with dev-mode envelope encryption.

    The field-level encryption uses:
    - DEK: unwrapped from KV using dev-mode KEK
    - AAD: "tenant_id:doc_id" (per base.py _pre_write)
    - Format: nonce (12) || ciphertext || tag (16), all base64-encoded
    """
    # Actually, the field-level encryption uses the raw DEK directly,
    # not the dev KEK. We need the DEK from Key Vault first.
    # But the DEK itself was wrapped with the dev KEK.
    # So we need: KV -> wrapped DEK -> dev_unwrap -> raw DEK -> decrypt field
    raise NotImplementedError("Need DEK from Key Vault first")


def _dev_unwrap_dek(wrapped_dek_b64: str, tenant_id: str) -> bytes:
    """Unwrap a DEK that was wrapped with dev-mode KEK."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    wrapped = base64.b64decode(wrapped_dek_b64)
    nonce = wrapped[:NONCE_SIZE]
    ct = wrapped[NONCE_SIZE:]
    aad = f"dek-wrap:{tenant_id}".encode()

    cipher = AESGCM(DEV_KEK)
    return cipher.decrypt(nonce, ct, aad)


def _decrypt_field(raw_dek: bytes, ciphertext_b64: str, tenant_id: str, doc_id: str) -> str:
    """Decrypt a field using the raw DEK."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    raw = base64.b64decode(ciphertext_b64)
    nonce = raw[:NONCE_SIZE]
    ct = raw[NONCE_SIZE:]
    aad = f"{tenant_id}:{doc_id}".encode()

    cipher = AESGCM(raw_dek)
    plaintext = cipher.decrypt(nonce, ct, aad)
    return plaintext.decode("utf-8")


async def _get_wrapped_dek_from_kv(tenant_id: str) -> str | None:
    """Fetch the wrapped DEK from Key Vault."""
    vault_url = os.environ.get("AZURE_KEYVAULT_URL", "")
    if not vault_url:
        vault_url = os.environ.get("KEY_VAULT_URL", "")
    if not vault_url:
        logger.error("No AZURE_KEYVAULT_URL or KEY_VAULT_URL set")
        return None

    from azure.identity.aio import DefaultAzureCredential
    from azure.keyvault.secrets.aio import SecretClient

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    try:
        secret_name = f"tenant-{tenant_id}-dek"
        secret = await client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        logger.warning("Could not fetch DEK for %s: %s", tenant_id, e)
        return None
    finally:
        await client.close()
        await credential.close()


async def fix_tenant(
    tenant_id: str,
    cosmos_db: Any,
    dry_run: bool,
) -> dict[str, int]:
    """Fix encryption for one tenant. Returns {collection: fields_fixed}."""
    stats: dict[str, int] = {}

    # Get the wrapped DEK from Key Vault
    wrapped_dek_b64 = await _get_wrapped_dek_from_kv(tenant_id)
    if not wrapped_dek_b64:
        logger.warning("No DEK found for tenant %s — skipping", tenant_id)
        return stats

    # Unwrap DEK using dev-mode KEK
    try:
        raw_dek = _dev_unwrap_dek(wrapped_dek_b64, tenant_id)
        logger.info("DEK unwrapped for %s (%d bytes)", tenant_id, len(raw_dek))
    except Exception as e:
        logger.error("Failed to unwrap DEK for %s: %s", tenant_id, e)
        return stats

    # Process each collection
    for collection_name, fields in ENCRYPTED_COLLECTIONS.items():
        container = cosmos_db.get_container_client(collection_name)
        fixed = 0

        # Query all documents in this tenant's partition
        query = "SELECT * FROM c"
        try:
            items = list(container.query_items(
                query=query,
                partition_key=tenant_id,
            ))
        except Exception as e:
            logger.warning("Could not query %s for %s: %s", collection_name, tenant_id, e)
            continue

        for doc in items:
            doc_id = doc.get("id", "")
            changes: dict[str, str] = {}

            for field in fields:
                value = doc.get(field)
                if not isinstance(value, str) or not value:
                    continue
                if not _looks_encrypted(value):
                    continue

                try:
                    plaintext = _decrypt_field(raw_dek, value, tenant_id, doc_id)
                    changes[field] = plaintext
                    logger.info(
                        "  %s/%s.%s: decrypted (%d chars -> %d chars)",
                        collection_name, doc_id[:12], field,
                        len(value), len(plaintext),
                    )
                except Exception as e:
                    logger.warning(
                        "  %s/%s.%s: decrypt failed (%s) — skipping",
                        collection_name, doc_id[:12], field, e,
                    )

            if changes and not dry_run:
                # Write plaintext back to Cosmos
                for field, plaintext in changes.items():
                    doc[field] = plaintext
                try:
                    container.replace_item(item=doc_id, body=doc)
                    fixed += len(changes)
                except Exception as e:
                    logger.error(
                        "  %s/%s: replace failed: %s",
                        collection_name, doc_id[:12], e,
                    )
            elif changes:
                fixed += len(changes)
                logger.info("  [DRY RUN] Would fix %d fields in %s/%s",
                            len(changes), collection_name, doc_id[:12])

        if fixed:
            stats[collection_name] = fixed

    return stats


async def main_async(dry_run: bool, force: bool) -> None:
    """Main entry point."""
    db_name = os.environ.get("COSMOS_DB_DATABASE", "")
    logger.info("Target database: %s", db_name or "(not set)")

    if not force:
        if "staging" not in db_name and "dev" not in db_name:
            logger.error(
                "SAFETY GATE: COSMOS_DB_DATABASE=%s looks like production. "
                "Pass --force to confirm.",
                db_name,
            )
            return

    # Initialize Cosmos client
    from azure.cosmos import CosmosClient

    endpoint = os.environ["COSMOS_DB_ENDPOINT"]
    key = os.environ["COSMOS_DB_KEY"]
    client = CosmosClient(endpoint, key)
    cosmos_db = client.get_database_client(db_name)

    # Get all tenants
    tenants_container = cosmos_db.get_container_client("tenants")
    tenants = list(tenants_container.query_items(
        query="SELECT c.id FROM c",
        enable_cross_partition_query=True,
    ))
    logger.info("Found %d tenants", len(tenants))

    total_fixed = 0
    for tenant_doc in tenants:
        tenant_id = tenant_doc["id"]
        logger.info("Processing tenant: %s", tenant_id)
        stats = await fix_tenant(tenant_id, cosmos_db, dry_run)
        for coll, count in stats.items():
            logger.info("  %s: %d fields %s",
                        coll, count, "would be fixed" if dry_run else "fixed")
            total_fixed += count

    action = "would be fixed" if dry_run else "fixed"
    logger.info("TOTAL: %d fields %s across %d tenants", total_fixed, action, len(tenants))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fix dev-mode encrypted fields by decrypting to plaintext"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--force", action="store_true", help="Bypass production safety gate")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    asyncio.run(main_async(dry_run=args.dry_run, force=args.force))


if __name__ == "__main__":
    main()
