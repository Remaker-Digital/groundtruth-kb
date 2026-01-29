# Agent Red Customer Engagement - Launch 1.0 Project Plan

> **Project:** Agent Red Customer Engagement
> **Release:** Launch 1.0
> **Timeline:** Q1 2026 (8-12 weeks)
> **Budget:** $500-1,000/month operational

---

## Executive Summary

Agent Red Customer Engagement is a commercial SaaS product built on the open-source AGNTCY Customer Engagement Platform foundation. Launch 1.0 targets MVP delivery within Q1 2026, focusing on core commercial infrastructure and Phase 1-2 marketing materials.

---

## Project Phases

### Phase 0: Project Setup (Week 1)
**Status:** Complete ✅

| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| Create project directory structure | ✅ Done | - | E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement |
| Create CLAUDE.md | ✅ Done | - | AI assistant guidance (v2.0 with full knowledge transfer) |
| Create PROJECT-PLAN.md | ✅ Done | - | This file |
| Create GitHub private repository | ✅ Done | - | github.com/Remaker-Digital/agent-red-customer-engagement |
| AGNTCY dependency model | ✅ Done | - | Arms-length via public GitHub (no submodule) |
| Migrate commercial materials | ✅ Done | - | SaaS proposal, product features, website content |
| Initial commit pushed | ✅ Done | - | 23 files, 5,825 lines |
| Docker dev environment | ✅ Done | - | Dockerfile, docker-compose.yml, requirements.txt |
| AGNTCY baseline verification (local) | ✅ Done | - | 15 containers healthy, 97.8% unit / 99.3% integration pass |
| AGNTCY baseline verification (Azure) | ✅ Done | - | All 53 resources operational, evaluation 94% intent / 100% escalation precision |
| Set up GitHub Project board | ✅ Done | - | [Project #2](https://github.com/orgs/Remaker-Digital/projects/2), 8 milestone issues (M1-M8) |

---

### Phase 1: Foundation (Weeks 2-4)

#### 1.1 Brand Identity *(can start immediately)*
**Direction:** Bold/Corporate — dark reds, navy/charcoal accents, strong sans-serif typography
**Approach:** AI-generated concepts and full brand system drafted in-house

| Task | Effort | Status |
|------|--------|--------|
| Logo concepts (primary, icon, wordmark) | 8 hrs | 📋 Todo |
| Color palette selection | 2 hrs | 📋 Todo |
| Typography selection | 2 hrs | 📋 Todo |
| Brand guidelines document | 4 hrs | 📋 Todo |
| Favicon and app icons | 2 hrs | 📋 Todo |

#### 1.2 Legal Documents *(can run parallel with 1.1)*
**Approach:** AI-draft all documents first. Termly/iubenda deferred until closer to launch.

| Task | Effort | Status |
|------|--------|--------|
| Draft Terms of Service | 4 hrs | 📋 Todo |
| Draft Privacy Policy | 2 hrs | 📋 Todo |
| Draft SLA document | 4 hrs | 📋 Todo |
| Draft Data Processing Agreement | 2 hrs | 📋 Todo |
| Validate via Termly/iubenda | 2 hrs | 📋 Deferred to pre-launch |

#### 1.3 Website Content *(depends on 1.1 brand identity)*
**Approach:** Full rewrite for commercial buyer audience. Existing AGNTCY content used as technical reference only.
**Platform:** Deferred — content written in markdown, hosting platform chosen later.

| Task | Effort | Status |
|------|--------|--------|
| Write homepage (commercial buyer focus) | 4 hrs | 📋 Todo |
| Write features page | 3 hrs | 📋 Todo |
| Write pricing page | 2 hrs | 📋 Todo |
| Write integrations page | 3 hrs | 📋 Todo |
| Write about page | 2 hrs | 📋 Todo |
| Write contact page | 2 hrs | 📋 Todo |

#### 1.4 Public Documentation *(can start alongside 1.3)*
**Approach:** Scaffold Docusaurus + conceptual guides now. API-specific docs deferred to Phase 2.

| Task | Effort | Status |
|------|--------|--------|
| Set up Docusaurus | 4 hrs | 📋 Todo |
| Write getting-started guide | 4 hrs | 📋 Todo |
| Write Shopify integration guide | 3 hrs | 📋 Todo |
| Write API authentication guide | 2 hrs | 📋 Deferred to Phase 2 |
| Document API endpoints | 8 hrs | 📋 Deferred to Phase 2 |

---

### Phase 2: Product & Infrastructure (Weeks 5-8)

#### 2.1 E-Commerce Store
**Platform:** Deferred decision — Shopify vs Stripe to be evaluated alongside multi-tenant architecture design.

| Task | Effort | Status |
|------|--------|--------|
| Evaluate Shopify vs Stripe for SaaS subscriptions | 4 hrs | 📋 Todo |
| Set up development store/account | 2 hrs | 📋 Todo |
| Create product catalog (3 tiers + 5 add-ons) | 4 hrs | 📋 Todo |
| Configure subscription/recurring billing | 8 hrs | 📋 Todo |
| Build license key / provisioning system | 12 hrs | 📋 Todo |
| Test checkout flow | 4 hrs | 📋 Todo |

#### 2.2 Multi-Tenant Infrastructure
**Approach:** Dedicated architecture document required before any implementation. Architecture approach TBD.

| Task | Effort | Status |
|------|--------|--------|
| Write multi-tenant architecture document | 8 hrs | 📋 Todo |
| Design tenant isolation architecture | 8 hrs | 📋 Todo |
| Implement tenant provisioning | 16 hrs | 📋 Todo |
| Build usage metering | 12 hrs | 📋 Todo |
| Create customer portal (basic) | 16 hrs | 📋 Todo |
| Implement API key management | 8 hrs | 📋 Todo |

#### 2.3 Admin Guides *(deferred — requires working product)*
| Task | Effort | Status |
|------|--------|--------|
| Initial setup guide | 4 hrs | 📋 Todo |
| Shopify connection guide | 2 hrs | 📋 Todo |
| Knowledge base setup guide | 3 hrs | 📋 Todo |
| Monitoring and alerts guide | 3 hrs | 📋 Todo |

#### 2.4 Demo Videos *(deferred — requires working product)*
| Task | Effort | Status |
|------|--------|--------|
| Platform overview (2-3 min) | 4 hrs | 📋 Todo |
| Quick start tutorial (3-5 min) | 4 hrs | 📋 Todo |

---

### Phase 3: Launch Preparation (Weeks 9-12)

#### 3.1 Testing & QA
| Task | Effort | Status |
|------|--------|--------|
| End-to-end checkout testing | 8 hrs | 📋 Todo |
| Multi-tenant isolation testing | 8 hrs | 📋 Todo |
| Load testing | 8 hrs | 📋 Todo |
| Security review | 8 hrs | 📋 Todo |

#### 3.2 Deployment
| Task | Effort | Status |
|------|--------|--------|
| Set up production environment | 8 hrs | 📋 Todo |
| Configure monitoring | 4 hrs | 📋 Todo |
| Set up alerting | 4 hrs | 📋 Todo |
| Document runbooks | 8 hrs | 📋 Todo |

#### 3.3 Launch Readiness
| Task | Effort | Status |
|------|--------|--------|
| Final website review | 4 hrs | 📋 Todo |
| Final documentation review | 4 hrs | 📋 Todo |
| Soft launch (beta users) | - | 📋 Todo |
| Address beta feedback | 16 hrs | 📋 Todo |
| Public launch | - | 📋 Todo |

---

## Budget Allocation

### Monthly Operational Costs

| Category | Service | Monthly Cost |
|----------|---------|--------------|
| **Infrastructure** | Azure (production) | $300-500 |
| **E-commerce** | Shopify or Stripe (TBD) | $0-79 |
| **Legal** | Termly + iubenda (deferred to pre-launch) | $0-52 |
| **Marketing** | Buffer (future) | $0-30 |
| **Documentation** | Docusaurus (Vercel) | $0 |
| **Domain/DNS** | Cloudflare | $0-20 |
| **Total** | | **$371-681** |

### One-Time Costs

| Item | Estimated Cost |
|------|----------------|
| Logo design (if outsourced) | $0-500 |
| Stock imagery | $0-100 |
| **Total** | **$0-600** |

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Timeline slip | High | Medium | MVP scope, prioritize core features |
| Budget overrun | Medium | Low | Aggressive cost monitoring, lean approach |
| Multi-tenant complexity | High | Medium | Start simple, iterate |
| Brand confusion with AGNTCY | Medium | Low | Clear differentiation messaging, full website rewrite |
| E-commerce platform fit | Medium | Medium | Evaluate Shopify vs Stripe before committing |

---

## Success Criteria

### Launch 1.0 Minimum Viable

| Criterion | Target |
|-----------|--------|
| Website live | ✅ Yes |
| Documentation published | ✅ Yes |
| Legal documents published | ✅ Yes |
| Shopify store operational | ✅ Yes |
| First trial signup | ✅ Yes |
| Platform stable for 48 hrs | ✅ Yes |

### Post-Launch (30 days)

| Metric | Target |
|--------|--------|
| Trial signups | 10+ |
| Paid conversions | 2+ |
| Uptime | 99.5%+ |
| Support ticket resolution | <24 hrs |

---

## Dependencies

### External Dependencies

| Dependency | Type | Risk |
|------------|------|------|
| AGNTCY open-source stability | Technical | Medium |
| Azure service availability | Infrastructure | Low |
| Shopify platform | E-commerce | Low |
| Termly/iubenda services | Legal | Low |

### Internal Dependencies

| Item | Depends On |
|------|------------|
| Website launch | Brand identity, content |
| E-commerce store | Pricing finalized, products defined, platform decision (Shopify vs Stripe) |
| Multi-tenant infra | Architecture design document approved |
| API documentation | Multi-tenant infrastructure built, API surface defined |
| Conceptual docs | Product features known (can start Phase 1) |
| Admin guides | Working product to document |
| Demo videos | Working product to demonstrate |

---

## Team & Responsibilities

| Role | Responsibilities |
|------|------------------|
| Product Owner | Scope decisions, prioritization, acceptance |
| Technical Lead | Architecture, code review, technical decisions |
| Developer | Implementation, testing, deployment |
| Content | Website copy, documentation, guides |
| Design | Brand identity, UI/UX (if applicable) |

---

## Communication

### Status Updates

| Meeting | Frequency | Purpose |
|---------|-----------|---------|
| Sprint planning | Weekly | Plan next week's work |
| Standup | Daily | Progress, blockers |
| Demo | Bi-weekly | Show completed work |
| Retrospective | Bi-weekly | Process improvement |

### Documentation

| Document | Update Frequency |
|----------|------------------|
| PROJECT-PLAN.md | Weekly |
| CLAUDE.md | As needed |
| GitHub Issues | Daily |
| Project Board | Daily |

---

## Milestones

| Milestone | Target Date | Deliverables |
|-----------|-------------|--------------|
| **M1: Setup Complete** | Week 1 | Repo, project board ✅ |
| **M2: Brand Ready** | Week 3 | Logo concepts, color palette, typography, brand guidelines |
| **M3: Legal Ready** | Week 4 | AI-drafted ToS, Privacy, SLA, DPA (Termly/iubenda deferred) |
| **M4: Website Live** | Week 5 | Marketing site deployed |
| **M5: Store Live** | Week 7 | E-commerce store operational (platform TBD) |
| **M6: Docs Complete** | Week 8 | Documentation published |
| **M7: Soft Launch** | Week 10 | Beta users invited |
| **M8: Public Launch** | Week 12 | General availability |

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-29 | Initial project plan |
| 1.1.0 | 2026-01-29 | Phase 0 complete: GitHub repo created, initial commit pushed, arms-length dependency model established |
| 1.2.0 | 2026-01-29 | Docker dev environment added, AGNTCY baseline verified (local Docker + production Azure) |
| 1.3.0 | 2026-01-29 | Work priority review complete: brand direction (Bold/Corporate), legal approach (AI-draft first), website (full rewrite), docs (conceptual now, API later), e-commerce platform deferred, multi-tenant architecture doc required, admin guides/videos deferred |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
