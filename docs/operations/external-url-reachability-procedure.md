# External URL Reachability Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-18 (session 47) — 35/37 PASS, 2 env transient (Steps 2.1, 2.2: MantineProvider fix not deployed)
# Last corrected: 2026-02-18 (session 47) — Step 2.2 EXPECTED updated to "Service Provider Administration"

---

## Purpose

Validates that every externally reachable URL in the Agent Red platform returns the
expected HTTP status code and content type. This procedure uses Chrome MCP tools to
navigate to each URL, capture screenshots, and check for console errors.

Run this procedure after every production deployment and as a standalone health check.

---

## Variables

| Variable | Value |
|----------|-------|
| `PROD_BASE` | `https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| `STANDALONE_URL` | `$PROD_BASE/admin/standalone` |
| `PROVIDER_URL` | `$PROD_BASE/admin/provider` |
| `SHOPIFY_URL` | `$PROD_BASE/admin/shopify` |
| `HEALTH_URL` | `$PROD_BASE/health` |
| `READY_URL` | `$PROD_BASE/ready` |
| `STATUS_URL` | `$PROD_BASE/api/status` |
| `WIDGET_JS_URL` | `$PROD_BASE/widget.js` |
| `OPENAPI_URL` | `$PROD_BASE/openapi.json` |
| `SUPERADMIN_KEY` | (from .env.local `SUPERADMIN_PREVIEW_API_KEY`; rotates on every re-seed) |
| `WIDGET_KEY` | (from .env.local `PREVIEW_WIDGET_KEY`; rotates on every re-seed) |

---

## Preconditions

- [ ] Chrome MCP tab available — `tabs_context_mcp` returns tab group with at least one tab
- [ ] Health endpoint returns 200 — navigate to `$HEALTH_URL`, verify page text contains `"status":"healthy"`
- [ ] Network connectivity to production — no DNS or TLS errors on health check

**Rule:** If any precondition fails, the procedure does not start.

---

## Steps

### Group 1 — Public System Endpoints (5 tests)

These endpoints require no authentication and must return specific content types.

```
STEP 1.1: Health endpoint
  ACTION:    Navigate to $HEALTH_URL. Read page text.
  EXPECTED:  HTTP 200. Page text contains "status" and "healthy".
  VERIFY:    get_page_text contains "healthy"
  ON FAIL:   Production is unhealthy. Do not proceed. Investigate Container App status.

STEP 1.2: Ready endpoint
  ACTION:    Navigate to $READY_URL. Read page text.
  EXPECTED:  HTTP 200. Page text contains "status" and "ready" (or "healthy").
  VERIFY:    get_page_text contains "ready" or "healthy"
  ON FAIL:   Production is not ready. Wait 60s and retry once. If still failing, investigate.

STEP 1.3: Public status API
  ACTION:    Navigate to $STATUS_URL. Read page text.
  EXPECTED:  HTTP 200. JSON response containing "overall_status".
  VERIFY:    get_page_text contains "overall_status"
  ON FAIL:   Status endpoint misconfigured. Check /api/status route in main.py.

STEP 1.4: Widget JavaScript bundle
  ACTION:    Navigate to $WIDGET_JS_URL. Read page text.
  EXPECTED:  HTTP 200. Response contains JavaScript code (function declarations or minified JS).
  VERIFY:    get_page_text contains "function" or "window" or "document"
  ON FAIL:   Widget bundle not served. Check static file mounting in main.py.

STEP 1.5: OpenAPI specification
  ACTION:    Navigate to $OPENAPI_URL. Read page text.
  EXPECTED:  HTTP 200. JSON response containing "openapi" and "paths".
  VERIFY:    get_page_text contains "openapi" and "paths"
  ON FAIL:   OpenAPI spec not generated. Check FastAPI app.openapi() configuration.
```

### Group 2 — Admin SPA Entry Points (3 tests)

Each SPA must return HTML with the `<div id="app">` mount point. Login pages render
client-side, so the check is for the HTML shell (not rendered content).

```
STEP 2.1: Standalone admin (merchant) login page
  ACTION:    Navigate to $STANDALONE_URL. Wait 3s. Take screenshot. Read console messages (errors only).
  EXPECTED:  Page renders login form (not blank). Zero console errors. Page text or DOM contains "API key" or "Sign in".
  VERIFY:    find("Sign in") or find("API key") returns elements. Console has zero error-level messages.
  ON FAIL:   Standalone admin SPA not rendering. Check MantineProvider wrapping (see D-MantineProvider fix).

