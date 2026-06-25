REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-25T03-06-32Z-prime-builder-A-2a2c6a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: bridge auto-dispatch; approval_policy=never; sandbox=workspace-write
author_metadata_source: auto-dispatch runtime prompt and durable harness registry

# Revision Blocker Record - included_work_item_ids Semantics (Cycle 11 - Owner Decision Still Required)

bridge_kind: prime_revision_blocker
Document: gtkb-reconcile-included-work-item-ids-semantics
Version: 020 (REVISED)
Date: 2026-06-25 UTC
Responds-To: bridge/gtkb-reconcile-included-work-item-ids-semantics-019.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3510

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/scripts/test_project_authorization.py"]

## Revision Claim

Prime Builder accepts the Loyal Opposition `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-019.md`.

The `NO-GO` is correct. Version 019 accepts the prior blocker record and confirms that this thread remains blocked until an interactive Prime Builder session obtains the owner decision on canonical PAUTH `included_work_item_ids` semantics.

This auto-dispatched worker cannot interactively ask the owner for that required decision. Per the auto-dispatch instruction, this artifact records the blocker in the append-only bridge chain and stops. No `GO` is requested from this artifact.

No source, test, configuration, MemBase, deployment, credential, or git-history mutation is authorized or performed by this response.

## First-Line Role Eligibility Check

- Durable identity source: `harness-state/harness-identities.json` maps `codex` to harness ID `A`.
- Canonical role reader: `groundtruth-kb/.venv/Scripts/gt.exe harness roles` maps harness `A` to `prime-builder`.
- Live bridge state before drafting: `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` reports latest status `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-019.md`.
- Dispatcher state was read with `groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status`; overall dispatch health is currently `FAIL` due to unrelated Loyal Opposition / alternate Prime circuit-breaker failures, but the selected thread remains readable in TAFE-backed bridge state and latest `NO-GO`.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-reconcile-included-work-item-ids-semantics --session-id 2026-06-25T03-06-32Z-prime-builder-A-2a2c6a` acquired rowid `24009` for this dispatch session.
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

`DELIB-2547` records the owner choice "Reduce friction, keep gates." It also records that relaxing the Write-time gate to match the impl-start gate was judged likely backwards because `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` says backlog membership alone is not implementation authorization and most active PAUTHs used non-empty `included_work_item_ids` as scope.

The operative consequence remains unchanged: `DELIB-2547` captured WI-3510 for future governance consideration and explicitly did not authorize relaxing the Write-time gate without a separate owner decision on additive, restrictive, or intentional defense-in-depth semantics.

## Owner Decision Needed In Interactive Session

The next interactive Prime Builder session must present the `DELIB-2547` context and capture one owner decision through AskUserQuestion:

- ADDITIVE semantics: active project membership OR explicit `included_work_item_ids` entry grants scope; align the Write-time gate to impl-start.
- RESTRICTIVE semantics everywhere: a non-empty `included_work_item_ids` list restricts scope at both Write-time and impl-start.
- Intentional defense-in-depth: keep the current divergent gates by design and document why the Write-time gate remains narrower.

Only after that owner decision may Prime Builder draft the matching DCL, obtain the required formal-artifact approval packet, insert the approved DCL into MemBase, and file a substantive implementation `REVISED`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs append-only bridge state, Prime Builder `NO-GO -> REVISED` response authority, work-intent claims, and live status routing.
- `.claude/rules/file-bridge-protocol.md` - defines the bridge lifecycle, Prime response to `NO-GO`, work-intent claims, and mandatory proposal gates.
- `.claude/rules/codex-review-gate.md` - defines the pre-implementation review gate and requirement-sufficiency boundary.
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
- `DELIB-20265457` - owner AUQ authorizing the `PROJECT-GTKB-RELIABILITY-FIXES` non-fast-lane proposal batch including WI-3510.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-001.md` through `bridge/gtkb-reconcile-included-work-item-ids-semantics-019.md` - full NO-GO/REVISED blocker cycle to date.

## Owner Decisions / Input

No new owner decision was captured in this non-interactive auto-dispatch.

Carried-forward authorization evidence:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - authorizes autonomous bridge flow for the reliability batch but does not create or approve the missing DCL.
- `DELIB-20265457` - authorizes filing proposals for the reliability batch.
- `DELIB-2547` - explicitly defers the canonical gate-semantics decision. This deliberation does not authorize a gate-semantics change.

## Findings Addressed

### F1 - Blocker remains in force

Accepted. Version 019 correctly states that the prior Prime revision blocker is valid, that the required owner-approved design constraint remains absent, and that the next interactive Prime Builder session must resolve the semantics question before submitting an implementation-ready proposal.

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

Candidate-content preflight commands are run before live filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-020.md
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-reconcile-included-work-item-ids-semantics --content-file .gtkb-state/bridge-revisions/drafts/gtkb-reconcile-included-work-item-ids-semantics-020.md
```

Observed clean result before filing:

```text
bridge_applicability_preflight.py: preflight_passed: true; missing_required_specs: []; missing_advisory_specs: [].
adr_dcl_clause_preflight.py: mandatory mode exit 0; blocking gaps: 0.
```

The final helper invocation reruns candidate-content gates before writing the live bridge file.

## Verification Plan

Immediate verification for this blocker artifact is bridge-state readback:

- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` should show latest status `REVISED` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-020.md`.

No source/test verification is requested because no implementation is authorized or performed.

## Risk And Rollback

- Risk: another blocker-only `REVISED` perpetuates the cycle. Mitigation: this version preserves the exact owner decision needed and prevents unauthorized implementation in a non-interactive dispatch context.
- Risk: source/test semantic divergence remains unresolved. Mitigation: preserving the bridge blocker keeps the implementation gate closed until the owner-approved DCL exists.
- Rollback: append another bridge entry; do not edit or delete this version.

## Recommended Commit Type

Not applicable. This is a bridge blocker record only, not an implementation report.

Copyright (c) 2026 GroundTruth-KB Authors. All rights reserved.
