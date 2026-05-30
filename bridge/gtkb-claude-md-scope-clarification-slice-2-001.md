NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 39611c3e-b51e-43f1-aa37-5ec4be3894b0
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

# GT-KB CLAUDE.md Scope Clarification - Slice 2 (18.I Implementation) - 001

bridge_kind: governance_review

Document: gtkb-claude-md-scope-clarification-slice-2
Version: 001 (NEW; implementation proposal carrying forward Slice 1 Codex GO and Approach C selection)
Date: 2026-05-28 UTC
Carries forward GO: bridge/gtkb-claude-md-scope-clarification-scoping-002.md
Parent scoping: bridge/gtkb-claude-md-scope-clarification-scoping-001.md

## Claim

This proposal implements the owner-selected **Approach C (Split)** from Slice 1 [`bridge/gtkb-claude-md-scope-clarification-scoping-001.md`](gtkb-claude-md-scope-clarification-scoping-001.md), expanded per owner direction to cover the full ISOLATION-018 sub-slice **18.I scope** (Agent Red identity + memory files at platform root).

The expansion was authorized by owner AskUserQuestion this session 2026-05-28: "ISOLATION-018 already planned CLAUDE.md correction as part of sub-slices 18.I + 18.K (umbrella WITHDRAWN; no sub-slices filed). How should Slice 2 relate?" → "Expand Slice 2 to 18.I scope".

Approach C selection was via AskUserQuestion this session 2026-05-28: "Codex GO at -002. Which structural approach should Slice 2 implement?" → "C: Split (recommended)".

This proposal covers 11 files at the GT-KB platform root: their per-file disposition (move, split, no-change), the verbatim content of the 3 files that change (root CLAUDE.md rewrite, new `applications/Agent_Red/CLAUDE.md`, CLAUDE-ARCHITECTURE.md line-12 path fix), the 3 formal-artifact-approval packets required for protected-path mutations, the cross-reference grep evidence per Codex Slice 1 Condition 5, the GOV-01 line-count compliance plan per Codex Slice 1 Condition 4, and the implementation/verification sequence per Codex Slice 1 Conditions 1-6.

## Specification Links

Carries forward from Slice 1 + 3 advisory specs per Codex Slice 1 Advisory A1.

