NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-14T10-00-36Z-prime-builder-A-wi5226-proposal
author_model: gpt-5
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; reasoning=high; role=Prime Builder; session=019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_metadata_source: codex-explicit-env

# Implementation Proposal - OpenRouter F governed LO dispatch exits 0xFFFFFFFF without diagnostics

bridge_kind: prime_proposal
Document: gtkb-wi5226-openrouter-diagnostic-telemetry
Version: 001
Date: 2026-07-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5226-F-DIAGNOSTIC-TELEMETRY-20260714
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5226

target_paths: ["scripts/dispatcher_runtime.py", "groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair WI-5226 diagnostic telemetry masking so dispatcher reconciliation preserves harness-level no_progress_loop/process diagnostics when a worker already emitted structured telemetry.

Work item description: Canonical bridge dispatch report observed genuine OpenRouter F LO dispatch 2026-07-14T01-28-52Z-loyal-opposition-F-033790 reviewing bridge/gtkb-modernization-wi5138-pauth-activation-007.md. The worker ran 256 seconds, produced zero stdout and zero stderr, exited 4294967295, and was classified only as subprocess_execution_failed. Canonical telemetry reconciled the exit and released the document lease exactly once, but no governed verdict was produced and the recorded stderr log E:\GT-KB\.gtkb-state\bridge-poller\dispatch-runs\2026-07-14T01-28-52Z-loyal-opposition-F-033790.stderr.log is zero bytes. This regresses resolved WI-5066's clear failure-diagnostic acceptance. Diagnose and preserve the actual provider/process cause in canonical telemetry without weakening the 600-turn, 900-second operation, 3600-second session, 29400-second worker, or 29700-second lease allowances. Candidate only; grants no implementation authority.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5226` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`, `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py`, `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - auto-linked governing or work-item specification.
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
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202666118` - Loyal Opposition Verdict — WI-5173 Shim-harness dispatch telemetry usage-coverage conformance (REVISED proposal review)
- `DELIB-202665739` - WI-4995 Document Lease Held Health — Post-Implementation Verification Verdict
- `DELIB-202666132` - gtkb-wi5185-dispatcher-identity-runtime-kind — Loyal Opposition Verdict (VERIFIED)
- `DELIB-20265493` - Loyal Opposition GO verdict - WI-4700 narrative approval packet scope fix
- `DELIB-20265240` - Loyal Opposition Review - Malformed Status Token Quarantine

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5226-F-DIAGNOSTIC-TELEMETRY-20260714` - active project authorization covering `WI-5226`.

## Proposed Scope

- Preserve harness-emitted stop_reason values during dispatcher exit reconciliation when the existing telemetry file already records a specific bounded failure such as no_progress_loop.
- Keep dispatcher-created partial telemetry for missing/corrupt telemetry files, external timeout, external termination, successful verdicts, and successful final responses.
- Add focused regression coverage for nonzero OpenRouter/F-style publisher-loop failure telemetry and dispatcher reconciliation so actionable diagnostics are not collapsed to process_error.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | groundtruth-kb\\.venv\\Scripts\\python.exe -m ruff check scripts/dispatcher_runtime.py groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py platform_tests/scripts/test_dispatcher_runtime.py |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A worker telemetry file with stop_reason=no_progress_loop and exit_code=1 remains no_progress_loop after dispatcher reconciliation instead of being overwritten to process_error.
- When no worker telemetry file exists, dispatcher reconciliation still creates a partial process_error/external-timeout/external-termination record as appropriate.
- No runtime JSON or lease files are edited directly, no dispatcher routing/eligibility changes are made, and all generous 600/900/3600/29400/29700 allowances remain unchanged.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py`
- `platform_tests/groundtruth_kb/test_shim_dispatch_telemetry.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`feat`
