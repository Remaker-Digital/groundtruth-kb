NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: codex-desktop
author_model_configuration: Codex Desktop Prime Builder session

# Implementation Proposal - Expand no-window process-spawn audit to every harness launcher, verifier, benchmark runner, and recurring worker

bridge_kind: prime_proposal
Document: gtkb-wi4905-parity-diff-raw-alias-normalization
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4905

target_paths: ["scripts/parity_discovery_diff.py", "platform_tests/scripts/test_parity_discovery_diff.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Supplement WI-4905 to fix a parity discovery-diff false positive for same-stem registered/raw hook aliases exposed by the restored Codex no-window hook registry.

Work item description: WI-4896 resolved dispatcher-owned background console flashes, but Phase 2 needs full coverage. Extend the static/runtime no-window spawn audit to all Python and PowerShell launch surfaces for harness adapters, readiness verifiers, benchmark runners, recurring evaluators, dispatcher helpers, and provider wrappers, including scripts such as verify_antigravity_dispatch.py that are outside the current release-runtime allowlist.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4905` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/parity_discovery_diff.py`, `platform_tests/scripts/test_parity_discovery_diff.py`.

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
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266423` - Separation Check
- `DELIB-20266413` - Separation Check
- `DELIB-20266107` - Owner decision: reconcile dispatch can_receive_dispatch drift to Honest-ON (WI-4821)
- `DELIB-20266470` - Separation Check
- `DELIB-20266349` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active project authorization covering `WI-4905`.

## Proposed Scope

- Treat a discovered same-stem Codex hook surface as satisfying the raw unregistered parity key even when that Codex surface is also upgraded to a registered capability id.
- Add a regression test for live-equivalent alias shape: Claude raw credential-scan/session_start_dispatch/spec-classifier stems and Codex registered same-stem fallbacks must not produce false missing-Codex findings.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
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
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run python scripts\parity_discovery_diff.py --json and focused parity-diff tests to prove no unwaived hook asymmetry remains. |
| `ADR-CROSS-HARNESS-PARITY-001` | Verify the implementation preserves discovery from live config rather than making the registry the existence authority. |

## Acceptance Criteria

- python scripts\parity_discovery_diff.py --json returns PASS for the restored Codex hook registry without suppressing unrelated unregistered asymmetries.
- Focused parity discovery-diff tests pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/parity_discovery_diff.py`
- `platform_tests/scripts/test_parity_discovery_diff.py`

## Recommended Commit Type

`feat`
