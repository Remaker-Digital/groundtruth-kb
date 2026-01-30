# E-Commerce Platform Evaluation

> **Decision:** Which billing and distribution platform should Agent Red use for Launch 1.0?
> **Date:** 2026-01-30
> **Status:** Draft — Pending Owner Approval
> **Candidates:** Stripe · Shopify App Store · Paddle

---

## Executive Summary

This evaluation compares three e-commerce platforms for selling Agent Red Customer Engagement as a B2B SaaS product. The assessment uses nine dimensions, with particular emphasis on **addressable market size**, **partner diversity**, and **partner program benefits** — the strategic criteria for joining an ecosystem with established competitors that Agent Red can match on technology and quality but beat dramatically on price.

### Recommendation: Dual-Channel (Shopify App Store + Stripe)

| Channel | Role | Billing | Why |
|---------|------|---------|-----|
| **Shopify App Store** | Primary distribution | Shopify Billing API | Discovery, trust, zero commission on first $1M, pre-qualified buyers |
| **Stripe** | Direct sales | Stripe Billing | Non-Shopify merchants, SEO/content leads, full billing control |

Paddle is not recommended for Launch 1.0. Its tax/compliance advantages do not outweigh its lack of discovery, higher fees, and the fact that Agent Red's primary target market (Shopify merchants) requires the Shopify Billing API anyway.

---

## Table of Contents

