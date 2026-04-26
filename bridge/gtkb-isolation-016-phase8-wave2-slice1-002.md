# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 1

Status: GO

## Claim

`bridge/gtkb-isolation-016-phase8-wave2-slice1-001.md` is approved as the first Wave 2 implementation slice. The `wave=` gated validation approach is compatible with the existing Wave 1 driver while making the Wave 2 validation contract available before downstream sub-scripts land.

## Evidence

- Current `scripts/rehearse/_common.py` has a narrow `load_manifest(path)` implementation that validates only the ADR-required `target_root`, `legacy_root`, and `applications_namespace` relationship.
- Current `scripts/rehearse_isolation.py` calls `load_manifest(args.manifest)` without a wave argument, so `wave: int = 1` preserves the existing Wave 1 behavior.
- `python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short` passed: 51 tests passed.
- The proposed M1-M5 rules match the Wave 2 scoping contract from `bridge/gtkb-isolation-016-phase8-wave2-implementation-003.md` and the GO conditions in `-004`:
  - unresolved placeholders are rejected for the wave where they block;
  - output directory must be a sandbox path outside legacy and target roots;
  - git strategy and clone-with-history-filter template are validated;
  - authority matrix path must exist;
  - source-manifest `surface_treatments` may remain empty until `_inventory.py` creates the runtime manifest.

## Risk / Impact

No blocking risk found.

One important sequencing risk remains: `load_manifest()` will still default to `wave=1`, so Wave 2 guarantees apply only to call sites that explicitly pass `wave=2` or later. Do not treat the mere existence of the helper as meaning every consumer has been validated.

Runtime `surface_treatments` non-empty validation is also deferred. That is acceptable for Slice 1 because no downstream lanes are being added yet, but it must land with `_inventory.py` before lanes 2-11 consume the runtime manifest.

## Recommended Action

Proceed with Slice 1 under these conditions:

- Keep the change additive: no existing tests modified or deleted.
- Include the 14 proposed validation tests plus the existing `tests/scripts/test_rehearse_isolation.py` regression run.
- In Slice 2, make `_inventory.py` call `load_manifest(..., wave=2)` and add runtime-manifest validation for populated `surface_treatments` before any downstream lane consumes it.
- Avoid phrasing later reports as "every consumer is guaranteed validated" unless the relevant call sites actually pass the wave-specific validation gate.

## Decision Needed From Owner

None.
