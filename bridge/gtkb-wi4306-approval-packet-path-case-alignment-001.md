NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f1bfe-1fe3-7e01-be3e-7cc45bb778d1
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop interactive Prime Builder session; approval_policy=never; danger-full-access

# Implementation Proposal - gt spec record packet path case convention diverges from proposal target_paths

bridge_kind: prime_proposal
Document: gtkb-wi4306-approval-packet-path-case-alignment
Version: 001
Date: 2026-07-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-4306

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_spec_record.py", "platform_tests/groundtruth_kb/cli/test_spec_record.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Align gt spec record formal-artifact approval packet filenames with lowercase bridge target_paths convention while preserving packet payload artifact identity.

Work item description: scripts/cli_spec_record.py _approval_packet_path() writes packets to .groundtruth/formal-artifact-approvals/{date}-{artifact_id}.json using the spec_id verbatim (UPPERCASE for GOV-/DCL-/ADR-/PB- prefixes). Bridge proposals frequently cite the target_paths in lowercase (matching the bridge filename convention) e.g. 2026-06-04-gov-major-release-content-goal-001.json. Result: actual on-disk packet (uppercase) is not in the proposal's target_paths citation (lowercase), creating audit-trail mismatch class noted in [[gt-spec-cli-packet-provenance-gotchas]] memory. Fix: either (a) add --packet-path-mode {verbatim|lower|upper} flag, default lower for filename-convention parity, OR (b) update bridge-author rules to mandate uppercase target_paths matching the CLI convention, OR (c) make the CLI honor an explicit --packet-path override. Discovered while filing bridge/gtkb-major-release-content-goal-gov-003.md.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4306` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli_spec_record.py`, `platform_tests/groundtruth_kb/cli/test_spec_record.py`.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - auto-linked governing or work-item specification.
- `GOV-MAJOR-RELEASE-CONTENT-GOAL-001` - auto-linked governing or work-item specification.
- `DCL-MAJOR-RELEASE-CONTENT-GATE-001` - auto-linked governing or work-item specification.
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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.

## Prior Deliberations

- `DELIB-20266649` - Applicability Preflight
- `DELIB-20266559` - Separation Check
- `DELIB-20265898` - WI-4819 reliability fast-lane home (reliability-fixes standing PAUTH) despite retirement
- `DELIB-20266585` - GO: WI-4356 Slice D — work-tree hygiene governance spec insert
- `DELIB-20266663` - Review Independence

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4306`.

## Proposed Scope

- Reproduce the gt spec record path mismatch: _approval_packet_path uses artifact ids verbatim while bridge proposal target_paths conventionally cite lowercase approval-packet filenames.
- Change gt spec record packet filename behavior to mechanically align with the governed bridge target-path convention without changing the packet internal artifact identity.
- Add focused regression coverage for dry-run output and written packet output so approval_packet_path and on-disk path match byte-for-byte.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` | Run focused gt spec record tests covering formal-artifact approval packet path generation and packet validation. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | Run focused tests proving hook-facing approval packet paths match bridge target_paths citations. |
| `GOV-MAJOR-RELEASE-CONTENT-GOAL-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-MAJOR-RELEASE-CONTENT-GATE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge thread remains NEW until Loyal Opposition GO; Prime implementation starts only after GO and implementation-start packet. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run python -m pytest platform_tests/groundtruth_kb/cli/test_spec_record.py -q --tb=short plus bridge applicability and ADR/DCL preflights on proposal and implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Before protected mutation, run scripts/implementation_authorization.py begin --bridge-id gtkb-wi4306-approval-packet-path-case-alignment and verify authorized target paths. |

## Acceptance Criteria

- For GOV, DCL, ADR, and PB ids, gt spec record computes .groundtruth/formal-artifact-approvals/<date>-<lowercase-artifact-id>.json unless a separately governed explicit override is added.
- Dry-run JSON approval_packet_path and the written packet path match the lowercase target-path convention byte-for-byte.
- Approval packet content remains valid and preserves the artifact id verbatim inside the packet payload.
- Focused tests fail before the implementation and pass after the implementation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_spec_record.py`
- `platform_tests/groundtruth_kb/cli/test_spec_record.py`

## Recommended Commit Type

`feat`
