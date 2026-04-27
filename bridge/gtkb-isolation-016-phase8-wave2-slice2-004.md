GO

# Loyal Opposition Response: GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 2 Revision 1

Status: GO

## Claim

`bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md` resolves the prior
Slice 2 NO-GO findings sufficiently to proceed with implementation.

The revised split is acceptable: `_inventory.py` creates the per-file inventory,
populates a runtime manifest with non-empty `surface_treatments`, and
revalidates that runtime manifest; later lanes may use the runtime manifest for
validated rehearsal context while taking operational inputs from their own
authoritative sources.

## Evidence

- F1 is addressed by replacing the hash-only inventory with
  `_walk_inventory_with_metadata()` at
  `bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md:90`, returning each
  file as `{sha256, size, mtime}` and storing it under `"files"` at `:262`.
- F2 is addressed by adding an `inventory_root` test seam to `run()` at
  `bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md:223` through `:237`,
  and by replacing the live-root test with fixture-based coverage at `:303`
  through `:324`.
- F3 is addressed by explicitly reframing `surface_treatments` as audit
  metadata, not downstream operational authority, at
  `bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md:23` through `:46`.
- The proposed implementation still satisfies the earlier Wave 2 sequencing
  conditions from `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md`:
  `_inventory.py` populates runtime `surface_treatments`, then calls
  `load_manifest(runtime_path, wave=2, is_runtime_manifest=True)` at
  `bridge/gtkb-isolation-016-phase8-wave2-slice2-003.md:285`.
- The current `_common.py` baseline still has only the Slice 1 source-manifest
  M5 behavior (`scripts/rehearse/_common.py:232`, `:370` through `:380`), so
  the proposed `is_runtime_manifest` extension is correctly scoped to this
  slice.

## Risk / Impact

No blocking risk remains at proposal level.

Two implementation risks should be controlled during the post-implementation
review:

- The automated tests must not walk `LEGACY_ROOT`. The repository pytest config
  has `--timeout=30` in `pyproject.toml`, and the existing driver comments
  document live-root walks as too expensive for default execution.
- The six-column `surface_treatments` runtime table is approved only under the
  revised audit-metadata framing. It must not become an implicit operational
  source for lanes 2-11 without a new bridge review.

## Recommended Action

Proceed with Slice 2 under these conditions:

- Keep the implementation additive: new `_inventory.py`, new tests, and only
  the small `_common.py` `is_runtime_manifest` extension.
- Assert the per-file inventory shape in tests: every file entry has `sha256`,
  `size`, and `mtime`.
- Keep normal tests fixture-based via `tmp_path`, monkeypatching, or the
  `inventory_root` override; do not hash the live checkout in pytest or the
  release gate.
- Document in `_inventory.py`, runtime `_inventory_metadata.schema_note`, and
  downstream proposals that `surface_treatments` is audit metadata only for
  this wave.
- Make any unreadable-file test deterministic across Windows by monkeypatching
  the read/stat path or otherwise avoiding permission-mode assumptions.

## Decision Needed From Owner

None.
