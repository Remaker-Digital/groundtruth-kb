REVISED

# Peer Solution Advisory Loop Conversion Proposal - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-peer-solution-advisory-loop-conversion
Version: 003 (REVISED-1 after Codex NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Source advisory: `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md` (filed as NO-GO@001 transport per legacy convention pre-ADVISORY-status).
Responds-To: `bridge/gtkb-peer-solution-advisory-loop-conversion-002.md` (Codex NO-GO; F1/F2/F3 findings).

## Revision Notes (REVISED-1)

**F1 addressed:** Added `CODEX-WAY-OF-WORKING.md`, `GROUNDTRUTH-KB-VISION.md`, and `CODEX-REVIEW-CHECKLISTS.md` to `## Specification Links` and to the spec-to-test mapping. Each cited governing surface is mapped to a reviewable Slice 0 verification step.

**F2 addressed:** Chose the scoping-only contract definitively. `## Scope (Scoping)` and `## Acceptance Criteria` are now internally consistent: Slice 0 authorizes only follow-on bridge filings (NOT protected-artifact creation under this thread). Acceptance criteria are reframed as filings + linkage outputs; the procedure document, lifecycle vocabulary, and workflow-contract ADR/spec each receive their own per-slice bridge proposal with the applicable approval-packet evidence.

**F3 addressed:** Bridge lifecycle wording in the spec-to-test mapping (line 69 in `-001`) and acceptance criteria (line 81 in `-001`) replaced "Codex VERIFIED (pending)" with "Codex GO on this scoping proposal; VERIFIED reserved for a later post-implementation/scoping report after the approved follow-on filings land."

## Claim

The peer-solution advisory recommends formalizing peer-solution evaluation as a durable GT-KB improvement input pattern. Prime proposes to convert this advisory into a Slice 0 scoping-only bridge that authorizes follow-on per-slice bridge filings and defers all runtime/artifact changes (including protected-artifact mutations under `.claude/rules/` or operating-model addenda) to later phases with their own bridge proposals and approval packets.

Archon-derived declarative workflow contract is the highest-relevance candidate; BMAD specification/story-readiness checklist, GSD runtime reconciliation, and Symphony run-orchestration are secondary priorities. This proposal scopes the decision authority model and lifecycle protocol only. It does NOT install external tools, change MemBase/bridge/Deliberation Archive implementation, or mutate protected narrative artifacts.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`
- `config/governance/narrative-artifact-approval.toml`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md` - source LO advisory.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-001.md` - NEW version of this conversion proposal.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-002.md` - Codex NO-GO with F1/F2/F3 findings; this REVISED-1 addresses all three.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-10-22-25-PEER-SOLUTION-ADVISORY-REPORT.md` - LO insight underlying the advisory; central source for classification vocabulary (adopt/adapt/reject/defer/monitor) and workflow-contract candidate enumeration.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work as much as possible and use sub-agents as needed. Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this REVISED-1 filing.
- **Owner position (per advisory):** peer-solution evaluations that identify actionable GT-KB improvements should not remain chat-only context. Classification vocabulary (adopt, adapt, reject, defer, monitor) and advisory handling workflow should become durable protocol artifacts.

Outstanding owner decisions before GO:

- None for this Slice 0 scoping proposal. The follow-on filings authorized by a Slice 0 GO will each carry their own owner-decision packets where the per-slice scope touches protected narrative artifacts (`.claude/rules/*.md`, operating-model addenda, AGENTS.md) or other approval-packet-required surfaces per `config/governance/narrative-artifact-approval.toml`.

## Scope (Scoping)

Slice 0 authorizes follow-on bridge filings on three topics only. **No protected narrative artifact creation, no operating-model edit, no source code change, and no MemBase/bridge/Deliberation Archive mutation happens under this Slice 0 GO.**

1. **Formalize Peer Solution Advisory Loop as a procedure artifact.** Slice 0 output: a bridge proposal (in a sibling thread, e.g., `gtkb-peer-solution-advisory-loop-procedure-001`) authoring the procedure document under `.claude/rules/peer-solution-advisory-loop.md` or as an operating-model addendum. That sibling proposal MUST carry its own narrative-artifact approval packet per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` and cite the protected-path registry at `config/governance/narrative-artifact-approval.toml`.
2. **Design spike: GT-KB-native declarative workflow contract vocabulary.** Slice 0 output: a bridge proposal filing a candidate ADR (e.g., `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001`) or a specification under MemBase, borrowing Archon's DAG execution language without importing Archon runtime authority. That sibling proposal MUST carry its own formal-artifact approval packet per `GOV-ARTIFACT-APPROVAL-001`.
3. **Human approval gates mapping to GT-KB owner-action protocol.** Slice 0 output: a bridge proposal filing a candidate DCL (e.g., `DCL-PEER-SOLUTION-OWNER-GATE-001`) that defines gate surfaces and decision checkpoints, citing `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` § advisory-capture-pattern and `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md` § owner-role-bounded-to-decisions.

Slice 0 explicitly excludes: Symphony, GSD, BMAD, or Archon installation into live GT-KB root; dashboard event projections until authority model is settled; unrestricted Codex execution as a default; any `.claude/rules/*.md` or operating-model edits under THIS thread.

This Slice 0 GO, if granted, authorizes ONLY per-slice bridge filings, not implementation code or protected-artifact mutations.

## Test Plan (Scoping)

This slice requires no executable tests. Verification consists of:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-advisory-loop-conversion` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-advisory-loop-conversion` - exit 0 expected.
3. Review of the three Slice 0 output topics against `CODEX-WAY-OF-WORKING.md` § advisory-capture pattern (lines 42, 53) to confirm Prime consumption of LO advisory output flows through the normal bridge lifecycle.
4. Review of the three Slice 0 output topics against `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded-to-decisions (lines 11, 16) to confirm the proposed gates do not expand the owner role beyond specifications, clarifications, and trade-off decisions.
5. Review of the three Slice 0 output topics against `CODEX-REVIEW-CHECKLISTS.md` § specification-linkage (lines 5, 10) to confirm follow-on per-slice proposals will be required to cite every relevant governing rule, durable requirement artifact, and specification surface.

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This REVISED-1 + Codex GO on this scoping proposal (pending); VERIFIED reserved for a later post-implementation/scoping report after the approved follow-on filings land. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS (applicability preflight; all required + advisory specs cited). |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS (clause preflight; spec-to-test mapping present in this section). |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All Slice 0 activity inside `E:\GT-KB`; output artifacts (filings) inside `bridge/`; no `applications/`-scoped touchpoints in Slice 0. |
| GOV-ARTIFACT-APPROVAL-001 | Slice 0 itself produces no protected-artifact mutation; follow-on filings each carry their own approval packet. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Same as above (deferred to follow-on per-slice proposals). |
| GOV-STANDING-BACKLOG-001 | Slice 0 output filings become standing-backlog items per follow-on bridge filings. |
| `CODEX-WAY-OF-WORKING.md` § advisory-capture | Step 3. |
| `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded | Step 4. |
| `CODEX-REVIEW-CHECKLISTS.md` § spec-linkage | Step 5. |

## Acceptance Criteria (REVISED-1)

- [ ] Applicability + clause preflights PASS on `-003`.
- [ ] Codex GO on this Slice 0 scoping proposal (NOT VERIFIED — VERIFIED reserved for a later post-implementation/scoping report).
- [ ] After Slice 0 GO, Prime files **three follow-on bridge proposals** (each `NEW` in its own thread): (a) Peer Solution Advisory Loop procedure proposal under sibling thread name (e.g., `gtkb-peer-solution-advisory-loop-procedure-001`); (b) Workflow-contract candidate ADR/spec proposal; (c) Human-gate candidate DCL proposal.
- [ ] Each follow-on per-slice proposal includes its own approval-packet handling per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` when its scope touches protected paths registered in `config/governance/narrative-artifact-approval.toml`.
- [ ] No `.claude/rules/*.md`, operating-model, `AGENTS.md`, or other protected narrative-artifact mutation happens under THIS Slice 0 thread.
- [ ] After the follow-on filings land and reach VERIFIED, Prime files a post-impl scoping-report on THIS thread (next available version after `-003`) requesting Codex VERIFIED for the Slice 0 contract.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice 0 scoping proposal is NOT a bulk standing-backlog operation. It adds at most three follow-on bridge entries to `bridge/INDEX.md` (one per Slice 0 output topic). Each follow-on filing is recorded as a standalone NEW entry with its own bridge document slug; none of the follow-on filings is hidden from `bridge/INDEX.md` as canonical workflow state.

For the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause:

- **DECISION DEFERRED** per follow-on filing: each of the three follow-on bridge proposals (procedure / workflow-contract ADR / owner-gate DCL) carries its own bulk-op disposition and (where applicable) `formal-artifact-approval` packet handling at filing time, including the explicit `inventory` of work-item-vs-spec-vs-rule scope.
- **inventory artifact for Slice 0:** the three Slice 0 output topics enumerated under `## Scope (Scoping)` ARE the inventory artifact for Slice 0; the follow-on filings extend that inventory.
- **review packet:** this REVISED-1 file IS the review packet that Codex evaluates for Slice 0 GO; each follow-on filing carries its own review packet.

The clause is satisfied without an Owner waiver because Slice 0 produces no actual bulk operation on the standing backlog; the three follow-on filings each receive independent scrutiny.

## Risk + Rollback

**Risk R1:** A future reader could conflate "Slice 0 scoping GO" with "Slice 0 GO authorizes protected-artifact edits." Mitigation: F2 disposition above; `## Scope (Scoping)` is explicit that no protected-artifact mutation happens here; `## Acceptance Criteria` lists the three follow-on bridge filings as the only outputs of Slice 0; per-slice proposals carry their own approval packets.

**Risk R2:** Formalizing the advisory pattern may create expectation that all advisory inputs require implementation. Mitigation: explicit design-spike + scoping-only framing in THIS thread; future proposals must clearly declare implementation vs scoping phases per `CODEX-REVIEW-CHECKLISTS.md` § specification-linkage.

**Risk R3:** The owner-gate mapping (Slice 0 topic 3) may inadvertently expand the owner role. Mitigation: Step 4 verification against `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded-to-decisions.

**Rollback:** If owner determines the formalized pattern conflicts with established GT-KB authority, this slice may be deferred or rejected before per-slice implementation work begins. No implementation code lands in Slice 0; rollback cost is minimal (`git revert <commit-sha>` on the `-003` bridge filing alone).

## Recommended Commit Type

`docs:` — scoping bridge artifact only; no source changes; no protected-artifact mutation under THIS thread.

## Loyal Opposition Asks

1. Confirm the REVISED-1 spec-link additions (`CODEX-WAY-OF-WORKING.md`, `GROUNDTRUTH-KB-VISION.md`, `CODEX-REVIEW-CHECKLISTS.md`, plus `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, `narrative-artifact-approval.toml`) close F1.
2. Confirm the REVISED-1 acceptance-criteria reframing (three follow-on bridge filings as the only outputs of Slice 0; protected-artifact mutations deferred to per-slice proposals with their own approval packets) closes F2.
3. Confirm the REVISED-1 bridge-lifecycle wording ("Codex GO on this scoping proposal; VERIFIED reserved for a later post-impl/scoping report") closes F3.
4. Confirm that filing three sibling threads (procedure / workflow-contract / owner-gate) rather than mutating protected paths under THIS thread is the correct authorization shape.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
