NEW

# WI-5219 - Exclude inactive harnesses from release-blocking Phase 2 parity evaluation

bridge_kind: prime_proposal
Document: gtkb-wi5219-phase2-active-harness-population
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-13 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5474-93a6-7f70-8e54-d6d8b0a31bb4
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex desktop interactive Prime Builder; build activity; full GT-KB governance

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5219-PHASE2-ACTIVE-POPULATION-20260712
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5219

target_paths: ["scripts/harness_parity_phase2.py", "platform_tests/scripts/test_harness_parity_phase2.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The read-only Phase 2 parity baseline reports `FAIL` because the evaluator
iterates every registry row and treats suspended Goose G as a release-blocking
active capability gap. Goose was deliberately replaced by Alibaba H and is not
part of the owner-requested A/B/C/D/F/H role-fitness population. The
`harness-parity-review` contract likewise defines parity over active harnesses.

Filter release-fitness cells and candidate work to active registry rows while
retaining a truthful excluded-harness inventory in the report. Active harness
evaluation, typed waivers, release-blocking classification, and every D/F/H
runtime allowance remain unchanged.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - parity measures role-equivalent capability for the selected active fleet.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - active harness gaps remain mechanically visible and blocking where required.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - lifecycle state determines which installed harnesses are current role-fitness subjects.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the correction requires the canonical proposal, verdict, report, and verification chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing parity requirements are linked before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - exact project, work item, PAUTH, and targets are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - post-implementation verification must execute the mapped lifecycle-population tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the baseline failure is preserved as a governed defect rather than silently ignored.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - WI, TEST, PAUTH, bridge evidence, implementation, and verification remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - a false release blocker in a required parity phase triggers correction.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both targets and all evidence remain in the GT-KB root.

## Prior Deliberations

- `DELIB-202666173` - complete genuine A/B/C/D/F/H proof, correct every discovered defect, and finish both parity phases.
- `DELIB-20260708-REPLACE-GOOSE-WITH-ALIBABA-CLOUD-STUDIO-HARNESS` - replace Goose G with Alibaba H rather than treating G as an active parity subject.
- `INTAKE-da01f846` - lifecycle state and dispatchability are distinct; this proposal filters role-fitness population by lifecycle without changing eligibility.

## Owner Decisions / Input

- `DELIB-202666173` supplies owner authority to correct defects discovered while completing the requested parity phases.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5219-PHASE2-ACTIVE-POPULATION-20260712` limits mutation to the evaluator, its focused tests, and this governed lifecycle.

## Requirement Sufficiency

Existing requirements sufficient - `ADR-CROSS-HARNESS-PARITY-001`,
`DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`, and the active-harness population
stated by the managed parity-review contract define the correction without a
new specification.

## Proposed Scope

- Partition registry rows into active evaluated harnesses and non-active excluded inventory.
- Build parity cells, release blockers, and candidate work only from active harnesses.
- Report excluded harness ID, name, lifecycle status, and role without classifying it as supported, blocked, or waived.
- Keep malformed active rows fail-closed; do not interpret missing/unknown lifecycle state as active.
- Preserve active harness eligibility reporting, waiver behavior, dimensions, and strict-mode exit semantics.
- Do not edit the registry, dispatcher rules, lifecycle states, routes, models, or generous worker allowances.

## Spec-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| Active-fleet parity carriers | Add suspended, inactive, and retired fixture rows beside active rows | Excluded rows create no evaluation cells, release blockers, waivers, or candidate work. |
| Truthful inventory | Inspect JSON/Markdown report metadata | Excluded rows remain visible with ID, name, status, and roles. |
| Fail-closed lifecycle | Add missing/unknown lifecycle fixture coverage | Non-active/invalid rows cannot silently enter the active role-fitness population. |
| Active-gap enforcement | Retain an active harness with a genuine required gap | Report remains FAIL and candidate work remains present. |
| Regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short` | Focused suite passes. |
| Fleet parity | `groundtruth-kb/.venv/Scripts/python.exe scripts/harness_parity_phase2.py --project-root . --format markdown` | Retired Goose no longer creates false release blockers; any remaining active gaps are truthful. |
| Static parity/discovery | Run Phase 1 and discovery diff | No new active-fleet catalog or hook asymmetry. |

## Acceptance Criteria

- Suspended, inactive, retired, missing-status, and unknown-status rows do not generate Phase 2 fitness cells or candidate work.
- Excluded rows remain visible in a dedicated report collection and count.
- Every active harness remains fully evaluated through the existing dimensions and waiver registry.
- A genuine active release-blocking gap still yields `FAIL` and strict-mode failure.
- The current suspended Goose G false release blockers disappear without a registry edit or waiver.
- Both target paths are clean at implementation start and the focused commit contains no foreign hunks.

## Risk / Rollback

The primary risk is hiding a malformed row by treating it as inactive. The
report therefore retains excluded rows and their raw lifecycle status, while
only the explicit canonical token `active` enters fitness evaluation. Rollback
reverts the two target paths in one focused commit; no registry state changes.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5219-phase2-active-harness-population`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects a false release-blocking Phase 2 result caused by lifecycle-population drift.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
