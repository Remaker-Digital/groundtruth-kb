NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access
author_metadata_source: explicit-current-session

# Implementation Proposal - Dispatcher health classifies spawn-rate and provider backpressure without false failure

bridge_kind: prime_proposal
Document: gtkb-wi4933-cursor-bridge-skill-route-repair
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933

target_paths: ["scripts/cursor_harness.py", "platform_tests/scripts/test_cursor_harness.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair Cursor LO bridge-review skill routing so dispatcher-driven Cursor reviews receive the bridge protocol rather than the generic proposal-review memo skill.

Work item description: Controlled daemon restart on 2026-06-30 produced gt bridge dispatch health WARN for loyal-opposition:F last_result=spawn_rate_limited with pending_count=2 while live workers were already in flight. OpenRouter F also previously returned HTTP 429 Too Many Requests and was classified as a generic subprocess execution failure. Dispatcher release-health should distinguish local rate limiting and provider backpressure from runtime crashes, honoring provider rate-limit signals and preserving genuine failure visibility.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4933` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/cursor_harness.py`, `platform_tests/scripts/test_cursor_harness.py`.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
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
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266192` - Owner decision: authorize WI-4852 watchdog-dormancy auto-restart for bounded implementation
- `DELIB-20266366` - Separation Check
- `DELIB-20266505` - Authorize dispatcher diagnostic health release fix
- `DELIB-20266508` - Authorize WI-4934 dispatcher failed-recipient LO failover repair
- `DELIB-20266368` - Separation Check

## Owner Decisions / Input

- `DELIB-20266507` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH` - active project authorization covering `WI-4933`.

## Proposed Scope

- Route Cursor Loyal Opposition bridge-review dispatches to the canonical bridge skill contract instead of the generic proposal-review skill.
- Keep verification dispatches routed to the verify skill and preserve fail-closed no-stdout behavior for bridge skills.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Focused Cursor harness tests prove the dispatcher-facing bridge-review route loads the bridge protocol contract required to write GO/NO-GO/VERIFIED files. |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Tests preserve fail-closed behavior when a bridge skill produces no stdout. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- A bridge-review Cursor dispatch prompt includes the gtkb-bridge skill contract, not proposal-review.
- Focused Cursor harness tests prove bridge-review, verification, and unknown skill routing behavior.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/cursor_harness.py`
- `platform_tests/scripts/test_cursor_harness.py`

## Recommended Commit Type

`feat`
