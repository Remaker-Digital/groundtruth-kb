# API Security & Penetration Testing Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-19 (45 passed, 0 failed — PASS)
# Last corrected: 2026-02-19 (/docs 404, httpx client-side header rejection, MFA 400)

This procedure validates that the Agent Red API gateway correctly enforces authentication, authorization, and input validation against adversarial requests. It tests against the live production endpoint using crafted requests designed to bypass security controls.

> **Audience:** AI assistants (Claude) and human operators.
> **Tooling:** pytest + httpx (same infrastructure as regression suite).
> **Test code:** `tests/security/test_live_penetration.py` (created by this procedure).

---

## Variables

```
PROJECT_ROOT        = E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
PROD_URL            = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
TEST_FILE           = tests/security/test_live_penetration.py

# Valid credentials (for baseline comparison)
VALID_API_KEY       = (from .env.local SUPERADMIN_PREVIEW_API_KEY; rotates on every re-seed)
VALID_WIDGET_KEY    = (from .env.local PREVIEW_WIDGET_KEY; rotates on every re-seed)

# Invalid / attacker credentials
INVALID_API_KEY     = ar_user_fake_AAAAAAAAAAAAAAAAAAAAAAAAAAAA_BBBBBB
INVALID_WIDGET_KEY  = pk_live_00000000_00000000
EXPIRED_MFA_TOKEN   = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxMDAwMDAwMDAwfQ.invalid
BLANK_KEY           = (empty string)

# Expected test counts
EXPECTED_PASS       = 45
EXPECTED_FAILURES   = 0
```

---

## Preconditions

```
[ ] Python 3.12+ available                    — python --version
[ ] pytest + httpx installed                   — python -m pytest --version && python -c "import httpx"
[ ] Production endpoint healthy                — curl $PROD_URL/health → 200
[ ] Valid API key works                        — curl -H "X-API-Key: $VALID_API_KEY" $PROD_URL/api/config → 200
[ ] Test file exists                           — ls $TEST_FILE
```

---

## Test Categories

### Category 1: Authentication Bypass (10 tests)

| ID | Test | Expected |
|----|------|----------|
| SEC-L01 | No auth header on /api/config | 401 |
| SEC-L02 | No auth header on /api/admin/conversations | 401 |
| SEC-L03 | Invalid API key format (no ar_user_ prefix) | 401 |
| SEC-L04 | Invalid API key (correct prefix, wrong hash) | 401 |
| SEC-L05 | Empty X-API-Key header | 401 |
| SEC-L06 | Empty X-Widget-Key header | 401 |
| SEC-L07 | API key in query parameter instead of header | 401 |
| SEC-L08 | Widget key on admin-only endpoint (/api/admin/conversations) | 401 |
| SEC-L09 | API key on widget-only endpoint (/api/chat/conversations) — returns data or 401 (both acceptable; must not crash) | 200 or 401 |
| SEC-L10 | Both API key and widget key headers simultaneously | 200 (should use one, not error) |

### Category 2: Auth-Exempt Endpoint Validation (8 tests)

| ID | Test | Expected |
|----|------|----------|
| SEC-L11 | /health accessible without auth | 200 |
| SEC-L12 | /ready accessible without auth | 200 |
| SEC-L13 | /api/status accessible without auth | 200 |
| SEC-L14 | /openapi.json accessible without auth | 200 |
| SEC-L15 | /api/webhooks/ path requires valid Shopify HMAC (reject without) | 401 or 403 |
| SEC-L16 | /api/shopify/gdpr/ path requires valid Shopify HMAC (reject without) | 401 or 403 |
| SEC-L17 | Auth-exempt paths do not leak tenant data in response | No tenant_id, api_key, or widget_key in /health response |
| SEC-L18 | /docs accessible without auth (OpenAPI docs) | 200 |

### Category 3: Header Injection & Malformed Requests (8 tests)

| ID | Test | Expected |
|----|------|----------|
| SEC-L19 | X-API-Key with SQL injection payload | 401 (not 500) |
| SEC-L20 | X-API-Key with XSS payload | 401 (not 500) |
| SEC-L21 | X-Widget-Key with null bytes | 401 (not 500) |
| SEC-L22 | Content-Type: text/xml on JSON endpoint | 400 or 422 (not 500) |
| SEC-L23 | Extremely long API key (10KB) | 401 (not 500, not timeout) |
| SEC-L24 | Unicode/emoji in API key header | 401 (not 500) |
| SEC-L25 | Newline injection in header value (CRLF) | 401 (not 500) |
| SEC-L26 | Duplicate auth headers (two X-API-Key headers) | Deterministic response (200 or 401, not 500) |

### Category 4: Path Traversal & IDOR (7 tests)

