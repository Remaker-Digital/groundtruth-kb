NEW
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f77f8-0931-75e2-a78d-7dea7037f743
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal - Prove the Dispatcher Next durable execution and A2A foundation

bridge_kind: prime_proposal
Document: gtkb-dispatcher-next-foundation-spike
Version: 001
Date: 2026-07-19 UTC

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5617

target_paths: ["groundtruth-kb/requirements-dispatcher-next-spike.txt", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py", "groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py", "platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

Prime Builder proposes a bounded, isolated compatibility spike for the accepted
Dispatcher Next architecture. The spike will prove or reject DBOS Transact
Python, the official A2A Python SDK, and one atomic multi-dimensional capacity
ledger before any production dispatcher integration is proposed.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-CENTRALIZED-DISPATCH-SERVICE-001`,
`SPEC-DISPATCHER-CONTROL-SURFACE-001`, and
`ADR-DISPATCHER-ARCHITECTURE-001`, together with owner decision
`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`, define the required
centralized service, governed control surface, durability, isolation, and
parallel migration constraints for this spike. WI-5618 owns any later
superseding ADR or requirement amendment; this proposal does not mutate formal
artifacts.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/requirements-dispatcher-next-spike.txt`, `groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py`, `groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py`, `platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires one persistent GT-KB dispatch service with harnesses acting only as consumers.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - requires governed CLI control of global and role caps, ranking, topology, reliability, and reporting without direct file mutation.
- `ADR-DISPATCHER-ARCHITECTURE-001` - requires durable centralized dispatch, recovery, harness isolation, and degraded continuity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves Prime-authored proposal and independent Loyal Opposition review authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves the accepted architecture, project, work items, tests, and adoption result as durable artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires the proposal and tests to remain linked to concrete requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires executed spec-derived tests before verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires exact PAUTH, project, work-item, and target-path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - preserves explicit owner-decision evidence and fail-closed owner-input boundaries.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the platform spike in GT-KB rather than an adopter application.
- `GOV-STANDING-BACKLOG-001` - keeps derived findings in MemBase instead of local notes.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex to self-enforce bridge and mutation gates.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires spike conclusions and derived defects to become governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - requires explicit lifecycle disposition of the spike and its findings.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - prohibits degradation of the live dispatcher while the replacement is developed in parallel.

## Prior Deliberations

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner acceptance of the replacement architecture and isolated Master Prime Builder program.
- `DELIB-202666925` - Loyal Opposition Review - WI-5233 Dispatch Selection Order Cap Repair (VERIFIED)
- `DELIB-202665720` - WI-4988 Direct Harness-to-Harness Launch Guard — Revised Proposal Review Verdict
- `DELIB-202666513` - Loyal Opposition Review - WI-5320 Starvation Fix
- `DELIB-202665729` - WI-4992 Impl-Auth Quarantine Dispatch Suppression — Proposal Review Verdict
- `DELIB-202667062` - NO-GO - WI-5427 Revised Proposal: Unaddressed Sibling-Thread File Conflict (WI-5429) And Unresolved Dispatcher-Hold Scope Ambiguity

## Owner Decisions / Input

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` accepts DBOS plus A2A as the preferred foundation subject to this bounded spike, authorizes an isolated parallel program, and requires independent review, shadowing, rollback, and terminal portfolio closure.
- `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719` is active, includes WI-5617 through WI-5624, and preserves every per-slice GO, work-intent, implementation-start, verification, activation, and release gate.

## Proposed Scope

- Add a spike-only pinned requirements manifest without modifying the currently dirty shared `groundtruth-kb/pyproject.toml` or `groundtruth-kb/uv.lock`.
- Add an isolated `groundtruth_kb.dispatcher_next` package with no imports from the live dispatcher runtime and no registration in the production CLI.
- Prove DBOS durable workflows and queue recovery against temporary SQLite databases under pytest-owned temporary directories.
- Prove an A2A task, structured artifact, status, cancellation, and failure round trip without contacting any real harness.
- Implement and stress an atomic capacity ledger that acquires all matching global, role, provider, model, and harness limits in one transaction.
- Prove deterministic semantic-operation idempotency across workflow retries without writing to the live `groundtruth.db`.
- Emit a machine-readable adoption result whose only valid outcomes are `adopt_dbos_a2a` or `reject_and_evaluate_hatchet`, with evidence for every mandatory predicate.
- Do not modify or restart the live daemon, supervisor, watchdog, dispatch rules, TAFE state, bridge routing, harness registry, roles, claims, leases, credentials, Git history, external systems, deployment, or release.

## Cross-Harness Disposition

- **A, B, C, D, E, F, H**: no real harness is launched or configured by this spike. All worker behavior uses deterministic stubs behind one protocol contract.
- Later adapter work is owned by WI-5621 and cannot begin from this proposal.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5617; TEST-11662; DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION; PAUTH-DISPATCHER-NEXT-PROGRAM-20260719",
  "canonical_authority": "SPEC-CENTRALIZED-DISPATCH-SERVICE-001, SPEC-DISPATCHER-CONTROL-SURFACE-001, ADR-DISPATCHER-ARCHITECTURE-001, and GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "gt bridge propose followed by the governed Codex bridge-propose helper",
  "before_behavior": "The live dispatcher uses fragmented runtime and configuration authorities; no isolated adopted durable-workflow and opaque-worker foundation has been proven on this host.",
  "after_behavior": "A six-file isolated spike produces binary evidence either adopting DBOS plus A2A or rejecting it and activating the Hatchet fallback evaluation, without changing live dispatch behavior.",
  "self_descriptive_naming": "dispatcher_next, capacity, foundation, protocol, and the focused foundation test name the bounded responsibilities directly.",
  "obsolete_guidance_disposition": "No production guidance or implementation is retired by this spike; WI-5618 owns formal architecture supersession after the result.",
  "history_preservation": "The numbered bridge chain, owner decision, project, PAUTH, work item, linked test, and adoption result remain append-only evidence.",
  "baseline": {
    "work_item": "WI-5617",
    "test": "TEST-11662",
    "project": "PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE",
    "live_dispatcher_authority_unchanged": true,
    "target_count": 6
  },
  "expected_result": {
    "allowed_outcomes": [
      "adopt_dbos_a2a",
      "reject_and_evaluate_hatchet"
    ],
    "required_dimensions": [
      "python_3_14",
      "durable_recovery",
      "a2a_task_artifact_round_trip",
      "atomic_intersecting_caps",
      "semantic_idempotency",
      "live_system_nonimpairment"
    ]
  },
  "rollback": {
    "instructions": "Under separate rollback authority, revert only the six new spike targets; never delete bridge, MemBase, project, PAUTH, or verification evidence.",
    "verification": "Run the focused nonimpairment and target-inventory assertions."
  },
  "hard_invariants": [
    "The live dispatcher remains the sole production routing authority.",
    "The spike never contacts or launches a real harness.",
    "No environment, TOML, daemon argument, registry, TAFE, or runtime sidecar becomes a new authority.",
    "Protected mutation requires independent GO, an exact claim, and implementation-start authorization."
  ],
  "fail_closed_conditions": [
    "Any mandatory predicate lacks binary evidence.",
    "Any cap is exceeded or any semantic transition is duplicated.",
    "Any target outside the six declared paths changes.",
    "The spike reads or mutates live dispatcher state.",
    "The adoption result is missing, malformed, or names an undeclared outcome."
  ],
  "essential_context_preservation": "The proposal retains the accepted architecture, isolation boundary, fallback, exact targets, specifications, tests, risks, rollback, and program sequencing."
}
```

## Specification-Derived Verification Plan

Candidate applicability preflight passed with
`missing_required_specs: []`, `missing_advisory_specs: []`,
`blocking_errors: []`, and packet
`sha256:632225689c11482cf2d815ba867059631a279aaa1b59b476cb44a958f4e6c164`.
The mandatory ADR/DCL clause preflight reported four `must_apply` clauses,
zero evidence gaps, and zero blocking gaps.

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Execute DBOS workflows through one isolated service facade, kill the executor during pending work, restart it, and assert exactly one semantic completion per workflow. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Configure global=16, PB=8, LO=8, provider=5, model=3, and harness-A=2 through the spike policy API; run at least 100 jobs and assert no observed dimension exceeds its limit. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Assert durable restart recovery, worker opacity, audit events, bounded retry, and deterministic operation IDs. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Snapshot relevant live dispatcher/config/TAFE/registry paths before and after the test and require byte-identical state; inspect process inventory to prove no real harness launch. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run proposal applicability and role-authority preflights; require independent LO GO before implementation and independent VERIFIED afterward. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Execute `TEST-11662` through `platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py` and carry exact commands/results into the implementation report. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Assert no owner input is inferred; unsupported or ambiguous adoption outcomes fail closed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Assert all targets remain under the GT-KB platform root and no Agent Red path is imported or changed. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Persist the adoption result in the implementation report and file every derived defect or fallback trigger as a governed WI before verification. |

## Acceptance Criteria

- Both pinned dependencies import and execute under the repository's Python 3.14 interpreter.
- At least 16 concurrent stub subprocess workflows complete, including an executor kill/restart, with one and only one semantic completion for each workflow ID.
- An A2A task completes status, structured artifact, failure, and cancellation round trips through the isolated protocol facade.
- At least 100 deterministic jobs obey simultaneous caps of global=16, PB=8, LO=8, provider=5, model=3, and harness-A=2; capacity acquisition and release remain atomic under contention and crash recovery.
- Repeating every semantic operation ID produces the original result without an additional domain mutation.
- The focused test emits a verification manifest with command, exit code, predicate, observed value, and cleanup fields; any failed or missing predicate exits nonzero.
- Relevant live dispatcher, TAFE, rules, registry, lease, and bridge-routing state remains byte-identical and no real harness process is launched.
- The implementation report records exactly one supported adoption outcome and files any derived defect before requesting VERIFIED.
- `python -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py -q --tb=short` passes.
- Ruff lint and format checks pass for every changed Python target.

## Risks / Rollback

Primary risks are DBOS SQLite behavior under Windows process interruption,
A2A protocol churn, dependency conflicts with the existing environment, and a
capacity design that appears correct under light load but leaks slots under
contention. The spike mitigates these with pinned spike-only requirements,
temporary databases, deterministic subprocess crash injection, at least 100
jobs, strict target isolation, and a binary fallback decision.

No existing file is modified by the implementation other than adding the six
declared targets. Rollback requires separate authority and removes or reverts
only those targets. It never deletes the proposal, verdicts, project, PAUTH,
work item, test, or adoption evidence.

## Files Expected To Change

- `groundtruth-kb/requirements-dispatcher-next-spike.txt`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_next/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_next/capacity.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_next/foundation.py`
- `groundtruth-kb/src/groundtruth_kb/dispatcher_next/protocol.py`
- `platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py`

## Recommended Commit Type

`feat`
