# Chrome-Automated Admin UI Test Procedure
# Type: Repeatable Procedure (see docs/operations/REPEATABLE-PROCEDURES.md)
# Last verified: 2026-02-19 (session 58) — full E2E pass: 770 PASS, 3 SOFT-PASS, 37 SKIP, 0 FAIL (v1.50.0, CSS centralization verified)
# Last corrected: 2026-02-19 (session 59) — added data-binding verification layer (9th dimension), logo/image assertions, Contact Us tests, Provider Console data-population tests

---

## Purpose

Chrome MCP-automated replacement for the manual `ui-test-procedure.md`. Uses Chrome
browser automation tools to navigate pages, verify DOM elements, check console errors,
capture screenshots, and verify data-binding correctness (API response fields populate
into visible UI elements with expected values).

**Authoritative test definitions:** `docs/operations/ui-test-procedure.md` remains the
authoritative source for test IDs, expected results, the defect log, and the activation
control disposition reference table. This procedure describes *how* to execute those
tests using Chrome MCP tools.

**Terminology:**
- **SPA** = Service Provider Administrator (Remaker Digital employee)
- **Superadmin / Admin** = Merchant users (customers)
- **SPA Console** = Provider Console at `/admin/provider` (for SPA use only)
- **Standalone Admin** = Merchant admin at `/admin/standalone` (for merchant superadmin/admin use)

---

## Variables

### Primary Tenant (remaker-digital-001 — production merchant)
| Variable | Value |
|----------|-------|
| `PROD_BASE` | `https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io` |
| `STANDALONE_URL` | `$PROD_BASE/admin/standalone` |
| `PROVIDER_URL` | `$PROD_BASE/admin/provider` |
| `MERCHANT_API_KEY` | (from .env.local `SUPERADMIN_PREVIEW_API_KEY`; rotates on every re-seed) |
| `PROVIDER_API_KEY` | (from .env.local `SUPERADMIN_PREVIEW_API_KEY`; same key has SUPERADMIN role) |
| `WIDGET_KEY` | (from .env.local `PREVIEW_WIDGET_KEY`; rotates on every re-seed) |
| `TENANT_ID` | `remaker-digital-001` |

### Simulated Customer Tenant (test-customer-001 — test data)
| Variable | Value |
|----------|-------|
| `TEST_TENANT_ID` | `test-customer-001` |
| `TEST_SUPERADMIN_KEY` | (from `logs/test_tenant_credentials.json` `superadmin_key`) |
| `TEST_WIDGET_KEY` | (from `logs/test_tenant_credentials.json` `widget_key`) |
| `TEST_TIER` | `starter` (can be changed via tier override endpoint) |

### Tier Override (for tier-gating tests)
| Variable | Value |
|----------|-------|
| `TIER_OVERRIDE_URL` | `$PROD_BASE/api/superadmin/tenants/$TEST_TENANT_ID/tier` |
| `TIER_OVERRIDE_AUTH` | `$MERCHANT_API_KEY` (requires remaker-digital-001 SUPERADMIN role) |

---

## Preconditions

- [ ] **Initialization procedure complete** — `docs/operations/initialization-procedure.md` executed, all 10 post-conditions (I.1-I.10) pass. Do not proceed until initialization is verified.
- [ ] **Simulated customer tenant exists** — `scripts/create_test_tenant.py --execute` completed, all 8 post-conditions pass. Credentials in `logs/test_tenant_credentials.json`.
- [ ] **Agent unit test gate** — `python -m pytest tests/agents/ -x -q` all 101 tests pass (0 failures)
- [ ] **Full unit test suite** — `python -m pytest tests/ --ignore=tests/integration --ignore=tests/regression --ignore=tests/performance -x -q` 4,000+ tests pass (0 failures)
- [ ] **Chrome MCP tab available** — `tabs_context_mcp` returns tab group with at least one tab
- [ ] **Credentials current** — `.env.local` keys match last seed output; Key Vault updated; revision restarted if re-seeded
- [ ] **External URL reachability** — `external-url-reachability-procedure.md` Group 1 + Group 2 pass (health OK, login pages render)

**Rule:** If any precondition fails, the procedure does not start.

---

## Auth Injection Sub-Procedure

Chrome MCP cannot type passwords into forms securely, but can inject session credentials
via `javascript_tool` to bypass the login page and access authenticated routes directly.

### Merchant Admin Auth Injection

```
STEP A.1: Navigate to $STANDALONE_URL
  ACTION:    navigate($STANDALONE_URL, tabId)
  EXPECTED:  Login page renders

STEP A.2: Inject merchant API key into sessionStorage
  ACTION:    javascript_tool(tabId, "sessionStorage.setItem('agentred_api_key', '$MERCHANT_API_KEY'); 'injected'")
  EXPECTED:  Returns "injected"

STEP A.3: Reload to trigger auth state
  ACTION:    javascript_tool(tabId, "location.reload(); 'reloading'")
  EXPECTED:  Page reloads

STEP A.4: Wait and verify authenticated state
  ACTION:    computer(action:'wait', duration:3, tabId). Then find("Dashboard", tabId) or find("Configuration", tabId).
  EXPECTED:  Sidebar navigation visible with Dashboard, Inbox, Configuration links.
  VERIFY:    find("Dashboard") returns at least one element.
  ON FAIL:   Auth injection failed. Verify $MERCHANT_API_KEY is valid. Check sessionStorage key name.
```

### SPA Provider Console Auth Injection

```
STEP B.1: Navigate to $PROVIDER_URL
  ACTION:    navigate($PROVIDER_URL, tabId)
  EXPECTED:  Login page renders

STEP B.2: Inject SPA API key into sessionStorage
  ACTION:    javascript_tool(tabId, "sessionStorage.setItem('agentred_provider_key', '$PROVIDER_API_KEY'); 'injected'")
  EXPECTED:  Returns "injected"

STEP B.3: Reload to trigger auth state
  ACTION:    javascript_tool(tabId, "location.reload(); 'reloading'")
  EXPECTED:  Page reloads

STEP B.4: Wait and verify authenticated state
  ACTION:    computer(action:'wait', duration:3, tabId). Then find("Health", tabId) or find("Tenants", tabId).
  EXPECTED:  Sidebar navigation visible with Health Dashboard, Tenants links.
  VERIFY:    find("Health") or find("Tenants") returns at least one element.
  ON FAIL:   Auth injection failed. Verify $PROVIDER_API_KEY has SUPERADMIN role. Check sessionStorage key name.
```

### Test Customer Tenant Auth Injection (test-customer-001)

Use this to test data-dependent pages (Team, Inbox, KB, Quick Actions) against the simulated customer tenant.

```
STEP C.1: Navigate to $STANDALONE_URL
  ACTION:    navigate($STANDALONE_URL, tabId)
  EXPECTED:  Login page or existing admin view renders

STEP C.2: Inject test customer API key into sessionStorage
  ACTION:    javascript_tool(tabId, "sessionStorage.setItem('agentred_api_key', '$TEST_SUPERADMIN_KEY'); 'injected'")
  EXPECTED:  Returns "injected"

STEP C.3: Reload to trigger auth state with test tenant
  ACTION:    javascript_tool(tabId, "location.reload(); 'reloading'")
  EXPECTED:  Page reloads, admin resolves test-customer-001 from API key

STEP C.4: Wait and verify test tenant loaded
  ACTION:    computer(action:'wait', duration:3, tabId). Then find("Starter", tabId) — tier badge should show Starter (not Professional).
  EXPECTED:  Header tier badge shows "Starter". Sidebar navigation visible.
  VERIFY:    find("Starter") returns at least one element.
  ON FAIL:   Auth injection failed. Verify $TEST_SUPERADMIN_KEY is valid and resolves to test-customer-001.
```

### Tier Override Sub-Procedure

Use this to test tier-gating UI behavior by cycling through tiers on test-customer-001.

```
STEP T.1: Override tier to target value
  ACTION:    javascript_tool(tabId, "fetch('$TIER_OVERRIDE_URL', {method:'PUT', headers:{'X-API-Key':'$MERCHANT_API_KEY','Content-Type':'application/json'}, body:JSON.stringify({tier:'TARGET_TIER'})}).then(r=>r.json())")
  EXPECTED:  Returns {tenant_id:'test-customer-001', previous_tier:'...', new_tier:'TARGET_TIER', updated_at:'...'}

STEP T.2: Reload page to pick up new tier
  ACTION:    javascript_tool(tabId, "location.reload(); 'reloading'")
  EXPECTED:  Page reloads, /api/tenants/lookup returns updated tier → tenantContext.tier updates → tierMeetsMin() re-evaluates

STEP T.3: Verify tier badge change
  ACTION:    computer(action:'wait', duration:3, tabId). Then find("TARGET_TIER_LABEL", tabId).
  EXPECTED:  Header tier badge shows updated tier name (Trial/Starter/Professional/Enterprise).

STEP T.RESTORE: Restore tier to starter after testing
  ACTION:    javascript_tool(tabId, "fetch('$TIER_OVERRIDE_URL', {method:'PUT', headers:{'X-API-Key':'$MERCHANT_API_KEY','Content-Type':'application/json'}, body:JSON.stringify({tier:'starter'})}).then(r=>r.json())")
  EXPECTED:  Returns {new_tier:'starter'}
  NOTE:      ALWAYS restore tier after tier-gating tests to avoid leaving test-customer-001 in unexpected state.
```

---

## Test Execution — Standalone Admin (Pages H, 0–10)

Each test references its ID from `ui-test-procedure.md`. The Chrome MCP verification
approach is described for each group.

### Execution Pattern (per page)

1. Navigate to the page URL
2. `computer(action:'wait', duration:2)` — allow React render
3. `read_console_messages(onlyErrors:true)` — check for runtime errors
4. `read_page(tabId)` or `find(query, tabId)` — verify expected DOM elements
5. `computer(action:'screenshot')` — capture visual state
6. Record each test ID as PASS / FAIL / SKIP with notes

### Page H: Header, Logo, and Contact Us (22 tests)

Verify the shared header bar, logo, action icons, and Contact Us feature. Auth injection must be performed first (Steps A.1–A.4). Navigate to any authenticated page (e.g., `$STANDALONE_URL`).

#### H.1 Logo and branding (6 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| H.1a | **Logo image rendered** — `javascript_tool(tabId, "document.querySelector('img[src*=primary-logo]')?.naturalWidth > 0")` — logo image loaded successfully (naturalWidth > 0 confirms it didn't 404) |
| H.1b | **Logo image source** — `javascript_tool(tabId, "document.querySelector('img[src*=primary-logo]')?.src")` — src contains "primary-logo-no-wordmark.svg" |
| H.1c | **Logo alt text** — `javascript_tool(tabId, "document.querySelector('img[src*=primary-logo]')?.alt")` — alt is "Agent Red" (brand identification) |
| H.1d | **Branding text** — `find("Customer Experience", tabId)` — header shows "Customer Experience" text next to logo |
| H.1e | **Logo dimensions** — `javascript_tool(tabId, "document.querySelector('img[src*=primary-logo]')?.offsetHeight")` — logo renders at expected height (~28px, not 0 or broken) |
| H.1f | **No duplicate logos** — `javascript_tool(tabId, "document.querySelectorAll('img[src*=logo]').length")` — exactly 1 logo image in header (no sidebar logo — removed session 59) |

#### H.2 Header action icons (6 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| H.2a | **Documentation icon** — `find("Documentation", tabId)` via hover tooltip, or `javascript_tool(tabId, "document.querySelector('[aria-label=\"Open documentation\"]') !== null")` — docs action icon present |
| H.2b | **Contact Us icon** — `javascript_tool(tabId, "document.querySelector('[aria-label=\"Contact us\"]') !== null")` — contact us action icon present |
| H.2c | **Dark mode toggle** — `javascript_tool(tabId, "document.querySelector('[aria-label=\"Toggle dark mode\"]') !== null")` — dark mode toggle present |
| H.2d | **Sign out icon** — `javascript_tool(tabId, "document.querySelector('[aria-label=\"Sign out\"]') !== null")` — sign out action icon present |
| H.2e | **Icon order** — `javascript_tool(tabId, "[...document.querySelectorAll('header [aria-label]')].map(e => e.getAttribute('aria-label')).join(', ')")` — icons appear in order: "Open documentation", "Contact us", "Toggle dark mode", "Sign out" |
| H.2f | **Tier badge** — `find("Professional", tabId)` or `find("Starter", tabId)` — tier badge visible in header with recognized tier name |

#### H.3 Contact Us modal (10 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| H.3a | Click Contact Us icon → `find("Contact us", tabId)` — modal opens with "Contact us" heading |
| H.3b | **Topic dropdown** — `find("Topic", tabId)` → click select → `javascript_tool(tabId, "document.querySelectorAll('[role=option]').length")` — dropdown has 5 options (Support, Feature request, Billing, Bug report, General) |
| H.3c | **Topic options populated** — `find("Support", tabId)`, `find("Feature request", tabId)`, `find("Bug report", tabId)` — at least 3 recognized topic options visible in dropdown |
| H.3d | **Subject field** — `find("Subject", tabId)` — text input present with max length 200 |
| H.3e | **Message field** — `find("Message", tabId)` — textarea present with max length 5000 |
| H.3f | **Cancel button** — `find("Cancel", tabId)` — Cancel button present in modal footer |
| H.3g | **Send button** — `find("Send message", tabId)` — Send message button present with blue (action) styling |
| H.3h | **Cancel closes modal** — Click Cancel → modal closes; Contact Us icon still present |
| H.3i | **Empty form validation** — Click Send message with empty subject/message → validation prevents submission (button stays enabled but form does not submit) |
| H.3j | **Topic default value** — `javascript_tool(tabId, "document.querySelector('select, [role=combobox]')?.textContent")` — topic defaults to "Support" |

### Page 0: Initial Provisioned State (20 tests)

**Precondition:** Run immediately after `seed_tenant.py --execute` on a fresh tenant.
Auth injection must be performed first (Steps A.1–A.4).

Navigate to `$STANDALONE_URL/configuration`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 0.1 | `find("Pending", tabId)` — sidebar badge shows Pending (yellow dot) |
| 0.2 | `find("Professional", tabId)` — header tier badge (green, capitalized) |
| 0.3 | `find("Brand name", tabId)` — field exists; value is empty or shows placeholder |
| 0.4 | `find("Brand voice", tabId)` — field exists; value is empty or shows placeholder |
| 0.5 | `find("Custom instructions", tabId)` — textarea empty |
| 0.6 | `find("Refund policy", tabId)` and `find("Shipping policy", tabId)` — textareas empty |
| 0.7 | `find("Activate", tabId)` — button present, yellow state (mandatory fields missing) |
| 0.8 | `find("Discard", tabId)` — button visible, enabled |
| 0.9 | `find("Roll back", tabId)` — button visible, disabled/greyed |
| 0.10 | `find("not yet active", tabId)` — welcome dialog message present |
| 0.10a | Dismiss welcome dialog → `find("not yet active", tabId)` no longer present; reload page → dialog does not reappear |
| 0.11 | `javascript_tool`: `fetch('$PROD_BASE/api/config/activation-status', {headers:{'X-API-Key':'$MERCHANT_API_KEY'}}).then(r=>r.json())` — verify `is_active=false, is_configured=false` |
| 0.12 | `javascript_tool`: `fetch('$PROD_BASE/api/config?state=draft', {headers:{'X-API-Key':'$MERCHANT_API_KEY'}}).then(r=>r.json())` — verify `brand_name` is empty |
| 0.13 | Click Discard → verify state unchanged (badge stays Pending, fields remain empty) |
| 0.13a | Discard on never-activated: no error notification appears (silent no-op) |
| 0.14 | Click Activate with brand_name empty → `find("Brand name is required", tabId)` in preflight dialog |
| 0.14a | Preflight dialog has no "Confirm" button when hard errors present — activation blocked |
| 0.15 | Click Activate with brand_voice empty → `find("Brand voice is required", tabId)` in preflight dialog |
| 0.16 | `javascript_tool`: `fetch('$PROD_BASE/api/chat/conversations', {method:'POST', headers:{'X-Widget-Key':'$WIDGET_KEY','Content-Type':'application/json'}, body:'{}'}).then(r=>r.status)` — expect 403 |
| 0.17 | `javascript_tool`: fetch widget config → verify `widget_active: false` |

