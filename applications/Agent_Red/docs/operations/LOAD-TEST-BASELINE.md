# Agent Red — Load Test Baseline Results

**Date:** 2026-02-06
**Target:** Production API Gateway (`agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io`)
**Tool:** Locust 2.43.1 (`tests/performance/locustfile.py`)
**Test:** `HealthProbeUser` class — /health, /ready, /api/tenants/lookup
**Duration:** 60 seconds
**Concurrent users:** 10

---

## Results Summary

| Metric | Value | SLA Target | Status |
|--------|-------|------------|--------|
| Total requests | 61 | — | — |
| Failures | 0 (0.00%) | — | PASS |
| Throughput | 1.04 req/s | — | — |
| P50 latency | 130ms | < 1,500ms | PASS |
| P95 latency | 690ms | < 2,000ms | PASS |
| P99 latency | 780ms | < 5,000ms | PASS |
| Max latency | 779ms | — | — |

## Per-Endpoint Breakdown

| Endpoint | Requests | Failures | P50 | P95 | P99 | Max |
|----------|----------|----------|-----|-----|-----|-----|
| GET /health [liveness] | 29 | 0 | 86ms | 390ms | 560ms | 564ms |
| GET /ready [readiness] | 26 | 0 | 160ms | 690ms | 710ms | 710ms |
| GET /api/tenants/lookup | 6 | 0 | 270ms | 780ms | 780ms | 779ms |

## Observations

1. **All requests succeeded** — 0% failure rate across 61 requests.
2. **All latency SLAs met** — P50 (130ms) is 10x under the 1,500ms target. P95 (690ms) is 3x under the 2,000ms target.
3. **/health is fastest** — 86ms P50, as expected (no dependency checks).
4. **/ready includes dependency health** — 160ms P50 reflects Key Vault and circuit breaker health checks.
5. **/api/tenants/lookup** — 270ms P50 includes Cosmos DB query for tenant resolution.
6. **Cold start visible** — Max latencies (560-780ms) likely reflect Azure Container Apps cold start or first-request Cosmos DB connection establishment. Subsequent requests are significantly faster.

## Scope and Limitations

- **Health probes only** — This baseline covers infrastructure latency (API Gateway → Cosmos DB → Key Vault). It does not measure:
  - Chat pipeline latency (requires provisioned tenant + Azure OpenAI)
  - Admin API latency under auth (requires valid API key)
  - SSE streaming performance
- **10 concurrent users** — Light load. Does not validate scaling behavior under peak concurrency.
- **Single region** — Test executed from East US (same region as deployment). Cross-region latency not measured.

## Next Steps

- [ ] Run full 3-scenario test (Widget + Admin + Health) after tenant #1 provisioned with valid credentials
- [ ] Measure chat pipeline P50/P95 with real Azure OpenAI calls
- [ ] Run 50-user sustained test (2 minutes) to validate auto-scaling triggers
- [ ] Document results in this file as additional test runs

---

## Raw Data

CSV exports available at:
- `tests/performance/baseline-health_stats.csv`
- `tests/performance/baseline-health_stats_history.csv`

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
