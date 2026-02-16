# Admin UI Test Procedure

**Type:** Repeatable Procedure
**Version:** 1.0.0
**Created:** 2026-02-13 (Session 17)
**Last Run:** 2026-02-13 (Session 18 — full 10-page review complete)

---

## Purpose

Page-by-page functional review of the production admin UI. Every defect found
during testing is added as a regression test before being fixed, ensuring it is
permanently checked in future runs.

## Variables

| Variable | Value |
|----------|-------|
| `ADMIN_URL` | `https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io/admin/standalone` |
| `DOCS_URL` | `https://agentredcx.com/docs` |
| `TENANT` | `remaker-digital-001` (blanco-9939) |

## Procedure

### Pre-flight

- [ ] If re-seeding tenant: run `seed_tenant.py --execute` **without `--demo`** for clean initial state (includes Phase 0 partition cleanup — deletes all stale data before seeding fresh). Do **not** use `--demo` unless specifically testing with conversation data.
- [ ] **After re-seeding:** Complete all POST-SEED STEPS in `scripts/seed_tenant.py` (Key Vault update → revision restart → verify authentication → update `.env.local` → update MEMORY.md). Skipping these leaves the admin UI unable to authenticate, causing missing tier badge, missing sidebar data, and broken functionality. See the procedure header in `seed_tenant.py` for exact commands.
- [ ] Open `ADMIN_URL` in browser (hard-refresh if previously loaded with stale credentials)
- [ ] Verify page loads without errors (no blank screen, no console errors)
- [ ] Verify sidebar navigation is fully rendered
- [ ] Verify tenant name and tier badge (capitalized, e.g. "Professional") are displayed in header
- [ ] If testing initial provisioned state (Page 0): verify Dashboard shows **0 conversations** (Total conversations = 0, Billable = 0)

---

### Page 0: Initial Provisioned State

Run immediately after `seed_tenant.py --execute` on a fresh tenant. This validates the owner's state model specification: a freshly provisioned tenant starts with all merchant-configurable fields empty, badge Pending, widget not serving, activation control yellow.

| # | Test | Expected | Status |
|---|------|----------|--------|
| 0.1 | Configuration badge after fresh seed | Pending (yellow dot) | |
| 0.2 | Header tier badge | Displays "Professional" (green, capitalized) | |
| 0.3 | Brand name field | Empty (placeholder "Your store or brand name" visible) | |
| 0.4 | Brand voice field | Empty (placeholder visible) | |
| 0.5 | Custom instructions textarea | Empty | |
| 0.6 | Refund policy / Shipping policy textareas | Empty | |
| 0.7 | Activation control disposition (never activated, mandatory fields missing) | Yellow / "Activate" — mandatory fields (brand_name, brand_voice) are empty, so activation is blocked | |
| 0.8 | Discard button | Visible, enabled | |
| 0.9 | Roll back button | Visible, disabled/greyed out (no prior state) | |
| 0.10 | Welcome dialog on first load | "Your AI customer service assistant is not yet active" message shown | |
| 0.11 | `GET /api/config/activation-status` | `has_pending_changes=true, active_version=0, active_activated_at=null, is_configured=false, is_active=false` | |
| 0.12 | `GET /api/config?state=draft` brand_name | Empty string `""` | |
| 0.13 | Click Discard on never-activated tenant | State unchanged: badge stays Pending, all fields remain empty | |
| 0.14 | Click Activate (yellow) with brand_name empty | Preflight dialog shows hard error: "Brand name is required before activation" | |
| 0.15 | Click Activate (yellow) with brand_voice empty | Preflight dialog shows hard error: "Brand voice is required before activation" | |
| 0.16 | Widget conversation gate (never activated) | `POST /api/chat/conversations` with valid widget key returns 403 `{"type": "not_active"}` — no conversation document created | |
| 0.17 | Widget.js config response (never activated) | Widget config fetch returns `widget_active: false` — widget does not mount on storefront | |

---

### Page 0A: Activation Control Lifecycle

Tests the full activation → deactivation → re-activation cycle. Run after Page 0 (starting from never-activated state with empty fields).

