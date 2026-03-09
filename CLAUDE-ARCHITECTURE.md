# CLAUDE-ARCHITECTURE.md — Project Structure & Module Inventory

> This file contains the project directory tree and module inventory. Read it on demand when navigating the codebase, investigating module relationships, or planning changes that touch multiple files.
>
> For active project guidance, see `CLAUDE.md`. For static reference data, see `CLAUDE-REFERENCE.md`.

---

## Project Structure

```
E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\
│
├── CLAUDE.md                       # AI assistant guidance (core, loaded every session)
├── CLAUDE-REFERENCE.md             # Static reference: legal, pricing, infra, AGNTCY rules
├── CLAUDE-ARCHITECTURE.md          # This file: project structure, module inventory
├── CLAUDE_ARCHIVE.md               # Historical session logs and detailed technical decisions
├── README.md                       # Project overview
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .env.local                      # Local credentials (git-ignored): Stripe, Shopify, env vars
├── package.json                    # Root package.json for Shopify CLI
├── shopify.app.toml                # Shopify Partner app config (client_id, scopes, GDPR URLs)
│
├── config/                         # Configuration files
│   └── stripe_product_ids.json     # Stripe test-mode product/price IDs (27 objects)
│
├── src/                            # Commercial source code
│   ├── __init__.py
│   ├── main.py                     # FastAPI app entrypoint (44 routers, ~140+ routes, 9 middleware, ~1,000 lines)
│   ├── integrations/               # Billing & platform integrations
│   │   ├── __init__.py
│   │   ├── provisioning.py         # Channel-agnostic tenant provisioning service
│   │   ├── stripe_catalog.py       # Typed Pydantic models for Stripe product catalog
│   │   ├── stripe_checkout.py      # Stripe Checkout session management + Rewardful referral
│   │   ├── stripe_packs.py         # Conversation pack purchase & FIFO balance tracking
│   │   ├── stripe_portal.py        # Stripe Customer Portal session management
│   │   ├── stripe_usage.py         # Metered usage reporting (3-tier: included→packs→overage)
│   │   ├── stripe_webhooks.py      # Stripe webhook handler (7 events → provisioning + tax)
│   │   ├── shopify_client.py       # Async Shopify GraphQL API client (httpx)
│   │   ├── shopify_billing.py      # Shopify Billing API (subscriptions + usage charges)
│   │   └── shopify_gdpr_webhooks.py # Shopify GDPR mandatory webhooks (3 endpoints, HMAC verification)
│   ├── multi_tenant/               # Multi-tenant infrastructure (89 modules + 16 repositories, ~55,000+ lines)
│   │   ├── __init__.py             # Package init with import hints
│   │   ├── cosmos_schema.py        # 20 collections, 12+ document models, 8 enums, tier defaults (incl. trial)
│   │   ├── cosmos_client.py        # CosmosManager singleton (lazy init, Managed Identity, health)
│   │   ├── repository.py           # TenantScopedRepository + 10 collection repositories
│   │   ├── auth.py                 # Triple auth: Shopify JWT + API key + publishable widget key
│   │   ├── middleware.py           # TenantAuthMiddleware + RateLimitMiddleware (with headers) + dependencies
│   │   ├── conversation_meter.py   # ConversationMeter: billable conv spec, 3-tier metering, alerts
│   │   ├── critic_policy.py        # Fail-closed Critic enforcement, circuit breaker, health
│   │   ├── nats_isolation.py       # NATS tenant isolation, topic namespace, subscription auth
│   │   ├── gdpr_services.py        # PII scrubbing, data export/deletion, consent management
│   │   ├── otel_tracing.py         # OpenTelemetry tenant tracing, correlation ID propagation
│   │   ├── pipeline_resilience.py  # Per-tenant concurrency, timeout budgets, circuit breakers
│   │   ├── system_prompt_builder.py # Dynamic per-agent prompt assembly (4-layer)
│   │   ├── usage_dashboard_api.py  # Billing transparency REST API (Decision #25)
│   │   ├── tenant_config_schema.py # Tenant config validation, onboarding model
│   │   ├── tenant_config_processor.py # Config merge: platform → tier → tenant overrides
│   │   ├── tenant_config_api.py    # Config REST API (12+ endpoints, /api/config)
│   │   ├── tenant_secret_service.py # Key Vault per-tenant secret management
│   │   ├── customer_profile_service.py # Layer 1 customer profile CRUD, Shopify sync, identity extraction
│   │   ├── conversation_vectorizer.py # Layer 2 vectorization pipeline, semantic search
│   │   ├── response_explainability.py # Per-response decision trace, explainability framework
│   │   ├── admin_conversation_api.py # Conversation inbox admin API (5 endpoints, escalate email)
│   │   ├── admin_knowledge_api.py  # Knowledge base CRUD + upload + scan admin API (13 endpoints)
│   │   ├── admin_analytics_api.py  # Analytics summary/topics/gaps admin API (3 endpoints)
│   │   ├── admin_team_api.py       # Team member management admin API (5 endpoints)
│   │   ├── admin_gdpr_api.py       # GDPR data export/deletion/consent admin API (5 endpoints)
│   │   ├── admin_audit_api.py      # Audit log query + CSV export admin API (2 endpoints)
│   │   ├── tenant_usage_monitor.py # Progressive throttling (Watch→Warn→Throttle→Isolate)
│   │   ├── security_middleware.py  # Body size limit, JSON depth, security headers, SLA latency recording
│   │   ├── api_versioning.py       # API version headers middleware (X-API-Version)
│   │   ├── structured_logging.py   # JSON structured logging (prod) + colored dev formatter
│   │   ├── activation_service.py   # Save→Activate two-phase commit: draft, activate, restore (~757 lines)
│   │   ├── trial_management.py     # Trial tier lifecycle, expiry, conversion, demo data (~1,200 lines)
│   │   ├── security_hardening.py   # Input sanitization, CORS, CSP, session validation (~570 lines)
│   │   ├── data_retention.py       # Tier-based data retention enforcement (~380 lines)
│   │   ├── sla_monitoring.py       # P50/P95/P99 latency tracking, uptime, compliance (~390 lines)
│   │   ├── cost_model.py           # Parameterized cost model calculator, projections (~370 lines)
│   │   ├── archival_pipeline.py    # Hot→Warm Parquet archival to Azure Blob Storage (~750 lines)
│   │   ├── alert_delivery.py       # Multi-channel alert routing: webhook, dashboard, email, log (~695 lines)
│   │   ├── pattern_extraction.py   # Layer 3 cross-session learning, pattern decay (~1,060 lines)
│   │   ├── fine_tuning_pipeline.py # Layer 4 fine-tuning pipeline, quality gates, A/B (~1,870 lines)
│   │   ├── admin_customer_profile_api.py # Customer profile admin API (~450 lines)
│   │   ├── admin_apikey_api.py     # API key management: generate, rotate, revoke, reset (~350 lines)
│   │   ├── admin_quick_action_api.py # Quick action CRUD + seed endpoint (~400 lines)
│   │   ├── knowledge_vectorizer.py # KB embedding pipeline, hybrid search (BM25+vector+RRF) (~520 lines)
│   │   ├── document_parser.py     # Document upload parsing: PDF, DOCX, CSV, TXT, HTML (~480 lines)
│   │   ├── staleness_service.py   # KB entry staleness detection + scoring (~540 lines)
│   │   ├── semantic_cache.py      # 3-tier semantic cache: embedding, search, response (~530 lines)
│   │   ├── kb_conflict_scanner.py # KB conflict/duplication scanner: 4-phase detection (~705 lines)
│   │   ├── superadmin_api.py      # SPA provider ops API: tenant directory, dashboard, billing, deploys, user management (~700+ lines)
│   │   ├── mcp_client.py          # MCP client: AgentRedMcpClient, config models, shop_domain guard, policy gate, PII scrub (~650 lines)
│   │   ├── mcp_credential_cache.py # In-memory credential cache: 5-min TTL, double-check locking, Key Vault backend (~270 lines)
│   │   ├── mutation_policy.py     # MutationPolicy, MutationRequest, MutationResult, evaluate_request (~230 lines)
│   │   ├── mutation_executor.py   # Critic-gated 6-stage mutation executor: policy→idempotency→Critic→confirm→execute→log (~310 lines)
│   │   ├── login_notification.py  # Non-blocking SPA login notification emails (SPEC-1676)
│   │   ├── spa_recovery.py        # SPA emergency key recovery via backup codes (SPEC-1678)
│   │   ├── tenant_recovery.py     # Tenant account recovery: recovery address + one-time auth links (SPEC-1677)
│   │   ├── tenant_name.py         # TenantName value object: human-readable slug generation from email domain
│   │   └── repositories/          # Collection-specific repository classes (16 modules)
│   │       ├── __init__.py
│   │       ├── base.py            # TenantScopedRepository base class
│   │       ├── platform_admin.py  # PlatformAdminRepository (platform_admins collection, SPEC-1667)
│   │       ├── platform.py        # PlatformScopedRepository
│   │       ├── tenant.py          # TenantRepository
│   │       ├── team.py            # TeamRepository
│   │       ├── conversation.py    # ConversationRepository
│   │       ├── knowledge.py       # KnowledgeRepository
│   │       ├── customer.py        # CustomerRepository
│   │       ├── memory.py          # MemoryRepository
│   │       ├── preferences.py     # PreferencesRepository
│   │       ├── usage.py           # UsageRepository
│   │       ├── alerts.py          # AlertsRepository
│   │       ├── incidents.py       # IncidentsRepository
│   │       ├── sla_snapshots.py   # SlaSnapshotsRepository
│   │       └── verification.py    # VerificationRepository
│   ├── chat/                       # Chat API
│   │   ├── __init__.py
│   │   ├── models.py              # Request/response Pydantic models + StreamEvent SSE format (~200 lines)
│   │   ├── session.py             # Conversation lifecycle management (~350 lines)
│   │   ├── pipeline.py            # 6-agent pipeline orchestrator via A2A agent delegation + SSE streaming (~800 lines)
│   │   ├── endpoints.py           # 6 FastAPI routes: conversations, message, stream, end, WS (~350 lines)
│   │   └── sse_manager.py         # SSE connection manager: heartbeat, reconnection, tenant limits (~280 lines)
│   ├── agents/                    # AGNTCY-compatible agent modules (Phase 2, session 25)
│   │   ├── __init__.py
│   │   ├── base.py               # AgentRedBaseAgent ABC + A2A message utilities (~150 lines)
│   │   ├── intent_classifier.py  # Intent classification agent (~130 lines)
│   │   ├── knowledge_retrieval.py # Knowledge retrieval agent: hybrid + keyword fallback + MCP augmentation (~400 lines, extended session 36-37)
│   │   ├── response_generator.py # Response generation agent: streaming + non-streaming (~199 lines)
│   │   ├── escalation_handler.py # Escalation detection agent (~140 lines)
│   │   ├── analytics_collector.py # Analytics collection agent (~85 lines)
│   │   ├── critic_supervisor.py  # Critic/supervisor agent: fail-closed validation (~235 lines)
│   │   └── containers/           # Container deployment infrastructure
│   │       ├── __init__.py
│   │       ├── Dockerfile        # Generic Dockerfile with AGENT_MODULE build arg
│   │       ├── agent_app.py      # FastAPI app factory: health/ready/process + NATS subscription (~221 lines)
│   │       ├── intent_classifier_app.py     # Container entry point
│   │       ├── knowledge_retrieval_app.py   # Container entry point
│   │       ├── response_generator_app.py    # Container entry point
│   │       ├── escalation_handler_app.py    # Container entry point
│   │       ├── analytics_collector_app.py   # Container entry point
│   │       └── critic_supervisor_app.py     # Container entry point
│   ├── jobs/                       # Scheduled job entry points (Azure Container App Jobs)
│   │   ├── __init__.py
│   │   ├── run_retention.py        # Cron entry: data retention enforcement (03:00 UTC daily)
│   │   └── run_archival.py         # Cron entry: archival pipeline (04:00 UTC daily)
│   ├── ai-features/                # Advanced AI (Phase 2.5)
│   └── white-label/                # Customization (future)
│
├── tests/                          # Test suites (5,984 offline tests, 936 live E2E, 0 failures)
│   ├── conftest.py                 # Shared fixtures: TestClient, MockCosmos, MockNATS, MockKV, auth helpers
│   ├── test_conftest_smoke.py      # Fixture smoke tests
│   ├── test_health.py              # Health/ready endpoint tests
│   ├── persistent_memory/          # Persistent Customer Memory tests
│   ├── multi_tenant/               # Multi-tenant infrastructure tests
│   ├── integrations/               # Billing integration tests
│   ├── security/                   # Adversarial/security tests
│   ├── performance/                # Performance/load tests + Locust config
│   ├── chat/                       # SSE/streaming tests
│   ├── agents/                    # AGNTCY agent module tests
│   ├── regression/                 # 73 regression tests (3-tier upgrade validation)
│   ├── e2e_live/                    # Live E2E Playwright tests (936 tests: standalone 576, provider 264, shopify 96)
│   └── integration/                # Azure service integration tests
│
├── widget/                         # Chat widget frontend (Preact + TypeScript, ~17KB gzip)
├── prototype/                      # Admin dashboard prototype (Mantine + Polaris, owner-approved)
├── extensions/                     # Shopify Theme App Extension
├── admin/                          # Admin dashboard frontends
│   ├── shared/                     # Shared components + hooks + types
│   ├── shopify/                    # Shopify embedded admin (Polaris + App Bridge)
│   ├── standalone/                 # Standalone admin (API key login)
│   └── provider/                   # Provider Console SPA (20 pages, Mantine + Recharts)
│
├── infrastructure/terraform/       # IaC for Azure
├── website/content/                # Marketing website content
├── docs/                           # Documentation (architecture, research, operations, shopify, guides, api)
├── docs-site/                      # Docusaurus documentation site (https://agentredcx.com)
├── branding/                       # Brand assets (logo, colors, guidelines)
├── legal/                          # Legal documents (terms, privacy, contracts)
└── scripts/                        # Automation (setup, stripe, build, deploy)
```

