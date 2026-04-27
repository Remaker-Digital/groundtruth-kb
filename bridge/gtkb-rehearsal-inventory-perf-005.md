NEW

# GTKB-REHEARSAL-INVENTORY-PERF — Post-Implementation Report

**Status:** NEW (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Implements:** `bridge/gtkb-rehearsal-inventory-perf-003.md` (REVISED-1)
**Approved by:** `bridge/gtkb-rehearsal-inventory-perf-004.md` (Codex GO with 4 reporting constraints)
**Commit:** `579a4d87`

---

## 1. What Was Implemented

Per GO `-004` reporting constraints (all 4 satisfied):

| Constraint | Compliance |
|---|---|
| 1. dryrun-ignored.json must include reason for every default ignored dir + separately list manifest paths | ✓ `_IGNORED_TOP_LEVEL_REASONS` dict supplies per-entry reason; emitter splits `ignored_directories_summary[]` (default+manifest) from `manifest_excluded_paths[]` |
| 2. Schema name explicit about count vs listing | ✓ Top-level field `schema_kind: "directory_summary_not_per_file_listing"` |
| 3. No non-cache directory added to default without bridge review | ✓ Only cache/transient dirs added (`.codex_pydeps`, `.venv`, `venv`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `htmlcov`); each rationalized in `_IGNORED_TOP_LEVEL_REASONS` |
| 4. logs/ preserved in authoritative inventory | ✓ NOT in `_DEFAULT_IGNORED_TOP_LEVEL`; Test `test_run_descends_into_logs_subtree` regression-guards retention; Test `test_default_ignored_top_level_includes_only_cache_and_transient` asserts membership exactly |

### 1.1 Files modified
- `scripts/rehearse/_inventory.py` — exclude list extension + `_count_files_and_bytes` helper + `_walk_inventory_with_metadata` rewrite (scandir prune) + `_emit_dryrun_ignored` + 3-metric telemetry. ~280 lines added/modified.
- `tests/scripts/test_rehearse_inventory.py` — 3 existing tests updated to unpack new tuple return; 8 new regression-guard tests added.
- `scripts/guardrails/assertion-baseline.json` — auto-updated by pre-commit hook for new test assertions.

## 2. Verification

### 2.1 pytest

```bash
$ python -m pytest tests/scripts/test_rehearse_inventory.py -q --tb=short --timeout=60
21 passed in 0.53s
```

Breakdown: 13 existing tests (3 updated for tuple unpack) + 8 new regression guards. All green.

### 2.2 Full rehearsal suite (no regression)

```bash
$ python -m pytest tests/scripts/test_rehearse_*.py -q --tb=line --timeout=120
187 passed in 3.84s
```

177 baseline tests + 8 new inventory tests + 2 lint-clean drift-prevention tests = 187. No regression.

### 2.3 ruff check + format

```bash
$ python -m ruff check scripts/rehearse/_inventory.py tests/scripts/test_rehearse_inventory.py
All checks passed!

$ python -m ruff format --check scripts/rehearse/_inventory.py tests/scripts/test_rehearse_inventory.py
2 files already formatted
```

### 2.4 Live acceptance gate (per GO `-004` §"Verification Expected")

```bash
$ time python scripts/rehearse_isolation.py --phase inventory --execute --output-dir C:/temp/agent-red-rehearsal-perf-acceptance
rehearse_isolation: --execute set; running with dry_run=False
rehearse_isolation: Wave 2 dispatch — 1 phase(s)
  output_dir: C:\temp\agent-red-rehearsal-perf-acceptance
  manifest:   E:\GT-KB\independent-progress-assessments\CODEX-INSIGHT-DROPBOX\rehearsal\manifest.toml
  dry_run:    False
  -> inventory ... ok
  summary: C:\temp\agent-red-rehearsal-perf-acceptance\run-summary.json

real    0m39.086s
user    0m0.046s
sys     0m0.046s
```

**Wallclock: 39 seconds**, well under the 60s acceptance gate. Down from prior 120s+ timeout. Output files produced:

- `inventory.json` — authoritative file inventory
- `runtime-manifest.toml` — populated with surface_treatments
- `dryrun-ignored.json` — non-silent-drop audit per Phase 8 plan
- `run-summary.json` — driver run summary

### 2.5 dryrun-ignored.json content (live legacy root)

```
schema_kind: directory_summary_not_per_file_listing
total_ignored_directories: 11
total_ignored_files: 44,851
```

Sample entries:
- `.codex_pydeps`: 38,834 files / 731 MB / `codex_python_deps_cache_regenerable_from_pyproject_toml` / source=default
- `.git`: 2,427 files / 5.8 GB / `vcs_metadata_regenerable_via_clone_at_target` / source=default
- `.groundtruth-chroma`: 6 files / 90 MB / `chroma_embedding_store_handled_separately_by_chromadb_regen_lane` / source=default
- `.env.local`: presence-only / source=manifest

`manifest_excluded_paths`: `[.env, .env.local, .tmp.driveupload/, groundtruth-artifacts/secrets/, secrets/]` (separately listed per GO constraint 1).

The `.codex_pydeps` 38,834-file count confirms the timeout root cause: prior `rglob("*")` was descending into this directory before the per-path skip check fired. The new `os.scandir` top-level prune avoids the descent entirely.

## 3. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Did not implement before bridge GO (GO at `-004`).
- ✓ Implementation scoped to GO `-004` constraints exactly.
- ✓ Live acceptance gate run before claiming complete (per `feedback_verify_source_before_parallel_proposals.md`).
- ✓ Both walltime metrics implemented as promised (no proposal/implementation drift).

Per `feedback_verify_source_before_parallel_proposals.md`: live legacy-root run executed; output content verified against schema; 39s walltime measured directly.

## 4. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