| # | Test | Expected | Status |
|---|------|----------|--------|
| 0A.1 | Fill brand_name only, save draft | Activation control stays yellow/"Activate" — brand_voice still missing | |
| 0A.2 | Fill brand_voice, save draft | Activation control turns green/"Activate" — all mandatory fields present in draft | |
| 0A.3 | Click Activate (green) | Confirmation dialog opens showing validation results; click confirm → activation succeeds | |
| 0A.4 | Badge after first activation | Green "Active" dot | |
| 0A.5 | Activation control after activation (no pending changes) | Red / "Deactivate" — system is active with no pending draft changes | |
| 0A.6 | `GET /api/config/activation-status` after activation | `is_active=true, is_configured=true, has_pending_changes=false, active_activated_at != null` | |
| 0A.7 | Widget conversation gate (active) | `POST /api/chat/conversations` with valid widget key returns 200 — conversation created successfully | |
| 0A.8 | Widget.js config response (active) | Widget config fetch returns `widget_active: true` — widget mounts on storefront | |
| 0A.9 | Click Deactivate (red) | Confirmation dialog opens: "Deactivating will immediately stop the chat widget on your storefront. Your configuration will be preserved." | |
| 0A.10 | Confirm deactivation | System deactivates; badge changes to red "Inactive" dot | |
| 0A.11 | Activation control after deactivation (config still complete) | Green / "Activate" — active config still has all mandatory fields, one-click re-activation available | |
| 0A.12 | `GET /api/config/activation-status` after deactivation | `is_active=false, is_configured=true, has_pending_changes=false` | |
| 0A.13 | Widget conversation gate (deactivated) | `POST /api/chat/conversations` with valid widget key returns 403 `{"type": "not_active"}` — no conversation created | |
| 0A.14 | Click Activate (green) to re-activate | Confirmation dialog → confirm → system re-activates; badge returns to green "Active" | |
| 0A.15 | Widget conversation gate (re-activated) | `POST /api/chat/conversations` returns 200 — conversations work again | |
| 0A.16 | Make draft change while active | Modify brand_name, save draft → activation control changes from red "Deactivate" to green "Activate" (pending changes with all mandatory fields present) | |
| 0A.17 | Make draft change that removes mandatory field while active | Clear brand_name in draft, save → activation control changes to yellow "Activate" (pending changes with mandatory field missing) | |
| 0A.18 | Sidebar badge during pending changes | Yellow "Pending" (regardless of whether system was previously active) | |

---

### Activation Control Disposition Summary (Reference)

| System State | Pending Changes? | Mandatory Fields Complete? | Button | Color | Badge |
|---|---|---|---|---|---|
| Never activated | Any | Missing | Activate | 🟡 Yellow | Pending |
| Never activated | Yes | All present | Activate | 🟢 Green | Pending |
| Active | No | N/A | Deactivate | 🔴 Red | Active |
| Active | Yes | Missing | Activate | 🟡 Yellow | Pending |
| Active | Yes | All present | Activate | 🟢 Green | Pending |
| Deactivated | No | Config still complete | Activate | 🟢 Green | Inactive |
| Deactivated | Yes | Missing | Activate | 🟡 Yellow | Pending |
| Deactivated | Yes | All present | Activate | 🟢 Green | Pending |

---

### Page 0B: Configuration Controls (Deactivate/Activate, Discard, Roll back)

Tests the four CONFIGURATION controls as an integrated set across different system states.
Run after Page 0A (system is now re-activated with brand_name + brand_voice set).

**Precondition:** System is Active (green badge, red "Deactivate" button), brand_name and brand_voice are set, active_version ≥ 1.

