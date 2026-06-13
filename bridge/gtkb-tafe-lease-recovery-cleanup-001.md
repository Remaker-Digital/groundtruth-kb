NEW

# TAFE Lease Recovery and Cleanup Service Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-lease-recovery-cleanup
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: fa771f21-61e3-4123-9427-e73327ca1f1f
author_model: gpt-5
author_model_version: 5
author_model_configuration: Codex desktop; Prime Builder declared via ::init gtkb pb; default

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-LEASE-RECOVERY-WI-4494
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4494

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_stage_leases.py", "groundtruth-kb/tests/test_tafe_flow_cli.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement WI-4494, the next TAFE Phase 1 lease-subsystem slice: expired active stage leases should be detected and recovered through append-only MemBase state so the affected stage becomes unclaimed and eligible for later dispatch.

This proposal builds directly on the VERIFIED WI-4492 `stage_leases` substrate and the VERIFIED WI-4493 claim/release/heartbeat commands. It does not delete lease history. "Cleanup" in this slice means appending a recovered lease version and an unclaimed stage-instance version, leaving the previous lease lifecycle auditable for later telemetry.

The proposed CLI/service surface is bounded to local recovery of expired leases. It must not implement dispatch scoring, dispatch tick/health, stuck-flow dashboards, generated bridge-view authority, dual-write mode, implementation-flow pilot behavior, or any change to `bridge/INDEX.md` authority.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - WI-4494 remains a parallel-run TAFE substrate slice; canonical bridge state is still `bridge/INDEX.md` until a later governed cutover.
- `SPEC-TAFE-R2` - requires single-claim semantics with TTL, heartbeat renewal, explicit release, stale recovery, and cleanup status at stage granularity.
- `SPEC-TAFE-R3` - requires bounded autonomous recovery after lease expiry and recording recovery attempts without widening into stuck-flow diagnosis.
- `SPEC-TAFE-R5` - stale/expired leases are a legitimate need-driven activation source; the CLI evaluates actual expired lease state rather than blind bulk polling.
- `SPEC-TAFE-R6` - recovery results must expose structured lease lifecycle evidence suitable for later telemetry, without implementing dashboard integration here.
- `SPEC-TAFE-R7` - canonical typed artifact-flow data and services must be accessed through dedicated CLI/services, so recovery belongs behind `gt flow` service behavior.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal/report/verdict evidence remains append-only bridge state; `bridge/INDEX.md` remains canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - PAUTH, project, work item, target paths, and governing specs are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present in this proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map the recovery behavior to each linked TAFE/governance requirement.
- `GOV-STANDING-BACKLOG-001` - WI-4494 is the backlog authority for this bounded recovery slice; WI-4499, WI-4505, and later dashboard/cutover work remain separate backlog items.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation may proceed only under the active bounded PAUTH cited above and a forthcoming Loyal Opposition GO.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - recovery decisions become durable artifact state rather than session-only cleanup behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decision, PAUTH, proposal, implementation report, and verification verdict preserve the artifact lifecycle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4494 should close only after implementation evidence and terminal VERIFIED.

## Prior Deliberations

- `DELIB-20263158` - active WI-4494 PAUTH owner-decision basis; authorizes only expired stage-lease detection, append-only recovery state, stage requeue/unclaim behavior, and bounded CLI/service recovery.
- `DELIB-20263151` - WI-4493 PAUTH and owner pacing directive; WI-4494 builds on the verified claim/release/heartbeat behavior.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - records the session-scoped never-self-review invariant that later dispatch/review flows must honor.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner selected the TAFE overhaul direction that produced SPEC-TAFE-R2/R3/R5/R6/R7 and WI-4494.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the TAFE specs, including SPEC-TAFE-R2/R3/R5/R6/R7, to `specified`.
- `bridge/gtkb-tafe-stage-leases-schema-004.md` - VERIFIED WI-4492 stage-lease substrate.
- `bridge/gtkb-tafe-flow-lease-commands-004.md` - VERIFIED WI-4493 claim/release/heartbeat commands.
- `bridge/gtkb-tafe-dispatch-policy-engine-006.md` - VERIFIED WI-4498 pure dispatch-policy engine; WI-4494 must not implement live dispatch tick/health.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No new owner decision is required. Existing authority is active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-LEASE-RECOVERY-WI-4494`, backed by `DELIB-20263158`. The deliberation applies the owner's autonomous PB backlog directive narrowly to WI-4494 and carries the requested 10-minute pause between work projects.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R2`, `SPEC-TAFE-R3`, `SPEC-TAFE-R5`, `SPEC-TAFE-R6`, `SPEC-TAFE-R7`, WI-4494, the VERIFIED WI-4492 lease table, and the VERIFIED WI-4493 lease commands provide enough detail for this bounded recovery/cleanup slice.