### Page 0A: Activation Control Lifecycle (26 tests)

Continue from Page 0 state. Tests 0A.1–0A.21 follow the activation/deactivation/re-activation cycle. Each test involves:
- Form fills via `find` + `computer(action:'left_click')` + `computer(action:'type')`
- Button clicks via `find("button text")` + `computer(action:'left_click', ref:...)`
- State verification via `find` for badge text, button text, dialog content
- API verification via `javascript_tool` for activation-status and chat endpoints

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 0A.1 | Fill brand_name, save → `find("Activate", tabId)` still yellow (brand_voice missing) |
| 0A.1a | After save: notification toast with "saved" or "Draft" text |
| 0A.2 | Fill brand_voice, save → Activate button turns green |
| 0A.3 | Click Activate (green) → confirmation dialog with validation results → confirm |
| 0A.3a | After activation: success notification with "activated" text |
| 0A.4 | `find("Active", tabId)` — green badge in sidebar |
| 0A.5 | `find("Deactivate", tabId)` — red button replaces Activate |
| 0A.6 | `javascript_tool`: activation-status → `is_active=true, is_configured=true` |
| 0A.7 | `javascript_tool`: POST conversations → 200 |
| 0A.8 | SKIP — storefront widget mount requires live Shopify storefront |
| 0A.9 | Click Deactivate → `find("immediately stop the chat widget", tabId)` — confirmation dialog |
| 0A.9a | Click Cancel in deactivation dialog → dialog closes, badge stays Active |
| 0A.10 | Confirm deactivation → `find("Inactive", tabId)` — red badge |
| 0A.10a | After deactivation: notification with "deactivated" text |
| 0A.11 | `find("Activate", tabId)` — green (config complete, one-click re-activate) |
| 0A.12 | `javascript_tool`: activation-status → `is_active=false, is_configured=true` |
| 0A.13 | `javascript_tool`: POST conversations → 403 |
| 0A.14 | Click Activate → confirm → `find("Active", tabId)` — re-activated |
| 0A.15 | `javascript_tool`: POST conversations → 200 |
| 0A.16 | Modify brand_name, save → Activate (green) replaces Deactivate |
| 0A.16a | After save: all 4 AI Configuration pages re-fetch via configRefreshKey |
| 0A.17 | Clear brand_voice, save → Activate turns yellow |
| 0A.18 | `find("Pending", tabId)` — yellow badge during pending changes |
| 0A.19 | When Active: chat bubble launcher visible in bottom-right — `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=launcher], [id*=widget]') !== null", tabId })` |
| 0A.20 | After deactivation: chat bubble disappears without refresh |
| 0A.21 | After re-activation: chat bubble reappears without refresh |

### Page 0B: Configuration Controls (16 tests)

Tests 0B.1–0B.12 verify Discard, Roll back, and Activate/Deactivate as an integrated set. Same Chrome MCP patterns as Pages 0/0A.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 0B.1 | Click Discard (no pending changes) → badge stays Active, Deactivate stays red |
| 0B.2 | Modify brand_name, save → badge changes to Pending (yellow); Activate (green) |
| 0B.2a | After save: notification toast with "saved" text |
| 0B.3 | Click Discard → badge returns to Active (green); Deactivate (red) |
| 0B.3a | After discard: notification toast confirming discard |
| 0B.4 | `javascript_tool`: GET draft → brand_name matches active (reverted) |
| 0B.5 | Modify brand_name, save, Activate → active_version increments; badge = Active |
| 0B.5a | `javascript_tool`: activation-status → active_version = 2 |
| 0B.6 | Click Roll back → `find("Confirm", tabId)` or confirmation dialog → confirm → brand_name reverts |
| 0B.6a | After roll back: notification with "rolled back" text |
| 0B.7 | Roll back button state: enabled if PREVIOUS exists, disabled otherwise |
| 0B.8 | Deactivate → modify → save → Discard: badge Inactive → Pending → Inactive |
| 0B.9 | Click Activate → badge returns to Active (green) |
| 0B.10 | Clear brand_voice, save, click Activate → `find("Brand voice is required", tabId)` — blocked |
| 0B.11 | Click Discard → brand_voice restored; badge returns to Active (green) |
| 0B.12 | Deactivate then Roll back → previous config restored AND system re-activates; badge = Active |

### Page 1: Dashboard (70 tests)

Navigate to `$STANDALONE_URL` (root = Dashboard).

#### 1.1 Metric stat cards

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 1.1 | `find("Total conversations", tabId)`, `find("Avg response time", tabId)`, `find("Resolution rate", tabId)`, `find("Customer satisfaction", tabId)`, `find("Escalation rate", tabId)` — all 5 metric cards present |
| 1.1a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=StatCard]')?.textContent", tabId })` — verify Total conversations card shows a numeric count (e.g., "218") |
| 1.1b | `find("Billable", tabId)` — sub-label under Total conversations shows "Billable: N" |
| 1.1c | `find("Avg response time", tabId)` — card shows value ending in "s" (e.g., "2.3s") |
| 1.19 | `find("Avg response time", tabId)` — card displays "0s" when no conversations exist |
| 1.1d | `find("Resolution rate", tabId)` — card shows value ending in "%" with "N resolved" detail |
| 1.1e | `find("Customer satisfaction", tabId)` — card shows value in "N/5" format (e.g., "4.2/5") |
| 1.20 | `find("Customer satisfaction", tabId)` — card displays "0/5" when no conversations exist |
| 1.1f | `find("Escalation rate", tabId)` — card shows "%" with "N escalated" detail |
| 1.1g | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.mantine-Skeleton').length", tabId })` — during initial load, Skeleton placeholders appear for all 5 cards |
| 1.1h | Verify cards display "--" when API returns null for a metric — `find("--", tabId)` present in at least one stat card area |

#### 1.2 Metric card tooltips and doc links

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 1.2 | `find("help icon", tabId)` or `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[class*=HelpTooltip] svg, [class*=helpIcon]').length >= 5", tabId })` — 5 help icons near metric cards |
| 1.2a | Hover first help icon → `read_page({ tabId, filter: 'all' })` — tooltip contains "conversations started in the selected period" |
| 1.2b | Hover Avg response time help icon → tooltip contains "Average time" or "generate a complete response" |
| 1.2c | Hover Resolution rate help icon → tooltip contains "resolved" and "without human escalation" |
| 1.2d | Hover Customer satisfaction help icon → tooltip contains "rating" and "1-5 scale" |
| 1.2e | Hover Escalation rate help icon → tooltip contains "handed off" or "human team member" |
| 1.3 | Click doc link in tooltip → `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=Tooltip] a')?.href", tabId })` — href contains expected anchor fragment (#total-conversations, #average-response-time, etc.) |
| 1.4 | Click doc link → navigates to correct docs page section — verify URL contains expected path and anchor |

#### 1.5 Period selector

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 1.5 | `find("7d", tabId)`, `find("14d", tabId)`, `find("30d", tabId)`, `find("90d", tabId)` — all 4 period selector buttons present |
| 1.5a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=SegmentedControl] [data-active]')?.textContent", tabId })` — returns "30d" on initial load |
| 1.5b | Click "7d" → `find("Last 7 days", tabId)` or chart title/label updates to reflect 7-day period |
| 1.5c | Click "14d" → chart label updates to reflect 14-day period |
| 1.5d | Click "90d" → chart label updates to reflect 90-day period |
| 1.5e | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=SegmentedControl] [data-active]')?.classList.toString()", tabId })` — active segment has distinct styling class |

#### 1.6 Conversation volume chart

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 1.6 | Click each period (7d, 14d, 30d, 90d) → `computer({ action: 'screenshot', tabId })` — chart visually changes data range each time |
| 1.6a | `find("Conversation volume", tabId)` — chart title present; help icon nearby for tooltip |
| 1.7 | Click conversation volume help icon → tooltip contains doc link with "conversation-volume" in href |
| 1.6b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.recharts-area').length", tabId })` — returns 2 (Total and Billable series) |
| 1.6c | `find("Total", tabId)` and `find("Billable", tabId)` — legend items present below chart |
| 1.6d | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Skeleton[style*=height]')?.style.height", tabId })` — during load, Skeleton with height ~320px shown |
| 1.6e | When no volume data: `find("No volume data", tabId)` or `find("No data available", tabId)` — empty state text shown |
| 1.6f | `computer({ action: 'hover', tabId, coordinate: [chartCenterX, chartCenterY] })` → `computer({ action: 'screenshot', tabId })` — tooltip with date, Total count, Billable count visible |
| 1.15 | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.recharts-cartesian-axis-tick text').length", tabId })` — chart X-axis tick labels all fall within or after tenant creation date |
| 1.16 | Select "7d" → verify X-axis spans 7 days; select "90d" → verify X-axis spans 90 days — `computer({ action: 'screenshot', tabId })` comparison |

#### 1.8 Recent conversations

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 1.8 | `find("Recent conversations", tabId)` — section heading renders; up to 5 conversation cards visible |
| 1.8a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[class*=conversationCard], [class*=ConversationCard]')[0]?.textContent", tabId })` — first card shows a customer name or "Unknown Customer" |
| 1.8b | `find("active", tabId)` or `find("idle", tabId)` or `find("ended", tabId)` or `find("escalated", tabId)` — status badge visible on at least one conversation card |
| 1.8c | `javascript_tool({ action: 'javascript_exec', text: "document.body.innerText.match(/\\d+ messages/)?.[0]", tabId })` — at least one "N messages" label found |
| 1.8d | `find("Assigned", tabId)` or `find("Escalated", tabId)` or `find("Unassigned", tabId)` — assignment label on conversation card |
| 1.8e | `javascript_tool({ action: 'javascript_exec', text: "document.body.innerText.match(/\\d{1,2}:\\d{2}/)?.[0]", tabId })` — time in HH:MM format present, or "--" when null |
| 1.8f | During load: `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.mantine-Skeleton').length >= 5", tabId })` — 5 skeleton rows shown |
| 1.8g | When no conversations: `find("No conversations yet", tabId)` — empty state message shown |
| 1.9 | Hover Recent conversations help icon → tooltip contains doc link with "conversation-list" in href |

#### 1.10 Top topics and Topic breakdown

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 1.10 | `find("Top topics", tabId)` — section heading renders |
| 1.10a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[class*=topicRow], [class*=TopicRow]')[0]?.textContent", tabId })` — first row shows a formatted topic label |
| 1.10b | Topic row shows invocation count — `javascript_tool({ action: 'javascript_exec', text: "document.body.innerText.match(/\\b\\d+\\b.*topic/i)?.[0]", tabId })` or numeric count visible next to topic name |
| 1.10c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[class*=Progress], .mantine-Progress-bar').length > 0", tabId })` — horizontal distribution bars present (BRAND_RED colored) |
| 1.10d | During load: `find("Loading", tabId)` or 5 Skeleton rows visible in top topics section |
| 1.10e | When no topics: `find("No topic data", tabId)` — empty state text shown |
| 1.10f | Hover Top topics help icon → tooltip contains doc link with "topic-breakdown" in href |
| 1.11 | `find("Topic breakdown", tabId)` or `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('table')[0]?.querySelectorAll('th').length >= 3", tabId })` — table with Topic, Count, Distribution columns renders |
| 1.11a | `javascript_tool({ action: 'javascript_exec', text: "[...document.querySelectorAll('table th')].map(th => th.textContent).join(', ')", tabId })` — headers include "Topic", "Count", "Distribution" |
| 1.11b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Progress-bar')?.style.backgroundColor", tabId })` — progress bar uses BRAND_RED (#ff3621); percentage text ("N%") shown |
| 1.11c | During load: `find("Loading topic data", tabId)` — loading indicator text shown |
| 1.11d | When no data: `find("No topic data", tabId)` — empty state text shown |

#### 1.12 Knowledge gaps

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 1.12 | `find("Knowledge gaps", tabId)` — section heading renders |
| 1.12a | `find("could not fully resolve", tabId)` — subtitle text present describing knowledge gap meaning |
| 1.12b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=Badge][style*=orange], .mantine-Badge')?.textContent", tabId })` — orange badge shows "N gaps" when gaps > 0 |
| 1.12c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[class*=knowledgeGap] table th, [class*=KnowledgeGap] table th').length >= 5", tabId })` — table with 5 columns: Conversation, Status, Turns, Messages, Started |
| 1.12d | `find("escalated", tabId)` or `find("ended", tabId)` or `find("active", tabId)` — status badge with color coding visible in knowledge gaps table |
| 1.12e | During load: `find("Loading knowledge gaps", tabId)` — loading text shown |
| 1.12f | When no gaps: `find("No knowledge gaps", tabId)` — empty state text shown |
| 1.13 | Hover Knowledge gaps help icon → tooltip contains doc link with "knowledge-gaps" in href |

#### 1.14 Sidebar configuration state

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 1.14 | `find("Active", tabId)` or `find("Pending", tabId)` or `find("Inactive", tabId)` — sidebar configuration badge present |
| 1.14a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=Badge][style*=green], .mantine-Badge--green')?.textContent", tabId })` — green badge shows "Active" when config is activated with no pending changes |
| 1.14b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=Badge][style*=yellow], .mantine-Badge--yellow')?.textContent", tabId })` — yellow badge shows "Pending" when never activated or has pending draft |
| 1.14c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=Badge][style*=red], .mantine-Badge--red')?.textContent", tabId })` — red badge shows "Inactive" when deactivated |
| 1.17 | If conversations exist (Total conversations > 0), badge must be "Active" — agent requires activated config to serve conversations |
| 1.18 | `find("Roll back", tabId)` → `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('button:has-text(Roll back)')?.disabled", tabId })` — disabled when `active_version < 2`; enabled when PREVIOUS config exists |

### Page 2: Inbox (82 tests)

Navigate to `$STANDALONE_URL/inbox`.

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, disposition variants, and **data-binding correctness** per the 9-dimension verification standard.
>
> **9th dimension — data-binding correctness:** API response fields populate visible UI elements with expected value types (numbers, dates, emails, recognized enum strings). Fields must not render as "undefined", empty, or "NaN". Logo/brand images must load successfully (naturalWidth > 0). Select/filter dropdowns must have populated options.
>
> Tests 2.4–2.18 require conversation data — SKIP if tenant has 0 conversations.

#### 2.1 Three-panel layout (4 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.1 | `read_page({ tabId, filter: 'all' })` — verify three distinct panel containers; left (conversation list), center (messages), right (details) |
| 2.1a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[style*=borderRight]').length > 0", tabId })` — left panel has right border |
| 2.1b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[style*=borderLeft]').length > 0", tabId })` — right panel has left border |
| 2.1c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[style*=height]')?.style.height", tabId })` — layout uses calc() viewport height |

