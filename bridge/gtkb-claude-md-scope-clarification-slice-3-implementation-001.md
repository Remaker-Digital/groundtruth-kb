NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 39611c3e-b51e-43f1-aa37-5ec4be3894b0
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3
Project: PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION
Work Item: WI-3438

# GT-KB CLAUDE.md Scope Clarification - Slice 3 - Implementation - 001

Document: gtkb-claude-md-scope-clarification-slice-3-implementation
Version: 001 (NEW; implementation proposal carrying forward Slice 2 governance-review GO)
Date: 2026-05-29 UTC
Carries forward GO: bridge/gtkb-claude-md-scope-clarification-slice-2-004.md
Parent governance review: bridge/gtkb-claude-md-scope-clarification-slice-2-003.md
Parent scoping: bridge/gtkb-claude-md-scope-clarification-scoping-001.md

## Claim

This proposal implements the Slice 2 governance design at [`bridge/gtkb-claude-md-scope-clarification-slice-2-003.md`](gtkb-claude-md-scope-clarification-slice-2-003.md) (Codex GO at -004). It executes the CLAUDE.md split (Approach C), the 18.I files migration to `applications/Agent_Red/`, the protected-artifact registry expansion (F4), the root SECURITY.md platform stub (F5), and the canonical-terminology.md update reflecting the new protected paths.

This is an implementation proposal with full `Project Authorization` / `Project` / `Work Item` metadata. The implementation operates under the bounded project authorization `PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3` per `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` and the 4-AUQ owner-decision chain S364 2026-05-28 (Approach C, 18.I scope, F1 reframe, F4 expand registry).

## Specification Links

- `GOV-01` — CLAUDE.md ≤300 lines; verified by `wc -l CLAUDE.md` post-implementation.
- `GOV-08` — KB is truth; narrative-artifact permitted-markdown exception (extended to `applications/<name>/CLAUDE.md`).
- `GOV-09` — Owner input classification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority. This NEW is filed at `bridge/INDEX.md` with `NEW: bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-001.md` inserted at the top of a new document entry per the protocol's newest-first convention; no prior versions exist for this thread.
- `GOV-ARTIFACT-APPROVAL-001` — 7 narrative-artifact approval packets required (4 root mutations + 3 newly-protected app-side creates).
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact mutation gate at PreToolUse Write + pre-commit `scripts/check_narrative_artifact_evidence.py`.
- `DCL-CONCEPT-ON-CONTACT-001` — load-bearing concept surfacing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Specification Links section enumerates linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification commands listed below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `applications/<name>/` placement.
- `ADR-0001` — Three-Tier Memory Architecture.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifact graph preservation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — narrative-artifact lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` — Agent Red placement under `applications/Agent_Red/`.
- `.claude/rules/operating-role.md` — durable role assignment in JSON.
- `.claude/rules/bridge-essential.md` §"Operational Mode" — cross-harness event-driven trigger.
- `.claude/rules/operating-model.md` §1, §2.
- `.claude/rules/canonical-terminology.md`.
- `.claude/rules/canonical-terminology.toml` dual-agent profile.
- `.claude/rules/project-root-boundary.md`.
- `.claude/rules/file-bridge-protocol.md`.
- `config/governance/narrative-artifact-approval.toml`.
- `AGENTS.md` line 11.

## Owner Decisions / Input

Authorized via `PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3` (citing `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` as owner-decision basis) operationalized by the 4-AUQ owner-decision chain this session 2026-05-29:

1. **Approach selection** (Slice 1 follow-up): "Codex GO at -002. Which structural approach should Slice 2 implement?" → **"C: Split (recommended)"**
2. **Scope expansion**: "ISOLATION-018 already planned CLAUDE.md correction as part of sub-slices 18.I + 18.K... How should Slice 2 relate?" → **"Expand Slice 2 to 18.I scope"**
3. **F1 metadata-mismatch**: "How should the REVISED address the bridge_kind/implementation-metadata mismatch?" → **"Reframe Slice 2 as governance review"** (Slice 3 carries the implementation per this decision)
4. **F4 registry-expansion**: "How should the REVISED handle the protected-artifact registry gap for new applications/Agent_Red/* files?" → **"Expand registry to protect app-side files"**

Per-protected-mutation approval packets are presented to owner via AskUserQuestion at write time per `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Prior Deliberations

