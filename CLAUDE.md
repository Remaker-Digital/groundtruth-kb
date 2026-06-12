# CLAUDE.md — GroundTruth-KB Platform

This document provides active guidance for AI assistants working on the GroundTruth-KB (GT-KB) platform. **Unless Mike explicitly says the session is application work (e.g., Agent Red), assume active work is GroundTruth-KB.** **GOV-01: This file MUST NOT exceed 300 lines.**

For application-scope guidance (Application Identity, Copyright, Adding Commercial Features, Branching Strategy, Hotfix Workflow), see [`applications/Agent_Red/CLAUDE.md`](applications/Agent_Red/CLAUDE.md). Application-scope files are consulted only when the active work subject is `application` and the named application is Agent Red.

**Role precedence:** active role is resolved at session start from `harness-state/harness-identities.json` (persistent harness identity) and `harness-state/harness-registry.json` (canonical role registry), read through `groundtruth_kb.harness_projection.read_roles` or the `roles` subcommand under `gt harness`. `.claude/rules/operating-role.md`, `AGENTS.md`, and `.claude/rules/*.md` files are explanatory guidance only — they describe behavior contracts but cannot override the durable role assignment map. If markdown text and the durable map differ, the durable map wins; surface the divergence as a defect rather than acting on the markdown. Interactive sessions MAY override the durable role for in-session surfaces (SessionStart disclosure, AXIS 2 Claude-native surface, focus menu, MemBase attribution, AUQ routing) by typing the canonical init keyword `::init gtkb (pb|lo)` on an owner prompt; the override lives in the ephemeral `.claude/session/active-session-role.json` marker for the rest of the session and is invalidated by the next SessionStart. Headless dispatch routing remains keyed to the durable role per `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001`.

> **📁 Application-scope reference** (Agent Red legal, pricing, infrastructure, AGNTCY rules): [`applications/Agent_Red/CLAUDE-REFERENCE.md`](applications/Agent_Red/CLAUDE-REFERENCE.md) — read on demand when working on Agent Red.
> **📁 Application-scope architecture** (Agent Red project structure, module inventory): [`applications/Agent_Red/CLAUDE-ARCHITECTURE.md`](applications/Agent_Red/CLAUDE-ARCHITECTURE.md) — read on demand.
> **📁 Application-scope historical archive** (Agent Red session logs, technical decisions): [`applications/Agent_Red/CLAUDE_ARCHIVE.md`](applications/Agent_Red/CLAUDE_ARCHIVE.md) — read when investigating Agent Red historical decisions.
> **📁 Platform session memory** (operational patterns, lessons): `memory/MEMORY.md` — the in-repo GT-KB notepad is authoritative; home-directory auto-memory is a non-authoritative harness cache and must be reconciled only through an owner-approved in-root export/snapshot.

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

