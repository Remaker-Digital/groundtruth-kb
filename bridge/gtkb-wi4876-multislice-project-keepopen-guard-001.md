NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Multi-slice project keep-open guard

bridge_kind: prime_proposal
Document: gtkb-wi4876-multislice-project-keepopen-guard
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4876

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_projects.py", "platform_tests/scripts/test_project_authorization.py", "platform_tests/scripts/test_projects_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Add a deterministic keep-open guard or election at project authorization time for multi-slice programs so a project does not auto-retire after an interim umbrella/slice WI goes terminal. This proposal will be filed as `bridge/gtkb-wi4876-multislice-project-keepopen-guard-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4876 records the multi-slice auto-retirement trap, and the active Harness Parity Phase 2 PAUTH includes WI-4876.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governs project auto-retirement and completion safety.
- `GOV-STANDING-BACKLOG-001` - project/backlog state must remain the durable authority for unfinished slices.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4876.

## Proposed Scope

- Extend `gt projects authorize` or its companion metadata path to record a plan_incomplete or keep-open guard for declared multi-slice programs.
- Add tests proving interim terminal WIs do not auto-retire a project when remaining slices are expected.
- Keep the behavior opt-in or evidence-driven so ordinary single-slice projects still retire normally.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Tests prove multi-slice projects stay active across interim terminal WIs. |
| `GOV-STANDING-BACKLOG-001` | Tests confirm unfinished slices remain represented in MemBase project/backlog state. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle and append-only numbered file chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- Multi-slice project authorization records a deterministic keep-open guard or requires an explicit keep-open election.
- Auto-retirement respects the guard until remaining slices are complete, superseded, deferred, or owner-dispositioned.
- Single-slice retirement behavior remains unchanged.

## Risks / Rollback

Risk is moderate because project lifecycle automation is shared. Mitigation is opt-in/evidence-driven behavior and focused tests. Rollback is a revert of source/tests.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_projects.py`
- `platform_tests/scripts/test_project_authorization.py`
- `platform_tests/scripts/test_projects_cli.py`

## Recommended Commit Type

`fix`
