# ARR Forecast Analysis — Agent Red Customer Experience

**Date:** 2026-02-01  
**Purpose:** Estimate customer counts to reach target ARR levels, gross profit at each level, and time-to-ARR under affiliate-led growth with normal churn.  
**Sources:** CLAUDE.md, cost_model.py, Master Plan §6, Rewardful benchmarks, B2B SaaS churn benchmarks

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## 1. Pricing and ARR Per Customer

| Tier | Monthly | Annual (list) | ARR per customer |
|------|---------|---------------|------------------|
| Starter | $149 | $1,788 | $1,788 |
| Professional | $399 | $4,788 | $4,788 |
| Enterprise | $999 | $11,988 | $11,988 |

*Note: Annual plans (17% off) reduce ARR slightly; this analysis uses list pricing.*

---

## 2. Customer Mix Assumptions

Typical SMB SaaS has more low-tier than high-tier. Three mixes:

| Mix | Starter | Professional | Enterprise | Weighted ARR/customer |
|-----|---------|--------------|------------|------------------------|
| **Conservative** | 60% | 30% | 10% | $3,708 |
| **Moderate** | 50% | 35% | 15% | $4,368 |
| **Optimistic** | 40% | 40% | 20% | $5,028 |

**Moderate** is used as the base case (typical for e-commerce SMB tools).

---

## 3. Customer Count to Reach Target ARR

| Target ARR | Conservative (60/30/10) | Moderate (50/35/15) | Optimistic (40/40/20) |
|------------|-------------------------|---------------------|------------------------|
| **$350,000** | 94 | 80 | 70 |
| **$1,000,000** | 270 | 229 | 199 |
| **$2,500,000** | 674 | 572 | 497 |
| **$10,000,000** | 2,697 | 2,290 | 1,989 |

**Base-case (moderate mix):** ~80 customers for $350K, ~229 for $1M, ~572 for $2.5M, ~2,290 for $10M.

---

## 4. Gross Profit at Each Level

**Cost basis (Master Plan §6, cost_model.py):**
- Fixed infrastructure: $252–436/month ($3,024–$5,232/year)
- Per-tenant marginal: ~$13–41/month at 10+ tenants
- Variable AI cost: ~$0.0073/conversation
- **Gross margin:** 76–90% by tier (Starter 87–90%, Pro 82–85%, Enterprise 83–85%)

**Blended gross margin (moderate mix):** ~85%

| Target ARR | Gross Profit (85% margin) | Gross Profit Range (82–88%) |
|------------|---------------------------|-----------------------------|
| **$350,000** | $297,500 | $287,000 – $308,000 |
| **$1,000,000** | $850,000 | $820,000 – $880,000 |
| **$2,500,000** | $2,125,000 | $2,050,000 – $2,200,000 |
| **$10,000,000** | $8,500,000 | $8,200,000 – $8,800,000 |

*Gross profit = revenue minus COGS (infrastructure + AI variable). Does not include affiliate commissions, sales, or marketing.*

**Affiliate commission impact (20% recurring for 12 months):** If 20% of new MRR is attributed to affiliates, that is a sales/marketing expense, not COGS. Gross profit is unchanged; operating profit would be reduced by affiliate payouts (~$30–37/customer/month for Starter per REWARDFUL-INTEGRATION.md).

---

## 5. Time to Reach Each ARR Level — Forecast

**Assumptions:**
- **Churn:** SMB B2B SaaS monthly churn 3–5% (benchmark: ~4.2% average 2024). Agent Red’s ICP (e-commerce SMB) aligns with higher end: **4% monthly** (~40% annual).
- **Affiliate channel:** Rewardful benchmarks for AI/ML SaaS: 15–25% MRR from affiliates once established; 6–12 months to meaningful affiliate revenue; 3–5× scaling possible in a quarter.
- **Primary marketing:** Affiliate links and discount codes (per CLAUDE.md); Shopify App Store discovery; limited paid spend.
- **Conversion:** Referral conversion 7%+ (industry benchmark); Shopify App Store conversion varies by listing quality.

