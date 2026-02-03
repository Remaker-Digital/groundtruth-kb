"""
Initialize all 10 Cosmos DB containers for Agent Red production.

Creates the database and all containers with partition keys, unique key
policies, composite indexes, TTL defaults, and DiskANN vector index.
Idempotent — safe to run multiple times.

Prerequisites:
    - .env.local with COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE
    - Cosmos DB account must have EnableNoSQLVectorSearch capability enabled
    - pip install azure-cosmos python-dotenv

Usage:
    python scripts/setup/initialize_cosmos_containers.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import asyncio
import os
import sys
import time

# Add project root to path for src imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from dotenv import load_dotenv


def main() -> None:
    # Load .env.local from project root
    env_path = os.path.join(project_root, ".env.local")
    if not os.path.exists(env_path):
        print(f"ERROR: {env_path} not found. Copy .env.example to .env.local and fill in credentials.")
        sys.exit(1)

    load_dotenv(env_path, override=True)

    endpoint = os.environ.get("COSMOS_DB_ENDPOINT", "")
    key = os.environ.get("COSMOS_DB_KEY", "")
    database_name = os.environ.get("COSMOS_DB_DATABASE", "")

    if not endpoint or not key or not database_name:
        print("ERROR: COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, and COSMOS_DB_DATABASE must be set in .env.local")
        sys.exit(1)

    print(f"Cosmos DB endpoint:  {endpoint}")
    print(f"Database name:       {database_name}")
    print()

    asyncio.run(run_initialization(endpoint, key, database_name))


async def run_initialization(endpoint: str, key: str, database_name: str) -> None:
    from azure.cosmos.aio import CosmosClient

    from src.multi_tenant.cosmos_schema import get_collection_configs, initialize_database

    configs = get_collection_configs()
    print(f"Will create {len(configs)} containers:")
    for cfg in configs:
        vector_tag = " [+DiskANN vector index]" if cfg.vector_embedding_policy else ""
        ttl_tag = f" [TTL={cfg.default_ttl}s]" if cfg.default_ttl else ""
        unique_tag = f" [unique: {cfg.unique_keys}]" if cfg.unique_keys else ""
        print(f"  - {cfg.name:<22} partition={cfg.partition_key}{unique_tag}{ttl_tag}{vector_tag}")
    print()

    async with CosmosClient(url=endpoint, credential=key) as client:
        print(f"Connected to Cosmos DB. Initializing database '{database_name}'...")
        start = time.monotonic()

        result = await initialize_database(client, database_name=database_name)

        elapsed = time.monotonic() - start
        print()
        print(f"Initialization complete in {elapsed:.1f}s")
        print(f"Database: {result['database']}")
        print()
        print("Container results:")

        all_ready = True
        for name, status in result["containers"].items():
            icon = "[OK]" if status == "ready" else "[FAIL]"
            if status != "ready":
                all_ready = False
            print(f"  {icon} {name}")

        print()
        if all_ready:
            print(f"All {len(result['containers'])} containers ready.")
        else:
            failed = [n for n, s in result["containers"].items() if s != "ready"]
            print(f"WARNING: {len(failed)} container(s) failed: {', '.join(failed)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