- `GOV-01` — CLAUDE.md MUST NOT exceed 300 lines. The new platform CLAUDE.md is ~260 lines verified by `wc -l` at implementation time.
- `GOV-08` — KB is truth; narrative artifacts are the permitted-markdown exception. Updated to include `applications/<name>/CLAUDE.md` in permitted markdown.
- `GOV-09` — Owner input classification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority. This proposal is filed at bridge/INDEX.md with `NEW: bridge/gtkb-claude-md-scope-clarification-slice-2-001.md` inserted at the top of the document entry per the protocol's newest-first convention; no prior-version deletion or rewrite.
- `GOV-ARTIFACT-APPROVAL-001` — formal-artifact-approval evidence contract; 3 narrative-artifact approval packets required for the 3 protected mutations (root CLAUDE.md update, root CLAUDE-REFERENCE.md delete, root CLAUDE-ARCHITECTURE.md delete).
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact mutation gate (PreToolUse Write + pre-commit `scripts/check_narrative_artifact_evidence.py`).
- `DCL-CONCEPT-ON-CONTACT-001` — load-bearing concepts surfaced on first contact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every bridge proposal must cite governing specs; this Specification Links section enumerates the linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification will execute spec-derived checks against the modified artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `applications/<name>/` placement convention. New `applications/Agent_Red/CLAUDE.md`, `applications/Agent_Red/CLAUDE-REFERENCE.md`, `applications/Agent_Red/CLAUDE-ARCHITECTURE.md`, `applications/Agent_Red/CLAUDE_ARCHIVE.md`, `applications/Agent_Red/CONTRIBUTING.md`, `applications/Agent_Red/CHANGELOG.md`, `applications/Agent_Red/SECURITY.md` all comply.
- `ADR-0001` — Three-Tier Memory Architecture.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Slice 2 mutations preserve the durable artifact graph (CLAUDE.md cross-references in operating-model.md, AGENTS.md, .claude/rules/ remain resolvable; new file references added).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — narrative-artifact lifecycle trigger discipline; mutations are owner-approved (Approach C via AUQ), Codex-reviewed (Slice 1 GO + Slice 2 review), and verifiable (approval packets + pre-commit gate).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance baseline.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` — Agent Red placement under `applications/Agent_Red/`; this proposal operationalizes the rule for narrative artifacts.
- `.claude/rules/operating-model.md` §1, §2.
- `.claude/rules/canonical-terminology.md`.
- `.claude/rules/canonical-terminology.toml` `dual-agent` profile (required_files contract preserved; CLAUDE.md remains at root with all 5 required_startup_terms present).
- `.claude/rules/project-root-boundary.md`.
- `.claude/rules/file-bridge-protocol.md`.
- `config/governance/narrative-artifact-approval.toml` (protected_artifacts registry; 3 protected mutations identified).
- `AGENTS.md` line 11.

## Owner Decisions / Input

Two owner AskUserQuestion answers this session 2026-05-28 authorize this Slice 2:

1. Approach selection (resolves Slice 1 Owner Action Required): "Codex GO at -002. Which structural approach should Slice 2 implement?" → **"C: Split (recommended)"**.
2. Scope expansion: "ISOLATION-018 already planned CLAUDE.md correction as part of sub-slices 18.I + 18.K (umbrella WITHDRAWN; no sub-slices filed). How should Slice 2 relate?" → **"Expand Slice 2 to 18.I scope"**.

Both decisions captured in chat transcript and will be harvested to the Deliberation Archive at session wrap.

Additional governance basis:
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` (owner-approved at memory/pending-owner-decisions.md:4050-4059 "Approve as drafted") + the source `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (owner-approved at memory/pending-owner-decisions.md:3972-3981 "Approve as drafted") establish the rule that Agent Red files belong under `applications/Agent_Red/`.

## Prior Deliberations

Carries forward from Slice 1 + ISOLATION-018 umbrella context:

- `DELIB-0877` — owner-decision: industry-alignment critique for GT-KB/application separation; asymmetric safety model.
- `DELIB-0785` — GT-KB has its own release-readiness lifecycle, separate from Agent Red.
- `DELIB-0834` — Agent Red as fully conformant application sustained by GT-KB.
- `DELIB-0023` — Membase / Agent Red coupling source-of-truth problem.
- `DELIB-0876` — durable work subject framing.
- `DELIB-0501` — Agent Red Large-Scale Commercial Production Plan (origin of application-focused CLAUDE.md framing).
- `DELIB-0327` — Hotfix / WIP Coexistence Operating Model (origin of CLAUDE.md branching strategy).
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` — placement-over-coercion design.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` — owner-approved retroactive source DELIB establishing Agent Red under `applications/Agent_Red/`; supersedes prior `DELIB-0879` conflicting recommendations.
- `DELIB-0706` — spec pipeline features are GT-KB product features, not Agent Red specific (cited by Codex in Slice 1 GO -002).
- `DELIB-0719` — owner decision for repo-tracked MEMORY.md placement (relevant to root MEMORY.md no-change disposition).

Related bridge threads:
- `bridge/gtkb-isolation-018-agent-red-file-migration-008.md` (umbrella plan with 12 sub-slices A-L; -008 line 173 listed 10 of the 11 files in this Slice 2 scope as 18.I; -008 line 174 listed AGENTS.md as OQ-4 with default-stays-at-root which this Slice 2 confirms).
- `bridge/gtkb-isolation-018-agent-red-file-migration-010.md` (umbrella WITHDRAWN as Prime Supersession Notice 2026-05-13; sub-slices must each file their own proposals; this Slice 2 is the first 18.I-scope sub-slice to be filed).
- `bridge/gtkb-canonical-terminology-agent-red-corrective-003.md` (WITHDRAWN 2026-05-10; addressed glossary entry, not CLAUDE.md scope; out of scope for this Slice 2).

## Per-File Disposition Matrix

| # | File | Lines | Current scope | Disposition | New location | Action | Approval packet? |
|---|---|---|---|---|---|---|---|
| 1 | `README.md` | 86 | Platform (GT-KB IDP intro) | NO CHANGE | root | — | No |
| 2 | `CLAUDE.md` | 301 | Mixed (platform + Agent Red) | **SPLIT** | platform stays at root (~260 lines); app content → `applications/Agent_Red/CLAUDE.md` (new) | Update root; Create app | **Yes** (root update) |
| 3 | `CONTRIBUTING.md` | 67 | Agent Red explicit | MOVE | `applications/Agent_Red/CONTRIBUTING.md` | git mv | No |
| 4 | `vision.md` | 2 | Platform ("Adding MCP servers" GT-KB future-work note) | NO CHANGE | root | — | No |
| 5 | `MEMORY.md` (root) | 41 | Platform (doctor profile marker pointing to `memory/MEMORY.md`) | NO CHANGE | root | — | No |
| 6 | `CHANGELOG.md` | 146 | Agent Red explicit | MOVE | `applications/Agent_Red/CHANGELOG.md` | git mv | No |
| 7 | `SECURITY.md` | 48 | Agent Red ("This policy covers the Agent Red platform") | MOVE | `applications/Agent_Red/SECURITY.md` | git mv | No |
| 8 | `CLAUDE-ARCHITECTURE.md` | 259 | Agent Red (stale: line 12 obsolete path) | **MOVE + UPDATE** | `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` (with line-12 fix) | git mv + edit | **Yes** (root delete) |
| 9 | `CLAUDE-REFERENCE.md` | 263 | Agent Red (legal, AGNTCY) | MOVE | `applications/Agent_Red/CLAUDE-REFERENCE.md` | git mv | **Yes** (root delete) |
| 10 | `CLAUDE_ARCHIVE.md` | 2293 | Agent Red historical session logs | MOVE | `applications/Agent_Red/CLAUDE_ARCHIVE.md` | git mv | No |
| 11 | `AGENTS.md` | 292 | Platform (default-to-GT-KB framing) | NO CHANGE (resolves umbrella OQ-4) | root | — | No |

**3 narrative-artifact approval packets required** (per `config/governance/narrative-artifact-approval.toml` protected_artifacts pattern matching):
1. Root `CLAUDE.md` — action: `update`
2. Root `CLAUDE-REFERENCE.md` — action: `delete`
3. Root `CLAUDE-ARCHITECTURE.md` — action: `delete`

**4 files no change**; **6 file moves** (5 unprotected at root + 1 protected-but-no-content-change CLAUDE-REFERENCE.md); **1 file split**; **1 file move + 1-line content update**.

## Embedded Content — Root CLAUDE.md (Rewritten Platform Content)

The proposed new content of `E:\GT-KB\CLAUDE.md` after Slice 2 implementation. Length ~260 lines; satisfies GOV-01 ≤300 cap. Contains all 5 required_startup_terms per dual-agent profile (MemBase, Deliberation Archive, MEMORY.md, Prime Builder, Loyal Opposition). Default-to-GT-KB framing mirrors AGENTS.md line 11.

```markdown
# CLAUDE.md — GroundTruth-KB Platform

