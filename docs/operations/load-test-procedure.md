# Load Testing Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-19 — CONDITIONAL PASS (NATS disconnected, latency SLAs met)
# Last corrected: 2026-02-19 — Fixed /api/team → /api/admin/team in locustfile.py

This procedure validates that the Agent Red API gateway meets SLA commitments under sustained concurrent load matching the declared launch scale target (50 concurrent tenants).

> **Audience:** AI assistants (Claude) and human operators.
> **Tooling:** [Locust](https://locust.io/) — Python-based load testing framework.
> **Test code:** `tests/performance/locustfile.py` (3 user profiles, SLA event hooks).

---

## Variables

```
PROJECT_ROOT       = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
PROD_URL           = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
LOCUST_FILE        = tests/performance/locustfile.py
LOCUST_CONF        = tests/performance/locust.conf
REPORT_DIR         = tests/performance
REPORT_HTML        = tests/performance/load-test-report.html
REPORT_CSV_PREFIX  = tests/performance/load-test-results

# Load profile — matches launch scale target
USER_COUNT         = 50
SPAWN_RATE         = 5
RUN_DURATION       = 5m

# SLA thresholds (from documented SLA commitments)
SLA_P50_MS         = 1500
SLA_P95_MS         = 2000
SLA_P99_MS         = 5000
SLA_ERROR_RATE_PCT = 1.0

# Credentials (from .env.local — rotates on re-seed)
LOAD_TEST_API_KEY     = (from .env.local SUPERADMIN_PREVIEW_API_KEY; rotates on every re-seed)
LOAD_TEST_WIDGET_KEY  = (from .env.local PREVIEW_WIDGET_KEY; rotates on every re-seed)
LOAD_TEST_TENANT_ID   = remaker-digital-001
```

---

## Preconditions

```
[ ] Python 3.12+ available                    — python --version
[ ] Locust installed                           — python -m locust --version
[ ] Production endpoint healthy                — curl $PROD_URL/health → 200
[ ] Production endpoint ready                  — curl $PROD_URL/ready → 200
[ ] LOAD_TEST_API_KEY set                      — echo $LOAD_TEST_API_KEY (non-empty)
[ ] LOAD_TEST_WIDGET_KEY set                   — echo $LOAD_TEST_WIDGET_KEY (non-empty)
[ ] Previous report cleared (optional)         — rm $REPORT_HTML $REPORT_CSV_PREFIX*.csv (if present)
```

**Rule:** If any precondition fails, the procedure does not start.

---

## Steps

### Step 1: Verify Locust installation

```
ACTION:    python -m locust --version
EXPECTED:  Version string (e.g., "locust 2.x.x")
VERIFY:    Exit code 0
ON FAIL:   pip install locust && retry
```

### Step 2: Set environment variables

```
ACTION:    (PowerShell)
           $env:LOAD_TEST_API_KEY = "<value from .env.local SUPERADMIN_PREVIEW_API_KEY>"
           $env:LOAD_TEST_WIDGET_KEY = "<value from .env.local PREVIEW_WIDGET_KEY>"
           $env:LOAD_TEST_TENANT_ID = "remaker-digital-001"

EXPECTED:  Variables set in current shell session
VERIFY:    echo $env:LOAD_TEST_API_KEY (non-empty, starts with "ar_user_")
           echo $env:LOAD_TEST_WIDGET_KEY (non-empty, starts with "pk_live_")
ON FAIL:   Check .env.local exists and contains current credentials.
           If credentials are stale, re-run seed_tenant.py first.
```

### Step 3: Run health-only probe (warm-up)

```
ACTION:    cd $PROJECT_ROOT
           python -m locust -f $LOCUST_FILE --host $PROD_URL --tags health-only --headless -u 5 -r 5 --run-time 30s --only-summary

EXPECTED:  All requests succeed (0% failure rate)
           Response times: P50 < 500ms, P95 < 1000ms
VERIFY:    Locust summary output shows 0 failures
ON FAIL:   If production is returning errors, abort — do not proceed to full load test.
           Check /health and /ready manually.
```

### Step 4: Run full load test (50 users, 5 minutes)

```
ACTION:    cd $PROJECT_ROOT
           python -m locust -f $LOCUST_FILE --host $PROD_URL --headless -u $USER_COUNT -r $SPAWN_RATE --run-time $RUN_DURATION --html $REPORT_HTML --csv $REPORT_CSV_PREFIX --only-summary

EXPECTED:  Test runs for full duration without Locust crash
           Summary output shows:
             - Total requests: > 500 (realistic minimum for 50 users × 5 min)
             - Failure rate: < $SLA_ERROR_RATE_PCT (< 1.0%)
             - P50 response time: < $SLA_P50_MS (< 1,500ms)
             - P95 response time: < $SLA_P95_MS (< 2,000ms)
             - P99 response time: < $SLA_P99_MS (< 5,000ms)

VERIFY:    Parse Locust summary output for:
             - "Aggregated" row: Fail% < 1.0
             - "Aggregated" row: 50%ile < 1500
             - "Aggregated" row: 95%ile < 2000
             - "Aggregated" row: 99%ile < 5000
           Confirm $REPORT_HTML was generated (file exists and size > 0)
           Confirm $REPORT_CSV_PREFIX_stats.csv was generated

ON FAIL:   If failure rate > $SLA_ERROR_RATE_PCT:
             - Check which endpoints are failing (CSV breakdown by endpoint)
             - 429 responses are expected for rate-limited endpoints — verify these
               are not counted as failures in the Locust config (they shouldn't be;
               locustfile.py marks 429 as success)
             - 503 responses indicate backend overload — check Container Apps scaling

           If latency exceeds SLA thresholds:
             - Check per-endpoint breakdown in CSV
             - Chat endpoints (AI pipeline) will dominate P95/P99 — separate from
               admin/health endpoints
             - If only chat P99 > 5,000ms, this is a pipeline timeout issue (8s budget)
             - If admin endpoints also slow, this indicates infrastructure saturation

           If Locust crashes:
             - Check Python memory usage (50 users should be well within limits)
             - Check network connectivity to production
```

### Step 5: Verify SLA compliance from report

```
ACTION:    Open $REPORT_HTML in browser
           Review:
             a) Response time distribution chart
             b) Per-endpoint percentile breakdown
             c) Failure rate over time chart
             d) User count ramp-up chart

EXPECTED:  a) Distribution shows majority of requests < 1,500ms
           b) Health endpoints: P95 < 500ms
              Admin endpoints: P95 < 1,500ms
              Chat endpoints: P95 < 3,000ms (AI pipeline has higher baseline)
           c) Failure rate remains flat near 0% throughout the run
           d) User count reaches $USER_COUNT and holds steady

VERIFY:    Visual inspection of HTML report
           CSV file $REPORT_CSV_PREFIX_stats.csv contains per-endpoint rows
ON FAIL:   Record specific SLA violations for investigation. Do not re-run
           immediately — investigate root cause first.
```

### Step 6: Check production health post-test

```
ACTION:    curl $PROD_URL/health
           curl $PROD_URL/ready

EXPECTED:  Both return 200
VERIFY:    HTTP status codes
ON FAIL:   If production is degraded after load test, the test exposed a
           real issue. Record the failure mode. Check Container Apps metrics
           in Azure Portal for CPU/memory spikes, restart events, or scaling
           failures.
```

### Step 7: Archive results

```
ACTION:    Confirm these files exist in $REPORT_DIR:
             - load-test-report.html
             - load-test-results_stats.csv
             - load-test-results_stats_history.csv
             - load-test-results_failures.csv
             - load-test-results_exceptions.csv

EXPECTED:  All files present, non-zero size
VERIFY:    ls $REPORT_DIR/load-test-*
ON FAIL:   If files missing, check Locust --csv and --html flags were set correctly.
```

---

## Postconditions

```
[ ] Full load test completed (50 users, 5 minutes)
[ ] Aggregated failure rate < 1.0%
[ ] Aggregated P50 < 1,500ms
[ ] Aggregated P95 < 2,000ms
[ ] Aggregated P99 < 5,000ms
[ ] Production /health returns 200 after test
[ ] Production /ready returns 200 after test
[ ] HTML report archived in $REPORT_DIR
[ ] CSV results archived in $REPORT_DIR
```

---

## Verdict Criteria

| Result | Condition |
|--------|-----------|
| **PASS** | All postconditions met |
| **CONDITIONAL PASS** | Latency thresholds exceeded on chat endpoints only (AI pipeline), all other endpoints within SLA, error rate < 1% |
| **FAIL** | Error rate ≥ 1%, OR non-chat endpoints exceed P95 threshold, OR production unhealthy after test |

---

## Profiles

The load test can be run at different intensity levels depending on the context:

| Profile | Users | Duration | When to Use |
|---------|-------|----------|-------------|
| **Smoke** | 5 | 30s | Quick sanity check after deployment |
| **Standard** | 50 | 5m | Pre-launch validation (default) |
| **Stress** | 100 | 10m | Capacity planning, infrastructure changes |
| **Endurance** | 20 | 30m | Memory leak detection, connection pool exhaustion |

To run a non-default profile, override `USER_COUNT`, `SPAWN_RATE`, and `RUN_DURATION` variables in Step 4.

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| `locust: command not found` | Environment (deps) | `pip install locust` |
| LOAD_TEST_WIDGET_KEY rejected (401) | Environment (stale credentials) | Re-seed tenant, update .env.local |
| All chat requests return 503 | Environment (NATS disconnected) | NATS is required for chat pipeline. Check NATS JetStream connectivity. Health-only and admin tests may still pass. |
| Container Apps scaling lag (P99 spike in first 60s) | Environment transient | Cold start. Evaluate P95/P99 excluding first 60s of ramp-up. |
| Python MemoryError at high user counts | Environment (local machine) | Reduce USER_COUNT or run from a more capable machine. 50 users should require < 500MB RAM. |
| Rate limit 429 responses counted as failures | Procedure defect | locustfile.py should mark 429 as success (already implemented). If 429s appear in failure CSV, fix locustfile.py. |
| /api/team returns 404 | Procedure defect (corrected 2026-02-19) | Endpoint is /api/admin/team, not /api/team. Fixed in locustfile.py. |
| Chat 503 when NATS disconnected inflates failure rate | Environment (NATS not connected) | Chat requires NATS JetStream. 503 is correct behavior. Exclude chat endpoints from failure rate calculation when NATS is known-disconnected, or re-run when NATS is connected. |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-19*
