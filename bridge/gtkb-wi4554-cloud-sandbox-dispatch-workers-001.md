NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Omnigent alignment cloud-sandbox dispatch workers

bridge_kind: prime_proposal
Document: gtkb-wi4554-cloud-sandbox-dispatch-workers
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-OMNIGENT-ALIGNMENT
Work Item: WI-4554

target_paths: ["config/dispatcher/sandbox-execution.toml", "scripts/dispatch_sandbox_plan.py", "platform_tests/scripts/test_dispatch_sandbox_plan.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OMNIGENT-CLOUD-SANDBOX-DISPATCH-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement a planning/control-plane slice for cloud-sandbox execution of dispatched workers, modeled after the Omnigent disposable sandbox pattern. This proposal does not activate external cloud runtimes; it defines the config contract, planner, and evidence report needed before any later runtime integration.

This proposal itself will be filed as `bridge/gtkb-wi4554-cloud-sandbox-dispatch-workers-001.md`, an append-only numbered bridge file in the versioned bridge file chain.

## Requirement Sufficiency

Existing requirements are sufficient for a non-runtime planning slice. The active Omnigent Alignment PAUTH covers WI-4554, and the owner directive is to emulate overlapping Omnigent capability shapes without duplicating effort or prematurely taking a dependency.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete spec links in the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `ADR-DISPATCHER-ARCHITECTURE-001` - sandbox execution must not replace the dispatcher daemon control plane.
- `ADR-CROSS-HARNESS-PARITY-001` - sandbox execution must preserve role/harness equivalence or typed waivers.

## Prior Deliberations

- `DELIB-OMNIGENT-ADVISORY-20260614` - Omnigent advisory source context.
- `DELIB-20263229` - owner-grilling-gate Omnigent alignment direction.
- `DELIB-20265586` - snapshot-bound project authorization.

## Owner Decisions / Input

- `PAUTH-PROJECT-OMNIGENT-ALIGNMENT-OMNIGENT-ALIGNMENT-BOUNDED-IMPLEMENTATION-2026-06-23` - active authorization covering WI-4554.

## Proposed Scope

- Add a sandbox-execution planning config that is disabled by default and has no live provider credentials.
- Add a read-only planner that maps dispatch work requirements to sandbox capability requirements, root-boundary constraints, artifact preservation rules, and required future owner decisions.
- Emit a governed report comparing local E-drive execution risk with disposable sandbox requirements.
- Add tests proving the planner is disabled-by-default, never launches a sandbox, and preserves root-boundary/credential constraints.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active WI-4554 PAUTH and target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected mutation occurs before GO and implementation-start. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle state before implementation and after report filing. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests prove the planner does not replace or launch the dispatcher daemon. |
| `ADR-CROSS-HARNESS-PARITY-001` | Report records harness-equivalence implications and typed-waiver needs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Include exact targeted pytest output in the implementation report. |

## Acceptance Criteria

- Sandbox execution remains disabled-by-default and planning-only.
- Planner output names provider prerequisites, artifact preservation needs, root-boundary implications, and future approval gates.
- Tests prove no external runtime launch, no credential lifecycle behavior, and no dispatcher replacement.

## Risks / Rollback

Risk is moderate because this work touches future execution topology. Mitigation is planning-only implementation. Rollback is a revert of config, planner, tests, and report.

## Files Expected To Change

- `config/dispatcher/sandbox-execution.toml`
- `scripts/dispatch_sandbox_plan.py`
- `platform_tests/scripts/test_dispatch_sandbox_plan.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OMNIGENT-CLOUD-SANDBOX-DISPATCH-*.md`

## Recommended Commit Type

`feat`
