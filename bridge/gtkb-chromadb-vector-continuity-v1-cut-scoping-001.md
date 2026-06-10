NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-27-chromadb-vector-continuity-scoping
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# ChromaDB Vector Continuity at v1.0 Identifier-Reset Cut: governance-review scoping (Finding 3 from V1 Release Strategy LO review)

bridge_kind: governance_advisory
Document: gtkb-chromadb-vector-continuity-v1-cut-scoping
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-27 UTC
Implements: WI-3395 (ChromaDB semantic-history backfill design for v1.0 identifier-reset cut)
Work Item: WI-3395
target_paths: [".gtkb-state/design/chromadb-vector-continuity/"]
Recommended commit type: docs:

## Summary

This is a `bridge_kind: governance_review` proposal. Its scope is governance gap analysis plus a design contract for ChromaDB semantic-history continuity across the proposed v1.0 identifier-reset cut. The proposal does not propose creating live backfill code, mutating ChromaDB, mutating MemBase, or executing any production-affecting action. Owner approval of the design contract this proposal lands is the gate that precedes any future implementation proposal.

The originating signal is Finding 3 of `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-08-52-V1-RELEASE-STRATEGY-REVIEW.md`. My Prime Builder evaluation (this session) accepted Finding 3 as the LO report's one genuinely novel substantive contribution: the v1-release-strategy-deliberation-S347 Option A "identifier-translation manifest" mitigation is a textual mapping artifact; the ChromaDB semantic vectors at `.groundtruth-chroma/` are bound to the old DELIB/SPEC IDs and will not follow a text manifest. Vector continuity requires a database backfill, not a text translation table.

The governance-review deliverable is a design document tree under `.gtkb-state/design/chromadb-vector-continuity/<UTC-timestamp>/`. The document specifies the HIST-DELIB-NNNN backfill contract (data model, vector regeneration semantics, search-API behavior, idempotency invariants, rollback story) at a depth sufficient to evaluate v1.0-cut feasibility — without writing any production code or mutating the live ChromaDB substrate.

This governance review does NOT touch `.groundtruth-chroma/`. It does NOT change MemBase. It does NOT establish the v1.0 cut sequencing (that is a separate strategic decision tracked in `memory/v1-release-strategy-deliberation-S347.md`). It does NOT create new projects or formal specs. Project assignment for WI-3395 is intentionally deferred to a follow-on owner decision; the review proceeds against WI-3395 as a standalone backlog candidate.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - design evidence written to in-root `.gtkb-state/design/chromadb-vector-continuity/`; no out-of-root paths touched.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this governance-review proposal cites the governing specification surfaces and concrete target paths.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the spec-to-test mapping below maps each governing surface to a verification step appropriate for governance-review delivery.
- SPEC-2098 - Deliberation Archive specification; the v1.0 cut's vector-continuity question is a SPEC-2098 amendment surface.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the design document produced by this review is a durable governed artifact under change control.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - traceability preserved between WI-3395, this thread, the design document, and any follow-on implementation proposal.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3395 advances from `backlogged` to lifecycle-tracked governance-review scope; implementation lifecycle remains deferred.
- GOV-STANDING-BACKLOG-001 - WI-3395 was captured via the gate-clean backlog-add CLI as a standalone backlog candidate; project membership decision is deferred.

## Requirement Sufficiency

