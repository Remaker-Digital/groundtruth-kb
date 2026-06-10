NEW

# GTKB Candidate Specification Intake — Six Owner Statements (2026-04-29/30 Conversation)

**Status:** NEW (intake proposal; presents 6 candidate specs in native review format for owner approval)
**Date:** 2026-04-29
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex Loyal Opposition advisory at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CANDIDATE-SPEC-STATEMENTS-BACKLOG-ADVISORY-2026-04-30.md` — six owner statements about desired GT-KB governance/spec/test/release/archive behavior, framed as candidate specifications. Codex assessed each as "partially correct" (mechanisms exist; mechanical enforcement incomplete) and recommended Prime Builder formulate one proposal converting the statements into candidate spec records for owner review.

bridge_kind: prime_proposal
work_item_ids: [GTKB-CANDIDATE-SPEC-INTAKE-2026-04-29]
spec_ids: []  # this bridge proposes new specs; does not implement against existing ones
target_project: groundtruth-kb (governance specs that apply to the platform)
implementation_scope: spec_creation (gated on per-spec owner approval)
requires_review: true
requires_verification: false  # this bridge's "implementation" is owner-driven approval; verification is bookkeeping

This bridge does NOT auto-create any spec record. Per `GOV-ARTIFACT-APPROVAL-001`, each candidate spec requires explicit owner approval before insertion. The bridge presents 6 candidate specs in native review format so the owner can approve, reject, modify, or defer each.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate.

**Source advisory:**
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CANDIDATE-SPEC-STATEMENTS-BACKLOG-ADVISORY-2026-04-30.md` — Codex's structured assessment of 6 owner statements; substance basis for this proposal.

**Governance specs / records that constrain this work:**
- `GOV-ARTIFACT-APPROVAL-001` (KB-resolved) — strict default for formal artifact approval; each candidate spec proposed here requires owner approval evidence before becoming canonical.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` (KB-resolved) — formal-artifact-approval gate ADR; this proposal explicitly respects it.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` (KB-resolved) — hook-side enforcement; this proposal does not bypass.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (DELIB-0874; KB-resolved) — owner directive that brainstormed/discussed items become artifacts when they cross from discussion into decision/plan/requirement; this proposal converts six owner statements into candidate spec artifacts.
- `GOV-STANDING-BACKLOG-001` (DELIB-0838; KB-resolved) — `memory/work_list.md` as standing backlog authority; the candidate-intake program adds a row.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — separates AI-mediated discussion from deterministic artifact recording; the candidate-spec workflow embodies this.

