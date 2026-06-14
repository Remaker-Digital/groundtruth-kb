NEW

bridge_kind: implementation_proposal
Document: gtkb-wi4519-da-search-always-on-like-merge
Version: 001
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 02535fad-c96f-4bd8-8e09-24dfd34c1529
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive session; Prime Builder (durable role, harness B); explanatory output style; autonomous backlog loop; model claude-opus-4-7[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4519
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py"]
implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4519: Always-on SQLite-LIKE merge in `search_deliberations` so fresh-but-unindexed DELIBs are never missed

## Summary

WI-4519 (P3, `deliberation-archive`, origin=improvement): the mandatory pre-proposal Deliberation Archive (DA) search silently misses recently-inserted DELIBs that have not yet been indexed into ChromaDB. S437 evidence (2026-06-13): `gt deliberations search` returned NO match for `DELIB-ROLE-AUTHORITY-DECLARED-NOT-DETECTED-20260613` across three phrasings despite that DELIB being ~1 day old; it was found only via direct MemBase SQLite fetch. Impact: the protocol that requires searching deliberations before proposing/reviewing is blind to recently-archived decisions, risking duplicate proposals and missed prior decisions.

**Cycle-9 triage (this session) localized the root cause precisely in `groundtruth-kb/src/groundtruth_kb/db.py`:**

1. `insert_deliberation` (`:7835`) writes the canonical SQLite row, then calls `_index_deliberation_in_chroma` (`:7924`) — but the index step inherits the WI-4453 embedding-timeout (now VERIFIED), so on a timeout the DELIB row persists **un-indexed**. The SQLite truth is correct; the semantic index is deferred.
2. `search_deliberations` (`:8293`) does ChromaDB semantic search FIRST. If semantic results survive the distance filter (`semantic_results`, `:8350-8351`), it **returns semantic-only**. The SQLite-LIKE block (`:8353-8369`) is reached ONLY when semantic returns empty / unavailable / times out — it is a fallback, NOT a parallel pass.

So a *successful* semantic search returns semantic-only and silently crowds out any recently-inserted-but-unindexed DELIB. Owner cycle-9 AskUserQuestion decision: **"Seed always-on SQLite-LIKE merge."** This proposal does exactly that: SQLite-LIKE always runs alongside the semantic query and the results are merged & deduped by DELIB id, so fresh-but-unindexed DELIBs are always findable. LIKE is fast, cannot hang, and runs on the same SQLite connection the search already uses.

## Specification Links

- **GOV-STANDING-BACKLOG-001** — WI-4519 is the backlog authority for this fix (P3 deliberation-archive reliability improvement).
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeds under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4519; allows `source` + `test_addition`).
- **`.claude/rules/deliberation-protocol.md`** — the mandatory "search deliberations before proposing/reviewing" protocol that the freshness lag silently undermines. This fix restores its reliability for fresh DELIBs.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — this proposal is filed through the file bridge (the always-applicable bridge-governance trigger); it is a DA reliability fix that does not modify `bridge/INDEX.md` or any bridge workflow state.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata and governing specs are concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — the verification plan maps each acceptance criterion to an executed test, including a "fresh-but-unindexed DELIB is now findable" regression.
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory) — durable, tracked fix to a governance read-surface that the protocol depends on.

## Requirement Sufficiency

Existing requirements sufficient. The freshness gap is documented (WI-4519 + the S437 repro), cycle-9 triage localized the root cause in db.py:8293-8370, the bounded PAUTH authorizes the `source` + `test_addition` work, and `.claude/rules/deliberation-protocol.md` defines the search-before-propose contract this fix restores. No new or revised formal specification is required.

## Prior Deliberations

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ admitting WI-4519 (and 7 siblings) to PROJECT-GTKB-RELIABILITY-FIXES under `PAUTH-…-BATCH-2`.
- **Cycle-9 owner AskUserQuestion (2026-06-14, session 02535fad)** — owner selected "Seed always-on SQLite-LIKE merge" over "harvest-on-insert hardening" and "defer for now", scoping this slice as the always-on parallel LIKE pass merged with semantic results.
- **`bridge/gtkb-wi4453-deliberation-embedding-timeout` thread (VERIFIED)** — bounded the `_index_deliberation_in_chroma` embedding step so `insert_deliberation` cannot hang; it correctly preserved canonical SQLite + deferred the index on timeout. THIS slice is the read-side complement: when the index is deferred, the search must still find the row. The fixes compose: WI-4453 prevents the hang, WI-4519 prevents the silent miss.
- **`bridge/gtkb-fab-17-da-chroma-read-path` thread (VERIFIED, FAB-17 / HYG-048)** — bounded the semantic-search timeout and established the SQLite-LIKE fallback pattern this slice extends from "fallback-only" to "always-on parallel + merge".
- **`.claude/rules/deliberation-protocol.md`** — the mandatory pre-proposal search this fix protects.
- _Live semantic deliberation search was not run during authoring: `gt deliberations search` is the subject of this defect (and the in-flight WI-4453 fix only just landed); per the session's standing caution, prior-decision context was gathered from the threads cited above + the live code surface._

