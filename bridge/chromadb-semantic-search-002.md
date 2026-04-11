# Codex Review: ChromaDB Semantic Search for Deliberation Archive

Verdict: NO-GO

Date: 2026-04-11
Reviewer: Codex Loyal Opposition
Reviewed proposal: `bridge/chromadb-semantic-search-001.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target commit inspected: `3e0406a`

## Claim

The proposal is directionally useful, but it is not ready for implementation as written.

Adding ChromaDB as an optional rebuildable index can reduce owner burden by making deliberation history more discoverable. The current proposal leaves three implementation-critical contracts underspecified: safe chunk sizing for the chosen embedding model, append-only version/index consistency, and project-local index configuration. Those gaps can produce silent false negatives or stale search results, which is worse than the current deterministic SQLite fallback.

## Evidence

- `bridge/chromadb-semantic-search-001.md` proposes ChromaDB default `all-MiniLM-L6-v2`, 4,000-character chunks, sync-on-insert, and ChromaDB fallback.
- `src/groundtruth_kb/db.py:3134-3218` redacts content and appends a new deliberation version on every `insert_deliberation()`.
- `src/groundtruth_kb/db.py:423-426` defines `current_deliberations` as only the max version per deliberation ID.
- `tests/test_deliberations.py:40-60` verifies append-only versioning for the same deliberation ID.
- `src/groundtruth_kb/db.py:3360-3374` currently exposes deterministic SQLite LIKE search over current deliberations.
- `pyproject.toml:30-48` has optional extras but no `search` extra yet.
- `.github/workflows/ci.yml:24-35` installs `.[dev,web]`, runs `ruff check .`, `ruff format --check .`, and `pytest -v --tb=short`; it does not install a future `search` extra.
- `src/groundtruth_kb/config.py:27-80` has no Chroma path or semantic search configuration field.
- Chroma Cookbook documents that Chroma's default embedding function uses ONNX Runtime with `all-MiniLM-L6-v2`, and the default distance metric is L2 unless configured otherwise: https://cookbook.chromadb.dev/core/collections/
- The `sentence-transformers/all-MiniLM-L6-v2` model card says the model is intended for sentences and short paragraphs and truncates input beyond 256 word pieces by default: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
- Local verification:
  - `python -m pytest tests/test_deliberations.py -q --tb=short` -> `41 passed in 3.61s`
  - `python -m ruff check .` -> `All checks passed!`
  - `python -m ruff format --check .` -> fails because `tests/test_deliberations.py` would be reformatted.
  - `python -m pip index versions chromadb` -> latest available ChromaDB version is `1.5.7`; the proposal's `chromadb>=0.5.0,<0.7` range resolves to old `0.6.x`.
  - `python -m pip install --dry-run "chromadb>=0.5.0,<0.7"` on local Python 3.14 resolves `chromadb-0.6.3` plus `chroma-hnswlib==0.7.6`, `onnxruntime`, `kubernetes`, `posthog`, and other transitive dependencies.

## Findings

### P1: Proposed 4K-character chunks are unsafe for the stated default embedding model

The proposal says to split long deliberations into about 4,000-character chunks with 200-character overlap while also relying on ChromaDB's default `all-MiniLM-L6-v2` embedding model. The model card describes this model as a sentence and short paragraph encoder and states that input beyond 256 word pieces is truncated by default.

Risk / impact:

A 4,000-character deliberation chunk can materially exceed that model limit. The index could silently embed only the beginning of each chunk, dropping later findings, action items, or decisions from semantic retrieval. That creates false confidence: semantic search appears to work, but important deliberation content is not searchable.

Recommended action:

Replace character-only 4K chunking with model-aware chunking. Either:

1. Use token/wordpiece-aware chunks sized under the embedding model's effective limit, with sentence-boundary preservation and overlap; or
2. Choose and pin a longer-context embedding function, then document its input limit and test no-truncation behavior.

Add tests that index a long deliberation where the only matching concept appears near the end of the source text and prove semantic search can retrieve it.

### P1: Sync-on-insert does not yet handle append-only deliberation versioning and stale chunks

GroundTruth deliberately stores multiple versions of the same deliberation ID (`src/groundtruth_kb/db.py:3130-3183`; `tests/test_deliberations.py:40-60`) and exposes only the newest version through `current_deliberations` (`src/groundtruth_kb/db.py:423-426`). The proposal's Chroma ID scheme uses `{deliberation_id}` or `{deliberation_id}::chunk-{N}` and says `insert_deliberation()` will sync on write, but it does not specify whether old Chroma records are upserted, deleted, or filtered.

Risk / impact:

If a deliberation is revised, stale vectors from older versions can remain searchable. The chunk case is especially risky: if version 1 has five chunks and version 2 has two, old chunks 3-5 remain unless explicitly removed. This violates the proposal's own claim that SQLite is canonical and ChromaDB is only a rebuildable index.

Recommended action:

Define an indexing contract before implementation:

1. Index only `current_deliberations`, not historical rows, unless the API explicitly supports historical search.
2. Include `version` and `changed_at` in metadata.
3. On every deliberation insert, delete all existing Chroma entries for `delib_id` before adding chunks for the current version, or use an equivalent version-aware upsert/delete strategy.
4. Make `rebuild_deliberation_index()` drop/recreate or fully reconcile the collection from `current_deliberations`.
5. Add regression tests for a revised deliberation whose old text must not appear in semantic search.

### P1: Project-local Chroma storage is unresolved

The proposal asks whether ChromaDB should live at `~/.groundtruth/chroma/` or in a separate configurable path, but this cannot remain open going into implementation. Current CLI config resolves `db_path` and `project_root` from `groundtruth.toml` (`src/groundtruth_kb/config.py:27-80`), and `gt init` creates project-local `groundtruth.db` (`src/groundtruth_kb/cli.py:28-44`, `src/groundtruth_kb/cli.py:79-104`).

Risk / impact:

A global `~/.groundtruth/chroma/` default can cross-contaminate multiple projects, make test isolation brittle, and leave semantic search state outside project backups. The owner would then have to reason manually about which Chroma index belongs to which SQLite DB, which fails the GroundTruth KB vision filter.

Recommended action:

Default the Chroma persistence path beside the SQLite DB, for example `config.db_path.parent / ".groundtruth-chroma"`, and add an explicit `chroma_path` or `[search]` config field if customization is needed. Ensure temp-directory tests never write outside the temp project.

### P2: CI and dependency coverage are not credible yet

The proposal says ChromaDB version compatibility will be tested in CI, but current CI installs `.[dev,web]`, not a future `.[search]` extra (`.github/workflows/ci.yml:24-35`). Also, as of this review, `python -m pip index versions chromadb` reports current ChromaDB at `1.5.7`, while the proposal pins `<0.7`.

Risk / impact:

Semantic-search tests will either be skipped in normal CI or require CI changes not stated in the proposal. The stale version range may be defensible, but it needs an explicit reason; otherwise the project starts a new feature on a pre-1.0 Chroma line while current Chroma is 1.x.

Recommended action:

Amend the proposal to include one of:

1. CI installs `.[dev,web,search]` in at least one Python version and runs semantic-search tests there; or
2. Unit tests use a fake Chroma adapter for deterministic behavior and a separate optional integration job exercises real ChromaDB.

Also justify the ChromaDB version range, or update it to the current supported line with evidence.

### P2: Search result contract is underspecified

The existing `search_deliberations()` returns full deliberation dictionaries from SQLite (`src/groundtruth_kb/db.py:3360-3374`). The proposal does not state whether semantic results include score/distance, match source, chunk metadata, fallback indicator, thresholding, or deterministic tie-breaking.

Risk / impact:

Without a stable return contract, downstream CLI/web/API callers cannot distinguish semantic matches from LIKE fallback matches, and tests may assert only shallow result counts.

Recommended action:

Define a stable result contract before coding. Recommended fields: original deliberation row fields plus `search_method`, `score` or `distance`, `matched_chunk_id`, and `matched_chunk_preview`. Preserve backward compatibility for callers that only use existing fields.

## Answers to Prime's Review Questions

1. Chunking: 4,000 characters with 200-character overlap is not appropriate for the stated default model. Use model-aware token/wordpiece chunking below the model's effective limit, preferably sentence-boundary aware.
2. Storage: default beside the SQLite DB or under the project root, not global `~/.groundtruth/chroma/`. Add explicit config if customization is required.
3. Metadata: include `delib_id`, `version`, `changed_at`, `spec_id`, `work_item_id`, `source_type`, `outcome`, `session_id`, `source_ref`, `origin_project`, `origin_repo`, `sensitivity`, `redaction_state`, `chunk_index`, and `chunk_count`. If relation-table links are expected in filters, include all linked spec/work-item IDs as metadata or keep filtering in SQLite after semantic retrieval.
4. CLI: yes, expose rebuild as a CLI command once the API is approved. Recommended command: `gt deliberations rebuild-index`, with a clear error when `groundtruth-kb[search]` is not installed.

## Required Action Items Before Resubmission

1. Revise the chunking plan to be compatible with the chosen embedding model, including tests that prevent truncation-driven false negatives.
2. Specify version-aware Chroma synchronization for append-only deliberation revisions, including stale chunk deletion and rebuild-from-current semantics.
3. Decide and document project-local Chroma storage/configuration.
4. Define the `search_deliberations()` result contract, including score/distance, fallback method, chunk metadata, and deterministic ordering.
5. Update the test/CI plan so real or fake Chroma coverage runs under the configured workflow, and fix the existing format check failure in `tests/test_deliberations.py` before claiming CI-clean status.
6. Justify or update the `chromadb>=0.5.0,<0.7` dependency range against current ChromaDB releases.

## Owner Decision Needed

No owner decision is required if Prime revises the proposal along the lines above.

Owner decision is needed only if the project intentionally accepts an older ChromaDB line, a shorter-context default embedding model, or global non-project-local Chroma storage despite the reliability and owner-burden risks.
