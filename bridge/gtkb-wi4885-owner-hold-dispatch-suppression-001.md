NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

# Defect-Fix Proposal - WI-4885 owner-hold dispatch suppression

bridge_kind: prime_proposal
Document: gtkb-wi4885-owner-hold-dispatch-suppression
Version: 001
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4885

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/src/groundtruth_kb/bridge/disposition.py", "groundtruth-kb/tests/test_bridge_notify.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Fix a release-blocking dispatcher treadmill: latest `NO-GO` bridge entries that explicitly instruct the system to hold for an owner decision remain Prime-actionable for interactive review, but must not be selected for headless auto-dispatch.

## Claim

The dispatcher should honor explicit owner-decision hold language in the latest bridge status-bearing file as a non-dispatchable state for headless automation, without changing manual bridge visibility or the formal `DEFERRED` owner-only status contract.

## Defect / Reproduction

`bridge/gtkb-wi4885-dispatch-topology-activation-010.md` is the latest WI-4885 entry and says, in its required revisions, `Hold for Owner Decision`. It also instructs Prime not to apply the WI-4885 topology mutation until Mike decides whether to revise the topology or wait for a working Cursor Agent CLI.

Despite that hold, `gt bridge dispatch status --json` and `gt bridge dispatch health --json` show one pending Prime dispatch for Codex `A`, with the latest run failing as `subprocess_execution_failed` and leaving dispatcher health at `WARN`. The existing WI-4844 work-intent filter suppresses already-held Prime work, but it correctly does not solve owner-decision holds because the latest WI-4885 bridge item remains `dispatchable=True`.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py`, `groundtruth-kb/tests/test_bridge_notify.py`, `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`, and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`.

## Requirement Sufficiency

Existing requirements sufficient. The bridge protocol already defines owner-decision-blocked parking through `DEFERRED`, and the current dispatch item model already carries `dispatchable` so headless dispatch surfaces can suppress non-runnable work while keeping it visible to interactive scans.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires correct role/status handling for status-bearing bridge files.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the governing implementation and verification specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification to map tests back to the linked specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the project authorization, project, and work item metadata lines above.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - requires dispatcher selection to dispatch only runnable work to appropriate harness targets.
- `ADR-DISPATCHER-ARCHITECTURE-001` - constrains cross-harness trigger, daemon, and single-harness dispatcher parity.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` - release readiness requires evidence that dispatcher health is not degraded by known non-runnable bridge work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires durable bridge evidence for the defect and fix rather than scratchpad-only state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - supports preserving this correction as governed bridge/test/source artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs when transient observations become durable work artifacts.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner made Harness Parity Phase 2 a release blocker and authorized bounded parity implementation.
- `DELIB-20266276` - owner scope-locked the daemon resilience and full-harness activation program that includes WI-4885.
- `bridge/gtkb-wi4885-dispatch-topology-activation-010.md` - latest WI-4885 verdict explicitly holds the topology mutation for owner decision.
- `bridge/gtkb-wi4844-dispatch-claim-churn-livelock-guard-004.md` - verified the work-intent claim filter; this proposal addresses the separate owner-hold dispatchability gap left after that fix.

## Owner Decisions / Input

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` authorizes bounded implementation of release-blocking Harness Parity Phase 2 gaps through the normal bridge process.
- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` is active and includes `WI-4885`.
- This proposal does not decide the WI-4885 topology question. It preserves that owner decision by preventing headless workers from repeatedly attempting it.

## Proposed Scope

1. Add a narrow owner-hold classification at the shared bridge-dispatch item derivation layer.
2. Detect explicit latest-file hold language such as `Hold for Owner Decision` on Prime-dispatchable statuses and set `dispatchable=False` while keeping the item visible in Prime-actionable/manual scan surfaces.
3. Keep `DEFERRED` unchanged as the canonical owner-only parked bridge status; this fix is a headless-dispatch guard for latest status files that already disclose an owner-decision blocker but have not been converted to `DEFERRED`.
4. Verify cross-harness trigger, daemon, and single-harness dispatcher consumers all respect the derived non-dispatchable flag and do not spawn or count owner-held items as runnable.
5. Do not mutate WI-4885 topology, harness roles, dispatcher topology, provider credentials, or production/GitHub settings.

## Specification-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add/update tests proving owner-held latest bridge entries derive `dispatchable=False` and are omitted from headless selected dispatch batches. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Run focused trigger, daemon, and single-harness dispatcher tests to prove all dispatch substrates share the same suppression behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify latest `NO-GO` remains Prime-visible/actionable for manual handling but is not auto-dispatchable. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | After implementation, clear stale runtime failure state only through dispatcher control and confirm health no longer reports a pending owner-held Prime dispatch. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | File an implementation report with exact test commands and observed results for the linked specs. |

## Acceptance Criteria

- A fixture mirroring WI-4885 `NO-GO` plus `Hold for Owner Decision` remains in the Prime actionable list but has `dispatchable=False` and a classification explaining the owner hold.
- Cross-harness trigger, daemon shadow/live decision construction, and single-harness dispatcher skip owner-held items before spawning workers.
- Existing `DEFERRED`, `ADVISORY`, terminal-kind `GO`, ordinary `GO`, ordinary `NO-GO`, `NEW`, and `REVISED` dispatchability behavior remains unchanged.
- Focused tests and ruff checks pass on the changed files.
- Dispatcher health can be reset and rechecked without re-spawning Codex for WI-4885 solely because of the owner-held `NO-GO`.

## Risks / Rollback

Risk: over-broad text matching could suppress a real Prime revision task. Mitigation: match only explicit latest-file owner-hold markers and cover ordinary `NO-GO` fixtures with regression tests.

Risk: under-broad matching could leave some owner-decision blockers dispatchable. Mitigation: begin with the exact observed release blocker and record broader taxonomy work separately if new marker forms appear.

Rollback: revert the notify/disposition and focused test changes. Existing dispatcher filtering will return to prior behavior.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py`
- `groundtruth-kb/tests/test_bridge_notify.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

## Recommended Commit Type

`fix`
