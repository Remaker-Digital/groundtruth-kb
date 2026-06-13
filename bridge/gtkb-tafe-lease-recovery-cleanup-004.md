NEW

# TAFE Lease Recovery and Cleanup Service Implementation Report

bridge_kind: implementation_report
Document: gtkb-tafe-lease-recovery-cleanup
Version: 004
Responds-To: bridge/gtkb-tafe-lease-recovery-cleanup-003.md
Implements: bridge/gtkb-tafe-lease-recovery-cleanup-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-13 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ebfe9-a347-75c1-bc8d-503ad3042bca
author_model: gpt-5
author_model_version: 5
author_model_configuration: Codex desktop automation; Prime Builder durable role

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

Implemented WI-4494 as a bounded TAFE lease-recovery slice.

The implementation adds:

- `KnowledgeDB.list_expired_stage_leases` to find current active stage leases whose `expires_at` is at or before an explicit evaluation timestamp.
- `KnowledgeDB.recover_expired_stage_leases` to append a non-active `recovered` lease version and append an unclaimed stage-instance version in one transaction.
- `FlowRuntimeService.list_expired_stage_leases` and `FlowRuntimeService.recover_expired_stage_leases` service wrappers.
- `gt flow recover-leases` with `--as-of`, `--limit`, `--dry-run`, and `--json`.
- Focused service and CLI tests proving expired-only recovery, dry-run non-mutation, append-only history, stage requeue/unclaim behavior, and reclaim-after-recovery behavior.

No dispatch scoring, dispatch tick/health behavior, stuck-flow detection, dashboard telemetry, generated bridge view, dual-write mode, bridge-authority cutover, or implementation-flow pilot behavior was implemented.

## Files Changed

Claimed implementation files:

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/db.py`
- `groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py`
- `groundtruth-kb/tests/test_tafe_stage_leases.py`
- `groundtruth-kb/tests/test_tafe_flow_cli.py`

Pre-existing unrelated dirty files were present in the worktree during this run and are not claimed by this implementation report.

## Specification Links

- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - WI-4494 remains a parallel-run TAFE substrate slice; `bridge/INDEX.md` remains canonical.
- `SPEC-TAFE-R2` - recovery preserves single-claim semantics by making expired active leases non-active and appending unclaimed stage state.
- `SPEC-TAFE-R3` - recovery is bounded to expired active leases and does not widen into stuck-flow diagnosis.
- `SPEC-TAFE-R5` - the CLI evaluates actual expired lease state via `--as-of` / current time instead of blind bulk polling.
- `SPEC-TAFE-R6` - recovered lease rows include structured recovery metadata for later telemetry work.
- `SPEC-TAFE-R7` - recovery is exposed through a dedicated `gt flow` service command.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation does not alter bridge authority or write bridge runtime state outside this report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation stayed inside the GO-approved target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, and work-item metadata are carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - executed tests below map to each linked requirement.
- `GOV-STANDING-BACKLOG-001` - sibling backlog items WI-4499 and WI-4505 remain open and out of scope.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start packet `sha256:e45b3dce8f1594f28ce0bcbfa92b95e590b9bb9e5d619e13d2b7fbe1c7f6ce34` was created from the live GO before editing.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - implementation, tests, report, and forthcoming verification preserve the artifact lifecycle.

## Owner Decisions / Input

No new owner decision was required. This implementation used the active project authorization `PAUTH-PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE-TAFE-PHASE-1-LEASE-RECOVERY-WI-4494`, backed by `DELIB-20263158`, and the live Loyal Opposition GO at `bridge/gtkb-tafe-lease-recovery-cleanup-003.md`.

## Requirement Sufficiency

Existing requirements were sufficient. The implementation follows the GO-approved requirement-sufficiency claim in `bridge/gtkb-tafe-lease-recovery-cleanup-002.md` and did not discover a need for new or revised requirements.

## Implementation Details

`groundtruth-kb/src/groundtruth_kb/db.py` now compares ISO timestamps through a shared UTC parser, so `Z`, offset-aware, and naive timestamps are handled consistently. Expired active leases are selected from `current_stage_leases` where `lease_status = 'active'` and `expires_at <= as_of`.

Recovery is append-only:

- the previous lease row remains unchanged;
- a new version of the same lease id is appended with `lease_status = 'recovered'`;
- holder/session/acquired/heartbeat/TTL/expires data are preserved;
- `released_at` and recovery metadata record the recovery event;
- a new stage-instance version is appended with `claim_status = 'unclaimed'` and cleared holder/session fields.

`gt flow recover-leases --dry-run` reports candidates without mutation. Normal mode recovers candidates and reports the recovered rows.

## Backlog Readback

Live MemBase readback during report preparation showed:

- `WI-4494` - open; this report is the implementation evidence, pending Loyal Opposition verification.
- `WI-4499` - open; dispatch tick/health commands remain sibling work and were not implemented here.
- `WI-4505` - open; stuck-flow detection/self-diagnosis remains sibling work and was not implemented here.

## Spec-To-Test Mapping

- `SPEC-TAFE-R2` - `test_stage_lease_recovery_recovers_only_expired_active_leases` verifies expired active leases become non-active, the stage becomes unclaimed, history remains append-only, and the stage can be reclaimed.
- `SPEC-TAFE-R3` - the same recovery test verifies bounded recovery after expiry without stuck-flow diagnosis or autonomous actuation.
- `SPEC-TAFE-R5` - `test_flow_recover_leases_dry_run_and_recover_stage` verifies explicit operator evaluation through `gt flow recover-leases --as-of`, including dry-run and normal mode.
- `SPEC-TAFE-R6` - the recovery service test verifies structured recovery metadata is recorded on the recovered lease version.
- `SPEC-TAFE-R7` - the CLI test verifies recovery is available through the `gt flow recover-leases` service command.
- `SPEC-TYPED-ARTIFACT-FLOW-ENGINE-UMBRELLA` - the combined runtime/CLI tests verify the slice remains additive to the current parallel-run TAFE substrate.
- `GOV-STANDING-BACKLOG-001` - live backlog readback above confirms WI-4499 and WI-4505 remain open sibling items.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each linked behavioral requirement above maps to executed tests and observed pass results.

## Verification Commands

```text
python -m pytest groundtruth-kb\tests\test_tafe_stage_leases.py -q --tb=short
Observed: 5 passed in 2.60s

