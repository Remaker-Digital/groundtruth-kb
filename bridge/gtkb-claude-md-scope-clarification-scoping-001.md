NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 39611c3e-b51e-43f1-aa37-5ec4be3894b0
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

# GT-KB CLAUDE.md Scope Clarification - Scoping - 001

bridge_kind: governance_advisory

Document: gtkb-claude-md-scope-clarification-scoping
Version: 001 (NEW; scoping proposal)
Date: 2026-05-28 UTC

## Claim

CLAUDE.md at the GT-KB project root (`E:\GT-KB\CLAUDE.md`) ambiguously conflates application-scoped guidance (Agent Red branching, deployment, commercial features, hotfix workflow) with platform-scoped guidance (GT-KB governance, bridge protocol, artifact discipline). Per the canonical operating-model and canonical-terminology, the default work subject is GT-KB infrastructure and an "application" (e.g., Agent Red) is a lifecycle object managed by the GT-KB platform — they are distinct subjects with distinct lifecycles. Today's CLAUDE.md presents Agent Red as if it were the project being managed, causing application-scoped sections to be misapplied to GT-KB platform work.

The owner stated this ambiguity directly in this session (paraphrased): "CLAUDE.md refers to the application (e.g., Agent Red) and the GT-KB host supporting that application in a production environment. It does not apply to our work when the subject is GT-KB itself. Please propose a correction of this ambiguity and inspect relevant artifacts for contradictions or contention."

This is a `governance_review` scoping proposal. It catalogs the ambiguity, enumerates contradictions across narrative artifacts, proposes alternative structural approaches with trade-offs, and requests owner approach-selection AUQ as the gate to Slice 2 implementation. No narrative-artifact mutations are proposed in this scoping slice.

## Bridge Index Entry

This NEW proposal is filed under `bridge/` with an INDEX update that inserts the document entry at the top of `bridge/INDEX.md` per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. No prior versions exist for this thread; no deletion or rewrite of prior versions occurs. INDEX entry: `Document: gtkb-claude-md-scope-clarification-scoping` followed by `NEW: bridge/gtkb-claude-md-scope-clarification-scoping-001.md`, inserted immediately after the header comments per the protocol's newest-first convention.

## Specification Links

- `GOV-01` — CLAUDE.md MUST NOT exceed 300 lines (current file is 301 lines per `wc -l`; sub-violation flagged below).
- `GOV-08` — KB is truth; narrative artifacts are the permitted-markdown exception.
- `GOV-09` — Owner input classification (specification language triggers spec-first workflow).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority; this proposal is filed via the bridge protocol and respects its statuses.
- `GOV-ARTIFACT-APPROVAL-001` — Slice 2 implementation requires formal-artifact-approval packets for narrative-artifact mutations.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact mutation gate (PreToolUse Write).
- `DCL-CONCEPT-ON-CONTACT-001` — load-bearing concepts surfaced on first contact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every bridge proposal must cite governing specs; this Specification Links section satisfies the linkage requirement for Slice 1, and Slice 2 implementation will carry the linkage forward with concrete file-touchpoint citations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Slice 2 verification will require spec-derived tests/checks for the narrative-artifact mutations (see Specification-Derived Verification Plan below). Slice 1 is a governance_review with no source mutation requiring tests; the verification plan applies on transition to Slice 2.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `applications/<name>/` placement convention for application files.
- `ADR-0001` — Three-Tier Memory Architecture (MemBase / MEMORY.md / Deliberation Archive).
- `.claude/rules/operating-model.md` §1 (operating model narrative) and §2 (canonical terminology with allowed synonyms and forbidden uses).
- `.claude/rules/canonical-terminology.md` (active glossary; application / platform / hosted application / adopter entries).
- `.claude/rules/project-root-boundary.md` (Agent Red as separate project; `applications/` placement for demo applications).
- `.claude/rules/file-bridge-protocol.md` (scoping-then-implementation pattern; `bridge_kind: governance_review` exemption).
- `AGENTS.md` line 11 (default-to-GT-KB framing already established for Codex side).