| ID | Title |
|----|-------|
| GOV-01 | CLAUDE.md must not exceed 300 lines |
| GOV-02 | CLAUDE.md must be minimum size without loss of fidelity |
| GOV-03 | Specs are the negotiation artifact for mutual understanding |
| GOV-04 | Spec granularity driven by test unambiguity, not mandatory decomposition |
| GOV-05 | Specs mature through iterative refinement |
| GOV-06 | Spec-first correction cycle: fix the spec, not the code |
| GOV-07 | No bug fixes during testing procedures |
| GOV-08 | Knowledge Database is the single source of truth |
| GOV-09 | Owner Input Classification Rule: detect specification language before implementation |
| GOV-10 | Test artifacts must exercise exposed production interfaces |
| GOV-11 | Design Decision Checkpoint Discipline |
| GOV-12 | Work item creation triggers test creation |
| GOV-13 | Test artifacts must be assigned to at least one test plan phase upon creation |
| GOV-14 | UI element test maintenance — add/retire tests when UI elements change |
| GOV-15 | Test fix approval gate — no autonomous fixes for failed tests |
| GOV-16 | Deployment approval gate — no autonomous deployments |
| GOV-17 | Automation script modification approval gate |
| GOV-19 | Outside-in testing principle |
| GOV-20 | Architecture Decision Governance |
| GOV-ACTING-PRIME-BUILDER-001 | Codex acts as Prime Builder while canonical Prime Builder is unavailable |
| GOV-AGENT-RED-GTKB-CONFORMANCE-001 | Agent Red is a separate project, not part of GroundTruth-KB |
| GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001 | GT-KB project root boundary: Agent Red MUST live at E:/GT-KB/applications/Agent_Red/; applications/ namespace contains only deployed applications |
| GOV-ARTIFACT-AMBIGUITY-AUDIT-001 | All project artifacts must be audited to remove application-specific framing from platform layer |
| GOV-ARTIFACT-APPROVAL-001 | Formal artifact approval gate |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Artifact-oriented governance is the default project interpretation stance |
| GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 | All cross-cutting technical requirements MUST be mechanically enforced for all implementation proposals, via two-layer defense in depth (write-time + review-time) |
| GOV-DOCUMENT-AUTHOR-PROVENANCE-001 | Document Artifact Author Provenance Contract |
| GOV-ENV-LOCAL-AUTHORITY-001 | env source-of-truth artifacts are authoritative per scope; single SoT per scope at a fixed relative path |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Live bridge index authority and permanent bridge repair authority |
| GOV-GLOSSARY-AS-DA-READ-SURFACE-001 | Canonical glossary is the Deliberation Archive's primary read surface |
| GOV-GTKB-ADOPTION-ENFORCEMENT-001 | A GroundTruth-KB adopter application must adopt and enforce available GT-KB governance capabilities |
| GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001 | GT-KB installs must prepare capable harnesses for Prime Builder and Loyal Opposition roles |
| GOV-HARNESS-ONBOARDING-CONTRACT-001 | Harness Onboarding Contract -- required artifacts, machine-checkable assertions, and capability floor for any new GT-KB coding harness |
| GOV-HARNESS-ROLE-PORTABILITY-001 | Prime Builder and Loyal Opposition are portable harness-assigned roles |
| GOV-HARNESS-STATE-SOT-CONSOLIDATION-001 | Harness State Source-of-Truth Consolidation |
| GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001 | LO Advisory Owner-Grilling Gate Before Implementation Proposal |
| GOV-MAJOR-RELEASE-CONTENT-GOAL-001 | Standing Major-Release Content Goal |
| GOV-PLATFORM-SOT-REGISTRY-001 | Platform-wide SoT Artifact Registry |
| GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 | Project-scoped implementation authorization |
| GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 | Project Authorization Requires Linked Specifications |
| GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 | VERIFIED-Driven Project Completion and Retirement Are Automatic (No Owner Confirmation) |
| GOV-RELEASE-READINESS-GOVERNED-TESTING-001 | Production release readiness requires governed test evidence |
| GOV-RELIABILITY-FAST-LANE-001 | Reliability fast-lane for small defect fixes |
| GOV-REQUIREMENTS-COLLECTION-HOOK-001 | A UserPromptSubmit hook MUST classify each owner message and force 3-option clarification when a requirement candidate is detected |
| GOV-SESSION-FORMALIZATION-AUDIT-001 | Session decisions and principles require artifact mapping audit |
| GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 | Sessions actively inform and engage the user with project priorities and suggested actions |
| GOV-SESSION-ROLE-AUTHORITY-001 | Session Role Authority Split - Durable vs Session-Stated |
| GOV-SESSION-SELF-INITIALIZATION-001 | Fresh sessions self-initialize with live role, governance, bridge, dashboard, priorities, and token context |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | Source-of-truth freshness: state claims derive from fresh canonical reads |
| GOV-SPEC-CAPTURE-TRANSPARENCY-001 | Specification capture transparency: surface every capture event + present full text on approve/reject |
| GOV-SPEC-CREATION-STANDING-AUTHORIZATION-001 | Spec creation from owner input has standing authorization |
| GOV-STANDING-BACKLOG-001 | Standing backlog is the durable cross-session work authority |
| GOV-TRIAD-COMPLETENESS-AUDIT-001 | Standing audit of spec/test/implementation triad completeness |
| GOV-V1-ACCEPTANCE-CRITERIA-001 | GT-KB v1.0 Acceptance Criteria (gating, 3-tier; sole anti-perpetual-rc1 checkpoint) |
| RETIRE-SPEC-HARNESS-STATE-ROLE-ASSIGNMENTS-001 | Retire harness-state/role-assignments.json legacy mirror |
| SPEC-1493 | Artifact Inventory: 8 managed artifact types, 2 supporting record types, 0 phantom references |
| SPEC-1499 | Orchestrating artifact principle: composing artifacts reference by ID without duplicating content |
| SPEC-1534 | AGNTCY SDK Mandatory for All Agent Communication |
| SPEC-1662 | GOV-18: Assertion Quality Standard — meaningfulness over coverage |
| SPEC-1830 | Operational Procedures Must Be Code, Not Conversation |
| SPEC-INTAKE-0ecc94 | GT-KB is the default locus for all new artifacts |
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

**Always use the Python API** (`groundtruth-kb/src/groundtruth_kb/db.py`) to access the root `groundtruth.db` — never edit SQLite directly. Web UI: `localhost:8090`. Claude is the sole writer; owner observes via read-only UI.

**Claude SessionStart hook** (`.claude/hooks/assertion-check.py`) runs assertions automatically in the Claude hook surface. Failing `specified` = expected. Failing `implemented`/`verified` = regression.

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

### Continuous Improvement Feedback

Provide brief inline coaching notes (prefixed with "💡 **Feedback:**") when observing: terminology inconsistency, bare approvals, credential exposure, or missing structure.

### AskUserQuestion as the Only Valid Owner-Decision Channel

Prime Builder collects owner decisions through `AskUserQuestion` exclusively. Prose decision-asks are invalid. See `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel for the full enforcement contract (Stop-mode hook detection, prose-pattern matching, `memory/pending-owner-decisions.md` recording).

In-scope decision classes (use `AskUserQuestion`, never prose): approvals, waivers, priority choices, formal artifact approvals, requirement clarifications, destructive actions, deployments, blocking owner decisions.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. Last Updated: 2026-05-29 (Slice 3 of `gtkb-claude-md-scope-clarification`). Version: 67.0.0.*
