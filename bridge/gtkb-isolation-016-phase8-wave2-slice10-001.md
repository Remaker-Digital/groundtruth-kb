NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 — `_chromadb_regen.py`

**Status:** NEW (slice; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Builds on:**
- `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md` (Wave 2 GO; umbrella)
- `bridge/gtkb-isolation-016-phase8-wave2-slice8-001.md` (Slice 8 NEW; partition manifest is optional cross-reference)

bridge_kind: implementation_slice
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_chromadb_regen.py + tests; driver dispatch already wired (table entry index 4: `("chromadb", "rehearse._chromadb_regen", "run")`)

**Filed in parallel with:** Slices 7, 8, 9 (Stage B) and 11 (`_dashboard_regen`) per owner direction 2026-04-27. Lanes are independent at the implementation level per umbrella -004.

---

## Prior Deliberations

- `DELIB-0877`: nine-phase GT-KB/application separation program.
- `DELIB-0878`: Phase 1 authority matrix plan.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: this slice reuses `_split_helper.emit_result()`. Does NOT use ID-prefix classification — ChromaDB embeddings classify by source-record ID lookup against Slice 8's partition manifest (when present) or by ID-prefix fallback when not.
- S311 wrap evidence: ChromaDB at `.groundtruth-chroma/` contains 6,990 chunks (mostly Deliberation Archive embeddings post WI-3168 migration). KB recovery in S311 confirmed ChromaDB independence from `groundtruth.db` (ChromaDB has its own SQLite backing).

## 1. Scope

Single Stage C leaf lane: `scripts/rehearse/_chromadb_regen.py`. Produces a **regeneration plan** for the ChromaDB embeddings store at the target child root. The lane DOES NOT execute regeneration — it only inventories the current store, computes the plan, and emits it for ISOLATION-018 cutover to execute.

Strictly additive: no driver changes (dispatch already registers `chromadb`), no manifest changes, no changes to `_common.py` or any earlier lane. Read-only on ChromaDB.

**Deliberate non-execution:** ChromaDB regeneration involves embedding API calls (token cost) and minutes of compute. The rehearsal lane only **plans** the regeneration; ISOLATION-018 cutover **executes** it. This matches the "preview" semantics of Phase 8 plan §2 ("dry-run output").

## 2. Authoritative Source Set

### 2.1 ChromaDB on disk

- **Source:** `LEGACY_ROOT/.groundtruth-chroma/chroma.sqlite3` (Chroma's SQLite backing) + collection-UUID directories alongside it (verified 2026-04-27: one collection with UUID `a44b3005-eddf-4379-8f2b-e59f5fb8060c`).
- **Access mode:** read-only via `chromadb.PersistentClient(path=..., settings=Settings(allow_reset=False))` — no `client.create_collection()`, no `client.delete_collection()`, no `collection.add()` / `update()` / `delete()`.
- **Collected metrics per collection:**
  - `name`
  - `id` (UUID)
  - `vector_count` (via `collection.count()`)
  - `metadata` keys present (sample first 5 records via `collection.peek(limit=5)` to extract schema)
  - estimated `embedding_dim` (from sample peek)

### 2.2 Slice 8 partition manifest (optional cross-reference)

- If `{output_dir}/membase_export/partition_manifest.json` exists from a prior Slice 8 run in the same rehearsal output dir, use it to compute per-record adopter/framework split for the regen plan.
- If absent, fall back to ID-prefix classification on the source record IDs (deliberation IDs, spec IDs, etc.) using `_split_helper.classify_by_id_prefix()`.

### 2.3 Configuration

- `LEGACY_ROOT/groundtruth.toml` (root) and any other ChromaDB config files referenced from `tools/knowledge-db/`.
- The lane reads but does not modify these. Records the configured ChromaDB path for the regen plan.

## 3. Algorithm

1. **Probe** ChromaDB store at `LEGACY_ROOT/.groundtruth-chroma/`. If absent: emit warning, classify as "no ChromaDB to migrate", return ok with empty plan.
2. **Open read-only.** Enumerate collections. For each collection, gather metrics per §2.1.
3. **Sample peek** (at most 5 records per collection) — extract metadata schema (which fields are stored alongside embeddings: `source_id`, `source_type`, `chunk_index`, etc.). Do NOT iterate full collection.
4. **Cross-reference** with Slice 8's `partition_manifest.json` if present. For each metadata `source_id`, look up classification. Aggregate per-collection counts: `{framework_chunk_count, adopter_chunk_count, unclassified_chunk_count}`.
5. **Compute regen plan** per collection:
   - Adopter chunks: regenerate at `applications/Agent_Red/.groundtruth-chroma/`
   - Framework chunks: regenerate at `<gt-kb-root>/.groundtruth-chroma/`
   - Unclassified chunks: emit owner-decision row in plan
6. **Estimate regen cost:** `total_chunks × avg_seconds_per_embed` (default 0.05s/embed for typical OpenAI/Azure embedding APIs) → walltime estimate. Token cost estimate: `total_chunks × avg_tokens_per_chunk` (default 256). Both are estimates; actual cost varies by content.
7. **Emit plan + summary.**

## 4. Output Layout

```
{output_dir}/chromadb_regen/
├── chromadb-regen-plan.json      # main artifact (machine-readable plan)
├── chromadb-regen-preview.md     # markdown summary for owner review
└── result.json                   # standard sub-script result per Wave 2 -003 §4.2
```

## 5. Schemas

### 5.1 `chromadb-regen-plan.json`

```json
{
  "schema_version": 1,
  "generated_at": "ISO timestamp",
  "source_chromadb_path": "E:/GT-KB/.groundtruth-chroma",
  "source_chromadb_exists": true,
  "collections": [
    {
      "name": "deliberations",
      "id": "a44b3005-eddf-4379-8f2b-e59f5fb8060c",
      "vector_count": 6990,
      "metadata_schema_sample": ["source_id", "source_type", "chunk_index", "session_id"],
      "embedding_dim_sample": 1536,
      "framework_chunk_count": 421,
      "adopter_chunk_count": 1832,
      "unclassified_chunk_count": 4737,
      "partition_source": "membase_export/partition_manifest.json"
    }
  ],
  "regen_plan": {
    "adopter_target_path": "applications/Agent_Red/.groundtruth-chroma",
    "framework_target_path": ".groundtruth-chroma",
    "regen_per_collection": [
      {
        "collection_name": "deliberations",
        "adopter_chunk_count": 1832,
        "framework_chunk_count": 421,
        "unclassified_chunk_count": 4737,
        "estimated_walltime_seconds": 350,
        "estimated_token_cost": 1789440
      }
    ],
    "total_estimated_walltime_seconds": 350,
    "total_estimated_token_cost": 1789440
  },
  "warnings": []
}
```

### 5.2 `chromadb-regen-preview.md` shape

```markdown
# ChromaDB Regeneration Plan

Generated: <ISO timestamp>
Source: GTKB-ISOLATION-016 Phase 8 rehearsal `_chromadb_regen.py` (Slice 10).

## Summary

- ChromaDB store: `E:/GT-KB/.groundtruth-chroma` (exists)
- Collections: 1
- Total vectors: 6,990
- Estimated regen walltime: ~6 minutes
- Estimated regen token cost: ~1.8M tokens

## Per-Collection Plan

### Collection `deliberations` (UUID a44b3005-...)

- Total chunks: 6,990
- Framework: 421 → regenerate at `<gt-kb-root>/.groundtruth-chroma`
- Adopter: 1,832 → regenerate at `applications/Agent_Red/.groundtruth-chroma`
- Unclassified: 4,737 → owner decision required (default: regenerate at adopter side per §2 fallback)

## Cutover Procedure (informational; ISOLATION-018 executes)

1. After cutover, run `groundtruth-kb-regen-chromadb --collection deliberations --partition-from {membase_export}/partition_manifest.json --target-root applications/Agent_Red`.
2. Smoke-check: `chromadb` peek at new path returns expected vector counts.
3. Acceptance gate: framework + adopter chunk counts match the plan ±0.1%.

## Owner Decisions Required

- Disposition of `unclassified` chunks (4,737): regenerate at adopter side (default), framework side, or skip.
- Whether to preserve original Chroma collection IDs (UUIDs) at the target, or generate fresh UUIDs (which breaks any external references).
```

## 6. Common Contract Compliance

- §4.1 signature: `def run(manifest, output_dir, *, dry_run=False, chroma_path=None, partition_manifest_path=None) -> dict` — ✓
- §4.2 output layout: under `{output_dir}/chromadb_regen/`; includes `result.json` — ✓
- §4.3 idempotency: re-runs overwrite — ✓
- §4.4 read-only on LEGACY_ROOT (read-only ChromaDB access; never `add`/`update`/`delete`) — ✓
- §4.5 driver dispatch: already wired (table index 4) — ✓
- `_emit_result()` from `_split_helper.py` wraps non-dry-run returns — ✓

`chroma_path=` and `partition_manifest_path=` parameters follow Slice 5/6/7/8/9 fixture-root pattern.

## 7. Test Plan

`tests/scripts/test_rehearse_chromadb_regen.py` (new; ~12-14 tests).

Mocking strategy:
- `chroma_path=` parameter overrides ChromaDB location for fixture trees
- `partition_manifest_path=` parameter overrides Slice 8 cross-reference path
- Tests use a real `chromadb.PersistentClient` against a `tmp_path` fixture (small synthetic collection with 5-10 vectors). Avoids embedding API calls (uses `Settings(anonymized_telemetry=False, allow_reset=False)`).

Test list:

| # | Test | Coverage |
|---|---|---|
| 1 | `test_run_dry_run_returns_skipped` | Common contract dry_run |
| 2 | `test_run_emits_warning_when_chromadb_absent` | Edge: no ChromaDB to migrate |
| 3 | `test_run_inventories_collection_metrics` | §3 step 2 |
| 4 | `test_run_samples_metadata_schema_via_peek` | §3 step 3 — peek only, not full iterate |
| 5 | `test_run_does_not_call_collection_add_or_update_or_delete` | **Safety regression guard:** monkeypatch chromadb client; assert no write methods called |
| 6 | `test_run_cross_references_partition_manifest_when_present` | §3 step 4 |
| 7 | `test_run_falls_back_to_id_prefix_when_partition_manifest_absent` | §2.2 fallback |
| 8 | `test_run_classifies_chunks_by_source_id_prefix` | `_split_helper.classify_by_id_prefix` reuse |
| 9 | `test_run_handles_missing_source_id_metadata_field` | Edge: chunk without `source_id` → unclassified |
| 10 | `test_run_emits_regen_plan_with_per_collection_costs` | §3 step 6 |
| 11 | `test_run_emits_walltime_and_token_estimates` | §5.1 |
| 12 | `test_run_writes_chromadb_regen_plan_json` | §5.1 |
| 13 | `test_run_writes_preview_markdown` | §5.2 |
| 14 | `test_run_writes_result_json_on_ok_path` | Slice 4 -006 F2 |
| 15 | `test_run_writes_result_json_on_error_path` | Error path forensics |
| 16 | `test_run_returns_error_when_chromadb_open_fails` | Connection failure |

Plus 1 driver integration test: advance the missing-lane fixture per Stage B/C GO ordering.

## 8. Files Changed (this slice's commit)

### 8.1 NEW
- `scripts/rehearse/_chromadb_regen.py` — ~200 LOC (probe + read-only enumerate + plan + estimate)
- `tests/scripts/test_rehearse_chromadb_regen.py` — ~400 LOC (~16 tests + chromadb fixture)
- `bridge/gtkb-isolation-016-phase8-wave2-slice10-001.md` (this file)

### 8.2 MODIFIED
- `bridge/INDEX.md` — new slice10 entry at top
- `tests/scripts/test_rehearse_isolation.py` — fixture advances per Stage B/C GO ordering

### 8.3 UNTOUCHED
- `scripts/rehearse_isolation.py`, `_common.py`, `_inventory.py`, `_path_rewrite.py`, `_split_helper.py`, `_bridge_split.py`, `_backlog_split.py`, `_release_readiness_split.py`
- All other Slice 1-9 tests
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`
- `.groundtruth-chroma/` (read-only access; no writes)

## 9. Out of Scope

- Stage B sibling lanes: `_ci_inventory.py` (Slice 7), `_membase_export.py` (Slice 8), `_production_effects.py` (Slice 9) — separate parallel slices.
- Stage C sibling: `_dashboard_regen.py` (Slice 11) — separate parallel slice.
- Stage D: `_rollback.py` (Slice 12) — composes other lanes' outputs; deferred.
- Actual ChromaDB regeneration — that's ISOLATION-018 cutover work; this slice produces only the plan.
- Embedding API invocations — strictly avoided; cost estimates are derived from chunk counts, not actual API calls.
- ChromaDB write operations of any kind — strictly forbidden.
- Chroma collection-ID preservation policy — surfaced in preview markdown as owner decision, not pre-decided here.
- Resolving `unclassified` chunks — surfaced as owner decision in preview.

## 10. Codex Review Asks

1. Confirm the read-only access pattern (`PersistentClient` + `peek()` + `count()`, never `add/update/delete`) is sufficient. Test 5 is the regression guard. Alternative: open ChromaDB SQLite backing directly with `sqlite3.connect(uri='file:...?mode=ro', uri=True)` to make read-only physical, not just by-convention. Tradeoff: bypasses Chroma's metadata schema.
2. Confirm the §2.2 cross-reference pattern (Slice 8 partition manifest is optional, ID-prefix fallback when absent) is right vs. requiring Slice 8 first (which would force ordering and break umbrella -004 "any order"). My read: optional cross-ref preserves independence.
3. Confirm the §3 step 6 cost estimate (chunks × per-embed walltime + tokens) is the right level of estimation, vs. probing the actual embedding model config from ChromaDB metadata.
4. Confirm the unclassified-chunks default (regenerate at adopter side) is right, vs. defaulting to skip + owner decision.
5. Confirm the preview markdown's "Cutover Procedure" section (lines naming a hypothetical `groundtruth-kb-regen-chromadb` CLI) is appropriately scoped — the actual command name is whatever ISOLATION-018 implements; this slice describes the procedure shape, not the literal command.
6. **GO / NO-GO** on Slice 10.

## 11. Decision Needed From Owner

None.

(The unclassified-chunk disposition default is a design choice surfaced in the preview, not a session-wrap owner decision.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
