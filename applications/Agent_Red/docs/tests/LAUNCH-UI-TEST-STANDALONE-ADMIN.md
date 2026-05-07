# Launch UI Test — Standalone Admin

> **Test ID:** LUIT-SA
> **Status:** Draft — pending implementation of prerequisite capabilities
> **Author:** Mazel (UX consultant), revised by engineering
> **Created:** 2026-02-08
> **Scope:** End-to-end UX workflow validation of the standalone admin interface
> **Gate:** Must pass before Shopify App Store submission (per SHOPIFY-APP-REVIEW-PREFLIGHT-CHECKLIST.md)
> **Execution:** Manual, browser-based (Chrome), with live production backend

---

## Purpose

Validates the complete merchant journey through the standalone admin interface:
authentication → dashboard → knowledge base management → analytics → AI configuration
→ widget customization → inbox management → billing → team management → integrations
→ setup wizard → Test Mode controlled rollout → chat verification → session management.

This test exercises every page, every major interaction, and the full Test Mode lifecycle
(first-time setup → production → test rollout → rollout/abandon).

---

## Prerequisites

### Environment
- [ ] Standalone admin URL accessible: `https://agent-red-api-gateway.lemonriver-f59f94b7.eastus2.azurecontainerapps.io/admin/standalone/`
- [ ] API Gateway running with healthy `/health` and `/ready` endpoints
- [ ] Azure OpenAI endpoint configured and responsive
- [ ] Cosmos DB tenant provisioned with test data
- [ ] Stripe test mode configured (for conversation pack purchase)

### Credentials (from `.env.local`)
- [ ] `ADMIN_PREVIEW_PASSWORD` — standalone password gate
- [ ] `ADMIN_PREVIEW_API_KEY` — API key for tenant authentication

### Pre-seeded Data
- [ ] At least one conversation exists in the inbox
- [ ] At least one KB article exists
- [ ] A team member named "Test" exists (email: any valid email)
- [ ] Knowledge base seeded with pricing/product data (for chat KB hit test)

### Test Files
- [ ] `tests/rag-documents-upload/PDF-document.pdf`
- [ ] `tests/rag-documents-upload/DOCX-document.docx`
- [ ] `tests/rag-documents-upload/CSV-document.csv`
- [ ] `tests/rag-documents-upload/TEXT-document.txt`

---

## Capability Dependencies

The following capabilities must be implemented before this test can execute.
Each is tagged with an implementation status.

| # | Capability | Status | Notes |
|---|-----------|--------|-------|
| C1 | Test Mode global toggle + sticky nav display | **Not implemented** | Global state, UI component, session routing |
| C2 | Test Mode controlled rollout (% routing, roll-out/abandon) | **Not implemented** | A/B routing engine, wizard integration |
| C3 | Named configuration lifecycle (Default undeletable) | **Not implemented** | Backend: named config CRUD; Frontend: activate/delete flows |
| C4 | Named widget appearance lifecycle (Default undeletable) | **Not implemented** | Same pattern as C3 for widget config |
| C5 | URL import into Knowledge Base (single page + crawl option) | **Not implemented** | Scraping service, chunking, admin UI |
| C6 | "Powered by Agent Red" toggle (tier-gated) | **Not implemented** | Widget config field, tier check, upgrade prompt |
| C7 | "Report an Issue" widget button (customer-facing) | **Not implemented** | Widget component, issue type selector, submission flow |
| C8 | Conversation escalation action from Inbox | **Partial** | Backend `POST /{id}/assign` exists; escalation action + UI needed |
| C9 | Conversation search + mark resolved from Inbox | **Partial** | Search UI exists; "mark resolved" status update needs wiring |
| C10 | Integrations page (configure/activate/deactivate/delete) | **Not implemented** | New admin page + backend management endpoints |
| C11 | Integrations step in Setup Wizard | **Not implemented** | New wizard step |
| C12 | Setup Wizard: full validation, help links, tooltips on all steps | **Partial** | Basic stepper exists; validation, links, tooltips incomplete |
| C13 | Setup Wizard: "Review and Launch" step with test population % | **Not implemented** | New wizard step + Test Mode activation flow |
| C14 | Setup Wizard: input locking during active Test Mode | **Not implemented** | Overlay/disabled state for non-AI-behavior fields |
| C15 | Conversation pack purchase flow in admin UI (Stripe test checkout) | **Partial** | Backend exists; admin UI purchase flow not wired |
| C16 | Test Mode / Production selector as wizard step 1 | **Not implemented** | Available only after first Production config exists |

