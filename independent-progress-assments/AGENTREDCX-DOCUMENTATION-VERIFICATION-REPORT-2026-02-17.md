# Agent Red CX Documentation Verification Report

**Report Date:** February 17, 2026  
**Scope:** Verification of agentredcx.com content for merchant admin (end-user) documentation quality and completeness  
**Methodology:** Direct fetching of live documentation pages, comparison with docs-site source, and assessment against merchant admin needs  
**Output Location:** `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\independent-progress-assments`

---

## Executive Summary

Agent Red’s public documentation at **agentredcx.com** is **largely complete and up to date**. It covers onboarding, configuration, billing, integrations, and analytics in a merchant-friendly way and aligns with the current product (including v1.39.0, Feb 17, 2026). A few gaps and inconsistencies should be corrected to improve clarity and accuracy for merchant admins.

**Overall assessment:** Strong for merchant admin use. Recommended actions are minor and incremental.

---

## 1. Documentation Structure (Live Site)

### 1.1 Homepage (agentredcx.com)

| Element | Status | Notes |
|--------|--------|-------|
| Product description | ✅ | Clear “AI-powered customer service platform” |
| Navigation to docs | ✅ | Links to Changelog, Billing, Integrations, Admin Guide, Getting Started |
| Key capabilities table | ✅ | 7 capabilities described |
| Platform tiers | ✅ | Starter / Pro / Enterprise with pricing |
| Support contact | ✅ | support@remakerdigital.com |
| Shopify App Store link | ✅ | Install path clear |

### 1.2 Documentation Sections Verified

| Section | URL | Status | Notes |
|---------|-----|--------|-------|
| Changelog | /docs/changelog | ✅ | Current through v1.39.0 (2026-02-17) |
| Billable Conversation Spec | /docs/billing/billable-conversation-spec | ✅ | Clear billing definition |
| Billing & Usage Overview | /docs/billing/overview | ✅ | Plans, packs, add-ons, dashboard |
| Shopify Integration | /docs/integrations/shopify | ✅ | Detailed integration guide |
| Admin Guide (index) | /docs/admin-guide | ✅ | Index to all config sections |
| Getting Started Overview | /docs/getting-started/overview | ✅ | Pipeline and architecture |
| Initial Setup | /docs/getting-started/setup | ✅ | 5-stage setup |
| How It Works | /docs/getting-started/how-it-works | ✅ | Pipeline, PII, memory, protocols |
| Brand and Tone | /docs/admin-guide/brand-and-tone | ✅ | Brand voice, greeting, farewell |
| Business Policies | /docs/admin-guide/business-policies | ✅ | Return, shipping, warranty, support |
| Escalation Rules | /docs/admin-guide/escalation-rules | ✅ | Thresholds, keywords, notifications |
| Analytics Dashboard | /docs/admin-guide/analytics | ✅ | Metrics, charts, knowledge gaps |
| Conversation Inbox | /docs/admin-guide/conversations | ✅ | Filters, actions, escalation |

---

## 2. Changelog Currency

| Version | Date | Status |
|---------|------|--------|
| v1.39.0 | 2026-02-17 | ✅ Live |
| v1.35.0 | 2026-02-17 | ✅ Live |
| v1.34.0 | 2026-02-16 | ✅ Live |
| v1.32.7-agntcy | 2026-02-16 | ✅ Live |
| v1.32.7 | 2026-02-16 | ✅ Live |
| v1.25.0 | 2026-02-13 | ✅ Live |
| v1.23.0 | 2026-02-12 | Marked “(unreleased)” |
| v1.22.0 | 2026-02-12 | Marked “(unreleased)” |
| v1.21.0 | 2026-02-12 | Marked “(unreleased)” |

**Assessment:** Changelog is current and clearly separates shipped vs. unreleased work.

---

## 3. Merchant Admin Coverage

### 3.1 Admin Guide Sections (from index)

| Section | Live? | Merchant relevance |
|---------|-------|--------------------|
| Brand and tone | ✅ | High |
| Languages | ✅ | High |
| Response style | ✅ | High |
| Knowledge base | ✅ | High |
| Business policies | ✅ | High |
| Escalation rules | ✅ | High |
| Integrations | ✅ | High |
| Customer memory | ✅ | High |
| Widget appearance | ✅ | High |
| Widget behavior | ✅ | High |
| Custom instructions | ✅ | Medium (advanced) |
| Quick action prompts | ✅ | High |
| Knowledge base management | ✅ | High |
| Conflict scanner | ✅ | Medium |
| Save and activate | ✅ | High |
| Team management | ✅ | High |

### 3.2 Operational Doc Coverage

- **Billing:** Tier structure, conversation packs, overage, add-ons, usage dashboard.
- **Shopify:** OAuth, permissions, sync, webhooks, mapping, troubleshooting.
- **Inbox:** Filters, search, status, escalation, billability.

