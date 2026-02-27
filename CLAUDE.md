# CLAUDE.md - Agent Red Customer Experience

This document provides active guidance for AI assistants working on the Agent Red Customer Experience commercial project. It is loaded at the start of every session. **GOV-01: This file MUST NOT exceed 300 lines.** Move detail to topic files when approaching the limit.

> **📁 Reference data** (legal, pricing, infrastructure, AGNTCY rules): `CLAUDE-REFERENCE.md` — read on demand.
> **📁 Architecture** (project structure, module inventory): `CLAUDE-ARCHITECTURE.md` — read on demand.
> **📁 Historical archive** (session logs, technical decisions): `CLAUDE_ARCHIVE.md` — read when investigating historical decisions.
> **📁 Session memory** (operational patterns, lessons): `~/.claude/projects/.../memory/MEMORY.md` — loaded automatically.

### CLAUDE.md vs MEMORY.md Boundary

| File | Role | Content | Update frequency |
|------|------|---------|-----------------|
| **CLAUDE.md** | Rules & architecture | How to work with this project: procedures, patterns, evaluation criteria, protected behaviors. | Rarely — only when rules or architecture change. |
| **MEMORY.md** | State & history | What has happened: current versions, test counts, recent sessions, quick reference values, topic file index. | Every session — updated during wrap-up. |

**Rule of thumb:** If it tells Claude *what to do*, it goes in CLAUDE.md. If it tells Claude *what has been done*, it goes in MEMORY.md. Version numbers, image tags, and environment values go in MEMORY.md only. **Project knowledge** (specifications, procedures, decisions, domain knowledge) goes in the **Knowledge Database** — not in markdown files.

### Session ID Convention

Session IDs follow the format `S{N}` where N is a monotonically increasing integer. The current session ID is derived by reading MEMORY.md's "Recent Sessions" section and incrementing the highest session number by 1. For example, if the most recent entry is "S97:", the current session is S98.

---

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | Agent Red Customer Experience |
| **Type** | Commercial SaaS Product (Shopify + Standalone) |
| **Status** | See `memory/MEMORY.md` "Current Status" for versions, test counts, and release progress. |
| **Owner** | Remaker Digital (DBA of VanDusen & Palmeter, LLC) |

### Copyright Notice

All new work in this repository must include:

```
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
```

---

## Specification Discipline

Specifications are the protocol for recording agreement between owner and Claude about what is being implemented. They are the shared artifact — the owner does not read code or write tests; Claude does not set business requirements. The specification is the mutual understanding. See `memory/specification-discipline.md` for history, examples, and phase progress.

### What Is a Specification?

A specification is a **requirement** — a business decision that affects customers or the business. The terms are interchangeable.

**The litmus test:** "Would a different choice affect the customer or the business?" If yes, it's a specification. If no, it's an implementation detail.

| IS a specification | NOT a specification |
|---|---|
| Intent taxonomy, tier pricing, conversation handling rules, privacy commitments, UI field inventory, integration choices (Shopify, MCP), quality criteria | Database schema, middleware ordering, startup sequence, API response shapes, env vars, internal module structure |

Specifications should be **as stable as the business need.** Leave maximum room for implementation variation — the implementation may change, but the specification should remain stable. Specs function as a **decision log** (what was agreed and why), not a **build specification** (how to construct the system).

### Principles (GOV-01 through GOV-08 in Knowledge DB)

1. **Specs are the negotiation artifact.** When the owner requests a change or identifies a flaw, Claude's first priority is creating/updating a specification. Testing and implementation proceed only after mutual understanding is established.

2. **Specs are immutable without owner consent.** Once recorded, a spec cannot be changed, retired, or contradicted without owner approval. Claude proposes; the owner decides.

3. **Spec granularity is driven by test unambiguity.** Specs are as detailed as business goals require — some broad, some granular. The binding constraint: every test derived from a spec MUST produce an unambiguous PASS/FAIL. If tests would be ambiguous, refine the spec.

4. **Specs mature through use.** Initial specs represent the best understanding at the time. When owner testing reveals a gap, the spec is refined — add specificity, remove ambiguity. This iterative refinement is normal maturation, not a defect.

5. **Fix the spec first, not the code.** When testing reveals an error, correct the specification first. Revised specs produce revised tests that automatically flag incorrect implementation. Jumping to a code fix without updating the spec leaves ambiguity in place.

6. **Specify on contact.** Pre-existing unspecified elements are *uncontrolled*, not defects. They become *controlled* when touched — via owner feedback, re-testing, or modification. New work (S106+) requires spec-first always.

7. **No bug fixes during testing.** When a defect is discovered during testing or spec-maturation, do NOT fix it. Review the spec and test, then record the defect as a backlog work item in the Knowledge DB. Bug fixes occur in separate implementation sessions following spec-first workflow. The backlog is the bridge between discovery and correction.