---

## Test Steps

### Section 1: Authentication (LUIT-SA-01 to LUIT-SA-04)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-01 | Open the standalone admin URL in Chrome | Password gate login page renders with correct brand logo (wide logo with wordmark, 200px width) and "Customer Experience Admin" subtitle |
| LUIT-SA-02 | Enter `ADMIN_PREVIEW_PASSWORD` from `.env.local` and submit | Password accepted, redirected to API key login page |
| LUIT-SA-03 | Enter `ADMIN_PREVIEW_API_KEY` from `.env.local` and submit | API key accepted, redirected to dashboard |
| LUIT-SA-04 | Confirm dashboard loads without errors | Dashboard page renders. No console errors. Stat cards, charts, and data areas visible (empty state with zeros/placeholders is OK) |

### Section 2: Dashboard (LUIT-SA-05 to LUIT-SA-08)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-05 | Verify dashboard displays tenant-scoped data | Data shown is scoped to the authenticated tenant (not cross-tenant). Empty state displays zeros or "No data yet" messages |
| LUIT-SA-06 | Verify brand name and logo in header | Brand logo (AR monogram + "agent red" wordmark) displayed prominently in the sidebar/header. "Customer Experience" product name visible |
| LUIT-SA-07 | Verify Test Mode toggle in sticky nav bar area | Test Mode toggle is visible in the sticky navigation area. Toggle shows "Off" / not enabled. **Dependency: C1** |
| LUIT-SA-08 | Wait for chat widget to auto-open, then close it | Chat widget launcher appears (bottom-right). Widget auto-opens after configured delay. Close the widget panel. Widget collapses to launcher button |

### Section 3: Knowledge Base (LUIT-SA-09 to LUIT-SA-16)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-09 | Navigate to Knowledge Base page | KB page loads with article list (may include pre-seeded articles) |
| LUIT-SA-10 | Add a brief test article (title: "Test Article", content: "This is a test KB entry") | Article creation form accepts input. Article saves successfully. Success feedback displayed |
| LUIT-SA-11 | Verify test article appears in list, edit it, then delete it | Article visible in list. Edit modal opens with correct content. Edit saves. Delete confirms and removes article from list |
| LUIT-SA-12 | Import `PDF-document.pdf` via file upload | Upload accepted. Processing indicator shown. PDF content parsed and appears as KB entry/entries |
| LUIT-SA-13 | Import `DOCX-document.docx` via file upload | Upload accepted. DOCX content parsed and appears as KB entry/entries |
| LUIT-SA-14 | Import `CSV-document.csv` via file upload | Upload accepted. CSV content parsed and appears as KB entry/entries |
| LUIT-SA-15 | Import `TEXT-document.txt` via file upload | Upload accepted. TXT content appears as KB entry/entries |
| LUIT-SA-16 | Verify each imported document entry can be edited and deleted | Each entry: opens in edit modal, saves edits, confirms deletion, removed from list |
| LUIT-SA-17 | Import URL `https://remakerdigital.com` | URL import dialog offers choice: "Single page" or "Crawl site". Select one. Import processes. Content appears as KB entry/entries. **Dependency: C5** |
| LUIT-SA-18 | Verify imported URL entry can be edited and deleted | Entry opens in edit modal, saves edits, confirms deletion, removed from list |

### Section 4: Analytics (LUIT-SA-19 to LUIT-SA-23)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-19 | Navigate to Analytics page | Charts and data display areas render without errors. Time period selector visible |
| LUIT-SA-20 | Verify Test Mode toggle is visible and disabled | Test Mode toggle visible in sticky nav. Toggle is Off (disabled state) |
| LUIT-SA-21 | Change the time period for data display | Time period selector accepts new value (e.g., 7 days → 30 days). Charts and data values update to reflect the selected period |
| LUIT-SA-22 | Enable Test Mode toggle | Data displayed changes to show Test Mode sessions only. Visual indicator confirms "Test Mode" filter is active. **Dependency: C1** |
| LUIT-SA-23 | Disable Test Mode toggle | Data returns to showing all sessions. Visual indicator confirms normal view restored |