| # | Test | Expected | Status |
|---|------|----------|--------|
| 0B.1 | **Discard when active with no pending changes** — click sidebar Discard | No visible change; badge stays Active (green); activation control stays red "Deactivate" — there is nothing to discard | |
| 0B.2 | **Make a draft change** — modify brand_name, click "Save draft inputs" | Badge changes to Pending (yellow); activation control changes to green "Activate" (all mandatory fields still present) | |
| 0B.3 | **Discard with pending changes while active** — click sidebar Discard | Draft reverts to match active config; badge returns to Active (green); activation control returns to red "Deactivate" | |
| 0B.4 | **Re-confirm discard** — verify `GET /api/config?state=draft` after discard | Draft brand_name matches the active config brand_name (reverted), not the modified value | |
| 0B.5 | **Make another draft change** — modify brand_name, save draft → then click Activate (green) | Activation dialog shows preflight results; confirm → activation succeeds; active_version increments; badge = Active (green); activation control = red "Deactivate" | |
| 0B.6 | **Roll back after second activation** — click Roll back | Confirmation dialog appears; confirm → previous config restored; active_version increments; badge = Active (green); brand_name reverts to value from first activation | |
| 0B.7 | **Roll back button state** — immediately after Roll back | Roll back remains enabled (the just-restored version is now the latest active, but the one before it is still available as PREVIOUS) — OR disabled if there is no further PREVIOUS state to restore | |
| 0B.8 | **Deactivate then Discard** — deactivate system (red → confirm), then modify brand_name in draft, save draft, then Discard | Badge changes to Inactive (red) after deactivate; after draft modification, badge changes to Pending (yellow); after Discard, badge returns to Inactive (red) with no pending changes; activation control = green "Activate" (config still complete) | |
| 0B.9 | **Re-activate after deactivation** — click Activate (green) | System re-activates; badge returns to Active (green); activation control = red "Deactivate" | |
| 0B.10 | **Clear mandatory field, attempt Activate** — clear brand_name in draft, save draft, click Activate (yellow) | Preflight dialog shows hard error "Brand name is required before activation"; activation blocked | |
| 0B.11 | **Discard after clearing mandatory field** — click sidebar Discard | Draft reverts; brand_name restored from active config; badge returns to Active (green); activation control returns to red "Deactivate" | |
| 0B.12 | **Roll back after deactivation** — deactivate system, then click Roll back | Roll back restores previous active config AND system returns to active state (deactivated_at cleared); badge = Active (green) | |

---

### Page 1: Dashboard

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.1 | Five metric cards render | Total conversations, Avg response time, Resolution rate, Customer satisfaction, Escalation rate — all with values or "--" | |
| 1.19 | Avg response time is 0 when no conversations exist | When `totalConversations=0`, the "Avg response time" metric card displays `0s` (not a non-zero default like 2.3s, and not "--") | |
| 1.20 | Customer satisfaction is 0 when no conversations exist | When `totalConversations=0`, the "Customer satisfaction" metric card displays `0/5` (not a non-zero default like 4.2/5, and not "--") | |
| 1.2 | Metric card tooltips have help icon | Each card shows (i) icon that opens tooltip on hover | |
| 1.3 | Tooltip doc links point to specific anchors | Total conversations → `analytics#total-conversations`, Avg response time → `analytics#average-response-time`, Resolution rate → `analytics#resolution-rate`, Customer satisfaction → `analytics#customer-satisfaction`, Escalation rate → `analytics#escalation-rate` | |
| 1.4 | Tooltip doc links open correct doc page section | Click link in tooltip → navigates to correct heading on docs site | |
| 1.5 | Period selector (7d/14d/30d/90d) is functional | Clicking each option changes the "Last X days" label | |
| 1.6 | Conversation volume chart respects period selector | Chart only shows data points within the selected period window (no data from before the cutoff date) | |
| 1.7 | Conversation volume chart doc link | Points to `analytics#conversation-volume-chart` | |
| 1.8 | Recent conversations section renders | Shows up to 5 conversations with name, message count, status, time | |
| 1.9 | Recent conversations doc link | Points to `conversations#conversation-list` | |
| 1.10 | Top topics section renders | Shows topic names with counts and distribution bars | |
| 1.11 | Topic breakdown table renders | Full table with Topic, Count, Distribution columns | |
| 1.12 | Knowledge gaps section renders | Shows escalated conversations with link, status, turns, messages, date | |
| 1.13 | Knowledge gaps doc link | Points to `analytics#knowledge-gaps` | |
| 1.14 | Configuration badge in sidebar shows correct state | Three states: "Active" (green) when active with no pending changes; "Pending" (yellow) when never activated or has pending changes; "Inactive" (red) when deactivated with no pending changes | |
| 1.17 | Configuration badge reflects actual system state | If conversations have been processed, the configuration must be in "Active" state (agent cannot serve without an activated config) | |
| 1.18 | Roll back button disabled when no previous activation exists | Roll back is always visible but disabled (greyed out) when `active_version < 2`; enabled only when a PREVIOUS config state exists to restore | |
| 1.15 | Chart shows no data before tenant creation date | Conversation volume chart must not display data points dated before the tenant's actual creation/first-activity date | |
| 1.16 | Chart X-axis spans full selected period | When 7d/14d/30d/90d is selected, the chart X-axis starts at exactly (today − N days) and ends at today, regardless of whether data exists for the full range | |

---

