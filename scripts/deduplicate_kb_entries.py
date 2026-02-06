"""
Deduplicate Knowledge Base entries for a tenant.

Groups active entries by content hash, keeps the newest entry per group,
and soft-deletes all duplicates (sets is_active = false).

Usage:
    # Dry run — show what would be deactivated:
    python scripts/deduplicate_kb_entries.py --tenant-id remaker-digital-001

    # Execute deduplication:
    python scripts/deduplicate_kb_entries.py --tenant-id remaker-digital-001 --execute

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local
_env_path = PROJECT_ROOT / ".env.local"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def run(tenant_id: str, execute: bool = False) -> None:
    """Deduplicate KB entries for a tenant."""

    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.repository import KnowledgeBaseRepository
    from src.multi_tenant.knowledge_vectorizer import compute_content_hash

    # Initialize Cosmos DB
    cosmos = get_cosmos_manager()
    await cosmos.initialize()

    repo = KnowledgeBaseRepository()

    # Fetch all active entries (lightweight — we need title, content, id, created_at)
    print("  Querying active KB entries...", flush=True)
    entries = await repo.query(
        tenant_id=tenant_id,
        query_text=(
            "SELECT c.id, c.title, c.content, c.content_hash, c.created_at "
            "FROM c WHERE c.is_active = true"
        ),
    )

    total = len(entries)
    print(flush=True)
    print("=" * 65)
    print("  AGENT RED - KB DEDUPLICATION")
    print("=" * 65)
    print(flush=True)
    print(f"  Tenant ID:          {tenant_id}", flush=True)
    print(f"  Active entries:     {total}", flush=True)

    if total == 0:
        print("  No active entries found. Nothing to do.")
        return

    # Group by content hash
    groups: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        # Compute hash dynamically (some entries may lack stored content_hash)
        title = entry.get("title", "")
        content = entry.get("content", "")
        h = entry.get("content_hash") or compute_content_hash(title, content)
        groups[h].append(entry)

    unique_count = len(groups)
    dup_groups = {h: g for h, g in groups.items() if len(g) > 1}
    dup_entry_count = sum(len(g) - 1 for g in dup_groups.values())

    print(f"  Unique articles:    {unique_count}", flush=True)
    print(f"  Duplicate groups:   {len(dup_groups)}", flush=True)
    print(f"  Entries to remove:  {dup_entry_count}", flush=True)
    print(flush=True)

    if dup_entry_count == 0:
        print("  No duplicates found. Nothing to do.")
        print()
        return

    if not execute:
        print("  [DRY RUN] Duplicate groups:", flush=True)
        for h, group in sorted(dup_groups.items(), key=lambda x: x[1][0].get("title", "")):
            title = group[0].get("title", "(no title)")
            print(f"    {title[:55]} — {len(group)} copies (keeping 1, removing {len(group)-1})")
        print()
        print(f"  Run with --execute to soft-delete {dup_entry_count} duplicate entries.")
        print()
        return

    # Execute deduplication
    print(f"  Soft-deleting {dup_entry_count} duplicate entries...", flush=True)
    deleted = 0
    errors = 0

    for h, group in dup_groups.items():
        # Sort by created_at descending — keep the newest
        group.sort(key=lambda e: e.get("created_at", ""), reverse=True)
        keep = group[0]
        remove = group[1:]

        title = keep.get("title", "(no title)")

        for entry in remove:
            try:
                await repo.soft_delete(tenant_id, entry["id"])
                deleted += 1
            except Exception as exc:
                print(f"    ERROR deactivating {entry['id'][:20]}: {exc}")
                errors += 1

        if deleted % 20 == 0 or deleted == dup_entry_count:
            print(f"    Progress: {deleted}/{dup_entry_count} deleted", flush=True)

    print(flush=True)
    print("-" * 65)
    print(f"  Soft-deleted:   {deleted} entries")
    print(f"  Errors:         {errors} entries")
    print(f"  Remaining:      {total - deleted} active entries")
    print()

    if errors == 0:
        print(f"  [OK] Deduplication complete. {unique_count} unique articles remain active.")
    else:
        print(f"  [WARN] {errors} entries failed. Re-run to retry.")

    print()
    print("=" * 65)
    print("  DEDUPLICATION COMPLETE")
    print("=" * 65)
    print()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deduplicate Knowledge Base entries for a tenant",
    )
    parser.add_argument(
        "--tenant-id",
        required=True,
        help="Tenant ID to deduplicate",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute deduplication (default is dry run)",
    )
    args = parser.parse_args()

    await run(tenant_id=args.tenant_id, execute=args.execute)


if __name__ == "__main__":
    asyncio.run(main())
