#!/usr/bin/env python3
"""Create the contact_messages Cosmos DB container (SPEC-1588).

Idempotent — safe to run multiple times. Uses the standard
get_collection_configs() schema definition from cosmos_schema.py.

Usage:
    python scripts/create_contact_messages_container.py --env staging
    python scripts/create_contact_messages_container.py --env production

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

CONTAINER_NAME = "contact_messages"


def main() -> None:
    parser = argparse.ArgumentParser(description="Create contact_messages container")
    parser.add_argument("--env", choices=["staging", "production"], default="staging")
    parser.add_argument("--dry-run", action="store_true", help="Print config without creating")
    args = parser.parse_args()

    from src.multi_tenant.cosmos_schema import get_collection_configs

    # Find the contact_messages config
    configs = get_collection_configs()
    cm_config = next((c for c in configs if c.name == CONTAINER_NAME), None)

    if cm_config is None:
        print(f"ERROR: {CONTAINER_NAME} not found in get_collection_configs()")
        sys.exit(1)

    env = ENVIRONMENTS[args.env]
    print(f"Environment: {args.env}")
    print(f"Endpoint: {env['endpoint']}")
    print(f"Database: {env['database']}")
    print(f"Container: {cm_config.name}")
    print(f"Partition key: {cm_config.partition_key}")

    if cm_config.indexing_policy:
        import json

        print(f"Indexing policy: {json.dumps(cm_config.indexing_policy, indent=2)}")

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
            "id": cm_config.name,
            "partition_key": PartitionKey(path=cm_config.partition_key),
        }
        if cm_config.indexing_policy:
            container_kwargs["indexing_policy"] = cm_config.indexing_policy

        database.create_container(**container_kwargs)
        print(f"\nContainer '{cm_config.name}' created successfully.")
    except Exception as exc:
        if "Conflict" in str(exc) or "409" in str(exc):
            print(f"\nContainer '{cm_config.name}' already exists (idempotent).")
        else:
            print(f"\nERROR creating container: {exc}")
            sys.exit(1)


if __name__ == "__main__":
    main()
