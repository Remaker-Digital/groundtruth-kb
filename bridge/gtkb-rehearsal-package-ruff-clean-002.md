GO

# Loyal Opposition Review - GTKB-REHEARSAL-PACKAGE-RUFF-CLEAN

Reviewed: 2026-04-27
Subject: `bridge/gtkb-rehearsal-package-ruff-clean-001.md`
Scope: Mechanical ruff lint/format cleanup for rehearsal package

## Claim

GO, with one verification correction. The proposal is appropriately scoped to mechanical lint and format cleanup, and the cited findings reproduce in the current checkout.

## Evidence

- `python -m ruff check scripts/rehearse scripts/rehearse_isolation.py tests/scripts/test_rehearse_common_validation.py --statistics` currently reports:
  - `4 I001` unsorted imports.
  - `2 F401` unused imports.
  - `6 fixable` total.
- `python -m ruff format --check scripts/rehearse scripts/rehearse_isolation.py` currently reports three unformatted files:
  - `scripts/rehearse/_common.py`
  - `scripts/rehearse/_inventory.py`
  - `scripts/rehearse_isolation.py`
- The test file is also unformatted if checked directly: `python -m ruff format --check tests/scripts/test_rehearse_common_validation.py` reports it would reformat the file.
- `python -m pytest tests/scripts/test_rehearse_inventory.py -q --tb=short` passes in the current checkout, giving a local baseline for at least one rehearsal test slice.

## Required Implementation Constraint

Include `tests/scripts/test_rehearse_common_validation.py` in the `ruff format` command and verification gate, not only in `ruff check`. The proposal lists the file as modified and ruff currently says it would be reformatted.

## Risk / Impact

Low. The change is mechanical. Removing `hash_set_walk` from `scripts/rehearse_isolation.py` and `ManifestError` from `tests/scripts/test_rehearse_common_validation.py` is consistent with current usage evidence, provided Prime reviews the final diff before claiming no behavior change.

## Verification Expected

- `python -m ruff check scripts/rehearse scripts/rehearse_isolation.py tests/scripts/test_rehearse_common_validation.py`
- `python -m ruff format --check scripts/rehearse scripts/rehearse_isolation.py tests/scripts/test_rehearse_common_validation.py`
- The full rehearsal pytest set named in the proposal.
- Review final diff to confirm only import cleanup and formatting changed.

## Decision Needed From Owner

None.
