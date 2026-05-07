# RAG Infrastructure Gap Analysis

> **Document Purpose:** This document captures the comprehensive gap analysis of Agent Red's RAG (Retrieval-Augmented Generation) infrastructure conducted on 2026-02-05, comparing current implementation against industry best practices and competitors.

> **Last Updated:** 2026-02-05
> **Version:** 1.0.0
> **Author:** Architecture Review Session

---

## Executive Summary

Agent Red has **two RAG-enabled systems** with significantly different maturity levels:

1. **Persistent Customer Memory (Layer 2)** — Correctly implemented with vector embeddings, DiskANN indexing, and semantic search
2. **Merchant Knowledge Base** — Basic CRUD with keyword search only; **missing enterprise RAG capabilities**

This document details the gaps and provides concrete work items (WI #209-225) to bring the Knowledge Base to production-grade RAG standards.

---

## Current Implementation Status

### What EXISTS (Conversation Memory — Layer 2) ✅

| Feature | Implementation | File |
|---------|---------------|------|
| Post-conversation vectorization | text-embedding-3-large, 3072d | conversation_vectorizer.py |
| Vector storage | Cosmos DB with DiskANN index | cosmos_schema.py |
| Semantic search | Top-K with tier-gated depth | conversation_vectorizer.py |
| Prompt compression | ~300 token budget | conversation_vectorizer.py |
| Consent gating | GDPR-compliant opt-in | gdpr_services.py |
| Chunking | 200-300 tokens with 30-token overlap | conversation_vectorizer.py |

### What is MISSING (Merchant Knowledge Base) ❌

| Feature | Current State | Required State |
|---------|--------------|----------------|
| Vector embeddings | None | Embed all KB entries |
| Semantic search | Keyword matching (word-in-string) | Cosine similarity search |
| Document upload | Manual text entry only | PDF, DOCX, CSV, URL |
| Hybrid retrieval | None | BM25 + vector with RRF |
| Staleness tracking | None | `last_verified_at`, staleness score |
| Retrieval monitoring | None | Precision, relevance metrics |
| Bulk operations | None | CSV import/export |
| Category/Status UI | Schema exists, no UI | Full management UI |

---

## Document Inconsistencies Identified

| Document | Claim | Actual | Resolution |
|----------|-------|--------|------------|
| PRODUCT-FEATURES-RAG.md line 525 | "1536-dimension embeddings" | 3072 dimensions | Update document |
| PRODUCT-FEATURES-RAG.md line 207 | "semantic embeddings...vector similarity search" for KB | Keyword matching | Implement vector search |
| PRODUCT-FEATURES-RAG.md line 466 | "Hybrid search (BM25 + dense vectors)" | Not implemented | Implement hybrid retrieval |
| PRODUCT-FEATURES-RAG.md line 221 | "Index freshness: < 1 hour" | No freshness tracking | Implement staleness service |

---

## Competitive Research Summary

### Salesforce Agentforce
- **Data sources**: Knowledge articles, PDF (≤100MB), HTML (≤4MB), TXT, cloud storage
- **Vectorization**: E5-Large-V2 (multilingual), auto-configured 512-token chunks
- **Hybrid search**: Semantic + keyword enabled by default
- **Parsing**: LLM-based (semantic) or Docling (structural)

### Intercom Fin AI
- **File types**: PDF, DOCX — max 100MB, 100 documents per workspace
- **Processing time**: 10 minutes to availability
- **Image handling**: Extracted from PDFs for visual references

### Tidio Lyro
- **Import methods**: CSV upload, URL scraping, conversation history learning
- **Auto-learning**: Suggests new Q&A pairs from chat history

### Zendesk AI
- **Staleness detection**: Automatically surfaces outdated content
- **Recent acquisition**: Unleash (enterprise AI search with permission-based RAG)

### Industry Best Practices (2026)
Source: Redis RAG at Scale

- **Freshness**: Daily re-indexing for dynamic content, hourly for real-time
- **Staleness**: Monitor embedding drift via cosine similarity distribution
- **Hybrid retrieval**: Vector + BM25 with Reciprocal Rank Fusion (1-9% recall improvement)
- **Semantic caching**: 68.8% reduction in LLM API calls
- **Chunking**: 256-512 tokens for factoid queries

---

## Work Items (WI #209-225)

### P0: Knowledge Base Vectorization (WI #209-213)

**WI #209: KB Vector Embedding Schema**
- Add `embedding: list[float] | None` to KnowledgeBaseDocument
- Add `embedding_model: str | None` field
- Add `embedded_at: str | None` timestamp
- Add DiskANN vector index configuration
- **Estimate: 1 day**

**WI #210: KB Embedding Pipeline**
- Create `knowledge_vectorizer.py` module
- Embed on create/update (async background job)
- Batch embedding for bulk imports
- Track embedding model version
- **Estimate: 2 days**

**WI #211: KB Vector Search**
- Replace keyword matching in `_call_knowledge_retrieval_direct()`
- Implement cosine similarity search via Cosmos DB
- Relevance score normalization
- **Estimate: 2 days**

**WI #212: Hybrid Retrieval**
- Add BM25 keyword scoring
- Implement Reciprocal Rank Fusion (RRF)
- Configurable alpha weight
- **Estimate: 2 days**

**WI #213: Retrieval Quality Monitoring**
- Log retrieval events with scores
- Track click-through on KB sources
- Dashboard for retrieval precision
- **Estimate: 2 days**

### P0: Document Upload & Processing (WI #214-218)

**WI #214: File Upload API**
- `POST /api/admin/knowledge/upload` endpoint
- Multipart/form-data support
- PDF, DOCX, CSV, TXT file types
- Size limits (50MB PDF, 4MB text)
- **Estimate: 1 day**

**WI #215: Document Parsing Pipeline**
- Create `document_parser.py` module
- PDF extraction (PyPDF2/pdfplumber)
- DOCX parsing (python-docx)
- CSV Q&A pair import
- HTML/URL scraping (BeautifulSoup + httpx)
- **Estimate: 3 days**

**WI #216: Document Chunking**
- Page-level chunking (256-512 tokens)
- Respect paragraph boundaries
- Preserve table structure
- Configurable overlap
- **Estimate: 2 days**

**WI #217: Bulk Import/Export**
- CSV export of all KB entries
- CSV import with validation
- Progress tracking
- **Estimate: 1 day**

**WI #218: Admin UI for Upload**
- File dropzone in KnowledgeBaseManager.tsx
- Upload progress indicator
- Processing status display
- **Estimate: 2 days**

### P1: Staleness & Freshness Management (WI #219-222)

**WI #219: Staleness Schema**
- Add `last_verified_at: str | None`
- Add `staleness_score: float | None`
- Add `auto_refresh_enabled: bool`
- **Estimate: 0.5 days**

**WI #220: Staleness Detection Service**
- Create `staleness_service.py`
- Compute staleness from age + feedback
- Configurable thresholds per entry type
- **Estimate: 1.5 days**

**WI #221: Refresh Prompts UI**
- Badge stale entries in table
- "Mark as verified" action
- Suggested refresh schedule
- **Estimate: 1 day**

**WI #222: Automatic Re-embedding**
- Scheduled job for stale entries
- Re-embed on content change
- Track embedding model versions
- Quarterly drift prevention
- **Estimate: 1.5 days**

### P1: Semantic Caching (WI #223-225)

**WI #223: Query Embedding Cache**
- Cache query embeddings
- TTL-based expiration
- **Estimate: 1 day**

**WI #224: Semantic Response Cache**
- Cache similar queries by vector similarity
- Configurable threshold (0.90 default)
- Cache hit logging
- **Estimate: 2 days**

**WI #225: Cache Monitoring Dashboard**
- Hit rate metrics
- Cost savings estimate
- Threshold tuning UI
- **Estimate: 1 day**

---

## Implementation Priority

| Priority | Work Items | Total Effort | Description |
|----------|------------|--------------|-------------|
| **P0** | WI #209-218 | 18 days | KB vectorization + document upload |
| **P1** | WI #219-225 | 8.5 days | Staleness + caching |
| **Total** | 17 items | 26.5 days | Full RAG infrastructure |

---

## Architecture Decision

**Decision RAG-1: KB Vector Search Implementation**

- **Status**: Approved (2026-02-05)
- **Context**: Knowledge Base retrieval uses naive keyword matching while Persistent Customer Memory (Layer 2) correctly uses vector search
- **Decision**: Extend the Layer 2 vectorization pattern to the Knowledge Base
- **Rationale**: Reuse proven architecture (conversation_vectorizer.py) for consistency and reduced implementation risk
- **Implications**:
  - KnowledgeBaseDocument gains `embedding` field
  - Collection needs DiskANN vector index
  - Pipeline.py KB retrieval switches from keyword to vector
  - Background embedding job required for existing entries

---

## References

- [Salesforce Agentforce RAG Best Practices](https://www.salesforce.com/agentforce/agentforce-and-rag/)
- [Redis RAG at Scale](https://redis.io/blog/rag-at-scale/)
- [Intercom Document Upload](https://www.intercom.com/help/en/articles/8124534-upload-and-manage-documents)
- [Zendesk AI Knowledge Base Guide](https://www.zendesk.com/service/help-center/ai-knowledge-base/)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
