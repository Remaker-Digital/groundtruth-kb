NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; reasoning=xhigh; approval_policy=never
author_metadata_source: canonical harness A invocation configuration plus current open session envelope

# Implementation Proposal - Treat latest NO-GO after prior GO as draft-revision state, not go_implementation

bridge_kind: prime_proposal
Document: gtkb-wi5337-latest-no-go-draft-claim-state
Version: 001
Date: 2026-07-16 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5337-LATEST-NO-GO-CLAIM-STATE-20260716
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5337

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Correct latest-status authority in normal work-intent claim classification so a latest NO-GO after an earlier GO is draft revision work, not executable implementation authority.

Work item description: Observed on WI-5310 after GO-002, Prime NO-ACTION-003, and corrected LO NO-GO-004. scripts/bridge_work_intent_registry.py::_go_implementation_claim_applies returns true whenever any prior GO exists and the latest status is NO-GO. bridge_claim_cli claim therefore creates a go_implementation claim, evaluates the obsolete approved proposal PAUTH, and denies target_mutation_class_not_allowed instead of allowing a draft claim for the required REVISED proposal. Latest-status authority requires NO-GO to be PB revision work, not executable implementation authority. Correct the state predicate and preserve latest GO as go_implementation, latest NO-GO as draft, explicit claim-no-action semantics, and post-verdict claim safety.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5337` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_work_intent_registry.py`, `platform_tests/scripts/test_bridge_work_intent_registry.py`.

## Specification Links

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
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-20263295` - Loyal Opposition GO Verdict: WI-4534 Claim Role Eligibility Guard
- `DELIB-20263296` - GO - WI-4534 Role-Eligibility Guard on go_implementation Claims
- `DELIB-20263755` - Loyal Opposition Review - WI-3372 KB-Mutation target_paths Closure
- `DELIB-20265662` - Loyal Opposition Review - Orphan-WI Retire Item Start-Gate Repair
- `DELIB-202666226` - Loyal Opposition NO-GO Verdict: gtkb-wi5223-dispatch-eligibility-precedence

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5337-LATEST-NO-GO-CLAIM-STATE-20260716` - active project authorization covering `WI-5337`.

## Proposed Scope

- Change only the latest-status predicate used by normal claim acquisition: latest GO remains go_implementation; every latest non-GO status, including NO-GO, follows the draft path unless an explicit special claim kind applies.
- Add focused TEST-11466 coverage for NEW -> GO -> NO-ACTION -> NO-GO and latest-GO control chains, including proof that obsolete proposal PAUTH evaluation is skipped only for the draft chain.
- Preserve explicit no_action_correction and project_authorization_bootstrap claim semantics, implementation-start enforcement, role provenance, claim timing, and PAUTH checks for genuine latest-GO implementation claims.
- Treat all existing dirty hunks in both targets as foreign. Implement and finalize only an exact reviewed function/test hunk after WI-5307 ownership disposition permits it; do not stage or commit either file wholesale.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run TEST-11466 against a numbered NEW/GO/NO-ACTION/NO-GO chain and assert normal acquisition is draft while latest GO is implementation. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry exact commands and results into the implementation report for independent LO verification. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-NO-ACTION-STATUS-SEMANTICS-001` | Run existing explicit no_action_correction tests for latest GO and NO-GO and verify the claim cannot satisfy implementation start. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Use a denying obsolete proposal PAUTH fixture to prove latest NO-GO draft acquisition skips implementation PAUTH evaluation, while latest GO still fails closed. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Run implementation-start and work-intent authorization regression suites; no latest-GO bypass is accepted. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A normal Prime claim on NEW, GO, NO-ACTION, NO-GO acquires claim_kind=draft and does not evaluate the obsolete GO proposal PAUTH.
- A normal Prime claim when GO is latest still acquires claim_kind=go_implementation and retains role-provenance, PAUTH operation, deadline, and implementation-start checks.
- Explicit claim-no-action remains Prime-only, valid only after latest GO or NO-GO, and never authorizes implementation.
- Focused registry and claim/start-gate regressions pass against an exact candidate that excludes every foreign dirty hunk.
- After verification, WI-5310 can acquire a draft claim on its latest NO-GO and file a governed REVISED proposal without implementation authority.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`

## Recommended Commit Type

`feat`
