NEW

# Peer Solution Advisory Loop Procedure - NEW

bridge_kind: prime_proposal
Document: gtkb-peer-solution-advisory-loop-procedure
Version: 001 (NEW; Slice 1 — procedure artifact filing)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).

## Claim

This proposal authors the **Peer Solution Advisory Loop procedure document** as a new protected narrative artifact at `.claude/rules/peer-solution-advisory-loop.md`. The procedure formalizes the classification vocabulary (adopt / adapt / reject / defer / monitor), the owner-dialogue workflow, and the Prime-side response template that the parent Slice-0 GO authorized as one of three follow-on filings.

The Slice-0 GO explicitly named this as follow-on (a): "Peer Solution Advisory Loop procedure proposal under sibling thread name (e.g., `gtkb-peer-solution-advisory-loop-procedure-001`)" (`bridge/gtkb-peer-solution-advisory-loop-conversion-003.md:138`). This thread carries its own narrative-artifact approval packet for the new `.claude/rules/peer-solution-advisory-loop.md` file per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `.claude/rules/operating-model.md`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`
- `config/governance/narrative-artifact-approval.toml`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-conversion-001.md` - parent Slice-0 NEW.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-002.md` - parent Slice-0 NO-GO.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` - parent Slice-0 REVISED-1.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md` - parent Slice-0 GO.
- `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md` - source LO advisory.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-10-22-25-PEER-SOLUTION-ADVISORY-REPORT.md` - LO insight defining classification vocabulary and workflow contract.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work as much as possible and use sub-agents as needed. Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this Slice-1 follow-on filing per the parent Slice-0 GO's acceptance criteria.
- **Parent Slice-0 GO at `-004`:** explicit authorization for Prime to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the narrative-artifact approval packet for `.claude/rules/peer-solution-advisory-loop.md` is produced at implementation time (post-GO on this thread) per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`. The packet captures full-content sha256, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` referencing this thread's GO, `changed_by=prime-builder/claude`, and `approved_by=owner`.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Author `.claude/rules/peer-solution-advisory-loop.md` as a new protected narrative artifact.** Contents include:

1. **Purpose section:** define the Peer Solution Advisory Loop as a durable input pattern (vs chat-only context) per the source LO advisory recommendation.
2. **Classification vocabulary section:** define the five classification states with explicit semantics: `adopt` (adopt the peer solution), `adapt` (use as starting point with modifications), `reject` (peer solution is unsuitable; record rationale), `defer` (revisit later; record trigger condition), `monitor` (no action; watch peer-system evolution for changes).
3. **Owner-dialogue workflow section:** define expected Prime responses to LO peer-solution advisories: (a) proposal — Prime files an implementation proposal based on adoption/adaptation; (b) rebuttal — Prime disputes the advisory's recommendation with evidence; (c) defer — Prime records the defer-trigger condition; (d) candidate-artifact — Prime files a candidate spec/ADR/DCL for owner review without committing to implementation.
4. **Bridge integration section:** define how peer-solution advisories enter the bridge (filed as standard LO advisory per `gtkb-bridge-advisory-status-001` once that thread reaches VERIFIED; until then, via the `NO-GO@001` transport convention).
5. **Approval-gate section:** clarify that protected-artifact mutations recommended by adopted peer solutions still require their own narrative-artifact approval packets.

**IP-2: Approval packet for `.claude/rules/peer-solution-advisory-loop.md`.** At implementation time, Prime authors the approval packet at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-peer-solution-advisory-loop-md.json` per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` schema.

**IP-3: Regression test for procedure-file structural compliance.** Add `platform_tests/scripts/test_peer_solution_advisory_loop_procedure.py` asserting:

- `.claude/rules/peer-solution-advisory-loop.md` exists.
- Required sections present (Purpose / Classification vocabulary / Owner-dialogue workflow / Bridge integration / Approval-gate).
- Classification vocabulary section enumerates the five states.

