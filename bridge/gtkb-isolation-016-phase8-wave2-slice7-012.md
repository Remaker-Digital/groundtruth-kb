VERIFIED

# Loyal Opposition Verification - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 Revision 3

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice7-011.md`
Implementation commits: `7ae15c79`, `f3f2a88d`, `5b3c6ec8`, `637860f4`

## Prior Deliberations

The required deliberation search was attempted before review with:

- `GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 7 excluded_paths python-tests`

The CLI returned no additional rows in this session. Relevant bridge context is this thread: `-008` rejected missing `excluded_paths` consumption and missing python-tests classifier coverage; `-010` rejected the first python-tests fix because it did not recognize the live GitHub Actions `test_args=...` pattern.

## Claim

VERIFIED. Revision `-011` addresses the `-010` blocker. The CI inventory lane now recognizes the live `.github/workflows/python-tests.yml` shard-resolver shape and classifies it as adopter, while preserving the prior release-candidate-gate cross-slice classification and excluded-path behavior.

## Evidence

- The revised implementation adds `_extract_pytest_targets()` for both literal `pytest tests/...` commands and GitHub Actions `test_args=tests/...` output-forwarding assignments: `scripts/rehearse/_ci_inventory.py`.
- The revised tests add live-shape coverage for the GHA `test_args` pattern plus helper tests for multi-target assignments and literal pytest commands: `tests/scripts/test_rehearse_ci_inventory.py`.
- Focused tests passed:
  - Command: `python -m pytest tests/scripts/test_rehearse_ci_inventory.py -q --tb=line --timeout=60`
  - Result: `27 passed in 0.54s`.
- Full rehearsal script tests passed:
  - Command: `python -m pytest @files -q --tb=line --timeout=120` over all `tests/scripts/test_rehearse_*.py`.
  - Result: `214 passed in 3.62s`.
- Ruff passed:
  - `python -m ruff check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py` -> `All checks passed!`
  - `python -m ruff format --check scripts/rehearse/_ci_inventory.py tests/scripts/test_rehearse_ci_inventory.py` -> `2 files already formatted`.
- Live smoke passed:
  - Command: `python scripts/rehearse_isolation.py --phase ci --execute --output-dir C:\temp\agent-red-rehearsal-slice7-revised3-codex-verify`
  - Result: `ci ... ok`.
  - Live `.github/workflows/python-tests.yml` row: `classification = "adopter"`, `classification_signal = "agent_red_pytest_workflow"`.
  - Live `.github/workflows/release-candidate-gate.yml` row remains `classification = "adopter"`, `classification_signal = "application_release_gate_surface"`, `mechanism_origin = "agent_red_local"`.

## Risk / Impact

The prior blocker is resolved. Remaining unclassified CI rows are expected owner-decision surfaces, not verification blockers for this slice:

- `.github/workflows/lint.yml` -> `mixed_scope_linter_owner_decision_required`
- `.github/workflows/sonarcloud.yml` -> `no_classification_signal`
- absent probed configs -> `absent_probed`

The live smoke summary after the fix is `workflow_count = 14`, `ci_config_count = 7`, `adopter_count = 15`, `unclassified_count = 6`, and `owner_decisions_required = 6`.

## Recommended Follow-Up

Wave 3 should resolve or explicitly preserve the remaining unclassified CI rows. No owner decision is needed for Slice 7 verification.

## Decision Needed From Owner

None.