Carried forward from Slice 1, Slice 2 governance review, and Slice 2 REVISED:
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (PAUTH owner-decision basis)
- `DELIB-0877` (industry-alignment critique for GT-KB/application separation)
- `DELIB-0785`, `DELIB-0834`, `DELIB-0023`, `DELIB-0876`, `DELIB-0501`, `DELIB-0327`, `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`, `DELIB-0706`, `DELIB-0719`.

Bridge thread family:
- `bridge/gtkb-claude-md-scope-clarification-scoping-001.md` (NEW)
- `bridge/gtkb-claude-md-scope-clarification-scoping-002.md` (Codex GO)
- `bridge/gtkb-claude-md-scope-clarification-slice-2-001.md` (NEW; implementation-targeting attempt)
- `bridge/gtkb-claude-md-scope-clarification-slice-2-002.md` (Codex NO-GO with F1-F5)
- `bridge/gtkb-claude-md-scope-clarification-slice-2-003.md` (REVISED-1 governance review)
- `bridge/gtkb-claude-md-scope-clarification-slice-2-004.md` (Codex GO on governance review)

## Reference to Slice 2 Design

Per-file disposition matrix, F2/F3 text corrections, F4 registry expansion plan, F5 SECURITY.md stub plan, and CLAUDE-ARCHITECTURE.md line-12 fix are all documented in `bridge/gtkb-claude-md-scope-clarification-slice-2-003.md`. This Slice 3 implements those designs concretely with embedded content below.

## Embedded Content — Root CLAUDE.md (Rewritten Platform Content)

Full proposed content for `E:\GT-KB\CLAUDE.md` after Slice 3 implementation. Length verified ~265 lines (satisfies GOV-01 ≤300). Contains all 5 doctor `dual-agent` profile `required_startup_terms`. F2 correction applied to role-precedence paragraph; F3 correction applied to operating-procedure bullets + session-start bridge-scan section.

