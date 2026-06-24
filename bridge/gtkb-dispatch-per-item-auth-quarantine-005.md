REVISED

# Per-Item Authorization Quarantine for Dispatch Head-of-Line Blocking

bridge_kind: prime_proposal
Document: gtkb-dispatch-per-item-auth-quarantine
Version: 005
Status: REVISED
Date: 2026-06-23
Responds-To: bridge/gtkb-dispatch-per-item-auth-quarantine-004.md

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019ef4ff-74fc-7a30-8d05-5994ac4fd565
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex desktop automation session; approval_policy=never; resolved_role=prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4770
target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py"]

## Summary

This revision responds to `bridge/gtkb-dispatch-per-item-auth-quarantine-004.md`.

The prior revision fixed mandatory specification linkage, but Loyal Opposition found the implementation scope incomplete because both live dispatch substrates contain the same batch authorization failure mode:

- `scripts/cross_harness_bridge_trigger.py`
- `scripts/single_harness_bridge_dispatcher.py`

This revision expands the proposal to cover both substrates and their focused tests. It also records the live dirty baseline on `scripts/cross_harness_bridge_trigger.py`: that file currently carries active WI-4742 dispatch-loop health work. Implementation of WI-4770 must preserve that unrelated diff and show final changes scoped to authorization quarantine functions plus tests.

## NO-GO Findings Addressed

### Finding P1 - Single-harness dispatcher retains the same batch authorization head-of-line blocker

Response: target paths now include `scripts/single_harness_bridge_dispatcher.py` and `platform_tests/scripts/test_single_harness_bridge_dispatcher.py`.

The proposed behavior applies to both implementations of `_issue_dispatch_authorization_for_selected()`:

- cross-harness trigger: one unauthorizable GO item is quarantined without blocking later healthy GO items.
- single-harness dispatcher: one unauthorizable GO item is quarantined without blocking later healthy GO items.

The specification-derived verification plan now includes focused coverage for both dispatch substrates.

### Finding P2 - Cross-harness target path is already dirty from active WI-4742 implementation work

Response: this revision acknowledges the live dirty baseline. Scoped status showed `scripts/cross_harness_bridge_trigger.py` modified before WI-4770 implementation starts, with the visible dirty area tied to `gtkb-wi4742-autonomous-dispatch-loop-health`.

Implementation-start and the implementation report for WI-4770 must state whether WI-4742 has been committed/verified or, if not, show that WI-4770 preserves the active WI-4742 diff. The final report must include a scoped diff summary proving WI-4770 edits are limited to the authorization quarantine function(s) and tests, not the WI-4742 diagnose/heartbeat area.

## Problem

Both dispatch substrates issue implementation authorization packets for selected GO items as one batch. If one selected GO item raises `AuthorizationError`, the whole selected batch can fail and later healthy GO items are not dispatched.

Known examples:

- `scripts/cross_harness_bridge_trigger.py` has `_issue_dispatch_authorization_for_selected()` and catches one `AuthorizationError` as a batch-level `implementation_authorization_packet_failed`.
- `scripts/single_harness_bridge_dispatcher.py` has its own `_issue_dispatch_authorization_for_selected()` and the same batch-level failure pattern.

The desired behavior is per-item quarantine: malformed or insufficiently authorized GO items should be recorded as dispatch failures, while healthy GO items continue through authorization and dispatch.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - this is a small defect-origin reliability fix to existing dispatch behavior with no new public API.
- `GOV-STANDING-BACKLOG-001` - WI-4770 is an open work item under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - single-harness dispatcher behavior must keep routing healthy candidates when one candidate is malformed or unauthorizable.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - desktop task binding constraints remain unchanged while dispatch failure handling becomes per-item.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised proposal cites the governing specifications and carries concrete links in the bridge artifact.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives tests from the linked dispatcher and bridge-governance requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries project authorization, project id, work-item id, and target path metadata.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Prime Builder implementation must wait for a fresh Loyal Opposition GO and implementation-start authorization matching these expanded target paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dispatch failures and quarantine records remain durable repo artifacts rather than session-only memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, scope correction, and later verification evidence are preserved in the bridge/work-item chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the NO-GO lifecycle event produced this revised proposal artifact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in the GT-KB platform root; no adopter application surface is touched.

## Prior Deliberations

- `WI-4658` / `gtkb-dispatch-malformed-status-token-quarantine` established the per-item quarantine pattern in `_acquire_prime_work_intent_batch()` for malformed status tokens.
- `DELIB-S421` - owner AUQ Part A+B approval in session `fce4df4c-b66a-422f-a0af-d26c56ad3613`; owner selected the option to fix PB per-item quarantine and defer the specific `wi4586` thread.
- `bridge/gtkb-dispatch-per-item-auth-quarantine-001.md` - original NEW proposal.
- `bridge/gtkb-dispatch-per-item-auth-quarantine-002.md` - NO-GO requiring mandatory cross-cutting specification citations.
- `bridge/gtkb-dispatch-per-item-auth-quarantine-004.md` - NO-GO requiring the single-harness substrate and dirty-baseline acknowledgement.