### Page 2: Inbox

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.1 | Three-panel layout renders | Left: conversation list, Center: message thread, Right: customer profile | |
| 2.2 | Filter tabs show correct counts | All, Active, Esc, Idle — counts match actual conversation statuses | |
| 2.3 | Conversation list items render | Avatar, name/ID, message count, status badge, timestamp, unread indicator | |
| 2.4 | Clicking a conversation updates detail panels | Center panel shows messages (or "No messages"), right panel shows conversation info | |
| 2.5 | Search by customer name | Searching a customer name returns matching conversations | |
| 2.6 | Search by message content | Searching a word from message content (e.g., "product") returns conversations containing that word in their messages | |
| 2.7 | Clicking search results updates detail panel | Selecting a search result populates center + right panels, even if the conversation is not in the current inbox page | |
| 2.8 | Escalate action updates status | Clicking "Escalate to human" changes conversation status to "escalated" | |
| 2.9 | Escalated conversation appears in Esc filter | After escalation, Esc tab count increments and conversation is visible in Esc filter | |
| 2.10 | Resolve action updates status | Clicking "Resolve" changes conversation status to "resolved" | |
| 2.11 | Escalate button hidden for escalated conversations | Already-escalated conversations do not show the escalate button | |
| 2.12 | Resolve button hidden for resolved conversations | Already-resolved conversations do not show the resolve button | |
| 2.13 | Search "no results" state | Searching a term with no matches shows "No matching conversations" message | |
| 2.14 | Message thread renders messages | Selecting a conversation with messages shows the message bubbles with role, content, timestamp | |

---

### Page 3: Team Members

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.1 | Team member list renders | Table with Team Member (name+email), Role, Joined, Last Active, Actions columns | PASS |
| 3.2 | Add team member | Clicking "+ Invite member" opens inline form with Email*, Name, Role*, Send invite button | PASS |
| 3.3 | Role edit inline | Changing role dropdown in table row updates role (Admin, Escalation agent, Viewer options) | PASS |
| 3.4 | Delete team member | Clicking trash icon shows confirmation dialog naming the member, warns permanent deletion | PASS |
| 3.5 | Role dropdown options | Dropdown shows Admin, Escalation agent, Viewer — Superadmin is hidden | PASS |
| 3.6 | Role tooltip | Hovering (?) next to ROLE header shows all 4 role descriptions | PASS |
| 3.7 | Owner row non-editable | Owner/Superadmin row shows badge instead of dropdown, no delete icon | PASS |
| 3.8 | Escalation agent categories | Escalation agents show category badges (Sales, Support, Service, Account, etc.) | PASS |

---

### Page 4: Agent Configuration

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.1 | Brand & persona section renders | Brand name* (required), Brand voice* (required), Formality dropdown, Response length dropdown | |
| 4.2 | Policies section renders | Return window selector, Refund policy textarea, Shipping policy textarea | PASS |
| 4.3 | Escalation section renders | Threshold slider (Conservative–Aggressive), 6 category accordions with toggles | PASS |
| 4.4 | Escalation category expand | Expanding a category shows Notification email, Keywords (chips with ×), Add keyword input, Reset button | PASS |
| 4.5 | Custom instructions section | Textarea with placeholder, safety note below ("Safety rules always take precedence") | PASS |
| 4.6 | Language section renders | Primary language dropdown (English only), Supported languages chips: English, Spanish (coming soon), French (coming soon), 5 planned languages (disabled) | |
| 4.7 | Idle timeout and Max turns | Numeric inputs with current values (30 minutes, 50 turns) | PASS |
| 4.8 | Save draft inputs button at bottom | "Save draft inputs" button at bottom of page; no per-page Discard button (sidebar Discard serves that purpose) | |
| 4.9 | Section tooltips | (?) icons on Brand & persona, Policies (if present), Escalation, Custom instructions, Language | PASS |
| 4.10 | Save draft inputs succeeds | Modify brand name, click "Save draft inputs" → success notification, changes persisted on page reload | |
| 4.11 | Sidebar Discard reverts unsaved changes | Modify a field, click sidebar Discard → field reverts to last saved value | |
| 4.12 | Error banner dismissible | If a save error occurs, the error banner X button closes the banner | |

---

