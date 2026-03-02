"""Cleanup orphaned conversations — patch is_billable=false for conversations
with 0 messages that are incorrectly marked as billable.

Targets staging environment only. Run after deploying SPEC-1606 (billable
classification deferral) to correct historical data pollution from Locust
load tests and verification scripts.

Usage:
    python scripts/cleanup_orphaned_conversations.py --env staging --dry-run
    python scripts/cleanup_orphaned_conversations.py --env staging

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import io
import os
import sys

# Windows cp1252 safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Environment configuration (same pattern as upgrade_verification.py)
# ---------------------------------------------------------------------------

ENVIRONMENTS = {
    "staging": {
        "base_url": "https://agent-red-staging.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
        "tenants": {
            "staging-001": {
                "api_key": "ar_user_stag_qejkqo2vSBoS-QceOJ8eg4wS0Gy82G5H",
            },
            "staging-002": {
                "api_key": "ar_user_stag_nn3mMFfxve98raVOJI0zzFQ7qH_PSJn9",
            },
        },
    },
}


async def cleanup_tenant(
    base_url: str,
    api_key: str,
    tenant_name: str,
    dry_run: bool = True,
) -> dict[str, int]:
    """Find and patch orphaned conversations for a single tenant.

    Returns counts: {'found': N, 'patched': N, 'errors': N}
    """
    import httpx

    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    stats = {"found": 0, "patched": 0, "errors": 0}

    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=30) as client:
        # Fetch all conversations (paginated)
        offset = 0
        limit = 50
        orphaned = []

        while True:
            resp = await client.get(
                "/api/admin/conversations",
                params={"offset": offset, "limit": limit, "archived": "include"},
            )
            if resp.status_code != 200:
                print(f"  [{tenant_name}] Error fetching conversations: {resp.status_code}")
                stats["errors"] += 1
                break

            data = resp.json()
            conversations = data.get("conversations", [])
            if not conversations:
                break

            for conv in conversations:
                if conv.get("messageCount", 0) == 0 and conv.get("isBillable", False):
                    orphaned.append(conv["conversationId"])

            total = data.get("totalCount", 0)
            offset += limit
            if offset >= total:
                break

        stats["found"] = len(orphaned)
        print(f"  [{tenant_name}] Found {len(orphaned)} orphaned conversations (0 messages, billable)")

        if dry_run:
            for conv_id in orphaned[:5]:
                print(f"    Would patch: {conv_id}")
            if len(orphaned) > 5:
                print(f"    ... and {len(orphaned) - 5} more")
            return stats

        # Patch each orphaned conversation
        for conv_id in orphaned:
            try:
                # Use the resolve endpoint to end the conversation
                # and let the finalization logic correct is_billable
                resp = await client.post(
                    f"/api/admin/conversations/{conv_id}/resolve",
                )
                if resp.status_code in (200, 204):
                    stats["patched"] += 1
                else:
                    print(f"    Error resolving {conv_id}: {resp.status_code}")
                    stats["errors"] += 1
            except Exception as e:
                print(f"    Exception patching {conv_id}: {e}")
                stats["errors"] += 1

            # Rate limiting: 10 rpm for starter tier
            await asyncio.sleep(0.5)

        print(f"  [{tenant_name}] Patched {stats['patched']}, errors {stats['errors']}")

    return stats


async def main() -> None:
    parser = argparse.ArgumentParser(description="Cleanup orphaned conversations")
    parser.add_argument("--env", choices=list(ENVIRONMENTS), required=True)
    parser.add_argument("--dry-run", action="store_true", default=False)
    args = parser.parse_args()

    env = ENVIRONMENTS[args.env]
    base_url = env["base_url"]
    mode = "DRY RUN" if args.dry_run else "LIVE"

    print(f"\n{'='*60}")
    print(f"Orphaned Conversation Cleanup — {args.env} ({mode})")
    print(f"{'='*60}\n")

    total_stats = {"found": 0, "patched": 0, "errors": 0}

    for tenant_name, tenant_cfg in env["tenants"].items():
        stats = await cleanup_tenant(
            base_url=base_url,
            api_key=tenant_cfg["api_key"],
            tenant_name=tenant_name,
            dry_run=args.dry_run,
        )
        for k in total_stats:
            total_stats[k] += stats[k]

    print(f"\n{'='*60}")
    print(f"Total: {total_stats['found']} found, {total_stats['patched']} patched, {total_stats['errors']} errors")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