This document provides active guidance for AI assistants working on the GroundTruth-KB (GT-KB) platform. **Unless Mike explicitly says the session is application work (e.g., Agent Red), assume active work is GroundTruth-KB.** **GOV-01: This file MUST NOT exceed 300 lines.**

For application-scope guidance (Application Identity, Copyright, Adding Commercial Features, Branching Strategy, Hotfix Workflow), see [`applications/Agent_Red/CLAUDE.md`](applications/Agent_Red/CLAUDE.md). Application-scope files are consulted only when the active work subject is `application` and the named application is Agent Red.

**Role precedence:** obey the newest owner role assignment reflected in `AGENTS.md` and the startup role-mapping rules under `.claude/rules/`. Loyal Opposition guidance applies only when the owner has explicitly activated that mode for Codex; otherwise Codex operates as Prime Builder.

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

**Strategic self-improvement directive:** Self-improvement is a GT-KB strategic imperative. When Prime Builder or Loyal Opposition notices a fix-worthy issue or useful workflow enhancement that would improve future work, add it to the MemBase standing backlog/work items for review and future consideration unless it is already tracked. Do not park future work in MEMORY.md or harness-local auto-memory. Backlog capture is not implementation approval; implementation-approved backlog items require explicit owner/governance approval and AskUserQuestion evidence when owner approval is required. Executing a review/consideration item means presenting the insight and implementation options to the owner and using AskUserQuestion to formalize selection and approval to proceed with an implementation proposal.