### Section 5: Configuration (LUIT-SA-24 to LUIT-SA-35)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-24 | Navigate to Configuration page | Configuration page loads. "Active Configuration" shows name "Default" |
| LUIT-SA-25 | Verify all configuration fields render with correct values | All AI behavior fields (brand voice, formality, response length, escalation rules, custom instructions, etc.) display with current values |
| LUIT-SA-26 | Verify all fields accept new input/selection and validate | Change each field. Validation runs on blur/submit. Invalid input shows error message. Valid input accepted |
| LUIT-SA-27 | Verify "Powered by Agent Red" toggle | Toggle visible. On Starter/Professional tier: toggle disabled with upgrade prompt. On Enterprise tier: toggle functional. **Dependency: C6** |
| LUIT-SA-28 | Verify "Report an Issue" button in widget | Button visible at bottom of chat widget. Clicking opens issue type selector with selectable issue categories. Select an issue type and submit. Confirmation shown. **Dependency: C7** |
| LUIT-SA-29 | Save configuration with name "Test", confirm activation | Save dialog accepts name "Test". Configuration saved. Activation confirmation dialog appears. Confirm. "Test" is now the active configuration. **Dependency: C3** |
| LUIT-SA-30 | Select "Apply new configuration" | Dropdown/modal shows available configurations: "Test" and "Default". **Dependency: C3** |
| LUIT-SA-31 | Select "Restore to Default" and confirm activation | Confirmation dialog appears. Confirm. Active configuration changes to "Default". All fields revert to Default values |
| LUIT-SA-32 | Verify configuration restored to Default values | All fields match the original Default configuration values |
| LUIT-SA-33 | Select "Delete configuration" and delete "Test" | Deletion confirmation dialog. Confirm. "Test" removed from configuration list |
| LUIT-SA-34 | Attempt to delete "Default" configuration | Deletion blocked. Error message: "Default configuration cannot be deleted" or delete option not available for Default |

### Section 6: Widget Appearance (LUIT-SA-35 to LUIT-SA-41)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-35 | Navigate to Widget page | Widget page loads. "Selected appearance" shows "Default" |
| LUIT-SA-36 | Verify widget preview matches appearance selections | Live preview panel reflects current appearance settings (colors, position, theme). Changes to controls update preview in real-time |
| LUIT-SA-37 | Change appearance fields, validate, save as "Test", confirm activation | All fields accept input (brand color, position, theme, launcher icon, etc.). Save with name "Test". Activation confirmed. **Dependency: C4** |
| LUIT-SA-38 | Select "Select new appearance" | Options show "Test" and "Restore to Default" |
| LUIT-SA-39 | Select and confirm activation of "Default" | Default appearance activated. Widget preview updates to Default appearance |
| LUIT-SA-40 | Select "Delete appearance" and delete "Test" | Deletion confirmed. "Test" removed from appearance list |
| LUIT-SA-41 | Attempt to delete "Default" appearance | Deletion blocked. Error message: "Default appearance cannot be deleted" or delete option not available |

### Section 7: Inbox (LUIT-SA-42 to LUIT-SA-47)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-42 | Navigate to Inbox | Conversation list loads. Any Test Mode conversations are clearly marked (badge, icon, or label) |
| LUIT-SA-43 | Filter conversation list to "Test Mode" only | Filter control available. When applied, list shows only Test Mode conversations (or empty state if none exist). **Dependency: C1** |
| LUIT-SA-44 | Select a conversation and assign to an agent | Agent assignment UI available. Select agent from list/dropdown. Assignment confirmed. Conversation shows assigned agent. **Dependency: C8** |
| LUIT-SA-45 | Select a conversation and escalate to human | Escalation action available. Confirm escalation. Conversation marked as escalated. **Dependency: C8** |
| LUIT-SA-46 | Search for a conversation | Search input accepts query. Results filter in real-time or on submit. Matching conversation(s) displayed |
| LUIT-SA-47 | Select a conversation and mark it resolved | "Mark resolved" action available. Confirm. Conversation status changes to resolved. **Dependency: C9** |

### Section 8: Billing (LUIT-SA-48 to LUIT-SA-50)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-48 | Navigate to Billing | All data display areas visible: current plan, usage progress, conversation allowance, overage rate, invoice history |
| LUIT-SA-49 | Verify usage chart renders with correct data | Usage chart displays daily/monthly conversation counts. Values match dashboard data |
| LUIT-SA-50 | Purchase additional conversation pack | "Purchase conversations" action available. Pack options displayed (1K/5K/20K). Select a pack. Stripe test-mode checkout flow completes (use test card `4242 4242 4242 4242`). Return to admin with purchase confirmation. Pack balance updated. **Dependency: C15** |

### Section 9: Team Management (LUIT-SA-51 to LUIT-SA-53)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-51 | Navigate to Team | Team member list loads. Pre-seeded "Test" member visible |
| LUIT-SA-52 | Delete team member "Test" | Deletion confirmation dialog. Confirm. "Test" removed from member list |
| LUIT-SA-53 | Invite team member: name "Test", email `info@remakerdigital.com` | Invite form accepts name and email. Invitation sent. "Test" appears in member list with pending/invited status |