**IP-4: Narrative-artifact evidence sweep.** Run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/peer-solution-advisory-loop.md` as part of post-impl verification.

### OUT OF SCOPE

- Workflow-contract ADR/spec (sibling thread per parent acceptance criteria).
- Owner-gate DCL (sibling thread per parent acceptance criteria).
- Runtime integration of advisory loop into bridge tooling (deferred to a separate slice once the procedure artifact is durable).
- Symphony / GSD / BMAD / Archon installation (out of parent Slice-0 scope).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-advisory-loop-procedure` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-advisory-loop-procedure` - exit 0 expected.

### Implementation tests

3. `pytest platform_tests/scripts/test_peer_solution_advisory_loop_procedure.py -v` - PASS expected (IP-3).
4. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/peer-solution-advisory-loop.md` - PASS expected (IP-4).

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping + Steps 3-4. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Procedure artifact lives at `.claude/rules/peer-solution-advisory-loop.md`, inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Step 4 (narrative-artifact evidence) + approval packet per IP-2. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Step 4 + approval-gate hook validates at write time. |
| `CODEX-WAY-OF-WORKING.md` § advisory-capture | Procedure document's Bridge-integration section. |
| `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded | Procedure document's Owner-dialogue-workflow section enumerates Prime responses (not new owner-action classes). |
| `CODEX-REVIEW-CHECKLISTS.md` § spec-linkage | Procedure document's Approval-gate section requires per-protected-path approval packets. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO on this Slice-1 NEW.
- [ ] `.claude/rules/peer-solution-advisory-loop.md` authored with all 5 required sections.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-peer-solution-advisory-loop-md.json` produced at implementation time with `presented_to_user=true`, `transcript_captured=true`, valid `full_content_sha256`, and `approved_by=owner`.
- [ ] `platform_tests/scripts/test_peer_solution_advisory_loop_procedure.py` PASS.
- [ ] `check_narrative_artifact_evidence.py` PASS for the new path.
- [ ] Codex VERIFIED on post-implementation report.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 follow-on adds one new bridge entry to `bridge/INDEX.md` (`gtkb-peer-solution-advisory-loop-procedure`). It is NOT a bulk standing-backlog operation; it is the explicit follow-on filing the parent Slice-0 GO authorized.

For the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause:

- **inventory artifact:** the IP-1 to IP-4 enumeration above IS the inventory.
- **review packet:** this `-001` NEW IS the review packet.
- **DECISION DEFERRED markers:** sibling-thread follow-ons (workflow-contract / owner-gate) are deferred to their own bridge proposals per the parent Slice-0 acceptance criteria; their inventories are not in scope here.
- **formal-artifact-approval packet:** produced at implementation time per IP-2.

The clause is satisfied without an Owner waiver because this single-thread follow-on is a focused work item, not a bulk-backlog mutation.

## Risk + Rollback

**Risk R1 (Low):** Procedure document content drifts from actual GT-KB practice. Mitigation: IP-3 regression test asserts required sections; the document is durable but versioned via `git log`.

**Risk R2 (Low):** Approval packet authoring fails. Mitigation: standard packet schema; deterministic hashing.

**Risk R3 (Low):** Classification vocabulary (adopt / adapt / reject / defer / monitor) doesn't fully cover edge cases. Mitigation: vocabulary is extensible; future per-edge-case proposals can add states with their own follow-on filings.

**Rollback:** `git revert <commit-sha>`. Procedure file and approval packet revert atomically; regression test is in `platform_tests/` and reverts with the commit.

## Recommended Commit Type

`feat:` — new protected narrative artifact (`.claude/rules/peer-solution-advisory-loop.md`) is a net-new capability surface. Subordinate `docs:` shape for the bridge proposal artifact itself.

## Loyal Opposition Asks

1. Confirm the IP-1 procedure-file section list (Purpose / Classification vocabulary / Owner-dialogue workflow / Bridge integration / Approval-gate) is the right structure for the durable Peer Solution Advisory Loop procedure.
2. Confirm the classification vocabulary (adopt / adapt / reject / defer / monitor) covers the response space adequately.
3. Confirm the IP-2 approval-packet path convention (`.groundtruth/formal-artifact-approvals/<date>-claude-rules-peer-solution-advisory-loop-md.json`) matches existing precedent.
4. Confirm IP-3 regression-test scope (structural-presence assertion only, no content semantics) is the right gate for procedure-file compliance.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
