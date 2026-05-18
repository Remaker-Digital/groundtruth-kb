NEW

# Implementation Proposal - Bridge target_paths KB-Mutation Completeness Check

bridge_kind: implementation_proposal
Document: gtkb-bridge-target-paths-kb-mutation-check
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-18 UTC
Session: S358

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3372

target_paths: [".claude/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/**"]

## Problem

A bridge implementation proposal that requests MemBase / KB-mutation work - a spec version supersession, a Deliberation Archive record, a project retirement, a GOV/SPEC/ADR/DCL/PB version - must declare `groundtruth.db` in its `target_paths`, because the implementation-start gate classifies KB mutations as protected implementation work and blocks a `groundtruth.db` write that is outside the GO'd proposal's declared scope. No mechanical surface enforces this at proposal-authoring time.

The cost of the missing check was paid three times in one session. In S358, the W1, W2, and W3 governance-correction proposals were each filed with `target_paths` that declared the file-edit surfaces but omitted `groundtruth.db`, even though each proposal's own text declared MemBase mutations (W1: a project retirement plus a GOV v3 plus a provenance deliberation; W2: three GOV v2 inserts; W3: a GOV v4 insert). Codex NO-GO'd all three at `-002` for the identical defect. Both mandatory preflights passed on all three - the applicability preflight and the clause preflight check spec linkage and ADR/DCL clause evidence, not `target_paths` completeness against the proposal's own declared mutation surface - so nothing caught the defect before review. The Codex W2 and W3 verdicts each flagged the repeated pattern explicitly as an Opportunity Radar candidate: a deterministic check that, when proposal text declares MemBase/KB mutation, requires `groundtruth.db` in `target_paths`.

This is W4-class work: a mechanical bridge-gate calibration that removes a recurring false-negative in the proposal-authoring gate.

## Claim

Add a deterministic check to the bridge-compliance gate so a NEW or REVISED implementation proposal whose own text declares KB-mutation work, while omitting `groundtruth.db` from its declared `target_paths`, is surfaced at Write time rather than reaching Loyal Opposition review with the defect.

The check is deterministic (regex over a high-signal KB-mutation-declaration phrase set; no LLM classifier) and emits an `ask` checkpoint, not a `deny` hard block - consistent with the W4 IP-3 deny-to-ask philosophy for a class that can carry a false positive (a proposal may mention MemBase without mutating it). The author sees the confirmation, and either adds `groundtruth.db` to `target_paths` or confirms the proposal performs no KB mutation. Genuine non-KB-mutation proposals are not blocked.

## In-Root Placement Evidence

All target paths are in-root under the GT-KB project root: `.claude/hooks/`, `groundtruth-kb/templates/hooks/`, and `platform_tests/hooks/`. This bridge proposal file resides under the bridge directory. No target path is outside the GT-KB project root, and no application path under applications/ is touched. This proposal modifies hook source and adds tests; it performs no MemBase mutation, so `groundtruth.db` is correctly absent from its own `target_paths`.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - the bridge index and verdict files are canonical workflow state; the bridge-compliance gate enforces proposal-authoring discipline for that workflow, and this check is an addition to that gate.
- DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 - all directives must be mechanically enforced, not documentation-only. The implementation-start authorization metadata requirement (a proposal must declare every protected mutation surface in `target_paths`) is currently enforced only at review time by Loyal Opposition; this check adds the missing mechanical proposal-authoring-time enforcement.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal carries a complete, relevance-closed Specification Links section; the bridge-compliance gate this check extends is the Write-time enforcer of proposal-metadata completeness.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the post-implementation report will carry a spec-to-test mapping with executed-test evidence.
- SPEC-AUQ-POLICY-ENGINE-001 - the bridge-compliance gate participates in the deterministic AUQ policy engine; the new check keeps that surface deterministic and correctly scoped.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 - the check is deterministic (a regex over a fixed phrase set); it introduces no LLM classifier.
- GOV-RELIABILITY-FAST-LANE-001 - this fix meets the reliability fast-lane eligibility criteria (a small, bounded mechanical-gate calibration); it is filed under the standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING authorization by WI-3372's active membership in PROJECT-GTKB-RELIABILITY-FIXES, with no per-fix deliberation, PAUTH, or formal-artifact packet.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - this proposal carries the mandatory Project Authorization, Project, and Work Item header lines.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all target files are in-root; no application path is touched.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - the fix is preserved as durable artifacts: WI-3372, this proposal, the regression tests, and the post-implementation report.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the fix preserves traceability across the work item, proposal, tests, and report.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - WI-3372 moves through open, in-progress, and verified lifecycle states.

