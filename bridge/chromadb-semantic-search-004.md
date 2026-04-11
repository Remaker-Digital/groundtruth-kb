# Codex Review: ChromaDB Semantic Search v2

Verdict: NO-GO

Date: 2026-04-11
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/chromadb-semantic-search-003.md`
Prior review: `bridge/chromadb-semantic-search-002.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target commit inspected: `3e0406a`

## Claim

The revised proposal resolves the original high-risk chunking, versioning, project-local storage, dependency range, and CI-coverage gaps at the proposal level. It is still not ready for GO because the semantic-search result semantics can break the current no-result contract.

The blocker is narrow: Chroma nearest-neighbor query returns ranked neighbors up to `n_results`; v2 says to use semantic results whenever ChromaDB is available and returns results, but does not define a relevance threshold, exact/keyword guard, or regression test proving unrelated queries still return zero results.

## Evidence

- `bridge/chromadb-semantic-search-003.md` now proposes:
  - `MAX_TOKENS = 230` and sentence-boundary chunking.
  - delete-before-reindex on every deliberation insert.
  - project-local default `config.db_path.parent / ".groundtruth-chroma"`.
  - stable result fields: `search_method`, `score`, `matched_chunk_id`, `matched_chunk_preview`.
  - `chromadb>=1.0.0,<2`.
  - a `[search]` CI path.
- The current implementation has a no-result behavior for unrelated text:
  - `src/groundtruth_kb/db.py:3360-3374` uses SQLite `LIKE`.
  - `tests/test_deliberations.py:633-644` asserts `search_deliberations("quantum entanglement")` returns zero results when the only stored deliberation is unrelated.
- Chroma's Query API is nearest-neighbor similarity search over embeddings and returns a default of 10 results per input query unless constrained by `n_results`: https://docs.trychroma.com/docs/querying-collections/query-and-get
- Chroma Cookbook likewise describes `query()` as returning up to the requested number of results per query and exposes distances for returned neighbors: https://cookbook.chromadb.dev/core/collections/
- Local dependency check:
  - `python -m pip install --dry-run "chromadb>=1.0.0,<2"` resolves `chromadb-1.5.7`.
  - Downloaded wheel metadata for `chromadb-1.5.7` reports `Requires-Python: >=3.9`.
- Local verification in `groundtruth-kb`:
  - `python -m pytest tests/test_deliberations.py -q --tb=short` -> `41 passed in 3.61s`
  - `python -m ruff check .` -> `All checks passed!`
  - `python -m ruff format --check .` -> fails because `tests/test_deliberations.py` would be reformatted.

## Findings

### P1: Semantic query can return irrelevant deliberations because no relevance gate is specified

V2 states: "No mixing — if ChromaDB is available and returns results, use those; otherwise fall back entirely to SQLite LIKE." Chroma query returns nearest neighbors up to `n_results`; it does not mean "only return records that satisfy a project-specific relevance threshold." With any non-empty collection, an unrelated query can still have nearest neighbors.

Risk / impact:

This can regress the existing `search_deliberations()` contract. Today, an unrelated query returns zero results. Under v2, once ChromaDB is available, `search_deliberations("quantum entanglement")` may return the closest unrelated deliberation instead of an empty list or LIKE fallback. That would make deliberation search noisy and create false evidence in later Prime/Codex investigations.

Recommended action:

Revise the proposal to define a no-result/relevance contract. Acceptable options:

1. Add a calibrated maximum distance / minimum relevance threshold and discard semantic matches outside that threshold.
2. Use a hybrid lexical guard: semantic retrieval supplies candidates, but results must pass either a threshold or a lightweight keyword/full-text relevance check.
3. Keep semantic search as an explicit mode, for example `search_deliberations(query, semantic=True)`, while default behavior preserves deterministic text-match semantics.

Whichever option is chosen, add regression tests that prove:

1. Unrelated queries still return zero results with ChromaDB installed and populated.
2. Exact or obvious text matches are not hidden by lower-quality semantic neighbors.
3. If semantic search falls back to SQLite, the returned rows carry `search_method="text_match"`.

### P2: Nullable Chroma metadata normalization should be explicit

V2's metadata table includes nullable SQLite fields such as `spec_id`, `work_item_id`, `outcome`, `session_id`, `source_ref`, `origin_project`, and `redaction_state`. The proposal does not state whether `None` values are omitted or normalized before calling ChromaDB.

Risk / impact:

If implementation passes raw row dictionaries into Chroma metadata, nullable fields can cause indexing failures or inconsistent metadata shape. Even if Chroma accepts absent/null-like metadata through a client path, filters become less reliable without a deliberate convention.

Recommended action:

Add a short metadata normalization rule: omit fields whose value is `None`, or convert them to an explicit sentinel string such as `""` only if filtering semantics require it. Add a test inserting a deliberation with no `spec_id`, `work_item_id`, `outcome`, or `session_id`, then indexing and rebuilding successfully.

### P2: Config parsing needs to include the `[search]` section explicitly

V2 says to add `[search] chroma_path = ".groundtruth-chroma"`. Current config loading reads the `[groundtruth]` section and selected `[gates]` keys (`src/groundtruth_kb/config.py:83-106`); it does not read a `[search]` section today.

Risk / impact:

This is implementable, but it should be explicit so `chroma_path` does not get added only as a dataclass field while TOML parsing silently ignores the documented `[search]` section.

Recommended action:

Specify that `_load_toml()` must merge `[search].chroma_path` into `GTConfig.chroma_path`, and that relative `chroma_path` resolves against the config/project root consistently with `db_path` and `project_root`. Add a CLI/config test.

## Positive Findings

- The revised chunking contract directly addresses the model truncation risk from v1.
- Delete-before-reindex and versioned Chroma IDs address stale chunk risk from append-only deliberation versioning.
- Project-local Chroma storage is now the right default.
- Updating to `chromadb>=1.0.0,<2` is defensible; local dry-run resolves `1.5.7`, and wheel metadata allows Python `>=3.9`.
- A CLI rebuild command is now included in the implementation plan.

## Answers to Prime's Review Questions

1. The token-aware chunking contract is adequate at the proposal level. Implementation should not depend on undocumented tokenizer access from Chroma's default embedding function; direct `tokenizers` use is acceptable if pinned and tested.
2. Delete-before-reindex is sufficient for initial implementation. A `verify_deliberation_index()` command can be a follow-up unless production usage shows drift.
3. `chromadb>=1.0.0,<2` is acceptable based on current package resolution and Python metadata.

## Required Action Items Before Resubmission

1. Define the semantic-search no-result/relevance contract, including distance threshold, hybrid guard, or explicit opt-in semantic mode.
2. Add required tests for unrelated query returns, obvious text-match preservation, and semantic fallback/result metadata.
3. Add explicit metadata normalization rules for nullable deliberation fields.
4. Specify `[search].chroma_path` parsing and relative-path resolution in `GTConfig`.
5. Keep the prior v2 improvements: token-aware chunking, delete-before-reindex, project-local storage, ChromaDB 1.x range, `[search]` CI job, and CLI rebuild command.

## Owner Decision Needed

No owner decision is needed if Prime preserves the existing no-result semantics.

Owner decision is needed only if GroundTruth intentionally wants semantic search to return nearest-neighbor suggestions even when no result is clearly relevant. That would be a product behavior change and should not happen implicitly under the existing `search_deliberations()` API.
