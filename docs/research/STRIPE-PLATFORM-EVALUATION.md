# Stripe Platform Evaluation for Agent Red Customer Experience

> **Project:** Agent Red Customer Experience
> **Purpose:** Formal evaluation of Stripe as the e-commerce/billing platform for Phase 2.1
> **Date:** 2026-01-29
> **Scope:** 9 evaluation dimensions for B2B SaaS subscription billing
> **Decision:** Shopify vs Stripe (ref: PROJECT-PLAN.md Phase 2.1)
> **Data Note:** Stripe pricing and features documented here are based on publicly available information as of early 2026. All fees, percentages, and feature details should be verified against https://stripe.com/pricing and https://stripe.com/billing before final commitment. Items marked [VERIFY] require live confirmation.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [SaaS Subscription Capabilities](#2-saas-subscription-capabilities)
3. [Marketplace & Ecosystem](#3-marketplace--ecosystem)
4. [Partner Program](#4-partner-program)
5. [Competitor Landscape](#5-competitor-landscape)
6. [Costs](#6-costs)
7. [Developer Experience](#7-developer-experience)
8. [Tax & Compliance](#8-tax--compliance)
9. [Provisioning Integration](#9-provisioning-integration)
10. [Strategic Fit Assessment](#10-strategic-fit-assessment)
11. [Agent Red Pricing Model Mapping](#11-agent-red-pricing-model-mapping)
12. [Recommendation](#12-recommendation)

---

## 1. Executive Summary

Stripe is the dominant payment infrastructure platform for B2B SaaS companies. Stripe Billing provides native support for every billing model Agent Red requires: recurring subscriptions, metered/usage-based billing, tiered pricing, add-on modules, pre-purchased credit packs, annual vs. monthly billing, and self-service customer portals. Stripe is not a marketplace where customers discover products -- it is invisible infrastructure that powers checkout and billing behind your own website.

**Key findings:**

| Dimension | Assessment | Rating |
|-----------|------------|--------|
| SaaS Subscription Capabilities | Excellent -- native support for all Agent Red billing models | 5/5 |
| Marketplace & Discovery | None -- Stripe is infrastructure, not a storefront | 1/5 |
| Partner/Affiliate Program | No native affiliate program; requires third-party tools | 2/5 |
| Competitor Landscape | Industry standard -- all major SaaS competitors use Stripe | 5/5 |
| Costs | Competitive at 2.9% + $0.30 per transaction; Billing adds 0.5% | 4/5 |
| Developer Experience | Industry-leading APIs, SDKs, docs, CLI, test mode | 5/5 |
| Tax & Compliance | Stripe Tax handles automatic calculation; +0.5% per transaction | 4/5 |
| Provisioning Integration | Excellent webhook system for automated tenant provisioning | 5/5 |
| Strategic Fit | Strong -- standard infrastructure for SaaS, not a channel | 4/5 |

**Bottom line:** Stripe is the right billing infrastructure for Agent Red. It is not a customer acquisition channel (unlike Shopify App Store). These are complementary, not competing, choices -- but for a standalone SaaS product selling directly to customers, Stripe is the standard.

---

## 2. SaaS Subscription Capabilities

### 2.1 Overview

Stripe Billing (https://stripe.com/billing) is purpose-built for SaaS subscription management. It handles the full lifecycle: signup, trial, recurring charges, usage metering, upgrades, downgrades, cancellations, and dunning.

### 2.2 Capability Matrix for Agent Red

| Agent Red Requirement | Stripe Capability | API Object | Notes |
|----------------------|-------------------|------------|-------|
| **Recurring billing** (monthly) | Native | `Subscription` | Core feature. Automatic charge on billing cycle date. |
| **Annual billing** (17% discount) | Native | `Subscription` with `billing_cycle_anchor` | Create separate Price objects for monthly vs. annual. |
| **Tiered pricing** ($149/$399/$999) | Native | `Product` + multiple `Price` objects | One Product, three Prices (or three Products). |
| **Metered/usage billing** (overage) | Native | `Subscription Item` with `usage_type: metered` | Report usage via `Usage Record` API. Aggregate at billing cycle end. |
| **Add-on modules** ($49-$399) | Native | Additional `Subscription Items` | Add/remove items from an existing subscription mid-cycle. |
| **Conversation packs** (pre-purchase credits) | Supported via one-time charges or credit grants | `Invoice Item` (one-time) or `Customer Balance` | Not a native "credit pack" object -- requires application logic for tracking balance and 90-day expiration. |
| **Free trial** (14-day) | Native | `Subscription.trial_period_days` | Automatic transition to paid at trial end. No card required option available. |
| **Self-service portal** | Native | `Customer Portal` (Stripe-hosted) | Customers manage billing, update payment, change plans, cancel. Customizable branding. |
| **Upgrade/downgrade** | Native | `Subscription.update()` with proration | Automatic proration calculations. Immediate or end-of-cycle options. |
| **Dunning (failed payments)** | Native | Smart Retries + configurable dunning | Machine-learning optimized retry timing. Customizable email sequences. |
| **Invoices** | Native | `Invoice` | Automatic or manual invoices. PDF generation. Email delivery. |
| **Payment methods** | Native | Cards, ACH, wire, SEPA, etc. | All major credit cards + bank transfers for Enterprise ACH/wire requirement. |
| **Coupons/discounts** | Native | `Coupon` + `Promotion Code` | Percentage or fixed amount. Duration: once, repeating, forever. For nonprofit/startup/agency programs. |
| **Usage alerts** (50%/80%/95%) | Requires application logic | Billing Meter alerts or custom | Stripe Billing Meter (newer API) supports threshold alerts. Alternatively, track in your own backend. |

### 2.3 Detailed Mapping: Agent Red Pricing Model

#### Base Subscription Tiers

```
Product: "Agent Red Customer Experience"
  Price: starter-monthly     → $149/month (recurring)
  Price: starter-annual      → $1,490/year (recurring, = $124.17/month effective)
  Price: professional-monthly → $399/month (recurring)
  Price: professional-annual  → $3,990/year (recurring, = $332.50/month effective)
  Price: enterprise-monthly   → $999/month (recurring)
  Price: enterprise-annual    → $9,990/year (recurring, = $832.50/month effective)
```

#### Metered Overage (Conversation Billing)

Stripe supports metered billing natively. The flow:

1. Create a metered Price for each tier's overage rate:
   - `starter-overage`: $0.04 per unit (metered, `aggregate_usage: sum`)
   - `professional-overage`: $0.025 per unit (metered, `aggregate_usage: sum`)
   - `enterprise-overage`: $0.015 per unit (metered, `aggregate_usage: sum`)

2. Each subscription includes the base Price + the metered overage Price as separate subscription items.

3. Your application reports usage via the API:
   ```
   POST /v1/subscription_items/{item_id}/usage_records
   {
     "quantity": 1,
     "timestamp": 1706500000,
     "action": "increment"
   }
   ```

4. At the end of each billing cycle, Stripe automatically calculates the overage charge based on reported usage minus the included allowance (the included allowance logic lives in your application -- Stripe bills all reported usage; you report only excess).

**Alternative approach with Billing Meter (newer API):** Stripe's Billing Meter API (introduced ~2024) provides a more integrated usage-based billing experience. You define meters, send events, and Stripe handles aggregation. This may be the preferred approach. [VERIFY current Billing Meter capabilities and pricing]

#### Conversation Packs (Pre-Purchase Credits)

Stripe does not have a native "credit pack" or "prepaid balance with expiration" object. Implementation options:

**Option A: One-Time Invoice Items**
- Create one-time `Price` objects for each pack ($29, $99, $249)
- Customer purchases via a one-time checkout session
- Your application tracks the credit balance and 90-day expiration
- Deduct from balance before reporting metered overage to Stripe

**Option B: Customer Balance Credits**
- Use Stripe's `Customer Balance` to credit the customer's account
- Customer buys a pack, your backend credits their Stripe balance
- Future invoices automatically draw from the balance first
- Limitation: Stripe's customer balance does not support expiration natively; your app must track and expire credits

**Option C: Custom Implementation (recommended)**
- Sell packs as one-time Stripe Checkout purchases
- Track pack balances, consumption, and 90-day expiration in your own database (Cosmos DB)
- Report to Stripe only the net overage after pack deduction
- Most flexible; cleanest separation of concerns

**Recommendation:** Option C. The 90-day expiration and "stack with included allowance" logic is application-specific. Stripe should handle payment; Agent Red should handle credit accounting.

#### Add-On Modules

Stripe handles add-ons as additional `Subscription Items` on an existing subscription:

```
Subscription: customer-123
  Item 1: professional-monthly ($399/mo)
  Item 2: professional-overage (metered)
  Item 3: multi-language-pack ($99/mo)      ← add-on
  Item 4: advanced-analytics ($149/mo)       ← add-on
  Item 5: mailchimp-integration ($49/mo)     ← add-on
```

Add-ons can be added or removed at any time. Stripe automatically prorates charges:
- **Adding mid-cycle:** Customer is charged a prorated amount for the remaining days
- **Removing mid-cycle:** Credit applied to next invoice (or immediate, configurable)

#### Annual vs. Monthly Toggle

Two approaches:

**Approach A: Separate Prices (recommended)**
- Create monthly and annual Price objects for each tier
- Switching from monthly to annual = update the subscription's Price
- Annual pays upfront; Stripe charges the full annual amount immediately

**Approach B: Single Price with billing interval**
- One Price per tier, use `recurring.interval` of `month` or `year`
- Same outcome, slightly less flexible

For Agent Red's "add-ons purchased during an annual plan are billed monthly" requirement: this works naturally in Stripe. The annual base plan is one subscription item with `interval: year`, and add-ons are separate items with `interval: month`. Stripe handles mixed-interval billing on a single subscription.

### 2.4 Customer Portal

Stripe's hosted Customer Portal (https://stripe.com/docs/customer-management/portal) provides:

| Feature | Available | Customizable |
|---------|-----------|-------------|
| Update payment method | Yes | N/A |
| View invoices and receipts | Yes | N/A |
| Download invoice PDFs | Yes | N/A |
| Switch plans (upgrade/downgrade) | Yes | Configure which plans are switchable |
| Cancel subscription | Yes | Configure cancellation flow (immediate, end-of-period, with survey) |
| Update billing address | Yes | N/A |
| Manage tax ID | Yes | N/A |
| Apply promotion codes | Yes | Enable/disable |
| Custom branding | Yes | Logo, colors, custom domain [VERIFY custom domain availability] |
| Custom links | Yes | Add links to your own pages (support, docs) |

**Limitations:**
- Cannot display usage/consumption data (your app must provide this)
- Cannot sell add-ons (your app must handle add-on management UI)
- Cannot display conversation pack balances (your app must provide this)
- Visual customization is limited to logo and colors; full CSS theming requires Stripe Elements or custom UI

**Recommendation:** Use Stripe Customer Portal for payment/invoice management. Build custom portal pages in Agent Red for usage dashboards, add-on management, and conversation pack tracking.

---

## 3. Marketplace & Ecosystem

### 3.1 Does Stripe Have a Marketplace?

**No.** Stripe does not operate a marketplace, app store, or directory where end customers discover and purchase SaaS products. Stripe is invisible infrastructure -- customers interact with your brand, your website, and your checkout flow. Stripe processes the payment behind the scenes.

This is fundamentally different from:
- **Shopify App Store** -- customers discover apps within the Shopify admin
- **Salesforce AppExchange** -- customers find apps within the Salesforce ecosystem
- **AWS Marketplace** -- customers find and purchase software within AWS

### 3.2 How Customers Find and Purchase SaaS Products Using Stripe

Customers do not "find" products through Stripe. The customer acquisition funnel is entirely owned by the SaaS vendor:

1. Customer discovers Agent Red via marketing, search, referral, or content
2. Customer visits agentred.io
3. Customer clicks "Start Free Trial" or selects a plan
4. Agent Red creates a Stripe Checkout Session or uses Stripe Elements
5. Customer enters payment information in a Stripe-powered form (on agentred.io or Stripe-hosted)
6. Stripe processes the payment and creates the subscription
7. Agent Red receives webhook confirmation and provisions the tenant

Stripe is the payment layer, not the discovery layer.

### 3.3 Addressable Market Size

While Stripe is not a discovery channel, its market reach indicates the scale of the infrastructure:

| Metric | Value | Source |
|--------|-------|--------|
| Businesses using Stripe | 3.1+ million [VERIFY for 2026] | Stripe reported figures |
| Countries supported | 47+ | stripe.com/global |
| Total payment volume (2023) | $1 trillion+ | Public reporting |
| Stripe valuation | ~$65 billion (2023 secondary) [VERIFY] | Press reports |
| SaaS companies on Stripe | Estimated 100,000+ | Industry estimates |
| Internet businesses on Stripe | "Millions" | Stripe marketing |

**Key context:** The number of businesses using Stripe is not Agent Red's addressable market. Agent Red's addressable market is e-commerce businesses needing AI customer service. Stripe's relevance is that those businesses are highly likely to already be familiar with Stripe-powered checkout flows, reducing friction.

### 3.4 Stripe App Marketplace (for Stripe Users)

Stripe does have an **App Marketplace** (https://marketplace.stripe.com), but this is for apps that extend Stripe's own dashboard -- not for selling SaaS products to end customers. Examples: accounting integrations, fraud tools, tax calculators, subscription analytics.

**Relevance to Agent Red:** Agent Red could potentially build a Stripe App that helps Stripe merchants manage their AI customer service from within the Stripe dashboard. This is a secondary distribution channel, not a primary one, and would require building to Stripe's Apps SDK.

[VERIFY: Current state of Stripe Marketplace, submission requirements, and whether it has meaningful discovery traffic for B2B SaaS]

---

## 4. Partner Program

### 4.1 Stripe Partner Ecosystem

Stripe has a partner program (https://stripe.com/partners) with multiple tiers:

| Partner Type | Description | Relevance to Agent Red |
|-------------|-------------|----------------------|
| **Technology Partners** | Companies that build integrations with Stripe | Agent Red would be a technology partner (integrates Stripe Billing) |
| **Consulting Partners** | Agencies and consultancies implementing Stripe for clients | Not directly relevant |
| **Platform Partners** | Companies building on Stripe Connect | Relevant if Agent Red becomes a platform with resellers |

### 4.2 Stripe Partner Program Benefits

Stripe's partner program is oriented toward companies that **drive Stripe adoption** (bring new merchants to Stripe), not toward companies that simply use Stripe for their own billing.

Typical benefits for technology partners:
- Co-marketing opportunities (case studies, blog features)
- Partner directory listing
- Technical integration support
- Early access to new features (beta programs)
- Dedicated partner manager (for larger partners)

### 4.3 Affiliate/Referral Program

**Stripe does not offer a native affiliate program for its partners to use.** Specifically:

- Stripe does not provide an affiliate tracking system for Agent Red to track referrals
- Stripe does not pay commissions for SaaS products sold through Stripe Billing
- There is no "Stripe Affiliate Network" equivalent

**For Agent Red's own affiliate/referral program** (the "Agency Partners" program offering 20% discount + recurring referral commission), you would need:

| Approach | Tool | Cost | Integration |
|----------|------|------|-------------|
| **Dedicated affiliate platform** | PartnerStack, FirstPromoter, Rewardful | $200-500+/mo | Stripe webhooks → affiliate tracking |
| **Stripe-integrated affiliate tool** | Rewardful (https://www.rewardful.com) | $49-99/mo [VERIFY] | Native Stripe integration, tracks referrals via Stripe customer metadata |
| **Custom built** | Your own referral tracking | Dev time | Full control, most work |

**Recommended tool: Rewardful**

Rewardful is purpose-built for Stripe-based SaaS affiliate programs:
- Native Stripe Billing integration
- Tracks referrals via `referral` parameter on Stripe Checkout
- Automatic commission calculation on recurring payments
- Affiliate dashboard for partners
- Supports percentage and flat-rate commissions
- Supports recurring commissions (affiliate earns on every renewal)
- Starting at ~$49/month [VERIFY current pricing]

**Agent Red affiliate program design (using Rewardful + Stripe):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Commission type | Recurring (% of each payment) | Aligns with CLAUDE.md's "$30-37/mo recurring" target |
| Commission rate | 20-25% of base plan | Starter: $30-37/mo, Professional: $80-100/mo |
| Cookie duration | 90 days | Standard for B2B SaaS |
| Payment threshold | $100 minimum | Standard |
| Payment method | PayPal or bank transfer via Rewardful | Automatic |
| Attribution | First-touch (first referral link clicked) | Simplest model |

### 4.4 Stripe Connect (Platform/Marketplace Model)

If Agent Red ever evolves into a platform where agencies resell Agent Red to their clients, **Stripe Connect** would enable:

- Agent Red as the platform, agencies as "connected accounts"
- Split payments (Agent Red takes platform fee, agency takes margin)
- Per-client billing managed through the platform

This is a future consideration (post-Launch 1.0), not an immediate requirement.

---

## 5. Competitor Landscape

### 5.1 AI Customer Service / Chatbot / Helpdesk SaaS on Stripe

The vast majority of B2B SaaS companies in the customer service space use Stripe for billing. This is relevant because it validates Stripe as the industry standard and means Agent Red's checkout experience will be familiar to target customers.

| Competitor | Uses Stripe | Pricing Model | Starting Price | AI Resolution Cost |
|-----------|-------------|---------------|----------------|-------------------|
| **Intercom** | Yes | Per-seat + per-resolution | ~$39/seat/mo + $0.99/resolution (Fin AI) | $0.99 per AI resolution |
| **Tidio** | Yes | Per-seat, tiered | ~$29/mo (Starter) | Included in Lyro add-on ($39/mo for 50 conversations) |
| **Gorgias** | Yes | Ticket-based tiers | ~$10/mo (Starter, 10 tickets) to $900/mo | $0.36/automated interaction (Automate) |
| **Zendesk** | Yes | Per-agent, tiered | ~$19/agent/mo (Suite Team) | $1.00 per automated resolution [VERIFY] |
| **Freshdesk** | Yes | Per-agent, tiered + add-ons | Free tier; $15/agent/mo (Growth) | Freddy AI add-on pricing varies |
| **Drift (Salesloft)** | Yes [VERIFY] | Custom pricing (sales-led) | Not published (~$2,500/mo+) | Included in platform |
| **Ada** | Yes [VERIFY] | Custom pricing (enterprise) | Not published | Per-resolution pricing |
| **Help Scout** | Yes | Per-user | $20/user/mo (Standard) | AI features included |
| **Crisp** | Yes [VERIFY] | Flat-rate tiers | Free; $25/mo (Pro); $95/mo (Unlimited) | AI included at higher tiers |
| **LiveChat** | Yes | Per-agent | $20/agent/mo (Starter) | ChatBot add-on: $52/mo |

### 5.2 Price Comparison: Agent Red vs. Competitors

Agent Red's key competitive claim is "50% below nearest comparable competitor." Here is the comparison for a business with 2,000 conversations/month:

| Platform | Monthly Cost (2,000 conv/mo) | What You Get | Cost Per AI Conversation |
|----------|------------------------------|--------------|-------------------------|
| **Agent Red Professional** | **$399 + $0** (5,000 included) | 6 AI agents, Shopify+Zendesk, full platform | **$0.00** (within allowance) |
| **Agent Red Starter** | **$149 + $40** overage | 6 AI agents, Shopify, full platform | **$0.04** (overage rate) |
| Intercom (Fin AI) | ~$234/mo (3 seats) + $1,980 (2,000 resolutions) = **~$2,214/mo** | Fin AI agent + inbox | **$0.99** per resolution |
| Gorgias Automate | ~$360/mo (Pro) + $720 (2,000 automations) = **~$1,080/mo** | Automate + helpdesk | **$0.36** per automation |
| Zendesk | ~$285/mo (3 agents Suite Pro) + $2,000 (2,000 resolutions) = **~$2,285/mo** | AI + full suite | **$1.00** per resolution |
| Tidio (Lyro) | ~$59/mo + Lyro ($159/mo for 2,000) = **~$218/mo** | Chatbot + live chat | **~$0.08** (estimated pack rate) |

**Key insight:** Agent Red at $399/month with 5,000 included conversations is dramatically cheaper than Intercom ($2,214/mo), Zendesk ($2,285/mo), and Gorgias ($1,080/mo) for the same 2,000-conversation workload. Tidio is the closest competitor on price but offers a simpler product (chatbot widget vs. six-agent AI pipeline).

### 5.3 Stripe Ecosystem Validation

The fact that all major competitors use Stripe validates several things:

1. **Stripe handles SaaS billing at scale** -- Intercom processes millions of subscriptions through Stripe
2. **B2B buyers are accustomed to Stripe checkout** -- no friction from unfamiliar payment flows
3. **Agent Red's billing model is implementable** -- competitors with similar models (metered + base) already run on Stripe
4. **No competitive advantage from payment platform** -- this is infrastructure, not differentiation (which is correct -- differentiation comes from product and price)

---

## 6. Costs

### 6.1 Stripe Fee Structure

Stripe uses a pay-as-you-go model with per-transaction fees. There are no monthly platform fees for using Stripe Payments.

#### Core Payment Processing

| Fee | Rate | Applied To | Notes |
|-----|------|------------|-------|
| **Standard card processing** | 2.9% + $0.30 | Per successful charge | US-issued cards [VERIFY for 2026] |
| **International cards** | +1.5% | Per international card charge | Cards issued outside US |
| **Currency conversion** | +1% | If currency conversion is needed | When charging in non-USD |
| **ACH Direct Debit** | 0.8% (capped at $5) | Per ACH transfer | Relevant for Enterprise annual invoicing |
| **Wire transfer** | Varies | Per wire | Available for large invoices |

#### Stripe Billing (Subscription Management)

| Fee | Rate | Applied To | Notes |
|-----|------|------------|-------|
| **Stripe Billing** | 0.5% of billing revenue | Per invoice generated through Billing | On top of payment processing fees |
| **Starter mode** | 0.5% | Recurring subscriptions | [VERIFY: may have changed with new Billing tiers] |
| **Scale mode** | 0.8% | Recurring subscriptions | Includes advanced features: revenue recovery, Billing Meter, etc. [VERIFY] |
| **Smart Retries** | Included | Failed payment recovery | ML-optimized retry timing |
| **Revenue Recovery** | Included (Scale) | Dunning emails, retry logic | [VERIFY: may be in Scale tier only] |

#### Stripe Tax

| Fee | Rate | Applied To | Notes |
|-----|------|------------|-------|
| **Stripe Tax** | 0.5% per transaction | Transactions where tax is calculated | On top of other fees |
| **Tax registration monitoring** | Included | Alerts when you reach tax thresholds | |
| **Tax reporting** | Included | Reports for filing | |

#### Other Relevant Fees

| Fee | Rate | Notes |
|-----|------|-------|
| **Stripe Invoicing** (standalone) | 0.4% per paid invoice (or $0.50 per invoice, whichever is greater) | For manually created invoices outside of Billing |
| **Radar (fraud protection)** | Included in standard processing | Basic fraud protection |
| **Radar for Fraud Teams** | $0.05-0.07/transaction | Advanced fraud rules, ML models |
| **Dispute/chargeback fee** | $15 per dispute | Refunded if you win |
| **Payout timing** | 2 business days (US) | Standard payout schedule |
| **Instant payouts** | 1% (min $0.50) | Optional same-day payout |

### 6.2 Cost Modeling for Agent Red

#### Scenario: 50 Customers (Year 1 Target)

Assuming a realistic Year 1 customer mix:

| Customer Segment | Count | Plan | Monthly Revenue | Annual Revenue |
|-----------------|-------|------|----------------|----------------|
| Starter (monthly) | 25 | $149/mo | $3,725 | $44,700 |
| Professional (monthly) | 15 | $399/mo | $5,985 | $71,820 |
| Professional (annual) | 5 | $332/mo ($3,990/yr) | $1,660 | $19,920 |
| Enterprise (monthly) | 3 | $999/mo | $2,997 | $35,964 |
| Enterprise (annual) | 2 | $832/mo ($9,990/yr) | $1,664 | $19,980 |
| **Subtotal (base)** | **50** | | **$16,031/mo** | **$192,384/yr** |
| Overage (estimated 20% of customers) | ~10 | Avg. $50/mo | $500 | $6,000 |
| Add-ons (estimated 30% adoption) | ~15 | Avg. $100/mo | $1,500 | $18,000 |
| **Total Revenue** | | | **$18,031/mo** | **$216,384/yr** |

#### Stripe Fees on This Revenue

| Fee Component | Calculation | Monthly Cost | Annual Cost |
|--------------|-------------|-------------|-------------|
| Payment processing (2.9% + $0.30) | $18,031 x 2.9% + (50 transactions x $0.30) | $538 | $6,452 |
| Stripe Billing (0.5%) | $18,031 x 0.5% | $90 | $1,082 |
| Stripe Tax (0.5%) | $18,031 x 0.5% | $90 | $1,082 |
| **Total Stripe fees** | | **$718/mo** | **$8,616/yr** |
| **Effective fee rate** | | **3.98%** | **3.98%** |

**Note:** If using Stripe Billing "Scale" tier (0.8%), the effective rate would be ~4.28%. Annual subscribers paying by ACH would have lower per-transaction fees (0.8% capped at $5 vs. 2.9% + $0.30).

#### Fixed Costs (Stripe)

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| Stripe Payments | $0 | No monthly fee |
| Stripe Billing | $0 | No monthly fee; percentage-based |
| Stripe Tax | $0 | No monthly fee; percentage-based |
| Stripe Customer Portal | $0 | Included with Billing |
| **Total fixed Stripe costs** | **$0** | All usage-based |

This is a significant advantage over Shopify, which charges $79/month (Shopify plan) or $299/month (Advanced) before any transaction fees.

### 6.3 Fee Comparison: Stripe vs. Shopify

| Fee Component | Stripe | Shopify (Basic $39/mo) | Shopify (Shopify $105/mo) |
|--------------|--------|----------------------|--------------------------|
| Monthly platform fee | $0 | $39/mo | $105/mo |
| Card processing | 2.9% + $0.30 | 2.9% + $0.30 (Shopify Payments) | 2.6% + $0.30 (Shopify Payments) |
| Third-party payment fee | N/A | +2% if not using Shopify Payments | +1% |
| Subscription management | 0.5% (Billing) | Requires app (Recharge, etc.) | Requires app |
| Subscription app fee | N/A | $99-499/mo (Recharge) [VERIFY] | $99-499/mo (Recharge) [VERIFY] |
| Metered billing | Included in Billing | Not natively supported | Not natively supported |
| Tax calculation | 0.5% (Stripe Tax) | Included (basic) | Included (basic) |
| Customer portal | Included | Via app | Via app |
| **Total for Agent Red** | **~4% effective** | **$39-105/mo + 2.9% + subscription app** | Higher total cost |

**Verdict:** Stripe is significantly cheaper than Shopify for B2B SaaS subscription billing. Shopify adds fixed monthly costs plus requires third-party subscription management apps, which add their own monthly fees. Shopify is designed for physical/digital product commerce, not SaaS subscription billing.

---

## 7. Developer Experience

### 7.1 Overview

Stripe is widely regarded as having the best developer experience of any payment platform. This is a core competitive advantage that is directly relevant to Agent Red's small team and aggressive timeline.

### 7.2 API Quality

| Dimension | Assessment | Details |
|-----------|------------|---------|
| **API design** | RESTful, consistent, predictable | Resource-oriented URLs, standard HTTP methods |
| **API versioning** | Explicit, backward-compatible | Date-based versions (e.g., `2024-04-10`). Old versions supported for years. Pin version in API key settings. |
| **Authentication** | Simple API key (secret key + publishable key) | Bearer token auth. Separate test/live keys. |
| **Error handling** | Structured error objects | Error type, code, message, and param. Machine-readable error codes. |
| **Pagination** | Cursor-based | Consistent across all list endpoints. `has_more` + `starting_after` pattern. |
| **Idempotency** | Native | `Idempotency-Key` header for safe retries. Critical for billing operations. |
| **Rate limiting** | Generous | 100 read requests/sec, 100 write requests/sec per secret key in live mode. Higher in test mode. [VERIFY current limits] |
| **Webhooks** | Comprehensive | Events for every state change. Signature verification. Retry with exponential backoff. |
| **Metadata** | On every object | Up to 50 key-value pairs per object. Essential for linking Stripe objects to Agent Red tenant IDs. |

### 7.3 SDKs

| Language | Package | Quality | Relevance to Agent Red |
|----------|---------|---------|----------------------|
| **Python** | `stripe` (PyPI) | Excellent | Primary -- Agent Red backend is Python 3.12+ |
| **Node.js** | `stripe` (npm) | Excellent | Useful if Agent Red builds a Node.js checkout frontend |
| **Ruby** | `stripe` (RubyGems) | Excellent | Not directly relevant |
| **Go** | `stripe-go` | Excellent | Not directly relevant |
| **Java** | `stripe-java` | Excellent | Not directly relevant |
| **.NET** | `Stripe.net` (NuGet) | Excellent | Not directly relevant |
| **PHP** | `stripe-php` | Excellent | Not directly relevant |

All SDKs are auto-generated from Stripe's OpenAPI spec, ensuring consistency. The Python SDK is particularly well-maintained and idiomatic.

**Python SDK example (creating Agent Red subscription):**

```python
import stripe
stripe.api_key = "sk_live_..."

# Create subscription with base plan + metered overage
subscription = stripe.Subscription.create(
    customer="cus_abc123",
    items=[
        {"price": "price_professional_monthly"},   # $399/mo base
        {"price": "price_professional_overage"},    # $0.025/conv metered
    ],
    trial_period_days=14,
    metadata={
        "tenant_id": "tenant_abc123",
        "plan": "professional",
    },
)
```

### 7.4 Stripe CLI

The Stripe CLI (https://stripe.com/docs/stripe-cli) provides:

| Feature | Description | Usefulness |
|---------|-------------|------------|
| `stripe listen` | Forward webhooks to local development server | Essential for dev/test |
| `stripe trigger` | Trigger test webhook events | Test provisioning flows |
| `stripe logs tail` | Real-time API request logs | Debug integration issues |
| `stripe resources` | CRUD operations on API objects | Quick testing |
| `stripe samples` | Clone sample integration projects | Jumpstart development |
| `stripe fixtures` | Create test data from YAML definitions | Repeatable test scenarios |

The CLI is available for Windows, macOS, and Linux. On Windows (Agent Red's dev environment), it installs via `scoop install stripe` or direct download.

### 7.5 Test Mode

Stripe's test mode is a complete parallel environment:

| Feature | Details |
|---------|---------|
| **Separate API keys** | `sk_test_...` and `pk_test_...` |
| **Test card numbers** | `4242424242424242` (success), `4000000000000002` (decline), etc. |
| **Test clocks** | Simulate future billing events (advance time to test renewals, trials ending, dunning) |
| **Full API parity** | Every API works identically in test mode |
| **No real charges** | Test mode never charges real cards |
| **Webhook testing** | Test webhooks fire for test-mode events |
| **Dashboard** | Full dashboard access for test data |

**Test Clocks** are particularly valuable for Agent Red: they let you simulate a customer's 14-day trial ending, monthly billing renewal, usage-based invoice generation, and dunning sequences without waiting in real time.

### 7.6 Documentation Quality

Stripe's API documentation (https://stripe.com/docs/api) is widely considered the gold standard for API documentation:

| Dimension | Rating | Notes |
|-----------|--------|-------|
| Completeness | 5/5 | Every endpoint, parameter, and field documented |
| Code examples | 5/5 | Every endpoint has examples in 7+ languages |
| Interactive | 4/5 | Right-panel shows request/response; can make test calls from docs |
| Guides | 5/5 | Extensive guides for billing, subscriptions, webhooks, etc. |
| Search | 5/5 | Fast, accurate, faceted |
| Changelog | 5/5 | Detailed changelog with migration guides |
| Quickstarts | 5/5 | Step-by-step quickstarts for common use cases |

### 7.7 Stripe-Hosted Checkout vs. Custom UI

Agent Red has two primary options for the checkout experience:

| Approach | Description | Pros | Cons |
|----------|-------------|------|------|
| **Stripe Checkout** (hosted) | Stripe-hosted payment page | Fastest to implement, PCI compliant by default, optimized conversion, supports 40+ payment methods | Less brand control, redirect away from agentred.io |
| **Stripe Elements** (embedded) | Stripe UI components embedded in your page | Full brand control, stays on agentred.io, customizable | More dev work, still PCI compliant (tokenization) |
| **Stripe Payment Links** | No-code shareable payment links | Zero development, instant setup | Very limited customization, not suitable for SaaS |

**Recommendation for Agent Red Launch 1.0:** Start with **Stripe Checkout** (hosted). It is the fastest path to a working checkout flow, is fully optimized for conversion, and requires minimal frontend development. Migrate to **Stripe Elements** in a later phase if brand cohesion demands it.

---

## 8. Tax & Compliance

### 8.1 Stripe Tax

Stripe Tax (https://stripe.com/tax) automates sales tax, VAT, and GST calculation:

| Feature | Details |
|---------|---------|
| **Automatic tax calculation** | Stripe determines the correct tax rate based on customer location, product type, and local tax rules |
| **Tax categories** | Pre-defined tax codes for SaaS, digital services, etc. Agent Red would use `txcd_10103000` (Software as a Service) or similar [VERIFY exact code] |
| **Supported jurisdictions** | All US states + 40+ countries (EU VAT, UK VAT, Canadian GST/HST, Australian GST, etc.) |
| **Tax registration monitoring** | Stripe tracks your sales per jurisdiction and alerts you when you approach economic nexus thresholds (e.g., state sales tax registration required) |
| **Tax reporting** | Generates reports for tax filing. Exports compatible with major tax software. |
| **Tax-inclusive or tax-exclusive pricing** | Configure whether displayed prices include or exclude tax |
| **Reverse charge (B2B)** | Handles EU reverse-charge VAT for B2B cross-border transactions |
| **Tax ID validation** | Validates customer VAT/tax IDs |

### 8.2 Cost

Stripe Tax charges **0.5% per transaction** where tax is calculated. This is on top of payment processing and Billing fees.

For Agent Red's international sales (especially EU, UK, Canada, Australia), Stripe Tax eliminates the need for a separate tax compliance service. Without Stripe Tax, Agent Red would need a tool like Avalara ($50-300+/month) or TaxJar (now part of Stripe, interestingly) or manual tax management.

### 8.3 Compliance Features

| Feature | Stripe Capability |
|---------|-------------------|
| **PCI DSS compliance** | Stripe handles all card data; Agent Red never touches raw card numbers. PCI SAQ-A (simplest level). |
| **SCA (Strong Customer Authentication)** | Automatic 3D Secure challenges for European cards when required by PSD2 |
| **GDPR** | Stripe is GDPR compliant. Data Processing Agreement available. Customer data deletion supported. |
| **SOC 2 Type II** | Stripe is SOC 2 certified |
| **Data residency** | Stripe stores data in the US by default. EU data residency available for EU-based Stripe accounts. [VERIFY current data residency options] |
| **W-9 / 1099** | Stripe handles 1099 reporting for US-based connected accounts (relevant if using Connect for affiliates) |

### 8.4 Relevance to Agent Red

Agent Red's pricing page states: "All payment processing through PCI-compliant providers." Stripe satisfies this requirement completely. Agent Red would:

1. Never handle raw credit card data (Stripe Checkout or Elements tokenizes)
2. Be PCI SAQ-A compliant (simplest self-assessment)
3. Automatically calculate tax in all supported jurisdictions
4. Receive alerts when tax registration is needed in new jurisdictions
5. Generate tax reports for filing

The 0.5% Stripe Tax fee is a reasonable cost to avoid hiring a tax compliance specialist or purchasing separate tax software.

---

## 9. Provisioning Integration

### 9.1 Webhook-Driven Tenant Provisioning

Stripe's webhook system is the primary integration point for automated tenant provisioning. When a customer subscribes, Stripe fires events that Agent Red can consume to automatically create the tenant's infrastructure.

#### Key Webhook Events for Agent Red

| Event | When Fired | Agent Red Action |
|-------|-----------|-----------------|
| `checkout.session.completed` | Customer completes checkout | Create tenant record, start provisioning |
| `customer.subscription.created` | Subscription created | Confirm plan, set feature flags |
| `customer.subscription.updated` | Plan changed (upgrade/downgrade) | Update tenant feature flags, adjust quotas |
| `customer.subscription.deleted` | Subscription cancelled | Start deprovisioning (grace period) |
| `customer.subscription.trial_will_end` | 3 days before trial ends | Send trial-ending notification |
| `invoice.paid` | Invoice successfully paid | Confirm active status, reset monthly conversation counter |
| `invoice.payment_failed` | Payment failed | Enter dunning state, send notification |
| `customer.subscription.paused` | Subscription paused | Suspend tenant access (maintain data) |

#### Provisioning Flow

```
Customer → Stripe Checkout → Payment → Stripe Webhook → Agent Red Backend → Azure Provisioning

Detailed flow:
1. Customer selects plan on agentred.io
2. Agent Red creates Stripe Checkout Session:
   - Includes plan Price, metered overage Price
   - Sets trial_period_days: 14
   - Sets metadata: { plan: "professional" }
   - Sets success_url: "https://agentred.io/welcome?session={CHECKOUT_SESSION_ID}"
   - Sets cancel_url: "https://agentred.io/pricing"

3. Customer completes Stripe Checkout

4. Stripe fires `checkout.session.completed` webhook to Agent Red

5. Agent Red webhook handler:
   a. Validate webhook signature (Stripe signing secret)
   b. Extract customer ID, subscription ID, plan metadata
   c. Create tenant record in Cosmos DB:
      - tenant_id (UUID)
      - stripe_customer_id
      - stripe_subscription_id
      - plan (starter/professional/enterprise)
      - status: "provisioning"
      - features: { ... based on plan }
      - conversation_allowance: 1000/5000/20000
      - conversation_used: 0
   d. Trigger Azure provisioning:
      - Create tenant namespace in NATS JetStream
      - Configure per-tenant topic routing
      - Set up tenant API key in Key Vault
      - Configure rate limits and quotas
      - Initialize knowledge base (empty)
   e. Update tenant status to "active"
   f. Send welcome email with onboarding link

6. Customer redirected to success_url, sees welcome page
```

### 9.2 Azure Integration Pattern

| Provisioning Step | Azure Service | Method |
|-------------------|---------------|--------|
| Tenant data storage | Cosmos DB | Direct SDK call |
| API key generation | Key Vault | Managed Identity + SDK |
| Tenant isolation (messaging) | NATS JetStream | Topic namespace creation |
| Configuration | App Configuration | Per-tenant feature flags |
| Monitoring | Application Insights | Custom dimensions per tenant |
| Secrets | Key Vault | Per-tenant API keys |

### 9.3 Webhook Reliability

Stripe webhooks are highly reliable:

| Feature | Details |
|---------|---------|
| **Retry policy** | Up to 3 days with exponential backoff (attempts at: immediate, 1hr, 2hr, 4hr, 8hr, ... up to 72 hours) |
| **Signature verification** | HMAC SHA-256 signature on every event |
| **Event ordering** | Events may arrive out of order; design handlers to be idempotent |
| **Event replay** | Re-send events from Stripe Dashboard for debugging |
| **Webhook endpoints** | Multiple endpoints supported; filter by event type |
| **Delivery logs** | Full delivery log with response codes in Dashboard |

### 9.4 Idempotency Considerations

Agent Red's webhook handler must be idempotent because Stripe may deliver the same event multiple times. Design pattern:

```python
# Pseudocode for idempotent webhook handling
def handle_webhook(event):
    # 1. Check if already processed
    existing = cosmos_db.get("webhook_events", event["id"])
    if existing:
        return {"status": "already_processed"}

    # 2. Process the event
    if event["type"] == "checkout.session.completed":
        provision_tenant(event["data"]["object"])

    # 3. Record as processed
    cosmos_db.upsert("webhook_events", {
        "id": event["id"],
        "type": event["type"],
        "processed_at": datetime.utcnow().isoformat(),
    })

    return {"status": "processed"}
```

### 9.5 Deprovisioning

When a customer cancels:

| Event | Agent Red Action | Timeline |
|-------|-----------------|----------|
| `customer.subscription.updated` (cancel_at_period_end: true) | Mark for end-of-period cancellation | Immediate |
| `customer.subscription.deleted` | Begin deprovisioning | End of billing period |
| (Agent Red internal) | Suspend access, maintain data | Day 0 |
| (Agent Red internal) | Send "reactivate?" email | Day 7 |
| (Agent Red internal) | Export data, send download link | Day 14 |
| (Agent Red internal) | Delete tenant data | Day 30 |

---

## 10. Strategic Fit Assessment

### 10.1 Agent Red's Strategy

From CLAUDE.md and the pricing page, Agent Red's strategy is:
- **Price disruption:** 50% below nearest comparable competitor
- **Transparency:** Full pricing visibility as competitive advantage
- **Affiliate/creator:** Higher affiliate payouts to drive content marketing
- **Open-source foundation:** Trust mechanism through AGNTCY transparency

### 10.2 How Stripe Supports This Strategy

| Strategy Element | Stripe Support | Assessment |
|-----------------|----------------|------------|
| **Price disruption** | Stripe is invisible infrastructure -- customers see Agent Red's price, not Stripe's. No Stripe markup on pricing. | Fully supports |
| **Pricing transparency** | Self-service checkout with clear pricing. No "contact sales" gatekeeping imposed by Stripe. | Fully supports |
| **Affiliate program** | No native affiliate support, but integrates with Rewardful/PartnerStack for affiliate tracking. | Partially supports (needs add-on tool) |
| **Free trial** | Native 14-day trial support. No credit card required option. | Fully supports |
| **Usage-based billing** | Native metered billing. Transparent per-conversation pricing. | Fully supports |
| **30-day money-back guarantee** | Refunds are straightforward via API or Dashboard. | Fully supports |
| **Annual billing** | Native support with any discount structure. | Fully supports |
| **Enterprise invoicing** | ACH/wire transfer for Enterprise customers paying annually by invoice. | Fully supports |

### 10.3 What Stripe Does NOT Provide

| Need | Stripe Gap | Solution |
|------|-----------|---------|
| **Customer discovery** | Stripe has no marketplace/storefront | Agent Red must drive all traffic (SEO, content, affiliates, ads) |
| **Affiliate tracking** | No native affiliate program | Add Rewardful (~$49/mo) or PartnerStack (~$200+/mo) |
| **Usage dashboard** | Stripe does not show usage to customers | Build in Agent Red's customer portal |
| **Conversation pack tracking** | No native credit/pack system | Build in Agent Red's backend (Cosmos DB) |
| **Usage alerts** | Limited native alert capabilities | Build in Agent Red's backend |
| **Full-featured customer portal** | Stripe Portal covers payment/billing only | Build Agent Red portal for usage, add-ons, settings |

### 10.4 Stripe vs. Shopify: Strategic Comparison

| Dimension | Stripe | Shopify | Winner for Agent Red |
|-----------|--------|---------|---------------------|
| **SaaS subscription billing** | Purpose-built | Requires third-party apps | Stripe |
| **Metered/usage billing** | Native | Not supported | Stripe |
| **Customer discovery** | None | Shopify App Store (but not for SaaS) | Neither (not applicable) |
| **Monthly platform cost** | $0 (usage-based only) | $39-299/mo + app fees | Stripe |
| **Developer experience** | Industry-leading | Good but commerce-focused | Stripe |
| **Checkout conversion** | Optimized for subscriptions | Optimized for product purchases | Stripe |
| **Tax handling** | Stripe Tax (0.5%) | Included (basic) | Tie |
| **Customer portal** | Basic (billing-only) | Not applicable | Stripe (with custom extension) |
| **Time to implement** | Days (for basic billing) | Weeks (with subscription app) | Stripe |
| **Brand control** | Full (your domain, your design) | Shopify-branded elements | Stripe |

**Verdict:** Stripe is the clear winner for Agent Red's B2B SaaS subscription billing. Shopify is designed for product commerce, not recurring SaaS subscriptions with metered usage. The Shopify option would require bolting on third-party subscription management (Recharge: ~$99-499/mo) and still would not natively support metered billing.

---

## 11. Agent Red Pricing Model Mapping

### 11.1 Complete Stripe Object Model

Here is the full mapping of Agent Red's pricing model to Stripe objects:

#### Products

```
Product: agent-red-platform
  name: "Agent Red Customer Experience"
  description: "AI-powered customer service platform for e-commerce"
  metadata: { type: "base_platform" }

Product: agent-red-conversations
  name: "AI Conversation Overage"
  description: "Per-conversation charge beyond included monthly allowance"
  metadata: { type: "metered_usage" }

Product: agent-red-multi-language
  name: "Multi-Language Pack"
  metadata: { type: "addon" }

Product: agent-red-advanced-analytics
  name: "Advanced Analytics"
  metadata: { type: "addon" }

Product: agent-red-mailchimp
  name: "Mailchimp Integration"
  metadata: { type: "addon" }

Product: agent-red-google-analytics
  name: "Google Analytics Integration"
  metadata: { type: "addon" }

Product: agent-red-white-label
  name: "White-Label Package"
  metadata: { type: "addon" }

Product: agent-red-priority-support
  name: "Priority Support Upgrade"
  metadata: { type: "addon" }

Product: agent-red-custom-integration
  name: "Custom Integration Development"
  metadata: { type: "addon" }

Product: agent-red-conversation-pack-1k
  name: "1,000 Conversation Pack"
  metadata: { type: "conversation_pack" }

Product: agent-red-conversation-pack-5k
  name: "5,000 Conversation Pack"
  metadata: { type: "conversation_pack" }

Product: agent-red-conversation-pack-20k
  name: "20,000 Conversation Pack"
  metadata: { type: "conversation_pack" }
```

#### Prices (Base Plans)

```
# Starter
Price: starter-monthly     → $149/month, recurring, interval: month
Price: starter-annual      → $1,490/year, recurring, interval: year

# Professional
Price: pro-monthly         → $399/month, recurring, interval: month
Price: pro-annual          → $3,990/year, recurring, interval: year

# Enterprise
Price: enterprise-monthly  → $999/month, recurring, interval: month
Price: enterprise-annual   → $9,990/year, recurring, interval: year
```

#### Prices (Metered Overage)

```
Price: starter-overage     → $0.04/unit, recurring, usage_type: metered, aggregate_usage: sum
Price: pro-overage         → $0.025/unit, recurring, usage_type: metered, aggregate_usage: sum
Price: enterprise-overage  → $0.015/unit, recurring, usage_type: metered, aggregate_usage: sum
```

#### Prices (Add-Ons)

```
Price: multi-language-monthly      → $99/month, recurring
Price: advanced-analytics-monthly  → $149/month, recurring
Price: mailchimp-monthly           → $49/month, recurring
Price: google-analytics-monthly    → $49/month, recurring
Price: white-label-monthly         → $399/month, recurring
Price: priority-support-monthly    → $99/month, recurring
Price: custom-integration-monthly  → $299/month, recurring
```

#### Prices (Conversation Packs -- One-Time)

```
Price: pack-1k   → $29, one_time
Price: pack-5k   → $99, one_time
Price: pack-20k  → $249, one_time
```

#### Coupons (Special Programs)

```
Coupon: nonprofit-25
  percent_off: 25
  duration: forever
  metadata: { program: "nonprofit" }

Coupon: startup-50-12mo
  percent_off: 50
  duration: repeating
  duration_in_months: 12
  metadata: { program: "startup" }

Coupon: agency-20
  percent_off: 20
  duration: forever
  metadata: { program: "agency" }
```

### 11.2 Subscription Item Structure

A Professional customer with two add-ons:

```json
{
  "subscription": {
    "customer": "cus_abc123",
    "items": [
      {
        "price": "price_pro_monthly",
        "quantity": 1
      },
      {
        "price": "price_pro_overage",
        "usage_type": "metered"
      },
      {
        "price": "price_multi_language_monthly",
        "quantity": 1
      },
      {
        "price": "price_mailchimp_monthly",
        "quantity": 1
      }
    ],
    "trial_period_days": 14,
    "metadata": {
      "tenant_id": "tenant_abc123",
      "plan": "professional",
      "addons": "multi-language,mailchimp"
    }
  }
}
```

---

## 12. Recommendation

### 12.1 Verdict: Use Stripe

**Stripe is the recommended billing platform for Agent Red Customer Experience.**

| Factor | Assessment |
|--------|------------|
| **Technical fit** | Excellent. Native support for all Agent Red billing models. |
| **Cost** | Low. No fixed fees. ~4% effective rate is standard. |
| **Time to implement** | Fast. Python SDK + Stripe Checkout = basic billing in days. |
| **Scalability** | Unlimited. Stripe handles billions in payment volume. |
| **Developer experience** | Best in class. Critical for Agent Red's small team. |
| **Industry standard** | All competitors use Stripe. Customers expect it. |

### 12.2 Stripe is NOT a Replacement for Shopify (as a Sales Channel)

This is an important distinction:

- **Stripe** = payment infrastructure (invisible to customers, powers checkout behind your website)
- **Shopify** = commerce platform (could provide a storefront, app store discovery, etc.)

For Agent Red as a B2B SaaS product, Shopify's commerce platform is not a good fit. B2B SaaS products are sold through their own websites, not through Shopify stores. The Shopify evaluation is effectively moot for this product category.

However, Agent Red could still benefit from being listed in the **Shopify App Store** as a Shopify app (since Shopify merchants are the primary target audience). This would be a customer discovery channel, separate from billing. In this model:
- Stripe handles billing (subscriptions, usage, invoices)
- Shopify App Store listing provides discovery (Shopify merchants find Agent Red)
- Agent Red's website is the primary sales channel

### 12.3 Implementation Priorities (Phase 2.1)

| Priority | Task | Effort | Notes |
|----------|------|--------|-------|
| P0 | Create Stripe account (live + test) | 1 hr | stripe.com/register |
| P0 | Create Products, Prices, Coupons in Stripe Dashboard (test mode) | 2 hrs | Per Section 11 mapping |
| P0 | Implement Stripe Checkout for plan selection | 4 hrs | Python backend + redirect |
| P0 | Implement webhook handler (subscription lifecycle) | 8 hrs | Provisioning, status changes |
| P0 | Implement basic tenant provisioning | 8 hrs | Cosmos DB + Key Vault + NATS |
| P1 | Implement metered usage reporting | 4 hrs | Report conversation counts to Stripe |
| P1 | Implement Stripe Customer Portal link | 1 hr | Customer portal for billing management |
| P1 | Implement conversation pack purchase flow | 4 hrs | One-time checkout + balance tracking |
| P2 | Build Agent Red customer dashboard (usage, add-ons) | 16 hrs | Custom portal for non-billing features |
| P2 | Set up Stripe Tax | 2 hrs | Enable tax calculation, set product tax codes |
| P2 | Set up Rewardful for affiliate program | 4 hrs | Affiliate tracking integration |
| P3 | Migrate to Stripe Elements (custom checkout) | 8 hrs | If brand cohesion requires it |

**Total estimated effort:** ~62 hours (aligns with Phase 2.1 estimate of ~34 hrs in PROJECT-PLAN.md, plus additional items for metered billing, packs, tax, and affiliate setup)

### 12.4 Costs to Budget

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| Stripe Payments | $0 fixed + 2.9%+$0.30/txn | Transaction fees only |
| Stripe Billing | +0.5% of billing revenue | Subscription management |
| Stripe Tax | +0.5% per taxed transaction | Automatic tax calculation |
| Rewardful (affiliate) | ~$49-99/mo [VERIFY] | Affiliate/referral tracking |
| **Total fixed** | **$49-99/mo** | Only Rewardful is fixed cost |
| **Total variable** | **~4% of revenue** | Transaction + Billing + Tax fees |

Compare to PROJECT-PLAN.md budget line: "E-commerce: Shopify or Stripe (TBD): $0-79/mo" -- Stripe comes in at $49-99/mo (Rewardful) + ~4% variable, which is within the expected range. The variable fees are unavoidable regardless of platform choice.

### 12.5 Open Questions for Verification

Before final commitment, verify the following at stripe.com and related sites:

| Item | Where to Verify | Why |
|------|-----------------|-----|
| Stripe Billing exact fee (0.5% vs. 0.8% tiers) | stripe.com/billing | Fee tiers may have changed |
| Stripe Tax exact fee | stripe.com/tax | May have updated pricing |
| Stripe Billing Meter capabilities | stripe.com/docs/billing/subscriptions/usage-based | Newer API, features evolving |
| Rewardful pricing and Stripe integration | rewardful.com | Confirm current plans |
| Stripe Customer Portal custom domain | stripe.com/docs/customer-management/portal | Feature availability |
| SaaS tax code | stripe.com/docs/tax/tax-codes | Correct code for Agent Red |
| Stripe Connect for future agency model | stripe.com/connect | Future planning |

---

## Appendix A: Stripe URLs Reference

| Resource | URL |
|----------|-----|
| Stripe Home | https://stripe.com |
| Stripe Pricing | https://stripe.com/pricing |
| Stripe Billing | https://stripe.com/billing |
| Stripe Tax | https://stripe.com/tax |
| Stripe Checkout | https://stripe.com/payments/checkout |
| Stripe Elements | https://stripe.com/payments/elements |
| Stripe Customer Portal | https://stripe.com/docs/customer-management/portal |
| Stripe CLI | https://stripe.com/docs/stripe-cli |
| Stripe API Reference | https://stripe.com/docs/api |
| Stripe Python SDK | https://pypi.org/project/stripe/ |
| Stripe Webhooks Guide | https://stripe.com/docs/webhooks |
| Stripe Test Cards | https://stripe.com/docs/testing |
| Stripe Test Clocks | https://stripe.com/docs/billing/testing/test-clocks |
| Stripe App Marketplace | https://marketplace.stripe.com |
| Stripe Partners | https://stripe.com/partners |
| Stripe Connect | https://stripe.com/connect |
| Rewardful (affiliate) | https://www.rewardful.com |
| PartnerStack (affiliate) | https://partnerstack.com |

---

## Appendix B: Stripe vs. Shopify Decision Summary

| Criterion | Stripe | Shopify | Verdict |
|-----------|--------|---------|---------|
| B2B SaaS subscription billing | Purpose-built | Requires third-party apps | **Stripe** |
| Metered/usage billing | Native | Not supported | **Stripe** |
| Monthly fixed cost | $0 | $39-299/mo + subscription app | **Stripe** |
| Customer discovery channel | None | Shopify App Store (limited for SaaS) | **Shopify** (marginal) |
| Developer experience for billing | Industry-best | Commerce-focused | **Stripe** |
| Time to implement billing | Days | Weeks | **Stripe** |
| Tax compliance | Stripe Tax (0.5%) | Basic included | **Tie** |
| Affiliate program | Via Rewardful | Via Shopify Collabs (product-focused) | **Stripe + Rewardful** |
| Brand control | Full | Shopify elements visible | **Stripe** |
| SaaS industry standard | Yes (all competitors use it) | No (Shopify is for commerce) | **Stripe** |

**Final recommendation:** Use **Stripe** for all billing and payment processing. Consider a **Shopify App Store listing** separately as a discovery channel (not for billing), since Shopify merchants are Agent Red's primary target audience.

---

*Research prepared for Agent Red Customer Experience Phase 2.1 E-Commerce Platform Evaluation.*
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
