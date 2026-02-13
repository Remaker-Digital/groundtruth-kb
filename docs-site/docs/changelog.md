---
sidebar_position: 100
title: Changelog
---

# Changelog

All notable changes to Agent Red Customer Experience are documented here.

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
