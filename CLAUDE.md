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
| **Status** | Production v1.32.7 HEALTHY. 2,360 unit tests (0 failures), 172 UI tests (144 PASS, 28 SKIP). AGNTCY Phase 2 pipeline decomposition COMPLETE (session 25). Next: creative assets for Shopify App Store submission. |
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
Current status: Production v1.32.7 HEALTHY. 2,330 unit tests (0 failures). Next: [describe task].
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
- `docs/operations/CATASTROPHIC-RECOVERY-RUNBOOK.md` — Azure environment setup
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

## Remaining Work (Priority Order, as of 2026-02-16)

### AGNTCY Platform Adoption ✅ Phase 2 COMPLETE
- Phase 1 (SDK Adoption): agntcy-app-sdk integrated, BaseAgentProtocol implemented (session 25)
- Phase 2 (Pipeline Decomposition): 6 agents extracted, pipeline rewritten, 100 agent tests, 2,360 total tests (session 25)
- Next: Phase 3 (MCP Client Framework), Phase 4 (UCP Commerce Protocol) — see `docs/operations/agntcy-platform-adoption-procedure.md`

### P0 — Owner Functional Review ✅ COMPLETE
- Full Pages 0-10 UI review: 172 tests, 144 PASS, 28 SKIP (sessions 23-24)
- D46-D52 defects fixed and deployed as v1.32.7

### Owner/Designer Tasks (blocking Shopify submission)
1. Screenshots (3-6 at 1600x900, one showing actual app UI) — designer
2. Submission screencast (install → features → billing → uninstall) — owner
3. Remove storefront password on blanco-9939 — owner
4. Configure pricing in Shopify Partners Dashboard — owner
5. Deploy GDPR webhook URLs (`shopify app deploy`) — owner
6. Stripe test→live mode flip (`config/stripe_product_ids.json` mode field + env keys)

### Known Issues (Non-Blocking, Deferred)
- D16/D20: KB/QA Save→Activate integration (creating article/action doesn't trigger Pending)
- D22: Avatar PNG upload (currently URL-based, 5 test assertions blocked)
- D30: Tier upgrade path on Billing page
- KB table "--" for Category/Status/Freshness on seeded articles

### Post-Launch Backlog
7. Conversation archival (archived_at flag, filter toggle)
8. Email verification identity flow
9. Blocked capabilities C1-C16 (42 UI steps)
10. Widget phases 3-5: mobile controls, targeting rules, localization
11. Code modularization (StandaloneLayout.tsx, Configuration.tsx)
12. Customer context pre-computation (WI #138)
13. Azure OpenAI PTU investigation (WI #139, defer to 50+ tenants)
14. Persistent Memory metrics dashboard
15. Zendesk/Mailchimp/GA4 backend API clients
16. Multi-user admin magic link auth (WI #295, 5-8 days)
17. Add-on checkout Stripe integration (currently shows "coming soon" toast)
18. Crawler/bot conversation protection — User-Agent filtering on conversation creation, `is_crawler` tag + non-billable classification, IP-based rate limiting (5 convos/min/IP/tenant)
19. Category-routed escalation — Manual: admin selects category or specific team member via dialog; AI-initiated: pipeline detects category from keywords. Routing: lookup `escalation_agent` members whose category badges match, assign one, send targeted email. `assigned_to` field on conversation; only assigned member can Resolve. Mapping configured on Team members page (already seeded with category badges).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-16*
*Version: 38.0.0*