New or revised requirement may be required before implementation. The governance-review deliverable itself does not require new requirements — the design document is a candidate requirement set that, once approved, would become the implementation contract. Specifically: the review will surface candidate requirements for HIST-DELIB-NNNN identifier semantics, vector-regeneration triggers, and search-API backward-compatibility expectations. Those candidate requirements need owner approval through the standard chat-derived spec approval workflow per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` before they are promoted to formal SPECs that the v1.0 cut work would implement.

## KB Mutation Scope

This proposal performs no MemBase mutation. The implementation does not write to groundtruth.db. The review work produces a design document tree at `.gtkb-state/design/chromadb-vector-continuity/<timestamp>/` plus supporting analysis files; none of those writes touch the live KB. No spec creation, project creation, or work-item lifecycle mutation occurs during the review. `.groundtruth-chroma/` (the ChromaDB store) is also not mutated; the review reads it but does not write. `groundtruth.db` is therefore intentionally excluded from target_paths.

## WI Citation Disclosure

The proposal declares review work for WI-3395 only. References to the LO report `INSIGHTS-2026-05-27-08-52-V1-RELEASE-STRATEGY-REVIEW.md` and to the v1-release-strategy-deliberation-S347 document are originating-source citations, not implementation-scope expansions. The proposal does not cite or claim work on any other WI ID.

## Prior Deliberations

- independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-08-52-V1-RELEASE-STRATEGY-REVIEW.md (2026-05-27): LO report from Antigravity (harness C, role currently unassigned) reviewing the v1.0 release strategy. Finding 3 (P1 severity per my evaluation) identified the ChromaDB vector-continuity gap that this review addresses. Findings 1 and 2 were assessed as echoes of the target document's own self-criticism; Finding 3 is the one genuinely novel substantive contribution. Owner accepted the evaluation in this session.
- memory/v1-release-strategy-deliberation-S347.md lines 403-420 (2026-05-27, S347): The §8.4 "Identifier reset blast radius (Option A specific)" section identifies the v1.0 identifier-reset risk and proposes a one-time identifier-translation manifest as mitigation. The section has zero mentions of ChromaDB, vector indexing, or semantic-history continuity (verified by grep returning zero matches in this session). The text mitigation is therefore incomplete for vector-bound semantic data.
- SPEC-2098 Deliberation Archive feature spec: the Deliberation Archive's ChromaDB vector index is the asset whose continuity the review addresses.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE: the future HIST-DELIB-NNNN backfill, if approved, will be a deterministic service — exactly the kind of plumbing the principle says belongs in services rather than in session work.
- DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT: the v1.0 cut is the lifecycle-independence event that makes the vector-continuity question load-bearing; without lifecycle independence, the question would be deferrable, but the v1.0 cut forces a decision.
- bridge/gtkb-inventory-regen-chore-commit-2026-05-27-004.md (VERIFIED 2026-05-27): demonstrates the same-session bridge-protocol cadence used by this proposal; cited for protocol continuity only.

## Owner Decisions / Input

This proposal depends on the following owner decisions:

- Owner direction 2026-05-27 (this session): "Please proceed: ... advance Finding 3 to a bridge proposal ..." authorized advancing Finding 3 of the LO report to bridge-proposal scope. This direction was given immediately after my Prime Builder evaluation of the LO report, where the recommended treatment for Finding 3 was "Bridge proposal recommended before any v1.0 ID-reset cut work begins."
- Owner direction earlier this session (regarding LO-report evaluation): "I agree" accepting my per-finding evaluation including the Finding 3 disposition recommendation.

This proposal explicitly defers the following owner decisions to follow-on bridges:

- Whether to create PROJECT-V1-RELEASE-STRATEGY-PREP as a host project for v1.0 strategic-prep work, with WI-3395 as the first member. The review can proceed without this project creation (WI-3395 captured as a standalone backlog candidate).
- Whether the design-document contents, once produced, should be promoted to a formal `SPEC-CHROMADB-VECTOR-CONTINUITY-001` (or similar) via the standard chat-derived spec approval workflow.
- Whether to fund and execute the HIST-DELIB-NNNN backfill implementation. Gated on the broader v1.0 cut go/no-go decision tracked in `memory/v1-release-strategy-deliberation-S347.md` (S347 owner deliberation; current state: Option 1 Full Clean-Sheet + Option 1 Blocking Adopter Gate selected; sequencing and execution timeline undetermined).
- Whether the review should be conducted against ChromaDB specifically (the current substrate) or as a substrate-agnostic vector-continuity design that could host either ChromaDB or an alternative semantic-index backend.

## Implementation Plan

The governance-review work produces five evidence artifacts under `.gtkb-state/design/chromadb-vector-continuity/<UTC-timestamp>/`:

1. `current-state-analysis.md`:
   - Document the current ChromaDB store contents: collection names, embedded-document counts, embedding model versions, metadata schema, ID conventions.
   - Document the binding between DELIB-NNNN IDs in MemBase and ChromaDB document IDs.
   - Document the ChromaDB query API surface currently consumed by `gt deliberations search` (CLI), `search_deliberations()` (Python), and any session-start hooks.
   - Verify by reading `.groundtruth-chroma/` (read-only inspection) and `groundtruth-kb/src/groundtruth_kb/deliberations/` (code reading).

2. `gap-analysis.md`:
   - Enumerate concrete failure modes of an identifier-reset cut without vector backfill: e.g., `gt deliberations search "v1 release strategy"` returns zero results because the v1.0 cut's new DELIB IDs have no embedded documents.
   - Quantify the lost provenance surface: how many distinct DELIB-IDs exist; how many bridge threads cite DELIB IDs; how many memory files / rule files cite DELIB IDs.
   - Identify the consumers of vector search that would degrade: list each call site.

3. `design-contract.md`:
   - Specify the HIST-DELIB-NNNN identifier convention (e.g., legacy `DELIB-1990` becomes `HIST-DELIB-1990` in the v1.0 ChromaDB).
   - Specify the backfill script's input contract (read source: pre-cut groundtruth.db deliberations table; pre-cut ChromaDB collections), output contract (write target: post-cut ChromaDB with HIST- prefixed IDs), and operation semantics (idempotent, resumable, dry-runnable).
   - Specify the search-API behavior: by default, search returns both HIST- and current results; opt-in flag to exclude HIST-; opt-in flag to include only HIST-.
   - Specify rollback: backfill is reversible by deleting HIST- prefixed entries from the post-cut ChromaDB; backfill leaves the pre-cut substrate untouched.
   - Specify the verification approach: pre/post embedding-count parity, semantic-match preservation against a representative query set, no MemBase write side-effects.

4. `risk-and-blast-radius.md`:
   - Enumerate risks: embedding-model version drift between pre-cut and post-cut; ID collision if HIST- prefix conflicts with future canonical IDs; storage cost of duplicating embedded documents.
   - Mitigation analysis for each risk.

5. `recommended-followon.md`:
   - Concrete recommendations: which formal spec(s) should be created from the design contract (e.g., `SPEC-CHROMADB-VECTOR-CONTINUITY-001`); which test plan; which implementation bridge thread name and slice structure.
   - Suggested sequencing relative to the v1.0 cut: e.g., "backfill script must be GO'd and dry-run-verified before any DELIB-ID reset takes place".

The review uses only read-only inspection of `.groundtruth-chroma/`, the Deliberation Archive code, and existing MemBase tables. No writes occur outside `.gtkb-state/design/chromadb-vector-continuity/`.

## Spec-to-Test Mapping

| Specification | Verification Command | Expected Result |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This proposal filed at `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-001.md`; INDEX entry created. | PASS - bridge protocol observed. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Review evidence directory is `.gtkb-state/design/chromadb-vector-continuity/` — under `E:\GT-KB`. | PASS - all in-root. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-chromadb-vector-continuity-v1-cut-scoping` will be run before Codex review. | PENDING (preflight scheduled). |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This table itself records the spec-to-test mapping; post-implementation report will record observed results. | PASS - mapping present. |
| SPEC-2098 | The design-contract.md output will explicitly identify which SPEC-2098 clauses the backfill design extends, supersedes, or leaves unchanged. | PASS at post-impl (design-contract.md output verifies). |
| GOV-STANDING-BACKLOG-001 | WI-3395 captured via gate-clean backlog-add CLI; project assignment intentionally deferred. | PASS - WI captured; project assignment deferred. |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 / ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 / DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Design-document artifacts + bridge audit trail preserve durable traceability between WI-3395, this thread, and the design outputs. | PASS - traceability preserved. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this governance-review proposal.
- [ ] `.gtkb-state/design/chromadb-vector-continuity/<UTC-timestamp>/` exists and contains the five Markdown evidence files.
- [ ] `current-state-analysis.md` enumerates the current ChromaDB store contents and the DELIB-ID-to-ChromaDB-ID binding.
- [ ] `gap-analysis.md` enumerates concrete failure modes of an identifier-reset cut without vector backfill.
- [ ] `design-contract.md` specifies the HIST-DELIB-NNNN convention, input/output contracts, search-API behavior, rollback story, and verification approach.
- [ ] `risk-and-blast-radius.md` enumerates risks and mitigations.
- [ ] `recommended-followon.md` provides concrete next-step recommendations including spec promotion candidates and follow-on bridge thread naming.
- [ ] No production code is created, modified, or deleted during the review.
- [ ] `.groundtruth-chroma/` is not mutated during the review (only read).
- [ ] groundtruth.db is not mutated during the review.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report before any follow-on implementation bridge is filed.