**Adjacent / parallel work this proposal explicitly aligns with:**
- `bridge/gtkb-spec-lifecycle-schema-2026-04-29-003.md` (REVISED-1; approved at -004) — defines `parent` attribute (`gtkb`/`application`/`all`); each candidate spec below carries a proposed `parent` value.
- `bridge/gtkb-membase-effective-use-recovery-2026-04-29-001.md` (umbrella; approved at -002) — Slices B+C deliver the chat-derived spec capture + confirm/reject loop that mechanically implements candidate Spec #4 below.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` (approved at -006) — VERIFIED runner + mechanical-enforcement work that addresses candidate Spec #3.
- `bridge/active-workspace-declaration-architecture-2026-04-29-003.md` (REVISED-1; approved at -004) — workspace-declaration that complements `parent` attribute for candidate Spec #2.

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md` — bridge protocol; satisfied here at scoping.
- `.claude/rules/codex-review-gate.md` — Codex must NO-GO unlinked proposals.
- `.claude/rules/deliberation-protocol.md` — owner statements should be archived as deliberations; this proposal cites the conversation.
- `.claude/rules/project-root-boundary.md` — all artifacts under `E:\GT-KB`.

**Test derivation statement:** This is an intake proposal for owner-gated spec creation. Each candidate spec, when approved, will need its own derived tests (per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) at the implementation slice. The intake bridge itself proposes no tests. Acceptance verification at this scoping stage is procedural (each candidate is presented in native review format; owner approval decision recorded for each).

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- **Source conversation:** owner statements made during 2026-04-29/2026-04-30 conversation (this session). Each statement is quoted verbatim in §2 below from the Codex advisory. Each owner statement should be archived as a separate deliberation row at session-wrap (per session-wrap protocol); this bridge does NOT archive them inline (would mix bridge filing with DA mutation).
- **`DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT`** — earlier Codex advisory that catalyzed `gtkb-membase-effective-use-recovery`; demonstrates the same advisory→bridge pattern this proposal follows.
- **`DELIB-0874`** — owner directive on artifact-oriented governance; supports treating brainstorm-cross-into-decision items as artifacts.
- **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — supports the workflow design (deterministic capture + owner approval + service-side enforcement).
- **No prior deliberation reverses this approach.** The 6 owner statements have not been previously formalized; this is the first formal-artifact intake for any of them.

---

## 1. Workflow Design

The candidate-spec intake follows GT-KB's existing formal-artifact-approval pattern:

1. **Present** (this bridge): each candidate spec is shown below in native review format (full content + metadata + proposed parent + source citation + present-state observations + target-state requirements).
2. **Owner approves / rejects / modifies / defers** each candidate (per-candidate decision; not bulk).
3. **Record** owner decision as deliberation (`source_type='owner_conversation'`, `outcome='owner_decision'`).
4. **Insert** approved candidates into KB as canonical specs (`type='governance'` per current taxonomy; or `type='requirement'` if owner prefers).
5. **Backfill** approval evidence into `.groundtruth/formal-artifact-approvals/` packets per existing convention.
6. **Update** `memory/work_list.md` with each new spec ID and any follow-on implementation work.

**Owner approval mechanics:** owner can approve all 6 in bulk, approve some + defer others, or reject any. Per Codex advisory Backlog item A acceptance criterion: "No candidate is silently converted into a canonical spec without owner confirmation of the final record content."

**Per-candidate decision template (suggested for owner reply):**
```
SPEC #N: APPROVE | REJECT | MODIFY | DEFER
[if MODIFY:] modifications: <text>
[if REJECT:] reason: <text>
[if DEFER:] defer until: <condition>
```

---

## 2. Six Candidate Specifications

Each candidate is presented in the format: **proposed ID** | **title** | **type** | **parent** | **source statement (verbatim)** | **present-state observation** | **target-state requirement**.

### 2.1 Candidate Spec #1 — Transcript-to-Deliberation Capture Mandate

**Proposed ID:** `GOV-CANDIDATE-TRANSCRIPT-DELIBERATION-CAPTURE-001`
**Title:** "Session transcripts MUST be mechanically harvested into the Deliberation Archive before any resulting SPEC, implementation proposal, or owner decision is treated as complete."
**Type:** governance
**Parent:** all (the rule applies whether the spec/proposal/decision is GT-KB platform or hosted application)

**Source statement (verbatim from advisory §1):**
> "We are mechanically harvesting session transcripts for deliberations which result in creation of specifications, implementation proposals and preceede user decisions related to implementation specifications."

**Present-state observation (per advisory §1):** Partially correct.
- `scripts/harvest_session_deliberations.py` exists.
- `gt deliberations` CLI exists.
- Recent owner-origin DELIBs (1400-1403) used as evidence.
- BUT: not yet always-on / invariant; harvest still relies on session-wrap, explicit scripts, or backfill rather than point-of-decision invariant.

**Target-state requirement (proposed spec text):**
- A formal SPEC, implementation proposal, or owner decision MUST cite a qualifying Deliberation Archive source row at creation time. Absence of a qualifying DA row is a fail-closed condition for the artifact-creation operation.
- Transcript harvest MUST be idempotent (re-running harvest on the same transcript produces no duplicate DA rows).
- Release-gate audit MUST verify every newly created formal artifact in the release window has at least one qualifying DA source reference.

**Implementation surfaces this would touch (not in this bridge's scope; future implementation slices):**
- `groundtruth-kb/src/groundtruth_kb/formal_artifact_creation.py` (or equivalent) — service-side check.
- `scripts/release_candidate_gate.py` — release-gate audit step.
- New tests under `groundtruth-kb/tests/test_formal_artifact_creation.py`.

### 2.2 Candidate Spec #2 — Implementation Proposal Spec Compliance + Scope Linkage

**Proposed ID:** `GOV-CANDIDATE-IMPL-PROPOSAL-SPEC-COMPLIANCE-SCOPE-001`
**Title:** "Implementation proposals MUST enumerate applicable functional specs, non-functional specs (ADRs/DCLs), and parent scope (`gtkb` / `application` / `all`) before bridge GO."
**Type:** governance
**Parent:** all

**Source statement (verbatim from advisory §2):**
> "We are mechanically ensuring that the approval (GO) of implementation proposals is contingent upon compliance with specifications, both functional and non-functional (e.g., ADRs) and that the specification is applicable to GT-KB, the contained application (e.g., Agent Red) or both."

**Present-state observation (per advisory §2):** Partially correct.
- Bridge process expects spec linkage; LO review judges compliance before GO.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 exists (KB-resolved); enforced by bridge-compliance-gate.py.
- BUT: parent scope (`gtkb` / `application` / `all`) is NOT yet in spec schema; mechanical scope enforcement absent.

**Target-state requirement:**
- Every implementation proposal MUST include a `Parent Scope:` declaration alongside `Specification Links`.
- Bridge-compliance-gate (and Codex review skill) MUST reject proposals lacking either.
- After spec-lifecycle migration (separate bridge already approved at -004): every cited spec MUST have its `parent` attribute matching or being a superset of the proposal's declared `Parent Scope:`.

**Direct overlap:** `gtkb-spec-lifecycle-schema-2026-04-29` (approved at -004) Slice 1 adds `parent` column to spec schema; Slice 4 backfills. This candidate Spec #2 is the GOVERNANCE rule that consumes that schema.

### 2.3 Candidate Spec #3 — Spec-Derived Tests Before Implementation + Before VERIFIED

**Proposed ID:** `GOV-CANDIDATE-TESTS-BEFORE-IMPL-AND-VERIFIED-001`
**Title:** "Executable acceptance tests MUST exist before implementation begins, and MUST be executed and pass before VERIFIED can be issued."
**Type:** governance
**Parent:** all

**Source statement (verbatim from advisory §3):**
> "We are mechanically enforcing the creation of executable tests which can determine whether the requirement has been met, and we are creating those tests before the implementation is executed, and we are applying those tests before we declare that an implementation has been verified."

**Present-state observation (per advisory §3):** Partially correct.
- Spec → test → impl → verification is intended workflow.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` is KB-resolved (VERIFIED-time gate).
- Triad audit (`audit_gtkb_triad_completeness.py`, committed `73c41ee4`) measures gaps.
- BUT: "tests created BEFORE implementation begins" is not yet mechanically enforced; "assertion-only evidence" being treated as implementation evidence is a known defect.

