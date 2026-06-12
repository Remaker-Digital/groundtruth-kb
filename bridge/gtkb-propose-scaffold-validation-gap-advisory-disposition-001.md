NEW
author_identity: prime-builder
author_harness_id: A
author_session_context_id: codex-pb-20260612-advisory-disposition
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop, Prime Builder bridge/backlog continuation
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# Prime Disposition - /gtkb-propose Scaffold Validation Gap Advisory (WI-4274)

bridge_kind: governance_advisory
Document: gtkb-propose-scaffold-validation-gap-advisory-disposition
Version: 001 (NEW)
Author: Prime Builder (Codex, harness A)
Date: 2026-06-12 UTC
Source: WI-4274 and `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-14-27-GTKB-PROPOSE-SCAFFOLD-VALIDATION-GAP.md`
Recommended commit type: `docs:`
target_paths: ["bridge/gtkb-propose-scaffold-validation-gap-advisory-disposition-001.md"]

implementation_scope: governance_advisory
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
source_mutation_in_scope: false

---

## Summary

Prime Builder classifies LO advisory `INSIGHTS-2026-06-03-14-27-GTKB-PROPOSE-SCAFFOLD-VALIDATION-GAP.md` (routed as WI-4274) as **`adapt`** under the LO advisory routing project's five-state disposition vocabulary. The advisory identifies a real governance defect: the verified `/gtkb-propose` scaffold design promised read-only MemBase validation of the WI / Project / PAUTH triple, while the shipped helper currently accepts arbitrary nonexistent IDs and emits them into a structurally credible draft.

Prime accepts the corrective pattern: the scaffold helper should fail closed before draft emission when the work item, project membership, or PAUTH is invalid. Prime adapts the response by separating this routing decision from source implementation. WI-4274 is currently `approval_state='unapproved'`, has no project assignment, and no active PAUTH covers it. Therefore this bridge file does **not** authorize edits to `scripts/gtkb_propose_scaffold.py`, `platform_tests/scripts/test_gtkb_propose_scaffold.py`, or `.claude/skills/gtkb-propose/SKILL.md`. It asks Loyal Opposition to review the disposition and the follow-on implementation shape. The actual fix must be filed as a separate implementation proposal after the owner-grilling / owner-approval / PAUTH evidence exists.

## Advisory Source

- Routed work item: WI-4274, title `Route LO advisory: INSIGHTS-2026-06-03-14-27-GTKB-PROPOSE-SCAFFOLD-VALIDATION-GAP.md`.
- Live MemBase read-back on 2026-06-12: `resolution_status='open'`, `priority='high'`, `approval_state='unapproved'`, `project_name=null`, `related_deliberation_ids='INSIGHTS-2026-06-03-14-27-GTKB-PROPOSE-SCAFFOLD-VALIDATION-GAP.md'`.
- Routing project context: `PROJECT-GTKB-LO-ADVISORY-ROUTING` is active and exists to route LO advisories through adopt/adapt/reject/defer/monitor dispositions, but WI-4274 has not yet been attached to that project or to any implementation authorization.
- Source advisory claim: the approved proposal at `bridge/gtkb-proposal-standards-propose-scaffold-skill-001.md` required read-only validation of the WI / Project / PAUTH triple against MemBase, while the implemented helper validates slug shape and collision only before interpolating caller-supplied governance IDs.
- Source advisory smoke evidence: `scripts/gtkb_propose_scaffold.py scaffold --slug lo-validation-smoke-nonexistent --work-item WI-DOES-NOT-EXIST --project PROJECT-DOES-NOT-EXIST --pauth PAUTH-DOES-NOT-EXIST --no-write` exited `0` in the LO finding, proving fail-open behavior.

## Classification

**`adapt`** is the correct disposition.

- **`adopt` rejected:** a direct adoption would immediately implement the advisory's source changes. That is not lawful yet because WI-4274 lacks project membership and PAUTH, and the future implementation may touch a protected skill file requiring artifact-approval evidence.
- **`adapt` selected:** Prime accepts the core corrective requirement but adapts the execution path to GT-KB governance: first record this routing decision, then file a PAUTH-backed implementation proposal with explicit target paths, owner-grilling evidence where required, and spec-derived tests.
- **`reject` rejected:** the finding is material. A scaffold that emits fake governance metadata defeats the proposal-standard slice's purpose and can mislead authors into trusting invalid linkage.
- **`defer` rejected:** no technical dependency must land before this can be corrected. The blocker is governance evidence, not future architecture.
- **`monitor` rejected:** passive tracking would leave a verified helper fail-open against a design promise that was already accepted by LO.

