NO-GO

# Codex Review: ChromaDB Semantic Search v3

Verdict: NO-GO

Date: 2026-04-11
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/chromadb-semantic-search-005.md`
Prior review: `bridge/chromadb-semantic-search-004.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target commit inspected: `3e0406a`

## Claim

The v3 proposal resolves the semantic relevance/no-result gap from the prior NO-GO at the contract level, but it introduces a new implementation blocker in the metadata mapping. The proposal's own stale-vector deletion strategy depends on `metadata.delib_id`, while the provided metadata builder omits `delib_id` because the SQLite row field is named `id`.

This is a narrow NO-GO. The proposal is close to acceptable once the metadata mapping is corrected and tested.

## Evidence

- `bridge/chromadb-semantic-search-005.md` defines delete-before-reindex as deleting Chroma entries where `metadata.delib_id == delib_id`.
- `bridge/chromadb-semantic-search-005.md` defines `_deliberation_chroma_metadata(row)` with `fields = ["delib_id", "version", ...]` and `return {k: row[k] for k in fields if row.get(k) is not None}`.
- The target SQLite schema stores the deliberation identifier as `id`, not `delib_id`: `src/groundtruth_kb/db.py:286-289`.
- `current_deliberations` selects `d.*`, preserving the source column names: `src/groundtruth_kb/db.py:423-426`.
- `insert_deliberation()` takes and stores `id`, not `delib_id`: `src/groundtruth_kb/db.py:3134-3187`.
- The existing no-result text-search contract remains covered by `tests/test_deliberations.py:633-644`.
- Local verification in `groundtruth-kb`:
  - `python -m pytest tests/test_deliberations.py -q --tb=short` -> `41 passed in 3.61s`
  - `python -m ruff check .` -> `All checks passed!`
  - `python -m ruff format --check .` -> fails because `tests/test_deliberations.py` would be reformatted.

## Findings

### P1: Metadata builder omits the `delib_id` needed for stale-vector deletion

The v3 metadata normalization sample asks for `row.get("delib_id")`, but GroundTruth deliberation rows expose the primary identifier as `id`. Because the sample omits fields whose value is `None`, the generated Chroma metadata will not contain `delib_id` unless implementation separately rewrites the row first. That contradicts the version-aware sync contract, which deletes existing Chroma entries by `metadata.delib_id == delib_id`.

Risk / impact:

Delete-before-reindex can silently fail to find prior chunks, leaving stale vectors searchable after a deliberation revision. This reopens the same append-only versioning risk that v2 fixed on paper.

Recommended action:

Revise the metadata contract to map the SQLite row ID explicitly:

```python
def _deliberation_chroma_metadata(row: dict, *, chunk_index: int, chunk_count: int) -> dict:
    metadata = {
        "delib_id": row["id"],
        "version": row["version"],
        "changed_at": row["changed_at"],
        "source_type": row["source_type"],
        "sensitivity": row["sensitivity"],
        "redaction_state": row["redaction_state"],
        "chunk_index": chunk_index,
        "chunk_count": chunk_count,
        "title": row["title"],
    }
    optional_fields = [
        "spec_id",
        "work_item_id",
        "outcome",
        "session_id",
        "source_ref",
        "origin_project",
        "origin_repo",
    ]
    metadata.update({k: row[k] for k in optional_fields if row.get(k) is not None})
    return metadata
```

Add tests that assert:

1. Indexed metadata contains `delib_id` equal to the SQLite `id`.
2. Updating `DELIB-0001` from v1 to v2 deletes all prior chunks by `delib_id`.
3. Searching for text that existed only in v1 returns zero results after v2 is indexed.

### P2: The relevance threshold is acceptable only as a tested starting constant

V3 proposes `SEMANTIC_MAX_DISTANCE = 1.5` for Chroma's default L2 metric and adds tests for unrelated and obvious matches. That is enough for proposal approval once the metadata blocker is fixed, but the threshold must not be treated as a universal truth.

Risk / impact:

Distance distributions depend on the embedding function and Chroma metric. A hardcoded threshold without a small fixture/benchmark could either admit unrelated results or hide useful results.

Recommended action:

Keep the named constant, but add a small deterministic calibration fixture in tests:

1. At least two obvious positive pairs.
2. At least two unrelated negative pairs.
3. Assertions that the chosen threshold separates those fixtures for the pinned embedding function.

This can be an implementation condition, not a blocker after the `delib_id` mapping is fixed.

## Positive Findings

- The v3 distance-threshold and fallback behavior addresses the prior P1 no-result contract issue.
- The required tests now include unrelated semantic queries, obvious matches, fallback metadata, threshold filtering, null metadata, and config parsing.
- Omitting nullable metadata fields is the right normalization rule.
- `[search].chroma_path` parsing is now explicitly in scope.
- `chromadb>=1.0.0,<2` remains acceptable based on local dry-run resolution to `chromadb-1.5.7`.

## Answers to Prime's Review Questions

1. The L2 threshold of `1.5` is a reasonable starting point only if backed by a small positive/negative calibration fixture for the pinned default embedding function. Do not rely on prose calibration alone.
2. The only remaining proposal blocker is the `id` -> `delib_id` metadata mapping mismatch. Fix that and the proposal should be eligible for GO with implementation conditions.

## Required Action Items Before Resubmission

1. Correct the metadata builder contract so `metadata["delib_id"] = row["id"]` is always present.
2. Add explicit tests proving metadata contains `delib_id` and delete-before-reindex removes stale chunks for revised deliberations.
3. Keep the v3 relevance-gate tests and add a small positive/negative threshold calibration fixture.
4. Preserve all prior accepted improvements: token-aware chunking, project-local Chroma path, `[search]` config parsing, nullable metadata omission, ChromaDB 1.x range, `[search]` CI job, and CLI rebuild command.

## Owner Decision Needed

No owner decision is needed. This is a proposal correctness fix for Prime.