#### 2.2 Filter tabs (8 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.2 | `find("All", tabId)`, `find("Active", tabId)`, `find("Esc", tabId)`, `find("Resolved", tabId)`, `find("Archived", tabId)` — 5 filter segments with counts in parentheses |
| 2.2a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=SegmentedControl] [data-active]')?.textContent", tabId })` — returns "All (N)" on initial load |
| 2.2b | Click "Active" segment → `javascript_tool` — conversation list shows only active status conversations |
| 2.2c | Click "Esc" segment → `javascript_tool` — only escalated conversations visible |
| 2.15 | Click "Resolved" → `find("resolved", tabId)` — only resolved conversations shown; count matches |
| 2.2d | Click "Archived" → API fetches archived conversations; list shows only archived items |
| 2.2e | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=SegmentedControl] [data-active]')?.classList.toString()", tabId })` — active segment has distinct styling |
| 2.16 | Naturally ended conversations show "resolved" badge, not "Completed" — `find("resolved", tabId)` present; `find("Completed", tabId)` absent |

#### 2.3 Conversation list items (12 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.3 | `read_page({ tabId, filter: 'all' })` — conversation items with Avatar, name, message count, badge, timestamp visible |
| 2.3a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Avatar')?.textContent", tabId })` — avatar shows initials (1-2 letters) |
| 2.3b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Avatar')?.style.background", tabId })` — avatar has color from AVATAR_PALETTE |
| 2.3c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[style*=cursor]')[0]?.textContent", tabId })` — shows customer name or conversation ID prefix |
| 2.3d | `javascript_tool({ action: 'javascript_exec', text: "document.body.innerText.match(/\\d+[mhd]/)?.[0]", tabId })` — relative time format present (e.g., "5m", "2h", "1d") |
| 2.3e | `find("messages", tabId)` — "N messages" text visible on conversation items |
| 2.3f | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Badge')?.dataset.color", tabId })` — status badge has correct color (blue/green/red/yellow) |
| 2.3g | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[style*=borderRadius][style*=background][style*=width: 8]') !== null", tabId })` — red unread dot present for active/escalated conversations |
| 2.3h | When conversation has assignedTo: `find` shows team member name text on the item |
| 2.3i | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[style*=borderLeft][style*=ff3621]') !== null", tabId })` — selected item has BRAND_RED left border |
| 2.3j | `computer({ action: 'hover', tabId })` on non-selected item → background changes; leave → restores |
| 2.3k | On page load: first conversation is auto-selected — center and right panels populated |

#### 2.4 Conversation selection and detail panels (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.4 | Click a different conversation item → center panel messages change; right panel info updates |
| 2.4a | When nothing selected: `find("Select a conversation from the list to view messages", tabId)` — center empty state |
| 2.4b | When nothing selected: `find("Select a conversation to view details", tabId)` — right panel empty state |
| 2.4c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[style*=borderBottom] [class*=Badge]')?.textContent", tabId })` — thread header shows status badge |
| 2.4d | Thread header shows "N messages" and "Assigned to {name}" when applicable |

#### 2.5 Search functionality (9 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.5 | `find("Search conversations", tabId)` → type customer name → verify matching results appear |
| 2.6 | Type message content keyword → search returns conversations with matching messages |
| 2.5a | `find("Search conversations", tabId)` — placeholder text with search icon |
| 2.5b | Type text → `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Loader') !== null", tabId })` — Loader appears during debounced search |
| 2.5c | `javascript_tool({ action: 'javascript_exec', text: "document.body.innerText.match(/snippet/i)", tabId })` — search results show matched snippet text |
| 2.5d | `find("matched_in badge text", tabId)` or `javascript_tool` — gray outline badge shows which field matched (e.g., "message") |
| 2.7 | Click a search result → center + right panels populate with conversation data |
| 2.13 | Search non-matching term → `find("No matching conversations", tabId)` + `find("Try adjusting", tabId)` |
| 2.5e | Clear search input → normal conversation list restored with current filter |

#### 2.8 Action buttons (17 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.8 | Select active conversation → `find("Escalate to human", tabId)` (tooltip) → click escalate icon → status changes to "escalated" |
| 2.8a | `computer({ action: 'hover', tabId })` on escalate icon → `read_page` — "Escalate to human" tooltip visible |
| 2.8b | Click escalate → `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-ActionIcon--loading') !== null", tabId })` — loading spinner; both action buttons disabled |
| 2.8c | After escalation: `find("Conversation escalated", tabId)` — orange notification toast; auto-dismisses after 4s |
| 2.9 | After escalation: click "Esc" filter → escalated conversation visible; Esc count incremented |
| 2.11 | Select an escalated conversation → escalate button NOT present in action group |
| 2.10 | Select active conversation → click resolve icon → status changes to "resolved" |
| 2.10a | `computer({ action: 'hover', tabId })` on resolve icon → "Resolve conversation" tooltip |
| 2.10b | After resolve: `find("Conversation marked as resolved", tabId)` — green notification |
| 2.12 | Select a resolved conversation → resolve button NOT present in action group |
| 2.8d | Select resolved/timed_out conversation (not archived) → archive button visible |
| 2.8e | `computer({ action: 'hover', tabId })` on archive icon → "Archive conversation" tooltip |
| 2.8f | After archive: `find("Conversation archived", tabId)` — gray notification |
| 2.8g | Select archived conversation → unarchive button visible |
| 2.8h | `computer({ action: 'hover', tabId })` on unarchive icon → "Unarchive conversation" tooltip |
| 2.8i | After unarchive: `find("Conversation unarchived", tabId)` — blue notification |
| 2.8j | When API fails: `javascript_tool` — red notification with error message |

#### 2.14 Message thread (9 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.14 | Select conversation with messages → `read_page({ tabId, filter: 'all' })` — message bubbles with content and timestamps visible |
| 2.14a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[style*=flex-end]')?.textContent", tabId })` — agent messages right-aligned; "Agent Red AI" label present |
| 2.14b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[style*=flex-start]')?.textContent", tabId })` — customer messages left-aligned; "Customer" label present |
| 2.14c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[style*=textAlign: center] [style*=italic]')?.textContent", tabId })` — system messages centered and italic |
| 2.14d | `javascript_tool({ action: 'javascript_exec', text: "document.body.innerText.match(/\\d{1,2}:\\d{2}\\s?(AM|PM)/)?.[0]", tabId })` — timestamps in HH:MM AM/PM format |
| 2.14e | Switch conversations → `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[ref=messageEnd]')?.getBoundingClientRect().top", tabId })` — auto-scrolled to bottom |
| 2.14f | `find("Loading messages", tabId)` — Loader and text visible during message fetch |
| 2.14g | When message API fails: `find("Failed to load messages", tabId)` — error text in red |
| 2.14h | When 0 messages: `find("No messages in this conversation yet", tabId)` |

#### 2.17 Right panel — Customer details (13 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.17 | Select escalated conversation → `find("Assigned to", tabId)` — right panel shows team member display name (resolved from ID) |
| 2.18 | Select escalated conversation → `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.mantine-Badge--light[data-color=blue]')[0]?.textContent", tabId })` — escalation category badge present |
| 2.17a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Avatar[style*=64]')?.textContent", tabId })` — large avatar with initials; customer name below |
| 2.17b | `find("ID:", tabId)` — customer ID shown when present |
| 2.17c | Right panel status badge color matches conversation status |
| 2.17d | `find("Messages", tabId)` in right panel → shows messageCount number |
| 2.17e | `find("Started", tabId)` → formatted date (e.g., "Feb 15, 2:30 PM") or "--" |
| 2.17f | `find("Last activity", tabId)` → relative time (e.g., "5m", "2h") or "--" |
| 2.17g | `find("Assigned to", tabId)` → team member display name (resolved from memberMap) |
| 2.17h | `javascript_tool` — escalation category badge shows category with underscores replaced by spaces |
| 2.17i | `find("Escalated", tabId)` — red filled badge when status=escalated |
| 2.17j | `find("Archived", tabId)` — gray badge with date when archivedAt is set |
| 2.17k | `find("Customer details will be available", tabId)` — customer profile placeholder text |

#### 2.19 Loading and error states (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 2.19a | On initial load with slow API: `find("Loading conversations", tabId)` — Loader + text |
| 2.19b | When conversation API fails: `find("Failed to load conversations", tabId)` — red error text |
| 2.19c | With 0 conversations: `find("No conversations yet", tabId)` — empty state with chat icon and "Conversations will appear here once customers start chatting" |
| 2.19d | With filter producing 0 results: `find("No matching conversations", tabId)` + `find("Try adjusting your filter", tabId)` |
| 2.19e | When search/filter yields 0: selected conversation is cleared — center panel shows "Select a conversation" |

### Page 3: Team Members (43 tests)

Navigate to `$STANDALONE_URL/team`.

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard.

#### 3.1 Page header and loading states (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 3.1 | `find("Team member", tabId)` — table header column; `find("Role", tabId)`, `find("Joined", tabId)`, `find("Last active", tabId)`, `find("Escalations", tabId)`, `find("Actions", tabId)` — 6 column headers |
| 3.1a | `find("Team members", tabId)` — page title; `find("Manage team members", tabId)` — subtitle |
| 3.1b | Before data loads: `find("Loading team", tabId)` or `find("Loading team members", tabId)` — loading state |
| 3.1c | When team API fails: `find("Failed to load team", tabId)` — error message; `find("Retry", tabId)` — retry button |
| 3.1d | Click "Retry" button → table renders after successful refetch |

#### 3.2 Member count and invite toggle (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 3.2 | Click `find("Invite member", tabId)` → invite form appears with Email, Name, Role fields |
| 3.2a | `find("team member", tabId)` — header text includes member count (e.g., "3 team members") |
| 3.2b | Click "+ Invite member" → button text changes to "Cancel"; click "Cancel" → form closes |
| 3.2c | When no members: `find("No team members yet", tabId)` — empty state message |
| 3.2d | `find("Invite your first team member", tabId)` — empty state call to action |

#### 3.3 Invite form (10 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 3.3a | `find("Email", tabId)`, `find("Name", tabId)`, `find("Role", tabId)`, `find("Send invite", tabId)` — form fields and submit button |
| 3.3b | Click Role dropdown → options include "Admin", "Escalation agent", "Viewer" — no "Superadmin" |
| 3.3c | Fill email + name + role → click "Send invite" → `read_network_requests` shows POST /api/admin/team |
| 3.3d | After successful invite: notification toast contains "Invited" and email address |
| 3.3e | After invite: form closes, fields clear, role resets to default |
| 3.3f | After invite: new member row appears in table (refetch occurred) |
| 3.3g | Submit with empty email → notification "Please enter an email address." |
| 3.3h | Submit with invalid email → notification "Please enter a valid email address." |
| 3.3i | During invite: "Send invite" button shows loading state |
| 3.3j | When invite fails: error notification with failure message |

#### 3.4 Team member table (8 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 3.4a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('th').length", tabId })` — returns 6 (Team member, Role, Joined, Last active, Escalations, Actions) |
| 3.4b | Each `<tr>` in tbody contains member name, email, role, dates — `read_page(tabId, { filter: 'all' })` |
| 3.5 | Click role dropdown in table row → options: "Admin", "Escalation agent", "Viewer" — no "Superadmin" |
| 3.3 | Change role dropdown → `read_network_requests` shows PUT /api/admin/team/{id}; success notification appears |
| 3.4c | When inline role PUT fails: notification "Failed to update role:" |
| 3.9 | Escalations column shows numeric count per member row |
| 3.8 | For escalation agents: category badges (Sales, Support, etc.) visible in row |
| 3.4d | Click category badge → `read_network_requests` shows PUT with escalation_categories array |

#### 3.5 Role tooltip (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 3.6 | Hover (?) next to "Role" header → `find("Superadmin", tabId)`, `find("Admin", tabId)`, `find("Escalation agent", tabId)`, `find("Viewer", tabId)` — all 4 roles described |
| 3.5a | Tooltip text describes permissions for each of the 4 roles |
| 3.5b | Move mouse away → tooltip closes; role descriptions no longer visible |

#### 3.6 Owner/superadmin row protection (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 3.7 | Superadmin row: `javascript_tool({ action: 'javascript_exec', text: "Array.from(document.querySelectorAll('tr')).some(r => r.textContent.includes('Superadmin') && !r.querySelector('select'))", tabId })` — badge not dropdown, no delete |
| 3.6a | Superadmin member shows static badge text, no editable select element |
| 3.6b | Superadmin row: no trash/remove icon in Actions column |

#### 3.7 Remove member dialog (6 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 3.4 | Click trash icon on non-owner row → confirmation dialog appears naming the member |
| 3.7a | Dialog text contains the member's email address |
| 3.7b | Click confirm → `read_network_requests` shows DELETE /api/admin/team/{id} |
| 3.7c | After removal: notification "Removed {email} from the team." |
| 3.7d | After removal: member row disappears from table (refetch occurred) |
| 3.7e | Click cancel → dialog closes, no DELETE request sent |

#### 3.8 Loading and error feedback (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 3.8a | During removal: confirm button shows loading state |
| 3.8b | When DELETE fails: notification "Failed to remove member:" |
| 3.8c | When category toggle fails: notification "Failed to update categories:" |

### Page 4: Agent Configuration (85 tests)

Navigate to `$STANDALONE_URL/configuration`.

> **Verification standard:** Every element tested for presence, correct value, input
> manipulation, valid population, state change, control activation, input validation,
> and disposition variants — as applicable per element type.

#### 4.1 Brand & persona section

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 4.1 | `find("Brand name", tabId)`, `find("Brand voice", tabId)`, `find("Formality", tabId)`, `find("Response length", tabId)` — all present in Paper card |
| 4.1a | `javascript_tool`: `fetch('/api/config?state=draft', {headers:{'X-API-Key':KEY}}).then(r=>r.json())` → compare `brand_name` with input value via `read_page` |
| 4.1b | `find("Brand name")` → `computer(action:'triple_click', ref:...)` → `computer(action:'type', text:'Acme Store')` → verify input value updated |
| 4.1c | `find("*")` near "Brand name" label — required asterisk present |
| 4.1d | Type new value → click `find("Save draft inputs")` → `javascript_tool` fetch draft → `brand_name` matches new value |
| 4.1e | `javascript_tool("location.reload()")` → `computer(action:'wait', duration:3)` → verify input still shows saved value via `find` |
| 4.1f | Modify field → click sidebar Discard → verify input reverted to pre-modification value |
| 4.1g | Clear input → Save → `find("Activate")` shows yellow → click → `find("Brand name is required")` in preflight dialog |
| 4.1h | Modify → Save → `find("Pending")` badge appears in sidebar (yellow dot) |
| 4.1i | `find("Brand voice")` → verify textarea shows saved `brand_voice` value or placeholder |
| 4.1j | Type multi-line text into Brand voice textarea → verify textarea height expands (screenshot comparison) |
| 4.1k | Required asterisk visible next to "Brand voice" label |
| 4.1l | Clear Brand voice → Save → Activate → `find("Brand voice is required")` in preflight |
| 4.1m | `find("Formality")` → verify Select shows current value (Casual/Professional/Formal) |
| 4.1n | Click Formality dropdown → `find("Casual")`, `find("Professional")`, `find("Formal")` — exactly 3 options |
| 4.1o | Select "Casual" → Save → `javascript_tool` fetch draft → `formality_level: "casual"` |
| 4.1p | `find("Response length")` → verify Select shows current value (Concise/Moderate/Detailed) |
| 4.1q | Select "Detailed" → Save → `javascript_tool` fetch draft → `response_length: "detailed"` |

