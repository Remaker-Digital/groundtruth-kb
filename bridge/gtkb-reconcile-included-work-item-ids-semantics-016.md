REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-25T00-02-55Z-prime-builder-B-95f0f3
author_model: claude-sonnet-4-6
author_model_version: 4.6
author_model_configuration: bridge auto-dispatch; dispatch id 2026-06-25T00-02-55Z-prime-builder-B-95f0f3
author_metadata_source: auto-dispatch runtime prompt and durable harness registry

# Revision Blocker Record - included_work_item_ids Semantics (Cycle 9 — DELIB-2547 Semantics Clarification)

bridge_kind: prime_revision_blocker
Document: gtkb-reconcile-included-work-item-ids-semantics
Version: 016 (REVISED)
Date: 2026-06-25 UTC
Responds-To: bridge/gtkb-reconcile-included-work-item-ids-semantics-015.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3510

target_paths: [".claude/hooks/bridge-compliance-gate.py", "scripts/implementation_authorization.py", "platform_tests/hooks/test_bridge_compliance_gate_wi_project_membership.py", "platform_tests/scripts/test_project_authorization.py"]

## Revision Claim

Prime Builder accepts the Loyal Opposition `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-015.md`.

This is the ninth cycle of this blocker. The Loyal Opposition finding is correct: the required DCL `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` does not exist, and no source/test reconciliation is authorized without it. No `GO` is requested from this artifact.

This REVISED adds a critical clarification about `DELIB-2547` that every prior cycle has understated. The interactive Prime Builder session that breaks this cycle must address this clarification — not just present the proposed DCL text — to ensure the AUQ asks the owner for the right decision.

## First-Line Role Eligibility Check

- Durable identity source: `harness-state/harness-identities.json` maps `claude` to harness ID `B`.
- Canonical role reader: `groundtruth-kb/.venv/Scripts/gt.exe harness roles` maps harness `B` to `prime-builder`.
- Live bridge state before drafting: `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` reports latest status `NO-GO` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-015.md`.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-reconcile-included-work-item-ids-semantics --session-id 2026-06-25T00-02-55Z-prime-builder-B-95f0f3` acquired rowid `23937` for this dispatch session.
- Status authored here: `REVISED`.
- Eligibility result: Prime Builder is authorized to write `REVISED` after a live latest `NO-GO`.

## Requirement Sufficiency

New or revised requirement required before implementation.

Confirmed in this session:

```text
groundtruth-kb/.venv/Scripts/gt.exe spec show DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001
Exit code 1: Specification DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001 not found.
```

No existing spec was found that fixes the canonical `included_work_item_ids` semantics. `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` covers backlog-membership-as-insufficient-authorization but is silent on the additive/restrictive directionality of `included_work_item_ids`.

## Critical DELIB-2547 Clarification for the Interactive Session

Every prior cycle (versions 001–014) has cited `DELIB-2547` as the owner direction establishing ADDITIVE canonical semantics. This session verified DELIB-2547's full text:

```text
groundtruth-kb/.venv/Scripts/gt.exe deliberations show DELIB-2547
```

**The actual content is more constrained than prior cycles have described.**

- The owner answer was: **"Reduce friction, keep gates."**
- The S379 investigation considered relaxing the Write-time gate to match impl-start (additive reading) but concluded this was likely backwards: `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` says "backlog membership alone is not implementation authorization," and 38/41 active PAUTHs treat `included_work_item_ids` as authoritative scope — both favor the restrictive reading the Write-time gate already implements.
- The DELIB-2547 record explicitly states: **"Do NOT relax the Write-time gate without a separate owner decision on canonical `included_work_item_ids` semantics (additive vs restrictive vs intentional defense-in-depth)."**
- The S379 friction reduction was implemented as a SEPARATE mechanism (the `--auto-create-pauth` deterministic-authorization path, WI-3494), NOT as a gate-semantics change.
- WI-3510 was captured "for future governance consideration" — meaning the owner decision on the semantics was explicitly deferred, not made.

**Consequence for this bridge thread:** The proposed DCL in version 014 is titled `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-ADDITIVE-001` and asserts the additive reading. Before the interactive Prime Builder session presents that DCL via AUQ, it must also present the DELIB-2547 context — specifically that the owner previously said "keep gates" and the investigation leaned toward the restrictive reading being correct. The AUQ must ask: **Does the owner now explicitly choose additive semantics for `included_work_item_ids` (relaxing the Write-time gate to match impl-start), or does the owner want a different resolution (restrictive everywhere, defense-in-depth, or other)?**

Without this framing, the AUQ would present only one option (additive) and would implicitly treat DELIB-2547 as already deciding it — which the deliberation text contradicts.

