"""
Cosmos DB full initialization script.

Creates the 'agentred' database and all 10 containers with their
partition keys, unique key policies, composite indexes, TTL settings,
and the DiskANN vector index on memory_vectors.

Prerequisites:
    - .env.local with COSMOS_DB_ENDPOINT and COSMOS_DB_KEY
    - EnableNoSQLVectorSearch capability enabled on the Cosmos DB account
    - Python packages: azure-cosmos, python-dotenv

Usage:
    python scripts/init_cosmos_containers.py

    Options:
        --dry-run    Print what would be created without executing
        --verify     After creation, verify all containers exist

The script is idempotent — safe to run multiple times.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import asyncio
import argparse
import json
import logging
import os
import sys

# Add project root to path so we can import src modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local
load_env_local()

from src.multi_tenant.cosmos_schema import (
    ALL_COLLECTIONS,
    DATABASE_NAME,
    get_collection_configs,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("init_cosmos")


def print_plan() -> None:
    """Print the initialization plan (containers, partition keys, policies)."""
    configs = get_collection_configs()
    database_name = os.environ.get("COSMOS_DB_DATABASE", DATABASE_NAME)
    endpoint = os.environ.get("COSMOS_DB_ENDPOINT", "(not set)")

    print("\n" + "=" * 70)
    print("COSMOS DB INITIALIZATION PLAN")
    print("=" * 70)
    print(f"  Endpoint:  {endpoint}")
    print(f"  Database:  {database_name}")
    print(f"  Containers: {len(configs)}")
    print("=" * 70)

    for i, config in enumerate(configs, 1):
        print(f"\n  {i}. {config.name}")
        print(f"     Partition key: {config.partition_key}")

        if config.unique_keys:
            keys_str = ", ".join(str(k) for k in config.unique_keys)
            print(f"     Unique keys:   {keys_str}")

        if config.default_ttl is not None:
            days = config.default_ttl // (24 * 60 * 60)
            print(f"     Default TTL:   {config.default_ttl}s ({days} days)")

        if config.indexing_policy:
            composite = config.indexing_policy.get("compositeIndexes", [])
            if composite:
                print(f"     Composite indexes: {len(composite)}")

            vector_indexes = config.indexing_policy.get("vectorIndexes", [])
            if vector_indexes:
                for vi in vector_indexes:
                    print(f"     Vector index:  {vi['path']} ({vi['type']})")

        if config.vector_embedding_policy:
            embeddings = config.vector_embedding_policy.get("vectorEmbeddings", [])
            for emb in embeddings:
                print(
                    f"     Vector embedding: {emb['path']} "
                    f"({emb['dataType']}, {emb['dimensions']}d, {emb['distanceFunction']})"
                )

    print("\n" + "=" * 70)


async def run_initialization() -> dict:
    """Run the full database initialization."""
    from src.multi_tenant.cosmos_client import get_cosmos_manager

    manager = get_cosmos_manager()

    try:
        logger.info("Starting Cosmos DB initialization...")
        result = await manager.initialize()
        return result
    finally:
        await manager.close()


async def verify_containers() -> None:
    """Verify all containers exist and are accessible."""
    from azure.cosmos.aio import CosmosClient

    endpoint = os.environ.get("COSMOS_DB_ENDPOINT", "")
    key = os.environ.get("COSMOS_DB_KEY", "")
    database_name = os.environ.get("COSMOS_DB_DATABASE", DATABASE_NAME)

    if not endpoint or not key:
        print("[ERROR] COSMOS_DB_ENDPOINT and COSMOS_DB_KEY must be set")
        sys.exit(1)

    client = CosmosClient(url=endpoint, credential=key)

    try:
        database = client.get_database_client(database_name)

        # List all containers
        containers_found = []
        async for container_props in database.list_containers():
            containers_found.append(container_props["id"])

        print(f"\n{'=' * 70}")
        print("VERIFICATION RESULTS")
        print(f"{'=' * 70}")
        print(f"  Database: {database_name}")
        print(f"  Containers found: {len(containers_found)}")
        print(f"  Containers expected: {len(ALL_COLLECTIONS)}")
        print()

        all_ok = True
        for name in ALL_COLLECTIONS:
            if name in containers_found:
                # Read container properties for detail
                container = database.get_container_client(name)
                props = await container.read()
                pk = props.get("partitionKey", {}).get("paths", ["?"])[0]
                ttl = props.get("defaultTtl", None)
                ttl_str = f" (TTL: {ttl}s)" if ttl else ""
                print(f"  [OK] {name:<25} partition={pk}{ttl_str}")
            else:
                print(f"  [MISSING] {name}")
                all_ok = False

        # Check for unexpected containers
        unexpected = set(containers_found) - set(ALL_COLLECTIONS)
        if unexpected:
            print()
            for name in sorted(unexpected):
                print(f"  [EXTRA] {name} (not in schema)")

        print()
        if all_ok:
            print("  Result: ALL 10 CONTAINERS VERIFIED")
        else:
            missing = set(ALL_COLLECTIONS) - set(containers_found)
            print(f"  Result: MISSING {len(missing)} containers: {sorted(missing)}")

        print(f"{'=' * 70}\n")

    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(
        description="Initialize Cosmos DB containers for Agent Red"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print initialization plan without executing",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify containers exist after creation (or standalone)",
    )
    args = parser.parse_args()

    # Always print the plan
    print_plan()

    if args.dry_run:
        print("\n  [DRY RUN] No changes made.\n")
        return

    # Validate environment
    endpoint = os.environ.get("COSMOS_DB_ENDPOINT", "")
    key = os.environ.get("COSMOS_DB_KEY", "")
    if not endpoint or not key:
        print("\n[ERROR] COSMOS_DB_ENDPOINT and COSMOS_DB_KEY must be set in .env.local")
        sys.exit(1)

    # Run initialization
    print("\nProceeding with initialization...\n")
    result = asyncio.run(run_initialization())

    # Print results
    print(f"\n{'=' * 70}")
    print("INITIALIZATION RESULTS")
    print(f"{'=' * 70}")
    print(f"  Database: {result['database']}")
    for name, status in result["containers"].items():
        icon = "[OK]" if status == "ready" else "[ERROR]"
        print(f"  {icon} {name}: {status}")

    ready_count = sum(1 for s in result["containers"].values() if s == "ready")
    total = len(result["containers"])
    print(f"\n  {ready_count}/{total} containers ready")
    print(f"{'=' * 70}\n")

    if ready_count < total:
        print("[ERROR] Some containers failed to create. Check logs above.")
        sys.exit(1)

    # Optional verification
    if args.verify:
        print("Running verification...\n")
        asyncio.run(verify_containers())


if __name__ == "__main__":
    main()