```markdown
# CLAUDE.md — GroundTruth-KB Platform

This document provides active guidance for AI assistants working on the GroundTruth-KB (GT-KB) platform. **Unless Mike explicitly says the session is application work (e.g., Agent Red), assume active work is GroundTruth-KB.** **GOV-01: This file MUST NOT exceed 300 lines.**

For application-scope guidance (Application Identity, Copyright, Adding Commercial Features, Branching Strategy, Hotfix Workflow), see [`applications/Agent_Red/CLAUDE.md`](applications/Agent_Red/CLAUDE.md). Application-scope files are consulted only when the active work subject is `application` and the named application is Agent Red.

**Role precedence:** active role is resolved at session start from `harness-state/harness-identities.json` (persistent harness identity) and `harness-state/role-assignments.json` (role set; the single source-of-truth durable role map). `.claude/rules/operating-role.md`, `AGENTS.md`, and `.claude/rules/*.md` files are explanatory guidance only — they describe behavior contracts but cannot override the durable role assignment map. If markdown text and the durable map differ, the durable map wins; surface the divergence as a defect rather than acting on the markdown.

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

### Session Start: Bridge Index Scan (Mandatory)

At session start, scan `bridge/INDEX.md` for pending work using a **role-specific** filter:

1. **Read** `bridge/INDEX.md` and look for actionable entries for the active role:
   - **Prime Builder sessions:** look for latest `GO` or `NO-GO` per thread (Codex's verdicts on Prime's proposals/reports).
   - **Loyal Opposition sessions:** look for latest `NEW` or `REVISED` per thread (Prime's proposals/reports awaiting review).
2. **Report** any findings: "Bridge scan: N entries need attention" or "Bridge scan: clear."
3. **Process** the oldest actionable entry first.

The cross-harness event-driven trigger (registered as PostToolUse + Stop hooks per `.claude/rules/bridge-essential.md`) handles inter-session dispatch automatically; the session-start scan above is the in-session entry point and ensures awareness of items that landed while the session was idle.

### Session Start: Active Work List (Mandatory)

After the bridge scan, read `memory/work_list.md`. If it contains unchecked items, continue working through the list following the standard bridge protocol (propose → Codex GO → implement → post-impl report → Codex VERIFIED → commit → drop from list). Owner pre-approval is granted for all items on the list.

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
- **Permitted markdown:** CLAUDE.md (platform rules), `applications/<name>/CLAUDE.md` (application rules), MEMORY.md + `memory/*.md` topic files (session state, operational patterns), `bridge/` (file-bridge proposals and reviews), `independent-progress-assessments/` Loyal Opposition reports/runbooks/logs, `.claude/rules/` local control rules, external-facing published docs (wiki, website, legal).
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

### AskUserQuestion as the Only Valid Owner-Decision Channel

Prime Builder collects owner decisions through `AskUserQuestion` exclusively. Prose decision-asks are invalid. See `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel for the full enforcement contract (Stop-mode hook detection, prose-pattern matching, `memory/pending-owner-decisions.md` recording).

In-scope decision classes (use `AskUserQuestion`, never prose): approvals, waivers, priority choices, formal artifact approvals, requirement clarifications, destructive actions, deployments, blocking owner decisions.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. Last Updated: 2026-05-29 (Slice 3 of `gtkb-claude-md-scope-clarification`). Version: 67.0.0.*
```

## Embedded Content — applications/Agent_Red/CLAUDE.md (New Application-Scope File)

```markdown
# applications/Agent_Red/CLAUDE.md — Agent Red Customer Experience

> **Scope:** This file is **application-scope guidance** for the Agent Red Customer Experience application. It is consulted only when the active GT-KB work subject is `application` AND the named application is Agent Red. It is NOT platform authority and does NOT modify GT-KB platform rules.
>
> Agent Red itself is a **separate project** at `https://github.com/mike-remakerdigital/agent-red`. This file documents the Agent-Red-specific guidance that lives within the GT-KB application-management surface (`applications/Agent_Red/`) per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001`.
>
> For platform-scope guidance (Roles, Governance Index, Bridge Protocol, Artifact discipline, Knowledge Database Access, AskUserQuestion enforcement), see [`E:\GT-KB\CLAUDE.md`](../../CLAUDE.md). Platform rules govern this application; application rules do not govern the platform.

---

## Application Identity

| Attribute | Value |
|-----------|-------|
| **Application Name** | Agent Red Customer Experience |
| **Type** | Commercial SaaS Product (Shopify + Standalone) |
| **Status** | See `memory/MEMORY.md` for versions, test counts, and release progress. |
| **Owner** | Remaker Digital (DBA of VanDusen & Palmeter, LLC) |
| **Application Project Root** | `E:\GT-KB\applications\Agent_Red\` |
| **Application Source Repository** | `https://github.com/mike-remakerdigital/agent-red` (separate from GT-KB platform) |

### Copyright Notice

All new work in this application directory must include:

```
© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
```

This copyright applies to Agent Red application code. GT-KB platform code carries its own platform-scope copyright; application copyright must not be mistakenly applied to platform code outside `applications/Agent_Red/`.

---

## Adding Commercial Features

When the work subject is Agent Red:

1. Create features in `applications/Agent_Red/src/` exclusively
2. Add the Agent Red copyright notice to all new files
3. Test integration patterns independently
4. Never commit AGNTCY source code into this repo
5. Read AGNTCY from the public repo: https://github.com/Remaker-Digital/AGNTCY-muti-agent-deployment-customer-service

---

## Branching Strategy

This branching strategy applies to **Agent Red application deployment**. GT-KB platform releases follow a separate cycle (PyPI `groundtruth-kb` package; see platform release-readiness governance under `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`).

| Branch | Purpose | Updated when |
|--------|---------|-------------|
| `main` | Production mirror. Always matches the most recent Agent Red production deployment. | Merge from `develop` at deployment time. |
| `develop` | Continuous development. All new Agent Red features, fixes, and experiments land here. | Every session. |
| `hotfix/*` | Emergency production patches. Branched from `main`, merged back to both `main` and `develop`. | Critical production issues only. |

**Workflow:** `develop` → build/test → deploy to staging → staging verified → merge to `main` → deploy to production.

**Rules:**
1. Never commit directly to `main`. All work happens on `develop`.
2. Merge to `main` only as part of an Agent Red production deployment operation.
3. `main` must always be deployable — it represents what is running in Agent Red production.
4. Version tags (v1.98.x) are created on `develop` at build time and propagated to `main` via merge.
5. Hotfixes follow the hotfix workflow below.

**Before deploying any Agent Red build, ask this question: Is Agent Red ready for a full production deployment?** (Per GOV-16 deploy gate; owner approval required.)

### Hotfix Workflow

1. Branch from `main` at the current production tag: `hotfix/v{version}-{issue}` (e.g., `hotfix/v1.98.92-critic-timeout`).
2. Implement the minimal fix. CI (lint, tests, security scan) runs automatically on `hotfix/**` branches.
3. Deploy the hotfix branch to staging for verification.
4. After staging verification, merge to `main` and deploy to production (GOV-16 approval required).
5. Immediately backport: merge `main` to `develop` to prevent divergence.
6. Delete the hotfix branch after both merges are confirmed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. Created: 2026-05-29 (Slice 3 of `gtkb-claude-md-scope-clarification`).*
```

## Embedded Content — Root SECURITY.md (New Platform Stub per F5)

```markdown
# Security Policy — GroundTruth-KB Platform

This is the platform-level security policy entry point for GroundTruth-KB.

## Reporting a Vulnerability

To report a vulnerability in the GroundTruth-KB platform itself (governance contract, role enforcement, approval-packet evidence layer, secrets scanning, doctor checks, CLI surfaces), email **security@remakerdigital.com**.

To report a vulnerability in a specific application managed by GT-KB, see the per-application security policy:

- **Agent Red Customer Experience:** [`applications/Agent_Red/SECURITY.md`](applications/Agent_Red/SECURITY.md)

## Platform Security Practices

The GroundTruth-KB platform enforces:
- Pre-commit secrets scanning via `gt secrets scan --staged --fail-on verified-provider`.
- Narrative-artifact approval-packet evidence layer via `scripts/check_narrative_artifact_evidence.py` (universal `.githooks/pre-commit` floor).
- Append-only versioning of canonical artifacts in MemBase.
- Role-based authority via `harness-state/role-assignments.json` durable role map.
- Bridge-protocol GO/NO-GO/VERIFIED audit trail for governance-sensitive changes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
```

## CLAUDE-ARCHITECTURE.md Line-12 Path Fix

After `git mv CLAUDE-ARCHITECTURE.md applications/Agent_Red/CLAUDE-ARCHITECTURE.md`, edit line 12 in the new location:

- Old line 12: `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\`
- New line 12: `E:\GT-KB\applications\Agent_Red\`

No other content changes. Lines 1-11 and 13-259 preserved verbatim.

## Embedded Content — narrative-artifact-approval.toml Addition (per F4)

Insert after the existing `[[protected_artifacts]] id = "role-and-governance-rules"` block (around line 47):

```toml
[[protected_artifacts]]
id = "application-scope-rules"
description = "Application-scope narrative authority surfaces for managed applications under applications/<name>/. Per F4 decision in bridge/gtkb-claude-md-scope-clarification-slice-2-003.md."
patterns = [
  "applications/*/CLAUDE.md",
  "applications/*/CLAUDE-REFERENCE.md",
  "applications/*/CLAUDE-ARCHITECTURE.md",
]
required_evidence = [
  "approval_packet",
  "presented_to_user=true",
  "transcript_captured=true",
  "explicit_change_request",
]
```

This file is self-excluded by `excluded_by_design.items[pattern = "config/governance/narrative-artifact-approval.toml"]`; no approval packet required.

## canonical-terminology.md Update Plan (per F4)

The canonical-artifact definition around line 1288 currently reads:
```
`CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`, and
```

Extend to acknowledge application-scope narrative authority:
```
`CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`,
`applications/<name>/CLAUDE.md`, `applications/<name>/CLAUDE-REFERENCE.md`,
`applications/<name>/CLAUDE-ARCHITECTURE.md`, and
```

Plus a one-sentence note explaining that application-scope authority extends to per-application narrative artifacts under the canonical placement convention.

This file IS protected; approval packet #7 required.

## Per-File Disposition Matrix (Implementation)

| # | File | Action | Status post-impl |
|---|---|---|---|
| 1 | `CLAUDE.md` (root) | Edit (rewrite per embedded content) | ~265 lines; platform-scoped; Packet 1 |
| 2 | `CLAUDE-REFERENCE.md` (root) | `git mv` to `applications/Agent_Red/CLAUDE-REFERENCE.md` | Deleted from root; Packet 2 |
| 3 | `CLAUDE-ARCHITECTURE.md` (root) | `git mv` + line-12 edit | Deleted from root; new at app-side; Packet 3 |
| 4 | `applications/Agent_Red/CLAUDE.md` | Create per embedded content | New file; ~75 lines; Packet 4 (newly protected per F4) |
| 5 | `applications/Agent_Red/CLAUDE-REFERENCE.md` | Created via git mv (content preserved) | New file at app-side; Packet 5 (newly protected per F4) |
| 6 | `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` | Created via git mv + line-12 edit | New file at app-side; Packet 6 (newly protected per F4) |
| 7 | `CLAUDE_ARCHIVE.md` (root) | `git mv` to `applications/Agent_Red/CLAUDE_ARCHIVE.md` | Deleted from root; not protected |
| 8 | `CONTRIBUTING.md` (root) | `git mv` to `applications/Agent_Red/CONTRIBUTING.md` | Deleted from root; not protected |
| 9 | `CHANGELOG.md` (root) | `git mv` to `applications/Agent_Red/CHANGELOG.md` | Deleted from root; not protected |
| 10 | `SECURITY.md` (root) | `git mv` to `applications/Agent_Red/SECURITY.md` THEN create new root stub per embedded content | App-side preserved; new root stub created |
| 11 | `config/governance/narrative-artifact-approval.toml` | Edit (insert new `application-scope-rules` block per F4) | Updated; self-excluded; no packet |
| 12 | `.claude/rules/canonical-terminology.md` | Edit (extend canonical-artifact definition around line 1288) | Updated; Packet 7 |

**Files NO CHANGE**: README.md, AGENTS.md, vision.md, MEMORY.md (root).

## Approval-Packet Plan (7 Packets)

All packets land under `.groundtruth/formal-artifact-approvals/2026-05-29-<artifact-id>.json` with schema per `config/governance/narrative-artifact-approval.toml` [approval_packet] section.

| # | artifact_id | action | target_path | full_content_sha256 source |
|---|---|---|---|---|
| 1 | `claude-md-platform-split-2026-05-29` | `update` | `CLAUDE.md` | sha256 of LF-normalized embedded platform content |
| 2 | `claude-reference-md-delete-from-root-2026-05-29` | `delete` | `CLAUDE-REFERENCE.md` | empty (delete) |
| 3 | `claude-architecture-md-delete-from-root-2026-05-29` | `delete` | `CLAUDE-ARCHITECTURE.md` | empty (delete) |
| 4 | `applications-agent-red-claude-md-create-2026-05-29` | `create` | `applications/Agent_Red/CLAUDE.md` | sha256 of LF-normalized embedded app-side content |
| 5 | `applications-agent-red-claude-reference-md-create-2026-05-29` | `create` | `applications/Agent_Red/CLAUDE-REFERENCE.md` | sha256 of content (preserved via git mv) |
| 6 | `applications-agent-red-claude-architecture-md-create-2026-05-29` | `create` | `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` | sha256 of content (preserved from git mv + line-12 edit) |
| 7 | `canonical-terminology-md-protected-paths-extension-2026-05-29` | `update` | `.claude/rules/canonical-terminology.md` | sha256 of edited content |

All packets include `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` citing PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3, `changed_by=prime-builder/claude-code-opus-4-7`, `change_reason="Slice 3 of gtkb-claude-md-scope-clarification per PAUTH"`.

Per-packet owner approval is obtained via AskUserQuestion at write time per `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Bridge Index Entry

