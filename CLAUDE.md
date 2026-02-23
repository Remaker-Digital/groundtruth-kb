# CLAUDE.md - Agent Red Customer Experience

This document provides active guidance for AI assistants working on the Agent Red Customer Experience commercial project. It is loaded at the start of every session.

> **📁 Reference data** (legal, pricing, infrastructure, AGNTCY rules): `CLAUDE-REFERENCE.md` — read on demand.
> **📁 Architecture** (project structure, module inventory): `CLAUDE-ARCHITECTURE.md` — read on demand.
> **📁 Historical archive** (session logs, technical decisions): `CLAUDE_ARCHIVE.md` — read when investigating historical decisions.
> **📁 Session memory** (operational patterns, lessons): `~/.claude/projects/.../memory/MEMORY.md` — loaded automatically.

---

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | Agent Red Customer Experience |
| **Type** | Commercial SaaS Product (Shopify + Standalone) |
| **Status** | Production v1.56.7 HEALTHY (revision 0000063, S76b). ALL 14 CYCLES + post-14 patches + Cycles 15-19 DEPLOYED. ~4,791 unit tests (1 pre-existing failure), 18/18 T0 regression, 917 UI tests, 25 CQ scenarios (4.75/5.0), CP.1–CP.21 21/21 PASS. See `memory/build-deploy-roadmap.md`. |
| **Owner** | Remaker Digital (DBA of VanDusen & Palmeter, LLC) |

### Copyright Notice

All new work in this repository must include:

```
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
```

---

## Working with This Project

### Starting a New Session

```
Continue work on Agent Red Customer Experience commercial project.
Location: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Current status: Production v1.51.1 HEALTHY. ALL 14 CYCLES + SDK Fix DEPLOYED. 3,985 unit tests, 25 CQ scenarios (CONDITIONAL PASS). Next: [describe task].
```

### Preferred Way of Working

For planning, prioritization, and multi-step decision-making, use an **iterative review process**:

1. Present one work item (or clarification) at a time with relevant context, options, and a recommendation
2. Pause for the owner's input before proceeding to the next item
3. Incorporate feedback immediately and adjust subsequent items as needed
4. Do not batch multiple decisions into a single prompt

This applies to: work priority reviews, architecture decisions, scope changes, milestone planning, and any situation where multiple choices must be made.

### Option Evaluation Criteria

When evaluating options, prioritize in order:

1. **Implementation quality:** Can this be implemented with high efficiency, robustness, reliability, and usability?
2. **Desirability:** Is this competitively strong, differentiating, or obviously superior in usability?
3. **Downstream confidence:** Can documentation, maintenance, and testing be fully accounted for?

**Avoid vague generalizations** ("simpler," "harder," "more complex"). State specifically what is gained or lost: which protocols, failure modes, components, test coverage implications. Token usage and elapsed time are not meaningful concerns.

### Continuous Improvement Feedback

Provide brief inline coaching notes (prefixed with "💡 **Feedback:**" at the end of responses) when observing:

- **Terminology inconsistency** — Standard terms: "WI #NNN" for numbered work items, "work item" for generic, "task" for ad-hoc, "issue" for GitHub Issues
- **Bare approvals that could carry steering** — suggest a one-sentence clarification
- **Approve-then-constrain pattern** — note combining into one message is more efficient
- **Open-ended questions** — suggest a format (table, list, yes/no with evidence)
- **Credential exposure** — flag secrets pasted into chat
- **Missing structure** — suggest bullets or numbers

Skip feedback when the message is already clear. Only flag genuine opportunities.

### Work Priority Bias

**Technical work has elevated priority over creative/content work.** Technical implementation, test case creation, testing/results analysis, and new capabilities are prioritized above creative assets, marketing, and cosmetic work.

### Master Test Plan

The **Master Test Plan** (`docs/MASTER-TEST-PLAN-1.0.md`) is the single canonical document that defines what must be tested and in what order for the 1.0 GA release. It specifies a 15-phase ordered execution sequence where each phase is a child Repeatable Procedure. All 15 phases must pass for the release gate to clear.

