---
sidebar_position: 100
title: Changelog
---

# Changelog

All notable changes to Agent Red Customer Experience are documented here.

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
- **Expired tenant filter:** The Provider Console tenant directory now includes an "Expired" status filter option with a complete set of static filter labels for all tenant lifecycle states.

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

## v1.57.5 — Provider Console hardening (2026-02-24)

### Bug fixes

- **Provider Console data validation:** Seven Provider Console components corrected to pass both partition key and document ID to repository read operations. Previously, the systemic single-argument pattern caused silent data lookup failures.
- **NATS health reporting:** Three code paths in the Provider Console incorrectly reported NATS as "deployed" based on manager object existence rather than actual connection status. Fixed to check connection state.
- **SPA static file serving:** Logo and favicon files in the Provider and Shopify SPA build outputs are now served correctly instead of falling through to the SPA catch-all route.

---

## v1.57.4 — Beta verification and quality hardening (2026-02-23)

### Beta readiness (v1.57.0)

Four features required for beta customer onboarding have been completed:

- **Conversation vectorization scanner:** A background task scans ended conversations every 5 minutes and vectorizes them for persistent memory retrieval. Each cycle processes up to 20 conversations per tenant. Vectorized conversations are marked with a timestamp to prevent re-processing.
- **Widget consent collection:** A consent banner appears in the chat widget when the tenant has enabled consent collection. Customer consent status (granted, denied, withdrawn) is stored on their profile and controls whether conversation memory is retained.
- **Cost analytics:** A new superadmin endpoint provides estimated per-tenant cost breakdowns including Azure OpenAI token costs, Cosmos DB request unit consumption, and container compute amortization.
- **Abuse detection:** Rate anomaly and error rate heuristics calculate a risk score (0-100) for each tenant. Operators can flag tenants from the Provider Console.

### Assessment fixes (v1.57.1)

An independent assessment review identified four items, all resolved:

- **Fine-tuning pipeline hardened:** Placeholder return values in the fine-tuning pipeline have been replaced with `NotImplementedError` exceptions. The existing triple-gate (feature flag, tier check, safety validation) already prevents user access, but the explicit errors provide defense-in-depth.
- **Storefront ingestion annotation:** A misleading "stub" comment has been corrected to accurately describe the module's production functionality.

### Critical path verification (v1.57.4)

The full 21-test critical path (CP.1–CP.21) has been verified against production, covering SPA provisioning, setup wizard, activation, all admin pages, live chat pipeline, dashboard, inbox, and configuration persistence. All 21 tests pass.

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

### SPA tenant provisioning

Service providers can now create tenants directly from the Provider Console without requiring Stripe or Shopify billing flows.

- **Create Tenant modal:** A new "Create Tenant" button in the Tenant Directory opens a modal form with fields for company name, tenant ID (auto-generated or custom), tier, billing channel, and contact email.
- **Manual billing channel:** A new `manual` billing channel type distinguishes tenants created by the service provider from those provisioned through Stripe, Shopify, or trial flows.
- **Auto-activation:** Manually provisioned tenants are automatically activated on creation — no separate activation step required.
- **Superadmin key generation:** When a contact email is provided, a superadmin team member and API key are automatically created and displayed in the success confirmation.

### Developer experience

- **Thermal-safe test harness:** A new `scripts/run-tests-thermal-safe.ps1` script distributes the test suite across 5 batches with configurable xdist parallelism and cooling pauses between batches. This prevents sustained CPU heat buildup that caused system instability during extended test runs.

### Tests

- 57 new tests across 5 test files — identity preprocessor (14), pipeline wiring (5), system prompt identity (12), SPA provisioning (12), superadmin tenant creation (8), plus 6 test drift fixes for new schema values

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
- **Provider Console camelCase fix:** Six Provider Console pages corrected to use camelCase field names matching API response format.
- **Data-binding verification (9th dimension):** Added data-binding correctness as a new test dimension across all 16 Provider Console pages.

### Test expansion
- 917 total UI tests (up from 810) — 802 standalone + 115 provider.
- 793 PASS, 4 SOFT-PASS, 62 SKIP, 0 FAIL (verified S60).

---

## v1.50.0 — 2026-02-19

