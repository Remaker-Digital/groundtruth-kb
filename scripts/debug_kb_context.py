#!/usr/bin/env python3
"""Debug script: see EXACTLY what knowledge context reaches GPT-4o.

Queries Cosmos DB for KB articles matching a pricing query,
formats them the same way format_for_pipeline() does,
then calls GPT-4o with different prompt strategies to find one that works.

Usage:
    python scripts/debug_kb_context.py
"""
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import asyncio
import json
import os
import sys
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local

load_env_local()

COSMOS_ENDPOINT = os.environ["COSMOS_DB_ENDPOINT"]
COSMOS_KEY = os.environ["COSMOS_DB_KEY"]
COSMOS_DB = os.environ.get("COSMOS_DB_DATABASE", "agentred")
TENANT_ID = "remaker-digital-001"

OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
OPENAI_KEY = os.environ["AZURE_OPENAI_API_KEY"]
OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")


async def get_kb_articles():
    """Fetch all active KB articles from Cosmos DB."""
    from azure.cosmos.aio import CosmosClient

    async with CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY) as client:
        db = client.get_database_client(COSMOS_DB)
        container = db.get_container_client("knowledge_bases")

        query = (
            "SELECT c.id, c.title, c.content, c.entry_type, c.is_active "
            "FROM c WHERE c.tenant_id = @tid AND c.is_active = true"
        )
        params = [{"name": "@tid", "value": TENANT_ID}]

        articles = []
        async for item in container.query_items(
            query=query,
            parameters=params,
            partition_key=TENANT_ID,
        ):
            articles.append(item)

    return articles


def simulate_keyword_search(articles, query):
    """Simulate the keyword scoring from pipeline.py fallback."""
    _STOP = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "can",
        "shall",
        "of",
        "in",
        "to",
        "for",
        "with",
        "on",
        "at",
        "by",
        "from",
        "and",
        "or",
        "but",
        "not",
        "no",
        "so",
        "if",
        "as",
        "it",
        "its",
        "this",
        "that",
        "what",
        "which",
        "who",
        "how",
        "your",
        "you",
        "my",
        "me",
        "i",
        "we",
        "our",
        "they",
        "their",
        "them",
        "he",
        "she",
        "his",
        "her",
    }
    query_words = {w for w in query.lower().split() if w not in _STOP and len(w) > 1}
    if not query_words:
        query_words = set(query.lower().split())

    scored = []
    for article in articles:
        title = (article.get("title") or "").lower()
        content = (article.get("content") or "").lower()
        title_words = {w for w in title.split() if w not in _STOP}
        content_words = set(content.split())
        title_overlap = len(query_words & title_words)
        content_overlap = len(query_words & content_words)
        score = (title_overlap * 3.0 + content_overlap) / max(len(query_words), 1)
        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:5]


def format_for_pipeline(results, max_chars=4000):
    """Exact replica of KnowledgeVectorizer.format_for_pipeline()."""
    context_parts = []
    total_chars = 0
    MIN_RELEVANCE_SCORE = 0.1

    for score, article in results:
        title = article.get("title", "Untitled")
        content = article.get("content", "")
        entry_type = article.get("entry_type", "")

        available = max_chars - total_chars - 50
        if available <= 0:
            break

        truncated = content[:available]
        if len(content) > available:
            truncated = truncated.rsplit(" ", 1)[0] + "..."

        part = f"[{entry_type.upper()}] {title}\n{truncated}"
        context_parts.append(part)
        total_chars += len(part)

    return "\n\n---\n\n".join(context_parts)


async def call_gpt4o(messages, label=""):
    """Call GPT-4o and print the response."""
    from openai import AsyncAzureOpenAI

    client = AsyncAzureOpenAI(
        azure_endpoint=OPENAI_ENDPOINT,
        api_key=OPENAI_KEY,
        api_version=OPENAI_API_VERSION,
    )

    print(f"\n{'=' * 60}")
    print(f"TEST: {label}")
    print(f"{'=' * 60}")
    print(f"Messages ({len(messages)}):")
    for m in messages:
        role = m["role"]
        content = m["content"]
        print(f"  [{role}] ({len(content)} chars)")
        if len(content) < 300:
            print(f"    {content}")
        else:
            print(f"    {content[:150]}...")
            print(f"    ...{content[-150:]}")

    resp = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=1024,
    )

    answer = resp.choices[0].message.content
    print(f"\nRESPONSE ({len(answer)} chars):")
    print(answer)
    print()
    await client.close()
    return answer