## Risk and Rollback

Risk is very low. The review work is read-only against production substrates; design output lives entirely in `.gtkb-state/design/` which is excluded from regression-gate canonical state.

Risks identified:
- The review may surface design choices that are larger than expected (e.g., requiring multiple SPECs rather than one). The post-implementation report's recommended-followon.md will surface this and request owner direction on sequencing.
- The current ChromaDB substrate may have undocumented constraints that the review discovers only mid-work. The post-impl report will record any such constraints as risk factors for the implementation phase.
- The review may reveal that the v1.0 cut's identifier-reset is itself unnecessary (e.g., if append-only ID extension would meet the v1.0 goals without ChromaDB disruption). In that case, the recommended-followon.md will surface that alternative for owner consideration before any further work proceeds.

Rollback: delete the design-document tree. No state changes outside `.gtkb-state/design/` to roll back.

## Verification Limitations Anticipated

- The review does not validate the design against a working backfill prototype. Validation against a prototype is reserved for the follow-on implementation slice.
- The review does not enumerate every possible failure mode of the post-cut ChromaDB; the gap-analysis.md focuses on the most consequential failure modes the LO report identified plus those uncovered during current-state-analysis.

## Files Touched (target_paths recap)

- `.gtkb-state/design/chromadb-vector-continuity/` (new design-document evidence tree)

Plus bridge filing artifacts (workflow infrastructure, not implementation scope):
- `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-001.md` (this file)
- `bridge/INDEX.md` (entry update)
- `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-NNN.md` (post-impl report)

## Loyal Opposition Asks

1. Verify the `bridge_kind: governance_review` framing is appropriate for this scoping work (gap analysis + design contract production, no production code or substrate mutation), or NO-GO with guidance on the correct bridge_kind.
2. Confirm the deferred owner decisions enumeration (PROJECT-V1-RELEASE-STRATEGY-PREP creation, SPEC promotion, backfill implementation funding, substrate-agnostic vs ChromaDB-specific design) is complete.
3. Confirm that filing a governance-review proposal under a WI with no current project membership (WI-3395 standalone) is acceptable given the metadata-exempt bridge_kind, or recommend a temporary project assignment.
4. Confirm the design-document scope (five artifacts; no production code) is sufficient to land the design contract for owner review, or recommend additional artifacts.
5. Note any cross-cutting governance specs (beyond the cited set) that should be added to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
