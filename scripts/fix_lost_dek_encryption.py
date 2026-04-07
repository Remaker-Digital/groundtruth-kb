#!/usr/bin/env python3
"""Fix lost-DEK encryption: overwrite unrecoverable ciphertext with known plaintext.

Root cause: S263 encryption migration ran in dev-mode (MASTER_KEK_KEY_ID and
AZURE_KEYVAULT_URL absent from .env.local). DEKs were created in-memory (dev store)
and lost when the script exited. A subsequent DEK provisioning step stored NEW
RSA-wrapped DEKs in KV, but these don't match the DEKs used to encrypt the data.

Two-phase remediation:
    Phase 1 (--inventory): Discover affected tenants/documents/fields and DEK secrets.
        Outputs a machine-readable JSON inventory file. No writes.
    Phase 2 (--execute <inventory.json>): Apply fixes using the reviewed inventory
        as an explicit allowlist. Only touches items listed in the inventory.

Usage:
    # Phase 1 — produce inventory (always safe, read-only):
    COSMOS_DB_DATABASE=agentred python scripts/fix_lost_dek_encryption.py --inventory --force

    # Phase 2 — apply fixes from reviewed inventory:
    COSMOS_DB_DATABASE=agentred python scripts/fix_lost_dek_encryption.py \
        --execute remediation-inventory-*.json --force

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env.local
_env_local = os.path.join(os.path.dirname(__file__), "..", ".env.local")
if os.path.exists(_env_local):
    with open(_env_local, "rb") as _f:
        for _line in _f:
            _line = _line.decode("utf-8", errors="replace").strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

logger = logging.getLogger("fix_lost_dek")

# Known plaintext values for seeded tenants (from seed_tenant.py).
# Tenants not in this map will have encrypted fields cleared to empty string.
KNOWN_PLAINTEXT: dict[str, dict[str, str]] = {
    "remaker-digital-001": {
        "customer_email": "mike@remakerdigital.com",
        "shopify_shop_domain": "blanco-9939.myshopify.com",
        "brand_name": "",
    },
    "test-customer-001": {
        "customer_email": "test-customer@remakerdigital.com",
        "shopify_shop_domain": "",
        "brand_name": "",
    },
}

KNOWN_TEAM_MEMBER_PLAINTEXT: dict[str, dict[str, str]] = {
    "remaker-digital-001": {"email": "mike@remakerdigital.com", "display_name": "Mike"},
    "test-customer-001": {"email": "test-customer@remakerdigital.com", "display_name": "Test Customer"},
}

# Fields that were encrypted by the S263 migration (tenants + team_members collections only).
TENANT_ENCRYPTED_FIELDS = ["customer_email", "shopify_shop_domain", "brand_name"]
TEAM_MEMBER_ENCRYPTED_FIELDS = ["email", "display_name"]


def _looks_encrypted(value: str) -> bool:
    """Check if value looks like base64 AES-256-GCM ciphertext."""
    if not value or len(value) < 20:
        return False
    try:
        raw = base64.b64decode(value)
        return len(raw) >= 29  # nonce(12) + min ct + tag(16)
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────
# Phase 1: Inventory (read-only discovery)
# ──────────────────────────────────────────────────────────────────────

async def build_inventory() -> dict:
    """Scan for affected documents and DEK secrets. Returns inventory dict."""
    from azure.cosmos import CosmosClient

    client = CosmosClient(os.environ["COSMOS_DB_ENDPOINT"], os.environ["COSMOS_DB_KEY"])
    db = client.get_database_client(os.environ["COSMOS_DB_DATABASE"])

    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": os.environ["COSMOS_DB_DATABASE"],
        "affected_tenants": [],
        "affected_team_members": [],
        "stale_dek_secrets": [],
        "summary": {"tenant_docs": 0, "team_member_docs": 0, "fields": 0, "dek_secrets": 0},
    }

    # Scan tenants collection
    container = db.get_container_client("tenants")
    all_tenants = list(container.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True,
    ))
    for doc in all_tenants:
        tid = doc["id"]
        affected_fields = {}
        for field in TENANT_ENCRYPTED_FIELDS:
            current = doc.get(field, "")
            if _looks_encrypted(current):
                plaintext = KNOWN_PLAINTEXT.get(tid, {}).get(field, "")
                affected_fields[field] = {
                    "ciphertext_length": len(current),
                    "restoration_value": plaintext,
                    "restoration_source": "known_plaintext" if tid in KNOWN_PLAINTEXT else "clear_to_empty",
                }
        if affected_fields:
            inventory["affected_tenants"].append({
                "tenant_id": tid,
                "document_id": doc["id"],
                "partition_key": tid,
                "fields": affected_fields,
            })
            inventory["summary"]["tenant_docs"] += 1
            inventory["summary"]["fields"] += len(affected_fields)

    # Scan team_members collection
    tm_container = db.get_container_client("team_members")
    for tenant_entry in inventory["affected_tenants"]:
        tid = tenant_entry["tenant_id"]
        items = list(tm_container.query_items(
            query="SELECT * FROM c",
            partition_key=tid,
        ))
        for doc in items:
            affected_fields = {}
            for field in TEAM_MEMBER_ENCRYPTED_FIELDS:
                current = doc.get(field, "")
                if _looks_encrypted(current):
                    plaintext = KNOWN_TEAM_MEMBER_PLAINTEXT.get(tid, {}).get(field, "")
                    affected_fields[field] = {
                        "ciphertext_length": len(current),
                        "restoration_value": plaintext,
                        "restoration_source": "known_plaintext" if tid in KNOWN_TEAM_MEMBER_PLAINTEXT else "clear_to_empty",
                    }
            if affected_fields:
                inventory["affected_team_members"].append({
                    "tenant_id": tid,
                    "document_id": doc["id"],
                    "partition_key": tid,
                    "fields": affected_fields,
                })
                inventory["summary"]["team_member_docs"] += 1
                inventory["summary"]["fields"] += len(affected_fields)

    # Also scan team_members for tenants NOT in affected_tenants (belt-and-suspenders)
    affected_tids = {t["tenant_id"] for t in inventory["affected_tenants"]}
    for tid, pt in KNOWN_TEAM_MEMBER_PLAINTEXT.items():
        if tid not in affected_tids:
            items = list(tm_container.query_items(
                query="SELECT * FROM c", partition_key=tid,
            ))
            for doc in items:
                affected_fields = {}
                for field in TEAM_MEMBER_ENCRYPTED_FIELDS:
                    current = doc.get(field, "")
                    if _looks_encrypted(current):
                        affected_fields[field] = {
                            "ciphertext_length": len(current),
                            "restoration_value": pt.get(field, ""),
                            "restoration_source": "known_plaintext",
                        }
                if affected_fields:
                    inventory["affected_team_members"].append({
                        "tenant_id": tid, "document_id": doc["id"],
                        "partition_key": tid, "fields": affected_fields,
                    })
                    inventory["summary"]["team_member_docs"] += 1
                    inventory["summary"]["fields"] += len(affected_fields)

    # Scan KV for stale DEK secrets
    try:
        from azure.identity.aio import DefaultAzureCredential
        from azure.keyvault.secrets.aio import SecretClient

        vault_url = os.environ.get("PRODUCTION_AZURE_KEYVAULT_URL",
                                   os.environ.get("AZURE_KEYVAULT_URL", ""))
        if vault_url:
            cred = DefaultAzureCredential()
            kv_client = SecretClient(vault_url=vault_url, credential=cred)
            try:
                async for prop in kv_client.list_properties_of_secrets():
                    if prop.name.startswith("tenant-") and prop.name.endswith("-dek"):
                        inventory["stale_dek_secrets"].append({
                            "secret_name": prop.name,
                            "vault_url": vault_url,
                            "created": prop.created_on.isoformat() if prop.created_on else None,
                        })
                        inventory["summary"]["dek_secrets"] += 1
            finally:
                await kv_client.close()
                await cred.close()
        else:
            logger.warning("No AZURE_KEYVAULT_URL set — skipping DEK secret scan")
    except Exception as e:
        logger.warning("KV scan failed (credentials may be stale): %s", e)
        inventory["stale_dek_secrets"] = [{"error": str(e)}]

    return inventory


# ──────────────────────────────────────────────────────────────────────
# Phase 2: Execute from reviewed inventory (explicit allowlist)
# ──────────────────────────────────────────────────────────────────────

async def execute_from_inventory(inventory_path: str) -> dict:
    """Apply fixes using a reviewed inventory file as the explicit allowlist."""
    with open(inventory_path) as f:
        inventory = json.load(f)

    from azure.cosmos import CosmosClient

    client = CosmosClient(os.environ["COSMOS_DB_ENDPOINT"], os.environ["COSMOS_DB_KEY"])
    db = client.get_database_client(os.environ["COSMOS_DB_DATABASE"])

    # Verify inventory matches current database
    if inventory["database"] != os.environ["COSMOS_DB_DATABASE"]:
        logger.error(
            "SAFETY: Inventory was generated for database '%s' but current target is '%s'. Aborting.",
            inventory["database"], os.environ["COSMOS_DB_DATABASE"],
        )
        sys.exit(1)

    results = {"tenants_fixed": 0, "team_members_fixed": 0, "fields_fixed": 0, "deks_deleted": 0, "errors": []}

    # Fix tenants — only those listed in inventory
    container = db.get_container_client("tenants")
    for entry in inventory.get("affected_tenants", []):
        tid = entry["tenant_id"]
        doc_id = entry["document_id"]
        pk = entry["partition_key"]
        try:
            items = list(container.query_items(
                query="SELECT * FROM c WHERE c.id=@id",
                parameters=[{"name": "@id", "value": doc_id}],
                partition_key=pk,
            ))
            if not items:
                logger.warning("Tenant doc %s not found — skipping", doc_id)
                results["errors"].append(f"tenant {doc_id} not found")
                continue

            doc = items[0]
            changed = False
            for field, field_info in entry["fields"].items():
                current = doc.get(field, "")
                if _looks_encrypted(current):
                    doc[field] = field_info["restoration_value"]
                    changed = True
                    results["fields_fixed"] += 1
                    logger.info("  tenants/%s.%s: restored (%s)", tid, field, field_info["restoration_source"])
                else:
                    logger.info("  tenants/%s.%s: already plaintext — skipping", tid, field)

            if changed:
                container.replace_item(item=doc["id"], body=doc)
                results["tenants_fixed"] += 1
        except Exception as e:
            logger.error("Error fixing tenant %s: %s", tid, e)
            results["errors"].append(f"tenant {tid}: {e}")

    # Fix team_members — only those listed in inventory
    tm_container = db.get_container_client("team_members")
    for entry in inventory.get("affected_team_members", []):
        tid = entry["tenant_id"]
        doc_id = entry["document_id"]
        pk = entry["partition_key"]
        try:
            items = list(tm_container.query_items(
                query="SELECT * FROM c WHERE c.id=@id",
                parameters=[{"name": "@id", "value": doc_id}],
                partition_key=pk,
            ))
            if not items:
                logger.warning("Team member doc %s not found — skipping", doc_id)
                results["errors"].append(f"team_member {doc_id} not found")
                continue

            doc = items[0]
            changed = False
            for field, field_info in entry["fields"].items():
                current = doc.get(field, "")
                if _looks_encrypted(current):
                    doc[field] = field_info["restoration_value"]
                    changed = True
                    results["fields_fixed"] += 1
                    logger.info("  team_members/%s/%s.%s: restored", tid, doc_id[:12], field)
                else:
                    logger.info("  team_members/%s/%s.%s: already plaintext", tid, doc_id[:12], field)

            if changed:
                tm_container.replace_item(item=doc["id"], body=doc)
                results["team_members_fixed"] += 1
        except Exception as e:
            logger.error("Error fixing team member %s/%s: %s", tid, doc_id, e)
            results["errors"].append(f"team_member {tid}/{doc_id}: {e}")

    # Delete DEK secrets — only those listed in inventory
    dek_entries = [e for e in inventory.get("stale_dek_secrets", []) if "secret_name" in e]
    if dek_entries:
        try:
            from azure.identity.aio import DefaultAzureCredential
            from azure.keyvault.secrets.aio import SecretClient

            vault_url = dek_entries[0]["vault_url"]
            cred = DefaultAzureCredential()
            kv_client = SecretClient(vault_url=vault_url, credential=cred)
            try:
                for entry in dek_entries:
                    secret_name = entry["secret_name"]
                    try:
                        await kv_client.delete_secret(secret_name)
                        results["deks_deleted"] += 1
                        logger.info("  Deleted DEK secret: %s", secret_name)
                    except Exception as e:
                        logger.error("Error deleting DEK %s: %s", secret_name, e)
                        results["errors"].append(f"dek {secret_name}: {e}")
            finally:
                await kv_client.close()
                await cred.close()
        except Exception as e:
            logger.error("KV cleanup failed: %s", e)
            results["errors"].append(f"kv_cleanup: {e}")

    return results


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

async def main_async(args: argparse.Namespace) -> None:
    db_name = os.environ.get("COSMOS_DB_DATABASE", "")
    logger.info("Target database: %s", db_name or "(not set)")

    if not args.force:
        if "staging" not in db_name and "dev" not in db_name:
            logger.error(
                "SAFETY GATE: COSMOS_DB_DATABASE=%s looks like production. "
                "Pass --force to confirm.",
                db_name,
            )
            sys.exit(1)

    if args.inventory:
        logger.info("Phase 1: Building inventory of affected documents and DEK secrets...")
        inventory = await build_inventory()

        filename = f"remediation-inventory-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "w") as f:
            json.dump(inventory, f, indent=2)

        logger.info("Inventory written to: %s", filepath)
        logger.info("Summary: %d tenant docs, %d team_member docs, %d fields, %d DEK secrets",
                     inventory["summary"]["tenant_docs"],
                     inventory["summary"]["team_member_docs"],
                     inventory["summary"]["fields"],
                     inventory["summary"]["dek_secrets"])
        logger.info("REVIEW this inventory, then run with --execute %s --force", filename)

    elif args.execute:
        if not os.path.exists(args.execute):
            logger.error("Inventory file not found: %s", args.execute)
            sys.exit(1)

        logger.info("Phase 2: Executing remediation from inventory: %s", args.execute)
        results = await execute_from_inventory(args.execute)

        logger.info("Results: %d tenants fixed, %d team_members fixed, %d fields restored, %d DEKs deleted",
                     results["tenants_fixed"], results["team_members_fixed"],
                     results["fields_fixed"], results["deks_deleted"])
        if results["errors"]:
            logger.warning("Errors: %s", results["errors"])
            sys.exit(1)
        logger.info("DONE. Re-run encryption migration with correct env vars to re-encrypt.")

    else:
        logger.error("Specify --inventory (Phase 1) or --execute <file> (Phase 2).")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix lost-DEK encrypted fields (two-phase)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--inventory", action="store_true",
                       help="Phase 1: discover affected items and output JSON inventory")
    group.add_argument("--execute", type=str, metavar="INVENTORY_FILE",
                       help="Phase 2: apply fixes from a reviewed inventory file")
    parser.add_argument("--force", action="store_true",
                        help="Required for production database")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
