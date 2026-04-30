REVISED

# GTKB Candidate Specification Intake — Six Owner Statements (REVISED-1)

**Status:** REVISED (REVISED-1; supersedes `-001` after Codex NO-GO at `-002`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-002.md` with three blocking findings (F1: verification incorrectly optional given proposed KB mutations; F2: bulk-approval mechanics violate the one-decision-at-a-time protocol; F3: canonical record identity and artifact type unresolved at owner-approval time).

bridge_kind: candidate_spec_intake
work_item_ids: [GTKB-CANDIDATE-SPEC-INTAKE-2026-04-29]
spec_ids: []  # this bridge proposes new specs; does not implement against existing ones
parent_bridge: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CANDIDATE-SPEC-STATEMENTS-BACKLOG-ADVISORY-2026-04-30.md (advisory source; archived as DELIB-1404)
target_project: gt-kb-platform (governance specs apply to the platform)
implementation_scope: presentation_only — F1 fix
requires_review: true
requires_verification: false  # F1 fix: this bridge is scoping/presentation-only; KB mutations are deferred to per-candidate follow-on bridges with their own GO + verification

**F1 fix — single unambiguous workflow:** This bridge is scoped to "present six candidate specs in native review format for owner per-candidate decision." It does NOT authorize any KB mutation, work-list update, or formal-artifact insertion. Each candidate that is approved by the owner becomes a separate per-candidate follow-on implementation bridge with its own Specification Links, test mapping, GO, post-impl, and VERIFIED. This bridge's VERIFIED is procedural (presentation completed correctly + at least one owner decision recorded as a DELIB).

---

## Specification Links

(Carried forward from `-001` §Specification Links.) Plus:
- `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-002.md` (Codex NO-GO) — drives this REVISED-1.

---

## Specification-Derived Verification

This is a presentation-only intake bridge per F1 fix. No KB / work-list / DA mutation in this bridge's authorized scope. Verification at this scoping stage is procedural:

| Spec / rule clause | Verification |
|---|---|
| `GOV-ARTIFACT-APPROVAL-001` (no canonical record without explicit owner approval) | This bridge writes nothing canonical; satisfied at the workflow level. |
| `.claude/rules/file-bridge-protocol.md` (Mandatory Specification Linkage Gate) | This bridge cites all relevant specs; satisfied. |
| `.claude/rules/codex-review-gate.md` (LO must NO-GO unlinked proposals) | This bridge IS linked; satisfied. |
| Codex F1 fix (single unambiguous workflow) | `requires_verification: false` declared; no KB mutation in scope; all KB mutation is deferred to per-candidate follow-on bridges. |
| Codex F2 fix (one decision at a time) | §1 workflow uses AskUserQuestion per-candidate; no bulk-approval path. |
| Codex F3 fix (canonical ID + type resolved before approval) | §2 carries final canonical IDs (semantic, no `CANDIDATE` prefix) and final type (`governance` for all six). |

Per-candidate **follow-on implementation bridges** (one per approved candidate) will carry their own Specification-Derived Verification per file-bridge-protocol Mandatory Spec-Derived Verification Gate at THAT bridge's filing time. This intake bridge does NOT pre-approve those tests.

---

## Prior Deliberations

(Carried forward from `-001` §Prior Deliberations.) Plus:
- `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-002.md` (Codex NO-GO) — drives this REVISED-1.

---

## Change Log Vs `-001`

| Change | Driving finding | Section |
|---|---|---|
| `requires_verification: true` removed; declared as **presentation-only** scoping bridge with no KB / work-list / DA mutation in scope. Each approved candidate becomes a separate follow-on implementation bridge. | F1 | metadata, §1, §6 |
| Owner decision flow changed from bulk-or-per-candidate to **strict per-candidate via AskUserQuestion**. Bulk approval removed as a default option (owner can still volunteer a single message that approves all six explicitly, but the harness asks one at a time). | F2 | §1 |
| Canonical IDs changed from `GOV-CANDIDATE-*-001` (intake labels) to **stable semantic IDs without `CANDIDATE`** per Codex F3: `GOV-TRANSCRIPT-DELIBERATION-CAPTURE-001`, `GOV-IMPL-PROPOSAL-SCOPE-LINKAGE-001`, `GOV-TESTS-BEFORE-IMPL-AND-VERIFIED-001`, `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`, `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001`, `GOV-RELEASE-MANIFEST-README-001`. All six remain `type='governance'`. | F3 | §2 (per-candidate ID + type) |
| Per-candidate ID + type now LOCKED at this bridge's filing time. Owner approval is approval of the exact final canonical content shown in §2 — no "we'll figure out the ID after approval" path. | F3 | §2 |
| Codex's open-question answers (1-6) folded into the proposal as decided rules, not as questions. | non-blocking | §1, §2, §3 |

All sections of `-001` not listed above are preserved unchanged.

---

## 1. Workflow Design (REVISED per F1, F2)

The candidate-spec intake follows GT-KB's existing formal-artifact-approval pattern with two changes:

**Workflow stages:**

1. **Present** (this bridge): each of six candidate specs is shown below in §2 in native review format (full content + final canonical metadata + source citation + present-state observations + target-state requirements). Owner sees the EXACT content that will become canonical if approved — no post-approval ID/type negotiation.

2. **Per-candidate decision via AskUserQuestion** (F2 fix): Prime asks the owner about ONE candidate at a time using AskUserQuestion with options `Approve / Reject / Modify / Defer`. After receiving each decision, Prime archives the decision as a deliberation (`source_type='owner_conversation'`, `outcome='owner_decision'`, linked_spec_ids=[<the candidate's semantic ID>]), then asks the next candidate. No bulk approval default.

3. **File per-candidate follow-on implementation bridge** (per approved candidate): Prime files a new bridge for inserting the approved candidate as a canonical spec, with full Specification Links + test mapping + GO + post-impl + VERIFIED. This intake bridge does NOT do the insertion itself.

4. **Reject / Modify / Defer outcomes:** rejected and deferred candidates are recorded as DELIB rows but no follow-on bridge is filed. Modified candidates: Prime presents the modified content for owner re-approval as a separate AskUserQuestion turn, then proceeds.

**Owner can volunteer a bulk approval out of band** (e.g., a free-form message saying "approve all six as written"). If the owner does so, Prime treats it as approval of each candidate's exact §2 content and archives one DELIB per candidate (still per-candidate audit trail). The harness still ASKS one at a time as the default.

**This bridge VERIFIED criteria** (procedural):
- All six candidates were presented in native review format with locked canonical ID + type.
- At least one owner decision was recorded as a DELIB before the bridge advances to VERIFIED.
- For each owner decision (approve / reject / modify / defer), the corresponding action was taken (follow-on bridge filed, or deferred record archived, etc.).
- No KB mutation was performed by THIS bridge.

---

## 2. Six Candidate Specifications (REVISED per F3 — final canonical IDs locked)

Each candidate is presented with **final canonical ID** (no CANDIDATE prefix; stable semantic), final type (`governance` for all six per Codex), final parent (`all` for #1-#4, `gtkb` for #5-#6 per Codex), and full text.

### 2.1 Candidate Spec #1 — Transcript-to-Deliberation Capture Mandate

**Canonical ID:** `GOV-TRANSCRIPT-DELIBERATION-CAPTURE-001` (no CANDIDATE prefix per F3)
**Title:** "Session transcripts MUST be mechanically harvested into the Deliberation Archive before any resulting SPEC, implementation proposal, or owner decision is treated as complete."
**Type:** `governance`
**Parent:** `all`

**Source citation:** `DELIB-1404` §1 (advisory at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/CANDIDATE-SPEC-STATEMENTS-BACKLOG-ADVISORY-2026-04-30.md` §1).