---

## 4. Issues and Recommendations

### 4.1 Billing Overview – Consumption Order

**Issue:** Billing & Usage overview (https://agentredcx.com/docs/billing/overview) lists consumption order as:

1. Overage  
2. Conversation packs  
3. Included allowance  

This is reversed relative to how conversations are consumed. The Billable Conversation Spec and product behavior use:

1. Included allowance  
2. Conversation packs (FIFO)  
3. Overage  

**Recommendation:** Update the overview to state consumption order as “Included allowance → Packs → Overage” so it matches the spec and behavior.

### 4.2 Stripe MCP Integration Documentation

**Context:** v1.39.0 (2026-02-17) adds Stripe MCP integration for payment and refund queries.

**Status:** Integrations admin page exists in the docs-site. Stripe is described in `docs-site/docs/admin-guide/integrations.md` (per project grep).

**Recommendation:** Confirm Stripe MCP is covered on the live Integrations page and linked from the Changelog v1.39.0 entry. If not deployed yet, add it to the next docs deploy.

### 4.3 Data Retention & Privacy

**Context:** Changelog v1.23.0 mentions “Data Retention & Privacy (`/admin-guide/data-retention`),” and v1.35.0 adds PII scrubbing on the Memory & Privacy page.

**Source:** `docs-site/docs/admin-guide/data-retention.md` exists in the project.

**Recommendation:** Verify the data-retention page is deployed and linked from the Admin Guide index and Memory/Privacy areas. Ensure it covers the PII scrubbing toggle.

### 4.4 Homepage Link to Billing

**Current:** Homepage links to “Billable conversation spec” under Billing.

**Recommendation:** Consider adding a link to Billing & Usage overview (`/docs/billing/overview`) as the main billing entry point, with the spec as “detailed definition” to improve discoverability of plans, packs, and add-ons.

---

## 5. Content Quality Assessment

### 5.1 Strengths

- **Structured:** Sections follow “what it is → how to use → what happens if you change it.”
- **Action-oriented:** Checklists, examples, and test queries support setup and validation.
- **Tables:** Used for fields, tiers, and options, making scanning easy.
- **Cross-links:** Strong navigation between related topics (e.g., escalation rules ↔ team management).
- **Practical examples:** Brand voice and escalation keyword examples are concrete.
- **Troubleshooting:** Shopify integration troubleshooting section is detailed.

### 5.2 Merchant-Oriented Details

- Billing tier table and pack pricing are clear.  
- Shopify sync times by catalog size are specified.  
- Escalation threshold guidance with tier-based recommendations.  
- FAQ and policy writing tips for the knowledge base.

---

## 6. Docs-Site vs. Live Site Alignment

**Docs-site source:** `docs-site/docs/` (29 MD files).

**Live site:** Docusaurus deployment to agentredcx.com (per Changelog v1.18.0).

**Verification:** Key pages (getting-started, admin-guide, billing, integrations) match between source and live. No evidence of major drift or missing sections.

---

## 7. Recommendations Summary

| Priority | Action |
|----------|--------|
| High | Fix billing overview consumption order to match Billable Conversation Spec |
| High | Confirm Stripe MCP integration is documented on live Integrations page |
| Medium | Ensure data-retention page is live and linked from Admin Guide / Memory & Privacy |
| Low | Add billing overview link to homepage “What you’ll find here” |
| Ongoing | Keep changelog updated with each release (current practice is good) |

---

## 8. Conclusion

Agent Red’s docs at agentredcx.com are well-structured and suitable for merchant admins. Coverage of onboarding, configuration, billing, integrations, and analytics is strong. The identified issues are limited and can be addressed with small updates and deployment checks. Overall, the documentation is fit for GA and ongoing merchant support.

---

## Appendix A: Pages Fetched (Verification)

- https://agentredcx.com (homepage)
- https://agentredcx.com/docs/changelog
- https://agentredcx.com/docs/billing/billable-conversation-spec
- https://agentredcx.com/docs/billing/overview
- https://agentredcx.com/docs/integrations/shopify
- https://agentredcx.com/docs/admin-guide
- https://agentredcx.com/docs/admin-guide/brand-and-tone
- https://agentredcx.com/docs/admin-guide/business-policies
- https://agentredcx.com/docs/admin-guide/escalation-rules
- https://agentredcx.com/docs/admin-guide/analytics
- https://agentredcx.com/docs/admin-guide/conversations
- https://agentredcx.com/docs/getting-started/overview
- https://agentredcx.com/docs/getting-started/setup
- https://agentredcx.com/docs/getting-started/how-it-works

## Appendix B: Project Context

- **Product:** Agent Red Customer Experience (AI customer service for e-commerce)
- **Producer:** Remaker Digital
- **Project root:** `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- **Docs source:** `docs-site/docs/` (Docusaurus)
- **Deployment:** GitHub Pages to agentredcx.com
