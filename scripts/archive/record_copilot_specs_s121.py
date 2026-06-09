"""
Record Co-pilot Agent specifications and work items — S121.

6 specifications (SPEC-1557..1562) and 6 work items (WI-0875..0880)
for the Admin Co-pilot Agent feature.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, "tools/knowledge-db")

import db

k = db.KnowledgeDB()
SESSION = "S121"

# ─── Specifications ──────────────────────────────────────────────────

specs = [
    {
        "id": "SPEC-1557",
        "title": "Co-Pilot Agent",
        "description": (
            "A new AGNTCY agent (co-pilot) extends AgentRedBaseAgent and serves as the "
            "dedicated handler for all admin team member conversations. The Co-pilot has "
            "access to the complete Agent Red product documentation, vectorized in a shared "
            "(non-tenant-scoped) vector database instance. It answers questions about "
            "administrative tasks, UI features, configuration options, and troubleshooting — "
            "scoped to the team member's role."
        ),
        "section": "AGENTS",
        "priority": "P1",
        "tags": ["co-pilot", "admin-assistant", "agent", "agntcy"],
        "assertions": [
            {
                "description": "CoPilotAgent extends AgentRedBaseAgent with agent_type = 'co-pilot'",
                "type": "structural",
            },
            {"description": "AgentTopic enum includes CO_PILOT = 'co-pilot'", "type": "structural"},
            {
                "description": "Co-pilot follows 3-tier dispatch (SLIM transport → HTTP container → in-process)",
                "type": "functional",
            },
            {
                "description": "Co-pilot retrieves documentation from a shared vector index, not the tenant's customer-facing KB",
                "type": "functional",
            },
            {
                "description": "Co-pilot responses cite documentation sources (page/section references)",
                "type": "functional",
            },
        ],
    },
    {
        "id": "SPEC-1558",
        "title": "Admin Intent Detection & Routing",
        "description": (
            "When a chat message is received from an authenticated team member (admin API key "
            "ar_user_*), the intent classifier includes admin_assistance in its taxonomy. When "
            "intent is admin_assistance, the pipeline routes to the Co-pilot agent instead of "
            "the standard KR → RG path. Authentication is verified via existing get_tenant_context "
            "middleware — only team members with roles SUPERADMIN, ADMIN, ESCALATION_AGENT, or "
            "VIEWER are routed to Co-pilot. Widget key (pk_live_*) authenticated requests are "
            "never routed to Co-pilot."
        ),
        "section": "AGENTS",
        "priority": "P1",
        "tags": ["co-pilot", "intent-classification", "routing", "authentication"],
        "assertions": [
            {"description": "admin_assistance is added to INTENT_TAXONOMY (18th intent)", "type": "structural"},
            {
                "description": "Intent classifier returns admin_assistance for admin-context questions about Agent Red features",
                "type": "functional",
            },
            {
                "description": "Pipeline dispatches to Co-pilot agent when intent is admin_assistance",
                "type": "functional",
            },
            {
                "description": "Widget-key-authenticated requests never receive admin_assistance classification",
                "type": "security",
            },
            {
                "description": "Admin-key-authenticated requests may receive any intent (including customer-facing intents when testing the widget)",
                "type": "functional",
            },
        ],
    },
    {
        "id": "SPEC-1559",
        "title": "Shared Documentation Vector Database",
        "description": (
            "Product documentation is stored in a dedicated Cosmos DB collection "
            "(admin_documentation_vectors) partitioned by document_category — not by tenant_id. "
            "This is a platform-level resource shared across all tenants. Documentation is "
            "embedded using the same model (text-embedding-3-large, 3072 dimensions) and supports "
            "the same hybrid search (vector + BM25) as the tenant knowledge base. Documentation "
            "covers all admin features: dashboard, knowledge base, widget configuration, team "
            "management, conversations, analytics, custom instructions, brand & tone, policies, "
            "escalation rules, integrations, and save & activate workflow."
        ),
        "section": "INFRASTRUCTURE",
        "priority": "P1",
        "tags": ["co-pilot", "vector-database", "cosmos-db", "embeddings", "documentation"],
        "assertions": [
            {
                "description": "admin_documentation_vectors collection exists in Cosmos DB (container #18)",
                "type": "structural",
            },
            {"description": "Partition key is /document_category, not /tenant_id", "type": "structural"},
            {"description": "Embeddings use text-embedding-3-large (3072 dimensions)", "type": "functional"},
            {"description": "Hybrid retrieval (vector 70% + BM25 30%) via RRF", "type": "functional"},
            {"description": "At least 12 document categories cover all admin feature areas", "type": "functional"},
            {
                "description": "Documentation updates propagate to all tenants without per-tenant migration",
                "type": "functional",
            },
        ],
    },
    {
        "id": "SPEC-1560",
        "title": "Co-Pilot Fine-Tuning",
        "description": (
            "Admin conversations with the Co-pilot are collected, PII-stripped, and used to "
            "fine-tune the Co-pilot model via the existing Layer 4 fine-tuning pipeline "
            "infrastructure (quality gates, A/B validation, evaluation metrics). Fine-tuning "
            "is performed on aggregated data across all tenants — not per-tenant. The training "
            "corpus consists of admin questions and Co-pilot responses that received positive "
            "feedback or led to successful task completion."
        ),
        "section": "AGENTS",
        "priority": "P2",
        "tags": ["co-pilot", "fine-tuning", "layer-4", "pii", "cross-tenant"],
        "assertions": [
            {
                "description": "Admin conversations are eligible for Co-pilot fine-tuning data collection",
                "type": "functional",
            },
            {
                "description": "PII tokenization is applied before conversation data enters the training corpus",
                "type": "security",
            },
            {
                "description": "Fine-tuning uses existing Layer 4 quality gates (hallucination, format, tone, accuracy, BLEU/ROUGE)",
                "type": "functional",
            },
            {"description": "Training data is aggregated cross-tenant (platform-level model)", "type": "functional"},
            {"description": "A/B validation compares fine-tuned Co-pilot against base model", "type": "functional"},
        ],
    },
    {
        "id": "SPEC-1561",
        "title": "Admin Conversation Analytics",
        "description": (
            "All Co-pilot conversations are stored with conversation_type: 'admin_assistance' on "
            "the ConversationDocument. A new conversation_type field distinguishes admin "
            "conversations from customer conversations. Admin conversations do not count toward "
            "the tenant's billable conversation quota. Aggregated analytics across all admin "
            "conversations enable tracking of: common questions, feature discovery patterns, "
            "documentation gaps, administration usage patterns, and product issue trends. "
            "Historical admin conversation data is PII-stripped before vectorization to prevent "
            "security and privacy violations."
        ),
        "section": "ANALYTICS",
        "priority": "P1",
        "tags": ["co-pilot", "analytics", "conversation-type", "pii", "billing"],
        "assertions": [
            {
                "description": "ConversationDocument includes conversation_type field (default: 'customer')",
                "type": "structural",
            },
            {
                "description": "Co-pilot conversations are stored with conversation_type: 'admin_assistance'",
                "type": "functional",
            },
            {
                "description": "Admin conversations are excluded from tenant billable conversation counts (is_billable: false)",
                "type": "functional",
            },
            {"description": "Admin conversation history is PII-tokenized before vectorization", "type": "security"},
            {
                "description": "Cross-tenant analytics query on conversation_type = 'admin_assistance' is supported",
                "type": "functional",
            },
        ],
    },
    {
        "id": "SPEC-1562",
        "title": "Widget Admin Mode",
        "description": (
            "When the chat widget is rendered within the Agent Red admin panel, it operates in "
            "admin mode: chat messages are sent using the admin API key for authentication (not "
            "the widget key), and the widget displays a Co-pilot mode indicator to distinguish "
            "from customer-preview mode. The admin API key is already available in "
            "StandaloneLayout.tsx via apiFetch. On storefront pages, the widget continues using "
            "widget key authentication and the standard customer pipeline."
        ),
        "section": "WIDGET_UI",
        "priority": "P1",
        "tags": ["co-pilot", "widget", "admin-mode", "authentication"],
        "assertions": [
            {
                "description": "Widget in admin panel authenticates chat messages with admin API key",
                "type": "functional",
            },
            {"description": "Widget in admin panel displays a Co-pilot mode indicator", "type": "ui"},
            {"description": "Widget on storefront uses widget key authentication (unchanged)", "type": "functional"},
            {
                "description": "Admin mode is determined by authentication method, not a client-side flag",
                "type": "security",
            },
        ],
    },
]

print(f"Recording {len(specs)} specifications...")
for spec in specs:
    result = k.insert_spec(
        id=spec["id"],
        title=spec["title"],
        status="specified",
        changed_by=SESSION,
        change_reason=f"{SESSION}: Co-pilot Agent feature — owner-approved specification",
        description=spec["description"],
        priority=spec.get("priority"),
        section=spec.get("section"),
        tags=spec.get("tags"),
        assertions=spec.get("assertions"),
    )
    print(f"  ✓ {spec['id']}: {spec['title']} (v{result['version']})")

# ─── Work Items ──────────────────────────────────────────────────────

work_items = [
    {
        "id": "WI-0875",
        "title": "Implement CoPilotAgent (AGNTCY agent + dispatch)",
        "source_spec_id": "SPEC-1557",
        "component": "agent_implementation",
        "description": (
            "Create CoPilotAgent extending AgentRedBaseAgent. Add CO_PILOT to AgentTopic enum. "
            "Add _call_co_pilot() to AgentDispatchMixin following 3-tier pattern. Create "
            "container app. Wire telemetry via trace_agent_operation()."
        ),
    },
    {
        "id": "WI-0876",
        "title": "Add admin_assistance intent + pipeline routing",
        "source_spec_id": "SPEC-1558",
        "component": "agent_implementation",
        "description": (
            "Add admin_assistance to INTENT_TAXONOMY. Update intent classifier system prompt. "
            "Add routing logic in ChatPipeline to dispatch to Co-pilot when intent is "
            "admin_assistance and auth is admin API key. Gate widget-key requests from "
            "receiving admin_assistance intent."
        ),
    },
    {
        "id": "WI-0877",
        "title": "Create shared admin_documentation_vectors Cosmos collection",
        "source_spec_id": "SPEC-1559",
        "component": "infrastructure_automation",
        "description": (
            "Create Cosmos DB container #18 (admin_documentation_vectors) with /document_category "
            "partition key and DiskANN vector index. Create document schema. Write ingestion "
            "script to vectorize docs-site/docs/admin-guide/ files. Create hybrid retrieval "
            "method for Co-pilot."
        ),
    },
    {
        "id": "WI-0878",
        "title": "Extend fine-tuning pipeline for Co-pilot training",
        "source_spec_id": "SPEC-1560",
        "component": "agent_implementation",
        "description": (
            "Extend Layer 4 fine-tuning pipeline to collect admin conversations. Add PII "
            "tokenization before training data ingestion. Implement cross-tenant aggregation. "
            "Configure quality gates for Co-pilot model evaluation."
        ),
    },
    {
        "id": "WI-0879",
        "title": "Add conversation_type field + admin analytics",
        "source_spec_id": "SPEC-1561",
        "component": "database",
        "description": (
            "Add conversation_type field to ConversationDocument (default: 'customer'). Set "
            "is_billable=false for admin_assistance conversations. Add PII tokenization before "
            "admin conversation vectorization. Create cross-tenant analytics query support."
        ),
    },
    {
        "id": "WI-0880",
        "title": "Implement widget admin mode (Co-pilot UI)",
        "source_spec_id": "SPEC-1562",
        "component": "customer_interface",
        "description": (
            "Configure widget in admin panel to use admin API key for chat authentication. "
            "Add Co-pilot mode indicator to widget header. Ensure storefront widget continues "
            "using widget key. Route admin chat to /api/admin/chat or equivalent endpoint."
        ),
    },
]

print(f"\nRecording {len(work_items)} work items...")
for wi in work_items:
    result = k.insert_work_item(
        id=wi["id"],
        title=wi["title"],
        origin="new",
        component=wi["component"],
        resolution_status="open",
        changed_by=SESSION,
        change_reason=f"{SESSION}: Co-pilot Agent feature — new work item",
        description=wi.get("description"),
        source_spec_id=wi.get("source_spec_id"),
        priority="P1",
    )
    print(f"  ✓ {wi['id']}: {wi['title']} (v{result['version']})")

# ─── Summary ─────────────────────────────────────────────────────────

total_assertions = sum(len(s.get("assertions", [])) for s in specs)
print(f"\n{'=' * 60}")
print(f"Recorded: {len(specs)} specifications, {len(work_items)} work items")
print(f"Spec IDs: SPEC-1557..SPEC-1562")
print(f"WI IDs:   WI-0875..WI-0880")
print(f"Total assertions: {total_assertions}")
print(f"All status: specified (specs), open (WIs)")
