# Rewardful Affiliate Integration

Integration guide for connecting Rewardful affiliate tracking to Agent Red's Stripe billing pipeline.

---

## Overview

Rewardful is an affiliate tracking platform built specifically for Stripe-based SaaS. It provides affiliate link generation, click tracking, conversion attribution, commission calculation, and payout management. Agent Red uses Rewardful to power its affiliate/partner program.

**Architecture:** Rewardful sits between your marketing site and Stripe. It tracks visitors via a JavaScript snippet, attributes conversions via `client_reference_id` on Stripe Checkout Sessions, and calculates commissions by listening to Stripe webhook events (invoices, refunds, subscription changes).

```
Visitor → affiliate link (?via=token)
    ↓
Rewardful JS → sets first-party cookie (referral UUID)
    ↓
Frontend → reads Rewardful.referral → sends to backend
    ↓
Backend → creates Stripe Checkout Session with client_reference_id = referral UUID
    ↓
Stripe → processes payment → sends webhook to Rewardful (automatic)
    ↓
Rewardful → matches referral → creates commission → writes metadata to Stripe Customer
    ↓
Affiliate → sees conversion in Rewardful dashboard
```

---

## What Agent Red Code Does

The code integration is minimal. Only one file was modified:

**`src/integrations/stripe_checkout.py`**
- Added optional `referral` field to `CheckoutRequest` (Rewardful referral UUID from frontend)
- Passes `referral` as `client_reference_id` on the Stripe Checkout Session
- Only included when non-empty (Stripe raises an error on empty `client_reference_id`)

Everything else (commission calculation, affiliate portal, payouts) is handled by Rewardful's platform.

---

## Pre-Launch Setup Checklist

These steps must be completed before the affiliate program goes live. Rewardful **does not support Stripe test mode** — all setup requires a live Stripe account.

### 1. Connect Rewardful to Live Stripe

- [ ] Switch Agent Red's Stripe account to live mode
- [ ] In Rewardful dashboard → Settings → Integrations → "Connect with Stripe"
- [ ] Authorize Rewardful's OAuth request (requires Stripe admin permissions)
- [ ] Verify connection shows "Connected" in Rewardful dashboard

Rewardful automatically registers its own webhook endpoints on your Stripe account during this step.

### 2. Create a Campaign

- [ ] In Rewardful dashboard → Campaigns → Create Campaign
- [ ] Configure commission structure:
  - **Recommended for launch:** 20% recurring commission for 12 months
  - This yields ~$30-37/month per referred Starter subscriber (see CLAUDE.md pricing rationale)
- [ ] Set cookie duration (recommended: 60 days)
- [ ] Set minimum payout threshold (recommended: $50)

### 3. Add JavaScript Snippet to Marketing Site

Add to the `<head>` tag of every page on the marketing site and application:

```html
<script>
(function(w,r){w._rwq=r;w[r]=w[r]||function(){(w[r].q=w[r].q||[]).push(arguments)}})(window,'rewardful');
</script>
<script async src='https://r.wdfl.co/rw.js' data-rewardful='YOUR_API_KEY'></script>
```

Replace `YOUR_API_KEY` with the API key from Rewardful dashboard → Settings → General.

For cross-domain tracking (if marketing site and app are on different domains):

```html
<script async src='https://r.wdfl.co/rw.js'
  data-rewardful='YOUR_API_KEY'
  data-domains='agentred.ai,app.agentred.ai'>
</script>
```

### 4. Wire Frontend Checkout to Pass Referral

When the frontend creates a checkout session, include the Rewardful referral UUID:

```javascript
rewardful('ready', function() {
  fetch('/api/checkout/session', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tier: 'starter',
      interval: 'month',
      referral: Rewardful.referral || null  // UUID or null
    })
  });
});
```

The backend (`stripe_checkout.py`) handles the rest — it passes the referral as `client_reference_id` on the Stripe Checkout Session.

### 5. Configure Payout Method

- [ ] In Rewardful dashboard → Settings → Payouts
- [ ] Connect PayPal or Wise for bulk affiliate payouts
- [ ] Set payout schedule (recommended: monthly, net-30)

### 6. Test End-to-End (Live Mode)

- [ ] Create a test affiliate account in Rewardful
- [ ] Generate a test affiliate link
- [ ] Visit the marketing site via the affiliate link
- [ ] Verify Rewardful cookie is set (browser dev tools → Application → Cookies)
- [ ] Complete a checkout with a real payment method
- [ ] Verify the conversion appears in the Rewardful dashboard
- [ ] Verify commission was calculated correctly
- [ ] Refund the test transaction and verify commission adjustment

---

## Rewardful API Reference (For Future Use)

The REST API is available for custom workflows but is **not required for launch**.

| Detail | Value |
|--------|-------|
| Base URL | `https://api.getrewardful.com/v1/` |
| Auth | HTTP Basic (API Secret as username, blank password) |
| Rate Limit | 45 requests per 30 seconds |
| Pagination | `{ pagination: {...}, data: [...] }` |

**Potentially useful endpoints:**
- `POST /affiliates` — programmatically create affiliates (e.g., auto-enroll customers)
- `GET /referrals` — list referrals with conversion status
- `GET /commissions` — list commissions for reporting

**Webhook events** (configured in Rewardful dashboard → Webhooks):
- `referral.converted` — a referred visitor became a paying customer
- `commission.created` — a commission was generated
- `payout.due` — a payout is ready for fulfillment

These webhooks are optional for launch. Rewardful handles the full affiliate lifecycle without them.

---

## Cost

| Plan | Monthly | Affiliate Revenue Cap |
|------|---------|----------------------|
| Starter | $49/mo | $7,500/mo |
| Growth | $99/mo | $15,000/mo |
| Enterprise | $149+/mo | Unlimited |

**Recommendation for launch:** Starter plan ($49/month). No transaction fees. The $7,500/month cap is well within Launch 1.0 expectations.

---

## Key Constraints

1. **Rewardful does not support Stripe test mode.** All integration testing requires live Stripe.
2. **Shopify channel is not supported.** Rewardful only works with Stripe (or Paddle). Shopify App Store merchants do not go through Stripe Checkout, so affiliate tracking does not apply to the Shopify billing channel.
3. **JavaScript snippet is required.** Without the frontend snippet, no referral cookies are set and `Rewardful.referral` will always be empty.
4. **Rewardful is not available as an NPM package.** It must be loaded via the `<script>` tag.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
