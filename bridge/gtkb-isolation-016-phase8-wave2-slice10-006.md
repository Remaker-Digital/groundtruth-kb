GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 REVISED-2

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md`
Scope: ChromaDB regeneration rehearsal lane proposal for `scripts/rehearse/_chromadb_regen.py`

## Prior Deliberations

The required deliberation search was attempted before review with:

- `GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 ChromaDB regeneration`
- `ChromaDB regeneration embedding_metadata delib_id`

The CLI returned no additional rows in this session. Relevant live bridge context is `-002` and `-004`, which rejected the earlier sample-count and object-shaped metadata assumptions.

## Claim

GO, with one implementation constraint. The REVISED-2 design corrects the prior blockers: it uses physical read-only SQLite, pivots key/value `embedding_metadata` rows per chunk id, uses live metadata keys, derives dimension from `collections.dimension`, and adds tests for the live schema shape.

## Evidence

- Live `.groundtruth-chroma/chroma.sqlite3` has `embedding_metadata(id, key, string_value, int_value, float_value, bool_value)`, matching the revised key/value pivot design in `bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md:58` to `:99`.
- Live `collections` includes `dimension = 384` for collection `deliberations`, matching the revised dimension source in `bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md:134` to `:136` and the example at `:150`.
- Live metadata key counts confirm the proposal's pointer basis: `delib_id` is present on 10,326 / 10,326 chunks, while `spec_id` and `work_item_id` are sparse. The revised hierarchy at `bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md:119` to `:127` is therefore directionally correct.
- The revised test plan includes key/value fixture rows, pivot validation, dimension-not-hardcoded validation, and typed value-column handling: `bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md:243` to `:253`.
- The prior read-only requirement remains covered by direct SQLite `mode=ro` and byte-stable checks retained from REVISED-1: `bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md:258` to `:262`.

## Implementation Constraint

Do not treat `DELIB-*` as a framework/adopter prefix. `classify_by_id_prefix()` only recognizes `GTKB-*` and `AR-*`; `DELIB-*` is an unknown prefix in the current helper. If Slice 8's partition manifest is absent or a `delib_id` is not found, the Slice 10 fallback must either:

- classify the chunk as `unclassified` with an explicit signal such as `partition_manifest_absent_delib_unknown_prefix`; or
- apply the same content-scan rules Slice 8 uses against available pivoted metadata, with tests proving the signal source.

The sentence in `bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md:125` saying "`DELIB-*` records carry session-id prefixes" must not become implementation behavior. The safe default is unclassified, not silent framework/adopter routing.

## Risk / Impact

Low after the constraint. The live-schema blocker is resolved. The remaining risk is classification drift in the no-manifest fallback path, which is contained by requiring explicit unclassified handling or tested content-scan behavior.

## Verification Expected

- New `tests/scripts/test_rehearse_chromadb_regen.py` passes, including key/value metadata, read-only connection, byte-stable proof, dimension-from-table, and fallback classification tests.
- Full `tests/scripts/test_rehearse_*.py` suite still passes.
- Ruff check and format check pass for the new lane and tests.
- A live smoke emits `exact_count_basis: "full_metadata_pivot_via_direct_sqlite"` and records `embedding_dimension_from_collections_table: 384`.

## Decision Needed From Owner

None.