**Maintenance rules:**
- Whenever a testing Repeatable Procedure is **created**, it MUST be added to the Master Test Plan as a new phase or within an existing phase.
- Whenever a testing Repeatable Procedure is **updated** (assertions added, removed, or modified), the Master Test Plan MUST be updated to reflect the new test counts, pass criteria, and any changed phase gates.
- The Master Test Plan's §10 Success Criteria table MUST always be consistent with the individual child procedures it references.

**Test outcome rules:**
- Every test in every procedure MUST result in one of three outcomes:
  1. **PASS** — the test executed and produced the expected result.
  2. **FAIL** — the test executed and produced an unexpected result. A FAIL blocks the release gate. The root cause must be investigated and fixed (either in the product code or the test itself).
  3. **Correction** — the test itself was found to be incorrect (wrong expected value, stale endpoint, outdated assertion). When a test is corrected, the corrected procedure MUST be re-executed to verify the correction is valid. A corrected test that has not been re-verified does not count as PASS.
- **CONDITIONAL PASS is not accepted.** Any test that does not cleanly PASS must be either fixed (product or test) and re-run, or documented as a 1.1 deferral with justification.
- **No pre-existing failures are accepted** for the 1.0 GA release gate. Known failing tests must be fixed or removed with justification before the release gate execution begins.

### Release Plan

The **Release Plan** (`docs/operations/release-plan-v1.57.md`) is the governing framework for all current work. It defines an 8-step process from Master Test Plan execution through beta deployment and non-disruptive upgrade.

**Key terminology:**
- **Beta (Prime)** — the production environment serving beta customers. Runs a pinned release image.
- **Staging** — an isolated parallel production environment for validating the next release and proving non-disruptive upgrade.
- All beta feedback fixes are developed on `main` toward v1.58.0.
- Non-disruptive upgrade is proven on Staging before applying to Beta (Prime).

**Branching model:** Tag-and-branch-forward (Model A). No long-lived development branches. `main` always moves forward.

### Repeatable Procedures

Some operational tasks are governed by **Repeatable Procedures** — structured SOPs with pinned variables, verification gates, and known failure modes. The specification is defined in `docs/operations/REPEATABLE-PROCEDURES.md`.

When executing a Repeatable Procedure:
- Follow the steps exactly as written, using the declared variables
- If an error occurs, classify it as a **procedure defect** or **environment transient** (see spec Section 3)
- For procedure defects: fix the procedure document before continuing, not just the immediate issue
- For environment transients: retry, do not modify the procedure

Active procedures:
- `docs/operations/release-plan-v1.57.md` — **Release Plan v1.57.0 Beta** (governing framework, 8 steps)
- `scripts/deploy/upgrade.ps1` — Production deployment
- `scripts/deploy/rollback.ps1` — Production rollback
- `scripts/seed_tenant.py` — Tenant provisioning (single tenant, destructive, superadmin only)
- `scripts/create_test_tenant.py` — Simulated customer tenant creation (test-customer-001, 8 phases, non-destructive)
- `docs/operations/initialization-procedure.md` — Tenant initialization (destructive, 10 post-conditions)
- `docs/operations/upgrade-verification-procedure.md` — Non-disruptive upgrade verification (35 assertions)
- `docs/operations/CATASTROPHIC-RECOVERY-RUNBOOK.md` — Azure environment setup
- `docs/operations/ui-test-procedure.md` — Admin UI regression tests (780 standalone tests, authoritative test definitions)
- `docs/operations/chrome-ui-test-procedure.md` — Chrome MCP-automated UI tests (917 total) + Critical Path CP.1–CP.21
- `docs/operations/external-url-reachability-procedure.md` — URL reachability pre-flight (37 URLs)
- Inline in spec: Unit test suite, Production regression suite
- `docs/operations/agntcy-platform-adoption-procedure.md` — AGNTCY platform adoption verification
- `docs/operations/load-test-procedure.md` — Load testing (50 users, SLA validation, Locust)
- `docs/operations/tenant-isolation-test-procedure.md` — Tenant isolation verification (30 cross-tenant tests)
- `docs/operations/api-security-test-procedure.md` — API security & penetration testing (45 tests)
- `docs/operations/rate-limit-test-procedure.md` — Rate limiting & DoS resilience (20 tests, per-tier enforcement)
- `docs/operations/conversation-quality-test-procedure.md` — Conversation quality regression (25 golden scenarios)
- `docs/operations/resilience-failover-test-procedure.md` — Resilience & failover testing (29 PASS + 6 SKIP)
- `docs/operations/data-integrity-test-procedure.md` — Data integrity & backup verification (25 Cosmos DB tests)

