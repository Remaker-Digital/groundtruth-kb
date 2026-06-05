# CLAUDE.md — GroundTruth-KB Platform

This document provides active guidance for AI assistants working on the GroundTruth-KB (GT-KB) platform. **Unless Mike explicitly says the session is application work (e.g., Agent Red), assume active work is GroundTruth-KB.** **GOV-01: This file MUST NOT exceed 300 lines.**

For application-scope guidance (Application Identity, Copyright, Adding Commercial Features, Branching Strategy, Hotfix Workflow), see [`applications/Agent_Red/CLAUDE.md`](applications/Agent_Red/CLAUDE.md). Application-scope files are consulted only when the active work subject is `application` and the named application is Agent Red.

**Role precedence:** active role is resolved at session start from `harness-state/harness-identities.json` (persistent harness identity) and `harness-state/harness-registry.json` (canonical role registry), read through `groundtruth_kb.harness_projection.read_roles` or `gt harness role`. `.claude/rules/operating-role.md`, `AGENTS.md`, and `.claude/rules/*.md` files are explanatory guidance only — they describe behavior contracts but cannot override the durable role assignment map. If markdown text and the durable map differ, the durable map wins; surface the divergence as a defect rather than acting on the markdown. Interactive sessions MAY override the durable role for in-session surfaces (SessionStart disclosure, AXIS 2 Claude-native surface, focus menu, MemBase attribution, AUQ routing) by typing the canonical init keyword `::init gtkb (pb|lo)` on an owner prompt; the override lives in the ephemeral `.claude/session/active-session-role.json` marker for the rest of the session and is invalidated by the next SessionStart. Headless dispatch routing remains keyed to the durable role per `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001`.

> **📁 Application-scope reference** (Agent Red legal, pricing, infrastructure, AGNTCY rules): [`applications/Agent_Red/CLAUDE-REFERENCE.md`](applications/Agent_Red/CLAUDE-REFERENCE.md) — read on demand when working on Agent Red.
> **📁 Application-scope architecture** (Agent Red project structure, module inventory): [`applications/Agent_Red/CLAUDE-ARCHITECTURE.md`](applications/Agent_Red/CLAUDE-ARCHITECTURE.md) — read on demand.
> **📁 Application-scope historical archive** (Agent Red session logs, technical decisions): [`applications/Agent_Red/CLAUDE_ARCHIVE.md`](applications/Agent_Red/CLAUDE_ARCHIVE.md) — read when investigating Agent Red historical decisions.
> **📁 Platform session memory** (operational patterns, lessons): `memory/MEMORY.md` — active GT-KB memory must resolve inside `E:\GT-KB`, not a home-directory mirror or legacy project path.

### Canonical Terminology

Load `.claude/rules/canonical-terminology.md` at session start; the operating-model glossary in `.claude/rules/operating-model.md` §2 is the rule-cited soft-authority baseline for `application`, `project`, `platform`, `hosted application`, `work item`, `backlog`, `specification`, `requirement`, `implementation proposal`, `implementation report`, `verification`, `release`, `MemBase`, `Deliberation Archive`, and `dashboard`. **Adopter:** an application that consumes GT-KB (like Agent Red Customer Experience). **AI coding harness:** a concrete AI-assisted development environment (e.g., Claude Code, Codex CLI); roles attach to harnesses by owner assignment, not by vendor.

### Mandatory Project Root Boundary