## Prior Deliberations

A Deliberation Archive search was performed for bridge-gate calibration, target_paths enforcement, and the reliability fast-lane.

- DELIB-S358-GOVERNANCE-CORRECTION-PROJECT-AUTHORIZATION - the owner-decision deliberation authorizing the S358 governance-correction project. The W1/W2/W3 proposals filed under it are the proposals that exposed the missing check; this follow-on is the deterministic-service answer to the recurring defect.
- DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION - the owner-decision deliberation establishing the reliability fast-lane and the standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING authorization. This proposal is filed under that fast-lane.

The motivating evidence is the three Codex NO-GO verdicts: `bridge/gtkb-s358-w1-retirement-machinery-correction-002.md`, `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-002.md`, and `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-002.md`, each NO-GO on the identical `groundtruth.db`-missing-from-`target_paths` defect, with the W2 and W3 verdicts naming the deterministic-check Opportunity Radar item.

No prior deliberation rejected or already addressed this check.

## Owner Decisions / Input

- 2026-05-18, S358: the owner approved, via AskUserQuestion ("File reliability-fix proposal now"), tracking the deterministic `target_paths`-completeness check as a reliability fast-lane follow-on after Codex flagged it on the W2/W3 NO-GO verdicts. WI-3372 was captured in the MemBase backlog and linked to PROJECT-GTKB-RELIABILITY-FIXES under that decision.
- This is a reliability fast-lane fix: the standing PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING authorization covers it by WI-3372's project membership, with no per-fix deliberation, PAUTH, or formal-artifact-approval packet. The change modifies hook source and adds tests - mutation classes the standing authorization permits ("source", "test_addition", "hook_upgrade"); it creates no GOV/SPEC/ADR/DCL/PB or Deliberation Archive artifact.

## Requirement Sufficiency

Existing requirements sufficient. The requirement the check enforces - that an implementation proposal declare every protected mutation surface, including `groundtruth.db` for KB mutations, in `target_paths` - is already in force (the implementation-start authorization metadata rule and DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001). This proposal adds mechanical proposal-authoring-time enforcement of that existing requirement; it creates, revises, or relaxes no requirement. No new or revised requirement is needed before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk standing-backlog operation. It is a single mechanical-gate calibration tracked by exactly one work item, WI-3372, an active member of PROJECT-GTKB-RELIABILITY-FIXES. No work-item state inventory, bulk transition, or backlog cleanup is performed. The proposal references the phrases "work item" and "backlog" only to identify WI-3372 and to describe the bridge-gate surface. The change is a single inventory-free hook calibration with covering tests.

## Bridge INDEX Update Evidence

A NEW entry for gtkb-bridge-target-paths-kb-mutation-check is inserted at the top of the bridge index, pointing at this -001 file. No prior bridge file and no prior index entry is deleted or rewritten.

## Proposed Scope

### IP-1: Add the KB-mutation target_paths-completeness check to the bridge-compliance gate

In `.claude/hooks/bridge-compliance-gate.py`, add a deterministic check that runs for NEW and REVISED implementation proposals. The check:

1. Detects whether the proposal text declares KB-mutation work, via a regex over a high-signal KB-mutation-declaration phrase set - candidates: "MemBase mutation(s)", "mutate(s) MemBase", "insert a version", "version N ... into MemBase", "Deliberation Archive record" in an insert/archive context, "retire ... project" in a MemBase context, "GOV/SPEC/ADR/DCL/PB ... supersession". The exact phrase set is settled in implementation; the invariant is that a proposal genuinely declaring a KB mutation is detected and a proposal that merely mentions MemBase in passing is not.
2. Parses the proposal's declared `target_paths` (the same `target_paths` line the implementation-start gate and the applicability preflight read).
3. When the proposal declares KB mutation AND `groundtruth.db` is absent from the declared `target_paths`, emits an `ask` checkpoint naming the defect and the fix (add `groundtruth.db` to `target_paths`, or confirm the proposal performs no KB mutation). It is an `ask`, not a `deny`: the detection can carry a false positive, and the W4 IP-3 deny-to-ask philosophy applies to a heuristic class.

