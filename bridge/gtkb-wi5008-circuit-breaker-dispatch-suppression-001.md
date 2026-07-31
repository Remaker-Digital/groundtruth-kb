NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: Codex desktop runtime 2026-07-04
author_model_configuration: Codex desktop interactive Prime Builder; reasoning inherited from session

# Implementation Proposal - OPS remediation for WI-5002 circuit-breaker .codex DACL and dispatch suppression

bridge_kind: prime_proposal
Document: gtkb-wi5008-circuit-breaker-dispatch-suppression
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5008-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5008

target_paths: ["scripts/dispatcher_runtime.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_scan_bridge.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Bounded OPS remediation proposal for WI-5008 to make the third-NO-ACTION circuit-breaker disposition mechanically non-dispatchable across dispatcher and scan/status surfaces while keeping future .codex DACL repair in this fresh governed lane.

Work item description: Follow-up remediation after bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-016.md recorded the third-NO-ACTION circuit breaker and retired the initial WI-5002 workflow as failed. Diagnose and remediate the owner-side .codex DACL authority blocker and the dispatcher/raw-scan suppression gap so terminal circuit-breaker NO-GO evidence does not redispatch the dead workflow. Any implementation requires a fresh bridge proposal, GO, PAUTH, and work-intent claim.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5008` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_scan_bridge.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`.

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

## Prior Deliberations

- `DELIB-20260703-WI5002-DOTDIR-SANDBOX-ACL-IMPLEMENTATION-APPROVED` - Approve WI-5002 Codex Dotdir Sandbox ACL Correction Implementation
- `DELIB-202665146` - Verdict: NO-GO
- `DELIB-202665178` - Verdict: NO-GO
- `DELIB-202665184` - Verdict: NO-GO
- `DELIB-202665185` - Verdict: NO-GO

## Owner Decisions / Input

- `DELIB-HARNESS-OPS-NO-ACTION-CIRCUIT-BREAKER-20260702` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5008-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5008`.

## Proposed Scope

- Treat third-NO-ACTION circuit-breaker evidence as non-dispatchable for the failed initial workflow, even when the latest bridge top token remains NO-GO.
- Keep remediation in WI-5008 as a fresh governed OPS lane and do not resurrect or continue WI-5002 without a later explicit recovery plan.
- Update canonical scan/status behavior without directly mutating generated .codex helper copies in this slice.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_bridge_dispatch_config.py -q --tb=short |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | manual backlog check proves WI-5002 remains terminal retired and WI-5008 owns remediation |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | pytest platform_tests/scripts/test_scan_bridge.py -q --tb=short |

## Acceptance Criteria

- Dispatcher PB selection no longer launches or reports pending work for a retired/circuit-broken initial workflow when its linked work item is terminal in MemBase.
- Bridge scan/status surfaces classify circuit-breaker retired workflows as blocked/non-activatable or terminal carry-forward, not PB implementation work.
- Tests cover a latest NO-GO bridge thread linked to a retired WI and a separate open OPS remediation WI.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_scan_bridge.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

## Recommended Commit Type

`feat`
