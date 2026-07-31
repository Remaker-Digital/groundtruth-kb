NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: gpt-5.5
author_model_configuration: Codex Desktop interactive Prime Builder
author_metadata_source: same-session .gtkb-state bridge proposal draft metadata

# Implementation Proposal - Make counterpart-state root fixture valid under in-root pytest temp policy

bridge_kind: prime_proposal
Document: gtkb-wi5434-inroot-counterpart-fixture-semantics
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5434

target_paths: ["platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Make counterpart-path assertions semantic under the mandatory in-root pytest temp policy without weakening canonical fallback behavior.

Work item description: platform_tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_uses_project_root_paths_when_provided asserts that a tmp_path-derived role registry is not lexically under the canonical E:/GT-KB root. The repository conftest deliberately roots tmp_path beneath E:/GT-KB/.pytest-tmp, so that assertion is impossible even though the function receives and uses the supplied synthetic project root. WI-3460 was resolved despite naming this exact path-resolution failure. Repair the fixture/assertion seam to prove reads resolve through the provided project_root without requiring out-of-root test artifacts, weakening canonical-root protections, altering runtime harness state, or impairing dispatchability.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5434` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/hooks/test_workstream_focus.py`.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - auto-linked governing or work-item specification.
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
- `GOV-PROJECT-ROOT-BOUNDARY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666102` - Verdict: NO-GO
- `DELIB-202666100` - Verdict
- `DELIB-202665726` - WI-4991 Headless-Ineligible Dispatch Suppression -- Implementation Verification Verdict
- `DELIB-2312` - Loyal Opposition Review - Agent Red Deployability Preservation Gate
- `DELIB-20261580` - Loyal Opposition Review - Early Project Specs Quality Audit

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5434`.

## Proposed Scope

- Replace the impossible lexical assertion that an in-root tmp_path sandbox is outside PROJECT_ROOT with exact assertions that every recorded role-assignment path is rooted at the supplied sandbox and equals the sandbox harness-registry location.
- Retain the adjacent fallback test proving omission of project_root uses the canonical registry; do not alter production hook code, canonical-root policy, runtime harness state, eligibility, or dispatch.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-SESSION-SELF-INITIALIZATION-001` | groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_uses_project_root_paths_when_provided platform_tests/hooks/test_workstream_focus.py::test_detect_counterpart_state_falls_back_to_canonical_when_project_root_omitted -q --tb=short |
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
| `GOV-PROJECT-ROOT-BOUNDARY-001` | Confirm pytest temporary artifacts remain beneath E:/GT-KB/.pytest-tmp and no out-of-root fixture is introduced. |

## Acceptance Criteria

- The supplied-project-root test proves detect_counterpart_state reads the sandbox registry and never substitutes the canonical registry, even though the sandbox itself is correctly under E:/GT-KB/.pytest-tmp.
- The exact failing node and the adjacent canonical-fallback node pass under the standard in-root pytest temporary policy.
- Only platform_tests/hooks/test_workstream_focus.py changes and no foreign dirt is absorbed.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/hooks/test_workstream_focus.py`

## Recommended Commit Type

`feat`
