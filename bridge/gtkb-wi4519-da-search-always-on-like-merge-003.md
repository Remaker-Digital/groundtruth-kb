NEW

bridge_kind: implementation_report
Document: gtkb-wi4519-da-search-always-on-like-merge
Version: 003
Responds-To: bridge/gtkb-wi4519-da-search-always-on-like-merge-002.md
Author: Prime Builder (Claude Code, harness B)
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T15-13-22Z-prime-builder-B-f3ee96
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Claude Code bridge auto-dispatch session; Prime Builder (durable role, harness B); explanatory output style; model claude-opus-4-8[1m]
Date: 2026-06-14 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4519
target_paths: ["groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py"]
implementation_scope: source, test
kb_mutation_in_scope: false
Recommended commit type: fix:

# WI-4519 Implementation Report: Always-on SQLite-LIKE merge in `search_deliberations`

## Summary

The GO'd design (`-001`, GO at `-002`) is **implemented and committed**. The always-on SQLite-LIKE merge in `KnowledgeDB.search_deliberations` runs the bounded ChromaDB semantic pass AND an in-process SQLite LIKE pass on every call, then merges the two result sets deduped by deliberation `id` (semantic head preserving relevance ordering, then LIKE-only rows by `rowid DESC` recency for the unindexed tail), capped to `limit`. This closes the S437 freshness gap: a recently-inserted deliberation whose ChromaDB index step was deferred (e.g. by the already-VERIFIED WI-4453 embedding-timeout guard) is surfaced by the very next search, restoring the mandatory pre-proposal/pre-review Deliberation Archive search contract.

## Provenance Note (faithful reporting)

The source and test changes were landed by a prior (abandoned) agent session and swept into commit `7cf382a0d` ("feat(gtkb): sweep — source implementations … WI-4519 search always-on LIKE … (abandoned agent sessions)"); the post-implementation report was never filed, leaving this thread parked at GO. This dispatched Prime Builder session did **not** re-implement. It verified the committed code against the approved `-001` design clause-by-clause, confirmed both `target_paths` are clean in git (no uncommitted drift), and executed the full spec-derived verification plan below. All gates are green. This report exists to close the bridge audit trail (GO → report → VERIFIED).

## Implemented Change (verified against `-001` Design)

`groundtruth-kb/src/groundtruth_kb/db.py`, `search_deliberations` (`:8293`–`:8396`):

1. **Always-on SQLite LIKE pass** (`:8366`–`:8384`) — runs on every call on the calling-thread connection against `current_deliberations` with the `content/summary/title LIKE ? ORDER BY rowid DESC LIMIT ?` predicate. Matches `-001` Design clause 1.
2. **Semantic pass unchanged** (`:8320`–`:8364`) — bounded ChromaDB query with the existing FAB-17 timeout/retry degradation; timeout/failure degrades to an empty semantic set (LIKE remains the safety net). Matches `-001` Design clause 2.
3. **Merge & dedupe by id** (`:8386`–`:8396`) — output is `semantic_results` first (relevance ordering preserved), then LIKE-only rows whose `id` was not already surfaced (recency ordering preserved), capped to `limit`. Each row carries the existing `search_method` field (`"semantic"` | `"text_match"`). Matches `-001` Design clause 3.
4. **No schema change, no index change, no `insert_deliberation` change** — the gap is closed read-side only. Matches `-001` Design clause 4.

The regression test file `groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py` is hermetic: it monkeypatches `_get_chroma_collection` with a configurable `_StubCollection` stand-in and never loads a real embedding model, so it runs whether or not ChromaDB is installed.

## Specification Links (carried forward from `-001`)

- **GOV-STANDING-BACKLOG-001** — WI-4519 is the backlog authority for this P3 deliberation-archive reliability fix.
- **GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001**, **DCL-PROJECT-AUTHORIZATION-ENVELOPE-001** — proceeded under `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDALONE-DEFECT-BATCH-2` (includes WI-4519; allows `source` + `test_addition`).
- **`.claude/rules/deliberation-protocol.md`** — the mandatory "search deliberations before proposing/reviewing" contract this fix restores for fresh DELIBs.
- **GOV-FILE-BRIDGE-AUTHORITY-001** — filed through the file bridge; this report does not modify `bridge/INDEX.md` workflow state beyond its own entry.
- **DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001**, **DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001** — PAUTH / project / work-item / target-path metadata concretely linked.
- **DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001** — every acceptance criterion maps to an executed test (table below).
- **ADR-ISOLATION-APPLICATION-PLACEMENT-001** — both `target_paths` are in-root under `E:\GT-KB`.
- **ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001** (advisory), **GOV-ARTIFACT-ORIENTED-GOVERNANCE-001** (advisory), **DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001** (advisory).

