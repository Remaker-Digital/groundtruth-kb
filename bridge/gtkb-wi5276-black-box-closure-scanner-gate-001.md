NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope active; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Black-box boundary regression scanner and verified project closure gate

bridge_kind: prime_proposal
Document: gtkb-wi5276-black-box-closure-scanner-gate
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5276-CLOSURE-SCANNER-GATE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5276

target_paths: ["scripts/project_verified_completion_scanner.py", "scripts/dispatch_blackbox_boundary_scanner.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "platform_tests/scripts/test_dispatch_blackbox_boundary_scanner.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_black_box_closure_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5276 proposes the black-box regression scanner and final closure gate: a read-only proof layer that blocks project closure until all child/derived work is terminal VERIFIED and ordinary PB/LO bridge work can complete through safe packet surfaces without black-box boundary violations.

Work item description: Create a regression scanner and final closure gate for the dispatcher black-box hardening project. The scanner must classify transcripts, dispatch logs, prompts, skills, and CLI outputs for ordinary-worker black-box violations, including direct protected reads, direct protected mutations, missing worker-safe packet usage, ops/build authority confusion, and case-authorization bypass. The closure gate must prove all child WIs are terminal VERIFIED and ordinary PB/LO assigned work can complete through safe packet surfaces.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5276` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/project_verified_completion_scanner.py`, `scripts/dispatch_blackbox_boundary_scanner.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_project_verified_completion_scanner.py`, `platform_tests/scripts/test_dispatch_blackbox_boundary_scanner.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_black_box_closure_cli.py`.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
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
- `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666170` - Loyal Opposition Review - GO - WI-5208 Concurrent Dispatcher Launch Ledger
- `DELIB-20265732` - Loyal Opposition Verification Verdict: WI-4691 Verified Finalization Repair
- `DELIB-20265604` - Loyal Opposition Review - Completion gate noncanonical WI recognition
- `DELIB-202665102` - Verdict
- `DELIB-202666310` - Loyal Opposition GO Verdict - Dispatcher Black-Box Specification Foundation

## Owner Decisions / Input

- `DELIB-20260715-DISPATCHER-BLACKBOX-PHASED-HARDENING` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5276-CLOSURE-SCANNER-GATE-20260717` - active project authorization covering `WI-5276`.

## Proposed Scope

- Add a read-only dispatcher black-box boundary scanner that classifies ordinary-worker protected read/write/shell/config/internal violations across prompts, skills, CLI outputs, dispatch logs, and transcript-derived evidence where available.
- Extend or compose with the project verified-completion scanner so this black-box project cannot close until all child/derived WIs are terminal VERIFIED and the boundary scanner reports no unresolved ordinary-worker black-box violations.
- Expose a deterministic CLI/report output suitable for LO verification and final project closure evidence without mutating dispatcher runtime/config state.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run scanner/closure tests proving dispatcher internals remain service-owned and scanner itself is read-only. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run all scanner/closure tests and map each finding class to spec-derived verification evidence before VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Test violation classification for ordinary protected reads/mutations and raw-internal dependencies. |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Test closure fails when safe packet usage is missing and passes only when worker-context/mediated packet surfaces are available. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Test scanner catches ops/build authority confusion and missing case authorization. |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | Verify final closure evidence proves ordinary PB/LO assigned work can complete through safe packet surfaces. |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | Verify closure logic requires active foundation specs and the active WI-5276 PAUTH. |

## Acceptance Criteria

- The scanner classifies direct protected reads, direct protected mutations, missing worker-safe packet usage, ops/build authority confusion, case-authorization bypass, and unsupported-surface waiver gaps.
- The closure gate reports NOT READY while any child/derived black-box WI is nonterminal or any related bridge thread is not latest VERIFIED.
- The closure gate reports READY only when child/derived WIs are terminal VERIFIED, all required bridge evidence is latest VERIFIED, safe packet surfaces support ordinary PB/LO work, and boundary scan findings are resolved or typed-waived.
- Tests include positive closure-ready fixtures and negative fixtures for each violation class and for nonterminal child work.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/project_verified_completion_scanner.py`
- `scripts/dispatch_blackbox_boundary_scanner.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_project_verified_completion_scanner.py`
- `platform_tests/scripts/test_dispatch_blackbox_boundary_scanner.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_black_box_closure_cli.py`

## Recommended Commit Type

`feat`
