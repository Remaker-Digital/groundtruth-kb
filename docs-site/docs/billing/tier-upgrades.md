---
sidebar_position: 3
title: Tier Upgrades & Add-ons
---

# Tier Upgrades & Add-ons

## Upgrading your plan

Agent Red offers three subscription tiers: **Starter**, **Professional**, and **Enterprise**. You can upgrade your plan at any time from the Account & billing page.

### How to upgrade

1. Navigate to **Account & billing** in your admin dashboard.
2. Click **Upgrade Plan** to see available tiers.
3. Review the **upgrade preview** — this shows your prorated cost, the features you'll gain, and the billing impact.
4. Click **Confirm Upgrade** to be redirected to Stripe Checkout.
5. Complete payment. Your plan upgrades immediately upon successful payment.

### What changes on upgrade

- **Included conversations** adjust to your new tier's monthly allowance.
- **Customer Memory layers** unlock (Professional adds cross-session learning; Enterprise adds predictive insights).
- **Overage rate** decreases on higher tiers.
- **Rate limits** are 300 requests per minute for all tiers — rate limits are a safety mechanism and do not change on upgrade.
- Billing is prorated — you only pay the difference for the remainder of your current billing cycle.

## Entitlements by tier

Each tier includes a set of entitlements that define what your Agent Red installation can do.

| Feature | Starter | Professional | Enterprise |
|---------|---------|-------------|------------|
| **Monthly conversations** | 1,000 | 5,000 | 20,000 |
| **Overage rate** | $0.04/conv | $0.025/conv | $0.015/conv |
| **Customer Memory layers** | Layer 1–2 | Layer 1–3 | Layer 1–4 |
| **Rate limit** | 300 RPM | 300 RPM | 300 RPM |
| **Concurrent conversations** | 5 | 10 | 30 |

### Customer Memory layers

Agent Red's Customer Memory system has four progressive layers:

1. **Layer 1 — Session context:** The AI remembers what was said within the current conversation.
2. **Layer 2 — Customer profiles:** The AI recognizes returning customers (via verified email) and recalls their preferences, order history, and previous issues.
3. **Layer 3 — Cross-session learning:** The AI identifies patterns across conversations to improve its responses over time. Available on Professional and Enterprise.
4. **Layer 4 — Predictive insights:** The AI anticipates customer needs based on behavioral patterns and proactively offers relevant information. Enterprise only.

## Rate limiting

All tiers share the same rate limit: **300 requests per minute** per tenant. Rate limiting is a safety mechanism to protect the platform, not a monetization lever.

- The rate limit applies uniformly across Starter, Professional, and Enterprise tiers.
- Typical admin dashboard usage is 5–15 requests per minute. Typical widget chat usage is 1–3 requests per minute. The 300 RPM limit is well above normal usage.
- When you exceed the rate limit, the API returns HTTP 429 with a `Retry-After` header indicating how many seconds to wait.
- Response headers include `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` so your integration can monitor usage.

## Trial period

New accounts start with a **14-day free trial** that includes Professional-tier entitlements (5,000 conversations, Memory layers 1–3). After the trial expires, you choose a paid tier to continue using Agent Red.

## Add-on modules

Add-on modules extend your plan with specialized capabilities. Available add-ons depend on your current tier.

### Purchasing add-ons

1. Navigate to **Account & billing** in your admin dashboard.
2. Scroll to the **Add-on Modules** section.
3. Click **Purchase** on the add-on you want.
4. Complete payment via Stripe Checkout.
5. The add-on activates immediately.

### Available add-ons

| Add-on | Minimum tier | Description |
|--------|-------------|-------------|
| Custom Model Training | Enterprise | Per-customer fine-tuning on 1,000+ interactions |
| Advanced Analytics | Professional | Extended analytics with intent breakdown and trend analysis |
| Priority Support | Professional | Dedicated support channel with guaranteed response times |
| Additional Conversation Packs | Starter | Top up your monthly conversation allowance |
| White-Label Widget | Enterprise | Remove Agent Red branding from the chat widget |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