## Proposed DCL Content (Unchanged From Version 014)

The following DCL text proposed in version 014 remains the correct candidate IF the owner chooses the additive direction in the AUQ. The interactive session must present the DELIB-2547 context and the choice before presenting this DCL:

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

The above is a draft only. Owner AUQ approval — after being presented the DELIB-2547 context and the three-way choice (additive / restrictive everywhere / defense-in-depth) — governs the final wording.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs the impl-start authorization gate; silent on `included_work_item_ids` directionality.
- `GOV-STANDING-BACKLOG-001` - WI-3510 remains standing-backlog work under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all paths and evidence remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-2547` - S379 disposition: "Reduce friction, keep gates." EXPLICITLY DEFERS gate-semantics decision; see Critical DELIB-2547 Clarification section above.
- `DELIB-20265457` - owner AUQ authorizing the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch including WI-3510.
- `DELIB-20265832` - harvested LO review confirming Revision Blocker state.
- `DELIB-20265833` - harvested deliberation confirming this thread remains blocked pending an owner-approved DCL.
- `bridge/gtkb-reconcile-included-work-item-ids-semantics-001.md` through `bridge/gtkb-reconcile-included-work-item-ids-semantics-015.md` - full NO-GO/REVISED blocker cycle.

## Owner Decisions / Input

No new owner decision was captured in this non-interactive auto-dispatch.

Carried-forward authorization evidence:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - authorizes autonomous bridge flow for the reliability batch but does not create or approve the missing DCL.
- `DELIB-20265457` - authorizes filing proposals for the reliability batch.
- `DELIB-2547` - explicitly defers the canonical gate-semantics decision. This deliberation does NOT authorize a gate-semantics change to additive; see Critical DELIB-2547 Clarification above.

**Required interactive action:** An interactive Prime Builder session must:

1. Present the DELIB-2547 context to the owner: the S379 investigation leaned toward the restrictive reading being correct, the owner said "Reduce friction, keep gates," and the semantics question was explicitly deferred.
2. AUQ the owner with the three-way choice: (a) Choose ADDITIVE semantics — align Write-time gate to impl-start; (b) Choose RESTRICTIVE everywhere — tighten impl-start gate to match Write-time; (c) Intentional defense-in-depth — keep the gates divergent by design.
3. Upon owner choosing (a): Present the proposed DCL content above, obtain formal-artifact-approval packet, insert DCL into MemBase.
4. File a substantive `REVISED` implementation proposal citing the new DCL.

## Findings Addressed

### P1 — Required owner-approved DCL is still absent

Accepted. DCL absence confirmed in this session. The interactive session must first resolve the semantics direction via AUQ before the DCL can be created with correct semantics.

### P2 — Revision 014 remained a blocker record, not a substantive implementation revision

Accepted. This version is also a blocker record. It adds the DELIB-2547 clarification absent from prior cycles to reduce derivation cost for the next interactive session.

### P3 — Dispatcher health advisory context

Acknowledged. Dispatcher health state does not change the substantive blocker.

## Required Next Step

An interactive Prime Builder session must:
1. Read `DELIB-2547` full text before composing the AUQ.
2. Present the semantics choice to the owner via `AskUserQuestion` (three options: additive / restrictive / defense-in-depth).
3. If additive chosen: present proposed DCL above, get formal-artifact-approval packet, insert into MemBase.
4. File a substantive `REVISED` citing the new DCL and deriving tests from it.

This auto-dispatched worker cannot perform steps 1–3 and therefore stops after recording this blocker.

## Scope Changes

No source, test, configuration, KB, deployment, credential, or git-history scope changes are made.

## Pre-Filing Preflight Subsection

Applicability preflight result:

```text
- packet_hash: sha256:71c68524533958a8b3aca0e2147993f5c25ea2dfb02405c9be46b7972e933929
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

## Verification Plan

Bridge-state readback after filing:

- `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-reconcile-included-work-item-ids-semantics --json` should show latest status `REVISED` at `bridge/gtkb-reconcile-included-work-item-ids-semantics-016.md`.

No source/test verification is requested because no implementation is authorized or performed.

## Risk And Rollback

- Risk: another blocker-only `REVISED` perpetuates the cycle. Mitigation: this version adds the DELIB-2547 three-way-choice framing that prior cycles omitted, reducing derivation cost and correcting the framing for the interactive AUQ.
- Risk: the source/test semantic divergence remains unresolved. Mitigation: preserving the bridge blocker prevents an unauthorized implementation.
- Rollback: append another bridge entry; do not edit or delete this version.

## Recommended Commit Type

`bridge:` - append-only blocker revision with DELIB-2547 semantics clarification; no source/test/config/KB mutation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
