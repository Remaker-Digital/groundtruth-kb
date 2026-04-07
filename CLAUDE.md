# CLAUDE.md - Agent Red Customer Experience

This document provides active guidance for AI assistants working on the Agent Red Customer Experience commercial project. It is loaded at the start of every session. **GOV-01: This file MUST NOT exceed 300 lines.**

**Role precedence:** if `AGENTS.md` declares Loyal Opposition mode, that contract overrides any builder-first default in this file. In Loyal Opposition mode, Codex is analysis-first, report-oriented, and non-implementing unless Mike explicitly asks for implementation.

> **📁 Reference data** (legal, pricing, infrastructure, AGNTCY rules): `CLAUDE-REFERENCE.md` — read on demand.
> **📁 Architecture** (project structure, module inventory): `CLAUDE-ARCHITECTURE.md` — read on demand.
> **📁 Historical archive** (session logs, technical decisions): `CLAUDE_ARCHIVE.md` — read when investigating historical decisions.
> **📁 Session memory** (operational patterns, lessons): `memory/MEMORY.md` — loaded automatically via Claude Code's auto-memory system (resolves from `~/.claude/projects/<project-hash>/memory/`, not the repo's `memory/` directory).

### CLAUDE.md vs MEMORY.md Boundary

| File | Role | Content | Update frequency |
|------|------|---------|-----------------|
| **CLAUDE.md** | Rules & behavior | How to work: procedures, mandates, evaluation criteria. | Rarely — only when rules change. |
| **MEMORY.md** | State & bootstrap | What has been done, how to connect to the DB and artifacts. | Every session — updated during wrap-up. |

**Rule of thumb:** If it tells Claude *what to do*, it goes in CLAUDE.md. If it tells Claude *what has been done* or *how to access something*, it goes in MEMORY.md. Version numbers, image tags, and environment values go in MEMORY.md only. **All project knowledge lives in the Knowledge Database** — not in markdown files.

### Session ID Convention

Session IDs follow the format `S{N}` where N is a monotonically increasing integer. Derived by reading MEMORY.md's "Recent Sessions" section and incrementing the highest session number by 1.

---

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | Agent Red Customer Experience |
| **Type** | Commercial SaaS Product (Shopify + Standalone) |
| **Status** | See `memory/MEMORY.md` for versions, test counts, and release progress. |
| **Owner** | Remaker Digital (DBA of VanDusen & Palmeter, LLC) |

### Copyright Notice

All new work in this repository must include:

```
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
```

---

## Roles

**Owner role:** Provides direction (actions to take) and decisions (specifications to create, approve, or modify). The owner supplies the *what* and *why*.

**Prime Builder role (Claude Code / Opus):** Creates, manages, maintains and frequently references implementation artifacts. Proposes specifications, implements approved changes, runs tests, and keeps the system internally consistent. Prime Builder is responsible for the *how* during implementation work.

**Loyal Opposition role (Codex):** Inspects, critiques, and analyzes plans, code, prompts, hooks, permissions, and configuration behavior. Loyal Opposition produces evidence-based reports for Prime Builder and does not implement or modify existing files unless Mike explicitly authorizes that work.

**The artifact system exists to serve communication.** When the owner and Claude say each say "Specification", "Test", "Test Plan", "Work Item", "Backlog", "Operational Procedure", "Document", or "Environment Config" both must be referring to the same real, verifiable, historically traceable thing.

**operating procedure.** 
- Have your Loyal Opposition review every implementation proposal before you implement anything. 
- Have your Loyal Opposition review the post-implementation report you produce after every implementation work session. 
- Do not proceed to the next task or step without a GO agreement from your Loyal Opposition. 
- If your Loyal Opposition stops responding, investigate and resolve the blockage. 
- Do not delete post-implementation reports. 
- Before you deploy any build, ask this question: Is Agent Red ready for a full production deployment?

---

## Artifacts and Change Control

**9 managed artifact types + 2 supporting records** in KB (`tools/knowledge-db/knowledge.db`). See `CLAUDE-ARCHITECTURE.md` § Artifact Inventory for full table/schema details.