### Adding Commercial Features

1. Create features in `src/` exclusively
2. Document in `docs/architecture/`
3. Add copyright notice to all new files
4. Test integration patterns independently
5. Never commit AGNTCY source code into this repo

### Referencing AGNTCY

- Read the public repository at https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service
- Do **not** reference local AGNTCY files by path — see isolation rules in `CLAUDE-REFERENCE.md`
- Agent Red uses in-process agent delegation (`USE_AGENT_CONTAINERS=false`); 6 extracted agent modules in `src/agents/` delegate to Azure OpenAI directly
- AGNTCY Phase 2 complete (session 25): pipeline decomposed into 6 containerized agent modules with A2A protocol; pipeline orchestrator delegates to agent instances

---

## Completed Roadmap — 14 Cycles + Cycles 15-19

Full plan: `memory/build-deploy-roadmap.md`

### Current Status — v1.56.7 DEPLOYED, Release Plan ACTIVE

Production is v1.56.7 (revision 0000063, session 76b). All 19 cycles deployed. 18/18 T0 PASS. Release Plan (`docs/operations/release-plan-v1.57.md`) is the governing framework — next step: Step 1 (Master Test Plan execution).

| Cycle | Version | Content | Status |
|-------|---------|---------|--------|
| **1-5** | v1.35.0→v1.39.0 | Compliance, refactoring, SLA, MCP, AGNTCY Phase 3 | ✅ DEPLOYED (S38) |
| **6-8** | v1.42.0 | CI + Email + SPA Phase 1 + R10/R3 + Phase 2 backend | ✅ DEPLOYED (S39) |
| **9** | v1.43.0 | SPA Phase 2 + HV-5/RB-4/RB-5 + UI quick wins | ✅ DEPLOYED (S41) |
| **10-14** | v1.48.0 | UI polish, magic link, Provider Phase 3-4, features, coverage, quality | ✅ DEPLOYED (S46) |
| **Post-14** | v1.49.2→v1.54.7 | SKIP resolution, CSS, SDK fix, quality, color mode, KA | ✅ DEPLOYED (S54-S65) |
| **15-19** | v1.55.0 | Customer identity, provisioning persistence, trial scanner, widget key gen, welcome email, trial expiry, wizard fix | ✅ DEPLOYED (S72) |

### Owner/Designer Tasks (blocking Shopify submission)
1. Screenshots (3-6 at 1600x900) — designer
2. Submission screencast — owner
3. Remove storefront password on blanco-9939 — owner
4. Configure pricing in Shopify Partners Dashboard — owner
5. Deploy GDPR webhook URLs — owner
6. Stripe test→live mode flip

### Deferred (Post-Cycle 14)
- Provider Admin Phase 4: NH-1 capacity, NH-2 AIOps, NH-3 BI
- MCP: Customer Account (widget OAuth), Checkout (AGNTCY Phase 4/UCP), GA4, Zendesk/Klaviyo
- Widget phases 3-5, AGNTCY Phase 4 (UCP Commerce Protocol)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-23*
*Version: 57.0.0*