**The artifact system exists to serve communication.** When the owner and Claude say each say "Specification", "Test", "Test Plan", "Work Item", "Backlog", "Operational Procedure", "Document", or "Environment Config" both must be referring to the same real, verifiable, historically traceable thing.

**Operating procedure.** File-based bridge protocol. See `.claude/rules/file-bridge-protocol.md`.
- **DO NOT implement anything without first preparing an implementation proposal and having it reviewed by Codex.**
- **All implementation proposals MUST be reviewed by Codex before any code is written.**
- **All post-implementation reports MUST be reviewed by Codex before committing.**
- **Propose:** Save proposal to `bridge/{name}-001.md`, add NEW entry to `bridge/INDEX.md`.
- **Review:** Codex scans INDEX for NEW/REVISED entries, reviews, adds GO or NO-GO version.
- **Execute:** After Codex GO, implement code, tests, and verify.
- **Report:** Save post-implementation report as new version, add NEW entry for verification.
- **Verify:** Codex reviews report and adds VERIFIED or NO-GO version.
- Both agents scan the index when triggered manually by the owner (`Bridge` or `Bridge scan` prompt). Automated polling was halted 2026-04-25; see `.claude/rules/bridge-essential.md` §"Operational Mode" and §"Bridge Polling: Halted" below.

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

At session start, scan `bridge/INDEX.md` for pending work:

1. **Read** `bridge/INDEX.md` and look for entries with GO or NO-GO status that haven't been actioned.
2. **Report** any findings: "Bridge scan: N entries need attention" or "Bridge scan: clear."
3. **Process** the oldest actionable entry first (GO → implement, NO-GO → revise).

### Bridge Polling: Halted (2026-04-25 owner directive)

The poller is not the bridge. The bridge is the durable handoff/review
mechanism in `bridge/INDEX.md`; the poller is only a monitoring/activation
service.

**Both the OS-level Windows scheduled-task pollers, the foreground bridge
monitor watchdog, and the in-session `CronCreate` poller are retired.**
Bridge scans are manual; bridge dispatch is event-driven via the cross-harness
trigger registered as PostToolUse and Stop hooks. See
`.claude/rules/bridge-essential.md` §"Operational Mode" for full details.

Do NOT recreate the in-session `CronCreate` poller, restore the bridge
monitor watchdog startup shortcut, or re-enable the Windows scheduled tasks
without explicit owner approval and the cost/benefit analysis required by
`.claude/rules/bridge-essential.md` §"Re-Enabling Pollers".

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

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. Last Updated: 2026-05-28 (Slice 2 of `gtkb-claude-md-scope-clarification`). Version: 67.0.0.*
```

## Embedded Content — applications/Agent_Red/CLAUDE.md (New Application-Scope File)

The proposed new content of `E:\GT-KB\applications\Agent_Red\CLAUDE.md` (does not yet exist; will be created at implementation time). Length ~75 lines. Explicitly bounded to Agent Red work subject per Codex Slice 1 Advisory A2.

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

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved. Created: 2026-05-28 (Slice 2 of `gtkb-claude-md-scope-clarification`).*
```

