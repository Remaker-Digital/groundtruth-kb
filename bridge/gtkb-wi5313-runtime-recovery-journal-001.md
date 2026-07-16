NEW

# Implementation Proposal - Implement bounded resumable runtime operation recovery journal

bridge_kind: prime_proposal
Document: gtkb-wi5313-runtime-recovery-journal
Version: 001
Date: 2026-07-15 UTC
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 2026-07-15T22-10-38Z-prime-builder-A-d49d16
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; Prime Builder A; default reasoning configuration

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES
Work Item: WI-5313

target_paths: ["groundtruth-kb/src/groundtruth_kb/runtime_recovery/__init__.py", "groundtruth-kb/src/groundtruth_kb/runtime_recovery/store.py", "platform_tests/scripts/test_modernization_runtime_recovery.py"]

## Claim

Adopt the exact current three-file runtime-recovery candidate as the bounded owner for frozen modernization handles MOD-RI05, MOD-RI07, MOD-RI08, MOD-RI13, and MOD-RI16. The candidate provides a SQLite-backed append-only operation journal with atomic ownership, bounded retries, durable checkpoints, stale-owner denial, quarantine, completion, and read-only recovery observations.

## Requirement Sufficiency

Existing requirements sufficient. The frozen release-candidate manifest identifies the implementation and acceptance-test paths, WI-5313 records ownership, and the project PAUTH plus the linked specifications define the review, non-impairment, and verification floors. No new formal requirement is needed to review the exact existing bytes.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/runtime_recovery/__init__.py`, `groundtruth-kb/src/groundtruth_kb/runtime_recovery/store.py`, and `platform_tests/scripts/test_modernization_runtime_recovery.py`.

## Specification Links

- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - Requires concrete before/after evidence, hard invariants, fail-closed conditions, and rollback for the cross-cutting modernization candidate.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Requires independent GO before protected candidate adoption and independent VERIFIED after the implementation report.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires the previously ownerless candidate to acquire durable work-item and evidence ownership.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to identify every governing specification used by the slice.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires the complete eight-test runtime-recovery module and non-impairment evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires exact PAUTH, project, work-item, and target linkage.
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` - Keeps recovery state subordinate to explicit session, role, bridge, project, and harness authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Requires all live implementation and evidence dependencies to remain within `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires this implementation candidate to be preserved and reviewed as a durable project artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Requires the implementation report and independent verification lifecycle after adoption.

## Prior Deliberations

- `DELIB-202666274` - Owner authorization for the full modernization program while preserving bridge, independent review, and separate mechanical-operation gates.

## Owner Decisions / Input

- `DELIB-202666274` authorizes the Runtime Interfaces project implementation program. This proposal does not request or imply Git staging, commit, push, release, deployment, dispatcher/TAFE/harness mutation, destructive cleanup, or credential lifecycle authority.

## Proposed Scope

- Treat the exact current pre-start bytes and recorded SHA-256 hashes of the three untracked runtime-recovery candidates as foreign implementation content pending independent review; preserve them byte-for-byte during adoption.
- Adopt only the SQLite-backed runtime-recovery journal package and its complete focused acceptance test.
- Exclude `groundtruth.db` mutation, live dispatcher/TAFE/harness mutation, routing, activation, external systems, Git operations, cleanup, release, and deployment.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274; WI-5313; frozen modernization handles MOD-RI05, MOD-RI07, MOD-RI08, MOD-RI13, and MOD-RI16",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-RUNTIME-INTERFACES-20260715-PROJECT-SCOPE",
  "primary_route": "groundtruth_kb.runtime_recovery.RecoveryStore with platform_tests/scripts/test_modernization_runtime_recovery.py",
  "before_behavior": "The frozen modernization contract names runtime-recovery evidence, but the three untracked candidate files had no durable owning work item or independent adoption review.",
  "after_behavior": "WI-5313 owns one bounded, independently reviewed runtime-recovery package whose exact bytes and complete acceptance behavior are explicit.",
  "self_descriptive_naming": "runtime_recovery, RecoveryStore, AttemptClaim, OperationSnapshot, RecoveryObservation, and RuntimeStatus identify their authority and lifecycle roles directly.",
  "obsolete_guidance_disposition": "No guidance surface is made authoritative and no retired or historical artifact is loaded by the package.",
  "history_preservation": "Project, work-item, bridge, and runtime event history remains append-only; adoption does not rewrite existing history.",
  "baseline": {
    "groundtruth-kb/src/groundtruth_kb/runtime_recovery/__init__.py": "SHA256 274195F5433DF232D54F87B475B25B55C241CDEB0D84E9DE2F9793B98A17BF83",
    "groundtruth-kb/src/groundtruth_kb/runtime_recovery/store.py": "SHA256 FDD47B769ACD599288E7C563E3783BF87666AA650FB5DDBD9D6142F52F67A9D7",
    "platform_tests/scripts/test_modernization_runtime_recovery.py": "SHA256 612E8B78CADE9022772F217EC87258C82A90CCD7755B8E5DEE11631B2179C9A8",
    "focused_tests": "8 passed in 1.01 seconds"
  },
  "expected_result": {
    "bytes": "All three target hashes remain unchanged through the implementation report.",
    "tests": "All eight runtime-recovery tests pass.",
    "scope": "No path outside the exact three targets changes."
  },
  "rollback": {
    "instructions": "If independent verification finds impairment, leave the reviewed pre-start bytes unfinalized and file a revised proposal; any later removal requires separately reviewed rollback authority.",
    "test": "Re-run the eight focused tests plus release Ruff and format checks on the exact targets."
  },
  "hard_invariants": [
    "No groundtruth.db mutation",
    "No live dispatcher, TAFE, harness, routing, role, or credential mutation",
    "No Git staging, commit, push, release, deployment, cleanup, or external-system mutation",
    "Runtime recovery state never overrides project, bridge, session, or role authority"
  ],
  "fail_closed_conditions": [
    "Any pre-start target hash drift",
    "Any focused-test, Ruff, or format failure",
    "Any mutation outside the exact three targets",
    "Missing independent GO, implementation-start authority, implementation report, or VERIFIED verdict"
  ],
  "essential_context_preservation": "The package records only bounded operation recovery state and preserves all project, bridge, role, specification, and owner-decision authority outside itself."
}
```

