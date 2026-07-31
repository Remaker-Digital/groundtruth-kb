NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; reasoning=xhigh; approval_policy=never; sandbox=danger-full-access

# WI-5139 - Restore fleet-goal MemBase carriers after WI-5138 rollback

bridge_kind: prime_proposal
Document: gtkb-wi5139-fleet-membase-carrier-restoration
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5139-FLEET-CARRIER-RESTORE-20260714
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5139

target_paths: ["groundtruth.db", "scripts/restore_fleet_membase_carriers.py", "platform_tests/scripts/test_restore_fleet_membase_carriers.py"]

implementation_scope: membase_governance_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Live fleet-goal reconciliation found that the current `groundtruth.db` no longer contains the governed carrier records for WI-5211, WI-5216, and WI-5222 through WI-5228, plus their linked tests and PAUTH rows. The rows are present in the in-root recovery snapshot `.gtkb-state/antigravity-wi5138-recovery-001/pre-finalization-groundtruth.db`, but absent from the live database after the WI-5138 PAUTH activation path. As a result, active GO threads for WI-5211, WI-5216, WI-5217, WI-5219, and WI-5222 report `bridge_metadata_unresolvable`, blocking the resumed fleet proof goal.

Implement a deterministic, idempotent carrier restoration that copies only the named fleet-goal WI/test/PAUTH carrier records from the recovery snapshot into live `groundtruth.db` when absent, preserves existing live rows when present, and records enough focused verification to show bridge metadata resolution has recovered. The repair must not edit dispatcher runtime JSON, lease files, harness roles, provider credentials, or unrelated dirty worktree files. Codex A remains Prime Builder only.