## CLAUDE-ARCHITECTURE.md Line-12 Path Fix (Move + Update)

Current state at root `CLAUDE-ARCHITECTURE.md` line 12:

```
E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\
```

New state at `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` line 12 (after move + edit):

```
E:\GT-KB\applications\Agent_Red\
```

No other content changes proposed. The full module inventory (lines 13-259) accurately describes Agent Red architecture and is preserved as-is; future Agent-Red-side updates can correct any remaining structural drift via a follow-on application-scope proposal (out of scope here).

## Non-Protected Move Operations (6 files)

For each, the operation is `git mv <root-path> applications/Agent_Red/<root-path>`. No content changes; content hash preserved through move.

1. `CONTRIBUTING.md` → `applications/Agent_Red/CONTRIBUTING.md`
2. `CHANGELOG.md` → `applications/Agent_Red/CHANGELOG.md`
3. `SECURITY.md` → `applications/Agent_Red/SECURITY.md`
4. `CLAUDE-REFERENCE.md` → `applications/Agent_Red/CLAUDE-REFERENCE.md` (root is protected; delete needs approval packet; new location is not protected; content preserved verbatim)
5. `CLAUDE_ARCHIVE.md` → `applications/Agent_Red/CLAUDE_ARCHIVE.md` (2293 lines; content preserved verbatim)
6. `CLAUDE-ARCHITECTURE.md` → `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` (with line-12 path fix per above; root is protected; delete needs approval packet)

## Approval-Packet Plan (3 Packets)

Per `config/governance/narrative-artifact-approval.toml`, 3 packets required:

### Packet 1: Root CLAUDE.md update

- Path: `.groundtruth/formal-artifact-approvals/2026-05-28-claude-md-platform-split.json`
- artifact_type: `narrative_artifact`
- artifact_id: `claude-md-platform-split-2026-05-28`
- action: `update`
- target_path: `CLAUDE.md`
- source_ref: `bridge/gtkb-claude-md-scope-clarification-slice-2-001.md`
- full_content: (full text of new platform CLAUDE.md as embedded above)
- full_content_sha256: (computed at implementation time from LF-normalized full_content)
- approval_mode: `approve`
- presented_to_user: `true`
- transcript_captured: `true`
- explicit_change_request: "Owner AUQ this session 2026-05-28: 'C: Split (recommended)' + 'Expand Slice 2 to 18.I scope'"
- changed_by: `prime-builder/claude-code-opus-4-7`
- change_reason: "Slice 2 of gtkb-claude-md-scope-clarification (Codex GO at scoping -002); 18.I sub-slice of ISOLATION-018 umbrella"

### Packet 2: Root CLAUDE-REFERENCE.md delete

- Path: `.groundtruth/formal-artifact-approvals/2026-05-28-claude-reference-md-delete-from-root.json`
- artifact_id: `claude-reference-md-delete-2026-05-28`
- action: `delete`
- target_path: `CLAUDE-REFERENCE.md`
- source_ref: same
- full_content: (empty; delete action) OR (current file content for audit trail; implementation determines per packet schema)
- approval_mode: `approve`
- presented_to_user: `true`
- transcript_captured: `true`
- explicit_change_request: same as Packet 1
- change_reason: "Slice 2 of gtkb-claude-md-scope-clarification; Agent Red reference file moves to applications/Agent_Red/CLAUDE-REFERENCE.md per ADR-ISOLATION-APPLICATION-PLACEMENT-001"

### Packet 3: Root CLAUDE-ARCHITECTURE.md delete

