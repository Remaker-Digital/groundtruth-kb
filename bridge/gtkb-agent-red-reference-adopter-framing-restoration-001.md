NEW

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: claude-code-2026-05-24-agent-red-framing-remediation
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: reasoning=high; mode=auto
author_metadata_source: Claude Code session environment

# Governance Review Proposal — Restore Agent Red Reference Adopter Framing — 001

bridge_kind: governance_advisory
Document: gtkb-agent-red-reference-adopter-framing-restoration
Version: 001
Author: Prime Builder (Claude harness B)
Date: 2026-05-24 UTC
Recommended commit type: docs:

target_paths:
- `.claude/rules/canonical-terminology.md` (Agent Red glossary entry, lines 257-273)
- `.claude/rules/project-root-boundary.md` (Agent Red clause, lines 11-14)
- `.claude/rules/loyal-opposition.md` (Mandatory Project Root Boundary subsection, lines 26-31)
- `.claude/rules/acting-prime-builder.md` (Agent Red Separate-Project Boundary subsection, lines 67-86; including subsection retitle)
- `.claude/rules/file-bridge-protocol.md` (root-boundary clause, line 16)

## Summary

Restore the canonical framing that Agent Red is the **reference adopter application** for GT-KB, with a deliberately lifecycle-independent repository and CI cadence, exercised as the active isolation validator. The implementation layer already encodes this intent. Four rule files have drifted into language that denies the adopter relationship outright; this proposal corrects the rule corpus to match owner-confirmed intent (S347) and the historical canonical framing (`GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `DELIB-0834`).

## Problem

S347 verification (this session) surfaced a load-bearing contradiction:

**Implementation layer (consistent with owner intent):**
- `CLAUDE.md` § Mandatory Project Root Boundary: "Agent Red application files MUST be within `E:\GT-KB\applications\Agent_Red\`."
- `.claude/rules/operating-model.md` §2 "application": "Examples: Agent Red, GT-KB itself (when GT-KB is the active application)."
- `applications/Agent_Red/.gtkb-app-isolation.json`: 118MB application subtree with isolation contract, validator schema, and per-artifact justification.
- `PROJECT-GTKB-ADOPTER-EXPERIENCE` + `WI-3248`: live in-flight project named "Adopter Experience" implementing the Agent Red deployability preservation gate.
- `bridge/gtkb-agent-red-deployability-preservation-gate-005.md` (NEW): partial Slice 1 of an adopter-focused gate that explicitly preserves Agent Red as the GT-KB adopter.
- `bridge/application-isolation-contract-006.md` (GO): the active isolation contract bridge thread that the `.gtkb-app-isolation.json` cites as its origin.
- Recent commit `c1021ab0 refactor(isolation): 18.E.1 atomic code cluster move (1,423 files)` (S339): the literal lifecycle-independence work moving Agent Red code from GT-KB root into the application subtree.

**Drifted rule corpus (contradicts owner intent):**

| File | Line | Quote |
|---|---|---|
| [.claude/rules/canonical-terminology.md](.claude/rules/canonical-terminology.md):261 | 261 | "A separate project, **not part of GT-KB**. Agent Red **previously** validated GT-KB during isolation work" (past tense) |
| [.claude/rules/project-root-boundary.md](.claude/rules/project-root-boundary.md):12 | 12 | "Agent Red project files **are not GT-KB files** and must not be treated as live GT-KB artifacts" |
| [.claude/rules/loyal-opposition.md](.claude/rules/loyal-opposition.md):27 | 27 | "Agent Red is a separate project, not part of GT-KB, and Agent Red files must not be used as live GT-KB artifacts" |
| [.claude/rules/acting-prime-builder.md](.claude/rules/acting-prime-builder.md):69 | 69 | "Owner correction 2026-05-04 supersedes the prior Agent Red conformance framing for current GT-KB work: Agent Red is not part of GT-KB" |
| [.claude/rules/file-bridge-protocol.md](.claude/rules/file-bridge-protocol.md):16 | 16 | "Agent Red files are not GT-KB files and must not be used as live GT-KB artifacts" |

**Root cause.** The 2026-05-04 owner correction was narrow in scope: it disallowed unqualified GT-KB tooling references (CLI, CI workflows, GitHub Actions, release evidence) from resolving silently to Agent Red repository/CI surfaces. The correction was preserved verbatim across the rule corpus in language that generalized into "Agent Red is severed from GT-KB" — a distinct and contradictory statement. The owner has confirmed (S347) that the broader statement was not provided and was not approved.

Owner-confirmed intent (S347):
1. Agent Red **is** the reference application for GT-KB.
2. Agent Red has a deliberately lifecycle-independent repository/CI cadence.
3. Agent Red **is** the isolation validator (present tense, not historical).
4. Agent Red must be portable between GT-KB installations.

## Specification Links

Required (cited as authority for this proposal):

- `.claude/rules/operating-model.md` §2 — canonical operating-model artifact defining "application" with Agent Red as an explicit example (rule-cited soft authority).
- `CLAUDE.md` § Mandatory Project Root Boundary — explicitly places Agent Red files within `applications/Agent_Red/`.
- `.claude/rules/canonical-terminology.md` — canonical glossary (target of remediation).
- `.claude/rules/project-root-boundary.md` — target of remediation.
- `.claude/rules/loyal-opposition.md` — target of remediation.
- `.claude/rules/acting-prime-builder.md` — target of remediation.
- `.claude/rules/file-bridge-protocol.md` — target of remediation (line 16).
- `GOV-ARTIFACT-APPROVAL-001` — formal artifact approval gate (governs the edits to protected narrative artifacts at implementation time).
- `PB-ARTIFACT-APPROVAL-001` — per-artifact owner approval discipline.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact-approval-gate hook contract.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` — owner-conversation corrections must enter via the spec-approval path; this proposal IS that path for the S347 correction.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage required.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification required.
- `GOV-SESSION-FORMALIZATION-AUDIT-001` — this remediation is exactly the audit class this GOV anticipates.
- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` — glossary edit affects the DA read surface; entry must remain DA-citable post-edit.
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` — glossary citations must be complete.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` — placement principle for DA-citing surfaces.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` — **the historical canonical framing this proposal restores**: Agent Red as a well-behaved, fully-conformant application supported and sustained by GroundTruth-KB.
- `DELIB-0834` — owner-decision record underlying `GOV-AGENT-RED-GTKB-CONFORMANCE-001`.

Implementation context (cited as factual evidence of the implementation layer's framing):

- `applications/Agent_Red/.gtkb-app-isolation.json` — Agent Red's live isolation declaration, citing `ADR-APPLICATION-ISOLATION-CONTRACT-001` (proposed) and `DCL-APP-ROOT-MINIMIZATION-001` (proposed).
- `bridge/application-isolation-contract-006.md` (GO) — isolation contract bridge thread.
- `bridge/gtkb-agent-red-deployability-preservation-gate-005.md` (NEW) — in-flight adopter deployability gate.
- `PROJECT-GTKB-ADOPTER-EXPERIENCE` / `WI-3248` / `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH-P0-DEPLOYABILITY-GATE`.

Out of scope (cited for awareness):
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` (v1 SCOPE clause) — covers per-cluster moves into `applications/Agent_Red/`; not modified by this proposal.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` — transient exception for current Agent Red CI binding; this proposal does not affect that exception or the v0.7.0-rc1 tag conditions.

## Prior Deliberations

Glossary-source seeds (extracted from `.claude/rules/canonical-terminology.md` Agent Red entry §"Source" plus the "isolation" entry §"Source"):

- `DELIB-S324-OM-DELTA-0003-CHOICE` — application/project/platform/hosted-application terminology decision (S324). Established Agent Red as an "application" example under the GT-KB operating model.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` (S319, 2026-04-28) — owner-verbatim lifecycle-independence contract that motivates the application-isolation work; Agent Red is the concrete subject.
- `DELIB-0877` (2026-04-22) — industry-alignment critique that frames adopter independence.
- `DELIB-0879` — `GTKB-ISOLATION-002` topology plan (2026-04-22).
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` — S331 owner clarification: ZIP-portability test for isolation; scope-bound write enforcement. Agent Red is the implicit subject.
- `DELIB-S321 owner directive: platform app non specific` — S321 clarification that the platform must not be application-specific (the adopter side of the same coin).

Owner-decision record from this session (to be captured at session wrap):

- **S347 owner direction** (2026-05-24, this conversation): Agent Red is the reference application; lifecycle-independent; isolation validator; portable between GT-KB installations. Remediation of rule-corpus drift authorized.

Semantic search candidates worth review:

- DA records around the 2026-05-04 owner correction — specifically the deliberation that captured the narrowing intent (if one exists separate from the rule-corpus edits). The verbatim correction is preserved in `acting-prime-builder.md` §"Agent Red Separate-Project Boundary"; the underlying owner-decision deliberation should be cross-referenced if it exists or captured if it does not.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` v1 — defines the SCOPE clause that covers per-cluster moves into `applications/Agent_Red/`. Relevant context for the implementation layer.

## Owner Decisions / Input

The remediation is authorized by three explicit owner statements in S347 (this session):

1. **Owner restated intent** (S347 turn 1, owner message):
   > "The intent is for Agent Red to be the reference application for GT-KB. It is a separate project, in the sense that it has a lifecycle that is deliberately not synchronized with GT-KB. It is the isolation validator: Agent Red must be portable between GT-KB installations. This is not a new requirement or use case."

2. **Owner identified the source of confusion** (S347 turn 1, owner message):
   > "I believe that there is some ongoing confusion about terms and intent. Can you verify that the current implementation matches this intent?"

3. **Owner authorized this remediation** (S347 turn 2, owner message):
   > "Yes. You have discovered ambiguity and inconsistency that we need to correct. Some GOV and specifications contain language that I did not provide or explicitly approve. I believe that we previously had gaps in mechanical enforcement that allowed contradictory or confusing language in specifications and directives. This is a prime example, but there may be other topics or areas of concern which are also contaminated. Please propose a remediation for this specific issue. We will then consider how to cleanse the project of historical artifacts that are potentially harmful."

**Authorization scope.** This proposal only. The owner's "we will then consider how to cleanse the project of historical artifacts" is explicitly DEFERRED to follow-up work and is NOT authorized by this proposal.

**Per-file approval packets.** Each rule-file edit will require its own `formal-artifact-approval-packet` per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`, collected at implementation time (not pre-bundled here). The packets are author-side gating for the narrative-artifact-approval-gate hook; they do not substitute for the bridge GO.

**Out-of-scope owner decisions.** No new owner AskUserQuestion is required for this proposal. The S347 conversation constitutes sufficient authorization for the bounded rule-corpus correction described in § Proposed Changes. Implementation-time per-artifact packets are author/owner ceremony, not new bridge-level decisions.

## Proposed Changes

The structure of each change is: file → current text → proposed text → rationale. All proposed text uses British/American-neutral GT-KB house style consistent with the existing rule corpus.

### Change 1 — canonical-terminology.md § Agent Red entry (lines 257-273)

**Current text (verbatim):**

> ### Agent Red
>
> **Canonical full name:** Agent Red Customer Experience.
>
> **Definition:** A separate project, not part of GT-KB. Agent Red previously
> validated GT-KB during isolation work, but unqualified GT-KB references must not
> resolve to Agent Red files, CI, GitHub Actions, or repository state.
>
> **Configured GitHub repository URLs (canonical-migration window in effect):**
>
> - **Current canonical:** `https://github.com/mike-remakerdigital/agent-red`. ...
> - **Migration target (de facto under transient exception):** ...
>
> When the canonical migration completes, the migration-target URL becomes the sole canonical and this entry is updated to remove the dual listing.
>
> **Not to be confused with:** the four small demo applications included with
> GT-KB, or with the GroundTruth-KB platform repository
> `https://github.com/Remaker-Digital/groundtruth-kb`.
>
> **Source:** owner correction, 2026-05-04; dual-repo clarification per S333 audit FINDING-P1-002 (downgraded to P3) and `bridge/gtkb-governance-hygiene-bundle-001.md` Change E.

**Proposed text:**

> ### Agent Red
>
> **Canonical full name:** Agent Red Customer Experience.
>
> **Definition:** The reference adopter application for GT-KB. Agent Red exercises the platform's application-isolation contract in continuous use through a deliberately lifecycle-independent repository and CI cadence. The application subtree lives at `applications/Agent_Red/` per `CLAUDE.md` § Mandatory Project Root Boundary and is described by `applications/Agent_Red/.gtkb-app-isolation.json`. The hosted form deploys from a lifecycle-independent repository (see "Configured GitHub repository URLs" below).
>
> **Role in GT-KB.** Agent Red is the isolation validator: portability of Agent Red between GT-KB installations is the operative test of the platform/application isolation contract (`ADR-APPLICATION-ISOLATION-CONTRACT-001` proposed; `DCL-APP-ROOT-MINIMIZATION-001` proposed; `applications/Agent_Red/.gtkb-app-isolation.json`). Active adopter-experience work tracks under `PROJECT-GTKB-ADOPTER-EXPERIENCE` (e.g., the Agent Red deployability preservation gate at `bridge/gtkb-agent-red-deployability-preservation-gate-*`).
>
> **Tooling-reference discipline (2026-05-04 narrowing).** Unqualified GT-KB tooling references — CLI invocations, CI workflows, GitHub Actions, release evidence, repository state — must not resolve silently to Agent Red surfaces. Agent Red surfaces are addressed explicitly when in scope (e.g., adopter-experience work, isolation validation, Agent Red CI binding). The narrowing scopes tooling-reference resolution; it does not alter Agent Red's role as the reference adopter application or the isolation validator.
>
> **Configured GitHub repository URLs (canonical-migration window in effect):**
>
> - **Current canonical:** `https://github.com/mike-remakerdigital/agent-red`. This is the repository whose contents are the canonical Agent Red truth at the time of writing.
> - **Migration target (de facto under transient exception):** `https://github.com/Remaker-Digital/agent-red-customer-engagement`. Agent Red CI evidence is currently captured against this repository under the transient exception in `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` while the canonical migration completes. The exception is evidence-scoped and does NOT authorize the GT-KB `v0.7.0-rc1` tag until canonical migration and canonical CI binding are complete.
>
> When the canonical migration completes, the migration-target URL becomes the sole canonical and this entry is updated to remove the dual listing.
>
> **Not to be confused with:** the four small demo applications included with GT-KB (those are scaffolded examples, not the reference adopter); the GroundTruth-KB platform repository `https://github.com/Remaker-Digital/groundtruth-kb` (the platform that manages Agent Red as its reference adopter); a deployed Agent Red instance running in service (that is a "hosted application" — Agent Red's hosted form). Separate-repository topology is the *mechanism* of lifecycle independence; it should not be misread as severance from GT-KB.
>
> **Source:** `GOV-AGENT-RED-GTKB-CONFORMANCE-001`; `DELIB-0834`; owner directive 2026-05-04 (tooling-reference narrowing); owner-decision capture S347 (2026-05-24, reference-adopter framing restoration); dual-repo clarification per S333 audit FINDING-P1-002 (downgraded to P3) and `bridge/gtkb-governance-hygiene-bundle-001.md` Change E.

**Rationale.** Restores reference-adopter framing without losing the 2026-05-04 narrowing or the dual-repo clarification. Adds an explicit "Role in GT-KB" subsection citing the active implementation surfaces. Reframes the "Not to be confused with" line to address the actual confusion (severance misreading of separate-repository topology). Adds S347 to the Source line.

### Change 2 — project-root-boundary.md (lines 11-14)

**Current text (verbatim):**

> - Agent Red project files are not GT-KB files and must not be treated as live
>   GT-KB artifacts. Agent Red's separate repository is
>   `https://github.com/mike-remakerdigital/agent-red`.

**Proposed text:**

> - Agent Red is the reference adopter application for GT-KB. Its application files live at `E:\GT-KB\applications\Agent_Red\` per `CLAUDE.md` § Mandatory Project Root Boundary, governed by the isolation contract at `applications/Agent_Red/.gtkb-app-isolation.json`. The hosted form deploys from a lifecycle-independent repository at `https://github.com/mike-remakerdigital/agent-red`. Unqualified GT-KB tooling references (CLI, CI workflows, GitHub Actions, release evidence) must not resolve silently to Agent Red repository or CI surfaces — Agent Red surfaces are addressed explicitly when in scope.

**Rationale.** Replaces severance language with reference-adopter framing while preserving the narrower correct rule about tooling-reference resolution.

### Change 3 — loyal-opposition.md (lines 26-31)

**Current text (verbatim):**

> All active GT-KB files and artifacts must remain within `E:\GT-KB`. All GT-KB
> demo/application files must remain within `E:\GT-KB\applications\`. Agent Red
> is a separate project, not part of GT-KB, and Agent Red files must not be used
> as live GT-KB artifacts. There are no exceptions. Any proposal, implementation,
> verification, or test that depends on a live path outside those roots is a
> NO-GO until revised.

**Proposed text:**

> All active GT-KB files and artifacts must remain within `E:\GT-KB`. All GT-KB application files must remain within `E:\GT-KB\applications\`. Agent Red is the reference adopter application for GT-KB at `applications/Agent_Red/`; its application subtree IS in-scope for GT-KB review under that root. Unqualified GT-KB tooling references must not resolve silently to Agent Red's lifecycle-independent repository or CI surfaces. There are no exceptions to the root-containment rule. Any proposal, implementation, verification, or test that depends on a live path outside those roots is a NO-GO until revised.

**Rationale.** Restores adopter-application status while preserving the root-boundary rule. Clarifies that Agent Red's `applications/Agent_Red/` subtree IS reviewable as part of GT-KB (which was always true given CLAUDE.md but was contradicted by the severance language).

### Change 4 — acting-prime-builder.md § "Agent Red Separate-Project Boundary" (lines 67-86)

**Subsection retitle.** "Agent Red Separate-Project Boundary" → "Agent Red Reference Adopter Application Boundary".

**Current text (verbatim, key paragraphs):**

> ## Agent Red Separate-Project Boundary
>
> Owner correction 2026-05-04 supersedes the prior Agent Red conformance framing
> for current GT-KB work: Agent Red is not part of GT-KB. It is a separate project
> whose repository is `https://github.com/mike-remakerdigital/agent-red`.
>
> Historical owner decision `DELIB-0834` and
> `GOV-AGENT-RED-GTKB-CONFORMANCE-001` said Agent Red is a well-behaved,
> fully-conformant application supported and sustained by GroundTruth-KB, not an
> ad hoc exception, and should not be treated as an ad hoc exception. The current
> interpretation is narrower: Release-readiness work should preserve and enforce GT-KB
> supported application behavior when Agent Red is explicitly in scope, and those
> behaviors should be documented, and regression-tested where possible, without
> treating Agent Red files as live GT-KB artifacts.
>
> GroundTruth-KB includes four small demo applications for validation and
> examples. Do not route unqualified GT-KB release, CI, bridge, source, or
> verification evidence to Agent Red. Agent Red work requires explicit owner
> scope and must use the separate Agent Red project identity.

**Proposed text:**

> ## Agent Red Reference Adopter Application Boundary
>
> Agent Red is the reference adopter application for GT-KB. The application subtree lives at `applications/Agent_Red/` per `CLAUDE.md` § Mandatory Project Root Boundary; its hosted form deploys from a lifecycle-independent repository at `https://github.com/mike-remakerdigital/agent-red`. Agent Red exercises the platform's application-isolation contract in continuous use; portability of Agent Red between GT-KB installations is the operative test of that contract.
>
> The canonical framing is established by `GOV-AGENT-RED-GTKB-CONFORMANCE-001` and `DELIB-0834`: Agent Red is a well-behaved, fully-conformant adopter supported and sustained by GroundTruth-KB, not an ad hoc exception, and is not to be treated as one. Active adopter-experience work tracks under `PROJECT-GTKB-ADOPTER-EXPERIENCE` (e.g., the Agent Red Deployability Preservation Gate at `bridge/gtkb-agent-red-deployability-preservation-gate-*`).
>
> The 2026-05-04 owner correction narrowed tooling-reference discipline: unqualified GT-KB tooling references — CLI invocations, CI workflows, GitHub Actions, release evidence, repository state — must not resolve silently to Agent Red surfaces. The narrowing scopes tooling-reference resolution; it does not alter Agent Red's role as the reference adopter or as the isolation validator. Agent Red surfaces are addressed explicitly when in scope.
>
> GroundTruth-KB also includes four small demo applications used as scaffold examples; those are distinct from Agent Red (the reference adopter). Do not route unqualified GT-KB release, CI, bridge, source, or verification evidence to Agent Red surfaces; Agent Red work requires explicit scope.

**Rationale.** Retitles to remove the misleading "Separate-Project Boundary" framing. Restores `GOV-AGENT-RED-GTKB-CONFORMANCE-001` and `DELIB-0834` as live authorities (they had been demoted to historical-context). Preserves the narrowing as a tooling-reference-discipline rule, not an adopter-relationship severance.

### Change 5 — file-bridge-protocol.md (line 16)

**Current text (verbatim):**

> remain within `E:\GT-KB\applications\`. Agent Red files are not GT-KB files and
> must not be used as live GT-KB artifacts. There are no exceptions. A bridge item
> that depends on a live path outside those roots is `NO-GO`.

**Proposed text:**

> remain within `E:\GT-KB\applications\`. Agent Red is the reference adopter application for GT-KB at `applications/Agent_Red/`; its subtree is in-scope for GT-KB bridge review. Unqualified GT-KB tooling references must not resolve silently to Agent Red's lifecycle-independent repository or CI surfaces. There are no exceptions to the root-containment rule. A bridge item that depends on a live path outside those roots is `NO-GO`.

**Rationale.** Same as Change 3, mirrored for the file-bridge-protocol clause.

### Cross-file consistency notes (no edits needed)

- `CLAUDE.md` § Mandatory Project Root Boundary already names `applications/Agent_Red/` as the canonical placement — no edit needed (it is consistent with the corrected framing).
- `.claude/rules/operating-model.md` §2 "application" entry already names Agent Red as an example application — no edit needed.
- `.claude/rules/canonical-terminology.toml` (lines 35, 48, 63, 82) lists "Agent Red" as a required-terms entry name only — no edit needed.
- `.claude/rules/bridge-essential.md` references the historical `Agent Red Bridge Monitor` watchdog (retired); that is descriptive history, not adopter-framing language — no edit needed.

## Requirement Sufficiency

**Existing requirements sufficient.** This proposal does not introduce new requirements; it restores rule-corpus consistency with existing requirements that were under-respected:

- `.claude/rules/operating-model.md` §2 — Agent Red named as an example application.
- `CLAUDE.md` § Mandatory Project Root Boundary — Agent Red placed within `applications/Agent_Red/`.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` / `DELIB-0834` — Agent Red as well-behaved fully-conformant application supported and sustained by GT-KB.
- `applications/Agent_Red/.gtkb-app-isolation.json` — live application-isolation contract.
- `PROJECT-GTKB-ADOPTER-EXPERIENCE` and the in-flight deployability-preservation gate.

The proposal documents that the 2026-05-04 owner correction was narrower than its current rule-corpus representation. That correction stands; this proposal only restores the framing to match the actual scope of the correction.

## Spec-to-Test Verification Plan

Each Specification Link maps to one or more verification checks. All checks are read-only greps or git operations.

| Spec link | Verification | Expected result |
|---|---|---|
| `.claude/rules/operating-model.md` §2 | Confirm operating-model.md unmodified by this implementation | `git diff --name-only` does not list `.claude/rules/operating-model.md` |
| `CLAUDE.md` § Mandatory Project Root Boundary | Confirm CLAUDE.md unmodified | `git diff --name-only` does not list `CLAUDE.md` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Confirm proposal includes Specification Links section with cited specs | (this section) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Confirm spec-to-test mapping (this table) | (this table) |
| Drift removal (canonical-terminology.md, project-root-boundary.md, loyal-opposition.md, acting-prime-builder.md, file-bridge-protocol.md) | Severance language removed | `grep -E "Agent Red.{0,50}(not part of GT-KB\|are not GT-KB files\|previously validated)" .claude/rules/{canonical-terminology,project-root-boundary,loyal-opposition,acting-prime-builder,file-bridge-protocol}.md` returns 0 hits |
| Reference-adopter framing present | New canonical phrase appears | `grep -l "reference adopter application" .claude/rules/{canonical-terminology,project-root-boundary,loyal-opposition,acting-prime-builder,file-bridge-protocol}.md` lists all 5 files |
| Narrowing preserved | Tooling-reference rule still present | `grep -l "unqualified GT-KB tooling references" .claude/rules/{canonical-terminology,project-root-boundary,loyal-opposition,acting-prime-builder,file-bridge-protocol}.md` lists all 5 files |
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` restored as live authority | Cited in acting-prime-builder.md and canonical-terminology.md | `grep -l "GOV-AGENT-RED-GTKB-CONFORMANCE-001" .claude/rules/{canonical-terminology,acting-prime-builder}.md` lists both |
| `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` | Each rule-file edit covered by a `formal-artifact-approval-packet` | `ls .groundtruth/formal-artifact-approvals/2026-*-canonical-terminology*.json` (and similar for the other four files) returns one matching packet per file |
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` + `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` | Edited Agent Red glossary entry remains DA-citable with complete Source line | Manual inspection: revised Source line names all authorities (`GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `DELIB-0834`, 2026-05-04 narrowing, S347 capture, S333 dual-repo) |
| No regression in implementation layer | `applications/Agent_Red/.gtkb-app-isolation.json` unchanged | `git diff --name-only` does not list the isolation JSON |

Post-implementation verification command (single composite):

```bash
# Confirm severance language removed across the five target files
grep -nE "Agent[ _]Red.{0,80}(not part of GT-KB|are not GT-KB files|previously validated)" \
  .claude/rules/canonical-terminology.md \
  .claude/rules/project-root-boundary.md \
  .claude/rules/loyal-opposition.md \
  .claude/rules/acting-prime-builder.md \
  .claude/rules/file-bridge-protocol.md \
  && { echo "FAIL: severance language remains"; exit 1; } || echo "PASS: severance language removed"

# Confirm reference-adopter framing present in all five files
for f in canonical-terminology project-root-boundary loyal-opposition acting-prime-builder file-bridge-protocol; do
  grep -q "reference adopter application" ".claude/rules/${f}.md" \
    || { echo "FAIL: ${f}.md missing reference adopter framing"; exit 1; }
done
echo "PASS: reference-adopter framing present in all 5 target files"

# Confirm narrowing preserved in all five files
for f in canonical-terminology project-root-boundary loyal-opposition acting-prime-builder file-bridge-protocol; do
  grep -q "unqualified GT-KB tooling references" ".claude/rules/${f}.md" \
    || { echo "FAIL: ${f}.md missing tooling-reference narrowing"; exit 1; }
done
echo "PASS: tooling-reference narrowing preserved in all 5 target files"

# Confirm non-target files unmodified
git diff --name-only HEAD | grep -E "^(CLAUDE\.md|\.claude/rules/operating-model\.md|applications/Agent_Red/\.gtkb-app-isolation\.json)$" \
  && { echo "FAIL: implementation-layer file modified out of scope"; exit 1; } || echo "PASS: implementation layer unchanged"
```

## Rollback

Each rule-file edit is a discrete text replacement; rollback is `git revert` of the implementation commit. The proposal does not modify any KB row, hook, script, or implementation-layer artifact, so rollback is purely textual.

If implementation completes but reveals an unanticipated downstream consumer that relied on the severed-framing language (e.g., a hook script grepping for "Agent Red is not part of GT-KB" as a routing signal):
1. `git revert` the implementation commit.
2. Inventory the downstream consumer and file a REVISED proposal addressing it.
3. Do not partially un-revert; rebase the corrected approach forward as a new clean commit.

## Out of Scope

Explicitly excluded from this proposal:

- The broader rule-corpus cleanse for other contaminated topics (owner-explicitly deferred to follow-up work per S347 turn 2).
- Capture of the S347 owner-decision conversation as a formal `DELIB-*` record. That capture is part of the deliberation-archive harvest at session wrap (post-VERIFIED), not part of this proposal.
- Promotion, modification, or creation of new GOV/ADR/DCL/PB/SPEC artifacts. The historical `GOV-AGENT-RED-GTKB-CONFORMANCE-001` is restored as the live canonical framing authority; no new spec is required.
- Any modification to `CLAUDE.md` or `.claude/rules/operating-model.md` (they already align with the corrected framing).
- Any modification to `applications/Agent_Red/` itself or to `applications/Agent_Red/.gtkb-app-isolation.json` (the isolation contract is consumed-as-evidence, not modified).
- Any change to the `v0.7.0-rc1` tag conditions or the `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` transient exception.
- Mechanical-enforcement improvements (hooks, scanners, gates) that would prevent recurrence of this drift class. The owner has flagged the underlying gap; the remediation of that gap is follow-up work, not part of this proposal.

## Open Decisions

None. The proposal is fully scoped within S347 owner authorization. Implementation can proceed under LO GO without further owner input, subject to per-file `formal-artifact-approval-packet` collection at implementation time.

## Applicability Preflight

To be run by Loyal Opposition before issuing a verdict:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-reference-adopter-framing-restoration
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-reference-adopter-framing-restoration
```

Expected: `preflight_passed: true`, `missing_required_specs: []`. Author has cited the documented cross-cutting specs (governance, artifact-approval, glossary, bridge-protocol, operating-model) above; preflight verification confirms the registry-driven required set is covered.

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
