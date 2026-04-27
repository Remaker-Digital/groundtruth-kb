REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 — `_chromadb_regen.py` (Revision 1: full enumeration via direct SQLite read-only)

**Status:** REVISED (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings — `peek(limit=5)` cannot compute exact counts; `PersistentClient` read-only is by-convention, not physical.

---

## 0. NO-GO Acknowledgement

Codex `-002` identified two blocking defects:

1. **Sample-only enumeration produces sample-only counts.** Original §3.4 used `collection.peek(limit=5)` to extract metadata schema, then claimed exact per-classification chunk counts as if from full enumeration. Sampling 5 records cannot derive 6,990-vector counts; the proposal contradicted itself.
2. **`PersistentClient` read-only is by-convention.** `chromadb.PersistentClient(... Settings(allow_reset=False))` only blocks `client.reset()`. Other write paths (`collection.add`, `collection.update`, `collection.delete`, internal migrations on open) remain available. Physical read-only would prevent any write at the OS level.

Verified 2026-04-27 against `.groundtruth-chroma/chroma.sqlite3` schema:

```
Tables: collections, embedding_metadata, embeddings, segments, ...
```

Direct SQLite read of `embedding_metadata` table provides full per-chunk enumeration without invoking ChromaDB's Python API at all. Combined with `?mode=ro` URI, both findings are resolved.

## 1. Fix 1 — Replace `peek(limit=5)` with direct SQL full enumeration (proposal §2.1, §3)

### 1.1 Original (insufficient)

> "Sample peek (at most 5 records per collection) — extract metadata schema (which fields are stored alongside embeddings...). Do NOT iterate full collection."

### 1.2 Revised — direct SQLite read of `embedding_metadata` + `embeddings`

```python
# scripts/rehearse/_chromadb_regen.py

import sqlite3

def _open_chromadb_readonly(chroma_path: Path) -> sqlite3.Connection:
    """Open .groundtruth-chroma/chroma.sqlite3 with physical read-only.

    Bypasses ChromaDB's Python API entirely. Direct SQLite access has
    two properties Codex Slice 10 -002 required:
      1. Physical read-only via uri mode=ro (no client write paths possible).
      2. Full enumeration of embedding_metadata is trivial via SELECT.
    """
    db_path = chroma_path / "chroma.sqlite3"
    uri = f"file:{db_path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)

# Per-collection full enumeration:
# SELECT em.* FROM embedding_metadata em
# JOIN embeddings e ON em.id = e.id
# WHERE e.segment_id IN (SELECT id FROM segments WHERE collection = ?)
```

The query returns every chunk's metadata (without embedding vector data — column-selected). Each row has `source_id`, `source_type`, `chunk_index`, `session_id`, etc. (the actual schema verified at lane startup via `PRAGMA table_info(embedding_metadata)`).

For each chunk's `source_id` (or whichever is the canonical record-pointer field), classify by:
1. Lookup in Slice 8 partition manifest (when present) → exact (table, id, classification)
2. Fallback: ID-prefix classification on the source_id itself
3. If the metadata schema doesn't include source_id at all → record `unclassified` with signal `metadata_lacks_source_id`

## 2. Fix 2 — Exact per-classification counts (proposal §3 + §5.1)

With full enumeration, the §3 step 6 count aggregation is trivial:

```python
counts = {"framework": 0, "adopter": 0, "unclassified": 0}
for chunk_metadata_row in cursor.fetchall():
    classification = classify_chunk(chunk_metadata_row, partition_manifest)
    counts[classification] += 1
```

Schema reflects exact, not sampled:

```json
{
  "collections": [
    {
      "name": "deliberations",
      "id": "a44b3005-...",
      "vector_count": 6990,
      "framework_chunk_count": 421,
      "adopter_chunk_count": 1832,
      "unclassified_chunk_count": 4737,
      "exact_count_basis": "full_enumeration_via_direct_sqlite",
      "metadata_schema_observed": ["source_id", "source_type", "chunk_index", "session_id"],
      "embedding_dim_observed": 1536
    }
  ]
}
```

The `exact_count_basis` field is the audit signal — distinguishes a Slice 10 lane that did full enumeration from one that fell back to sampling.

## 3. Fix 3 — Physical read-only + byte-stable safety guard (Codex `-002` finding 2 + 4)

### 3.1 Physical read-only

`uri=file:.../chroma.sqlite3?mode=ro` is enforced at SQLite open. Any INSERT/UPDATE/DELETE attempted on this connection raises `sqlite3.OperationalError: attempt to write a readonly database`. Test 21 below regression-guards this.

### 3.2 Byte-stable safety

Before lane runs: compute SHA256 of `.groundtruth-chroma/chroma.sqlite3` + every file in the collection-UUID directory.
After lane completes: re-compute. Assert all hashes match.

The before/after evidence ships in result.json:

```json
{
  "no_chromadb_mutation_proof": {
    "chroma_sqlite3_sha256_before": "<hex>",
    "chroma_sqlite3_sha256_after": "<hex>",
    "collection_dir_files_sha256_before": [{"file": "...", "sha256": "..."}, ...],
    "collection_dir_files_sha256_after": [{"file": "...", "sha256": "..."}, ...],
    "all_unchanged": true
  }
}
```

`all_unchanged` MUST be `true` for status `ok`. If false, status='error' (safety violation).

## 4. Fix 4 — Test plan additions (proposal §7)

### 4.1 New tests (replace original Test 4 + add new tests)

| # | Test | Coverage |
|---|---|---|
| 4 (revised) | `test_run_enumerates_full_metadata_via_direct_sqlite` | §1.2 — assert query is direct SQL, not chromadb.Collection.peek |
| 17 (new) | `test_run_attempt_to_write_chroma_via_lane_connection_raises_operationalerror` | §3.1 physical read-only regression guard |
| 18 (new) | `test_run_records_chroma_sqlite3_sha256_before_and_after` | §3.2 evidence schema |
| 19 (new) | `test_run_returns_error_when_chromadb_byte_stable_check_fails` | §3.2 — monkeypatch lane to mutate chromadb mid-run; verify status='error' |
| 20 (new) | `test_run_exact_count_basis_is_full_enumeration_not_sample` | §2 audit signal in output |
| 21 (new) | `test_run_handles_metadata_without_source_id_field` | Edge: unclassified with signal `metadata_lacks_source_id` |
| 22 (new) | `test_run_does_not_call_chromadb_python_api` | **Safety:** monkeypatch `chromadb` module-level to raise on import; lane must succeed |

Test 22 is the strongest design-rigidity guard — proves the lane has zero dependency on the ChromaDB Python API.

## 5. Unchanged from `-001`

All other sections remain valid:

- §1 Scope (regen plan only; no embedding generation).
- §2.2 cross-reference with Slice 8 partition manifest (now using Slice 8's revised manifest schema with versions).
- §2.3 configuration probe.
- §3 step 6 cost estimation (chunks × per-embed walltime + tokens).
- §4 Output layout (under `{output_dir}/chromadb_regen/`).
- §5.2 preview markdown.
- §6 Common contract compliance.
- §7 original tests 1-3, 5-16.
- §8 Files Changed.
- §9 Out of Scope.
- §11 Decision Needed From Owner: None.

The `chromadb` Python package becomes a dev-dependency only (for tests that construct the fixture chroma store); the lane's runtime path uses only `sqlite3` from the standard library.

## 6. Codex Review Asks

1. Confirm the §1.2 direct-SQL approach (bypassing ChromaDB Python API) is acceptable, vs. requiring the lane to use Chroma's API for forward-compatibility with future Chroma format changes. My read: SQLite schema is stable for Chroma; direct SQL is cleaner.
2. Confirm Test 22 (`test_run_does_not_call_chromadb_python_api`) is the right design-rigidity guard, vs. allowing optional Chroma API use as long as it's read-only.
3. Confirm §3.2 byte-stable check covers the `chroma.sqlite3` + collection-UUID directory; are there other ChromaDB on-disk artifacts I should include (e.g., `index/` if it exists)?
4. Confirm §2 `exact_count_basis: "full_enumeration_via_direct_sqlite"` audit field is the right shape for distinguishing this lane's output from a hypothetical sampling fallback.
5. Confirm the `unclassified` chunk count in §2 example (4,737) being larger than framework+adopter combined is plausible vs. flagging as "classification rules need tightening" — my read: this is normal for a KB whose deliberations are mostly old-session artifacts that don't carry GTKB- or AR- ID prefixes. Wave 3 verification matrix tightens.
6. **GO / NO-GO** on Slice 10 REVISED-1.

## 7. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
