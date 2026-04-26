VERIFIED

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 1 Post-Implementation

Status: VERIFIED

## Claim

Slice 1 is verified. The implementation lands the Wave 2 manifest-validation
base in `scripts/rehearse/_common.py` without breaking the existing Wave 1
driver path, and the requested regression set passes.

## Evidence

- `scripts/rehearse/_common.py:112` adds `ManifestValidationError` as a
  `ManifestError` subclass, preserving existing `except ManifestError`
  behavior.
- `scripts/rehearse/_common.py:232` changes `load_manifest()` to
  `load_manifest(path, *, wave: int = 1)`, so the existing driver call remains
  Wave 1 compatible.
- `scripts/rehearse/_common.py:241` documents the required caveat that Wave 2
  guarantees apply only when call sites explicitly pass `wave=2` or later.
- `scripts/rehearse/_common.py:285` gates M1-M5 validation behind
  `if wave >= 2`, with the Wave 3 `db_reconciliation_strategy` rejection kept
  at the intended later boundary.
- `tests/scripts/test_rehearse_common_validation.py:62` through
  `tests/scripts/test_rehearse_common_validation.py:218` provide the 14
  additive tests covering M1-M5 plus Wave 1 compatibility.
- Verification command run in this checkout:
  `python -m pytest tests/scripts/test_rehearse_common_validation.py tests/scripts/test_rehearse_isolation.py -q --tb=short`
  Result: 65 passed in 0.45s.

## Risk / Impact

No blocking risk found in Slice 1.

The remaining sequencing risk is external to this slice: downstream Wave 2
lanes still must not consume the source manifest as if it had runtime
`surface_treatments`. Slice 2 or its successor must add the runtime manifest
population and revalidation before lanes 2-11 consume it.

## Recommended Action

Treat Slice 1 as complete. Continue Wave 2 only through a reviewed
runtime-manifest path that explicitly opts into `load_manifest(..., wave=2)` and
validates populated `surface_treatments` before downstream lane consumption.

## Decision Needed From Owner

None.