### Page 5: Knowledge Base

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.1 | Page renders with stats | Total articles, Published, Draft, Needs attention cards with counts | PASS |
| 5.2 | Article table renders | Title, Category, Status, Freshness, Last updated, Actions columns | PASS |
| 5.3 | Freshness badges | Articles show Fresh (green) or Aging (yellow) badges | PASS |
| 5.4 | Search filters articles | Typing in search box filters articles by title and content | PASS |
| 5.5 | Edit article modal | Clicking edit icon opens modal with Title*, Category*, Content*, Status* fields pre-filled | PASS |
| 5.6 | Action buttons present | Scan for conflicts, Export CSV, Import, + Add article buttons visible | PASS |
| 5.7 | Category and status filters | Two "All" dropdowns filter the article list | PASS |
| 5.8 | Needs attention tooltip | Hovering "Needs attention" card shows explanation text | PASS |
| 5.9 | Created article shows Category and Status in list | After creating an article with Category and Status, both values display in the article table row (not "--") | |
| 5.10 | Category/Status filters match article data | Filtering by the assigned category or status returns the matching article | |
| 5.11 | KB article create triggers Pending config state | After saving a new article, sidebar config badge changes to "Pending" and Activate button becomes available | |
| 5.12 | Archived article visually distinguished | After archiving, the article row shows a clear visual indicator (e.g. "Archived" status badge, strikethrough, or removed from active list) | |
| 5.13 | Freshness value meaningful for new articles | Newly created articles show "Fresh" (green), not "--" | |
| 5.14 | Archived article can be restored | An archived article has a visible control to restore it to its previous status (Published or Draft) | |

---

### Page 6: Quick Actions

| # | Test | Expected | Status |
|---|------|----------|--------|
| 6.1 | Prompt library tab renders | Table with Order, Icon, Label, Prompt template, Status, Actions columns; count in tab label | PASS |
| 6.2 | Empty state with examples | "No quick actions yet" message with 4 QA starter chips (Track my order, Return policy, Product recommendations, Help with my order) | PASS |
| 6.3 | Create quick action button | Red "Create quick action" button visible | PASS |
| 6.4 | Page assignments tab renders | Table with 9 page types (All pages fallback, Home, Product, Collection, Cart, Search, Blog, Page, Other) | PASS |
| 6.5 | Page assignment controls | Each row has Slot 1, Slot 2 dropdowns, Auto-open toggle, Delay (s) input | PASS |
| 6.6 | Page assignments explanation | Info card explains slot/fallback behavior | PASS |
| 6.7 | Quick action create triggers Pending config state | After creating a quick action, sidebar config badge changes to "Pending" | |
| 6.8 | Auto-open toggle functional | Toggling Auto-open on a page assignment row enables/disables auto-open and persists on reload | |

---

### Page 7: Widget Configuration

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.1 | Live preview renders | Chat widget preview on right side with header, messages, input, launcher | PASS |
| 7.2 | Appearance section | Header left/right color pickers with hex input, color swatches, gradient toggle | PASS |
| 7.3 | Font family dropdown | Dropdown with Inter (System) default | PASS |
| 7.4 | Border radius slider | Slider 0–24px with current value label | PASS |
| 7.5 | Launcher size slider | Slider 48–72px with current value label | PASS |
| 7.6 | Launcher icon dropdown | Dropdown with Chat bubble default | PASS |
| 7.7 | Position toggle | Bottom right / Bottom left segmented control | PASS |
| 7.8 | Panel width control | Compact / Standard / Wide segmented control with tooltip | PASS |
| 7.9 | Panel shadow control | None / Subtle / Standard / Heavy segmented control | PASS |
| 7.10 | Behavior section | Greeting message toggle + text input with template variables, Pre-chat form toggle, Sound notifications toggle | PASS |
| 7.11 | Template variables | Clickable chips: FIRST_NAME, LAST_NAME, FULL_NAME, COMPANY | PASS |
| 7.12 | Content section | Header title, Header subtitle, Input placeholder text fields | PASS |
| 7.13 | Agent identity | Agent display name, Agent avatar URL fields | PASS |
| 7.14 | Action buttons | Reset to defaults and "Save draft inputs" buttons at bottom | |
| 7.15 | Section tooltips | (?) icons on Appearance, Panel width, Behavior, Content | PASS |
| 7.16 | Agent avatar upload accepts PNG file | Click upload control → file picker opens → selecting a valid PNG shows preview | |
| 7.17 | Agent avatar rejects non-PNG files | Selecting a non-PNG file (JPG, GIF, SVG, etc.) shows validation error | |
| 7.18 | Agent avatar crop/position control | After upload, a crop UI allows positioning the viewable area to enforce correct aspect ratio | |
| 7.19 | Agent avatar resize | Uploaded image is resized to the correct avatar dimensions after crop | |
| 7.20 | Agent avatar persists on save | After upload + crop, clicking Save persists the avatar; avatar displays correctly in widget preview and on reload | |
| 7.21 | Widget launcher opens chat window | Clicking the launcher button (red circle) in the live preview opens the chat panel | |
| 7.22 | Widget config save succeeds | Modifying any widget setting and clicking "Save draft inputs" → success notification, changes persisted on reload | |

