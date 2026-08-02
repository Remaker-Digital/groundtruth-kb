REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: reasoning_effort=default; thread_source=automation
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5448-dead-daemon-lease-restart
Version: 007
Responds to: bridge/gtkb-wi5448-dead-daemon-lease-restart-006.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5448-DEAD-DAEMON-LEASE-RESTART-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5448
related_work_items: ["WI-5427", "WI-5429", "WI-5451", "WI-5552", "WI-5566"]

target_paths: ["scripts/ensure_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]
implementation_scope: dead_daemon_orphan_lease_restart_admission_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
KB mutation: none; this proposal performs no KB mutation.

# WI-5448 Revised Implementation Proposal — Distinguish Dead-Daemon Orphan Leases Without Touching Live Runtime State

## Revision Claim

Version 006 is correct: the original four-target implementation proposal was substantive, and claim absence or carrier age could not convert it to terminal `NO-ACTION`. No WI-5448 implementation report, executed TEST-11552 result, independent post-implementation verdict, or attributable commit exists. WI-5448 remains open.

Current source still treats every aggregate document-lease count as active dispatch work even when lease evidence belongs only to a dead daemon and no provenance-valid live worker backs it. This revision proposes the narrow two-target prevention slice that can be implemented without adopting adjacent daemon/runtime work. It removes `scripts/gtkb_dispatcher_daemon.py` and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` from the implementation cohort, preserving WI-5552/WI-5566 ownership and avoiding a shared-file cycle.

## Requirement Sufficiency

**Existing requirements sufficient.** `WI-5448`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, and `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` already require fail-closed live-worker protection and bounded canonical daemon supervision. This revision changes only how the supervisor classifies existing lease/liveness evidence before deciding whether a successor may start; it creates no new dispatcher topology, runtime control, or product requirement.

## Current Evidence and Preimages

- `scripts/ensure_dispatcher_daemon.py` is tracked, Git-clean, byte-identical to HEAD, and SHA-256 `5F172CE9A0917532500632E91F37625975D5C4C140524428A27F3AEDE4B9C317`.
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py` is tracked, Git-clean, byte-identical to HEAD, and SHA-256 `8B50F98738CB396EF2A012AFA20D7070C512CD923935C834BC9A0644DFCA4975`.
- `scripts/gtkb_dispatcher_daemon.py` is clean at SHA-256 `E9A9DFB96D94D6623ACE9110A861AA901DFFC38864187C5D10B21BD3BFD2DE1C`, but is not a target in this revision.
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` is clean at SHA-256 `F68B9A8BEE0A8BA72073FE39AE545CDE1B8C89126BFDE33B1F4DB6C9FDB93C30`, but is not a target in this revision.
- The supervisor still classifies any aggregate `live_document_lease_count` as `dispatch_work_active`; the daemon report supplies lease document/PID/path and a count but no positive distinction between provenance-valid live-worker-backed leases and leases whose recorded owner is proven dead.
- TEST-11552 exists in MemBase but has no test file/function mapping and no last result/execution timestamp. This proposal maps it to focused deterministic coverage in the existing supervision test module.
- Generic commit `9373c523164ecfa8a2acadfe4c6e7fd1dcb008ee` changed all four historical proposal targets without WI-5448 attribution. Clean current bytes are baseline evidence, not WI-5448 implementation evidence.
- WI-5448 has active direct project membership. Exact PAUTH `PAUTH-DISPATCHER-BLACK-BOX-WI5448-DEAD-DAEMON-LEASE-RESTART-20260717` was append-only normalized to v2 under unchanged owner decision `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`: every allowed class, WI/spec boundary, scope sentence, and registered prohibition remains unchanged; only unregistered forbidden-operation tokens were removed. Configuration and `runtime_state` mutation classes remain excluded, while the unchanged scope expressly forbids TAFE/dispatcher configuration, lease/runtime-state mutation, live reset/restart, and unrelated work.

## Proposed Design

### Slice A — Typed lease/liveness classification in the supervisor

At the existing supervisor admission seam, derive one immutable classification from canonical daemon-status evidence and process provenance. The classification has exactly three outcomes:

1. `live_worker_backed`: at least one lease is backed by a currently live worker whose PID and create-time provenance match the recorded launch/lease evidence;
2. `proven_dead_owner_orphan`: every relevant lease belongs to a daemon/worker identity proven dead or provenance-mismatched, with no matching live worker; or
3. `unknown`: evidence is missing, malformed, ambiguous, stale without a provable owner, or internally inconsistent.

`live_worker_backed` and `unknown` fail closed as `dispatch_work_active`. Only `proven_dead_owner_orphan` may cease blocking supervisor restart admission. Aggregate counts alone cannot prove any outcome.

The supervisor must consume existing canonical status/evidence; it must not delete, expire, rewrite, release, reconcile, or otherwise mutate a lease or runtime record. It must not infer dead ownership from age alone. PID reuse is handled only by PID plus create-time provenance, never PID equality by itself.

### Slice B — Canonical successor admission, not activation in this work cycle

When daemon identity is proven dead and lease classification is `proven_dead_owner_orphan`, the existing supervisor decision may report that one canonical hidden successor is eligible to start. This proposal and its tests do not start a live successor. No live reset/restart, TAFE/dispatcher activation, topology/configuration change, operator quiesce, lease edit, or runtime-state mutation is authorized.

Production start behavior remains behind the existing canonical supervisor controls and all deployment/operation approvals. Implementation verification uses only isolated temporary roots, fake process provenance, and captured launch intents.

### Slice C — Deterministic tests

Extend only `platform_tests/scripts/test_dispatcher_daemon_supervision.py` to prove:

- a provenance-valid live worker plus lease blocks restart;
- a reused PID with create-time mismatch cannot borrow liveness;
- proven-dead ownership with no live worker is classified orphaned and no longer blocks the admission decision;
- unknown/malformed/mixed evidence fails closed;
- repeated evaluation is idempotent and never mutates lease/runtime evidence;
- at most one hidden canonical successor intent is produced in the isolated harness; and
- no TAFE/dispatcher configuration or live process operation occurs.

## Dependency and Collision Order

- WI-5429 remains the runtime-generation admission predecessor. Its physical chain is currently strict-invalid and latest physical status is NO-GO; it cannot be treated as terminal evidence.
- WI-5427's historical chain is strict-invalid even though a later physical file says WITHDRAWN. A fresh strict-resolvable post-WI-5429 successor must establish the usable generation-handoff predecessor.
- Implementation ordering is: strict WI-5429 disposition, strict post-WI-5429 WI-5427 successor disposition, then WI-5448. Filing this proposal does not satisfy those start gates.
- WI-5451 remains downstream and cannot treat this proposal as implemented or terminal.
- WI-5552 owns exited-worker launch/lease reconciliation; its current v007 proposal is test-only and no longer targets daemon source.
- WI-5566 remains a separate daemon overlap. This revision declares neither daemon source nor its daemon test, so the exact implementation cohort is disjoint.

## Acceptance Criteria

1. Only the two declared targets change, and both preimages match at implementation start.
2. The supervisor distinguishes live-worker-backed, proven-dead-owner orphan, and unknown lease evidence using PID plus create-time provenance.
3. Live or unknown evidence always blocks restart; only proven-dead ownership with no matching live worker can stop blocking admission.
4. No lease, runtime record, TAFE/dispatcher configuration, live worker, daemon, provider, operator-quiesce state, or external system is mutated.
5. Focused tests prove PID reuse, mixed/unknown evidence, idempotence, zero evidence mutation, and at-most-one hidden successor intent under isolated state.
6. WI-5429 and the strict post-WI-5429 WI-5427 successor are resolved before implementation starts.
7. Current independent GO, exact work-intent claim, schema-v3 start packet, unchanged preimages, independent verification, and governed finalization remain mandatory.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5448; DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION; PAUTH-DISPATCHER-BLACK-BOX-WI5448-DEAD-DAEMON-LEASE-RESTART-20260717 v2; bridge/gtkb-wi5448-dead-daemon-lease-restart-006.md",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001 with ADR-DISPATCHER-ARCHITECTURE-001, DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001, and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "Independent bridge GO, strict dependency clearance, exact claim, schema-v3 start, two-target implementation, implementation report, and independent VERIFIED.",
  "before_behavior": "Supervisor restart admission treats every aggregate lease count as active work, so leases backed only by a proven-dead daemon can block recovery indefinitely.",
  "after_behavior": "The supervisor fails closed for live or unknown evidence and stops treating leases as active only when exact PID/create-time evidence proves every relevant owner dead and no matching live worker exists, without mutating any lease/runtime record.",
  "self_descriptive_naming": "Typed outcome names live_worker_backed, proven_dead_owner_orphan, and unknown state the safety meaning at the decision point.",
  "obsolete_guidance_disposition": "Count-only liveness inference is removed from restart admission; historical bridge and generic-commit evidence remains preserved.",
  "history_preservation": "All bridge, PAUTH, MemBase, Git, lease, runtime, and dependency evidence remains append-only or byte-preserved; no prior artifact is rewritten.",
  "baseline": {
    "supervisor_sha256": "5F172CE9A0917532500632E91F37625975D5C4C140524428A27F3AEDE4B9C317",
    "supervision_test_sha256": "8B50F98738CB396EF2A012AFA20D7070C512CD923935C834BC9A0644DFCA4975",
    "test_record": "TEST-11552 exists but has no mapped function or execution result",
    "dependency_state": "WI-5429 and WI-5427 physical chains are not strict-resolvable terminal predecessors"
  },
  "expected_result": {
    "classification": "Only exact process provenance can prove live-worker backing or dead-owner orphan status.",
    "safety": "Live and unknown evidence remain blocking; no live worker or lease is disturbed.",
    "admission": "Isolated tests capture at most one canonical hidden successor intent without live activation."
  },
  "rollback": {
    "instructions": "Revert only the approved supervisor and focused-test hunks through governed authority.",
    "verification": "Re-run focused supervision tests and confirm lease/runtime/TAFE/dispatcher state is unchanged."
  },
  "hard_invariants": [
    "No live reset/restart, daemon or TAFE activation, configuration/topology change, lease/runtime-state mutation, provider request, Git operation, deployment, release, or external-system mutation.",
    "Unknown or mixed evidence fails closed and cannot enable a successor.",
    "PID equality without matching create-time provenance never establishes liveness.",
    "Only two declared clean targets are attributable to this implementation."
  ],
  "fail_closed_conditions": [
    "Missing, stale, invalid, or mismatched GO, dependency disposition, claim, PAUTH, start packet, PB role, or target preimage.",
    "Any implementation needs daemon source, daemon-test, configuration, runtime-state, lease, or live-process mutation.",
    "Evidence cannot distinguish a live worker from a dead/reused PID with exact create-time provenance.",
    "The test harness consults or mutates non-temporary TAFE/dispatcher/runtime state."
  ],
  "essential_context_preservation": "The design preserves v006's non-closure finding, the persistent defect, generic-commit provenance, active PAUTH v2, strict WI-5429/WI-5427 ordering, WI-5552/WI-5566 scope separation, disabled live dispatcher/TAFE posture, and all independent lifecycle gates."
}
```

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — canonical dispatcher/supervisor behavior.
- `ADR-DISPATCHER-ARCHITECTURE-001` — preserves the existing substrate and canonical hidden supervisor route.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` — fail-closed liveness and exact successor admission.
- `GOV-SESSION-ROLE-AUTHORITY-001` — process or daemon identity cannot supply session-role authority.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — live workers, leases, routing, and runtime state cannot be impaired.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — exact active project membership and PAUTH govern authority.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — v2 PAUTH must be re-evaluated at filing/start.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — numbered-file currentness and fresh GO/claim/start are mandatory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governing specifications are cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — TEST-11552 coverage and independent verification derive from these requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — exact project, PAUTH, WI, and target cohort are declared.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets and evidence remain inside `E:/GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserve defect, PAUTH, test, report, and verdict traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — no terminal state is asserted without implementation/verification evidence.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` / `ADR-DISPATCHER-ARCHITECTURE-001` | Focused isolated tests prove the existing supervisor route receives one eligible successor intent only for proven-dead orphan state. |
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` | Exercise live, dead, reused-PID, mixed, malformed, missing, and repeated-evaluation cases with PID/create-time provenance. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Snapshot all fake lease/runtime inputs before/after; assert no mutation and no live process/config call. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Re-run schema-v3 applicability and exact v2 PAUTH evaluation before implementation start. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Require canonical current GO, strict dependencies, exact claim/start, independent verdict, and governed finalization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Map TEST-11552 and every executed focused/static check to the acceptance criteria in the implementation report. |

## Risks and Rollback

The critical risk is a false orphan classification that disturbs live work. Exact PID/create-time provenance, three-state classification, unknown fail-closed behavior, zero lease/runtime mutation, and isolated tests bound that risk. Dependency drift is a second risk; implementation cannot start until strict WI-5429/WI-5427 predecessors are established. Rollback is limited to the two approved hunks; bridge and PAUTH history remain append-only.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes bounded PAUTH carriers and governed proposals for in-scope fleet defects while preserving every exact later gate.
- PAUTH v2 is a taxonomy-only normalization under that unchanged decision and does not expand authority.
- No new owner decision is required to file this two-target proposal. No live restart/activation is requested or authorized.

## In-Root and Append-Only Evidence

Both declared targets are inside `E:/GT-KB`. The numbered bridge chain and PAUTH versions remain append-only. No source, test, Git, lease, runtime, TAFE/dispatcher, or index-lock mutation occurs during proposal filing.

## Essential Context Preservation

This proposal preserves the original defect and test intent, v006's correction, exact clean preimages, generic-commit non-attribution, PAUTH v2 normalization, strict dependency defects/order, adjacent WI ownership, non-activation boundary, risk controls, rollback, and the complete independent review/claim/start/verification lifecycle.