## Spec-to-Test Mapping (Specification-Derived Verification)

| Acceptance criterion | Test | Governing spec | Result |
|---|---|---|---|
| Fresh-but-unindexed DELIB found via LIKE alongside semantic results (WI-4519 S437 repro) | `test_unindexed_delib_surfaces_via_like` | `.claude/rules/deliberation-protocol.md`, GOV-STANDING-BACKLOG-001 | PASS |
| Existing semantic results preserved (no FAB-17 regression) | `test_semantic_results_preserved` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | PASS |
| Dedupe by id: a DELIB matched by both paths appears once (semantic wins) | `test_dedupe_prefers_semantic_for_overlap` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | PASS |
| Order: semantic head then LIKE-only tail; cap to limit | `test_result_order_semantic_first_then_like` | `.claude/rules/deliberation-protocol.md` | PASS |
| LIKE-only path works when ChromaDB unavailable/empty (FAB-17 preserved) | `test_like_only_when_no_semantic` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | PASS |
| LIKE pass is fast and cannot hang (no new latency path) | `test_like_pass_does_not_hang` | WI-4519 risk/rollback | PASS |

## Verification Evidence (exact commands + observed results)

Interpreter: `groundtruth-kb/.venv/Scripts/python.exe`; ruff: `groundtruth-kb/.venv/Scripts/ruff.exe`.

1. Pre-file code-quality gates (both changed files):
   - `ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py` → **All checks passed!**
   - `ruff format --check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py` → **2 files already formatted**
2. Focused regression suite:
   - `python -m pytest groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py -q --tb=short` → **6 passed in 3.59s**
3. Existing DA / FAB-17 / WI-4453 regression coverage (semantic preservation, LIKE fallback, embedding-timeout guard):
   - `python -m pytest groundtruth-kb/tests/test_deliberations.py groundtruth-kb/tests/test_deliberation_index_embedding_timeout.py groundtruth-kb/tests/test_cli_deliberations.py -q --tb=short` → **89 passed, 11 skipped in 40.09s** (the 11 skips are ChromaDB-optional tests that skip when ChromaDB is unavailable; the SQLite-LIKE + timeout-guard paths under test all pass).
4. Git target-path cleanliness: `git status --short -- groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/tests/test_search_deliberations_always_on_like_merge.py` → no entries (committed at `7cf382a0d`, no uncommitted drift).

## Owner Decisions / Input

This report carries forward the durable owner-decision evidence cited in `-001`; no new owner AskUserQuestion is required for verification.

- **`DELIB-2026-06-13-RELIABILITY-STANDALONE-DEFECT-BATCH-2-ADMISSION`** — owner AUQ (2026-06-13) admitting WI-4519 under `PAUTH-…-BATCH-2` (allowed: `source`, `test_addition`).
- **Cycle-9 scope AskUserQuestion (2026-06-14, session 02535fad)** — owner selected **"Seed always-on SQLite-LIKE merge"**, authorizing exactly this scope. The implementation stays within `source` + `test_addition` and changes no formal artifact or schema.

## Recommended Commit Type

`fix:` — repairs broken behavior (the mandatory pre-proposal search silently missing fresh DELIBs), restoring a governance read-surface invariant. The diff is one method-body change in `db.py` plus one net-new regression-test file; no new capability surface, so `fix:` (not `feat:`) per the Conventional Commits discipline (`.claude/rules/file-bridge-protocol.md`). NOTE: the change is already committed under the broad sweep commit `7cf382a0d`; this recommendation records the type the WI-4519 slice would carry as a standalone commit for changelog/semantic-version inference.

## Risk / Rollback

Low. One read-side method-body change (an existing fallback SQL query now runs on every call; a small Python merge). No schema change, no migration, no new dependency, no change to `insert_deliberation` / `_index_deliberation_in_chroma`. Cannot make any search slower than the existing `limit`-bounded LIKE and cannot hang (in-process SQLite). Rollback: revert the `search_deliberations` edit + delete the test file; no migration, no KB mutation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