**Target-state requirement:**
- An implementation proposal MUST cite test files (existing OR planned) that derive from each linked spec, before bridge GO.
- A bridge cannot reach VERIFIED without those named tests existing AND being executed AND passing.
- Triad audit MUST distinguish "spec has assertions" from "spec has executable derived tests"; only the latter counts toward implementation evidence.

**Direct overlap:** `gtkb-platform-spec-coverage-verified-runner-2026-04-29` (NO-GO at -002; awaiting REVISED-1) implements the VERIFIED runner that mechanically enforces this. This candidate Spec #3 is the GOVERNANCE rule the runner enforces.

### 2.4 Candidate Spec #4 — Reliable Chat Detection + Owner Approval Before Spec Creation

**Proposed ID:** `GOV-CANDIDATE-CHAT-DERIVED-SPEC-APPROVAL-001`
**Title:** "Chat-derived specification candidates MUST flow through an explicit owner-approval workflow before record creation; the workflow MUST be enforced at the service tier, not only at harness hooks."
**Type:** governance
**Parent:** all

**Source statement (verbatim from advisory §4):**
> "We are reliably detecting specifications in user chat and are mechanically enforcing user approval of the contents of a specification record before it is created."

**Present-state observation (per advisory §4):** "Partially correct, leaning incorrect as a present-state claim."
- Hooks exist for chat detection.
- `GOV-ARTIFACT-APPROVAL-001` requires formal-artifact approval where applicable.
- BUT: reliability not demonstrated end-to-end; scripted backfills and manual creation paths can bypass; hook presence ≠ reliable enforcement across all surfaces.

