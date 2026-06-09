#!/usr/bin/env python3
"""Create the pii_token_mappings Cosmos DB container (SPEC-1545).

Idempotent — safe to run multiple times. Uses the standard
get_collection_configs() schema definition from cosmos_schema.py.

Usage:
    python scripts/create_pii_container.py --env staging
    python scripts/create_pii_container.py --env production

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import io
import os
import sys

# Windows cp1252 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


ENVIRONMENTS = {
    "staging": {
        "endpoint": "https://cosmos-agentred-eastus.documents.azure.com:443/",
        "database": "agentred",
    },
    "production": {
        "endpoint": "https://cosmos-agentred-eastus.documents.azure.com:443/",
        "database": "agentred",
    },
}

CONTAINER_NAME = "pii_token_mappings"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create pii_token_mappings container")
    parser.add_argument("--env", choices=["staging", "production"], default="staging")
    parser.add_argument("--dry-run", action="store_true", help="Print config without creating")
    args = parser.parse_args()

    from src.multi_tenant.cosmos_schema import get_collection_configs

    # Find the pii_token_mappings config
    configs = get_collection_configs()
    pii_config = next((c for c in configs if c.name == CONTAINER_NAME), None)

    if pii_config is None:
        print(f"ERROR: {CONTAINER_NAME} not found in get_collection_configs()")
        sys.exit(1)

    env = ENVIRONMENTS[args.env]
    print(f"Environment: {args.env}")
    print(f"Endpoint: {env['endpoint']}")
    print(f"Database: {env['database']}")
    print(f"Container: {pii_config.name}")
    print(f"Partition key: {pii_config.partition_key}")
    print(f"Default TTL: {pii_config.default_ttl}s ({pii_config.default_ttl // 86400}d)")

    if pii_config.indexing_policy:
        import json

        print(f"Indexing policy: {json.dumps(pii_config.indexing_policy, indent=2)}")

    if args.dry_run:
        print("\n[DRY RUN] Would create container. Use without --dry-run to execute.")
        return

    try:
        from azure.cosmos import CosmosClient, PartitionKey
    except ImportError:
        print("ERROR: azure-cosmos package not installed. Run: pip install azure-cosmos")
        sys.exit(1)

    # Use DefaultAzureCredential (managed identity in Azure, CLI locally)
    try:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        client = CosmosClient(env["endpoint"], credential=credential)
    except Exception as exc:
        print(f"ERROR: Failed to authenticate: {exc}")
        sys.exit(1)

    database = client.get_database_client(env["database"])

    # Create container (idempotent — 409 Conflict is OK)
    try:
        container_kwargs = {
            "id": pii_config.name,
            "partition_key": PartitionKey(path=pii_config.partition_key),
        }
        if pii_config.default_ttl is not None:
            container_kwargs["default_ttl"] = pii_config.default_ttl
        if pii_config.indexing_policy:
            container_kwargs["indexing_policy"] = pii_config.indexing_policy

        container = database.create_container(**container_kwargs)
        print(f"\nContainer '{pii_config.name}' created successfully.")
    except Exception as exc:
        if "Conflict" in str(exc) or "409" in str(exc):
            print(f"\nContainer '{pii_config.name}' already exists (idempotent).")
        else:
            print(f"\nERROR creating container: {exc}")
            sys.exit(1)


if __name__ == "__main__":
    main()
