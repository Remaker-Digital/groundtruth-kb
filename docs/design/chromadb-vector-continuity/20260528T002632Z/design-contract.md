# Design Contract — HIST-DELIB-NNNN ChromaDB Backfill

**Investigation run:** 20260528T002632Z
**Bridge thread:** `gtkb-chromadb-vector-continuity-v1-cut-scoping`
**Work item:** WI-3395
**Status:** design contract; candidate requirement pending owner-approved spec intake per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

## 1. Scope

This contract specifies the behavior of a one-time HIST-DELIB-NNNN backfill script that preserves ChromaDB semantic-search continuity across the proposed v1.0 identifier-reset cut. The contract is design-level; no implementation code is created by this slice.

## 2. Identifier Convention

**Pre-cut DELIB IDs** retain their canonical form: `DELIB-NNNN` (numeric four-digit) or `DELIB-SNNN-<TOPIC>-<DATE>` (session-prefixed descriptive).

**Post-cut canonical DELIB IDs** restart from a chosen starting point (per S347 Option A; concrete starting point is an owner decision not part of this contract).

**Historical preservation IDs:** every pre-cut DELIB ID becomes `HIST-<original-id>` in the post-cut ChromaDB substrate. Examples:
- `DELIB-0001` → `HIST-DELIB-0001`
- `DELIB-S347-V1-RELEASE-STRATEGY-CHOICES-2026-05-13` → `HIST-DELIB-S347-V1-RELEASE-STRATEGY-CHOICES-2026-05-13`

**Rationale for the `HIST-` prefix** (over alternatives like `LEGACY-`, `PRE-V1-`, or `Y2026Q2-`):
- 4-character prefix; predictable string length addition.
- "HIST" is monosyllabic, universally readable.
- Distinct from `DELIB-`, `SPEC-`, `WI-`, `ADR-`, `DCL-`, `GOV-`, `PB-` — no collision with current identifier prefixes.
- Mirrors S347 §8.4's textual translation manifest convention if the manifest also adopts `HIST-` prefixing.

## 3. Backfill Script Contract

### Inputs

- **Source ChromaDB store:** the pre-cut `.groundtruth-chroma/` (read-only access).
- **Source MemBase deliberations table:** the pre-cut `groundtruth.db` `deliberations` table (read-only access).
- **Target ChromaDB store:** the post-cut `.groundtruth-chroma/` (write access — newly initialized at v1.0 cut).
- **Configuration:**
  - `--dry-run` (no writes; emit a summary of what would be written).
  - `--verbose` (per-chunk log).
  - `--limit N` (process only N chunks; for testing).
  - `--source-chroma <path>` (override default source path).
  - `--target-chroma <path>` (override default target path).
  - `--embedding-model-version-pin <model-id>` (assert that the source store was indexed with the same embedding model as the target, refusing to proceed on mismatch).

### Outputs

- **HIST-prefixed chunks in the post-cut ChromaDB store**, one chunk per pre-cut chunk:
  - chunk ID: `HIST-<original-chunk-id>` (e.g., `HIST-DELIB-0003::v1::chunk-000`)
  - metadata `delib_id`: `HIST-<original-delib-id>` (e.g., `HIST-DELIB-0003`)
  - metadata `original_id`: original pre-cut DELIB ID for audit (NEW field)
  - metadata `backfilled_at`: UTC timestamp of backfill run
  - metadata `backfill_source_run_id`: unique ID for the backfill run
  - all other metadata fields: copied verbatim from source
  - embedding vector: copied verbatim from source (no re-embedding required; assumes embedding model version matches)
- **Backfill manifest file:** `.gtkb-state/chromadb-backfill/<run_id>/manifest.json`
  - schema_version, run_id, started_at, ended_at, source_chunk_count, target_chunk_count, embedding_model_version_pin, mode (dry-run/live), exit_status.
- **Per-chunk log file:** `.gtkb-state/chromadb-backfill/<run_id>/chunks.jsonl` (if `--verbose`)
  - one line per source chunk: `{src_id, target_id, status: written|skipped|error, error?}`.

### Operation Semantics

