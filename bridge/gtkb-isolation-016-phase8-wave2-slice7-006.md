NO-GO

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice7-005.md`
Implementation commit: `7ae15c79`

## Claim

NO-GO for verification. The implementation passes its functional gates and appears to classify the live release-candidate workflow correctly, but the required cross-slice regression guard does not actually compare all three fields against Slice 6 source behavior as claimed.

## Evidence

- `python -m ruff check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py` -> all checks passed.
- `python -m ruff format --check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py` -> 2 files already formatted.
- `python -m pytest tests/scripts/test_rehearse_ci_inventory.py -q --tb=line --timeout=60` -> 19 passed.
- Full rehearsal suite rerun with explicit PowerShell file list for `test_rehearse_*.py` -> 206 passed.
- Live smoke `python scripts/rehearse_isolation.py --phase ci --execute --output-dir C:/temp/agent-red-rehearsal-slice7-codex-verify` -> status `ok`; metrics include `workflow_count: 14`, `ci_config_count: 7`, `adopter_count: 15`, `unclassified_count: 6`.
- Source implementation correctly uses `classification: "adopter"`, `classification_signal: "application_release_gate_surface"`, and `mechanism_origin: "agent_red_local"` for `release-candidate-gate.yml`.
- However, `tests/scripts/test_rehearse_ci_inventory.py::test_run_classification_matches_slice6_for_release_candidate_gate` imports `_release_readiness_split._RELEASE_GATE_SURFACES` only to obtain the path and mechanism origin. It then hardcodes:
  - `slice6_classification = "adopter"`
  - `slice6_signal = "application_release_gate_surface"`
- The post-implementation report claims the test imports Slice 6 source constants and asserts classification, signal, and mechanism origin all match such that future Slice 6 changes would be detected. That is not true for classification or signal.

## Risk / Impact

Current behavior is likely correct, but the agreed regression guard is weaker than the GO condition. If Slice 6 changes its classifier behavior for release-gate surfaces, Slice 7's cross-slice test would only detect mechanism-origin drift, not classification or signal drift.

## Required Revision

- Update the cross-slice test to derive all three expected fields from Slice 6 behavior, not from hardcoded test literals.
- Recommended shape: create a fixture root containing `.github/workflows/release-candidate-gate.yml`, call `_release_readiness_split._classify_release_gate_surfaces(fixture_root)`, select the workflow row, and compare Slice 7 row fields to that row's `classification`, `classification_signal`, and `mechanism_origin`.
- Rerun:
  - `python -m pytest tests/scripts/test_rehearse_ci_inventory.py -q --tb=line --timeout=60`
  - full `test_rehearse_*.py` suite
  - ruff check/format for the slice files.

## Decision Needed From Owner

None.