### Design system centralization
- **CSS custom properties:** New `tokens.css` file defines 30+ design tokens (colors, spacing, borders) as CSS custom properties, replacing hardcoded hex values.
- **TypeScript token constants:** New `styles.ts` module exports typed token references for use in Mantine `sx` props and inline styles.
- **57 files refactored:** Over 200 hardcoded dark-mode hex color values replaced with design token references across all three admin distributions (Shopify, Standalone, Provider).
- **Stone neutral palette:** New warm-gray palette (Chrome #0c0a09, Page #1c1917, Surface #292524, Border #44403c) replaces generic dark grays.
- **Zero regressions:** Full 810-test E2E verification confirmed no visual or functional regressions.

---

## v1.49.2 — 2026-02-19

### SKIP resolution
- **Avatar upload UI:** File upload zone for agent avatar with circular preview and remove button, integrated into the Widget Appearance page.
- **Tier override endpoint:** Superadmin API endpoint for changing tenant tier without Stripe webhooks.
- **Simulated customer tenant:** Automated 8-phase creation script (`create_test_tenant.py`) for test-customer-001 with 9 team members, 12 quick actions, 7 KB docs, 19 conversations.
- **Provider Console null-safety:** Added `?? {}` null coalescing to 8 Provider Console pages to prevent crashes when backend returns null aggregate fields.
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

### Provider admin — Phase 3 & 4
- **Support diagnostics (HV-1):** Provider console page showing per-tenant diagnostic data — recent errors, configuration health, and resolution suggestions.
- **Cost analytics (HV-2):** Unit economics dashboard with per-tenant cost breakdown, resource consumption trends, and cost-per-conversation metrics.
- **Abuse detection (HV-4):** Automated detection of abnormal usage patterns (spike detection, rate abuse, content policy violations) with tenant-level risk scoring.

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
- **ApiKeyLogin** and **McpConfigPanel** migrated from custom styling to Mantine component library for visual consistency with the Provider console.

### Design system
- **Dual-surface design system document:** Codified the visual language for Shopify Polaris (tenant admin) and Mantine (provider admin) surfaces, including color tokens, spacing scale, and component mapping.
- **HelpTooltip coverage:** Extended tooltip help text to all remaining configuration inputs.

---

## v1.43.0 — 2026-02-17

### Provider admin — Phase 2
- **4 new SPA pages:** Status Page, Alert Configuration, Compliance Dashboard, Secret Posture — completing the Provider console's operational monitoring suite.
- **Grouped sidebar navigation:** 4 navigation groups (Overview, Operations, Compliance & Security, Account) with collapsible sections.
- **Incident management (HV-5):** Full incident lifecycle — create, acknowledge, update, resolve. Public status page at `/api/status` (no authentication required) shows overall system health and active incidents.
- **Alerting engine (RB-4):** Background alert evaluation loop (5-minute interval) with 6 metric collectors, configurable threshold rules, cooldown enforcement, and severity auto-derivation.
- **MFA/TOTP (RB-5):** Two-factor authentication for the Provider console — TOTP setup with QR code, 10 backup codes (SHA-256 hashed, single-use), and JWT session tokens with 8-hour lifetime.

### UI quality
- **Shopify route fix:** Resolved Shopify admin route conflicts with the standalone admin.
- **Shared theme:** Extracted `agentRedTheme` for consistent Mantine theming across provider and standalone surfaces.
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

### Provider SPA console — Phase 1
- **Provider admin scaffold:** Vite + Mantine + Recharts single-page application (818KB / 240KB gzip) mounted at `/admin/provider/`.
- **API key login:** Provider authentication using API key credentials.
- **5 data pages:** Health Dashboard, Tenant Directory, Deployment History, Queue Health, Integration Health.

### Refactoring
- **R10 pipeline decomposition:** Monolithic `pipeline.py` split into 7-file mixin package for maintainability.
- **R3 config YAML migration:** 78 configuration fields migrated from hardcoded defaults to structured YAML configuration.

### Provider backend endpoints
- **Queue depth monitoring (C-1):** Real-time queue depth metrics for all background processing queues.
- **Compliance dashboard (C-3):** Configuration compliance scoring and remediation tracking.
- **Secret posture (C-4):** Key Vault secret rotation status and expiry monitoring.
- **Integration reliability (HV-3):** Health check metrics for all external service integrations.

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
- **Disabled by default:** Mutation execution is built and fully tested but globally disabled. This will be enabled in a future release when the customer confirmation UX is implemented.

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
- Supported languages: English (primary), Spanish (coming soon), French (coming soon)

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
- Upgrade script: SPA dist freshness check, ACR tag validation, source integrity verification
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
- 9 Azure Container Apps (East US 2)
- Cosmos DB Serverless with DiskANN vector index
- KEDA auto-scaling with night profiles
- Zero-downtime rolling deployment

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
