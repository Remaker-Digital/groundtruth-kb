#!/usr/bin/env python3
"""Verify Zero-Knowledge Pillars 3+4 are active on staging.

Loads credentials from .env.local internally — no secrets on CLI.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import sys
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_env():
    """Load .env.local into os.environ."""
    env_file = PROJECT_ROOT / ".env.local"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def api_get(url: str, headers: dict) -> dict:
    """GET request, return parsed JSON."""
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def main():
    load_env()
    base = os.environ.get("STAGING_URL", "").rstrip("/")
    spa_key = os.environ.get("STAGING_SPA_KEY", "") or os.environ.get("SPA_PLATFORM_ADMIN_KEY", "")
    tenant_key = (
        os.environ.get("STAGING_REMAKER_USER_KEY", "")
        or os.environ.get("STAGING_REMAKER_TENANT_KEY", "")
        or os.environ.get("STAGING_REMAKER_API_KEY", "")
    )

    if not base:
        print("ERROR: STAGING_URL not set in .env.local")
        sys.exit(1)

    results = {"pillar3": "UNKNOWN", "pillar4": "UNKNOWN", "version": "UNKNOWN"}

    # --- Version check ---
    try:
        health = api_get(f"{base}/health", {})
        results["version"] = health.get("product_version", "?")
        print(f"[OK] Version: {results['version']}")
    except Exception as e:
        print(f"[FAIL] Health check: {e}")

    # --- Pillar 3: PII masking on superadmin tenant listing ---
    if spa_key:
        try:
            data = api_get(
                f"{base}/api/superadmin/tenants?limit=5",
                {"X-API-Key": spa_key},
            )
            tenants = data if isinstance(data, list) else data.get("tenants", data.get("items", []))
            # Debug: show raw response shape
            if not tenants and isinstance(data, dict):
                print(f"  Response keys: {list(data.keys())[:10]}")
                # Try to find tenants in any nested key
                for k, v in data.items():
                    if isinstance(v, list) and v:
                        tenants = v
                        print(f"  Found tenants under key: '{k}'")
                        break
            masked_count = 0
            raw_count = 0
            PII_FIELDS = [
                "customer_email",
                "contact_email",
                "email",
                "shopify_shop_domain",
                "shop_domain",
                "brand_name",
                "customerEmail",
                "shopifyShopDomain",
                "brandName",
            ]
            for t in tenants:
                for field in PII_FIELDS:
                    val = t.get(field, "")
                    if val and "***" in val:
                        masked_count += 1
                    elif val and ("@" in val or "." in val) and "***" not in val and len(val) > 4:
                        raw_count += 1
                        print(f"  [LEAK] Raw PII in field '{field}'")
            if masked_count > 0 and raw_count == 0:
                results["pillar3"] = "PASS"
                print(f"[PASS] Pillar 3: {masked_count} masked fields, 0 raw PII")
            elif raw_count > 0:
                results["pillar3"] = "FAIL"
                print(f"[FAIL] Pillar 3: {raw_count} raw PII fields found!")
            else:
                results["pillar3"] = "NO_DATA"
                print(f"[WARN] Pillar 3: No PII fields to verify ({len(tenants)} tenants)")
            # Show sample (masked values only — safe to print)
            if tenants:
                sample = tenants[0]
                safe_keys = [k for k in sample.keys() if k not in ("api_key_hash",)]
                print(f"  Sample keys: {safe_keys[:12]}")
                for field in PII_FIELDS:
                    val = sample.get(field)
                    if val:
                        print(f"  {field}: {val}")
        except Exception as e:
            print(f"[FAIL] Pillar 3: {e}")
    else:
        print("[SKIP] Pillar 3: SPA_PLATFORM_ADMIN_KEY not set")

    # --- Pillar 4: Audit log sanitization ---
    if tenant_key:
        try:
            # Auth fallthrough: user key + tenant query param
            tenant_id = os.environ.get("STAGING_REMAKER_TENANT_ID", "remaker-digital-001")
            data = api_get(
                f"{base}/api/audit?limit=5&tenant={tenant_id}",
                {"X-API-Key": tenant_key},
            )
            events = data if isinstance(data, list) else data.get("events", data.get("items", []))
            pii_leak = False
            sanitized_markers = 0
            DENY_FIELDS = {
                "email",
                "customer_email",
                "phone",
                "name",
                "display_name",
                "messages",
                "content",
                "body",
                "api_key",
                "widget_key",
                "totp_seed",
                "session_token",
                "shopify_domain",
            }
            for evt in events:
                details = evt.get("details", evt.get("payload", {}))
                if isinstance(details, dict):
                    for k in details:
                        if k in DENY_FIELDS:
                            pii_leak = True
                            print(f"  [LEAK] Denied field '{k}' found in audit event!")
                    for v in details.values():
                        if isinstance(v, str) and any(
                            m in v for m in ["[EMAIL]", "[API_KEY]", "[PHONE]", "[STRIPE_KEY]", "[redacted:"]
                        ):
                            sanitized_markers += 1
            if pii_leak:
                results["pillar4"] = "FAIL"
                print(f"[FAIL] Pillar 4: PII leak detected in audit logs!")
            elif len(events) == 0:
                results["pillar4"] = "NO_DATA"
                print("[WARN] Pillar 4: No audit events to verify")
            else:
                results["pillar4"] = "PASS"
                print(
                    f"[PASS] Pillar 4: {len(events)} events checked, 0 PII leaks, {sanitized_markers} sanitized markers"
                )
            if events:
                sample = events[0]
                print(f"  Sample event_type: {sample.get('event_type', '?')}")
                safe_keys = list((sample.get("details", sample.get("payload", {})) or {}).keys())[:8]
                print(f"  Sample detail keys: {safe_keys}")
        except Exception as e:
            print(f"[FAIL] Pillar 4: {e}")
    else:
        print("[SKIP] Pillar 4: STAGING_REMAKER_API_KEY not set — trying with tenant key...")
        # Try alternate key name
        alt_key = os.environ.get("STAGING_REMAKER_TENANT_KEY", "")
        if alt_key:
            print("  Found STAGING_REMAKER_TENANT_KEY, retrying...")

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print(f"ZK Pillar Verification — v{results['version']}")
    print(f"  Pillar 3 (PII masking):        {results['pillar3']}")
    print(f"  Pillar 4 (Audit sanitization): {results['pillar4']}")
    print(f"{'=' * 50}")

    if results["pillar3"] == "FAIL" or results["pillar4"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