---

## Key Documents

| Document | Location | Purpose |
|----------|----------|---------|
| CLAUDE.md | Root | AI assistant guidance (core) |
| CLAUDE-REFERENCE.md | Root | Static reference: legal, pricing, infra, AGNTCY |
| CLAUDE-ARCHITECTURE.md | Root | This file: structure, modules |
| CLAUDE_ARCHIVE.md | Root | Historical session logs |
| PROJECT-PLAN.md | docs/ | Launch 1.0 milestones and tasks |
| APP-STORE-LISTING.md | docs/shopify/ | Shopify App Store listing copy, asset specs |
| COMPETITOR-COMPARISON.md | docs/shopify/ | Agent Red vs 5 competitors |
| **SHOPIFY-APP-REVIEW-PREFLIGHT-CHECKLIST.md** | **docs/operations/** | **Canonical checklist** for Shopify submission |
| LAUNCH-CHECKLIST.md | docs/operations/ | 10-step launch process (owner tasks) |
| DEPLOYMENT-RUNBOOK.md | docs/operations/ | Deployment procedure, DR, maintenance |
| UPGRADE-RUNBOOK-1.0-TO-1.1.md | docs/operations/ | Non-disruptive upgrade procedure |
| COMPREHENSIVE-TEST-PLAN.md | docs/ | ~880 enumerated tests |
| BACKLOG-NEW-WORK-ITEMS.md | docs/ | Work items backlog (WI #101-225) |
| Master-Plan-Review-01-30-2026.md | docs/ | Architecture review: 32 decisions |

---

## Artifact Inventory (SPEC-1493)

The project maintains exactly **9 managed artifact types** and **2 supporting record types**, all stored in the Knowledge Database (`tools/knowledge-db/knowledge.db`).

| # | Artifact | Table | Purpose |
|---|----------|-------|---------|
| 1 | **Specification** | `specifications` | Testable description of system behavior or content |
| 2 | **Test** | `tests` | Individual testable assertion derived from a specification |
| 3 | **Test Plan** | `test_plans` + `test_plan_phases` | Ordered test phases with gate criteria |
| 4 | **Work Item** | `work_items` | Unit of work: regression, defect, or new capability |
| 5 | **Backlog** | `backlog_snapshots` | Point-in-time snapshot of active work items |
| 6 | **Operational Procedure** | `operational_procedures` | Step-by-step repeatable process |
| 7 | **Document** | `documents` | General-purpose project knowledge |
| 8 | **Environment Config** | `environment_config` | Environment-specific values under change control |

Supporting records: **Assertion Runs** (`assertion_runs`) and **Session Prompts** (`session_prompts`).

### Orchestrating Artifact Principle (SPEC-1499)

An orchestrating artifact (test plan, backlog) contains ordering, criteria, and execution context. It references other artifacts by ID without duplicating their content. Each referenced artifact is independently managed and versioned.

### Append-Only Change Control

All artifact tables use append-only versioning: `UNIQUE(id, version)`. Every mutation creates a new version row with mandatory `changed_by`, `changed_at`, `change_reason`. No UPDATE in place, no DELETE. `current_*` views surface the latest version per ID.

---

## Work Item Taxonomy (SPEC-1496)

**By origin:** Regression (previously PASSing test now FAILs), Defect (test FAILs against implementation), New (specification exists but no implementation yet), Hygiene (process improvement, tooling, drift reduction — improves the project management system, not the product).

**By component:** test_plan, test_procedure, operational_procedure, tenant_administration, provider_administration, agent_implementation, infrastructure_automation, database, test_harness, maintenance_tool, customer_interface, external_integration, development_environment.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-03-08*
