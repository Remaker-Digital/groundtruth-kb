# CLAUDE.md - Agent Red Customer Experience

This document provides active guidance for AI assistants working on the Agent Red Customer Experience commercial project. It is loaded at the start of every session. **GOV-01: This file MUST NOT exceed 300 lines.**

**Role precedence:** obey the newest owner role assignment reflected in `AGENTS.md` and the startup role-mapping rules under `.claude/rules/`. Loyal Opposition guidance applies only when the owner has explicitly activated that mode for Codex; otherwise Codex operates as Prime Builder.

> **📁 Reference data** (legal, pricing, infrastructure, AGNTCY rules): `CLAUDE-REFERENCE.md` — read on demand.
> **📁 Architecture** (project structure, module inventory): `CLAUDE-ARCHITECTURE.md` — read on demand.
> **📁 Historical archive** (session logs, technical decisions): `CLAUDE_ARCHIVE.md` — read when investigating historical decisions.
> **📁 Session memory** (operational patterns, lessons): `memory/MEMORY.md` — active GT-KB memory must resolve inside `E:\GT-KB`, not a home-directory mirror or legacy project path.

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

## Application Identity

| Attribute | Value |
|-----------|-------|
| **Application Name** | Agent Red Customer Experience |
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

**GroundTruth KB vision filter:** For GroundTruth-related work, prefer choices that reduce the owner's role to adding or refining specifications, answering clarification questions, and making explicit trade-off decisions. Flag approaches that leave routine implementation, deployment plumbing, traceability reconciliation, generated-artifact inspection, or cross-agent process state with the owner.

**Strategic self-improvement directive:** Self-improvement is a GT-KB strategic imperative. When Prime Builder or Loyal Opposition notices a fix-worthy issue or useful workflow enhancement that would improve future work, add it to the MemBase standing backlog/work items for review and future consideration unless it is already tracked. Do not park future work in MEMORY.md or harness-local auto-memory. Backlog capture is not implementation approval; implementation-approved backlog items require explicit owner/governance approval and AskUserQuestion evidence when owner approval is required. Executing a review/consideration item means presenting the insight and implementation options to the owner and using AskUserQuestion to formalize selection and approval to proceed with an implementation proposal.

**The artifact system exists to serve communication.** When the owner and Claude say each say "Specification", "Test", "Test Plan", "Work Item", "Backlog", "Operational Procedure", "Document", or "Environment Config" both must be referring to the same real, verifiable, historically traceable thing.

**operating procedure.** File-based bridge protocol. See `.claude/rules/file-bridge-protocol.md`.
- **DO NOT implement anything without first preparing an implementation proposal and having it reviewed by Codex.**
- **All implementation proposals MUST be reviewed by Codex before any code is written.**
- **All post-implementation reports MUST be reviewed by Codex before committing.**
- **Propose:** Save proposal to `bridge/{name}-001.md`, add NEW entry to `bridge/INDEX.md`.
- **Review:** Codex scans INDEX for NEW/REVISED entries, reviews, adds GO or NO-GO version.
- **Execute:** After Codex GO, implement code, tests, and verify.
- **Report:** Save post-implementation report as new version, add NEW entry for verification.
- **Verify:** Codex reviews report and adds VERIFIED or NO-GO version.
- Both agents scan the index when triggered manually by the owner (`Bridge` or `Bridge scan` prompt). Automated polling was halted 2026-04-25; see `.claude/rules/bridge-essential.md` §"Operational Mode" and §"Bridge Polling: Halted" below.
- Before you deploy any build, ask this question: Is Agent Red ready for a full production deployment?

---

## Artifacts and Change Control

