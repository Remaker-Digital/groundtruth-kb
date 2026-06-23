"""SPEC-1742 How It Works knowledge retrieval technical detail coverage.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.local_env

ROOT = Path(__file__).resolve().parents[2]
HOW_IT_WORKS = ROOT / "docs-site" / "docs" / "getting-started" / "how-it-works.md"


def _knowledge_retrieval_section() -> str:
    markdown = HOW_IT_WORKS.read_text(encoding="utf-8")
    heading = "### Knowledge retrieval technical detail"
    start = markdown.find(heading)
    assert start != -1, "How It Works must include the knowledge retrieval technical detail section"

    section = markdown[start:]
    end_match = re.search(r"^\*\*5\. Response Generator", section, flags=re.MULTILINE)
    assert end_match, "Knowledge retrieval technical detail section must precede response generation step"
    return section[: end_match.start()]


def _normalized_section() -> str:
    return (
        _knowledge_retrieval_section()
        .replace("**", "")
        .replace("\u00d7", "x")
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )


def test_embedding_and_indexing_details_are_documented() -> None:
    section = _normalized_section()

    expected_terms = [
        "text-embedding-3-large",
        "3,072",
        "Cosine distance",
        "Cosmos DB DiskANN",
        "float32",
        "entry type",
        "title",
        "tags",
        "content",
        "one embedding",
        "not chunked",
        "SHA-256",
        "skips re-embedding",
    ]

    for term in expected_terms:
        assert term in section


def test_hybrid_search_rrf_and_weighting_are_documented() -> None:
    section = _normalized_section()

    expected_terms = [
        "hybrid strategy",
        "Vector similarity",
        "BM25 keyword score",
        "Reciprocal Rank Fusion",
        "Weight: 0.7 (70%)",
        "Weight: 0.3 (30%)",
        "70%",
        "30%",
        "weight / (k + rank)",
        "k=60",
        "0-1 range",
    ]

    for term in expected_terms:
        assert term in section


def test_retrieval_parameters_are_documented() -> None:
    section = _normalized_section()

    expected_rows = [
        "| Default results returned | 5 |",
        "| Maximum results | 20 |",
        "| Candidate pool | 3x top-k |",
        "| Minimum relevance score | 0.1 |",
        "| High relevance threshold | 0.7 |",
        "| Maximum context budget | 4,000 characters |",
        "| BM25 k1 | 1.5 |",
        "| BM25 b | 0.75 |",
    ]

    for row in expected_rows:
        assert row in section


def test_kb_guidance_caching_and_fallback_chain_are_documented() -> None:
    section = _normalized_section()

    guidance_terms = [
        "clear, specific titles",
        "exact terms your customers use",
        "focused on one topic",
        "Tags help retrieval",
    ]
    cache_terms = [
        "Exact query cache",
        "Semantic cache",
        "Embedding cache",
    ]

    for term in guidance_terms + cache_terms:
        assert term in section

    fallback_terms = [
        "Hybrid (default)",
        "Vector-only fallback",
        "BM25-only fallback",
        "Empty result",
    ]
    positions = [section.index(term) for term in fallback_terms]
    assert positions == sorted(positions)
