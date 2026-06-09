#!/usr/bin/env python3
"""Fix lost-DEK encryption: overwrite unrecoverable ciphertext with known plaintext.

Root cause: S263 encryption migration ran in dev-mode (MASTER_KEK_KEY_ID and
AZURE_KEYVAULT_URL absent from .env.local). DEKs were created in-memory (dev store)
and lost when the script exited. A subsequent DEK provisioning step stored NEW
RSA-wrapped DEKs in KV, but these don't match the DEKs used to encrypt the data.

Two-phase remediation with HARDCODED INCIDENT SCOPE:
    Phase 1 (--inventory): Read EXACT documents by hardcoded document ID from
        the incident allowlist. Every query uses partition_key + WHERE c.id=@id.
        Outputs evidence JSON (current field values, _etag, restore_to values).
        NO container scans, NO vault scans, NO SELECT * FROM c, NO heuristics.
    Phase 2 (--execute <inventory.json>): Apply fixes using the reviewed inventory.
        Only touches documents whose document_id is in the hardcoded allowlist.
        DEK cleanup is a SEPARATE manual step documented in the inventory output.

Incident scope (hardcoded from S263/S264 investigation):
    - Tenants: remaker-digital-001, test-customer-001
    - DEK secrets: tenant-remaker-digital-001-dek, tenant-test-customer-001-dek
    - Collections: tenants (customer_email, shopify_shop_domain, brand_name),
                   team_members (email, display_name)

Usage:
    # Phase 1 — capture evidence (read-only, no scans):
    COSMOS_DB_DATABASE=agentred python scripts/fix_lost_dek_encryption.py --inventory --force

    # Phase 2 — apply fixes from reviewed inventory:
    COSMOS_DB_DATABASE=agentred python scripts/fix_lost_dek_encryption.py \
        --execute remediation-inventory-*.json --force

    # Phase 3 (manual) — delete orphaned DEK secrets via az CLI:
    #   az keyvault secret delete --vault-name <vault> --name tenant-remaker-digital-001-dek
    #   az keyvault secret delete --vault-name <vault> --name tenant-test-customer-001-dek

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
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

# ──────────────────────────────────────────────────────────────────────
# HARDCODED INCIDENT ALLOWLIST — no runtime discovery
# ──────────────────────────────────────────────────────────────────────

# Exact tenant IDs affected by S263 dev-mode encryption incident.
# These are the only two tenants that existed when the migration ran.
AFFECTED_TENANT_IDS = ["remaker-digital-001", "test-customer-001"]

# Exact DEK secret names created during S263 (convention: tenant-{id}-dek).
AFFECTED_DEK_SECRETS = [
    "tenant-remaker-digital-001-dek",
    "tenant-test-customer-001-dek",
]

# Fields encrypted by the S263 migration in each collection.
TENANT_FIELDS = ["customer_email", "shopify_shop_domain", "brand_name"]
TEAM_MEMBER_FIELDS = ["email", "display_name"]

# Authoritative restoration values from seed_tenant.py.
TENANT_RESTORE: dict[str, dict[str, str]] = {
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

# Exact document IDs for team_members (format: {tenant_id}:{email}).
# For remaker-digital-001, CUSTOMER_EMAIL defaults to mike@remakerdigital.com
# (same as superadmin email), so only one document exists (second upsert wins).
# For test-customer-001, CUSTOMER_EMAIL is test-customer@remakerdigital.com,
# so two distinct documents exist.
AFFECTED_TEAM_MEMBER_IDS: dict[str, list[str]] = {
    "remaker-digital-001": [
        "remaker-digital-001:mike@remakerdigital.com",
    ],
    "test-customer-001": [
        "test-customer-001:mike@remakerdigital.com",
        "test-customer-001:test-customer@remakerdigital.com",
    ],
}

# Restore values keyed by exact document ID (from seed_tenant.py).
# remaker-digital-001:mike@... — last seed upsert wins → Account Administrator.
# test-customer-001:mike@... — superadmin → Owner.
# test-customer-001:test-customer@... — admin → Account Administrator.
TEAM_MEMBER_RESTORE: dict[str, dict[str, str]] = {
    "remaker-digital-001:mike@remakerdigital.com": {
        "email": "mike@remakerdigital.com",
        "display_name": "Account Administrator",
    },
    "test-customer-001:mike@remakerdigital.com": {
        "email": "mike@remakerdigital.com",
        "display_name": "Owner",
    },
    "test-customer-001:test-customer@remakerdigital.com": {
        "email": "test-customer@remakerdigital.com",
        "display_name": "Account Administrator",
    },
}


# ──────────────────────────────────────────────────────────────────────
# Phase 1: Evidence-only inventory (read-only, no scans)
# ──────────────────────────────────────────────────────────────────────


async def build_inventory() -> dict:
    """Read exact documents from the hardcoded allowlist. No scans."""
    from azure.cosmos import CosmosClient

    client = CosmosClient(os.environ["COSMOS_DB_ENDPOINT"], os.environ["COSMOS_DB_KEY"])
    db = client.get_database_client(os.environ["COSMOS_DB_DATABASE"])

    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "database": os.environ["COSMOS_DB_DATABASE"],
        "incident_scope": {
            "tenant_ids": AFFECTED_TENANT_IDS,
            "dek_secrets": AFFECTED_DEK_SECRETS,
            "note": "DEK secret cleanup is manual (az keyvault secret delete). Not automated.",
        },
        "tenant_evidence": [],
        "team_member_evidence": [],
    }

    # Read specific tenant documents by partition key (no cross-partition query)
    container = db.get_container_client("tenants")
    for tid in AFFECTED_TENANT_IDS:
        items = list(
            container.query_items(
                query="SELECT * FROM c WHERE c.id=@id",
                parameters=[{"name": "@id", "value": tid}],
                partition_key=tid,
            )
        )
        if not items:
            logger.warning("Tenant %s not found in database", tid)
            inventory["tenant_evidence"].append(
                {
                    "tenant_id": tid,
                    "status": "NOT_FOUND",
                }
            )
            continue

        doc = items[0]
        fields = {}
        for field in TENANT_FIELDS:
            current = doc.get(field, "")
            fields[field] = {
                "current_value": current,
                "current_length": len(current),
                "restore_to": TENANT_RESTORE[tid][field],
            }

        inventory["tenant_evidence"].append(
            {
                "tenant_id": tid,
                "document_id": doc["id"],
                "partition_key": tid,
                "_etag": doc.get("_etag", ""),
                "fields": fields,
            }
        )

    # Read exact team_member documents by document ID (no partition scan)
    tm_container = db.get_container_client("team_members")
    for tid in AFFECTED_TENANT_IDS:
        for doc_id in AFFECTED_TEAM_MEMBER_IDS[tid]:
            items = list(
                tm_container.query_items(
                    query="SELECT * FROM c WHERE c.id=@id",
                    parameters=[{"name": "@id", "value": doc_id}],
                    partition_key=tid,
                )
            )
            if not items:
                logger.warning("Team member %s not found in database", doc_id)
                inventory["team_member_evidence"].append(
                    {
                        "tenant_id": tid,
                        "document_id": doc_id,
                        "status": "NOT_FOUND",
                    }
                )
                continue

            doc = items[0]
            restore_values = TEAM_MEMBER_RESTORE[doc_id]
            fields = {}
            for field in TEAM_MEMBER_FIELDS:
                current = doc.get(field, "")
                fields[field] = {
                    "current_value": current,
                    "current_length": len(current),
                    "restore_to": restore_values[field],
                }

            inventory["team_member_evidence"].append(
                {
                    "tenant_id": tid,
                    "document_id": doc["id"],
                    "partition_key": tid,
                    "_etag": doc.get("_etag", ""),
                    "fields": fields,
                }
            )

    return inventory


# ──────────────────────────────────────────────────────────────────────
# Phase 2: Execute from reviewed inventory
# ──────────────────────────────────────────────────────────────────────


async def execute_from_inventory(inventory_path: str) -> dict:
    """Apply restoration using a reviewed inventory as the allowlist."""
    with open(inventory_path) as f:
        inventory = json.load(f)

    from azure.cosmos import CosmosClient

    # Safety: verify target database matches inventory
    target_db = os.environ["COSMOS_DB_DATABASE"]
    if inventory["database"] != target_db:
        logger.error(
            "SAFETY: Inventory for '%s' but target is '%s'. Aborting.",
            inventory["database"],
            target_db,
        )
        sys.exit(1)

    client = CosmosClient(os.environ["COSMOS_DB_ENDPOINT"], os.environ["COSMOS_DB_KEY"])
    db = client.get_database_client(target_db)

    results = {"tenants_fixed": 0, "team_members_fixed": 0, "fields_fixed": 0, "errors": []}

    # Restore tenant documents
    container = db.get_container_client("tenants")
    for entry in inventory.get("tenant_evidence", []):
        if entry.get("status") == "NOT_FOUND":
            continue
        tid = entry["tenant_id"]
        # Safety: only process tenants in the hardcoded allowlist
        if tid not in AFFECTED_TENANT_IDS:
            logger.error("SAFETY: tenant %s not in incident allowlist. Skipping.", tid)
            results["errors"].append(f"tenant {tid} not in allowlist")
            continue

        try:
            items = list(
                container.query_items(
                    query="SELECT * FROM c WHERE c.id=@id",
                    parameters=[{"name": "@id", "value": entry["document_id"]}],
                    partition_key=entry["partition_key"],
                )
            )
            if not items:
                results["errors"].append(f"tenant {tid} not found")
                continue

            doc = items[0]
            changed = False
            for field, info in entry["fields"].items():
                restore_value = info["restore_to"]
                current = doc.get(field, "")
                if current != restore_value:
                    doc[field] = restore_value
                    changed = True
                    results["fields_fixed"] += 1
                    logger.info("  tenants/%s.%s: restored", tid, field)

            if changed:
                container.replace_item(item=doc["id"], body=doc)
                results["tenants_fixed"] += 1
        except Exception as e:
            logger.error("Error fixing tenant %s: %s", tid, e)
            results["errors"].append(f"tenant {tid}: {e}")

    # Restore team_member documents (by exact document ID)
    tm_container = db.get_container_client("team_members")
    for entry in inventory.get("team_member_evidence", []):
        if entry.get("status") == "NOT_FOUND":
            continue
        tid = entry["tenant_id"]
        doc_id = entry["document_id"]
        if tid not in AFFECTED_TENANT_IDS:
            logger.error("SAFETY: team_member tenant %s not in allowlist. Skipping.", tid)
            results["errors"].append(f"team_member tenant {tid} not in allowlist")
            continue
        if doc_id not in TEAM_MEMBER_RESTORE:
            logger.error("SAFETY: team_member %s not in document-ID allowlist. Skipping.", doc_id)
            results["errors"].append(f"team_member {doc_id} not in document-ID allowlist")
            continue

        try:
            items = list(
                tm_container.query_items(
                    query="SELECT * FROM c WHERE c.id=@id",
                    parameters=[{"name": "@id", "value": entry["document_id"]}],
                    partition_key=entry["partition_key"],
                )
            )
            if not items:
                results["errors"].append(f"team_member {entry['document_id']} not found")
                continue

            doc = items[0]
            changed = False
            for field, info in entry["fields"].items():
                restore_value = info["restore_to"]
                current = doc.get(field, "")
                if current != restore_value:
                    doc[field] = restore_value
                    changed = True
                    results["fields_fixed"] += 1
                    logger.info("  team_members/%s/%s.%s: restored", tid, doc["id"][:12], field)

            if changed:
                tm_container.replace_item(item=doc["id"], body=doc)
                results["team_members_fixed"] += 1
        except Exception as e:
            logger.error("Error fixing team_member %s: %s", tid, e)
            results["errors"].append(f"team_member {tid}: {e}")

    logger.info("NOTE: DEK secret cleanup is manual. Run:")
    for name in AFFECTED_DEK_SECRETS:
        logger.info("  az keyvault secret delete --vault-name <vault> --name %s", name)

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
                "SAFETY GATE: COSMOS_DB_DATABASE=%s looks like production. Pass --force to confirm.",
                db_name,
            )
            sys.exit(1)

    if args.inventory:
        logger.info("Phase 1: Capturing evidence for %d tenants (no scans)...", len(AFFECTED_TENANT_IDS))
        inventory = await build_inventory()

        filename = f"remediation-inventory-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "w") as f:
            json.dump(inventory, f, indent=2)

        logger.info("Inventory written to: %s", filepath)
        logger.info("Tenants: %d evidence records", len(inventory["tenant_evidence"]))
        logger.info("Team members: %d evidence records", len(inventory["team_member_evidence"]))
        logger.info("REVIEW this inventory, then run --execute %s --force", filename)

    elif args.execute:
        if not os.path.exists(args.execute):
            logger.error("Inventory file not found: %s", args.execute)
            sys.exit(1)

        logger.info("Phase 2: Executing from inventory: %s", args.execute)
        results = await execute_from_inventory(args.execute)

        logger.info(
            "Results: %d tenants, %d team_members, %d fields restored",
            results["tenants_fixed"],
            results["team_members_fixed"],
            results["fields_fixed"],
        )
        if results["errors"]:
            logger.warning("Errors: %s", results["errors"])
            sys.exit(1)
        logger.info("Phase 3: Delete orphaned DEK secrets manually (see output above).")
        logger.info("Phase 4: Re-run encryption migration with correct env vars.")

    else:
        logger.error("Specify --inventory (Phase 1) or --execute <file> (Phase 2).")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix lost-DEK encrypted fields")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--inventory", action="store_true", help="Phase 1: capture evidence from hardcoded allowlist (read-only)"
    )
    group.add_argument(
        "--execute", type=str, metavar="INVENTORY_FILE", help="Phase 2: apply fixes from reviewed inventory"
    )
    parser.add_argument("--force", action="store_true", help="Required for production database")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