STEP 2.2: Service Provider Administrator (SPA) console login page
  ACTION:    Navigate to $PROVIDER_URL. Wait 3s. Take screenshot. Read console messages (errors only).
  EXPECTED:  Page renders login form (not blank). Zero console errors. Page text or DOM contains "Service Provider Administration" or "API key".
  VERIFY:    find("Service Provider Administration") or find("API key") returns elements. Console has zero error-level messages.
  ON FAIL:   SPA Provider Console not rendering. Check MantineProvider wrapping (see D-MantineProvider fix).

STEP 2.3: Shopify embedded admin shell
  ACTION:    Navigate to $SHOPIFY_URL. Wait 3s. Take screenshot.
  EXPECTED:  Page loads (may show App Bridge error since we're outside Shopify context). HTTP 200 HTML returned.
  VERIFY:    Page is not a 404 or 500 error. get_page_text returns non-empty content.
  ON FAIL:   Shopify admin HTML shell not served. Check shopify/index.html in static files.
```

### Group 3 — SPA Catch-All Routing (25 tests)

Single-page applications use client-side routing. All sub-routes must return the same
HTML shell (the SPA framework handles rendering). These tests verify the server does
not return 404 for client-side routes.

**Standalone Admin Routes (10 tests):**

```
STEP 3.1:  Navigate to $STANDALONE_URL/inbox — EXPECTED: HTML page loads (not 404)
STEP 3.2:  Navigate to $STANDALONE_URL/configuration — EXPECTED: HTML page loads
STEP 3.3:  Navigate to $STANDALONE_URL/knowledge-base — EXPECTED: HTML page loads
STEP 3.4:  Navigate to $STANDALONE_URL/widget — EXPECTED: HTML page loads
STEP 3.5:  Navigate to $STANDALONE_URL/quick-actions — EXPECTED: HTML page loads
STEP 3.6:  Navigate to $STANDALONE_URL/billing — EXPECTED: HTML page loads
STEP 3.7:  Navigate to $STANDALONE_URL/team — EXPECTED: HTML page loads
STEP 3.8:  Navigate to $STANDALONE_URL/integrations — EXPECTED: HTML page loads
STEP 3.9:  Navigate to $STANDALONE_URL/memory-privacy — EXPECTED: HTML page loads
STEP 3.10: Navigate to $STANDALONE_URL/nonexistent-route — EXPECTED: HTML page loads (SPA catch-all redirects to /)
```

**Verification pattern for each:** `get_page_text` returns non-empty content; page is not
a raw "404 Not Found" or "Cannot GET" error.

**ON FAIL for any:** Server catch-all route not configured. Check `StaticFiles` mount and
SPA fallback in `main.py`.

**SPA Provider Console Routes (15 tests):**

```
STEP 3.11: Navigate to $PROVIDER_URL/tenants — EXPECTED: HTML page loads
STEP 3.12: Navigate to $PROVIDER_URL/deployments — EXPECTED: HTML page loads
STEP 3.13: Navigate to $PROVIDER_URL/queues — EXPECTED: HTML page loads
STEP 3.14: Navigate to $PROVIDER_URL/integrations — EXPECTED: HTML page loads
STEP 3.15: Navigate to $PROVIDER_URL/status — EXPECTED: HTML page loads
STEP 3.16: Navigate to $PROVIDER_URL/alerts — EXPECTED: HTML page loads
STEP 3.17: Navigate to $PROVIDER_URL/diagnostics — EXPECTED: HTML page loads
STEP 3.18: Navigate to $PROVIDER_URL/compliance — EXPECTED: HTML page loads
STEP 3.19: Navigate to $PROVIDER_URL/secrets — EXPECTED: HTML page loads
STEP 3.20: Navigate to $PROVIDER_URL/billing — EXPECTED: HTML page loads
STEP 3.21: Navigate to $PROVIDER_URL/costs — EXPECTED: HTML page loads
STEP 3.22: Navigate to $PROVIDER_URL/sla — EXPECTED: HTML page loads
STEP 3.23: Navigate to $PROVIDER_URL/abuse — EXPECTED: HTML page loads
STEP 3.24: Navigate to $PROVIDER_URL/mfa — EXPECTED: HTML page loads
STEP 3.25: Navigate to $PROVIDER_URL/nonexistent-route — EXPECTED: HTML page loads (SPA catch-all redirects to /)
```

### Group 4 — Authentication Enforcement (4 tests)

Authenticated API endpoints must reject unauthenticated requests. These tests verify
that key endpoints return 401 or 403 without credentials.

```
STEP 4.1: Tenant config without auth
  ACTION:    javascript_tool: fetch('$PROD_BASE/api/config').then(r => r.status)
  EXPECTED:  HTTP 401 or 403
  VERIFY:    Response status is 401 or 403
  ON FAIL:   Config endpoint is unprotected. Critical security issue.

STEP 4.2: Admin analytics without auth
  ACTION:    javascript_tool: fetch('$PROD_BASE/api/admin/analytics/summary').then(r => r.status)
  EXPECTED:  HTTP 401 or 403
  VERIFY:    Response status is 401 or 403
  ON FAIL:   Analytics endpoint is unprotected. Critical security issue.

STEP 4.3: Superadmin tenants without auth
  ACTION:    javascript_tool: fetch('$PROD_BASE/api/superadmin/tenants/summary').then(r => r.status)
  EXPECTED:  HTTP 401 or 403
  VERIFY:    Response status is 401 or 403
  ON FAIL:   Superadmin endpoint is unprotected. Critical security issue.

STEP 4.4: Chat conversation creation without valid widget key
  ACTION:    javascript_tool: fetch('$PROD_BASE/api/chat/conversations', {method:'POST', headers:{'Content-Type':'application/json','X-Widget-Key':'invalid_key'}, body:'{}'}).then(r => r.status)
  EXPECTED:  HTTP 401 or 403
  VERIFY:    Response status is 401 or 403
  ON FAIL:   Chat endpoint accepts invalid widget keys. Critical security issue.
```

---

## Postconditions

- [ ] All 5 public system endpoints return expected content (Group 1: 5/5 PASS)
- [ ] All 3 admin SPA entry points render login pages with zero console errors (Group 2: 3/3 PASS)
- [ ] All 25 SPA sub-routes return HTML (not 404) (Group 3: 25/25 PASS)
- [ ] All 4 auth enforcement checks return 401/403 (Group 4: 4/4 PASS)
- [ ] Total: 37 URL checks PASS
- [ ] Screenshots captured for all Group 2 tests (3 screenshots minimum)

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| Health returns 503 immediately after deployment | Environment transient | Wait 30-60s for Container App cold start. Retry. |
| Widget.js returns 404 | Procedure defect (if bundle not included in build) or Environment transient (if deploy in progress) | Verify `admin/widget/dist/widget.js` exists in Docker image. |
| SPA route returns raw 404 | Procedure defect (if catch-all misconfigured) | Check `main.py` StaticFiles mount order — SPA catch-all must be after API routes. |
| Console error: "MantineProvider was not found" | Procedure defect (if MantineProvider not hoisted) | See MantineProvider fix from session 47 — provider must wrap `<App />` at mount point. |
| CORS error on fetch in Group 4 | Environment transient | Browser same-origin policy may block fetch. Use `javascript_tool` with `{mode:'no-cors'}` or check status via network tab instead. |

---

## Execution Notes

### Chrome MCP Tool Mapping

| Procedure Action | Chrome MCP Tool |
|-----------------|-----------------|
| Navigate to URL | `navigate(url, tabId)` |
| Wait N seconds | `computer(action:'wait', duration:N, tabId)` |
| Take screenshot | `computer(action:'screenshot', tabId)` |
| Read page text | `get_page_text(tabId)` |
| Check console errors | `read_console_messages(tabId, onlyErrors:true)` |
| Find element on page | `find(query, tabId)` |
| Execute JavaScript | `javascript_tool(action:'javascript_exec', text:code, tabId)` |
| Read DOM/accessibility | `read_page(tabId)` |

### Execution Pattern (per URL)

1. `navigate` to the URL
2. `computer(action:'wait', duration:2)` — allow page to load
3. `computer(action:'screenshot')` — capture visual state
4. `read_console_messages(onlyErrors:true)` — check for errors
5. `get_page_text` or `find` — verify expected content
6. Record PASS/FAIL with test ID

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