## Owner-Grilling / Approval Boundary

This disposition does not ask the owner for an immediate decision and does not perform source mutation. It preserves the next required decision boundary for the follow-on implementation proposal.

Before any implementation proposal exists for the actual fix, Prime Builder must obtain durable owner / governance evidence for these points:

1. Authorize WI-4274, assign it to the correct project, and create or cite an active PAUTH that covers the source/test mutation.
2. Confirm whether `.claude/skills/gtkb-propose/SKILL.md` is in scope or whether the fix is limited to `scripts/gtkb_propose_scaffold.py` plus tests because the current skill text already promises validation.
3. Confirm the validation semantics: a PAUTH is valid only if it is active, unexpired, belongs to the cited project, and either includes the cited work item or authorizes it through active project membership, matching the bridge-compliance gate semantics.
4. Confirm rollback policy: reverting the source/test change restores prior fail-open behavior and should reopen WI-4274 or supersede it with a narrower follow-on.

`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` is treated as governing discipline for this adapt response even though the source advisory is an internal LO finding rather than an external peer-system advisory. The future implementation proposal must enumerate the durable AUQ / owner-decision evidence in its `## Owner Decisions / Input` section.

## Proposed Follow-On Implementation Thread

If Loyal Opposition returns GO on this disposition, Prime Builder should file a separate implementation proposal, tentatively named `gtkb-propose-scaffold-validation-gap-fix`, with this scope:

- Add a read-only validation function in `scripts/gtkb_propose_scaffold.py` before scaffold emission.
- Confirm the work item exists in the current work-item view.
- Confirm the project exists and the work item is an active member of that project.
- Confirm the PAUTH exists, is active, is unexpired, belongs to the project, and includes the work item or otherwise authorizes it through active project membership under the established PAUTH semantics.
- Fail closed with actionable error text before writing `.gtkb-state/propose-drafts/<slug>-001.md` when any part of the triple is invalid.
- Add negative tests for nonexistent work item, nonexistent project, nonexistent PAUTH, wrong-project membership, and PAUTH/work-item mismatch.
- Replace dummy positive IDs in `platform_tests/scripts/test_gtkb_propose_scaffold.py` with a controlled real or in-memory MemBase fixture that proves real validation rather than string interpolation.
- Update `.claude/skills/gtkb-propose/SKILL.md` only if operator guidance changes; if current skill text remains accurate after the fix, leave it untouched.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v1 (verified) - this disposition uses the live bridge and live `bridge/INDEX.md` as the handoff authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) - this file links the governing requirements and explicitly separates routing from implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) - future implementation verification must map the validation semantics to negative and positive tests; this disposition has no source implementation.
- `GOV-STANDING-BACKLOG-001` v5 (verified) - WI-4274 is a standing-backlog advisory-router item and remains open until governed disposition / implementation evidence resolves it.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) - the source defect concerns invalid project-linkage metadata; this governance-advisory file is metadata-exempt because it authorizes no implementation.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 (specified) - adopt/adapt advisory-derived implementation must be owner-grilled before the implementation proposal exists.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 (specified) - mechanical gate contract; current lint coverage remains slice-deferred, so this proposal carries the gate evidence explicitly.
- `GOV-ARTIFACT-APPROVAL-001` v3 (verified) - future protected skill-file edits or formal-artifact mutations require formal artifact approval packets.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified) - all work remains inside `E:\GT-KB`; no Agent Red or other application subtree is in scope.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 (verified), `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 (verified), and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 (verified) - this advisory is preserved as a durable artifact with explicit lifecycle state instead of being lost as an insight report.
- `.claude/rules/peer-solution-advisory-loop.md` - supplies the adopt/adapt/reject/defer/monitor vocabulary used by the LO advisory routing project.
- `.claude/rules/file-bridge-protocol.md` - supplies the live-index, preflight, author-metadata, and spec-derived verification obligations.

## Prior Deliberations

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-03-14-27-GTKB-PROPOSE-SCAFFOLD-VALIDATION-GAP.md` - source LO advisory.
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-001.md` - approved Slice 4 proposal that promised read-only WI / Project / PAUTH validation.
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-002.md` - LO GO for the scaffold skill proposal.
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-003.md` - implementation report that claimed no deviation and referred to validated inputs.
- `bridge/gtkb-proposal-standards-propose-scaffold-skill-004.md` - terminal VERIFIED state for the original scaffold skill implementation.
- `.claude/skills/gtkb-propose/SKILL.md` - current operator-facing skill text promising read-only validation.
- `PROJECT-GTKB-LO-ADVISORY-ROUTING` - active routing project created by owner directive S366 to stop LO advisory work items aging in standalone limbo.
- _No prior bridge thread specifically disposes WI-4274 or authorizes source mutation for the validation-gap fix._

## Owner Decisions / Input

- Current owner instruction, 2026-06-12: continue PB-actionable work from the bridge or backlog and hand it off via the bridge protocol. This authorizes Prime to file a routing handoff, not to bypass project authorization or protected-artifact approval gates.
- Owner directive S366, 2026-05-30: create `PROJECT-GTKB-LO-ADVISORY-ROUTING` for the Route LO advisory cluster so these items stop aging in standalone limbo.
- No owner decision currently authorizes the source/test mutation for WI-4274. That is the reason this file is a `governance_advisory` disposition and not an implementation proposal.
- Future implementation requires durable AUQ / owner-decision evidence and a PAUTH-backed proposal before any source file changes.

## Clause Scope Clarification

This disposition is a single-advisory routing record. It does not perform a bulk backlog operation, does not resolve WI-4274, does not create a PAUTH, does not mutate MemBase, and does not edit source, test, skill, hook, or configuration files. The only immediate artifacts are this bridge file and its live index entry.

## Requirement Sufficiency

Existing requirements sufficient for the routing disposition. The source advisory, the verified original `/gtkb-propose` proposal, and the current governance specs already define the missing validation expectation. New or revised requirements are not needed to record this `adapt` disposition. A future implementation proposal must cite these same requirements and include project-linkage metadata once WI-4274 has active project/PAUTH coverage.

## Acceptance Criteria

1. Loyal Opposition confirms that `adapt` is the correct disposition for WI-4274.
2. Loyal Opposition confirms this file does not authorize source mutation and correctly blocks the actual fix on future owner / PAUTH evidence.
3. Loyal Opposition confirms the proposed follow-on implementation scope covers the validation gap without overreaching into unrelated `/gtkb-propose` behavior.
4. Applicability preflight and ADR/DCL clause preflight pass for this bridge file.
5. Prime Builder can use the GO, if granted, to pursue the owner-grilling / authorization step and then file a separate implementation proposal.

## Spec-Derived Verification Plan

| Linked specification / rule | Verification evidence for this disposition |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live `bridge/INDEX.md` contains `Document: gtkb-propose-scaffold-validation-gap-advisory-disposition` with `NEW: bridge/gtkb-propose-scaffold-validation-gap-advisory-disposition-001.md`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-validation-gap-advisory-disposition` must report no missing required or advisory specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No source implementation occurs in this disposition; the future implementation proposal must execute targeted pytest negative/positive cases for the MemBase validation semantics. |
| `GOV-STANDING-BACKLOG-001` | DB read-back confirms WI-4274 exists and is open/unapproved; this file records the single-item routing state and does not perform bulk resolution. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This `governance_advisory` is metadata-exempt and explicitly explains why implementation metadata is absent; the future implementation proposal must include project-linkage lines. |
| `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` / `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` | This file lists the required future owner-grilling decisions before implementation proposal filing. |
| `GOV-ARTIFACT-APPROVAL-001` | Any future protected skill-file edit or formal-artifact mutation remains blocked on a formal-artifact approval packet. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All referenced active paths are under `E:\GT-KB`; no `applications/` subtree mutation is proposed. |
| Artifact-oriented governance specs | The LO advisory becomes a durable bridge disposition with explicit lifecycle state. |

Verification commands for Loyal Opposition / Prime self-check:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-propose-scaffold-validation-gap-advisory-disposition
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-propose-scaffold-validation-gap-advisory-disposition
```

## Risk and Rollback

- **Risk: false-positive governance block.** If LO finds that the existing verified Slice 4 proposal already authorizes a corrective patch without a new PAUTH, LO should issue NO-GO with the exact authorization evidence. Prime can revise this disposition into a direct implementation proposal.
- **Risk: under-scoped follow-on.** If `.claude/skills/gtkb-propose/SKILL.md` must change to explain the new validation errors, LO should require that protected path and its artifact-approval evidence in the follow-on proposal.
- **Risk: over-applying peer-advisory vocabulary.** If LO considers WI-4274 an internal defect advisory rather than a peer/advisory-loop item, LO can still GO the core routing result or require a revised classification label. The operational boundary remains the same: no source mutation until authorization exists.
- **Rollback:** remove this bridge file and index line before commit if LO rejects the routing approach. No source, test, DB, or protected-rule rollback is needed because this disposition performs no such mutation.

End of proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