### Section 10: Integrations (LUIT-SA-54 to LUIT-SA-56)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-54 | Navigate to Integrations page | All available integrations listed: Shopify (connected), Zendesk, Mailchimp, Google Analytics. Each shows status and "Configure" option. **Dependency: C10** |
| LUIT-SA-55 | Select an integration, configure it, apply | Configuration form renders with integration-specific fields. Enter valid test values. Apply configuration. Integration status changes to configured/active |
| LUIT-SA-56 | Delete the integration configuration | Delete action available. Confirmation dialog. Confirm. Integration returns to unconfigured state |

### Section 11: Setup Wizard — First-Time Flow (LUIT-SA-57 to LUIT-SA-70)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-57 | Navigate to Setup Wizard | Wizard loads at step 1. **Test Mode selector is NOT available** (first-time setup). **Dependency: C16** |
| LUIT-SA-58 | Step: Brand and Tone | Brand name and voice/tone fields render. Change values. Validation passes. Click "Next" |
| LUIT-SA-59 | Step: Languages | Primary language selector visible. Additional languages multi-select available. Change both. Validation passes. Click "Next". **Dependency: C12** |
| LUIT-SA-60 | Step: Response Style | All response style inputs render (formality, length, emoji usage, etc.). Change values. Validation passes. Click "Next" |
| LUIT-SA-61 | Step: Knowledge Base — verify help | Help links point to documentation. Tooltips appear on hover for all fields. **Dependency: C12** |
| LUIT-SA-62 | Step: Knowledge Base — inputs | All KB configuration inputs render. Change values. Validation passes. Click "Next" |
| LUIT-SA-63 | Step: Business Policies — verify help | Help links point to documentation. Tooltips appear on hover for all fields. **Dependency: C12** |
| LUIT-SA-64 | Step: Business Policies — inputs | All policy inputs render. Change values. Validation passes. Click "Next" |
| LUIT-SA-65 | Step: Escalation Rules — verify rendering | Escalation settings and controls render properly |
| LUIT-SA-66 | Adjust Escalation Threshold | Threshold slider/input accepts new value. Value updates |
| LUIT-SA-67 | Disable Service escalation option | Toggle/checkbox for service escalation. Disable it. State changes to disabled |
| LUIT-SA-68 | Change support email and add keyword | Change notification email to `info@remakerdigital.com`. Add keyword "test" to escalation keywords. Click "Next" |
| LUIT-SA-69 | Step: Integrations | Integration activation controls render. Configured integrations can be activated. Unconfigured integrations show "Configure first" state and cannot be activated. Click "Next". **Dependency: C11** |
| LUIT-SA-70 | Step: Memory and Privacy | Memory layer options render (consent, history depth, etc.). Change values. Validation passes. Click "Next". **Dependency: C12** |

### Section 12: Chat Verification — Pre-Test-Mode (LUIT-SA-71 to LUIT-SA-75)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-71 | Open the chat widget | Widget opens. Chat panel visible. Greeting message displayed |
| LUIT-SA-72 | Send a KB-hitting message: "What is your pricing?" | Message sent. SSE streaming begins. Response streams in with accurate pricing information from the knowledge base. Streaming cursor visible during generation |
| LUIT-SA-73 | Send escalation message: "This is a support escalation test" | Message sent. AI processes. Response may acknowledge escalation trigger. Conversation flagged for escalation |
| LUIT-SA-74 | Close the chat widget | Widget panel closes. Launcher button remains visible |
| LUIT-SA-75 | Navigate to Inbox, open the escalation conversation | Conversation appears in inbox. Transcript shows both messages and AI responses. Metadata visible (timestamps, message count, escalation status). Conversation marked as escalated to support |

