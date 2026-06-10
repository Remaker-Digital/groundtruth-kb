REVISED
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-05-27-prime-builder-bridge-continuation
author_model: GPT-5
author_model_version: codex
author_model_configuration: reasoning=medium
author_metadata_source: session

# Revised Governance-Review Proposal - ChromaDB Vector Continuity at v1.0 Identifier-Reset Cut

bridge_kind: governance_advisory
Document: gtkb-chromadb-vector-continuity-v1-cut-scoping
Version: 003 (REVISED)
Date: 2026-05-27 UTC

Implements: WI-3395 (ChromaDB semantic-history backfill design for v1.0 identifier-reset cut)
Work Item: WI-3395
target_paths: ["docs/design/chromadb-vector-continuity/"]
Recommended commit type: docs

## Revision Claim

This revision addresses the NO-GO findings in `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-002.md` by moving the five design-contract artifacts from ignored runtime state under `.gtkb-state/` to a tracked durable in-root location under `docs/design/chromadb-vector-continuity/`, and by adding `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` to the governing specification and verification mapping.

## Bridge INDEX Audit Trail

This artifact is filed under `bridge/`. The live `bridge/INDEX.md` entry for this document is the canonical queue state. This revision adds:

`REVISED: bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-003.md`

No prior bridge versions are deleted or rewritten. The prior chain remains:

- `NO-GO: bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-002.md`
- `NEW: bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-001.md`

## Summary

This is a `bridge_kind: governance_review` proposal. Its scope is governance gap analysis plus a design contract for ChromaDB semantic-history continuity across the proposed v1.0 identifier-reset cut. The proposal does not create live backfill code, mutate ChromaDB, mutate MemBase, or execute any production-affecting action.

The originating signal is Finding 3 of `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-08-52-V1-RELEASE-STRATEGY-REVIEW.md`: the v1-release-strategy-deliberation-S347 Option A identifier-translation manifest is a textual mapping artifact, while the ChromaDB semantic vectors at `.groundtruth-chroma/` are bound to old DELIB/SPEC IDs and will not follow a text manifest. Vector continuity requires a database backfill design, not only a text translation table.

The governance-review deliverable is a tracked design document tree under `docs/design/chromadb-vector-continuity/<UTC-timestamp>/`. It specifies the HIST-DELIB-NNNN backfill contract at enough depth to evaluate v1.0-cut feasibility without writing production code or mutating the live ChromaDB substrate.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - design evidence is written to in-root `docs/design/chromadb-vector-continuity/`; no out-of-root paths touched.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this governance-review proposal cites the governing specification surfaces and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each governing surface to a verification step appropriate for governance-review delivery.
- `SPEC-2098` - Deliberation Archive specification; the v1.0 vector-continuity question is a SPEC-2098 amendment surface.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the design document produced by this review is a durable governed artifact under change control.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved between WI-3395, this thread, the design document, and any follow-on implementation proposal.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3395 advances from backlog candidate to lifecycle-tracked governance-review scope; implementation lifecycle remains deferred.
- `GOV-STANDING-BACKLOG-001` - WI-3395 was captured as a standalone backlog candidate; project membership decision is deferred.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` - candidate requirements discovered by the review remain candidates until owner-approved spec intake promotes them.

## Requirement Sufficiency

The governance-review deliverable itself does not require new formal requirements. It will surface candidate requirements for HIST-DELIB-NNNN identifier semantics, vector-regeneration triggers, and search-API backward-compatibility expectations. Those candidates must remain explicitly marked as candidates until a follow-on owner-approved spec-intake workflow promotes them under `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

## KB Mutation Scope

This proposal performs no MemBase mutation and does not write to `groundtruth.db`. The review work produces a tracked design document tree at `docs/design/chromadb-vector-continuity/<UTC-timestamp>/` plus supporting analysis files. No formal SPEC, project, or work-item lifecycle mutation occurs during this governance review. `.groundtruth-chroma/` is read-only inspection input and is not mutated.

## WI Citation Disclosure

The proposal declares review work for WI-3395 only. References to the LO report and to `memory/v1-release-strategy-deliberation-S347.md` are originating-source citations, not implementation-scope expansions.

## Prior Deliberations

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-08-52-V1-RELEASE-STRATEGY-REVIEW.md` - Finding 3 identified the ChromaDB vector-continuity gap.
- `memory/v1-release-strategy-deliberation-S347.md` - Section 8.4 identifies the v1.0 identifier-reset risk and proposes a text translation manifest, but does not address ChromaDB vector continuity.
- `SPEC-2098` - Deliberation Archive feature spec.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - future backfill belongs in deterministic service tooling if approved.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` - v1.0 lifecycle independence makes vector continuity load-bearing.

## Owner Decisions / Input

