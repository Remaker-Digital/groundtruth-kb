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
| **Status** | Production v1.34.0 HEALTHY. 2,476 unit tests (0 failures), 178 UI tests. AGNTCY Phase 2 COMPLETE. Provider Admin Phase 1 COMPLETE. Config Compliance COMPLETE. P0 Refactoring Cycle 1 COMPLETE. MCP Assessment COMPLETE. Next: 5-cycle roadmap (v1.35.0→v1.39.0). See `memory/build-deploy-roadmap.md`. |
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

## Remaining Work — 5-Cycle Roadmap (Owner-Approved, Session 32)

Full plan: `memory/build-deploy-roadmap.md`

### Cycle 1: v1.35.0 — Ship S30-31 Work (1 day, LOW risk)
- Deploy existing compliance + P0 refactoring (R1/R7/R8/R9a). No new development.

### Cycle 2: v1.36.0 — P1 Refactoring (4-5 days, MEDIUM risk)
- **R2:** Repository file split — `repository.py` → `src/multi_tenant/repositories/` (10 domain files + re-export)
- **R4:** Config processor decomposition — `tenant_config_processor.py` → `src/multi_tenant/config/` (6 files). **Fix latent bug line 1197.**
- **R6 partial:** Hooks barrel split — `hooks/index.ts` → 6 domain files + re-export barrel

### Cycle 3: v1.37.0 — Provider Admin Phase 2 Start (4-6 days, MEDIUM risk)
- **C-2:** SLA persistence — new Cosmos collection, hourly snapshots, startup hydration, error budget, trends API
- **C-1:** Queue depth + job health (if time permits)

### Cycle 4: v1.38.0 — AGNTCY Phase 3A: MCP Client + Shopify Storefront MVP (2-3 weeks, MEDIUM-HIGH risk)
- MCP client implementation with HTTP transport (relax assertion 3.4 for external servers)
- Tenant MCP server registry in Cosmos DB PreferencesDocument
- KR agent MCP integration (secondary source: KB → MCP → keyword fallback)
- Read-only policy gate, shop_domain guard, credential cache, circuit breaker, PII tokenization
- **Assessment:** `independent-progress-assments/MCP-SERVER-INTEGRATION-ASSESSMENT-2026-02-17.md`
- **Architecture:** `memory/mcp-integration.md`

### Cycle 5: v1.39.0 — AGNTCY Phase 3B: Stripe MCP + Mutation Safety + Admin UI (2-3 weeks, MEDIUM-HIGH risk)
- Stripe MCP (remote `mcp.stripe.com`, per-tenant restricted keys, read-only initially)
- Mutation safety architecture (MutationPolicy, Critic-gated confirmation, idempotency keys)
- Admin UI for MCP configuration (Integrations page)
- **Milestone: AGNTCY Phase 3 COMPLETE** — all 14 assertions verified

### Completed Milestones
- ✅ P0 Refactoring Cycle 1 (Session 31): R1 main.py split, R9a sourcemaps, R7 env loader, R8 CamelCaseModel
- ✅ Configuration Strategy Compliance (Session 30): 25 files, 4 priority levels
- ✅ Provider Admin Phase 1 (Session 29): 5 superadmin endpoints, 20 tests
- ✅ AGNTCY Phase 2 (Session 25): 6 agents, pipeline decomposition, 100 agent tests
- ✅ Owner Functional Review (Sessions 23-26): 178 UI tests, D46-D67 fixed, v1.34.0 deployed
- ✅ MCP Assessment (Session 32): Independent cross-reference, 6 findings, revised sequencing

### Deferred (Post-Cycle 5)
- **Provider Admin Phase 2 remaining:** C-3 compliance, C-4 secret posture, HV-3 integration reliability, HV-5 status page, RB-5 MFA, RB-4 alerting
- **Provider Admin Phase 3-4:** Support diagnostics, cost economics, abuse detection, capacity, AIOps, BI
- **MCP post-Phase 3:** Customer Account MCP (widget OAuth UX), Checkout MCP (AGNTCY Phase 4 / UCP), GA4 MCP (experimental), Zendesk/Klaviyo (no official servers)
- **Refactoring:** R3 config YAML, R6 full component slices, R9b CDN split, R10 pipeline.py → Phase 3/4

### Owner/Designer Tasks (blocking Shopify submission)
1. Screenshots (3-6 at 1600x900) — designer
2. Submission screencast — owner
3. Remove storefront password on blanco-9939 — owner
4. Configure pricing in Shopify Partners Dashboard — owner
5. Deploy GDPR webhook URLs — owner
6. Stripe test→live mode flip

### Post-Launch Backlog
- Email verification, blocked capabilities C1-C16 (42 UI steps)
- Widget phases 3-5, multi-user admin auth (WI #295, 5-8 days)
- Add-on Stripe checkout, customer context pre-computation (WI #138)
- Azure OpenAI PTU (WI #139), Persistent Memory dashboard
- D22 avatar PNG upload, D30 tier upgrade path
- AGNTCY Phase 4 (UCP Commerce Protocol)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-17*
*Version: 44.0.0*
