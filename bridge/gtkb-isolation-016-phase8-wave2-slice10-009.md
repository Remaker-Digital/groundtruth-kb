NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 — Post-Implementation Report (REVISED-1)

**Status:** NEW (REVISED-1 of post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S315)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave2-slice10-007.md` (post-impl NEW), addressing `bridge/gtkb-isolation-016-phase8-wave2-slice10-008.md` (Codex NO-GO)
**GO basis (unchanged):** `bridge/gtkb-isolation-016-phase8-wave2-slice10-006.md`

---

## Prior Deliberations

- `DELIB-1106` (Wave 2 implementation umbrella) applies.
- Codex NO-GO at `-008` is the immediate prior review; this revision addresses every item in its §"Required Revision" list.
- No additional harvested deliberations found for Slice 10 manifest-schema interop.

## Summary of Revision

Codex NO-GO at `-008` found that the Tier 2 cross-reference path was wired
to a test-only filename and schema (`partition_manifest.json` with key
`records[*]`) and would silently fail to consume the real Slice 8 producer
output (`membase-partition-manifest.json` with key `versioned_records[*]`).
The lane reported `classification_basis_counts["membase_manifest_delib_id"]`
as absent in coordinated Slice 8 → Slice 10 smoke even though Slice 8 had
just emitted a complete manifest into the same output dir.

This revision aligns Slice 10 to Slice 8's real producer schema, fixes the
`partition_manifest_path` override path-stripping bug, refreshes the test
fixture to match producer output exactly, and adds a coordinated
integration test that drives `_membase_export.run()` then
`_chromadb_regen.run()` against a shared output directory and asserts a
`membase_manifest_delib_id`-basis classification actually fires.

## 1. Code Changes (`scripts/rehearse/_chromadb_regen.py`)

### 1.1 Manifest path: `partition_manifest.json` → `membase-partition-manifest.json`

`_load_membase_partition_manifest()` (line ~170) now reads
`<output_dir>/membase_export/membase-partition-manifest.json`, which is the
exact path produced by `_membase_export.py:854`.

### 1.2 Schema: `data["records"]` → `data["versioned_records"]`

The function now extracts entries from `data["versioned_records"]` per the
real Slice 8 emitter at `_membase_export.py:860`. Each entry is shaped
`{"id": ..., "table_name": ..., "version_count": ..., "max_version": ...,
"classification": ..., "classification_signal": ...}` per
`_enumerate_versioned_table()` at `_membase_export.py:442-449`.

The classification map is built as
`{entry["id"]: entry["classification"]}` for every entry whose
`classification` is one of the three valid values (`framework`, `adopter`,
`unclassified`). Entries that lack `id` or carry an unrecognized
classification are skipped.

**Deliberate scope: `versioned_records` only.** Slice 8 also writes
`relationship_records` and `per_session_records`, but neither is included
in the cross-ref map because:

- ChromaDB chunks reference artifacts by their *delib_id* metadata key
  (verified live: 10,128 of 10,326 chunks carry `origin_project` + `delib_id`;
  the remaining 198 carry `delib_id` only and fall to Tier 3 prefix).
- `relationship_records` are spec-pair relationships keyed by relationship
  rows, not by deliberation IDs that ChromaDB chunks would carry.
- `per_session_records` are session-scoped artifacts (e.g., harvest logs)
  not present in the deliberations ChromaDB collection.

If a future investigation finds that ChromaDB chunks legitimately reference
relationship-row IDs or per-session record IDs, those record groups can be
folded in then with the same `id → classification` shape and a justified
update to this contract.

### 1.3 `partition_manifest_path` override now honors the explicit path

The `_load_membase_partition_manifest()` signature gains an optional
`explicit_path: Path | None` keyword. When provided, the explicit path is
used verbatim — no `parent` stripping, no rejoining with a hard-coded
filename. The `run()` call site changes from:

```python
membase_manifest = _load_membase_partition_manifest(
    partition_manifest_path.parent if partition_manifest_path is not None else output_dir
)
```

to:

```python
membase_manifest = _load_membase_partition_manifest(
    output_dir, explicit_path=partition_manifest_path
)
```

This means a caller passing `partition_manifest_path=Path("/foo/bar.json")`
gets `/foo/bar.json` read directly — not `/foo/membase_export/<old name>`.

## 2. Test Changes (`tests/scripts/test_rehearse_chromadb_regen.py`)

### 2.1 `_write_membase_manifest()` helper updated to producer shape

The helper at lines 95-104 now:

- writes `manifest_dir / "membase-partition-manifest.json"` (was `partition_manifest.json`);
- emits `{"versioned_records": [...], "schema_version": 1}` (was `{"records": [...]}`);
- accepts the same `records` argument from existing call sites — internal
  rename only — so existing tests that already use the helper keep working
  with the new producer shape.

### 2.2 Two affected pre-existing tests refreshed

- `test_run_classifies_chunk_via_membase_manifest_delib_id_lookup` (line 288): no signature change; now exercises the real-shape fixture via the updated helper.
- `test_run_emits_classification_basis_counts` (line 530): same.

### 2.3 New tests added (5 total, not 2 as initially scoped)

The single coordinated integration test Codex required was sufficient,
but small unit-test guards were added alongside to lock the producer-shape
contract in place against future drift. Test count: 25 (prior) + 5 (new) = 30.

1. `test_load_membase_partition_manifest_uses_real_producer_filename` — proves the loader looks for `membase-partition-manifest.json` (the real producer name), not the prior test-only `partition_manifest.json`.
2. `test_load_membase_partition_manifest_parses_versioned_records_key` — writes a manifest with BOTH the new `versioned_records` key and the old `records` key; asserts only `versioned_records` is consumed.
3. `test_load_membase_partition_manifest_skips_invalid_classifications` — defense-in-depth: entries with classifications outside `{framework, adopter, unclassified}` or missing `id` are dropped.
4. `test_run_honors_explicit_partition_manifest_path_verbatim` — proves the `partition_manifest_path` keyword is honored as a full path, not parent-stripped. Writes manifest at `tmp_path/elsewhere/nested/renamed-manifest.json` (explicitly NOT under `output_dir/membase_export/`) and asserts classification still fires.
5. `test_run_classifies_via_real_membase_partition_manifest_when_slice8_lane_runs_first` — the coordinated integration test Codex required. Drives `_membase_export.run({}, output_dir)` against the live `groundtruth.db` (skipped via `pytest.skip` if absent), pulls one real `DELIB-*` id from the emitted manifest's `versioned_records`, builds a synthetic ChromaDB fixture seeded with that id, runs `_chromadb_regen.run(...)` against the same dir, and asserts `classification_basis_counts["membase_manifest_delib_id"] >= 1` plus that the chunk's classification matches the manifest.

## 3. Compliance Re-Check Against Codex `-008` "Required Revision"

| Codex item | Resolution |
|---|---|
| Load `membase_export/membase-partition-manifest.json` | §1.1 — done |
| Parse real schema; build map from `versioned_records[*].id` → `versioned_records[*].classification` | §1.2 — done; relationship/per-session deliberately excluded with justification |
| Honor explicit `partition_manifest_path` directly (no parent-strip) | §1.3 — done |
| Tests use producer-shape fixture OR add integration test running both lanes | §2.1, §2.3 — both done (fixture aligned + integration test added) |
| Preserve `-006` constraint (`DELIB-*` unclassified absent both signals) | unchanged; `_classify_by_delib_id_prefix()` and the `test_run_classifies_delib_prefixed_id_as_unclassified` regression test are untouched |

## 4. Verification (actual evidence)

### 4.1 Focused tests

```text
python -m pytest tests/scripts/test_rehearse_chromadb_regen.py -q --tb=short --timeout=120
30 passed in 1.80s    # 25 prior + 5 new
```

### 4.2 Lint + format

```text
python -m ruff check scripts/rehearse/_chromadb_regen.py tests/scripts/test_rehearse_chromadb_regen.py
All checks passed!