- Path: `.groundtruth/formal-artifact-approvals/2026-05-28-claude-architecture-md-delete-from-root.json`
- artifact_id: `claude-architecture-md-delete-2026-05-28`
- action: `delete`
- target_path: `CLAUDE-ARCHITECTURE.md`
- source_ref: same
- approval_mode: `approve`
- presented_to_user: `true`
- transcript_captured: `true`
- explicit_change_request: same as Packet 1
- change_reason: "Slice 2 of gtkb-claude-md-scope-clarification; Agent Red architecture file moves to applications/Agent_Red/CLAUDE-ARCHITECTURE.md (with line-12 path fix from obsolete E:\\Claude-Playground to E:\\GT-KB\\applications\\Agent_Red)"

## Bridge Index Entry

This NEW proposal is filed under `bridge/` with an INDEX update that inserts the document entry at the top of `bridge/INDEX.md` per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. No prior versions exist for this thread; no deletion or rewrite of prior versions occurs. INDEX entry inserted: `Document: gtkb-claude-md-scope-clarification-slice-2` followed by `NEW: bridge/gtkb-claude-md-scope-clarification-slice-2-001.md`, inserted immediately after the header comments per the protocol's newest-first convention.

## target_paths

- `CLAUDE.md` (update; protected; packet 1)
- `CLAUDE-REFERENCE.md` (delete; protected; packet 2)
- `CLAUDE-ARCHITECTURE.md` (delete; protected; packet 3)
- `applications/Agent_Red/CLAUDE.md` (create; not protected; no packet)
- `applications/Agent_Red/CLAUDE-REFERENCE.md` (create; not protected; no packet)
- `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` (create with line-12 fix; not protected; no packet)
- `applications/Agent_Red/CONTRIBUTING.md` (create via git mv; not protected)
- `applications/Agent_Red/CHANGELOG.md` (create via git mv; not protected)
- `applications/Agent_Red/SECURITY.md` (create via git mv; not protected)
- `applications/Agent_Red/CLAUDE_ARCHIVE.md` (create via git mv; not protected)
- `CONTRIBUTING.md` (delete via git mv; not protected)
- `CHANGELOG.md` (delete via git mv; not protected)
- `SECURITY.md` (delete via git mv; not protected)
- `CLAUDE_ARCHIVE.md` (delete via git mv; not protected)
- `.groundtruth/formal-artifact-approvals/2026-05-28-claude-md-platform-split.json` (create)
- `.groundtruth/formal-artifact-approvals/2026-05-28-claude-reference-md-delete-from-root.json` (create)
- `.groundtruth/formal-artifact-approvals/2026-05-28-claude-architecture-md-delete-from-root.json` (create)

## Specification-Derived Verification Plan

Implementation verification at the post-implementation report stage. Per Codex Slice 1 Conditions 4-5:

| Spec / clause | Executed verification evidence |
|---|---|
| `GOV-01` (≤300 lines) | `wc -l CLAUDE.md` returns ≤300 after Slice 2 implementation. Expected: ~260 lines. |
| `canonical-terminology.toml dual-agent profile` (required_files + required_startup_terms) | New CLAUDE.md contains MemBase, Deliberation Archive, MEMORY.md, Prime Builder, Loyal Opposition (verified via grep). |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | This Slice 2 INDEX entry committed; no prior bridge file deletions; per-thread version chains intact. |
| `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` | 3 approval packets generated with correct content hashes; pre-commit `scripts/check_narrative_artifact_evidence.py --staged` passes for staged narrative-artifact paths. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` + `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | All new app-side files land under `applications/Agent_Red/`. |
| Cross-reference preservation (Codex Slice 1 Condition 5) | Grep results before/after for CLAUDE.md anchors in `.claude/rules/`, `AGENTS.md`, `bridge/`, `memory/` show no broken references. CLAUDE.md continues to exist at root for `canonical-terminology.toml` `required_files` contract. `operating-model.md:107` anchor preserved. `peer-solution-advisory-loop.md:78` protected-paths reference preserved. `canonical-terminology.md:1328` GOV-06 anchor preserved (Governance Index table kept in new platform CLAUDE.md). |
| Application-scope-bound preamble (Codex Slice 1 Advisory A2) | New `applications/Agent_Red/CLAUDE.md` carries the explicit "consulted only when work subject is application and named application is Agent Red" preamble; declares "NOT platform authority". |
| Advisory specs carry-forward (Codex Slice 1 Advisory A1) | Specification Links above cites `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. |

## Requirement Sufficiency

Existing requirements sufficient. No new specifications need to be authored. This proposal operationalizes existing canonical artifacts:

- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` (owner-approved governance establishing Agent Red placement)
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (source deliberation)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (placement convention)
- ISOLATION-018 umbrella `-008` 18.I plan (now withdrawn but disposition matrix carries forward)
- AGENTS.md line 11 default-to-GT-KB framing (symmetrizing for Claude side)
- Slice 1 Codex GO at `-002` (approves scoping direction)
- Two owner AUQ answers this session (Approach C + 18.I scope expansion)