### Section 13: Setup Wizard — Review, Launch & Test Mode Activation (LUIT-SA-76 to LUIT-SA-86)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-76 | Navigate to Setup Wizard, reach "Review and Launch" step | Review step shows summary of all configuration choices. Values can be altered from this screen. **Dependency: C13** |
| LUIT-SA-77 | Enter Test population percentage: "10" | Input accepts numeric value "10". Validation passes (valid range, e.g., 1-50%) |
| LUIT-SA-78 | Click "Confirm" | Test population setting saved |
| LUIT-SA-79 | Activate Test Mode toggle and confirm in dialog | Confirmation dialog appears with warning about Test Mode implications. Click "Confirm". Click "Next" |
| LUIT-SA-80 | Verify Readiness message | Message contains warning that this will be Test Mode. States that 10% of new sessions will receive the test configuration. **Dependency: C2** |
| LUIT-SA-81 | Select "Activate AI Agent Test" and confirm | Confirmation dialog appears. Click "Confirm". Test Mode activates |
| LUIT-SA-82 | Verify activation state | "Activate AI Agent Test" button is replaced by message: "Test Mode Activated" |
| LUIT-SA-83 | Navigate through Setup Wizard steps | All non-AI-behavior inputs are locked/greyed/hidden behind a "Test Mode Active" overlay. AI behavior fields (brand voice, response style, escalation keywords) remain viewable but reflect the test configuration. **Dependency: C14** |

### Section 14: Chat Verification — During Test Mode (LUIT-SA-84 to LUIT-SA-88)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-84 | Open the chat widget | Widget opens. Chat panel visible |
| LUIT-SA-85 | Send a KB-hitting message: "What is your pricing?" | Message sent. SSE streaming. Response is accurate based on the (possibly modified) test configuration |
| LUIT-SA-86 | Close the chat widget | Widget closes |
| LUIT-SA-87 | Navigate to Inbox, open this conversation | Conversation visible. Transcript and metadata displayed. Conversation is tagged/marked as a Test Mode conversation |

### Section 15: Test Mode Deactivation (LUIT-SA-88 to LUIT-SA-91)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-88 | Switch Test Mode toggle to "Off" in sticky nav | Dialog appears with two options: "Roll out" (apply test config to 100% of sessions) and "Abandon" (revert to previous Production config). **Dependency: C2** |
| LUIT-SA-89 | Select "Abandon" and confirm | Test configuration discarded. Production configuration restored. All wizard inputs unlocked. Test Mode toggle shows "Off" |
| LUIT-SA-90 | Attempt to switch Test Mode toggle to "On" | User is automatically navigated to the Setup Wizard (since Test Mode requires going through the wizard flow). **Dependency: C16** |

### Section 16: Session Management (LUIT-SA-91 to LUIT-SA-93)

| ID | Step | Expected Result |
|----|------|-----------------|
| LUIT-SA-91 | Refresh the standalone admin page (F5) | Page reloads. Session persists — user remains authenticated on the dashboard (not returned to password gate) |
| LUIT-SA-92 | Log out (if logout button exists) or clear cookies manually | Session cleared |
| LUIT-SA-93 | Navigate to standalone admin URL | Password gate reappears. Full authentication flow required to re-enter |

---

## Test Result Summary

| Section | Steps | Pass | Fail | Blocked | Notes |
|---------|-------|------|------|---------|-------|
| 1. Authentication | 4 | | | | |
| 2. Dashboard | 4 | | | | |
| 3. Knowledge Base | 10 | | | | |
| 4. Analytics | 5 | | | | |
| 5. Configuration | 11 | | | | |
| 6. Widget Appearance | 7 | | | | |
| 7. Inbox | 6 | | | | |
| 8. Billing | 3 | | | | |
| 9. Team Management | 3 | | | | |
| 10. Integrations | 3 | | | | |
| 11. Setup Wizard | 14 | | | | |
| 12. Chat Pre-Test-Mode | 5 | | | | |
| 13. Review & Test Mode | 8 | | | | |
| 14. Chat During Test Mode | 4 | | | | |
| 15. Test Mode Deactivation | 3 | | | | |
| 16. Session Management | 3 | | | | |
| **Total** | **93** | | | | |

---

## Notes

- **Test Mode is not available on first-time wizard run.** The merchant must complete the
  wizard once to establish a Production configuration before Test Mode becomes available.
- **Test Mode only exposes AI behavior fields.** Structural settings (brand name, integrations,
  knowledge base content) are locked during Test Mode since they affect all users equally.
- **"Default" configuration/appearance cannot be deleted.** It serves as the immutable
  baseline that always exists.
- **"Powered by Agent Red" toggle is tier-gated.** Visible on all tiers; functional only on
  Enterprise tier (with White-Label add-on). Starter and Professional tiers see an upgrade prompt.
- **"Report an Issue" is customer-facing.** Allows end customers to submit structured issue
  reports to the merchant, distinct from the thumbs-up/down rating system.
- **URL import offers single-page or crawl options.** Merchant chooses scope; each scraped
  page becomes a separate KB entry.
- **Stripe test card for billing test:** `4242 4242 4242 4242`, any future expiry, any CVC.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
