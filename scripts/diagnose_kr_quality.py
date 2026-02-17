"""
Diagnose Knowledge Retrieval quality for a tenant.

(c) 2026 Remaker Digital. All rights reserved.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local
load_env_local()

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
for _n in ["azure", "azure.core.pipeline.policies.http_logging_policy",
           "urllib3", "httpx", "openai", "httpcore"]:
    logging.getLogger(_n).setLevel(logging.WARNING)

DEFAULT_TENANT_ID = "remaker-digital-001"
DEFAULT_QUERY = "What is your pricing?"


async def run(tenant_id: str, query: str, top_k: int = 10) -> None:
    """Run diagnostic search and print detailed results."""

    from src.multi_tenant.cosmos_client import get_cosmos_manager
    from src.multi_tenant.repository import KnowledgeBaseRepository
    from src.multi_tenant.knowledge_vectorizer import (
        KnowledgeVectorizer,
        get_knowledge_vectorizer,
        MIN_RELEVANCE_SCORE,
    )

    SEP = "=" * 75
    DASH = "-" * 75
    TILDE = "~" * 70
    P = lambda *a, **kw: print(*a, flush=True, **kw)

    P(SEP)
    P("  AGENT RED - KNOWLEDGE RETRIEVAL QUALITY DIAGNOSTIC")
    P(SEP)
    P()
    P(f"  Tenant:   {tenant_id}")
    P(f'  Query:    "{query}"')
    P(f"  Top K:    {top_k}")
    P()

    P("  [1/5] Initializing Cosmos DB...")
    cosmos = get_cosmos_manager()
    await cosmos.initialize()

    P("  [2/5] Counting KB entries for tenant...")
    kb_repo = KnowledgeBaseRepository()
    all_entries = await kb_repo.list_active(tenant_id=tenant_id)
    embedded_entries = [e for e in all_entries if e.get("embedding_model")]
    unembedded_entries = [e for e in all_entries if not e.get("embedding_model")]

    P(f"         Total active entries:    {len(all_entries)}")
    P(f"         With embeddings:         {len(embedded_entries)}")
    P(f"         Without embeddings:      {len(unembedded_entries)}")
    P()

    if not all_entries:
        P("  [ERROR] No active KB entries found for this tenant. Aborting.")
        return

    type_counts: dict[str, int] = {}
    for e in all_entries:
        t = e.get("entry_type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    P("         Entry types:")
    for t, c in sorted(type_counts.items()):
        P(f"           {t}: {c}")
    P()

    P("  [3/5] Configuring vectorizer + Azure OpenAI...")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    if not endpoint or not api_key:
        P("  [ERROR] AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY required.")
        return

    from openai import AsyncAzureOpenAI
    openai_client = AsyncAzureOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version="2024-10-21",
    )

    vectorizer = get_knowledge_vectorizer()
    vectorizer.configure(kb_repo=kb_repo, openai_client=openai_client)
    P(f"         Endpoint:  {endpoint}")
    P("         Model:     text-embedding-3-large (3072d)")
    P()

    P(f'  [4/5] Running hybrid search for: "{query}"')
    P("         (vector weight=0.7, BM25 weight=0.3, RRF k=60)")
    P()

    t0 = time.monotonic()
    results = await vectorizer.search(tenant_id=tenant_id, query=query, top_k=top_k)
    elapsed_ms = (time.monotonic() - t0) * 1000

    P(DASH)
    P(f"  SEARCH RESULTS  ({len(results)} results in {elapsed_ms:.0f}ms)")
    P(DASH)
    P()

    if not results:
        P("  [WARN] No results returned.")
        if not embedded_entries:
            P("         Likely cause: no entries have embeddings yet.")
            P("         Run: python scripts/embed_knowledge_base.py --embed")
        P()
    else:
        for i, r in enumerate(results):
            title = r.get("title", "(no title)")
            entry_type = r.get("entry_type", "?")
            rrf = r.get("rrf_score", 0.0)
            vec_sim = r.get("vector_similarity", r.get("similarity"))
            bm25 = r.get("bm25_score")
            vec_rank = r.get("vector_rank")
            bm25_rank = r.get("bm25_rank")
            content = r.get("content", "")
            tags = r.get("tags", [])
            entry_id = str(r.get("id", "?"))

            P(f"  [{i+1}] {title}")
            eid = entry_id[:40] + ("..." if len(entry_id) > 40 else "")
            P(f"      ID:              {eid}")
            P(f"      Type:            {entry_type}")
            tag_str = ", ".join(tags) if tags else "(none)"
            P(f"      Tags:            {tag_str}")
            P(f"      RRF Score:       {rrf:.6f}")
            if vec_sim is not None:
                P(f"      Vector Sim:      {vec_sim:.6f}")
            else:
                P("      Vector Sim:      N/A")
            if bm25 is not None:
                P(f"      BM25 Score:      {bm25:.6f}")
            else:
                P("      BM25 Score:      N/A")
            if vec_rank is not None:
                P(f"      Vector Rank:     {vec_rank}")
            else:
                P("      Vector Rank:     N/A")
            if bm25_rank is not None:
                P(f"      BM25 Rank:       {bm25_rank}")
            else:
                P("      BM25 Rank:       N/A")
            P(f"      Content length:  {len(content)} chars")
            preview = content[:200].replace(chr(10), " ")
            if len(content) > 200:
                preview += "..."
            P(f"      Content:         {preview}")
            P()

        above = [r for r in results if r.get("rrf_score", 0) >= MIN_RELEVANCE_SCORE]
        below = [r for r in results if r.get("rrf_score", 0) < MIN_RELEVANCE_SCORE]
        P(f"  MIN_RELEVANCE_SCORE = {MIN_RELEVANCE_SCORE}")
        P(f"  Results above threshold: {len(above)}")
        P(f"  Results below threshold: {len(below)} (would be filtered by format_for_pipeline)")
        P()

    P(DASH)
    P("  PIPELINE CONTEXT (format_for_pipeline output)")
    P(DASH)
    P()

    formatted = KnowledgeVectorizer.format_for_pipeline(results, max_chars=2500)
    ctx = formatted.get("context", "")
    P(f"  Retrieval mode:  {formatted.get('retrieval_mode', '?')}")
    P(f"  Model:           {formatted.get('model', '?')}")
    P(f"  Sources count:   {len(formatted.get('sources', []))}")
    P(f"  Context length:  {len(ctx)} chars")
    P()

    sources = formatted.get("sources", [])
    if sources:
        P("  Sources included in pipeline context:")
        for s in sources:
            sc = s.get("score", 0)
            ti = s.get("title", "?")
            ty = s.get("type", "?")
            mo = s.get("retrieval_mode", "?")
            P(f"    - [{ty}] {ti}  (score={sc:.4f}, mode={mo})")
        P()

    if ctx:
        P("  Full context string passed to Response Generator:")
        P("  " + TILDE)
        for ln in ctx.split(chr(10)):
            P(f"  {ln}")
        P("  " + TILDE)
    else:
        P("  [WARN] Context string is EMPTY. No KB content will reach the LLM.")
    P()

    P(SEP)
    P("  DIAGNOSTIC SUMMARY")
    P(SEP)
    P()

    issues: list[str] = []
    if not all_entries:
        issues.append("NO KB entries exist for this tenant")
    if not embedded_entries:
        issues.append("NO entries have embeddings -- vector search is unavailable")
    elif len(unembedded_entries) > 0:
        issues.append(f"{len(unembedded_entries)} entries lack embeddings (partial coverage)")
    if not results:
        issues.append("Search returned 0 results")
    if results and all(r.get("rrf_score", 0) < MIN_RELEVANCE_SCORE for r in results):
        issues.append(f"ALL results below MIN_RELEVANCE_SCORE ({MIN_RELEVANCE_SCORE}) -- pipeline gets no context")
    if not ctx:
        issues.append("format_for_pipeline produced EMPTY context string")
    if ctx and len(ctx) < 100 and results:
        issues.append(f"Context string very short ({len(ctx)} chars) -- may be truncated aggressively")

    if issues:
        P("  ISSUES FOUND:")
        for issue in issues:
            P(f"    [!] {issue}")
    else:
        P("  No issues detected. Search and formatting appear healthy.")
    P()

    metrics = vectorizer.metrics
    summary = metrics.summary()
    P(f"  Search count:    {summary.get('search_count', 0)}")
    P(f"  Avg latency:     {summary.get('avg_latency_ms', 0):.0f}ms")
    P(f"  Avg results:     {summary.get('avg_result_count', 0):.1f}")
    P()

    await openai_client.close()
    P("  Done.")
    P()


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Diagnose Knowledge Retrieval quality for a tenant",
    )
    parser.add_argument("--tenant-id", default=DEFAULT_TENANT_ID,
                        help=f"Tenant ID (default: {DEFAULT_TENANT_ID})")
    parser.add_argument("--query", default=DEFAULT_QUERY,
                        help="Search query (default: What is your pricing?)")
    parser.add_argument("--top-k", type=int, default=10,
                        help="Number of results to retrieve (default: 10)")
    args = parser.parse_args()
    await run(tenant_id=args.tenant_id, query=args.query, top_k=args.top_k)


if __name__ == "__main__":
    asyncio.run(main())

