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
| **Status** | Production v1.58.3. Staging v1.58.1-rc3. Release Plan Step 4 (beta feedback) IN PROGRESS. See `memory/MEMORY.md` for full status. |
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
Next: [describe task].
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

### Protected Behaviors & Removal Rule

**Never remove code, tests, features, or procedure entries without explicit owner approval in the current session.** If something looks wrong, unnecessary, or like a bug — ASK rather than act. The absence of documentation for a behavior means "I don't know its purpose" — not "it has no purpose."

The file `docs/PROTECTED-BEHAVIORS.md` lists behaviors with machine-verifiable assertions. The Build & Deploy procedure's Phase 0 regression gate checks these before every build. When adding a new protected behavior, update both the registry and the regression gate.

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

Active procedures are listed in `docs/operations/REPEATABLE-PROCEDURES.md`. Key procedures: release plan (`release-plan-v1.57.md`), deploy/rollback scripts, seed/test tenant scripts, initialization, upgrade verification (parameterized for staging/production), and 8 test procedures (UI, Chrome MCP, load, isolation, security, rate limit, quality, resilience, data integrity).

### Session Scheduler

The file `.claude/SCHEDULE.md` contains pre-planned prompts that are automatically injected via a `UserPromptSubmit` hook (`.claude/hooks/scheduler.py`). Groups of sequential prompts are processed FIFO — one prompt per user message.

**Trigger types:** `always` (next prompt), `session_end` (wrap-up keywords detected), `after:N` (after N prompts).

**Claude's permissions:** Claude may append new groups to SCHEDULE.md when anticipating future housekeeping needs (e.g., "after this deployment, remind me to update the procedure"). The owner can delete groups to cancel, or reorder groups to change priority.

### Session Wrap-Up & Handoff

At the end of every working session, execute the **Session Wrap-Up Repeatable Procedure** (`docs/operations/session-wrap-up-procedure.md`). This is triggered automatically by the Session Scheduler when wrap-up keywords are detected ("wrap up", "done", "end session", etc.) or can be invoked manually.

**5-phase procedure:** (1) Update Knowledge DB, MEMORY.md, CLAUDE.md → (2) Verify Repeatable Procedures → (3) External updates (docs site, GitHub project/wiki) → (4) Staging deployment (with risk gate) → (5) Generate and store next-session handoff prompt.

**Session handoff prompt:** The final step stores a structured prompt in the Knowledge Database via `db.insert_session_prompt()`. The next session's SessionStart hook automatically retrieves and displays it. This eliminates the need for the owner to craft session-start prompts manually.

**Python API for session prompts:**
```python
db.insert_session_prompt("S97", "Continue work on...", context={...})  # Store
db.get_next_session_prompt()                                            # Retrieve (unconsumed)
db.consume_session_prompt("S97")                                        # Mark as used
```

### Knowledge Database

The **Knowledge Database** (`tools/knowledge-db/knowledge.db`) is the canonical source of truth for all specifications, test procedures, and operational procedures. It replaces the markdown backlog (now FROZEN) with an append-only SQLite store providing change control, version history, and machine-verifiable assertions. Web UI: `localhost:8090` (run `python tools/knowledge-db/app.py`).

**Core principle — append-only:** No rows are ever updated or deleted. Every change creates a new versioned record with `changed_by`, `changed_at`, and `change_reason`. Current state = latest version per ID.

**Claude is the sole writer.** The owner observes through the read-only web UI. When the owner spots a discrepancy, they tell Claude, and Claude creates a corrected version.

**Python API** (always use this — never edit SQLite directly or modify `seed.py` for status changes):

```python
import sys; sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()
db.get_spec("245")                       # Latest version
db.list_specs(status="implemented")      # Filtered list
db.get_summary()                         # Counts by status
db.update_spec("245", changed_by="claude",
               change_reason="Verified in S97",
               status="implemented")
db.close()                               # Always close when done
```

**When to update the database:**

| Trigger | Action |
|---------|--------|
| Implement a specified WI | `update_spec(id, status="implemented", change_reason="...")` |
| Verify an implemented WI passes tests | `update_spec(id, status="verified", change_reason="...")` |
| Discover a wrong status | `update_spec(id, status=corrected, change_reason="...")` |
| Modify a test/operational procedure | Create new version via `insert_test_procedure()` or `insert_op_procedure()` |
| Retire a spec (no longer applicable) | `update_spec(id, status="retired", change_reason="...")` |

**Session-start hook:** `.claude/hooks/assertion-check.py` runs all assertions at session start. Failing specs with status `"specified"` are expected (not yet implemented). Failing specs with status `"implemented"` or `"verified"` indicate **regressions** requiring investigation.

**Do not modify** `docs/BACKLOG-NEW-WORK-ITEMS.md` — it is FROZEN. The Knowledge Database is the canonical source.

### Adding Commercial Features

1. Create features in `src/` exclusively
2. Document in `docs/architecture/`
3. Add copyright notice to all new files
4. Test integration patterns independently
5. Never commit AGNTCY source code into this repo

### Referencing AGNTCY

- Read the public repository at https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service
- Do **not** reference local AGNTCY files by path — see isolation rules in `CLAUDE-REFERENCE.md`
- Agent Red uses in-process agent delegation (`USE_AGENT_CONTAINERS=false`); 7 extracted agent modules in `src/agents/` delegate to Azure OpenAI directly
- AGNTCY Phase 2 complete (session 25): pipeline decomposed into 7 containerized agent modules with A2A protocol; pipeline orchestrator delegates to agent instances

---

## Roadmap & Remaining Tasks

All 19 cycles deployed. Full history: `memory/build-deploy-roadmap.md`.

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
*Last Updated: 2026-02-25*
*Version: 58.2.0*