#### 4.2 Policies section

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 4.2 | `find("Return window", tabId)`, `find("Refund policy", tabId)`, `find("Shipping policy", tabId)` — all in Paper card |
| 4.2a | `find("Return window")` → verify NumberInput shows draft `return_window` value with " days" suffix |
| 4.2b | Clear Return window → type 60 → verify shows "60 days"; type 0 → "0 days"; type 365 → "365 days" |
| 4.2c | Type -1 → verify clamped to 0; type 400 → verify clamped to 365 |
| 4.2d | Change to 14 → Save → reload → verify shows "14 days" |
| 4.2e | `find("Refund policy")` → verify textarea shows saved `return_policy` or placeholder |
| 4.2f | Type 10+ lines into Refund policy → verify textarea height increases (screenshot) |
| 4.2g | `find("Shipping policy")` → verify textarea shows saved `shipping_info` or placeholder |
| 4.2h | Hover (?) icon next to "Policies" → tooltip with doc link to business-policies |

#### 4.3 Escalation section

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 4.3 | `find("Escalation", tabId)`, `find("Sales", tabId)`, `find("Support", tabId)`, `find("Service", tabId)`, `find("Account", tabId)`, `find("Technical assistance", tabId)`, `find("General inquiry", tabId)` — slider + 6 categories |
| 4.3a | `javascript_tool` fetch draft → `escalation_threshold`; verify slider position matches (screenshot or read_page) |
| 4.3b | `find("Conservative")`, `find("Aggressive")`, `find("0.5")` — slider marks present |
| 4.3c | Drag slider → verify tooltip shows value to 2 decimal places (screenshot) |
| 4.3d | Drag slider to ~0.35 → Save → `javascript_tool` fetch draft → `escalation_threshold` ≈ 0.35 |
| 4.3e | All 6 category labels visible: `find("Sales")`, `find("Support")`, `find("Service")`, `find("Account")`, `find("Technical assistance")`, `find("General inquiry")` |
| 4.3f | `find("keywords")` — each category shows badge with keyword count (e.g., "7 keywords") |
| 4.3g | Set email on a category → save → `find("✉")` badge appears on that category; remove email → badge gone |
| 4.3h | Toggle category off → screenshot shows reduced opacity (0.6); toggle on → full opacity |

#### 4.4 Escalation category expanded detail

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 4.4 | Click category row (e.g., Sales) → `find("Notification email")`, keyword chips, "Add keyword" input all visible |
| 4.4a | `find("Notification email")` → verify input shows saved email or placeholder "{category}@yourcompany.com" |
| 4.4b | Type "team@example.com" in email → Save → reload → verify email persisted |
| 4.4c | Keyword chips: `read_page` for Badge elements with × icons inside expanded category |
| 4.4d | Type "new-keyword" in add input → `computer(action:'key', text:'Enter')` → new chip appears |
| 4.4e | Type existing keyword → Enter → no duplicate chip added (count unchanged) |
| 4.4f | Type keyword belonging to another category → Enter → not added (count unchanged) |
| 4.4g | Click × on keyword chip → chip removed (keyword count decreases) |
| 4.4h | Click reset icon → keyword list reverts to default count for that category |
| 4.4i | Toggle category off → `find("Notification email")` input is disabled; add keyword input disabled |
| 4.4j | Click chevron again → category detail collapses (Notification email no longer visible) |
| 4.4k | Modify any category field → `find("Save draft inputs")` button becomes enabled |

#### 4.5 Custom instructions section

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 4.5 | `find("Custom instructions", tabId)` — Paper card with textarea |
| 4.5a | Textarea shows draft `custom_instructions` or placeholder "Provide advisory instructions…" |
| 4.5b | Type 6+ lines → textarea height expands (screenshot comparison) |
| 4.5c | `find("Safety rules always take precedence")` — safety note text present below textarea |
| 4.5d | (?) icon next to "Custom instructions" header → tooltip with doc link |
| 4.5e | Type instructions → Save → reload → textarea shows saved text |

#### 4.6 Language section

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 4.6 | `find("Primary language", tabId)`, `find("Supported languages", tabId)` — Paper card |
| 4.6a | `find("Primary language")` → Select shows "English" |
| 4.6b | Click Primary language dropdown → exactly 1 option: "English" |
| 4.6c | `find("English")`, `find("Spanish (coming soon)")`, `find("French (coming soon)")` — 3 chips present |
| 4.6d | English chip shows selected state (filled/colored) |
| 4.6e | Click "Spanish (coming soon)" → no state change; chip remains unselected |
| 4.6f | (?) icon next to "Language" header → tooltip with doc link |

#### 4.7 Idle timeout and Max turns

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 4.7 | `find("Idle timeout", tabId)`, `find("Max turns", tabId)` — two NumberInputs side by side |
| 4.7a | Idle timeout shows draft `idle_timeout_minutes` with " minutes" suffix. Default: "30 minutes" |
| 4.7b | Clear → type 1 → "1 minutes"; type 120 → "120 minutes" |
| 4.7c | Type 0 → clamped to 1; type 999 → clamped to 120 |
| 4.7d | (?) tooltip next to "Idle timeout" with doc link (D58 regression) |
| 4.7e | Max turns shows draft `max_ai_turns_before_escalation`. Default: 50 |
| 4.7f | Type 5 → accepts; type 200 → accepts |
| 4.7g | Type 3 → clamped to 5; type 500 → clamped to 200 |
| 4.7h | (?) tooltip next to "Max turns" with doc link (D58 regression) |

#### 4.8–4.14 Controls and cross-cutting behavior

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 4.8 | `find("Save draft inputs", tabId)` — button at bottom of page with save icon |
| 4.8a | On initial load, button is disabled (greyed, not clickable) |
| 4.8b | Modify any field → button becomes enabled with brand red color |
| 4.8c | Click Save → button shows loading spinner while API request in flight |
| 4.9 | (?) icons on Brand & persona, Policies, Escalation, Custom instructions, Language — all present |
| 4.9a | Hover any (?) icon → dark tooltip appears with help text |
| 4.9b | Tooltip doc link → navigates to `agentredcx.com/docs/admin-guide/{section}` |
| 4.10 | Modify brand name → click "Save draft inputs" → success notification "Draft configuration saved successfully." |
| 4.10a | After save, F5 reload → all modified fields retain saved values |
| 4.10b | After save, sidebar Discard reverts to NEW saved values (not pre-save values) |
| 4.10c | After save, sidebar badge updates to Pending (if config was previously Active) |
| 4.11 | Modify field (no save) → sidebar Discard → field reverts to last saved draft value |
| 4.11a | After Discard, "Save draft inputs" button returns to disabled state |
| 4.12 | Simulate save failure → red Alert "Save failed" with error text and X close button |
| 4.12a | Error text from API response displayed (not generic "Something went wrong") |
| 4.12b | Click X → banner disappears; Save button remains enabled for retry |
| 4.13 | Before config data loads → LoadingState component shown ("Loading configuration") |
| 4.14 | Config API failure → red Alert "Failed to load configuration" with Retry button |
| 4.14a | Click Retry → config re-fetches; on success, form populates |

### Page 5: Knowledge Base (87 tests)

Navigate to `$STANDALONE_URL/knowledge-base`.

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard.

#### 5.1 Summary stat cards (10 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.1 | `find("Total articles", tabId)` and `find("Published", tabId)` and `find("Draft", tabId)` and `find("Archived", tabId)` and `find("Needs attention", tabId)` — 5 stat cards |
| 5.1a | `javascript_tool(tabId, "document.querySelector('[class*=\"xl\"]')?.textContent")` — Total articles count matches API |
| 5.1b | `find("Published", tabId)` — count displayed in green |
| 5.1c | `find("Draft", tabId)` — count displayed in yellow |
| 5.1d | `find("Archived", tabId)` — count displayed dimmed |
| 5.1e | `find("Needs attention", tabId)` — count displayed in red, = stale + very_stale |
| 5.1f | After article create → stat counts update (verify via `find` re-check) |
| 5.1g | After archive action → Published/Archived counts change |
| 5.8 | Hover "Needs attention" card → tooltip text appears |
| 5.16 | All 5 stat cards present with correct labeled values (D62 regression) |

#### 5.2 Articles table (11 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.2 | `find("Title", tabId)` and `find("Category", tabId)` and `find("Freshness", tabId)` — table renders with column headers |
| 5.2a | `read_page(tabId)` — 6 column headers: Title, Category, Status, Freshness, Last updated, Actions |
| 5.2b | `find("Policies", tabId)` or `find("Products", tabId)` — category badges with color coding |
| 5.2c | `find("published", tabId)` or `find("draft", tabId)` — status badges with correct colors |
| 5.3 | `find("Fresh", tabId)` or `find("Aging", tabId)` — freshness badges present |
| 5.3a | `find("Stale", tabId)` or `find("Very stale", tabId)` — stale articles show red badge |
| 5.3b | Date column shows formatted dates (e.g., "Jan 15, 2026") |
| 5.12 | After archiving → `javascript_tool` check `opacity: 0.5` and `line-through` on row |
| 5.13 | Newly created article → `find("Fresh", tabId)` — green badge, not "--" |
| 5.18 | Archived row still shows Category and Status badges (not "--") |
| 5.19 | Filter to empty result → `find("No articles match your filters", tabId)` |

#### 5.4 Search and filters (14 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.4 | `find("Search articles", tabId)` — search input renders |
| 5.4a | `read_page(tabId, filter:'interactive')` — search input with placeholder "Search articles..." |
| 5.4b | Type article title keyword → table filters to show matching articles only |
| 5.4c | Type content keyword (not in title) → table shows matching articles |
| 5.4d | Type "POLICY" (uppercase) → matches "policy" articles (case insensitive) |
| 5.4e | Clear search → all articles visible again |
| 5.7 | `find("Category", tabId)` and `find("Status", tabId)` — two filter dropdowns render |
| 5.7a | Click Category dropdown → `read_page(tabId)` — 8 options visible |
| 5.7b | Select "Products" → only Products articles shown |
| 5.7c | Click Status dropdown → `read_page(tabId)` — 4 options visible |
| 5.7d | Select "Published" → only Published articles shown |
| 5.7e | Search + Category + Status combined → intersection of all three filters |
| 5.10 | Assigned category/status matches filter selection |
| 5.17 | "Products" category filter matches articles with category "Products" including entryType-derived (D63 regression) |

#### 5.5 Article CRUD — Edit modal (10 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.5 | Click edit icon → `find("Edit article", tabId)` — modal opens with pre-filled fields |
| 5.5a | `read_page(tabId)` — Title input shows article's current title |
| 5.5b | Category dropdown shows article's current category |
| 5.5c | Content textarea shows article's current content |
| 5.5d | Status dropdown shows article's current status |
| 5.5e | Click "Save changes" → `find("updated successfully", tabId)` or notification |
| 5.5f | Click "Cancel" → modal closes, no changes saved |
| 5.5g | Clear title or content → "Save changes" button disabled |
| 5.5h | (Simulated failure) → red error text appears in modal |
| 5.9 | After creating article with Category+Status → both display in table row (not "--") |

#### 5.6 Action buttons and controls (13 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.6 | `find("Scan for conflicts", tabId)` and `find("Export CSV", tabId)` and `find("Import", tabId)` and `find("Add article", tabId)` — 4 buttons |
| 5.6a | Click "Add article" → `find("Add article", tabId)` modal with empty form, "Create article" button |
| 5.6b | Fill form + click "Create article" → `find("created successfully", tabId)` notification |
| 5.6c | Hover "Add article" → tooltip about creating new KB article |
| 5.6d | Hover "Scan for conflicts" → tooltip about detecting duplicates |
| 5.6e | With 0 articles → "Scan for conflicts" button disabled |
| 5.6f | Click "Scan for conflicts" → button shows loading spinner |
| 5.6g | Hover "Export CSV" → tooltip about downloading CSV file |
| 5.6h | With 0 articles → "Export CSV" button disabled |
| 5.6i | Click "Export CSV" → button shows loading spinner |
| 5.6j | After export → `find("exported as CSV", tabId)` notification |
| 5.6k | Hover "Import" → tooltip about uploading files or importing URL |
| 5.11 | After article create → sidebar badge changes to "Pending" (D16 regression) |

#### 5.14 Table row actions (8 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.14 | Archived article row → `find` Restore icon (blue arrow) |
| 5.14a | Click Archive icon → `find("archived", tabId)` notification |
| 5.14b | After archive → row opacity 0.5, title line-through, "archived" badge |
| 5.14c | Click Restore icon → `find("restored as Draft", tabId)` notification |
| 5.14d | After restore → row normal opacity, "draft" badge |
| 5.14e | Verify icon only on stale/aging/very_stale articles (conditional rendering) |
| 5.14f | Click Verify → `find("verified as current", tabId)` notification |
| 5.15 | Hover action icons → styled Mantine tooltips with arrows (D60 regression) |

#### 5.20 Import modal (10 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.20 | Click "Import" → `find("Upload file", tabId)` and `find("Import URL", tabId)` — modal with 2 tabs |
| 5.20a | `find("Drop a file here", tabId)` — drag-drop zone with instructions |
| 5.20b | Drag file over zone → border highlights with BRAND_RED |
| 5.20c | During upload → `find("Uploading", tabId)` or `find("Processing", tabId)` with progress bar |
| 5.20d | After upload → `find("Import successful", tabId)` with entries count and "Back to knowledge base" button |
| 5.20e | Upload failure → red error text "File upload failed" |
| 5.20f | Click "Import URL" tab → `find("Website URL", tabId)` TextInput visible |
| 5.20g | URL input empty → Import button disabled |
| 5.20h | Enter URL + click Import → success notification with entries count |
| 5.20i | URL import failure → red error text "URL import failed" |

#### 5.21 Conflict scan results modal (8 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.21 | No conflicts → `find("All clear", tabId)` green Alert |
| 5.21a | `find("Entries scanned", tabId)` and `find("With embeddings", tabId)` and `find("Scan time", tabId)` and `find("Issues found", tabId)` — 4 stat cards |
| 5.21b | `find("high severity", tabId)` or `find("medium", tabId)` or `find("low", tabId)` — severity badges |
| 5.21c | Conflict accordion items with severity + type badges + article pair names |
| 5.21d | Expand accordion → similarity scores, conflicting facts, suggested resolution |
| 5.21e | 503 error → `find("Conflict scanner is not available", tabId)` |
| 5.21f | `find("Re-scan", tabId)` → click triggers force re-scan |
| 5.21g | Footer shows scan timestamp + skipped entries count |

#### 5.22 Loading and error states (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 5.22 | `find("Loading knowledge base", tabId)` — spinner shown during fetch |
| 5.22a | On API error → `find("Failed to load knowledge base", tabId)` red text with Retry button |
| 5.22b | Click "Retry" → page re-fetches and renders normally on success |

### Page 6: Quick Actions (62 tests)

Navigate to `$STANDALONE_URL/quick-actions`.

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard.

#### 6.1 Tab navigation and page header (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 6.1 | `find("Prompt library", tabId)` — tab renders; `read_page({ tabId, filter: 'all' })` — table with Order, Icon, Label, Prompt template, Status, Actions columns |
| 6.1a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=Tab][data-active]')?.textContent", tabId })` — tab label includes count "(N)" |
| 6.1b | `find("Quick actions", tabId)` — page title; `find("Manage contextual prompt buttons", tabId)` — subtitle |
| 6.1c | `find("Page assignments", tabId)` → click → `read_page({ tabId, filter: 'all' })` — assignment table visible |
| 6.1d | On page load: `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('[class*=Tab][data-active]')?.textContent", tabId })` — returns "Prompt library" |

