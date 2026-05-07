# RAG Configuration Management Enhancements Proposal
Date: 2026-02-07
Owner: Product + Engineering
Status: Proposal

This proposal benchmarks Agent Red's current RAG administration capabilities against
leading SaaS systems and outlines concrete enhancements to reach best-in-class
configurability for merchants.

---

## 1. Executive Summary

Agent Red already supports knowledge base CRUD, file/URL import, embedding, and
staleness verification. The gaps versus leading systems center on administrative
control of sources, ingestion cadence, targeting, and retrieval behavior. This
proposal recommends adding source-level governance, audience targeting, connector
management, and retrieval tuning with safe defaults.

---

## 2. Current Capabilities (Agent Red)

**Admin UI (Knowledge Base)**
- Create, edit, delete, and filter articles by category and status.
- Upload files (PDF, DOCX, CSV, TXT) and import from URL.
- Export CSV.
- Staleness summary, per-article verification, and freshness badges.

**Admin API**
- List/filter entries by type, language, active status, and title.
- Auto-embedding on create/update.
- Chunked import and batch embedding.
- Staleness metrics and verify endpoint.

**What’s missing**
- Source-level controls (sync cadence, enable/disable, audience scoping).
- Connector support (Help Center sync, CRM/ERP, cloud drives).
- Retrieval tuning (top-k, hybrid search weighting, recency boost).
- Content guidance rules (force or prefer sources for certain intents).
- Admin visibility into which sources drive answers.

---

## 3. Benchmark: Common RAG Admin Features in Leading Systems

**Salesforce Agentforce (Data Library)**
- Admins can select Salesforce knowledge articles or upload files into an
  Agentforce Data Library for RAG.
- Supports additional sources when configuring RAG manually, including
  object fields, related files, and cloud storage. citeturn1search1

**Intercom Fin**
- Content sources include internal articles and synced sources.
- Website sources can be synced and managed with per-source enable/disable,
  audience targeting, and last-sync visibility. citeturn1search5
- Content guidance allows admins to force or prefer specific sources for
  certain question types. citeturn1search0
- Audiences can be applied to content and guidance for precise targeting. citeturn1search2

**Microsoft Copilot Studio**
- Knowledge sources can include public URLs, SharePoint sites/files, Teams
  chats, and uploaded files, with limits and readiness states. citeturn0search1
- File upload is supported as a first-class knowledge source. citeturn0search2

---

## 4. Gap Analysis (Agent Red vs. Benchmarks)

1. **Source management**
   - Missing: per-source enable/disable, last-sync, audience targeting.
   - Benchmarks: Intercom provides per-source status, sync, and audience. citeturn1search5turn1search2

2. **Content guidance**
   - Missing: rules to prefer or require sources for specific intent types.
   - Benchmarks: Intercom content guidance is explicit and configurable. citeturn1search0

3. **Connector ecosystem**
   - Missing: native connectors to help centers, cloud drives, CRM/ERP.
   - Benchmarks: Copilot Studio supports SharePoint and public websites. citeturn0search1turn0search2

4. **Ingestion cadence**
   - Missing: scheduled re-sync or crawl intervals.
   - Benchmarks: Intercom provides managed sync lifecycle for website sources. citeturn1search5

5. **Retrieval tuning**
   - Missing: admin controls for top-k, hybrid weighting, recency boosting,
     min-score thresholds, and cite-on-answer requirements.
   - Benchmarks: Not always surfaced to SMBs, but enterprise systems expose
     advanced controls or guided defaults.

6. **Explainability and governance**
   - Missing: per-answer source usage and coverage metrics in admin views.
   - Benchmarks: Intercom surfaces source usage and content involvement. citeturn1search5

---

## 5. Proposed Enhancements

### Phase 1 — Source Governance (Foundational)
Add source-level objects and management UI:
- Enable/disable source.
- Last sync timestamp and status.
- Audience targeting for sources.
- Manual re-sync and health checks.

### Phase 2 — Content Guidance Rules
Add rules that bind question types or intents to preferred sources:
- “If question matches refund/policy, prefer policy sources.”
- “If question matches inventory, prefer product sources.”

