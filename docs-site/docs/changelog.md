---
sidebar_position: 100
title: Changelog
---

# Changelog

All notable changes to Agent Red Customer Experience are documented here.

---

## v1.98.91 — Phone Identity, Canonical Identity & Production Hardening (Staging, 2026-04-09)

### Phone identity channel (SPEC-1879)

Full SMS OTP verification flow for customer identity.

- **Phone OTP endpoints** — send-sms / verify-sms with E.164 validation, SHA-256 hashed tokens
- **Conversation-scoped verification** — phone_verified separate from customer_verified
- **Widget integration** — PhoneOtpVerification component, pre-chat phone field, 8 locale files
- **Admin inbox** — phone display in identity panel, escalation gate for unverified phones
- **Tier gate** — professional+ tier required for phone identity features
- **Azure Communication Services** — toll-free SMS via ACS (verification submitted)

### Canonical identity (ADR-004)

Internal stable customer identity replacing contact-means-as-key.

- **Canonical ID** — `cid_<uuid>` as primary key, contact means as mutable attributes
- **Contact attributes** — array-based contact_attributes replacing flat email fields
- **Session find-or-create** — automatic identity resolution on conversation start
- **Admin APIs** — identity lookup, merge, and contact attribute management
- **Migration script** — production-safe migration with rollback capability

### Production hardening

- **Envelope encryption** — P0 incident closed; DEK recovery, field restoration, safety gates
- **Deploy procedure** — 5 work packages: approval gate, rollback, unified config, structured logging, canonical paths
- **Tenant provisioning** — display_name (auto-generated), hard contact gate on provision_tenant()
- **CI stability** — lint zero errors (E/F) in `src/`, 9/11 test shards green, ~50 test fixes

### Code quality improvements

- **Lint remediation** — 1,446 ruff errors resolved to zero (E/F rules) in `src/`; non-`src/` directories (tests, admin, scripts) retain pre-existing violations
- **Import cycle detection** — automated detector, 0 real cycles across 281 modules
- **GitHub hygiene** — README refresh, wiki sync, branch protection, issue templates
- **Evaluation reports** — Agent Red and OrbaTech technical assessment documents

---

## v1.98.16 — Self-Service Deployment Pipeline & Dashboard Overhaul (Production, 2026-03-23)

### Self-service deployment pipeline (SPEC-1825)

Build, deploy, and verify directly from internal operations tooling without CLI access.

- **Trigger Pipeline** — one-click build, deploy, and verify for any version tag
- **Pipeline actions** — full pipeline, build-only, or deploy-only
- **GitHub Actions integration** — builds trigger `workflow_dispatch` events, with real-time status polling
- **Deployment history** — every pipeline run recorded with status, duration, and outcome
- **Environment isolation** — each environment can only deploy to itself (auto-detected from FQDN, SPEC-0058)

### Dashboard health overhaul (SPEC-1851)

Simplified the Platform Dashboard to show only operational infrastructure:

- **4 health cards** — Cosmos DB, Redis, Key Vault, API Version
- Removed decommissioned NATS card (was always showing "Disconnected")
- Removed non-functional Circuit Breakers card (was always showing "Unknown")
- Key Vault probe now reflects actual status instead of always "Degraded"
- Help tooltip with infrastructure explanations

### Environment isolation enforcement (SPEC-0058)

Complete separation of staging and production:

- Server auto-detects its environment from `CONTAINER_APP_FQDN`
- Environment selector removed from deployment and test execution UIs
- No hardcoded FQDNs or API keys in source code
- Credential scan guardrail prevents accidental secret commits

### Additional fixes

- Tenant identity in navbar never shows blank (SPEC-1848)
- Knowledge base sortable columns and hide-archived toggle (SPEC-1850)
- Test execution detail popup with blob URL viewer (SPEC-1845)

---

## v1.98.0 — Quality Guardrails & Automated Testing Infrastructure (Production, 2026-03-21)

### Quality guardrails

4 pre-commit hooks that run automatically on every code change:

- **Test deletion guard** — prevents accidental test removal
- **Assertion ratchet** — ensures test count never decreases
- **Architectural guards** — enforces module boundaries and import rules
- **Credential scan** — blocks secrets from entering the repository

### Fuzzing suite (SPEC-1839)

Schema-driven fuzz testing using Schemathesis against the live OpenAPI spec:

- Generates random valid/invalid payloads for all API endpoints
- Response model annotations added to 13 endpoints for proper schema validation
- Conditional test skips classified correctly (legitimate vs evasive)

### Test host infrastructure

Cloud-native test container running 9,200+ tests across 12 suites:

- Parallel test execution with `pytest-xdist`
- HMAC-based internal authentication for cross-replica verification
- Dedicated Dockerfile with Node.js, Playwright, and all test dependencies
- GitHub Actions CI/CD for automatic test host builds

---

## v1.96.0 — Test Execution Console & Cloud-Native Verification (Production, 2026-03-19)

### Test execution tooling (SPEC-1826)

Full test management from internal operations tooling:

- Trigger test runs with suite selection (smoke, regression, e2e, full)
- Auto-polling detail modal with live progress bar
- Performance chart showing pass rates over time
- Checkbox suite selector for custom test combinations
- Copy-for-Claude button exports failure JSON for debugging
- Drill-down into individual test results

### Verification runner improvements

- Shared HTTP client — single TLS handshake per run
- TOCTOU-safe concurrent run guard (sentinel-based)
- Progressive Cosmos updates for real-time status polling
- Proper duration tracking on error and cancel paths
- Stale run timeout increased for reliability

---

## v1.93.5 — Cloud-Native Verification Runner & Code Review Hardening (Staging, 2026-03-18)

### Cloud-native verification runner (SPEC-1845/1846)

Tooling-triggered end-to-end health checks that run entirely within the Azure environment:

- **4 verification suites:** Smoke (8 health probes, ~5s), Regression (25 checks, ~3min), E2E (31 checks, ~8min), Full (36 checks, ~12min)
- **Progressive Cosmos updates** — real-time progress polling with pass/fail counts
- **Shared HTTP client** — single TLS handshake per run instead of per-check
- **GOV-10 compliance** — all health checks use live HTTP interfaces, not internal imports
- **TOCTOU-safe concurrent run guard** — sentinel-based protection prevents duplicate runs
- **Fail-closed FQDN resolution** — cross-environment runs require explicit env var config

### Test execution tooling (SPEC-1826)

- Trigger test runs from internal operations tooling with environment and suite selection
- Auto-polling detail modal with live-updating progress bar
- Copy-for-Claude button exports failure JSON to clipboard
- Unmount-safe polling with `useRef` guard

### Code review fixes (12 items)

- Sync Redis `.ping()` wrapped with `asyncio.to_thread()` to prevent event loop blocking
- Environment allowlist validation on `list_test_runs` filter
- Key Vault probe honestly labeled as config-only check
- `started_at` timestamp captured once (no drift across progressive updates)
- Stale `detailRun` modal fixed — derived from `runs` array via ID
- Null date guard prevents "Invalid Date" rendering

---

## v1.91.0 — Operational Control Plane (Production, 2026-03-17)

### Operational Control Plane

Complete data-driven runtime configuration system replacing all hardcoded tier constants:

- **EntitlementService** — 3-tier cache (LRU 5s, Redis 60s, Cosmos DB) with frozen fallback values
- **39 Control Plane API endpoints** — entitlement CRUD, feature flags, blocklists, rate limits, alerts, diagnostics, maintenance mode
- **Internal operations workflows expanded** — control-plane coverage increased across runtime management flows
- **Configuration audit trail** — old/new key snapshots, diff summaries, and change reasons on every config change
- **Build & deploy orchestrators** — deterministic scripts replacing conversation workflows

### Infrastructure

- Deployed to production (ACR ca65, revision --0000115) and staging
- 12/12 Control Plane endpoints verified on production
- 200+ tests across all Control Plane features

---

## v1.89.0 — Transport Hierarchy & Sign-In Codes (Staging, 2026-03-16)

### AGNTCY transport hierarchy

Completed the 4-tier transport hierarchy for agent communication:

- **Tier 1 — SLIM** (primary): SLIM routing service with HTTP/2 ingress and shared secret auth
- **Tier 2 — NATS JetStream** (fallback): WebSocket mode to work within Azure Container Apps Envoy proxy
- **Tier 3 — HTTP Containers**: Direct internal HTTP dispatch
- **Tier 4 — In-process**: Python method call for development

### AGNTCY Directory integration

- Dynamic agent discovery with static fallback
- Agent containers register with Directory on startup
- `AgentTopic` enum deprecated in favor of directory-resolved topics

### Sign-in code authentication

- 6-digit sign-in code alternative to magic link click
- `POST /verify-code` endpoint with code delivered via email
- Frontend code entry modal with error handling

---

## v1.88.1 — Spec Verification Hotfix (Production, 2026-03-16)

- Verified all 2,009 specifications against source code
- Fixed SPEC-0429: login now magic-link-primary when `?tenant=` parameter present
- Created 7 missing specifications (SPEC-1806 through SPEC-1812)
- 24 new assertions added

---

## v1.88.0 — Bug Fixes & Email Refactor (Production, 2026-03-15)

### Bug fixes

