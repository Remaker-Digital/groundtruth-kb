# Shopify App Review Pre-Flight Checklist

**Date:** 2026-02-07
**Owner:** Release Manager
**Scope:** Public apps submitted to the Shopify App Store
**Status:** Copy-of-record for Agent Red (canonical — all other checklists defer to this document)

This checklist consolidates authoritative Shopify guidance and required
submission elements. It must be completed before submitting a new app
for review.

**Authoritative sources (verified 2026-02-07):**
- https://shopify.dev/docs/apps/launch/app-requirements-checklist
- https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements
- https://shopify.dev/docs/apps/launch/app-store-review/submit-app-for-review
- https://shopify.dev/docs/apps/launch/app-store-review/review-process
- https://shopify.dev/changelog/starting-april-2025-new-public-apps-submitted-to-shopify-app-store-must-use-graphql
- Shopify Partners blog (review timeline guidance)

**Cross-references within this project:**
- `docs/shopify/APP-STORE-LISTING.md` — listing copy, asset specs (defers to this checklist for submission procedure)
- `docs/operations/LAUNCH-CHECKLIST.md` — broader launch steps including Azure env, storefront, Stripe (defers to this checklist for Shopify-specific items)
- `docs/operations/PRE-GA-VERIFICATION-CHECKLIST.md` — final single-pass verification (defers to this checklist for Shopify review readiness)

---

## 0) Timeline Expectations (Plan Your Launch)

- [ ] **Official average review time** noted in planning materials. Shopify's
      Partners blog states that app reviews are **on average within 7 business
      days**.
- [ ] **Set stakeholder expectations** that timelines can vary and revisions
      extend approval time. Shopify advises review time can vary and revisions
      are common.
- [ ] **Escalation path noted**: Shopify community guidance suggests contacting
      Partner Support if review stalls beyond 30+ business days. Treat this as
      community guidance, not official policy.

---

## 1) App Review Readiness (Required by Shopify)

- [ ] **Install on a development store** and validate the full flow end-to-end
      before submission.
- [ ] **Check OAuth installs for errors** (or use Shopify managed installation
      via CLI). OAuth flow must complete before any app UI renders — reviewer
      sees nothing until install succeeds.
- [ ] **Test in Chrome incognito mode** — session token authentication must work
      without pre-existing cookies or cached state.
- [ ] **Billing API**: all app charges use the Shopify Billing API and test
      charges were executed with `"test": true`, then reset to `"test": false`
      before submission.
- [ ] **Plan upgrade/downgrade tested**: if the app offers multiple tiers, the
      reviewer will test changing between plans. Verify `appSubscriptionCreate`
      handles upgrades (prorate) and downgrades gracefully.
- [ ] **Install eligibility verified**: confirm the app's `scopes` and
      `access_scopes` are correct and the app can install on stores in all
      intended markets.
- [ ] **Protected customer data**: if your app uses protected customer data,
      request access via Partner Dashboard **before** review.
- [ ] **GraphQL Admin API mandate**: as of April 2025, all new public apps
      submitted to the Shopify App Store must use the GraphQL Admin API
      exclusively. REST Admin API calls will fail review. _(Agent Red status:
      `shopify_client.py` uses GraphQL — compliant.)_

---

## 2) Submission Setup (Partner Dashboard Review Page)

- [ ] **Submission contact email** is monitored; `app-submissions@shopify.com`
      and `noreply@shopify.com` are allow-listed.
- [ ] **App configuration** complete:
      - URLs do not contain "Shopify" or "Example."
      - API contact email does not contain "Shopify."
      - App icon uploaded and valid (see §4 for specs).
      - Mandatory compliance webhooks configured.
      - Emergency developer contact (email + phone) set.
- [ ] **Automated checks** in the App Store review page pass. Resolve all
      flagged items before submitting — the reviewer will not proceed until
      automated checks pass.

---

## 3) Compliance & Privacy