### Phase 3 — Connector Expansion
Add native connectors with scheduled sync:
- Shopify store policies, product catalogs, and FAQ pages.
- Public website crawler with page inclusion/exclusion.
- Cloud storage (Drive, SharePoint, S3) with file sync.

### Phase 4 — Retrieval Tuning (Advanced)
Expose safe controls:
- top-k results
- hybrid scoring weights (BM25 vs embeddings)
- recency boosting
- minimum relevance threshold
- “cite sources in response” toggle

### Phase 5 — Observability and QA
Add admin analytics:
- Source contribution metrics
- Stale content alerts
- Coverage gaps (frequent unanswered intents)

---

## 6. Concrete Examples to Emulate

- **Intercom content guidance**: rules that direct the AI to specific sources for
  specific topics. citeturn1search0
- **Intercom source management**: per-website content visibility, sync status,
  and audience targeting. citeturn1search5turn1search2
- **Copilot Studio knowledge sources**: add URL, SharePoint, files, and observe
  readiness state. citeturn0search1turn0search2
- **Agentforce Data Library**: upload files and select knowledge articles for
  rapid RAG setup, with deeper customization available through manual pipelines. citeturn1search1

---

## 7. Implementation Map (Files)

**Backend**
- `src/multi_tenant/cosmos_schema.py`
- `src/multi_tenant/admin_knowledge_api.py`
- `src/multi_tenant/knowledge_vectorizer.py`
- `src/multi_tenant/document_parser.py`

**Admin UI**
- `admin/shared/KnowledgeBaseManager.tsx`
- `admin/shared/hooks/*`

**New modules**
- `src/multi_tenant/source_registry.py` (proposed)
- `src/multi_tenant/rag_rules.py` (proposed)

---

## 8. Risks and Mitigations

**Risk:** Overwhelming merchants with advanced options.  
**Mitigation:** Tiered UI with “Basic” and “Advanced” tabs and strong defaults.

**Risk:** Sync and connector failures create stale content.  
**Mitigation:** Source health monitoring, retry logic, and “last good” state.

**Risk:** Retrieval tuning degrades answer quality if misconfigured.  
**Mitigation:** Guardrails and recommended presets with rollback.

---

## 9. Deliverables

- Source management UI and API
- Content guidance rules
- Connector integration roadmap
- Retrieval tuning controls
- Analytics for source usage and content freshness

---

## 10. Versioned Requirements

### v1.1 (Foundational Governance)
- Source objects with enable/disable, last sync, and health status.
- Manual re-sync trigger and source health panel.
- Audience targeting at the source level (basic segmentation).
- Minimal admin API for source CRUD and sync status.

### v1.2 (Guidance + Basic Connectors)
- Content guidance rules (intent → source preference).
- Public URL source with inclusion/exclusion patterns.
- Shopify knowledge sync for policies and FAQs.

### v1.3 (Retrieval Tuning + Observability)
- Admin controls for `top_k`, min relevance threshold, and recency boost.
- Hybrid search weighting (BM25 vs embeddings).
- Source contribution analytics and coverage gap alerts.

### v1.4 (Advanced Connectors)
- Cloud storage (Drive/SharePoint) connectors.
- Scheduled sync cadence and change detection.
- Versioned source snapshots with rollback.

---

## 11. Phased Backlog with LOE Estimates

LOE scale: S (1–2 days), M (3–5 days), L (6–10 days), XL (2+ weeks).

### Phase 1 — Source Governance (v1.1)
- Define source schema + storage (`source_registry`) — M  
- Admin API: CRUD + status endpoints — M  
- Admin UI: sources list + detail panel — M  
- Manual re-sync trigger — S  
- Health/status background task — M  

### Phase 2 — Content Guidance + Basic Connectors (v1.2)
- Guidance rules schema + evaluator — M  
- Admin UI for rules (intent → source mapping) — M  
- Public URL source with include/exclude — M  
- Shopify policy/FAQ sync — L  

### Phase 3 — Retrieval Tuning + Observability (v1.3)
- Retrieval parameters in config + validation — S  
- Hybrid weighting and min-score thresholds — M  
- Source contribution metrics — M  
- Coverage gap reporting — M  

