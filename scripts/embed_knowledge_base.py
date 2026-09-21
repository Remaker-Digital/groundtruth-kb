"""
Embed all unembedded Knowledge Base entries for a tenant.

Connects to production Cosmos DB, creates an Azure OpenAI client,
and embeds KB entries one at a time with rate-limit-aware retry logic.

Usage:
    # Dry run - show unembedded count only:
    python scripts/embed_knowledge_base.py

    # Embed all unembedded entries for tenant #1:
    python scripts/embed_knowledge_base.py --embed

    # Embed for a specific tenant:
    python scripts/embed_knowledge_base.py --embed --tenant-id my-tenant-123

Requires Azure credentials in applications/Agent_Red/.env.local or the environment:
    COSMOS_DB_ENDPOINT, COSMOS_DB_KEY, COSMOS_DB_DATABASE,
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import binascii
import logging
import os
import sys
import time
from datetime import UTC
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = REPO_ROOT / "applications" / "Agent_Red"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts._env import load_env_local  # noqa: E402 - standalone script bootstrap

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
# Suppress verbose Azure SDK HTTP logging
logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Default tenant
DEFAULT_TENANT_ID = "remaker-digital-001"

# Rate limit handling
INTER_ENTRY_DELAY = 0.5  # seconds between individual entries
RATE_LIMIT_WAIT = 65.0  # seconds to wait on 429 (API says retry after 60)
MAX_RETRIES = 3


def require_decoded_text(entry: dict) -> None:
    """Refuse ciphertext that an uninitialized repository reader left unchanged."""
    for field in ("title", "content"):
        value = entry.get(field)
        if not isinstance(value, str) or len(value) < 40:
            continue
        try:
            decoded = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError):
            continue
        if len(decoded) >= 29:
            raise RuntimeError(
                f"KB entry {entry['id']} has undecoded {field}; "
                "use the application embedding pipeline with tenant decryption initialized"
            )


async def run(tenant_id: str, do_embed: bool = False) -> None:
    """Embed all unembedded KB entries for a tenant."""

    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.knowledge_vectorizer import (
        EMBEDDING_DIMENSIONS,
        EMBEDDING_MODEL,
        MAX_CONTENT_CHARS,
        compute_content_hash,
    )
    from src.multi_tenant.repository import KnowledgeBaseRepository

    # Initialize Cosmos DB
    cosmos = get_cosmos_manager()
    openai_client = None
    try:
        await cosmos._ensure_client()

        kb_repo = KnowledgeBaseRepository()

        # Inspect the actual vectors, not model metadata left by a partial write.
        print("  Querying Cosmos DB for KB entries...", flush=True)
        summary = await kb_repo.query(
            tenant_id=tenant_id,
            query_text=("SELECT c.id, c.title, c.is_active, c.embedding FROM c WHERE c.is_active = true"),
        )
        embedded_count = sum(1 for e in summary if e.get("embedding"))
        unembedded_ids = [e["id"] for e in summary if not e.get("embedding")]
        total = len(summary)

        print()
        print("=" * 65)
        print("  AGENT RED - KB EMBEDDING PIPELINE")
        print("=" * 65)
        print()
        print(f"  Tenant ID:          {tenant_id}")
        print(f"  Total KB entries:   {total}", flush=True)
        print(f"  Already embedded:   {embedded_count}", flush=True)
        print(f"  Need embedding:     {len(unembedded_ids)}", flush=True)
        print(flush=True)

        if not unembedded_ids:
            print("  All entries are already embedded. Nothing to do.")
            print()
            return

        if not do_embed:
            print("  [DRY RUN] Run with --embed to vectorize entries.")
            print()
            print("  First 10 entries needing embedding:")
            for eid in unembedded_ids[:10]:
                matching = [e for e in summary if e["id"] == eid]
                title = matching[0].get("title", "(no title)") if matching else eid
                print(f"    - {title[:60]}")
            if len(unembedded_ids) > 10:
                print(f"    ... and {len(unembedded_ids) - 10} more")
            print()
            return

        # Create Azure OpenAI client
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        if not endpoint or not api_key:
            raise RuntimeError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY are required")

        from datetime import datetime

        from openai import AsyncAzureOpenAI

        openai_client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-10-21",
        )

        total_to_embed = len(unembedded_ids)
        print(f"  Embedding {total_to_embed} entries one at a time...", flush=True)
        print(f"  Inter-entry delay: {INTER_ENTRY_DELAY}s  |  Rate limit wait: {RATE_LIMIT_WAIT}s", flush=True)
        print(flush=True)

        start = time.monotonic()
        success_count = 0
        fail_count = 0

        for idx, entry_id in enumerate(unembedded_ids):
            # Fetch full entry from Cosmos DB
            try:
                entry = await kb_repo.read(tenant_id, entry_id)
            except Exception as exc:
                print(f"  [{idx + 1}/{total_to_embed}] Failed to read entry {entry_id[:20]}: {exc}", flush=True)
                fail_count += 1
                continue

            title = entry.get("title", "(no title)")
            content = entry.get("content", "")
            require_decoded_text({**entry, "id": entry_id})

            # Prepare embedding text (same as vectorizer._prepare_embedding_text)
            tags = ", ".join(entry.get("tags", []))
            entry_type = entry.get("entry_type", "")
            parts = [f"[{entry_type.upper()}] {title}"]
            if tags:
                parts.append(f"Tags: {tags}")
            if content:
                truncated = content[:MAX_CONTENT_CHARS]
                if len(content) > MAX_CONTENT_CHARS:
                    truncated = truncated.rsplit(" ", 1)[0] + "..."
                parts.append(truncated)
            embed_text = "\n".join(parts)

            # Embed with retry
            if idx == 0:
                print(f"  Starting first embedding: {title[:50]}...", flush=True)
            embedding = None
            for attempt in range(MAX_RETRIES):
                try:
                    response = await openai_client.embeddings.create(
                        model=EMBEDDING_MODEL,
                        input=[embed_text],
                        dimensions=EMBEDDING_DIMENSIONS,
                    )
                    embedding = response.data[0].embedding
                    break
                except Exception as exc:
                    exc_str = str(exc)
                    if "429" in exc_str or "RateLimitReached" in exc_str:
                        wait = RATE_LIMIT_WAIT
                        print(f"  [{idx + 1}/{total_to_embed}] Rate limited. Waiting {wait}s...", flush=True)
                        await asyncio.sleep(wait)
                    else:
                        print(f"  [{idx + 1}/{total_to_embed}] ERROR: {exc_str[:100]}")
                        if attempt < MAX_RETRIES - 1:
                            await asyncio.sleep(5)

            if embedding is None:
                fail_count += 1
                print(f"  [{idx + 1}/{total_to_embed}] FAILED: {title[:50]}")
                continue

            # Update entry in Cosmos DB
            now = datetime.now(UTC).isoformat()
            content_hash = compute_content_hash(title, content)

            try:
                await kb_repo.patch(
                    tenant_id=tenant_id,
                    document_id=entry_id,
                    operations=[
                        {"op": "set", "path": "/embedding", "value": embedding},
                        {"op": "set", "path": "/embedding_model", "value": EMBEDDING_MODEL},
                        {"op": "set", "path": "/embedded_at", "value": now},
                        {"op": "set", "path": "/content_hash", "value": content_hash},
                    ],
                )
                success_count += 1
                if success_count % 10 == 0 or idx == total_to_embed - 1:
                    elapsed = time.monotonic() - start
                    print(
                        f"  [{idx + 1}/{total_to_embed}] "
                        f"Embedded {success_count} entries "
                        f"({elapsed:.0f}s elapsed, "
                        f"{elapsed / success_count:.1f}s/entry)",
                        flush=True,
                    )
            except Exception as exc:
                fail_count += 1
                print(f"  [{idx + 1}/{total_to_embed}] DB update failed: {exc}")

            # Rate limit delay between entries
            if idx < total_to_embed - 1:
                await asyncio.sleep(INTER_ENTRY_DELAY)

        elapsed = time.monotonic() - start

        print()
        print("-" * 65)
        print(f"  Embedded:   {success_count} entries")
        print(f"  Failed:     {fail_count} entries")
        print(f"  Duration:   {elapsed:.1f}s ({elapsed / max(success_count, 1):.1f}s per entry)")
        print()

        if fail_count == 0:
            print("  [OK] All KB entries are now vectorized.")
            print("  Hybrid search (BM25 + vector + RRF) is now available.")
        else:
            raise RuntimeError(f"{fail_count} entries failed to embed; re-run to retry")

        print()
        print("=" * 65)
        print("  EMBEDDING COMPLETE")
        print("=" * 65)
        print()

    finally:
        try:
            if openai_client is not None:
                await openai_client.close()
        finally:
            await cosmos.close()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Embed Knowledge Base entries for a tenant",
    )
    parser.add_argument(
        "--embed",
        action="store_true",
        help="Run embedding (omit for dry run)",
    )
    parser.add_argument(
        "--tenant-id",
        default=DEFAULT_TENANT_ID,
        help=f"Tenant ID (default: {DEFAULT_TENANT_ID})",
    )
    args = parser.parse_args()
    load_env_local(env_file=APP_ROOT / ".env.local")

    await run(tenant_id=args.tenant_id, do_embed=args.embed)


if __name__ == "__main__":
    asyncio.run(main())
