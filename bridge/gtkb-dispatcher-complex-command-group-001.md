NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex interactive session; ::init gtkb pb; model gpt-5.5; long-running build envelope

# Implementation Proposal - Slice 2 - complex command group

bridge_kind: prime_proposal
Document: gtkb-dispatcher-complex-command-group
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5024

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py", "platform_tests/scripts/test_dispatcher_complex_control.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Slice 2 of PROJECT-GTKB-DISPATCHER-COMPLEX-CLI: add the gt bridge dispatch complex owner-facing command group that fans out over the existing daemon, supervisor, and watchdog surfaces while preserving runtime fault isolation.

Work item description: Add gt bridge dispatch complex {status,health,enable,disable,start,stop} fanning out over daemon + supervisor + watchdog. Per ADR-DISPATCHER-COMPLEX-CLI-001 decision 1. Depends on slice 1.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5024` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py`, `scripts/gtkb_dispatcher_daemon.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`, `platform_tests/scripts/test_dispatcher_complex_control.py`.

## Specification Links

- `SPEC-INTAKE-5e9375` - auto-linked governing or work-item specification.
- `ADR-DISPATCHER-COMPLEX-CLI-001` - auto-linked governing or work-item specification.
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
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION` - active project authorization covering `WI-5024`.

## Proposed Scope

- Add a gt bridge dispatch complex {status,health,enable,disable,start,stop} command group as the owner-facing lifecycle control surface for the dispatcher daemon complex.
- Implement a dispatcher-complex aggregation module that calls the existing daemon, supervisor, and watchdog control/status APIs; preserve separate daemon, supervisor, and watchdog runtime processes.
- Keep direct component commands (daemon, daemon supervisor, daemon watchdog) available and make the complex group a fan-out/rollup layer, not a replacement runtime.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-5e9375` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-DISPATCHER-COMPLEX-CLI-001` | pytest platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py platform_tests/scripts/test_dispatcher_complex_control.py -q --tb=short |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | implementation report carries exact commands, observed results, and spec-to-test mapping |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | tests assert complex commands orchestrate existing component APIs and do not combine daemon/supervisor/watchdog into one runtime process |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | tests assert supervisor/watchdog scheduled-task controls remain delegated to their governed modules |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | gt bridge dispatch complex status --json and health --json smoke checks after implementation |

## Acceptance Criteria

- gt bridge dispatch complex status --json reports daemon, supervisor, and watchdog component status in one payload with a deterministic aggregate status.
- gt bridge dispatch complex health --json summarizes lifecycle health separately from existing routing/config health and does not mutate runtime state.
- nable and disable fan out only to supervisor/watchdog scheduled-task controls; start and stop drive the daemon lifecycle through existing daemon control paths without merging runtimes.
- Focused tests prove verb availability, fan-out order/error handling, dry-run/safe behavior where applicable, and fault-isolation from component runtime internals.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_supervisor.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_watchdog.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`
- `platform_tests/scripts/test_dispatcher_complex_control.py`

## Recommended Commit Type

`feat`