**Source statement (verbatim):**
> "We are mechanically harvesting session transcripts for deliberations which result in creation of specifications, implementation proposals and preceede user decisions related to implementation specifications."

**Target-state requirement (proposed canonical spec text — owner approves THIS exact content):**
- A formal SPEC, implementation proposal, or owner decision MUST cite a qualifying Deliberation Archive source row at creation time. Absence of a qualifying DA row is a fail-closed condition for the artifact-creation operation.
- Transcript harvest MUST be idempotent (re-running harvest on the same transcript produces no duplicate DA rows).
- Release-gate audit MUST verify every newly created formal artifact in the release window has at least one qualifying DA source reference.

(Present-state observations from `-001` §2.1 are kept as REVIEW context but are NOT part of the canonical spec text.)

### 2.2 Candidate Spec #2 — Implementation Proposal Spec Compliance + Scope Linkage

**Canonical ID:** `GOV-IMPL-PROPOSAL-SCOPE-LINKAGE-001`
**Title:** "Implementation proposals MUST enumerate applicable functional specs, non-functional specs (ADRs/DCLs), and parent scope (`gtkb` / `application` / `all`) before bridge GO."
**Type:** `governance`
**Parent:** `all`

**Source citation:** `DELIB-1404` §2.

**Source statement (verbatim):**
> "We are mechanically ensuring that the approval (GO) of implementation proposals is contingent upon compliance with specifications, both functional and non-functional (e.g., ADRs) and that the specification is applicable to GT-KB, the contained application (e.g., Agent Red) or both."

