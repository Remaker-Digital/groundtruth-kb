REVISED

# Phase-1 Harness-State SoT Consolidation - Backlog Conflict Revision

bridge_kind: governance_advisory
Document: gtkb-harness-state-sot-consolidation-phase-1
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-harness-state-sot-consolidation-phase-1-002.md (NO-GO)
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: keep-working-pb-2026-06-04T16-56Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop automation, Prime Builder bridge revision

target_paths: []
requires_verification: false
implementation_scope: governance_only

## Revision Claim

This revision resolves the NO-GO at
`bridge/gtkb-harness-state-sot-consolidation-phase-1-002.md` by bringing the
pre-existing open backlog item `WI-4214` into the Phase 1 mirror-retirement
scope instead of leaving it as a duplicate tracker outside the project.

No implementation authority changes are taken in this umbrella revision. The
final mirror-retirement child bridge must explicitly handle both `WI-4336` and
`WI-4214` before the legacy mirror is treated as complete.

## Specification Links

| Spec | Severity | How this revision complies |
|------|----------|----------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | Files the response as an append-only `REVISED` bridge version and updates the live index chain. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | Preserves the umbrella's explicit specification-linkage section and adds the backlog-conflict response here. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | Keeps executable verification delegated to child implementation bridges; this umbrella remains governance review only. |
| `GOV-STANDING-BACKLOG-001` | blocking | Addresses the duplicate open backlog item directly and prevents orphan work-item drift. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | Keeps implementation deferred to child bridges with their own authorization evidence. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | Requires the mirror-retirement child to ensure `WI-4214` is covered by its implementation/resolution authorization before execution. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | Preserves the owner directive, duplicate backlog item, revision, and child-bridge constraints as durable artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | Keeps work-item lineage explicit so implementation and backlog closure remain traceable. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | Records the blocked-to-revised lifecycle transition before child implementation begins. |

## Prior Deliberations

- `DELIB-20260668` - owner decision record for the 8-AUQ harness-state SoT
  consolidation scope.
- `DELIB-20260669` - session-harvest drift evidence for registry vs legacy
  mirror divergence.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001.md` - original
  governance umbrella.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-002.md` - operative
  NO-GO identifying the `WI-4214` duplicate backlog conflict.

No new owner decision is required. This revision links existing backlog work
to the already owner-directed clean-delete scope.

## Finding Addressed

### P1 - Open WI-4214 is now linked to the mirror-retirement child

The Phase 1 roster is amended as follows:

| WI | Title (short) | Child Bridge |
|----|---------------|--------------|
| WI-4336 + WI-4214 | Delete and retire `harness-state/role-assignments.json`; resolve legacy duplicate tracker | mirror-retirement (final) |

The final child bridge
`gtkb-harness-state-sot-consolidation-phase-1-mirror-retirement-001` must:

1. Cite both `WI-4336` and `WI-4214`.
2. Treat `WI-4214` as the pre-existing legacy tracker for the same
   `role-assignments.json` mirror-retirement scope.
3. Ensure its implementation/resolution authorization covers both the physical
   deletion work and the backlog resolution work before execution.
4. Resolve both work items together after the mirror is deleted and all live
   referencers have migrated.

If the existing Phase 1 PAUTH cannot mechanically cover `WI-4214`, the child
bridge must either obtain/update an authorization envelope that includes
`WI-4214`, or include explicit owner-approved GOV-15 evidence for resolving the
legacy duplicate as part of the mirror-retirement child. The umbrella GO alone
does not authorize bypassing that child-level check.

## Scope Changes

Only the backlog mapping changes. The design/spec drafts, four-child sequence,
SoT boundary, retired-path inventory, and explicit Phase 1 exclusions from
`-001` remain unchanged.

## Pre-Filing Preflight Subsection

Observed commands:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1
```

Observed result:

- Applicability preflight PASS.
- Packet hash: `sha256:df5d1a2a7c3f118e78b1425188d94e87ef6f1f6e1d5b20b2f11eaace87d73337`.
- Missing required specs: none.
- Missing advisory specs: none.
- Clause preflight PASS.
- Clauses evaluated: 5.
- Must-apply clauses: 3.
- Blocking gaps: 0.

Live filing wrote `bridge/gtkb-harness-state-sot-consolidation-phase-1-003.md`
and inserted `REVISED: bridge/gtkb-harness-state-sot-consolidation-phase-1-003.md`
at the top of the existing `Document: gtkb-harness-state-sot-consolidation-phase-1`
entry in `bridge/INDEX.md`. Prior versions `-001` and `-002` remain append-only
and unchanged.

## Specification-Derived Verification Plan

This umbrella remains a governance-review document with `target_paths: []`.
The child implementation proposals must carry executable verification. The
mirror-retirement child must additionally verify:

- `WI-4214` is cited in the child bridge and either covered by child
  authorization or resolved with explicit GOV-15 owner-approved evidence.
- `WI-4336` and `WI-4214` are both terminal after the mirror-retirement child
  completes.
- `harness-state/role-assignments.json` is absent only after all live
  referencers have migrated.

## Risk And Rollback

Risk is low. This revision reduces backlog drift by linking a duplicate legacy
tracker into the final child rather than creating a second independent cleanup
path.

Rollback is to file a later REVISED umbrella if Loyal Opposition wants `WI-4214`
to replace `WI-4336` outright instead of being grouped with it. No source,
database, or protected narrative file is changed by this umbrella revision.

## Recommended Outcome

GO for the revised governance umbrella, with the final mirror-retirement child
required to handle both `WI-4336` and `WI-4214`.
