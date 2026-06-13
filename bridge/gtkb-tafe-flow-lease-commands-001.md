NEW

# TAFE Flow Lease Commands Proposal

bridge_kind: prime_proposal
Document: gtkb-tafe-flow-lease-commands
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: fa771f21-61e3-4123-9427-e73327ca1f1f
author_model: gpt-5
author_model_version: 5
author_model_configuration: Codex desktop; Prime Builder declared via ::init gtkb pb; default

Project Authorization: PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-LEASE-CLI-WI-4493
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4493

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py", "groundtruth-kb/tests/test_tafe_stage_leases.py", "groundtruth-kb/tests/test_tafe_flow_cli.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Implement WI-4493, the next Phase 1 Typed Artifact-Flow Engine lease-subsystem slice: replace the Phase 0 no-op `gt flow claim`, `gt flow release`, and `gt flow heartbeat` placeholders with bounded CLI/service behavior backed by the VERIFIED WI-4492 `stage_leases` MemBase substrate.

This proposal is intentionally bounded to active lease acquisition, explicit release, and heartbeat renewal. It must not implement expired-lease recovery or cleanup, dispatch policy/scoring, dispatch tick/health, generated bridge views, dual-write mode, implementation-flow pilot behavior, or any change to `bridge/INDEX.md` authority. WI-4494 remains the sibling work item for recovery/cleanup; WI-4498/WI-4499 remain the sibling dispatch-policy items.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - WI-4493 remains a parallel-run TAFE substrate slice. It introduces MemBase-backed lease commands while the file bridge and `bridge/INDEX.md` remain authoritative until a later governed cutover.
- `SPEC-TAFE-R2` - requires single-claim semantics at stage granularity, owner session/context identity, TTL, heartbeat renewal, explicit release, and dispatch-visible unclaimed stages. This slice implements the claim/release/heartbeat portion only.
- `SPEC-TAFE-R3` - requires bounded self-management and recovery after lease expiry. This slice records TTL/heartbeat/release state in the shape WI-4494 recovery will consume, but does not perform recovery or cleanup.
- `SPEC-TAFE-R7` - canonical typed artifact-flow data and services must be accessed through dedicated CLI/services. This slice moves the claim/release/heartbeat surface from no-op placeholders to service-backed `gt flow` commands.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal/report/verdict chain remains append-only bridge evidence; `bridge/INDEX.md` remains canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - PAUTH, project, work item, target paths, and governing specs are linked before implementation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - machine-readable project authorization metadata is present in this proposal header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map command/service tests to each linked TAFE and governance requirement.
- `GOV-STANDING-BACKLOG-001` - WI-4493 is the backlog authority for this bounded slice; WI-4494, WI-4498, and WI-4499 must remain open sibling work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation proceeds under the active bounded PAUTH cited above plus a forthcoming Loyal Opposition GO.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - lease state transitions become durable governed artifact state rather than session-only behavior.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner decision, PAUTH, bridge proposal, implementation report, and LO verdict preserve the artifact lifecycle evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4493 should close only after implementation evidence and terminal VERIFIED.

## Prior Deliberations

- `DELIB-20263151` - active WI-4493 PAUTH owner-decision basis; authorizes claim/release/heartbeat CLI/service behavior only, with bridge GO, implementation-start, report, VERIFIED, and the requested 10-minute pause before the next work project.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D1-20260612` - records the session-scoped never-self-review invariant that later dispatch/review flows must honor.
- `DELIB-BRIDGE-DISPATCH-OVERHAUL-D3-20260612` - owner selected the TAFE overhaul direction that produced SPEC-TAFE-R2/R3/R7 and WI-4493.
- `DELIB-TAFE-SPEC-PROMOTION-APPROVAL-20260612` - owner approved promoting the TAFE specs, including SPEC-TAFE-R2/R3/R7, to `specified`.
- `DELIB-TAFE-PHASE-0-ENABLEMENT-PAUTH-20260612` - Phase 0 TAFE substrate authority; this slice builds on the verified CLI skeleton instead of widening it silently.
- `bridge/gtkb-tafe-stage-leases-schema-004.md` - VERIFIED WI-4492 stage-lease substrate; the verdict confirms claim/release/heartbeat command behavior remained intentionally unimplemented and belongs to WI-4493.
- `bridge/gtkb-tafe-flow-cli-skeleton-004.md` - VERIFIED Phase 0 `gt flow` command skeleton; WI-4493 replaces only the three lease placeholders with real behavior.

## Owner Decisions / Input

No new owner decision is required. Existing authority is the active PAUTH `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-LEASE-CLI-WI-4493`, backed by `DELIB-20263151`. The deliberation records the owner's directive to continue PB-actionable bridge/backlog work autonomously through the bridge protocol, plus the pacing requirement to insert a 10-minute timer between work projects. WI-4493 is explicitly included in that authorization, and the authorization forbids recovery cleanup, dispatch policy, generated-view authority, dual-write mode, pilot eligibility expansion, implementation-flow pilot behavior, and bridge-authority changes.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA`, `SPEC-TAFE-R2`, `SPEC-TAFE-R3`, `SPEC-TAFE-R7`, WI-4493, the VERIFIED Phase 0 CLI/runtime substrate, the VERIFIED WI-4492 `stage_leases` substrate, and the active WI-4493 PAUTH provide enough requirement detail for this bounded claim/release/heartbeat slice.

