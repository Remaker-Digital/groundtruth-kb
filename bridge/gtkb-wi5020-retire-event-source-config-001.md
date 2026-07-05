NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; reasoning=xhigh; approval_policy=never; resolved_role=prime-builder

# Implementation Proposal - Retire vestigial can_fire_events/event_driven_hooks harness-event-source config

bridge_kind: prime_proposal
Document: gtkb-wi5020-retire-event-source-config
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5020-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5020

target_paths: ["config/dispatcher/rules.toml", "harness-state/harness-registry.json", "config/agent-control/declarative-agent-role-manifest.yaml", "groundtruth-kb/src/groundtruth_kb/harness_projection.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge/state_report.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_bridge_dispatch_transactions.py", "platform_tests/scripts/test_cross_harness_protocol_parity.py", "platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-5020` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: config/dispatcher/rules.toml and the generated harness-registry projection still carry can_fire_events / event_driven_hooks, encoding the harness-as-event-source trigger model that ADR-DISPATCHER-ARCHITECTURE-001 lists as a Failed Approach. Vestigial after the cross_harness_bridge_trigger removal; it is the only remaining gt bridge dispatch health WARN (harness B rules.toml true vs registry false). Follow-on: remove the surface through the governed change path so no config keeps implying the rejected trigger model.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5020` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `config/dispatcher/rules.toml`, `harness-state/harness-registry.json`, `config/agent-control/declarative-agent-role-manifest.yaml`, `groundtruth-kb/src/groundtruth_kb/harness_projection.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, `platform_tests/scripts/test_bridge_dispatch_transactions.py`, `platform_tests/scripts/test_cross_harness_protocol_parity.py`, `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`.

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

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-202665470` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5020-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5020`.

## Proposed Scope

- Remove vestigial harness-as-event-source eligibility from dispatcher config/projection surfaces so dispatcher routing remains daemon-owned.
- Preserve receive-dispatch eligibility, reviewer precedence, cost/quality/availability ranking, and headless worker routing.
- Update state-report and regression tests so health/status no longer imply harness-originated bridge triggers.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-DISPATCHER-ARCHITECTURE-001` | python -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_bridge_dispatch_transactions.py platform_tests/scripts/test_cross_harness_protocol_parity.py platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py -q --tb=short |
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

## Acceptance Criteria

- gt bridge dispatch health remains PASS after the config/projection cleanup.
- No runtime surface presents can_fire_events/event_driven_hooks as an active dispatcher trigger authority.
- Focused dispatcher config/projection tests pass with receive-dispatch semantics preserved.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `config/dispatcher/rules.toml`
- `harness-state/harness-registry.json`
- `config/agent-control/declarative-agent-role-manifest.yaml`
- `groundtruth-kb/src/groundtruth_kb/harness_projection.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/state_report.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/scripts/test_bridge_dispatch_transactions.py`
- `platform_tests/scripts/test_cross_harness_protocol_parity.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_state_report_cli.py`

## Recommended Commit Type

`feat`