- **Idempotent:** re-running the backfill against a target store that already has HIST-prefixed entries skips existing target IDs without error and records skips in the chunks.jsonl log.
- **Resumable:** if interrupted, re-running picks up where it left off (using target-store ID existence as the resumption oracle).
- **Read-only against source:** the script must not write to the source ChromaDB store or source MemBase.
- **Single-collection:** operates on the `deliberations` collection only. Other collections (if any are added in the future) are not in scope unless the contract is extended.
- **Embedding-model parity required:** if the source ChromaDB embedding model differs from the target, the script must refuse to proceed with an explicit error citing the version mismatch. This prevents silent semantic drift between HIST- and current-era vectors.

## 4. Search API Behavior Post-Backfill

Three search modes are added to `KnowledgeDB.search_deliberations` and the `gt deliberations search` CLI:

### 4.1 Default mode (current behavior preserved)

`search_deliberations(query, limit=5)` and `gt deliberations search "..."` return BOTH HIST- and current results, ranked by semantic score.

- **Rationale:** the default is "all relevant history"; the caller doesn't have to think about HIST/current distinction.
- **Display convention:** HIST- entries are clearly marked in CLI output (e.g., `[HIST] [semantic score=0.95] HIST-DELIB-XXX...`).

### 4.2 Current-only mode

`search_deliberations(query, limit=5, scope="current")` and `gt deliberations search "..." --scope current` filter out HIST- entries.

- **Use case:** when explicitly working in the post-v1.0 cut context and the caller wants to avoid pre-cut precedent (e.g., when surveying current decisions only).

### 4.3 History-only mode

`search_deliberations(query, limit=5, scope="history")` and `gt deliberations search "..." --scope history` return only HIST- entries.

- **Use case:** audit, archaeology, and provenance research (e.g., "what was decided about X before v1.0?").

### 4.4 Storage of original IDs

For each HIST-prefixed result, the API should also surface the `original_id` metadata field. CLI output convention:
```
[HIST] [semantic score=0.95] HIST-DELIB-S347-... (orig: DELIB-S347-V1-RELEASE-STRATEGY-CHOICES-2026-05-13)
  v1: <title>
  <preview>
```

This lets a future human or agent map between the HIST identifier and the pre-cut canonical identifier without consulting the text translation manifest.

## 5. Rollback Story

The backfill is fully reversible. To undo:
1. Run `gt deliberations rollback-backfill --run-id <run_id>`.
2. The rollback removes every chunk whose `backfill_source_run_id` matches the run ID.
3. Source ChromaDB and source MemBase are untouched (they were read-only inputs); rollback leaves them in their pre-backfill state.

**Rollback does not require a separate script:** it's a method on the same backfill module that filters by `backfill_source_run_id` metadata for the target collection.

## 6. Verification Approach

The post-implementation verification for the BACKFILL IMPLEMENTATION (a follow-on bridge proposal, not this scoping) will:

1. **Embedding-count parity:** post-backfill target chunk count = pre-backfill target chunk count + source HIST-prefixed chunk count.
2. **Semantic-match preservation:** run a representative query set (e.g., 30 queries covering owner decisions, LO reviews, governance topics) against both pre-cut substrate and post-backfill HIST-scope substrate. The top-3 hits for each query, after ID normalization, should match.
3. **No MemBase mutation:** assert that `groundtruth.db` row counts and content hashes are unchanged.
4. **No source ChromaDB mutation:** assert that the source ChromaDB store's chunk count and IDs are unchanged.
5. **Search API integration:** assert that the three search modes (default/current-only/history-only) return correct subsets per a fixture-query test suite.

This verification approach is itself a candidate requirement; it would land as test specifications in the follow-on implementation slice.

## 7. Candidate Requirements (Pending Owner-Approved Spec Intake)

Per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`, the following are CANDIDATE requirements surfaced by this design — they remain candidates until an owner-approved chat-derived spec intake workflow promotes them:

- `CANDIDATE-SPEC-CHROMADB-VECTOR-CONTINUITY-001` — HIST- prefix convention.
- `CANDIDATE-SPEC-CHROMADB-BACKFILL-API-001` — backfill script's input/output/idempotency/rollback contract.
- `CANDIDATE-SPEC-DELIB-SEARCH-MODES-001` — default/current/history scope modes for `search_deliberations`.
- `CANDIDATE-SPEC-DELIB-ORIGINAL-ID-METADATA-001` — `original_id` metadata field convention.
- `CANDIDATE-SPEC-EMBEDDING-MODEL-PARITY-001` — embedding-model version pin requirement.

None of these candidates are formal SPECs until owner approval is captured per the standard chat-derived spec approval workflow.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