- [ ] **Mandatory compliance webhooks** are implemented and verified:
      `customers/data_request`, `customers/redact`, `shop/redact`. _(Agent Red
      status: `shopify_gdpr_webhooks.py` — 3 endpoints, HMAC-SHA256 verified.)_
- [ ] **Webhook verification**: invalid HMAC on compliance webhooks returns
      `401 Unauthorized`.
- [ ] **Privacy policy URL** included in the listing. This is a hard
      requirement — Shopify will reject apps without a linked privacy policy.
- [ ] **No unsubstantiated claims in listing content**: Shopify prohibits
      statistics, performance data, guarantees, or unverified claims anywhere
      in listing text or images. _(Broader than "no unsubstantiated claims" —
      includes any numeric data or stats, e.g. "reduces support tickets by 40%"
      is not allowed unless independently verified.)_
- [ ] **Temporary suspension awareness**: Shopify may temporarily pause or
      suspend your app after approval if issues are found post-launch. Ensure
      monitoring is in place (see §8).

---

## 4) App Store Listing & Assets

### Branding & Naming

- [ ] **App name** is ≤30 characters, starts with the brand name (not a generic
      descriptor), and is consistent across Dev Dashboard (TOML) and listing
      form. _(Example: "Agent Red Customer Experience" — starts with brand
      "Agent Red", not "AI Customer Service".)_
- [ ] **App icon** is identical in Dev Dashboard and listing.

### Listing Accuracy

- [ ] Listing is accurate and truthful about features and requirements.
- [ ] Languages listed reflect actual admin UI languages (do not claim
      languages the app does not support in the admin interface).

### Media & Assets

| Asset | Specification | Required? |
|-------|---------------|-----------|
| **App icon** | 1200×1200 px, JPEG or PNG, square corners (Shopify auto-rounds) | Yes |
| **Screenshots** | 1600×900 px (16:9), 3–6 desktop screenshots, at least one showing actual app UI | Yes |
| **Feature images** | 1600×900 px (16:9), used for App Store feature cards | Recommended |
| **Submission screencast** | Screen recording of full install → core workflow, narrated or captioned in English, submitted to review team | **Mandatory** |
| **Feature/promotional video** | Optional video embedded in listing page for merchants | Optional |

- [ ] **App icon** follows required format (1200×1200, JPEG/PNG, square corners).
- [ ] **Screenshots** are 1600×900 (16:9), minimum 3, at least one showing
      actual app UI in the Shopify admin (not just marketing graphics).
- [ ] **Feature images** comply with 1600×900 size and content rules.
- [ ] **Submission screencast** is ready and submitted (mandatory for review).
      Must be in English. This is a screen recording of the install flow through
      core functionality — it is separate from any promotional video in the
      listing.
- [ ] **Promotional video** (optional) — if included in listing, it is
      distinct from the submission screencast. The listing video is
      merchant-facing; the screencast is reviewer-facing.
- [ ] Pricing is shown only in the pricing section (not in images or
      screenshots).
- [ ] No statistics, data claims, or unsubstantiated guarantees in listing
      text or images.

### Demo Store

- [ ] Demo store URL provided and links directly to the best page to showcase
      core functionality. _(Agent Red: `blanco-9939.myshopify.com` with widget
      active.)_

---

## 5) Review Preparation & Testing Instructions

- [ ] **Testing instructions** are clear, complete, and walk the reviewer
      through every feature step-by-step.
- [ ] **Valid test credentials** provided with full access to all features.
      Shopify explicitly requires complete instructions and valid credentials.
- [ ] If third-party platforms are needed, provide working sandbox credentials.
- [ ] **Screencast covers the full flow**: install → OAuth → onboarding →
      core features → billing → uninstall. Reviewer watches this before
      testing manually.

---

## 6) Performance & Storefront Impact

- [ ] If the app affects the storefront (e.g., injects a widget), run
      **Lighthouse performance checks** on the affected pages.
