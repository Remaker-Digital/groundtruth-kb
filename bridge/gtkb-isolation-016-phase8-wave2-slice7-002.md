NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md`
Scope: CI inventory rehearsal lane proposal for `scripts/rehearse/_ci_inventory.py`

## Claim

Slice 7 is not ready to implement. The proposal misclassifies the release-candidate gate workflow as a GT-KB framework surface, contradicting the verified Slice 6 outcome it cites as authority.

## Evidence

- The proposal states that Slice 6 classified `.github/workflows/release-candidate-gate.yml` as `framework` with `release_gate_framework_surface` and says Slice 7 inherits that classification verbatim: `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md:25`.
- The Slice 7 rules table and sample outputs repeat that error:
  - `release-candidate-gate.yml` -> `framework`: `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md:70`.
  - Sample CSV classifies `.github/workflows/release-candidate-gate.yml` as `framework`: `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md:111`.
  - Preview says keep the workflow at GT-KB root as framework: `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md:140` to `:142`.
  - Test plan asks for `test_run_classifies_release_candidate_gate_as_framework`: `bridge/gtkb-isolation-016-phase8-wave2-slice7-001.md:210`.
- Verified Slice 6 says the opposite:
  - `_release_readiness_split.py` documents release-gate implementation surfaces, including workflow YAML, as `adopter`: `scripts/rehearse/_release_readiness_split.py:14` to `:16`.
  - `_classify_release_gate_surfaces()` writes `classification: "adopter"` and `classification_signal: "application_release_gate_surface"`: `scripts/rehearse/_release_readiness_split.py:147` to `:165`.
  - The regression guard is explicitly named `test_release_gate_surfaces_classified_as_adopter_not_framework`: `tests/scripts/test_rehearse_release_readiness_split.py:293`.
  - Slice 6 verification records `.github/workflows/release-candidate-gate.yml -> application_release_gate_surface`: `bridge/gtkb-isolation-016-phase8-wave2-slice6-010.md:111` to `:116`.

## Risk / Impact

If implemented as written, the CI relocation preview would keep an adopter-local application release gate at the GT-KB root. That directly undermines the isolation objective and creates inconsistent cross-lane evidence between CI inventory and release-readiness split.

## Required Revision

- Classify `.github/workflows/release-candidate-gate.yml` as `adopter`.
- Use the Slice 6 signal `application_release_gate_surface`, or a CI-specific adopter signal that preserves that ownership meaning.
- Update the rule table, sample CSV, preview text, summary counts, JSON example, and regression test name/assertions.
- Remove or correct the false statement that Slice 6 classified the workflow as framework.

## Decision Needed From Owner

None. This is a proposal defect against already-verified project evidence.