All active files for the GT-KB project MUST be within `E:\GT-KB`. No GT-KB
artifact may be created, read as a live dependency, updated, verified, or
required from outside that root. GT-KB application files MUST be within
`E:\GT-KB\applications\`; Agent Red application files MUST be within
`E:\GT-KB\applications\Agent_Red\`. There are no exceptions.
`E:\Claude-Playground` is an archive only and must not be used as a live
GT-KB, Agent Red, harness-state, bridge, dashboard, memory, source,
verification, or dependency location.

Apply `.claude/rules/project-root-boundary.md` to all GT-KB work, all
implementation proposals, all Codex reviews, all tests, all dashboard
generation, all harness configuration, and all applications developed or
managed by GT-KB.

### CLAUDE.md vs MEMORY.md Boundary

CLAUDE.md = rules & behavior (how to work: procedures, mandates; updated rarely). MEMORY.md = state & bootstrap (what has been done, how to access artifacts; updated every session). **All project knowledge lives in MemBase** (`groundtruth.db` per `.claude/rules/operating-model.md` §2) — not markdown files. Version numbers, image tags, and environment values go in MEMORY.md only. Future-work proposals, enhancement candidates, and backlog items go to MemBase `work_items`, not MEMORY.md.

### Session ID Convention

`S{N}` format; N is a monotonically increasing integer derived by reading MEMORY.md's "Recent Sessions" section.

---

## Roles

**Owner role:** Provides direction (actions to take) and decisions (specifications to create, approve, or modify). The owner supplies the *what* and *why*.

**Prime Builder role (Claude Code / Opus):** Creates, manages, maintains and frequently references implementation artifacts. Proposes specifications, implements approved changes, runs tests, and keeps the system internally consistent. Prime Builder is responsible for the *how* during implementation work.

**Loyal Opposition role (Codex):** Inspects, critiques, and analyzes plans, code, prompts, hooks, permissions, and configuration behavior. Loyal Opposition produces evidence-based reports for Prime Builder and does not implement or modify existing files unless Mike explicitly authorizes that work.

**GroundTruth KB vision filter:** For GroundTruth-related work, prefer choices that reduce the owner's role to adding or refining specifications, answering clarification questions, and making explicit trade-off decisions. Flag approaches that leave routine implementation, deployment plumbing, traceability reconciliation, generated-artifact inspection, or cross-agent process state with the owner.

**Strategic self-improvement directive:** Self-improvement is a GT-KB strategic imperative. When Prime Builder or Loyal Opposition notices a fix-worthy issue or useful workflow enhancement that would improve future work, add it to the MemBase standing backlog/work items for review and future consideration unless it is already tracked. Do not park future work in MEMORY.md or harness-local auto-memory. Backlog capture is not implementation approval; implementation-approved backlog items require explicit owner/governance approval and AskUserQuestion evidence when owner approval is required.

**The artifact system exists to serve communication.** When the owner and Claude say each say "Specification", "Test", "Test Plan", "Work Item", "Backlog", "Operational Procedure", "Document", or "Environment Config" both must be referring to the same real, verifiable, historically traceable thing.

**Operating procedure.** File-based bridge protocol. See `.claude/rules/file-bridge-protocol.md` and `.claude/rules/bridge-essential.md` §"Operational Mode".

- **DO NOT implement anything without first preparing an implementation proposal and having it reviewed by Codex.**
- **All implementation proposals MUST be reviewed by Codex before any code is written.**
- **All post-implementation reports MUST be reviewed by Codex before committing.**
- **Propose:** Save proposal to `bridge/{name}-001.md`, add NEW entry to `bridge/INDEX.md`.
- **Review:** Codex scans INDEX for NEW/REVISED entries, reviews, adds GO or NO-GO version.
- **Execute:** After Codex GO, implement code, tests, and verify.
- **Report:** Save post-implementation report as new version, add NEW entry for verification.
- **Verify:** Codex reviews report and adds VERIFIED or NO-GO version.
- **Dispatch:** Bridge dispatch automation is the **cross-harness event-driven trigger** at `scripts/cross_harness_bridge_trigger.py`, registered as PostToolUse and Stop hooks in `.claude/settings.json` and `.codex/hooks.json`. The trigger fires on tool-use and Stop events. It dispatches Codex on latest `NEW` or `REVISED` (Loyal-Opposition-actionable) and Prime on latest `GO` or `NO-GO` (Prime-Builder-actionable). `VERIFIED` is terminal and not dispatched. The retired OS pollers and the retired smart poller are archived; do not re-enable without owner approval per `.claude/rules/bridge-essential.md` §"Re-Enabling Pollers".
- **Manual scan is fallback** when the trigger is unhealthy or intentionally stopped: the owner triggers a bridge scan with a brief prompt such as `Bridge` or `Bridge scan`; agents then read `bridge/INDEX.md` and act on role-appropriate actionable entries.

---

## Artifacts and Change Control

**9 managed artifact types + 2 supporting records** in KB (`groundtruth.db`). See application-side architecture documentation (when active) for application-specific schema details; for platform-side artifact authority, see `.claude/rules/operating-model.md`.

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

For application-specific origin/component taxonomy, see application-side architecture documentation when active (SPEC-1496).

---

## Working with This Project

### Starting a New Session

```
Continue work on GroundTruth-KB platform.
Location: E:\GT-KB
Key files: CLAUDE.md, memory/MEMORY.md
Next: [describe task].
```

**Canonical startup load order:** `config/agent-control/SESSION-STARTUP-INDEX.md` is the compact role-neutral statement of what loads at startup and in what order; load the role overlay (`PRIME-BUILDER-STARTUP-OVERLAY.md` or `LOYAL-OPPOSITION-STARTUP-OVERLAY.md`) and consult `SESSION-STARTUP-CONTROL-MAP.md` for the classified surface inventory. The condensed session-start guidance below defers to that index for the full step-by-step.

### Session Start (Mandatory)

Scan live `bridge/INDEX.md` (role-filtered — Prime Builder acts on latest `GO`/`NO-GO`; Loyal Opposition on latest `NEW`/`REVISED`), then review the active MemBase backlog (`gt backlog list`). Full step-by-step and role-specific bridge handling: `config/agent-control/SESSION-STARTUP-INDEX.md` + the role overlays. The cross-harness event-driven trigger (PostToolUse + Stop hooks per `.claude/rules/bridge-essential.md`) handles inter-session dispatch. Implementable backlog items follow the standard bridge protocol (propose → GO → implement → report → VERIFIED → commit); items already authorized (project authorization or recorded owner decision) need no fresh approval.

### Protected Behaviors & Removal Rule

**Never remove code, tests, features, or procedure entries without explicit owner approval.** If something looks wrong — ASK rather than act. Protected behaviors are specifications with `type = 'protected_behavior'` (PB-* IDs) carrying machine-verifiable assertions.

### Work Priority Bias

**Technical work has elevated priority over creative/content work.**

### Knowledge Database Access

**Always use the Python API** (`tools/knowledge-db/db.py`) — never edit SQLite directly. Web UI: `localhost:8090`. Claude is the sole writer; owner observes via read-only UI.

**Session-start hook** (`.claude/hooks/assertion-check.py`) runs assertions automatically. Failing `specified` = expected. Failing `implemented`/`verified` = regression.

**Anti-drift rules:**
- **All project knowledge lives in the KB.** Specifications, tests, work items, procedures, documents → use the appropriate `db.insert_*()` method.
- **DO NOT create new markdown files** to store canonical project knowledge or session memory outside approved exception paths.
- **Permitted markdown:** CLAUDE.md (platform rules), `applications/<name>/CLAUDE.md` (application rules), MEMORY.md + `memory/*.md` topic files (session state, operational patterns), `bridge/` (file-bridge proposals and reviews), `independent-progress-assessments/` Loyal Opposition reports/logs, `.claude/rules/` local control rules/runbooks/checklists, external-facing published docs (wiki, website, legal).
- **Topic files are NOT canonical** — they are Claude's operational memory. The KB is the source of truth.

### Deliberation Archive Protocol

**Deliberation search is mandatory before proposals and reviews.** See `.claude/rules/deliberation-protocol.md` for full rules.

- **Before proposing:** Search `search_deliberations()` for prior reviews on the same spec/WI/component. Cite DELIB-IDs in proposals.
- **Before reviewing:** Search for prior deliberations. Add "Prior Deliberations" section to reviews.
- **Owner decisions:** Archive immediately as `source_type=owner_conversation`.
- **Session wrap:** Harvest runs automatically as part of `kb-session-wrap`.
- **LO reports:** Include SPEC/WI IDs in report headers for linkage coverage.

### Session Wrap-Up & Handoff

- **Prime Builder sessions:** Execute `/kb-session-wrap <session-id>` for the full 5-phase procedure. Every 5th session is an **audit session** (extra hygiene steps included in the skill).
- **Loyal Opposition sessions:** default wrap-up is an evidence-based report in `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/` plus unresolved-item updates in `independent-progress-assessments/loyal-opposition-log.md`. Do not update KB, MEMORY.md, push, or deploy unless Mike explicitly asked for it.

### Session Scheduler

`.claude/SCHEDULE.md` contains pre-planned prompts injected via `UserPromptSubmit` hook.

### Continuous Improvement Feedback

Provide brief inline coaching notes (prefixed with "💡 **Feedback:**") when observing: terminology inconsistency, bare approvals, credential exposure, or missing structure.

### AskUserQuestion as the Only Valid Owner-Decision Channel

Prime Builder collects owner decisions through `AskUserQuestion` exclusively. Prose decision-asks are invalid. See `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel for the full enforcement contract (Stop-mode hook detection, prose-pattern matching, `memory/pending-owner-decisions.md` recording).

In-scope decision classes (use `AskUserQuestion`, never prose): approvals, waivers, priority choices, formal artifact approvals, requirement clarifications, destructive actions, deployments, blocking owner decisions.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. Last Updated: 2026-05-29 (Slice 3 of `gtkb-claude-md-scope-clarification`). Version: 67.0.0.*
