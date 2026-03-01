#!/usr/bin/env python3
"""
Record specifications and work items for S126.

Three feature areas:
1. Secret Posture defects (SPEC-1568..1569, WI-0882..0883)
2. Co-Pilot Knowledge Management UI (SPEC-1570..1580, WI-0884..0890)
3. Pipeline Observatory (SPEC-1581..1592, WI-0891..0898)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")

from db import KnowledgeDB

db = KnowledgeDB()

# ============================================================================
# 1. SECRET POSTURE DEFECTS
# ============================================================================

print("\n=== SECRET POSTURE DEFECTS ===\n")

# SPEC-1568: Secret Posture must aggregate secrets from all storage locations
db.insert_spec(
    id="SPEC-1568",
    title="Secret Posture aggregates secrets from all storage locations",
    description=(
        "The Secret Posture page must report secrets from all storage locations, "
        "not only Key Vault tenant-prefixed secrets. Sources: (1) Key Vault secrets "
        "matching tenant-{tenant_id}-* prefix, (2) Cosmos DB TenantDocument fields "
        "api_key_hash and widget_key_hash (presence indicates API key / widget key exist), "
        "(3) TOTP seeds stored as user-{member_id}-totp-seed in Key Vault, resolved "
        "via team_members collection lookup for each tenant. The hasApiKey flag must "
        "be true when api_key_hash is non-null. The hasShopify flag must be true when "
        "shopify_shop_domain is non-null. secretCount must include all sources."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "api_key_hash",
            "description": "Secret posture checks Cosmos DB api_key_hash field",
        },
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "widget_key_hash",
            "description": "Secret posture checks Cosmos DB widget_key_hash field",
        },
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "shopify_shop_domain",
            "description": "Secret posture checks shopify_shop_domain for hasShopify",
        },
    ],
    changed_by="S126",
    change_reason="Secret Posture page shows empty data for all tenants because it only queries Key Vault tenant-prefixed secrets",
)
print("  SPEC-1568: Secret Posture aggregates all storage locations")

# SPEC-1569: Provider Console tenant tables must show human-readable identification
db.insert_spec(
    id="SPEC-1569",
    title="Provider Console tenant tables show human-readable tenant identification",
    description=(
        "All Provider Console pages that display per-tenant tables must show "
        "human-readable tenant identification instead of raw UUIDs. Primary display: "
        "customer_email from TenantDocument (superadmin email for that tenancy). "
        "Secondary display: shopify_shop_domain if available, or tenant_id as fallback. "
        "The raw tenant_id UUID must be available as a tooltip (mouse-over) or in an "
        "expandable accordion row detail, not as the primary identifier. This applies to: "
        "Secret Posture, Tenant Directory, Compliance Dashboard, Cost Analytics, "
        "Billing Health, and any future per-tenant tables. The API response must include "
        "customerEmail and shopifyShopDomain fields alongside tenantId."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "admin/provider/pages/SecretPosture.tsx",
            "pattern": "customerEmail",
            "description": "Secret Posture displays customer email",
        },
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "customer_email",
            "min_count": 2,
            "description": "Superadmin API includes customer_email in secret posture response",
        },
    ],
    changed_by="S126",
    change_reason="Owner feedback: Tenant ID UUIDs are insufficient to identify tenants in Provider Console tables",
)
print("  SPEC-1569: Human-readable tenant identification in Provider Console")

# Work items for Secret Posture
db.insert_work_item(
    id="WI-0882",
    title="Secret Posture: aggregate secrets from Key Vault + Cosmos DB + TOTP seeds",
    description=(
        "Fix the secret_posture endpoint to aggregate secrets from all three sources: "
        "(1) Key Vault tenant-{tid}-* secrets (existing), "
        "(2) Cosmos DB TenantDocument api_key_hash/widget_key_hash presence, "
        "(3) TOTP seeds via team_members lookup per tenant. "
        "Update hasShopify to also check shopify_shop_domain on TenantDocument. "
        "Update hasApiKey to also check api_key_hash presence."
    ),
    origin="defect",
    component="provider_administration",
    resolution_status="open",
    source_spec_id="SPEC-1568",
    changed_by="S126",
    change_reason="Secret Posture page shows 0 secrets for all tenants in production",
)
print("  WI-0882: Fix secret posture data aggregation")

db.insert_work_item(
    id="WI-0883",
    title="Provider Console: human-readable tenant identification across all pages",
    description=(
        "Add customerEmail and shopifyShopDomain to TenantSecretInfo response model. "
        "Update SecretPosture.tsx to display email as primary identifier with tenant_id "
        "as tooltip. Apply same pattern to Tenant Directory, Compliance Dashboard, "
        "Cost Analytics, and Billing Health pages."
    ),
    origin="defect",
    component="provider_administration",
    resolution_status="open",
    source_spec_id="SPEC-1569",
    changed_by="S126",
    change_reason="Owner feedback: raw UUIDs insufficient for tenant identification",
)
print("  WI-0883: Human-readable tenant identification")

# ============================================================================
# 2. CO-PILOT KNOWLEDGE MANAGEMENT UI
# ============================================================================

print("\n=== CO-PILOT KNOWLEDGE MANAGEMENT UI ===\n")

db.insert_spec(
    id="SPEC-1570",
    title="Co-Pilot Knowledge Management: document CRUD API endpoints",
    description=(
        "The superadmin API must expose CRUD endpoints for admin documentation: "
        "GET /api/superadmin/copilot-docs (list, filterable by category/active/embedded), "
        "GET /api/superadmin/copilot-docs/{doc_id} (single document with full content), "
        "POST /api/superadmin/copilot-docs (create from manual entry or URL), "
        "PUT /api/superadmin/copilot-docs/{doc_id} (update, triggers re-embedding if hash changes), "
        "DELETE /api/superadmin/copilot-docs/{doc_id} (soft-delete via is_active=false). "
        "All endpoints require SUPERADMIN role."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "copilot-docs",
            "min_count": 3,
            "description": "Superadmin API has copilot-docs endpoints",
        },
    ],
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1570: Document CRUD API endpoints")

db.insert_spec(
    id="SPEC-1571",
    title="Co-Pilot Knowledge Management: batch ingestion from docs-site",
    description=(
        "POST /api/superadmin/copilot-docs/ingest must scan docs-site/docs/admin-guide/*.md, "
        "parse markdown by section headings, compute SHA-256 content hash, embed via "
        "text-embedding-3-large (3072 dims), and upsert to admin_documentation_vectors. "
        "Must support incremental ingestion: skip documents whose content_hash matches "
        "the existing document. Returns count of new, updated, unchanged, and errored documents."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "copilot-docs/ingest",
            "description": "Ingestion endpoint exists",
        },
    ],
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1571: Batch ingestion from docs-site")

db.insert_spec(
    id="SPEC-1572",
    title="Co-Pilot Knowledge Management: URL import source",
    description=(
        "The document creation endpoint must accept a source_url parameter. When provided, "
        "the system fetches the URL, converts HTML to markdown, stores the content with "
        "source_file set to the URL, and embeds it. URL sources are tracked separately "
        "from docs-site sources for re-scan scheduling."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1572: URL import source")

db.insert_spec(
    id="SPEC-1573",
    title="Co-Pilot Knowledge Management: re-embedding trigger",
    description=(
        "POST /api/superadmin/copilot-docs/re-embed must trigger re-embedding for "
        "documents whose content has changed (stale hash) or for all documents when "
        "force=true. Must report: documents re-embedded, documents skipped (unchanged), "
        "errors. Uses text-embedding-3-large with 3072 dimensions."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "re-embed",
            "description": "Re-embedding endpoint exists",
        },
    ],
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1573: Re-embedding trigger")

db.insert_spec(
    id="SPEC-1574",
    title="Co-Pilot Knowledge Management: collection statistics endpoint",
    description=(
        "GET /api/superadmin/copilot-docs/stats must return: total document count, "
        "count by category, count with embeddings vs without, count of stale documents "
        "(content changed since last embedding), oldest and newest embedded_at timestamps, "
        "total active vs inactive documents."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "copilot-docs/stats",
            "description": "Stats endpoint exists",
        },
    ],
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1574: Collection statistics endpoint")

db.insert_spec(
    id="SPEC-1575",
    title="Co-Pilot Knowledge Management: scan scheduling",
    description=(
        "The system must support configurable scan schedules for automatic re-ingestion: "
        "manual-only, daily, or weekly. Schedule configuration is stored as a platform-scoped "
        "document. Manual trigger available via UI button. Schedule includes: frequency, "
        "scan scope (docs-site, registered URLs, or both), last scan timestamp, next scan "
        "timestamp, and scan history (last 10 results)."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1575: Scan scheduling")

db.insert_spec(
    id="SPEC-1576",
    title="Co-Pilot Knowledge Management: configurable retrieval parameters",
    description=(
        "The CoPilotAgent must read retrieval parameters from a CopilotConfig document "
        "instead of hardcoded DEFAULT_* constants. Configurable parameters: "
        "vector_weight (default 0.7), bm25_weight (default 0.3), rrf_k (default 60), "
        "top_k (default 5), min_score (default 0.1). Changes take effect on next query "
        "without restart."
    ),
    status="specified",
    section="agent_implementation",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/agents/co_pilot.py",
            "pattern": "CopilotConfig\\|copilot_config\\|config\\.vector_weight",
            "description": "CoPilotAgent reads from config document",
        },
    ],
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1576: Configurable retrieval parameters")

db.insert_spec(
    id="SPEC-1577",
    title="Co-Pilot Knowledge Management: test query endpoint",
    description=(
        "POST /api/superadmin/copilot-docs/test-query must accept a query string, "
        "run the full hybrid retrieval pipeline (vector + BM25 + RRF), and return "
        "the top-k results with scores, categories, titles, and content excerpts. "
        "Used for validating retrieval parameter tuning without starting a conversation."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "test-query",
            "description": "Test query endpoint exists",
        },
    ],
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1577: Test query endpoint")

db.insert_spec(
    id="SPEC-1578",
    title="Co-Pilot Knowledge Management: Provider Console UI page",
    description=(
        "A new Provider Console page 'Co-Pilot Knowledge' in the Operations group. "
        "Four tabs: (1) Documents — sortable/filterable table with CRUD actions, "
        "(2) Ingestion — batch scan with diff preview and progress indicator, "
        "(3) Schedule — recurring scan configuration with history log, "
        "(4) Parameters — retrieval tuning sliders with test query input. "
        "Uses Mantine v7 components consistent with existing Provider Console pages."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "glob",
            "pattern": "admin/provider/pages/CopilotKnowledge*",
            "description": "Co-Pilot Knowledge page component exists",
        },
    ],
    changed_by="S126",
    change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
)
print("  SPEC-1578: Provider Console UI page")

# Work items for Co-Pilot Knowledge Management
for wi_id, title, desc, component in [
    ("WI-0884", "Co-Pilot Knowledge: document CRUD API endpoints",
     "Implement 5 CRUD endpoints on superadmin API for copilot-docs (list, get, create, update, soft-delete).",
     "provider_administration"),
    ("WI-0885", "Co-Pilot Knowledge: batch ingestion pipeline",
     "Implement POST /copilot-docs/ingest — scan docs-site/docs/admin-guide/*.md, parse sections, hash, embed, upsert. Incremental via SHA-256.",
     "provider_administration"),
    ("WI-0886", "Co-Pilot Knowledge: URL import and re-embed endpoints",
     "Implement URL fetch+convert for document creation and POST /copilot-docs/re-embed for triggered re-embedding.",
     "provider_administration"),
    ("WI-0887", "Co-Pilot Knowledge: collection stats endpoint",
     "Implement GET /copilot-docs/stats — counts by category, embedding coverage, staleness metrics.",
     "provider_administration"),
    ("WI-0888", "Co-Pilot Knowledge: scan scheduler",
     "Implement CopilotDocScheduler with configurable frequency (manual/daily/weekly), scan scope, and history tracking.",
     "provider_administration"),
    ("WI-0889", "Co-Pilot Knowledge: CoPilotAgent runtime config",
     "Replace hardcoded DEFAULT_* constants in CoPilotAgent with CopilotConfig document. Add test-query endpoint.",
     "agent_implementation"),
    ("WI-0890", "Co-Pilot Knowledge: Provider Console UI (4 tabs)",
     "Build CopilotKnowledge.tsx page with Documents, Ingestion, Schedule, and Parameters tabs.",
     "provider_administration"),
]:
    db.insert_work_item(
        id=wi_id,
        title=title,
        description=desc,
        origin="new",
        component=component,
        resolution_status="open",
        source_spec_id="SPEC-1570",
        changed_by="S126",
        change_reason="Co-Pilot Knowledge Management feature — owner approved proposal",
    )
    print(f"  {wi_id}: {title}")

# ============================================================================
# 3. PIPELINE OBSERVATORY
# ============================================================================

print("\n=== PIPELINE OBSERVATORY ===\n")

db.insert_spec(
    id="SPEC-1579",
    title="Pipeline Observatory: topology endpoint with aggregate traffic metrics",
    description=(
        "GET /api/superadmin/pipeline/topology must return the 7-agent pipeline topology "
        "with aggregate traffic metrics per agent (node) and per edge (agent-to-agent). "
        "Per-node: invocation_count, avg_latency_ms, p50/p95/p99_latency_ms, error_rate, "
        "avg_tokens_in, avg_tokens_out, avg_cost. Per-edge: volume, avg_transition_latency_ms, "
        "drop_off_rate. Time-windowed via since/until/period query parameters."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "pipeline/topology",
            "description": "Pipeline topology endpoint exists",
        },
    ],
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1579: Pipeline topology endpoint")

db.insert_spec(
    id="SPEC-1580",
    title="Pipeline Observatory: per-agent detailed metrics endpoint",
    description=(
        "GET /api/superadmin/pipeline/agents/{agent}/metrics must return detailed "
        "performance metrics for a single agent: latency histogram (distribution), "
        "latency trend over time (sparkline data), error log (recent failures with "
        "conversation IDs), token usage trend, cost per invocation trend. "
        "Time-windowed via since/until/period parameters."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "pipeline/agents",
            "description": "Per-agent metrics endpoint exists",
        },
    ],
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1580: Per-agent detailed metrics")

db.insert_spec(
    id="SPEC-1581",
    title="Pipeline Observatory: tenant comparison endpoint with sort/filter",
    description=(
        "GET /api/superadmin/pipeline/tenants must return all tenants with pipeline "
        "metrics summary: total_conversations, billable_conversations, avg_latency_ms, "
        "error_rate, escalation_rate, token_consumption, cost, estimated_ru, "
        "avg_conversation_length, resolution_rate. Must support: sort by any column, "
        "filter by tier, min/max range filters on numeric columns, text search on "
        "tenant name/ID. Response includes customerEmail and shopifyShopDomain per SPEC-1569."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "pipeline/tenants",
            "description": "Tenant comparison endpoint exists",
        },
    ],
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1581: Tenant comparison endpoint")

db.insert_spec(
    id="SPEC-1582",
    title="Pipeline Observatory: per-tenant pipeline metrics detail",
    description=(
        "GET /api/superadmin/pipeline/tenants/{tenant_id}/metrics must return "
        "detailed pipeline metrics for a single tenant: conversation volume trend, "
        "cost trend, agent invocation breakdown, intent distribution, "
        "recent conversations table with pipeline_trace data."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1582: Per-tenant pipeline metrics detail")

db.insert_spec(
    id="SPEC-1583",
    title="Pipeline Observatory: database operational metrics",
    description=(
        "GET /api/superadmin/pipeline/database must return Cosmos DB operational "
        "metrics: document counts per collection per tenant, estimated storage per "
        "tenant, RU consumption trends (estimated from conversation + KB operations). "
        "Average database volumes must be visible per-tenant."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/superadmin_api.py",
            "pattern": "pipeline/database",
            "description": "Database metrics endpoint exists",
        },
    ],
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1583: Database operational metrics")

db.insert_spec(
    id="SPEC-1584",
    title="Pipeline Observatory: metrics aggregation engine",
    description=(
        "A PipelineMetricsAggregator class must query conversation documents across "
        "all tenants and compute per-agent metrics (from pipeline_trace.stages[]), "
        "per-edge metrics (agent-to-agent flow volume and latency), and per-tenant "
        "aggregate metrics. Must handle time windowing efficiently and cache results "
        "for dashboard responsiveness."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "grep",
            "file": "src/multi_tenant/*.py",
            "pattern": "PipelineMetricsAggregator",
            "description": "Aggregation engine class exists",
        },
    ],
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1584: Metrics aggregation engine")

db.insert_spec(
    id="SPEC-1585",
    title="Pipeline Observatory: Traffic Flow visual topology tab",
    description=(
        "The Pipeline Observatory page must have a Traffic Flow tab showing a visual "
        "node-link diagram of the 7 agents with directed edges. Edge thickness = message "
        "volume. Node color = health (green <1%% error, yellow 1-5%%, red >5%%). "
        "Click node for drill-down. Click edge for transition metrics. "
        "Time range selector (1h, 6h, 24h, 7d, 30d). Annotations: total messages, "
        "average end-to-end latency, overall error rate."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    assertions=[
        {
            "type": "glob",
            "pattern": "admin/provider/pages/PipelineObservatory*",
            "description": "Pipeline Observatory page component exists",
        },
    ],
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1585: Traffic Flow visual topology tab")

db.insert_spec(
    id="SPEC-1586",
    title="Pipeline Observatory: Agent Metrics performance cards tab",
    description=(
        "The Pipeline Observatory page must have an Agent Metrics tab showing one "
        "card per agent (7 cards). Each card: invocation count, latency sparkline, "
        "P50/P95/P99 latency, error rate, avg token usage, avg cost per invocation. "
        "Expandable detail panel with latency histogram and error log."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1586: Agent Metrics performance cards tab")

db.insert_spec(
    id="SPEC-1587",
    title="Pipeline Observatory: Tenant Comparison sortable/filterable table tab",
    description=(
        "The Pipeline Observatory page must have a Tenant Comparison tab with a "
        "multi-tenant metrics table. Columns: tenant identifier (per SPEC-1569), tier, "
        "conversations (total/billable), avg latency, error rate, escalation rate, "
        "token consumption, cost, Cosmos RU, avg conversation length, resolution rate. "
        "Must support: click column header to sort, tier dropdown filter, min/max range "
        "filters on numeric columns, text search on tenant name/email, CSV export. "
        "Click row to drill-down to single-tenant detail view."
    ),
    status="specified",
    section="provider_administration",
    type="requirement",
    changed_by="S126",
    change_reason="Pipeline Observatory feature — owner approved proposal",
)
print("  SPEC-1587: Tenant Comparison table tab")

# Work items for Pipeline Observatory
for wi_id, title, desc, component in [
    ("WI-0891", "Pipeline Observatory: PipelineMetricsAggregator engine",
     "Implement cross-tenant conversation trace aggregation with per-agent, per-edge, and per-tenant metric computation. Time windowing and caching.",
     "provider_administration"),
    ("WI-0892", "Pipeline Observatory: topology endpoint",
     "Implement GET /api/superadmin/pipeline/topology — agent-to-agent flow with aggregate metrics.",
     "provider_administration"),
    ("WI-0893", "Pipeline Observatory: per-agent metrics endpoint",
     "Implement GET /api/superadmin/pipeline/agents/{agent}/metrics — latency histograms, error logs, token trends.",
     "provider_administration"),
    ("WI-0894", "Pipeline Observatory: tenant comparison endpoint",
     "Implement GET /api/superadmin/pipeline/tenants — all tenants with sortable/filterable pipeline metrics.",
     "provider_administration"),
    ("WI-0895", "Pipeline Observatory: per-tenant detail + database metrics endpoints",
     "Implement per-tenant drill-down and database operational metrics endpoints.",
     "provider_administration"),
    ("WI-0896", "Pipeline Observatory: Traffic Flow tab UI",
     "Build visual node-link topology diagram with health coloring, drill-down, and time range selector using Recharts/SVG.",
     "provider_administration"),
    ("WI-0897", "Pipeline Observatory: Agent Metrics tab UI",
     "Build 7-agent performance card grid with sparklines, expandable detail panels.",
     "provider_administration"),
    ("WI-0898", "Pipeline Observatory: Tenant Comparison tab UI",
     "Build sortable/filterable/searchable metrics table with CSV export and tenant drill-down.",
     "provider_administration"),
]:
    db.insert_work_item(
        id=wi_id,
        title=title,
        description=desc,
        origin="new",
        component=component,
        resolution_status="open",
        source_spec_id="SPEC-1579",
        changed_by="S126",
        change_reason="Pipeline Observatory feature — owner approved proposal",
    )
    print(f"  {wi_id}: {title}")

# ============================================================================
# Summary
# ============================================================================

print("\n=== SUMMARY ===")
print(f"  Specifications recorded: SPEC-1568 through SPEC-1587 (20 specs)")
print(f"  Work items recorded: WI-0882 through WI-0898 (17 WIs)")
print(f"    - Secret Posture defects: 2 specs, 2 WIs")
print(f"    - Co-Pilot Knowledge Management: 9 specs, 7 WIs")
print(f"    - Pipeline Observatory: 9 specs, 8 WIs")

db.close()
print("\nDone.")
