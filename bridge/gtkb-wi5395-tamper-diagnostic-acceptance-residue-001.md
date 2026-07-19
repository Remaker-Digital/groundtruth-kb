NEW

# WI-5395 - Close the falsely reconciled tamper-diagnostic residue

bridge_kind: prime_proposal
Document: gtkb-wi5395-tamper-diagnostic-acceptance-residue
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5395

target_paths: ["groundtruth-kb/src/groundtruth_kb/modernization/workflow.py", "platform_tests/scripts/test_modernization_workflow_diagnostics.py"]

implementation_scope: stable workflow error classification and focused regression only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Close the physical and acceptance residue left after WI-5367 was reconciled as
resolved from terminal workflow metadata. The exact frozen end-to-end command
still reports three failures, including the same tampered-session case WI-5367
was meant to repair. The workflow still forwards the internal validator error,
and the proposed focused diagnostics module does not exist.

Preserve the strengthened session-envelope validator while restoring the stable
public distinction between a missing runtime session and a present-but-invalid
authoritative session document. Classify from exact document state, never from
exception prose, and retain the original exception as the chained cause.

The workflow source remains a pre-existing untracked WI-5315 candidate absent
from HEAD. Implementation is prohibited until WI-5315's exact four-file
baseline is independently VERIFIED and mechanically finalized. The frozen
acceptance module remains foreign baseline evidence and is not a WI-5395 target.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` - contradictory role provenance remains
  fail-closed while the public workflow error is normalized.
- `ADR-ENVELOPE-META-MODEL-001` - the per-session document is authoritative
  runtime envelope evidence.
- `DCL-ENVELOPE-META-MODEL-001` - invocation, role, and payload provenance must
  remain coherent and attributable.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - the public behavior is identical for any
  valid harness identity.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - missing and contradictory
  authority require deterministic failure classes.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the unchanged
  frozen acceptance assertion remains executable and blocking.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - no validator, provenance field,
  or fail-closed boundary may be weakened.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - terminal metadata cannot
  substitute for a passing frozen release activity.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5315 baseline finalization is a
  hard predecessor.
- `GOV-WORK-TREE-HYGIENE-001` - completion requires physical hunk closure
  without absorbing foreign untracked files.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - WI-5367 history, current failure,
  successor patch, tests, verdict, and finalization remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - terminal review evidence that
  contradicts live acceptance creates a successor correction.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the contradiction is preserved as
  hygiene work rather than hidden.
- `GOV-STANDING-BACKLOG-001` - WI-5395 owns the remaining acceptance residue.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project scope does not waive
  GO, claim, start, verification, or Git gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - live authority
  is rechecked before protected mutation.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED are mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the exact source,
  test, predecessor, and governing requirements are explicit.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work
  item, and exact targets are declared.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification executes
  missing, tampered, wrong-session, chained-cause, and frozen acceptance cases.

## Prior Deliberations

- `DELIB-202666274` - supplies project-scoped modernization authority while
  preserving independent review, predecessor, and exact Git gates.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - explains the
  metadata-based reconciliation that resolved WI-5367; WI-5386 separately owns
  strengthening that general reconciler rule.
- Owner directive, 2026-07-16 - flawed audit trails deserve correction but do
  not block unrelated modernization work.
- WI-5315 - owns the exact untracked workflow baseline.
- WI-5367 - preserves the original repair design and terminal history.
- WI-5386 - owns the general physical-residue reconciliation defect.

## Owner Decisions / Input

No new owner decision is required. The owner authorized the modernization
program and standing hygiene capture. This proposal does not mutate the
database, frozen acceptance baseline, dispatcher, TAFE, routing, harness roles,
eligibility, credentials, Git index, commit history, deployment, or release.

## Requirement Sufficiency

Existing requirements are sufficient. The frozen diagnostic contract and
current fail-closed envelope requirements already determine the result.

## Proposed Scope

1. Fail closed unless WI-5315 is independently VERIFIED and its exact four-file
   baseline is present in the committed parent.
2. Add a private read-only helper that determines whether the exact requested
   session document exists under canonical bounded session directories without
   interpolating untrusted input into a path.
3. Catch the typed session-envelope validation exception separately from
   unrelated I/O or value failures.
4. If the exact requested document exists but validation fails, raise the
   stable authoritative-provenance conflict and chain the original exception.
5. If the exact document does not exist, retain the pre-existing-runtime-session
   error and chain the original exception.
6. Never classify by matching or rewriting internal exception text.
7. Add the focused test module for present-invalid, missing, wrong-session,
   chained-cause, and no-workspace-mutation behavior.
8. Rerun the unchanged frozen tamper case and full end-to-end activity.
9. Exclude WI-5178 PAUTH/start-packet failures and every unrelated byte.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| WI-5315 predecessor; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Confirm the exact four-file baseline is committed before claim/start. | WI-5395 owns only a source hunk plus its new focused test. |
| `DCL-SESSION-ROLE-RESOLUTION-001`; envelope meta-model | Create the exact requested document and inject typed validation failure. | Public error states authoritative provenance conflict; original exception is chained. |
| Missing-session contract | Inject the same typed failure with no exact requested document. | Existing pre-existing-runtime-session error remains unchanged. |
| Exact identity and traversal safety | Create only another session ID and exercise malformed IDs. | Unrelated or unsafe input cannot satisfy document presence or escape bounded enumeration. |
| Frozen enforcement | Run the unchanged tamper test and full end-to-end activity. | Tamper case passes; only the two separately owned WI-5178 failures may remain. |
| Scope and hygiene | Run focused diagnostics, exact diff check, and independent review. | Only two target paths contain WI-5395 changes; VERIFIED precedes finalization. |

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5395; exact AT-END-TO-END-WORKFLOW rerun on 2026-07-17; WI-5367 metadata-only reconciliation","canonical_authority":"DCL-SESSION-ROLE-RESOLUTION-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"typed validation failure plus exact authoritative session-document presence","before_behavior":"A present tampered session is rejected safely but leaks an internal role-field conflict, the frozen public diagnostic fails, and the prior work item appears resolved.","after_behavior":"The same tamper is rejected at the same boundary with a stable authoritative-provenance conflict while missing sessions remain distinguishable and the original exception stays chained.","self_descriptive_naming":"The helper and public errors name exact requested-session document state rather than incidental validator wording.","obsolete_guidance_disposition":"WI-5367 history is preserved; WI-5395 supplies the missing physical implementation and acceptance closure without rewriting the old terminal record.","history_preservation":"WI-5315 baseline, WI-5367 verdict history, WI-5386 reconciler repair, current failing output, WI-5395 patch, and independent verdict remain separate.","baseline":{"end_to_end":"3 failed, 5 passed","tamper_rejected":true,"public_contract":false,"focused_module":"absent"},"expected_result":{"end_to_end_tamper":true,"tamper_rejected":true,"public_contract":true,"focused_module":"all pass"},"rollback":{"instructions":"Revert only the WI-5395 hunk and focused module through a governed successor; preserve WI-5315 and envelope validation.","verification":"focused diagnostics plus unchanged frozen tamper test"},"hard_invariants":["WI-5315 committed predecessor","tamper fails before workspace mutation","missing and present-invalid remain distinct","no classification by exception text","no validator weakening","no database, dispatcher, TAFE, routing, role, eligibility, credential, deployment, or unrelated Git mutation"],"fail_closed_conditions":["WI-5315 absent from HEAD","exact document state cannot be evaluated safely","tamper assertion is edited, skipped, or weakened","unrelated session satisfies presence","GO, claim, start, or independent verification is absent"],"essential_context_preservation":"Retain exact session identity, document presence, strong provenance validation, public error taxonomy, predecessor ownership, terminal-history contradiction, and frozen acceptance evidence."}
```

