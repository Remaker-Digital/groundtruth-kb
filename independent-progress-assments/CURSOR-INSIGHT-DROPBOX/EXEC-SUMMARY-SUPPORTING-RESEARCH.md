# Executive Summary — Supporting Research and Data

**Purpose:** Background data, citations, and elaboration material not included in the 3–5 minute executive summary. For future consideration or detailed elaboration.  
**Date:** 2026-02-01  
**Consumer:** Loyal Opposition, Lead Builder, project owner

---

## 1. Competitor Pricing (Verified 2026-02-01)

| Competitor | Scenario A (1K conv) | Scenario B (5K conv, 3 agents) | Scenario C (20K conv, 5 agents) |
|------------|---------------------|--------------------------------|---------------------------------|
| Tidio | ~$198-208 | ~$749+ | — |
| Gorgias | ~$960 | ~$1,440-3,690 | ~$6,300-15,300 |
| Re:amaze | ~$49 | ~$147 | — |
| Intercom | ~$620 | ~$2,730-3,639 | ~$12,540 |
| Zendesk | ~$579+ | ~$5,615 | ~$21,025 |
| **Agent Red** | **$149** | **$399** | **$999** |

Source: docs/research/UI-UX-COMPETITIVE-ANALYSIS.md; all verified against live pricing pages 2026-02-01.

---

## 2. Cost Model (Monthly)

| Component | Cost |
|-----------|------|
| Fixed infrastructure (Option B+) | $252-436 |
| Per-conversation variable | ~$0.0073 |
| Break-even | 2 Starter tenants |

Source: docs/Master-Plan-Review-01-30-2026.md §6.

---

## 3. AWS/GCP Cost Comparison — Not Yet Evaluated

The project has not conducted a formal cost comparison of Azure vs. AWS vs. GCP. References to AWS in the repo are limited to:
- STRIPE-PLATFORM-EVALUATION.md (AWS Marketplace as discovery channel)
- PER-CUSTOMER-AI-PERSONALIZATION-RESEARCH.md (AWS SageMaker for LoRA serving)

**Opportunity:** A dedicated cloud cost comparison (Azure vs. AWS vs. GCP) for the Agent Red stack (container runtime, vector DB, message queue, AI inference, observability) could identify cost reduction or capability improvement opportunities.

---

## 4. Implementation Metrics

| Metric | Value |
|--------|-------|
| Source modules | 38+ in multi_tenant, 10+ in integrations, 5 in chat |
| Lines of code | ~25,000 multi_tenant, ~3,200 widget, ~5,400 admin shared, ~2,700 Shopify admin, ~2,800 standalone admin |
| Tests | 777 passing, 0 warnings |
| Test coverage | P0 + P1 COMPLETE; P2 (~135 tests) not yet run |
| API routes | 17 routers, 66 routes |
| Middleware layers | 8 |

---

## 5. Critical Gaps (from Competitive Analysis)

- Admin frontend build validation not yet run (npm install/build for admin/shopify and admin/standalone)
- Widget bundle not yet copied to Theme App Extension assets
- Integration testing with real Stripe test mode and Shopify partner sandbox not done
- Creative assets (icon, screenshots, demo video) blocked on design

---

## 6. Key Document References

- CLAUDE.md — canonical status
- docs/Master-Plan-Review-01-30-2026.md — 32 decisions, 100 work items
- docs/research/UI-UX-COMPETITIVE-ANALYSIS.md — 5-competitor feature matrix, pricing
- docs/architecture/ECOMMERCE-PLATFORM-EVALUATION.md — Stripe/Shopify/Paddle decision
- docs/COMPREHENSIVE-TEST-PLAN.md — ~880 enumerated tests
- docs/BACKLOG-NEW-WORK-ITEMS.md — WI #101-163+

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
