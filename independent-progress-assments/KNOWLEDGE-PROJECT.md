# Knowledge: Project — Agent Red Customer Experience

**Purpose:** Persistent project knowledge for Cursor: key risks, open decisions, and areas that warrant periodic re-check or opposition attention.  
**Location:** `independent-progress-assments/`.  
**Update:** Add when a risk or decision recurs; update status when resolved or deferred; trim when obsolete.

---

## 1. Key Risks (Loyal Opposition Watch List)

| Risk | Source | Status | Notes |
|------|--------|--------|--------|
| Planning docs lag implementation | cursor-assessment-report 2026-01-31; Master Plan / PROJECT-PLAN | Partially addressed | CLAUDE.md is canonical status; Master Plan work item registry and PROJECT-PLAN were updated in follow-up. Re-check after major milestones. |
| Admin frontend not build-validated | CLAUDE.md "Next priority" | Open | npm install, TypeScript compile, bundle check for admin/shopify and admin/standalone not yet confirmed. |
| Widget bundle not copied to Theme App Extension | CLAUDE.md | Open | Built widget IIFE should be copied to `extensions/agent-red-chat/assets/`. |
| P2 launch-quality tests not run | COMPREHENSIVE-TEST-PLAN.md §6 | Open | ~135 tests; launch quality gate. |
| Integration testing with real Stripe/Shopify | CLAUDE.md | Open | End-to-end flows with test mode / partner sandbox not yet done. |
| Creative assets for App Store blocked on design | CLAUDE.md | Deferred | Icon, screenshots, demo video. |
| Layer 3 PatternExtractionService not implemented | Phase 2.5 | Deferred | Professional+; WI #90-92. |

---

## 2. Constraints (Loyal Opposition)

- **File operations:** Loyal Opposition may create/add/modify documents **only within** `independent-progress-assments/` without permission. Must not create, delete, or modify files outside that directory without explicit permission from Mike.
- **INSIGHTS naming:** Session-specific files: `INSIGHTS-MM-DD-YYYY-HH-mm.md` (e.g. `INSIGHTS-02-01-2026-14:35.md`).

## 3. Open Decisions / Tensions

- **Loyal opposition output format:** Findings in LOYAL-OPPOSITION-LOG.md; optional separate "open questions" file if Mike prefers. Current: single log with status.
- **Scope of opposition:** Technical, process, product, commercial (all in scope per CURSOR-LOYAL-OPPOSITION-ROLE.md) until Mike narrows.

---

## 4. Areas for Periodic Re-Check

- **CLAUDE.md vs. other docs:** README, PROJECT-PLAN, Master Plan work items, pricing tables — keep alignment with CLAUDE.md as source of truth.
- **Test count and warnings:** CLAUDE.md states "777 tests passing, 0 warnings"; re-check after test additions or refactors.
- **Middleware and auth wiring:** Past critical gap (auth middleware not wired) was fixed; any new routers or middleware should be explicitly wired and documented in CLAUDE.md route map.
- **Executive Summary metrics:** When producing or validating Executive Summaries, key counts (tests, routers, routes, modules) should be sourced and dated (per EXEC-SUMMARY-REPORT-GUIDE §10) so third-party validators (e.g. Kiro) can reconcile against their snapshot.

---

## 5. References

- **CLAUDE.md** — Canonical status, working style, priorities.
- **docs/BACKLOG-NEW-WORK-ITEMS.md** — WI #101–163 and beyond.
- **docs/COMPREHENSIVE-TEST-PLAN.md** — P0–P3, security, performance.
- **docs/Master-Plan-Review-01-30-2026.md** — 32 decisions, 100 work items.
- **CURSOR-INSIGHT-DROPBOX/** — Reports, supporting research, INSIGHTS. See CURSOR-KNOWLEDGE-BASE-INDEX.md for contents.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
