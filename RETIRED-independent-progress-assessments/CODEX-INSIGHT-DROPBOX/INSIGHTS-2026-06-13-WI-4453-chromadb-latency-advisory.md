# Loyal Opposition Advisory - WI-4453 ChromaDB Latency

Date: 2026-06-13  
Reviewer: Codex, Loyal Opposition, harness A  
Automation: keep-working-lo  
Work item: WI-4453 - gt deliberations record / search / gt bridge propose hang on ChromaDB embedding step

## Claim

WI-4453 should remain open, but the failure mode is narrower than the original incident. In the current Python 3.14 live checkout, `gt deliberations search` and `gt bridge propose --dry-run` return quickly because ChromaDB is disabled and the SQLite fallback path is used. That does not satisfy the work item's acceptance contract because the real synchronous `gt deliberations record` indexing path is still not timeout-bound, and there is no regression benchmark covering median latency for all three named CLI surfaces.

## Evidence

- Live backlog source: `python -m groundtruth_kb.cli backlog show WI-4453 --json` reports WI-4453 as open P0, approval_state `unapproved`, with acceptance requiring `gt deliberations record`, `gt deliberations search`, and `gt bridge propose` to return within `<= 10s` on a warm cache and a median-latency regression benchmark.
- Live bridge source: direct `bridge/INDEX.md` read plus `.claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json` reported no latest `NEW` or `REVISED` Loyal Opposition-actionable bridge entries before this advisory work.
- Live runtime probe: `python -c "import sys; from groundtruth_kb import db; print(...)"` reported Python `3.14.0`, `HAS_CHROMADB: False`, and `chroma_loaded: False`.
- Live store probe: `.groundtruth-chroma/chroma.sqlite3` exists and is about 253 MB, but the active runtime does not exercise it because `HAS_CHROMADB` is false.
- Direct command probe: `python -m groundtruth_kb.cli deliberations search "DELIB-S312 deterministic services principle chromadb" --limit 5 --json` returned `[]` with exit 0 in the tool's 1.5s wall time.
- Direct command probe: `python -m groundtruth_kb bridge propose --kind defect-fix --wi WI-4453 --slug gtkb-wi4453-chromadb-timeout-advisory --target-path groundtruth-kb/src/groundtruth_kb/db.py --target-path groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py --dry-run` emitted a non-dispatchable draft with exit 0 in the tool's 2.6s wall time.
- Safety limit: an attempted wrapped timing probe for `gt deliberations record --dry-run` was blocked by the LO file-safety hook as `GTKB-LO-FILE-SAFETY: unresolved or opaque shell mutation target requires a non-shell edit path`. I did not bypass that guard.
- Source inspection: `groundtruth-kb/src/groundtruth_kb/db.py` defines `_call_with_timeout()` and applies it to `search_deliberations()` Chroma queries, so search can degrade to SQLite fallback instead of hanging.
- Source inspection: `groundtruth-kb/src/groundtruth_kb/db.py` still runs `insert_deliberation()` as SQLite commit first, then synchronous `_index_deliberation_in_chroma(id)` without a timeout wrapper. Exceptions are contained, but a blocking embedding/index call can still consume the caller's wall clock after the authoritative write.
- Source inspection: `groundtruth-kb/src/groundtruth_kb/cli_deliberations_record.py` returns before approval-packet write, DB insert, and Chroma indexing when `dry_run` is true, so dry-run tests do not exercise the observed post-write indexing hang.
- Source inspection: `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py` uses `db.search_deliberations()` for auto prior-deliberation loading and catches exceptions. The live WI-4453 draft still rendered `_No prior deliberations auto-loaded_` even though WI-4453 has related deliberation IDs, so search fallback can become a quality degradation even when it is fast.

## Verification

- `python -m pytest platform_tests\test_groundtruth_kb_import_budget.py -q --tb=short` passed: 3 passed, 1 skipped in 0.54s.
- `python -m pytest platform_tests\groundtruth_kb\cli\test_deliberations_record.py groundtruth-kb\tests\test_cli_bridge_propose.py groundtruth-kb\tests\test_cli_deliberations.py -q --tb=short` passed: 50 passed in 14.08s.
- `python -m pytest platform_tests\scripts\test_fab17_chroma_read_path.py groundtruth-kb\tests\test_deliberations.py::TestChromaFailureContainment groundtruth-kb\tests\test_cli_bridge_propose.py::test_cli_bridge_propose_no_optional_deps groundtruth-kb\tests\test_cli_bridge_propose.py::test_auto_prior_delibs_fallback_safe -q --tb=short` passed: 10 passed in 3.02s.

## Risk / Impact

- The current live fallback path is responsive, so WI-4453 is not reproduced as an immediate multi-minute blocker in this Python 3.14 environment.
- The acceptance criteria remain unmet because there is no median-latency regression benchmark for the three named CLI commands, and the real non-dry-run record path can still block after canonical SQLite commit if ChromaDB indexing stalls instead of raising.
- Because ChromaDB is disabled under this runtime, a clean probe here could mask the original embedding model-load tax on supported runtimes where ChromaDB is active.
- Prior-deliberation seeding for `gt bridge propose` should not rely only on semantic search. Work item explicit `related_deliberation_ids` are deterministic metadata and should be included before any optional semantic query.

## Recommended Action

Prime Builder should file a narrow defect-fix proposal for WI-4453 rather than close it from the current evidence. The proposal should:

1. Add a regression benchmark or benchmark-style test that measures median latency for `gt deliberations search`, `gt bridge propose --dry-run`, and the governed record service on a non-trivial seeded store, with a documented warm-cache baseline and a CI failure threshold at the WI's `<= 10s` budget.
2. Bound or decouple `insert_deliberation()` Chroma indexing so canonical SQLite writes and governed record CLI completion do not wait indefinitely for embedding/index work. Acceptable approaches include daemon-thread timeout with fallback, out-of-band index queue, or batch rebuild-only indexing after writes.
3. Preserve the existing lazy optional-dependency behavior and search fallback tests.
4. Seed `gt bridge propose` Prior Deliberations from work item `related_deliberation_ids` deterministically before optional semantic search, so proposal quality does not collapse when ChromaDB is disabled or times out.

## Owner Decision Needed

No owner decision is required for this advisory. The next decision point is Prime Builder's implementation proposal scope for WI-4453.