**Target-state requirement:**
- Every chat-derived candidate spec MUST land at `outcome='deferred'` in the Deliberation Archive (or equivalent intake table) before becoming a canonical SPEC row.
- An explicit owner approval (via `confirm intake INTAKE-XXX` or equivalent) MUST be the ONLY path to canonical spec creation from chat-detected candidates.
- The approval gate MUST be enforced at the service tier (e.g., `KnowledgeDB.insert_spec()` checks for owner-approval evidence) — not only via harness hooks. Negative tests prove unapproved insertion through CLI / scripts / direct service API fails.

**Direct overlap:** `gtkb-membase-effective-use-recovery` Slices B (auto-capture as deferred) + C (confirm/reject loop) deliver the workflow. Slice B's formal-artifact-approval handling explicitly addresses the service-tier gate. This candidate Spec #4 is the GOVERNANCE rule those slices implement.

### 2.5 Candidate Spec #5 — Platform Inventory + Two-Stage Release Gate

**Proposed ID:** `GOV-CANDIDATE-RELEASE-GATE-PLATFORM-INVENTORY-TWO-STAGE-001`
**Title:** "GT-KB releases MUST include a complete constituent component inventory with versions, and MUST pass a two-stage validation: GT-KB platform validation followed by Agent Red staging validation."
**Type:** governance
**Parent:** gtkb (the rule governs GT-KB release engineering, not Agent Red app code)

**Source statement (verbatim from advisory §5):**
> "We are actively maintaining a detailed inventory of the GT-KB platform artifacts and their component version numbers (where feasible) and capture all version numbers when testing the canonical Agent Red application in the staging environment. The testing of the GT-KB, followed by the testing of the reference pplication (Agent Red) in the staging environment is the final gate for GT-KB release."

**Present-state observation (per advisory §5):** Partially correct.
- Release-readiness, dashboard, inventory, backlog evidence surfaces exist.
- GT-KB treated as platform; Agent Red as reference adopter.
- BUT: not every feasible component version inventoried; not every staging test version captured; two-stage gate not codified or mechanically enforced.

**Target-state requirement:**
- Every GT-KB release MUST be accompanied by a release manifest enumerating constituent component versions (or explicit "not versioned" markers).
- The release pipeline MUST require: (a) GT-KB platform validation pass; (b) Agent Red staging validation pass with captured component versions and run evidence; (c) only then can the release be tagged on GitHub.
- Release-gate automation MUST reject releases failing either stage or lacking the component inventory.

**Net new — no current bridge addresses this. After approval, would require its own implementation bridge.**

### 2.6 Candidate Spec #6 — GitHub Release Manifest + README Constituent Versions

**Proposed ID:** `GOV-CANDIDATE-RELEASE-MANIFEST-README-COMPONENT-VERSIONS-001`
**Title:** "GitHub release artifacts MUST include a release manifest and README release section detailing constituent platform component versions."
**Type:** governance
**Parent:** gtkb