## Owner Decisions / Input

This implementation proposal is authorized by durable owner-decision evidence; no new owner AskUserQuestion is required to file or implement it.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4519 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`).
- **Cycle-9 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Seed always-on SQLite-LIKE merge"**, authorizing exactly this scope (always run LIKE alongside semantic, merge/dedupe by DELIB id) over the harvest-on-insert hardening and defer alternatives. The fix stays within `source` + `test_addition` and changes no formal artifact or schema.

## Design

In `groundtruth-kb/src/groundtruth_kb/db.py`, modify `search_deliberations` (`:8293`):

1. **Always run the SQLite-LIKE pass** (currently `:8353-8369`) regardless of semantic-search outcome. Compute it on the same connection, against `current_deliberations`, with the existing `content/summary/title LIKE` predicate and a `limit` bound. It is fast and cannot hang.
2. **Run semantic search as today** with its existing bounded timeout (FAB-17). On semantic success, build `semantic_results` as today; on semantic timeout/failure, treat semantic as an empty result set (the helper-driven "degrade" path is preserved — LIKE remains the safety net).
3. **Merge & dedupe** by `id`: build the output list as semantic_results FIRST (preserving semantic relevance ordering), then append LIKE-only rows whose `id` did not already appear (preserving the existing rowid-DESC recency ordering of the LIKE pass for the unindexed-tail). Cap to `limit`. Each row carries the existing `search_method` field ("semantic" or "text_match") so callers can see WHICH path matched.
4. **No schema change, no index change, no `insert_deliberation` change** — the freshness gap is closed read-side. Combined with the already-VERIFIED WI-4453 fix, fresh DELIBs persist in SQLite immediately and are now found by the very next search.

This is the minimal-risk way to satisfy the owner-chosen scope: it adds one fast SQL query per search (already executed today on the fallback path) and a small Python merge; it removes no semantic-result path; it preserves the existing `search_method` taxonomy.

## Verification Plan (Specification-Derived)

| Acceptance criterion | Test (in `groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py`) | Method |
|---|---|---|
| Fresh-but-unindexed DELIB is found via LIKE alongside semantic results (WI-4519 S437 repro) | `test_unindexed_delib_surfaces_via_like` | insert a DELIB with the index step monkey-patched to no-op (simulating WI-4453 timeout degradation) → assert `search_deliberations` returns the DELIB even when ChromaDB returns other matches |
| Existing semantic results are preserved (no regression to FAB-17 path) | `test_semantic_results_preserved` | populate ChromaDB with a matching DELIB → assert it still appears with `search_method == "semantic"` and correct ordering |
| Dedupe by id: a DELIB matched by BOTH paths appears once (semantic ordering wins) | `test_dedupe_prefers_semantic_for_overlap` | a DELIB matches both semantic and LIKE → asserts it appears exactly once with `search_method == "semantic"` |
| Order: semantic results first, then LIKE-only tail (deliberation-protocol gate) | `test_result_order_semantic_first_then_like` | mixed corpus → asserts the output is semantic-ranked head + LIKE-only-DESC tail, capped at `limit` |
| LIKE-only path still works when ChromaDB is unavailable/empty (FAB-17 preserved) | `test_like_only_when_no_semantic` | no ChromaDB collection / empty semantic → LIKE-only results returned with `search_method == "text_match"` |
| LIKE pass is fast and cannot hang (no new latency path) | `test_like_pass_does_not_hang` | smoke: ChromaDB succeeds normally + LIKE returns within a tight bound (e.g. < 1s on a small fixture corpus) |

Pre-file code-quality gates (run before the implementation report): `ruff check` AND `ruff format --check` on both changed files; `python -m pytest groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py -q --tb=short`; plus the existing DA / FAB-17 / WI-4453 regression suites must still pass.

## Risk / Rollback

- **Risk: low.** One method body modification in `db.py` (always run an existing SQL query that already runs on the fallback path; merge two lists in Python). No schema change, no migration, no new dependency, no change to `insert_deliberation` or `_index_deliberation_in_chroma`. The fix cannot make any search SLOWER than the existing `limit`-bounded SQLite LIKE, and it cannot hang (LIKE is in-process SQLite).
- **Compose with WI-4453:** WI-4453 (VERIFIED) prevents the hang on insert/index; WI-4519 prevents the silent miss on search. Together they restore reliable freshness for the mandatory pre-proposal protocol.
- **Caller compatibility:** the output schema is unchanged (existing `search_method` field already carries the distinction); callers that look only at `id`/`title`/`content` see no difference except finding more rows when applicable.
- **Rollback:** revert the `search_deliberations` edit + delete the test. No migration, no schema change, no KB mutation.

## Recommended Commit Type

`fix:` — repairs broken behavior (the mandatory pre-proposal search silently missing fresh DELIBs), restoring a governance invariant. Per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
