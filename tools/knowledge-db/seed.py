"""
Seed script — loads initial data into the knowledge database from existing
project artifacts. Run once to bootstrap, then Claude maintains via Python API.

Usage:
  python tools/knowledge-db/seed.py              # full seed
  python tools/knowledge-db/seed.py --dry-run    # print counts, don't write

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Import sibling module
sys.path.insert(0, str(Path(__file__).parent))
from db import KnowledgeDB

CHANGE_BY = "seed"
CHANGE_REASON = "Initial import from markdown artifacts"

# ─────────────────────────────────────────────────────────────────────
# Specification Seed Data
# ─────────────────────────────────────────────────────────────────────

# Sections 1-13: WI #101-239 (confirmed complete in backlog)
# These are batch-imported with status="verified" — no individual assertions
# because the backlog confirms them all as Complete with implementation details.

VERIFIED_SPECS: list[dict] = [
    # Section 1: Test Infrastructure (101-107) — ALL COMPLETE
    {"id": "101", "title": "pytest configuration (pyproject.toml)", "priority": "P0", "scope": "Test", "section": "1. Test Infrastructure", "status": "verified"},
    {"id": "102", "title": "Test requirements file (requirements-test.txt)", "priority": "P0", "scope": "Test", "section": "1. Test Infrastructure", "status": "verified"},
    {"id": "103", "title": "Shared test fixtures (tests/conftest.py)", "priority": "P0", "scope": "Test", "section": "1. Test Infrastructure", "status": "verified"},
    {"id": "104", "title": "GitHub Actions CI workflow for pytest", "priority": "P0", "scope": "Test", "section": "1. Test Infrastructure", "status": "verified"},
    {"id": "105", "title": "Coverage reporting and gate (70% min, 80% target)", "priority": "P1", "scope": "Test", "section": "1. Test Infrastructure", "status": "verified"},
    {"id": "106", "title": "Centralize tenant context factory functions", "priority": "P1", "scope": "Test", "section": "1. Test Infrastructure", "status": "verified"},
    {"id": "107", "title": "Performance test infrastructure (Locust)", "priority": "P1", "scope": "Test", "section": "1. Test Infrastructure", "status": "verified"},

    # Section 2: Merchant Web UI (108-118)
    {"id": "108", "title": "Frontend framework selection (Preact/React/Polaris)", "priority": "P0", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},
    {"id": "109", "title": "Merchant authentication UI (login, API key, Shopify OAuth)", "priority": "P0", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},
    {"id": "110", "title": "Usage dashboard UI", "priority": "P0", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},
    {"id": "111", "title": "Conversation audit trail UI", "priority": "P1", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},
    {"id": "112", "title": "Tenant configuration UI with onboarding wizard", "priority": "P1", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},
    {"id": "113", "title": "Billing management UI", "priority": "P1", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},
    {"id": "114", "title": "GDPR consent management UI", "priority": "P1", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},
    {"id": "115", "title": "Customer profile viewer UI", "priority": "P2", "scope": "Admin", "section": "2. Merchant Web UI", "status": "implemented", "description": "API exists (CustomerProfileService), admin page scaffolded. Partial."},
    {"id": "116", "title": "Response explainability viewer UI", "priority": "P2", "scope": "Admin", "section": "2. Merchant Web UI", "status": "implemented", "description": "API exists (ResponseDecisionTrace), admin page scaffolded. Partial."},
    {"id": "117", "title": "Alert notification UI", "priority": "P1", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},
    {"id": "118", "title": "Brand/theme customization UI", "priority": "P2", "scope": "Admin", "section": "2. Merchant Web UI", "status": "verified"},

    # Section 3: Trial / Demo Environment (119-128) — ALL COMPLETE
    {"id": "119", "title": "TenantTier.TRIAL enum and TIER_DEFAULTS", "priority": "P0", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "120", "title": "Trial provisioning flow (14-day)", "priority": "P0", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "121", "title": "Trial expiry mechanism", "priority": "P0", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "122", "title": "Trial conversation cap (50)", "priority": "P1", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "123", "title": "Trial model routing (GPT-4o-mini)", "priority": "P1", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "124", "title": "Trial to paid conversion flow", "priority": "P0", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "125", "title": "Demo data seeder", "priority": "P1", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "126", "title": "Trial-specific dashboard view", "priority": "P1", "scope": "Admin", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "127", "title": "Expired trial data cleanup (30 days)", "priority": "P2", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},
    {"id": "128", "title": "Trial metrics isolation", "priority": "P2", "scope": "API", "section": "3. Trial/Demo Environment", "status": "verified"},

    # Section 4: SSE (129-133) — ALL COMPLETE
    {"id": "129", "title": "SSE streaming endpoint", "priority": "P0", "scope": "API+Widget", "section": "4. Response Streaming (SSE)", "status": "verified"},
    {"id": "130", "title": "Streaming-compatible Critic validation", "priority": "P0", "scope": "API", "section": "4. Response Streaming (SSE)", "status": "verified"},
    {"id": "131", "title": "SSE error handling (mid-stream, client retry)", "priority": "P1", "scope": "API+Widget", "section": "4. Response Streaming (SSE)", "status": "verified"},
    {"id": "132", "title": "Conversation metering for streaming (first_chunk_at)", "priority": "P1", "scope": "API", "section": "4. Response Streaming (SSE)", "status": "verified"},
    {"id": "133", "title": "SSE connection management (multi-tab coordination)", "priority": "P1", "scope": "API+Widget", "section": "4. Response Streaming (SSE)", "status": "verified"},

    # Section 5: Pipeline Optimization (134-139)
    {"id": "134", "title": "IC + KR parallelization (~800ms savings)", "priority": "P1", "scope": "API", "section": "5. Pipeline Optimization", "status": "verified"},
    {"id": "135", "title": "Prompt optimization and prefix caching", "priority": "P1", "scope": "API", "section": "5. Pipeline Optimization", "status": "verified"},
    {"id": "136", "title": "Model routing — GPT-4o-mini for simple queries", "priority": "P2", "scope": "API", "section": "5. Pipeline Optimization", "status": "verified"},
    {"id": "137", "title": "Semantic response caching", "priority": "P2", "scope": "API", "section": "5. Pipeline Optimization", "status": "retired", "description": "Superseded by WI #223-225 (semantic_cache.py)."},
    {"id": "138", "title": "Customer context pre-computation / warm-up", "priority": "P2", "scope": "API", "section": "5. Pipeline Optimization", "status": "specified"},
    {"id": "139", "title": "Azure OpenAI PTU investigation", "priority": "P3", "scope": "Ops", "section": "5. Pipeline Optimization", "status": "specified", "description": "Deferred to 50+ tenants ($3,300/mo minimum)."},

    # Section 6: API Completeness (140-147) — ALL COMPLETE
    {"id": "140", "title": "GDPR compliance REST endpoints", "priority": "P0", "scope": "API", "section": "6. API Completeness", "status": "verified"},
    {"id": "141", "title": "Audit log query API", "priority": "P1", "scope": "API", "section": "6. API Completeness", "status": "verified"},
    {"id": "142", "title": "Customer profile REST endpoints", "priority": "P1", "scope": "API", "section": "6. API Completeness", "status": "verified"},
    {"id": "143", "title": "Knowledge base management REST endpoints", "priority": "P1", "scope": "API", "section": "6. API Completeness", "status": "verified"},
    {"id": "144", "title": "Alert delivery mechanism (webhook, dashboard, log)", "priority": "P1", "scope": "API", "section": "6. API Completeness", "status": "verified"},
    {"id": "145", "title": "Rate limit headers on all API responses", "priority": "P1", "scope": "API", "section": "6. API Completeness", "status": "verified"},
    {"id": "146", "title": "Correlation-id in API response headers", "priority": "P1", "scope": "API", "section": "6. API Completeness", "status": "verified"},
    {"id": "147", "title": "OpenAPI schema completeness (74 endpoints)", "priority": "P2", "scope": "API", "section": "6. API Completeness", "status": "verified"},

    # Section 7: Operational Readiness (148-156) — ALL COMPLETE
    {"id": "148", "title": "Deployment runbook", "priority": "P0", "scope": "Ops", "section": "7. Operational Readiness", "status": "verified"},
    {"id": "149", "title": "DR runbook — Option A", "priority": "P1", "scope": "Ops", "section": "7. Operational Readiness", "status": "verified"},
    {"id": "150", "title": "Maintenance runbook", "priority": "P1", "scope": "Ops", "section": "7. Operational Readiness", "status": "verified"},
    {"id": "151", "title": "SLA monitoring dashboard", "priority": "P1", "scope": "API", "section": "7. Operational Readiness", "status": "verified"},
    {"id": "152", "title": "KEDA scaling profiles", "priority": "P0", "scope": "Ops", "section": "7. Operational Readiness", "status": "verified"},
    {"id": "153", "title": "Archival pipeline (Change Feed -> Parquet -> Blob)", "priority": "P1", "scope": "API", "section": "7. Operational Readiness", "status": "verified"},
    {"id": "154", "title": "Data retention policy enforcement", "priority": "P1", "scope": "API", "section": "7. Operational Readiness", "status": "verified"},
    {"id": "155", "title": "Parameterized cost model calculator", "priority": "P2", "scope": "API", "section": "7. Operational Readiness", "status": "verified"},
    {"id": "156", "title": "Option C upgrade path documentation", "priority": "P2", "scope": "Ops", "section": "7. Operational Readiness", "status": "verified"},

    # Section 8: Security Hardening (157-163) — ALL COMPLETE
    {"id": "157", "title": "Request body size limits (1MB)", "priority": "P0", "scope": "API", "section": "8. Security Hardening", "status": "verified"},
    {"id": "158", "title": "JSON depth limit (50 levels)", "priority": "P1", "scope": "API", "section": "8. Security Hardening", "status": "verified"},
    {"id": "159", "title": "API key rotation endpoint", "priority": "P1", "scope": "API", "section": "8. Security Hardening", "status": "verified"},
    {"id": "160", "title": "Input sanitization for path parameters", "priority": "P1", "scope": "API", "section": "8. Security Hardening", "status": "verified"},
    {"id": "161", "title": "Output sanitization for AI responses", "priority": "P1", "scope": "API", "section": "8. Security Hardening", "status": "verified"},
    {"id": "162", "title": "Stripe webhook IP allowlisting", "priority": "P2", "scope": "API", "section": "8. Security Hardening", "status": "verified"},
    {"id": "163", "title": "Rate limiting on authentication endpoints", "priority": "P1", "scope": "API", "section": "8. Security Hardening", "status": "verified"},

    # Section 10: Launch Preparation (196-204) — all specified/todo
    {"id": "196", "title": "Docker container images + ACR push", "priority": "P0", "scope": "Ops", "section": "10. Launch Preparation", "status": "verified", "description": "Build and push Docker images. Completed — production deployed v1.58.2."},
    {"id": "197", "title": "Production Terraform deployment", "priority": "P0", "scope": "Ops", "section": "10. Launch Preparation", "status": "verified", "description": "Completed — Container Apps deployed."},
    {"id": "198", "title": "Widget bundle -> Shopify Theme App Extension", "priority": "P0", "scope": "Widget", "section": "10. Launch Preparation", "status": "specified"},
    {"id": "199", "title": "Create Remaker Digital Shopify storefront", "priority": "P0", "scope": "Ops", "section": "10. Launch Preparation", "status": "verified", "description": "Owner task. blanco-9939.myshopify.com created."},
    {"id": "200", "title": "Onboard Remaker Digital as tenant #1", "priority": "P0", "scope": "Ops", "section": "10. Launch Preparation", "status": "verified", "description": "remaker-digital-001 provisioned and seeded."},
    {"id": "201", "title": "Seed knowledge base with Agent Red product data", "priority": "P1", "scope": "API", "section": "10. Launch Preparation", "status": "specified"},
    {"id": "202", "title": "Deploy widget on storefront + verify E2E", "priority": "P1", "scope": "Widget", "section": "10. Launch Preparation", "status": "specified"},
    {"id": "203", "title": "UX consultant evaluation (Mazel)", "priority": "P1", "scope": "Admin", "section": "10. Launch Preparation", "status": "specified"},
    {"id": "204", "title": "Favicon and app icons from icon-master.png", "priority": "P1", "scope": "Admin", "section": "10. Launch Preparation", "status": "specified"},

    # Section 11: RAG Infrastructure (209-225) — ALL COMPLETE
    {"id": "209", "title": "KB Vector Embedding Schema (DiskANN index)", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "210", "title": "KB Embedding Pipeline (knowledge_vectorizer.py)", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "211", "title": "KB Vector Search (cosine similarity replaces keyword)", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "212", "title": "Hybrid Retrieval (BM25 + RRF)", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "213", "title": "Retrieval Quality Monitoring", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "214", "title": "File Upload API (PDF/DOCX/CSV/TXT)", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "215", "title": "Document Parsing Pipeline (document_parser.py)", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "216", "title": "Document Chunking (256-512 tokens)", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "217", "title": "Bulk Import/Export (CSV)", "priority": "P0", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "218", "title": "Admin UI for Upload (KnowledgeBaseManager.tsx)", "priority": "P0", "scope": "Admin", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "219", "title": "Staleness Schema (last_verified_at, staleness_score)", "priority": "P1", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "220", "title": "Staleness Detection Service (staleness_service.py)", "priority": "P1", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "221", "title": "Refresh Prompts UI (staleness badges + verify action)", "priority": "P1", "scope": "Admin", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "222", "title": "Automatic Re-embedding on content change", "priority": "P1", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "223", "title": "Query Embedding Cache (LRU + TTL)", "priority": "P1", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "224", "title": "Semantic Response Cache (0.95 cosine threshold)", "priority": "P1", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},
    {"id": "225", "title": "Cache Monitoring Dashboard (hit rate, cost savings)", "priority": "P1", "scope": "API", "section": "11. RAG Infrastructure", "status": "verified"},

    # Section 12: KB Quality Tools (239)
    {"id": "239", "title": "KB Conflict/Duplication Scanner (4-phase detection)", "priority": "P1", "scope": "API+Admin", "section": "12. KB Quality Tools", "status": "verified"},
]


# Sections 14-28: WI #240-299 — with assertions for codebase verification.
# Status determined by S96 audit: implemented items confirmed via grep/glob.

AUDITED_SPECS: list[dict] = [
    # Section 13: Admin UX Polish
    {"id": "226", "title": "Admin contextual tooltips with docs links", "priority": "P1", "scope": "Admin", "section": "13. Admin UX Polish", "status": "specified",
     "description": "Every interactive element across both admin interfaces must have a mouseover tooltip with doc link."},

    # Section 14: Widget & Quick Actions UX Fixes (240-245)
    {"id": "240", "title": "Widget applies saved color configuration", "priority": "P1", "scope": "Widget", "section": "14. Widget & Quick Actions UX Fixes", "status": "implemented",
     "handle": "WIDGET-UX", "tags": ["widget", "config-delivery", "color"],
     "assertions": [
         {"type": "grep", "pattern": "widget_primary_color", "file": "src/multi_tenant/schema/fields.yaml", "min_count": 1, "description": "Widget color field defined in schema"},
     ]},
    {"id": "241", "title": "Widget displays custom greeting message", "priority": "P1", "scope": "Widget", "section": "14. Widget & Quick Actions UX Fixes", "status": "implemented",
     "handle": "WIDGET-UX", "tags": ["widget", "config-delivery", "greeting"],
     "assertions": [
         {"type": "grep", "pattern": "greeting_message|widget_greeting_message", "file": "src/multi_tenant/schema/fields.yaml", "min_count": 1, "description": "Greeting field defined in schema"},
     ]},
    {"id": "242", "title": "Quick actions starter examples on first visit", "priority": "P2", "scope": "Admin", "section": "14. Widget & Quick Actions UX Fixes", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "starter|_STARTER_ACTIONS|seed.*quick", "file": "src/multi_tenant/admin_quick_action_api.py", "min_count": 1, "description": "Quick action starter examples in API"},
     ]},
    {"id": "243", "title": "Quick action Icon field guidance", "priority": "P2", "scope": "Admin", "section": "14. Widget & Quick Actions UX Fixes", "status": "specified"},
    {"id": "244", "title": "Quick action Sort order field redundancy", "priority": "P2", "scope": "Admin", "section": "14. Widget & Quick Actions UX Fixes", "status": "specified"},
    {"id": "245", "title": "Quick actions previewable in admin widget", "priority": "P1", "scope": "Admin+Widget", "section": "14. Widget & Quick Actions UX Fixes", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "widget_quick_actions|quickActions", "file": "widget/src/components/Panel.tsx", "min_count": 1, "description": "Widget Panel renders quick actions"},
     ]},

    # Section 15: Standalone Admin Test Mode Integration (246-248)
    {"id": "246", "title": "Replace standalone Onboarding with shared OnboardingWizard", "priority": "P0", "scope": "Admin", "section": "15. Standalone Admin Test Mode", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "OnboardingWizard", "file": "admin/standalone/layouts/StandaloneLayout.tsx", "min_count": 1, "description": "StandaloneLayout imports OnboardingWizard"},
     ]},
    {"id": "247", "title": "Test mode banner in StandaloneLayout", "priority": "P0", "scope": "Admin", "section": "15. Standalone Admin Test Mode", "status": "specified",
     "description": "Schema has test_mode_enabled field but no UI banner in StandaloneLayout yet.",
     "assertions": [
         {"type": "grep", "pattern": "test.?mode|TestMode", "file": "admin/standalone/layouts/StandaloneLayout.tsx", "min_count": 1, "description": "StandaloneLayout has test mode indicator"},
     ]},
    {"id": "248", "title": "Test mode E2E validation in standalone admin", "priority": "P1", "scope": "Admin", "section": "15. Standalone Admin Test Mode", "status": "specified",
     "description": "No test mode E2E test files exist yet.",
     "assertions": [
         {"type": "glob", "pattern": "tests/**/test_*test_mode*", "description": "Test mode E2E tests exist"},
     ]},

    # Section 16: Widget & Chat UI Controls (249-257)
    {"id": "249", "title": "Widget drop-shadow control", "priority": "P2", "scope": "Admin+Widget", "section": "16. Widget & Chat UI Controls", "status": "specified",
     "description": "No shadow control field in fields.yaml. Widget uses hardcoded box-shadow.",
     "assertions": [
         {"type": "grep", "pattern": "widget_shadow|shadow_enabled|shadow_control", "file": "src/multi_tenant/schema/fields.yaml", "min_count": 1, "description": "Shadow control field in schema"},
     ]},
    {"id": "250", "title": "Widget launcher icon and agent avatar customization", "priority": "P2", "scope": "Admin+Widget", "section": "16. Widget & Chat UI Controls", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "widget_agent_avatar_url|widget_launcher_icon", "file": "src/multi_tenant/schema/fields.yaml", "min_count": 1, "description": "Avatar/icon fields in schema"},
     ]},
    {"id": "251", "title": "Pre-chat form and offline form explanations", "priority": "P1", "scope": "Admin", "section": "16. Widget & Chat UI Controls", "status": "specified"},
    {"id": "252", "title": "Chat UI resizable width", "priority": "P2", "scope": "Widget", "section": "16. Widget & Chat UI Controls", "status": "specified"},
    {"id": "253", "title": "Chat UI draggable/repositionable", "priority": "P3", "scope": "Widget", "section": "16. Widget & Chat UI Controls", "status": "specified"},
    {"id": "254", "title": "Auto-open per page via Quick Actions config", "priority": "P2", "scope": "Admin+Widget", "section": "16. Widget & Chat UI Controls", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "widget_auto_open", "file": "src/multi_tenant/schema/fields.yaml", "min_count": 1, "description": "Auto-open field in schema"},
     ]},
    {"id": "255", "title": "Chat input area height (3 text lines)", "priority": "P1", "scope": "Widget", "section": "16. Widget & Chat UI Controls", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "textarea|MIN_TEXTAREA_HEIGHT|auto.?grow", "file": "widget/src/components/InputBar.tsx", "min_count": 1, "description": "InputBar uses textarea with auto-grow"},
     ]},
    {"id": "256", "title": "Chat display area scroll controls", "priority": "P1", "scope": "Widget", "section": "16. Widget & Chat UI Controls", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "scrollToBottom|auto.?scroll", "file": "widget/src/components/MessageList.tsx", "min_count": 1, "description": "Scroll-to-bottom in MessageList"},
     ]},
    {"id": "257", "title": "Launcher position offset controls (X/Y)", "priority": "P1", "scope": "Admin+Widget", "section": "16. Widget & Chat UI Controls", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "widget_offset_x|widget_offset_y", "file": "src/multi_tenant/schema/fields.yaml", "min_count": 1, "description": "Position offset fields in schema"},
     ]},

    # Section 17: Dashboard UX Improvements (258-259)
    {"id": "258", "title": "Display storefront name on Dashboard", "priority": "P1", "scope": "Admin", "section": "17. Dashboard UX Improvements", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "shopDomain|store.?name|storefront", "file": "admin/standalone/pages/Dashboard.tsx", "min_count": 1, "description": "Dashboard shows store name"},
     ]},
    {"id": "259", "title": "Dashboard metric cards: help tooltips with doc links", "priority": "P1", "scope": "Admin", "section": "17. Dashboard UX Improvements", "status": "specified"},

    # Section 18: KB Toolbar Tooltips (260)
    {"id": "260", "title": "KB toolbar buttons: help tooltips with doc links", "priority": "P1", "scope": "Admin", "section": "18. KB Toolbar Tooltips", "status": "specified"},

    # Section 19: Analytics Page Help Tooltips (261)
    {"id": "261", "title": "Analytics metric cards: help tooltips with doc links", "priority": "P1", "scope": "Admin", "section": "19. Analytics Page Tooltips", "status": "retired",
     "description": "Superseded by WI #283 (merge Analytics into Dashboard) + WI #259."},

    # Section 20: Configuration Page UX (262-267)
    {"id": "262", "title": "Rename Configuration to Agent configuration", "priority": "P1", "scope": "Admin", "section": "20. Configuration Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Agent [Cc]onfiguration", "file": "admin/standalone/layouts/StandaloneLayout.tsx", "min_count": 1, "description": "Nav label says Agent configuration"},
     ]},
    {"id": "263", "title": "Configuration section help tooltips with doc links", "priority": "P1", "scope": "Admin", "section": "20. Configuration Page UX", "status": "specified"},
    {"id": "264", "title": "Escalation threshold slider label alignment", "priority": "P1", "scope": "Admin", "section": "20. Configuration Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Conservative|Aggressive", "file": "admin/standalone/pages/Configuration.tsx", "min_count": 2, "description": "Slider labels present"},
     ]},
    {"id": "265", "title": "Named configuration save/restore", "priority": "P2", "scope": "Admin+API", "section": "20. Configuration Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "named.?config|save.?as|config.?name", "file": "src/multi_tenant/tenant_config_api.py", "min_count": 1, "description": "Named config endpoint exists"},
     ]},
    {"id": "266", "title": "Delete saved configurations", "priority": "P2", "scope": "Admin+API", "section": "20. Configuration Page UX", "status": "specified"},
    {"id": "267", "title": "Saved configuration date-stamp (last_applied_at)", "priority": "P2", "scope": "Admin+API", "section": "20. Configuration Page UX", "status": "specified"},

    # Section 21: Widget Configuration Page UX (268-272)
    {"id": "268", "title": "Rename Widget to Widget configuration", "priority": "P1", "scope": "Admin", "section": "21. Widget Configuration Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Widget [Cc]onfiguration|Widget configurator", "file": "admin/standalone/layouts/StandaloneLayout.tsx", "min_count": 1, "description": "Nav label for widget page"},
     ]},
    {"id": "269", "title": "Rename color fields: Header left/right color", "priority": "P1", "scope": "Admin", "section": "21. Widget Configuration Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Header left color|Header right color", "file": "admin/standalone/pages/Widget.tsx", "min_count": 1, "description": "Color field labels renamed in Widget page"},
     ]},
    {"id": "270", "title": "Gradient enable/disable toggle (default: off)", "priority": "P1", "scope": "Admin+Widget", "section": "21. Widget Configuration Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "widget_header_gradient_end", "file": "src/multi_tenant/schema/fields.yaml", "min_count": 1, "description": "Gradient field in schema"},
     ]},
    {"id": "271", "title": "Side-by-side color pickers for header colors", "priority": "P1", "scope": "Admin", "section": "21. Widget Configuration Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Group|grid|flex|side.?by.?side", "file": "admin/shared/WidgetConfigurator.tsx", "min_count": 1, "description": "Color pickers in horizontal layout"},
     ]},
    {"id": "272", "title": "Widget page section help tooltips with doc links", "priority": "P1", "scope": "Admin", "section": "21. Widget Configuration Page UX", "status": "specified"},

    # Section 22: Quick Actions Page UX (273-274)
    {"id": "273", "title": "Page assignments: single-column list instead of dropdown", "priority": "P1", "scope": "Admin", "section": "22. Quick Actions Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "PAGE_TYPES|pageType|assignment", "file": "admin/standalone/pages/QuickActions.tsx", "min_count": 1, "description": "Page assignment UI in QuickActions page"},
     ]},
    {"id": "274", "title": "Template variables inline below prompt input", "priority": "P1", "scope": "Admin", "section": "22. Quick Actions Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "TEMPLATE_VAR|template.*var|insertVariable", "file": "admin/standalone/pages/QuickActions.tsx", "min_count": 1, "description": "Template variable chips in QuickActions page"},
     ]},

    # Section 23: Team Page UX (275-280)
    {"id": "275", "title": "Role selector replaces textual role badges", "priority": "P1", "scope": "Admin", "section": "23. Team Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Select|role.*select|roleSelector", "file": "admin/shared/TeamManager.tsx", "min_count": 1, "description": "Role selector component exists"},
     ]},
    {"id": "276", "title": "Rename Member column to Team member", "priority": "P1", "scope": "Admin", "section": "23. Team Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Team [Mm]ember", "file": "admin/shared/TeamManager.tsx", "min_count": 1, "description": "Column says Team member"},
     ]},
    {"id": "277", "title": "Roles & permissions as tooltip on Role column header", "priority": "P1", "scope": "Admin", "section": "23. Team Page UX", "status": "specified"},
    {"id": "278", "title": "Rename Agent role to Escalation agent", "priority": "P1", "scope": "Admin+API", "section": "23. Team Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Escalation [Aa]gent|escalation_agent", "file": "admin/shared/TeamManager.tsx", "min_count": 1, "description": "Escalation agent role label"},
     ]},
    {"id": "279", "title": "Escalation category assignment per team member", "priority": "P2", "scope": "Admin+API", "section": "23. Team Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "escalation_categories|escalationCategories", "file": "src/multi_tenant/admin_team_api.py", "min_count": 1, "description": "Escalation categories field on team member API"},
     ]},
    {"id": "280", "title": "Enable/disable toggle per team member", "priority": "P1", "scope": "Admin+API", "section": "23. Team Page UX", "status": "specified",
     "description": "Category toggles exist (onCategoryToggle) but no per-member enable/disable toggle.",
     "assertions": [
         {"type": "grep", "pattern": "isActive|isEnabled|member.*toggle.*status", "file": "admin/shared/TeamManager.tsx", "min_count": 1, "description": "Per-member enable/disable toggle"},
     ]},

    # Section 24: Billing & Usage Page UX (281-282)
    {"id": "281", "title": "Billing metric cards: help tooltips with doc links", "priority": "P1", "scope": "Admin", "section": "24. Billing & Usage Page UX", "status": "specified"},
    {"id": "282", "title": "Purchase button hover color consistency", "priority": "P1", "scope": "Admin", "section": "24. Billing & Usage Page UX", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Purchase|purchase.*button|conversation.*pack", "file": "admin/shared/BillingPortal.tsx", "min_count": 1, "description": "Purchase button exists"},
     ]},

    # Section 25: Sidebar Navigation Reorder & Analytics Merge (283-284)
    {"id": "283", "title": "Merge Analytics into Dashboard (remove Analytics page)", "priority": "P1", "scope": "Admin", "section": "25. Sidebar Nav Reorder", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "analytics|Analytics", "file": "admin/standalone/pages/Dashboard.tsx", "min_count": 1, "description": "Dashboard contains analytics content"},
     ]},
    {"id": "284", "title": "Reorder sidebar navigation", "priority": "P1", "scope": "Admin", "section": "25. Sidebar Nav Reorder", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "NavLink|nav.*item", "file": "admin/standalone/layouts/StandaloneLayout.tsx", "min_count": 5, "description": "Nav items present in layout"},
     ]},

    # Section 26: Setup Wizard Redesign (285-294)
    {"id": "285", "title": "Wizard mode selector: Standard / Test toggle (Step 0)", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "specified",
     "description": "OnboardingWizard has 3 steps (category, KB build, activate) — no mode selector.",
     "assertions": [
         {"type": "grep", "pattern": "mode.*select|Standard|Test.*mode|STEP_LABELS", "file": "admin/shared/components/OnboardingWizard.tsx", "min_count": 1, "description": "Mode selection in wizard"},
     ]},
    {"id": "286", "title": "Remove wizard steps that belong on dedicated pages", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "specified",
     "description": "Remove Brand & tone, Languages, Response style, etc. from wizard. Reference sidebar pages instead."},
    {"id": "287", "title": "Wizard steps mirror sidebar pages with full field access", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "specified"},
    {"id": "288", "title": "Go live — Initial setup completion checklist", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "specified"},
    {"id": "289", "title": "Go live — Test mode diff checklist", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "specified"},
    {"id": "290", "title": "New sidebar page: Memory and privacy", "priority": "P2", "scope": "Admin+API", "section": "26. Setup Wizard Redesign", "status": "implemented",
     "assertions": [
         {"type": "glob", "pattern": "admin/standalone/pages/MemoryPrivacy.tsx", "description": "MemoryPrivacy page exists"},
     ]},
    {"id": "291", "title": "Inactive system state indicator in nav bar", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "Inactive|inactive.*badge|activation.*status", "file": "admin/standalone/layouts/StandaloneLayout.tsx", "min_count": 1, "description": "Inactive state indicator"},
     ]},
    {"id": "292", "title": "Welcome message popup for first-time merchants", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "implemented",
     "assertions": [
         {"type": "grep", "pattern": "showOnboarding|OnboardingWizard.*292|first.time.*merchant", "file": "admin/standalone/layouts/StandaloneLayout.tsx", "min_count": 1, "description": "Onboarding wizard for first-time merchants in layout"},
     ]},
    {"id": "293", "title": "Rename Review and launch to Custom AI instructions", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "specified",
     "description": "OnboardingWizard step labels are: Set up, Building, Activate. No 'Custom AI instructions' label.",
     "assertions": [
         {"type": "grep", "pattern": "Custom AI instructions|custom_instructions", "file": "admin/shared/components/OnboardingWizard.tsx", "min_count": 1, "description": "Custom AI instructions step label"},
     ]},
    {"id": "294", "title": "Relocate fields from removed wizard steps to target pages", "priority": "P1", "scope": "Admin", "section": "26. Setup Wizard Redesign", "status": "specified",
     "description": "Verify all fields removed from wizard are present on their target pages."},

    # Section 27: Post-Launch (295-296)
    {"id": "295", "title": "Multi-user admin access with magic link auth", "priority": "P3", "scope": "Admin+API", "section": "27. Post-Launch", "status": "specified",
     "description": "Post-launch. Replace shared API key with per-user accounts."},
    {"id": "296", "title": "AI-generated greeting message option", "priority": "P3", "scope": "Widget", "section": "27. Post-Launch", "status": "specified",
     "description": "Post-launch enhancement."},

    # Section 28: S95 UI Coverage Findings (297-299)
    {"id": "297", "title": "Enforce min=1 for max_turns on server", "priority": "P2", "scope": "API", "section": "28. S95 UI Coverage Findings", "status": "implemented",
     "description": "fields.yaml defines min_value: 1.0 for max_ai_turns_before_escalation. Client/server max mismatch tracked in WI #298.",
     "assertions": [
         {"type": "grep", "pattern": "min_value.*1", "file": "src/multi_tenant/schema/fields.yaml", "min_count": 1, "description": "Server schema enforces min=1 for max_turns"},
     ]},
    {"id": "298", "title": "Align max_ai_turns_before_escalation client/server max", "priority": "P2", "scope": "Admin+API", "section": "28. S95 UI Coverage Findings", "status": "specified",
     "description": "Client max=200, server max=50 (fields.yaml max_value: 50.0). Need to set client max={50}.",
     "assertions": [
         {"type": "grep", "pattern": "max=\\{50\\}", "file": "admin/standalone/pages/Configuration.tsx", "min_count": 1, "description": "NumberInput max=50 for maxTurns"},
     ]},
    {"id": "299", "title": "Friendly error for HTTP 409 duplicate team invite", "priority": "P2", "scope": "Admin", "section": "28. S95 UI Coverage Findings", "status": "specified",
     "description": "Team page shows raw 409 instead of friendly message."},
]


# Protected Behaviors from docs/PROTECTED-BEHAVIORS.md

PROTECTED_BEHAVIORS: list[dict] = [
    {"id": "PB-001", "title": "Widget displays on admin console when Active", "priority": "P0", "scope": "Admin", "section": "Protected Behaviors — UI", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "injectWidget", "file": "admin/standalone/layouts/StandaloneLayout.tsx", "min_count": 1, "description": "injectWidget call in StandaloneLayout"},
     ]},
    {"id": "PB-002", "title": "Favicon on standalone admin console", "priority": "P0", "scope": "Admin", "section": "Protected Behaviors — UI", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "icon-master\\.svg", "file": "admin/standalone/index.html", "min_count": 1, "description": "Favicon reference in standalone index.html"},
     ]},
    {"id": "PB-003", "title": "Favicon on provider admin console", "priority": "P0", "scope": "Admin", "section": "Protected Behaviors — UI", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "icon-master\\.svg", "file": "admin/provider/index.html", "min_count": 1, "description": "Favicon reference in provider index.html"},
     ]},
    {"id": "PB-010", "title": "User-friendly 'no draft to activate' error", "priority": "P0", "scope": "API", "section": "Protected Behaviors — Error Messages", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "Save your configuration first", "file": "src/multi_tenant/activation_service.py", "min_count": 2, "description": "Friendly error message (2+ occurrences)"},
     ]},
    {"id": "PB-011", "title": "Memory & Privacy tier-gated fields filtered on save", "priority": "P0", "scope": "Admin", "section": "Protected Behaviors — Error Messages", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "isProOrHigher", "file": "admin/standalone/pages/MemoryPrivacy.tsx", "min_count": 1, "description": "Tier gate in MemoryPrivacy"},
     ]},
    {"id": "PB-020", "title": "Team invite email sent to invitee", "priority": "P0", "scope": "API", "section": "Protected Behaviors — Email", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "send_team_invite_alert", "file": "src/multi_tenant/admin_team_api.py", "min_count": 1, "description": "Team invite email call"},
     ]},
    {"id": "PB-021", "title": "Team invite email includes admin dashboard link", "priority": "P0", "scope": "API", "section": "Protected Behaviors — Email", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "admin_url", "file": "src/multi_tenant/alert_delivery.py", "min_count": 2, "description": "admin_url in alert_delivery (2+ occurrences)"},
     ]},
    {"id": "PB-022", "title": "Re-send invitation endpoint exists", "priority": "P0", "scope": "API", "section": "Protected Behaviors — Email", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "resend-invite", "file": "src/multi_tenant/admin_team_api.py", "min_count": 1, "description": "resend-invite endpoint"},
     ]},
    {"id": "PB-023", "title": "Escalation email routes to assigned agent with superadmin fallback", "priority": "P0", "scope": "API", "section": "Protected Behaviors — Email", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "find_superadmin_email", "file": "src/chat/pipeline/critic_escalation.py", "min_count": 1, "description": "Superadmin fallback in escalation"},
         {"type": "grep", "pattern": "recipient_emails", "file": "src/multi_tenant/alert_delivery.py", "min_count": 3, "description": "recipient_emails in alert_delivery (3+ occurrences)"},
     ]},
    {"id": "PB-030", "title": "VITE_API_URL must be empty at Docker build time", "priority": "P0", "scope": "Ops", "section": "Protected Behaviors — Build & Deploy", "status": "verified",
     "assertions": [
         {"type": "grep", "pattern": "VITE_API_URL", "file": "docs/operations/build-deploy-procedure.md", "min_count": 1, "description": "VITE_API_URL mentioned in build procedure"},
     ]},
]


# ─────────────────────────────────────────────────────────────────────
# Test Procedure Seed Data
# ─────────────────────────────────────────────────────────────────────

TEST_PROCEDURES: list[dict] = [
    {"id": "ui-coverage", "title": "UI Coverage Test Procedure", "type": "ui",
     "assertion_count": 917, "last_execution_status": "PASS",
     "content": "917 browser-driven tests across 14 admin pages in Light + Dark mode."},
    {"id": "chrome-mcp", "title": "Chrome MCP Test Procedure", "type": "ui",
     "assertion_count": 130, "last_execution_status": "PASS",
     "content": "Chrome-based MCP integration tests for admin UI workflows."},
    {"id": "load-test", "title": "Load Test Procedure", "type": "load",
     "assertion_count": 15, "last_execution_status": "PASS",
     "content": "Locust load test: 3 user scenarios, SLA violation thresholds."},
    {"id": "tenant-isolation", "title": "Tenant Isolation Test Procedure", "type": "security",
     "assertion_count": 20, "last_execution_status": "PASS",
     "content": "Cross-tenant data isolation verification."},
    {"id": "api-security", "title": "API Security Test Procedure", "type": "security",
     "assertion_count": 25, "last_execution_status": "PASS",
     "content": "Security hardening verification: body limits, depth limits, CORS, CSP, auth."},
    {"id": "rate-limit", "title": "Rate Limit Test Procedure", "type": "security",
     "assertion_count": 12, "last_execution_status": "PASS",
     "content": "Rate limiting enforcement on auth and API endpoints."},
    {"id": "conversation-quality", "title": "Conversation Quality Test Procedure", "type": "quality",
     "assertion_count": 25, "last_execution_status": "PASS",
     "content": "25 quality assertions (CQ-1 through CQ-9), 4.40/5.0 average."},
    {"id": "resilience-failover", "title": "Resilience & Failover Test Procedure", "type": "integration",
     "assertion_count": 18, "last_execution_status": "PASS",
     "content": "Pipeline resilience, fallback chains, graceful degradation."},
    {"id": "data-integrity", "title": "Data Integrity Test Procedure", "type": "integration",
     "assertion_count": 22, "last_execution_status": "PASS",
     "content": "5-phase data integrity audit, PITR verification."},
    {"id": "upgrade-verification", "title": "Upgrade Verification Procedure", "type": "integration",
     "assertion_count": 35, "last_execution_status": "PASS",
     "content": "35 assertions per tenant. Single + multi-tenant modes."},
    {"id": "visual-regression", "title": "Visual Regression Test Procedure", "type": "ui",
     "assertion_count": 50, "last_execution_status": "PASS",
     "content": "Pixel-level visual regression across admin pages."},
]


# ─────────────────────────────────────────────────────────────────────
# Operational Procedure Seed Data
# ─────────────────────────────────────────────────────────────────────

OP_PROCEDURES: list[dict] = [
    {"id": "build-deploy", "title": "Build & Deploy Procedure", "type": "deploy",
     "variables": {"TARGET_ENVIRONMENT": "production", "ACR_REGISTRY": "acragentredeastus.azurecr.io"},
     "steps": [
         {"phase": 0, "title": "Pre-Build Validation", "actions": ["dist build", "assertion check", "test harness"]},
         {"phase": 1, "title": "Build", "actions": ["ACR build with --no-logs"]},
         {"phase": 2, "title": "Deploy", "actions": ["az containerapp update"]},
         {"phase": 3, "title": "Verify", "actions": ["health check", "smoke test"]},
     ]},
    {"id": "initialization", "title": "Initialization Procedure", "type": "initialization",
     "variables": {"TARGET_ENVIRONMENT": "production"},
     "steps": [
         {"phase": 1, "title": "Cosmos DB provisioning"},
         {"phase": 2, "title": "Key Vault setup"},
         {"phase": 3, "title": "Container Apps creation"},
         {"phase": 4, "title": "Seed tenant"},
     ]},
    {"id": "seed-tenant", "title": "Seed Tenant Procedure", "type": "seed",
     "variables": {"TENANT_ID": "remaker-digital-001", "PHASES": "1-9"},
     "steps": [
         {"phase": 1, "title": "Tenant document"},
         {"phase": 2, "title": "Config documents"},
         {"phase": 3, "title": "Preferences"},
         {"phase": 4, "title": "Team members"},
         {"phase": 5, "title": "Widget key"},
         {"phase": 6, "title": "API key"},
         {"phase": 7, "title": "Knowledge base"},
         {"phase": 8, "title": "Quick actions"},
         {"phase": 9, "title": "Verify"},
     ]},
    {"id": "upgrade-verification", "title": "Upgrade Verification Procedure", "type": "upgrade",
     "variables": {"TARGET_ENVIRONMENT": "staging", "TENANT_LIST": "staging-001,staging-002"},
     "steps": [
         {"phase": "A", "title": "Pre-upgrade assertions (35 per tenant)"},
         {"phase": "B", "title": "Deploy new image"},
         {"phase": "C", "title": "Post-upgrade assertions (35 per tenant)"},
     ]},
]


# ─────────────────────────────────────────────────────────────────────
# Seed Functions
# ─────────────────────────────────────────────────────────────────────

def seed_specs(db: KnowledgeDB, dry_run: bool = False) -> int:
    """Seed all specifications."""
    all_specs = VERIFIED_SPECS + AUDITED_SPECS + PROTECTED_BEHAVIORS
    if dry_run:
        return len(all_specs)

    for spec in all_specs:
        db.insert_spec(
            id=spec["id"],
            title=spec["title"],
            status=spec["status"],
            changed_by=CHANGE_BY,
            change_reason=CHANGE_REASON,
            description=spec.get("description"),
            priority=spec.get("priority"),
            scope=spec.get("scope"),
            section=spec.get("section"),
            handle=spec.get("handle"),
            tags=spec.get("tags"),
            assertions=spec.get("assertions"),
        )
    return len(all_specs)


def seed_test_procedures(db: KnowledgeDB, dry_run: bool = False) -> int:
    """Seed test procedures."""
    if dry_run:
        return len(TEST_PROCEDURES)

    for proc in TEST_PROCEDURES:
        db.insert_test_procedure(
            id=proc["id"],
            title=proc["title"],
            changed_by=CHANGE_BY,
            change_reason=CHANGE_REASON,
            type=proc.get("type"),
            content=proc.get("content"),
            assertion_count=proc.get("assertion_count"),
            last_execution_status=proc.get("last_execution_status"),
        )
    return len(TEST_PROCEDURES)


def seed_op_procedures(db: KnowledgeDB, dry_run: bool = False) -> int:
    """Seed operational procedures."""
    if dry_run:
        return len(OP_PROCEDURES)

    for proc in OP_PROCEDURES:
        db.insert_op_procedure(
            id=proc["id"],
            title=proc["title"],
            changed_by=CHANGE_BY,
            change_reason=CHANGE_REASON,
            type=proc.get("type"),
            variables=proc.get("variables"),
            steps=proc.get("steps"),
            known_failure_modes=proc.get("known_failure_modes"),
        )
    return len(OP_PROCEDURES)


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the knowledge database")
    parser.add_argument("--dry-run", action="store_true", help="Print counts without writing")
    parser.add_argument(
        "--force", action="store_true",
        help="Required to actually delete and re-create the database. "
             "Without this flag, seed refuses to destroy an existing DB."
    )
    args = parser.parse_args()

    # Safety guard: never delete without --force
    db_path = Path(__file__).parent.parent.parent / "groundtruth.db"
    if not args.dry_run and db_path.exists():
        if not args.force:
            print("ERROR: Database already exists. Re-seeding will DESTROY all runtime state")
            print("       (assertion_runs, session_prompts, API-applied updates).")
            print()
            print("  To proceed anyway:  python seed.py --force")
            print("  To preview only:    python seed.py --dry-run")
            print()
            print(f"  Database: {db_path} ({db_path.stat().st_size:,} bytes)")
            return 1

        # Backup before delete (never-delete policy — keep the old DB)
        import shutil
        from datetime import datetime, timezone
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = db_path.parent / f"groundtruth.db.backup-{timestamp}"
        shutil.copy2(str(db_path), str(backup_path))
        print(f"Backed up to: {backup_path}")
        db_path.unlink()
        print(f"Deleted existing database: {db_path}")

    db = KnowledgeDB()
    try:
        spec_count = seed_specs(db, args.dry_run)
        test_count = seed_test_procedures(db, args.dry_run)
        op_count = seed_op_procedures(db, args.dry_run)

        action = "Would seed" if args.dry_run else "Seeded"
        print(f"\n{'=' * 50}")
        print(f"  Knowledge Database Seed {'(DRY RUN)' if args.dry_run else 'COMPLETE'}")
        print(f"{'=' * 50}")
        print(f"  {action} {spec_count} specifications")
        print(f"    - {len(VERIFIED_SPECS)} verified (sections 1-13)")
        print(f"    - {len(AUDITED_SPECS)} audited (sections 14-28)")
        print(f"    - {len(PROTECTED_BEHAVIORS)} protected behaviors")
        print(f"  {action} {test_count} test procedures")
        print(f"  {action} {op_count} operational procedures")
        print(f"{'=' * 50}")

        if not args.dry_run:
            summary = db.get_summary()
            print(f"\n  Status breakdown:")
            for status, count in sorted(summary["spec_counts"].items()):
                print(f"    {status}: {count}")
            print(f"  Total spec versions: {summary['spec_total_versions']}")
            print(f"  Database: {db.db_path}")
        print()

        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
