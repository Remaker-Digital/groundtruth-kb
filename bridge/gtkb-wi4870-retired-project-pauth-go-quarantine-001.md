NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - Retired-project PAUTH GO-thread quarantine

bridge_kind: prime_proposal
Document: gtkb-wi4870-retired-project-pauth-go-quarantine
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4870

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli_projects.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_projects_cli.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Prevent retired projects from stranding open GO bridge threads whose active PAUTH is no longer attached to an active project, and suppress unbounded dispatcher re-offer churn for such threads. This proposal will be filed as `bridge/gtkb-wi4870-retired-project-pauth-go-quarantine-001.md`, an append-only numbered bridge file.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4870 records the live-pipeline failure class, and the active Harness Parity Phase 2 PAUTH includes WI-4870.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - governs project retirement safety.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher should quarantine unimplementable work instead of re-offering indefinitely.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner authorized Harness Parity Phase 2 implementation.

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active authorization covering WI-4870.

## Proposed Scope

- Add prevention so project retirement detects open non-terminal GO threads or active PAUTHs that would be orphaned.
- Add containment so dispatcher/implementation-start surfaces classify retired-project PAUTH failures once and suppress repeated re-offer churn.
- Add tests for retirement prevention, begin failure classification, and dispatcher suppression/backoff.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Tests prove retirement cannot silently strand open GO threads. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests prove unimplementable retired-project PAUTH threads are quarantined/backed off. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle and append-only numbered file chain. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report includes exact targeted test output. |

## Acceptance Criteria

- Project retirement skips, blocks, or flags retirement when open GO threads would be stranded.
- Dispatcher health/status does not repeatedly re-offer the same retired-project PAUTH failure without suppression.
- Implementation-start diagnostics identify retired-project PAUTH as the failure class.

## Risks / Rollback

Risk is moderate because project retirement and dispatch filters affect automation flow. Mitigation is narrow classification and tests. Rollback is a revert of source/tests.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli_projects.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_projects_cli.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Recommended Commit Type

`fix`
