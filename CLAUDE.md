# CLAUDE.md - Agent Red Customer Experience

This document provides active guidance for AI assistants working on the Agent Red Customer Experience commercial project. It is loaded at the start of every session. **GOV-01: This file MUST NOT exceed 300 lines.**

> **📁 Reference data** (legal, pricing, infrastructure, AGNTCY rules): `CLAUDE-REFERENCE.md` — read on demand.
> **📁 Architecture** (project structure, module inventory): `CLAUDE-ARCHITECTURE.md` — read on demand.
> **📁 Historical archive** (session logs, technical decisions): `CLAUDE_ARCHIVE.md` — read when investigating historical decisions.
> **📁 Session memory** (operational patterns, lessons): `memory/MEMORY.md` — loaded automatically.

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

**Claude role:** Creates, manages, and maintains all artifacts. Proposes specifications, implements changes, runs tests, and keeps the system internally consistent. Claude is responsible for the *how* — and for ensuring that the artifact system faithfully represents the shared understanding at all times.

**The artifact system exists to serve communication.** When the owner says "backlog" and Claude says "backlog," both must be referring to the same real, verifiable, historically traceable thing.

**Standard:** If Claude references something, it must exist. If it exists, it must be under change control. If it's under change control, its history must be retrievable.

---

## Artifacts and Change Control

The project maintains exactly **8 managed artifact types** and **2 supporting record types**, all stored in the Knowledge Database (`tools/knowledge-db/knowledge.db`). No phantom artifacts are permitted — every entity referenced as "managed" must correspond to a real, versioned, queryable database record.

### Artifact Inventory (SPEC-1493)

| # | Artifact | Table | Purpose |
|---|----------|-------|---------|
| 1 | **Specification** | `specifications` | Testable description of system behavior or content |
| 2 | **Test** | `tests` | Individual testable assertion derived from a specification |
| 3 | **Test Plan** | `test_plans` + `test_plan_phases` | Ordered test phases with gate criteria |
| 4 | **Work Item** | `work_items` | Unit of work: regression, defect, or new capability |
| 5 | **Backlog** | `backlog_snapshots` | Point-in-time snapshot of active work items |
| 6 | **Operational Procedure** | `operational_procedures` | Step-by-step repeatable process |
| 7 | **Document** | `documents` | General-purpose project knowledge |
| 8 | **Environment Config** | `environment_config` | Environment-specific values under change control |

Supporting records: **Assertion Runs** (`assertion_runs`) and **Session Prompts** (`session_prompts`).

### Orchestrating Artifact Principle (SPEC-1499)

An orchestrating artifact (test plan, backlog) contains ordering, criteria, and execution context. It references other artifacts by ID without duplicating their content. Each referenced artifact is independently managed and versioned.

### Append-Only Change Control

All artifact tables use append-only versioning: `UNIQUE(id, version)`. Every mutation creates a new version row with mandatory `changed_by`, `changed_at`, `change_reason`. No UPDATE in place, no DELETE. `current_*` views surface the latest version per ID.

---

## Specification Discipline

Specifications are the protocol for recording agreement between owner and Claude. The owner does not read code or write tests; Claude does not set business requirements. The specification is the mutual understanding.

### What Is a Specification?

A specification is a **requirement** — a business decision that affects customers or the business.

**The litmus test:** "Would a different choice affect the customer or the business?" If yes, it's a specification. If no, it's an implementation detail.

Specifications should be **as stable as the business need.** Specs function as a **decision log** (what was agreed and why), not a build specification (how to construct the system).

### Governance Principles (GOV-01 through GOV-13 in KB)

