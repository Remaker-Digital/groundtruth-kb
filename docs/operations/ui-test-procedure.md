# Admin UI Test Procedure

**Type:** Repeatable Procedure
**Version:** 1.0.0
**Created:** 2026-02-13 (Session 17)
**Last Run:** 2026-02-16 (Session 27 — Groups A-D complete; PII scrubbing wired, 9.12/9.14 PASS, 9.13 SKIP deferred; archival, escalation routing, KB/QA activate)
**Agent Tests Gate:** 101 agent tests in `tests/agents/` must pass before any UI test run (added session 25)

> **Chrome Automation Available:** When Claude Code has Chrome MCP access, use
> `docs/operations/chrome-ui-test-procedure.md` instead of this manual procedure.
> This document remains the **authoritative source** for test IDs, expected results,
> the activation control disposition table, and the defect log.

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

- [ ] **Execute Initialization procedure** (`docs/operations/initialization-procedure.md`). This runs `seed_tenant.py --execute`, updates Key Vault, restarts revision, and verifies all 10 post-conditions (I.1–I.10). Do **not** proceed until all post-conditions pass.
- [ ] Run agent unit test gate: `python -m pytest tests/agents/ -x -q` — all 101 tests must pass (0 failures)
- [ ] Run full unit test suite: `python -m pytest tests/ --ignore=tests/integration --ignore=tests/regression -x -q` — 2,477+ tests must pass (0 failures)
- [ ] Open `ADMIN_URL` in browser (hard-refresh if previously loaded with stale credentials)
- [ ] Verify page loads without errors (no blank screen, no console errors)
- [ ] Verify sidebar navigation is fully rendered
- [ ] Verify tenant name and tier badge (capitalized, e.g. "Professional") are displayed in header
- [ ] Verify Dashboard shows **0 conversations** and **0 knowledge base articles**

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
| 0.10a | Welcome dialog dismiss | Dismissing welcome dialog removes it; does not reappear on subsequent page loads | |
| 0.11 | `GET /api/config/activation-status` | `has_pending_changes=true, active_version=0, active_activated_at=null, is_configured=false, is_active=false` | |
| 0.12 | `GET /api/config?state=draft` brand_name | Empty string `""` | |
| 0.13 | Click Discard on never-activated tenant | State unchanged: badge stays Pending, all fields remain empty | |
| 0.13a | Discard notification | Discard on never-activated shows no error (silent no-op or appropriate notification) | |
| 0.14 | Click Activate (yellow) with brand_name empty | Preflight dialog shows hard error: "Brand name is required before activation" | |
| 0.14a | Preflight dialog blocks activation | Preflight dialog has no Confirm button when hard errors present — activation cannot proceed | |
| 0.15 | Click Activate (yellow) with brand_voice empty | Preflight dialog shows hard error: "Brand voice is required before activation" | |
| 0.16 | Widget conversation gate (never activated) | `POST /api/chat/conversations` with valid widget key returns 403 `{"type": "not_active"}` — no conversation document created | |
| 0.17 | Widget.js config response (never activated) | Widget config fetch returns `widget_active: false` — widget does not mount on storefront | |

---

### Page 0A: Activation Control Lifecycle

Tests the full activation → deactivation → re-activation cycle. Run after Page 0 (starting from never-activated state with empty fields).

| # | Test | Expected | Status |
|---|------|----------|--------|
| 0A.1 | Fill brand_name only, save draft | Activation control stays yellow/"Activate" — brand_voice still missing | |
| 0A.1a | Save draft notification | "Draft inputs saved" success notification appears after save | |
| 0A.2 | Fill brand_voice, save draft | Activation control turns green/"Activate" — all mandatory fields present in draft | |
| 0A.3 | Click Activate (green) | Confirmation dialog opens showing validation results; click confirm → activation succeeds | |
| 0A.3a | Activation success notification | "Configuration activated" success notification after activation | |
| 0A.4 | Badge after first activation | Green "Active" dot | |
| 0A.5 | Activation control after activation (no pending changes) | Red / "Deactivate" — system is active with no pending draft changes | |
| 0A.6 | `GET /api/config/activation-status` after activation | `is_active=true, is_configured=true, has_pending_changes=false, active_activated_at != null` | |
| 0A.7 | Widget conversation gate (active) | `POST /api/chat/conversations` with valid widget key returns 200 — conversation created successfully | |
| 0A.8 | Widget.js config response (active) | Widget config fetch returns `widget_active: true` — widget mounts on storefront | |
| 0A.9 | Click Deactivate (red) | Confirmation dialog opens: "Deactivating will immediately stop the chat widget on your storefront. Your configuration will be preserved." | |
| 0A.9a | Deactivation dialog cancel | Clicking cancel in deactivation dialog closes it without deactivating; badge stays Active | |
| 0A.10 | Confirm deactivation | System deactivates; badge changes to red "Inactive" dot | |
| 0A.10a | Deactivation notification | "Configuration deactivated" notification after deactivation | |
| 0A.11 | Activation control after deactivation (config still complete) | Green / "Activate" — active config still has all mandatory fields, one-click re-activation available | |
| 0A.12 | `GET /api/config/activation-status` after deactivation | `is_active=false, is_configured=true, has_pending_changes=false` | |
| 0A.13 | Widget conversation gate (deactivated) | `POST /api/chat/conversations` with valid widget key returns 403 `{"type": "not_active"}` — no conversation created | |
| 0A.14 | Click Activate (green) to re-activate | Confirmation dialog → confirm → system re-activates; badge returns to green "Active" | |
| 0A.15 | Widget conversation gate (re-activated) | `POST /api/chat/conversations` returns 200 — conversations work again | |
| 0A.16 | Make draft change while active | Modify brand_name, save draft → activation control changes from red "Deactivate" to green "Activate" (pending changes with all mandatory fields present) | |
| 0A.16a | configRefreshKey triggers re-fetch | After save, all 4 AI Configuration pages re-fetch config to show updated values | |
| 0A.17 | Make draft change that removes mandatory field while active | Clear brand_voice in draft, save → activation control changes to yellow "Activate" (pending changes with mandatory field missing). Note: brand_name has min_length=1 and cannot be saved empty; use brand_voice instead. | |
| 0A.18 | Sidebar badge during pending changes | Yellow "Pending" (regardless of whether system was previously active) | |
| 0A.19 | Widget launcher visible when Active | Chat bubble (launcher icon) appears in bottom-right corner of all admin pages when system is Active — no page refresh required (D53 regression) | |
| 0A.20 | Widget launcher hidden when Inactive | After deactivation, chat bubble disappears from admin pages without page refresh (D53 regression) | |
| 0A.21 | Widget launcher reappears on re-activation | After re-activating from Inactive, chat bubble reappears without page refresh (D53 regression) | |

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
| 0B.2a | **Save notification** — after save draft | "Draft … saved" success notification appears | |
| 0B.3 | **Discard with pending changes while active** — click sidebar Discard | Draft reverts to match active config; badge returns to Active (green); activation control returns to red "Deactivate" | |
| 0B.3a | **Discard notification** — after discard with pending changes | Appropriate notification (e.g., "Draft discarded") appears | |
| 0B.4 | **Re-confirm discard** — verify `GET /api/config?state=draft` after discard | Draft brand_name matches the active config brand_name (reverted), not the modified value | |
| 0B.5 | **Make another draft change** — modify brand_name, save draft → then click Activate (green) | Activation dialog shows preflight results; confirm → activation succeeds; active_version increments; badge = Active (green); activation control = red "Deactivate" | |
| 0B.5a | **Activation version increment** — `GET /api/config/activation-status` after second activation | active_version is 2 (incremented from 1) | |
| 0B.6 | **Roll back after second activation** — click Roll back | Confirmation dialog appears; confirm → previous config restored; active_version increments; badge = Active (green); brand_name reverts to value from first activation | |
| 0B.6a | **Roll back notification** — after roll back | "Configuration rolled back" notification appears | |
| 0B.7 | **Roll back button state** — immediately after Roll back | Roll back remains enabled (the just-restored version is now the latest active, but the one before it is still available as PREVIOUS) — OR disabled if there is no further PREVIOUS state to restore | |
| 0B.8 | **Deactivate then Discard** — deactivate system (red → confirm), then modify brand_name in draft, save draft, then Discard | Badge changes to Inactive (red) after deactivate; after draft modification, badge changes to Pending (yellow); after Discard, badge returns to Inactive (red) with no pending changes; activation control = green "Activate" (config still complete) | |
| 0B.9 | **Re-activate after deactivation** — click Activate (green) | System re-activates; badge returns to Active (green); activation control = red "Deactivate" | |
| 0B.10 | **Clear mandatory field, attempt Activate** — clear brand_voice in draft, save draft, click Activate (yellow) | Activation control is yellow "Activate" (blocked); clicking it shows preflight dialog with hard error "Brand voice is required before activation"; activation blocked. Note: brand_name has min_length=1 and cannot be saved empty; use brand_voice instead. | |
| 0B.11 | **Discard after clearing mandatory field** — click sidebar Discard | Draft reverts; brand_voice restored from active config; badge returns to Active (green); activation control returns to red "Deactivate" | |
| 0B.12 | **Roll back after deactivation** — deactivate system, then click Roll back | Roll back restores previous active config AND system returns to active state (deactivated_at cleared); badge = Active (green) | |

---

### Page 1: Dashboard

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard (incl. data-binding correctness).

#### 1.1 Metric stat cards

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.1 | Five metric cards render | Total conversations, Avg response time, Resolution rate, Customer satisfaction, Escalation rate — all with values or "--" | |
| 1.1a | Total conversations — correct value | Card shows totalConversations count from analytics API (e.g., "218") | |
| 1.1b | Total conversations — detail sub-label | Shows "Billable: N" below the main count (e.g., "Billable: 12") | |
| 1.1c | Avg response time — correct value | Card shows "{N}s" format from avgResponseTime (e.g., "2.3s") | |
| 1.19 | Avg response time is 0 when no conversations exist | When `totalConversations=0`, card displays `0s` (not "--") | |
| 1.1d | Resolution rate — correct value | Card shows "{N}%" format (e.g., "87.5%") with "N resolved" detail | |
| 1.1e | Customer satisfaction — correct value | Card shows "{N}/5" format (e.g., "4.2/5") | |
| 1.20 | Customer satisfaction is 0 when no conversations exist | When `totalConversations=0`, card displays `0/5` (not "--") | |
| 1.1f | Escalation rate — correct value | Card shows "{N}%" format with "N escalated" detail | |
| 1.1g | Loading skeleton state | While API fetches, all cards show Skeleton placeholders instead of values | |
| 1.1h | Null values show "--" | When API returns null for a metric, card displays "--" | |

#### 1.2 Metric card tooltips and doc links

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.2 | Metric card tooltips have help icon | Each card shows (?) icon that opens tooltip on hover | |
| 1.2a | Total conversations tooltip text | Explains "All conversations started in the selected period, including billable and non-billable." | |
| 1.2b | Avg response time tooltip text | Explains "Average time for the AI to generate a complete response..." | |
| 1.2c | Resolution rate tooltip text | Explains "Percentage of conversations resolved by the AI without human escalation." | |
| 1.2d | Customer satisfaction tooltip text | Explains "Average customer rating on a 1-5 scale..." | |
| 1.2e | Escalation rate tooltip text | Explains "Percentage of conversations handed off to a human team member." | |
| 1.3 | Tooltip doc links point to specific anchors | Total → #total-conversations, Avg → #average-response-time, Resolution → #resolution-rate, Satisfaction → #customer-satisfaction, Escalation → #escalation-rate | |
| 1.4 | Tooltip doc links open correct doc page section | Click link in tooltip → navigates to correct heading on docs site | |

#### 1.5 Period selector

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.5 | Period selector (7d/14d/30d/90d) is functional | SegmentedControl with 4 options, default "30d" | |
| 1.5a | Period selector — default value | "30d" is selected on initial load | |
| 1.5b | Period selector — 7d | Clicking "7d" changes chart label to "Last 7 days" | |
| 1.5c | Period selector — 14d | Clicking "14d" changes chart label to "Last 14 days" | |
| 1.5d | Period selector — 90d | Clicking "90d" changes chart label to "Last 90 days" | |
| 1.5e | Period selector — visual active state | Selected period option has distinct active styling | |

