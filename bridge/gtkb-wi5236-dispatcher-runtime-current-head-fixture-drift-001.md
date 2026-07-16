NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder; active fleet goal; approval_policy=never; workspace=E:\GT-KB

# Implementation Proposal - Dispatcher runtime current-HEAD verification fixtures block WI-5222 and WI-5233

bridge_kind: prime_proposal
Document: gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift
Version: 001
Date: 2026-07-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5236-DISPATCHER-RUNTIME-FIXTURE-DRIFT-20260714
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5236

target_paths: ["platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair current-HEAD dispatcher_runtime test fixture drift that blocks WI-5222 verification without changing dispatcher runtime behavior.

Work item description: Current HEAD fails four dispatcher-runtime tests used as broad verification evidence for WI-5222 and observed again during WI-5233 verification: test_prime_spawn_creates_dispatch_authorization_packet_and_env, test_issue_dispatch_auth_uses_go_items_from_mixed_list, test_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy, and test_antigravity_stdin_dispatch_removes_prompt_from_child_argv. The failures reflect drift after implementation-authorization import/packet helpers, Antigravity stdin sidecar pointer transport, and _spawn_harness behavior changed. This blocks terminal verification reports that rely on platform_tests/scripts/test_dispatcher_runtime.py as a current-HEAD confidence suite. Candidate only; grants no implementation authority.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5236` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `platform_tests/scripts/test_dispatcher_runtime.py`.

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
- `DELIB-202666000` - Post-Implementation Verification Verdict - gtkb-wi5041-dispatcher-thread-reoffer-backoff - 004 (VERIFIED)
- `DELIB-202665726` - WI-4991 Headless-Ineligible Dispatch Suppression -- Implementation Verification Verdict
- `DELIB-20265665` - Loyal Opposition Verification - Pending Owner Decisions Surface Cache Resurface

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5236-DISPATCHER-RUNTIME-FIXTURE-DRIFT-20260714` - active project authorization covering `WI-5236`.

## Proposed Scope

- Refresh only current-HEAD dispatcher_runtime test fixtures/expectations that were broken by committed API and Antigravity prompt-transport changes.
- Do not alter dispatcher runtime behavior unless the focused failing tests prove the production interface is wrong rather than the fixture.
- Preserve WI-5222 and WI-5233 source hunks and avoid groundtruth.db, runtime JSON, leases, and dispatcher eligibility changes.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps each refreshed fixture expectation to the failing assertion it resolves and records the exact pytest result. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- The four WI-5222 NO-GO named failures in platform_tests/scripts/test_dispatcher_runtime.py pass on current HEAD.
- Focused full module command python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short passes or any unrelated failures are separately tracked before verification.
- No source, bridge runtime state, lease, eligibility, or MemBase DB mutation is included in the implementation.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `platform_tests/scripts/test_dispatcher_runtime.py`

## Recommended Commit Type

`feat`
