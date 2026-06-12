# PLAN-001 Pipeline Phases

## 13 Active Phases

| Phase | Name | Tests |
|-------|------|-------|
| 1 | Pre-flight | Platform health gates |
| 2 | Data Seeding | Populate test data via REST |
| 3 | Production Regression | Playwright E2E (widget, SPA) |
| 5 | Tenant Isolation | Cross-tenant verification |
| 6 | API Security | SQLi, XSS, auth bypass |
| 7 | Rate Limiting | RPM enforcement, backpressure |
| 8 | Data Integrity | Cosmos consistency checks |
| 9 | Resilience | Circuit breaker, fallback paths |
| 10 | Load Testing | Locust headless (sustained load) |
| 11 | Conversation Quality | Widget API conversation flow |
| 13 | SPA Provisioning | Config pipeline, activation |
| 14 | Upgrade Verification | 35 assertions per tenant |
| 15 | External Verification | CDN, docs site reachability |
| 16 | Widget Embed | Widget bundle, config, CORS |

## Required Environment Variables

In `.env.local`:
- `STAGING_REMAKER_TENANT_KEY` / `PRODUCTION_REMAKER_TENANT_KEY`
- `STAGING_REMAKER_WIDGET_KEY` / `PRODUCTION_REMAKER_WIDGET_KEY`
- `STAGING_SPA_KEY` / `PRODUCTION_SPA_KEY`

## Batch Inventory (Thermal-Safe Runner)

| Batch | Tests | Scope |
|-------|-------|-------|
| `core-a` | ~2,400 | `tests/multi_tenant/` |
| `core-b` | ~680 | `tests/unit/`, `tests/migrations/`, root tests |
| `agents-chat` | ~600 | `tests/agents/`, `tests/chat/`, `tests/persistent_memory/`, `tests/evaluation/` |
| `integrations` | ~400 | `tests/integrations/`, `tests/security/test_adversarial.py` |
| `sequential` | ~120 | `tests/integration/`, `tests/regression/`, `tests/performance/` (no xdist) |

## PowerShell Parameters (Thermal-Safe Runner)

- `-Workers N` — parallel xdist workers (default: 4)
- `-CoolDown N` — seconds between batches (default: 30)
- `-Fast` — no cooling pauses
- `-SkipLive` — skip sequential/live batch
- `-Coverage` — enable coverage collection
- `-StopOnFail` — stop on first failure
- `-DryRun` — print commands without executing
