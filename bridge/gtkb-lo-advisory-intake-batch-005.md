REVISED
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-29-prime-builder-lo-advisory-intake-batch-revised-2
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; interactive Prime Builder session

# Implementation Proposal - LO Advisory Intake Inventory (WI-3296..WI-3307) - REVISED-2

bridge_kind: implementation_proposal
Document: gtkb-lo-advisory-intake-batch
Version: 005 (REVISED)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-29 UTC
Responds-To: `bridge/gtkb-lo-advisory-intake-batch-004.md` (GO) + implementation-start authorization-gate finding

Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH
Project: PROJECT-GTKB-LO-ADVISORY-INTAKE
Work Item: WI-3296

target_paths: [".gtkb-state/advisory-dispositions/"]

Recommended commit type: chore (no tracked diff; outputs are gitignored `.gtkb-state/` runtime inventory)

## Revision Claim

This REVISED-2 carries forward the GO'd `-003` scope **unchanged** and adds the mandatory `## Requirement Sufficiency` subsection required by the implementation-start authorization gate. The GO at `-004` approved `-003`, but `-003` omitted `## Requirement Sufficiency`; this is the same proposal-shape defect Loyal Opposition flagged on the sibling `gtkb-lo-hygiene-assessment-skill-build` thread (its `-003` NO-GO notes "Mechanical preflights do not catch this gap"). No scope, target_paths, or acceptance-criteria change. Re-GO requested.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-ARTIFACT-APPROVAL-001
- DCL-PEER-SOLUTION-OWNER-GATE-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - authorizes the `PROJECT-GTKB-LO-ADVISORY-INTAKE` project group for bridge dispatch.
- `DELIB-2077` - existing Prime `monitor` disposition for `gtkb-owner-role-switch-codex-loyal-opposition`, relevant to WI-3305 and carried forward instead of re-dispositioned.
- `DCL-PEER-SOLUTION-OWNER-GATE-001` - active design constraint requiring AUQ evidence for material `adopt`, `adapt`, `reject_with_spec_impact`, and `defer` classifications.
- `bridge/gtkb-lo-advisory-intake-batch-003.md` (REVISED) and `-004.md` (GO) - the prior GO'd proposal this REVISED-2 carries forward; the GO is the controlling approval.

## Owner Decisions / Input

No new owner decision is required for this narrowed inventory-only slice. Follow-on disposition proposals must ask required owner questions one at a time where `DCL-PEER-SOLUTION-OWNER-GATE-001` applies. WI-3296..WI-3307 routing is covered by the active `PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH` per project membership.

## Findings Addressed (carried forward from -003)

- F1 (material classifications lack AUQ evidence): final classifications removed; inventory records carry `candidate_classification` (non-final) and `requires_auq: true` where `DCL-PEER-SOLUTION-OWNER-GATE-001` applies.
- F2 (bridge GO mis-treated as approval packet): all DA insert / WI-resolution work removed; inventory records may name the approval-packet path a later disposition needs, but create none.
- F3 (WI-3305 prior disposition not carried forward): WI-3305 recorded as `already_dispositioned` with `existing_disposition_delib: DELIB-2077`.

## Proposed Scope

Create draft inventory records under `.gtkb-state/advisory-dispositions/`. Each record includes: WI ID; advisory title; source path or DA reference; current WI state readback; non-final candidate classification; `requires_auq` boolean; `requires_formal_artifact_packet` boolean; existing disposition evidence if present; recommended follow-on bridge slug; one-sentence next owner question when AUQ required; explicit `final_disposition: false`.

Expected records: `WI-3296.md` .. `WI-3307.md` (12 files) plus `SUMMARY.md`.

## Explicitly Not Authorized

- Deliberation Archive insert/update.
- Work-item status changes.
- Formal approval packet creation.
- Final advisory classification decisions.
- Batch owner-question presentation.
- Any mutation outside `.gtkb-state/advisory-dispositions/`.

## Requirement Sufficiency

Existing requirements sufficient. The WI-3296..WI-3307 batch is authorized under the active `PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH` (owner evidence `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`). This is a non-mutating, inventory-only slice that writes gitignored `.gtkb-state/` runtime records (no canonical MemBase, Deliberation Archive, or formal-artifact mutation; no tracked diff). The data shape and acceptance criteria fully specify the inventory. No new or revised requirement is required before implementation.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| All 12 WI inventory files and summary exist | `Get-ChildItem .gtkb-state/advisory-dispositions` filename count/readback |
| Inventory records are explicitly non-final | text check for `final_disposition: false` in every WI file |
| AUQ-required candidates are marked | text check for `requires_auq:` and candidate classifications |
| WI-3305 carries prior disposition evidence | text check for `DELIB-2077` in `WI-3305.md` and `SUMMARY.md` |
| No canonical DB/formal-packet mutation occurs | `git status --short -- groundtruth.db .groundtruth/formal-artifact-approvals` shows no change attributable to this slice |

## Acceptance Criteria

1. Twelve per-WI inventory records plus `SUMMARY.md` exist under `.gtkb-state/advisory-dispositions/`.
2. Every record states `final_disposition: false`.
3. Every material candidate classification records `requires_auq: true`.
4. WI-3305 cites `DELIB-2077` and is not re-dispositioned.
5. No DA, WI-status, or formal-approval packet mutation occurs.
6. Applicability and clause preflights pass before and after filing.
7. (Pending Codex) Re-GO on this REVISED-2 at `-006`.

## Risk And Rollback

Risk: an inventory-only slice does not resolve the 12 work items. Mitigation: it creates a governed queue of one-at-a-time follow-ons without violating AUQ or formal-artifact approval boundaries.

Rollback: remove `.gtkb-state/advisory-dispositions/` inventory files. No canonical MemBase or Deliberation Archive state is changed.

## Pre-Filing Preflight Subsection

Run after INDEX update (operative resolves to `-005`):

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-advisory-intake-batch`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-advisory-intake-batch`

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
