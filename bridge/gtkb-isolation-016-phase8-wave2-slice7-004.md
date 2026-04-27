GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice7-003.md`
Scope: CI inventory rehearsal lane proposal for `scripts/rehearse/_ci_inventory.py`

## Claim

GO, with one cross-slice consistency constraint. The revised proposal corrects the blocking ownership defect from `-002`: `.github/workflows/release-candidate-gate.yml` is now classified as `adopter` with `application_release_gate_surface`.

## Evidence

- Slice 7 revision explicitly replaces the false framework classification with adopter classification and updates CSV, JSON, preview placement, counts, and tests.
- Live Slice 6 source classifies release-gate surfaces as `adopter` with `classification_signal: "application_release_gate_surface"`: `scripts/rehearse/_release_readiness_split.py:147` to `:166`.
- Live Slice 6 mechanism origins are declared in `_RELEASE_GATE_SURFACES`; for `.github/workflows/release-candidate-gate.yml`, the value is `agent_red_local`: `scripts/rehearse/_release_readiness_split.py:50` to `:53`.

## Required Implementation Constraint

If Slice 7 adopts `mechanism_origin`, reuse the exact Slice 6 value for the same surface: `agent_red_local`. Do not introduce `framework_provided_workflow_invoked_against_adopter_code` as a parallel vocabulary unless a separate canonicalization change updates Slice 6 too. The cross-slice regression test should compare classification, signal, and mechanism origin exactly.

## Risk / Impact

Low after the constraint. The original isolation risk was fixed; the remaining issue is vocabulary drift between lanes.

## Verification Expected

- New `tests/scripts/test_rehearse_ci_inventory.py` passes.
- Existing Slice 6 release-readiness split tests still pass.
- Cross-slice test proves release-candidate-gate classification, signal, and mechanism origin match Slice 6.

## Decision Needed From Owner

None.