**Source statement (verbatim from advisory §6):**
> "The GT-KB release that we push to GitHub contains a minifest and a readme which details the versions of the constituent GT-KB platform."

**Present-state observation (per advisory §6):** "Partially correct, but materially incomplete."
- `groundtruth-kb/pyproject.toml` declares README; package version `0.6.1` in `__init__.py` and README.
- BUT: no release manifest enumerating constituent components; existing manifest is project/adopter scaffold metadata only; README does not detail every constituent version.

**Target-state requirement:**
- Every GitHub release MUST include a release manifest file (e.g., `release-manifest.toml` or `release-manifest.json`) with: GT-KB package version, commit SHA, schema version, CLI version, template/scaffold version, hook/config versions where feasible, dashboard/reporting artifact versions, relevant dependency versions, and explicit "not versioned" markers.
- The README MUST contain a release section summarizing the manifest contents.
- A release test MUST fail if the manifest is missing, stale, or inconsistent with package metadata.

**Net new — no current bridge addresses this. After approval, would require its own implementation bridge. Closely coupled with Spec #5 (both are release-engineering governance).**

---

## 3. Sequencing After Owner Approval

If all 6 candidates are approved (or any subset), implementation work follows:

| Candidate | Implementation path |
|-----------|---------------------|
| #1 (transcript→DA capture) | Net-new bridge: `gtkb-formal-artifact-da-source-required-impl-2026-04-29`. |
| #2 (impl proposal scope linkage) | Extends `bridge/gtkb-spec-lifecycle-schema-2026-04-29` Slice 4 (which already adds `parent`). New bridge for the GOV rule + bridge-compliance-gate update. |
| #3 (tests-before-impl + VERIFIED) | Closes with `gtkb-platform-spec-coverage-verified-runner-2026-04-29` REVISED-1 (currently NO-GO at -002; will be revised). |
| #4 (chat-derived spec approval) | Closes with `gtkb-membase-effective-use-recovery` Slices B+C (in flight). |
| #5 (release inventory + two-stage gate) | Net-new bridge: `gtkb-release-gate-platform-inventory-two-stage-impl`. |
| #6 (release manifest + README) | Net-new bridge: `gtkb-release-manifest-readme-impl`. Closely coupled with #5; could ship as one bridge or two. |

**Cross-cutting follow-on (per advisory Backlog B):** mechanical-enforcement-gap-audit bridge — separate filing after #1-#6 approved/rejected. That bridge would classify each candidate's enforcement surface (service / hook / bridge / CI / report / convention) and identify gaps.

---

## 4. Acceptance Criteria

This intake bridge VERIFIED requires:

1. Each of 6 candidate specs is presented in native review format (full content + metadata + parent + source + present-state + target-state). **Satisfied in §2 above.**
2. Each candidate carries a proposed `parent` value (`gtkb` / `application` / `all`). **Satisfied (§2: 4× all + 2× gtkb).**
3. The bridge does NOT auto-create any spec record. **Satisfied (no KB mutation in this bridge).**
4. Owner has clear per-candidate decision options (APPROVE / REJECT / MODIFY / DEFER). **Satisfied (§1 workflow).**
5. Each candidate cites its source advisory + verbatim owner statement. **Satisfied (§2).**
6. Each candidate is linked to the most relevant in-flight bridge (or marked net-new). **Satisfied (§2 + §3).**
7. Approval workflow respects `GOV-ARTIFACT-APPROVAL-001` (no canonical record without explicit owner approval). **Satisfied (§1).**

---

## 5. Project Root Boundary

Per `.claude/rules/project-root-boundary.md`:
- All artifacts under `E:\GT-KB`.
- Spec records (when approved) live in `groundtruth.db` at `E:\GT-KB\groundtruth.db`.
- No external paths, no home-dir mirrors.

---

## 6. Files Touched (this bridge — scoping/intake only)

**New:** none (this bridge does not create any spec records; owner approves per-candidate first).