**9 managed artifact types + 2 supporting records** in KB (`groundtruth.db`). See `CLAUDE-ARCHITECTURE.md` § Artifact Inventory for full table/schema details.

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
Location: E:\GT-KB
Key files: CLAUDE.md, memory/MEMORY.md
Next: [describe task].
```

### Session Start: Bridge Index Scan (Mandatory)

At session start, scan `bridge/INDEX.md` for pending work:

1. **Read** `bridge/INDEX.md` and look for entries with GO or NO-GO status that haven't been actioned.
2. **Report** any findings: "Bridge scan: N entries need attention" or "Bridge scan: clear."
3. **Process** the oldest actionable entry first (GO → implement, NO-GO → revise).

### Bridge Polling: Halted (2026-04-25 owner directive)

The poller is not the bridge. The bridge is the durable handoff/review
mechanism in `bridge/INDEX.md`; the poller is only a monitoring/activation
service.

**Both the OS-level Windows scheduled-task pollers, the foreground bridge
monitor watchdog, and the in-session `CronCreate` poller are now retired.**
Bridge scans are manual:

- The owner triggers a Prime bridge scan with a brief prompt such as
  `Bridge` or `Bridge scan`.
- Prime then reads `bridge/INDEX.md`, identifies actionable entries
  (NEW/REVISED needing Prime response; GO/NO-GO from Codex needing Prime
  acknowledgement), and acts.
- Codex bridge scans are similarly owner-triggered in the Codex harness.

Do NOT recreate the in-session `CronCreate` poller, restore the bridge
monitor watchdog startup shortcut, or re-enable the Windows scheduled tasks
(`AgentRedFileBridgeIndexScan-*`, `AgentRedBridgeLivenessAlert`,
`AgentRedPollerLivenessWatcher`) without explicit owner approval and the
cost/benefit analysis required by `.claude/rules/bridge-essential.md`
§"Re-Enabling Pollers".

Rationale: the OS Claude poller (activated ~2026-04-23) fired on a
fixed interval regardless of bridge activity — a ~10× spawn jump
(~12.5M tokens/day) mostly doing work without information, not token
volume. The bridge protocol itself is unaffected.

### Session Start: Active Work List (Mandatory)

After the bridge scan, read `memory/work_list.md`. If it contains unchecked items, continue working through the list following the standard bridge protocol (propose → Codex GO → implement → post-impl report → Codex VERIFIED → commit → drop from list). Owner pre-approval is granted for all items on the list.

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
- **Permitted markdown:** CLAUDE.md (rules), MEMORY.md + `memory/*.md` topic files (session state, operational patterns), `bridge/` (file-bridge proposals and reviews), `independent-progress-assessments/` Loyal Opposition reports/runbooks/logs, `.claude/rules/` local control rules, external-facing published docs (wiki, website, legal).
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

## Branching Strategy

| Branch | Purpose | Updated when |
|--------|---------|-------------|
| `main` | Production mirror. Always matches the most recent production deployment. | Merge from `develop` at deployment time. |
| `develop` | Continuous development. All new features, fixes, and experiments land here. | Every session. |
| `hotfix/*` | Emergency production patches. Branched from `main`, merged back to both `main` and `develop`. | Critical production issues only. |

**Workflow:** `develop` → build/test → deploy to staging → staging verified → merge to `main` → deploy to production.

**Rules:**
1. Never commit directly to `main`. All work happens on `develop`.
2. Merge to `main` only as part of a production deployment operation.
3. `main` must always be deployable — it represents what is running in production.
4. Version tags (v1.98.x) are created on `develop` at build time and propagated to `main` via merge.
5. Hotfixes follow the hotfix workflow below.

**Hotfix Workflow:**
1. Branch from `main` at the current production tag: `hotfix/v{version}-{issue}` (e.g., `hotfix/v1.98.92-critic-timeout`).
2. Implement the minimal fix. CI (lint, tests, security scan) runs automatically on `hotfix/**` branches.
3. Deploy the hotfix branch to staging for verification.
4. After staging verification, merge to `main` and deploy to production (GOV-16 approval required).
5. Immediately backport: merge `main` to `develop` to prevent divergence.
6. Delete the hotfix branch after both merges are confirmed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. Last Updated: 2026-04-30 (S324). Version: 66.1.0.*