---

### Page 8: Integrations

| # | Test | Expected | Status |
|---|------|----------|--------|
| 8.1 | Page renders with cards | 4 integration cards: Shopify, Zendesk, Mailchimp, Google Analytics | PASS |
| 8.2 | Shopify card (connected) | Logo, description, Deactivate and Disconnect buttons | PASS |
| 8.3 | Coming Soon integrations | Zendesk, Mailchimp, Google Analytics show "Coming Soon" badge and development message | PASS |
| 8.4 | Integration count footer | "1 of 4 integrations active" text at bottom | PASS |
| 8.5 | Tooltips on integration names | (?) icon next to each integration name | PASS |
| 8.6 | Deactivate/Disconnect hover state has no border change | Hovering Deactivate or Disconnect buttons changes background only — border does not become more visible or change color | |

---

### Page 9: Memory & Privacy

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.1 | Memory features render | Customer context (All tiers), Conversation memory (All tiers), Cross-session learning (Professional+) cards | PASS |
| 9.2 | Tier badges | "All tiers" (green), "Professional+" (purple), "Enterprise required" (gray) badges on each feature | PASS |
| 9.3 | Feature toggles | Enabled/Disabled toggles for each feature, state reflects current config | PASS |
| 9.4 | Dedicated model training | Enterprise required card with upgrade banner and pricing ($299/month) | PASS |
| 9.5 | Data retention section | Collapsible "Data retention & privacy" section with tooltip | PASS |
| 9.6 | Retention period dropdown | "1 year" default with dropdown options | PASS |
| 9.7 | Privacy toggles | PII scrubbing, Consent required, Automatic deletion on request — all with descriptions | PASS |
| 9.8 | Save draft inputs button | Red "Save draft inputs" button at bottom of page (no button at top) | |
| 9.9 | Feature tooltips | (?) icon on each feature card and Data retention section | PASS |
| 9.10 | Tier-gated features non-toggleable | Features requiring a higher tier than the tenant's current plan (e.g. "Cross-session learning" requires Professional+) must be visually disabled / greyed out and cannot be toggled | PASS |
| 9.11 | Save draft inputs persists all Memory & Privacy settings | After modifying toggles/sliders and clicking "Save draft inputs", all 8 fields persist correctly on page reload (memory_enabled, pattern_learning_enabled, data_retention_days, consent_collection_enabled, pii_scrubbing, conversation_memory, cross_session_learning, pattern_decay_days) | |

---

### Page 10: Billing & Usage

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.1 | Current plan header | Plan name (Professional), Active badge, tooltip, included/used/remaining counts | PASS |
| 10.2 | Usage metric cards | Conversations used (with progress ring), Pack balance, Current overage, Estimated overage cost — all with tooltips | PASS |
| 10.3 | Daily usage chart | 30-day chart with Total (red) and Billable (blue) lines and legend | PASS |
| 10.4 | Conversation packs | 3 pack options (1K/$29, 5K/$99, 20K/$249) with per-conversation rates and Purchase buttons | PASS |
| 10.5 | Add-on modules | 5 add-on cards (no Priority Support, no White-Label Package) with tier badges, descriptions, pricing, Subscribe/Upgrade buttons | |
| 10.6 | Tier-gated add-ons | Enterprise-only add-ons show "Upgrade to Enterprise" (grayed) instead of Subscribe | PASS |
| 10.7 | Add-on tier badges | All tiers (green), Pro+ (blue), Starter/Pro (blue), Enterprise (gray) badges | PASS |
| 10.8 | Add-on tier badges show required entitlement | Each add-on card displays the minimum entitlement required for activation (All, Starter, Pro, Pro+, Enterprise) regardless of current tier | |
| 10.9 | Subscribe disabled for unavailable add-ons | Add-ons requiring a higher tier than current show the minimum required entitlement on a disabled button instead of "Subscribe" | |
| 10.10 | Tier upgrade path displayed on Billing page | An upgrade section shows Starter → Pro → Pro+ → Enterprise in order of entitlement, with an "Upgrade" option for each higher tier; upgrading changes which add-ons show "Subscribe" vs greyed-out | |

---

## Defect Log

