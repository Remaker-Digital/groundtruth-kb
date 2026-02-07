# Agent Red Customer Experience — Pre-GA Verification Checklist
Date: 2026-02-07
Owner: Release Manager
Purpose: Single-pass verification before GA launch.

Use this checklist after all code changes are frozen and legal/creative assets
are ready. Mark each item complete with evidence notes.

---

## 1. Production Configuration

- [ ] `SHOPIFY_API_KEY` set on API Gateway Container App
- [ ] `SHOPIFY_API_SECRET` set on API Gateway Container App
- [ ] `AZURE_OPENAI_ENDPOINT` set on API Gateway Container App
- [ ] `AZURE_OPENAI_API_KEY` set on API Gateway Container App
- [ ] `APP_CORS_ORIGINS` set to explicit allowlist (no `*`)
- [ ] `APP_CORS_ORIGIN_REGEX` (if used) matches expected Shopify domains only
- [ ] `ENVIRONMENT=production` in production
- [ ] `APPLICATIONINSIGHTS_CONNECTION_STRING` set
- [ ] `AZURE_KEYVAULT_URL` set and health check passes
- [ ] `NATS_URL` set and `/ready` reports connected (if NATS enabled)

Evidence:
- /health:
- /ready:

---

## 2. Shopify App Store Readiness

- [ ] `shopify.app.toml` API version verified against current Shopify supported version
- [ ] `application_url` and GDPR webhook URLs match production FQDN
- [ ] App listing copy reviewed in `docs/shopify/APP-STORE-LISTING.md`
- [ ] Creative assets complete:
  - [ ] 1200x1200 icon
  - [ ] 3 key benefit images (1600x1200)
  - [ ] Desktop screenshot (1600x900+)
  - [ ] Mobile screenshot (750x1334+)
- [ ] Privacy Policy URL published and linked in listing
- [ ] DPA published and linked (if required)
- [ ] Test credentials and testing instructions verified

Evidence:
- Shopify Partner app submission URL:

---

## 3. Stripe Direct Channel

- [ ] Live-mode products/prices created to match `config/stripe_product_ids.json`
- [ ] Live Stripe keys set in production
- [ ] Stripe webhook secret set in production
- [ ] Stripe tax settings verified (origin, auto tax, tax code)
- [ ] Rewardful connected and tested (if enabled)

Evidence:
- Stripe dashboard links:

---

## 4. End-to-End Functional Tests (Production)

- [ ] Tenant #1 provisioned successfully
- [ ] Knowledge base seeded and embedded
- [ ] Chat: start conversation and receive AI response
- [ ] Chat: KB-aware response returns correct pricing
- [ ] Admin (Shopify embedded) loads and navigates
- [ ] Admin (standalone) login works, API key auth works
- [ ] Billing portal opens for a test tenant
- [ ] Usage dashboard returns data
- [ ] GDPR export endpoint works for test tenant
- [ ] GDPR delete endpoint works for test tenant

Evidence:
- Conversation ID:
- Admin URL:

---

## 5. Browser/Device Verification

### Desktop
- [ ] Chrome (latest): widget + admin + chat
- [ ] Edge (latest): widget + admin + chat
- [ ] Firefox (latest): widget + admin + chat

### Mobile
- [ ] iOS Safari: widget renders, chat works
- [ ] Android Chrome: widget renders, chat works

Evidence:
- Device notes:

---

## 6. Observability & Operations

- [ ] /health returns 200
- [ ] /ready returns 200 with Key Vault healthy
- [ ] Circuit breakers all CLOSED
- [ ] Application Insights shows <1% error rate over 5 minutes
- [ ] P95 latency < 2s over 5 minutes (baseline)
- [ ] Log scrubbing verified (no PII in logs)

Evidence:
- App Insights query:

---

## 7. Security & Access Control

- [ ] Standalone admin password changed from any preview value
- [ ] API key rotation endpoint verified (admin only)
- [ ] Widget key scope enforced (cannot access non-chat endpoints)
- [ ] Pre-auth rate limiting verified (429 after repeated failures)
- [ ] Security headers present on API responses

Evidence:
- Header sample:

---

## 8. Final Go/No-Go

- [ ] Legal review complete (ToS, Privacy, DPA)
- [ ] Shopify submission approved or in final review window
- [ ] Rollback plan reviewed (DEPLOYMENT-RUNBOOK)
- [ ] Launch checklist completed (LAUNCH-CHECKLIST)
- [ ] Final sign-off recorded

Sign-off:
- Product Owner:
- Engineering Lead:
- Ops/On-call:

