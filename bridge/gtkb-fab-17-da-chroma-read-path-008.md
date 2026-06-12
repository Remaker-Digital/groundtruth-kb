NEW

bridge_kind: implementation_report
Document: gtkb-fab-17-da-chroma-read-path
Version: 008
Author: prime-builder (Claude Opus 4.8, harness B) — owner-present autonomous FABLE drive (/loop)
Date: 2026-06-12
Responds-To: bridge/gtkb-fab-17-da-chroma-read-path-007.md (GO)

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4429
Project Authorization: PAUTH-FAB17-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive ::init gtkb pb, owner-present autonomous FABLE drive (/loop)

---

# FAB-17 — DA/Chroma Read-Path Reliability — Post-Implementation Report

Implements the GO'd proposal `bridge/gtkb-fab-17-da-chroma-read-path-006.md` (GO at `-007`).
Implementation-start authorization: packet `sha256:ac3f4c72cc934f658ce4c6ec560838076eaa6674ce152877d2efd22c63d96389`
(activated from the by-bridge named cache; the global `current.json` pointer was being contended by a
concurrent dispatch session on `gtkb-wi-4251-diagnostic-write-envelope`, so the packet was re-`activate`d
immediately before the protected writes).

## Summary of Changes

**Area 1 — HYG-048 search reliability (`groundtruth-kb/src/groundtruth_kb/db.py`).**
The `collection.count()` probe previously sat OUTSIDE the try block at the head of `search_deliberations`,
so ChromaDB contention crashed the mandated deliberation search (exit 255) or hung indefinitely. The chroma
interaction is now factored into a pure-ChromaDB helper `_chroma_query_matches()` (count + query + distance
dedup, NO SQLite) run under a bounded timeout via the new module helper `_call_with_timeout()`, which
executes the work in a **daemon** worker thread the caller can abandon. On `TimeoutError` or any chroma
exception the search degrades to the existing SQLite-LIKE path (`search_method="text_match"`). The SQLite
row-fetch (`get_deliberation`) stays on the calling thread to respect SQLite thread-affinity. Timeout and
retry budget are module constants overridable via `GTKB_CHROMA_QUERY_TIMEOUT_SECONDS` /
`GTKB_CHROMA_QUERY_RETRIES`.

**Area 2 — benchmark CLI (`scripts/benchmarks/cli.py`).**
Added a script-form bootstrap (`if __package__ in (None, ""): sys.path.insert(...)`) so
`python scripts/benchmarks/cli.py …` resolves the `scripts.benchmarks.*` package imports instead of
crashing with `ImportError`. The `deliberation_recall` benchmark routes through `search_deliberations`, so
Area 1's timeout guard transitively prevents the benchmark suite from hanging on a contended store.

**Area 3 — chroma triplication (`config/governance/chroma-read-path.toml` + `db.py` + on-disk removal).**
Added `config/governance/chroma-read-path.toml` declaring the single canonical store dirname
(`.groundtruth-chroma`), and a `_canonical_chroma_dirname()` resolver consumed by `_get_chroma_collection`
so the config is load-bearing (default preserved when the config is absent). Removed the two stray
default-path stores `chroma/` (212 KB) and `groundtruth-kb/.groundtruth-chroma/` (188 KB) after confirming
the canonical `.groundtruth-chroma` holds the live content (253 MB `chroma.sqlite3`). DA row count
unchanged (5003 before and after) — only the derived index copies were removed.

## Specification Links

(Carried forward from the GO'd proposal `-006`.)

- `SPEC-2098` (Deliberation Archive read path must degrade, not crash).
- `GOV-08` (canonical store is `groundtruth.db`; chroma is a regenerable derived index).
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (one canonical chroma index; no divergent aliases).
- `SPEC-DA-DOCTOR-CHECK` (DA read-surface health).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (all changes in-root).
- `GOV-STANDING-BACKLOG-001` (WI-4429).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Spec-to-Test Mapping

| Spec / requirement | Derived test | Result |
|---|---|---|
| `SPEC-2098` + `GOV-08` (HYG-048, crash) | `test_search_degrades_on_chroma_crash` — count()/query() raise -> returns `text_match`, no crash | PASS |
| `SPEC-2098` + `GOV-08` (HYG-048, hang) | `test_search_degrades_on_chroma_timeout` — stalling collection -> returns `text_match` in <3 s (timeout 0.3 s) | PASS |
| timeout primitive | `test_call_with_timeout_returns_value`, `..._raises_on_stall`, `..._propagates_error` | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (Area 3 config) | `test_canonical_chroma_dirname_reads_config`, `..._defaults_when_config_absent` | PASS |
| `SPEC-DA-DOCTOR-CHECK` (Area 2 benchmark CLI) | manual: `python scripts/benchmarks/cli.py run --benchmark deliberation_recall` | EXIT 0 |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (Area 3 dedup) | manual: strays removed, canonical intact, DA count 5003->5003 | PASS |

## Verification Commands and Observed Results

```
python -m pytest platform_tests/scripts/test_fab17_chroma_read_path.py -q
  -> 7 passed in 1.47s

python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py scripts/benchmarks/cli.py \
                     platform_tests/scripts/test_fab17_chroma_read_path.py
  -> All checks passed!

python -m ruff format --check <same three files>
  -> 3 files already formatted

python scripts/benchmarks/cli.py run --benchmark deliberation_recall
  -> EXIT 0; run_id 20260612-144205

# Area 3 dedup evidence
DA_COUNT_BEFORE 5003 ; .groundtruth-chroma sqlite_bytes=253829120 (canonical, retained)
chroma sqlite_bytes=212992 (removed) ; groundtruth-kb/.groundtruth-chroma sqlite_bytes=188416 (removed)
After: chroma exists=False ; groundtruth-kb/.groundtruth-chroma exists=False ; .groundtruth-chroma exists=True
DA_COUNT_AFTER 5003
```

Note: this verification host runs Python 3.14, where `HAS_CHROMADB` is gated False, so the production search
path already falls back to LIKE; the crash/timeout tests inject fake collections to exercise the guarded
paths directly (valid for the Python <3.14 deployments where chroma is live).

## Acceptance Criteria Check

1. **Area 1** — `search_deliberations` degrades to text-match on chroma exception OR timeout (no crash, no
   multi-minute hang); mock-collection tests pass. PASS
2. **Area 2** — benchmark CLI runs under its documented (script-form) invocation without hanging. PASS (exit 0)
3. **Area 3** — single canonical `.groundtruth-chroma` index; both stray stores removed; canonical
   `groundtruth.db` / DA records unchanged (5003 = 5003). PASS
4. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file. PASS

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` (chartering advisory; HYG-048).
- `DELIB-FAB17-REMEDIATION-20260610` (owner fix-scope + determined fixes).
- `bridge/gtkb-fab-17-da-chroma-read-path-005.md` (Codex corrective NO-GO requiring full duplicate-store
  target-path coverage; addressed by -006).

## Owner Decisions / Input

Fix-scope owner decisions were collected via `AskUserQuestion` on 2026-06-10 and persisted to
`DELIB-FAB17-REMEDIATION-20260610` (HYG-048 = wrap count() + timeout/retry; benchmark CLI repair; resolve
chroma triplication to one canonical index). No new owner decision was required for implementation; this
report carries forward those decisions. The owner-present FABLE drive (2026-06-12) authorized autonomous
execution of GO'd threads.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/db.py` — Area 1 search hardening + Area 3 canonical-dirname resolver.
- `scripts/benchmarks/cli.py` — Area 2 script-form bootstrap.
- `config/governance/chroma-read-path.toml` — NEW; Area 3 canonical-store declaration.
- `platform_tests/scripts/test_fab17_chroma_read_path.py` — NEW; spec-derived tests (7).
- Removed: `chroma/`, `groundtruth-kb/.groundtruth-chroma/` (Area 3 stray-store dedup).

## Recommended Commit Type

`fix:` — repairs the DA search crash/hang, the benchmark CLI script-form crash, and the chroma
triplication; includes a small `feat:`-class addition (the chroma read-path config + the bounded
timeout/retry guard).