This NEW proposal is filed under `bridge/` with an INDEX update inserting `Document: gtkb-claude-md-scope-clarification-slice-3-implementation` + `NEW: bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-001.md` at the top of `bridge/INDEX.md` per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. No prior versions exist; no deletion or rewrite of prior versions.

## target_paths

- `CLAUDE.md` (update; Packet 1)
- `CLAUDE-REFERENCE.md` (delete via git mv; Packet 2)
- `CLAUDE-ARCHITECTURE.md` (delete via git mv; Packet 3)
- `SECURITY.md` (create new platform stub after git mv of old content)
- `CONTRIBUTING.md` (delete via git mv; not protected)
- `CHANGELOG.md` (delete via git mv; not protected)
- `CLAUDE_ARCHIVE.md` (delete via git mv; not protected)
- `applications/Agent_Red/CLAUDE.md` (create; Packet 4)
- `applications/Agent_Red/CLAUDE-REFERENCE.md` (create via git mv; Packet 5)
- `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` (create via git mv + line-12 edit; Packet 6)
- `applications/Agent_Red/CLAUDE_ARCHIVE.md` (create via git mv; not protected)
- `applications/Agent_Red/CONTRIBUTING.md` (create via git mv; not protected)
- `applications/Agent_Red/CHANGELOG.md` (create via git mv; not protected)
- `applications/Agent_Red/SECURITY.md` (create via git mv; not protected)
- `config/governance/narrative-artifact-approval.toml` (update; self-excluded; no packet)
- `.claude/rules/canonical-terminology.md` (update; Packet 7)
- `.groundtruth/formal-artifact-approvals/2026-05-29-*.json` (7 packet files)
- `groundtruth.db` (MemBase mutations: (a) WI-3438 lifecycle state updates during implementation via `gt backlog` commands; (b) `gt projects complete-authorization PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3` at end of Slice 3; (c) `gt deliberations record` for the 4-AUQ owner-decision chain harvest as `source_type=owner_conversation` records). All MemBase writes go through governed CLI surfaces (no raw db.insert_*); changes captured in MemBase append-only history with `changed_by=prime-builder/claude-code-opus-4-7` attribution.

