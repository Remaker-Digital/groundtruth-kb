NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-auto-builder-2026-06-30T10-52Z
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop automation Auto-builder; role=prime-builder; approval_policy=never; filesystem=unrestricted
author_metadata_source: auto-builder automation explicit env

# Implementation Proposal - impl-auth REQUIREMENT_SUFFICIENCY_PHRASES missing 'New requirement required' state

bridge_kind: prime_proposal
Document: gtkb-wi4304-requirement-sufficiency-governance-review-lane
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-4304

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for WI-4304 to add a narrow implementation-authorization lane for governance_review proposals that declare the required gap-state phrase, without weakening the normal source/test requirements-gap blocker.

Work item description: scripts/implementation_authorization.py defines REQUIREMENT_SUFFICIENCY_PHRASES as 6 phrase variants of 'Existing requirements sufficient'. It has NO accepted phrase for the second operative state defined by .claude/rules/file-bridge-protocol.md: 'New or revised requirement required before implementation'. Result: every governance-capture bridge proposal (governance_review with new GOV/DCL/SPEC creation) hits 'impl-auth begin' with exit code 2: 'Approved proposal is missing ## Requirement Sufficiency'. Fix: extend REQUIREMENT_SUFFICIENCY_PHRASES with the 'New or revised requirement required' state variants AND emit a distinct authorization sub-mode for governance-capture (no source mutation, only approval-packet-gated KB writes), OR formalize the impl-auth-bypass for governance_review bridge_kind in the rule. Discovered while executing bridge/gtkb-major-release-content-goal-gov-003.md.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4304` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`, `platform_tests/scripts/test_implementation_authorization.py`.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `GOV-MAJOR-RELEASE-CONTENT-GOAL-001` - auto-linked governing or work-item specification.
- `DCL-MAJOR-RELEASE-CONTENT-GATE-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-20266141` - Separation Check
- `DELIB-20265990` - Loyal Opposition Review - Requirement-Sufficiency negated-plural follow-up
- `DELIB-20265963` - WI-4750 implementation report — auto-retire verify-helper parity regression
- `DELIB-20265986` - Applicability Preflight
- `DELIB-20266258` - Applicability Preflight

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4304`.

## Proposed Scope

- Teach the implementation authorization packet path a narrow governance_review lane for proposals that declare the exact gap-state phrase New or revised requirement required before implementation.
- Preserve the existing hard block for ordinary source/test implementation proposals that declare a requirements gap.
- Add focused regression coverage for the classifier, source-proposal denial, and governance_review authorization path.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short and confirm the generated proposal contains concrete Specification Links. |
| `GOV-MAJOR-RELEASE-CONTENT-GOAL-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-MAJOR-RELEASE-CONTENT-GATE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run gt bridge show gtkb-wi4304-requirement-sufficiency-governance-review-lane --json and verify the append-only numbered bridge chain. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short to exercise the spec-derived governance_review authorization path. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Run python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4304-requirement-sufficiency-governance-review-lane after GO and confirm an authorization packet is issued only after project authorization validation. |

## Acceptance Criteria

- requirement_sufficiency_state continues to classify the exact gap-state phrase as gap rather than missing or unrecognized.
- create_authorization_packet authorizes a GO'd governance_review proposal carrying the exact gap-state phrase through an explicit documented sub-mode, while retaining source/test denial.
- Focused platform tests pass for scripts/implementation_authorization.py and the implementation-authorization regression suite.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Recommended Commit Type

`feat`
