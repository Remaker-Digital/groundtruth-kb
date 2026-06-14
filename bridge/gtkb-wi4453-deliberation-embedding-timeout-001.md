NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4453-deliberation-embedding-timeout
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 37191790-3efe-4e97-a707-f8d798f7f238
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-8[1m]
Date: 2026-06-13 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4453
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4453: Bound the ChromaDB deliberation-index embedding step so record/propose cannot hang

## Summary

WI-4453 (P0 defect): `gt deliberations record`, `gt deliberations search`, and `gt bridge propose` can hang indefinitely on the ChromaDB embedding step. Investigation pinpoints the remaining unbounded path precisely:

- `KnowledgeDB._get_chroma_collection()` (`db.py` ~8062) calls `get_or_create_collection(...)` with **no explicit `embedding_function`**, so ChromaDB uses its `DefaultEmbeddingFunction` (ONNX all-MiniLM-L6-v2), which **downloads/loads a model on first embed**. When offline or the download stalls, that call blocks forever.
- The **search** path is already bounded (FAB-17 / HYG-048): `search_deliberations` (~8265) wraps `_chroma_query_matches` (the `collection.query` embed) in `_call_with_timeout(..., _CHROMA_QUERY_TIMEOUT_SECONDS)` and degrades to a SQLite LIKE fallback on `TimeoutError`.
- The **index/record** path is **NOT** bounded: `_index_deliberation_in_chroma` (~8193) calls `collection.add(ids=..., documents=..., metadatas=...)` (line ~8230) with no timeout. That `collection.add` triggers the same first-embed model load — so `gt deliberations record` (which writes the SQLite row, then indexes) and any `gt bridge propose` path that indexes a deliberation **hang** on the unbounded add.

This slice extends the **already-VERIFIED FAB-17 timeout pattern** to the index path: wrap the embedding-triggering `collection.add` in `_call_with_timeout` with a new, env-overridable `_CHROMA_INDEX_TIMEOUT_SECONDS`, and degrade gracefully on timeout. The deliberation's SQLite row is written separately by `insert_deliberation` (verified non-hanging), so on index timeout the **canonical DA record still persists** and only the disposable semantic index is deferred (rebuildable via the existing `rebuild_deliberation_index`). The result: record/propose return promptly instead of hanging, with no loss of canonical data.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4453 is the backlog authority for this fix (P0 reliability defect).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implementation proceeds under the active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1` (which includes WI-4453 and allows `source` + `test_addition`).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `gt bridge propose` is a load-bearing bridge-workflow surface; its deliberation-step hang undermines the protocol. The fix makes that surface resilient (it cannot hang on embedding) without altering bridge authority.
- **GOV-SOURCE-OF-TRUTH-FRESHNESS-001** — the Deliberation Archive (a freshness/source surface) must remain usable; degrading to a deferred-but-rebuildable index keeps the canonical SQLite DA record authoritative and intact.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH/project/work-item/target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked fix; degraded state (deferred index) is explicit and recoverable, not silently dropped.

## Requirement Sufficiency

Existing requirements sufficient. The FAB-17 search-timeout fix establishes the bounded-embedding pattern and the `_call_with_timeout` helper; this slice applies the same established contract to the index path. The bounded PAUTH (owner decision below) authorizes the source/test work. No new or revised formal specification is required.

## Prior Deliberations