## Owner Decisions / Input

Owner approval is already captured through AskUserQuestion evidence in `DELIB-S421`: owner selected "Both A + B" for the per-item quarantine fix plus the `wi4586` DEFERRED filing. Part B is already complete at `bridge/gtkb-wi4586-benchmark-informed-dispatch-enforcement-design-003.md`.

This revision adds no new owner decision. It corrects the implementation target scope so the proposal matches the live dispatch substrates implicated by the cited specs.

## Requirement Sufficiency

Existing requirements remain sufficient. The fix extends the per-item quarantine pattern already established for malformed bridge-status handling to the dispatch authorization phase, in both current dispatch substrates. No new public interface, bridge status token, schema, deployment, credential lifecycle change, MemBase mutation, or project-membership mutation is proposed.

## Proposed Changes

### File: `scripts/cross_harness_bridge_trigger.py`

In `_issue_dispatch_authorization_for_selected()`:

1. Issue authorization per selected GO item rather than as one fail-fast batch.
2. On `AuthorizationError`, record a per-item dispatch failure/quarantine with reason `impl_auth_quarantined` or an equivalent specific reason, then continue.
3. Collect successful packets for healthy items.
4. If every selected GO item is quarantined, return an explicit all-quarantined failure.
5. If at least one item succeeds, write authorization packet state for the healthy set and include quarantine detail in the result.
6. Preserve any active WI-4742 diagnose/heartbeat diff in this file.

### File: `scripts/single_harness_bridge_dispatcher.py`

Apply the same per-item authorization/quarantine semantics to its `_issue_dispatch_authorization_for_selected()` implementation. The scheduled/single-harness dispatcher must not keep the batch-level `implementation_authorization_packet_failed` head-of-line behavior when some healthy GO items remain dispatchable.

### Tests

Add focused regression coverage:

- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` covers one bad GO item plus one healthy GO item and verifies healthy dispatch succeeds while the bad item is quarantined.
- `platform_tests/scripts/test_single_harness_bridge_dispatcher.py` covers the same mixed batch behavior for the scheduled/single-harness dispatcher.
- Existing all-healthy authorization behavior remains covered or is extended to prove no regression.

## Explicit Non-Scope

- No dispatcher rule configuration changes.
- No bridge status-token changes.
- No deployment, credential, formal-artifact, MemBase, database, or project-membership mutation.
- No change to the already-filed `wi4586` DEFERRED entry.
- No overwrite or cleanup of unrelated active WI-4742 changes in `scripts/cross_harness_bridge_trigger.py`.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | Diff inspection confirms a small reliability defect fix over existing dispatch code and tests, with no new public API. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Focused single-harness test proves one unauthorizable GO item is quarantined while a healthy GO item still dispatches. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Existing single-harness task dispatch behavior remains intact for healthy items. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implementation starts only after this revised proposal receives Loyal Opposition GO and implementation-start authorization for all declared target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps executed cross-harness and single-harness tests to linked specs and includes observed results. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths remain under `E:\GT-KB\scripts\` or `E:\GT-KB\platform_tests\`; no `applications/` surface is touched. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Quarantine/failure records remain deterministic dispatch artifacts suitable for later diagnosis. |

Required implementation commands:

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-per-item-auth-quarantine
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-per-item-auth-quarantine
git diff --name-status -- scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
```

The implementation report must also state how it handled the pre-existing WI-4742 dirty baseline in `scripts/cross_harness_bridge_trigger.py`.

## Pre-Filing Preflight Subsection

The final draft preflights passed:

```text
python scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-dispatch-per-item-auth-quarantine-005.md
```

Observed result:

```text
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: []
```

```text
python scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-dispatch-per-item-auth-quarantine-005.md
```

Observed result:

```text
must_apply: 4, may_apply: 1, not_applicable: 0
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
Exit: 0
```

## Acceptance Criteria

- Applicability preflight passes on this revised proposal with no missing required or advisory specs.
- Loyal Opposition can review the expanded target scope covering both dispatch substrates.
- A bad GO item no longer blocks authorization/dispatch for later healthy GO items in either dispatch substrate.
- All-healthy batches preserve existing behavior.
- Implementation report explicitly accounts for the active WI-4742 baseline and proves WI-4770 did not overwrite it.
- No source edit occurs until a fresh Loyal Opposition GO exists for this revision.

## Risk and Rollback

Risk is moderate only because `scripts/cross_harness_bridge_trigger.py` currently has unrelated active WI-4742 edits. The implementation must work with that baseline, not reset it. Rollback is to revert the WI-4770 function/test edits after implementation; this proposal revision itself is append-only bridge history.

## Recommended Commit Type

`fix:` - repair to broken dispatch behavior with no new public capability surface.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