python -m pytest groundtruth-kb\tests\test_tafe_flow_cli.py -q --tb=short
Observed: 6 passed in 3.49s

python -m pytest groundtruth-kb\tests\test_tafe_runtime_tables.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py -q --tb=short
Observed: 14 passed in 9.15s

python -m pytest groundtruth-kb\tests\test_tafe_dispatch_policy.py groundtruth-kb\tests\test_tafe_stage_leases.py -q --tb=short
Observed: 16 passed in 2.78s

python -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py
Observed: All checks passed.

python -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\db.py groundtruth-kb\src\groundtruth_kb\typed_artifact_flow.py groundtruth-kb\tests\test_tafe_stage_leases.py groundtruth-kb\tests\test_tafe_flow_cli.py
Observed: 5 files already formatted.

git diff --check -- groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/typed_artifact_flow.py groundtruth-kb/tests/test_tafe_stage_leases.py groundtruth-kb/tests/test_tafe_flow_cli.py
Observed: exit 0; no whitespace errors. Git emitted CRLF normalization warnings for some touched files.
```

## Risk / Rollback

Primary risk was accidentally expanding WI-4494 into sibling dispatch or stuck-flow behavior. The implementation avoids that by limiting runtime mutation to recovered lease versions and unclaimed stage versions. Tests prove WI-4499 and WI-4505 remain unimplemented sibling scope.

Rollback is a single source/test revert of the five claimed target files before verification. Existing bridge and PAUTH evidence should remain in the append-only audit trail.

## Recommended Commit Type

Recommended commit type: feat:

feat: adds a new TAFE expired-lease recovery service/CLI behavior with focused tests.

## Bridge Filing

This report should be filed as:

```text
NEW: bridge/gtkb-tafe-lease-recovery-cleanup-004.md
```

under the existing `Document: gtkb-tafe-lease-recovery-cleanup` entry in `bridge/INDEX.md`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
