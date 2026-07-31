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

# Implementation Proposal - Reject non-owner deliberations as PAUTH owner-decision evidence

bridge_kind: prime_proposal
Document: gtkb-wi5282-pauth-owner-decision-evidence-gate
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5282

target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_cli_backlog_authorize_implementation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-5282` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: Authorization audit on 2026-07-15 found active Goose Harness Adoption PAUTH rows for WI-5257, WI-5258, WI-5259, WI-5267 and related fleet slices citing DELIB-202666173 as owner_decision_deliberation_id. Canonical readback proves DELIB-202666173 is source_type=bridge_thread, outcome=no_go, title='Loyal Opposition Verdict: NO-GO', authored by LO B; it is not an owner decision. The project authorization writer currently appears to validate deliberation existence but not owner-decision semantics. Make PAUTH creation/amendment fail closed unless the cited current deliberation carries canonical owner-decision provenance (source_type=owner_conversation and outcome=owner_decision, or an explicitly governed equivalent defined by specification), and surface exact denial before mutation. Add a read-only audit for existing active PAUTHs with invalid evidence, quarantine them for governed reissue, and never revoke or rewrite historical rows automatically. Candidate only; grants no implementation authority.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5282` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/db.py`, `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_project_authorization.py`, `platform_tests/scripts/test_cli_backlog_authorize_implementation.py`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
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

- `DELIB-20263057` - WI-4250 status reconciliation authorization captured
- `DELIB-202666172` - Loyal Opposition Verdict: GO — WI-5210 Provider LO Governed Verdict Publication
- `DELIB-20265779` - Loyal Opposition Review - WI-4740 Bridge Verdict-File Overwrite Guard
- `DELIB-20261095` - Loyal Opposition Review - Deterministic Handoff-Prompt Service Impl (NO-GO)
- `DELIB-20261238` - Loyal Opposition Review - Deterministic Handoff-Prompt Service Impl (NO-GO)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5282`.

## Proposed Scope

- Move owner-decision provenance validation into the project authorization creation/amendment path so PAUTH rows cannot be created from arbitrary existing deliberations.
- Require canonical owner-decision provenance (source_type=owner_conversation and outcome=owner_decision) unless a future governed specification defines an explicit equivalent.
- Add a read-only audit for active PAUTH rows whose owner_decision_deliberation_id lacks valid owner-decision provenance; report and quarantine for governed reissue without rewriting or revoking historical rows.
- Preserve the existing gt backlog authorize-implementation owner-authority behavior while sharing the stricter validation with gt projects authorize.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5282; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Authorization audit on 2026-07-15 found active Goose Harness Adoption PAUTH rows for WI-5257, WI-5258, WI-5259, WI-5267 and related fleet slices citing DELIB-202666173 as owner_decision_deliberation_id. Canonical readback proves DELIB-202666173 is source_type=bridge_thread, outcome=no_go, title='Loyal Opposition Verdict: NO-GO', authored by LO B; it is not an owner decision. The project authorization writer currently appears to validate deliberation existence but not owner-decision semantics. Make PAUTH creation/amendment fail closed unless the cited current deliberation carries canonical owner-decision provenance (source_type=owner_conversation and outcome=owner_decision, or an explicitly governed equivalent defined by specification), and surface exact denial before mutation. Add a read-only audit for existing active PAUTHs with invalid evidence, quarantine them for governed reissue, and never revoke or rewrite historical rows automatically. Candidate only; grants no implementation authority.",
  "after_behavior": "File a governed implementation proposal for `WI-5282` using deterministic project, authorization, target-path, and preflight wiring.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5282",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS",
    "target_paths": [
      "groundtruth-kb/src/groundtruth_kb/db.py",
      "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py",
      "groundtruth-kb/src/groundtruth_kb/cli.py",
      "platform_tests/scripts/test_project_authorization.py",
      "platform_tests/scripts/test_cli_backlog_authorize_implementation.py"
    ],
    "linked_specifications": [
      "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
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
    "summary": "File a governed implementation proposal for `WI-5282` using deterministic project, authorization, target-path, and preflight wiring.",
    "scope": [
      "Move owner-decision provenance validation into the project authorization creation/amendment path so PAUTH rows cannot be created from arbitrary existing deliberations.",
      "Require canonical owner-decision provenance (source_type=owner_conversation and outcome=owner_decision) unless a future governed specification defines an explicit equivalent.",
      "Add a read-only audit for active PAUTH rows whose owner_decision_deliberation_id lacks valid owner-decision provenance; report and quarantine for governed reissue without rewriting or revoking historical rows.",
      "Preserve the existing gt backlog authorize-implementation owner-authority behavior while sharing the stricter validation with gt projects authorize."
    ],
    "acceptance_criteria": [
      "gt projects authorize rejects a bridge_thread/no_go deliberation as --owner-decision evidence before writing PAUTH state.",
      "gt projects authorize still accepts source_type=owner_conversation/outcome=owner_decision deliberations.",
      "A read-only authorization audit reports active PAUTH rows backed by non-owner deliberations without mutating MemBase.",
      "gt backlog authorize-implementation remains fail-closed for non-owner deliberations and continues to pass focused regression tests."
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
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run focused project authorization CLI/service tests covering valid owner decisions, invalid reviewer verdict deliberations, no-write failure behavior, and read-only invalid-evidence audit reporting. |
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

- gt projects authorize rejects a bridge_thread/no_go deliberation as --owner-decision evidence before writing PAUTH state.
- gt projects authorize still accepts source_type=owner_conversation/outcome=owner_decision deliberations.
- A read-only authorization audit reports active PAUTH rows backed by non-owner deliberations without mutating MemBase.
- gt backlog authorize-implementation remains fail-closed for non-owner deliberations and continues to pass focused regression tests.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_project_authorization.py`
- `platform_tests/scripts/test_cli_backlog_authorize_implementation.py`

## Recommended Commit Type

`feat`