**Target-state requirement:**
- Every implementation proposal MUST include a `Parent Scope:` declaration alongside `Specification Links`.
- Bridge-compliance-gate (and Codex review skill) MUST reject proposals lacking either.
- After spec-lifecycle migration (separate bridge approved at -004): every cited spec MUST have its `parent` attribute matching or being a superset of the proposal's declared `Parent Scope:`.

### 2.3 Candidate Spec #3 — Spec-Derived Tests Before Implementation + Before VERIFIED

**Canonical ID:** `GOV-TESTS-BEFORE-IMPL-AND-VERIFIED-001`
**Title:** "Executable acceptance tests MUST exist before implementation begins, and MUST be executed and pass before VERIFIED can be issued."
**Type:** `governance`
**Parent:** `all`

**Source citation:** `DELIB-1404` §3.

**Source statement (verbatim):**
> "We are mechanically enforcing the creation of executable tests which can determine whether the requirement has been met, and we are creating those tests before the implementation is executed, and we are applying those tests before we declare that an implementation has been verified."

**Target-state requirement:**
- An implementation proposal MUST cite test files (existing OR planned) that derive from each linked spec, before bridge GO.
- A bridge cannot reach VERIFIED without those named tests existing AND being executed AND passing.
- Triad audit MUST distinguish "spec has assertions" from "spec has executable derived tests"; only the latter counts toward implementation evidence.

### 2.4 Candidate Spec #4 — Reliable Chat Detection + Owner Approval Before Spec Creation

**Canonical ID:** `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`
**Title:** "Chat-derived specification candidates MUST flow through an explicit owner-approval workflow before record creation; the workflow MUST be enforced at the service tier, not only at harness hooks."
**Type:** `governance`
**Parent:** `all`

**Source citation:** `DELIB-1404` §4.

**Source statement (verbatim):**
> "We are reliably detecting specifications in user chat and are mechanically enforcing user approval of the contents of a specification record before it is created."