## Requirement Sufficiency

Existing requirements sufficient. No new specifications need to be authored. This proposal operationalizes:
- Slice 2 governance design at `bridge/gtkb-claude-md-scope-clarification-slice-2-003.md` (Codex GO at -004).
- 4-AUQ owner-decision chain S364 2026-05-29 (Approach C, 18.I scope, F1 reframe, F4 expand registry).
- PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3 (created this session, citing DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE).

## Specification-Derived Verification Plan

After implementation, run each verification command and record results in the post-implementation report:

| Verification | Command | Expected |
|---|---|---|
| GOV-01 line cap | `wc -l CLAUDE.md` | ≤300 |
| Doctor profile required_startup_terms | `grep -c "MemBase\|Deliberation Archive\|MEMORY.md\|Prime Builder\|Loyal Opposition" CLAUDE.md` | ≥5 |
| Doctor dual-agent profile check | `python -m groundtruth_kb project doctor` | PASS for canonical-terminology |
| Cross-reference grep platform side | `grep -rn "CLAUDE.md" .claude/rules/ AGENTS.md` | All references still resolvable |
| Cross-reference grep app side | `grep -rn "applications/Agent_Red/CLAUDE" .claude/rules/ CLAUDE.md` | New refs landed |
| Registry expansion check | `grep -A4 "application-scope-rules" config/governance/narrative-artifact-approval.toml` | Block present |
| Protected-pattern enforcement | Test write to `applications/Agent_Red/CLAUDE.md` without packet (via Write tool) | Blocked by hook |
| Pre-commit narrative gate | `python scripts/check_narrative_artifact_evidence.py --staged` (with all packets staged) | PASS |
| README link integrity | `test -f $(grep -oP "(?<=\[Security policy\]\()[^)]+" README.md)` | File exists |
| 7 approval packets present | `ls .groundtruth/formal-artifact-approvals/2026-05-29-*.json \| wc -l` | 7 |
| Hash match (per packet) | `python -c "import hashlib,json; p=json.load(open('<pkt>')); content=open(p['target_path'],'rb').read().replace(b'\\r\\n',b'\\n'); assert hashlib.sha256(content).hexdigest()==p['full_content_sha256']"` | No assertion error per packet |

