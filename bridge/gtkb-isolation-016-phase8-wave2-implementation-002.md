# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Implementation

Status: NO-GO

## Claim

`bridge/gtkb-isolation-016-phase8-wave2-implementation-001.md` is not approved because the checked-out repository does not match the proposal's asserted prerequisite state. The rehearsal manifest still contains unresolved owner-decision placeholders, and the referenced authority matrix path does not exist.

## Evidence

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml` still contains:
  - `output_dir = "OWNER_DECISION_REQUIRED"`
  - `git_strategy = "OWNER_DECISION_REQUIRED"`
  - `db_reconciliation_strategy = "OWNER_DECISION_REQUIRED"`
  - an empty `[surface_treatments]` table
- The same manifest references `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE-1-AUTHORITY-MATRIX.md`.
- That referenced file does not exist in the checkout.
- Repository search shows the available authority-matrix plan filename is `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`, not the path referenced by the manifest/proposal.
- `scripts/rehearse_isolation.py` remains a Wave 1 dispatch stub.
- `scripts/rehearse/_common.py` currently validates only a narrow subset of manifest fields and does not reject `OWNER_DECISION_REQUIRED` placeholders or validate output-directory safety and surface-treatment completeness.

## Risk / Impact

Wave 2 implementation would build against a manifest that still encodes unresolved decisions. That makes the sub-script contracts ambiguous and can lead to generated scripts inheriting invalid defaults.

The missing authority matrix path is a direct traceability break: the proposal says surface treatment coverage is grounded in that matrix, but the referenced artifact is not present.

## Recommended Action

Revise before implementation:

- Land the manifest update claimed by the proposal, including concrete `output_dir`, `git_strategy`, `git_filter_command`, and surface-treatment entries.
- Correct the authority matrix reference or create the canonical referenced matrix artifact.
- Add early manifest validation for unresolved placeholders, output sandbox safety, git strategy, and surface-treatment completeness before adding Wave 2 sub-scripts.

## Decision Needed From Owner

None.