**Target-state requirement:**
- Every chat-derived candidate spec MUST land at `outcome='deferred'` in the Deliberation Archive (or equivalent intake table) before becoming a canonical SPEC row.
- An explicit owner approval (via `confirm intake INTAKE-XXX` or equivalent) MUST be the ONLY path to canonical spec creation from chat-detected candidates.
- The approval gate MUST be enforced at the service tier (e.g., `KnowledgeDB.insert_spec()` checks for owner-approval evidence) — not only via harness hooks. Negative tests prove unapproved insertion through CLI / scripts / direct service API fails. **(Service-tier enforcement explicitly carried forward per Codex non-blocking observation on `-001` §2.4.)**

### 2.5 Candidate Spec #5 — Platform Inventory + Two-Stage Release Gate

**Canonical ID:** `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001`
**Title:** "GT-KB releases MUST include a complete constituent component inventory with versions, and MUST pass a two-stage validation: GT-KB platform validation followed by Agent Red staging validation."
**Type:** `governance`
**Parent:** `gtkb` (governs GT-KB release engineering, not adopter app code per Codex F3-Q2)

**Source citation:** `DELIB-1404` §5.

**Source statement (verbatim; sic for the typos in the original):**
> "We are actively maintaining a detailed inventory of the GT-KB platform artifacts and their component version numbers (where feasible) and capture all version numbers when testing the canonical Agent Red application in the staging environment. The testing of the GT-KB, followed by the testing of the reference pplication (Agent Red) in the staging environment is the final gate for GT-KB release."

**Target-state requirement:**
- Every GT-KB release MUST be accompanied by a release manifest enumerating constituent component versions (or explicit "not versioned" markers).
- The release pipeline MUST require: (a) GT-KB platform validation pass; (b) Agent Red staging validation pass with captured component versions and run evidence; (c) only then can the release be tagged on GitHub.
- Release-gate automation MUST reject releases failing either stage or lacking the component inventory.

### 2.6 Candidate Spec #6 — GitHub Release Manifest + README Constituent Versions

**Canonical ID:** `GOV-RELEASE-MANIFEST-README-001`
**Title:** "GitHub release artifacts MUST include a release manifest and README release section detailing constituent platform component versions."
**Type:** `governance`
**Parent:** `gtkb`

**Source citation:** `DELIB-1404` §6.

**Source statement (verbatim):**
> "The GT-KB release that we push to GitHub contains a minifest and a readme which details the versions of the constituent GT-KB platform."

**Target-state requirement:**
- Every GitHub release MUST include a release manifest file (e.g., `release-manifest.toml` or `release-manifest.json`) with: GT-KB package version, commit SHA, schema version, CLI version, template/scaffold version, hook/config versions where feasible, dashboard/reporting artifact versions, relevant dependency versions, and explicit "not versioned" markers.
- The README MUST contain a release section summarizing the manifest contents.
- A release test MUST fail if the manifest is missing, stale, or inconsistent with package metadata.

---

## 3. Sequencing After Owner Approval (per Codex Q6)

| Candidate | Implementation path |
|---|---|
| #1 (`GOV-TRANSCRIPT-DELIBERATION-CAPTURE-001`) | Net-new bridge: `gtkb-formal-artifact-da-source-required-impl`. |
| #2 (`GOV-IMPL-PROPOSAL-SCOPE-LINKAGE-001`) | Extends `gtkb-spec-lifecycle-schema-2026-04-29` Slice 4 (which adds `parent`). New bridge for the GOV rule + bridge-compliance-gate update. |
| #3 (`GOV-TESTS-BEFORE-IMPL-AND-VERIFIED-001`) | Closes via `gtkb-platform-spec-coverage-verified-runner-2026-04-29` REVISED-1 (filed in this same session). |
| #4 (`GOV-CHAT-DERIVED-SPEC-APPROVAL-001`) | Closes via `gtkb-membase-effective-use-recovery` Slices B+C. |
| **#5 + #6 (`GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001` + `GOV-RELEASE-MANIFEST-README-001`)** | **One combined scoping/architecture bridge** per Codex Q6, with two implementation slices: Slice 5a (release-gate / inventory; covers #5) and Slice 5b (manifest / README validation; covers #6). |

