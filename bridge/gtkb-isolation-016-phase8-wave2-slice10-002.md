NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md`
Scope: ChromaDB regeneration rehearsal lane proposal for `scripts/rehearse/_chromadb_regen.py`

## Claim

Slice 10 is not ready to implement. The proposal cannot produce exact per-classification chunk counts from a five-record sample, and its read-only guarantee is by convention rather than physical access mode.

## Evidence

- The proposal promises read-only ChromaDB access using `chromadb.PersistentClient(... Settings(allow_reset=False))`: `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md:41` to `:42`.
- The proposal samples at most five records per collection and explicitly says not to iterate the full collection: `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md:47`, `:63` to `:64`, and `:189`.
- The next step says it will cross-reference each metadata `source_id` and aggregate exact counts for `{framework_chunk_count, adopter_chunk_count, unclassified_chunk_count}`: `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md:65`.
- The sample output presents exact counts and acceptance criteria against a 6,990-vector collection: `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md:96` to `:111`, `:135` to `:154`.
- The proposal itself notes the safer alternative of direct SQLite read-only access: `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md:235`.
- The live legacy ChromaDB exists at `.groundtruth-chroma/chroma.sqlite3` with one collection directory, so this is not a hypothetical path.

## Risk / Impact

Sampling five records can reveal metadata shape, but it cannot prove or compute exact per-subject chunk counts across the collection. A plan built from sample-derived counts would make regeneration cost, acceptance, and owner decisions unreliable. Separately, using a Chroma persistent client does not prove the legacy store cannot be touched by client metadata writes, migrations, or lock behavior.

## Required Revision

- Iterate or page through all ids/metadatas needed for classification counts without fetching embeddings, or explicitly label per-classification counts as sample-only and do not use them for acceptance gates.
- Prefer a physical read-only strategy for the legacy store, such as SQLite URI `mode=ro` where feasible, or copy the Chroma store to a sandbox before opening it with Chroma APIs.
- Add tests that distinguish metadata-only full enumeration from `peek(limit=5)` sampling.
- Add a safety test or implementation constraint proving legacy `.groundtruth-chroma/` remains byte-stable after the lane runs.

## Decision Needed From Owner

None. This is a correctness and safety issue in the proposed lane design.
