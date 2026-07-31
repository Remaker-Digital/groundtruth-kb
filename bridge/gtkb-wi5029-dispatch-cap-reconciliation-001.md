NEW
author_identity: Codex Prime Builder A
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop Prime Builder; interactive build envelope; approval_policy=never

# Implementation Proposal - Reconcile two divergent per-role dispatch concurrency caps: unwired WI-3375 slot module (LO=3/Prime=2) vs live CA9165 flat-3

bridge_kind: prime_proposal
Document: gtkb-wi5029-dispatch-cap-reconciliation
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5029-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5029

target_paths: ["scripts/dispatcher_runtime.py", "scripts/bridge_dispatch_concurrency.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py", "platform_tests/scripts/test_bridge_dispatch_concurrency.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Reconcile the live dispatcher per-role cap implementation with the unwired WI-3375 slot-file cap module so maintainers have one authoritative cap mechanism/default story.

Work item description: LO investigation (2026-07-05) of dispatcher concurrency limits found two independent per-role concurrency implementations with divergent defaults and mechanisms, only one wired. LIVE: CA9165 inline cap in scripts/dispatcher_runtime.py (_max_live_dispatched_per_role, default flat 3 for BOTH roles; PID-token scan enforcement in _spawn_harness ~line 4250). UNWIRED: scripts/bridge_dispatch_concurrency.py (WI-3375) slot-file bounded pool with role-differentiated defaults loyal-opposition=3/prime-builder=2; docstring admits wiring deferred; repo-wide search shows it is imported by nothing except its own test (platform_tests/scripts/test_bridge_dispatch_concurrency.py) and historical bridge markdown. Related bridge threads: bridge/gtkb-perrole-concurrency-cap-dispatch-001.md (CA9165 live cap) and bridge/gtkb-bridge-scheduler-lanes-leases-slice-4-001.md (WI-3375 slot module). Impact P3 hygiene: a maintainer reading bridge_dispatch_concurrency.py to determine live caps would wrongly conclude Prime is capped at 2. The S350 throughput directive referenced in the module (LO 2-4, Prime 1-3) suggests role-differentiated caps were design intent, which the live flat-3 does not honor. Disposition options: wire the slot module in and retire the CA9165 inline cap, OR retire/mark the slot module superseded and reconcile intended defaults. Consideration-only capture; not implementation approval.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5029` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/bridge_dispatch_concurrency.py`, `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`, `platform_tests/scripts/test_bridge_dispatch_concurrency.py`.

## Specification Links

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
- `GOV-AUTOMATION-VALUE-VS-COST-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-20260705-WI5029-5031-IMPLEMENT-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5029-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-5029`.

## Proposed Scope

- Inspect the live CA9165 inline per-role cap in scripts/dispatcher_runtime.py and the unwired WI-3375 slot pool in scripts/bridge_dispatch_concurrency.py.
- Choose the least-regret reconciliation: either wire the slot module into the live dispatch path or explicitly mark/retire it as superseded while preserving tests for the retained cap mechanism.
- Preserve global-cap precedence, per-role cap suppression reason metadata, and role-scoped count semantics.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py and platform_tests/scripts/test_bridge_dispatch_concurrency.py to verify dispatcher-owned cap behavior remains deterministic. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run targeted dispatcher runtime cap tests showing cap logic remains daemon/dispatcher-owned and does not reintroduce harness-triggered control. |
| `GOV-AUTOMATION-VALUE-VS-COST-001` | Verify the retained cap gate remains a cheap deterministic pre-spawn check and no additional expensive worker launch is needed to discover cap saturation. |

## Acceptance Criteria

- One maintained per-role cap implementation/default contract is authoritative for live dispatch.
- Tests prove role-scoped cap behavior, below-cap spawning, at-cap suppression, and global-cap precedence.
- Any superseded module or divergent default is documented in code comments/docstrings so maintainers cannot mistake it for live behavior.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/bridge_dispatch_concurrency.py`
- `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`
- `platform_tests/scripts/test_bridge_dispatch_concurrency.py`

## Recommended Commit Type

`feat`