Each row above becomes a separate implementation bridge AFTER the owner approves the corresponding candidate.

**Cross-cutting follow-on (per Codex advisory Backlog B):** mechanical-enforcement-gap-audit bridge — separate filing after #1-#6 approved/rejected.

---

## 4. Acceptance Criteria

This intake bridge VERIFIED requires:

1. Each of six candidate specs presented in native review format with **final canonical ID + type locked at filing time** (per F3 fix). **Satisfied in §2.**
2. Each candidate carries final canonical metadata: ID (semantic, no CANDIDATE prefix), type (`governance`), parent (`all` × 4, `gtkb` × 2). **Satisfied (§2).**
3. Bridge does NOT auto-create any spec / work-list / approval-packet record (per F1 scoping-only). **Satisfied (`requires_verification: false`; no KB mutation in scope).**
4. Owner has clear per-candidate decision options via AskUserQuestion (per F2). **Satisfied (§1).**
5. Bulk approval is NOT a default harness path; owner-volunteered bulk approvals are processed per-candidate. **Satisfied (§1).**
6. Each approved candidate triggers a separate per-candidate follow-on implementation bridge. **Satisfied (§3).**
7. Approval workflow respects `GOV-ARTIFACT-APPROVAL-001`. **Satisfied (§1; no canonical record without explicit owner approval).**

---

## 5. Project Root Boundary

(Unchanged from `-001` §5.)

---

## 6. Files Touched (REVISED per F1)

**This bridge — scoping/intake only — touches NO source files, NO KB rows, NO work-list rows, NO approval packets.** The only file written by this bridge is the bridge document itself.

**Per-candidate follow-on bridges** (deferred; one per approved candidate) will touch:
- `groundtruth.db` — new spec rows (via `KnowledgeDB.insert_spec()` in their VERIFIED phase).
- `.groundtruth/formal-artifact-approvals/<filename>.json` — owner approval packet for that specific candidate.
- `memory/work_list.md` — new row for `GTKB-CANDIDATE-SPEC-INTAKE-2026-04-29` and any follow-on implementation work.

Those touches are NOT authorized by this bridge's GO; they are authorized by each per-candidate follow-on bridge's own GO.

---

## 7. Out of Scope

(Unchanged from `-001` §7.) Plus:
- KB mutation, work-list update, formal-artifact insertion (per F1 — deferred to per-candidate follow-on bridges).
- Bulk owner approval as a default harness path (per F2).
- Candidate-spec content modification after owner approval (per F3 — final content is what's shown in §2 above).

---

## 8. Codex Review Request

(Codex's `-002` answers to `-001` questions are now folded into the proposal. The remaining open questions:)

1. **DELIB linkage granularity (per Codex Q5):** §2 carries `DELIB-1404` as the common source advisory plus per-candidate verbatim source statements. Each per-candidate owner-decision DELIB will be a separate row when approval happens. Is that acceptable, or should each candidate's source statement also be archived as its own pre-approval DELIB now?
2. **Combined sequencing of #5 + #6 (per Codex Q6):** §3 plans one combined scoping bridge with two slices. Codex confirmed this is reasonable; this is asked again only for explicit GO acknowledgement before filing the combined bridge.

---

## 9. Decision Needed From Owner

**Per-candidate decision required for each of six specs.** Prime will ask via `AskUserQuestion` one candidate at a time, starting with #1 unless the owner explicitly redirects. Owner can volunteer a bulk approval out of band (Prime processes per-candidate but skips the asks).

This bridge cannot reach VERIFIED until at least one owner decision is recorded.

---

## 10. Aligns With

(Unchanged from `-001` §10.) Plus:
- Codex `-002` NO-GO findings F1-F3 (each addressed in §Change Log).
- Codex `-002` open-question answers (Q1-Q6) folded into §2 + §3.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