## Acceptance Criteria

1. WI-5315 exact baseline is independently VERIFIED and committed first.
2. Present-but-invalid exact session documents produce the stable public
   authoritative-provenance conflict.
3. Missing exact session documents retain the pre-existing-session error.
4. Classification uses exact bounded filesystem state, never exception text.
5. The original validation exception remains chained and validation is not
   weakened.
6. The focused diagnostics module passes all cases.
7. The unchanged frozen tamper acceptance passes before any completion claim.
8. WI-5178 and all concurrent worktree bytes remain outside scope.
9. Independent VERIFIED precedes exact hunk finalization.

## Risk / Rollback

The principal risk is mistaking another session document for requested
authority. Exact filename equality after bounded enumeration prevents that.
Normalizing too early could conceal validation defects, so normalization occurs
only after typed validation has failed and preserves the original exception as
the cause. Rollback restores only the two WI-5395 targets through a governed
successor and reruns the focused and frozen cases.

## Bridge Filing

File through the governed Codex non-bypass helper as the next numbered bridge
file. The numbered bridge file chain is append-only: no prior version is
deleted or rewritten. Deterministic TAFE routing remains external; this filing
does not inspect queue state, contact a harness, or manipulate routing.

## Recommended Commit Type

`fix` - close the live frozen-acceptance residue left by metadata-only
reconciliation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
