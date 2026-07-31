NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; reasoning=xhigh; approval_policy=never; resolved_role=prime-builder

# Implementation Proposal - Serialize implementation of GO'd bridge threads that share target_paths source files

bridge_kind: prime_proposal
Document: gtkb-wi4996-target-path-dispatch-serialization
Version: 001
Date: 2026-07-05 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4996

target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Serialize headless Prime implementation dispatch for GO bridge threads whose declared target_paths overlap, preventing one dispatched batch from entangling unverified source changes across work items.

Work item description: Observed 2026-07-03: WI-4995 (document-lease-held-health) and WI-4992 (impl-auth-quarantine-suppression) both list groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py in target_paths and were implemented in parallel by Codex-A without committing between them. The working-tree file ended up containing BOTH threads' changes (WI-4995 classifier branch + 11 WI-4992 quarantine-suppression matches) while WI-4992 was still mid-implementation (live go_implementation claim, canonical GO, no report). WI-4995's VERIFIED could not finalize because its pathspec-limited commit of bridge_dispatch_config.py would capture WI-4992's unverified in-progress code (governance-integrity violation); LO issued NO-GO on the contention. Root cause: nothing serializes implementation of multiple GO'd threads whose target_paths overlap on a source file. This is amplified by WI-4994 PB fan-out (parallel PB workers over independent documents) which does not account for source-file overlap between documents. Fix candidates: (a) dispatcher/impl-auth-start gate detects target_paths overlap with another open (GO/in-implementation) thread and serializes or warns; (b) PB fan-out (WI-4994) excludes documents whose target_paths intersect an already-selected sub-batch; (c) require commit-between-implementations when a PB session touches a shared file across threads. Evidence: bridge/gtkb-wi4995-document-lease-held-health-004.md NO-GO.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4996` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`.

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

## Prior Deliberations

- _No prior deliberations auto-loaded; author must confirm before review._

## Owner Decisions / Input

- `DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4996-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4996`.

## Proposed Scope

- Add Prime-dispatch target-path overlap serialization so a GO item whose implementation target paths intersect an earlier selected GO item is suppressed/deferred instead of dispatched in the same headless batch.
- Preserve existing work-intent/project claim filtering, document leases, selected-batch signature semantics, and provider-failure backoff behavior.
- Record deterministic suppression evidence for skipped overlapping GO items so dispatch health can distinguish intentional serialization from provider failure.

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
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py -q --tb=short |
| `ADR-DISPATCHER-ARCHITECTURE-001` | gt bridge dispatch status --json |

## Acceptance Criteria

- A dispatcher batch with two GO bridge documents sharing a source target path launches only the oldest eligible document and records a target-path-overlap suppression for the later one.
- A dispatcher batch with GO documents whose target_paths are disjoint still fans out up to the effective max-items cap.
- NO-GO revision dispatch and latest NEW/REVISED Loyal Opposition handling are unchanged.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`

## Recommended Commit Type

`feat`
