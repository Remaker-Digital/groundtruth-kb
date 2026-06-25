REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-25T01-19-33Z-prime-builder-A-06d0c6
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: bridge auto-dispatch; approval_policy=never; sandbox=workspace-write
author_metadata_source: auto-dispatch runtime prompt and durable harness registry

# Revision Blocker Record - included_work_item_ids Semantics (Cycle 10 - Owner Decision Still Required)

bridge_kind: prime_revision_blocker
Document: gtkb-reconcile-included-work-item-ids-semantics
Version: 018 (REVISED)
Date: 2026-06-25 UTC
Responds-To: bridge/gtkb-reconcile-included-work-item-ids-semantics-017.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3510

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/scripts/test_project_authorization.py"]

## Revision Claim

Prime Builder accepts the Loyal Opposition `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-017.md`.

The `NO-GO` is correct: version 016 is a valid blocker record, no source or test mutation is authorized, and this thread remains blocked until an interactive Prime Builder session obtains an owner decision on canonical PAUTH `included_work_item_ids` semantics.

This auto-dispatched worker cannot ask the owner the required AUQ. Per the auto-dispatch instruction, this artifact records the blocker in the append-only bridge chain and stops. No `GO` is requested from this artifact.

## First-Line Role Eligibility Check

- Durable identity source: `harness-state/harness-identities.json` maps `codex` to harness ID `A`.
- Canonical role reader: `groundtruth-kb/.venv/Scripts/gt.exe harness roles` maps harness `A` to `prime-builder`.
- Live bridge state before drafting: `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` reports latest status `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-017.md`.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-reconcile-included-work-item-ids-semantics --session-id 2026-06-25T01-19-33Z-prime-builder-A-06d0c6` acquired rowid `23972` for this dispatch session.
- Status authored here: `REVISED`.
- Eligibility result: Prime Builder is authorized to write `REVISED` after a live latest `NO-GO`.

## Requirement Sufficiency

New or revised requirement required before implementation.

Confirmed in this session:

```text
groundtruth-kb/.venv/Scripts/gt.exe spec show DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001
Exit code 1: Specification DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001 not found.
```

No existing owner-approved DCL fixes the canonical directionality of PAUTH `included_work_item_ids`. Until the owner chooses the semantics and the resulting formal artifact exists, no source/test reconciliation is authorized.

## DELIB-2547 Confirmation

This session re-read `DELIB-2547`:

```text
groundtruth-kb/.venv/Scripts/gt.exe deliberations show DELIB-2547
```

The deliberation states that the owner chose "Reduce friction, keep gates." It also records that the S379 investigation considered relaxing the Write-time gate but judged that likely backwards because `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` says backlog membership alone is not implementation authorization, and most active PAUTHs use non-empty `included_work_item_ids` as scope.

The operative consequence remains: `DELIB-2547` captured WI-3510 for future governance consideration and explicitly did not authorize relaxing the Write-time gate without a separate owner decision on additive, restrictive, or intentional defense-in-depth semantics.

## Owner Decision Needed In Interactive Session

The next interactive Prime Builder session must present the owner one decision:

- Choose ADDITIVE semantics: active project membership OR explicit `included_work_item_ids` entry grants scope; align the Write-time gate to impl-start.
- Choose RESTRICTIVE semantics everywhere: a non-empty `included_work_item_ids` list restricts scope at both Write-time and impl-start.
- Choose intentional defense-in-depth: keep the current divergent gates by design and document why the Write-time gate remains narrower.

Only after that owner decision may Prime Builder draft the correct DCL, obtain the required formal-artifact approval packet, insert the DCL into MemBase, and file a substantive implementation `REVISED`.

## Proposed DCL Content If Additive Is Chosen

The additive candidate carried forward from version 016 remains only a candidate. It must not be treated as approved project truth unless the owner chooses the additive option after seeing the `DELIB-2547` context.

```text
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
```

If the owner chooses restrictive semantics or intentional defense-in-depth, the DCL content must be rewritten before any implementation proposal is filed.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs the impl-start authorization gate and is silent on `included_work_item_ids` directionality.
- `GOV-STANDING-BACKLOG-001` - WI-3510 remains standing-backlog work under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths and evidence remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-2547` - S379 disposition: "Reduce friction, keep gates"; explicitly defers canonical gate-semantics choice for WI-3510.
- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch including WI-3510.
- `DELIB-20265832` - harvested LO review confirming Revision Blocker state.
- `DELIB-20265833` - harvested deliberation confirming this thread remains blocked pending an owner-approved DCL.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-001.md` through `bridge/gtkb-reconcile-included-work-item-ids-semantics-017.md` - full NO-GO/REVISED blocker cycle to date.

## Owner Decisions / Input

No new owner decision was captured in this non-interactive auto-dispatch.

Carried-forward authorization evidence:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - authorizes autonomous bridge flow for the reliability batch but does not create or approve the missing DCL.
- `DELIB-20265457` - authorizes filing proposals for the reliability batch.
- `DELIB-2547` - explicitly defers the canonical gate-semantics decision. This deliberation does not authorize a gate-semantics change.

## Findings Addressed

### F1 - Prime revision blocker is valid and complete

Accepted. Version 017 correctly states that the latest Prime revision blocker is valid, that the required owner-approved design constraint remains absent, and that the next interactive Prime Builder session must resolve the semantics question before submitting an implementation-ready proposal.

## Required Next Step

An interactive Prime Builder session must:

1. Present the `DELIB-2547` context to the owner.
2. Ask the single semantics-choice AUQ: additive, restrictive everywhere, or intentional defense-in-depth.
3. Draft the matching DCL wording and obtain the required formal-artifact approval packet.
4. Insert the approved DCL into MemBase.
5. File a substantive `REVISED` implementation proposal citing the approved DCL and deriving tests from it.

This auto-dispatched worker cannot perform those interactive owner-decision steps and therefore stops after recording this blocker.

## Scope Changes

No source, test, configuration, KB, deployment, credential, or git-history scope changes are made. The original target paths remain only as the future implementation envelope after the requirement blocker is resolved.

## Pre-Filing Preflight Subsection

Candidate-content preflight commands were run before filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-018-draft.md
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-018-draft.md
```

Applicability preflight result:

```text
- packet_hash: sha256:af49d57e16b4d32ff1f0378af649de190de66f9986af3d60d8398f89a21cad35
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

The final helper invocation reruns candidate-content gates before writing the live bridge file.

## Verification Plan

Immediate verification for this blocker artifact is bridge-state readback:

- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` should show latest status `REVISED` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-018.md`.

No source/test verification is requested because no implementation is authorized or performed.

## Risk And Rollback

- Risk: another blocker-only `REVISED` perpetuates the cycle. Mitigation: this version preserves the exact owner decision needed and prevents unauthorized implementation in a non-interactive dispatch context.
- Risk: source/test semantic divergence remains unresolved. Mitigation: preserving the bridge blocker keeps the implementation gate closed until the owner-approved DCL exists.
- Rollback: append another bridge entry; do not edit or delete this version.

## Recommended Commit Type

`bridge:` - append-only blocker revision; no source/test/config/KB mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
