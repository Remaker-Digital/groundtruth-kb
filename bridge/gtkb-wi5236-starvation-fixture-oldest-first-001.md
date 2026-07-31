NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; Prime Builder A; default reasoning configuration

# Implementation Proposal - Dispatcher runtime current-HEAD verification fixtures block WI-5222 and WI-5233

bridge_kind: prime_proposal
Document: gtkb-wi5236-starvation-fixture-oldest-first
Version: 001
Date: 2026-07-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5236

target_paths: ["platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair only the migrated WI-4943 starvation-test input-order contract so current-HEAD verification reflects the independently restored dispatcher queue semantics.

Work item description: Current HEAD fails four dispatcher-runtime tests used as broad verification evidence for WI-5222 and observed again during WI-5233 verification: test_prime_spawn_creates_dispatch_authorization_packet_and_env, test_issue_dispatch_auth_uses_go_items_from_mixed_list, test_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy, and test_antigravity_stdin_dispatch_removes_prompt_from_child_argv. The failures reflect drift after implementation-authorization import/packet helpers, Antigravity stdin sidecar pointer transport, and _spawn_harness behavior changed. This blocks terminal verification reports that rely on platform_tests/scripts/test_dispatcher_runtime.py as a current-HEAD confidence suite. Candidate only; grants no implementation authority.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5236` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`.

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

## Prior Deliberations

- `DELIB-202666201` - Authorize WI-5236 dispatcher_runtime fixture drift repair
- `DELIB-202666134` - Loyal Opposition Verdict — WI-5185 Dispatcher Identity/Runtime-Kind Separation (post-implementation verification)
- `DELIB-202666242` - Loyal Opposition Corrected Verdict - WI-5236 Dispatcher Runtime Fixture Drift
- `DELIB-202666000` - Post-Implementation Verification Verdict - gtkb-wi5041-dispatcher-thread-reoffer-backoff - 004 (VERIFIED)
- `DELIB-202666237` - Summary

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5236`.

## Proposed Scope

- Change only the two stale starvation-selector fixtures from retired newest-first input to dispatcher_runtime oldest-first input.
- Preserve production scripts/dispatcher_runtime.py and all telemetry behavior unchanged.
- Preserve every unrelated same-path hunk and finalization scope.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run pytest for platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py and prove production dispatcher files are byte-unchanged. |
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

- Both currently failing starvation telemetry tests pass against current dispatcher_runtime._selected_oldest_first.
- The fixture asserts queue-head oldest-first cap semantics and identifies only the newest tail item as starved.
- Focused test file and release Ruff/format checks pass.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/scripts/test_bridge_dispatch_starvation_telemetry.py`

## Recommended Commit Type

`feat`