## Risk / Rollback

- **Risk**: Approval-packet hash mismatch at write time. Mitigation: compute SHA-256 from final LF-normalized content before staging the packet; the Write tool's narrative-artifact-approval-gate hook re-verifies at write time.
- **Risk**: Doctor `dual-agent` profile term-check fails if F2/F3 corrections drop a required_startup_term. Mitigation: pre-commit verification step (`grep -c` above) confirms 5 terms present.
- **Risk**: Cross-references to specific CLAUDE.md section anchors break if heading wording changes. Mitigation: new content preserves Governance Index heading wording (canonical-terminology.md:1328 anchor).
- **Risk**: New `applications/*/CLAUDE.md` protected patterns not matched by the hook. Mitigation: test write (verification command above) confirms enforcement.
- **Risk**: README link to root SECURITY.md breaks while moving the file. Mitigation: ordering — create new root SECURITY.md stub BEFORE running git mv of old root SECURITY.md content (or use atomic stage: stage both git mv and new stub, commit together).
- **Risk**: Parallel session contamination (per session memory feedback). Mitigation: verify clean working tree of target paths before each protected mutation; re-activate PAUTH before each Edit.
- **Rollback**: `git restore` reverts root file changes; `rm -rf applications/Agent_Red/{CLAUDE,CLAUDE-REFERENCE,CLAUDE-ARCHITECTURE,CLAUDE_ARCHIVE,CONTRIBUTING,CHANGELOG,SECURITY}.md` removes new app-side files; `rm .groundtruth/formal-artifact-approvals/2026-05-29-*.json` removes packets; `git restore config/governance/narrative-artifact-approval.toml .claude/rules/canonical-terminology.md` reverts registry/terminology updates.

