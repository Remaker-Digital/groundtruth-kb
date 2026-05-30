REVISED
author_identity: Codex
author_harness_id: A
author_session_context_id: 019e425a-79e8-7351-80bc-38c73b0b9429
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning

# Implementation Proposal - LO Advisory Intake Inventory (WI-3296..WI-3307) - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-lo-advisory-intake-batch
Version: 003 (REVISED)
Author: Prime Builder (Codex, harness A)
Date: 2026-05-20 UTC
Session: 019e425a-79e8-7351-80bc-38c73b0b9429
Responds-To: `bridge/gtkb-lo-advisory-intake-batch-002.md`

Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-INTAKE-LO-ADVISORY-INTAKE-PARALLEL-BATCH
Project: PROJECT-GTKB-LO-ADVISORY-INTAKE
Work Item: WI-3296

target_paths: [".gtkb-state/advisory-dispositions/"]

## Revision Claim

This revision narrows the batch from final advisory disposition to non-mutating intake inventory only. It creates draft per-WI inventory records that preserve source advisory context, likely classification candidates, existing disposition evidence, and the owner-decision or approval-packet work still required.

This proposal does not authorize final `adopt`, `adapt`, `reject`, `defer`, or `monitor` decisions. It does not authorize Deliberation Archive inserts. It does not authorize WI status transitions. It does not treat bridge GO as a formal-artifact approval packet.

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
- DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - authorizes the `PROJECT-GTKB-LO-ADVISORY-INTAKE` project group for bridge dispatch.
- `DELIB-2077` - existing Prime `monitor` disposition for `gtkb-owner-role-switch-codex-loyal-opposition`, relevant to WI-3305 and carried forward instead of re-dispositioned.
- `DCL-PEER-SOLUTION-OWNER-GATE-001` - active design constraint requiring AUQ evidence for material `adopt`, `adapt`, `reject_with_spec_impact`, and `defer` classifications.

## Owner Decisions / Input

No new owner decision is required for this narrowed inventory-only slice. Follow-on disposition proposals must ask required owner questions one at a time where `DCL-PEER-SOLUTION-OWNER-GATE-001` applies.

## Findings Addressed

### F1 - P1 - Material advisory classifications lack the required AUQ decision evidence

Response: Final classifications are removed from this implementation scope. Inventory records may include `candidate_classification` values for triage, but they must not mark any candidate as final. For `adopt`, `adapt`, `defer`, or reject-with-spec-impact candidates, the inventory must include `requires_auq: true` and a proposed single-question follow-up.

### F2 - P1 - Bridge GO is incorrectly treated as the formal-artifact approval packet for DELIB inserts

Response: Removed all Deliberation Archive insert and WI-resolution work from this slice. The inventory records may include the approval-packet path that a later final disposition would need, but no packet is created and no DA row is inserted here.

### F3 - P2 - Prior disposition state for WI-3305 is not carried forward

Response: WI-3305 must be recorded as `already_dispositioned` with `existing_disposition_delib: DELIB-2077`. The inventory must state that only a later WI-status cleanup may remain, and that any such cleanup must cite `DELIB-2077` as completion evidence.

## Proposed Scope

Create draft inventory records under `.gtkb-state/advisory-dispositions/`.

Each record must include:

- WI ID;
- advisory title;
- source path or Deliberation Archive reference;
- current WI state readback;
- candidate classification, explicitly marked non-final;
- `requires_auq` boolean;
- `requires_formal_artifact_packet` boolean;
- existing disposition evidence if already present;
- recommended follow-on bridge slug;
- one-sentence next owner question when an AUQ is required;
- no canonical mutation performed by this inventory record.

Expected records:

- `.gtkb-state/advisory-dispositions/WI-3296.md`
- `.gtkb-state/advisory-dispositions/WI-3297.md`
- `.gtkb-state/advisory-dispositions/WI-3298.md`
- `.gtkb-state/advisory-dispositions/WI-3299.md`
- `.gtkb-state/advisory-dispositions/WI-3300.md`
- `.gtkb-state/advisory-dispositions/WI-3301.md`
- `.gtkb-state/advisory-dispositions/WI-3302.md`
- `.gtkb-state/advisory-dispositions/WI-3303.md`
- `.gtkb-state/advisory-dispositions/WI-3304.md`
- `.gtkb-state/advisory-dispositions/WI-3305.md`
- `.gtkb-state/advisory-dispositions/WI-3306.md`
- `.gtkb-state/advisory-dispositions/WI-3307.md`
- `.gtkb-state/advisory-dispositions/SUMMARY.md`

## Explicitly Not Authorized

- Deliberation Archive insert/update.
- Work-item status changes.
- Formal approval packet creation.
- Final advisory classification decisions.
- Batch owner-question presentation.
- Any mutation outside `.gtkb-state/advisory-dispositions/`.

## Follow-On Workflow

After this inventory slice is VERIFIED, Prime should select one advisory at a time and either:

- ask the owner a single AUQ when `DCL-PEER-SOLUTION-OWNER-GATE-001` applies;
- file a narrow no-owner-needed monitor/reject-with-no-spec-impact disposition with a formal approval packet if the rule permits;
- file a follow-on implementation proposal for `adopt` / `adapt` after owner approval.

## Specification-Derived Verification Plan

| Behavior / spec obligation | Verification |
|---|---|
| All 12 WI inventory files and summary exist | `Get-ChildItem .gtkb-state/advisory-dispositions` plus filename count/readback |
| Inventory records are explicitly non-final | text check for `final_disposition: false` in every WI file |
| AUQ-required candidates are marked | text check for `requires_auq:` and candidate classifications |
| WI-3305 carries prior disposition evidence | text check for `DELIB-2077` in `WI-3305.md` and `SUMMARY.md` |
| No canonical DB/formal-packet mutation occurs | `git status --short -- groundtruth.db .groundtruth/formal-artifact-approvals` and report evidence |

## Acceptance Criteria

1. Twelve per-WI inventory records plus `SUMMARY.md` exist under `.gtkb-state/advisory-dispositions/`.
2. Every record states `final_disposition: false`.
3. Every material candidate classification records `requires_auq: true`.
4. WI-3305 cites `DELIB-2077` and is not re-dispositioned.
5. No DA, WI-status, or formal-approval packet mutation occurs.
6. Applicability and clause preflights pass before and after filing.

## Risk And Rollback

Risk: an inventory-only slice does not resolve the 12 work items. Mitigation: it creates a governed queue of one-at-a-time follow-ons without violating AUQ or formal-artifact approval boundaries.

Risk: `.gtkb-state` records are not final canonical dispositions. Mitigation: every record is explicitly non-final and names the required follow-on path.

Rollback: remove `.gtkb-state/advisory-dispositions/` inventory files. No canonical MemBase or Deliberation Archive state is changed.

## Pre-Filing Preflight Subsection

To be executed by the bridge revision helper before live filing:

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-lo-advisory-intake-batch --content-file .gtkb-state\bridge-revisions\drafts\gtkb-lo-advisory-intake-batch-003.md`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-lo-advisory-intake-batch --content-file .gtkb-state\bridge-revisions\drafts\gtkb-lo-advisory-intake-batch-003.md`

End of revision.