1. **Specs are the negotiation artifact.** Claude's first priority on any change request is creating/updating a specification.
2. **Specs are immutable without owner consent.** Claude proposes; the owner decides.
3. **Spec granularity is driven by test unambiguity.** Every test must produce an unambiguous PASS/FAIL.
4. **Specs mature through use.** Iterative refinement is normal maturation, not a defect.
5. **Fix the spec first, not the code.** Correct the specification before changing implementation.
6. **Specify on contact.** Unspecified elements become controlled when touched.
7. **No bug fixes during testing.** Record defects as work items; fix in separate sessions.
8. **Knowledge Database is the single source of truth.** All project knowledge lives in the KB.
9. **Owner input classification.** Specification language triggers spec-first workflow (GOV-09, below).
10. **Tests must exercise exposed production interfaces.** Source inspection tests are regression supplements, not Test artifacts. Each Test must produce PASS/FAIL against observable outcomes on live/staging systems. Tests are written and linked to specs **before** implementation (GOV-10).
11. **Design decision checkpoint discipline.** At each WI/phase completion boundary, Claude must review implementation decisions for spec coverage before proceeding. Batched checkpoint, not real-time pause (GOV-11).
12. **Work item creation triggers test creation.** Creating a work item initiates test creation; the backlog initiates implementation. Tests may be logical assertions, user story descriptions, or abstract descriptions (GOV-12).
13. **Test plan phase assignment upon creation.** Every Test artifact must be assigned to at least one test plan phase (PLAN-001) at creation time. The Master Test Plan must cover every Test artifact — no orphan tests. This closes the hierarchy: specs produce tests (GOV-12), tests must be in procedures (GOV-13), all procedures compose the Master Test Plan (GOV-13).

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

### Work Item Taxonomy (SPEC-1496)

**By origin:** Regression (previously PASSing test now FAILs), Defect (test FAILs against implementation), New (specification exists but no implementation yet), Hygiene (process improvement, tooling, drift reduction — improves the project management system, not the product).

**By component:** test_plan, test_procedure, operational_procedure, tenant_administration, provider_administration, agent_implementation, infrastructure_automation, database, test_harness, maintenance_tool, customer_interface, external_integration, development_environment.

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

For planning, prioritization, and multi-step decision-making, use an **iterative review process**: present one item at a time, pause for owner input, incorporate feedback, adjust subsequent items. Do not batch multiple decisions.

### Option Evaluation Criteria

Prioritize: (1) Implementation quality, (2) Desirability, (3) Downstream confidence. **Avoid vague generalizations** — state specifically what is gained or lost.

### Protected Behaviors & Removal Rule

**Never remove code, tests, features, or procedure entries without explicit owner approval.** If something looks wrong — ASK rather than act. Protected behaviors are specifications with `type = 'protected_behavior'` (PB-* IDs) carrying machine-verifiable assertions. The Build & Deploy Phase 0 regression gate checks these before every build.

### Work Priority Bias

**Technical work has elevated priority over creative/content work.**

### Knowledge Database Access

**Always use the Python API** (`tools/knowledge-db/db.py`) — never edit SQLite directly. Web UI: `localhost:8090`. Claude is the sole writer; owner observes via read-only UI.

**Session-start hook** (`.claude/hooks/assertion-check.py`) runs assertions automatically. Failing `specified` = expected. Failing `implemented`/`verified` = regression.

**Anti-drift rules:**
- **All project knowledge lives in the KB.** Specifications, tests, work items, procedures, documents → use the appropriate `db.insert_*()` method.
- **DO NOT create new markdown files** to store project knowledge. Ask: "Should this be a KB record instead?" The answer is almost always yes.
- **Permitted markdown:** CLAUDE.md (rules), MEMORY.md + `memory/*.md` topic files (session state, operational patterns), external-facing published docs (wiki, website, legal).
- **Topic files are NOT canonical** — they are Claude's operational memory. The KB is the source of truth.

### Session Wrap-Up & Handoff

Session wrap-up procedure (stored in KB as operational procedure): (1) Update KB/MEMORY/CLAUDE → (2) Verify procedures → (3) External updates → (4) Staging deploy (risk gate) → (5) Generate handoff prompt via `db.insert_session_prompt()`. Every 5th session is an **audit session**.

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
*Last Updated: 2026-02-28*
*Version: 62.0.0*