## Specification-Derived Verification Plan

| Specification | Executed evidence required before implementation report |
|---|---|
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run all eight runtime-recovery tests, release Ruff and format checks on the exact three targets, compare all three SHA-256 hashes, and prove no unrelated path changed. |
| `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001` | Verify recovery state remains a local runtime interface and cannot override session-role, bridge, project, owner, or harness authority. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry the exact commands, observed results, target hashes, and spec-to-test mapping into the implementation report for independent review. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm every implementation and test dependency resolves inside `E:\GT-KB`. |

## Acceptance Criteria

- All three reviewed candidate files remain byte-identical through the implementation report.
- The complete runtime-recovery module passes all eight tests.
- Concurrent ownership, recovery, retry, quarantine, completion, collision, and observation semantics remain bounded and deterministic.
- Release Ruff and format checks pass for the exact three targets.
- No project SoT, runtime authority, or unrelated path is mutated.

## Risks / Rollback

The primary risk is adopting a plausible but incomplete recovery abstraction. Fail closed on hash drift, any focused-test or static-check failure, extra-path mutation, or missing independent evidence. Because this is byte-preserving candidate adoption, rollback before finalization is to leave the candidate uncommitted and file a revised proposal; no destructive cleanup is authorized here.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/runtime_recovery/__init__.py`
- `groundtruth-kb/src/groundtruth_kb/runtime_recovery/store.py`
- `platform_tests/scripts/test_modernization_runtime_recovery.py`

## Recommended Commit Type

`feat`
