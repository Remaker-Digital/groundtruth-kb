# WI-4453 Chroma DA Latency - Loyal Opposition Advisory

Date: 2026-06-12
Role: Loyal Opposition
Work item: WI-4453

## Claim

`WI-4453` is still valid, but its current acceptance surface should be narrowed. The live read path for `gt deliberations search` no longer reproduces a hang in this environment and is partially remediated by FAB-17; the remaining high-risk surface is the write path, where `insert_deliberation()` commits SQLite first and then calls `_index_deliberation_in_chroma()` synchronously without a timeout around `collection.add()` when ChromaDB is enabled.

## Evidence

- Live bounded reproduction, Python 3.14 venv:
  - `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "bridge dispatch" --limit 3 --json`
  - Result: exit 0 in about 2.06 seconds; results used `search_method: "text_match"`.
- Semantic-only check:
  - `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "bridge dispatch" --limit 3 --semantic-only --json`
  - Result: exit 1 with `--semantic-only requires ChromaDB`; current Python 3.14 host reports `HAS_CHROMADB: false`.
- FAB-17 status:
  - `bridge/INDEX.md` lists `gtkb-fab-17-da-chroma-read-path` as `VERIFIED`.
  - `platform_tests/scripts/test_fab17_chroma_read_path.py` has tests for Chroma crash and timeout fallback on `search_deliberations()`.
  - `python -m pytest platform_tests\scripts\test_fab17_chroma_read_path.py -q --tb=short` passed: 7 passed in 1.43s.
- Source inspection:
  - `groundtruth-kb/src/groundtruth_kb/db.py` wraps Chroma count/query in `_call_with_timeout()` inside `search_deliberations()`.
  - `groundtruth-kb/src/groundtruth_kb/db.py` `insert_deliberation()` commits SQLite, then calls `_index_deliberation_in_chroma(id)` in a `try/except`, but the Chroma call is synchronous.
  - `_index_deliberation_in_chroma()` calls `collection.delete(...)` and `collection.add(...)` directly; exceptions are caught by the caller, but a stall is not bounded unless Chroma itself returns.

## Risk / Impact

The current Python 3.14 host avoids the hang because ChromaDB is disabled, so local `search` is healthy. Python versions or environments where ChromaDB is enabled can still pay unbounded wall time during deliberation writes after the canonical SQLite row has already committed. That matches the WI's original observation: killing the command after the canonical write is safe for data integrity, but it is operationally expensive and confusing.

## Recommended Action

Revise `WI-4453` into a targeted write-path fix:

- Keep FAB-17 as the read-path/search mitigation and do not duplicate that work.
- Add a bounded timeout or out-of-band queue for `_index_deliberation_in_chroma()` after SQLite commit.
- Add a regression test using a fake Chroma collection whose `add()` stalls, proving `insert_deliberation()` returns promptly and the SQLite row remains readable.
- Optionally retain a CLI latency benchmark, but make it validate write-path behavior separately from `search_deliberations()`.

## Decision Needed From Owner

No owner decision is needed for the next engineering step. The existing P0 backlog item is enough authority for Prime Builder to file an implementation proposal that narrows scope to the write-side index timeout/decoupling gap.
