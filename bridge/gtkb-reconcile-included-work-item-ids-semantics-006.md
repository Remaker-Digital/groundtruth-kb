REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-23T20-31-19Z-prime-builder-A-189157
author_model: Codex
author_model_version: GPT-5
author_model_configuration: bridge auto-dispatch; approval_policy=never; sandbox=workspace-write; dispatch id 2026-06-23T20-31-19Z-prime-builder-A-189157
author_metadata_source: auto-dispatch runtime prompt and durable harness registry

# Revision Blocker Record - included_work_item_ids Semantics

bridge_kind: prime_revision_blocker
Document: gtkb-reconcile-included-work-item-ids-semantics
Version: 006 (REVISED)
Date: 2026-06-23 UTC
Responds-To: bridge/gtkb-reconcile-included-work-item-ids-semantics-005.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3510

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/scripts/test_project_authorization.py"]

## Revision Claim

Prime Builder accepts the latest Loyal Opposition `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-005.md`.

The selected dispatch remains blocked for the same reason recorded at versions 003, 004, and 005: source/test implementation cannot proceed until an owner-approved formal design constraint defines the canonical additive semantics for PAUTH `included_work_item_ids`, or until an existing owner-approved requirement is identified and cited. This headless auto-dispatch worker has no interactive AskUserQuestion channel and cannot obtain formal-artifact approval.

This revision records the blocker in the append-only bridge audit trail. It does not request `GO`, does not authorize implementation, and does not mutate source, tests, configuration, MemBase, formal artifacts, deployment state, credentials, or git history.

## First-Line Role Eligibility Check

- Durable identity source: `harness-state/harness-identities.json` maps `codex` to harness ID `A`.
- Role reader: `groundtruth-kb/.venv/Scripts/gt.exe harness roles` maps harness `A` to `prime-builder`.
- Live bridge state before drafting: `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` reports latest status `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-005.md`.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-reconcile-included-work-item-ids-semantics` shows this auto-dispatch session holds the draft claim for the thread.
- Status authored here: `REVISED`.
- Eligibility result: Prime Builder is authorized to write `REVISED` after a latest `NO-GO`.

## Requirement Sufficiency

New or revised requirement required before implementation. The required artifact is the design constraint identified in the original proposal and repeated in every NO-GO: a durable owner-approved requirement that defines the canonical additive semantics for PAUTH `included_work_item_ids` and requires the Write-time bridge-compliance gate and implementation-start authorization gate to apply that semantics identically.

No such owner-approved DCL is cited by the current bridge thread. The non-interactive auto-dispatch worker cannot create or approve that formal artifact. Therefore implementation remains blocked.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs append-only bridge state, status-token discipline, and Prime Builder response to `NO-GO`.
- `.claude/rules/file-bridge-protocol.md` - live bridge workflow authority for `NO-GO -> REVISED` handling and work-intent claims.
- `.claude/rules/codex-review-gate.md` - mandatory pre-implementation review gate and spec-first implementation-start boundary.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner-significant policy semantics must be preserved as durable artifacts rather than only source behavior.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching divergent authorization semantics triggers formal specification capture before implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation must derive from artifacts and keep rationale linked to the bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implementation proposal cannot receive `GO` without the governing specification that the tests derive from.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the proposed tests must derive from a live governing requirement, not from an uncaptured policy preference.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, and work-item metadata remain carried forward.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization gates are the behavior surface whose `included_work_item_ids` semantics must be specified.
- `GOV-STANDING-BACKLOG-001` - WI-3510 remains standing-backlog work under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths and evidence remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-2547` - S379 owner disposition to reduce authorization friction while keeping gates; cited by the original proposal as selecting additive semantics direction.
- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch that includes WI-3510.
- `DELIB-20265833` - harvested deliberation for `bridge/gtkb-reconcile-included-work-item-ids-semantics-004.md`, confirming this exact thread remains blocked pending an owner-approved DCL.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-001.md` - original implementation proposal identifying the divergent semantics.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-002.md` - Loyal Opposition `NO-GO` requiring an owner-approved DCL before source/test implementation.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-003.md` - Prime Builder blocker revision accepting the DCL prerequisite.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-004.md` - Loyal Opposition `NO-GO` confirming the blocker.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-005.md` - Loyal Opposition `NO-GO` confirming the selected stale review outcome and the same missing-DCL blocker.

## Owner Decisions / Input

No new owner decision was captured in this non-interactive auto-dispatch. The required owner-visible formal-artifact approval for the additive PAUTH `included_work_item_ids` design constraint remains the blocker recorded by this revision.

Carried-forward authorization evidence:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - authorizes autonomous bridge flow for the project batch but does not create or approve the missing DCL.
- `DELIB-20265457` - authorizes filing proposals for the reliability batch.
- `DELIB-2547` - supplies the policy direction, but the NO-GO findings correctly require a durable owner-approved design constraint before source/test implementation.

## Findings Addressed

### Finding P1-001 - Required Design Constraint Still Missing

Accepted. Prime Builder will not implement the source/test reconciliation from this thread until the missing formal design constraint exists and is cited as the governing requirement, or until an existing owner-approved requirement is identified and cited.

Required next action outside this auto-dispatch: an interactive Prime Builder session must create and obtain owner approval for the additive PAUTH `included_work_item_ids` design constraint through the governed formal-artifact path, or identify an existing owner-approved requirement that already states the same semantics. After that, Prime Builder can file a substantive `REVISED` implementation proposal that cites the live requirement and restores the source/test verification mapping.

## Scope Changes

This revision preserves the same target paths and work-item linkage only as the blocked future implementation envelope. It does not request `GO`, does not add target paths, and does not authorize implementation.

## Pre-Filing Preflight Subsection

Candidate preflight commands run before live filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-006.md --json
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-006.md
```

Observed applicability result on the completed draft: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; packet hash `sha256:3047e13d2658b35d83bc45d4c9f4d7b97f421809a5b6ef052a19e1e645c5ab2c`.

Observed clause result on the completed draft: exit 0; clauses evaluated: 5; must_apply: 4; evidence gaps in must-apply clauses: 0; blocking gaps: 0.

The revision helper must rerun both candidate preflights before writing the live bridge file.

## Verification Plan

No implementation verification is requested by this blocker record. The only verification for this revision is bridge-state readback:

- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` should show latest status `REVISED` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-006.md` after filing.
- `groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-reconcile-included-work-item-ids-semantics --format json` should show version chain including `006 REVISED`.

## Risk And Rollback

- Risk: latest `REVISED` may route back to Loyal Opposition even though this artifact records a blocker rather than a new implementation-ready proposal. Mitigation: the file states that no `GO` is requested and identifies the exact owner-approved DCL prerequisite.
- Risk: the implementation remains open while source behavior is unreconciled. Mitigation: this preserves the bridge audit trail and prevents unauthorized source/test mutation from a non-interactive worker.
- Rollback: append another bridge entry; do not edit or delete this one. The eventual substantive revision should supersede this blocker after the required DCL exists.

## Recommended Commit Type

`bridge:` - append-only blocker revision; no source/test/config/KB mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
