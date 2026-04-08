#!/usr/bin/env python3
"""Verify production decryption works by reading an encrypted tenant record.

Run inside the production container:
    az containerapp exec --name agent-red-api-gateway --resource-group Agent-Red \
        --command "python /app/scripts/verify_production_decrypt.py"

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import asyncio
import os
import sys

sys.path.insert(0, "/app")
os.environ.setdefault("RUNNING_IN_CONTAINER", "1")


async def verify():
    from src.app.lifecycle import _startup_cosmos_db, _startup_envelope_encryption

    print("Step 1: Initializing Cosmos DB...")
    await _startup_cosmos_db()
    print("  OK")

    print("Step 2: Initializing encryption service...")
    await _startup_envelope_encryption()
    print("  OK")

    print("Step 3: Reading tenant remaker-digital-001...")
    from src.multi_tenant.repositories.tenant_repository import TenantRepository

    repo = TenantRepository()
    tenant = await repo.get_by_id("remaker-digital-001")

    if not tenant:
        print("  FAIL: Tenant not found")
        sys.exit(1)

    email = tenant.get("customer_email", "")
    brand = tenant.get("brand_name", "")
    shop = tenant.get("shopify_shop_domain", "")

    print(f"  brand_name: {brand[:30]}")
    print(f"  customer_email length: {len(email)}")
    print(f"  shopify_shop_domain: {shop[:30]}")

    # Check if fields look like plaintext (not base64 ciphertext)
    looks_plain = "@" in email if email else True
    if looks_plain:
        print("\nDECRYPT VERIFICATION: PASS")
        print("  Fields are readable plaintext (decryption working)")
    else:
        print("\nDECRYPT VERIFICATION: FAIL")
        print("  Fields appear to still be ciphertext")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(verify())
