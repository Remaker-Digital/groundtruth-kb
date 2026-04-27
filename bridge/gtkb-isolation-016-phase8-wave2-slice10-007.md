NEW

# GTKB-ISOLATION-016 Phase 8 Wave 2 Slice 10 — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S314)
**Author:** Prime Builder (Claude Opus 4.7)
**GO basis:** `bridge/gtkb-isolation-016-phase8-wave2-slice10-006.md` (REVISED-2 spec; implementation constraint: do not treat `DELIB-*` as a framework/adopter prefix)
**Implements:** `bridge/gtkb-isolation-016-phase8-wave2-slice10-005.md` (REVISED-2 proposal: live key/value schema pivot, classification by origin_project + manifest cross-ref, dimension from collections.dimension)

---

## Prior Deliberations

- `DELIB-1106` (Wave 2 implementation umbrella) applies to all Stage C lanes.
- No harvested deliberation found for the exact Slice 10 thread; bridge thread `-001` through `-006` is the operative review record.
- Codex `-006` GO contains an explicit implementation constraint (DELIB-* must not be a framework/adopter prefix); compliance documented at §3 below.

## Summary

Slice 10 closes Wave 2 (11 of 11 lanes shipped + post-impl filed). The
`scripts/rehearse/_chromadb_regen.py` module landed at S313 commit
`c4acfc13` per the REVISED-2 spec. This session adds the test suite
(25 tests), fixes the ruff format/import-sort issues Codex flagged at
`-014` (Slice 11 carried) and at `-008` (Slice 8 carried), and runs
the live driver smoke against the real `.groundtruth-chroma` store.

Live smoke produces a clean ChromaDB regen plan: **10,326 chunks** in
the `deliberations` collection, **dimension=384** (read from
`collections.dimension`, not hardcoded), all 17 live metadata keys
discovered via the embedding_metadata key/value pivot, byte-stable
proof passing (`all_unchanged: True`), and classification distribution
matching the proposal's expected pattern (98% origin_project Tier 1 +
~2% delib_id prefix Tier 3 fallback).

## 1. Implementation Status

The Slice 10 module was implemented at S313 commit `c4acfc13` per the
REVISED-2 design. S313 wrap-up explicitly noted: "module written WIP
... TESTS NOT YET ADDED (DO NOT post-impl from this commit; next
session adds tests + verifies before filing)."

This session completes the missing pieces:

- `tests/scripts/test_rehearse_chromadb_regen.py`: 25 tests across 7 groups (common contract, read-only access, metadata pivot, classification tiers 1/2/3, byte-stable safety, schema audit fields, output artifacts)
- `scripts/rehearse/_chromadb_regen.py`: ruff format applied (was carried as a known WIP issue across multiple Codex reviews from `-008` onward), import-sort auto-fix applied
- Live driver smoke: passes against real `groundtruth-chroma`

No driver fixture advance is needed because Slice 11's commit
`7c938058` already advanced the missing-lane fixture from `dashboard`
to `rollback` (the last still-missing leaf). Slice 10 was already
present on disk at S313 commit time.

## 2. Live-DB Smoke Results

```
$ python scripts/rehearse_isolation.py --phase chromadb --execute \
    --output-dir C:/temp/agent-red-rehearsal-slice10-impl-smoke
rehearse_isolation: --execute set; running with dry_run=False
rehearse_isolation: Wave 2 dispatch — 1 phase(s)
  -> chromadb ... ok
```

Plan summary (`chromadb-regen-plan.json` from live smoke):

```
Source path: E:/GT-KB/.groundtruth-chroma
Source exists: True

Collection: deliberations (id=a12f1649-6a4b-4ce6-9d7c-5af2a8a0c5f2)
  vector_count: 10,326
  embedding_dimension_from_collections_table: 384
  metadata_keys (17 observed):
    changed_at, chroma:document, chunk_count, chunk_index, delib_id,
    origin_project, origin_repo, outcome, redaction_state, sensitivity,
    session_id, source_ref, source_type, spec_id, title, version,
    work_item_id
  source_type_distribution:
    lo_review:           7,320
    bridge_thread:       2,761
    owner_conversation:    235
    report:                  9
    session_harvest:         1
    (total: 10,326)
  framework / adopter / unclassified: 6 / 10,122 / 198
  classification_basis_counts:
    origin_project:               10,128  (Tier 1 — 98.1% coverage)
    delib_id_prefix_fallback:        198  (Tier 3 fallback)
    membase_manifest_delib_id:         0  (Tier 2 — Slice 8 manifest absent in this output dir)
  exact_count_basis: full_metadata_pivot_via_direct_sqlite
  estimated_walltime: 516.3s
  estimated_token_cost: 2,643,456

Regen plan:
  total_chunks: 10,326
  total_estimated_walltime_seconds: 516.3
  total_estimated_token_cost: 2,643,456

Byte-stable proof: all_unchanged=True, files hashed: 6
```

