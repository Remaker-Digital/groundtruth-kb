NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex Desktop; reasoning=xhigh; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Restore dispatcher oldest-first selection and dispatch max-item caps

bridge_kind: prime_proposal
Document: gtkb-wi5233-dispatch-selection-order-cap-repair
Version: 001
Date: 2026-07-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5233-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5233

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair the dispatcher selection regression that reverses the already-oldest-first LO actionable list and ignores dispatch-surface max-item caps, causing WI-5139 starvation and F over-batching.

Work item description: Live dispatcher evidence on 2026-07-14 shows the canonical LO actionable queue is oldest-first (WI-5138, WI-5139, WI-5222, WI-5223, WI-5226), but scripts/dispatcher_runtime.py::_selected_oldest_first reverses that already-oldest-first list and dispatches WI-5226/WI-5223 first. The same path ignores dispatch-surface dispatch_max_items and reads only headless.max_items, so OpenRouter F selected two documents despite the dispatch cap of one. This starves WI-5139 finalization and contributes to repeated D/F failure loops.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5233` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
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
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265026` - Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff
- `DELIB-20266133` - Owner decision: re-home all open DISPATCHER-COMPLETION work and retire the project
- `DELIB-202665296` - WI-4977 Headless Dispatch Stability — REVISED Proposal Review Verdict
- `DELIB-20266268` - Owner decision: clear daemon residue WIs (WI-4859, WI-4861) before PHASE-Y
- `DELIB-20266575` - Review Findings

## Owner Decisions / Input

- `DELIB-202666173` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5233-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5233`.

## Proposed Scope

- Fix dispatcher selection so the current canonical LO actionable list is not reversed when it is already oldest-first.
- Honor dispatch-surface dispatch_max_items before falling back to headless max_items so F/D/H per-target caps are enforced consistently.
- Do not edit runtime JSON, lease files, harness roles, provider credentials, or unrelated dirty dispatcher hunks.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run focused dispatcher runtime tests for queue selection, cap handling, launch metadata, and document lease behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm implementation starts only after independent LO GO and matching work-intent claim. |
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
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Verify bridge dispatch status/report selected counts no longer overstate F cap behavior in the synthetic regression. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A focused integration test reproduces the current raw LO queue [WI-5138, WI-5139, WI-5222, WI-5223, WI-5226] and proves cap=1 selects WI-5138 rather than WI-5226.
- A focused regression proves a target with dispatch.dispatch_max_items=1 and headless.max_items absent or larger receives exactly one selected document.
- Existing dispatcher runtime tests covering selected-batch signatures, document leases, and provider backoff remain passing.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`feat`
