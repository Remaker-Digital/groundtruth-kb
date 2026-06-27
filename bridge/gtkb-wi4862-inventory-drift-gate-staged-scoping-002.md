GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4862-inventory-drift-gate-staged-scoping
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-27 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4862-inventory-drift-gate-staged-scoping-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4862
Recommended commit type: fix

## Separation Check

Proposal `-001` author session `eb4f5b12-588a-43b5-bf6b-5439c7a97cf0` (harness B);
independent Cursor LO session `cursor-e-20260626-lo-autoproc-5` (harness E).

## Review Summary

**GO.** Live code confirms the defect: `evaluate_drift` (~226–233) blocks on
`material_inventory_drift` unconditionally while pre-commit invokes `--staged`
(`.githooks/pre-commit` L17–19). Whole-tree drift from untracked inventoried
surfaces can block unrelated commits — matches the session finalization pile-up.

Staged-mode downgrade when no staged inventoried surface is touched is sound;
release gate (`staged=False`) unchanged per `DELIB-20266208`. Test plan covers
warn/block/unstaged paths.

## Residual risks (non-blocking)

- Hand-maintained `INVENTORIED_SURFACE_PATTERNS` mirror — mitigated by comment +
  release-gate backstop; follow-up export from collector is reasonable.

## Prior Deliberations

- DELIB-20266208 — owner AUQ for staged scoping + release strictness.
- bridge/gtkb-wi4862-inventory-drift-gate-staged-scoping-001.md (NEW).

## Recommendation

Proceed with implementation per `-001`.
