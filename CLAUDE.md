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
| **Status** | Production v1.35.0 HEALTHY. Cycle 5 IMPLEMENTED (AGNTCY Phase 3 COMPLETE — 14/14 assertions). 2,646 unit tests (0 failures), 178 UI tests. Commit pending for v1.39.0. See `memory/build-deploy-roadmap.md`. |
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
Current status: Production v1.34.0 HEALTHY. 2,497 unit tests (0 failures). Next: [describe task].
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

### Repeatable Procedures

Some operational tasks are governed by **Repeatable Procedures** — structured SOPs with pinned variables, verification gates, and known failure modes. The specification is defined in `docs/operations/REPEATABLE-PROCEDURES.md`.

When executing a Repeatable Procedure:
- Follow the steps exactly as written, using the declared variables
- If an error occurs, classify it as a **procedure defect** or **environment transient** (see spec Section 3)
- For procedure defects: fix the procedure document before continuing, not just the immediate issue
- For environment transients: retry, do not modify the procedure

Active procedures:
- `scripts/deploy/upgrade.ps1` — Production deployment
- `scripts/deploy/rollback.ps1` — Production rollback
- `scripts/seed_tenant.py` — Tenant provisioning
- `docs/operations/initialization-procedure.md` — Tenant initialization (destructive, 10 post-conditions)
- `docs/operations/upgrade-verification-procedure.md` — Non-disruptive upgrade verification
- `docs/operations/CATASTROPHIC-RECOVERY-RUNBOOK.md` — Azure environment setup
- `docs/operations/ui-test-procedure.md` — Admin UI regression tests (178 tests)
- Inline in spec: Unit test suite, Production regression suite
- `docs/operations/agntcy-platform-adoption-procedure.md` — AGNTCY platform adoption verification

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

## Remaining Work — 14-Cycle Roadmap (Re-scoped Session 41)

Full plan: `memory/build-deploy-roadmap.md`

### Active Cycle

**Cycle 9: v1.43.0** — SPA Phase 2 + HV-5/RB-4/RB-5 + UI Quick Wins (IMPLEMENTING S40-41)
- S40: 4 SPA pages, grouped nav, incidents/status, alerting, MFA/TOTP (125+ tests)
- S41: Shopify route fix, theme extraction, emoji→SVG icons

### Planned Cycles

| Cycle | Version | Content | Risk |
|-------|---------|---------|------|
| **10** | v1.44.0 | UI consistency, empty states, a11y, loading states, login migration, tooltips, design docs | LOW-MEDIUM |
| **11** | v1.45.0 | R6 component slices + magic link auth + C1/C8/C9 | MEDIUM |
| **12** | v1.46.0 | Provider Phase 3-4 (HV-1/HV-2/HV-4) + R9b CDN | MEDIUM |
| **13** | v1.47.0 | C5/C10/C14/C15/C3 + D22/D30 + WI#138/WI#139 | MEDIUM |
| **14** | v1.48.0 | Coverage 80%, regression, perf validation, launch | LOW |

### Completed Milestones
- ✅ **Cycles 6-8** (Session 39): CI + Email + SPA Phase 1 + R10/R3 + Phase 2 backend → v1.42.0
- ✅ **Cycle 5 Phase 3B** (Session 37): Stripe MCP + mutation safety + Admin UI → AGNTCY Phase 3 14/14 PASS
- ✅ **Cycles 1-4** (Sessions 33-36): Compliance, refactoring, SLA, MCP client → v1.39.0
- ✅ Pre-cycle work (Sessions 25-31): AGNTCY Phase 2, UI review, Provider Phase 1, config compliance, P0 refactoring

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
*Last Updated: 2026-02-18*
*Version: 46.0.0*