- [ ] **Lighthouse 10-point threshold**: Shopify tests storefront performance
      by comparing Lighthouse scores with and without the app. The app must
      not reduce the Lighthouse score by more than 10 points. Shopify weights
      pages: home (17%), product details (40%), collection (43%).
- [ ] Widget bundle size confirmed within target. _(Agent Red: ~17KB gzip vs
      Tidio ~40-60KB, Intercom ~80-100KB — well within threshold.)_

---

## 7) Security, APIs & App Bridge

- [ ] App uses **GraphQL Admin API** exclusively (REST Admin API not permitted
      for new public apps as of April 2025).
- [ ] App uses the **latest App Bridge version** (mandatory as of March 13,
      2024 — apps must use the current version at time of submission).
      _(Agent Red: App Bridge loaded via CDN in `admin/shopify/index.html`.)_
- [ ] Sensitive data is handled in compliance with privacy requirements.
- [ ] App respects Shopify API versioning policies (uses a supported,
      non-deprecated API version).
- [ ] Session token authentication works in **Chrome incognito mode** (no
      reliance on pre-existing cookies).

---

## 8) Submission & Post-Submission Monitoring

- [ ] Submit only **production-ready** app (no beta, no missing features,
      no placeholder content).
- [ ] Monitor Partner Dashboard status and submission email for reviewer
      requests.
- [ ] Respond quickly to reviewer questions to reduce delays (Shopify pauses
      the review clock while waiting for responses).
- [ ] If review exceeds **30+ business days**, contact Partner Support for
      an update (community guidance — not official SLA).
- [ ] **Post-approval monitoring**: Shopify may temporarily suspend apps
      post-launch if issues are discovered. Ensure Azure Monitor alerts and
      health check monitoring are active.

---

## Agent Red-Specific Status

Quick reference for Agent Red's compliance with each major requirement area:

| Requirement | Agent Red Status | Notes |
|-------------|-----------------|-------|
| GraphQL Admin API | ✅ Compliant | `shopify_client.py` uses GraphQL exclusively |
| GDPR webhooks | ✅ Implemented | `shopify_gdpr_webhooks.py` — 3 endpoints, HMAC-SHA256 |
| Billing API | ✅ Implemented | `shopify_billing.py` — `appSubscriptionCreate`, usage records |
| App Bridge | ✅ Current | CDN script in `admin/shopify/index.html` |
| Session tokens | ✅ Implemented | JWT HS256 verification in `auth.py` |
| Privacy policy | ⏳ Pending | URL needed (iubenda — see Legal section in CLAUDE.md) |
| App icon | ⏳ Pending | 1200×1200 — owner/designer task |
| Screenshots | ⏳ Pending | 1600×900 — owner/designer task |
| Submission screencast | ⏳ Pending | Owner/designer task |
| Demo store | ✅ Ready | `blanco-9939.myshopify.com` |
| Lighthouse performance | ⏳ Not tested | Widget ~17KB gzip, expected to pass 10-point threshold |
| Plan upgrade/downgrade | ⏳ Not tested | Needs E2E validation |
| Chrome incognito | ⏳ Not tested | Session token auth — needs manual verification |

---

## Appendix: Key Authoritative References

| Topic | URL |
|-------|-----|
| App requirements checklist | https://shopify.dev/docs/apps/launch/app-requirements-checklist |
| App Store requirements | https://shopify.dev/docs/apps/launch/shopify-app-store/app-store-requirements |
| Submit for review | https://shopify.dev/docs/apps/launch/app-store-review/submit-app-for-review |
| Review process & statuses | https://shopify.dev/docs/apps/launch/app-store-review/review-process |
| GraphQL mandate (April 2025) | https://shopify.dev/changelog/starting-april-2025-new-public-apps-submitted-to-shopify-app-store-must-use-graphql |
| Mandatory compliance webhooks | https://shopify.dev/docs/apps/build/privacy/mandatory-webhooks |
| Partners blog: review timelines | Shopify Partners Blog (search "app review timeline") |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last updated: 2026-02-07*