1. [Agent Red's Billing Requirements](#1-agent-reds-billing-requirements)
2. [Platform Overviews](#2-platform-overviews)
3. [Addressable Market Size](#3-addressable-market-size)
4. [Partner Diversity & Competitor Landscape](#4-partner-diversity--competitor-landscape)
5. [Partner Program Benefits](#5-partner-program-benefits)
6. [Billing Capabilities](#6-billing-capabilities)
7. [Fee Structure & Cost Modeling](#7-fee-structure--cost-modeling)
8. [Developer Experience](#8-developer-experience)
9. [Tax & Compliance](#9-tax--compliance)
10. [Strategic Fit Assessment](#10-strategic-fit-assessment)
11. [Recommended Architecture](#11-recommended-architecture)
12. [Implementation Roadmap](#12-implementation-roadmap)
13. [Items Requiring Verification](#13-items-requiring-verification)
14. [Appendix A: Shopify App Store Approval & Partner Growth Path](#appendix-a-shopify-app-store-approval--partner-growth-path)
15. [Appendix B: Stripe Partner Program & Enhanced Benefits](#appendix-b-stripe-partner-program--enhanced-benefits)

---

## 1. Agent Red's Billing Requirements

Agent Red's pricing model combines a platform fee, metered usage, add-on modules, and pre-purchased credits. The billing platform must support all of these natively or with minimal custom logic.

| Requirement | Detail |
|-------------|--------|
| **3 subscription tiers** | Starter ($149/mo), Professional ($399/mo), Enterprise ($999/mo) |
| **Annual billing** | 17% discount: $1,490/yr, $3,990/yr, $9,990/yr |
| **Metered overage** | Per-conversation: $0.04 (Starter), $0.025 (Pro), $0.015 (Enterprise) |
| **7 add-on modules** | $49–$399/mo each, attachable to any tier |
| **3 conversation packs** | 1K ($29), 5K ($99), 20K ($249) — one-time, 90-day expiration |
| **Free trial** | 14 days, no credit card required |
| **Coupons** | Nonprofit (25% off forever), Startup (50% off 12 months), Agency (20% off forever) |
| **Affiliate program** | Recurring commissions ($30–$37/mo per referral) |
| **Self-service portal** | View invoices, update payment, change plan, cancel |
| **Webhook provisioning** | Subscription events trigger Azure tenant provisioning |

---

## 2. Platform Overviews

### Stripe

Stripe is invisible payment infrastructure for internet businesses. Agent Red owns the entire customer relationship — Stripe processes payments behind the scenes. No marketplace, no discovery channel. Every competitor in the AI customer service space (Intercom, Gorgias, Tidio, Zendesk, Freshdesk) uses Stripe.

- **Model:** Payment processor
- **Founded:** 2010
- **Businesses using Stripe:** 3.1M+ (reported)
- **SaaS companies on Stripe:** ~100,000+
- **Payment volume:** $1T+ (2023)
- **Countries:** 47+

### Shopify App Store

The Shopify App Store is a distribution marketplace where Shopify merchants discover, install, and pay for third-party apps. All billing goes through Shopify's Billing API — charges appear on the merchant's existing Shopify invoice. Shopify reviews apps for quality before listing.

- **Model:** Marketplace + billing
- **Active merchants:** ~4.8–5M+ (estimated Q1 2026)
- **US e-commerce platform share:** 28–32%
- **Global e-commerce share:** 10–12%
- **App Store apps:** Thousands across categories
- **GMV (2023):** $235B+

### Paddle

Paddle is a Merchant of Record (MoR) that acts as the legal seller to end customers. Paddle handles all sales tax, VAT, GST calculation, filing, and remittance globally. No marketplace, no discovery channel.

- **Model:** Merchant of Record
- **SaaS companies using Paddle:** 4,000+
- **Payment volume:** $4B+ (reported 2024)
- **Countries (sell to):** 200+
- **Tax jurisdictions:** All US states, EU27, UK, Canada, Australia, Japan, India

---

## 3. Addressable Market Size

This is the most important strategic dimension. Agent Red needs to reach e-commerce merchants who need AI customer service.

### Shopify App Store

| Metric | Value |
|--------|-------|
| Active Shopify stores | ~4.8–5M+ |
| Shopify Plus (enterprise tier) | ~30,000–40,000 |
| Merchants using customer service apps | 15–20% (~700K–1M) |
| Merchants with 1,000+ monthly support conversations | ~50,000–100,000 |
| Agent Red's Shopify-specific TAM | $180–$360M/yr |
| Customer service app category in App Store | 200–400+ apps |

**Key insight:** Shopify merchants are Agent Red's exact target customer. They are e-commerce businesses that receive customer service inquiries about orders, products, and policies — precisely what Agent Red's six-agent pipeline is designed to handle. The Shopify App Store puts Agent Red directly in front of buyers who are actively searching for solutions.

### Stripe

| Metric | Value |
|--------|-------|
| Businesses using Stripe | 3.1M+ |
| SaaS companies on Stripe | ~100,000+ |
| Agent Red's addressable via Stripe | All e-commerce merchants globally (not limited to Shopify) |

**Key insight:** Stripe provides no discovery mechanism. The 3.1M businesses are Stripe's customers, not Agent Red's. Agent Red must drive 100% of traffic through SEO, content marketing, paid ads, affiliates, and partnerships. However, Stripe expands the addressable market beyond Shopify to include BigCommerce, WooCommerce, Magento, and custom-platform merchants.

### Paddle

| Metric | Value |
|--------|-------|
| SaaS companies using Paddle | 4,000+ |
| Customer discovery channel | None |
| Agent Red's addressable via Paddle | Zero additional (no discovery) |

**Key insight:** Paddle provides zero customer acquisition benefit. Its 4,000+ SaaS companies are sellers, not buyers. Paddle's ecosystem skews toward developer tools and productivity SaaS, not e-commerce services.

### Verdict: Addressable Market

| Platform | Market Access | Rating |
|----------|---------------|--------|
| **Shopify App Store** | Direct access to 700K–1M merchants actively using CS tools | ★★★★★ |
| **Stripe** | Access to all e-commerce merchants (requires own marketing) | ★★★☆☆ |
| **Paddle** | No market access; pure infrastructure | ★☆☆☆☆ |

---

## 4. Partner Diversity & Competitor Landscape

A healthy ecosystem with established competitors signals validated demand and creates an environment where a price disruptor can thrive. Agent Red's strategy is to join this ecosystem and compete on value.

### Shopify App Store Competitors

The "Customer support" category has 200–400+ apps across segments:

| Competitor | Rating | Reviews | Pricing | AI Approach |
|------------|--------|---------|---------|-------------|
| **Gorgias** | 4.3–4.4/5 | 700–800+ | $10–$900/mo + $0.36/automation | AI bolted onto helpdesk |
| **Tidio** | 4.6–4.7/5 | 1,800–2,000+ | Free–$499/mo + $39/mo Lyro | Chat widget + basic AI bot |
| **Re:amaze** | 4.7/5 | 200–300+ | $29–$899/mo (per-agent) | Multi-channel helpdesk |
| **Richpanel** | 4.5–4.6/5 | 100–200+ | $29–$899/mo (per-conversation) | Self-service + AI |
| **Zendesk** | 3.5–3.7/5 | 150–200+ | $19–$115/agent/mo + AI add-on | Enterprise helpdesk + AI add-on |
| **Intercom** | 4.0–4.3/5 | 50–100+ | $39–$139/seat + $0.99/resolution | Messaging + Fin AI |
| **HelpCenter** | 4.6–4.7/5 | 1,500–2,000+ | Free–$19.99/mo | FAQ builder (no AI) |
| **Certainly** | 4.5+/5 | 50–100+ | Custom pricing | Conversational AI |

**The competitive gap:** No app in the Shopify ecosystem offers a purpose-built, six-agent AI customer service platform at Agent Red's price point. Established competitors charge 2–13x more per interaction:

| Platform | Cost at 5,000 conversations/mo | vs. Agent Red Pro ($399) |
|----------|-------------------------------|--------------------------|
| Intercom + Fin AI | ~$5,049 | 12.7x more |
| Gorgias + Automate | ~$1,250–$2,100 | 3.1–5.3x more |
| Zendesk + AI | ~$575–$1,000 | 1.4–2.5x more |
| Richpanel | ~$499–$899 | 1.3–2.3x more |
| Tidio + Lyro | ~$218 | 0.5x (but basic AI, no pipeline) |
| **Agent Red Professional** | **$399** | **Baseline** |

### Stripe Ecosystem Competitors

All major AI customer service platforms use Stripe for billing: Intercom, Gorgias, Tidio, Zendesk, Freshdesk, Help Scout, Crisp, LiveChat. This validates Stripe's billing infrastructure but provides no discovery advantage.

### Paddle Ecosystem Competitors

Paddle users skew toward developer tools (1Password, Framer, CleanMyMac). Few or no AI customer service platforms use Paddle. No established competitor ecosystem to disrupt.

### Verdict: Partner Diversity

| Platform | Competitor Ecosystem | Disruption Opportunity | Rating |
|----------|---------------------|----------------------|--------|
| **Shopify App Store** | 200–400+ CS apps, established leaders with high prices | Excellent — clear price gap in AI-native category | ★★★★★ |
| **Stripe** | All major competitors use it (validates infrastructure) | N/A — Stripe is invisible infrastructure | ★★★☆☆ |
| **Paddle** | Few CS/AI competitors | Poor — no ecosystem to disrupt | ★☆☆☆☆ |

---

## 5. Partner Program Benefits

### Shopify Partner Program

| Benefit | Detail | Value to Agent Red |
|---------|--------|--------------------|
| **0% commission on first $1M** | No revenue share until annual app revenue exceeds $1M | Critical — free distribution at launch |
| **15% commission above $1M** | Only on incremental revenue past $1M/year | Acceptable at scale |
| **Free Partner account** | No setup, listing, or membership fees | Zero cost to start |
| **Free development stores** | Unlimited test stores for QA | Essential for integration testing |
| **App Store listing** | Distribution to ~5M merchants | Primary discovery channel |
| **Partner Dashboard** | Revenue analytics, install/uninstall tracking, review management | Business intelligence |
| **Partner Academy** | Free courses, certifications | Team development |
| **Staff Picks eligibility** | High-quality apps may be editorially featured | Organic visibility boost |
| **Co-marketing opportunities** | Blog features, case studies (earned, not guaranteed) | Marketing amplification |
| **Shopify CLI** | App scaffolding, local dev, automatic HTTPS tunneling | Development productivity |
| **Billing friction elimination** | Charges on existing Shopify invoice — no new payment entry | Higher conversion rates |

### Stripe Partner Program

| Benefit | Detail | Value to Agent Red |
|---------|--------|--------------------|
| **Technology Partner listing** | Partner directory at stripe.com/partners | Minimal visibility |
| **Co-marketing (selective)** | Available for larger partners | Unlikely at launch |
| **Technical support** | Integration assistance | Helpful but standard |
| **Beta program access** | Early access to new features | Minor advantage |
| **No commission on revenue** | Stripe charges processing fees only | Standard model |

### Paddle Partner Program

| Benefit | Detail | Value to Agent Red |
|---------|--------|--------------------|
| **No partner marketplace** | No partner directory or listing | No visibility |
| **Technical support** | Integration assistance | Standard |
| **Tax/compliance handled** | Primary value proposition | Operational benefit |
| **No commission beyond fees** | Paddle charges transaction fees only | Standard model |

### Affiliate Program Support (All Platforms)

None of the three platforms provide native affiliate management. All require a third-party tool:

| Tool | Cost | Integrates With |
|------|------|-----------------|
| **Rewardful** | ~$49–$99/mo | Stripe, Paddle |
| **FirstPromoter** | ~$49–$99/mo | Stripe, Paddle |
| **PartnerStack** | ~$200–$500+/mo | Stripe, Paddle |
| **Shopify Collabs** | Basic | Shopify only |

For Agent Red's planned recurring affiliate commissions ($30–$37/mo per Starter referral), Rewardful + Stripe is the recommended combination for the direct channel. For the Shopify channel, the Shopify Billing API handles revenue, and affiliate tracking would be managed through Agent Red's own referral system.

### Verdict: Partner Program

| Platform | Program Quality | Launch-Stage Value | Rating |
|----------|----------------|-------------------|--------|
| **Shopify App Store** | Comprehensive: $0 commission, distribution, tools, education | Exceptional | ★★★★★ |
| **Stripe** | Basic: partner listing, technical support | Minimal | ★★☆☆☆ |
| **Paddle** | None meaningful | None | ★☆☆☆☆ |

---

## 6. Billing Capabilities

### Feature Comparison Matrix

| Capability | Stripe | Shopify Billing API | Paddle |
|------------|--------|--------------------:|--------|
| Recurring subscriptions | ✅ Native | ✅ Native | ✅ Native |
| Annual + monthly intervals | ✅ Native | ✅ Native | ✅ Native |
| Mixed intervals (annual base + monthly add-ons) | ✅ Native | ⚠️ Requires separate subscriptions | ✅ Native |
| Metered/usage-based billing | ✅ Mature (Usage Records API) | ⚠️ Supported (appUsageRecordCreate) with capped amount | ⚠️ Supported (verify maturity) |
| Add-on modules | ✅ Subscription Items | ⚠️ Multi-line items or separate subscriptions | ✅ Multi-item subscriptions |
| One-time charges (packs) | ✅ Checkout Sessions | ✅ appPurchaseOneTimeCreate | ✅ One-time charges |
| Pack expiration (90-day) | ❌ App logic required | ❌ App logic required | ❌ App logic required |
| Free trial | ✅ trial_period_days | ✅ trialDays parameter | ✅ Trial support |
| Coupons/discounts | ✅ Coupon + Promotion Code objects | ⚠️ Limited (no native coupon system) | ✅ Discount support |
| Self-service portal | ✅ Hosted (billing-only) | ❌ Must build custom | ✅ Hosted (basic) |
| Upgrade/downgrade | ✅ With proration | ✅ New subscription replaces old | ✅ With proration |
| Dunning (failed payment) | ✅ Smart Retries + emails | ✅ Shopify handles collection | ✅ Smart retries + emails |
| Webhook provisioning | ✅ Comprehensive events | ✅ App-specific events | ✅ Comprehensive events |
| Test mode | ✅ Full parity + test clocks | ✅ test: true parameter | ✅ Full sandbox |

### Shopify Billing API Limitations

Two notable constraints for Agent Red:

1. **Capped usage amount:** Merchants must pre-approve a maximum monthly overage when subscribing. Agent Red cannot charge beyond the cap without re-approval. Mitigation: set reasonable default caps, notify at 80%, offer one-click cap increase.

2. **No native coupons:** Shopify's Billing API does not have a coupon/promotion code system. Nonprofit, startup, and agency discounts would need to be implemented as custom pricing tiers or manually adjusted subscriptions.

### Verdict: Billing Capabilities

| Platform | Capability Match | Rating |
|----------|-----------------|--------|
| **Stripe** | Complete — every requirement supported natively or with minimal app logic | ★★★★★ |
| **Shopify Billing API** | Strong — core billing works, some constraints on coupons and capped usage | ★★★★☆ |
| **Paddle** | Good — metered billing maturity needs verification | ★★★☆☆ |

---

## 7. Fee Structure & Cost Modeling

### Per-Transaction Costs

| Transaction | Stripe (2.9% + $0.30) | Stripe + Tax (3.4% + $0.30) | Shopify (0% < $1M) | Shopify (15% > $1M) | Paddle (5% + $0.50) |
|-------------|----------------------|---------------------------|---------------------|---------------------|--------------------|
| $149/mo Starter | $4.62 (3.1%) | $5.37 (3.6%) | $0.00 (0%) | $22.35 (15%) | $7.95 (5.3%) |
| $399/mo Professional | $11.87 (3.0%) | $13.87 (3.5%) | $0.00 (0%) | $59.85 (15%) | $20.45 (5.1%) |
| $999/mo Enterprise | $29.27 (2.9%) | $34.27 (3.4%) | $0.00 (0%) | $149.85 (15%) | $50.45 (5.0%) |

### Annual Revenue Impact at Scale

**Scenario: 50 customers (20 Starter, 20 Professional, 10 Enterprise, all monthly)**

Monthly revenue: ~$17,960

| Platform | Monthly Fees | Annual Fees | Effective Rate |
|----------|-------------|-------------|----------------|
| **Shopify (under $1M)** | $0 | $0 | 0.0% |
| **Stripe** | ~$538 | ~$6,456 | 3.0% |
| **Stripe + Tax** | ~$628 | ~$7,536 | 3.5% |
| **Paddle** | ~$923 | ~$11,076 | 5.1% |
| **Shopify (above $1M)** | ~$2,694 | ~$32,328 | 15.0% |

**Key breakpoints:**

| Milestone | Shopify Effective Rate | Stripe + Tax Rate | Shopify Break-Even vs Stripe |
|-----------|----------------------|-------------------|------------------------------|
| $0–$1M ARR | 0% | 3.5% | Shopify wins by $35K |
| $1.2M ARR | ~2.5% | 3.5% | Shopify still wins |
| $2.3M ARR | ~8.5% | 3.5% | Stripe wins |
| $4.8M ARR | ~11.9% | 3.5% | Stripe wins by $403K |

**Conclusion:** For Agent Red's first $1M in revenue (likely the first 1–2 years), Shopify's 0% commission saves approximately $35,000 compared to Stripe. As revenue scales past ~$2.3M/year, the dual-channel model becomes important: new Shopify merchants install through the App Store (billing via Shopify), while direct/non-Shopify customers use the website (billing via Stripe). This naturally balances the fee structure.

### Fixed Platform Costs

| Cost | Stripe | Shopify | Paddle |
|------|--------|---------|--------|
| Platform fee | $0/mo | $0/mo (Partner account is free) | $0/mo |
| Affiliate tool | ~$49–$99/mo (Rewardful) | N/A (custom tracking) | ~$49–$99/mo (FirstPromoter) |
| Tax compliance | $0 (Stripe Tax) or ~$50–$300/mo (Avalara) | N/A (Shopify handles) | $0 (included in MoR) |
| Total fixed | $49–$399/mo | $0/mo | $49–$99/mo |

### Verdict: Cost

| Platform | Year 1 Economics | At Scale | Rating |
|----------|-----------------|----------|--------|
| **Shopify App Store** | Best (0% to $1M) | Expensive (15%) | ★★★★★ (at launch) |
| **Stripe** | Good (3–3.5%) | Best (consistent 3–3.5%) | ★★★★☆ |
| **Paddle** | Expensive (5.1–5.4%) | Expensive (5.1–5.4%) | ★★☆☆☆ |

---

## 8. Developer Experience

| Dimension | Stripe | Shopify | Paddle |
|-----------|--------|---------|--------|
| **API design** | Excellent (industry gold standard) | Good (GraphQL primary, REST fallback) | Good (modern REST) |
| **SDKs** | 10+ languages, auto-generated from OpenAPI | Node.js, Ruby, PHP (Remix template) | JS, Node.js, Python |
| **CLI tools** | Stripe CLI (webhook forwarding, test triggers, fixtures) | Shopify CLI (app scaffold, local dev, tunneling) | None notable |
| **Test mode** | Full parity + test clocks (simulate future events) | test: true flag + development stores | Full sandbox |
| **Documentation** | Best-in-class (interactive, examples in 7+ languages) | Very good (shopify.dev, interactive GraphQL explorer) | Good (developer.paddle.com) |
| **Webhook reliability** | Retry up to 72 hrs, HMAC verification, delivery logs | Event-driven, Shopify-managed delivery | Retry with backoff, signature verification |
| **Checkout customization** | Full (Elements for embedded, Checkout for hosted) | Embedded in Shopify Admin (Billing API flow) | Limited (overlay/inline only) |
| **Time to implement** | Days (billing) | 1–2 weeks (app submission + review) | Days (billing) |
| **Community** | Very large | Large (Shopify-specific) | Smaller |

### Shopify App-Specific Development

Building a Shopify app requires additional development beyond billing:

| Component | Effort | Required? |
|-----------|--------|-----------|
| Shopify OAuth integration | Already built (Agent Red's Shopify integration exists) | ✅ Yes |
| Shopify Billing API integration | New development | ✅ Yes (for App Store billing) |
| App Bridge UI (embedded admin panel) | New development | ⚠️ Recommended but not strictly required |
| Polaris-styled admin UI | New development | ⚠️ Optional but improves review chances |
| App Store listing (screenshots, description, demo video) | Content creation | ✅ Yes |
| App review submission | 5–15 business days | ✅ Yes |

Agent Red's existing Shopify integration (OAuth, product sync, order lookup, customer profiles, inventory) is already 80% of what a Shopify app requires. The primary new work is the Billing API integration and the App Store listing materials.

### Verdict: Developer Experience

| Platform | Dev Experience | Agent Red Readiness | Rating |
|----------|---------------|-------------------|--------|
| **Stripe** | Best-in-class | No existing integration; start from scratch | ★★★★★ |
| **Shopify App Store** | Very good | 80% of integration already exists | ★★★★☆ |
| **Paddle** | Good | No existing integration; start from scratch | ★★★☆☆ |

---

## 9. Tax & Compliance

| Dimension | Stripe | Shopify | Paddle |
|-----------|--------|---------|--------|
| **US sales tax** | Stripe Tax (0.5%/tx) or self-manage | Shopify handles for App Store sales | Paddle handles everything (MoR) |
| **EU VAT** | Stripe Tax or self-manage | Shopify handles | Paddle handles |
| **Tax filing** | Agent Red files (or use Stripe Tax reports) | Shopify files for App Store revenue | Paddle files everything |
| **Tax registration** | Agent Red registers in nexus states | Not required for App Store revenue | Not required |
| **PCI compliance** | SAQ-A (minimal — Stripe.js handles card data) | Not applicable (Shopify handles) | Not applicable (Paddle MoR) |
| **Invoice compliance** | Agent Red generates | Shopify generates for merchants | Paddle generates for customers |
| **Chargeback handling** | Agent Red responds ($15/dispute) | Shopify handles | Paddle absorbs cost |
| **Compliance effort** | Moderate (Stripe Tax helps) | None (for App Store channel) | None |

### Tax Burden Comparison for a 2-Person Startup

| Scenario | Stripe (with Stripe Tax) | Shopify App Store | Paddle |
|----------|-------------------------|-------------------|--------|
| Register for sales tax | Agent Red must register in nexus states | Not needed | Not needed |
| File tax returns | Agent Red files (with Stripe Tax reports) | Not needed | Not needed |
| Monitor nexus thresholds | Agent Red monitors (Stripe Tax helps) | Not needed | Not needed |
| Annual compliance cost | $1,000–$5,000 (accounting + filing) | $0 | $0 |
| Annual compliance time | 20–40 hours | 0 hours | 0 hours |

### Verdict: Tax & Compliance

| Platform | Compliance Burden | Rating |
|----------|------------------|--------|
| **Paddle** | Zero (full MoR) | ★★★★★ |
| **Shopify App Store** | Zero (for App Store revenue) | ★★★★★ |
| **Stripe** | Moderate (Stripe Tax helps but Agent Red still files) | ★★★☆☆ |

---

## 10. Strategic Fit Assessment

### User's Strategic Criteria

> *"We want to join an ecosystem that includes a number of established competitors with popular offerings which we can match in terms of technology, features and quality, but beat dramatically on price."*

Scoring each platform against this specific strategy:

| Criterion | Shopify App Store | Stripe | Paddle |
|-----------|-------------------|--------|--------|
| **Ecosystem with established competitors** | ✅ Gorgias (700+ reviews), Tidio (1,800+), Zendesk, Intercom, Re:amaze, Richpanel — all present | ⚠️ Same competitors use Stripe, but invisible to customers | ❌ No CS/AI competitor ecosystem |
| **Competitors have popular offerings** | ✅ Multiple apps with hundreds/thousands of reviews and active installs | N/A (Stripe is infrastructure) | ❌ |
| **Agent Red can match on technology/quality** | ✅ Six-agent AI pipeline is architecturally superior to bolt-on AI features | N/A | N/A |
| **Agent Red can beat on price** | ✅ 2–13x cheaper per interaction than every major competitor | N/A | N/A |
| **Buyers can discover Agent Red** | ✅ Category browsing, search, featured apps | ❌ Must drive all traffic | ❌ Must drive all traffic |
| **Buyers can compare directly** | ✅ Side-by-side in App Store | ❌ Only via own marketing | ❌ Only via own marketing |
| **Low barrier to switching** | ✅ Easy install from App Store, charges on existing invoice | ⚠️ Requires new payment entry | ⚠️ Requires new payment entry |
| **Trust signal for new product** | ✅ App Store review = quality endorsement | ❌ Must build trust from zero | ❌ Must build trust from zero |

### Why Dual-Channel Wins

The Shopify App Store satisfies the strategic criteria perfectly: established competitors, direct comparison, pre-qualified buyers, and frictionless conversion. But it limits reach to Shopify merchants only.

Stripe extends reach to **all** e-commerce merchants (BigCommerce, WooCommerce, Magento, custom platforms) who find Agent Red through SEO, content marketing, or referrals. These merchants cannot install from the Shopify App Store.

Together, the two channels cover Agent Red's complete addressable market:

| Channel | Audience | Acquisition | Billing |
|---------|----------|-------------|---------|
| Shopify App Store | Shopify merchants (~5M stores) | Organic discovery + search + comparison | Shopify Billing API |
| Agent Red website (Stripe) | All e-commerce merchants | SEO, content, affiliates, ads | Stripe Billing |

**Critical rule:** Merchants who install from the Shopify App Store **must** be billed through Shopify's Billing API (mandatory per Partner Program Agreement). Merchants who sign up on agentred.io are billed through Stripe, even if they happen to use Shopify. The same Agent Red product and infrastructure serves both channels — only the billing integration and onboarding flow differ.

### Why Not Paddle

| Reason | Detail |
|--------|--------|
| **No ecosystem to disrupt** | Paddle has no marketplace, no competitor landscape, no buyer discovery |
| **Higher fees** | 5% + $0.50 vs. Stripe's 3.5% (with Tax) or Shopify's 0% |
| **Redundant with Shopify** | Shopify handles tax/compliance for App Store sales at 0% commission — Paddle's MoR advantage is nullified |
| **Dual-system complexity** | Would still need Shopify Billing API for App Store + Paddle for direct = two systems |
| **Slower payouts** | Net-15/30 vs. Stripe's T+2 — cash flow risk for early-stage startup |
| **Revenue accounting** | MoR model creates complex revenue recognition (net vs. gross) |
| **Metered billing maturity** | Less proven than Stripe for usage-based pricing |

Paddle's sole advantage — eliminating tax/compliance burden — is already provided by the Shopify channel (Shopify handles tax for App Store revenue) and manageable on the Stripe channel (Stripe Tax at 0.5% per transaction, with tax reports for filing).

---

## 11. Recommended Architecture

### Billing Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Red Platform                         │
│                                                              │
│  ┌─────────────────┐          ┌──────────────────┐          │
│  │  Shopify App     │          │  Direct Website   │          │
│  │  Store Channel   │          │  Channel          │          │
│  │                  │          │                   │          │
│  │  Discovery:      │          │  Discovery:       │          │
│  │  App Store       │          │  SEO, Content,    │          │
│  │  search/browse   │          │  Affiliates, Ads  │          │
│  │                  │          │                   │          │
│  │  Billing:        │          │  Billing:         │          │
│  │  Shopify         │          │  Stripe           │          │
│  │  Billing API     │          │  Billing          │          │
│  │                  │          │                   │          │
│  │  Tax:            │          │  Tax:             │          │
│  │  Shopify handles │          │  Stripe Tax       │          │
│  │                  │          │                   │          │
│  │  Commission:     │          │  Fees:            │          │
│  │  0% (first $1M)  │          │  ~3.5% per tx     │          │
│  └────────┬─────────┘          └────────┬──────────┘          │
│           │                              │                    │
│           ▼                              ▼                    │
│  ┌─────────────────────────────────────────────────┐         │
│  │          Unified Webhook Handler                  │         │
│  │  (subscription.created → provision tenant)        │         │
│  │  (subscription.updated → adjust features)         │         │
│  │  (subscription.canceled → deprovision)            │         │
│  └────────────────────┬────────────────────────────┘         │
│                       │                                       │
│                       ▼                                       │
│  ┌─────────────────────────────────────────────────┐         │
│  │          Azure Tenant Infrastructure              │         │
│  │  Cosmos DB · Key Vault · Container Apps · NATS    │         │
│  └─────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Channel Priority

| Priority | Channel | Rationale |
|----------|---------|-----------|
| **P0 (Launch 1.0)** | Shopify App Store | Pre-qualified buyers, zero commission, frictionless conversion, competitive positioning |
| **P0 (Launch 1.0)** | Stripe direct | Non-Shopify merchants, SEO/content traffic, full billing control |
| **P2 (Post-Launch)** | Evaluate channel mix | Measure which channel drives more revenue and higher-quality customers |
| **Deferred** | Paddle | Reconsider if international tax burden becomes unmanageable on the Stripe channel |

---

## 12. Implementation Roadmap

### Phase 2.1 Tasks (Updated)

| Priority | Task | Effort | Channel |
|----------|------|--------|---------|
| P0 | Create Stripe account (live + test mode) | 1 hr | Stripe |
| P0 | Create Products, Prices, Coupons in Stripe (test mode) | 2 hrs | Stripe |
| P0 | Implement Stripe Checkout for plan selection | 4 hrs | Stripe |
| P0 | Implement Stripe webhook handler (subscription lifecycle) | 8 hrs | Stripe |
| P0 | Implement metered usage reporting to Stripe | 4 hrs | Stripe |
| P0 | Add Shopify Billing API integration to existing Shopify app code | 8 hrs | Shopify |
| P0 | Create Shopify App Store listing (description, screenshots, demo) | 4 hrs | Shopify |
| P0 | Submit for Shopify App Store review | 1 hr | Shopify |
| P1 | Implement Stripe Customer Portal link | 1 hr | Stripe |
| P1 | Implement conversation pack purchase flow | 4 hrs | Both |
| P1 | Build unified webhook handler (both channels → provisioning) | 8 hrs | Both |
| P1 | Set up Stripe Tax | 2 hrs | Stripe |
| P2 | Build Agent Red customer dashboard (usage, add-ons) | 16 hrs | Both |
| P2 | Set up Rewardful for affiliate program | 4 hrs | Stripe |
| P3 | Migrate to Stripe Elements (custom checkout UI) | 8 hrs | Stripe |
| **Total** | | **75 hrs** | |

### Budget Impact

| Line Item | Monthly Cost |
|-----------|-------------|
| Stripe processing (variable) | ~3.5% of direct revenue |
| Shopify commission | $0 (first $1M ARR) |
| Rewardful (affiliate tracking) | ~$49–$99/mo |
| **Total fixed** | **$49–$99/mo** |

This is within the PROJECT-PLAN.md budget line of "$0–79/mo for e-commerce" (with the Rewardful cost slightly above if using the higher tier).

---

## 13. Items Requiring Verification

Before committing to implementation, the following items should be verified against current published information:

### High Priority

| Item | Verification Source |
|------|-------------------|
| Shopify revenue share (0% < $1M, 15% > $1M) | shopify.dev/docs/apps/billing, Partner Program Agreement |
| Shopify Billing API capped amount behavior | shopify.dev/docs/apps/billing/subscriptions |
| Stripe Billing fee tiers (Starter 0.5% vs Scale 0.8%) | stripe.com/billing |
| Stripe Tax fee (0.5%/tx) | stripe.com/tax |
| Active Shopify merchant count (Q1 2026) | investors.shopify.com |
| Competitor pricing (Gorgias, Tidio, Intercom) | Individual app listings at apps.shopify.com |

### Medium Priority

| Item | Verification Source |
|------|-------------------|
| Shopify App Store review timeline | shopify.dev/docs/apps/store/review |
| Competitor review counts and ratings | apps.shopify.com |
| Rewardful pricing and Stripe integration | rewardful.com |
| Stripe Test Clocks current capabilities | stripe.com/docs/billing/testing |
| Shopify App Store paid promotion availability | Shopify Partner Dashboard |

### Low Priority

| Item | Verification Source |
|------|-------------------|
| Paddle metered billing maturity | developer.paddle.com |
| Paddle current fee structure (5% + $0.50) | paddle.com/pricing |
| Stripe data residency options (EU) | stripe.com |
| AI customer service market size projections | Industry reports |

---

## Appendix A: Shopify App Store Approval & Partner Growth Path

### App Store Approval Process (9 Steps)

| Step | Action | Timeline |
|------|--------|----------|
| 1 | Create Partner account at partners.shopify.com | Instant (Agent Red already has one) |
| 2 | Create public app in Partner Dashboard | Same day |
| 3 | Build to Shopify technical standards | Development phase |
| 4 | Create app listing (name, screenshots, description, pricing, privacy policy) | 1–2 days |
| 5 | Complete pre-submission checklist in Partner Dashboard | 1 day |
| 6 | Submit for review (include test credentials, development store with app installed) | Same day |
| 7 | Shopify App Review Team manually tests | 5–10 business days |
| 8 | Outcome: Approved, Changes Required (specific feedback), or Rejected | — |
| 9 | Post-approval monitoring (reviews, API version compliance) | Ongoing |

**Total timeline (no issues):** 1–2 weeks. **With feedback rounds:** 2–4 weeks.

### What the Review Team Checks

| Category | Key Checks |
|----------|-----------|
| **Technical** | OAuth 2.0 with HMAC validation, App Bridge integration, Billing API for all charges, GDPR webhooks (3 mandatory endpoints), session token auth, HTTPS everywhere, current API version |
| **User Experience** | Clear onboarding, graceful empty states, error handling, loading indicators, Polaris design conventions, responsive layout, clean uninstall |
| **Listing** | Description matches real behavior, accurate screenshots, transparent pricing, valid support URL, valid privacy policy, no keyword stuffing |
| **Policy** | Minimal API scopes, no selling merchant data, no redirecting to competitors, no deceptive practices |

### Mandatory Technical Requirements

| Requirement | Documentation |
|-------------|--------------|
| OAuth 2.0 (HMAC, state param, secure token storage) | shopify.dev/docs/apps/auth/oauth |
| App Bridge 3.x+ (embedded experience) | shopify.dev/docs/api/app-bridge |
| Shopify Billing API (all charges) | shopify.dev/docs/apps/billing |
| 3 GDPR webhooks (customers/data_request, customers/redact, shop/redact) | shopify.dev/docs/apps/webhooks/configuration/mandatory-webhooks |
| Session token authentication (not cookies) | shopify.dev/docs/apps/auth |
| Polaris design system | polaris.shopify.com |
| Current, non-deprecated API version | shopify.dev/docs/api/usage/versioning |

### Common Rejection Reasons

Not using Billing API · Requesting excessive API scopes · Missing GDPR webhooks · Poor onboarding UX · Broken OAuth flow · Listing doesn't match actual app · No clear value proposition · Crashes during review · Missing privacy policy · Slow load times · Not using App Bridge · Deprecated API version.

### "Built for Shopify" Badge

A quality certification badge introduced in 2023 that signals the highest integration standards.

| Requirement Type | Criteria |
|------------------|----------|
| **Technical** | Latest App Bridge, embedded app, Polaris UI, session tokens, GraphQL Admin API, app extensions where applicable, current API version, GDPR webhooks |
| **Quality** | Fast load times, low error/crash rate, guided onboarding, responsive support, ~4.0+ star rating (verify), meaningful install count |
| **Business** | Live on App Store, no policy violations, ongoing maintenance |

**Benefits:** Trust badge on listing, potential search ranking boost, increased conversion, higher likelihood of Staff Picks and editorial features.

**Agent Red strategy:** Build to Built for Shopify standards from day one (avoids costly retrofit). Apply for the badge ~3–6 months post-launch once installs, reviews, and stability track record are established.

### Partner Growth Path (No Formal Tiers)

Shopify does **not** have named tiers (Bronze/Silver/Gold). Benefits scale informally with growth:

| Growth Stage | Installs | Benefits That Unlock |
|-------------|----------|---------------------|
| **Launch** | 0–100 | Standard partner support, documentation, free dev stores, Partner Dashboard analytics |
| **Growing** | 100–1,000 | Potential editorial features, improved review team responsiveness |
| **Established** | 1,000–10,000 | Dedicated partner support contact, beta feature access invitations |
| **Major** | 10,000–50,000 | Dedicated partner manager, co-marketing, event invitations, early API access |
| **Top-tier** | 50,000+ | Strategic partnership, joint marketing campaigns, keynote mentions |

### Revenue Share

| Revenue Bracket | Shopify Commission | Developer Keeps |
|----------------|-------------------|-----------------|
| First $1M (lifetime/annual — verify) | 0% | 100% |
| Above $1M | 15% | 85% |

### App Store Optimization (ASO) Factors

| Factor | Weight | Agent Red Action |
|--------|--------|-----------------|
| Keyword relevance (name, tagline, description) | High | Name: "Agent Red AI Customer Service" |
| Install count + momentum | High | Launch promotion, affiliates |
| Average star rating (target 4.5+) | High | In-app review prompt after positive outcomes |
| Review count + recency | Medium-High | Steady review velocity over time |
| Retention rate (installs ÷ uninstalls) | Medium-High | Excellent onboarding, time-to-value |
| Listing quality (video, screenshots, completeness) | Medium | Professional screenshots, demo video |
| Built for Shopify badge | Medium | Apply at 3–6 months |

### App Store Advertising

Shopify introduced App Store Ads (~2024). Pay-per-click search ads and category page placements. Availability and pricing should be verified at shopify.dev/docs/apps/launch/promote. Highly relevant for accelerating initial installs.

### Additional Shopify Programs

| Program | Relevance | When to Pursue |
|---------|-----------|----------------|
| **Shopify Plus Partners** | High (enterprise merchants = $999/mo tier) | After 5–10 Plus merchant customers |
| **App Challenges / Competitions** | Medium (AI-themed challenges increasingly common) | Monitor announcements |
| **Partner Academy certifications** | Low-Medium (team credibility) | Complete App Development cert pre-submission |
| **Referral program** | Low (refers merchants to Shopify, not apps) | Not primary focus |

---

## Appendix B: Stripe Partner Program & Enhanced Benefits

### Partner Types

| Type | Description | Agent Red Fit |
|------|-------------|---------------|
| **Technology Partner** | Software companies integrating Stripe into their products | Primary fit |
| **Consulting Partner** | Agencies implementing Stripe for clients | Not applicable |
| **Platform Partner** | Companies using Stripe Connect for marketplace payments | Future (if agency model) |

### Application Process

1. Submit at stripe.com/partners (company info, use case, projected volume)
2. Stripe partnerships team reviews (2–6 weeks reported)
3. Approval grants access to partner portal and basic benefits

### Partner Program (No Formal Named Tiers)

Like Shopify, Stripe does **not** publish a rigid tier ladder. Benefits scale with volume and strategic importance:

| Stage | Processing Volume | Benefits |
|-------|------------------|----------|
| **Standard** | Any | Partner portal, badge, directory listing, documentation, email support |
| **Verified** | Live integration required | "Stripe Verified" badge, enhanced directory listing, improved credibility, potential co-marketing |
| **Growth** | ~$50K–$250K/mo | Rate discussions, potential account representative |
| **Strategic** | ~$250K+/mo | Dedicated partner manager, co-marketing funds, joint case studies, conference invitations, early API access |
| **Enterprise** | $1M+/mo | Named account manager, quarterly business reviews, custom commercial terms, dedicated engineering support |

### Stripe Verified Partner Program

| Aspect | Detail |
|--------|--------|
| **What it is** | Quality certification badge — Stripe validates integration quality and business standing |
| **Requirements** | Live production integration, technical review (API usage, error handling, security), business review, customer references |
| **Application** | Through partner portal (4–8 weeks review) |
| **Benefits** | "Stripe Verified" badge, enhanced directory listing, increased credibility, potential co-marketing access |

### Volume-Based Pricing Negotiation

| Monthly Volume | Likely Outcome |
|----------------|---------------|
| Under $50K/mo | Standard rates (2.9% + $0.30), no negotiation leverage |
| $50K–$80K/mo | Initial rate discussions possible |
| $80K–$250K/mo | Meaningful reductions (interchange-plus, lower per-tx fee) |
| $250K–$1M/mo | Significant custom pricing, account representative assigned |
| Over $1M/mo | Premium terms, dedicated account manager, quarterly reviews |

**Agent Red at launch:** ~$15K/mo processing → standard rates apply. Custom pricing becomes relevant at ~200+ customers.

### Stripe for Startups

| Aspect | Detail |
|--------|--------|
| **URL** | stripe.com/startups |
| **Typical benefits** | Waived fees on initial volume (~$20K), product credits, priority onboarding |
| **Eligibility** | Typically accelerator/VC-backed; bootstrapped companies may qualify for direct programs |
| **Agent Red action** | Check eligibility — costs nothing to apply |

### Stripe App Marketplace

| Aspect | Detail |
|--------|--------|
| **URL** | marketplace.stripe.com |
| **Purpose** | Apps that extend the Stripe Dashboard (not standalone SaaS distribution) |
| **Agent Red fit** | Not primary. Could build a lightweight analytics widget as a lead-gen tool post-launch |
| **Review process** | Submit via developer tools, 2–4 week review for security/quality/UX |

### Marketing & Co-Marketing Benefits

| Benefit | Standard Partner | Verified | Strategic |
|---------|-----------------|----------|-----------|
| Partner directory listing | ✅ | ✅ Enhanced | ✅ Featured |
| Partner badge | ✅ Basic | ✅ Verified badge | Custom |
| Blog / case study features | Unlikely | Possible | Likely |
| Co-marketing funds (MDF) | ❌ | Unlikely | ✅ |
| Stripe Sessions conference | Purchase tickets | Complimentary | VIP + speaking |
| Email newsletter features | ❌ | ❌ | Possible |

### Stripe Climate

| Aspect | Detail |
|--------|--------|
| **What** | Contribute a % of revenue to carbon removal projects |
| **Cost** | 0.5%–1% of Stripe-processed revenue (~$75–$150/mo at launch) |
| **Benefits** | "Stripe Climate" badge, customer-facing messaging, potential blog features |
| **Agent Red action** | Consider enabling at 0.5% post-launch for brand differentiation |

### Key Stripe URLs

| Resource | URL |
|----------|-----|
| Partner Program | stripe.com/partners |
| Verified Partners | stripe.com/partners/verified |
| Partner Directory | stripe.com/partners/directory |
| App Marketplace | marketplace.stripe.com |
| Startups Program | stripe.com/startups |
| Stripe Climate | stripe.com/climate |
| Stripe Sessions | stripe.com/sessions |

### Items Requiring Verification (Partner-Specific)

| Item | Source |
|------|--------|
| Formal partner tier names (if introduced post-May 2025) | stripe.com/partners |
| Verified Partner exact requirements | stripe.com/partners/verified |
| Startup program eligibility for bootstrapped LLCs | stripe.com/startups |
| Volume pricing thresholds (not publicly documented) | Contact Stripe sales |
| App Marketplace submission requirements | marketplace.stripe.com |
| Stripe Climate badge program current status | stripe.com/climate |

---

## Summary Scorecard

| Dimension | Weight | Shopify App Store | Stripe | Paddle |
|-----------|--------|-------------------|--------|--------|
| Addressable market size | 25% | ★★★★★ | ★★★☆☆ | ★☆☆☆☆ |
| Partner diversity / competitors | 20% | ★★★★★ | ★★★☆☆ | ★☆☆☆☆ |
| Partner program benefits | 15% | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ |
| Billing capabilities | 15% | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| Cost / fees | 10% | ★★★★★ | ★★★★☆ | ★★☆☆☆ |
| Developer experience | 5% | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| Tax & compliance | 5% | ★★★★★ | ★★★☆☆ | ★★★★★ |
| Strategic fit (price disruption) | 5% | ★★★★★ | ★★★☆☆ | ★☆☆☆☆ |
| **Weighted Score** | **100%** | **★★★★★ (4.7)** | **★★★☆☆ (3.3)** | **★★☆☆☆ (1.6)** |

### Final Recommendation

**Use both Shopify App Store (primary) and Stripe (secondary).** Do not use Paddle.

The Shopify App Store is the highest-value channel because it satisfies every strategic criterion: a large addressable market of pre-qualified buyers, a rich ecosystem of established competitors with high prices, a partner program that charges zero commission on the first $1M, and a discovery mechanism that puts Agent Red directly in front of merchants actively searching for AI customer service. Agent Red's existing Shopify integration provides an 80% head start on building the app.

Stripe provides the essential complement: full billing control for non-Shopify merchants, the industry's best developer experience for complex subscription management, and a consistent ~3.5% fee structure that scales predictably.

Together, the two channels cover Agent Red's complete market with optimal economics at every growth stage.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