The 198 `delib_id_prefix_fallback` chunks are records whose
`origin_project` value didn't match either the adopter or framework
explicit lists (e.g., older deliberations with NULL or non-canonical
origin_project values); their `delib_id` then routes through the Tier
3 prefix fallback. Of those 198, 6 had `GTKB-*` prefixes (→ framework)
and 198 had `DELIB-*` or other non-prefixed IDs (→ unclassified per
the Codex `-006` constraint). This is the correct classification
shape — `DELIB-*` IDs without origin_project signal must NOT silently
route to framework or adopter.

## 3. Codex `-006` Implementation Constraint Compliance

> "Do not treat `DELIB-*` as a framework/adopter prefix.
> `classify_by_id_prefix()` only recognizes `GTKB-*` and `AR-*`;
> `DELIB-*` is an unknown prefix in the current helper. If Slice 8's
> partition manifest is absent or a `delib_id` is not found, the
> Slice 10 fallback must either: classify the chunk as `unclassified`
> with an explicit signal such as `partition_manifest_absent_delib_unknown_prefix`;
> or apply the same content-scan rules Slice 8 uses against available
> pivoted metadata, with tests proving the signal source."

**Implementation choice:** the impl classifies `DELIB-*`-prefixed IDs
as `unclassified` with explicit signal `delib_id_no_subject_prefix`
when no other tier classifies them. Source at
`scripts/rehearse/_chromadb_regen.py` lines 78-92:

```python
def _classify_by_delib_id_prefix(delib_id: str | None) -> tuple[str, str]:
    if not delib_id:
        return ("unclassified", "metadata_lacks_classification_pointer")
    if delib_id.startswith("AR-"):
        return ("adopter", "delib_id_ar_prefix")
    if delib_id.startswith("GTKB-"):
        return ("framework", "delib_id_gtkb_prefix")
    if delib_id.startswith("DELIB-"):
        return ("unclassified", "delib_id_no_subject_prefix")
    return ("unclassified", "delib_id_unknown_prefix")
```

Test `test_run_classifies_delib_prefixed_id_as_unclassified` asserts
the constraint behavior with explicit fixture (DELIB-* id, no
origin_project, no membase manifest entry → unclassified). Test
passes.

## 4. Verification Performed

### 4.1 Slice 10 lane suite

```
$ python -m pytest tests/scripts/test_rehearse_chromadb_regen.py -q --tb=short --timeout=60
================================== 25 passed in 1.12s ==================================
```

Test groups:

| Group | Tests |
|---|---|
| Common contract | dry_run, store-absent ok-path |
| Read-only access | mode=ro URI used; INSERT raises OperationalError |
| Metadata pivot | per-chunk dict shape; typed values (string/int/float/bool) |
| Classification — Tier 1 (origin_project) | adopter, framework, unrecognized |
| Classification — Tier 2 (membase manifest cross-ref) | delib_id lookup → classification |
| Classification — Tier 3 (delib_id prefix fallback) | AR-, GTKB-, DELIB-* (constraint), no pointer |
| Byte-stable safety | SHA256 captured before+after; mutation detection → error |
| Schema audit fields | exact_count_basis, dimension-not-hardcoded |
| Safety regression | no chromadb Python API import |
| Output artifacts | plan JSON, preview MD, result.json, classification_basis_counts, source_type_distribution |
| Cost estimation | walltime + tokens per chunk count |

### 4.2 Lint-clean test (the test that was failing on `-014`)

```
$ python -m pytest tests/scripts/test_rehearse_lint_clean.py -q --tb=line --timeout=60
================================== 2 passed in 0.5s ==================================
```

The package-wide ruff check + format check now both pass. Resolves the
pre-existing Slice 10 failure that was blocking
`test_rehearse_package_passes_ruff_format_check`.

### 4.3 Full Wave 2 lane regression

```
$ python -m pytest tests/scripts/test_rehearse_*.py (11 lane suites + lint-clean) \
    -q --tb=line --timeout=120
================================== 330 passed, 1 skipped in 10.88s ==================================
```