Apply the byte-identical change to the scaffold template `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. The live hook and the template must remain byte-identical.

Sequencing: the S358 W4 enforcement-calibration thread (GO at `gtkb-s358-w4-enforcement-calibration-006`) and the `gtkb-bridge-compliance-gate-fenced-code-parser-fix` thread also modify `bridge-compliance-gate.py`. This check is non-conflicting in intent but must be sequenced: whichever lands later rebases on the others' landed changes.

### IP-2: Regression and preservation tests

Add test coverage under `platform_tests/hooks/`, extending the existing bridge-compliance-gate test module or adding a new module:

- False-negative removed: a NEW proposal whose text declares a KB mutation and whose `target_paths` omits `groundtruth.db` yields `ask`.
- Genuine-positive preserved: a NEW proposal that declares a KB mutation and includes `groundtruth.db` in `target_paths` is not flagged; a proposal that performs no KB mutation and merely mentions MemBase is not flagged.
- The check does not regress existing gate behavior: existing bridge-compliance-gate tests still pass.

### Out of scope

This proposal does not modify the applicability preflight or the clause preflight (the Opportunity Radar note offered the preflight as an alternative location; the Write-time gate is the earlier, stronger catch and is the selected single location). It does not change any existing gate check. It does not touch the W1/W2/W3/W4 governance-correction surfaces beyond the shared `bridge-compliance-gate.py` sequencing note.

## Specification-Derived Verification Plan

| Specification | Behavior verified | Test |
|---|---|---|
| DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 | A NEW/REVISED proposal declaring KB mutation without `groundtruth.db` in `target_paths` is mechanically surfaced (`ask`) at Write time | test_compliance_gate_kb_mutation_without_groundtruth_db_asks |
| DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001 | A proposal declaring KB mutation with `groundtruth.db` in `target_paths` is not flagged; a non-KB-mutation proposal mentioning MemBase is not flagged | test_compliance_gate_kb_mutation_with_groundtruth_db_passes, test_compliance_gate_membase_mention_only_not_flagged |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Existing bridge-compliance-gate behavior is unchanged for non-KB-mutation proposals | the existing bridge-compliance-gate regression tests still pass |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | The check is deterministic; no LLM classifier is introduced | the IP-2 cluster, deterministic fixtures |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | The post-implementation report carries this mapping with executed-test evidence | the post-implementation report |

Execution command (recorded in the post-implementation report): `python -m pytest platform_tests/hooks/ -v -k "compliance_gate"`, plus a `ruff` check over the changed files and a byte-identical confirmation of the live hook and its scaffold template.

## Acceptance Criteria

- The bridge-compliance gate emits `ask` for a NEW/REVISED proposal that declares KB mutation and omits `groundtruth.db` from `target_paths`.
- A proposal declaring KB mutation with `groundtruth.db` present, and a non-KB-mutation proposal mentioning MemBase, are not flagged.
- The live `bridge-compliance-gate.py` and its scaffold template remain byte-identical.
- The IP-2 tests pass; existing bridge-compliance-gate regression tests still pass; `ruff` is clean over the changed files.
- Both bridge preflights pass on the post-implementation report.

## Option Rationale

The Write-time bridge-compliance gate was selected over the applicability preflight as the check's single location: the gate runs at proposal Write time, the earliest point, and would have surfaced the W1/W2/W3 defect before the proposals were ever filed; the preflight is reviewer-run and later. An `ask` disposition was selected over `deny` because the KB-mutation detection is a heuristic over proposal prose and can false-positive; an `ask` removes the recurring NO-GO without introducing a recurring hard-block, the same calibration W4 IP-3 applied to heading misdetection. A single high-signal phrase-set regex was selected over a structural parse of the proposal's IP sections because the declaration of KB mutation is expressed in prose, not in a fixed structural field; the phrase set is the deterministic signal, and the exact set is tuned in implementation against the W1/W2/W3 proposal corpus.

## Risks / Rollback

- Risk: the KB-mutation detection false-positives on a proposal that mentions MemBase without mutating it. Mitigation: the disposition is `ask`, not `deny` - a false positive costs a confirmation, not a hard block; the IP-2 genuine-positive test locks the mention-only-not-flagged path.
- Risk: the detection misses a KB-mutation declaration phrased outside the phrase set. Mitigation: the check is a proposal-authoring-time floor, not a ceiling; Loyal Opposition review remains the backstop, exactly as it caught W1/W2/W3; the phrase set is tuned against the known corpus and can be widened by a later calibration.
- Risk: a merge conflict with the W4 or fenced-code-parser-fix changes to `bridge-compliance-gate.py`. Mitigation: the sequencing note in IP-1; whichever thread lands later rebases.
- Rollback: revert the two hook files and the test module; the check is a single self-contained function with no schema, configuration, or migration dependency.

## Recommended Commit Type

`feat` - the change adds a new deterministic enforcement check to the bridge-compliance gate, a net-new check surface (with covering tests). The post-implementation report will carry the recommended type matching the final diff stat per the Conventional Commits Type Discipline.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
