NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice10-003.md`
Scope: ChromaDB regeneration rehearsal lane proposal for `scripts/rehearse/_chromadb_regen.py`

## Claim

NO-GO. The revised proposal correctly chooses physical read-only SQLite and full enumeration, but it misunderstands the live ChromaDB schema. `embedding_metadata` is key/value rows, not one metadata object row per chunk.

## Evidence

- Live `.groundtruth-chroma/chroma.sqlite3` tables include `collections`, `segments`, `embeddings`, and `embedding_metadata`.
- Live `embedding_metadata` columns are `id`, `key`, `string_value`, `int_value`, `float_value`, and `bool_value`.
- Sample live rows show many metadata rows per embedding id: e.g. id `17` has keys such as `chunk_index`, `origin_project`, `outcome`, `source_type`, `version`, `chroma:document`, `source_ref`, `delib_id`, and others.
- The revision says the query returns every chunk's metadata row with fields such as `source_id`, `source_type`, `chunk_index`, and `session_id`. That is not the live row shape; the implementation must pivot/group key/value rows per embedding id.
- The live collection dimension is `384`; the revised example still uses `1536`.

## Risk / Impact

Implementing the direct SQL query as described would either overcount metadata rows as chunks or fail to reconstruct per-chunk metadata. Exact framework/adopter/unclassified counts would still be unreliable, which is the blocking defect the revision was meant to fix.

## Required Revision

- Define a pivot/grouping step keyed by `embedding_metadata.id` / `embeddings.id` so one chunk record is built from all metadata key/value rows for that embedding.
- Use live metadata keys. There is `delib_id`; there may not be a generic `source_id` for this collection.
- Define the canonical classification pointer for this Chroma collection, likely `delib_id` plus `version`, with fallback to `source_ref` or other metadata only if documented.
- Use `collections.dimension` for embedding dimension evidence instead of hardcoded/sample values.
- Add tests with key/value-style `embedding_metadata` fixture rows, not object-shaped rows.

## Decision Needed From Owner

None. Prime needs to revise against the actual ChromaDB SQLite schema.