8. **Knowledge Database is the single source of truth.** All specifications, procedures, backlog items, and project knowledge live in the Knowledge DB. The only markdown files are CLAUDE.md (rules) and MEMORY.md (state/history). No operational artifacts in standalone markdown — the DB provides change history, versioning, and queryability that files cannot.

### Workflow

**When making any change:** update the specification first, then the implementation, then verify the test passes. For complex changes, this expands to: extract specs → record in KB → check contradictions → derive tests → implement → verify.

### Specification Forms

Specs are form-agnostic. Valid forms: external standard reference, user story, textual description, image reference, metric. The only requirement: unambiguous enough to test and implement.

### Change Control

- Created via `db.insert_spec()` / `db.update_spec()` with `changed_by` and `change_reason`
- Status: `specified` → `implemented` → `verified` (or `retired` with owner approval)
- Append-only versioning — every change creates a new record
- Deduplication resolves at test time, not during extraction

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

Provide brief inline coaching notes (prefixed with "💡 **Feedback:**") when observing: terminology inconsistency, bare approvals that could carry steering, credential exposure, or missing structure. Skip when the message is already clear.

### Work Priority Bias

**Technical work has elevated priority over creative/content work.** Technical implementation, test case creation, testing/results analysis, and new capabilities are prioritized above creative assets, marketing, and cosmetic work.

### Master Test Plan

The **Master Test Plan** (`docs/MASTER-TEST-PLAN-1.0.md`) defines the 15-phase ordered test sequence for the 1.0 GA release. All phases must pass for the release gate to clear. When test procedures are created or updated, the Master Test Plan MUST be updated to match. Test outcomes: PASS, FAIL (blocks release), or Correction (re-execute to verify). No CONDITIONAL PASS accepted.

### Release Plan

The **Release Plan** (`docs/operations/release-plan-v1.57.md`) governs the 8-step process from test execution through beta deployment. **Beta (Prime)** = production for beta customers. **Staging** = parallel environment for upgrade validation. Branching: tag-and-branch-forward, `main` always moves forward.

### Repeatable Procedures

Structured SOPs with pinned variables and verification gates (`docs/operations/REPEATABLE-PROCEDURES.md`). Follow steps exactly. Errors: classify as **procedure defect** (fix the doc) or **environment transient** (retry). Key procedures: release plan, deploy/rollback, seed/test tenant, initialization, upgrade verification, and 8 test procedures.

### Session Scheduler

`.claude/SCHEDULE.md` contains pre-planned prompts injected via `UserPromptSubmit` hook. Triggers: `always`, `session_end`, `after:N`. Claude may append new groups; owner can delete/reorder.

### Session Wrap-Up & Handoff

Execute the **Session Wrap-Up Repeatable Procedure** (`docs/operations/session-wrap-up-procedure.md`) at end of session — triggered automatically by Session Scheduler on wrap-up keywords or invoked manually. 5-phase: (1) Update KB/MEMORY/CLAUDE → (2) Verify procedures → (3) External updates → (4) Staging deploy (risk gate) → (5) Generate handoff prompt.

Handoff prompts are stored via `db.insert_session_prompt()` and auto-retrieved at next session start. Every 5th session is an **audit session** (KB integrity, doc accuracy, design debt review).

### Knowledge Database

The **Knowledge Database** (`tools/knowledge-db/knowledge.db`) is the canonical source of truth for all specifications, test procedures, and operational procedures. Append-only SQLite with change control and version history. Web UI: `localhost:8090`. Claude is the sole writer; owner observes via read-only UI.

**Always use the Python API** — never edit SQLite directly. Key operations: `db.insert_spec()`, `db.update_spec()`, `db.get_spec()`, `db.list_specs()`, `db.get_summary()`, `db.export_json()`. Status flow: `specified` → `implemented` → `verified` (or `retired`).

**Session-start hook** (`.claude/hooks/assertion-check.py`) runs assertions automatically. Failing `specified` = expected. Failing `implemented`/`verified` = regression.

**Knowledge boundary — anti-drift rules:**
- **All project knowledge lives in the KB.** Specifications, procedures, backlog items, decisions, and domain knowledge → `db.insert_spec()`, `db.insert_document()`, or `db.insert_procedure()`.
- **DO NOT create new markdown files** to store project knowledge. When tempted to create a `.md` file, ask: "Should this be a KB document instead?" The answer is almost always yes.
- **Permitted markdown exceptions:** CLAUDE.md (bootstrap rules), MEMORY.md + `memory/*.md` topic files (session state, operational patterns for cross-session continuity), external-facing published docs (wiki, website, legal, branding).
- **Topic files are NOT canonical** for specifications or procedures — they are Claude's operational memory for patterns and lessons. The KB is the source of truth.

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
*Last Updated: 2026-02-26*
*Version: 60.3.0*
