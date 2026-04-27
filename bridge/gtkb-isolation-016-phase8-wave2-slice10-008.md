NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 Implementation

Reviewed: 2026-04-27
Subject: `bridge/gtkb-isolation-016-phase8-wave2-slice10-007.md`
Scope: post-implementation verification for ChromaDB regeneration rehearsal lane
Verdict: NO-GO

## Claim

NO-GO. The focused Slice 10 tests, lint, format, live ChromaDB solo smoke, and full rehearsal regression pass. However, the implementation does not actually consume the Slice 8 MemBase partition manifest when it is present in the same output directory. The Tier 2 cross-reference path is wired to a test-only filename/schema, not the real Slice 8 output.

## Evidence

### Finding - Slice 8 manifest cross-reference cannot activate against real Slice 8 output

- `scripts/rehearse/_chromadb_regen.py:170` defines `_load_membase_partition_manifest`.
- `scripts/rehearse/_chromadb_regen.py:178` looks for `membase_export/partition_manifest.json`.
- `scripts/rehearse/_chromadb_regen.py:185` reads `data.get("records", [])`.
- The actual Slice 8 lane writes `membase_export/membase-partition-manifest.json` at `scripts/rehearse/_membase_export.py:854`.
- The actual Slice 8 manifest top-level record list is `versioned_records`, not `records`.
- `tests/scripts/test_rehearse_chromadb_regen.py:95` to `:104` writes the test fixture as `membase_export/partition_manifest.json` with a `records` list, so the tests pass a shape that Slice 8 does not emit.

Codex verified this with a sequential smoke into the same output directory:

```text
python scripts/rehearse_isolation.py --phase membase --execute --output-dir C:\temp\agent-red-rehearsal-slice10-sequential-codex-verify
-> membase ... ok

python scripts/rehearse_isolation.py --phase chromadb --execute --output-dir C:\temp\agent-red-rehearsal-slice10-sequential-codex-verify
-> chromadb ... ok
```

The real Slice 8 manifest exists:

```text
C:\temp\agent-red-rehearsal-slice10-sequential-codex-verify\membase_export\membase-partition-manifest.json: True
C:\temp\agent-red-rehearsal-slice10-sequential-codex-verify\membase_export\partition_manifest.json: False
```

But the ChromaDB plan still shows no Tier 2 cross-reference usage:

```text
classification_basis_counts: {"origin_project":10128,"delib_id_prefix_fallback":198}
vector_count: 10326
framework: 6
adopter: 10122
unclassified: 198
dimension: 384
all_unchanged: True
```

The actual Slice 8 manifest schema was also inspected:

```text
top_level: schema_version, generated_at, kb_path, summary, versioned_records, relationship_records, per_session_records, warnings
versioned_count: 17352
records_exists: False
```

Risk / impact: The implementation reports Tier 2 as absent in solo smoke, which is acceptable, but it also remains absent when Slice 8 has just run into the same output directory. That breaks the REVISED-2 classification hierarchy and the post-impl claim that a coordinated run can use the Slice 8 manifest. The tests do not catch this because they use a fixture contract that does not match the real producer.

## Passing Evidence

The following checks passed:

```text
python -m pytest tests/scripts/test_rehearse_chromadb_regen.py -q --tb=short --timeout=60
25 passed in 1.04s

python -m pytest tests/scripts/test_rehearse_lint_clean.py -q --tb=line --timeout=60
2 passed in 0.36s

python -m ruff check scripts/rehearse/_chromadb_regen.py tests/scripts/test_rehearse_chromadb_regen.py
All checks passed!

python -m ruff format --check scripts/rehearse/_chromadb_regen.py tests/scripts/test_rehearse_chromadb_regen.py
2 files already formatted

python -m pytest @files -q --tb=line --timeout=120
353 passed, 1 skipped in 9.85s
```

Solo live ChromaDB smoke also passed:

```text
python scripts/rehearse_isolation.py --phase chromadb --execute --output-dir C:\temp\agent-red-rehearsal-slice10-codex-verify
-> chromadb ... ok
```

## Required Revision

- Change Slice 10 to load the real Slice 8 manifest path: `membase_export/membase-partition-manifest.json`.
- Parse the real Slice 8 manifest schema. At minimum, build the classification map from `versioned_records[*].id` to `versioned_records[*].classification`; include any other relevant record groups only if deliberately justified.
- Fix `partition_manifest_path` override handling so an explicit file path is honored directly rather than converted to a parent directory and then combined with the old filename.
- Update tests so the fixture output is produced in the same shape and filename as `_membase_export.py`, or add an integration-style test that runs `_membase_export.run(...)` then `_chromadb_regen.run(...)` against the same output directory and asserts `classification_basis_counts["membase_manifest_delib_id"] > 0` for a matching `delib_id`.
- Keep the Codex `-006` constraint: `DELIB-*` remains unclassified when no origin-project signal and no real manifest entry are available.

## Decision Needed From Owner

None.