No new or revised requirement is needed because this proposal deliberately excludes lease recovery/cleanup, dispatch scoring, dispatch tick/health, generated bridge views, dual-write mode, bridge-authority cutover, and implementation-flow pilot behavior.

## Implementation Plan

1. Add low-level lease-state helpers in `groundtruth-kb/src/groundtruth_kb/db.py` / `typed_artifact_flow.py` that acquire an active lease for a stage only when no current active lease exists, append a released version for the current holder, and append a heartbeat-renewed version for the current holder.
2. Preserve append-only version history in `stage_leases`; do not delete or overwrite prior lease rows.
3. Update `gt flow claim`, `gt flow release`, and `gt flow heartbeat` in `groundtruth-kb/src/groundtruth_kb/cli.py` to call the service layer and emit JSON-compatible payloads with `mutated`, `status`, `stage_instance_id`, `lease_id`, and holder/session evidence.
4. Provide deterministic options for holder identity and lease timing, scoped to local platform state only. No production deployment, external-system mutation, credential handling, or bridge authority change is in scope.
5. Add tests proving single active lease behavior, holder mismatch rejection, append-only release/heartbeat history, CLI success/error payloads, and sibling backlog boundaries.

## Spec-Derived Verification Plan

The implementation report must include these commands and expected outcomes:

```text
python -m pytest groundtruth-kb\tests\test_tafe_stage_leases.py -q --tb=short
Expected: pass; verifies the WI-4492 substrate still exists and WI-4493 adds bounded claim/release/heartbeat behavior with append-only lease history.

python -m pytest groundtruth-kb\tests\test_tafe_flow_cli.py -q --tb=short
Expected: pass; verifies `gt flow claim`, `gt flow release`, and `gt flow heartbeat` are service-backed commands with JSON payloads and command-level error handling.

python -m pytest groundtruth-kb\tests\test_tafe_runtime_tables.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py -q --tb=short
Expected: pass; verifies WI-4493 remains compatible with the VERIFIED Phase 0 runtime table and CLI substrate.

python -m pytest groundtruth-kb\tests\test_tafe_doctor.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py -q --tb=short
Expected: pass; verifies the lease-command slice does not regress TAFE doctor checks.

python -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py
Expected: pass.

python -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py
Expected: pass.

git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_stage_leases.py groundtruth-kb/tests/test_tafe_flow_cli.py
Expected: no output, exit 0.
```

Spec mapping:

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - combined runtime/CLI tests prove the new behavior remains a parallel-run TAFE service surface and does not change bridge authority.
- `SPEC-TAFE-R2` - stage-lease service tests prove single active lease semantics, holder/session identity, TTL/heartbeat state, and explicit release.
- `SPEC-TAFE-R3` - tests prove heartbeat/release state is retained for later recovery, while recovery/cleanup itself remains absent and assigned to WI-4494.
- `SPEC-TAFE-R7` - CLI tests prove claim/release/heartbeat are available through dedicated `gt flow` service-backed commands instead of ad hoc file or queue mutation.
- `GOV-STANDING-BACKLOG-001` - implementation report must read back WI-4494, WI-4498, and WI-4499 as open sibling work, not silently implemented.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - report must map each linked spec above to executed evidence.

## Risk / Rollback

Primary risk is over-expanding WI-4493 into lease recovery/cleanup or dispatch behavior. Mitigation: keep code limited to active claim, explicit release, heartbeat renewal, and command payloads; tests and the implementation report must prove WI-4494 and dispatch siblings remain open.

A second risk is introducing weak contention semantics in SQLite. Mitigation: implement claim through one short DB transaction or equivalent guarded current-row read/write path, and test the single-active-lease invariant at the service layer. Cross-process hardening may be refined later, but this slice must not pretend to solve recovery/cleanup or dispatch contention beyond the active single-holder rule.

Rollback is a normal source/test revert before VERIFIED. If a local database has appended lease rows during manual testing, the rows are append-only audit state; destructive DB cleanup remains out of scope.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `gtkb-tafe-flow-lease-commands` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

feat - this turns the existing TAFE lease CLI placeholders into bounded service-backed claim/release/heartbeat behavior with focused tests.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