| ID | Page | Defect | Session | Fix | Regression Test |
|----|------|--------|---------|-----|-----------------|
| D1 | Dashboard | Chart shows data outside selected period | S17 | Client-side period filter added | 1.6 |
| D2 | Dashboard | Tooltip doc links point to page root, not anchors | S17 | Per-metric anchors added | 1.3, 1.4 |
| D3 | Inbox | Search result click doesn't update detail panel | S17 | Fallback to SearchResult object | 2.7 |
| D4 | Inbox | Message content search returns no results when filter tab active | S17 | Search now ignores status filter (always searches all) | 2.6 |
| D5 | Inbox | Escalation has no team member/category selection | S17 | Feature gap (logged) | — |
| D6 | Inbox | Esc filter count doesn't update after escalation | S17 | 500ms delay before refetch (Cosmos read-after-write) | 2.9 |
| D7 | Dashboard | Conversation volume chart shows phantom historical data before tenant existed | S18 | Deferred to batch fix | 1.15 |
| D8 | Dashboard | Chart X-axis doesn't span full selected period (e.g. 90d shows ~14d) | S18 | Deferred to batch fix | 1.16 |
| D9 | Sidebar | Config badge shows "Not configured" despite tenant having active conversations | S18 | Deferred to batch fix | 1.17 |
| D10 | Sidebar | Badge label "Not configured" is not a valid state — should be "Active" or "Pending" only | S18 | Deferred to batch fix | 1.14 |
| D11 | Sidebar | Roll back button visible when no previous activation exists to restore | S18 | Deferred to batch fix | 1.18 |
| D12 | Agent Config | Save fails: "'dict' object has no attribute 'model_dump'" | S18 | BLOCKING — deferred to batch fix | 4.8 |
| D13 | Agent Config | Discard button non-functional | S18 | Deferred to batch fix | 4.8 |
| D14 | Agent Config | "Save failed" error banner X close button non-functional | S18 | Deferred to batch fix | — |
| D15 | Knowledge Base | Created article shows "--" for Category and Status in article table; filters return no results | S18 | Deferred to batch fix | 5.9, 5.10 |
| D16 | Knowledge Base | Creating/saving a KB article does not change config state to "Pending" | S18 | Deferred to batch fix | 5.11 |
| D17 | Knowledge Base | Archived article has no visual distinction — still appears in list identically | S18 | Deferred to batch fix | 5.12 |
| D18 | Knowledge Base | Freshness shows "--" for newly created article instead of "Fresh" | S18 | Deferred to batch fix | 5.13 |
| D19 | Knowledge Base | No way to restore an archived article | S18 | Deferred to batch fix | 5.14 |
| D20 | Quick Actions | Creating a quick action does not change config state to "Pending" | S18 | Deferred to batch fix (same pattern as D16) | 6.7 |
| D21 | Quick Actions | Auto-open toggle on page assignments is non-functional | S18 | Deferred to batch fix | 6.8 |
| D22 | Widget Config | Agent avatar: replace URL input with PNG upload + validation + resize + aspect-ratio crop | S18 | Design change — deferred to batch fix | 7.16–7.20 |
| D23 | Widget Config | Widget launcher click does not open chat window in live preview | S18 | Deferred to batch fix | 7.21 |
| D24 | Widget Config | Save fails with same model_dump error as D12 | S18 | Same root cause as D12 — deferred to batch fix | 7.22 |
| D25 | Integrations | Deactivate and Disconnect buttons acquire incorrect white border on hover | S18 | Deferred to batch fix | 8.6 |
| D26 | Memory & Privacy | Cross-session learning toggle appears non-gated — actually PASS: "Professional+" means Professional and above; toggle IS correctly disabled for Starter tier | S18 | Not a defect (tier gate works correctly) | 9.10 |
| D27 | Memory & Privacy | Save changes silently drops 6 of 8 fields — frontend field names don't match backend schema | S18 | Deferred to batch fix | 9.11 |
| D28 | Billing & Usage | Add-on tier badges use green/gray for met/unmet instead of always showing the required entitlement level | S18 | Design change — deferred to batch fix | 10.8 |
| D29 | Billing & Usage | Subscribe button shown for all tier-met add-ons without indicating required entitlement on unavailable ones | S18 | Deferred to batch fix | 10.9 |
| D30 | Billing & Usage | No visible tier upgrade path on Billing page — admin cannot view/compare Starter → Pro → Pro+ → Enterprise and upgrade inline | S18 | Design change — deferred to batch fix | 10.10 |
| D31 | Billing & Usage | Priority Support add-on shown but not available at launch — remove from add-on list, defer to post-launch | S18 | Deferred to batch fix | 10.5 |
| D32 | Billing & Usage | White-Label Package add-on shown but not available at launch — remove from add-on list, defer to post-launch | S18 | Deferred to batch fix | 10.5 |
| D33 | Dashboard | Phantom conversation data from pre-draft seed — Cosmos still contains demo conversations from earlier seed run; tenant has never had real traffic | S19 | Fixed in v1.29.0 — cleanup_demo_data.py purged 265 conversations, 2 profiles, 12 vectors, 1 usage counter; prefs patched to draft | 1.15 |
| D34 | Sidebar | Config badge shows "Active" (green) when mandatory fields are missing — badge ignores `is_configured` flag from backend; `isActivated` check treats version>0 as activated even in DRAFT state | S19 | Fixed in v1.29.0 — three-state badge uses is_configured; isActivated derived from activation-status polling | 1.14, 1.17 |
| D35 | Sidebar | Activate button should pre-validate and immediately show all missing mandatory fields across Agent Config, Knowledge Base, Quick Actions, and Widget Config — instead of requiring two-step dialog flow | S19 | Fixed in v1.29.0 — new /api/config/draft/preflight endpoint; ActivationDialog shows hard_errors + warnings on open | — |
| D36 | Dashboard | Avg response time shows 2.3s when totalConversations=0 — should be 0 | S21 | Fixed — admin_analytics_api.py default changed from 2.3 to 0; repository.py empty-result fallback now includes avg_response_time=0 | 1.19 |
| D37 | Dashboard | Customer satisfaction shows 4.2/5 when totalConversations=0 — should be 0 | S21 | Fixed — admin_analytics_api.py default changed from 4.2 to 0; repository.py empty-result fallback now includes customer_satisfaction=0 | 1.20 |
| D38 | Header | Tier badge shows lowercase "professional" — should be "Professional" | S21 | Fixed — TIER_BADGE_LABELS now uses full capitalized names; badge renders label instead of raw tier enum | 0.2 |
| D39 | Header | "Inactive" badge is redundant with sidebar "Pending" — removed | S21 | Fixed — badge element removed from StandaloneLayout.tsx | 0.2 |
| D40 | Agent Config | "Save changes" and "Discard" at page top conflict with sidebar Activate/Discard/Roll back state model | S21 | Fixed — per-page Discard removed; "Save changes" renamed to "Save draft inputs" and moved to page bottom across all CONFIGURATION pages | 4.8 |
| D41 | Agent Config | Brand voice not mandatory — should be required for activation | S21 | Fixed — frontend `required` attribute added; backend preflight promoted brand_voice from warning to hard_error; is_configured check now includes brand_voice | 0.15, 4.1 |
| D42 | Agent Config | Language section shows 8 languages as all available — only English is currently supported; Spanish/French coming soon, others planned | S21 | Fixed — Primary language: English only; Supported languages: English, Spanish/French (coming soon), 5 others (planned, disabled) | 4.6 |
| D43 | Dashboard | Dashboard shows 42 stale demo conversations after re-seed — `seed_tenant.py` was previously run with `--demo` and stale data remained because post-seed Key Vault update was not documented | S21 | Procedure defect: (1) Re-seeded without `--demo` to clear stale conversations; (2) Added POST-SEED STEPS to `seed_tenant.py` for mandatory Key Vault update + revision restart; (3) Added pre-flight check to UI test procedure; (4) Added pre-flight assertion: Dashboard must show 0 conversations for initial state | Pre-flight, 1.19, 1.20 |
| D44 | Widget / Activation | Widget creates phantom conversation shells (54 empty conversations with 0 messages) when tenant has never activated — conversation creation endpoint has no activation gate; activation control has no "Deactivate" disposition for active-with-no-changes state | S22 | (1) Backend gate: `POST /api/chat/conversations` returns 403 when `is_active=false`; (2) New `is_active` field on activation-status; (3) Deactivate action + confirmation dialog; (4) Three-state sidebar badge (Active/Pending/Inactive); (5) Activation control three-disposition model (red/yellow/green) | 0.7, 0.11, 0.16, 0.17, 0A.1–0A.18, 1.14 |

---

## Failure Classification

Per the Repeatable Procedures spec (Section 3):

- **Procedure defect:** A test step is wrong, missing, or ambiguous → fix the procedure first
- **Environment transient:** Cosmos timeout, browser disconnection, deploy lag → retry, don't modify procedure

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