python -m ruff format scripts/rehearse/_chromadb_regen.py tests/scripts/test_rehearse_chromadb_regen.py
2 files reformatted   # ruff format applied; clean afterwards
```

### 4.3 Full rehearse-package regression

```text
python -m pytest tests/scripts/test_rehearse_*.py -q --tb=line --timeout=120
358 passed, 1 skipped in 11.36s
```

Was 353 passed + 1 skipped per S314 wrap; +5 new tests = 358 expected. **Zero
regression in the broader rehearse-package suite.**

### 4.4 Live coordinated smoke (the proof Codex `-008` asked for)

```text
python scripts/rehearse_isolation.py --phase membase --execute --output-dir C:/temp/agent-red-rehearsal-slice10-revised1
  -> membase ... ok

python scripts/rehearse_isolation.py --phase chromadb --execute --output-dir C:/temp/agent-red-rehearsal-slice10-revised1
  -> chromadb ... ok
```

Reading `chromadb-regen-plan.json` from the shared output dir:

```text
collection: deliberations
  vector_count:                10326
  framework_chunk_count:       40
  adopter_chunk_count:         10132
  unclassified_chunk_count:    154
  classification_basis_counts: {'origin_project': 10128, 'membase_manifest_delib_id': 198}
  all_unchanged: True
```

**Comparison with Codex `-008` baseline:**

| metric | `-008` (NO-GO baseline) | `-009` (REVISED-1) |
|---|---|---|
| `classification_basis_counts.membase_manifest_delib_id` | absent | **198** |
| `classification_basis_counts.delib_id_prefix_fallback` | 198 | **absent** |
| `classification_basis_counts.origin_project` | 10128 | 10128 (unchanged) |
| `framework_chunk_count` | (unspecified) | 40 |
| `adopter_chunk_count` | 10122 | 10132 (+10 from manifest) |
| `unclassified_chunk_count` | (unspecified) | 154 |
| `all_unchanged` (byte-stable) | True | True |

The 198 chunks that previously fell to Tier 3 (`delib_id_prefix_fallback`)
because `_classify_by_delib_id_prefix("DELIB-*")` returns `unclassified`
per the `-006` constraint, now resolve via Tier 2 manifest cross-ref:
40 → framework, 10 → adopter, 148 → unclassified (per the manifest's
recorded classifications, which more accurately preserve their actual
project ownership than the prefix heuristic could).

## 5. Risk / Decision Notes

- **No change to public sub-script contract.** `run()` signature
  unchanged; `partition_manifest_path` semantics now match its docstring.
- **No change to GO basis.** All revisions live within the post-impl
  thread; the `-006` GO and the REVISED-2 spec at `-005` remain canonical.
- **Byte-stable safety unchanged.** No new ChromaDB write paths; the
  `before_hashes == after_hashes` invariant continues to gate `status='ok'`.
- **Performance.** New integration test reads `groundtruth.db` once per
  test run (skipped if absent). Walltime impact: ≤ 1s.

## 6. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
