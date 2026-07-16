NEW

# gtkb-wi5333-modernization-e2e-timeout - Bound the multi-process modernization acceptance test realistically

bridge_kind: prime_proposal
Document: gtkb-wi5333-modernization-e2e-timeout
Version: 001
Author: Prime Builder (Codex A)
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: interactive Prime Builder A

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5333

target_paths: ["platform_tests/scripts/test_modernization_end_to_end_workflow.py"]

implementation_scope: test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

The frozen release-candidate composition timed out
`test_public_workflow_uses_external_reviews_and_resumes_exactly_once` under the
repository-wide 30-second pytest limit. The unchanged test then passed in
33.09 seconds with `--timeout=120`, and process inspection found no leaked
child. The case intentionally performs multiple isolated Git and Python
subprocess transactions, so the global unit-test floor is not a realistic
bound for this acceptance test.

Add only a test-local `pytest.mark.timeout(120)` marker to this one case. Keep
the global timeout, workflow implementation, subprocess semantics, independent
review assertions, exactly-once assertions, and output contract unchanged.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires independent proposal review and post-implementation verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing specification linkage.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - binds the proposal to the Assurance project and WI-5333.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the focused acceptance test and full-file evidence before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - governs durable capture of the newly observed RC blocker.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the correction to preserve timeout detection and ordinary test behavior.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the project-scoped Assurance PAUTH permits test work while retaining GO/start/VERIFIED gates.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the observed regression, proposal, test evidence, and final disposition to remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps WI-5333 candidate, implementation, verification, and completion states explicit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires this concrete RC blocker to remain a durable work item rather than transient chat state.

## Prior Deliberations

- `DELIB-202666274` - authorizes project-scoped Assurance implementation against the frozen acceptance contract while preserving independent GO, start, and VERIFIED gates.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-0-HANDLE-MAP` - freezes the 94-handle release-candidate scope whose clean runs exercise this acceptance case.

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666274` already authorizes the
Assurance project, and WI-5333 is a non-semantic test-harness correction needed
to execute the frozen contract. Git commit, release, deployment, credentials,
dispatcher mutation, and external-system mutation remain separately excluded.

## Requirement Sufficiency

Existing requirements sufficient. The linked non-impairment, project
authorization, bridge, and verification requirements fully define this
one-file test correction; no frozen-scope change is proposed.

## Spec-Derived Verification Plan

1. `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`: run the exact case three times
   with its test-local bound; each run must pass, leave no matching child
   process, and retain every existing semantic assertion.
2. `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: run the complete
   `test_modernization_end_to_end_workflow.py`; all tests must pass under the
   repository default configuration.
3. `GOV-FILE-BRIDGE-AUTHORITY-001` and project-linkage requirements: the
   implementation report must cite the exact one-file diff, commands, elapsed
   times, work-intent claim, and implementation-start evidence.

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_end_to_end_workflow.py::test_public_workflow_uses_external_reviews_and_resumes_exactly_once -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_modernization_end_to_end_workflow.py -q --tb=short
```

Expected result: both commands exit 0; the exact case remains bounded at 120
seconds and produces no leaked subprocesses.

## Intuitiveness/Non-Impairment Disposition

```json
{"schema_version":1,"applicability":"applicable","provenance":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","canonical_authority":"GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001","primary_route":"pytest test-local timeout marker on the single multi-process acceptance case","before_behavior":"a valid 33.09-second end-to-end acceptance run is killed by the repository-wide 30-second unit-test timeout","after_behavior":"the same acceptance semantics run under a 120-second test-local hard bound while the global timeout remains unchanged","self_descriptive_naming":"WI-5333 and the existing test name identify the acceptance workflow and bounded-timeout purpose","obsolete_guidance_disposition":"no guidance is added or retired","history_preservation":"the existing test body and all assertions remain in place; bridge and Git history remain append-only","baseline":{"global_timeout_seconds":30,"observed_passing_runtime_seconds":33.09},"expected_result":{"test_local_timeout_seconds":120,"global_timeout_seconds":30,"semantic_assertions_changed":0},"rollback":{"instructions":"remove only the WI-5333 test-local timeout marker","test":"run the exact acceptance case under the repository default timeout and confirm the prior false timeout reproduces"},"hard_invariants":["no global timeout increase","no workflow source change","no assertion removal","no subprocess leak","real hangs still fail within 120 seconds"],"fail_closed_conditions":["test exceeds 120 seconds","matching child process remains after completion","any existing workflow assertion changes or fails"],"essential_context_preservation":"independent review, exactly-once recovery, Git finalization, and frozen RC assertions remain fully exercised"}
```

## Risk / Rollback

The only risk is allowing a genuinely stuck case to run longer before failure.
The bound remains finite and test-local, while process-leak checks and three
repetitions distinguish slow valid execution from a hang. Rollback removes the
single marker; no source, data, or runtime migration is involved.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5333-modernization-e2e-timeout`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`test`: the diff changes only the execution bound of one acceptance test and
does not alter production behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