- **`bridge/gtkb-fab-17-da-chroma-read-path` (VERIFIED, FAB-17 / HYG-048)** — bounded the deliberation **search** (query) path with `_call_with_timeout` + SQLite-LIKE degradation. This proposal extends the identical, proven pattern to the **index** path it did not cover. Primary precedent.
- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ decision (2026-06-13) admitting WI-4453 to PROJECT-GTKB-RELIABILITY-FIXES under the bounded PAUTH that authorizes this work.
- **`.claude/rules/deliberation-protocol.md`** — mandatory deliberation search before proposing/reviewing; WI-4453's hang directly impairs that governance workflow, so the fix restores its usability.
- _Live semantic deliberation search was not run during authoring: `gt deliberations search` / `search_deliberations` is the subject of this defect, and although FAB-17 bounds its query, the first-use model load remains a residual hang risk. Prior-decision context was gathered from the FAB-17 thread and the deliberation-protocol rule instead._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ approval (2026-06-13) admitting WI-4453 (and 8 sibling reliability WIs) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1` (allowed: `source`, `test_addition`; forbids formal-artifact mutation). This slice stays strictly within that scope: it edits `db.py` (source) + adds a test, performs no formal-artifact or KB mutation, and changes no bridge authority. No expanded owner authorization is requested.

## Design (Slice)

In `groundtruth-kb/src/groundtruth_kb/db.py`:

1. **New module constant** mirroring the FAB-17 query constants (~lines 89-90):
   `_CHROMA_INDEX_TIMEOUT_SECONDS = float(os.environ.get("GTKB_CHROMA_INDEX_TIMEOUT_SECONDS") or "15")`.
2. **Bound the index embed** in `_index_deliberation_in_chroma` (~8193): wrap the `collection.add(ids=..., documents=..., metadatas=...)` call (line ~8230) in the existing `_call_with_timeout(lambda: collection.add(...), _CHROMA_INDEX_TIMEOUT_SECONDS)`. On `TimeoutError`:
   - log a warning (mirroring the search path's degradation log),
   - return a degraded sentinel (e.g., `0` chunks indexed) indicating "semantic index deferred,"
   - do **not** raise — the caller (`gt deliberations record`, the index-on-record path) completes; the canonical SQLite row written by `insert_deliberation` is untouched and authoritative; the semantic index can be rebuilt via the existing `rebuild_deliberation_index`.
3. **Close the first-use model-load gap defensively:** ensure the model-materializing work runs *inside* the timeout boundary. `collection.add` is where the default embedding function first loads the model on the index path, so wrapping the `add` covers it. (The acquisition `_get_chroma_collection()` returns a collection handle without embedding; no model load occurs there.)
4. **Optional hardening (same slice, if low-risk):** apply the same bounded-add to the per-record loop inside `rebuild_deliberation_index` so an offline rebuild degrades per-record instead of hanging on the first record. Kept minimal; primary fix is the record/propose hot path.

No change to the search path (already FAB-17-bounded), no change to `insert_deliberation`, no schema change, no bridge-authority change.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py`) | Method |
|---|---|---|
| Index add cannot hang (GOV-FILE-BRIDGE-AUTHORITY-001, WI-4453) | `test_index_add_times_out_and_degrades` | monkeypatch the collection so `.add` sleeps > timeout → assert `_index_deliberation_in_chroma` returns within ~timeout (degraded sentinel), does NOT hang |
| Canonical DA row preserved on index timeout (GOV-SOURCE-OF-TRUTH-FRESHNESS-001) | `test_sqlite_row_intact_after_index_timeout` | after an index timeout, assert `get_deliberation(id)` still returns the row (insert_deliberation unaffected) |
| Timeout is env-overridable | `test_index_timeout_env_override` | set `GTKB_CHROMA_INDEX_TIMEOUT_SECONDS` low → assert the degraded path triggers at the configured bound |
| Normal (fast) index path unchanged | `test_fast_index_path_still_indexes` | a fast stub `.add` → assert `_index_deliberation_in_chroma` returns the real chunk count |
| Search path regression guard (FAB-17 preserved) | `test_search_still_bounded` | confirm the existing search-timeout/degradation behavior is unchanged by this edit |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py -q --tb=short`.

## Risk / Rollback

- **Risk: low.** The change is localized to `_index_deliberation_in_chroma` + two module constants, and **reuses the already-VERIFIED `_call_with_timeout` helper** and degradation idiom from the search path. It cannot lose canonical data — the SQLite DA row is written independently and the only degraded artifact is the disposable, rebuildable ChromaDB index.
- **Thread-abandonment note:** `_call_with_timeout` runs the embed in a worker thread; on timeout the blocked thread is abandoned (the model download continues in the background and may complete later). This is the same accepted tradeoff FAB-17 already made for the search path; it does not corrupt state.
- **Concurrency:** no new write-path contention; `db.py`'s SQLite thread-affinity is respected because the bounded callable is pure-ChromaDB (no SQLite), matching the FAB-17 `_chroma_query_matches` design.
- **Rollback:** revert the `_index_deliberation_in_chroma` edit + the constant + the test. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs a P0 hang defect in the deliberation-index embedding path by extending the existing bounded-embedding pattern; no new capability surface, no schema/authority change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