### Phase 4 — Advanced Connectors + Versioning (v1.4)
- Drive/SharePoint connectors — XL
- Scheduled sync + change detection — L
- Source snapshot versioning + rollback — L

---

## 12. Release 1.1 Re-evaluation Notes

**Date added:** 2026-02-07
**Context:** Phase 1 items (retrieval tuning, intent routing, cite sources) implemented
in Agent Red 1.0. The following notes capture decisions deferred to the v1.1 content
plan review and the rationale for deferral.

### Items Implemented in 1.0 (from this proposal)
- Retrieval tuning exposure: `retrieval_top_k`, `retrieval_vector_weight`,
  `retrieval_bm25_weight`, `retrieval_min_score` added to PreferencesDocument and
  wired through the pipeline. Admin UI controls with guardrails.
- Intent-to-source routing: `intent_source_mapping` in tenant config. Pipeline
  passes resolved intent as `entry_type` filter to `hybrid_search()`.
- Cite sources toggle: `cite_sources_in_response` boolean in tenant config. When
  enabled, source titles appended to AI responses.

### Items Deferred to v1.1 Review — Evaluate with Production Data

**Source Governance (Proposal Phase 1)**
- `KnowledgeSourceDocument` entity grouping KB entries by import batch. Deferred
  because launch merchants will have small KBs (10-50 entries) where per-entry
  management is sufficient. Re-evaluate when any merchant exceeds 200 entries or
  uses 3+ source types.
- Source enable/disable at aggregate level. Currently `is_active` per entry is
  sufficient. Source-level toggle adds value only when merchants import large
  batches and want to disable an entire import at once.
- Source health monitoring background task. Deferred — staleness_service.py
  already covers content freshness. Source-level health adds value only when
  connectors (URL sync, Shopify sync) are implemented.

**Audience Targeting (Proposal Phase 1)**
- Per-source or per-entry audience tags. Deferred because it requires a customer
  segmentation system (how are customers classified?). Persistent Customer Memory
  Layer 3 (pattern extraction) provides the data foundation, but no segment
  taxonomy exists yet. Re-evaluate after 3+ months of production conversation data
  reveals natural customer segments.
- Prerequisite: define segment taxonomy (new vs returning, purchase tier, product
  interest). This is a product design decision, not an engineering one.

**Content Guidance Rules (Proposal Phase 2)**
- Beyond simple intent→entry_type routing (implemented), richer rules like
  "prefer policy sources for refund questions" or "require product sources for
  inventory queries." Deferred because the simple mapping covers 80% of the value.
  Re-evaluate if merchants report answer quality issues due to wrong source
  selection.

**Connector Expansion (Proposal Phase 3)**
- Shopify policy/FAQ auto-sync: highest priority connector. Requires Shopify
  Admin API (pages, metaobjects, or blog articles). Evaluate merchant demand
  before building — manual upload may be sufficient for launch.
- Public URL crawler: moderate demand signal expected. Watch for merchants asking
  "can I point it at my help center?" as the trigger.
- Cloud storage (Drive/SharePoint/S3): Enterprise tier only. Do not build until
  Enterprise subscribers request it.

**Coverage Gap Detection (Proposal Phase 5)**
- Tracking queries with zero or low-relevance KB results. Valuable for merchant
  content strategy. Implementation path: log retrieval scores in pipeline, aggregate
  low-score queries into "unanswered topics" report. Re-evaluate after production
  pipeline generates retrieval logs (requires live conversations).

**Source Snapshot Versioning + Rollback**
- Over-engineered for current scale. `content_hash` drift detection already
  identifies changes. Full versioning with rollback is a v2.0 feature. Do not
  build unless a merchant reports data loss from a bad KB update.

### Metrics to Watch (triggers for v1.1 implementation)
- Merchant KB size > 200 entries (triggers source governance)
- Merchant uses 3+ source types (triggers source entity)
- Customer segments emerge from Layer 3 data (triggers audience targeting)
- Merchants report wrong-source answers (triggers content guidance rules)
- "Can I sync my help center?" support requests (triggers URL crawler)
- Enterprise subscriber requests cloud storage (triggers connectors)
- Retrieval precision < 80% in production logs (triggers coverage gap detection)

