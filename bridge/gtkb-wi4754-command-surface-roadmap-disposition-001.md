NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Command-surface roadmap disposition and slicing

bridge_kind: prime_proposal
Document: gtkb-wi4754-command-surface-roadmap-disposition
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4754

target_paths: ["config/agent-control/command-surface.toml", "scripts/command_surface_disposition.py", "platform_tests/scripts/test_command_surface_disposition.py", "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/COMMAND-SURFACE-ROADMAP-DISPOSITION-*.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Disposition the preserved CS-2+ command-surface roadmap into a concrete governed slice plan before any broad command dispatcher implementation. This proposal will be filed as `bridge/gtkb-wi4754-command-surface-roadmap-disposition-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient for disposition and slicing. The work item preserves the retired command-surface roadmap, while the active Harness Parity Phase 2 PAUTH includes WI-4754.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - command surfaces must not diverge silently across harnesses.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - roadmap decisions must become durable artifacts or explicit retirements.

## Prior Deliberations

- `DELIB-CMD-SURFACE-RETIRE-DIRECTIVE-20260622` - owner directive preserving CS-2+ as reversible carry-forward.
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation scope.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4754.

## Proposed Scope

- Add a read-only disposition helper for CS-2..CS-7 that classifies each command-surface slice as implement, defer, supersede, retire, or needs owner decision.
- Preserve `::init` and `::wrap` as already shipped/superseding slices where applicable.
- Emit a compact report with target paths and bridge requirements for any surviving child slice.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Report records durable disposition for each roadmap slice. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Tests verify command slices include harness-parity disposition fields. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle and append-only numbered file chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- CS-2..CS-7 have explicit disposition rows and no ambiguous consideration-only residue.
- Any implementable child slice names required target paths, specs, PAUTH needs, and bridge proposal needs.
- No live `::` command dispatcher implementation happens in this slice.

## Risks / Rollback

Risk is low to moderate because this is disposition/planning rather than command execution. Rollback is a revert of helper, config, tests, and report.

## Files Expected To Change

- `config/agent-control/command-surface.toml`
- `scripts/command_surface_disposition.py`
- `platform_tests/scripts/test_command_surface_disposition.py`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/COMMAND-SURFACE-ROADMAP-DISPOSITION-*.md`

## Recommended Commit Type

`docs`
