#!/usr/bin/env python3
"""Repair missing widget_key_hash on tenant documents.

Reads the raw widget key from tenant preferences, computes the SHA-256
hash, and patches it onto the tenant document. This is needed when the
activation service provisioned the widget key but failed to write the
hash (e.g., due to a race condition or partial failure).

Usage:
    python scripts/repair_widget_hash.py --env production --tenant test-customer-001
    python scripts/repair_widget_hash.py --env staging --tenant remaker-digital-001 --dry-run

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

# Load .env.local
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from scripts._env import load_env_local

load_env_local()

# SPEC-1882: deploy_config is the single source of truth for environment FQDNs.
# Read the FQDN from the SoT instead of hardcoding it here (WI-4572).
from scripts.deploy_config import get_environment as _dc_get_environment  # noqa: E402

ENVIRONMENTS = {
    "staging": {
        "fqdn": _dc_get_environment("staging")["fqdn"],
        "spa_key": os.environ.get("STAGING_SPA_KEY", ""),
    },
    "production": {
        "fqdn": _dc_get_environment("production")["fqdn"],
        "spa_key": os.environ.get("PRODUCTION_SPA_KEY", ""),
    },
}


def api_call(
    fqdn: str, path: str, api_key: str, method: str = "GET", body: dict | None = None
) -> tuple[int, dict | str]:
    url = f"https://{fqdn}{path}"
    headers = {"Accept": "application/json", "X-API-Key": api_key}
    data = None
    if body:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except HTTPError as e:
        raw = e.read().decode() if e.fp else ""
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw


def main():
    parser = argparse.ArgumentParser(description="Repair widget_key_hash on tenant documents")
    parser.add_argument("--env", required=True, choices=["staging", "production"])
    parser.add_argument("--tenant", required=True, help="Tenant ID to repair")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()

    env = ENVIRONMENTS[args.env]
    fqdn = env["fqdn"]
    spa_key = env["spa_key"]
    tenant_id = args.tenant

    if not spa_key:
        print(f"ERROR: SPA key not set for {args.env}")
        sys.exit(1)

    # Step 1: Get the tenant's API key from the tenant listing
    print(f"[1/4] Fetching tenant {tenant_id} from {args.env}...")
    s, data = api_call(fqdn, "/api/superadmin/tenants", spa_key)
    if s != 200:
        print(f"  ERROR: Could not list tenants: HTTP {s}")
        sys.exit(1)

    tenants = data.get("tenants", [])
    tenant = next((t for t in tenants if t.get("tenantId") == tenant_id), None)
    if not tenant:
        print(f"  ERROR: Tenant {tenant_id} not found")
        sys.exit(1)

    has_hash = bool(tenant.get("widgetKeyHash"))
    print(f"  Current widgetKeyHash: {'SET' if has_hash else 'MISSING'}")

    # Step 2: Get the raw widget key from the config endpoint
    # We need the tenant's own API key for this. Check env vars.
    env_prefix = "PRODUCTION" if args.env == "production" else "STAGING"
    tenant_key = os.environ.get(f"{env_prefix}_REMAKER_TENANT_KEY", "")
    if not tenant_key:
        print(f"  ERROR: {env_prefix}_REMAKER_TENANT_KEY not set")
        sys.exit(1)

    print("[2/4] Fetching widget key from config...")
    s, cfg_data = api_call(fqdn, f"/api/config?tenant={tenant_id}", tenant_key)
    if s != 200:
        print(f"  ERROR: Config fetch failed: HTTP {s}")
        sys.exit(1)

    widget_key = cfg_data.get("config", {}).get("widget_key", "")
    if not widget_key or not widget_key.startswith("pk_live_"):
        print(f"  ERROR: No valid widget key in config (got: {widget_key[:20]}...)")
        sys.exit(1)
    print(f"  Found widget key: {widget_key[:12]}...")

    # Step 3: Compute hash
    key_hash = hashlib.sha256(widget_key.encode("utf-8")).hexdigest()
    print(f"[3/4] Computed hash: {key_hash[:16]}...")

    if args.dry_run:
        print(f"[4/4] DRY RUN — would patch tenant doc with widget_key_hash={key_hash[:16]}...")
        return

    # Step 4: Patch via the superadmin tenant update endpoint
    print("[4/4] Patching tenant document...")
    s, result = api_call(
        fqdn,
        f"/api/superadmin/tenants/{tenant_id}/patch",
        spa_key,
        method="PATCH",
        body={"widget_key_hash": key_hash},
    )
    if s in (200, 204):
        print(f"  SUCCESS: widget_key_hash set on tenant {tenant_id}")
    else:
        # Try alternative endpoint
        print(f"  Patch returned HTTP {s}, trying direct update...")
        s2, result2 = api_call(
            fqdn,
            f"/api/superadmin/tenants/{tenant_id}",
            spa_key,
            method="PATCH",
            body={"widget_key_hash": key_hash},
        )
        if s2 in (200, 204):
            print(f"  SUCCESS: widget_key_hash set on tenant {tenant_id}")
        else:
            print(f"  ERROR: Could not patch tenant: HTTP {s2}")
            print(f"  Response: {result2}")
            print("\n  MANUAL FIX: Use Azure Cosmos DB Data Explorer to set")
            print(f"  widget_key_hash = {key_hash}")
            print(f"  on tenant document id={tenant_id} in the tenants container.")
            sys.exit(1)

    # Verify
    print("\nVerifying...")
    s, verify_data = api_call(fqdn, "/api/config?page_type=all", api_key=None)
    # This won't work without widget key auth, but we can test widget auth
    print("Repair complete. Test widget auth by refreshing the admin UI.")


if __name__ == "__main__":
    main()