| ID | Test | Expected |
|----|------|----------|
| SEC-L27 | /api/admin/conversations/../../health | 404 (path traversal blocked) |
| SEC-L28 | /api/admin/conversations/{{random-uuid}} | 404 (not 500) |
| SEC-L29 | /api/admin/knowledge/{{random-uuid}} | 404 (not 500) |
| SEC-L30 | /api/team/{{random-uuid}} | 404 (not 500) |
| SEC-L31 | Conversation ID with special characters | 400 or 404 (sanitized, not 500) |
| SEC-L32 | Tenant ID manipulation in URL (if any endpoint exposes it) | 404 or no effect |
| SEC-L33 | /api/admin/avatar/upload without file body | 400 or 422 (not 500) |

### Category 5: Provider Console / Superadmin Protection (6 tests)

| ID | Test | Expected |
|----|------|----------|
| SEC-L34 | /api/superadmin/dashboard without superadmin key | 401 or 403 |
| SEC-L35 | /api/superadmin/tenants with regular admin key | 401 or 403 |
| SEC-L36 | /api/superadmin/tenants with widget key | 401 or 403 |
| SEC-L37 | Provider MFA endpoint without MFA token | 401 or requires MFA |
| SEC-L38 | Provider MFA with expired/invalid JWT token | 401 |
| SEC-L39 | Provider tier override endpoint with non-superadmin key | 401 or 403 |

### Category 6: CORS & Response Headers (6 tests)

| ID | Test | Expected |
|----|------|----------|
| SEC-L40 | OPTIONS preflight request returns correct CORS headers | Access-Control-Allow-Origin present |
| SEC-L41 | Response includes security headers (X-Content-Type-Options, etc.) | nosniff present |
| SEC-L42 | Response does not include server version in headers | No Server: or X-Powered-By: leaking framework |
| SEC-L43 | 401 response body does not leak internal details | No stack trace, no file paths |
| SEC-L44 | 404 response body does not leak internal details | No stack trace, no file paths |
| SEC-L45 | 500 error response (if triggerable) does not leak internal details | Generic error message only |

---

## Steps

### Step 1: Run the full security test suite

```
ACTION:    PROD_URL=$PROD_URL python -m pytest $TEST_FILE -v --tb=short -x

EXPECTED:  $EXPECTED_PASS passed, 0 failed
VERIFY:    Exit code 0
           Summary line: "N passed" where N >= $EXPECTED_PASS
ON FAIL:   Any failure indicates a security vulnerability.
           SEVERITY: CRITICAL for Categories 1, 3, 4, 5 (auth bypass, injection, IDOR, privilege escalation)
           SEVERITY: HIGH for Categories 2, 6 (info leakage, header misconfiguration)
           Do not deploy or accept customer data until resolved.
```

### Step 2: Review response bodies for information leakage

```
ACTION:    Re-run with verbose output:
           PROD_URL=$PROD_URL python -m pytest $TEST_FILE -v --tb=long -s 2>&1 | tee tests/security/penetration-results.log

EXPECTED:  No response body contains:
           - Stack traces or file paths
           - Internal IP addresses
           - Database connection strings
           - Environment variable values
           - Framework version identifiers
VERIFY:    grep -i "traceback\|file.*\.py\|10\.\|172\.\|192\.168\.\|cosmos\|azure" tests/security/penetration-results.log
           (Should return no matches from response bodies)
ON FAIL:   Information leakage finding. Review error handling middleware.
```

### Step 3: Verify production remains healthy after adversarial requests

```
ACTION:    curl $PROD_URL/health
           curl $PROD_URL/ready

EXPECTED:  Both return 200
VERIFY:    HTTP status codes
ON FAIL:   If production is degraded after security testing, the adversarial
           requests may have triggered a denial-of-service condition.
           Record the specific test that caused degradation.
```

---

## Postconditions

```
[ ] All $EXPECTED_PASS tests passed, 0 failures
[ ] No auth bypass: all protected endpoints reject unauthenticated requests
[ ] No injection vulnerabilities: malformed inputs return 4xx, never 500
[ ] No path traversal: directory traversal attempts return 404
[ ] No privilege escalation: regular keys cannot access superadmin endpoints
[ ] No information leakage: error responses contain generic messages only
[ ] CORS headers correctly configured
[ ] Production healthy after adversarial test run
[ ] Results log archived in tests/security/penetration-results.log
```

---

## Verdict Criteria

| Result | Condition |
|--------|-----------|
| **PASS** | All tests pass |
| **FAIL (CRITICAL)** | Any auth bypass, injection, IDOR, or privilege escalation test fails |
| **FAIL (HIGH)** | Information leakage or missing security headers |

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| Valid API key returns 401 | Environment (stale credentials) | Re-seed tenant, update .env.local |
| 503 on all requests | Environment (production unhealthy) | Check /health, wait for recovery |
| Path traversal test returns 301 redirect | Procedure defect | FastAPI may normalize paths. Update test to follow redirect and verify final response. |
| CORS headers missing | Procedure defect or code gap | Check CORSMiddleware configuration in main.py |
| Shopify webhook endpoint returns 200 without HMAC | **CRITICAL** code finding | Webhook HMAC validation is missing or bypassed |
| Superadmin endpoint returns 200 with regular admin key | **CRITICAL** code finding | Role-based access control not enforced |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-19*
