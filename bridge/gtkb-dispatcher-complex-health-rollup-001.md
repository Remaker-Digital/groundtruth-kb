NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex interactive session; ::init gtkb pb; model gpt-5.5; long-running build envelope

# Implementation Proposal - Slice 3 - health complex rollup

bridge_kind: prime_proposal
Document: gtkb-dispatcher-complex-health-rollup
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-COMPLEX-CLI
Work Item: WI-5025

target_paths: ["groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_dispatcher_complex_control.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Slice 3 of PROJECT-GTKB-DISPATCHER-COMPLEX-CLI: implement the complex-health rollup for gt bridge dispatch health, conditioned on WI-5024 verification.

Work item description: Refactor gt bridge dispatch health into a two-dimension aggregate verdict: (a) complex-lifecycle (daemon liveness + supervisor + watchdog task-state + heartbeats), (b) existing routing/config findings. Define per-component WARN/FAIL severity. Per ADR-DISPATCHER-COMPLEX-CLI-001 decisions 3-4.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5025` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `platform_tests/scripts/test_dispatcher_complex_control.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`.

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

- `PAUTH-PROJECT-GTKB-DISPATCHER-COMPLEX-CLI-DISPATCHER-COMPLEX-CLI-IMPLEMENTATION` - active project authorization covering `WI-5025`.

## Proposed Scope

- Condition any implementation on WI-5024 latest VERIFIED; if WI-5024 returns NO-GO, stop this slice and revise the proposal instead of building on an unverified surface.
- Refactor gt bridge dispatch health into a two-dimension aggregate: complex lifecycle (daemon, supervisor, watchdog) and existing routing/config health findings.
- Add per-component WARN/FAIL severity rules for daemon liveness, supervisor task state, watchdog task state, and heartbeat freshness without merging the three runtime processes.
- Keep gt bridge dispatch complex status/health and direct daemon/supervisor/watchdog commands available; preserve lifecycle-first/scoring-last precedence and make no lane scoring changes.
- Keep dispatcher report and status JSON consumers aligned with the new health shape while preserving existing routing/config findings.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-5e9375` | Focused CLI tests prove the health rollup exists and is owner-facing through gt bridge dispatch health plus complex health. |
| `ADR-DISPATCHER-COMPLEX-CLI-001` | Tests verify ADR decisions 3 and 4: two-dimensional aggregate health and per-component WARN/FAIL severity. |
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
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests verify daemon, supervisor, and watchdog remain separate components and no lifecycle command merges their runtime responsibilities. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Supervisor/watchdog existing regression tests continue to pass alongside the new complex-health tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | gt bridge dispatch health/status/report smoke or focused tests prove central dispatcher visibility is preserved. |

## Acceptance Criteria

- No source implementation starts until WI-5024 is VERIFIED; this dependency is restated in the implementation report.
- gt bridge dispatch health --json reports both complex_lifecycle and routing_config dimensions, with an aggregate health_status that escalates WARN/FAIL deterministically.
- Complex lifecycle WARN/FAIL findings identify the affected component and reason; routing/config findings remain visible and are not hidden by lifecycle rollup.
- Existing complex status/health and direct component commands continue to work; no daemon/supervisor/watchdog process merger is introduced.
- Focused CLI/report/dispatcher tests and ruff gates pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/dispatcher_complex.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_dispatcher_complex_control.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_complex.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`

## Recommended Commit Type

`feat`
