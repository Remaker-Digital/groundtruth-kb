NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Release exited D/F document leases after mixed concurrent outcomes

bridge_kind: prime_proposal
Document: gtkb-wi5552-exited-worker-lease-reconciliation
Version: 001
Date: 2026-07-18 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5552

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "platform_tests/scripts/test_wi5552_exited-worker-reconciliation.py", "bridge/hunks/gtkb-wi5552-exited-worker-lease-reconciliation.patch"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Prove and, only where the new integration fixture fails, repair exact-once reconciliation of authoritative exited D/F launches across the runtime ledger, daemon tick, report liveness projection, and per-launch document leases without duplicating terminal WI-5208 or mutating dispatcher configuration/runtime state.

Work item description: Canonical dispatcher evidence on 2026-07-18 reports mixed D/F exits, stale document leases, and deferred runtime generation handoff. Dispatch 2026-07-18T07-44-57Z-loyal-opposition-F-7df449 started at 07:44:57Z and its canonical recent-run record reached state exit_nonzero with exit code 1, zero stdout bytes, 306 stderr bytes, and last modification at 07:45:03Z, yet dispatcher liveness continued counting its PID as a live worker for roughly one hour. Other exited D/F launches likewise retained document leases and blocked fresh dispatch. This regresses terminal WI-5208 concurrent-launch ledger reconciliation. Repair exact-once per-launch exit reconciliation so an authoritative exited run cannot remain live through a stale or reused PID; require PID plus create-time provenance for live classification; release only the exited launch's leases; preserve genuinely live workers and their leases; unblock fresh dispatch and generation handoff without direct lease edits, broad reset, worker interruption, or dispatcher configuration change.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5552` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`, `platform_tests/scripts/test_wi5552_exited-worker-reconciliation.py`, `bridge/hunks/gtkb-wi5552-exited-worker-lease-reconciliation.patch`.

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
- `ADR-DISPATCHER-ARCHITECTURE-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20265026` - Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff
- `DELIB-202665740` - WI-4995 Document Lease Held Health Classification -- Proposal Review Verdict
- `DELIB-20266642` - Verdict
- `DELIB-20260704-WITHDRAW-GTKB-WI4821-DISPATCH-CAN-RECEIVE-DISPATCH-DRIFT-RECONCILE-GO` - Withdraw stale GO for WI-4821 dispatch drift reconcile
- `DELIB-20266133` - Owner decision: re-home all open DISPATCHER-COMPLETION work and retire the project

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` - active project authorization covering `WI-5552`.

## Proposed Scope

- Add one isolated TEST-11610 integration fixture reproducing mixed concurrent D/F launches where one authoritative exit sidecar arrives while another worker remains live and a completed PID is dead or reused.
- Treat an authoritative parseable exit sidecar as terminal for its exact dispatch_id regardless of PID liveness; otherwise require PID plus create-time provenance before classifying a no-exit launch as live.
- Reconcile the exited launch exactly once, release only its recorded document leases exactly once, retain every genuinely live launch and lease unchanged, and refresh launch-ledger active/completed counts deterministically.
- Require daemon tick reconciliation before dispatch and generation-handoff quiescence decisions, and require the canonical report to agree with reconciled runtime state instead of preserving a stale live projection.
- If the new fixture passes against committed WI-5208/current-generation behavior, keep implementation test-only and record the historical incident as stale-generation exposure owned by WI-5429 then WI-5427; modify source only for an independently demonstrated residual gap.
- Serialize any source hunk after WI-5429 and WI-5427 terminal ownership and preserve current live workers, topology, roles, eligibility, routing, caps, allowances, leases, and dispatcher configuration.

## Cross-Harness Disposition

- **A**: Prime Builder dispatch path must reconcile its own exits identically but remains PB-only.
- **B**: Shared runtime parity only; not part of current qualification topology.
- **C**: Shared runtime parity only; not part of current qualification topology.
- **D**: Operative Loyal Opposition lane; mixed-exit fixture and fresh dispatcher proof are required.
- **E**: Shared runtime parity only; not part of current qualification topology.
- **F**: Operative Loyal Opposition lane and historical reproducer; exact exited-launch reconciliation and fresh proof are required.
- **G**: Not an operative harness; retired registry metadata only and excluded from qualification.
- **H**: Shared provider/runtime parity only; not part of current qualification topology.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5552; PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Canonical dispatcher evidence on 2026-07-18 reports mixed D/F exits, stale document leases, and deferred runtime generation handoff. Dispatch 2026-07-18T07-44-57Z-loyal-opposition-F-7df449 started at 07:44:57Z and its canonical recent-run record reached state exit_nonzero with exit code 1, zero stdout bytes, 306 stderr bytes, and last modification at 07:45:03Z, yet dispatcher liveness continued counting its PID as a live worker for roughly one hour. Other exited D/F launches likewise retained document leases and blocked fresh dispatch. This regresses terminal WI-5208 concurrent-launch ledger reconciliation. Repair exact-once per-launch exit reconciliation so an authoritative exited run cannot remain live through a stale or reused PID; require PID plus create-time provenance for live classification; release only the exited launch's leases; preserve genuinely live workers and their leases; unblock fresh dispatch and generation handoff without direct lease edits, broad reset, worker interruption, or dispatcher configuration change.",
  "after_behavior": "Prove and, only where the new integration fixture fails, repair exact-once reconciliation of authoritative exited D/F launches across the runtime ledger, daemon tick, report liveness projection, and per-launch document leases without duplicating terminal WI-5208 or mutating dispatcher configuration/runtime state.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5552",
    "project": "PROJECT-GTKB-RELIABILITY-FIXES",
    "target_paths": [
      "scripts/dispatcher_runtime.py",
      "scripts/gtkb_dispatcher_daemon.py",
      "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py",
      "platform_tests/scripts/test_wi5552_exited-worker-reconciliation.py",
      "bridge/hunks/gtkb-wi5552-exited-worker-lease-reconciliation.patch"
    ],
    "linked_specifications": [
      "SPEC-CENTRALIZED-DISPATCH-SERVICE-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "ADR-DISPATCHER-ARCHITECTURE-001",
      "DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001",
      "GOV-SESSION-ROLE-AUTHORITY-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
    ]
  },
  "expected_result": {
    "summary": "Prove and, only where the new integration fixture fails, repair exact-once reconciliation of authoritative exited D/F launches across the runtime ledger, daemon tick, report liveness projection, and per-launch document leases without duplicating terminal WI-5208 or mutating dispatcher configuration/runtime state.",
    "scope": [
      "Add one isolated TEST-11610 integration fixture reproducing mixed concurrent D/F launches where one authoritative exit sidecar arrives while another worker remains live and a completed PID is dead or reused.",
      "Treat an authoritative parseable exit sidecar as terminal for its exact dispatch_id regardless of PID liveness; otherwise require PID plus create-time provenance before classifying a no-exit launch as live.",
      "Reconcile the exited launch exactly once, release only its recorded document leases exactly once, retain every genuinely live launch and lease unchanged, and refresh launch-ledger active/completed counts deterministically.",
      "Require daemon tick reconciliation before dispatch and generation-handoff quiescence decisions, and require the canonical report to agree with reconciled runtime state instead of preserving a stale live projection.",
      "If the new fixture passes against committed WI-5208/current-generation behavior, keep implementation test-only and record the historical incident as stale-generation exposure owned by WI-5429 then WI-5427; modify source only for an independently demonstrated residual gap.",
      "Serialize any source hunk after WI-5429 and WI-5427 terminal ownership and preserve current live workers, topology, roles, eligibility, routing, caps, allowances, leases, and dispatcher configuration."
    ],
    "acceptance_criteria": [
      "TEST-11610 creates two concurrent launches, writes one nonzero or zero exit sidecar, leaves the other provenance-valid worker live, and proves only the exited launch becomes terminal.",
      "Repeated reconciliation releases the exited launch document leases once, never releases or rewrites the live launch leases, and yields exact active/completed ledger counts without PID-reuse false liveness.",
      "The daemon can offer fresh eligible work after the failed launch backoff contract permits it, and generation handoff no longer defers because of an already-exited launch or its released leases.",
      "Canonical dispatch report classifies parseable exit sidecars as exit_0 or exit_nonzero and requires PID/create-time agreement for no-exit live classification; runtime and report projections agree.",
      "The existing 208-test dispatcher-runtime suite and 62-test daemon suite, focused report tests, Ruff, format check, compilation, applicability, and clause preflights pass without stopping or restarting any worker or daemon."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Run TEST-11610 plus full runtime, daemon, and report suites and inspect canonical dispatcher telemetry for fresh exact-exit reconciliation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require latest GO, exact claim, schema-v3 implementation start, independent post-implementation verdict, and focused finalization. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Map TEST-11610 and all executed focused/static checks to the implementation report before VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Prove the existing daemon/runtime/report path remains the only dispatcher substrate and no alternate queue or reconciler is introduced. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Exercise mixed exits, missing sidecars, dead PID, reused PID, create-time mismatch, repeated ticks, and generation-quiescence classification. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | Assert launch identity uses exact dispatch_id plus PID/create-time provenance and cannot borrow liveness from an unrelated process. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Assert no live process termination, live lease release, eligibility/config mutation, alternate dispatch, or allowance reduction occurs. |

## Acceptance Criteria

- TEST-11610 creates two concurrent launches, writes one nonzero or zero exit sidecar, leaves the other provenance-valid worker live, and proves only the exited launch becomes terminal.
- Repeated reconciliation releases the exited launch document leases once, never releases or rewrites the live launch leases, and yields exact active/completed ledger counts without PID-reuse false liveness.
- The daemon can offer fresh eligible work after the failed launch backoff contract permits it, and generation handoff no longer defers because of an already-exited launch or its released leases.
- Canonical dispatch report classifies parseable exit sidecars as exit_0 or exit_nonzero and requires PID/create-time agreement for no-exit live classification; runtime and report projections agree.
- The existing 208-test dispatcher-runtime suite and 62-test daemon suite, focused report tests, Ruff, format check, compilation, applicability, and clause preflights pass without stopping or restarting any worker or daemon.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `platform_tests/scripts/test_wi5552_exited-worker-reconciliation.py`
- `bridge/hunks/gtkb-wi5552-exited-worker-lease-reconciliation.patch`

## Recommended Commit Type

`feat`