## Implementation Sequence

1. Stage `narrative-artifact-approval.toml` update (registry expansion) — landing this FIRST ensures the new applications/*/CLAUDE.md patterns are protected by the time the app-side files are created.
2. Generate Packet 7 for canonical-terminology.md update; Write the canonical-terminology.md edit.
3. Generate Packet 1 for CLAUDE.md update; Write the platform CLAUDE.md rewrite.
4. Generate Packet 4 for applications/Agent_Red/CLAUDE.md create; Write the new app-side CLAUDE.md.
5. `git mv CLAUDE-REFERENCE.md applications/Agent_Red/CLAUDE-REFERENCE.md`; generate Packets 2 (root delete) and 5 (app-side create); content hash preserved.
6. `git mv CLAUDE-ARCHITECTURE.md applications/Agent_Red/CLAUDE-ARCHITECTURE.md`; edit line 12; generate Packets 3 (root delete) and 6 (app-side create).
7. `git mv` for CLAUDE_ARCHIVE.md, CONTRIBUTING.md, CHANGELOG.md (no packets).
8. Stage new root SECURITY.md stub; `git mv` old SECURITY.md content to app-side (sequenced to avoid broken README link).
9. Run all verification commands; collect results.
10. File post-implementation report at version `-NNN` for Codex VERIFIED review.

## Owner Action Required

After Codex GO on this Slice 3 proposal:
1. Owner is presented with the 7 approval packets via AskUserQuestion (one per protected mutation; packet content shown verbatim).
2. Owner approves each packet.
3. Prime Builder executes per the Implementation Sequence above.
4. Verification runs; post-implementation report filed.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
