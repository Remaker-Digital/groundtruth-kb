"""Key Vault Audit & Tenant Key Rotation — WI-1108 + WI-1109.

Provides two operations:
1. audit  — Lists all Key Vault secrets, cross-references against Cosmos DB
            tenant documents, and identifies orphaned entries.
2. rotate — Regenerates API keys for specified tenants, stores new hashes
            in Cosmos, and emails raw keys directly to tenant superadmins.
            Old keys stop working immediately (hash mismatch).

SPEC-1673: Provider MUST NOT hold raw tenant API keys.
Keys are generated in-memory, hashed for Cosmos, emailed to tenant, then discarded.

Usage:
    python scripts/key_vault_audit.py audit --env production
    python scripts/key_vault_audit.py rotate --env production --tenant <id> [--dry-run]

Requires:
    - Azure CLI logged in (az login)
    - COSMOS_ENDPOINT + COSMOS_KEY env vars (or az identity)
    - SMTP_HOST or AZURE_COMM_CONNECTION_STRING for email delivery

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

KEY_VAULT_NAME = "kv-agentred-eastus"
COSMOS_ENDPOINT = "https://cosmos-agentred-eastus.documents.azure.com:443/"

ENVIRONMENTS = {
    "production": {"database": "agentred"},
    "staging": {"database": "agentred-staging"},
}


# ---------------------------------------------------------------------------
# Key Vault operations (via az CLI)
# ---------------------------------------------------------------------------


def list_key_vault_secrets() -> list[dict]:
    """List all secrets in Key Vault (names only, no values)."""
    result = subprocess.run(
        [
            "az",
            "keyvault",
            "secret",
            "list",
            "--vault-name",
            KEY_VAULT_NAME,
            "--query",
            "[].{name:name, enabled:attributes.enabled, updated:attributes.updated}",
            "-o",
            "json",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        logger.error("az keyvault secret list failed: %s", result.stderr)
        return []
    return json.loads(result.stdout)


def get_secret_value(name: str) -> str | None:
    """Get a secret value from Key Vault."""
    result = subprocess.run(
        [
            "az",
            "keyvault",
            "secret",
            "show",
            "--vault-name",
            KEY_VAULT_NAME,
            "--name",
            name,
            "--query",
            "value",
            "-o",
            "tsv",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        logger.warning("Failed to read secret %s: %s", name, result.stderr.strip())
        return None
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Cosmos DB operations
# ---------------------------------------------------------------------------


async def get_cosmos_client(database_name: str):
    """Get an async Cosmos DB client."""
    from azure.cosmos.aio import CosmosClient

    endpoint = os.environ.get("COSMOS_ENDPOINT", COSMOS_ENDPOINT)
    key = os.environ.get("COSMOS_KEY", "")

    if not key:
        # Try managed identity
        from azure.identity.aio import DefaultAzureCredential

        credential = DefaultAzureCredential()
        client = CosmosClient(endpoint, credential=credential)
    else:
        client = CosmosClient(endpoint, credential=key)

    database = client.get_database_client(database_name)
    return client, database


async def list_tenants_with_keys(database) -> list[dict]:
    """List all tenants with their key hashes."""
    container = database.get_container_client("tenants")
    query = (
        "SELECT c.tenant_id, c.customer_email, c.status, c.tier, "
        "c.api_key_hash, c.widget_key_hash, c.user_api_key_hash "
        "FROM c"
    )
    tenants = []
    async for item in container.query_items(query=query):
        tenants.append(item)
    return tenants


async def get_tenant_superadmin_email(database, tenant_id: str) -> str | None:
    """Find the superadmin email for a tenant."""
    container = database.get_container_client("team_members")
    query = "SELECT c.email FROM c WHERE c.tenant_id = @tid AND c.role = 'superadmin' AND c.is_active = true"
    params = [{"name": "@tid", "value": tenant_id}]
    async for item in container.query_items(query=query, parameters=params):
        return item.get("email")
    return None


async def rotate_tenant_key(database, tenant_id: str, dry_run: bool = True) -> dict:
    """Rotate API key for a tenant. Returns status dict."""
    from src.multi_tenant.auth import generate_user_api_key, hash_api_key

    # Find superadmin for this tenant
    superadmin_email = await get_tenant_superadmin_email(database, tenant_id)
    if not superadmin_email:
        return {"tenant_id": tenant_id, "status": "SKIP", "reason": "No superadmin found"}

    # Generate new key
    new_key = generate_user_api_key(tenant_id)
    new_hash = hash_api_key(new_key)
    new_prefix = new_key[:12] + "..."

    if dry_run:
        return {
            "tenant_id": tenant_id,
            "email": superadmin_email,
            "status": "DRY_RUN",
            "new_prefix": new_prefix,
        }

    # Update Cosmos — find and update the superadmin team member
    container = database.get_container_client("team_members")
    query = "SELECT * FROM c WHERE c.tenant_id = @tid AND c.role = 'superadmin' AND c.is_active = true"
    params = [{"name": "@tid", "value": tenant_id}]
    member = None
    async for item in container.query_items(query=query, parameters=params):
        member = item
        break

    if not member:
        return {"tenant_id": tenant_id, "status": "FAIL", "reason": "Superadmin doc not found"}

    # Update hash in Cosmos
    member["user_api_key_hash"] = new_hash
    member["user_api_key_prefix"] = new_prefix
    member["updated_at"] = datetime.now(timezone.utc).isoformat()
    await container.upsert_item(member)

    # Email new key to tenant (SPEC-1673: provider never sees raw key)
    email_sent = False
    try:
        from src.multi_tenant.welcome_email import send_welcome_email

        email_sent = await send_welcome_email(
            to_email=superadmin_email,
            tenant_id=tenant_id,
            superadmin_key=new_key,
            tier=member.get("tier", "unknown"),
        )
    except Exception as exc:
        logger.error("Email delivery failed for %s: %s", tenant_id[:8], exc)

    # Discard raw key from memory
    new_key = "(discarded)"  # noqa: F841

    return {
        "tenant_id": tenant_id,
        "email": superadmin_email,
        "status": "ROTATED",
        "new_prefix": new_prefix,
        "email_sent": email_sent,
    }


# ---------------------------------------------------------------------------
# Audit command
# ---------------------------------------------------------------------------


async def audit_command(env: str) -> None:
    """Cross-reference Key Vault secrets against Cosmos tenants."""
    db_name = ENVIRONMENTS[env]["database"]

    print(f"\n=== Key Vault Audit ({env}) ===\n")

    # 1. List Key Vault secrets
    secrets = list_key_vault_secrets()
    print(f"Key Vault secrets: {len(secrets)}")
    for s in secrets:
        print(f"  {s['name']} (enabled={s.get('enabled', '?')})")

    # 2. List Cosmos tenants with key hashes
    client, database = await get_cosmos_client(db_name)
    try:
        tenants = await list_tenants_with_keys(database)
        print(f"\nCosmos tenants: {len(tenants)}")

        tenants_with_keys = [t for t in tenants if t.get("api_key_hash")]
        tenants_without_keys = [t for t in tenants if not t.get("api_key_hash")]
        print(f"  With api_key_hash: {len(tenants_with_keys)}")
        print(f"  Without api_key_hash: {len(tenants_without_keys)}")

        # 3. Identify Key Vault entries that look like tenant keys
        kv_tenant_keys = [
            s for s in secrets if "API-KEY" in s["name"].upper() and s["name"] != "SPA-PLATFORM-ADMIN-KEY"
        ]
        print(f"\nKey Vault tenant-related secrets: {len(kv_tenant_keys)}")

        # 4. Cross-reference
        # Key Vault secrets that store raw keys should NOT exist per SPEC-1673
        if kv_tenant_keys:
            print("\n*** ORPHANED KEY VAULT ENTRIES (SPEC-1673 violation) ***")
            for s in kv_tenant_keys:
                print(f"  ORPHAN: {s['name']} — raw tenant key should not be in Key Vault")
            print(f"\nRecommendation: Delete {len(kv_tenant_keys)} orphaned Key Vault entries.")
            print("  Per SPEC-1673, tenant keys are stored as hashes in Cosmos only.")
            print("  Raw keys are delivered to tenants via email and never stored.")
        else:
            print("\nNo orphaned Key Vault entries found. SPEC-1673 compliant.")

        # 5. Report SPA key status
        spa_key = next((s for s in secrets if s["name"] == "SPA-PLATFORM-ADMIN-KEY"), None)
        if spa_key:
            print(f"\nSPA Platform Admin Key: PRESENT (enabled={spa_key.get('enabled', '?')})")
        else:
            print("\nSPA Platform Admin Key: MISSING")

    finally:
        await client.close()


# ---------------------------------------------------------------------------
# Rotate command
# ---------------------------------------------------------------------------


async def rotate_command(env: str, tenant_ids: list[str], dry_run: bool) -> None:
    """Rotate API keys for specified tenants."""
    db_name = ENVIRONMENTS[env]["database"]

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"\n=== Key Rotation ({env} — {mode}) ===\n")

    client, database = await get_cosmos_client(db_name)
    try:
        if not tenant_ids:
            # Rotate all tenants with existing keys
            tenants = await list_tenants_with_keys(database)
            active_tenants = [t for t in tenants if t.get("status") == "active" and t.get("user_api_key_hash")]
            tenant_ids = [t["tenant_id"] for t in active_tenants]
            print(f"Found {len(tenant_ids)} active tenants with user API keys")

        results = []
        for tid in tenant_ids:
            result = await rotate_tenant_key(database, tid, dry_run=dry_run)
            results.append(result)
            print(
                f"  {result['status']:10s} {tid[:12]}... "
                f"email={result.get('email', 'N/A')} "
                f"prefix={result.get('new_prefix', 'N/A')}"
            )

        # Summary
        rotated = sum(1 for r in results if r["status"] == "ROTATED")
        skipped = sum(1 for r in results if r["status"] == "SKIP")
        failed = sum(1 for r in results if r["status"] == "FAIL")
        dry = sum(1 for r in results if r["status"] == "DRY_RUN")

        print(f"\nSummary: {rotated} rotated, {skipped} skipped, {failed} failed, {dry} dry-run")

        if not dry_run and rotated > 0:
            emails_sent = sum(1 for r in results if r.get("email_sent"))
            print(f"Email delivery: {emails_sent}/{rotated} sent successfully")

    finally:
        await client.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Key Vault Audit & Tenant Key Rotation")
    sub = parser.add_subparsers(dest="command", required=True)

    # audit
    audit_p = sub.add_parser("audit", help="Cross-reference Key Vault vs Cosmos")
    audit_p.add_argument("--env", choices=list(ENVIRONMENTS), default="production")

    # rotate
    rotate_p = sub.add_parser("rotate", help="Rotate tenant API keys")
    rotate_p.add_argument("--env", choices=list(ENVIRONMENTS), default="production")
    rotate_p.add_argument("--tenant", nargs="*", default=[], help="Tenant IDs (all active if omitted)")
    rotate_p.add_argument("--dry-run", action="store_true", default=True, help="Preview only (default)")
    rotate_p.add_argument("--execute", action="store_true", help="Actually rotate keys")

    args = parser.parse_args()

    if args.command == "audit":
        asyncio.run(audit_command(args.env))
    elif args.command == "rotate":
        dry_run = not args.execute
        asyncio.run(rotate_command(args.env, args.tenant, dry_run))


if __name__ == "__main__":
    main()
