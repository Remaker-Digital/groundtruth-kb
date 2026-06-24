REVISED

# Per-Item Authorization Quarantine for Dispatch Head-of-Line Blocking

bridge_kind: prime_proposal
Document: gtkb-dispatch-per-item-auth-quarantine
Version: 003
Status: REVISED
Date: 2026-06-23

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019ef4ff-74fc-7a30-8d05-5994ac4fd565
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex desktop automation session; approval_policy=never; resolved_role=prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4770
target_paths: ["scripts/cross_harness_bridge_trigger.py"]

## Summary

This revision responds to `bridge/gtkb-dispatch-per-item-auth-quarantine-002.md`.
The proposed implementation scope is unchanged: fix head-of-line blocking in
`_issue_dispatch_authorization_for_selected()` so one GO item's
`AuthorizationError` is quarantined per item instead of blocking the entire
Prime Builder dispatch lane.

The revision repairs the proposal metadata and `Specification Links` section so
the bridge applicability preflight can recognize the mandatory cross-cutting
specifications and advisory governance surfaces.

## NO-GO Findings Addressed

### FINDING-P1-001 - Missing Mandatory Cross-Cutting Specifications

Response: The `Specification Links` section below now cites the three missing
mandatory specifications exactly:

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`

It also cites the advisory specs reported by the same preflight:

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

No source or test scope changed.

## Problem

`_issue_dispatch_authorization_for_selected()` in
`scripts/cross_harness_bridge_trigger.py` creates authorization packets as a
batch. If any `create_authorization_packet()` call raises `AuthorizationError`
for a single GO item, the whole Prime Builder dispatch lane fails and later
healthy GO items are not dispatched.

Concrete example: `gtkb-wi4586-benchmark-informed-dispatch-enforcement-design`
had GO at `-002` with empty `target_paths`. That specific thread has since been
parked with `DEFERRED` at `-003`, but the structural head-of-line defect remains
for any future malformed or insufficiently authorized GO item.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` - this is a small, defect-origin reliability
  fix with one source target and no new public API.
- `GOV-STANDING-BACKLOG-001` - WI-4770 is an open work item under
  `PROJECT-GTKB-RELIABILITY-FIXES`.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - dispatch substrate behavior
  must continue routing healthy candidates when one candidate is malformed or
  unauthorizable.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - platform binding
  constraints remain unchanged.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised
  proposal explicitly cites the governing specifications and corrects the
  missing-linkage NO-GO.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan
  derives tests from the linked dispatcher and bridge-governance requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries
  project authorization, project id, work-item id, and target path metadata.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the proposal uses the canonical numbered
  bridge chain and keeps Prime Builder implementation behind Loyal Opposition
  GO plus implementation-start authorization.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dispatch-state and failure records
  remain durable artifacts instead of ambiguous session memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defect, proposed change, and
  verification evidence are preserved as a bridge/work-item artifact chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the NO-GO lifecycle event produced
  this revised proposal artifact.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the target path is in the GT-KB
  platform root; no adopter application surface is touched.

## Prior Deliberations

- `WI-4658` / `gtkb-dispatch-malformed-status-token-quarantine` established
  the per-item quarantine pattern in `_acquire_prime_work_intent_batch()` for
  `MalformedBridgeStatusError`.
- `DELIB-S421` - owner AUQ Part A+B approval in session
  `fce4df4c-b66a-422f-a0af-d26c56ad3613`; owner selected the option to fix PB
  per-item quarantine and defer the specific `wi4586` thread.
- `bridge/gtkb-dispatch-per-item-auth-quarantine-001.md` - original NEW
  proposal.
- `bridge/gtkb-dispatch-per-item-auth-quarantine-002.md` - NO-GO requiring
  mandatory cross-cutting specification citations.

## Owner Decisions / Input

Owner approval is already captured through AskUserQuestion evidence in
`DELIB-S421`: owner selected "Both A + B" for the per-item quarantine fix plus
the `wi4586` DEFERRED filing. Part B is already complete at
`bridge/gtkb-wi4586-benchmark-informed-dispatch-enforcement-design-003.md`.

This revision adds no new owner decision, does not broaden scope, and does not
authorize implementation before Loyal Opposition GO and implementation-start
authorization.

## Requirement Sufficiency

Existing requirements remain sufficient. The fix extends the per-item
quarantine pattern already established for malformed bridge status handling to
the dispatch authorization phase. No new public interface, bridge status token,
schema, deployment, credential lifecycle change, or formal artifact mutation is
proposed.

## Proposed Changes

### File: `scripts/cross_harness_bridge_trigger.py`

In `_issue_dispatch_authorization_for_selected()`:

1. Iterate over selected GO items one at a time.
2. Call `create_authorization_packet()` per item.
3. On `AuthorizationError`, record a per-item quarantine in
   `dispatch-failures.jsonl` with reason `impl_auth_quarantined`, then continue
   to the next item.
4. Collect successful packets.
5. If all GO items are quarantined, return an explicit failure reason such as
   `all_go_items_quarantined`.
6. If any item succeeds, write named packets and `current.json` for the healthy
   item set, returning success plus quarantine detail.

The pattern mirrors `_acquire_prime_work_intent_batch()`, which already
quarantines malformed bridge-status items instead of blocking the whole batch.

## Explicit Non-Scope

- No target paths beyond `scripts/cross_harness_bridge_trigger.py`.
- No change to dispatcher rule configuration.
- No bridge status-token change.
- No deployment, credential, formal-artifact, MemBase, or project-membership
  mutation.
- No change to the already-filed `wi4586` DEFERRED entry.

## Spec-Derived Verification Plan

| Specification | Verification |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | Diff inspection confirms a small single-file defect fix with no new public API. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Test a batch with one unauthorizable GO item and one healthy GO item; expect healthy dispatch success and bad-item quarantine. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify implementation starts only from this revised proposal after Loyal Opposition GO and implementation authorization. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map executed tests to linked specs and include observed results. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Confirm the only source target is under `E:\GT-KB\scripts\`. |

Required implementation commands:

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-per-item-auth-quarantine
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-per-item-auth-quarantine
```

## Pre-Filing Preflight Subsection

Candidate preflights were run against this completed revision draft before
filing:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatch-per-item-auth-quarantine-003.md
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-dispatch-per-item-auth-quarantine-003.md
```

Observed results are carried forward in the filing record by the governed
revision helper; the intended passing criteria are:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- clause preflight exit code `0`
- blocking gaps `0`

## Acceptance Criteria

- Applicability preflight passes on the revised proposal with no missing
  required or advisory specs.
- Loyal Opposition can review the source change on the original declared target
  path only.
- A bad GO item no longer blocks authorization/dispatch for later healthy GO
  items.
- All-healthy batches preserve existing behavior.
- No source edit occurs until a fresh Loyal Opposition GO exists for this
  revision.

## Risk and Rollback

Risk is low because the proposed pattern already exists in the adjacent
work-intent acquisition phase. Rollback is to revert the single function body
change after implementation; this proposal revision itself is append-only bridge
history.

## Recommended Commit Type

`fix:` - repair to broken dispatch behavior with no new capability surface.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
