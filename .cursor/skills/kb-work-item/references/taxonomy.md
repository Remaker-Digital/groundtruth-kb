# Work Item Taxonomy (SPEC-1496)

## Origin

| Origin | When to Use |
|--------|------------|
| `regression` | Previously PASSing test now FAILs |
| `defect` | Test FAILs against implementation (never passed) |
| `new` | Spec exists but no implementation yet |
| `hygiene` | Process improvement, tooling, drift reduction |

## Component

| Component | Scope |
|-----------|-------|
| `test_plan` | Test plan structure and phases |
| `test_procedure` | Test implementation and execution |
| `operational_procedure` | Deployment, seeding, monitoring |
| `tenant_administration` | Tenant CRUD, config, activation |
| `provider_administration` | Provider console, platform admin |
| `agent_implementation` | AI agents, AGNTCY, chat pipeline |
| `infrastructure_automation` | Azure, Docker, CI/CD, scaling |
| `database` | Cosmos DB, Redis, data layer |
| `test_harness` | Test framework, fixtures, utilities |
| `maintenance_tool` | KB, scripts, developer tooling |
| `customer_interface` | Widget, storefront, end-user UX |
| `external_integration` | Shopify, Stripe, email, NATS |
| `development_environment` | Local dev, IDE, debugging |

## PLAN-001 Phase Assignment (GOV-13)

| Phase | Scope | Typical Tests |
|-------|-------|--------------|
| 1 | Pre-flight | Health, connectivity, version checks |
| 2 | Data Seeding | Tenant provisioning, data setup |
| 3 | Production Regression | Playwright E2E, critical paths |
| 5 | Tenant Isolation | Cross-tenant, RBAC, data boundaries |
| 6 | API Security | SQLi, XSS, auth bypass |
| 7 | Rate Limiting | RPM enforcement, backpressure |
| 8 | Data Integrity | Cosmos consistency, backup |
| 9 | Resilience | Circuit breaker, fallback |
| 10 | Load Testing | Sustained load, concurrency |
| 11 | Conversation Quality | Widget API, intent, memory |
| 13 | SPA Provisioning | Config pipeline, activation |
| 14 | Upgrade Verification | Multi-tenant assertions |
| 15 | External Verification | CDN, docs site, storefront |
| 16 | Widget Embed | Bundle, config, CORS |
