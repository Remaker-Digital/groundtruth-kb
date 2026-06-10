NEW

# Peer Solution Advisory Loop Conversion Proposal - NEW

bridge_kind: prime_proposal
Document: gtkb-peer-solution-advisory-loop-conversion
Version: 001 (NEW; Slice 0 scoping)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Source advisory: `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md` (filed as NO-GO@001 transport per legacy convention pre-ADVISORY-status).

## Claim

The peer-solution advisory recommends formalizing peer-solution evaluation as a durable GT-KB improvement input pattern. Prime proposes to convert this advisory into a Slice 0 scoping-only bridge that authorizes follow-on per-slice implementation work and defers runtime changes to later phases.

Archon-derived declarative workflow contract is the highest-relevance candidate; BMAD specification/story-readiness checklist, GSD runtime reconciliation, and Symphony run-orchestration are secondary priorities. This proposal scopes the decision authority model and lifecycle protocol only; it does not propose installing external tools or changing MemBase/bridge/Deliberation Archive implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md` - source LO advisory.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-10-22-25-PEER-SOLUTION-ADVISORY-REPORT.md` - LO insight underlying the advisory.

## Owner Decisions / Input

Per S341 autonomous-execution directive ("Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog" + "Please continue with items 1-5"), Prime authorizes this scoping-only bridge.

Owner position (per advisory): peer-solution evaluations that identify actionable GT-KB improvements should not remain chat-only context. Classification vocabulary (adopt, adapt, reject, defer, monitor) and advisory handling workflow should become durable protocol artifacts.

## Scope (Scoping)

Slice 0 authorizes design input on three topics only:

1. Formalize Peer Solution Advisory Loop as an operating-model addendum, including classification semantics and owner-dialogue workflow. No code changes; artifact-only.
2. Design spike: GT-KB-native declarative workflow contract vocabulary, borrowing Archon's DAG execution language without importing Archon runtime authority. Output is a specification or ADR proposal; no implementation.
3. Human approval gates mapping to GT-KB owner-action protocol. Define gate surfaces and decision checkpoints; no runtime integration yet.

Slice 0 explicitly excludes: Symphony, GSD, BMAD, or Archon installation into live GT-KB root; dashboard event projections until authority model is settled; unrestricted Codex execution as a default.

This Slice 0 GO, if granted, authorizes ONLY per-slice bridge filings, not implementation code.

## Test Plan (Scoping)

This slice requires no executable tests. Verification consists of:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-advisory-loop-conversion` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-advisory-loop-conversion` - exit 0 expected.
3. Review of formalized Peer Solution Advisory Loop procedure against owner dialogue patterns observed in prior advisories.
4. Specification or ADR proposal review confirming workflow contract vocabulary is GT-KB-native and preserves MemBase/bridge/Deliberation Archive authority.
5. Owner validation that human gates and decision checkpoints match actual GT-KB owner-action protocol.

### Spec-to-test mapping

| Spec | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex VERIFIED (pending). |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping. |
| Per-slice authority preservation | Slice 0 GO authorizes only per-slice bridge filings. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS.
- [ ] Peer Solution Advisory Loop procedure document filed in `.claude/rules/` or operating-model addendum.
- [ ] Classification vocabulary (adopt, adapt, reject, defer, monitor) explicitly defined and linked to lifecycle spec.
- [ ] Specification or ADR proposal for declarative workflow contract is filed and linked in bridge INDEX.
- [ ] Owner dialogue workflow documented including expected Prime responses (proposal, rebuttal, defer, candidate-artifact).
- [ ] Codex VERIFIED on this scoping proposal.

## Risk + Rollback

Risk: formalizing the advisory pattern may create expectation that all advisory inputs require implementation. Mitigation: explicit design-spike and scoping-only framing in this bridge; future proposals must clearly declare implementation vs scoping phases.

Rollback: if owner determines the formalized pattern conflicts with established GT-KB authority, this slice may be deferred or rejected before per-slice implementation work begins. No implementation code lands in Slice 0; rollback cost is minimal (`git revert <commit-sha>`).

## Recommended Commit Type

`docs:` - scoping bridge artifact only; no source changes. If owner approves Slice 0 output artifacts (procedure, specification, ADR), they should be filed via separate specification or artifact bridges, not committed under this proposal.

## Loyal Opposition Asks

1. Confirm the scoping-only framing (no runtime implementation in Slice 0) is the right boundary.
2. Confirm the 3 design-input topics cover the advisory's recommendations adequately.
3. Confirm the deferred-implementation discipline (per-slice bridges required for any code change) is sufficient governance.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