## Risk / Rollback

- **Risk**: Approval-packet content hash mismatch at write time. Mitigation: compute SHA-256 from final LF-normalized content before staging; verify packet `full_content_sha256` matches before commit.
- **Risk**: Doctor `dual-agent` profile fails if new CLAUDE.md omits any required_startup_term. Mitigation: grep verification at post-impl step explicitly checks for MemBase, Deliberation Archive, MEMORY.md, Prime Builder, Loyal Opposition.
- **Risk**: Cross-references to specific CLAUDE.md section anchors break if heading text differs. Mitigation: new platform CLAUDE.md preserves the heading wording of all sections being kept; specifically preserves "### Governance Index" (referenced by canonical-terminology.md:1328 GOV-06).
- **Risk**: `applications/Agent_Red/CLAUDE.md` consumed by an active Agent Red work-subject session before the loader knows about it. Mitigation: this proposal explicitly notes the file is documentation, not yet auto-loaded; auto-load mechanism is a future-work follow-on slice (separate bridge thread).
- **Rollback**: `git restore CLAUDE.md CLAUDE-REFERENCE.md CLAUDE-ARCHITECTURE.md CONTRIBUTING.md CHANGELOG.md SECURITY.md CLAUDE_ARCHIVE.md` reverts root deletions; `rm -rf applications/Agent_Red/{CLAUDE.md,CLAUDE-REFERENCE.md,CLAUDE-ARCHITECTURE.md,CONTRIBUTING.md,CHANGELOG.md,SECURITY.md,CLAUDE_ARCHIVE.md}` removes new app-side files (depending on which exist post-mutation); remove approval packets at `.groundtruth/formal-artifact-approvals/2026-05-28-*.json`.

## Follow-On Slices (Documented; Not in Scope for Slice 2)

Subsequent slices remain available per the Slice 1 scoping documentation:
- **Slice 3** — CLAUDE-REFERENCE.md content scope review (the content itself; this Slice 2 only moves it). Out of scope here; the moved file content is preserved verbatim.
- **Slice 4** — CLAUDE-ARCHITECTURE.md rewrite for current GT-KB / Agent Red structure (beyond the line-12 path fix). Out of scope here.
- **Slice 5** — `applications/` directory hygiene: ~95 `_test_*` rehearsal-artifact directories cleanup.
- **Future** — Auto-load mechanism for `applications/<name>/CLAUDE.md` when work subject is `application`.
- **Future** — ISOLATION-018 sub-slices 18.J (repo separation) and 18.L (verification) per the WITHDRAWN umbrella plan.

## Owner Action Required

Owner AUQ already answered for the Slice 2 scope (Approach C + 18.I expansion). No additional owner AUQ required for Slice 2 Codex review.

After Codex GO:
1. Owner reviews + presents formal-artifact-approval packets via AskUserQuestion (one per protected mutation).
2. Prime Builder writes the new content, performs git mv operations, generates approval packets at `.groundtruth/formal-artifact-approvals/`.
3. Prime Builder runs verification per the Specification-Derived Verification Plan.
4. Prime Builder files a post-implementation report at version `-NNN` for Codex VERIFIED review.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
