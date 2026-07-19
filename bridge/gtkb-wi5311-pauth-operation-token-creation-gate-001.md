NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f765b-9cc2-7ae3-bfa1-fc2e2b6fca41
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: reasoning_effort=xhigh; Codex Desktop; approval_policy=never; sandbox=danger-full-access; thread_source=user
author_metadata_source: codex-config-and-thread-env

# Implementation Proposal - Reject unregistered PAUTH operation tokens at authorization creation

bridge_kind: prime_proposal
Document: gtkb-wi5311-pauth-operation-token-creation-gate
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5311

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_cli_backlog_authorize_implementation.py", "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-5311` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: gt projects authorize currently accepts free-form forbidden_operations labels that the operation-time authority gate later rejects as unknown_forbidden_operation. This repeatedly creates apparently active but non-executable PAUTHs and wastes independent review, claim, and implementation-start cycles. Validate allowed mutation classes and forbidden operations against their canonical taxonomies before any PAUTH version is written; report every unknown token with canonical alternatives; add a read-only audit for already-active malformed PAUTHs.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5311` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/db.py`, `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_project_authorization.py`, `platform_tests/scripts/test_cli_backlog_authorize_implementation.py`, `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`.

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20260716-WI5320-PAUTH-AUTHORIZATION` - Owner authorizes new project-scoped PAUTH for WI-5320 dispatcher starvation fix
- `DELIB-202666516` - Loyal Opposition Proposal Review - GO - WI-5321 WI-5299 Failed VERIFIED Finalization Repair
- `DELIB-202665962` - Loyal Opposition Verdict — GO
- `DELIB-202666140` - Loyal Opposition Verdict — WI-5189 / WI-5195 Document-Authoritative GO-Claim Corrective Finalization (VERIFIED: the corrected single-patch commit collects and passes in isolation)
- `DELIB-202666234` - Loyal Opposition Review – GO

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5311`.

## Proposed Scope

- Add creation-time PAUTH vocabulary validation for allowed mutation classes and forbidden operations using the canonical operation taxonomy.
- Fail closed before append-only PAUTH insertion when an authorization request uses unregistered operation or mutation-class tokens.
- Add a read-only audit surface for already-active malformed PAUTH records, reporting unknown forbidden-operation and mutation-class tokens without mutating MemBase.
- Preserve existing operation-time evaluator behavior and append-only authorization history; do not alter project lifecycle status semantics.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5311; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "gt projects authorize currently accepts free-form forbidden_operations labels that the operation-time authority gate later rejects as unknown_forbidden_operation. This repeatedly creates apparently active but non-executable PAUTHs and wastes independent review, claim, and implementation-start cycles. Validate allowed mutation classes and forbidden operations against their canonical taxonomies before any PAUTH version is written; report every unknown token with canonical alternatives; add a read-only audit for already-active malformed PAUTHs.",
  "after_behavior": "File a governed implementation proposal for `WI-5311` using deterministic project, authorization, target-path, and preflight wiring.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5311",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/db.py",
      "groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py",
      "groundtruth-kb/src/groundtruth_kb/cli.py",
      "platform_tests/scripts/test_project_authorization.py",
      "platform_tests/scripts/test_cli_backlog_authorize_implementation.py",
      "groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py"
    ],
    "linked_specifications": [
      "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
    ]
  },
  "expected_result": {
    "summary": "File a governed implementation proposal for `WI-5311` using deterministic project, authorization, target-path, and preflight wiring.",
    "scope": [
      "Add creation-time PAUTH vocabulary validation for allowed mutation classes and forbidden operations using the canonical operation taxonomy.",
      "Fail closed before append-only PAUTH insertion when an authorization request uses unregistered operation or mutation-class tokens.",
      "Add a read-only audit surface for already-active malformed PAUTH records, reporting unknown forbidden-operation and mutation-class tokens without mutating MemBase.",
      "Preserve existing operation-time evaluator behavior and append-only authorization history; do not alter project lifecycle status semantics."
    ],
    "acceptance_criteria": [
      "gt projects authorize rejects an unregistered --forbid token without writing an active authorization.",
      "gt backlog authorize-implementation rejects unregistered forbidden-operation or mutation-class input before ProjectLifecycleService writes PAUTH state.",
      "A read-only project authorization audit reports active malformed PAUTH records and exits nonzero only in strict/check mode.",
      "Existing valid registered aliases such as production-deploy continue to normalize and store successfully."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Run focused project authorization CLI, backlog authorization CLI, and operation-time evaluator tests for unknown forbidden operations, unknown mutation classes, valid aliases, no-write failure behavior, and read-only malformed-authorization audit reporting. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- gt projects authorize rejects an unregistered --forbid token without writing an active authorization.
- gt backlog authorize-implementation rejects unregistered forbidden-operation or mutation-class input before ProjectLifecycleService writes PAUTH state.
- A read-only project authorization audit reports active malformed PAUTH records and exits nonzero only in strict/check mode.
- Existing valid registered aliases such as production-deploy continue to normalize and store successfully.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_project_authorization.py`
- `platform_tests/scripts/test_cli_backlog_authorize_implementation.py`
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`

## Recommended Commit Type

`feat`
