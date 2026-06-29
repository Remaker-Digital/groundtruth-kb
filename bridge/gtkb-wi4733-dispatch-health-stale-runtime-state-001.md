NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1078-0168-7573-8a31-a68af5b9842a
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: codex-desktop-prime-builder-auto-builder

# Implementation Proposal - bridge dispatch health reports stale last_result as FAIL (no live recompute; orphaned/active-session records never clear)

bridge_kind: prime_proposal
Document: gtkb-wi4733-dispatch-health-stale-runtime-state
Version: 001
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4733

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

File a governed implementation proposal for `WI-4733` using deterministic project, authorization, target-path, and preflight wiring.

Work item description: gt bridge dispatch health reports FAIL by reading the persisted last_result in .gtkb-state/bridge-poller/dispatch-state.json instead of recomputing live state. Two failure modes observed 2026-06-21: (1) STALE LIVENESS - it reported prime-builder launch_failed with per_role_live=3 from a record 3h old; the trigger's own _count_live_dispatched_processes_for_role returned 0 live (the 3 PIDs had exited, exit_code 1073807364 = externally terminated). (2) ORPHANED RECORDS NEVER CLEAR - prime-builder:B last_result=launch_failed persists because B is the active interactive session and is never a headless dispatch target; --reset-recipient clears circuit_breaker/failure_count but NOT last_result/last_launch, so there is no operational path to clear it. Similarly a role that moves harnesses (e.g. A from loyal-opposition to prime-builder) leaves an orphaned loyal-opposition:A failure record. Fix: health should recompute live liveness (PID-alive) rather than trust last_result; treat active-session-own-harness and role-orphaned recipient records as non-failures; annotate staleness (last dispatch age) and the loop-prevention-disabled state ('disabled' not 'FAIL'). Discovered while diagnosing the GTKB_NO_CROSS_HARNESS_TRIGGER kill-switch incident.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4733` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`.

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

## Prior Deliberations

- `DELIB-20266268` - Owner decision: clear daemon residue WIs (WI-4859, WI-4861) before PHASE-Y
- `DELIB-20266140` - Owner decision: WI-4804 kill-switch handling - visibility (doctor warning), not auto-clear
- `DELIB-20266166` - Owner decision: WI-4804 scope split - kill-switch visibility now, dormancy auto-restart to the daemon program
- `DELIB-20266343` - Loyal Opposition Review - WI-4894 Restore pythonw-safe reaper output
- `DELIB-20266397` - Separation Check

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-RELIABILITY-FIXES-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4733`.

## Proposed Scope

- Reclassify stale or orphaned persisted dispatch runtime failure state so bridge dispatch health reflects live selected recipients instead of old dispatch-state rows.
- Annotate stale failure evidence as warning when recipient evidence points at a different role/harness, and avoid FAIL for role-moved or nonselected records.
- Preserve existing hard-fail behavior for current selected recipients with pending work and fresh failure evidence.

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

## Acceptance Criteria

- A stale launch_failed/provider_failure record whose recipient evidence no longer matches the selected recipient does not make health FAIL.
- Runtime classification includes stale-failure metadata and a warning finding when pending work exists but failure evidence points to another recipient.
- Existing selected-recipient runtime failures still produce FAIL, and existing nonselected failures remain ignored.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

## Recommended Commit Type

`feat`
