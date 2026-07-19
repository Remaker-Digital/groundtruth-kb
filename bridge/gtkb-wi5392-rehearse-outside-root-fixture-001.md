NEW

# WI-5392 - Make the rehearsal outside-legacy fixture root-relative

bridge_kind: prime_proposal
Document: gtkb-wi5392-rehearse-outside-root-fixture
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder; current worktree authoritative; no direct harness contact

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5392

target_paths: ["platform_tests/scripts/test_rehearse_isolation.py"]

implementation_scope: one test-fixture correction
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Repair the second current failure in frozen `AT-AGENT-RED-PORTABILITY`
without weakening production application-placement enforcement. The test
`test_target_root_allowed_outside_legacy_root` assumes pytest's `tmp_path` is
outside the GT-KB root, but the governed test environment deliberately keeps
temporary evidence under the project root. The test therefore passes an
in-root non-application path to `validate_target_root`, which correctly rejects
it.

Change only this fixture: use `monkeypatch` to bind the rehearsal module's
legacy root and applications namespace to a synthetic child of `tmp_path`, then
pass a sibling target that is semantically outside that synthetic legacy root.
All scratch paths remain in-root, production constants and behavior remain
unchanged, and every refusal case continues to exercise the real contract.

## Specification Links

- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root adopter targets belong
  under the applications namespace; the production rejection is correct.
- `DCL-GTKB-INDEPENDENT-TEST-SUITE-001` - the platform acceptance fixture must
  independently and deterministically exercise the placement boundary.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - the repair must not weaken root
  enforcement or move active test evidence outside the project.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the frozen acceptance
  result must be reproducible from the declared one-file test artifact.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authority does not
  waive GO, claim, start, verification, or Git-operation gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - live authority
  must be rechecked before the protected test edit.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - independent GO and VERIFIED remain
  mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing
  requirements are explicitly linked.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, WI,
  and exact target are explicit.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification maps the
  placement rule to focused and frozen acceptance evidence.
- `GOV-STANDING-BACKLOG-001` - WI-5392 durably owns the discovered failure.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - work item, proposal, test hunk,
  report, verdict, and finalization remain traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - completion requires implementation,
  independent verification, and exact finalization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fixture contradiction is
  corrected as governed work rather than waived in transcript.

## Prior Deliberations

- `DELIB-20265227` - selected the application-placement ADR and paired
  minimization contract exercised by this acceptance activity.
- `DELIB-202666274` - supplies active project-scoped modernization Assurance
  authority while retaining independent review and mechanical Git gates.
- Owner directive, 2026-07-16 - fix all modernization blockers, preserve the
  project-root boundary, and add discovered defects as hygiene work.

## Owner Decisions / Input

No new owner decision is required. The existing project PAUTH and owner
directive cover this bounded fixture correction. Git staging, commit, push,
deployment, release, cleanup, credentials, dispatcher, TAFE, harness routing,
roles, and eligibility remain excluded.

## Requirement Sufficiency

Existing requirements are sufficient. The production code already implements
the placement rule correctly; only the test's environmental assumption is
stale.

## Proposed Scope

1. Add `monkeypatch` to the one positive test's fixture parameters.
2. Define a synthetic legacy root and applications namespace beneath
   `tmp_path`, and patch only the imported rehearsal module constants.
3. Validate a sibling path beneath the same governed pytest root and assert it
   is outside the synthetic legacy root before invoking production validation.
4. Leave production code, refusal fixtures, repository configuration, and all
   other tests byte-for-byte unchanged.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the focused positive and refusal cases in the sole target. | The synthetic outside-root case passes; in-root paths outside applications and conflated surfaces still fail closed. |
| `DCL-GTKB-INDEPENDENT-TEST-SUITE-001`; `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` | Run the complete sole target with the package venv. | The full test module passes from in-root scratch state. |
| Frozen acceptance contract | Run the manifest-declared `AT-AGENT-RED-PORTABILITY` activity with its configured interpreter and timeout. | The former rehearsal fixture failure is absent; the separately owned WI-5381 relocation failure remains explicit until its own repair. |
| Scope and lifecycle | Inspect `git diff --` and `git diff --check --` for the sole target, then require independent implementation review. | Only the bounded fixture hunk exists, formatting is clean, and VERIFIED precedes any finalization. |

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"WI-5392; frozen AT-AGENT-RED-PORTABILITY result from 2026-07-16","canonical_authority":"ADR-ISOLATION-APPLICATION-PLACEMENT-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"synthetic legacy boundary inside the governed pytest root","before_behavior":"The positive outside-legacy test assumes tmp_path is outside GT-KB, but the in-root test environment makes it an invalid in-root non-application target.","after_behavior":"The test models outside-legacy semantics relative to a synthetic root while every scratch path remains inside GT-KB.","self_descriptive_naming":"synthetic_legacy_root and outside_target identify the semantic boundary directly","obsolete_guidance_disposition":"Remove only the stale docstring claim that tmp_path lives outside GT-KB; production placement guidance remains unchanged.","history_preservation":"WI-5392, the one-file diff, exact failing baseline, report, and append-only bridge chain preserve the correction history.","baseline":{"frozen_activity":"70 passed and 2 failed","owned_failure":"test_target_root_allowed_outside_legacy_root raises TargetRootError because tmp_path is under GT-KB"},"expected_result":{"focused":"positive synthetic outside-root case passes and all production refusal cases remain green","frozen_activity":"the WI-5392 failure is removed without masking the separately owned relocation failure"},"rollback":{"instructions":"revert only the WI-5392 test hunk through a governed successor","verification":"rerun focused placement tests and frozen portability activity"},"hard_invariants":["all active files remain under E:/GT-KB","production validate_target_root is unchanged","in-root non-application targets remain rejected","no harness or dispatch impairment","no Git effect"],"fail_closed_conditions":["production source changes","real placement checks are weakened","scratch evidence moves outside the project root","another acceptance failure is waived or relabeled","GO, claim, start, or independent verification is absent"],"essential_context_preservation":"Retain the application-placement ADR, real refusal coverage, in-root scratch boundary, and separate WI-5381 relocation ownership."}
```

## Acceptance Criteria

1. The positive outside-legacy fixture uses an explicit synthetic boundary and
   passes in the governed in-root test environment.
2. Production application-placement code and constants are unchanged.
3. Every in-root refusal case remains green.
4. The frozen activity no longer reports this fixture failure and still reports
   any independently owned remaining failure exactly.
5. Independent VERIFIED precedes exact mechanical finalization.

## Risk / Rollback

The risk is accidentally making the test tautological. The focused test must
assert the selected target is outside the synthetic legacy root before calling
the production validator, while the existing negative tests continue using the
real module constants. Rollback is the one-file hunk through a governed
successor; no broad reset or unrelated path change is permitted.

## Bridge Filing

File through the governed Codex non-bypass helper. The numbered bridge file
chain is append-only. Deterministic TAFE routing remains external; this filing
does not contact or configure any harness.

## Recommended Commit Type

`test` - correct the frozen portability fixture without changing product
behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