#### 6.2 Empty state and starter examples (7 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 6.2 | `find("No quick actions yet", tabId)` — empty state message; `find("Track my order", tabId)`, `find("Return policy", tabId)`, `find("Product recommendations", tabId)`, `find("Help with my order", tabId)` — 4 starter chips |
| 6.2a | `find("Track my order", tabId)` → click → verify table refreshes with new action containing "Track my order" label |
| 6.2b | `find("Return policy", tabId)` → click → verify new action with "Return policy" label created |
| 6.2c | `find("Product recommendations", tabId)` → click → verify action created; prompt contains "{{product_title}}" |
| 6.2d | `find("Help with my order", tabId)` → click → verify action created |
| 6.2e | After clicking a starter chip: `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('table tbody tr').length", tabId })` — at least 1 row; empty state no longer visible |
| 6.2f | `find("Click any example to add it", tabId)` — instruction text visible below starter chips |

#### 6.3 Prompt library table (11 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 6.3 | `find("Create quick action", tabId)` — red button visible |
| 6.3a | `javascript_tool({ action: 'javascript_exec', text: "[...document.querySelectorAll('table th')].map(th => th.textContent).join(', ')", tabId })` — includes "Order", "Icon", "Label", "Prompt template", "Status", "Actions" |
| 6.3b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('table tbody tr td')?.textContent", tabId })` — first cell shows sort order number |
| 6.3c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('table tbody tr td')[1]?.textContent", tabId })` — shows emoji icon or "—" |
| 6.3d | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('table tbody tr td')[2]?.textContent", tabId })` — shows label text |
| 6.3e | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('table tbody tr td')[3]?.textContent?.length < 200", tabId })` — prompt text is truncated (lineClamp=2) |
| 6.9 | `find("Active", tabId)` or `find("Inactive", tabId)` — badge text fully visible without truncation |
| 6.3f | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Badge--filled[data-color=green]')?.textContent", tabId })` — green filled "Active" badge when isActive=true |
| 6.3g | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Badge--outline')?.textContent", tabId })` — gray outline "Inactive" badge when isActive=false |
| 6.3h | `find("Edit", tabId)` — tooltip on hover; `computer({ action: 'left_click', tabId })` on edit icon → modal opens with "Edit quick action" title |
| 6.3i | `find("Delete", tabId)` — tooltip on hover; `computer({ action: 'left_click', tabId })` on trash icon → confirm delete modal opens |

#### 6.4 Page assignments tab (16 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 6.4 | Click "Page assignments" tab → `find("All pages", tabId)`, `find("Home", tabId)`, `find("Product", tabId)`, `find("Collection", tabId)`, `find("Cart", tabId)`, `find("Search", tabId)`, `find("Blog", tabId)` — 9 page type rows |
| 6.5 | `read_page({ tabId, filter: 'interactive' })` — each row has 2 Select dropdowns, 1 Switch, 1 NumberInput |
| 6.6 | `find("How page assignments work", tabId)` — info alert with explanation text |
| 6.4a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Badge--light[data-color=blue]')?.textContent", tabId })` — "All pages (fallback)" badge is blue; others are gray |
| 6.4b | Click a Slot 1 dropdown → `read_page({ tabId, filter: 'all' })` — options list all quick actions with icon + label; inactive marked "(inactive)"; clear option available |
| 6.4c | Slot 2 dropdown opens independently; can select same or different action from Slot 1 |
| 6.4d | Change Slot 1 value → page assignments refresh; `read_page({ tabId, filter: 'all' })` — selected value persists |
| 6.4e | Clear both slots for a page type → assignment removed; `javascript_tool` confirms no slot values for that row |
| 6.8 | Toggle Auto-open Switch ON → reload page → switch still ON; toggle OFF → reload → switch OFF |
| 6.4f | `computer({ action: 'hover', tabId })` on "Auto-open" header → `read_page({ tabId, filter: 'all' })` — tooltip text "Auto-open the widget on this page type" |
| 6.4g | When Auto-open is ON: NumberInput is interactive — `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('input[type=number]:not([disabled])')?.value", tabId })` returns a number |
| 6.4h | When Auto-open is OFF: `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('input[type=number][disabled]') !== null", tabId })` — NumberInput is disabled |
| 6.4i | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('input[type=number]')?.min + ',' + document.querySelector('input[type=number]')?.max", tabId })` — returns "1,60"; input shows "s" suffix |
| 6.4j | Default delay value: `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('input[type=number]')?.value", tabId })` — returns "3" (derived from 3000ms) |
| 6.4k | `computer({ action: 'hover', tabId })` on "Delay (s)" header → tooltip text "Seconds to wait before auto-opening the widget" |
| 6.10 | After any assignment change: `find("Pending", tabId)` in sidebar — config badge shows "Pending" (draft write, not committed) |

#### 6.5 Create/Edit quick action modal (15 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 6.5a | Click "Create quick action" → `find("Create quick action", tabId)` — modal title |
| 6.5b | Click edit icon on existing row → `find("Edit quick action", tabId)` — modal title |
| 6.5c | `find("Button label", tabId)` — TextInput with required star; `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('input[maxlength]')?.maxLength", tabId })` — returns 100 |
| 6.5d | `find("Prompt template", tabId)` — Textarea with required star; `javascript_tool` — maxLength=2000 |
| 6.5e | `find("{{page_type}}", tabId)`, `find("{{page_handle}}", tabId)`, `find("{{page_title}}", tabId)`, `find("{{page_url}}", tabId)`, `find("{{product_title}}", tabId)`, `find("{{collection_title}}", tabId)` — 6 template variable chips |
| 6.5f | Click `{{product_title}}` chip → `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('textarea')?.value", tabId })` — value contains "{{product_title}}" |
| 6.5g | `find("Icon (optional)", tabId)` — TextInput present with placeholder "e.g. 📦" |
| 6.5h | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('button').length", tabId })` — 12 emoji quick-pick buttons visible; click one → icon field updates |
| 6.5i | `find("Active", tabId)` within modal — Switch with description "Inactive quick actions won't appear in the widget" |
| 6.5j | Type a label → `find("Preview", tabId)` — preview pill appears with icon + label in rounded border |
| 6.5k | Clear label field → `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('button[data-disabled]')?.textContent", tabId })` — Create/Save button is disabled |
| 6.5l | During save: `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Button-loading')?.textContent", tabId })` — button shows spinner |
| 6.5m | Click "Cancel" → modal closes; no changes saved |
| 6.5n | Edit existing action → `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('input[maxlength=\"100\"]')?.value", tabId })` — label pre-populated; textarea has prompt; icon field has icon |
| 6.7 | After saving new action: `find("Pending", tabId)` in sidebar — config badge changes to "Pending" |

#### 6.6 Confirm delete modal (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 6.6a | Click delete icon → `find("Delete quick action", tabId)` — modal title; action label shown in bold |
| 6.6b | `find("also remove it from any page assignments", tabId)` — warning text present |
| 6.6c | Click "Cancel" → modal closes; `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('table tbody tr').length", tabId })` — same row count as before |
| 6.6d | Click "Delete" → table refreshes; row count decreases by 1 |
| 6.6e | After delete: verify notification "Quick action deleted" appears — `find("Quick action deleted", tabId)` or `read_page` for notification element |

#### 6.7 Loading and error states (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 6.7a | On initial load: `find("Loading quick actions", tabId)` — LoadingState component visible |
| 6.7b | When API fails: `find("Failed to load", tabId)` — error Alert with "Retry" button |
| 6.7c | Click "Retry" → `find("Loading quick actions", tabId)` — re-enters loading state, then data appears |

### Page 7: Widget Configuration (118 tests)

Navigate to `$STANDALONE_URL/widget`.

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard.

#### 7.1 Live preview (12 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.1 | `find("Live preview", tabId)` — preview panel renders on right side |
| 7.1a | `javascript_tool(tabId, "document.querySelector('[style*=\"background\"]')?.style.background")` — check header background contains primaryColor |
| 7.1b | `find("Support", tabId)` — header title present; `find("We typically reply", tabId)` — subtitle present |
| 7.1c | `find("Hi there", tabId)` or `find("How can I help", tabId)` — greeting bubble renders in preview |
| 7.1d | Change primaryColor hex input → `computer(action:'screenshot')` — verify preview header color changed |
| 7.1e | `find` the launcher circle → `computer(action:'left_click')` on launcher → `computer(action:'screenshot')` — chat panel toggles |
| 7.1f | Click "Bottom left" in Position segmented control → `computer(action:'screenshot')` — launcher moves to left |
| 7.1g | Click "Wide" in Panel width → `computer(action:'screenshot')` — panel visibly wider |
| 7.1h | Click "None" in Panel shadow → `computer(action:'screenshot')` — shadow removed from panel |
| 7.1i | Click "Light" in Color mode → `computer(action:'screenshot')` — preview background becomes light |
| 7.1j | Select "Headset" in Launcher icon dropdown → `computer(action:'screenshot')` — launcher icon changes |
| 7.1k | `read_page(tabId)` — check for LoadingOverlay element before config loads |

#### 7.2 Appearance — Color pickers (12 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.2 | `find("Header left color", tabId)` and `find("Header right color", tabId)` — both color pickers present |
| 7.2a | `javascript_tool(tabId, "document.querySelector('input[placeholder=\"#RRGGBB\"]')?.value")` — shows saved primaryColor hex |
| 7.2b | Type "#2563EB" into hex input → `computer(action:'screenshot')` — swatch + preview header turn blue |
| 7.2c | Attempt to type "#ZZZZZZ" → verify input rejects (value remains unchanged due to regex filter) |
| 7.2d | `find` a color swatch → `computer(action:'left_click')` — hex input updates to swatch color |
| 7.2e | `computer(action:'left_click')` on ColorPicker gradient area → hex input updates in real-time |
| 7.2f | Verify gradient is OFF → `javascript_tool(tabId, "document.querySelector('[style*=\"opacity: 0.4\"]') !== null")` — right picker dimmed |
| 7.2g | Toggle "Enable header gradient" ON → right color picker becomes interactable (opacity 1) |
| 7.2h | `javascript_tool(tabId, "document.querySelectorAll('input[placeholder=\"#RRGGBB\"]')[1]?.value")` — shows headerGradientEnd |
| 7.2i | `find("Enable header gradient", tabId)` — Switch renders with label text |
| 7.2j | `read_page(tabId, filter:'interactive')` — gradient switch is unchecked by default |
| 7.2k | Toggle gradient ON → `computer(action:'screenshot')` — preview header shows gradient blend |

#### 7.3 Appearance — Font, sliders, selects (16 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.3 | `find("Font family", tabId)` — Select dropdown renders |
| 7.3a | `read_page(tabId)` — Font family combobox shows "Inter (System)" as current value |
| 7.3b | Click dropdown → `read_page(tabId)` — 4 options visible: Inter (System), Inter, Roboto, Open Sans |
| 7.3c | Select "Roboto" → `computer(action:'screenshot')` — preview font changes |
| 7.4 | `find("Border radius", tabId)` — Slider renders with "(…px)" label |
| 7.4a | `find("Border radius", tabId)` — label includes current value in px (e.g., "16px") |
| 7.4b | `find("0", tabId)` and `find("8", tabId)` and `find("16", tabId)` and `find("24", tabId)` — slider marks visible |
| 7.4c | Drag slider to 0 → `computer(action:'screenshot')` — preview corners become square |
| 7.5 | `find("Launcher size", tabId)` — Slider renders with "(…px)" label |
| 7.5a | `find("Launcher size", tabId)` — label includes current value in px (e.g., "60px") |
| 7.5b | `find("48", tabId)` and `find("60", tabId)` and `find("72", tabId)` — slider marks visible |
| 7.5c | Drag slider to 72 → `computer(action:'screenshot')` — launcher circle visibly larger |
| 7.6 | `find("Launcher icon", tabId)` — Select dropdown renders |
| 7.6a | `read_page(tabId)` — Launcher icon combobox shows "Chat bubble" as current value |
| 7.6b | Click dropdown → `read_page(tabId)` — 3 options: Chat bubble, Headset, Help circle |
| 7.6c | Select "Headset" → `computer(action:'screenshot')` — launcher icon SVG changes |

#### 7.7 Appearance — Position and offsets (9 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.7 | `find("Bottom right", tabId)` and `find("Bottom left", tabId)` — segmented control renders |
| 7.7a | `read_page(tabId)` — Position segmented control has "Bottom right" selected |
| 7.7b | Click "Bottom left" → `computer(action:'screenshot')` — launcher moves to left side of preview |
| 7.7c | `find("Horizontal offset", tabId)` — NumberInput renders with description "Distance from edge (px)" |
| 7.7d | `javascript_tool(tabId, "...querySelector('input[aria-label*=\"Horizontal\"]')?.value || ...")` — shows "20" with " px" suffix |
| 7.7e | Type 250 → verify clamped to max 200 or rejected; type -1 → verify clamped to min 0 |
| 7.7f | `find("Vertical offset", tabId)` — NumberInput renders with description "Distance from bottom (px)" |
| 7.7g | `javascript_tool(tabId, "...querySelector('input[aria-label*=\"Vertical\"]')?.value || ...")` — shows "20" with " px" suffix |
| 7.7h | Type 250 → verify clamped to max 200 or rejected; type -1 → verify clamped to min 0 |

#### 7.8 Appearance — Color mode, panel width, shadow (12 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.8 | `find("Compact", tabId)` and `find("Standard", tabId)` and `find("Wide", tabId)` — panel width segmented control |
| 7.8a | `read_page(tabId)` — Panel width segmented control has "Standard" selected |
| 7.8b | `find("Panel width", tabId)` then look for (?) tooltip icon — tooltip text about 320px/380px/440px |
| 7.8c | Click "Wide" → `computer(action:'screenshot')` — chat panel wider in preview |
| 7.8d | `find("Light", tabId)` and `find("Dark", tabId)` and `find("Auto", tabId)` — color mode segmented control |
| 7.8e | `read_page(tabId)` — Color mode segmented control has "Dark" selected |
| 7.8f | Click "Light" → `computer(action:'screenshot')` — preview switches to light theme |
| 7.8g | Click "Auto" → verify preview follows admin theme (screenshot comparison) |
| 7.9 | `find("None", tabId)` and `find("Subtle", tabId)` and `find("Heavy", tabId)` — panel shadow segmented control |
| 7.9a | `read_page(tabId)` — Panel shadow segmented control has "Standard" selected |
| 7.9b | Click "None" → `computer(action:'screenshot')` — no shadow visible on chat panel |
| 7.9c | Click "Heavy" → `computer(action:'screenshot')` — deep shadow visible on chat panel |

#### 7.10 Behavior — Greeting, pre-chat, sound (20 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.10 | `find("Greeting message", tabId)` and `find("Pre-chat form", tabId)` and `find("Sound notifications", tabId)` |
| 7.10a | `read_page(tabId, filter:'interactive')` — Greeting message switch is checked (ON by default) |
| 7.10b | Toggle greeting OFF → `javascript_tool(tabId, "document.querySelector('textarea[disabled]') !== null")` — textarea disabled |
| 7.10c | With greeting OFF → `find("<FIRST_NAME>", tabId)` returns no results — variable buttons hidden |
| 7.10d | With greeting OFF → `computer(action:'screenshot')` — no greeting bubble in preview |
| 7.10e | `javascript_tool(tabId, "document.querySelector('textarea')?.value")` — shows greeting message with 👋 emoji |
| 7.10f | `find` the (?) icon near "Greeting message" label → hover → tooltip about static welcome message |
| 7.10g | Clear textarea + type "Welcome!" → preview greeting bubble updates to "Welcome!" |
| 7.10h | Type a long greeting (4+ lines) → textarea grows up to maxRows=4 |
| 7.11 | `find("<FIRST_NAME>", tabId)` and `find("<LAST_NAME>", tabId)` and `find("<FULL_NAME>", tabId)` and `find("<COMPANY>", tabId)` — 4 template buttons |
| 7.11a | Click \<FIRST_NAME\> button → `javascript_tool` read textarea value — contains "\<FIRST_NAME\>" token |
| 7.11b | With token in greeting → preview bubble shows "Sarah" instead of \<FIRST_NAME\> |
| 7.11c | `find("Pre-chat form", tabId)` — Switch renders with label and description |
| 7.11d | `read_page(tabId, filter:'interactive')` — Pre-chat form switch is unchecked (OFF by default) |
| 7.11e | Toggle pre-chat ON → `find("Name", tabId)` and `find("Email", tabId)` and `find("Phone", tabId)` and `find("Company", tabId)` — 4 chips visible |
| 7.11f | `read_page(tabId)` — Name and Email chips are selected by default |
| 7.11g | Click Phone chip → verify it becomes selected; click Email chip → verify it becomes deselected |
| 7.11h | `find("Sound notifications", tabId)` — Switch renders with label |
| 7.11i | `read_page(tabId, filter:'interactive')` — Sound notifications switch is checked (ON by default) |
| 7.11j | Toggle Sound notifications OFF → verify switch state changes |