## Specification Links

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner-resumed fleet-goal directive and the missing carrier regression must be preserved as durable work item, test, decision, PAUTH, bridge, implementation, and verification evidence.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the MemBase repair requires this bridge proposal, independent Loyal Opposition review, a latest GO, implementation report, and verification.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5139-FLEET-CARRIER-RESTORE-20260714` bounds this repair to WI-5139.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH does not bypass bridge GO, work-intent claim, implementation-start, target path limits, or verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites the governance and dispatcher requirements before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, Work Item, and PAUTH metadata are declared above for implementation-start validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must map the repair to focused restoration tests and dispatcher metadata-resolution evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - bridge dispatcher queue state must reflect resolvable, governed metadata for active GO threads.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - final health/status checks must use canonical `gt bridge dispatch ...` controls, not direct runtime JSON edits.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher remains daemon-owned; the repair must not alter daemon ownership, roles, or dispatch topology.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation must preserve traceability from owner decision through work item/test/PAUTH/bridge/commit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the discovered rollback and metadata-unresolvable blockers trigger governed correction rather than ad hoc database edits.

## Prior Deliberations

- `DELIB-20260714-FLEET-GOAL-RESUME-CARRIER-REPAIR` - owner resumed the fleet proof goal and authorized a governed carrier repair path for the missing MemBase rows.
- `bridge/gtkb-wi5223-dispatch-eligibility-precedence-005.md` - current A-authored REVISED evidence for D review; A remains PB-only.
- `.gtkb-state/antigravity-wi5138-recovery-001/pre-finalization-groundtruth.db` - in-root recovery snapshot containing the missing WI/test/PAUTH carrier rows.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-20262356` — seed=search; bridge_thread; Bridge thread: gtkb-rc-gate-membase-seed-resilient-fixture (1 versions, ORPHAN)
- DA: `DELIB-20260635` — seed=search; owner_conversation; Dispatch/work-envelope design folded into the session-lifecycle envelope program
- DA: `DELIB-202666149` — seed=search; bridge_thread; WI-5200..5202 - Generous cloud-harness recovery, runtime envelopes, and truthful
- DA: `DELIB-20262280` — seed=search; bridge_thread; Bridge thread: gtkb-membase-effective-use-audit-test-restoration (1 versions, OR
- DA: `DELIB-20261850` — seed=search; bridge_thread; Bridge thread: gtkb-membase-effective-use-audit-test-restoration (2 versions, NO

## Owner Decisions / Input

The owner explicitly resumed the active fleet goal and required every discovered defect to be corrected through work item, linked test, PAUTH, bridge GO, implementation, testing, independent verification, and focused commit. `DELIB-20260714-FLEET-GOAL-RESUME-CARRIER-REPAIR` captures that directive and binds it to `WI-5139`.

## Requirement Sufficiency

Existing requirements are sufficient. This is a carrier restoration and metadata-resolution repair, not a new dispatcher behavior design. The bounded PAUTH and this proposal restrict the work to restoring or successor-linking missing governance carrier rows and proving the bridge queue no longer reports the fleet GO threads as metadata-unresolvable.

## Spec-Derived Verification Plan

| Governing surface | Verification | Expected result |
| --- | --- | --- |
| Artifact-oriented governance | Focused restoration test builds a temp live DB missing the named fleet carriers and a temp recovery DB containing them | The repair inserts only the missing WI/test/PAUTH carrier rows and is idempotent on a second run. |
| PAUTH and bridge authority | `implementation_authorization.py begin` is run only after a latest GO and matching claim for this slug | Implementation-start accepts only `groundtruth.db`, `scripts/restore_fleet_membase_carriers.py`, and `platform_tests/scripts/test_restore_fleet_membase_carriers.py`. |
| Dispatcher metadata resolution | After repair, run `gt bridge dispatch report --json --compact` and inspect the previously blocked GO threads | Fleet GO threads no longer fail solely because WI/test/PAUTH carrier metadata is absent. |
| A PB-only boundary | Verify `gt harness roles` and bridge author metadata | A remains role `[prime-builder]` and does not author GO/NO-GO/VERIFIED. |
| Focused tests | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_restore_fleet_membase_carriers.py -q --tb=short` | Restoration behavior and idempotency pass. |
| Dispatcher controls | `gt bridge dispatch report --json --compact`, `gt bridge dispatch daemon status --json`, and final fleet health/status checks | Daemon remains healthy; no direct runtime JSON or lease mutation is used. |

## Acceptance Criteria

- `WI-5139`, `TEST-11305`, the owner decision record, and the PAUTH remain live and traceable.
- The repair restores or successor-links the missing carrier rows for WI-5211/WI-5216/WI-5222-WI-5228 and their linked tests/PAUTHs from governed in-root evidence.
- Existing live rows are never overwritten with older snapshot content.
- The implementation is idempotent and reports inserted/skipped rows.
- Bridge dispatch reports no `bridge_metadata_unresolvable` blockers caused by the missing fleet-goal carrier rows.
- No dispatcher runtime JSON, lease file, provider credential, harness role, or unrelated dirty file is edited.
- A remains PB-only throughout; independent LO verification is dispatcher-produced.

## Risk / Rollback

Primary risk: copying rows from a snapshot could reintroduce stale carrier metadata if a newer live row already exists. Mitigation: the repair inserts only absent rows and leaves existing live rows untouched; tests cover idempotency and non-overwrite behavior. Secondary risk: repairing carrier rows could unblock several GO threads at once; mitigation is to inspect dispatcher state immediately after repair and continue oldest/highest-priority governed work deliberately.

Rollback is a focused revert of the WI-5139 commit plus a targeted database restore from the pre-repair backup if verification finds incorrect carrier insertion. Because the script is idempotent and does not overwrite existing rows, rollback should be needed only for an incorrect allowlist or schema mismatch.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi5139-fleet-membase-carrier-restoration`; no dispatcher runtime files or leases are edited. Dispatcher/TAFE state plus the numbered bridge file chain remain the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(governance)`: restores governed MemBase carrier metadata required for the active dispatcher-produced fleet proof goal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.)*