async def main():
    print("Fetching KB articles from Cosmos DB...")
    articles = await get_kb_articles()
    print(f"Found {len(articles)} active articles")

    query = "How much does Agent Red cost?"
    print(f"\nQuery: '{query}'")

    # Keyword search simulation
    scored = simulate_keyword_search(articles, query)
    print(f"\nTop {len(scored)} keyword matches:")
    for score, art in scored:
        print(
            f"  score={score:.2f}  [{art.get('entry_type', '')}] {art['title']} ({len(art.get('content', ''))} chars)"
        )

    # Format for pipeline
    knowledge_context = format_for_pipeline(scored)
    print(f"\n{'=' * 60}")
    print("FORMATTED KNOWLEDGE CONTEXT (this is what GPT-4o sees):")
    print(f"{'=' * 60}")
    print(knowledge_context)
    print(f"{'=' * 60}")
    print(f"Total length: {len(knowledge_context)} chars")

    # Now test different prompt strategies with GPT-4o
    # -----------------------------------------------

    # Strategy 1: Current approach (knowledge in system message)
    system_base = (
        "You are a friendly and knowledgeable customer service agent. "
        "Your goal is to make every customer feel welcomed, heard, and helped."
    )

    system_with_kb = (
        f"{system_base}\n\n"
        "═══════════════════════════════════════════\n"
        "VERIFIED KNOWLEDGE BASE — USE THIS DATA\n"
        "═══════════════════════════════════════════\n"
        "The articles below contain VERIFIED, ACCURATE information.\n"
        "You MUST incorporate specific details from them into your "
        "response: exact dollar amounts, tier names, feature lists, "
        "quantities, percentages, and policy terms.\n"
        "Include ALL relevant items — if there are multiple tiers, "
        "list ALL of them. If there are multiple features, list ALL.\n"
        "NEVER say 'check our website' or 'contact sales' when the "
        "answer is right here.\n\n"
        f"{knowledge_context}\n\n"
        "═══════════════════════════════════════════\n"
        "END OF KNOWLEDGE BASE\n"
        "═══════════════════════════════════════════"
    )

    await call_gpt4o(
        [
            {"role": "system", "content": system_with_kb},
            {"role": "user", "content": query},
        ],
        "Strategy 1: KB in system message (current v1.13.9)",
    )

    # Strategy 2: KB in user message
    user_with_kb = (
        f"Customer question: {query}\n\n"
        "Here is the relevant knowledge base data — use ALL the specific "
        "details from these articles in your response:\n\n"
        f"{knowledge_context}"
    )
    await call_gpt4o(
        [
            {"role": "system", "content": system_base},
            {"role": "user", "content": user_with_kb},
        ],
        "Strategy 2: KB in user message",
    )

    # Strategy 3: Only the most relevant article (avoid confusion from many articles)
    if scored:
        best_score, best_article = scored[0]
        single_context = (
            f"[{best_article.get('entry_type', '').upper()}] {best_article['title']}\n{best_article['content']}"
        )
        system_single = (
            f"{system_base}\n\n"
            "KNOWLEDGE BASE:\n"
            f"{single_context}\n\n"
            "Use the specific details from this knowledge to answer the customer."
        )
        await call_gpt4o(
            [
                {"role": "system", "content": system_single},
                {"role": "user", "content": query},
            ],
            "Strategy 3: Single best article only",
        )

    # Strategy 4: Structured markdown with explicit enumeration
    # Manually build a clean pricing table from the raw articles
    system_structured = f"{system_base}\n\nPRODUCT PRICING (verified, accurate data):\n\n"
    # Find pricing-related articles
    pricing_articles = [
        a for s, a in scored if "pric" in a.get("title", "").lower() or "cost" in a.get("title", "").lower()
    ]
    if pricing_articles:
        for art in pricing_articles:
            system_structured += f"---\n{art['title']}:\n{art['content']}\n\n"
    else:
        system_structured += f"---\n{knowledge_context}\n"

    system_structured += "\nUse ALL the pricing details above when answering."

    await call_gpt4o(
        [
            {"role": "system", "content": system_structured},
            {"role": "user", "content": query},
        ],
        "Strategy 4: Pricing-focused articles with header",
    )

    # Strategy 5: Direct instruction + knowledge as assistant pretend
    await call_gpt4o(
        [
            {"role": "system", "content": system_base},
            {
                "role": "user",
                "content": (
                    "Before answering, review this knowledge base data:\n\n"
                    f"{knowledge_context}\n\n"
                    "---\n\n"
                    f"Now answer this customer question using ALL the specific details "
                    f"from the knowledge above: {query}"
                ),
            },
        ],
        "Strategy 5: KB as user context with explicit 'review first' instruction",
    )


if __name__ == "__main__":
    asyncio.run(main())
