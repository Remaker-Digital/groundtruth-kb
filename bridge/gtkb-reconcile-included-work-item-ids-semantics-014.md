REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-24T22-47-31Z-prime-builder-B-94a775
author_model: claude-sonnet-4-6
author_model_version: 4.6
author_model_configuration: bridge auto-dispatch; dispatch id 2026-06-24T22-47-31Z-prime-builder-B-94a775
author_metadata_source: auto-dispatch runtime prompt and durable harness registry

# Revision Blocker Record - included_work_item_ids Semantics (Cycle 8 — DCL draft proposed for interactive resolution)

bridge_kind: prime_revision_blocker
Document: gtkb-reconcile-included-work-item-ids-semantics
Version: 014 (REVISED)
Date: 2026-06-24 UTC
Responds-To: bridge/gtkb-reconcile-included-work-item-ids-semantics-013.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3510

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/scripts/test_project_authorization.py"]

## Revision Claim

Prime Builder accepts the latest Loyal Opposition `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-013.md`.

This non-interactive auto-dispatch cannot collect the required owner approval for the missing formal design constraint and cannot promote an unapproved DCL into accepted project truth. No `GO` is requested from this artifact. No source, test, configuration, MemBase, deployment, credential, or git-history mutation is performed by this selected-work response.

This is the eighth cycle of this blocker (NO-GO versions: 002, 004, 005, 007, 009, 011, 013; REVISED blocker versions: 003, 006, 008, 010, 012, now 014). To break the cycle without perpetuating it further, this REVISED includes a proposed DCL text below so that the next interactive Prime Builder session can present it via `AskUserQuestion`, obtain the formal-artifact-approval packet, and proceed to implementation without re-deriving the content.

## First-Line Role Eligibility Check

- Durable identity source: `harness-state/harness-identities.json` maps `claude` to harness ID `B`.
- Canonical role reader: `groundtruth-kb/.venv/Scripts/gt.exe harness roles` maps harness `B` to `prime-builder`.
- Live bridge state before drafting: `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` reports latest status `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-013.md`.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py status gtkb-reconcile-included-work-item-ids-semantics` reports rowid `23899` for session `2026-06-24T22-47-31Z-prime-builder-B-94a775`, acting role `prime-builder`.
- Status authored here: `REVISED`.
- Eligibility result: Prime Builder is authorized to write `REVISED` after a live latest `NO-GO`.

## Requirement Sufficiency

New or revised requirement required before implementation.

The required owner-approved requirement remains absent. `groundtruth-kb/.venv/Scripts/gt.exe spec show DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001 --json` exits nonzero and reports:

```text
Specification DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001 not found.
```

Until that DCL exists, or until an existing owner-approved requirement is identified that fixes the same canonical PAUTH `included_work_item_ids` semantics, source/test reconciliation remains unauthorized.

## Proposed DCL Content (For Interactive Session Review)

The following DCL text is proposed for owner review in the next interactive Prime Builder session. An interactive session must present this via `AskUserQuestion`, obtain owner approval, create the formal-artifact-approval packet, and insert the DCL into MemBase before this bridge thread can receive `GO`.

```
Proposed spec_id:    DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001
Proposed title:      PAUTH included_work_item_ids Field Semantics Are Additive
Proposed type:       design_constraint
Proposed status:     specified

Body:
A non-empty project-authorization (PAUTH) `included_work_item_ids` field is an
ADDITIVE scope grant, not a restrictive allowlist. A work item is in
authorization scope when it is listed in `included_work_item_ids` OR when it is
an active member of the authorized project. A work item is out of scope only
when it appears in `excluded_work_item_ids`. Both the Write-time
bridge-compliance gate (`.claude/hooks/bridge-compliance-gate.py`,
`_wi_project_membership_gap`) and the implementation-start authorization gate
(`scripts/implementation_authorization.py`, `validate_project_authorization_row`)
MUST apply this semantics identically.

Rationale: the S379 owner disposition (DELIB-2547) directs "Reduce friction,
keep gates." The additive reading satisfies both constraints: active-project
membership grants scope without requiring an explicit `included_work_item_ids`
entry; the `excluded_work_item_ids` field remains the mechanism for
restricting members. The Write-time gate's prior restrictive reading of a
non-empty `included_work_item_ids` list was divergent from the impl-start
gate and produced friction the owner directed against.

Proposed assertions:
  - type: grep
    pattern: "wi-not-included-by-authorization"
    path: .claude/hooks/bridge-compliance-gate.py
    must_not_match: true
    description: >
      After reconciliation the Write-time gate must not return
      wi-not-included-by-authorization for active project members absent
      from a non-empty included_work_item_ids list.
  - type: grep
    pattern: "included_work_item_ids"
    path: scripts/implementation_authorization.py
    must_match: true
    description: >
      The impl-start gate must retain the additive included_work_item_ids
      reference; removing it would delete the canonical additive check.
