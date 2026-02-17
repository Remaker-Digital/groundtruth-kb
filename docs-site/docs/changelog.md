---
sidebar_position: 100
title: Changelog
---

# Changelog

All notable changes to Agent Red Customer Experience are documented here.

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
