#!/usr/bin/env python3
"""Refresh live regression test credentials from Azure Key Vault.

Retrieves current SUPERADMIN_PREVIEW_API_KEY from Key Vault and updates
.env.local. The PREVIEW_WIDGET_KEY must be set manually (stored in Cosmos,
not Key Vault — see seed_tenant.py POST-SEED STEPS).

Usage:
    python scripts/refresh_test_credentials.py              # refresh from staging vault
    python scripts/refresh_test_credentials.py --env prod   # refresh from production vault
    python scripts/refresh_test_credentials.py --dry-run    # show what would change
    python scripts/refresh_test_credentials.py --verify     # just run preflight probe

Prerequisites:
    - Azure CLI authenticated: `az login`
    - Key Vault read access: "Key Vault Secrets User" on the vault

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_LOCAL = PROJECT_ROOT / ".env.local"

VAULT_NAME = "kv-agentred-eastus"
API_KEY_SECRET = "ADMIN-PREVIEW-API-KEY"

# Env var names in .env.local
ENV_API_KEY = "SUPERADMIN_PREVIEW_API_KEY"
ENV_WIDGET_KEY = "PREVIEW_WIDGET_KEY"

# Environment configs
ENVIRONMENTS = {
    "staging": {
        "vault": "kv-agentred-eastus",
        "secret": "superadmin-preview-api-key",
        "url_var": "STAGING_URL",
    },
    "prod": {
        "vault": "kv-agentred-eastus",
        "secret": "ADMIN-PREVIEW-API-KEY",
        "url_var": "PROD_URL",
    },
}


def _az_get_secret(vault: str, secret_name: str) -> str | None:
    """Retrieve a secret value from Azure Key Vault via CLI."""
    try:
        result = subprocess.run(
            [
                "az", "keyvault", "secret", "show",
                "--vault-name", vault,
                "--name", secret_name,
                "--query", "value",
                "-o", "tsv",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        print(f"  [ERROR] az keyvault secret show failed: {result.stderr.strip()}")
        return None
    except FileNotFoundError:
        print("  [ERROR] Azure CLI (az) not found. Install: https://aka.ms/installazurecli")
        return None
    except subprocess.TimeoutExpired:
        print("  [ERROR] Azure CLI timed out after 30s. Check az login status.")
        return None


def _read_env_local() -> dict[str, str]:
    """Parse .env.local into dict."""
    result: dict[str, str] = {}
    if not ENV_LOCAL.is_file():
        return result
    for line in ENV_LOCAL.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        result[key.strip()] = value.strip()
    return result


def _write_env_local(values: dict[str, str]) -> None:
    """Write dict back to .env.local, preserving comments and structure."""
    lines: list[str] = []
    written_keys: set[str] = set()

    if ENV_LOCAL.is_file():
        for line in ENV_LOCAL.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key, _, _ = stripped.partition("=")
                key = key.strip()
                if key in values:
                    lines.append(f"{key}={values[key]}")
                    written_keys.add(key)
                    continue
            lines.append(line)

    # Append any new keys not already in the file
    for key, value in values.items():
        if key not in written_keys:
            lines.append(f"{key}={value}")

    ENV_LOCAL.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _verify_credentials(base_url: str, api_key: str, widget_key: str) -> dict[str, str]:
    """Run preflight probe against credentials. Returns dict of problems."""
    import httpx  # noqa: delayed import

    problems: dict[str, str] = {}

    if api_key:
        try:
            with httpx.Client(timeout=10.0) as c:
                resp = c.get(
                    f"{base_url}/api/superadmin/dashboard",
                    headers={"X-API-Key": api_key},
                )
                if resp.status_code in (401, 403):
                    problems["API_KEY"] = f"returned {resp.status_code} — stale or invalid"
                elif resp.status_code == 200:
                    pass  # valid
                else:
                    problems["API_KEY"] = f"unexpected status {resp.status_code}"
        except Exception as e:
            problems["API_KEY"] = f"probe failed: {e}"

    if widget_key:
        try:
            with httpx.Client(timeout=10.0) as c:
                resp = c.get(
                    f"{base_url}/api/config?page_type=index",
                    headers={"X-Widget-Key": widget_key},
                )
                if resp.status_code in (401, 403):
                    problems["WIDGET_KEY"] = f"returned {resp.status_code} — stale or invalid"
                elif resp.status_code == 200:
                    pass  # valid
                else:
                    problems["WIDGET_KEY"] = f"unexpected status {resp.status_code}"
        except Exception as e:
            problems["WIDGET_KEY"] = f"probe failed: {e}"

    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh test credentials from Key Vault")
    parser.add_argument("--env", choices=["staging", "prod"], default="staging",
                        help="Environment to pull credentials from (default: staging)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would change without writing")
    parser.add_argument("--verify", action="store_true",
                        help="Only run preflight probe on current .env.local credentials")
    args = parser.parse_args()

    env_config = ENVIRONMENTS[args.env]
    current = _read_env_local()

    if args.verify:
        base_url = current.get(env_config["url_var"], current.get("PROD_URL", ""))
        if not base_url:
            print(f"[ERROR] No base URL found in .env.local ({env_config['url_var']} or PROD_URL)")
            sys.exit(1)
        api_key = current.get(ENV_API_KEY, "")
        widget_key = current.get(ENV_WIDGET_KEY, "")
        print(f"Verifying credentials against {base_url}...")
        problems = _verify_credentials(base_url, api_key, widget_key)
        if problems:
            print("STALE credentials detected:")
            for k, v in problems.items():
                print(f"  {k}: {v}")
            sys.exit(1)
        else:
            print("All credentials valid.")
            sys.exit(0)

    # Refresh API key from Key Vault
    print(f"Refreshing {ENV_API_KEY} from Key Vault ({env_config['vault']}/{env_config['secret']})...")
    new_api_key = _az_get_secret(env_config["vault"], env_config["secret"])

    if not new_api_key:
        print("[ERROR] Could not retrieve API key from Key Vault.")
        print("  Check: az login, RBAC role, vault/secret name.")
        sys.exit(1)

    old_api_key = current.get(ENV_API_KEY, "")
    changed = new_api_key != old_api_key

    if args.dry_run:
        print(f"\n[DRY RUN] {ENV_API_KEY}:")
        if changed:
            print(f"  OLD: {old_api_key[:12]}...{old_api_key[-4:]}" if old_api_key else "  OLD: (not set)")
            print(f"  NEW: {new_api_key[:12]}...{new_api_key[-4:]}")
        else:
            print("  No change (already current)")
        print(f"\n[DRY RUN] {ENV_WIDGET_KEY}:")
        print("  Not managed by Key Vault — update manually from seed output or Cosmos.")
        return

    # Write updated API key
    if changed:
        current[ENV_API_KEY] = new_api_key
        _write_env_local(current)
        print(f"  Updated {ENV_API_KEY} in .env.local")
    else:
        print(f"  {ENV_API_KEY} already current — no change")

    # Widget key reminder
    widget_key = current.get(ENV_WIDGET_KEY, "")
    if not widget_key:
        print(f"\n[WARNING] {ENV_WIDGET_KEY} is not set in .env.local.")
        print("  Widget key is stored in Cosmos (PreferencesDocument.widget_key),")
        print("  not in Key Vault. Set it manually from seed_tenant.py output.")

    # Verify
    base_url = current.get(env_config["url_var"], current.get("PROD_URL", ""))
    if base_url:
        print(f"\nVerifying credentials against {base_url}...")
        problems = _verify_credentials(base_url, new_api_key, widget_key)
        if problems:
            print("STALE credentials still detected:")
            for k, v in problems.items():
                print(f"  {k}: {v}")
            print("\nNote: If API key was just rotated, the container may need a revision restart.")
        else:
            print("All credentials valid.")
    else:
        print(f"\n[SKIP] No base URL for verification ({env_config['url_var']} not in .env.local)")

    print("\nDone.")


if __name__ == "__main__":
    main()