- Owner direction 2026-05-27: "Please proceed: ... advance Finding 3 to a bridge proposal ..." authorized advancing Finding 3 of the LO report to bridge proposal scope.
- Owner direction earlier in the same evaluation: "I agree" accepted the Prime evaluation that Finding 3 deserved bridge proposal treatment before any v1.0 ID-reset cut work begins.

Deferred owner decisions:

- Whether to create PROJECT-V1-RELEASE-STRATEGY-PREP as a host project for v1.0 strategic-prep work.
- Whether the design-document contents should be promoted to a formal `SPEC-CHROMADB-VECTOR-CONTINUITY-001` or similar through `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.
- Whether to fund and execute a HIST-DELIB-NNNN backfill implementation.
- Whether follow-on implementation should remain ChromaDB-specific or become substrate-agnostic.

## Implementation Plan

The governance-review work produces five tracked evidence artifacts under `docs/design/chromadb-vector-continuity/<UTC-timestamp>/`:

1. `current-state-analysis.md`
   - Document current ChromaDB store contents: collection names, embedded-document counts, embedding model versions, metadata schema, and ID conventions.
   - Document the binding between DELIB-NNNN IDs in MemBase and ChromaDB document IDs.
   - Document the ChromaDB query API surface currently consumed by `gt deliberations search`, `search_deliberations()`, and session-start hooks.

2. `gap-analysis.md`
   - Enumerate concrete failure modes of an identifier-reset cut without vector backfill.
   - Quantify lost provenance surface: DELIB IDs, bridge citations, memory citations, and rule citations.
   - Identify consumers of vector search that would degrade.

3. `design-contract.md`
   - Specify the HIST-DELIB-NNNN identifier convention.
   - Specify backfill input/output contract and operation semantics.
   - Specify search-API behavior for current-only, history-only, and combined search.
   - Specify rollback and verification approach.

4. `risk-and-blast-radius.md`
   - Enumerate embedding-model drift, ID collision, storage cost, and derived-index integrity risks.
   - Map each risk to mitigation.

5. `recommended-followon.md`
   - Recommend candidate formal specs, test plan, follow-on bridge thread naming, and sequencing relative to the v1.0 cut.
   - Mark all requirement candidates as not approved until follow-on owner-approved spec intake occurs.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This revision is filed at `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-003.md` and inserted in `bridge/INDEX.md`. | PASS - bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Review evidence directory is `docs/design/chromadb-vector-continuity/` under `E:\GT-KB`. | PASS - all in-root. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-chromadb-vector-continuity-v1-cut-scoping`. | PASS before LO review. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps specs to verification; post-implementation report records observed results. | PASS - mapping present. |
| `SPEC-2098` | `design-contract.md` identifies which Deliberation Archive behavior the backfill design extends, supersedes, or leaves unchanged. | PASS at post-implementation review. |
| `GOV-STANDING-BACKLOG-001` | WI-3395 remains the cited backlog item and no unrelated work item is claimed. | PASS - work-item scope preserved. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tracked design-document artifacts plus bridge audit trail preserve durable traceability. | PASS - design contract is tracked. |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | `recommended-followon.md` marks discovered requirements as candidates and defers formal SPEC promotion to owner-approved spec intake. | PASS - no candidate requirement is treated as approved. |

## Acceptance Criteria

- Loyal Opposition returns GO on this governance-review proposal.
- `docs/design/chromadb-vector-continuity/<UTC-timestamp>/` exists and contains the five Markdown evidence files.
- `current-state-analysis.md` enumerates current ChromaDB contents and DELIB-ID-to-ChromaDB-ID binding.
- `gap-analysis.md` enumerates concrete failure modes of an identifier-reset cut without vector backfill.
- `design-contract.md` specifies HIST-DELIB-NNNN convention, input/output contracts, search-API behavior, rollback story, and verification approach.
- `risk-and-blast-radius.md` enumerates risks and mitigations.
- `recommended-followon.md` provides next-step recommendations and explicitly marks candidate requirements as awaiting owner-approved spec intake.
- No production code is created, modified, or deleted.
- `.groundtruth-chroma/` is not mutated.
- `groundtruth.db` is not mutated.
- Loyal Opposition returns VERIFIED on the post-implementation report before any follow-on implementation bridge is filed.

## Risk And Rollback

Risk is low. The review is read-only against production substrates; design output is a tracked documentation artifact under `docs/design/chromadb-vector-continuity/`.

Rollback: delete the specific timestamped design-document tree and file a bridge follow-up explaining why the governance review output was withdrawn. No production or KB substrate state requires rollback.

## Required Revision Response

- Finding 1, durable design contract path: addressed by changing target paths and implementation outputs to `docs/design/chromadb-vector-continuity/`.
- Finding 2, missing approval workflow link: addressed by adding `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` to Specification Links and the Spec-to-Test Mapping.

## Pre-Filing Preflights

Prime will file this revision with the bridge helper so candidate applicability and ADR/DCL clause preflights run before the live `bridge/INDEX.md` update.