#### 7.12 Content — Header, placeholder, agent identity (15 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.12 | `find("Header title", tabId)` and `find("Header subtitle", tabId)` and `find("Input placeholder", tabId)` — 3 text fields |
| 7.12a | `javascript_tool(tabId, "...querySelector('input')...value")` — Header title shows "Support" (or saved value) |
| 7.12b | Clear Header title → type "Help Desk" → preview header updates to "Help Desk" |
| 7.12c | Clear Header title → `read_page(tabId)` — placeholder text "Support" visible |
| 7.12d | Header subtitle input value shows saved text (default "We typically reply within minutes") |
| 7.12e | Type new subtitle → preview header subtitle updates in real-time |
| 7.12f | Input placeholder input value shows saved text (default "Type your message...") |
| 7.12g | Type new placeholder → preview input bar placeholder text updates |
| 7.13 | `find("Agent display name", tabId)` and `find("Agent avatar URL", tabId)` — both fields present below divider |
| 7.13a | Agent display name input value — empty by default, placeholder "Agent Red" |
| 7.13b | Type "Maya" → preview agent initials change from "AR" to "MA" |
| 7.13c | Agent avatar URL input value — empty by default, placeholder "https://example.com/avatar.png" |
| 7.13d | Enter valid image URL → `find("Avatar preview", tabId)` — circular preview appears below input |
| 7.13e | After setting avatar URL → `computer(action:'screenshot')` — preview shows avatar image in header and bubbles |
| 7.13f | Enter broken URL → avatar img element hidden (onError handler) |