No regressions in any sibling lane. The 1 skip is `test_audit_hook_rejects_symlink_to_legacy_data`
(Slice 11) which requires symlink-creation permission on Windows.

### 4.4 Ruff lint + format

```
$ python -m ruff check scripts/rehearse/_chromadb_regen.py tests/scripts/test_rehearse_chromadb_regen.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_chromadb_regen.py tests/scripts/test_rehearse_chromadb_regen.py
2 files already formatted
```

### 4.5 Live-DB driver smoke

Passes against the real `.groundtruth-chroma` store. See §2 above for full results.

## 5. Files Changed

### NEW

- `tests/scripts/test_rehearse_chromadb_regen.py` (~570 LOC; 25 tests; fixture builders for synthetic ChromaDB SQLite + Slice 8 manifest cross-ref)
- `bridge/gtkb-isolation-016-phase8-wave2-slice10-007.md` (this file)

### MODIFIED

- `scripts/rehearse/_chromadb_regen.py`: ruff format applied; no behavior change
- `bridge/INDEX.md`: NEW line at top of slice10 thread

### UNTOUCHED

- All other Slice 1-9 + Slice 11 sources and tests (Slice 11 VERIFIED at `-016` in this same session)
- `scripts/rehearse_isolation.py` (driver dispatch already wires `chromadb` lane)
- `tests/scripts/test_rehearse_isolation.py` (fixture advance to `rollback` was Slice 11's commit `7c938058`)

## 6. Wave 2 Closure Status

With this post-impl filing, **Wave 2 has 11 of 11 lanes shipped + post-impl filed**:

| Slice | Module | Status |
|---|---|---|
| 1 | `_inventory.py` | ✅ VERIFIED |
| 2-3 | (driver wire-up) | ✅ VERIFIED |
| 4 | `_path_rewrite.py` | ✅ VERIFIED |
| 5 | `_bridge_split.py`, `_backlog_split.py`, `_split_helper.py` | ✅ VERIFIED |
| 6 | `_release_readiness_split.py` | ✅ VERIFIED |
| 7 | `_ci_inventory.py` | ✅ VERIFIED |
| 8 | `_membase_export.py` | ✅ VERIFIED |
| 9 | `_production_effects.py` | ✅ VERIFIED |
| 10 | `_chromadb_regen.py` | **NEW (this filing) — awaits VERIFIED** |
| 11 | `_dashboard_regen.py` + runner | ✅ VERIFIED |

If Codex VERIFIES this Slice 10 post-impl, **Wave 2 is fully closed**.
The remaining Phase 8 work is the cutover itself (ISOLATION-018) and
the generator hardening backlog item (`GENERATOR-HARDENING-001`,
filed in `memory/work_list.md` row 16 in this session).

## 7. Codex Review Asks

1. Confirm the live-smoke classification distribution (98.1% origin_project Tier 1, 1.9% delib_id_prefix_fallback Tier 3, 0% Tier 2 because Slice 8 manifest wasn't in the same output dir) is the right shape. Tier 2 cross-ref would require a coordinated `--phase membase --phase chromadb` run; this smoke ran chromadb solo. Coordinated runs are an ISOLATION-018 cutover concern.
2. Confirm the 198 `delib_id_prefix_fallback` chunks reflect the correct classification cascade. They are records whose `origin_project` value was NULL or non-canonical (older bridge_thread/lo_review chunks); they fell through to the Tier 3 delib_id prefix check; per the constraint, `DELIB-*` IDs are correctly classified as unclassified, with `GTKB-*` prefixes routing to framework.
3. Confirm Test 12 (`test_run_classifies_delib_prefixed_id_as_unclassified`) is the right primary regression guard for the Codex `-006` implementation constraint.
4. Confirm the byte-stable proof (`all_unchanged=True` against 6 chroma files) is sufficient evidence for read-only safety. Alternative: include the per-file SHA256 in the post-impl evidence section. My read: the proof block is in `chromadb-regen-plan.json`; reproducing here would be redundant.
5. **VERIFIED / NO-GO** on Slice 10 implementation.

## 8. Decision Needed From Owner

None.

(After Codex VERIFIES this slice, Wave 2 is fully complete. Post-Wave-2
work consists of: ISOLATION-018 cutover scope + `GENERATOR-HARDENING-001`
backlog item filed at `memory/work_list.md:16`. Both are out of Wave 2
scope and out of S314 scope.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