## Owner Decisions / Input

This proposal is owner-approval-dependent. Source evidence:

- Owner directive this session, paraphrased: "CLAUDE.md refers to the application (e.g., Agent Red) and the GT-KB host supporting that application in a production environment. It does not apply to our work when the subject is GT-KB itself. Please propose a correction of this ambiguity and inspect relevant artifacts for contradictions or contention."
- No prior AUQ-recorded decision on CLAUDE.md scope structure exists; this proposal is the scoping artifact that gathers the structural-approach question for owner AUQ.

The Slice 1 (this proposal) deliverable is the scoping content + alternatives. Approach selection via AskUserQuestion is the gate to Slice 2 implementation. Slice 2 narrative-artifact writes will additionally require formal-artifact-approval packets at `.groundtruth/formal-artifact-approvals/` matching the final content hash.

## Prior Deliberations

- `DELIB-0877` — owner-decision: industry-alignment critique for GT-KB/application separation. Key claims: "Application-subject sessions must be unable, by default, to alter GT-KB product artifacts. GT-KB-subject sessions may retain broader authority where needed for release engineering, adopter validation, and migration work. The isolation plan therefore needs an asymmetric safety model."
- `DELIB-0785` — GT-KB has its own release-readiness lifecycle, separate from Agent Red production readiness.
- `DELIB-0834` — Agent Red as fully conformant application sustained by GT-KB (not an ad-hoc exception).
- `DELIB-0023` — Membase / Agent Red coupling source-of-truth problem; reusable platform work must move upstream and Agent Red becomes downstream consumer + proving ground.
- `DELIB-0876` — durable work subject; initial `work subject application` / `work subject GT-KB` proposal.
- `DELIB-0501` — Agent Red Large-Scale Commercial Production Plan (origin of CLAUDE.md's application-focused framing).
- `DELIB-0327` — Hotfix / WIP Coexistence Operating Model (origin of CLAUDE.md's branching strategy section).
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` — lifecycle independence; placement-over-coercion design principle.

## Ambiguity Locus in CLAUDE.md

CLAUDE.md is 301 lines (current head). Line refs below from that revision.

| Line(s) | Section | Current scope | Defect |
|---|---|---|---|
| 1 | Title | `# CLAUDE.md - Agent Red Customer Experience` | Title encodes application-only scope; misleads when work subject is GT-KB. |
| 3 | First-line declaration | "This document provides active guidance for AI assistants working on the Agent Red Customer Experience commercial project." | Same — implicitly defaults all guidance to Agent Red. |
| 1 (rule cite) | GOV-01 reference | "GOV-01: This file MUST NOT exceed 300 lines." | File is 301 lines — sub-violation of its own stated cap. |
| ~38-43 | Application Identity table | Agent Red as the application; type "Commercial SaaS Product"; owner Remaker Digital | Presents Agent Red as if it IS the project being managed. No platform identity present. |
| ~47-51 | Copyright Notice | Required on "all new work in this repository"; copyright is Agent Red commercial | Universal copyright requirement misapplies Agent Red commercial copyright to GT-KB platform code. |
| ~213-218 | Adding Commercial Features | "Create features in `src/`"; "Add copyright notice"; "Never commit AGNTCY source"; "Read AGNTCY from public repo" | Explicitly Agent Red commercial-feature workflow; not applicable to GT-KB platform features. |
| ~223-237 | Branching Strategy | develop → staging → main as production for "Agent Red" | Application deployment cycle; GT-KB platform releases (PyPI `groundtruth-kb` package) are a separate cycle not documented here. |
| ~234 | Production deploy question | "Before you deploy any build, ask this question: Is Agent Red ready for a full production deployment?" | Per-application gating question, not universal. GT-KB has its own release-readiness criteria (per `DELIB-0785`). |
| ~244-254 | Hotfix Workflow | Agent Red emergency patches; hotfix branch from main at production tag | Application emergency-deployment workflow; not applicable to GT-KB platform hotfixes. |

## Contradictions Across Related Artifacts

1. **AGENTS.md line 11 vs CLAUDE.md silence on default scope.** AGENTS.md (Codex side) states: "Unless Mike explicitly says the session is Agent Red work, assume active work is GroundTruth-KB." CLAUDE.md has no equivalent and implicitly defaults to Agent Red. This is the most direct contradiction — sibling narrative artifacts giving conflicting default-scope signals to two harnesses.

2. **`.claude/rules/operating-model.md` §1 vs CLAUDE.md "Application Identity".** Operating-model says: "GT-KB is both the platform and the active application, but the same application/project distinction applies." CLAUDE.md collapses the distinction by presenting only Agent Red identity.

3. **`.claude/rules/canonical-terminology.md` (Agent Red entry) vs CLAUDE.md title.** Canonical terminology says Agent Red is a separate project. CLAUDE.md title presents Agent Red as if it IS the project at this repo root.

4. **`.claude/rules/project-root-boundary.md` vs CLAUDE.md "Branching Strategy".** Project-root-boundary says Agent Red's separate repository is `https://github.com/mike-remakerdigital/agent-red`. CLAUDE.md's branching strategy section reads as if Agent Red lives in this repo (`E:\GT-KB`), describing develop → main as the Agent Red deployment cycle.

5. **GOV-01 self-reference vs file length.** CLAUDE.md line 1 cites GOV-01 (≤300 lines) while the file is 301 lines.

6. **CLAUDE-ARCHITECTURE.md line 12 vs project-root-boundary.md.** CLAUDE-ARCHITECTURE.md references the obsolete path `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement\` as the project root. Project-root-boundary.md explicitly states `E:\Claude-Playground` is archive-only. The entire CLAUDE-ARCHITECTURE.md module inventory describes the pre-migration Agent Red repo, not the current GT-KB structure.

7. **CLAUDE-REFERENCE.md content scope vs location.** CLAUDE-REFERENCE.md line 19-34 is entirely application-scoped (Agent Red legal, AGNTCY rules, IP separation). It correctly identifies as application reference material but is located at the platform root, contributing to the same root-level conflation as CLAUDE.md.

8. **`applications/Agent_Red/` exists with real Agent Red structure** (admin, branding, config, docs, src, tests, widget) — i.e., Agent Red HAS been migrated under the canonical `applications/` placement. Yet CLAUDE.md continues to treat the platform root as Agent Red's home.

9. **`applications/` directory hygiene defect** (related but separate): ~95 `_test_*` artifact directories under `applications/` from rehearsal/scaffold tests. Out of scope for this proposal; flagged as hygiene follow-on.

## Proposed Correction Approaches (Slice 1 Scoping; Slice 2 Implements Selected)

### Approach A — Default-GT-KB CLAUDE.md + scope-marker convention + new `applications/Agent_Red/CLAUDE.md`

- CLAUDE.md is rewritten to default scope to GT-KB platform work. Title becomes `# CLAUDE.md — GroundTruth-KB Platform`. First-line declaration cites the default-to-GT-KB framing mirroring AGENTS.md line 11.
- Application-deployment-cycle sections (Branching Strategy, Hotfix Workflow, Adding Commercial Features, "Deploy: Is Agent Red Ready?" question) move to a new `applications/Agent_Red/CLAUDE.md` (does not yet exist).
- Sections in CLAUDE.md that apply to BOTH platform and application work (Roles, Artifacts, Governance Index, Three Interdependent Artifacts, Working with This Project, Knowledge Database Access, Deliberation Archive Protocol, Session Wrap-Up) remain in CLAUDE.md unchanged or lightly annotated.
- Trade-off: cleanest separation; aligns with project-root-boundary.md `applications/` placement; matches AGENTS.md framing; brings CLAUDE.md under GOV-01 cap.

### Approach B — Single-file CLAUDE.md with `[Applies to: …]` per-section scope markers

- Keep CLAUDE.md as one file.
- Add explicit `[Applies to: Platform]`, `[Applies to: Application]`, or `[Applies to: Both]` markers on every section heading.
- Add an "Active Scope" preamble explaining the marker convention.
- Trade-off: less disruptive; no new file. Does NOT solve GOV-01 300-line cap (line count grows due to markers + preamble). Scope discipline depends on author/reader honoring markers; no mechanical enforcement.

### Approach C — Split: platform CLAUDE.md (rewrite) + new `applications/Agent_Red/CLAUDE.md` (move app content)

- Rewrite CLAUDE.md content to be platform-only (Roles, governance, bridge protocol, artifact discipline, work-subject framing matching AGENTS.md). New length comfortably under 300 lines.
- Move application-deployment, copyright, commercial-feature, and branching-strategy content to a new `applications/Agent_Red/CLAUDE.md` (does not yet exist). When the work subject is `application` and the named application is Agent Red, that file is loaded.
- Trade-off: cleanest structural separation; eliminates scope-marker dependency; matches `DELIB-0877` asymmetric safety model. Most disruptive (two new authoring artifacts); both need formal-artifact-approval packets at Slice 2.

### Approach D — Defer to broader CLAUDE-*.md triad proposal

- Defer scope clarification of CLAUDE.md until a broader proposal addresses CLAUDE.md + CLAUDE-REFERENCE.md + CLAUDE-ARCHITECTURE.md + CLAUDE_ARCHIVE.md together, plus the `applications/` hygiene defect.
- Trade-off: comprehensive single review cycle; risks bundling unrelated changes (violates `.claude/rules/bridge-essential.md` scoped-commits-only rule); longer time to resolution of the specific ambiguity the owner flagged.

### Recommendation: Approach C

Rationale: (1) Cleanest mapping to the canonical operating-model and project-root-boundary distinctions. (2) Eliminates ambiguity at the structural level instead of relying on scope markers being followed. (3) Brings CLAUDE.md under the GOV-01 300-line cap by reducing scope. (4) Matches AGENTS.md's already-correct default-to-GT-KB framing for symmetry. (5) Aligns with the `DELIB-0877` asymmetric safety model: application-subject sessions read `applications/Agent_Red/CLAUDE.md`; platform-subject sessions read `CLAUDE.md`. (6) Sets precedent for future adopter applications under `applications/<name>/CLAUDE.md`.

Approach A is the runner-up if owner prefers a smaller-blast-radius first step (keeps existing CLAUDE.md mostly intact, only carves out the explicitly-application sections).

## Follow-On Slices (Documented; Not in Scope for Slice 1 or Slice 2)

- **Slice 2 (immediate next; this thread)** — apply selected approach to CLAUDE.md (+ new `applications/Agent_Red/CLAUDE.md` if A or C). Implementation proposal with target_paths, formal-artifact-approval packets, narrative-artifact pre-commit gate verification.
- **Slice 3 (separate thread)** — CLAUDE-REFERENCE.md scope review and relocation/scope-marking (application-only content currently at platform root).
- **Slice 4 (separate thread)** — CLAUDE-ARCHITECTURE.md rewrite for current GT-KB structure (line 12 path obsolete; full module inventory stale).
- **Slice 5 (separate thread)** — `applications/` directory hygiene: ~95 `_test_*` rehearsal-artifact directories cleanup; `.gitignore` or test-isolation patches.

## Specification-Derived Verification Plan

Slice 1 is a scoping/governance-review slice. No source/test/config mutations. Verification:
- Bridge applicability preflight passes (`scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-md-scope-clarification-scoping-001`) with `missing_required_specs: []`.
- Clause preflight passes (`scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-md-scope-clarification-scoping-001`) with no blocking gaps.
- Codex review issues GO/NO-GO based on the inventoried ambiguity, contradictions, and approach trade-offs.

Slice 2 (implementation) verification will additionally include:
- New CLAUDE.md compliance with GOV-01 (≤300 lines), verified by `wc -l`.
- New CLAUDE.md formal-artifact-approval packet hash-match (`full_content_sha256` equals computed LF-normalized hash).
- New `applications/Agent_Red/CLAUDE.md` formal-artifact-approval packet hash-match (Approach A or C).
- Pre-commit `scripts/check_narrative_artifact_evidence.py --staged` passes on staged narrative-artifact paths.
- Cross-references to CLAUDE.md from `.claude/rules/operating-model.md`, `AGENTS.md`, `.claude/rules/project-root-boundary.md`, `.claude/rules/file-bridge-protocol.md`, and any other rule files remain resolvable.

## target_paths

Slice 1 (this proposal — governance_review): no implementation files; no target_paths required per `bridge_kind` exemption.

Slice 2 (implementation; tracked here for transparency only):
- `CLAUDE.md` (rewrite)
- `applications/Agent_Red/CLAUDE.md` (new; if Approach A or C selected)
- `.groundtruth/formal-artifact-approvals/<date>-claude-md-scope-correction.json` (new packet)
- `.groundtruth/formal-artifact-approvals/<date>-applications-agent-red-claude-md.json` (new packet; if A or C)

## Requirement Sufficiency

Existing requirements sufficient. The work derives from:
- Owner directive this session (paraphrased above).
- `.claude/rules/operating-model.md` §1 + §2 (canonical operating-model + canonical terminology already established).
- `.claude/rules/canonical-terminology.md` (Agent Red, application, platform, hosted application, adopter entries already canonical).
- `DELIB-0877`, `DELIB-0785`, `DELIB-0834`, `DELIB-0023`, `DELIB-0876` (deliberation-archive evidence already canonical).
- `AGENTS.md` line 11 default-to-GT-KB framing (already canonical for Codex side; symmetrizing for Claude side requires no new spec, only operationalization of the existing default).

No new requirements need to be authored; this proposal operationalizes existing canonical specifications for the CLAUDE.md surface.

## Risk / Rollback

- **Risk (Slice 1)**: None substantive — governance_review only; no mutations.
- **Risk (Slice 2)**: Narrative-artifact write requires formal-artifact-approval packet; mismatch causes pre-commit narrative-evidence gate failure. Mitigation: compute packet hash from final LF-normalized content before staging; verify `full_content_sha256` field matches.
- **Risk (Slice 2)**: Cross-references to CLAUDE.md from rule files may break if section anchors change. Mitigation: pre-Slice-2 grep for CLAUDE.md anchors across `.claude/rules/`, `AGENTS.md`, `bridge/`, `memory/` and update or preserve anchors as part of the same commit.
- **Rollback (Slice 1)**: `git restore` the bridge file and INDEX entry; no DB mutations occur.
- **Rollback (Slice 2)**: `git restore` CLAUDE.md and `applications/Agent_Red/CLAUDE.md` (if newly created); remove the approval-packet files.

## Owner Action Required

After Codex GO on this scoping proposal, the owner is asked via AskUserQuestion to select the structural approach:

- **A**: Default-GT-KB CLAUDE.md + scope markers + new `applications/Agent_Red/CLAUDE.md` (carve-out).
- **B**: Single-file CLAUDE.md with per-section `[Applies to: …]` markers.
- **C** (Prime Builder recommendation): Split — rewrite CLAUDE.md as platform-only + new `applications/Agent_Red/CLAUDE.md` for app content.
- **D**: Defer to broader CLAUDE-*.md triad proposal.

Selection authorizes Slice 2 implementation proposal authoring.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