#### 7.14 Controls — Reset and Save (8 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.14 | `find("Reset to defaults", tabId)` and `find("Save draft inputs", tabId)` — both buttons present |
| 7.14a | Change a setting → click "Reset to defaults" → all fields revert to defaults (primaryColor=#ff3621, etc.) |
| 7.14b | After reset → `computer(action:'screenshot')` — preview shows default appearance |
| 7.14c | Click "Save draft inputs" → `find("saved successfully", tabId)` or notification appears with success message |
| 7.14d | `read_page(tabId)` — Save button shows loading spinner while API call in progress |
| 7.14e | (Simulated failure) — verify error notification "Failed to save widget settings" displays |
| 7.14f | After successful save → sidebar activation badge updates (refreshActivationStatus) |
| 7.14g | After save → reload page → verify saved values persist (not reverted to defaults) |

#### 7.15 Section tooltips (7 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.15 | `find("?", tabId)` or `find("HelpTooltip", tabId)` — (?) icons on Appearance, Panel width, Greeting, Pre-chat, Content |
| 7.15a | Hover Appearance (?) → tooltip shows "Colors, position, size, and visual style..." |
| 7.15b | Hover Behavior (?) → tooltip shows "Auto-open timing, sound notifications..." |
| 7.15c | Hover Content (?) → tooltip shows "Header text, greeting message, agent identity..." |
| 7.15d | Hover Panel width (?) → tooltip mentions Compact (320px), Standard (380px), Wide (440px) |
| 7.15e | Hover Greeting message (?) → tooltip explains static welcome message, not AI-generated |
| 7.15f | Hover Pre-chat form (?) → tooltip explains self-reported identity, not for authentication |

#### 7.16–7.20 Agent avatar upload (5 tests — SKIP D22)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.16 | SKIP (D22 deferred) — avatar upload not yet implemented |
| 7.17 | SKIP (D22 deferred) — file type validation not yet implemented |
| 7.18 | SKIP (D22 deferred) — crop UI not yet implemented |
| 7.19 | SKIP (D22 deferred) — resize not yet implemented |
| 7.20 | SKIP (D22 deferred) — avatar persistence not yet implemented |

#### 7.21–7.22 End-to-end (2 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 7.21 | Click launcher in preview → chat panel opens/closes — `computer(action:'screenshot')` before and after |
| 7.22 | Change a setting → Save → reload → verify values persisted — full save round-trip test |

### Page 8: Integrations (32 tests)

Navigate to `$STANDALONE_URL/integrations`.

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard.

#### 8.1 Page header and loading states (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 8.1 | `find("Shopify", tabId)`, `find("Zendesk", tabId)`, `find("Mailchimp", tabId)`, `find("Google Analytics", tabId)` — integration cards render |
| 8.1a | `find("Integrations", tabId)` — page title; `find("Connect third-party services", tabId)` — subtitle |
| 8.1b | Before data loads: `find("Loading integrations", tabId)` — loading state |
| 8.1c | When API fails: `find("Failed to load integrations", tabId)` — error message in red |
| 8.1d | When empty array: `find("No integrations available", tabId)` — empty state |

#### 8.2 Integration card layout (8 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 8.2 | For Shopify (connected): `find("Deactivate", tabId)` and `find("Disconnect", tabId)` — action buttons present |
| 8.2a | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('img[alt*=logo]').length", tabId })` — logo images render (or fallback SVGs) |
| 8.2b | `find("Shopify", tabId)` — integration name in bold text |
| 8.2c | `find("Connected", tabId)` — green status badge with dot for connected integrations |
| 8.2d | For disconnected: `find("Not Connected", tabId)` — gray status badge |
| 8.2e | For error state: `find("Error", tabId)` — red status badge |
| 8.2f | Each card has description text below name (e.g., "Core commerce integration" for Shopify) |
| 8.5 | Hover (?) next to each integration name → tooltip with description and doc link containing "integrations" |

#### 8.3 Coming Soon and tier-gated badges (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 8.3 | `find("Coming Soon", tabId)` — purple badges on coming-soon integrations |
| 8.3a | `find("under development", tabId)` — coming-soon message text |
| 8.3b | Coming-soon cards: no "Activate", "Deactivate", or "Disconnect" buttons present |
| 8.3c | For tier-gated: yellow badge with tier name (e.g., "↑ Professional tier") |
| 8.3d | `find("Upgrade to", tabId)` — tier-gated upgrade message |

#### 8.4 Activate / Deactivate / Disconnect actions (11 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 8.4a | For disconnected + tier-met: `find("Activate", tabId)` — primary red button |
| 8.4b | Click "Activate" → button text changes to "Activating..." |
| 8.4c | After activate: `read_network_requests` shows activate API call; success notification; card shows "Connected" |
| 8.4d | When activate fails: notification "Failed to activate integration." |
| 8.4e | For connected: `find("Deactivate", tabId)` — outline button |
| 8.4f | Click "Deactivate" → button text changes to "Deactivating..." |
| 8.4g | After deactivate: success notification; card shows disconnected state |
| 8.4h | Click "Disconnect" → inline confirmation: `find("This removes credentials", tabId)` with "Confirm" and "Cancel" |
| 8.4i | Click "Confirm" → `read_network_requests` shows disconnect API call; success notification |
| 8.4j | Click "Cancel" → confirmation text disappears; no API call |
| 8.6 | Hover "Deactivate" or "Disconnect" → background changes only, no border change |

#### 8.5 Summary footer (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 8.4 | `find("integrations active", tabId)` — footer text with count |
| 8.5a | On Starter/Trial tier: `find("require Professional", tabId)` — tier hint text |
| 8.5b | On Professional+ tier: "require Professional" text NOT present |

### Page 9: Memory & Privacy (58 tests)

Navigate to `$STANDALONE_URL/memory-privacy`.

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard.

#### 9.1 Page header and upgrade banner (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.1 | `find("Customer context", tabId)`, `find("Conversation memory", tabId)`, `find("Cross-session learning", tabId)` — 3 feature cards present |
| 9.1a | `find("Memory & privacy", tabId)` — page title; `find("Configure how your AI remembers", tabId)` — subtitle |
| 9.1b | For Starter tier: `find("Unlock advanced memory features", tabId)` — upgrade banner present |
| 9.1c | For Professional+ tier: `find("Unlock advanced memory features", tabId)` should NOT be present |

#### 9.2 Layer 1 — Customer context (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.2a | `find("Customer context", tabId)` — card title; `find("Structured customer profiles", tabId)` — description |
| 9.2 | `find("All tiers", tabId)` — green badge on Customer context card |
| 9.2b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.mantine-Switch-input')[0]?.checked", tabId })` — matches config.memory_enabled |
| 9.2c | Click Customer context switch → label toggles between "Enabled" / "Disabled" |
| 9.2d | `find("help icon near Customer context", tabId)` or hover (?) → tooltip with "customer profiles" text; doc link contains "customer-memory" |

#### 9.3 Layer 2 — Conversation memory (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.3a | `find("Conversation memory", tabId)` — card title; `find("All tiers", tabId)` — green badge |
| 9.3 | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.mantine-Switch-input')[1]?.checked", tabId })` — matches config state |
| 9.3b | When Customer context OFF: `javascript_tool` — second switch is disabled |
| 9.3c | When Customer context ON: second switch is enabled and clickable |
| 9.3d | Hover (?) → tooltip with "Vectorized conversation transcripts" text; doc link contains "memory-enabled" |

#### 9.4 Layer 3 — Cross-session learning (12 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.4a | `find("Cross-session learning", tabId)` — card title present |
| 9.4b | For Pro+ tier: `javascript_tool` — blue "Professional+" badge present |
| 9.4c | For Starter tier: `find("Professional+ required", tabId)` — gray badge |
| 9.10 | For Starter tier: `javascript_tool` — cross-session switch is disabled (cannot toggle) |
| 9.4d | When memoryEnabled=false: cross-session switch disabled regardless of tier |
| 9.4e | On Pro+ with memory ON: toggle switch → label changes "Enabled" / "Disabled" |
| 9.4f | When Pro+ AND crossSessionLearning ON: `find("Pattern decay", tabId)` — slider section visible |
| 9.4g | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Slider')?.getAttribute('aria-valuemin') + ',' + document.querySelector('.mantine-Slider')?.getAttribute('aria-valuemax')", tabId })` — returns "30,365" |
| 9.4h | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Slider')?.getAttribute('aria-valuenow')", tabId })` — matches config patternDecayDays |
| 9.4i | When memoryEnabled=false: slider is disabled |
| 9.4j | Hover (?) on Cross-session → tooltip with "behavioral patterns" text; doc link contains "pattern-learning" |
| 9.4k | Hover (?) on Pattern decay → tooltip explaining decay duration |

#### 9.5 Layer 4 — Dedicated model training (6 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.4 | `find("Dedicated model training", tabId)` — card present; `find("$299/month", tabId)` — pricing shown |
| 9.5a | `find("1,000+ historical interactions", tabId)` — description text |
| 9.5b | For Enterprise: `find("Enterprise add-on", tabId)` — grape badge |
| 9.5c | For non-Enterprise: `find("Enterprise required", tabId)` — gray badge |
| 9.5d | For non-Enterprise: `find("Upgrade to Enterprise", tabId)` — upgrade alert |
| 9.5e | For Enterprise: upgrade alert NOT present |
| 9.5f | Hover (?) → tooltip with "custom AI model"; doc link contains "dedicated-model-training" |

#### 9.6 Data retention & privacy accordion (14 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.5 | `find("Data retention & privacy", tabId)` — collapsible accordion section |
| 9.6 | `find("90 days", tabId)` or `find("1 year", tabId)` — retention period select with current value |
| 9.6a | Accordion expanded by default (content visible without clicking) |
| 9.6b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Select-input')?.value", tabId })` — matches retentionDays from config |
| 9.6c | Click retention select → `read_page` — 5 options: 30 days, 90 days, 180 days, 1 year, 2 years |
| 9.6d | Select different option → value updates in select display |
| 9.7 | `find("PII scrubbing", tabId)`, `find("Consent required", tabId)`, `find("Automatic deletion", tabId)` — 3 privacy toggles present |
| 9.6e | `javascript_tool` — PII scrubbing switch checked matches config.pii_scrubbing |
| 9.6f | `find("redact personally identifiable information", tabId)` — PII scrubbing description |
| 9.6g | `javascript_tool` — Consent required switch checked matches config.consent_collection_enabled |
| 9.6h | `find("Require explicit customer consent", tabId)` — consent description |
| 9.6i | `javascript_tool` — Auto-delete switch checked matches config.auto_delete_on_request |
| 9.6j | `find("GDPR deletion request", tabId)` — auto-delete description |
| 9.9 | Hover (?) on "Data retention & privacy" → tooltip with data retention explanation |

#### 9.7 Save and persist (6 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.8 | `find("Save draft inputs", tabId)` — red button at bottom; NOT present at top of page |
| 9.7a | Click Save → `javascript_tool` — button shows loading spinner |
| 9.11 | Toggle settings → Save → reload page → `javascript_tool` — all 8 fields persist correctly |
| 9.7b | After save: `find("Draft memory & privacy settings saved", tabId)` — green notification |
| 9.7c | When save fails: notification with error message |
| 9.7d | After save: sidebar badge may change to "Pending" — `find("Pending", tabId)` |

#### 9.8 Backend-verified tests (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.12 | API verification: `javascript_tool` fetch conversation transcript → verify [REDACTED:email] / [REDACTED:phone] patterns in stored messages |
| 9.13 | SKIP — consent prompt deferred to widget phase 3-5 |
| 9.14 | API verification: GDPR deletion covered by 48 unit tests; E2E webhook testing deferred |

#### 9.9 Loading and error states (2 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 9.9a | On initial load: `find("Loading memory settings", tabId)` — LoadingState component |
| 9.9b | When config API fails: `find("Failed to load settings", tabId)` — error Alert |

### Page 10: Billing & Usage (77 tests)

Navigate to `$STANDALONE_URL/billing`.

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard.

#### 10.1 Page header and error states (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 10.1 | `find("Billing & usage", tabId)` — page title; `find("Manage your subscription", tabId)` — subtitle |
| 10.1a | Before data loads: `find("Loading billing data", tabId)` — LoadingState renders |
| 10.1b | When usage API forced error: `find("Usage data unavailable", tabId)` — red Alert with error message |
| 10.1c | After error: remaining page sections still render below the Alert (non-blocking) |
| 10.1d | After API resolves: `find("Loading billing data", tabId)` no longer present; page content renders |

#### 10.2 Plan card (12 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 10.2a | `find("Current plan", tabId)` — plan card renders with label |
| 10.2b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Badge-root.mantine-Badge-filled')?.textContent", tabId })` — returns tier name (e.g., "Professional"); badge color matches tier (green for professional) |
| 10.2c | `find("Active", tabId)` — green status badge |
| 10.2d | `find("Included conversations", tabId)` — label renders; value ends with "/mo" |
| 10.2e | `find("Used this period", tabId)` — label renders with numeric value |
| 10.2f | `find("Remaining", tabId)` — label renders with numeric value |
| 10.2g | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.mantine-Text-root').length", tabId })` — page has expected element count after data refresh |
| 10.2h | When no usage: "Used this period" shows "0"; "Remaining" equals "Included" value |
| 10.2i | For Stripe tenant: `find("Manage subscription", tabId)` — button present and clickable |
| 10.2j | For non-Stripe tenant: `find("Manage subscription", tabId)` should NOT be present |
| 10.2k | Click "Manage subscription" → verify network request to POST /api/billing/portal via `read_network_requests` |
| 10.2l | Hover (?) near "Current plan" → HelpTooltip with "subscription tier" text; doc link contains "billing/overview" |

#### 10.3 Usage stat cards (16 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 10.3 | `find("Conversations used", tabId)`, `find("Pack balance", tabId)`, `find("Current overage", tabId)`, `find("Estimated overage cost", tabId)` — all 4 cards present |
| 10.3a | `javascript_tool({ action: 'javascript_exec', text: "Array.from(document.querySelectorAll('.mantine-Text-root')).find(e => e.textContent.includes('/')).textContent", tabId })` — "X / Y" format for conversations used |
| 10.3b | `find("of included allowance", tabId)` — percentage subtext present |
| 10.3c | `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-RingProgress-root') !== null", tabId })` — RingProgress renders; color changes at thresholds (>90%=red, >75%=yellow) |
| 10.3d | Near "Pack balance": value is formatted number from API |
| 10.3e | `find("remaining conversations", tabId)` — pack balance subtext |
| 10.3f | Near "Current overage": dollar value formatted with $ prefix |
| 10.3g | When overage > 0: `find("overage conversations", tabId)` — count subtext; when 0: `find("No overage charges", tabId)` |
| 10.3h | Near "Estimated overage cost": dollar value |
| 10.3i | `find("Additional charges this period", tabId)` — estimated cost subtext |
| 10.3j | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('[data-tippy-root], .mantine-Tooltip-tooltip, .mantine-Popover-dropdown').length >= 0", tabId })` — tooltips accessible via hover |
| 10.3k | Hover (?) near "Conversations used" → tooltip mentions "billing period" and "monthly allowance" |
| 10.3l | Hover (?) near "Pack balance" → tooltip mentions "pre-purchased packs" |
| 10.3m | Hover (?) near "Current overage" → tooltip mentions "beyond your included allowance" |
| 10.3n | Hover (?) near "Estimated overage cost" → tooltip mentions "projected additional charges" |
| 10.3o | With zero data: "0 / 0" conversations, "0" pack balance, "$0.00" cost values |

#### 10.4 Usage alerts (3 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 10.4a | When API returns activeAlerts: `find("Usage alerts", tabId)` — yellow Alert renders |
| 10.4b | Each alert string renders as readable Text inside the Alert |
| 10.4c | When activeAlerts empty: `find("Usage alerts", tabId)` should NOT be present |

#### 10.5 Daily usage chart (10 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 10.5 | `find("Daily usage (30 days)", tabId)` — chart section title; `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.recharts-responsive-container') !== null", tabId })` — chart renders |
| 10.5a | Hover (?) near "Daily usage" → HelpTooltip with "billable conversations per day"; doc link contains "billing/overview" |
| 10.5b | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.recharts-area').length", tabId })` — returns 2 (Total and Billable) |
| 10.5c | `find("Total", tabId)` and `find("Billable", tabId)` — legend items below chart |
| 10.5d | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('.recharts-xAxis .recharts-cartesian-axis-tick').length > 0", tabId })` — X-axis ticks present |
| 10.5e | Chart data points correspond to dailyVolume API response days array |
| 10.5f | While loading chart: `javascript_tool({ action: 'javascript_exec', text: "document.querySelector('.mantine-Loader-root') !== null", tabId })` — Loader spinner in chart area |
| 10.5g | When no data: `find("No usage data available yet", tabId)` — empty state message |
| 10.5h | `javascript_tool({ action: 'javascript_exec', text: "document.querySelectorAll('linearGradient').length >= 2", tabId })` — gradient fills defined |
| 10.5i | Hover over chart area → Recharts tooltip with Date, Total, Billable values |

#### 10.6 Conversation packs (11 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 10.6a | `find("Conversation packs", tabId)` — section title; `find("Pre-purchase conversations at a discounted rate", tabId)` — subtitle |
| 10.6b | Hover (?) near "Conversation packs" → tooltip mentions "pre-purchase" and "FIFO" and "90 days"; doc link contains "billing/overview" |
| 10.4 | `find("1,000", tabId)`, `find("5,000", tabId)`, `find("20,000", tabId)` — 3 pack cards |
| 10.6c | Near "1,000": `find("$29.00", tabId)` — price; `find("$0.029/conversation", tabId)` — rate |
| 10.6d | Near "5,000": `find("$99.00", tabId)` — price; `find("$0.020/conversation", tabId)` — rate |
| 10.6e | Near "20,000": `find("$249.00", tabId)` — price; `find("$0.012/conversation", tabId)` — rate |
| 10.6f | `javascript_tool({ action: 'javascript_exec', text: "Array.from(document.querySelectorAll('button')).filter(b => b.textContent.trim() === 'Purchase').length", tabId })` — returns 3 |
| 10.6g | Click "Purchase" on 1K pack → `read_network_requests` shows POST /api/packs/purchase with pack_id "pack_1k" |
| 10.6h | During purchase: clicked button shows loading state (spinner), button disabled |
| 10.6i | Other pack Purchase buttons remain enabled while one is purchasing |
| 10.6j | When purchase API fails: notification toast with "Failed to start purchase" — `read_console_messages` or check toast text |

#### 10.7 Add-on modules (15 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 10.5 | `find("Multi-Language Pack", tabId)`, `find("Advanced Analytics", tabId)`, `find("Mailchimp Integration", tabId)`, `find("Google Analytics", tabId)`, `find("Custom Integration", tabId)` — 5 cards |
| 10.7a | Near "Multi-Language Pack": `find("$99.00", tabId)`, `find("All tiers", tabId)` green badge, description text |
| 10.7b | Near "Advanced Analytics": `find("$149.00", tabId)`, `find("Professional+", tabId)` blue badge |
| 10.7c | Near "Mailchimp Integration": `find("$49.00", tabId)`, `find("Professional+", tabId)` blue badge |
| 10.7d | Near "Google Analytics": `find("$49.00", tabId)`, `find("Professional+", tabId)` blue badge |
| 10.7e | Near "Custom Integration": `find("$299.00", tabId)`, `find("Enterprise", tabId)` grape badge |
| 10.7 | `javascript_tool({ action: 'javascript_exec', text: "Array.from(document.querySelectorAll('.mantine-Badge-root')).map(b => b.textContent).join(',')", tabId })` — verify badge color mapping (green=All tiers, blue=Professional+, grape=Enterprise) |
| 10.6 | For tier-met add-ons: `find("Subscribe", tabId)` — enabled outline buttons present |
| 10.7f | For tier-not-met add-ons: `find("Requires", tabId)` — disabled gray buttons with tier name |
| 10.9 | `javascript_tool({ action: 'javascript_exec', text: "Array.from(document.querySelectorAll('.mantine-Paper-root')).filter(p => p.style.opacity === '0.65').length", tabId })` — unavailable add-on cards have reduced opacity |
| 10.7g | Click "Subscribe" on available add-on → info notification "Add-on checkout coming soon." |
| 10.8 | Disabled button text reads "Requires Professional+" or "Requires Enterprise" — showing minimum entitlement |
| 10.7h | Inject Starter tier → Multi-Language has "Subscribe"; Analytics/Mailchimp/GA4 show "Requires Professional+"; Custom shows "Requires Enterprise" |
| 10.7i | Inject Professional tier → Multi-Language/Analytics/Mailchimp/GA4 have "Subscribe"; Custom shows "Requires Enterprise" |
| 10.10 | Inject Enterprise tier → all 5 add-ons show "Subscribe" (none gated) |

#### 10.8 Manage billing card (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| 10.8a | For Stripe tenant: `find("Invoices & payment methods", tabId)` — manage billing card renders |
| 10.8b | `find("View invoice history, update payment methods", tabId)` — description text |
| 10.8c | Click "Manage billing" → `read_network_requests` shows POST /api/billing/portal; opens new tab |
| 10.8d | For non-Stripe tenant: `find("Invoices & payment methods", tabId)` should NOT be present |
| 10.8e | When portal API fails: notification toast "Failed to open billing portal. Please try again." |

---

## Test Execution — SPA Provider Console (115 tests)

After completing Standalone Admin tests, inject SPA auth (Steps B.1–B.4) and verify
each Provider Console page loads and renders its primary content.

> Provider Console tests verify presence, no-error rendering, correct navigation group structure, **data-binding correctness** (API response fields populate visible UI elements), **dropdown operability** (filter selects have populated options), **data value visibility** (tenant IDs, emails, dates, status values render with expected types), and **logo/branding integrity**. Pages are read-only dashboards — input manipulation and state-change dimensions are not applicable.

#### P.0 Provider auth and navigation (5 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.0a | Auth injection: `javascript_tool` set `agentred_provider_key` + `agentred_provider_mfa_token` in sessionStorage → navigate to `$PROVIDER_URL` → page loads (no login redirect) |
| P.0b | Sidebar navigation groups: `find("Overview", tabId)`, `find("Operations", tabId)`, `find("Compliance", tabId)` or `find("Security", tabId)`, `find("Account", tabId)` — 4 nav groups |
| P.0c | Sidebar nav items: at least 13 navigation links present via `read_page(tabId, { filter: 'interactive' })` |
| P.0d | `read_console_messages(onlyErrors:true)` — zero console errors on initial load |
| P.0e | Provider header shows "Service Provider Console" text — not tenant admin branding |

#### P.1 Health Dashboard (8 tests)

Navigate to `$PROVIDER_URL/`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.1a | `find("Health", tabId)` — dashboard page heading renders |
| P.1b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.1c | **Data-binding: System health status** — `javascript_tool(tabId, "document.body.innerText.match(/healthy\|degraded\|unhealthy/i)?.[0]")` — system status renders a recognized value (not undefined/empty) |
| P.1d | **Data-binding: Tenant summary stats** — `javascript_tool(tabId, "document.body.innerText.match(/Total tenants.*?(\\d+)/s)?.[1]")` — "Total tenants" stat card shows a numeric count ≥ 1 |
| P.1e | **Data-binding: By-status breakdown** — `find("active", tabId)` within tenant summary section — at least one status category renders with a count |
| P.1f | **Data-binding: Circuit breaker states** — `find("closed", tabId)` or `find("open", tabId)` — circuit breaker section renders actual state values (not empty) |
| P.1g | **Data-binding: Recent deployments** — `javascript_tool(tabId, "document.querySelectorAll('table tbody tr').length > 0 || document.body.innerText.includes('No recent')")` — deployment table has rows OR shows explicit empty state |
| P.1h | `computer(action:'screenshot')` — capture visual state |

#### P.2 Tenant Directory (12 tests)

Navigate to `$PROVIDER_URL/tenants`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.2a | `find("Tenant", tabId)` — page heading renders |
| P.2b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.2c | **Data-binding: Total tenant count** — `javascript_tool(tabId, "document.body.innerText.match(/Total.*?(\\d+)/)?.[1]")` — total tenants stat card shows numeric count ≥ 1 |
| P.2d | **Data-binding: Tenant ID visible** — `find("remaker-digital-001", tabId)` — at least one tenant row shows a tenant ID string (not empty cell) |
| P.2e | **Data-binding: Billing channel** — `javascript_tool(tabId, "document.body.innerText.match(/stripe\|shopify\|manual/i)?.[0]")` — billing channel column shows a recognized value |
| P.2f | **Data-binding: Customer email** — `javascript_tool(tabId, "document.body.innerText.match(/[\\w.-]+@[\\w.-]+\\.[a-z]{2,}/)?.[0]")` — email column shows an email address pattern (or "--" if unset) |
| P.2g | **Data-binding: Created date** — `javascript_tool(tabId, "document.body.innerText.match(/\\d{4}-\\d{2}-\\d{2}\|\\w{3} \\d{1,2}/)?.[0]")` — created column shows a date (not empty) |
| P.2h | **Data-binding: Status filter dropdown** — `find("Status", tabId)` → click select → `javascript_tool(tabId, "document.querySelectorAll('[role=option]').length")` — dropdown has ≥ 2 options (e.g., active, inactive) |
| P.2i | **Data-binding: Tier filter dropdown** — `find("Tier", tabId)` → click select → `javascript_tool(tabId, "document.querySelectorAll('[role=option]').length")` — dropdown has ≥ 2 options (e.g., starter, professional) |
| P.2j | **Data-binding: Channel filter dropdown** — `find("Channel", tabId)` → click select → `javascript_tool(tabId, "document.querySelectorAll('[role=option]').length")` — dropdown has ≥ 1 option |
| P.2k | **Data-binding: Shop domain** — `javascript_tool(tabId, "document.body.innerText.match(/\\.myshopify\\.com/)?.[0]")` — shop domain column shows a domain string (or "--" if billing_channel is not shopify) |
| P.2l | `computer(action:'screenshot')` — capture visual state |

#### P.3 Deployment History (7 tests)

Navigate to `$PROVIDER_URL/deployments`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.3a | `find("Deployment", tabId)` or `find("deployment", tabId)` — page heading renders |
| P.3b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.3c | **Data-binding: Deployment table rows** — `javascript_tool(tabId, "document.querySelectorAll('table tbody tr').length")` — table has ≥ 1 row (at least current deployment) |
| P.3d | **Data-binding: Event type values** — `javascript_tool(tabId, "document.body.innerText.match(/deploy\|rollback\|scale\|restart/i)?.[0]")` — event type column shows recognized deployment event type |
| P.3e | **Data-binding: Version string** — `javascript_tool(tabId, "document.body.innerText.match(/v\\d+\\.\\d+\\.\\d+/)?.[0]")` — version column shows semantic version (e.g., "v1.51.0") |
| P.3f | **Data-binding: Timestamp** — `javascript_tool(tabId, "document.body.innerText.match(/\\d{4}-\\d{2}-\\d{2}\|\\w{3} \\d{1,2}/)?.[0]")` — timestamp column shows a date value |
| P.3g | `computer(action:'screenshot')` — capture visual state |

#### P.4 Queue Health (8 tests)

Navigate to `$PROVIDER_URL/queues`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.4a | `find("Queue", tabId)` or `find("queue", tabId)` — page heading renders |
| P.4b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.4c | **Data-binding: Queue summary stats** — `javascript_tool(tabId, "document.body.innerText.match(/Total (tenants\|messages\|bytes).*?(\\d+)/si)?.[0]")` — at least one summary stat card shows a numeric value |
| P.4d | **Data-binding: Stream table rows** — `javascript_tool(tabId, "document.querySelectorAll('table tbody tr').length")` — table has ≥ 1 row OR shows explicit "No queue data" empty state |
| P.4e | **Data-binding: Tenant ID in table** — `javascript_tool(tabId, "[...document.querySelectorAll('table td')].some(td => /remaker-digital\|test-customer/.test(td.textContent))")` — tenant ID column shows recognized tenant identifier (not empty) |
| P.4f | **Data-binding: Stream name** — `javascript_tool(tabId, "[...document.querySelectorAll('table td')].some(td => td.textContent.length > 0)")` — stream name column populated (not blank cells) |
| P.4g | **Data-binding: Consumer count** — `javascript_tool(tabId, "document.body.innerText.match(/consumer/i)")` — consumer count column header and values render |
| P.4h | `computer(action:'screenshot')` — capture visual state |

#### P.5 Integration Health (4 tests)

Navigate to `$PROVIDER_URL/integrations`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.5a | Page renders with integration status content — `find("Integration", tabId)` or `find("integration", tabId)` |
| P.5b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.5c | **Data-binding: Integration status values** — `javascript_tool(tabId, "document.body.innerText.match(/connected\|disconnected\|healthy\|degraded/i)?.[0]")` — at least one integration shows a recognized status (not empty) |
| P.5d | `computer(action:'screenshot')` — capture visual state |

#### P.6 Status Page (4 tests)

Navigate to `$PROVIDER_URL/status`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.6a | `find("Status", tabId)` — page management renders |
| P.6b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.6c | **Data-binding: Overall status** — `javascript_tool(tabId, "document.body.innerText.match(/operational\|degraded\|outage\|maintenance/i)?.[0]")` — overall status shows a recognized value |
| P.6d | `computer(action:'screenshot')` — capture visual state |

#### P.7 Alert Configuration (5 tests)

Navigate to `$PROVIDER_URL/alerts`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.7a | `find("Alert", tabId)` or `find("alert", tabId)` — page renders |
| P.7b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.7c | **Data-binding: Alert rules list** — `javascript_tool(tabId, "document.querySelectorAll('table tbody tr, [class*=Card]').length")` — alert rules table/cards have ≥ 1 item OR shows explicit "No alerts" empty state |
| P.7d | **Data-binding: Rule type values** — `javascript_tool(tabId, "document.body.innerText.match(/queue_depth\|secret_expiry\|circuit_breaker\|sla_breach\|incident/i)?.[0]")` — at least one rule type is a recognized AlertEngine type |
| P.7e | `computer(action:'screenshot')` — capture visual state |

#### P.8 Support Diagnostics (4 tests)

Navigate to `$PROVIDER_URL/diagnostics`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.8a | `find("Diagnostic", tabId)` or `find("diagnostic", tabId)` — page renders |
| P.8b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.8c | **Data-binding: Diagnostic data** — `javascript_tool(tabId, "document.querySelectorAll('table tbody tr, [class*=Card], [class*=Section]').length > 0")` — diagnostic content renders (not blank page) |
| P.8d | `computer(action:'screenshot')` — capture visual state |

#### P.9 Compliance Dashboard (5 tests)

Navigate to `$PROVIDER_URL/compliance`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.9a | `find("Compliance", tabId)` or `find("compliance", tabId)` — page renders |
| P.9b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.9c | **Data-binding: Assessment results** — `javascript_tool(tabId, "document.body.innerText.match(/pass\|fail\|warning\|compliant\|non-compliant/i)?.[0]")` — at least one compliance check shows a recognized result (not empty) |
| P.9d | **Data-binding: Assessment item count** — `javascript_tool(tabId, "document.querySelectorAll('table tbody tr, [class*=Card], [class*=item]').length")` — compliance checklist has ≥ 1 item |
| P.9e | `computer(action:'screenshot')` — capture visual state |

#### P.10 Secret Posture (5 tests)

Navigate to `$PROVIDER_URL/secrets`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.10a | `find("Secret", tabId)` or `find("secret", tabId)` — page renders |
| P.10b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.10c | **Data-binding: Secret status indicators** — `javascript_tool(tabId, "document.body.innerText.match(/valid\|expiring\|expired\|rotated/i)?.[0]")` — at least one secret shows a recognized status |
| P.10d | **Data-binding: Secret list** — `javascript_tool(tabId, "document.querySelectorAll('table tbody tr, [class*=Card]').length")` — secrets table/cards have ≥ 1 item |
| P.10e | `computer(action:'screenshot')` — capture visual state |

#### P.11 Billing Health (8 tests)

Navigate to `$PROVIDER_URL/billing`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.11a | Page renders with billing health content — `find("Billing", tabId)` or `find("billing", tabId)` |
| P.11b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.11c | **Data-binding: Total tenants stat** — `javascript_tool(tabId, "document.body.innerText.match(/Total.*?(\\d+)/)?.[1]")` — stat card shows numeric tenant count ≥ 1 |
| P.11d | **Data-binding: Tenant ID in table** — `javascript_tool(tabId, "[...document.querySelectorAll('table td')].some(td => /remaker-digital\|test-customer/.test(td.textContent))")` — billing table shows recognized tenant ID |
| P.11e | **Data-binding: Reconciliation status** — `javascript_tool(tabId, "document.body.innerText.match(/reconciled\|pending\|failed\|review/i)?.[0]")` — reconciliation column shows recognized status value |
| P.11f | **Data-binding: Webhook success rate** — `javascript_tool(tabId, "document.body.innerText.match(/(\\d+\\.?\\d*)%/)?.[0]")` — webhook success rate shows percentage value |
| P.11g | **Data-binding: Needs review flag** — `javascript_tool(tabId, "document.body.innerText.match(/needs review/i)?.[0] || 'none flagged'")` — review status renders (explicit value or absence) |
| P.11h | `computer(action:'screenshot')` — capture visual state |

#### P.12 Cost Analytics (4 tests)

Navigate to `$PROVIDER_URL/costs`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.12a | `find("Cost", tabId)` or `find("cost", tabId)` — page renders |
| P.12b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.12c | **Data-binding: Cost data** — `javascript_tool(tabId, "document.body.innerText.match(/\\$\\d+\\.?\\d*\|\\d+\\.?\\d*%/)?.[0]")` — cost figures or percentages render (not empty page) |
| P.12d | `computer(action:'screenshot')` — capture visual state |

#### P.13 SLA Trends (8 tests)

Navigate to `$PROVIDER_URL/sla`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.13a | `find("SLA", tabId)` or `find("sla", tabId)` — page renders |
| P.13b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.13c | **Data-binding: Uptime percentage** — `javascript_tool(tabId, "document.body.innerText.match(/(\\d+\\.?\\d*)%/)?.[0]")` — uptime stat shows percentage value (e.g., "99.9%") |
| P.13d | **Data-binding: Latency metrics** — `javascript_tool(tabId, "document.body.innerText.match(/p50\|p95\|p99/i)?.[0]")` — latency percentile labels render |
| P.13e | **Data-binding: Latency values** — `javascript_tool(tabId, "document.body.innerText.match(/(\\d+\\.?\\d*)\\s*ms/)?.[0]")` — latency values show numeric ms values (e.g., "45ms") |
| P.13f | **Data-binding: Error budget** — `javascript_tool(tabId, "document.body.innerText.match(/budget.*?(\\d+)/si)?.[0]")` — error budget section shows numeric values |
| P.13g | **Data-binding: Range selector** — `find("7", tabId)` or `find("30", tabId)` or `find("90", tabId)` — range/period selector buttons present with operable options |
| P.13h | `computer(action:'screenshot')` — capture visual state |

#### P.14 Abuse Detection (4 tests)

Navigate to `$PROVIDER_URL/abuse`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.14a | `find("Abuse", tabId)` or `find("abuse", tabId)` — page renders |
| P.14b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.14c | **Data-binding: Abuse data** — `javascript_tool(tabId, "document.querySelectorAll('table tbody tr, [class*=Card]').length >= 0")` — abuse detection table/cards render (even if 0 items with empty state) |
| P.14d | `computer(action:'screenshot')` — capture visual state |

#### P.15 MFA Settings (4 tests)

Navigate to `$PROVIDER_URL/mfa`.

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.15a | `find("MFA", tabId)` or `find("Multi-factor", tabId)` — page renders |
| P.15b | `read_console_messages(onlyErrors:true)` — zero console errors |
| P.15c | **Data-binding: MFA status** — `javascript_tool(tabId, "document.body.innerText.match(/enabled\|disabled\|not configured\|setup/i)?.[0]")` — MFA status shows a recognized value |
| P.15d | `computer(action:'screenshot')` — capture visual state |

#### P.16 Provider Logo and Branding (6 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.16a | **Logo image rendered** — `javascript_tool(tabId, "document.querySelector('img[src*=primary-logo]')?.naturalWidth > 0")` — logo image loaded successfully (naturalWidth > 0 confirms it didn't 404) |
| P.16b | **Logo image source** — `javascript_tool(tabId, "document.querySelector('img[src*=primary-logo]')?.src")` — src contains "primary-logo-no-wordmark.svg" |
| P.16c | **Logo alt text** — `javascript_tool(tabId, "document.querySelector('img[src*=primary-logo]')?.alt")` — alt is empty string (decorative image — branding text is separate) |
| P.16d | **Branding text** — `find("Service Provider Console", tabId)` — header text reads "Service Provider Console" (not "Provider Console" or "Agent Red") |
| P.16e | **No duplicate branding** — `javascript_tool(tabId, "document.querySelectorAll('img[src*=logo]').length")` — exactly 1 logo image in header (no duplicates, no leftover alt text) |
| P.16f | **Logo dimensions** — `javascript_tool(tabId, "document.querySelector('img[src*=primary-logo]')?.offsetHeight")` — logo renders at expected height (~28px, not 0 or broken) |

#### P.17 Cross-page verification (10 tests)

| Test ID | Chrome MCP Verification |
|---------|------------------------|
| P.17a | Each P.1–P.15 page: `read_console_messages(onlyErrors:true)` after navigation — zero errors |
| P.17b | Each page transition: `computer(action:'screenshot')` — capture visual state for regression comparison |
| P.17c | **Data-binding spot check: Health Dashboard** — P.1 stat cards show numeric values (not "undefined", not empty, not "NaN") |
| P.17d | **Data-binding spot check: Tenant Directory** — P.2 tenant table has ≥ 1 row with non-empty tenant ID cell |
| P.17e | **Data-binding spot check: Alert Config** — P.7 alert rules list or configuration form renders with content |
| P.17f | **Data-binding spot check: Compliance** — P.9 compliance assessment results or checklist renders |
| P.17g | **Data-binding spot check: Secret Posture** — P.10 secret status indicators render with values |
| P.17h | **Data-binding spot check: SLA Trends** — P.13 chart or metrics render with percentage/ms values (not empty state) |
| P.17i | **Data-binding spot check: MFA Settings** — P.15 MFA configuration form or status indicator renders |
| P.17j | Navigate to invalid route (e.g., `/nonexistent`) → catch-all page renders gracefully |

**Per-test pattern:**
1. Navigate to `$PROVIDER_URL{route}`
2. `computer(action:'wait', duration:2)`
3. `read_console_messages(onlyErrors:true)` — zero errors expected
4. `find(query)` — verify primary content element exists
5. **Data-binding verification** — `javascript_tool` to verify API response fields populate visible elements with expected value types (numbers, dates, emails, recognized enum strings) — not "undefined", not empty, not "NaN"
6. `computer(action:'screenshot')` — capture visual state
7. Record PASS/FAIL

---

## Known Exclusions

| Exclusion | Reason |
|-----------|--------|
| Shopify embedded admin | Requires App Bridge auth context — cannot inject via Chrome MCP outside Shopify |
| MFA TOTP flow | Requires time-based OTP generation — auth injection bypasses MFA by design |
| Avatar upload tests (7.16–7.20) | Deferred per D22 — requires Azure Blob Storage + client-side cropping |
| Storefront widget mount (0A.8) | Requires access to live Shopify storefront (blanco-9939.myshopify.com) |
| Consent prompt (9.13) | Widget consent UI not yet built — deferred to widget phases 3-5 |
| Contact Us email delivery (H.3k) | Cannot verify email actually arrives at support@remakerdigital.com — ACS delivery is tested by unit tests. UI tests verify modal form, validation, and submit behavior only. |
| Provider Console data-binding: exact values | Data-binding tests verify values are populated and have expected *types* (numeric, email, date, enum). Exact numeric values depend on live data and may vary between runs. |

---

## Postconditions

- [ ] **Standalone Admin:** 838 tests executed (802 prior + 36 KA tests), results recorded with test ID / PASS / FAIL / SKIP
- [ ] **SPA Provider Console:** 115 tests executed (P.0–P.17), all PASS or documented FAIL
- [ ] **Total:** 953 tests (838 standalone + 115 provider)
- [ ] **Zero unexpected console errors** across all pages
- [ ] **Screenshots captured** for each page group (minimum 27 screenshots — 11 standalone page groups + 16 provider pages)
- [ ] **Auth injection verified** for both Standalone and Provider Console
- [ ] **Data-binding verification:** Every Provider Console page with data tables/stat cards verified for populated values (not "undefined", not empty, not "NaN")
- [ ] **Logo/branding verification:** Both Standalone and Provider Console headers verified for correct logo rendering, image source, dimensions, and branding text
- [ ] **Contact Us feature:** Modal opens, topic dropdown has 5 options, form fields render, cancel/send buttons present

---

## Known Failure Modes

| Failure | Classification | Resolution |
|---------|---------------|------------|
| Auth injection returns undefined | Procedure defect (wrong sessionStorage key) | Verify key names: `agentred_api_key` (standalone), `agentred_provider_key` (provider) |
| Page renders blank after auth injection | Environment transient (API key expired/rotated) | Re-run `seed_tenant.py`, update `.env.local`, re-inject |
| find() returns no elements for expected content | Procedure defect (query text changed) or Environment transient (slow render) | Increase wait time to 5s. If still failing, check component text in source. |
| Console error: "MantineProvider was not found" | Procedure defect (MantineProvider not hoisted) | See MantineProvider fix — provider must wrap `<App />` at mount point |
| Provider Console pages show "Loading..." indefinitely | Environment transient (API timeout) | Superadmin endpoints depend on Cosmos DB queries; may be slow on cold start. Wait 10s. |
| SPA pages fail P.1–P.15 with 401 | Environment transient (API key lacks SUPERADMIN role) | Verify the API key used has SUPERADMIN role. Re-seed if necessary. |
| Data-binding: table cells empty but page loads | Code defect (snake_case/camelCase mismatch) | Backend uses `CamelCaseModel` (pydantic `alias_generator=to_camel`) — all API response fields are camelCase. Frontend TypeScript interfaces MUST use camelCase. Check interface field names match API response. |
| Data-binding: stat cards show "undefined" or "NaN" | Code defect (wrong field name or missing null coalescing) | Verify the stat card reads the correct camelCase field. Add `?? 0` or `?? '--'` fallback. |
| Data-binding: select/filter dropdowns have 0 options | Code defect (options derived from empty array due to field mismatch) | Verify the dropdown `data` prop reads from correct camelCase response field. Add `?? []` fallback. |
| Logo image shows broken icon (0x0 pixels) | Procedure defect (wrong asset path) | Verify `primary-logo-no-wordmark.svg` exists in admin dist's public folder. Check image `naturalWidth > 0`. |
| Contact Us modal doesn't open | Code defect (missing onClick handler or icon component) | Verify `[aria-label="Contact us"]` ActionIcon renders and `contactHandlers.open` is wired. |
| Contact Us topic dropdown empty | Code defect (Select data prop missing) | Verify the `Select` component's `data` array has 5 topic options in StandaloneLayout.tsx. |

---

## Results Recording Format

Results should be recorded in markdown table format:

```
| Test ID | Result | Console Errors | Notes |
|---------|--------|----------------|-------|
| H.1a    | PASS   | 0              | naturalWidth=60 |
| H.3b    | PASS   | 0              | 5 topic options |
| 0.1     | PASS   | 0              |       |
| 0.2     | PASS   | 0              |       |
| 0A.8    | SKIP   | —              | Requires Shopify storefront |
| P.1c    | PASS   | 0              | Status: "healthy" |
| P.2d    | PASS   | 0              | Tenant ID: remaker-digital-001 |
| P.2h    | PASS   | 0              | Status dropdown: 3 options |
| P.16a   | PASS   | 0              | Logo naturalWidth=60 |
```

**Data-binding test result notes:** For data-binding tests (marked with `**Data-binding:**` prefix), record the actual value observed in the Notes column. This creates an audit trail for regression — if a value changes from "2" to "undefined" between runs, the defect is immediately visible.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