**Modified on approval (each, separately, per-candidate):**
- `groundtruth.db` — new spec rows for each approved candidate (via `KnowledgeDB.insert_spec()` with `changed_by='prime-builder/claude'`, `change_reason='owner-approved candidate spec from CANDIDATE-SPEC-INTAKE-2026-04-29 bridge §<N>'`).
- `.groundtruth/formal-artifact-approvals/2026-04-29-candidate-spec-<id>.json` — owner approval packet per approved candidate.
- `memory/work_list.md` — new row for `GTKB-CANDIDATE-SPEC-INTAKE-2026-04-29` and any follow-on implementation work items per approved candidate.

**Not touched in this bridge:**
- `bridge/INDEX.md` (only the entry insertion for this bridge itself).
- Any source code (`groundtruth-kb/src/**`, `scripts/**`, `tests/**`).

---

## 7. Out of Scope

- Implementation of any candidate spec's enforcement (each requires its own implementation bridge after owner approval).
- Mechanical-enforcement-gap audit (per advisory Backlog B; separate bridge filing).
- Spec-source linkage table population (per advisory Backlog D; covered by `gtkb-spec-lifecycle-schema-2026-04-29` Slice 1 deliverable).
- Bulk owner approval; per §1, each candidate gets a per-candidate decision.
- Modifying CLAUDE.md or session-startup reports to claim these candidates as "we already do this" — per advisory's methodological recommendation #2.

---

## 8. Codex Review Request

1. **Spec ID format:** are `GOV-CANDIDATE-*-001` prefixes appropriate? Or should approved specs use `GOV-NNNN` (numeric) per existing convention?
2. **Parent assignment:** §2.5 and §2.6 are `parent='gtkb'` because they govern GT-KB release engineering. Are these correctly scoped, or should they be `parent='all'` (since adopter projects might inherit similar release patterns)?
3. **Type vocabulary:** §2 uses `type='governance'` for all 6. Should some be `type='requirement'` instead (per the existing taxonomy)? The semantic difference: `governance` is a binding rule; `requirement` is a stated need that may have multiple implementation paths.
4. **Workflow ordering:** §1 proposes owner approves each candidate per-spec. Acceptable, OR should there be a bulk approval option for owner convenience?
5. **Per-candidate deliberation archival:** §1 step 3 records owner decision as a deliberation. Should the source statement (verbatim) ALSO be archived as a separate deliberation, OR is one deliberation per decision sufficient?
6. **Sequencing of net-new candidates (#5 + #6):** these are closely coupled (release engineering). Should the implementation bridge be one combined or two separate? Recommend Codex preference.

---

## 9. Decision Needed From Owner

**Per-candidate decision required for each of 6 specs.** Owner reply format suggested in §1 ("SPEC #N: APPROVE | REJECT | MODIFY | DEFER"). Bulk approval (e.g., "approve all 6 with §2 text as-is") is also acceptable.

This bridge cannot reach VERIFIED until at least one owner decision is recorded. Per `GOV-ARTIFACT-APPROVAL-001`, no canonical spec is created without owner approval evidence.

---

## 10. Aligns With

- Codex advisory `CANDIDATE-SPEC-STATEMENTS-BACKLOG-ADVISORY-2026-04-30.md` (substance source).
- Codex advisory's Recommended Action #1 ("Convert these six statements into candidate spec records for owner review").
- Codex advisory's Backlog A acceptance criterion ("No candidate is silently converted into a canonical spec without owner confirmation of the final record content").
- DELIB-0874 (artifact-oriented governance — discussion items become artifacts when they cross into decision/plan/requirement).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (deterministic capture + owner approval workflow).
- GOV-ARTIFACT-APPROVAL-001 (explicit owner approval required for formal artifact creation).
- GOV-AGENT-RED-GTKB-CONFORMANCE-001 (parent scope distinguishes platform vs adopter).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
