NEW

bridge_kind: implementation_report
Document: gtkb-wi4453-deliberation-embedding-timeout
Version: 003
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-13T23-38-43Z-prime-builder-B-b86063
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch session; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-13 UTC

Implements GO: bridge/gtkb-wi4453-deliberation-embedding-timeout-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4453
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py"]
implementation_scope: source, test
Recommended commit type: fix:

# WI-4453 Implementation Report: Bound the ChromaDB deliberation-index embedding step

## Summary

Implemented the GO'd slice (`-002`). The unbounded `collection.add(...)` in
`_index_deliberation_in_chroma` — the record/propose write path that triggers the
first-use `DefaultEmbeddingFunction` model load and could hang indefinitely —
is now wrapped in the existing FAB-17 `_call_with_timeout` daemon-worker helper
under a new, env-overridable `_CHROMA_INDEX_TIMEOUT_SECONDS` (default 15s,
`GTKB_CHROMA_INDEX_TIMEOUT_SECONDS`). On timeout the index step degrades to a
deferred (rebuildable) semantic index — sentinel `0` chunks, no raise — while the
canonical SQLite DA row (committed by `insert_deliberation` *before* indexing)
remains authoritative and readable.

Because `rebuild_deliberation_index` drives the same `_index_deliberation_in_chroma`
per record, bounding that function also hardens the rebuild path: an offline
rebuild now degrades per-record (0 chunks, no error) instead of hanging on the
first record. This satisfies GO condition 3 ("rebuild hardened in the same slice
→ focused test required"), covered by `test_rebuild_degrades_per_record_on_index_timeout`.

No change to the already-FAB-17-bounded search path, no change to
`insert_deliberation`, no schema change, no KB mutation, no bridge-authority
change.

## Specification Links

_Carried forward from the GO'd proposal `-001`._

- **GOV-STANDING-BACKLOG-001** — WI-4453 is the backlog authority for this P0 reliability fix.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — implemented under active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1` (includes WI-4453; allows `source` + `test_addition`).
- **GOV-FILE-BRIDGE-AUTHORITY-001** — `gt bridge propose` is a load-bearing bridge surface; the fix makes its deliberation-index step resilient (cannot hang) without altering bridge authority.
- **GOV-SOURCE-OF-TRUTH-FRESHNESS-001** — the canonical SQLite DA record stays authoritative and intact; only the disposable semantic index is deferred-but-rebuildable.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH/project/work-item/target-path metadata and governing specs linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — each acceptance criterion maps to an executed test (table below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`.

## Spec-to-Test Mapping (executed)

| Acceptance criterion | Governing spec | Test | Result |
|---|---|---|---|
| Index `collection.add` timeout returns promptly (degraded sentinel `0`), does not hang | GOV-FILE-BRIDGE-AUTHORITY-001, WI-4453 | `test_index_add_times_out_and_degrades` | PASS |
| Canonical SQLite DA row readable after index timeout | GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | `test_sqlite_row_intact_after_index_timeout` | PASS |
| Timeout env-overridable via `GTKB_CHROMA_INDEX_TIMEOUT_SECONDS` | WI-4453 (env contract) | `test_index_timeout_env_override` | PASS |
| Normal (fast) index path returns real chunk count (unchanged) | WI-4453 (no behavior change) | `test_fast_index_path_still_indexes` | PASS |
| Search timeout/SQLite-LIKE fallback NOT regressed (FAB-17 preserved) | GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (FAB-17) | `test_search_still_bounded` | PASS |
| Rebuild degrades per-record on index timeout (GO condition 3) | WI-4453, GOV-SOURCE-OF-TRUTH-FRESHNESS-001 | `test_rebuild_degrades_per_record_on_index_timeout` | PASS |

## Real Diff (limited to the two target paths)

### `groundtruth-kb/src/groundtruth_kb/db.py` (+29 / -1)

1. New module constant alongside the FAB-17 query constants (after `_CHROMA_QUERY_RETRIES`):

```python
# WI-4453: the index/record path (collection.add) triggers the SAME first-embed
# DefaultEmbeddingFunction model load as the query path, so `gt deliberations
# record` and any `gt bridge propose` that indexes a deliberation could hang
# indefinitely on an offline/stalled embedding step. Bound the add under the
# same daemon-worker timeout used for the query path (FAB-17). On timeout the
# canonical SQLite DA row — already committed by insert_deliberation before
# indexing — is preserved and only the rebuildable semantic index is deferred
# (recoverable via rebuild_deliberation_index). Overridable via env.
_CHROMA_INDEX_TIMEOUT_SECONDS = float(os.environ.get("GTKB_CHROMA_INDEX_TIMEOUT_SECONDS") or "15")
```

2. Bounded the embedding-triggering add in `_index_deliberation_in_chroma`:

```python
        # WI-4453: bound the embedding-triggering add so record/propose cannot
        # hang on a first-use model load. On timeout, degrade to a deferred
        # semantic index (sentinel 0 chunks) rather than raising — the canonical
        # SQLite DA row is already committed and the index is rebuildable.
        try:
            _call_with_timeout(
                lambda: collection.add(ids=ids, documents=documents, metadatas=metadatas),
                _CHROMA_INDEX_TIMEOUT_SECONDS,
            )
        except TimeoutError as _chroma_index_timeout:  # intentional-catch: degrade to deferred index
            _log.warning(
                "ChromaDB index add timed out after %.1fs for %s; deferring semantic "
                "index (canonical SQLite row preserved, rebuildable via "
                "rebuild_deliberation_index): %s",
                _CHROMA_INDEX_TIMEOUT_SECONDS,
                delib_id,
                _chroma_index_timeout,
            )
            return 0
        return len(chunks)
```

(Replaced the prior single line `collection.add(ids=ids, documents=documents, metadatas=metadatas)` immediately preceding `return len(chunks)`.)

### `groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py` (new file, +~200)

Hermetic test module (6 tests). Stubs `_get_chroma_collection` with an in-memory
`_StubCollection` whose `add`/`query`/`count` can simulate the unbounded first-embed
load via configurable delays, so the tests never load a real model and run
regardless of whether ChromaDB is installed. The fast-path test asserts the real
single-chunk index; the timeout tests lower the module constant (or env var) and
assert prompt degradation; the search test confirms FAB-17 fallback; the rebuild
test confirms per-record degradation.

## Executed Verification Commands

```
$ python -m pytest groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py -q --tb=short
......                                                                   [100%]
6 passed in 5.45s

$ python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py
All checks passed!     (exit 0)

$ python -m ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py
2 files already formatted     (exit 0)
```

Regression check (existing deliberation suite, no behavior change):

```
$ python -m pytest groundtruth-kb/tests/test_deliberations.py -q --tb=short
59 passed, 11 skipped in 21.48s
```

(The 11 skips are `requires_chromadb` tests — ChromaDB is not installed in this
environment, which is precisely why the new tests are hermetic and stub the
collection rather than depending on a live model.)

## Rebuild Path Disposition (GO condition 3)

`rebuild_deliberation_index()` **is hardened in this slice** as a direct
consequence of bounding `_index_deliberation_in_chroma` (the per-record indexer
it calls). The focused test `test_rebuild_degrades_per_record_on_index_timeout`
covers it: two records, a slow stub add, lowered index timeout → rebuild returns
`{"indexed": 2, "chunks": 0, "errors": []}` promptly instead of hanging.

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no new owner AskUserQuestion is
required.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner AUQ approval (2026-06-13) admitting WI-4453 to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-1` (allowed: `source`, `test_addition`; forbids formal-artifact/KB mutation). This implementation stays strictly within that scope: source + test only, no formal-artifact or KB mutation, no bridge-authority change.

## Prior Deliberations

- **`bridge/gtkb-fab-17-da-chroma-read-path-009.md` (VERIFIED, FAB-17 / HYG-048)** — bounded the deliberation **search** path with `_call_with_timeout` + SQLite-LIKE degradation; this slice extended the identical proven pattern to the index path. Primary precedent.
- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-ADMISSION`** — owner admission + PAUTH for the bounded reliability defect batch.
- **`DELIB-20261667`** — observed DA/Chroma hang defect context (cited in the GO verdict `-002`).
- **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** — the deterministic-services principle this P0 reliability fix supports.

## Recommended Commit Type

`fix:` — repairs a P0 hang defect in the deliberation-index embedding path by
extending the existing bounded-embedding pattern to the write/index path; no new
capability surface, no schema/authority change. Diff stat: `db.py` +29/-1 plus a
new hermetic test module (≈200 lines).

## Risk / Rollback

- **Risk: low.** Localized to `_index_deliberation_in_chroma` + one module
  constant; reuses the already-VERIFIED `_call_with_timeout` helper and the
  search-path degradation idiom. Cannot lose canonical data — the SQLite DA row
  is written independently; only the disposable, rebuildable ChromaDB index is
  deferred on timeout.
- **Thread-abandonment note:** on timeout the blocked embed thread is abandoned
  (daemon); the background model download may complete later. Same accepted
  tradeoff FAB-17 made for the search path; it does not corrupt state.
- **Rollback:** revert the `_index_deliberation_in_chroma` edit + the constant +
  delete the test module. No migration, no schema change, no KB mutation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