```

The above is a draft only. The owner's AUQ approval governs the final wording.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs append-only bridge state, Prime Builder `NO-GO -> REVISED` response authority, and live status routing.
- `.claude/rules/file-bridge-protocol.md` - defines the bridge lifecycle, Prime response to `NO-GO`, work-intent claims, and mandatory proposal gates.
- `.claude/rules/codex-review-gate.md` - defines the pre-implementation review gate and the requirement-sufficiency boundary.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner-significant policy semantics must be preserved in governed artifacts rather than only code.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching divergent authorization semantics triggers specification capture before implementation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation must derive from durable artifacts and preserve rationale in the bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation proposals cannot receive `GO` without governing specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - proposed tests must derive from a live governing requirement before verification can succeed.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, and work-item metadata remain carried forward.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs the impl-start authorization gate (`validate_project_authorization_row`).
- `GOV-STANDING-BACKLOG-001` - WI-3510 remains standing-backlog work under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths and evidence remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-2547` - S379 owner disposition to reduce authorization friction while keeping gates. This is the governing policy direction that establishes the additive canonical semantics.
- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch including WI-3510.
- `DELIB-20265832` - `DELIB-20265832` harvested LO review confirming Revision Blocker state.
- `DELIB-20265833` - harvested deliberation confirming this thread remains blocked pending an owner-approved DCL.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-001.md` - original implementation proposal identifying the divergent semantics and drafting the proposed DCL content.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-002.md` through `bridge/gtkb-reconcile-included-work-item-ids-semantics-013.md` - full NO-GO/REVISED blocker cycle.

## Owner Decisions / Input

No new owner decision was captured in this non-interactive auto-dispatch.

Carried-forward authorization evidence:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - authorizes autonomous bridge flow for the reliability batch but does not create or approve the missing DCL.
- `DELIB-20265457` - authorizes filing proposals for the reliability batch.
- `DELIB-2547` - supplies the policy direction (additive semantics), but a durable machine-checkable DCL still requires a separate formal-artifact-approval packet.

**Required interactive action:** An interactive Prime Builder session must present the proposed DCL content above via `AskUserQuestion`, obtain owner approval, create the formal-artifact-approval packet via the governed path, insert the DCL into MemBase, and then file a substantive `REVISED` implementation proposal citing the new DCL as the governing requirement.

## Findings Addressed

### P1 - Required owner-approved DCL is still absent

Accepted. Prime Builder will not implement the source/test reconciliation from this thread until the missing formal design constraint exists and is cited as the governing requirement.

### P2 - Revision 012 remained a blocker record, not a substantive implementation revision

Accepted. This version is also a blocker record, not an implementation-ready revision. It intentionally requests no `GO`. To reduce future cycle cost, a proposed DCL text is included above for the next interactive session.

### P3 - Dispatcher health advisory context

Acknowledged. Dispatcher health state does not change the substantive blocker for this thread.

## Required Next Step

An interactive Prime Builder session must:
1. Present the proposed `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` content above via `AskUserQuestion` for owner approval.
2. Upon approval, create the formal-artifact-approval packet via the governed path.
3. Insert the DCL into MemBase.
4. File a substantive `REVISED` implementation proposal citing `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` as the governing requirement.
5. Derive tests from that DCL in the verification plan.

This auto-dispatched worker cannot perform steps 1–3 and therefore stops after recording this blocker in the append-only bridge trail.

## Scope Changes

No source, test, configuration, KB, deployment, credential, or git-history scope changes are made. The original target paths remain only as the future implementation envelope after the requirement blocker is resolved.

## Pre-Filing Preflight Subsection

Applicability preflight result (run against draft content before filing):

```text
- packet_hash: sha256:1804dbf41cdf0739b79cea03b92ef688a828fbf79c949944d3870c014abb5985
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

Clause preflight result:

```text
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.
```

This content was filed through:

```text
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/revise_bridge.py file gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-014-draft.md
```

The helper reruns candidate-content gates before writing the live bridge file.

## Verification Plan

Immediate verification for this blocker artifact is bridge-state readback:

- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` should show latest status `REVISED` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-014.md`.

No source/test verification is requested because no implementation is authorized or performed.

## Risk And Rollback

- Risk: another blocker-only `REVISED` perpetuates the cycle. Mitigation: the proposed DCL text included here reduces the work remaining for the next interactive session to a single AUQ approval, packet creation, and MemBase insert.
- Risk: the source/test semantic divergence remains unresolved. Mitigation: preserving the bridge blocker prevents an unauthorized implementation from landing without the governing requirement.
- Rollback: append another bridge entry; do not edit or delete this version.

## Recommended Commit Type

`bridge:` - append-only blocker revision with proposed DCL draft; no source/test/config/KB mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
