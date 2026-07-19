NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; build envelope active; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - Worker-safe and operator CLI split for dispatcher internals

bridge_kind: prime_proposal
Document: gtkb-wi5273-worker-operator-cli-split
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5273-WORKER-OPERATOR-CLI-SPLIT-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5273

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py", "groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py", "platform_tests/scripts/test_bridge_read_commands.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-5273 proposes a source/test split between ordinary worker-safe CLI surfaces and operator/maintenance dispatcher diagnostics, sequenced behind the activity-envelope and worker-packet foundation.

Work item description: Split and redact dispatcher/bridge/TAFE CLI surfaces so ordinary-worker commands expose only worker-safe summaries and assigned packet content, while operator/maintenance diagnostics expose protected internals only under the appropriate ops or build activity envelope and case authorization. Apply to dispatch status, health, report, complex health, bridge show/view, and related control-plane commands as applicable.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5273` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`, `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`, `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`, `platform_tests/scripts/test_bridge_read_commands.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py`.

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

- `DELIB-20260715-DISPATCHER-WORKER-CONTEXT-PACKET` - Dispatcher Black Box Worker Context Packet CLI
- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE` - Dispatcher Complex Strict Operational Black Box Scope
- `DELIB-20260715-DISPATCHER-BLACKBOX-ORDINARY-WORKER-DEFINITION` - Dispatcher Black Box Ordinary Worker Definition
- `DELIB-202665786` - LO Review: OPS remediation for WI-5002 circuit-breaker .codex DACL and dispatch suppression
- `DELIB-202666208` - Loyal Opposition NO-GO Verdict - Dispatcher Black-Box Spec Foundation

## Owner Decisions / Input

- `DELIB-20260715-DISPATCHER-BLACKBOX-SCOPE` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5273-WORKER-OPERATOR-CLI-SPLIT-20260717` - active project authorization covering `WI-5273`.

## Proposed Scope

- Split dispatcher/bridge/TAFE CLI output into ordinary worker-safe views and operator/maintenance diagnostics without mutating dispatcher runtime/config state.
- Ordinary worker CLI modes expose only assigned packet content, safe blocker/no-work reasons, minimal availability, and safe summaries; operator modes may expose protected internals only when activity-envelope/case authority is validated.
- Sequence implementation behind WI-5269 authority validators and WI-5270/WI-5271 packet surfaces, composing with those facades instead of creating competing raw-read paths.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run targeted CLI report/status/health/show tests proving dispatcher internals remain service-owned and read-only. |
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
| `DCL-DISPATCHER-ORDINARY-WORKER-BLACK-BOX-BOUNDARY-001` | Assert ordinary CLI modes omit raw bridge, dispatcher, TAFE, harness registry, runtime/config, ranking, and unrelated queue internals. |
| `DCL-DISPATCHER-WORKER-SAFE-PACKET-CONTRACT-001` | Assert ordinary CLI modes expose assigned packet content and safe blocker/no-work context needed for PB/LO work. |
| `DCL-DISPATCHER-ACTIVITY-ENVELOPE-AUTHORITY-001` | Assert operator/internal modes require the correct ops/build/case authority and do not treat ops/build as interchangeable. |
| `ADR-DISPATCHER-WORKER-CONTEXT-FACADE-001` | Verify worker-safe CLI modes compose with the worker-context/mediated packet facade instead of reading raw bridge files directly. |
| `DCL-DISPATCHER-BLACK-BOX-FOUNDATION-FIRST-GATE-001` | Verify implementation remains covered by the active WI-5273 PAUTH and foundation specs. |

## Acceptance Criteria

- Worker-safe CLI output for status/report/health/show/view paths omits raw bridge paths, bridge index/state internals, dispatcher runtime/config paths, TAFE internals, harness registry internals, worker ranking, and unrelated queue state.
- Operator/maintenance CLI output remains available through an explicit operator/internal mode and is denied or redacted for ordinary sessions without the appropriate ops/build/case authority.
- Existing operator diagnostics keep enough information for maintenance while ordinary commands remain sufficient to complete assigned PB/LO bridge work through safe packet surfaces.
- Tests cover JSON and human output for worker-safe and operator modes, including negative cases for ordinary access to protected internals.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/read_commands.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_worker_context.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`
- `platform_tests/scripts/test_bridge_read_commands.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_worker_context_cli.py`

## Recommended Commit Type

`feat`