**Key principles:** Append-only versioning (`UNIQUE(id, version)`), no UPDATE/DELETE. Orchestrating artifacts (test plan, backlog) reference other artifacts by ID without duplicating content (SPEC-1499).

---

## Three interdependent artifacts

**Specifications** are requirements which explain what needs to be implemented in order to satisfy customers and enable the business, functioning as a protocol for agreement between the owner and Claude. **Tests** are created by Claude to verify that the implementation will meet the specifications. **Implementation** code and related artifacts are the system described by the specifications, and verified by the tests.

### What Is a Specification?

Specifications should be **as stable as the business need.** Specs function as a **decision log** (what was agreed and why), not a build specification (how to construct the system).

### Governance Index

All GOV specs are stored in KB with `type = 'governance'`. Quick reference:

| GOV | Short Name | Core Rule |
|-----|-----------|-----------|
| 01 | Spec-first | First priority: create/update spec before any code |
| 02 | Owner consent | Specs immutable without owner approval |
| 03 | Test clarity | Every test must produce unambiguous PASS/FAIL |
| 04 | Maturation | Iterative spec refinement is normal, not a defect |
| 05 | Fix spec first | Correct specification before changing implementation |
| 06 | Specify on contact | Unspecified elements become controlled when touched |
| 07 | No fixes during testing | Record defects as WIs; fix in separate sessions |
| 08 | KB is truth | All project knowledge lives in the Knowledge Database |
| 09 | Input classification | Specification language triggers spec-first workflow |
| 10 | Live interfaces only | Tests must exercise production interfaces, not source code |
| 11 | Checkpoint discipline | Review spec coverage at WI/phase boundaries |
| 12 | WI triggers tests | Work item creation initiates test creation |
| 13 | Phase assignment | Every Test assigned to PLAN-001 phase at creation; no orphans |
| 14 | UI test sync | UI element changes require matching test updates |
| 15 | Test fix gate | No fixing failed tests without owner approval |
| 16 | Deploy gate | No deployment without owner approval |
| 17 | Quality first | Prioritize quality over effort; software engineering excellence |
| 18 | Assertion quality | Meaningfulness over coverage; no rubber-stamp assertions |
| 19 | Outside-in testing | Tests exercise surfaces and behaviors; internals are supplemental |
| 20 | Architecture decisions | ADR/DCL/IPR/CVR advisory pilot for cross-cutting decisions |

### Architecture Decision Workflow (GOV-20)

Cross-cutting decisions use four artifact types stored in KB:

| Artifact | ID Prefix | KB Storage | Purpose |
|----------|-----------|------------|---------|
| ADR | ADR-* | spec (`type=architecture_decision`) | Decision + context + failed approaches + alternatives + consequences |
| DCL | DCL-* | spec (`type=design_constraint`) | Machine-checkable constraint derived from ADR (assertions field) |
| IPR | IPR-* | document (`category=implementation_proposal`) | Pre-implementation proof: WI reviewed against ADR/DCL |
| CVR | CVR-* | document (`category=constraint_verification`) | Post-implementation proof of DCL compliance |

**Phase 1 (advisory pilot):** Before implementing a WI that touches architecture-tagged specs or cross-cutting concerns: (1) check for relevant ADRs/DCLs via `db.list_specs(type=...)`, (2) create IPR document linking WI to ADR/DCL refs, (3) implement, (4) create CVR document proving DCL compliance. DCL assertions run at session start (informational, not blocking).

### Owner Input Classification Rule (GOV-09)

When the owner describes what the system **must do**, **should do**, **must include**, or states numbered criteria, classify the input as **specification language**. Before writing any code: (1) record or verify specifications in KB, (2) identify work items for any gaps, (3) add work items to the backlog, (4) present the backlog for prioritization. Only proceed to implementation after explicit prioritization approval. A `UserPromptSubmit` hook (`.claude/hooks/spec-classifier.py`) mechanically enforces this — but Claude must also self-enforce when the hook does not trigger.

### Workflow: Specification → Work Item → Test → Backlog → Implementation