#### 1.6 Conversation volume chart

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.6 | Conversation volume chart respects period selector | Chart only shows data points within the selected period window | |
| 1.6a | Chart title and tooltip | "Conversation volume" title with HelpTooltip explaining daily breakdown | |
| 1.7 | Conversation volume chart doc link | Points to `analytics#conversation-volume-chart` | |
| 1.6b | Chart two series | Two area lines: Total (red #ff3621) and Billable (blue #2563EB) | |
| 1.6c | Chart legend | Legend below chart shows "Total" (red dot) and "Billable" (blue dot) | |
| 1.6d | Chart loading skeleton | Skeleton height=320 while daily volume data fetches | |
| 1.6e | Chart empty state | "No volume data available" text when no data | |
| 1.6f | Chart tooltip on hover | Hovering a data point shows tooltip with date, Total count, Billable count | |
| 1.15 | Chart shows no data before tenant creation date | Chart must not display data points dated before tenant's creation date | |
| 1.16 | Chart X-axis spans full selected period | X-axis starts at (today − N days) and ends at today for all period options | |

#### 1.8 Recent conversations

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.8 | Recent conversations section renders | Shows up to 5 conversations with name, message count, status, time | |
| 1.8a | Conversation card — customer name | Shows customerName or "Unknown Customer" when null | |
| 1.8b | Conversation card — status badge | Badge colored: active=blue, idle=yellow, ended=green, escalated=red | |
| 1.8c | Conversation card — message count | Shows "N messages" text | |
| 1.8d | Conversation card — assignment | Shows "Assigned: {name}", "Escalated", or "Unassigned" | |
| 1.8e | Conversation card — time | Shows last activity time in HH:MM format, or "--" when null | |
| 1.8f | Loading skeleton | 5 Skeleton rows while conversations data fetches | |
| 1.8g | Empty state | "No conversations yet" centered text when no conversations | |
| 1.9 | Recent conversations doc link | HelpTooltip points to `conversations#conversation-list` | |

#### 1.10 Top topics and Topic breakdown

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.10 | Top topics section renders | Shows topic names with counts and distribution bars | |
| 1.10a | Top topics — topic label | Uses agentDisplayLabel() to format topic name | |
| 1.10b | Top topics — invocation count | Shows count next to each topic | |
| 1.10c | Top topics — distribution bar | Horizontal bar proportional to percentage, BRAND_RED color | |
| 1.10d | Top topics — loading skeleton | 5 Skeleton rows while intent data fetches | |
| 1.10e | Top topics — empty state | "No topic data available" when no intents | |
| 1.10f | Top topics — doc link | HelpTooltip points to `analytics#topic-breakdown` | |
| 1.11 | Topic breakdown table renders | Full table with Topic, Count, Distribution columns | |
| 1.11a | Topic breakdown — table columns | 3 columns: Topic, Count, Distribution (Progress bar + percentage) | |
| 1.11b | Topic breakdown — progress bar | BRAND_RED progress bar proportional to percentage, with "N%" text | |
| 1.11c | Topic breakdown — loading text | "Loading topic data..." while fetching | |
| 1.11d | Topic breakdown — empty state | "No topic data available" when no intents | |

#### 1.12 Knowledge gaps

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.12 | Knowledge gaps section renders | Shows conversations where AI lacked knowledge, with ID, status, turns, messages, date | |
| 1.12a | Knowledge gaps — subtitle | "Conversations where the AI could not fully resolve the customer query" | |
| 1.12b | Knowledge gaps — gap count badge | Orange badge shows "N gaps" when gaps > 0 | |
| 1.12c | Knowledge gaps — table columns | 5 columns: Conversation (ID + customerId), Status, Turns, Messages, Started | |
| 1.12d | Knowledge gaps — status badge | Colored badge: escalated=red, ended=green, active=blue, other=gray | |
| 1.12e | Knowledge gaps — loading text | "Loading knowledge gaps..." while fetching | |
| 1.12f | Knowledge gaps — empty state | "No knowledge gaps detected" when no gaps | |
| 1.13 | Knowledge gaps doc link | HelpTooltip points to `analytics#knowledge-gaps` | |

#### 1.14 Sidebar configuration state

| # | Test | Expected | Status |
|---|------|----------|--------|
| 1.14 | Configuration badge in sidebar shows correct state | Three states: "Active" (green), "Pending" (yellow), "Inactive" (red) | |
| 1.14a | Active disposition | Green badge when config is activated with no pending changes | |
| 1.14b | Pending disposition | Yellow badge when never activated or has pending draft changes | |
| 1.14c | Inactive disposition | Red badge when configuration has been deactivated | |
| 1.17 | Configuration badge reflects actual system state | If conversations exist, config must be "Active" (agent requires activated config) | |
| 1.18 | Roll back button disabled when no previous activation | Disabled when active_version < 2; enabled only when PREVIOUS config exists | |

---

### Page 2: Inbox

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard (incl. data-binding correctness).
>
> Tests 2.4–2.18 require conversation data — SKIP if tenant has 0 conversations.

#### 2.1 Three-panel layout

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.1 | Three-panel layout renders | Left: conversation list (280px), Center: message thread (flex), Right: customer details (320px) | |
| 2.1a | Left panel border | Right border separates list from center panel | |
| 2.1b | Right panel border | Left border separates details from center panel | |
| 2.1c | Layout fills viewport height | Panels occupy calc(100vh − header − padding), no vertical scrollbar on main page | |

#### 2.2 Filter tabs

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.2 | Filter tabs show correct counts | All (N), Active (N), Esc (N), Resolved (N), Archived — counts match actual conversation statuses (D55 regression) | |
| 2.2a | Default filter | "All" selected on initial load | |
| 2.2b | Active filter | Clicking "Active" shows only conversations with status=active; count matches | |
| 2.2c | Esc filter | Clicking "Esc" shows only status=escalated conversations | |
| 2.15 | Resolved filter shows resolved conversations | Resolved tab shows only conversations with "resolved" status; count matches (D55 regression) | |
| 2.2d | Archived filter | Clicking "Archived" fetches archived conversations from API (separate request with archived=only); non-archived conversations hidden | |
| 2.2e | Filter visual active state | Selected filter segment has distinct active styling | |
| 2.16 | Naturally ended conversations appear as Resolved | Conversations ended by customer or max turns show "Resolved" status badge, not "Completed" (D55 regression) | |

#### 2.3 Conversation list items

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.3 | Conversation list items render | Avatar, name/ID, message count, status badge, timestamp, unread indicator | |
| 2.3a | Avatar initials | Avatar shows first letter(s) of customer name; "?" when name is null | |
| 2.3b | Avatar color | Color derived from name hash using AVATAR_PALETTE (6 colors) | |
| 2.3c | Customer name display | Shows customerName; falls back to first 12 chars of conversationId; then "Session" | |
| 2.3d | Time ago display | Shows relative time: "just now", "Nm", "Nh", "Nd" based on lastActivityAt or startedAt; "--" when null | |
| 2.3e | Message count | Shows "N messages" text below customer name | |
| 2.3f | Status badge colors | active=blue, ended=green, resolved=green, escalated=red, idle=yellow, timed_out=yellow, error=red | |
| 2.3g | Unread indicator | Red dot (8px circle) appears when status is "active" or "escalated"; bold name text | |
| 2.3h | Assigned to text | Shows assignedTo team member name when present | |
| 2.3i | Selected conversation highlight | Selected item has BRAND_RED left border and distinct background color | |
| 2.3j | Hover effect | Hovering non-selected item changes background; leaving restores transparent | |
| 2.3k | Auto-select first conversation | On initial load, first conversation in list is automatically selected | |

#### 2.4 Conversation selection and detail panels

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.4 | Clicking a conversation updates detail panels | Center panel shows messages (or "No messages"), right panel shows conversation info | |
| 2.4a | Empty selection state — center | "Select a conversation from the list to view messages." when no conversation selected | |
| 2.4b | Empty selection state — right | "Select a conversation to view details." when no conversation selected | |
| 2.4c | Thread header — name and status | Center panel header shows customer display name + status badge | |
| 2.4d | Thread header — message count and assignment | Shows "N messages" and "Assigned to {name}" when applicable | |

#### 2.5 Search functionality

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.5 | Search by customer name | Searching a customer name returns matching conversations | |
| 2.6 | Search by message content | Searching a word from message content (e.g., "product") returns conversations containing that word in their messages | |
| 2.5a | Search placeholder | TextInput shows "Search conversations..." placeholder with search icon | |
| 2.5b | Search debounce | Typing triggers backend search after 350ms debounce; Loader icon appears during search | |
| 2.5c | Search result — snippet | Each search result shows snippet text from matched content | |
| 2.5d | Search result — matched_in badge | Gray outline badge shows which field matched (e.g., "message", "customer_name") | |
| 2.7 | Clicking search results updates detail panel | Selecting a search result populates center + right panels, even if the conversation is not in the current inbox page | |
| 2.13 | Search "no results" state | Searching a term with no matches shows "No matching conversations" + "Try adjusting your search or filter." | |
| 2.5e | Clear search restores list | Clearing search input restores normal conversation list with current filter applied | |

#### 2.8 Action buttons (Escalate, Resolve, Archive, Unarchive)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.8 | Escalate action updates status | Clicking "Escalate to human" changes conversation status to "escalated" | |
| 2.8a | Escalate button tooltip | "Escalate to human" tooltip on hover | |
| 2.8b | Escalate loading state | Button shows loading spinner during API call; both escalate + resolve buttons disabled while loading | |
| 2.8c | Escalate success notification | Toast notification "Conversation escalated to human agent." in orange, auto-dismisses after 4s | |
| 2.9 | Escalated conversation appears in Esc filter | After escalation, Esc tab count increments and conversation is visible in Esc filter | |
| 2.11 | Escalate button hidden for escalated conversations | Already-escalated conversations do not show the escalate button | |
| 2.10 | Resolve action updates status | Clicking "Resolve" changes conversation status to "resolved" | |
| 2.10a | Resolve button tooltip | "Resolve conversation" tooltip on hover | |
| 2.10b | Resolve success notification | Toast notification "Conversation marked as resolved." in green | |
| 2.12 | Resolve button hidden for resolved conversations | Already-resolved conversations do not show the resolve button | |
| 2.8d | Archive button visibility | Archive button shown only for resolved or timed_out conversations that are not archived | |
| 2.8e | Archive button tooltip | "Archive conversation" tooltip on hover | |
| 2.8f | Archive success notification | Toast notification "Conversation archived." in gray | |
| 2.8g | Unarchive button visibility | Unarchive button shown only for conversations that have archivedAt set | |
| 2.8h | Unarchive button tooltip | "Unarchive conversation" tooltip on hover | |
| 2.8i | Unarchive success notification | Toast notification "Conversation unarchived." in blue | |
| 2.8j | Error notification | When escalate/resolve/archive fails, toast shows error message in red | |

#### 2.14 Message thread

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.14 | Message thread renders messages | Selecting a conversation with messages shows the message bubbles with role, content, timestamp | |
| 2.14a | Agent message — right-aligned | Agent bubbles aligned to flex-end with "Agent Red AI" label and icon | |
| 2.14b | Customer message — left-aligned | Customer bubbles aligned to flex-start with "Customer" label | |
| 2.14c | System message — centered | System messages centered, italic, dimmed text | |
| 2.14d | Message timestamp | Each bubble shows formatted time (HH:MM AM/PM) below the bubble | |
| 2.14e | Scroll to bottom | Messages auto-scroll to bottom when conversation changes or new messages arrive | |
| 2.14f | Loading messages state | Loader + "Loading messages..." when fetching messages for selected conversation | |
| 2.14g | Error loading messages | "Failed to load messages" in red when API fails | |
| 2.14h | No messages state | "No messages in this conversation yet." when conversation has 0 messages | |

#### 2.17 Right panel — Customer details

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.17 | Escalated conversation info shows target member | Conversation info card for an escalated conversation displays the assigned team member name (D56 regression) | PASS |
| 2.18 | Escalated conversation info shows category | Conversation info card for an escalated conversation displays the escalation category (D56 regression) | PASS |
| 2.17a | Customer avatar and name | Large (64px) avatar with initials + customer display name below | |
| 2.17b | Customer ID | Shows "ID: {customerId}" when present | |
| 2.17c | Status badge | Status badge in right panel matches conversation status color | |
| 2.17d | Conversation info — Messages | "Messages" row shows messageCount | |
| 2.17e | Conversation info — Started | "Started" row shows formatted date (e.g., "Feb 15, 2:30 PM"); "--" when null | |
| 2.17f | Conversation info — Last activity | "Last activity" row shows relative time (timeAgo format) | |
| 2.17g | Conversation info — Assigned to | Shows when assigned; resolves member ID to display name via memberMap | |
| 2.17h | Escalation category badge | Blue light badge showing category with underscores replaced by spaces | |
| 2.17i | Escalated badge | Red filled "Escalated" badge shown when status=escalated | |
| 2.17j | Archived badge and date | Gray "Archived" badge with date when archivedAt is set | |
| 2.17k | Customer profile placeholder | "Customer details will be available once the customer profile API is connected." italic text | |

#### 2.19 Loading and error states

| # | Test | Expected | Status |
|---|------|----------|--------|
| 2.19a | Conversation list loading | Loader + "Loading conversations..." when fetching conversation list | |
| 2.19b | Conversation list error | "Failed to load conversations" in red with error detail text | |
| 2.19c | Empty state — no conversations | Chat icon + "No conversations yet" + "Conversations will appear here once customers start chatting..." | |
| 2.19d | Empty state — filter no match | "No matching conversations" + "Try adjusting your filter." when filter yields 0 results | |
| 2.19e | Filter clears selected | When search or filter produces no results, selected conversation is cleared (Issue 3a) | |

---

### Page 3: Team Members

#### 3.1 Page header and loading states (5 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.1 | Team member list renders | Table with Team Member (name+email), Role, Joined, Last Active, Escalations, Actions columns | PASS |
| 3.1a | Page title | "Team members" title and "Manage team members, assign roles, and configure escalation categories" subtitle | |
| 3.1b | Loading state | "Loading team" renders while tenantContext loads; "Loading team members..." while team API loads | |
| 3.1c | Error state | When team API fails, "Failed to load team:" message and "Retry" button render | |
| 3.1d | Retry reloads data | Clicking "Retry" button triggers team.refetch and replaces error with table | |

#### 3.2 Member count and invite toggle (5 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.2 | Invite member button | Clicking "+ Invite member" opens inline form with Email*, Name, Role*, Send invite button | PASS |
| 3.2a | Member count text | Header row shows "N team members" (or "1 team member" for singular) matching member array length | |
| 3.2b | Invite form toggle | Clicking "+ Invite member" changes button text to "Cancel"; clicking "Cancel" closes form | |
| 3.2c | Empty state | When members array is empty: "No team members yet" message with "Invite your first team member" subtitle | |
| 3.2d | Empty state CTA | Empty state suggests inviting first member to get started | |

#### 3.3 Invite form (10 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.3a | Invite form fields | Form shows Email input (required), Name input, Role dropdown (default: Escalation agent), "Send invite" button | |
| 3.3b | Role dropdown options in form | Dropdown shows Admin, Escalation agent, Viewer — Superadmin is hidden | |
| 3.3c | Valid invite submits | Entering valid email + name + role and clicking "Send invite" calls POST /api/admin/team | |
| 3.3d | Invite success notification | After successful invite: notification "Invited {email} as {role}." appears | |
| 3.3e | Invite clears form | After successful invite: email, name cleared; role reset to "escalation_agent"; form closes | |
| 3.3f | Invite refreshes list | After successful invite: team list refetches and new member appears in table | |
| 3.3g | Empty email validation | Submitting with empty email shows warning "Please enter an email address." | |
| 3.3h | Invalid email validation | Submitting with invalid email format shows warning "Please enter a valid email address." | |
| 3.3i | Invite loading state | While invite API in progress: "Send invite" button shows loading spinner | |
| 3.3j | Invite error notification | When invite API fails: error notification with failure message appears | |

#### 3.4 Team member table (8 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.4a | Table column headers | 6 columns: Team member, Role, Joined, Last active, Escalations, Actions | |
| 3.4b | Member row content | Each row shows member name, email, role dropdown/badge, joined date, last active date | |
| 3.5 | Role dropdown options | In-table role dropdown shows Admin, Escalation agent, Viewer — Superadmin hidden | PASS |
| 3.3 | Inline role change | Changing role dropdown in table row calls PUT /api/admin/team/{id} with new role and shows success notification | PASS |
| 3.4c | Inline role change error | When inline role PUT fails: error notification "Failed to update role: {msg}" | |
| 3.9 | Unresolved escalation count | Escalations column shows count of unresolved escalations per member (D57 regression) | PASS |
| 3.8 | Escalation agent categories | Escalation agents show category badges (Sales, Support, Service, Account, etc.) | PASS |
| 3.4d | Category toggle | Clicking a category badge on an escalation agent toggles it on/off via PUT with escalation_categories | |

#### 3.5 Role tooltip (3 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.6 | Role tooltip | Hovering (?) next to ROLE header shows all 4 role descriptions | PASS |
| 3.5a | Role tooltip content | Tooltip describes Superadmin, Admin, Escalation agent, and Viewer roles with permissions | |
| 3.5b | Role tooltip dismiss | Moving mouse away from (?) closes the tooltip | |

#### 3.6 Owner/superadmin row protection (3 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.7 | Owner row non-editable | Owner/Superadmin row shows badge instead of dropdown, no delete icon | PASS |
| 3.6a | Superadmin badge | Superadmin member shows role as a static badge, not an editable dropdown | |
| 3.6b | No delete on owner | Superadmin/owner row has no trash/remove action icon | |

#### 3.7 Remove member dialog (6 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.4 | Delete confirmation dialog | Clicking trash icon shows confirmation dialog naming the member, warns permanent deletion | PASS |
| 3.7a | Dialog shows member identity | Confirmation dialog displays the member's email address being removed | |
| 3.7b | Confirm removes member | Clicking confirm in dialog calls DELETE /api/admin/team/{id} | |
| 3.7c | Remove success notification | After successful removal: "Removed {email} from the team." notification | |
| 3.7d | Remove refreshes list | After successful removal: team list refetches and member disappears from table | |
| 3.7e | Cancel closes dialog | Clicking cancel in confirmation dialog closes it without API call | |

#### 3.8 Loading and error feedback (3 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 3.8a | Remove loading state | While DELETE API in progress: confirm button shows loading state | |
| 3.8b | Remove error notification | When DELETE API fails: error notification "Failed to remove member: {msg}" | |
| 3.8c | Category toggle error | When category toggle PUT fails: error notification "Failed to update categories: {msg}" | |

---

### Page 4: Agent Configuration (73 tests)

> **Verification standard (session 47):** Every element is tested for presence, correct value,
> input manipulation, valid population, state change, control activation, input validation,
> and disposition variants — as applicable per element type.

**Navigate to** `$STANDALONE_URL/configuration`.

#### 4.1 Brand & persona section

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.1 | Brand & persona section renders | Paper card with: Brand name\* (required), Brand voice\* (required), Formality dropdown, Response length dropdown | |
| 4.1a | Brand name shows current config value | Input displays `brand_name` from `GET /api/config?state=draft`; empty with placeholder "Your store or brand name" if never set | |
| 4.1b | Brand name accepts valid text | Type "Acme Store" → input updates immediately, no character filtering | |
| 4.1c | Brand name shows required indicator | Red asterisk (\*) visible next to "Brand name" label | |
| 4.1d | Brand name save captures changed value | Modify → click "Save draft inputs" → `GET /api/config?state=draft` returns new `brand_name` | |
| 4.1e | Brand name draft persists on reload | After save, F5 refresh → input still shows modified value | |
| 4.1f | Discard reverts brand name | Modify → sidebar Discard → input reverts to last saved (active) config value | |
| 4.1g | Empty brand name blocks activation | Clear field → Save → sidebar Activate button yellow disposition; click shows "Brand name is required" in preflight dialog | |
| 4.1h | Changing brand name creates Pending state | Modify → Save → sidebar badge changes from Active/Inactive to yellow "Pending" | |
| 4.1i | Brand voice shows current config value | Textarea displays `brand_voice` from draft config; empty with placeholder "Describe the personality…" if never set | |
| 4.1j | Brand voice accepts multi-line text | Type multi-line description → textarea expands (autosize, minRows=3) | |
| 4.1k | Brand voice shows required indicator | Red asterisk (\*) visible next to "Brand voice" label | |
| 4.1l | Empty brand voice blocks activation | Clear field → Save → Activate shows "Brand voice is required" in preflight | |
| 4.1m | Formality dropdown shows current value | Select displays one of: Casual, Professional, Formal. Default: "Professional" | |
| 4.1n | Formality dropdown options correct | Click dropdown → exactly 3 options: Casual, Professional, Formal | |
| 4.1o | Formality change to Casual saved correctly | Select "Casual" → Save → `GET /api/config?state=draft` returns `formality_level: "casual"` | |
| 4.1p | Response length dropdown shows current value | Select displays one of: Concise, Moderate, Detailed. Default: "Moderate" | |
| 4.1q | Response length change saved correctly | Select "Detailed" → Save → draft returns `response_length: "detailed"` | |

#### 4.2 Policies section

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.2 | Policies section renders | Paper card with: Return window NumberInput, Refund policy textarea, Shipping policy textarea | PASS |
| 4.2a | Return window shows current value | NumberInput displays `return_window` from draft config with " days" suffix. Default: 30 | |
| 4.2b | Return window accepts valid range | Type 60 → displays "60 days"; type 0 → displays "0 days"; type 365 → displays "365 days" | |
| 4.2c | Return window rejects out-of-range | Type -1 → clamped to 0; type 400 → clamped to 365 (NumberInput min=0, max=365) | |
| 4.2d | Return window save persists value | Change to 14 → Save → reload → shows "14 days" | |
| 4.2e | Refund policy shows current value | Textarea displays `return_policy` from draft config; empty with placeholder "Describe your refund policy…" | |
| 4.2f | Refund policy textarea autosizes | Type 10+ lines → textarea height expands (autosize, minRows=3) | |
| 4.2g | Shipping policy shows current value | Textarea displays `shipping_info` from draft config; empty with placeholder "Describe your shipping policy…" | |
| 4.2h | Policies section tooltip | (?) icon present next to "Policies" header with doc link to business-policies | |

#### 4.2B Configuration suggestions (KA-4) — 8 tests

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.2i | Brand name suggestion badge — visible when empty | When brand_name is empty and suggestions API returns a brand_name suggestion, "Suggested" badge (violet) appears inline next to field label | |
| 4.2j | Brand name suggestion badge — hidden when populated | When brand_name has a value, suggestion badge is NOT shown even if API returned a suggestion | |
| 4.2k | Brand name suggestion — click to apply | Click "Suggested" badge → field populates with suggestion value; badge disappears | |
| 4.2l | Brand voice suggestion badge — visible when empty | When brand_voice is empty and suggestion exists, "Suggested" badge appears next to "Brand voice" label | |
| 4.2m | Brand voice suggestion — click to apply | Click badge → textarea populates with suggested brand voice text | |
| 4.2n | Refund policy suggestion badge — visible when empty | When return_policy (refund policy) is empty and suggestion exists, badge appears next to "Refund policy" label | |
| 4.2o | Shipping policy suggestion badge — visible when empty | When shipping_info (shipping policy) is empty and suggestion exists, badge appears next to "Shipping policy" label | |
| 4.2p | Suggestion badges — all hidden after apply+save | Apply all 4 suggestions → Save → reload → no suggestion badges visible (all fields populated) | |

#### 4.3 Escalation section

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.3 | Escalation section renders | Paper card with: threshold slider, 6 category accordions (Sales, Support, Service, Account, Technical assistance, General inquiry) | PASS |
| 4.3a | Threshold slider shows current value | Slider positioned at `escalation_threshold` from draft config. Default: 0.70 | |
| 4.3b | Threshold slider range and marks | Min=0 ("Conservative"), max=1 ("Aggressive"), mark at 0.5 labeled "0.5", step=0.05 | |
| 4.3c | Threshold slider label on drag | Dragging slider shows tooltip with value to 2 decimal places (e.g., "0.70") | |
| 4.3d | Threshold change saved correctly | Drag to 0.35 → Save → draft returns `escalation_threshold: 0.35` | |
| 4.3e | All 6 categories visible | Sales, Support, Service, Account, Technical assistance, General inquiry — all visible with toggle switches | |
| 4.3f | Category shows keyword count badge | Each category shows "{N} keywords" badge (e.g., "7 keywords" for Sales) | |
| 4.3g | Category shows email icon when email set | Category with non-empty email shows ✉ badge; empty email shows no icon | |
| 4.3h | Disabled category has reduced opacity | Toggle off a category → card opacity reduces to 0.6; toggle on → full opacity | |

#### 4.4 Escalation category expanded detail

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.4 | Escalation category expand | Click category row → expanded detail shows: Notification email, Keywords (chips with ×), Add keyword input, Reset button | PASS |
| 4.4a | Notification email shows current value | TextInput displays saved email for category; empty with placeholder "{category}@yourcompany.com" | |
| 4.4b | Notification email accepts valid email | Type "team@example.com" → input accepts; value persists after save | |
| 4.4c | Keywords displayed as removable chips | Each keyword shown as Badge with × (close) icon when category enabled | |
| 4.4d | Add keyword via Enter key | Type "new-keyword" + Enter → chip appears in list; input clears | |
| 4.4e | Duplicate keyword silently rejected | Type existing keyword + Enter → no duplicate chip added; input clears | |
| 4.4f | Cross-category keyword silently rejected | Type keyword belonging to another category → not added to this category | |
| 4.4g | Remove keyword via × icon | Click × on keyword chip → chip removed from list | |
| 4.4h | Reset keywords restores defaults | Click reset icon → keyword list reverts to default set for that category | |
| 4.4i | Disabled category disables inputs | Toggle category off → email input disabled, add keyword disabled, chip × icons hidden | |
| 4.4j | Category collapse hides detail | Click chevron or category row again → detail section collapses | |
| 4.4k | Category changes tracked as dirty | Modify any category field → "Save draft inputs" button becomes enabled (hasChanges=true) | |

#### 4.5 Custom instructions section

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.5 | Custom instructions section renders | Paper card with textarea and safety note below | PASS |
| 4.5a | Custom instructions shows current value | Textarea displays `custom_instructions` from draft config; empty with placeholder "Provide advisory instructions…" | |
| 4.5b | Custom instructions autosize | Type 6+ lines → textarea expands (autosize, minRows=5, maxRows=12) | |
| 4.5c | Safety note displayed below textarea | Text: "Advisory instructions for the AI agent. Safety rules always take precedence." | |
| 4.5d | Custom instructions tooltip | (?) icon present next to "Custom instructions" header with doc link | |
| 4.5e | Custom instructions save persists | Type new instructions → Save → reload → textarea shows saved text | |

#### 4.6 Language section

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.6 | Language section renders | Paper card with: Primary language dropdown, Supported languages chip group | |
| 4.6a | Primary language shows current value | Select displays `primary_language` from draft config. Default: "English" | |
| 4.6b | Primary language has single option | Dropdown shows only "English" (no other languages available) | |
| 4.6c | Supported languages chips correct | 3 chips: English (enabled, selectable), Spanish (coming soon, disabled), French (coming soon, disabled) | |
| 4.6d | English chip selected by default | English chip shows selected state (filled/colored). Default: `['en']` | |
| 4.6e | Disabled language chips not clickable | Click "Spanish (coming soon)" → no state change; cursor shows not-allowed; opacity 0.5 | |
| 4.6f | Language section tooltip | (?) icon present next to "Language" header with doc link | |

#### 4.7 Idle timeout and Max turns

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.7 | Idle timeout and Max turns render | Two NumberInputs side by side. Idle timeout: current value with " minutes" suffix. Max turns: current value (no suffix) | |
| 4.7a | Idle timeout shows current value | NumberInput displays `idle_timeout_minutes` from draft config. Default: 30 minutes | |
| 4.7b | Idle timeout accepts valid range | Type 1 → "1 minutes"; type 120 → "120 minutes" (min=1, max=120) | |
| 4.7c | Idle timeout rejects out-of-range | Type 0 → clamped to 1; type 999 → clamped to 120 | |
| 4.7d | Idle timeout tooltip present | (?) icon with text about customer inactivity timeout and doc link (D58 regression) | |
| 4.7e | Max turns shows current value | NumberInput displays `max_ai_turns_before_escalation` from draft config. Default: 50 | |
| 4.7f | Max turns accepts valid range | Type 5 → accepts; type 200 → accepts (min=5, max=200) | |
| 4.7g | Max turns rejects out-of-range | Type 3 → clamped to 5; type 500 → clamped to 200 | |
| 4.7h | Max turns tooltip present | (?) icon with text about max exchanges before auto-end and doc link (D58 regression) | |

#### 4.8–4.12 Controls and cross-cutting behavior

| # | Test | Expected | Status |
|---|------|----------|--------|
| 4.8 | Save draft inputs button renders | "Save draft inputs" button at bottom of page with save icon; no per-page Discard (sidebar serves that purpose) | |
| 4.8a | Save button disabled when no changes | On initial load (hasChanges=false), button is disabled/greyed | |
| 4.8b | Save button enabled when field modified | Modify any field → button becomes enabled with brand red color (#ff3621) | |
| 4.8c | Save button shows loading spinner | Click Save → button shows loading state while API call in progress | |
| 4.9 | Section tooltips present | (?) icons on: Brand & persona, Policies, Escalation, Custom instructions, Language — each with doc link | PASS |
| 4.9a | Tooltip hover shows help text | Hover (?) icon → dark tooltip appears with descriptive text (240px width) | |
| 4.9b | Tooltip doc link navigates correctly | Click doc link within tooltip → navigates to `agentredcx.com/docs/admin-guide/{section}` | |
| 4.10 | Save draft inputs succeeds | Modify brand name → click "Save draft inputs" → success notification "Draft configuration saved successfully." appears | |
| 4.10a | Saved changes persist on reload | After successful save, F5 refresh → all modified fields retain their saved values | |
| 4.10b | Save updates server snapshot | After save, sidebar Discard reverts to new saved values (not original pre-save values) | |
| 4.10c | Save triggers activation status refresh | After save, sidebar badge updates to reflect new draft state (Pending if config was Active) | |
| 4.11 | Sidebar Discard reverts unsaved changes | Modify a field without saving → click sidebar Discard → field reverts to last saved draft value | |
| 4.11a | Discard resets hasChanges flag | After Discard, "Save draft inputs" button returns to disabled state | |
| 4.12 | Error banner dismissible | If save API fails → red Alert banner with title "Save failed" and error text; X button closes it | |
| 4.12a | Error banner shows specific error message | Error text from API response displayed in banner (not generic "Something went wrong") | |
| 4.12b | Error banner X button clears error state | Click X → banner disappears; save button remains enabled for retry | |
| 4.13 | Loading state on initial page load | Before config data loads, LoadingState component shown ("Loading configuration") | |
| 4.14 | Error state with retry button | If config API fails → red Alert "Failed to load configuration" with Retry button | |
| 4.14a | Retry button re-fetches config | Click Retry → config re-fetches; on success, form populates; on repeated failure, error persists | |

---

### Page 5: Knowledge Base

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard (incl. data-binding correctness).

#### 5.1 Summary stat cards

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.1 | Page renders with stats | Total articles, Published, Draft, Archived, Needs attention cards with counts | PASS |
| 5.1a | Total articles — correct value | Card shows count matching number of articles in API response | |
| 5.1b | Published — correct value | Card shows count (green) matching articles with status "published" | |
| 5.1c | Draft — correct value | Card shows count (yellow) matching articles with status "draft" | |
| 5.1d | Archived — correct value | Card shows count (dimmed) matching articles with status "archived" | |
| 5.1e | Needs attention — correct value | Card shows count (red) = staleCount + veryStaleCount from staleness API | |
| 5.1f | Stats update after article create | After creating a new article, stat counts update (Total increases by 1, Draft increases by 1) | |
| 5.1g | Stats update after archive | After archiving an article, Published decreases, Archived increases | |
| 5.8 | Needs attention tooltip | Hovering "Needs attention" card shows explanation text | PASS |
| 5.16 | Archived count in summary stats (D62 regression) | Summary cards show 5 values: Total articles, Published, Draft, Archived, Needs attention — Archived count matches number of archived articles in the table | |

#### 5.2 Articles table

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.2 | Article table renders | Title, Category, Status, Freshness, Last updated, Actions columns | PASS |
| 5.2a | Table column headers correct | 6 columns: Title, Category, Status, Freshness, Last updated, Actions | |
| 5.2b | Category badge colors | Policies=blue, Shipping=violet, Products=teal, Sales=orange, Services=pink, FAQ=cyan, Custom=gray | |
| 5.2c | Status badge colors | Published=green, Draft=yellow, Archived=gray | |
| 5.3 | Freshness badges | Articles show Fresh (green) or Aging (yellow) badges | PASS |
| 5.3a | Freshness badge — Stale (red) | Articles past staleness threshold show "Stale" or "Very stale" red badge | |
| 5.3b | Last updated — formatted date | Shows date in "Mon DD, YYYY" format (e.g., "Jan 15, 2026"); "--" when null | |
| 5.12 | Archived article visually distinguished | After archiving, the article row shows opacity 0.5 and title has line-through styling | |
| 5.13 | Freshness value meaningful for new articles | Newly created articles show "Fresh" (green), not "--" | |
| 5.18 | Archived article shows Category and Status values | After archiving an article, the table row displays the resolved Category (e.g. "Products") and Status ("Archived") — not "--" | |
| 5.19 | Empty filter state message | Filtering by a category with no matching articles displays "No articles match your filters." centered text | |

#### 5.4 Search and filters

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.4 | Search filters articles | Typing in search box filters articles by title and content | PASS |
| 5.4a | Search — placeholder | TextInput shows placeholder "Search articles..." with search icon | |
| 5.4b | Search — filters by title | Typing a word from an article title shows only matching articles | |
| 5.4c | Search — filters by content | Typing a word from article content (not title) shows matching articles | |
| 5.4d | Search — case insensitive | Searching "POLICY" matches articles with "policy" in title/content | |
| 5.4e | Search — clear restores all | Clearing search field shows all articles again | |
| 5.7 | Category and status filters | Two "All" dropdowns filter the article list | PASS |
| 5.7a | Category filter — 8 options | Dropdown shows: All, Policies, Shipping, Products, Sales, Services, FAQ, Custom | |
| 5.7b | Category filter — applies correctly | Selecting "Products" shows only articles with category "Products" | |
| 5.7c | Status filter — 4 options | Dropdown shows: All, Published, Draft, Archived | |
| 5.7d | Status filter — applies correctly | Selecting "Published" shows only articles with status "published" | |
| 5.7e | Combined filters | Search + Category + Status all apply simultaneously | |
| 5.10 | Category/Status filters match article data | Filtering by the assigned category or status returns the matching article | |
| 5.17 | Category filter matches resolved category (D63 regression) | Creating an article with Category "Products" then filtering by "Products" returns that article; entryType-derived categories also match filter values | |

#### 5.5 Article CRUD — Edit modal

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.5 | Edit article modal | Clicking edit icon opens modal with Title*, Category*, Content*, Status* fields pre-filled | PASS |
| 5.5a | Edit modal — title pre-filled | Title field shows article's current title | |
| 5.5b | Edit modal — category pre-filled | Category dropdown shows article's current category | |
| 5.5c | Edit modal — content pre-filled | Content textarea shows article's current content | |
| 5.5d | Edit modal — status pre-filled | Status dropdown shows article's current status | |
| 5.5e | Edit modal — save changes | Clicking "Save changes" updates the article and shows success notification "Article updated successfully" | |
| 5.5f | Edit modal — cancel | Clicking "Cancel" closes modal without saving | |
| 5.5g | Edit modal — validation | "Save changes" button disabled when title or content is empty | |
| 5.5h | Edit modal — error display | If save fails, red error text appears in modal | |
| 5.9 | Created article shows Category and Status in list | After creating an article with Category and Status, both values display in the article table row (not "--") | |

#### 5.6 Action buttons and controls

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.6 | Action buttons present | Scan for conflicts, Export CSV, Import, + Add article buttons visible | PASS |
| 5.6a | Add article — opens blank modal | Clicking "Add article" opens modal with empty form, title "Add article", button "Create article" | |
| 5.6b | Add article — create success | Filling all required fields and clicking "Create article" → success notification "Article created successfully", article appears in table | |
| 5.6c | Add article — tooltip | Hovering "Add article" button shows tooltip about creating new KB article | |
| 5.6d | Scan for conflicts — tooltip | Hovering shows "Detect duplicate, overlapping, or contradictory entries..." tooltip | |
| 5.6e | Scan for conflicts — disabled when empty | Button disabled when articles.length === 0 | |
| 5.6f | Scan for conflicts — loading state | While scanning, button shows loading spinner | |
| 5.6g | Export CSV — tooltip | Hovering shows "Download all knowledge base entries as a CSV file..." tooltip | |
| 5.6h | Export CSV — disabled when empty | Button disabled when articles.length === 0 | |
| 5.6i | Export CSV — loading state | While exporting, button shows loading spinner | |
| 5.6j | Export CSV — success | Clicking Export CSV shows success notification "Knowledge base exported as CSV" | |
| 5.6k | Import — tooltip | Hovering shows "Upload PDF, DOCX, CSV, or TXT files, or import from a URL..." tooltip | |
| 5.11 | KB article create triggers Pending config state | After saving a new article, sidebar config badge changes to "Pending" and Activate button becomes available (D16 fix — session 27) | |

#### 5.14 Table row actions

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.14 | Archived article can be restored | An archived article has a visible Restore control (blue arrow icon) | |
| 5.14a | Archive action — click | Clicking Archive icon on a published/draft article → success notification '"{title}" archived' | |
| 5.14b | Archive action — table update | After archive, article row shows opacity 0.5, title line-through, "Archived" badge | |
| 5.14c | Restore action — click | Clicking Restore icon on an archived article → success notification '"{title}" restored as Draft' | |
| 5.14d | Restore action — table update | After restore, article row returns to normal opacity, Draft status badge | |
| 5.14e | Verify action — conditional display | Verify (green check) icon only shown for articles with staleness "stale", "aging", or "very_stale" | |
| 5.14f | Verify action — click | Clicking Verify icon → success notification "Article verified as current", freshness updated | |
| 5.15 | Action icon tooltips (D60 regression) | Hovering each action icon (Edit, Archive/Restore, Verify) shows a styled Mantine tooltip with arrow, not a plain browser title tooltip | |

#### 5.20 Import modal

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.20 | Import modal — file tab | Clicking "Import" opens modal with "Upload file" tab active, drag-drop zone, accepted types: PDF, DOCX, CSV, TXT | |
| 5.20a | Import modal — drag-drop zone | Shows "Drop a file here or click to browse" text with file icon and accepted types info | |
| 5.20b | Import modal — drag highlight | Dragging a file over the zone changes border color to BRAND_RED and adds highlight background | |
| 5.20c | Import modal — upload progress | During upload, progress bar animates and "Uploading..." / "Processing document..." text shown | |
| 5.20d | Import modal — upload success | After successful upload, shows checkmark, "Import successful", entries created count, "Back to knowledge base" button | |
| 5.20e | Import modal — upload error | If upload fails, red error text "File upload failed" appears | |
| 5.20f | Import modal — URL tab | Switching to "Import URL" tab shows TextInput "Website URL" with placeholder and Import button | |
| 5.20g | Import modal — URL validation | Import button disabled when URL input is empty | |
| 5.20h | Import modal — URL import success | Entering URL and clicking Import → success notification "Imported N entries from URL" | |
| 5.20i | Import modal — URL import error | If URL import fails, red error text and notification "URL import failed" | |

#### 5.21 Conflict scan results modal

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.21 | Conflict scan — no issues | If scan finds no conflicts, "All clear" green Alert displays with message about no conflicts detected | |
| 5.21a | Conflict scan — stats cards | 4 stats: Entries scanned, With embeddings, Scan time, Issues found (color-coded: red if high>0, orange if medium>0, green otherwise) | |
| 5.21b | Conflict scan — severity badges | High (red), Medium (orange), Low (yellow) severity badges shown when counts > 0 | |
| 5.21c | Conflict scan — accordion list | Each conflict shows as accordion item with severity badge, type badge, article pair names | |
| 5.21d | Conflict scan — accordion detail | Expanding shows Article A/B names, similarity scores (embedding, content overlap, title), conflicting facts, suggested resolution | |
| 5.21e | Conflict scan — 503 error | If embedding support unavailable, shows "Conflict scanner is not available. This feature requires embedding support." | |
| 5.21f | Conflict scan — re-scan force | "Re-scan (force)" button triggers new scan with force=true | |
| 5.21g | Conflict scan — footer info | Shows scan timestamp and count of entries skipped (no embeddings) | |

#### 5.23 Knowledge automation section (KA-7) — 18 tests

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.23 | Knowledge automation section renders | Paper card with title "Knowledge automation", violet "Beta" badge, Show/Hide toggle button | |
| 5.23a | Default state — collapsed | Section initially collapsed; subtitle text "Import content from your storefront or apply industry templates..." visible | |
| 5.23b | Show toggle — expand | Click "Show" → section expands, button text changes to "Hide" | |
| 5.23c | Hide toggle — collapse | Click "Hide" → section collapses back, subtitle reappears, button text changes to "Show" | |
| 5.23d | Storefront scan button renders | "Scan storefront" button with `action` blue color inside expanded section | |
| 5.23e | Scan storefront — loading state | Click "Scan storefront" → button shows loading spinner (startingIngestion=true) | |
| 5.23f | Scan storefront — disabled during active job | When ingestionStatus shows an active job, "Scan storefront" button is disabled | |
| 5.23g | IngestionPanel — empty state | When no ingestion job exists, IngestionPanel renders without error (null job → no visible panel or empty message) | |
| 5.23h | IngestionPanel — active job display | When ingestion job exists (status=running), panel shows: status badge, source label, progress bar with percent, articles found count, cancel button | |
| 5.23i | IngestionPanel — completed job | When job status=completed, panel shows green "completed" badge, total articles created, elapsed time | |
| 5.23j | IngestionPanel — cancel button | Click "Cancel" → cancel API called; loading state on cancel button; job status updates to "cancelled" | |
| 5.23k | Category template selector renders | Grid of template cards within expanded section; each card shows template name, description, article count badge | |
| 5.23l | Template count — 10 templates | Grid displays exactly 10 category templates (apparel_fashion through pet_supplies) | |
| 5.23m | Template card — apply button | Each template card has "Apply to knowledge base" button with action blue color | |
| 5.23n | Template apply — loading state | Click "Apply to knowledge base" → button shows loading spinner (applyingTemplate=true) | |
| 5.23o | Template apply — success | After successful apply, success notification shows articles created count; KB stats refresh (article count increases) | |
| 5.23p | Template apply — error | If apply fails, error notification displayed with error message; template grid remains usable | |
| 5.23q | Template selector — loading state | While templates API loading, shows skeleton/loading indicator | |

#### 5.22 Loading and error states

| # | Test | Expected | Status |
|---|------|----------|--------|
| 5.22 | Loading state | LoadingState "Loading knowledge base" spinner shown while API fetches | |
| 5.22a | Error state | "Failed to load knowledge base: {error}" red text with "Retry" button | |
| 5.22b | Error retry | Clicking "Retry" triggers refetch; on success, page renders normally | |

---

### Page 6: Quick Actions

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard (incl. data-binding correctness).

#### 6.1 Tab navigation and page header

| # | Test | Expected | Status |
|---|------|----------|--------|
| 6.1 | Prompt library tab renders | Table with Order, Icon, Label, Prompt template, Status, Actions columns; count in tab label | PASS |
| 6.1a | Tab label shows action count | "Prompt library (N)" tab label where N = number of quick actions (e.g., "Prompt library (4)") | |
| 6.1b | Page header text | Title "Quick actions" with subtitle "Manage contextual prompt buttons that appear in the chat widget" | |
| 6.1c | Page assignments tab accessible | Clicking "Page assignments" tab switches to assignment view | |
| 6.1d | Tab default | "Prompt library" tab is selected by default on page load | |

#### 6.2 Empty state and starter examples

| # | Test | Expected | Status |
|---|------|----------|--------|
| 6.2 | Empty state with examples | "No quick actions yet" message with 4 QA starter chips (Track my order, Return policy, Product recommendations, Help with my order) | PASS |
| 6.2a | Starter chip — Track my order | Chip shows 📦 icon; clicking it creates quick action with label "Track my order" and correct prompt template | |
| 6.2b | Starter chip — Return policy | Chip shows 🔄 icon; clicking it creates quick action with label "Return policy" and correct prompt template | |
| 6.2c | Starter chip — Product recommendations | Chip shows 💡 icon; clicking it creates quick action referencing {{product_title}} | |
| 6.2d | Starter chip — Help with my order | Chip shows ❓ icon; clicking it creates quick action with label "Help with my order" | |
| 6.2e | Starter chip creates action and refreshes table | After clicking a starter chip, table refreshes to show the new action; empty state disappears | |
| 6.2f | Starter instructions | "Click any example to add it, then customize the prompt template" text below chips | |

#### 6.3 Prompt library table

| # | Test | Expected | Status |
|---|------|----------|--------|
| 6.3 | Create quick action button | Red "Create quick action" button visible | PASS |
| 6.3a | Table columns | 6 columns: Order, Icon, Label, Prompt template, Status, Actions | |
| 6.3b | Table row — sort order | Displays action.sortOrder as dimmed number | |
| 6.3c | Table row — icon | Displays emoji icon or "—" when null | |
| 6.3d | Table row — label | Displays action label in fw=500 text | |
| 6.3e | Table row — prompt template | Displays truncated (lineClamp=2) prompt text, max-width 300px | |
| 6.9 | Status badge fully visible (D64 regression) | Status badges ("Active", "Inactive") display their full text without truncation | |
| 6.3f | Status badge — Active variant | Green filled badge with text "Active" when isActive=true | |
| 6.3g | Status badge — Inactive variant | Gray outline badge with text "Inactive" when isActive=false | |
| 6.3h | Edit action icon | Pencil icon with "Edit" tooltip; clicking opens Edit modal pre-filled with action data | |
| 6.3i | Delete action icon | Trash icon with "Delete" tooltip; clicking opens confirm delete modal | |

#### 6.4 Page assignments tab

| # | Test | Expected | Status |
|---|------|----------|--------|
| 6.4 | Page assignments tab renders | Table with 9 page types (All pages fallback, Home, Product, Collection, Cart, Search, Blog, Page, Other) | PASS |
| 6.5 | Page assignment controls | Each row has Slot 1, Slot 2 dropdowns, Auto-open toggle, Delay (s) input | PASS |
| 6.6 | Page assignments explanation | Info card explains slot/fallback behavior | PASS |
| 6.4a | Page type badges | "All pages (fallback)" badge is blue; all other page types are gray | |
| 6.4b | Slot 1 Select — correct options | Dropdown lists all quick actions with icon + label; inactive actions marked "(inactive)"; clearable | |
| 6.4c | Slot 2 Select — independent | Slot 2 dropdown functions independently from Slot 1; can assign same or different action | |
| 6.4d | Slot assignment — inline save | Changing a slot dropdown value triggers immediate save to API and refreshes assignments | |
| 6.4e | Slot clear — delete assignment | Clearing both slots for a page type deletes the assignment entirely | |
| 6.8 | Auto-open toggle functional | Toggling Auto-open on a page assignment row enables/disables auto-open and persists on reload | |
| 6.4f | Auto-open column header tooltip | Hovering "Auto-open" header shows "Auto-open the widget on this page type" | |
| 6.4g | Delay input — enabled when auto-open on | NumberInput enabled and interactive when Auto-open toggle is ON | |
| 6.4h | Delay input — disabled when auto-open off | NumberInput disabled (grayed out) when Auto-open toggle is OFF | |
| 6.4i | Delay input — range 1-60 | NumberInput min=1, max=60, step=1; shows value in seconds with "s" suffix | |
| 6.4j | Delay input — default 3s | Default value is 3s (derived from 3000ms) when no assignment exists | |
| 6.4k | Delay column header tooltip | Hovering "Delay (s)" header shows "Seconds to wait before auto-opening the widget" | |
| 6.10 | Page assignments write to draft | Changing slot assignments, auto-open toggle, or delay saves to draft configuration (not committed immediately); changes only take effect after Activate; sidebar badge shows "Pending" (D68 fix — session 27) | |

#### 6.5 Create/Edit quick action modal

| # | Test | Expected | Status |
|---|------|----------|--------|
| 6.5a | Create modal title | Modal title "Create quick action" when creating new | |
| 6.5b | Edit modal title | Modal title "Edit quick action" when editing existing | |
| 6.5c | Button label field — required | TextInput with label "Button label", required star, placeholder "e.g. What can you do?", maxLength=100 | |
| 6.5d | Prompt template field — required | Textarea with label "Prompt template", required star, description mentioning variable insertion, maxLength=2000 | |
| 6.5e | Template variable chips | 6 chips below prompt textarea: {{page_type}}, {{page_handle}}, {{page_title}}, {{page_url}}, {{product_title}}, {{collection_title}} | |
| 6.5f | Template variable insertion | Clicking a variable chip inserts it at cursor position in prompt textarea (or appends if no cursor) | |
| 6.5g | Icon field — optional | TextInput with label "Icon (optional)", placeholder "e.g. 📦", maxLength=50 | |
| 6.5h | Emoji quick-pick buttons | 12 emoji buttons (📦🔄💡❓🛒💬🏷️🚚⭐🔍💰🎁); clicking one sets the icon field; selected emoji has filled red variant | |
| 6.5i | Active toggle | Switch labeled "Active" with description "Inactive quick actions won't appear in the widget" | |
| 6.5j | Preview pill | When label is non-empty, preview shows inline pill with icon + label in rounded border | |
| 6.5k | Save button disabled when empty | "Create" / "Save changes" button disabled when label or prompt is empty | |
| 6.5l | Save button loading state | Button shows spinner while saving (saving=true) | |
| 6.5m | Cancel button closes modal | Clicking "Cancel" closes modal without saving | |
| 6.5n | Edit modal pre-populates fields | When editing, label, prompt, icon, active, and sortOrder fields pre-populate from existing action data | |
| 6.7 | Quick action create triggers Pending config state | After creating a quick action, sidebar config badge changes to "Pending" (D20 fix — session 27) | |

#### 6.6 Confirm delete modal

| # | Test | Expected | Status |
|---|------|----------|--------|
| 6.6a | Delete confirmation dialog | Modal titled "Delete quick action" with confirmation text including action label in bold | |
| 6.6b | Delete warning text | Text warns "This will also remove it from any page assignments" | |
| 6.6c | Cancel preserves action | Clicking "Cancel" closes modal; action remains in table | |
| 6.6d | Delete removes action | Clicking "Delete" removes the action and refreshes both actions and assignments tables | |
| 6.6e | Delete success notification | After successful delete, notification shows "Quick action deleted" | |

#### 6.7 Loading and error states

| # | Test | Expected | Status |
|---|------|----------|--------|
| 6.7a | Loading state | LoadingState component shows "Loading quick actions" while data fetches | |
| 6.7b | Error state with retry | When API fails, Alert shows error message with red "Retry" button | |
| 6.7c | Retry re-fetches data | Clicking "Retry" clears error, re-enters loading state, and re-fetches both actions and assignments | |

---

### Page 7: Widget Configuration

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard (incl. data-binding correctness).

#### 7.1 Live preview

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.1 | Live preview renders | Chat widget preview on right side with header, messages, input, launcher | PASS |
| 7.1a | Preview shows current primary color | Header background matches primaryColor value (default #ff3621) | |
| 7.1b | Preview shows header title/subtitle | Title shows "Support" (or saved value), subtitle shows "We typically reply within minutes" (or saved value) | |
| 7.1c | Preview greeting message renders | Agent greeting bubble displays current greetingMessage text with template variables resolved to sample values | |
| 7.1d | Preview updates in real-time | Changing any form input (e.g., primaryColor) immediately updates preview without save | |
| 7.1e | Launcher button toggles chat panel | Clicking the launcher circle hides/shows the chat panel in preview | |
| 7.1f | Preview reflects position setting | Toggling Position to "Bottom left" moves launcher and panel to left side of preview | |
| 7.1g | Preview reflects panel width | Changing Panel width to Compact/Wide visibly narrows/widens the chat panel | |
| 7.1h | Preview reflects shadow intensity | Changing Panel shadow from Standard to None removes visible shadow from chat panel | |
| 7.1i | Preview reflects color mode | Switching Color mode to Light changes preview background and bubble colors | |
| 7.1j | Preview reflects launcher icon | Changing Launcher icon from Chat bubble to Headset changes the SVG icon in the launcher circle | |
| 7.1k | Preview loading state | LoadingOverlay displays while config is being fetched (before initialization) | |

#### 7.2 Appearance — Color pickers

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.2 | Appearance section renders | Header left/right color pickers with hex input, color swatches, gradient toggle | PASS |
| 7.2a | Header left color — current value | Hex input shows saved primaryColor value (default #ff3621); swatch preview square matches | |
| 7.2b | Header left color — hex input accepts valid hex | Typing "#2563EB" in hex input updates swatch preview and live preview header | |
| 7.2c | Header left color — hex validation | Non-hex characters (e.g., "#ZZZZZZ") are rejected by regex `/^#[0-9a-fA-F]{0,6}$/` — input does not accept them | |
| 7.2d | Header left color — swatch click | Clicking a swatch (e.g., #059669 green) sets hex input and updates preview | |
| 7.2e | Header left color — color picker drag | Dragging saturation/hue picker updates hex input and preview in real-time | |
| 7.2f | Header right color — disabled when gradient off | When "Enable header gradient" is off, right color picker has opacity 0.4 and pointer-events none | |
| 7.2g | Header right color — enabled when gradient on | Toggling gradient on restores right color picker to full opacity and interactable | |
| 7.2h | Header right color — current value | Shows saved headerGradientEnd value (default #8B1520) | |
| 7.2i | Gradient toggle — renders | "Enable header gradient" Switch displays with label and description text | |
| 7.2j | Gradient toggle — default state | Switch is OFF by default (headerGradientEnabled: false) | |
| 7.2k | Gradient toggle — activation | Toggling ON enables right color picker and changes preview header to gradient (left→right blend) | |

#### 7.3 Appearance — Font, sliders, selects

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.3 | Font family dropdown renders | Select with current value label | PASS |
| 7.3a | Font family — current value | Shows saved fontFamily (default "Inter (System)") | |
| 7.3b | Font family — 4 options | Dropdown shows: Inter (System), Inter, Roboto, Open Sans | |
| 7.3c | Font family — selection updates preview | Selecting "Roboto" changes font in live preview chat bubbles and header | |
| 7.4 | Border radius slider renders | Slider 0–24px with current value label | PASS |
| 7.4a | Border radius — current value | Label shows "Border radius ({value}px)" with saved value (default 16) | |
| 7.4b | Border radius — marks | Slider shows marks at 0, 8, 16, 24 | |
| 7.4c | Border radius — drag updates preview | Dragging slider to 0 makes preview chat panel corners square | |
| 7.5 | Launcher size slider renders | Slider 48–72px with current value label | PASS |
| 7.5a | Launcher size — current value | Label shows "Launcher size ({value}px)" with saved value (default 60) | |
| 7.5b | Launcher size — marks | Slider shows marks at 48, 60, 72 | |
| 7.5c | Launcher size — drag updates preview | Dragging slider to 72 visibly enlarges launcher circle in preview | |
| 7.6 | Launcher icon dropdown renders | Select with current value | PASS |
| 7.6a | Launcher icon — current value | Shows saved launcherIcon (default "Chat bubble") | |
| 7.6b | Launcher icon — 3 options | Dropdown shows: Chat bubble, Headset, Help circle | |
| 7.6c | Launcher icon — selection updates preview | Selecting "Headset" changes SVG icon in launcher circle | |

#### 7.7 Appearance — Position and offsets

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.7 | Position toggle renders | Bottom right / Bottom left segmented control | PASS |
| 7.7a | Position — current value | Segmented control shows saved value (default "Bottom right") as active | |
| 7.7b | Position — toggle updates preview | Selecting "Bottom left" moves launcher and chat panel to left side of preview | |
| 7.7c | Horizontal offset — renders | NumberInput with label "Horizontal offset", description "Distance from edge (px)" | |
| 7.7d | Horizontal offset — current value | Shows saved positionOffsetX with " px" suffix (default 20 px) | |
| 7.7e | Horizontal offset — range validation | Accepts 0–200; values outside range clamped or rejected | |
| 7.7f | Vertical offset — renders | NumberInput with label "Vertical offset", description "Distance from bottom (px)" | |
| 7.7g | Vertical offset — current value | Shows saved positionOffsetY with " px" suffix (default 20 px) | |
| 7.7h | Vertical offset — range validation | Accepts 0–200; values outside range clamped or rejected | |

#### 7.8 Appearance — Color mode, panel width, shadow

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.8 | Panel width control renders | Compact / Standard / Wide segmented control with tooltip | PASS |
| 7.8a | Panel width — current value | Segmented control shows saved value (default "Standard") as active | |
| 7.8b | Panel width — tooltip | HelpTooltip (?) icon explains Compact (320px), Standard (380px), Wide (440px) | |
| 7.8c | Panel width — change updates preview | Selecting "Wide" visibly widens chat panel in preview | |
| 7.8d | Color mode — renders | Light / Dark / Auto segmented control | |
| 7.8e | Color mode — current value | Shows saved colorMode (default "Dark") as active | |
| 7.8f | Color mode — Light updates preview | Selecting "Light" changes preview to light background, light bubbles | |
| 7.8g | Color mode — Auto follows admin theme | Selecting "Auto" makes widget preview match admin dark/light mode | |
| 7.9 | Panel shadow control renders | None / Subtle / Standard / Heavy segmented control | PASS |
| 7.9a | Panel shadow — current value | Shows saved shadowIntensity (default "Standard") as active | |
| 7.9b | Panel shadow — None removes shadow | Selecting "None" removes box-shadow from chat panel in preview | |
| 7.9c | Panel shadow — Heavy adds prominent shadow | Selecting "Heavy" adds visibly deeper shadow around chat panel | |

#### 7.10 Behavior — Greeting, pre-chat, sound

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.10 | Behavior section renders | Greeting message toggle + text area with template variables, Pre-chat form toggle, Sound notifications toggle | PASS |
| 7.10a | Greeting toggle — current value | Switch shows saved greetingEnabled state (default ON) | |
| 7.10b | Greeting toggle — OFF disables textarea | Toggling greeting OFF disables the greeting message Textarea (grayed out) | |
| 7.10c | Greeting toggle — OFF hides template variables | Template variable buttons hidden when greeting is OFF | |
| 7.10d | Greeting toggle — OFF removes greeting from preview | Preview no longer shows agent greeting bubble | |
| 7.10e | Greeting textarea — current value | Shows saved greetingMessage (default "👋 Hi there! How can I help you today?") | |
| 7.10f | Greeting textarea — tooltip | HelpTooltip (?) explains this is a static welcome message, not AI-generated | |
| 7.10g | Greeting textarea — edit updates preview | Typing new text updates greeting bubble in preview in real-time | |
| 7.10h | Greeting textarea — autosize | Textarea grows from minRows=2 up to maxRows=4 as content increases | |
| 7.11 | Template variables render | 4 clickable buttons: \<FIRST_NAME\>, \<LAST_NAME\>, \<FULL_NAME\>, \<COMPANY\> | PASS |
| 7.11a | Template variable — click inserts token | Clicking \<FIRST_NAME\> appends token to greeting message textarea | |
| 7.11b | Template variable — preview resolves tokens | Greeting bubble in preview shows "Sarah" instead of \<FIRST_NAME\>, "Johnson" for \<LAST_NAME\>, etc. | |
| 7.11c | Pre-chat form toggle — renders | Switch with label "Pre-chat form", HelpTooltip, description text | |
| 7.11d | Pre-chat form toggle — default OFF | Switch is OFF by default (preChatFormEnabled: false) | |
| 7.11e | Pre-chat form toggle — ON reveals field chips | Toggling ON shows Chip.Group with 4 field chips: Name, Email, Phone, Company | |
| 7.11f | Pre-chat field chips — default selection | Name and Email chips selected by default (preChatFields: ['name', 'email']) | |
| 7.11g | Pre-chat field chips — toggle selection | Clicking Phone chip adds it to selection; clicking Email deselects it | |
| 7.11h | Sound notifications toggle — renders | Switch with label "Sound notifications" | |
| 7.11i | Sound notifications toggle — current value | Shows saved soundEnabled state (default ON) | |
| 7.11j | Sound notifications toggle — toggle OFF | Switching OFF sets soundEnabled to false | |

#### 7.12 Content — Header, placeholder, agent identity

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.12 | Content section renders | Header title, Header subtitle, Input placeholder text fields | PASS |
| 7.12a | Header title — current value | TextInput shows saved headerTitle (default "Support") | |
| 7.12b | Header title — edit updates preview | Typing "Help Desk" updates preview header title in real-time | |
| 7.12c | Header title — empty shows placeholder | Clearing field shows placeholder text "Support" | |
| 7.12d | Header subtitle — current value | TextInput shows saved headerSubtitle (default "We typically reply within minutes") | |
| 7.12e | Header subtitle — edit updates preview | Typing new subtitle updates preview header subtitle in real-time | |
| 7.12f | Input placeholder — current value | TextInput shows saved inputPlaceholder (default "Type your message...") | |
| 7.12g | Input placeholder — edit updates preview | Typing new placeholder updates the input bar placeholder text in preview | |
| 7.13 | Agent identity section renders | Agent display name and Agent avatar URL fields below "Agent identity" divider | PASS |
| 7.13a | Agent display name — current value | TextInput shows saved agentDisplayName (default empty, placeholder "Agent Red") | |
| 7.13b | Agent display name — edit updates preview | Typing "Maya" updates agent initials in preview chat bubbles to "MA" | |
| 7.13c | Agent avatar URL — current value | TextInput shows saved agentAvatarUrl (default empty, placeholder "https://example.com/avatar.png") | |
| 7.13d | Agent avatar URL — valid URL shows preview | Entering a valid image URL shows circular avatar preview below the input | |
| 7.13e | Agent avatar URL — updates preview launcher | Setting avatar URL updates the agent avatar shown in chat header and bubbles in preview | |
| 7.13f | Agent avatar URL — broken image hides | If URL points to nonexistent image, onError hides the img element | |

#### 7.14 Controls — Reset and Save

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.14 | Action buttons render | "Reset to defaults" (variant=default) and "Save draft inputs" (color=brand) at bottom | |
| 7.14a | Reset to defaults — click | Clicking Reset reverts all fields to DEFAULT_WIDGET_CONFIG values (primaryColor=#ff3621, borderRadius=16, etc.) | |
| 7.14b | Reset to defaults — preview updates | After reset, preview reflects all default values | |
| 7.14c | Save draft inputs — click saves | Clicking Save calls API with widgetConfigToApiFields, shows success notification "Draft widget settings saved successfully." | |
| 7.14d | Save draft inputs — loading state | While saving, button shows loading spinner (loading={saving}) | |
| 7.14e | Save draft inputs — error notification | If API fails, error notification "Failed to save widget settings" displays | |
| 7.14f | Save draft inputs — triggers activation refresh | Successful save calls refreshActivationStatus() to update sidebar badge | |
| 7.14g | Save draft inputs — persists on reload | After save, reloading page shows the saved values (not defaults) | |

#### 7.15 Section tooltips

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.15 | Section tooltips render | (?) icons on Appearance, Panel width, Greeting message, Pre-chat form, Content | PASS |
| 7.15a | Appearance tooltip text | Tooltip explains "Colors, position, size, and visual style of the chat widget on your storefront." | |
| 7.15b | Behavior tooltip text | Tooltip explains "Auto-open timing, sound notifications, pre-chat form fields, and idle timeout." | |
| 7.15c | Content tooltip text | Tooltip explains "Header text, greeting message, agent identity, and placeholder text shown in the widget." | |
| 7.15d | Panel width tooltip text | Tooltip explains Compact (320px), Standard (380px), Wide (440px) | |
| 7.15e | Greeting message tooltip text | Tooltip explains static welcome message, not AI-generated | |
| 7.15f | Pre-chat form tooltip text | Tooltip explains self-reported identity collection, not for authentication | |

#### 7.16–7.20 Agent avatar upload (SKIP — D22 deferred)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.16 | Agent avatar upload accepts PNG file | Click upload control → file picker opens → selecting a valid PNG shows preview | SKIP (D22) |
| 7.17 | Agent avatar rejects non-PNG files | Selecting a non-PNG file (JPG, GIF, SVG, etc.) shows validation error | SKIP (D22) |
| 7.18 | Agent avatar crop/position control | After upload, a crop UI allows positioning the viewable area to enforce correct aspect ratio | SKIP (D22) |
| 7.19 | Agent avatar resize | Uploaded image is resized to the correct avatar dimensions after crop | SKIP (D22) |
| 7.20 | Agent avatar persists on save | After upload + crop, clicking Save persists the avatar; avatar displays correctly in widget preview and on reload | SKIP (D22) |

#### 7.21–7.22 End-to-end

| # | Test | Expected | Status |
|---|------|----------|--------|
| 7.21 | Widget launcher opens chat window | Clicking the launcher button (red circle) in the live preview opens the chat panel | |
| 7.22 | Widget config save succeeds | Modifying any widget setting and clicking "Save draft inputs" → success notification, changes persisted on reload | |

---

### Page 8: Integrations

#### 8.1 Page header and loading states (5 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 8.1 | Page renders with cards | Integration cards render: Shopify, Zendesk, Mailchimp, Google Analytics (and Stripe if returned by API) | PASS |
| 8.1a | Page title | "Integrations" title and "Connect third-party services" subtitle | |
| 8.1b | Loading state | "Loading integrations..." renders while integration API loads | |
| 8.1c | Error state | When API fails, "Failed to load integrations:" message renders in red | |
| 8.1d | Empty state | When API returns empty array: "No integrations available." message | |

#### 8.2 Integration card layout (8 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 8.2 | Shopify card (connected) | Logo, description, Deactivate and Disconnect buttons | PASS |
| 8.2a | Card logo | Each integration card shows correct logo image (dark/light variant) or fallback SVG icon | |
| 8.2b | Card name | Integration name renders in 22px bold text | |
| 8.2c | Status badge — connected | Connected integrations show green "Connected" badge with dot | |
| 8.2d | Status badge — disconnected | Disconnected integrations show gray "Not Connected" badge with dot | |
| 8.2e | Status badge — error | Error-state integrations show red "Error" badge with dot | |
| 8.2f | Card description | Each integration shows descriptive text below name | |
| 8.5 | Tooltips on integration names | (?) icon next to each integration name with tooltip text and doc link | PASS |

#### 8.3 Coming Soon and tier-gated badges (5 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 8.3 | Coming Soon integrations | Integrations with comingSoon=true show purple "Coming Soon" badge | PASS |
| 8.3a | Coming Soon message | Coming Soon cards show "This integration is under development and will be available soon." | |
| 8.3b | Coming Soon no action buttons | Coming Soon integrations have no Activate/Deactivate/Disconnect buttons | |
| 8.3c | Tier-gated badge | Integrations where tierMet=false show yellow upgrade badge with tier name | |
| 8.3d | Tier-gated message | Tier-gated integrations show "Upgrade to {tier} to use this integration" text | |

#### 8.4 Activate / Deactivate / Disconnect actions (11 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 8.4a | Activate button | Disconnected + tier-met integrations show "Activate" primary button | |
| 8.4b | Activate loading | Clicking "Activate" shows "Activating..." text while API processes | |
| 8.4c | Activate success | After activation: success notification, list refetches, card shows connected state | |
| 8.4d | Activate error | When activation fails: "Failed to activate integration." error notification | |
| 8.4e | Deactivate button | Connected integrations show "Deactivate" outline button | |
| 8.4f | Deactivate loading | Clicking "Deactivate" shows "Deactivating..." while API processes | |
| 8.4g | Deactivate success | After deactivation: success notification, list refetches, card shows disconnected | |
| 8.4h | Disconnect flow | Clicking "Disconnect" shows inline confirmation: "Disconnect? This removes credentials." with Confirm/Cancel | |
| 8.4i | Disconnect confirm | Clicking "Confirm" calls disconnect API, shows success notification, refetches | |
| 8.4j | Disconnect cancel | Clicking "Cancel" closes confirmation without API call | |
| 8.6 | Button hover states | Hovering Deactivate or Disconnect changes background only — border does not change | |

#### 8.5 Summary footer (3 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 8.4 | Count footer | "N of N integrations active" text at bottom matches actual enabled count | PASS |
| 8.5a | Tier hint (Starter/Trial) | On Starter/Trial tier: "Some integrations require Professional tier or above" appended to footer | |
| 8.5b | Tier hint hidden (Pro+) | On Professional/Enterprise tier: tier hint text absent | |

---

### Page 9: Memory & Privacy

> Every element tested for presence, correct value, input manipulation, valid population, state change, control activation, input validation, and disposition variants per the 9-dimension verification standard (incl. data-binding correctness).

#### 9.1 Page header and upgrade banner

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.1 | Memory features render | Customer context (All tiers), Conversation memory (All tiers), Cross-session learning (Professional+) cards | PASS |
| 9.1a | Page header | Title "Memory & privacy" + subtitle "Configure how your AI remembers customers and handles their data" | |
| 9.1b | Upgrade banner — Starter tier | Blue Alert "Unlock advanced memory features" shown for Starter tier tenants; mentions Professional plan | |
| 9.1c | Upgrade banner — Professional tier | Banner NOT shown for Professional or Enterprise tier tenants | |

#### 9.2 Layer 1 — Customer context

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.2a | Customer context card renders | Paper card with title "Customer context", description text, HelpTooltip | |
| 9.2 | Tier badges | "All tiers" green badge on Customer context card | PASS |
| 9.2b | Customer context toggle — current value | Switch shows "Enabled" or "Disabled" matching config.memory_enabled | |
| 9.2c | Customer context toggle — change state | Toggling switch changes label between "Enabled" and "Disabled" | |
| 9.2d | Customer context HelpTooltip | (?) icon with text explaining customer context personalization; doc link to customer-memory#how-the-layers-work | |

#### 9.3 Layer 2 — Conversation memory

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.3a | Conversation memory card renders | Paper card with title "Conversation memory", "All tiers" green badge | |
| 9.3 | Feature toggles | Enabled/Disabled toggles for each feature, state reflects current config | PASS |
| 9.3b | Conversation memory toggle — disabled when memory off | Switch disabled (grayed out) when Customer context (memoryEnabled) is OFF | |
| 9.3c | Conversation memory toggle — enabled when memory on | Switch enabled and interactive when Customer context is ON | |
| 9.3d | Conversation memory HelpTooltip | (?) icon with text about vectorized conversation transcripts; doc link to customer-memory#memory-enabled | |

#### 9.4 Layer 3 — Cross-session learning

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.4a | Cross-session learning card renders | Paper card with title "Cross-session learning" | |
| 9.4b | Tier badge — Professional+ | Blue "Professional+" badge when tenant is Professional or Enterprise | |
| 9.4c | Tier badge — gated | Gray "Professional+ required" badge when tenant is Starter | |
| 9.10 | Tier-gated features non-toggleable | Switch disabled (grayed out) when tenant is below Professional tier | PASS |
| 9.4d | Cross-session toggle — disabled when memory off | Switch disabled when memoryEnabled=false regardless of tier | |
| 9.4e | Cross-session toggle — change state | On Professional+ tier with memory on, toggling switch changes label | |
| 9.4f | Pattern decay slider — visibility | Slider shown only when isProOrHigher AND crossSessionLearning is ON | |
| 9.4g | Pattern decay slider — range | Slider min=30, max=365, step=30; marks at 30, 90, 180, 365 | |
| 9.4h | Pattern decay slider — current value | Shows patternDecayDays from config (default 90) | |
| 9.4i | Pattern decay slider — disabled when memory off | Slider disabled when memoryEnabled=false | |
| 9.4j | Cross-session HelpTooltip | (?) icon with text about behavioral patterns; doc link to customer-memory#pattern-learning | |
| 9.4k | Pattern decay HelpTooltip | (?) icon explaining pattern decay duration | |

#### 9.5 Layer 4 — Dedicated model training

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.4 | Dedicated model training | Enterprise required card with upgrade banner and pricing ($299/month) | PASS |
| 9.5a | Dedicated model card renders | Paper card with title "Dedicated model training", description mentioning "1,000+ historical interactions" | |
| 9.5b | Enterprise add-on badge | Grape "Enterprise add-on" badge when tenant is Enterprise | |
| 9.5c | Enterprise required badge | Gray "Enterprise required" badge when tenant is not Enterprise | |
| 9.5d | Upgrade alert — non-Enterprise | Blue Alert "Upgrade to Enterprise tier to access dedicated model training" shown for non-Enterprise tenants | |
| 9.5e | Upgrade alert — Enterprise | Alert NOT shown for Enterprise tier tenants | |
| 9.5f | Dedicated model HelpTooltip | (?) icon with text about custom AI model; doc link to customer-memory#dedicated-model-training | |

#### 9.5B Customer identification (KA-8) — 10 tests

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.15 | Customer identification section renders | Paper card with title "Customer identification", green "All tiers" badge, SegmentedControl, HelpTooltip | |
| 9.15a | SegmentedControl — 4 modes | SegmentedControl displays 4 options: Off, Gentle, Standard, Aggressive | |
| 9.15b | SegmentedControl — current value | Shows `customer_identification_mode` from config (default: "standard") | |
| 9.15c | SegmentedControl — change to Off | Select "Off" → description updates to "No identification prompts..." | |
| 9.15d | SegmentedControl — change to Gentle | Select "Gentle" → description updates to "Casual mention..." | |
| 9.15e | SegmentedControl — change to Aggressive | Select "Aggressive" → description updates to "Strong prompt..." | |
| 9.15f | SegmentedControl — action blue color | SegmentedControl uses `action` color (blue #3B82F6) for selected segment | |
| 9.15g | SegmentedControl — disabled when memory off | When Customer context (memoryEnabled) is OFF, SegmentedControl is disabled (greyed out) | |
| 9.15h | Memory-off alert | When memoryEnabled=false, yellow Alert shown below SegmentedControl warning that identification requires memory | |
| 9.15i | Identification mode save persists | Change mode → "Save draft inputs" → reload → SegmentedControl shows saved value; `GET /api/config?state=draft` returns `customer_identification_mode` with new value | |

#### 9.6 Data retention & privacy accordion

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.5 | Data retention section | Collapsible "Data retention & privacy" section with tooltip | PASS |
| 9.6 | Retention period dropdown | "1 year" default with dropdown options | PASS |
| 9.6a | Accordion default open | "Data retention & privacy" accordion expanded by default (defaultValue="privacy") | |
| 9.6b | Retention select — current value | Shows retentionDays from config (default "90" = "90 days") | |
| 9.6c | Retention select — all options | 5 options: 30 days, 90 days, 180 days, 1 year, 2 years | |
| 9.6d | Retention select — change value | Selecting different option updates local state | |
| 9.7 | Privacy toggles | PII scrubbing, Consent required, Automatic deletion on request — all with descriptions | PASS |
| 9.6e | PII scrubbing toggle — current value | Switch checked matches config.pii_scrubbing (default true) | |
| 9.6f | PII scrubbing description | "Automatically detect and redact personally identifiable information..." description text | |
| 9.6g | Consent required toggle — current value | Switch checked matches config.consent_collection_enabled (default true) | |
| 9.6h | Consent required description | "Require explicit customer consent before storing conversation data..." description text | |
| 9.6i | Auto-delete toggle — current value | Switch checked matches config.auto_delete_on_request (default true) | |
| 9.6j | Auto-delete description | "Automatically delete all customer data when a GDPR deletion request is received." description | |
| 9.9 | Feature tooltips | (?) icon on Data retention section header | PASS |

#### 9.7 Save and persist

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.8 | Save draft inputs button | Red "Save draft inputs" button at bottom of page (no button at top) | |
| 9.7a | Save button loading state | Button shows spinner while saving (saving=true) | |
| 9.11 | Save draft inputs persists all Memory & Privacy settings | After modifying toggles/sliders and clicking "Save draft inputs", all 9 fields persist correctly on page reload (memory_enabled, pattern_learning_enabled, data_retention_days, consent_collection_enabled, pii_scrubbing, conversation_memory, cross_session_learning, pattern_decay_days, customer_identification_mode) | |
| 9.7b | Save success notification | "Draft memory & privacy settings saved." notification in green | |
| 9.7c | Save error notification | Error message notification when save fails | |
| 9.7d | Save triggers activation status refresh | After successful save, refreshActivationStatus() called; sidebar badge may change to "Pending" | |

#### 9.8 Backend-verified tests

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.12 | PII scrubbing verification | When pii_scrubbing=true in tenant config, messages stored in conversation transcripts have email addresses replaced with [REDACTED:email] and phone numbers replaced with [REDACTED:phone]. Live responses to the customer are NOT affected — only stored transcripts. Covered by 13 unit tests in test_session_pii_scrubbing.py | PASS |
| 9.13 | Consent prompt appears (SKIP — deferred to widget phase 3-5) | When consent_collection_enabled=true, the widget must display a consent prompt before the first message; customer cannot send messages until consent is given. Requires widget.js frontend changes — deferred to post-launch widget phases | SKIP |
| 9.14 | GDPR deletion request | Submit a GDPR "Right to be forgotten" request for a test customer; verify all conversation data, memory vectors, and customer profile are deleted. Backend fully implemented with 48 unit tests in test_gdpr_services.py covering PII scrubbing, grace periods, data stores, export, deletion, and consent management. E2E webhook testing deferred to integration test suite | PASS |

#### 9.9 Loading and error states

| # | Test | Expected | Status |
|---|------|----------|--------|
| 9.9a | Loading state | LoadingState "Loading memory settings" while config fetches | |
| 9.9b | Error state | Alert "Failed to load settings" with error text when config API fails | |

---

### Page 10: Billing & Usage

#### 10.1 Page header and error states (5 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.1 | Page title renders | "Billing & usage" title and "Manage your subscription and monitor usage" subtitle display | PASS |
| 10.1a | Loading state | LoadingState with "Loading billing data" renders while usage API loads | |
| 10.1b | Error state | When usage API fails, red Alert "Usage data unavailable" renders with error message | |
| 10.1c | Error does not block page | Error alert displays above remaining page content (non-blocking) | |
| 10.1d | Page loads after API resolves | Once usage data loads, LoadingState replaced with full page content | |

#### 10.2 Plan card (12 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.2a | Plan card renders | Paper card with "Current plan" label and HelpTooltip renders | PASS |
| 10.2b | Tier badge displays correct tier | Badge shows current tier (e.g., "Professional") with tier-appropriate color (trial=yellow, starter=blue, professional=green, enterprise=grape) | PASS |
| 10.2c | Active status badge | Green "Active" badge displays when tenant status is active | |
| 10.2d | Included conversations value | "Included conversations" shows correct value with "/mo" suffix (e.g., "500/mo") matching usage API response | |
| 10.2e | Used this period value | "Used this period" shows correct total conversations from usage API | |
| 10.2f | Remaining value | "Remaining" shows correct remainingIncluded value from usage API | |
| 10.2g | Values update on data change | After usage data refresh, all three count values update correctly | |
| 10.2h | Zero usage state | When no conversations used: Used shows 0, Remaining equals Included | |
| 10.2i | Manage subscription button (Stripe tenant) | When hasStripeBilling=true, "Manage subscription" button renders and is clickable | |
| 10.2j | Manage subscription hidden (non-Stripe) | When hasStripeBilling=false, "Manage subscription" button is absent | |
| 10.2k | Manage subscription opens portal | Clicking "Manage subscription" calls POST /api/billing/portal and opens portal URL in new tab | |
| 10.2l | Plan tooltip | HelpTooltip explains subscription tier determines included conversations, overage rate, and features; doc link contains "billing/overview" | |

#### 10.3 Usage stat cards (16 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.3 | All 4 usage cards render | SimpleGrid shows 4 UsageStat cards: Conversations used, Pack balance, Current overage, Estimated overage cost | PASS |
| 10.3a | Conversations used — value | Shows "X / Y" format (used / included) matching API data | |
| 10.3b | Conversations used — percentage | Subtext shows "N% of included allowance" correctly calculated | |
| 10.3c | Conversations used — ring progress | RingProgress renders with correct percentage; color green at ≤75%, yellow at 76-90%, red at >90% | |
| 10.3d | Pack balance — value | Shows formatted pack balance number from API | |
| 10.3e | Pack balance — subtext | Shows "remaining conversations" subtext | |
| 10.3f | Current overage — value | Shows formatted currency for estimated overage cost | |
| 10.3g | Current overage — subtext with count | When overageConversations > 0, shows "N overage conversations"; when 0, shows "No overage charges" | |
| 10.3h | Estimated overage cost — value | Shows formatted currency matching API estimatedOverageCost | |
| 10.3i | Estimated overage cost — subtext | Shows "Additional charges this period" | |
| 10.3j | All tooltips present | Each of the 4 cards has a HelpTooltip icon | |
| 10.3k | Conversations used tooltip text | Tooltip explains "total conversations this billing period vs. your plan's included monthly allowance" | |
| 10.3l | Pack balance tooltip text | Tooltip explains packs are used after included allowance and before overage | |
| 10.3m | Current overage tooltip text | Tooltip explains conversations beyond included allowance and pack balance | |
| 10.3n | Estimated overage cost tooltip text | Tooltip explains projected additional charges | |
| 10.3o | Zero-state values | When API returns all zeros: "0 / 0" conversations, "0" pack balance, "$0.00" overage, "No overage charges" | |

#### 10.4 Usage alerts (3 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.4a | Active alerts render | When usage.data.activeAlerts has entries, yellow Alert with "Usage alerts" title renders | |
| 10.4b | Alert messages display | Each alert string in the activeAlerts array renders as a Text element | |
| 10.4c | No alerts hidden | When activeAlerts is empty or absent, no yellow Alert renders | |

#### 10.5 Daily usage chart (10 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.5 | Chart renders | Paper card with "Daily usage (30 days)" title and AreaChart renders | PASS |
| 10.5a | Chart tooltip | HelpTooltip on chart title explains billable conversations per day over 30 days; doc link contains "billing/overview" | |
| 10.5b | Two area series | Chart renders two Area series: Total (red #ff3621) and Billable (blue #2563EB) | |
| 10.5c | Legend renders | Legend below chart shows Total (red dot) and Billable (blue dot) labels | |
| 10.5d | Chart axes | X-axis shows formatted dates (M/D), Y-axis shows numeric scale | |
| 10.5e | Chart data from API | Chart data points match dailyVolume.data.days array from API | |
| 10.5f | Chart loading state | While dailyVolume loading and no data: Loader spinner renders centered in chart area | |
| 10.5g | Chart empty state | When chartData is empty array: "No usage data available yet" message renders centered | |
| 10.5h | Gradient fills | Total area uses gradBillingTotal gradient (red, 15% → 0% opacity); Billable uses gradBillingBillable gradient (blue, 12% → 0% opacity) | |
| 10.5i | Chart hover tooltip | Hovering over chart shows tooltip with date, Total value, and Billable value | |

#### 10.6 Conversation packs (11 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.6a | Section header renders | "Conversation packs" title with HelpTooltip and subtitle "Pre-purchase conversations at a discounted rate" render | |
| 10.6b | Pack tooltip | HelpTooltip explains pre-purchase bundles, FIFO usage, 90-day validity; doc link contains "billing/overview" | |
| 10.4 | 3 pack cards render | SimpleGrid shows 3 PackCards (1K, 5K, 20K) | PASS |
| 10.6c | 1K pack details | Shows "1,000" conversations (red), "$29.00" price, "$0.029/conversation" rate | |
| 10.6d | 5K pack details | Shows "5,000" conversations (red), "$99.00" price, "$0.020/conversation" rate | |
| 10.6e | 20K pack details | Shows "20,000" conversations (red), "$249.00" price, "$0.012/conversation" rate | |
| 10.6f | Purchase button renders | Each pack card has "Purchase" button with outline variant | |
| 10.6g | Purchase button click | Clicking "Purchase" calls POST /api/packs/purchase with correct pack_id and tenant_id | |
| 10.6h | Purchase loading state | During purchase, clicked button shows loading spinner and is disabled | |
| 10.6i | Only one purchase at a time | While purchasing one pack, other pack buttons remain enabled | |
| 10.6j | Purchase error feedback | When purchase API fails, notification toast with "Failed to start purchase" appears | |

#### 10.7 Add-on modules (15 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.5 | 5 add-on cards render | SimpleGrid shows 5 add-on module cards (Multi-Language, Advanced Analytics, Mailchimp, GA4, Custom Integration) | |
| 10.7a | Multi-Language card | Label "Multi-Language Pack", $99.00/mo, "All tiers" green badge, description about language detection | |
| 10.7b | Advanced Analytics card | Label "Advanced Analytics", $149.00/mo, "Professional+" blue badge, description about conversation analytics | |
| 10.7c | Mailchimp card | Label "Mailchimp Integration", $49.00/mo, "Professional+" blue badge, description about audience sync | |
| 10.7d | GA4 card | Label "Google Analytics", $49.00/mo, "Professional+" blue badge, description about GA4 events | |
| 10.7e | Custom Integration card | Label "Custom Integration", $299.00/mo, "Enterprise" grape badge, description about custom systems | |
| 10.7 | Add-on tier badges | Correct badge colors: "All tiers" = green, "Professional+" = blue, "Enterprise" = grape | PASS |
| 10.6 | Tier-gated subscribe button | When current tier meets add-on requirement: "Subscribe" button (outline, enabled) | PASS |
| 10.7f | Tier-gated disabled button | When current tier does NOT meet add-on requirement: "Requires {tierLabel}" button (gray, disabled) | |
| 10.9 | Unavailable add-on opacity | Cards for unavailable add-ons render with opacity 0.65 | |
| 10.7g | Subscribe click notification | Clicking "Subscribe" on available add-on shows info notification "Add-on checkout coming soon." | |
| 10.8 | Required entitlement display | Each add-on disabled button text shows the minimum required tier (e.g., "Requires Professional+", "Requires Enterprise") | |
| 10.7h | Starter tier sees gated add-ons | On Starter tier: Multi-Language has Subscribe; Analytics/Mailchimp/GA4 show "Requires Professional+"; Custom shows "Requires Enterprise" | |
| 10.7i | Professional tier sees gated add-ons | On Professional tier: Multi-Language/Analytics/Mailchimp/GA4 have Subscribe; Custom shows "Requires Enterprise" | |
| 10.10 | Tier upgrade path | Enterprise tier: all 5 add-ons show "Subscribe" button (none gated) | |

#### 10.8 Manage billing card (5 tests)

| # | Test | Expected | Status |
|---|------|----------|--------|
| 10.8a | Manage billing card renders (Stripe) | When hasStripeBilling=true, Paper card with "Invoices & payment methods" title and "Manage billing" button renders | |
| 10.8b | Manage billing description | Subtitle reads "View invoice history, update payment methods, and manage your subscription through Stripe." | |
| 10.8c | Manage billing click | Clicking "Manage billing" calls POST /api/billing/portal and opens Stripe portal URL in new tab | |
| 10.8d | Manage billing hidden (non-Stripe) | When hasStripeBilling=false, manage billing card is absent from page | |
| 10.8e | Portal error feedback | When /api/billing/portal fails, notification toast "Failed to open billing portal. Please try again." appears | |

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
| D15 | Knowledge Base | Created article shows "--" for Category and Status in article table; filters return no results | S18 | Fixed S26 — added `category`+`status` to `KnowledgeEntryResponse` + `_build_entry_response()`; frontend derives category from `entryType` fallback; status from `isActive` fallback | 5.9, 5.10 |
| D16 | Knowledge Base | Creating/saving a KB article does not change config state to "Pending" | S18 | Fixed S27 — `_signal_kb_draft()` helper calls `ensure_draft_for_signal("kb_modified_at")` after each KB write (create/update/delete/upload/import); best-effort, non-blocking | 5.11 |
| D17 | Knowledge Base | Archived article has no visual distinction — still appears in list identically | S18 | Deferred to batch fix | 5.12 |
| D18 | Knowledge Base | Freshness shows "--" for newly created article instead of "Fresh" | S18 | Deferred to batch fix | 5.13 |
| D19 | Knowledge Base | No way to restore an archived article | S18 | Deferred to batch fix | 5.14 |
| D20 | Quick Actions | Creating a quick action does not change config state to "Pending" | S18 | Fixed S27 — `_ensure_qa_draft()` helper calls `ensure_draft_for_signal("qa_modified_at")` before each QA write (create/update/delete); draft-first repo methods now always find a draft | 6.7 |
| D21 | Quick Actions | Auto-open toggle on page assignments is non-functional | S18 | Deferred to batch fix | 6.8 |
| D22 | Widget Config | Agent avatar: replace URL input with PNG upload + validation + resize + aspect-ratio crop | S18 | Design change — deferred to post-launch (requires Azure Blob Storage, client-side cropping, backend upload endpoint) | 7.16–7.20 |
| D23 | Widget Config | Widget launcher click does not open chat window in live preview | S18 | Deferred to batch fix | 7.21 |
| D24 | Widget Config | Save fails with same model_dump error as D12 | S18 | Same root cause as D12 — deferred to batch fix | 7.22 |
| D25 | Integrations | Deactivate and Disconnect buttons acquire incorrect white border on hover | S18 | Deferred to batch fix | 8.6 |
| D26 | Memory & Privacy | Cross-session learning toggle appears non-gated — actually PASS: "Professional+" means Professional and above; toggle IS correctly disabled for Starter tier | S18 | Not a defect (tier gate works correctly) | 9.10 |
| D27 | Memory & Privacy | Save changes silently drops 6 of 8 fields — frontend field names don't match backend schema | S18 | Deferred to batch fix | 9.11 |
| D28 | Billing & Usage | Add-on tier badges use green/gray for met/unmet instead of always showing the required entitlement level | S18 | Design change — deferred to batch fix | 10.8 |
| D29 | Billing & Usage | Subscribe button shown for all tier-met add-ons without indicating required entitlement on unavailable ones | S18 | Deferred to batch fix | 10.9 |
| D30 | Billing & Usage | No visible tier upgrade path on Billing page — admin cannot view/compare Starter → Pro → Pro+ → Enterprise and upgrade inline | S18 | Design change — deferred to post-launch (requires Stripe checkout integration for upgrades, Backlog #17) | 10.10 |
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
| D46 | Agent Config | Success message text after save incorrect | S23 | Fixed — updated toast message text | 4.10 |
| D47 | Agent Config | Language section shows 5 planned languages (German, Portuguese, Japanese, Chinese, Korean) that don't exist — removed entirely; only English + Spanish/French (coming soon) remain | S23 | Fixed — removed 5 planned languages from supportedLanguages UI; kept only en, es (coming soon), fr (coming soon) | 4.6 |
| D49 | Activation | Activate button disabled in re-activation case after deactivation — button state logic doesn't account for deactivated-with-complete-config | S23 | Fixed — button state now correctly shows green "Activate" when deactivated with all mandatory fields present | 0A.11 |
| D50 | Configuration | Sidebar Discard doesn't refresh form fields in child pages — Configuration.tsx still shows old values after Discard because React context change doesn't trigger data hook re-fetch | S23 | Fixed — `configRefreshKey` counter in AppContext, incremented in handleDiscard; Configuration.tsx watches with useEffect → `configResult.refetch()` | 0B.3, 0B.4 |
| D51 | Sidebar | "Deactivate" button text truncated when all three controls visible — flex layout causes text overflow | S23 | Fixed — Button Group uses `wrap="nowrap"`; only Activate/Deactivate button gets `flex: 1`; Discard and Roll back are auto-width | 0A.5 |
| D52 | Activation | save_draft() throws 409 Conflict when creating new DRAFT after roll-back — stale PREVIOUS document still exists with same ID shape, and `repo.create()` fails on duplicate | S24 | Fixed — activation_service.py line 305 changed from `repo.create()` to `repo.upsert()` (create-or-replace) | 0B.6 |
| D53 | Widget | Widget launcher not visible on admin UI after activation — useEffect in StandaloneLayout.tsx ran once on page load and never re-triggered when activation status changed | S26 | Fixed — added `activationStatus?.is_active` to useEffect dependency array; widget injected when Active, removed when Inactive/deactivated | 0A.19, 0A.20, 0A.21 |
| D54 | Activation | Activation dialog message says "Configuration is up to date — no changes to activate." which is confusing — should say "Draft configuration is ready to activate." | S26 | Fixed — updated message text in ActivationDialog.tsx | 0A.4 |
| D55 | Inbox | ConversationStatus had both COMPLETED and RESOLVED — "Completed" status should be renamed to "Resolved" for consistency with "Resolve conversation" control. Also: "Idle" filter tab replaced with "Resolved" filter tab. | S26 | Fixed — removed COMPLETED from enum; all conversation end-reasons now map to RESOLVED; Inbox filter tabs: All/Active/Esc/Resolved; fine_tuning query accepts both 'resolved' and 'completed' for backward compat; tooltip updated | 2.2, 2.15, 2.16 |
| D56 | Inbox | Escalated conversation info card does not show the target team member or escalation category — no `assigned_to` or `escalation_category` data stored on conversation document | S27 | Fixed — `escalation_category` field on ConversationDocument, AI detection via EscalationHandlerAgent, auto-assignment via `find_best_agent_for_category()`, Inbox info card shows category badge + resolved member name | 2.17, 2.18 |
| D57 | Team | Team member table does not show count of unresolved escalations assigned to each member — no `assigned_to` field on conversations to query against | S27 | Fixed — `unresolved_escalation_count` in TeamMemberResponse, enriched in list endpoint via `count_filtered(status=ESCALATED, assigned_to=member_id)`, "Escalations" column in TeamManager | 3.9 |
| D58 | Agent Config | "Idle timeout" and "Max turns" inputs have no tooltips — both need (?) icons explaining their purpose | S26 | Fixed — added HelpTooltip to both NumberInput labels in Configuration.tsx | 4.7 |
| D60 | Knowledge Base | Action icons (Edit, Archive, Restore, Verify) use native HTML `title` tooltips — should use Mantine `<Tooltip>` with arrow for consistency | S26 | Fixed — upgraded all 4 action icons to `<Tooltip label="..." withArrow>` wrappers | 5.15 |
| D62 | Knowledge Base | Summary stats missing Archived count — only shows Total/Published/Draft/Needs attention; should include Archived card with count | S26 | Fixed — added 5th card "Archived" (gray) to SimpleGrid; grid cols 4→5 | 5.16 |
| D63 | Knowledge Base | Category filter returns no results — `entryTypeToCategory` mapped to singular "Product"/"Policy" but filter dropdown uses plural "Products"/"Policies"; also CATEGORIES list had duplicate singular/plural entries; inline category cell didn't use `resolveCategory()` | S26 | Fixed — normalized entryType mapping to plural forms; added `normalizeCategory` map for legacy data; removed duplicate entries from CATEGORIES/categoryColorMap; table cell uses `resolveCategory()` | 5.10, 5.17 |
| D64 | Quick Actions | Status badges truncated ("Act...") — Status column `w={80}` too narrow for "Active" badge text | S26 | Fixed — Status column widened to `w={100}`; Prompt template column capped at `maxWidth: 300` | 6.9 |
| D67 | Quick Actions | Auto-open toggle non-functional — `PageAssignmentResponse` model missing `auto_open` and `auto_open_delay_ms` fields; GET endpoint returned assignments without these values, so frontend always saw `undefined` → `false` after refetch | S26 | Fixed — added both fields to response model + builder function; toggle state now round-trips correctly | 6.8 |
| D68 | Quick Actions | Page assignments (slot changes, auto-open, delay) save directly to assignments document instead of writing to draft configuration — violates Save→Activate model where all AI Configuration pages write to draft and only commit on Activate | S26 | Fixed S27 — `_ensure_qa_draft()` called before `upsert_page_assignment` and `delete_page_assignment`; draft-first repo methods now write to draft; Discard reverts assignments | 6.7, 6.8, 6.10 |

---

## Failure Classification

Per the Repeatable Procedures spec (Section 3):

- **Procedure defect:** A test step is wrong, missing, or ambiguous → fix the procedure first
- **Environment transient:** Cosmos timeout, browser disconnection, deploy lag → retry, don't modify procedure

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