No new or revised requirement is needed because this proposal deliberately excludes dispatch scoring, live dispatch tick/health, stuck-flow detection, dashboard telemetry, generated bridge views, dual-write mode, bridge-authority cutover, and implementation-flow pilot behavior.

## Implementation Plan

1. Add low-level lease-recovery helpers in `groundtruth-kb/src/groundtruth_kb/db.py` / `typed_artifact_flow.py` that find current active stage leases whose `expires_at` is at or before an explicit evaluation timestamp.
2. Recover each expired lease by appending a new `stage_leases` version with a non-active recovery status, preserving original holder/session, acquisition, heartbeat, TTL, expiration, and metadata history.
3. Append a new `stage_instances` version for each recovered stage with `claim_status = unclaimed` and cleared holder/session fields so later dispatch can route it.
4. Add a bounded `gt flow recover-leases` CLI command with `--as-of`, `--limit`, `--dry-run`, and `--json` options. Dry run reports candidates without mutation; normal mode appends recovery state.
5. Add focused service and CLI tests proving expired lease recovery, non-expired lease preservation, dry-run non-mutation, append-only history, and sibling backlog boundaries.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
python -m pytest groundtruth-kb\tests\test_tafe_stage_leases.py -q --tb=short
Expected: pass; verifies WI-4494 service recovery, append-only lease history, stage requeue/unclaim behavior, and non-expired lease preservation.

python -m pytest groundtruth-kb\tests\test_tafe_flow_cli.py -q --tb=short
Expected: pass; verifies `gt flow recover-leases` normal and dry-run payloads plus existing claim/release/heartbeat CLI behavior.

python -m pytest groundtruth-kb\tests\test_tafe_runtime_tables.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py -q --tb=short
Expected: pass; verifies recovery remains compatible with the VERIFIED Phase 0 runtime table and CLI substrate.

python -m pytest groundtruth-kb\tests\test_tafe_dispatch_policy.py groundtruth-kb\tests\test_tafe_stage_leases.py -q --tb=short
Expected: pass; verifies recovery leaves dispatch policy as a pure selection engine while exposing unclaimed stages through lease availability state.

python -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py
Expected: pass.

python -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_stage_leases.py groundtruth-kb/tests/test_tafe_flow_cli.py
Expected: no whitespace errors.
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - combined runtime/CLI tests prove recovery remains a parallel-run TAFE service surface and does not change bridge authority.
- `SPEC-TAFE-R2` - stage-lease service tests prove stale active leases become recoverable, prior lease rows remain auditable, and recovered stages become unclaimed.
- `SPEC-TAFE-R3` - recovery tests prove bounded autonomous recovery after lease expiry without implementing broader stuck-flow diagnosis.
- `SPEC-TAFE-R5` - CLI dry-run and mutation tests prove recovery is triggered by actual expired lease state and explicit operator action.
- `SPEC-TAFE-R6` - structured payload assertions prove lease lifecycle/recovery evidence is available for later telemetry work.
- `SPEC-TAFE-R7` - CLI tests prove recovery is exposed through a dedicated `gt flow` service command.
- `GOV-STANDING-BACKLOG-001` - implementation report must read back WI-4499 and WI-4505 as open sibling work, not silently implemented.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - report must map each linked spec above to executed evidence.

## Risk / Rollback

Primary risk is over-expanding WI-4494 into dispatch tick/health, stuck-flow diagnosis, or dashboard telemetry. Mitigation: keep code limited to expired active stage-lease recovery and structured payloads; tests and report read-backs must prove WI-4499 and WI-4505 remain open.

Rollback is single-slice source/test rollback for the target files plus removal of the proposal/report/verdict chain only through normal bridge supersession rules. MemBase approval evidence should not be deleted; it remains durable governance history.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of the `gtkb-tafe-lease-recovery-cleanup` document list in `bridge/INDEX.md`; no prior version is deleted or rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

feat: adds a new TAFE lease recovery service/CLI behavior and focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
