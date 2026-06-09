#!/usr/bin/env python3
"""S129: Create Test artifacts for 57 implemented/verified specs without linked tests.

Eliminates assertion orphans — every spec assertion is now visible to the
artifact system (test plans, coverage metrics, get_untested_specs()).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools", "knowledge-db"))
import db as kb

SESSION = "S129"
CHANGED_BY = f"claude/{SESSION}"
CHANGE_REASON = "GOV-12 compliance: link Test artifact to spec — eliminate assertion orphan"

# Starting TEST ID
NEXT_ID = 2798

# ─── Test definitions ───────────────────────────────────────────────────────
# Each tuple: (spec_id, title, test_type, expected_outcome, description)

TESTS = [
    # ── Cluster 1: Governance process rules (3) ──────────────────────────────
    (
        "GOV-10",
        "Verify GOV-10: Tests exercise production interfaces",
        "manual",
        "PASS when: every Test artifact in the KB references an observable production outcome (API response, UI element, metric value) — not source code inspection alone",
        "Abstract description test. GOV-10 requires that Test artifacts exercise exposed production interfaces. Source inspection tests are regression supplements, not Test artifacts. Verification: audit a sample of Test artifacts and confirm each specifies an observable outcome on a live/staging system.",
    ),
    (
        "GOV-11",
        "Verify GOV-11: Design decision checkpoint discipline",
        "manual",
        "PASS when: at each WI/phase completion boundary, implementation decisions are reviewed for spec coverage before proceeding (batched checkpoint, not real-time pause)",
        "Abstract description test. GOV-11 requires a design decision checkpoint at each WI/phase boundary. Verification: session transcripts show spec-coverage review at completion boundaries. 3 procedural assertions on the spec confirm the discipline structure.",
    ),
    (
        "GOV-12",
        "Verify GOV-12: Work item creation triggers test creation",
        "manual",
        "PASS when: (1) every new WI has a linked Test artifact before entering 'backlogged' stage, (2) _check_untested_work_items() in assertion-check.py reports no drift at session start",
        "Abstract description test. GOV-12 requires that creating a work item initiates test creation; the backlog initiates implementation. Verification: assertion-check.py drift detection at session start + audit of recent WIs for linked tests.",
    ),
    # ── Cluster 2: Co-Pilot design decisions (4) ────────────────────────────
    (
        "SPEC-1563",
        "Verify admin conversations are non-billable",
        "assertion",
        "PASS when: conversation_type='admin_assistance' conversations have is_billable=False in Cosmos persistence and are excluded from merchant billing metrics",
        "Structural/functional assertion test. Spec has 3 assertions (2 structural, 1 functional). Verifies that Co-Pilot admin conversations do not count toward tenant billing.",
    ),
    (
        "SPEC-1564",
        "Verify Co-Pilot bypasses Critic validation",
        "assertion",
        "PASS when: admin_assistance pipeline branch skips CriticSupervisorAgent (critic_passed=None in conversation record)",
        "Structural assertion test. Spec has 2 structural assertions. Co-Pilot responses are trusted admin content — Critic validation is unnecessary overhead.",
    ),
    (
        "SPEC-1565",
        "Verify admin API key query parameter authentication",
        "assertion",
        "PASS when: SSE/WebSocket connections with ?api_key=<valid_key> return HTTP 200, and requests without api_key return 401",
        "Structural/functional assertion test. Spec has 2 assertions (1 structural, 1 functional). Query param auth enables widget admin mode where header-based auth is unavailable.",
    ),
    (
        "SPEC-1566",
        "Verify admin widget Co-Pilot mode",
        "assertion",
        "PASS when: widget with data-admin-key attribute renders Co-Pilot branding, uses X-API-Key header for HTTP and api_key query param for SSE/WS, and sends conversation_type='admin_assistance'",
        "Structural assertion test. Spec has 6 structural assertions covering TransportConfig.adminApiKey, conditional auth, and branding overrides in StandaloneLayout.",
    ),
    # ── Cluster 3: Dashboard billable-only filtering (8) ────────────────────
    (
        "SPEC-1593",
        "Verify dashboard resolution rate excludes non-billable",
        "assertion",
        "PASS when: resolution rate Cosmos query includes is_billable filter and non-billable conversations do not affect the metric",
        "Grep assertion test. Spec asserts is_billable appears in the resolution rate query path.",
    ),
    (
        "SPEC-1594",
        "Verify dashboard conversation volume chart excludes non-billable",
        "assertion",
        "PASS when: volume chart Cosmos query filters on is_billable=true and chart shows single 'Conversations' line (not separate billable/non-billable)",
        "Grep assertion test. Spec asserts is_billable.*true pattern in volume chart query.",
    ),
    (
        "SPEC-1595",
        "Verify dashboard total conversations stat card excludes non-billable",
        "assertion",
        "PASS when: total conversations count query and display both filter on is_billable, showing only billable conversation count",
        "Grep assertion test. Spec has 2 assertions for is_billable filtering at query and display layers.",
    ),
    (
        "SPEC-1596",
        "Verify dashboard average response time excludes non-billable",
        "assertion",
        "PASS when: average response time Cosmos query includes is_billable filter",
        "Grep assertion test. Spec asserts is_billable appears in response time query path.",
    ),
    (
        "SPEC-1597",
        "Verify dashboard escalation rate excludes non-billable",
        "assertion",
        "PASS when: escalation rate Cosmos query includes is_billable filter",
        "Grep assertion test. Spec asserts is_billable appears in escalation rate query path.",
    ),
    (
        "SPEC-1598",
        "Verify dashboard top topics excludes non-billable",
        "assertion",
        "PASS when: top topics Cosmos query includes is_billable filter",
        "Grep assertion test. Spec asserts is_billable appears in top topics query path.",
    ),
    (
        "SPEC-1599",
        "Verify dashboard recent conversations excludes non-billable",
        "assertion",
        "PASS when: recent conversations list query and frontend filter both exclude non-billable conversations (isBillable !== false)",
        "Grep assertion test. Spec has 2 assertions for is_billable filtering at query and frontend layers.",
    ),
    (
        "SPEC-1600",
        "Verify dashboard topic breakdown excludes non-billable",
        "assertion",
        "PASS when: topic breakdown table Cosmos query includes is_billable filter",
        "Grep assertion test. Spec asserts is_billable appears in topic breakdown query path.",
    ),
    # ── Cluster 4: AGNTCY infrastructure (16) ───────────────────────────────
    (
        "SPEC-1516",
        "Verify 680-merchant scale target in configuration",
        "assertion",
        "PASS when: grep finds '680' in scale-related configuration files (Locust config, load test, spec references)",
        "Grep assertion test. Spec has 3 grep assertions for '680' across config and test files.",
    ),
    (
        "SPEC-1517",
        "Verify MCP and AGNTCY/SLIM transport centrality",
        "assertion",
        "PASS when: grep finds 'slim' and 'agntcy' references confirming these are wired as transport layers, not optional features",
        "Grep assertion test. Spec has 2 grep assertions for slim and agntcy presence in source.",
    ),
    (
        "SPEC-1534",
        "Verify AGNTCY SDK mandatory for all agent communication",
        "assertion",
        "PASS when: (1) AgntcyFactory present, (2) create_mcp_client used, (3) no 'relaxation' bypass language exists, (4) USE_AGENT_CONTAINERS defaults true",
        "Grep assertion test. Spec has 4 assertions (3 grep, 1 grep_absent) ensuring AGNTCY SDK is the sole agent communication path.",
    ),
    (
        "SPEC-1535",
        "Verify containerized agent deployment",
        "assertion",
        "PASS when: (1) container app files exist at src/agents/containers/*_app.py, (2) /health endpoints defined, (3) USE_AGENT_CONTAINERS=true, (4) _transport_available fallback logic present",
        "Glob/grep assertion test. Spec has 4 assertions (1 glob, 3 grep) for container deployment infrastructure.",
    ),
    (
        "SPEC-1536",
        "Verify A2A transport for all agent communication",
        "assertion",
        "PASS when: intent-classifier, knowledge-retrieval, create_a2a_client, and SLIM|NATS references all present in source",
        "Grep assertion test. Spec has 4 grep assertions confirming A2A transport wiring for each agent.",
    ),
    (
        "SPEC-1537",
        "Verify streaming response generation over transport",
        "assertion",
        "PASS when: /generate/stream endpoint and _transport_available check both present in response generation code",
        "Grep assertion test. Spec has 2 grep assertions for streaming transport capability.",
    ),
    (
        "SPEC-1538",
        "Verify pipeline behavior preservation after decomposition",
        "assertion",
        "PASS when: INTENT_TAXONOMY and CriticSupervisorAgent both present — full pipeline preserved after transport decomposition",
        "Grep assertion test. Spec has 2 grep assertions confirming pipeline integrity.",
    ),
    (
        "SPEC-1539",
        "Verify per-agent OpenTelemetry spans",
        "assertion",
        "PASS when: pipeline.process root span, trace_agent_operation helper, and ATTR_AGENT attribute all present in source",
        "Grep assertion test. Spec has 3 grep assertions for OTel tracing infrastructure.",
    ),
    (
        "SPEC-1540",
        "Verify token usage and cost attribution",
        "assertion",
        "PASS when: ATTR_LLM_PROMPT_TOKENS, calculate_llm_cost, and ATTR_LLM_COST_USD all present in source",
        "Grep assertion test. Spec has 3 grep assertions for cost attribution model.",
    ),
    (
        "SPEC-1541",
        "Verify execution tree reconstruction",
        "assertion",
        "PASS when: pipeline.process root span and trace_agent_operation present — enabling execution tree reconstruction from OTel data",
        "Grep assertion test. Spec has 2 grep assertions for trace tree capability.",
    ),
    (
        "SPEC-1542",
        "Verify tracing latency requirement",
        "assertion",
        "PASS when: BatchSpanProcessor is used (not SimpleSpanProcessor) — ensuring async span export does not add request latency",
        "Grep assertion test. Spec has 1 grep assertion for BatchSpanProcessor.",
    ),
    (
        "SPEC-1543",
        "Verify PII tokenization before external AI calls",
        "assertion",
        "PASS when: pii_tokenizer.py exists and is imported/called before agent dispatch in the pipeline",
        "Glob/grep assertion test. Spec has 2 assertions (1 glob, 1 grep) for PII tokenization infrastructure.",
    ),
    (
        "SPEC-1544",
        "Verify PII detokenization before customer response",
        "assertion",
        "PASS when: detokenize function is called after Critic validation, ensuring PII tokens are replaced with original values before customer sees the response",
        "Grep assertion test. Spec has 2 grep assertions for detokenize at two pipeline stages.",
    ),
    (
        "SPEC-1545",
        "Verify PII token mapping storage",
        "assertion",
        "PASS when: PiiTokenMappingDocument defined in cosmos_schema.py with TTL configuration for automatic expiry",
        "Grep assertion test. Spec has 2 grep assertions for PiiTokenMappingDocument and ttl.",
    ),
    (
        "SPEC-1546",
        "Verify PII tokenization entity detection",
        "assertion",
        "PASS when: tokenizer detects email, phone, and order number patterns in customer messages",
        "Grep assertion test. Spec has 3 grep assertions for email, phone, and order entity detection.",
    ),
    (
        "SPEC-1567",
        "Verify Shopify app configuration matches Dev Dashboard",
        "assertion",
        "PASS when: shopify.app.toml contains correct app URL, redirect URLs, GDPR endpoints, and scopes matching the active Dev Dashboard version",
        "Grep assertion test. Spec has 4 grep assertions for Shopify configuration values.",
    ),
    # ── Cluster 5: Visual regression baselines (26) ─────────────────────────
    (
        "VR-agentconfig-s0-topleft",
        "Verify agent config page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 7 visual assertions for the agent configuration page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 7 assertions verify layout, content, and styling of the agent configuration page's primary content area.",
    ),
    (
        "VR-billing-s0-topleft",
        "Verify billing page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 7 visual assertions for the billing & usage page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 7 assertions verify layout, content, and styling of the billing page's primary content area.",
    ),
    (
        "VR-dashboard-s0-topleft",
        "Verify dashboard page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 7 visual assertions for the dashboard page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 7 assertions verify layout, content, and styling of the dashboard's primary content area.",
    ),
    (
        "VR-inbox-s0-topleft",
        "Verify inbox page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 6 visual assertions for the inbox page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 6 assertions verify layout, content, and styling of the inbox page's primary content area.",
    ),
    (
        "VR-integrations-s0-topleft",
        "Verify integrations page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 7 visual assertions for the integrations page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 7 assertions verify layout, content, and styling of the integrations page's primary content area.",
    ),
    (
        "VR-knowledgebase-s0-topleft",
        "Verify knowledge base page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 7 visual assertions for the knowledge base page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 7 assertions verify layout, content, and styling of the knowledge base page's primary content area.",
    ),
    (
        "VR-memoryprivacy-s0-topleft",
        "Verify memory & privacy page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 7 visual assertions for the memory & privacy page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 7 assertions verify layout, content, and styling of the memory & privacy page's primary content area.",
    ),
    (
        "VR-quickactions-s0-topleft",
        "Verify quick actions page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 6 visual assertions for the quick actions page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 6 assertions verify layout, content, and styling of the quick actions page's primary content area.",
    ),
    (
        "VR-shared-style",
        "Verify shared admin UI style baseline",
        "assertion",
        "PASS when: all 9 visual assertions for the shared admin UI style (applies to all standalone admin pages) match the verified baseline",
        "Visual assertion test. 9 assertions verify cross-page styling: fonts, colors, spacing, sidebar, header, and responsive behavior.",
    ),
    (
        "VR-team-s0-topleft",
        "Verify team members page visual baseline: top-left quadrant",
        "assertion",
        "PASS when: all 7 visual assertions for the team members page top-left content quadrant (240,56)-(640,351) match the verified baseline",
        "Visual assertion test. 7 assertions verify layout, content, and styling of the team page's primary content area.",
    ),
    (
        "VR-widget-s0-appearance-start",
        "Verify widget page visual baseline: appearance section start",
        "assertion",
        "PASS when: all 3 visual assertions for the widget page appearance section start (240,600)-(830,702) match the verified baseline",
        "Visual assertion test. 3 assertions verify the beginning of the widget appearance configuration section.",
    ),
    (
        "VR-widget-s0-embed-code",
        "Verify widget page visual baseline: embed code region",
        "assertion",
        "PASS when: all 3 visual assertions for the widget page embed code region (240,400)-(540,600) match the verified baseline",
        "Visual assertion test. 3 assertions verify the embed code display area of the widget configuration page.",
    ),
    (
        "VR-widget-s0-header-center",
        "Verify widget page visual baseline: header center",
        "assertion",
        "PASS when: all 2 visual assertions for the widget page header center region (240,0)-(640,56) match the verified baseline",
        "Visual assertion test. 2 assertions verify the center header area of the widget configuration page.",
    ),
    (
        "VR-widget-s0-header-left",
        "Verify widget page visual baseline: header left",
        "assertion",
        "PASS when: all 5 visual assertions for the widget page header left region (0,0)-(240,56) match the verified baseline",
        "Visual assertion test. 5 assertions verify the left header area (logo, navigation) of the widget configuration page.",
    ),
    (
        "VR-widget-s0-header-right",
        "Verify widget page visual baseline: header right",
        "assertion",
        "PASS when: all 5 visual assertions for the widget page header right region (850,0)-(1280,56) match the verified baseline",
        "Visual assertion test. 5 assertions verify the right header area (actions, profile) of the widget configuration page.",
    ),
    (
        "VR-widget-s0-install-body",
        "Verify widget page visual baseline: installation card body",
        "assertion",
        "PASS when: all 5 visual assertions for the widget page installation card body (240,200)-(540,400) match the verified baseline",
        "Visual assertion test. 5 assertions verify the installation instructions card body content.",
    ),
    (
        "VR-widget-s0-install-right",
        "Verify widget page visual baseline: installation card right side",
        "assertion",
        "PASS when: all 4 visual assertions for the widget page installation card right side (540,200)-(830,400) match the verified baseline",
        "Visual assertion test. 4 assertions verify the right portion of the installation card (preview, status).",
    ),
    (
        "VR-widget-s0-layout",
        "Verify widget page visual baseline: two-column layout",
        "assertion",
        "PASS when: all 5 visual assertions for the widget page two-column layout structure match the verified baseline (production v1.61.0)",
        "Visual assertion test. 5 assertions verify the overall two-column layout: config panel left, preview panel right.",
    ),
    (
        "VR-widget-s0-nav-bottom",
        "Verify widget page visual baseline: navbar bottom",
        "assertion",
        "PASS when: all 4 visual assertions for the widget page navbar bottom region (0,490)-(240,702) match the verified baseline",
        "Visual assertion test. 4 assertions verify the bottom navigation area (secondary links, version info).",
    ),
    (
        "VR-widget-s0-nav-mid",
        "Verify widget page visual baseline: navbar middle",
        "assertion",
        "PASS when: all 4 visual assertions for the widget page navbar middle region (0,256)-(240,490) match the verified baseline",
        "Visual assertion test. 4 assertions verify the middle navigation area (page links, active states).",
    ),
    (
        "VR-widget-s0-nav-top",
        "Verify widget page visual baseline: navbar top",
        "assertion",
        "PASS when: all 6 visual assertions for the widget page navbar top region (0,56)-(240,256) match the verified baseline",
        "Visual assertion test. 6 assertions verify the top navigation area (brand, primary links).",
    ),
    (
        "VR-widget-s0-preview-chat",
        "Verify widget page visual baseline: preview chat area",
        "assertion",
        "PASS when: all 4 visual assertions for the widget page live preview chat area (830,256)-(1130,456) match the verified baseline",
        "Visual assertion test. 4 assertions verify the live preview chat message area.",
    ),
    (
        "VR-widget-s0-preview-fab",
        "Verify widget page visual baseline: preview FAB/launcher",
        "assertion",
        "PASS when: all 3 visual assertions for the widget page preview FAB/launcher (1130,620)-(1280,702) match the verified baseline",
        "Visual assertion test. 3 assertions verify the floating action button (launcher) in the live preview panel.",
    ),
    (
        "VR-widget-s0-preview-header",
        "Verify widget page visual baseline: preview panel header",
        "assertion",
        "PASS when: all 4 visual assertions for the widget page live preview panel header (830,56)-(1130,256) match the verified baseline",
        "Visual assertion test. 4 assertions verify the preview panel header (brand, title, close button).",
    ),
    (
        "VR-widget-s0-preview-input",
        "Verify widget page visual baseline: preview input area",
        "assertion",
        "PASS when: all 4 visual assertions for the widget page live preview input area (830,456)-(1130,656) match the verified baseline",
        "Visual assertion test. 4 assertions verify the preview panel input field and send button.",
    ),
    (
        "VR-widget-s0-title",
        "Verify widget page visual baseline: page title region",
        "assertion",
        "PASS when: all 5 visual assertions for the widget page title region (240,56)-(540,200) match the verified baseline",
        "Visual assertion test. 5 assertions verify the page title, subtitle, and action buttons at the top of the widget configuration page.",
    ),
]


def main():
    """Insert all 57 Test artifacts."""
    database = kb.KnowledgeDB()
    created = 0
    errors = 0

    for i, (spec_id, title, test_type, expected_outcome, description) in enumerate(TESTS):
        test_id = f"TEST-{NEXT_ID + i:04d}"
        try:
            result = database.insert_test(
                id=test_id,
                title=title,
                spec_id=spec_id,
                test_type=test_type,
                expected_outcome=expected_outcome,
                changed_by=CHANGED_BY,
                change_reason=CHANGE_REASON,
                description=description,
            )
            print(f"  OK  {test_id} -> {spec_id}: {title[:60]}")
            created += 1
        except Exception as e:
            print(f"  ERR {test_id} -> {spec_id}: {e}")
            errors += 1

    print(f"\n{'=' * 60}")
    print(f"Created: {created}/{len(TESTS)}")
    print(f"Errors:  {errors}")
    print(f"ID range: TEST-{NEXT_ID:04d} through TEST-{NEXT_ID + len(TESTS) - 1:04d}")
    print(f"{'=' * 60}")

    # Verify by querying untested specs
    untested = database.get_untested_specs()
    untested_impl = [s for s in untested if s.get("status") in ("implemented", "verified")]
    print(f"\nRemaining untested implemented/verified specs: {len(untested_impl)}")
    if untested_impl:
        for s in untested_impl:
            print(f"  {s['id']}: {s.get('title', '?')[:60]}")


if __name__ == "__main__":
    main()
