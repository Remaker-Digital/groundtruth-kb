# Work Item Taxonomy

SPEC-1496 records this vocabulary for Agent Red. Current native work-item fields use the origin and component values below; select the actual application and project before recording work.

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

## Select a current test-plan phase (GOV-13)

Read the selected plan and its phases through `gt test-plans` and `gt test-phases`. Preserve existing phase members when assigning a test. Test definitions and phase membership must be read back before linking implementation work; an unphased definition is not executable coverage.

The following table describes the Agent Red GA plan PLAN-001 only. It is not a platform default or authority to place another application's tests there. For GT-KB platform work, select the current applicable platform plan/phase; do not infer scope from a reused phase number.

### Agent Red PLAN-001 reference

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