**Forecast methodology:** Uses industry benchmarks for AI SaaS + B2B SMB, adjusted for affiliate-led growth. No company-specific historical data exists; these are illustrative ranges.

| Target ARR | Customers (moderate) | Time to Reach | Rationale |
|------------|----------------------|---------------|-----------|
| **$350,000** | ~80 | **12–18 months** | Achievable in Year 1 for AI SaaS with strong affiliate (HeadshotPro, getimg.ai: 15% MRR from affiliates, $50K+ monthly from program within 6–12 months). 80 customers at 4% churn requires ~5–7 net new/month sustained; affiliate ramp (6–12 mo) supports this once program matures. |
| **$1,000,000** | ~229 | **24–36 months** | Year 2–3. Affiliate at 15–25% of MRR; rest from organic Shopify discovery, trials, word-of-mouth. 229 customers implies ~10–12 net new/month sustained after churn. Middle tier of Rewardful programs ($100K–$500K annual affiliate revenue) fits this scale. |
| **$2,500,000** | ~572 | **42–60 months** | Year 3.5–5. Requires scaling affiliate network, possible partner/agency channel, stronger Shopify ranking. Top 15% of Rewardful programs reach $500K–$1M affiliate revenue; Agent Red would need to be in that cohort. |
| **$10,000,000** | ~2,290 | **72–120 months** | Year 6–10. Enterprise-level scale. Typically requires sales motion, partner channel, and/or significant paid acquisition in addition to affiliate. Top 6% of affiliate programs exceed $1M annual affiliate revenue; Agent Red would need multiple channels beyond affiliate-only. |

**Sensitivity:**  
- **Lower churn (3% monthly):** Time to each level shortens by ~15–25%.  
- **Higher affiliate contribution (25%+ MRR):** Time to $350K–$1M can shorten by ~20–30% if affiliate ramps quickly.  
- **Paid acquisition added:** Would accelerate all milestones but is out of scope for “primary marketing via affiliate.”

---

## 6. Summary Table

| Target ARR | Customers (moderate mix) | Gross Profit | Time (months) | Time (years) |
|------------|--------------------------|--------------|---------------|--------------|
| $350,000 | ~80 | ~$297,500 | 12–18 | 1.0–1.5 |
| $1,000,000 | ~229 | ~$850,000 | 24–36 | 2.0–3.0 |
| $2,500,000 | ~572 | ~$2,125,000 | 42–60 | 3.5–5.0 |
| $10,000,000 | ~2,290 | ~$8,500,000 | 72–120 | 6.0–10.0 |

---

## 7. Caveats and Data Gaps

1. **No historical data:** Agent Red has no prior customer or revenue history. Forecasts rely on industry benchmarks only.
2. **Churn:** 4% monthly is a benchmark; actual churn depends on product-market fit, onboarding, and support quality.
3. **Affiliate mix:** Rewardful data is for established programs. New programs take 6–12 months to reach 15–25% MRR contribution.
4. **Shopify effect:** App Store discovery can materially change growth if listing and reviews perform well; not modeled explicitly.
5. **Add-ons:** Revenue from add-on modules (Multi-Language, Advanced Analytics, etc.) could raise ARR per customer and reduce customer count needed; not included in this analysis.

---

## 8. References

- [Rewardful SaaS Affiliate Program Benchmarks 2025](https://www.rewardful.com/articles/saas-affiliate-program-benchmarks) — AI/ML SaaS 15–25% MRR, 6–12 months to meaningful revenue
- [B2B SaaS Churn Benchmarks 2024](https://usermotion.com/saas-churn-rate-benchmark-2024) — SMB 3–5% monthly, ~4.2% average
- CLAUDE.md — Pricing, cost model
- docs/Master-Plan-Review-01-30-2026.md §6 — Cost validation, margins
- docs/architecture/REWARDFUL-INTEGRATION.md — Affiliate commission structure

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