- Button color corrected (#D32F2F to #e03131)
- Auto-save stale closure fix in draft editor
- Starter tier `custom_instructions` gate removed
- Avatar upload 413 error fix

### Email improvements

- Unsubscribe footer added to all branded emails via `format_branded_email()` refactor (12 modules)
- AI-generated widget greeting (template-based)
- Info pane width increased (280px to 320px)

---

## v1.87.0 — Data-Driven Rate Limiting & Agent Containerization (Production, 2026-03-15)

### Data-driven rate limiting

Rate limits are now derived from empirical load testing rather than arbitrary values. A ramp-to-overload test (10→150 concurrent users) established the safe throughput ceiling at **1,380 requests per minute per replica**.

- **300 RPM per tenant** — derived from production capacity (2,760 RPM at min=2 replicas ÷ 9 safety margin for concurrent max-rate tenants). Down from the previous 500 RPM.
- **10 RPM minimum floor** — prevents any configuration path (per-tenant override, tier default, or misconfiguration) from setting a tenant to 0 RPM. Admin authentication always works.
- **Uniform across all tiers** — rate limits are a platform safety mechanism, not a monetization lever. Starter, Professional, and Enterprise all share the same 300 RPM limit.
- **Per-tenant override** — individual tenants can be assigned custom RPM values, subject to the 10 RPM floor.

### Agent containerization (staging)

All six AI agents plus the Co-Pilot now run as independent Azure Container Apps with HTTP dispatch:

- **7 agent containers:** Intent Classifier, Knowledge Retrieval, Response Generator, Escalation Handler, Analytics Collector, Critic Supervisor, and Co-Pilot — each independently scalable.
- **3-tier dispatch architecture:** NATS transport (Tier 1) → HTTP containers (Tier 2) → in-process fallback (Tier 3). Production currently uses Tier 3; staging uses Tier 2.
- **AGNTCY SDK integration:** Protocol negotiation working with A2A, MCP, and FastMCP protocols. NATS transport initialized but blocked by Azure Container Apps TCP routing limitation.

### Other changes

- **Tenant operations:** Per-tenant rate limit RPM values are now visible and editable in internal operations tooling.
- **Test consolidation:** Rate limit tests consolidated from 4 scattered files into a unified suite (41 tests).
- **RATE_LIMIT_DISABLED env var:** New environment variable to skip rate limit middleware registration entirely, for test environments.

---

## v1.83.0 — 680-Tenant Infrastructure Scaling (Production, 2026-03-13)

### Distributed rate limiting with Redis

Agent Red now uses **Azure Cache for Redis** for distributed rate limiting across multiple application replicas. Rate limit windows are shared across all workers and replicas, ensuring consistent enforcement at scale.

- **Sharded rate limiting:** 16 independent rate limit shards eliminate global lock contention. Each tenant is deterministically assigned to a shard for O(1) lookup.
- **Redis bridge:** Rate limit middleware automatically detects and delegates to the Redis backend, with graceful fallback to local shards if Redis is unavailable.

### Cross-replica cache invalidation

When tenant configuration changes on one replica, all other replicas are notified via **Redis pub/sub** and invalidate their local caches immediately. This eliminates the previous 5-minute TTL delay for configuration changes to propagate.

### Per-tier entitlement caps

Each subscription tier now enforces limits on:

- Knowledge base articles
- Website sources
- Escalation categories
- Team members
- Conversation history retention (days)

Attempts to exceed tier limits return a clear `403 Forbidden` with the specific cap and current count. Enterprise tier has the highest limits, Starter the lowest.

### Scaling infrastructure

- **4 uvicorn workers per replica** (up from 1) — at minimum 2 replicas, production runs 8 concurrent workers.
- **Global SSE connection limit** (5,000) prevents connection exhaustion under load.
- **LRU-bounded data structures** — pre-auth IP tracker (10,000 max) and TOCTOU locks (1,000 max) prevent unbounded memory growth.
- **Tenant metadata cache** with 300-second TTL reduces Cosmos DB reads by ~80% for repeated requests.

### Health metrics endpoint

New `GET /health/metrics` endpoint (platform admin only) reports real-time operational metrics: active SSE connections, cache sizes, rate limiter state, uptime, and event loop latency.

### Redis connectivity

- **Azure Cache for Redis Standard C1** connected on both staging and production.
- Channel: `agentred:cache:invalidate` for cross-replica coordination.

---

## v1.82.1 — Rate Limiter Fix, Superadmin API Refactor, Config Authority (Production, 2026-03-12)

### Configuration authority over knowledge base

When configuration fields (brand name, persona, language, custom instructions) are set, they are now declared **authoritative over knowledge base articles**. If a KB article contradicts a config field, the config value takes precedence in the AI's responses.

- **Conflict scanner integration:** The Knowledge Base and Configuration admin pages now show warning banners when KB articles conflict with authoritative config fields.

### Email template improvements

- **Welcome email:** Removed API key blocks from the welcome email template. The email now directs new tenants to the admin dashboard to view and manage their keys securely.
- **Login notification and recovery emails:** Added clickable admin dashboard URL buttons and security warning links.

### Rate limiter consolidation

- **Shared backend:** Account recovery and admin forgot-password rate limiters now use the shared `RateLimitBackend` instead of per-module dictionaries.
- **Middleware ordering fix:** `TrustedProxyMiddleware` now runs before `PreAuthRateLimitMiddleware`, ensuring rate limiting uses the real client IP (not Azure's internal proxy IP).
- **Platform admin exemption:** Privileged operational keys are exempt from both rate limiters.
- **IP exemption:** `PRE_AUTH_RATE_LIMIT_EXEMPT_IPS` allows specific IPs to bypass pre-auth rate limiting.

### Superadmin API refactoring

The administrative API monolith (5,085 lines) has been split into five domain submodules for maintainability: tenants, dashboard, operations, copilot, and platform. The public API is unchanged.

### Infrastructure

- **Pre-auth rate limit IP exemption** (`PRE_AUTH_RATE_LIMIT_EXEMPT_IPS` env var) for CI/CD pipelines and monitoring.

---

## v1.82.0 — Mock Dev Environment and Admin UI Polish (Staging, 2026-03-11)

### Mock development environment

- **Zero-backend UI development:** New `npm run dev:mock` mode enables frontend development without a running backend. Uses in-memory fixture data, client-side router interceptor, and mock API handlers for all admin endpoints.
- **527 mock E2E tests:** Comprehensive test suite verifying all 12 admin pages work correctly in mock mode (522 pass, 5 skip).

### Admin UI improvements

- **Auto-save on focus out:** Configuration, Widget, Memory & Privacy, and Knowledge Base pages now auto-save draft inputs when focus leaves a field (500ms debounce). Replaces explicit "Save draft" buttons.
- **Agent identity section:** Grouped "Brand & Persona" and "Custom Instructions" into a single "Agent identity" section on the Configuration page.
- **Policy overrides:** Moved Policies from Configuration to Knowledge Base page as "Policy overrides" with priority documentation.
- **Integrations mock data:** Full mock fixtures for 5 integration types with 8 endpoint handlers.

---

## v1.81.0 — Auth Hardening, Rate Limit Backend, and CI/CD (Production, 2026-03-10)

### Authentication hardening

- **Inactivity auto-logout:** Admin sessions now expire after 30 minutes of inactivity with automatic logout.
- **Cross-tab token protection:** Session tokens are bound to a single browser tab to prevent token theft across tabs.
- **Clickjacking protection:** `X-Frame-Options: DENY` and `Content-Security-Policy: frame-ancestors 'none'` headers added to auth middleware.

### Rate limit backend

- **Shared rate limit infrastructure:** Extracted `RateLimitBackend` protocol with `InMemoryRateLimitBackend` implementation. Both middleware and security hardening modules now share a single backend instance.

### CI/CD pipeline

- **GitHub Actions workflow:** New CI pipeline with parallel lint (ruff), typecheck (pyright), test (pytest), and security scan (bandit + safety) stages.
- **Makefile targets:** 8 `make` targets for common development tasks.

### Superadmin API split

- **Package restructuring:** Split `superadmin_api.py` (2,100+ lines) into 5 domain submodules (`_tenants.py`, `_dashboard.py`, `_operations.py`, `_copilot.py`, `_platform.py`) for better maintainability.

---

## v1.80.5 — Widget Config UX, Launcher Preview, and KB Freshness (Production, 2026-03-10)

### Widget configuration improvements

- **Dedicated launcher color:** A new `widget_launcher_color` field controls the launcher button color independently from the widget's primary color. Previously, the launcher always matched the primary color.
- **Real-time launcher preview:** Changes to launcher color, icon, position, and size now update the live preview instantly without requiring a page reload.
- **Two-column launcher layout:** The Widget configuration page now uses a two-column layout for launcher settings (color on the left, icon and size on the right).

### Knowledge base freshness

- **No-cache headers:** Knowledge base API endpoints no longer return `max-age=86400` cache headers. Admin users now see recently added or modified articles immediately.

### Onboarding wizard

- **Duplicate article detection:** The setup wizard now checks for existing KB articles and shows a warning banner ("Existing articles detected") to prevent accidental duplicate imports.

### Pydantic validation fix

- Fixed `widget_page_rules` and `widget_pre_chat_fields` rejecting `None` values during configuration save.

---

## v1.80.0 — Privileged Authentication Isolation, Key Recovery, and Login Notifications (Production, 2026-03-09)

### Platform admin isolation

- **Dedicated auth path:** Privileged operational keys now use a dedicated auth path and separate identity store, isolating operational access from tenant access.
- **Key regeneration:** Platform admins can regenerate their privileged key.

### Emergency key recovery

- **Backup code recovery:** If a platform admin loses their key, they can recover access using backup codes delivered during initial provisioning. Rate limited to 3 attempts per 15 minutes per IP with enumeration prevention.

### Login notifications

- **Email on privileged auth:** Platform admins receive a notification email whenever their key is used to authenticate, including timestamp and source IP.

### Tenant account recovery

- **Recovery email address:** Tenants can configure a recovery email for emergency account access. Verification uses single-use tokens with session JWTs.

---

## v1.79.2 — Rate Limit Exemption and Hotfix (Production, 2026-03-08)

### Platform admin rate limit exemption

- Platform admin keys are now exempt from both the identity-based rate limiter (middleware) and the path-based rate limiter (security hardening). This prevents CI/CD pipelines and monitoring from being throttled.

### Hotfix

- Fixed `replace_item()` in Cosmos SDK leaking `partition_key` through `**kwargs` to aiohttp — changed to `upsert_item()`.

---

## v1.77.0 — Human-Readable Tenant IDs and Test Mode Removal (Production, 2026-03-08)

### Human-readable tenant IDs

- New tenants are provisioned with human-readable IDs derived from the account holder's email domain (e.g., `acme-outdoor` instead of a UUID). Existing tenants retain their current IDs.

### Test mode removal

- Removed the `test_mode_enabled` field from the configuration schema and all admin web interfaces. Test mode was a development feature that is no longer needed.

---

## v1.76.0 — CORS Fix, Widget Resilience, and UX Improvements (Production, 2026-03-07)

:::note
Originally deployed to staging for validation. Promoted to production on 2026-03-08.
:::

### Widget resilience

The chat widget now automatically retries transient HTTP errors to improve reliability on high-traffic storefronts.

- **Exponential backoff:** Failed requests to the API (429 Too Many Requests, 502, 503, 504) are retried automatically with increasing delays. Configuration fetches retry up to 3 times with a 1.5-second base delay; conversation start retries up to 2 times.
- **Retry-After header support:** When the server sends a `Retry-After` header, the widget respects the requested delay (capped at 30 seconds) before retrying.

### CORS middleware fix

A critical fix ensures that CORS headers are present on all HTTP responses, including rate-limited (429) responses.

- **Root cause:** The CORS middleware was positioned as the innermost middleware layer, meaning rate limit rejections were sent to the browser before CORS headers could be added. Modern browsers block responses missing CORS headers, causing silent failures.
- **Fix:** CORS middleware is now the outermost middleware layer, ensuring every response includes the correct cross-origin headers regardless of which middleware generated the response.

### Issue report improvements

- **Done button:** After submitting an issue report, the confirmation screen now shows a "Done" button instead of "Cancel." The previous label incorrectly suggested the submission could be undone. This change applies across all 8 supported languages (English, German, French, Spanish, Japanese, Korean, Chinese, Portuguese).

### Shopify CDN deployment

- **Permanent widget URLs:** Widget bundles are now deployed using `shopify app deploy` which creates permanent, versioned CDN paths. Previously, development-mode paths could expire, causing the widget script to return 404 on the storefront.

### Infrastructure

- **Async safety:** Background tasks are now properly tracked to prevent fire-and-forget coroutines from being garbage collected.
- **Redis rate limiting:** A new Redis-backed rate limiting backend using sorted sets is available for production scaling. Automatically configures from `REDIS_URL` environment variable with in-memory fallback.
- **Cloudflare proxy support:** A new trusted proxy middleware correctly extracts visitor IP addresses from Cloudflare headers (`CF-Connecting-IP`, `X-Forwarded-For`) for accurate rate limiting behind CDN proxies.
- **GitHub Actions CI:** Automated linting and unit test execution on every push.

---

## v1.62.0 — Co-Pilot Agent, PII Tokenization, and AGNTCY Platform (2026-03-01)

### Admin Co-Pilot Agent

A new AI-powered assistant is available directly inside the admin console, helping merchant administrators manage their Agent Red configuration.

- **Admin assistance intent:** A new `admin_assistance` intent category enables the Co-Pilot to answer questions about Agent Red features, configuration, and best practices using a dedicated admin documentation knowledge base.
- **Widget admin mode:** The chat widget can operate in admin mode (using the `data-admin-key` attribute), providing administrators with a Co-Pilot conversation interface embedded directly in the admin console. Admin mode conversations are non-billable and bypass the Critic Supervisor for faster responses.
- **Three-tier dispatch:** The Co-Pilot Agent uses the same AGNTCY transport infrastructure as the customer-facing pipeline, with in-process fallback for zero-downtime operation.

### PII tokenization

A new reversible PII tokenization layer protects customer data during AI processing.

- **Tokenize before AI:** Customer PII (emails, phone numbers, order numbers) is replaced with reversible UUID tokens before being sent to external AI models. The AI never sees raw PII.
- **Detokenize after validation:** After the Critic Supervisor validates the response, original values are restored before delivering to the customer.
- **GDPR lifecycle integration:** PII token mappings are included in data export and deletion workflows. Token mappings have a 7-day TTL and are automatically cleaned up.

### AGNTCY SDK integration

Agent Red now uses the AGNTCY SDK as its mandatory foundation for all agent-to-agent communication.

- **Containerized agent deployment:** All seven specialized AI agents (Intent Classifier, Knowledge Retriever, Response Generator, Critic Supervisor, Escalation Handler, Analytics Collector, and Co-Pilot) can run as independent containers with A2A transport.
- **Transport-first routing:** Agent dispatch uses a three-tier approach — AGNTCY transport (preferred), HTTP fallback, in-process fallback — ensuring zero downtime during infrastructure transitions.
- **Streaming over transport:** Response generation supports SSE streaming through the A2A transport layer for real-time customer-facing responses.

### Observability and cost attribution

- **Per-agent OpenTelemetry spans:** Every agent invocation is wrapped in a traced span with parent-child relationships forming a complete execution tree.
- **Token usage capture:** Prompt and completion token counts from Azure OpenAI responses are recorded on each span.
- **Cost attribution model:** Estimated costs per agent call are calculated using current model pricing (GPT-4o, GPT-4o-mini, embedding) and recorded as span attributes.

### Dedicated model training (Layer 4)

- **Memory & Privacy admin UI:** The new Dedicated Model Training section is now visible in the admin console for Enterprise tier merchants. Per-customer AI fine-tuning on 1,000+ historical interactions is available as an Enterprise add-on ($299/month).

### Bug fixes

- **MemoryPrivacy page TypeScript fix:** Resolved a TypeScript strict mode error where config property access returned `unknown` type, preventing the Memory & Privacy admin page from compiling. The page now renders all six sections correctly.

---

## v1.61.0 — Targeting Rules, Engagement Triggers, and Documentation Audit (2026-02-28)

### Targeting rules and engagement triggers
- **Page-level targeting rules:** Configure which pages the widget appears on using URL include/exclude patterns with `+` and `-` prefix syntax. Managed from both standalone and embedded admin UIs.
- **Exit-intent trigger:** Detect when a customer's cursor moves toward the browser close button and proactively show the widget. Configurable sensitivity and one-trigger-per-session guard.
- **Scroll-depth trigger:** Show the widget when a customer scrolls past a configurable percentage of the page (default: 50%). Supports the full 4-layer field pipeline (fields.yaml, field_mapping, cosmos_schema, widget runtime).
- **SDK runtime config methods:** New `setConfigPartial()` and `setTargetingRules()` methods allow programmatic widget configuration updates from the hosting page.

### Documentation corrections
- **Architecture accuracy:** Removed false claims about gRPC/SLIM transport, Application Gateway WAF, KEDA auto-scaling, and per-agent container separation. Documentation now accurately reflects the unified API Gateway architecture with HTTP endpoints and NATS JetStream event bus.
- **Region correction:** Fixed "East US 2" references to "East US" across all documentation pages.
- **FQDN correction:** Updated example API endpoints from a placeholder FQDN to the correct production gateway address.
- **Performance claims:** Replaced unverified metrics (3,071 rps, 98% accuracy, 100% precision/recall) with honest design targets. Removed aspirational numbers that lacked code or test evidence.
- **NATS retention:** Corrected 7-day retention claim to actual 5-minute retention (`MESSAGE_MAX_AGE_SECONDS = 300`).
- **PII protection:** Clarified that PII protection consists of storage-layer scrubbing and the Azure security perimeter.
- **Customer Memory:** Corrected documentation to reflect that Layer 4 (Dedicated Model Training) was not yet implemented. Layer 4 was subsequently implemented in v1.62.0 as an Enterprise add-on.
- **Admin UI screenshots:** Added 6 production screenshots to documentation pages (dashboard, agent configuration, widget configuration, memory & privacy, team management, knowledge base).

---

## v1.59.0 — Unified Auth, 2FA, and RBAC (2026-02-26)

### Unified authentication and 2FA

A comprehensive security overhaul brings multi-factor authentication and role-based access control enforcement to the tenant admin console.

- **Team member identity in magic links:** Magic link authentication sessions now correctly identify the team member who clicked the link, preserving their role and permissions throughout the session. Multi-tenant disambiguation handles team members who belong to multiple tenants.
- **SMS-based two-factor authentication:** Team members can enable 2FA via SMS verification. After API key login, a second challenge step requires a one-time code sent to the team member's registered phone number.
- **MFA management API:** Six new endpoints for managing MFA enrollment — check status, enroll, confirm enrollment, disable, and grant or revoke opt-out for team members who cannot use SMS.
- **Brute-force mitigation:** Failed 2FA attempts are tracked with exponential backoff and lockout after repeated failures.

### RBAC enforcement

- **Middleware-level enforcement:** A new `enforce_rbac` middleware layer validates that the authenticated team member's role has permission to access the requested API path. Previously, role checks were only applied in the frontend.
- **17 admin-only path prefixes:** API paths under `/api/admin/` require admin or superadmin role. Escalation agents and viewers are restricted to their permitted endpoints.
- **Frontend route protection:** New `ProtectedRoute` component wraps admin pages, redirecting unauthorized roles to their permitted landing page.
- **2FA challenge component:** A `TwoFaChallenge` component presents the SMS verification step during login when the team member has MFA enabled.

### Admin UI improvements

- **Setup checklist:** A new guided checklist helps merchants track onboarding progress — configure brand, add knowledge, customize widget, and activate.
- **Named configuration delete:** Merchants can now delete saved configuration snapshots.
- **Configuration timestamps:** Saved configurations display their creation and last-modified timestamps.
- **Favicon and PWA manifest:** The standalone admin now has proper favicons and a Progressive Web App manifest for installability.
- **Test mode diff view:** A visual diff showing configuration differences between live and test mode.
- **3 new configuration fields:** `shadow_intensity`, `panel_width`, and `greeting_mode` added to the widget configuration.

### Knowledge Database infrastructure

- **Event-sourced session prompts:** The session handoff system now uses event sourcing for reliability.
- **7 database indexes:** Query performance improved with targeted indexes on frequently accessed columns.
- **WAL mode:** SQLite Write-Ahead Logging enabled for concurrent read/write safety.
- **JSON export:** New `db.export_json()` method for full logical backups.
- **Audit cadence:** Automatic integrity audits every 5th session with configurable intervals.

### Tests

- 113 new tests across 4 test files (RBAC enforcement, MFA auth, team MFA API, magic link auth improvements)
- 4,539+ total tests, 0 failures

---

## v1.57.20 — Staging environment and email polish (2026-02-24)

### Parallel staging environment

A complete parallel staging environment has been provisioned for validating the next release before applying it to the beta production environment. The staging environment includes its own Container App, isolated Cosmos DB database, and dedicated Key Vault. It scales to zero when idle, incurring no cost outside of active testing.

### Email template improvements

- **Helper text:** Recovery instructions added below the Admin API Key and Widget Key code blocks in the welcome email, guiding merchants on how to retrieve credentials if they lose the initial email.
- **Visual consistency:** All border-radius removed from email template elements for a cleaner, sharper appearance across all email clients.
- **Template structure:** Both welcome email and system alert templates updated.

---

## v1.57.19 — Email architecture overhaul (2026-02-24)

### SMTP-first email delivery

All nine email modules have been restructured to use Titan SMTP as the primary delivery provider, with Azure Communication Services as a fallback. This resolves rate limiting issues with Azure managed email domains and provides faster, more reliable email delivery (average 3 seconds to inbox).

### Email template redesign

- **Dark theme wrapper:** The shared email template now uses a dark (#141414) outer background with the Agent Red logo and footer rendered directly on the dark surface, creating a premium branded appearance.
- **Logo hosting:** Email logo served from agentredcx.com with cache-busting to ensure email clients always display the current version.
- **Security notice:** Updated wording per owner feedback on credential recovery instructions.

### Widget and inbox fixes

- **Pre-chat form:** Defaults to OFF for new and existing tenants. Merchants can enable it from the Widget page when explicit customer identification is desired before chat.
- **Inbox message display:** Fixed a role mapping issue where AI-generated responses were rendered on the customer side of the conversation view. The TypeScript message role type now correctly maps the backend `ai` role to the agent display column.
- **Shopify extension v18:** Updated widget bundle deployed to Shopify CDN with latest widget changes.

### Infrastructure

- **ACS rate-limit protection:** Azure Communication Services SDK configured with aggressive retry limits (2 retries, 5-second max backoff) to prevent indefinite blocking when the email quota is exceeded.

---

## v1.57.12 — Widget key rotation fix (2026-02-24)

### Critical fixes

- **Widget key rotation:** Fixed a document ID format issue where the rotation endpoint used an incorrect ID pattern to locate the preferences document. The endpoint now correctly discovers the document ID before patching, ensuring rotated keys are immediately reflected in the admin UI.
- **Cache invalidation:** Direct Cosmos DB patches now trigger config cache invalidation, preventing stale data from being served for up to 60 seconds after key rotation.
- **Resend welcome email:** Fixed false-success toast notifications — the frontend now checks both HTTP status and delivery confirmation flag before showing success.

### Email improvements

- **Thread pool offload:** All email send operations moved to background thread pool execution across eight modules, preventing I/O blocking on the main event loop.

---

## v1.57.7 — Widget key display and welcome email branding (2026-02-24)

### Widget key display and rotation

A new **Installation** section has been added to the Widget page, giving merchants direct access to their widget key and embed code.

- **Widget key visibility:** The widget key is displayed in a read-only monospace field with a one-click copy button.
- **Embed code snippet:** A ready-to-use HTML script tag is shown with the merchant's actual widget key and API URL pre-filled, along with a copy button and placement instructions.
- **Key rotation:** A "Rotate key" button opens a confirmation dialog explaining that rotation immediately invalidates the current key. After rotation, the new key is displayed instantly.
- **Empty state:** Before configuration activation, the section shows a clear message directing merchants to complete and activate their configuration.

### Avatar upload fix

The avatar upload size limit has been increased from 500 characters (intended for external URLs) to 400,000 characters, correctly supporting base64-encoded data URIs for images up to 256KB. Validation errors are now surfaced with descriptive messages instead of a generic failure.

### Welcome email branding

- **Resend endpoint:** A new superadmin API endpoint allows re-sending the welcome email with current credentials for any tenant.
- **Customer profile display:** The Inbox sidebar now shows the customer's verified email address and verification status from the identity preprocessor pipeline.

---

## v1.57.4 — Beta verification and quality hardening (2026-02-23)

### Beta readiness (v1.57.0)

Four features required for beta customer onboarding have been completed:

- **Conversation vectorization scanner:** A background task scans ended conversations every 5 minutes and vectorizes them for persistent memory retrieval. Each cycle processes up to 20 conversations per tenant. Vectorized conversations are marked with a timestamp to prevent re-processing.
- **Widget consent collection:** A consent banner appears in the chat widget when the tenant has enabled consent collection. Customer consent status (granted, denied, withdrawn) is stored on their profile and controls whether conversation memory is retained.
- **Cost analytics:** A new superadmin endpoint provides estimated per-tenant cost breakdowns including Azure OpenAI token costs, Cosmos DB request unit consumption, and container compute amortization.
- **Abuse detection:** Rate anomaly and error rate heuristics calculate a risk score (0-100) for each tenant, with automated flagging for investigation.

### Assessment fixes (v1.57.1)

An independent assessment review identified four items, all resolved:

- **Fine-tuning pipeline hardened:** Placeholder return values in the fine-tuning pipeline have been replaced with `NotImplementedError` exceptions. The existing triple-gate (feature flag, tier check, safety validation) already prevents user access, but the explicit errors provide defense-in-depth.
- **Storefront ingestion annotation:** A misleading "stub" comment has been corrected to accurately describe the module's production functionality.

### Critical path verification (v1.57.4)

The full 21-test critical path (CP.1–CP.21) has been verified against production, covering tenant provisioning, setup wizard, activation, all admin pages, live chat pipeline, dashboard, inbox, and configuration persistence. All 21 tests pass.

### Tests

- 4,522 unit tests (0 failures), 56 regression tests (all tiers), 21/21 critical path, load test pass (50 users, 0% failures)

---

## v1.56.0 — Identity pipeline and tenant provisioning (2026-02-22)

### Identity preprocessor pipeline

A new centralized identity preprocessing stage has been added to the chat pipeline. Before the AI orchestrator processes a message, the identity preprocessor extracts verified customer identity from all available sources — OTP tokens, Shopify HMAC, pre-chat form data, and session context — and injects it into the conversation. This ensures every AI response has access to the customer's verified identity regardless of how they authenticated.

- **Centralized extraction:** Identity resolution is now a single pipeline stage instead of being scattered across multiple components. The preprocessor runs before the orchestrator and populates customer identity fields (name, email, verification status) on the session and conversation records.
- **Session identity persistence:** Verified customer identity is stored on the chat session, so subsequent messages in the same conversation automatically carry the customer's identity without re-verification.
- **System prompt identity injection:** A new Layer 6 in the system prompt builder injects the customer's verified identity directly into the AI's context. The AI knows the customer's name, email, and verification level, enabling personalized responses from the first message.
- **Widget identity forwarding:** The widget now forwards pre-chat form data (name, email) and OTP verification tokens to the backend on every message, not just the first one. This ensures identity is available even if the session is resumed.

### Developer experience

- **Thermal-safe test harness:** A new `scripts/run-tests-thermal-safe.ps1` script distributes the test suite across 5 batches with configurable xdist parallelism and cooling pauses between batches. This prevents sustained CPU heat buildup that caused system instability during extended test runs.

### Tests

- 57 new tests across 5 test files — identity preprocessor (14), pipeline wiring (5), system prompt identity (12), tenant provisioning (12), superadmin creation (8), plus 6 test drift fixes for new schema values

---

## v1.55.1 — Hotfix (2026-02-22)

### Bug fix

- **Configuration endpoint fix:** Fixed a server error (500) on `/api/config` caused by the `step_order` field in the configuration field registry rejecting fractional values. The `customer_email_verification` field (added in v1.55.0 for OTP verification) uses `step_order: 16.5` to position it between existing fields. The field type has been changed from integer to float to support fractional ordering.

---

## v1.55.0 — Cycles 15-19 (2026-02-22)

### Onboarding polish (Cycle 19)
- **Automatic widget key generation (WI-E1):** Widget keys are now generated automatically when a tenant is provisioned — no manual setup required. Keys are created during Stripe checkout, Shopify billing confirmation, and trial provisioning. The rotation endpoint now correctly updates both the authentication hash and the admin-visible raw key.
- **Welcome email (WI-E2):** New merchants receive a branded welcome email upon account creation containing their API key and widget key credentials, security notices, and getting-started steps. Sent via Azure Communication Services with SMTP fallback.
- **Trial expiry warning emails (WI-E3):** Trial tenants receive automated warning emails at 7 days, 3 days, and 1 day before expiry. Each tier has distinct urgency styling (blue/info, amber/warning, red/critical). Deduplication prevents repeat sends. Background task runs every 12 hours.
- **Setup wizard re-trigger (WI-E4):** The onboarding wizard now re-appears on each new browser session for merchants who haven't completed activation, instead of being permanently dismissed after the first viewing.

### Provisioning persistence (Cycle 17)
- **Cosmos DB primary store (WI-C1):** All tenant provisioning data is now persisted in Cosmos DB. Three in-memory dictionaries that were lost on container restart have been removed. All seven core provisioning functions are now async with durable storage.
- **Superadmin auto-provisioning (WI-C2):** A superadmin team member and API key are automatically created when a merchant completes Stripe checkout. The API key is included in the welcome email.

### Background task hardening (Cycle 18)
- **Trial expiry scanner (WI-D1):** Proactively marks expired trial tenants as `trial_expired` in the database. Runs hourly as a background task. Defense-in-depth: the middleware already rejects expired trials at request time; the scanner ensures status accuracy for dashboards and reports.

### Customer authentication (Cycle 16)
- **OTP email verification (AUTH-3):** Customers entering their email in the pre-chat form can verify their identity via a 6-digit one-time password sent to their email. Verified customers unlock full Persistent Customer Memory — the AI remembers them across conversations. OTP codes have a 10-minute TTL with rate limiting (3 per 5 minutes).
- **Shopify customer passthrough (AUTH-4):** Logged-in Shopify customers are automatically identified via HMAC-SHA256 verification — zero-friction identity that skips the pre-chat form entirely. Configure your Customer Identity Secret in the Shopify theme settings.
- **Profile linkage (AUTH-5):** Verified customer identity (via OTP or Shopify HMAC) is now linked to the conversation record, enabling the AI to retrieve purchase history, preferences, and past interactions. A critical transport bug was fixed where non-Shopify customers' email addresses were not transmitted to the backend.

### Pre-chat identification gate (Cycle 15)
- **Pre-chat form default ON (AUTH-1):** The pre-chat form (Name + Email) is now enabled by default for all new tenants. Existing tenants are unaffected.
- **Guest access with warning:** Customers can skip identification ("Continue as guest"), but the AI immediately warns about limited capabilities — order lookups, account management, loyalty programs, and personalized recommendations are unavailable without identification. Customers must confirm they want to proceed anonymously.
- **Anonymous session AI rules:** The AI prompts anonymous customers for their email when they ask about identity-gated topics (orders, account, loyalty, rewards).

### Activation and backend improvements (Cycle 15)
- **Escalation re-escalation window (WI-A5):** Resolved conversations can be re-escalated within 24 hours. After 24 hours, the conversation is fully closed.
- **Conversation auto-archival (WI-A7):** Background sweep task runs hourly, archiving the oldest resolved/timed-out conversations when a tenant exceeds 1,000 active conversations.
- **Widget close fix (D9):** Fixed a race condition where closing the widget could terminate the conversation before the UI finished rendering.
- **Quick action auto-open (WI-A4):** Quick actions can now configure automatic widget opening with a configurable delay.
- **Knowledge base filter labels (WI-A6):** Filter dropdowns on the Knowledge Base page now have explicit labels for accessibility.

### Tests
- 99 new unit tests across Cycles 15-19 (9 + 35 + 20 + 35) — all pass, 0 new failures

---

## v1.54.7 — 2026-02-21

### Light/dark color mode
- **CSS custom property theming:** All surface, text, and overlay tokens in `styles.ts` now reference CSS custom properties (`var(--ar-*)`) instead of hardcoded hex values. The browser resolves these at paint time, enabling instant theme switching without React re-renders.
- **Light mode override:** New `html[data-mantine-color-scheme="light"]` block in `tokens.css` redefines all mode-dependent tokens — surfaces become white, text becomes dark, borders and overlays lighten.
- **Auto color mode default:** The widget `colorMode` setting defaults to `Auto`, which follows the visitor's OS preference via `prefers-color-scheme`.
- **Header always dark:** The admin header retains its dark chrome in both modes via hardcoded CSS rules.
- **Widget preview isolation:** The widget preview panel always renders with a dark background using hardcoded hex values, independent of the admin's active color scheme.
- **Toggle persistence:** Color mode selection persists across page reloads via Mantine's `localStorage` mechanism.
- **10th verification dimension:** New "Color Mode Consistency" test dimension (CM.1–CM.4) added to both UI test procedures — verifying light mode rendering, dark mode regression, widget preview isolation, and toggle persistence.

### Light-mode palette
| Token | Dark | Light |
|-------|------|-------|
| Chrome | `#0c0a09` | `#f5f5f5` |
| Page | `#1c1917` | `#f0f0ef` |
| Surface | `#292524` | `#ffffff` |
| Border | `#44403c` | `#e5e3e0` |
| Text Primary | `#fafaf9` | `#1c1917` |
| Text Secondary | `#f5f5f4` | `#292524` |
| Text Muted | `#a8a29e` | `#78716c` |

---

## v1.54.0 — 2026-02-20

### Knowledge automation
- **Storefront content ingestion (KA-1):** Automatic extraction of product titles, descriptions, collections, and policies from your Shopify storefront. Ingested content is stored as knowledge base articles with `storefront` source attribution.
- **Industry template library (KA-2):** 11 industry-specific knowledge base templates (Electronics, Fashion, Beauty, Food, Health, Home, Jewelry, Pet, Sports, Toys, General) with pre-written FAQ articles, shipping policies, and return procedures.
- **Config suggestion engine (KA-3):** Analyzes ingested knowledge base content to suggest optimal values for brand name, brand voice, greeting message, escalation keywords, and display name — with confidence scores and source attribution.
- **Suggestion badges (KA-4):** Visual badges on configuration inputs indicating when an AI-generated suggestion is available. Click to preview and apply the suggested value.
- **Onboarding wizard (KA-5):** Three-step setup wizard (Connect Store → Review Knowledge → Configure Agent) that guides new merchants through initial activation, with progress tracking and skip-ahead navigation.
- **Document parser (KA-6):** Expanded document parsing to extract meaningful content from Shopify HTML pages, handling product descriptions, policy pages, and collection metadata.
- **Knowledge automation procedure:** New repeatable procedure (`docs/operations/knowledge-automation-procedure.md`) with 6 verification steps and 11 post-conditions.

---

## v1.51.1 — 2026-02-19

### Chat pipeline reliability
- **AGNTCY SDK import resilience:** All imports from the agntcy-app-sdk package are now wrapped in try/except with local stub fallbacks. This prevents pipeline initialization failures when the SDK removes or renames exported classes (as occurred when SDK 0.5.x removed `BaseAgentProtocol`).
- **Improved error diagnostics:** The lifecycle startup handler now logs exception tracebacks (`exc_info=True`), making root-cause analysis of pipeline initialization failures significantly faster.
- **Environment variable fix:** Added `AZURE_KEYVAULT_URL` to the production container configuration, ensuring Key Vault access for secret resolution.

### Conversation quality testing
- **Live quality runner:** New `evaluation/run_quality_live.py` executes all 25 golden scenarios against production via SSE streaming, collecting response text, timing, escalation flags, and critic verdicts.
- **First live execution:** 22/25 scenarios responded (3 jailbreak correctly blocked by Critic). Scores: Faithfulness 4.72/5.0, Relevancy 3.23/5.0, Tone 4.96/5.0, Overall 4.17/5.0. Verdict: CONDITIONAL PASS.

---

## v1.51.0 — 2026-02-19

### UI improvements
- **Contact Us feature:** New Contact Us page accessible from the admin navigation, providing support contact information and feedback form.

### Test expansion
- 917 total UI tests (up from 810).
- 793 PASS, 4 SOFT-PASS, 62 SKIP, 0 FAIL (verified S60).

---

## v1.50.0 — 2026-02-19

### Design system centralization
- **CSS custom properties:** New `tokens.css` file defines 30+ design tokens (colors, spacing, borders) as CSS custom properties, replacing hardcoded hex values.
- **TypeScript token constants:** New `styles.ts` module exports typed token references for use in Mantine `sx` props and inline styles.
- **57 files refactored:** Over 200 hardcoded dark-mode hex color values replaced with design token references across all admin distributions.
- **Stone neutral palette:** New warm-gray palette (Chrome #0c0a09, Page #1c1917, Surface #292524, Border #44403c) replaces generic dark grays.
- **Zero regressions:** Full 810-test E2E verification confirmed no visual or functional regressions.

---

## v1.49.2 — 2026-02-19

### SKIP resolution
- **Avatar upload UI:** File upload zone for agent avatar with circular preview and remove button, integrated into the Widget Appearance page.
- **Tier override endpoint:** Superadmin API endpoint for changing tenant tier without Stripe webhooks.
- **Simulated customer tenant:** Automated 8-phase creation script (`create_test_tenant.py`) for test-customer-001 with 9 team members, 12 quick actions, 7 KB docs, 19 conversations.
- **Admin null-safety:** Added `?? {}` null coalescing to admin pages to prevent crashes when backend returns null aggregate fields.
- **UI test results:** 770 PASS, 3 SOFT-PASS, 37 SKIP, 0 FAIL (improved from 649/2/159/0).

---

## v1.48.0 — 2026-02-18

### Conversation quality infrastructure
- **Golden dataset (CQ-1):** 25 test scenarios across 10 categories (product inquiry, returns, shipping, billing, escalation, multilingual, edge cases, memory recall, policy enforcement, and multi-turn) for automated response quality evaluation.
- **Quality pilot framework (CQ-2):** Phase 0 heuristic evaluation framework that scores AI responses on completeness, tone, accuracy, and context retention without requiring external LLM-as-judge dependencies.
- **Critic rule hardening (CQ-3):** Expanded Critic rule #7 into three sub-rules covering jailbreak prompt detection, role-play manipulation, and instruction override attempts.
- **DeepEval scaffold (CQ-4):** Graceful degradation adapter for the DeepEval evaluation framework — runs quality tests when DeepEval is installed, skips gracefully when unavailable.

### Test coverage expansion
- **4 parallel coverage agents** wrote 879 new tests targeting repositories, security/config, chat/integrations, and knowledge/pipeline modules.
- **Performance validation:** 50-tenant concurrent load testing framework with 12 tests.
- **4,159 unit tests** passed, 0 failures (up from 3,231).

---

## v1.47.0 — 2026-02-18

### New capabilities
- **Chunking preview (C5):** Knowledge base articles now show a chunk visualization, letting merchants see exactly how their content will be split for AI retrieval.
- **Concurrent edit locking (C14):** ETag-based optimistic locking prevents configuration overwrite when multiple team members edit simultaneously. Conflicting saves receive a clear resolution prompt.
- **Avatar upload (D22):** Team members can upload PNG profile photos via the Team Management page.
- **Tier upgrade flow (D30):** Self-service plan upgrade via Stripe Checkout with preview (prorated cost, feature comparison) before committing.
- **Add-on checkout (WI#138):** Purchase add-on modules (e.g., Custom Model Training, Advanced Analytics) through Stripe Checkout sessions.
- **Memory dashboard (WI#139):** Persistent customer memory dashboard showing memory statistics, per-customer memory details, and memory deletion controls.
- **First-contact resolution (CQ-5):** FCR proxy metric tracks conversations resolved in a single interaction — visible in the Analytics API summary.

### Verification
- 7 new upgrade verification assertions (C.26–C.32)
- 3,231 tests (up from 2,994)

---

## v1.46.0 — 2026-02-18

### Platform monitoring
- **Cost analytics:** Unit economics dashboard with per-tenant cost breakdown, resource consumption trends, and cost-per-conversation metrics.
- **Abuse detection:** Automated detection of abnormal usage patterns (spike detection, rate abuse, content policy violations) with tenant-level risk scoring.

### CDN static hosting (R9b)
- Architecture document for splitting widget JavaScript and admin static assets to a CDN origin, reducing API Gateway load and improving global load times.

---

## v1.45.0 — 2026-02-18

### Magic link authentication (WI#295)
- **Passwordless login:** Team members can sign in via a magic link emailed to their registered address — no password required.
- **Token security:** HMAC-signed, single-use tokens with 15-minute expiry and rate limiting.
- **Seamless flow:** Click the link → auto-authenticated → redirected to the admin dashboard.

### Component refactoring (R6)
- **WidgetConfigurator** split into focused sub-components (appearance, behavior, greeting, pre-chat form).
- **KnowledgeBaseManager** split into table, editor, conflict scanner, and upload sub-components.
- **TeamManager** split into member list, role editor, and invitation sub-components.

### New capabilities
- **Period filtering (C1):** Analytics endpoints and dashboard support custom date range filtering (7d, 30d, 90d, custom).
- **Escalation UI (C8):** Category assignment and agent reassignment directly from the conversation inbox.
- **Search and resolve (C9):** Full-text conversation search with bulk resolve actions.

---

## v1.44.0 — 2026-02-18

### UI consistency and accessibility
- **Shared icon library:** SVG icon components replace emoji characters across all admin surfaces for consistent, accessible rendering.
- **EmptyState component:** Standardized empty state illustrations and CTAs for pages with no data.
- **Loading states:** Skeleton loaders replace spinner-only patterns on all data-fetching pages.
- **Accessibility foundation:** `eslint-plugin-jsx-a11y` enforced in CI; `aria-label` attributes added to all interactive elements.

### Login migration
- **ApiKeyLogin** and **McpConfigPanel** migrated from custom styling to Mantine component library for visual consistency.

### Design system
- **Design system document:** Codified the visual language including color tokens, spacing scale, and component mapping.
- **HelpTooltip coverage:** Extended tooltip help text to all remaining configuration inputs.

---

## v1.43.0 — 2026-02-17

### Platform capabilities
- **Incident management:** Full incident lifecycle — create, acknowledge, update, resolve. Public status page at `/api/status` (no authentication required) shows overall system health and active incidents.
- **Alerting engine:** Background alert evaluation loop (5-minute interval) with 6 metric collectors, configurable threshold rules, cooldown enforcement, and severity auto-derivation.

### UI quality
- **Shopify route fix:** Resolved Shopify admin route conflicts with the standalone admin.
- **Shared theme:** Extracted `agentRedTheme` for consistent Mantine theming across admin surfaces.
- **SVG icons:** Replaced emoji-based navigation icons with proper SVG components.

### Tests
- 2,994 unit tests passed, 0 failures (up from 2,941)
- Regression: C.15–C.19 assertions added

---

## v1.42.0 — 2026-02-17

### CI/CD pipeline
- **Parallel test matrix:** GitHub Actions CI runs tests in parallel shards for faster feedback.
- **Coverage trend:** PR comments include test coverage delta and trend indicators.
- **Branch protection:** Main branch requires passing CI checks before merge.

### Email integration
- **Azure Communication Services:** Email infrastructure provisioned for transactional notifications.
- **Email verification:** Domain verification endpoints with SPF/DKIM/DMARC compliance.

### Refactoring
- **R10 pipeline decomposition:** Monolithic `pipeline.py` split into 7-file mixin package for maintainability.
- **R3 config YAML migration:** 78 configuration fields migrated from hardcoded defaults to structured YAML configuration.

### Tests
- 2,941 unit tests passed, 0 failures (up from 2,646)

---

## v1.39.0 — 2026-02-17

### Stripe MCP integration
- **AI-powered payment queries:** Agent Red can now answer customer questions about payments, subscriptions, invoices, and refund status by connecting to your Stripe account via the Model Context Protocol (MCP).
- **Secure credential management:** Stripe API keys are stored in Azure Key Vault with an in-memory credential cache (5-minute TTL) for low-latency access.
- **Admin UI configuration:** New MCP configuration panel on the Integrations page — enter your Stripe restricted API key, test the connection, and see the available tools.
- **Read-only safety:** All Stripe queries are read-only. The mutation safety architecture (MutationPolicy, MutationExecutor) is built and tested but not activated — no write operations are permitted.

### Shopify Storefront MCP integration
- **Live product data:** The Knowledge Retrieval agent can now augment knowledge base results with real-time product data from your Shopify storefront via the Storefront MCP server.
- **Hybrid retrieval flow:** Knowledge base search results are merged with MCP storefront data when available, with graceful fallback to keyword search when the MCP connection is unavailable.
- **Shop domain security:** Cross-tenant URL validation ensures each tenant can only access their own storefront data.

### MCP client framework
- **Model Context Protocol support:** New `AgentRedMcpClient` with HTTP transport, configurable timeouts, and circuit breaker protection for external MCP server connections.
- **Per-tenant server registry:** Each tenant's MCP server configurations are stored in Cosmos DB and resolved dynamically at query time.
- **PII scrubbing:** Customer PII is automatically scrubbed from outbound MCP tool arguments before they leave the system.

### Mutation safety architecture
- **Policy framework:** Per-tenant mutation policies with configurable safety gates (Critic approval, customer confirmation, operation allowlists, per-conversation rate limits).
- **Critic-gated execution:** Six-stage mutation pipeline with fail-closed Critic validation, idempotency keys for replay prevention, and Cosmos DB audit logging.
- **Disabled by default:** Mutation execution is built and fully tested but globally disabled.

### Integration registry
- **Stripe added:** The Integrations page now shows Stripe (MCP) alongside Shopify, Zendesk, Mailchimp, and Google Analytics.
- **Dynamic configuration:** Four new admin API endpoints for Stripe credential management, connection testing, tool discovery, and disconnection.

### Tests
- 2,646 unit tests passed, 0 failures (up from 2,477)
- 140 new tests across MCP client, credential cache, mutation safety, Stripe integration, and KR+MCP integration

---

## v1.35.0 — 2026-02-17

### Category-routed escalation
- **AI category detection:** The escalation pipeline now classifies conversations into categories (service, support, sales, account, technical assistance, general inquiry) using AI analysis.
- **Workload-based auto-assignment:** Escalated conversations are automatically assigned to the escalation agent with the fewest unresolved cases in the matching category, respecting per-agent concurrency caps.
- **Manual category selection:** When manually escalating from the Inbox, you can now select a category and optionally choose a specific team member.
- **Inbox escalation details:** Escalated conversations display a category badge and the assigned team member's name in the detail pane.
- **Team workload column:** The Team page now shows an "Escalations" column with the live count of unresolved escalations per agent.

### Conversation archival
- **Archive and unarchive actions:** Resolved and timed-out conversations can be archived for long-term storage. Archived conversations are hidden from the default list but accessible via the new "Archived" filter tab.
- **Idle conversation scanner:** Background task automatically closes idle conversations that exceed the 30-minute inactivity timeout, running every 5 minutes across all tenants.

### Save and activate improvements
- **Knowledge base draft integration (D16):** Creating, updating, or deleting knowledge base articles now triggers the Pending badge, ensuring you see that activation is needed.
- **Quick action draft integration (D20/D68):** Quick action CRUD and page assignment changes now trigger the Pending badge. Page assignment changes (slot, auto-open, delay) are saved to the draft and only committed on Activate.
- **Activation dialog grouping:** The change summary groups KB modifications under "Knowledge base" and QA modifications under "Quick actions" with human-readable labels.

### Privacy and compliance
- **PII scrubbing:** New toggle on the Memory & Privacy page. When enabled, email addresses and phone numbers are automatically scrubbed from stored conversation transcripts (live responses are unaffected).

### Test coverage
- **52 new tests** from independent test coverage audit (2,477 total, 0 failures)
- New test files: admin integration API (13), customer profile API (12), security middleware (16), structured logging (11)
- Fixed regression test collection gap: integration tests now correctly excluded from unit suite

---

## v1.34.0 — 2026-02-16

### Knowledge base improvements
- **Category filter fix:** Article categories now match correctly between the table and filter dropdown. Previously, filtering by "Products" returned no results because internal mappings used singular forms.
- **Archived article stats:** The knowledge base summary cards now include an "Archived" count alongside Total, Published, Draft, and Needs attention.
- **Action icon tooltips:** All action icons (Edit, Archive, Restore, Verify) now show styled tooltips on hover instead of plain browser tooltips.
- **Category and status display:** Articles created via the admin console now correctly display their Category and Status values in the table (previously showed "--").

### Quick actions improvements
- **Auto-open toggle fixed:** The auto-open toggle on page assignments now correctly persists its state. Previously, the API response was missing the auto-open fields, causing the toggle to reset.
- **Status badge display:** Status badges ("Active", "Inactive") are no longer truncated — the column width has been increased.

### Conversation management
- **Status consolidation:** The "Completed" conversation status has been renamed to "Resolved" for consistency with the "Resolve" action button. The Inbox filter tabs now show All / Active / Esc / Resolved (replacing the "Idle" tab).

### Agent configuration
- **Tooltip additions:** Idle timeout and Max conversation turns inputs now have help tooltips explaining their purpose.
- **Activation dialog:** Updated messaging to "Draft configuration is ready to activate" for clarity.

### Widget
- **Dynamic injection:** The widget launcher now appears/disappears immediately when the system is activated/deactivated, without requiring a page refresh.

### Operational procedures
- **Tenant initialization:** New repeatable procedure for provisioning a clean tenant with zero pre-existing data. Includes 10 verification post-conditions.
- **Non-disruptive upgrade verification:** New repeatable procedure for verifying data preservation during production deployments.

### Tests
- 2,455 unit tests passed, 0 failures
- 178 UI regression tests in the repeatable procedure

---

## v1.32.7-agntcy — 2026-02-16

### AGNTCY Platform Phase 2: Pipeline Decomposition
The monolithic AI pipeline has been decomposed into six independent agent modules following the AGNTCY Agent-to-Agent (A2A) protocol. This is an internal architecture improvement with no customer-visible behavior change.

- **Six agent modules** extracted from the monolithic pipeline: Intent Classifier, Knowledge Retrieval, Response Generator, Escalation Handler, Analytics Collector, and Critic/Supervisor
- **Agent base class** (`AgentRedBaseAgent`) extends the AGNTCY SDK's `BaseAgentProtocol` with standardized message handling, error wrapping, and metadata injection
- **Container-ready deployment** — each agent has its own Dockerfile and FastAPI app with health/ready probes, enabling independent scaling and fault isolation
- **Pipeline orchestrator rewrite** — the main pipeline now delegates to agent instances via the A2A protocol interface instead of inline Azure OpenAI calls
- **101 new agent tests** covering all six agents plus the container app factory
- **2,360 total unit tests** passed, 0 failures (up from 2,330)

### Tests
- 2,360 unit tests passed, 0 failures
- 101 new agent module tests across 8 test files

---

## v1.32.7 — 2026-02-16

### Widget activation gate
- **Conversation creation gate:** The chat widget endpoint now returns 403 when the tenant configuration is not active. This prevents phantom conversations from being created before the merchant has completed setup and activated their configuration.
- **Deactivate action:** Merchants can take their AI agent offline temporarily by clicking "Deactivate" in the sidebar. The widget stops responding immediately.
- **Re-activation:** One-click re-activation when the configuration is still complete.

### Three-disposition activation control
The sidebar activation button now uses three color-coded states:
- **Green (Activate)** — All required fields present, ready to go live
- **Yellow (Activate, blocked)** — Required fields missing, activation blocked until resolved
- **Red (Deactivate)** — System is active with no pending changes, click to take offline

### Three-state sidebar badge
- **Active (green)** — Configuration is live and serving customers
- **Pending (yellow)** — Changes are pending or setup is incomplete
- **Inactive (red)** — Configuration was deactivated, widget is offline

### Configuration controls
- **Discard** now refreshes all form fields across configuration pages immediately (previously required manual page reload)
- **Roll back** after deactivation re-activates the widget automatically
- **Brand voice** is now mandatory for activation (alongside brand name and widget key)

### Language support
- Removed planned languages (German, Portuguese, Japanese, Chinese, Korean) from the admin UI
- Supported languages: English (primary)

### Bug fixes
- Fixed button text truncation on "Deactivate" when all three sidebar controls are visible
- Fixed draft save collision (409 error) after roll-back operations
- Fixed activation button incorrectly disabled during re-activation after deactivation
- Fixed success message text on configuration save
- Dashboard metrics (response time, satisfaction) now show 0 instead of placeholder values when no conversations exist
- Tier badge uses full capitalized names (Professional, not Pro+)

### Tests
- 2,330 unit tests passed, 0 failures
- 172 UI regression tests: 144 passed, 28 skipped (require conversation data or deferred features)

---

## v1.25.0 — 2026-02-13

### Inbox content search
- Search conversations by message content, not just customer name
- Debounced search with result snippets showing matched text and location

### Knowledge base content search
- Search articles by title and body content simultaneously

### Escalation email notifications
- Automatic email alerts when a conversation is escalated to a human agent

### Add-on modules
- 5 add-on modules displayed on the Billing page with tier-gated availability
- Tier badges show the minimum required plan for each add-on

### Identity extraction
- Automatic detection of customer names and email addresses from conversation text
- Stored in customer profile for personalization

---

## v1.23.0 — 2026-02-12 (unreleased)

### Admin UI polish
- **Integrations page:** Redesigned with horizontal card layout — 180×180 logo containers, light-mode card styling, hover effects on all action buttons, per-integration tooltips with documentation links
- **Button hover effects:** All primary buttons across BillingPortal (Manage billing, Purchase packs, Upgrade tier) now have visual hover feedback
- **Sidebar logo:** Dark and light mode variants — the footer logo now switches between `NEW-BLOCK-LOGO-HORIZONTAL-DARK.svg` and `NEW-BLOCK-LOGO-HORIZONTAL-LIGHT.svg` based on the active color scheme
- **Dashboard:** Removed stale All/Production/Test segmented control (test mode was removed in v1.22.0)

### Tooltip audit (71 tooltips)
Every HelpTooltip in the admin UI now includes both contextual help text and a "Learn more" link to the relevant documentation page with a section anchor. Updated across 10 component files.

### Documentation
- **Analytics Dashboard** (`/admin-guide/analytics`) — Key metrics, conversation volume chart, top intents, intent breakdown, knowledge gaps
- **Conversation Inbox** (`/admin-guide/conversations`) — Conversation list, detail view, customer profile panel, billable conversation indicator
- **Data Retention & Privacy** (`/admin-guide/data-retention`) — Retention period, PII scrubbing, consent, automatic deletion
- **Billing & Usage** (`/billing/overview`) — Subscription plans, billing tiers, conversation packs, usage dashboard, subscription management

---

## v1.22.0 — 2026-02-12 (unreleased)

### Save and activate

Configuration changes now use a two-phase commit model. Saving a setting writes to a draft — the live AI agent is unaffected until you explicitly activate.

- **Draft layer:** All configuration saves go to a draft. Multiple pages can be edited before activation.
- **Activation banner:** Persistent banner in the admin console shows when draft changes are pending, with Activate and Discard actions.
- **Activation dialog:** Review all pending changes grouped by category, see validation results, and go live with one click.
- **Restore:** One-level undo — swap the active configuration with the previous activation snapshot.
- **Atomic activation:** Agent Configuration, Quick Actions, and Widget Configuration activate together. Knowledge Base is validated but not snapshotted.
- **Validation:** Brand name and widget key are required. Activation is blocked if validation fails.

### New frontend components
- `ActivationBanner` — polls activation status every 30 seconds, shows Activate/Discard actions
- `ActivationDialog` — validation display, change summary, activate confirmation
- `RestoreDialog` — previous configuration details and restore confirmation

### API endpoints
- `GET /api/config/activation-status` — lightweight activation state for the banner
- `GET /api/config/draft` — full draft state with change diff for the activation dialog
- `POST /api/config/draft/activate` — validate and promote draft to active
- `POST /api/config/draft/discard` — delete all draft changes
- `POST /api/config/restore` — swap active with previous activation snapshot

### Removed
- **Onboarding wizard** — replaced by direct page editing combined with the activation workflow
- **Test mode A/B routing** — replaced by the draft/activate model (edit freely, activate when ready)
- `OnboardingWizard.tsx` and `Onboarding.tsx` deleted
- `test_mode_service.py` and its test suite deleted

### Migration
- Lazy migration from the old `PreferencesDocument` format: existing tenants are upgraded to the new `config_state` model on first access with no downtime

### Tests
- 176 new tests: 94 activation service, 52 config API activation, 30 migration compatibility
- Total test suite: 2,301 passed, 0 failures

---

## v1.21.0 — 2026-02-12 (unreleased)

### Team management and role-based access
- 4-role system: superadmin, admin, escalation agent, and viewer
- Per-user API keys with automatic role resolution on login
- Role-based sidebar navigation and page access control
- Superadmin is hidden from other users and cannot be deleted
- Escalation agents see only the Inbox, filtered to their assigned categories

### Escalation notifications
- AI pipeline escalation events trigger email notifications to matching escalation agents
- Urgency-to-severity mapping: high (critical), medium (warning), low (informational)

### Configuration
- Escalation keywords now ship with 9 sensible defaults for new tenants

### Deployment safeguards
- Upgrade script: admin dist freshness check, ACR tag validation, source integrity verification
- Rollback script: verifies image tag exists in ACR before deploying

### Observability
- Debug logging for authentication routing and role access decisions
- Info logging for escalation alert events

---

## v1.20.1 — 2026-02-12

### Admin dashboard
- 46 UX work items: sidebar renames, page reordering, tooltips, widget controls
- Wizard redesign: mode selector, step restructure, Go Live checklists
- Memory and Privacy page with 4-layer memory controls and privacy accordion
- Dashboard and Analytics merged into single Dashboard view
- Draggable chat panel with cross-frame positioning

---

## v1.20.0 — 2026-02-11

### Admin dashboard
- Test mode A/B rollout engine with 7-priority implementation
- Unified onboarding wizard: standalone admin now uses the shared `OnboardingWizard` component (previously had a separate 1,497-line implementation)
- Test mode banner in standalone admin header (polls every 30s, amber badge)
- Fixed TypeScript build errors in both admin SPAs (standalone + Shopify)

---

## v1.18.2 — 2026-02-11

### Admin security
- Immutable HMAC signing key for multi-replica password reset tokens
- Fixed f-string token placeholder: `\{\{token\}\}` in hidden form fields now renders correctly
- Auto-login cookie set on successful password reset

---

## v1.18.0 — 2026-02-11

### Admin security
- Email-based forgot-password flow replaces the old change-password endpoint
- HMAC-signed reset tokens work across multiple replicas without shared state
- 15-minute token expiry, single-use enforcement, rate limiting (3 requests per 5 minutes)
- Branded HTML email with reset link delivered via SMTP (Titan Email)

### Widget
- Quick Action prompt buttons: configurable pill buttons in the widget greeting area that send pre-defined prompts
- Template variable substitution (`\{\{product_name\}\}`, `\{\{collection_name\}\}`, `\{\{page_handle\}\}`) for page-aware prompts
- Improved panel drop-shadow (dual-layer) for visibility on busy storefront backgrounds

### Admin dashboard
- Quick Action CRUD: 8-endpoint API for creating, editing, ordering, and assigning prompts to page types
- Conversation search endpoint (previously returned 405)
- Fixed audit log 500 error (Cosmos DB query initialization)
- Fixed customer profile list 503 error

### Logo
- Fixed corrupted logo on forgot-password pages (replaced invalid PNG data URI with SVG)

### Documentation
- Docs site deployed to agentredcx.com (Docusaurus + GitHub Pages)
- MDX escaping fixes for template variable documentation

---

## v1.15.2 — 2026-02-10

### Bug fixes
- Fixed FastAPI route ordering: static routes (`/stale`, `/export`, `/staleness`) now registered before the `/{entry_id}` catch-all in the knowledge base API
- Widget config loading: Shopify Liquid template no longer overrides API-fetched tenant configuration with default values
- Widget default API URL corrected to production FQDN

### Infrastructure
- API Gateway restored after Azure subscription suspension and recovery
- Admin UI validation: 86/86 endpoints passing

---

## v1.14.0 — 2026-02-09

### Bug fixes
- Fixed hybrid search score filtering: `rrf_score` key mismatch caused all search results to be filtered out by the minimum score check
- Improved Critic prompt engineering to reduce false blocks on product feature descriptions

### Knowledge base
- Conflict scanner: 4-phase detection (embedding similarity, title trigrams, content overlap, factual conflict regex) with HIGH/MEDIUM/LOW severity ratings
- Admin UI "Scan for conflicts" button in the knowledge base manager toolbar

### App Store preparation
- Listing accuracy review: 8 inaccurate claims corrected to verifiable facts
- Non-disruptive upgrade infrastructure: automated upgrade/rollback scripts with 43-test regression suite

---

## v1.0.0 — 2026-02-09

**Initial release**

### AI pipeline
- Six specialized AI agents: intent classification, knowledge retrieval, response generation, escalation detection, analytics, and content safety (Critic/Supervisor)
- Direct Azure OpenAI integration (GPT-4o for responses, GPT-4o-mini for classification)
- Stream-then-validate pattern: AI responses stream in real-time, Critic validates post-stream

### Persistent customer memory
- **Layer 1 — Customer context:** Structured profiles with purchase history, geography, preferences, and account state injected into every interaction
- **Layer 2 — Conversation memory:** Vectorized transcripts with semantic search across full interaction history (Cosmos DB DiskANN)
- **Layer 3 — Cross-session learning:** Pattern extraction with confidence scoring and monthly decay (Professional and Enterprise tiers)
- **Layer 4 — Dedicated model training:** Per-customer fine-tuning on 1,000+ interactions (Enterprise add-on)

### Knowledge base
- Hybrid retrieval: BM25 keyword matching + vector similarity with Reciprocal Rank Fusion
- Document upload: PDF, DOCX, CSV, TXT, HTML parsing with automatic chunking
- Staleness detection with 3-factor scoring (age, embedding drift, verification recency)
- 3-tier semantic caching (embedding, search results, semantic similarity)

### Chat widget
- Preact-based widget (~17KB gzip) with Shadow DOM isolation
- SSE streaming for real-time AI responses
- WebSocket for typing indicators and presence
- Light and dark mode support
- Configurable appearance, greeting, pre-chat form, and offline form
- Shopify Theme App Extension delivery

### Admin dashboard
- Embedded Shopify admin (Polaris + App Bridge)
- Standalone admin with API key authentication
- Conversation inbox with message threading
- Knowledge base manager with document upload
- Analytics overview with intent breakdown
- Widget configurator with live preview
- Team management with role-based access
- 9-step onboarding wizard

### Billing
- Shopify Billing API integration (subscriptions + usage charges)
- 3-tier consumption: included allowance → conversation packs → overage
- Usage dashboard with real-time metrics and CSV export
- 14-day free trial on all tiers

### Security and compliance
- GDPR: 3 mandatory Shopify webhooks, PII scrubbing, data export/deletion, consent management
- Fail-closed Critic policy: responses blocked unless explicitly approved
- Per-tenant data isolation (Cosmos DB partition keys)
- Rate limiting per tier (Starter 10/min, Professional 50/min, Enterprise 200/min)

### Infrastructure
- Azure Container Apps (East US) with native auto-scaling
- Cosmos DB Serverless with DiskANN vector index
- NATS JetStream event bus with tenant-level stream isolation
- Zero-downtime rolling deployment

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