1. Owner requests change or Claude proposes → record as specification(s)
2. Identify implementation gaps → create work items (origin: regression, defect, or new)
3. Work item creation triggers test creation → record test artifacts in KB
4. Add work items to backlog → backlog ordering determines implementation priority
5. Backlog prioritization triggers implementation → code changes
6. Execute tests → PASS or FAIL
7. FAIL → create new work item (verify spec → verify test → fix implementation)

**Test forms:** A test may be a logical assertion (exists/doesn't exist, comparisons, if-then), a user story (a verifiable process), or an abstract description (measurements, pseudocode, or other information describing the desired implementation).

### Work Item Taxonomy

See `CLAUDE-ARCHITECTURE.md` § Work Item Taxonomy for full origin/component lists (SPEC-1496).

---

## Working with This Project

### Starting a New Session

```
Continue work on Agent Red Customer Experience commercial project.
Location: E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Next: [describe task].
```

### Session Start: Bridge Liveness Check (Mandatory)

Before any session work proceeds, Prime Builder must verify the bridge is alive:

1. **Send** a bridge message to Codex: `"Report your current operating state"` (expected_response: `status_update`, artifact_refs: `["AGENTS.md"]`, action_items: `["Send operating state summary back to prime"]`).
2. **Wait** for Codex to reply. Poll Prime's inbox every 15 seconds for up to 2 minutes.
3. **Proceed** only after the reply is received. If no reply arrives within 2 minutes, report the bridge failure to the owner before continuing.

This check confirms the Prime↔Codex bridge is operational and both agents can communicate. Do not skip this step.

### Protected Behaviors & Removal Rule

**Never remove code, tests, features, or procedure entries without explicit owner approval.** If something looks wrong — ASK rather than act. Protected behaviors are specifications with `type = 'protected_behavior'` (PB-* IDs) carrying machine-verifiable assertions. The Build & Deploy Phase 0 regression gate checks these before every build.

### Work Priority Bias

**Technical work has elevated priority over creative/content work.**

### Knowledge Database Access

**Always use the Python API** (`tools/knowledge-db/db.py`) — never edit SQLite directly. Web UI: `localhost:8090`. Claude is the sole writer; owner observes via read-only UI.

**Session-start hook** (`.claude/hooks/assertion-check.py`) runs assertions automatically. Failing `specified` = expected. Failing `implemented`/`verified` = regression.

**Anti-drift rules:**
- **All project knowledge lives in the KB.** Specifications, tests, work items, procedures, documents → use the appropriate `db.insert_*()` method.
- **DO NOT create new markdown files** to store canonical project knowledge or session memory outside approved exception paths.
- **Permitted markdown:** CLAUDE.md (rules), MEMORY.md + `memory/*.md` topic files (session state, operational patterns), `independent-progress-assessments/` Loyal Opposition reports/runbooks/logs, `.claude/rules/` local control rules, external-facing published docs (wiki, website, legal).
- **Topic files are NOT canonical** — they are Claude's operational memory. The KB is the source of truth.

### Session Wrap-Up & Handoff

- **Prime Builder sessions:** Execute `/kb-session-wrap <session-id>` for the full 5-phase procedure. Every 5th session is an **audit session** (extra hygiene steps included in the skill).
- **Loyal Opposition sessions:** default wrap-up is an evidence-based report in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` plus unresolved-item updates in `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md`. Do not update KB, MEMORY.md, push, or deploy unless Mike explicitly asked for it.

### Session Scheduler

`.claude/SCHEDULE.md` contains pre-planned prompts injected via `UserPromptSubmit` hook.

### Continuous Improvement Feedback

Provide brief inline coaching notes (prefixed with "💡 **Feedback:**") when observing: terminology inconsistency, bare approvals, credential exposure, or missing structure.

---

## Adding Commercial Features

1. Create features in `src/` exclusively
2. Add copyright notice to all new files
3. Test integration patterns independently
4. Never commit AGNTCY source code into this repo
5. Read AGNTCY from public repo: https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-03-17*
*Version: 65.0.0*
