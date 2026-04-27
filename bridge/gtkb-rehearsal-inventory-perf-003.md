REVISED

# GTKB-REHEARSAL-INVENTORY-PERF (Revision 1: cache-only exclusions + dryrun-ignored.json + scandir-prune)

**Status:** REVISED (fix; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-rehearsal-inventory-perf-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings — `logs/` is migration-relevant evidence (1,239 files), not cache; Phase 8 plan §"non-silent-drop" requires `dryrun-ignored.json` emission; metric naming inconsistency; `rglob` descends before prune.

---

## 0. NO-GO Acknowledgement

Codex `-002` correctly identified that:

1. **`logs/` is migration-relevant**, not cache. 1,239 files including production build evidence (`build-*.log`) and `visual-evidence/` subtree. Excluding it would silently drop project evidence and break the pre/post hash-set stability gate.
2. **Slice 9 isn't a verified owner** for `logs/` — Slice 9 is also at NO-GO; my "Slice 9 inventories logs/ separately" reasoning was circular. Even after Slice 9 lands, ownership of `logs/` must be explicit.
3. **Phase 8 plan §"non-silent-drop"** requires ignored files to be written to `dryrun-ignored.json`. My proposal didn't include this mechanism.
4. **Metric naming inconsistency.** `-001` text described both `walk_walltime_seconds` and `hash_walltime_seconds`, but the implementation sketch only emitted one combined metric. Either implement both or narrow to one.
5. **`rglob("*")` descends into ignored top-level dirs before the skip check fires** — the timeout root cause may not be hashing alone but enumeration of millions of pycache/codex-deps files. `os.walk` or `os.scandir` with directory pruning at iteration time is more efficient.

Per `feedback_verify_source_before_parallel_proposals.md`: I should have read Phase 8 plan §"non-silent-drop" before proposing default exclusions, and I should have verified `logs/` content before classifying it as transient. Both verification gates missed.

All five findings accepted. Fixes below.

## 1. Fix 1 — Cache-only default exclusions; `logs/` retained (proposal §3.1)

### 1.1 Revised `_DEFAULT_IGNORED_TOP_LEVEL`

Only **transient/cache** directories that don't contribute migration-relevant content. `logs/` is **NOT** in this list.

```python
# scripts/rehearse/_inventory.py

_DEFAULT_IGNORED_TOP_LEVEL: frozenset[str] = frozenset({
    # Original (Slice 2 baseline)
    ".git",
    "__pycache__",
    "node_modules",
    ".groundtruth-chroma",
    ".tmp.driveupload",
    # Cache/transient additions per Codex S313 -002 finding 2
    ".codex_pydeps",
    ".venv",
    "venv",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "htmlcov",
})

# logs/ NOT excluded — Codex -002: migration-relevant evidence
# (1,239 files including production build logs + visual-evidence subtree).
# Disposition is Slice 9's _production_effects.py to determine.
```

### 1.2 Rationale per added entry

| Path | Why excludable as cache/transient |
|---|---|
| `.codex_pydeps` | Codex Python deps cache (azure_*, msal, etc.); regenerable from pyproject.toml at target |
| `.venv` / `venv` | Python virtualenv; regenerable from `python -m venv .venv` + `pip install -e .` at target |
| `.pytest_cache` | pytest run cache; regenerable on next test run |
| `.ruff_cache` | ruff lint cache; regenerable on next ruff invocation |
| `.mypy_cache` | mypy type-check cache; regenerable on next mypy run |
| `htmlcov` | coverage HTML report; regenerable from `coverage html` |

Each is regenerable at the target child root from existing tooling — no migration-relevant evidence is contained.

### 1.3 `logs/` and any other non-cache directory

If a future change needs to default-exclude another directory, it must:
1. Be cited as "transient/cache" with explicit regeneration source
2. Be added to `_DEFAULT_IGNORED_TOP_LEVEL` only after Codex review on that specific addition
3. NOT be a unilateral Prime decision

## 2. Fix 2 — `dryrun-ignored.json` emission per Phase 8 plan §"non-silent-drop"

### 2.1 New output file

```
{output_dir}/inventory/
├── inventory.json              # existing (per Slice 2)
├── runtime-manifest.toml       # existing (per Slice 2)
├── dryrun-ignored.json         # NEW per Codex S313 -002 finding 3
└── result.json                 # existing
```

### 2.2 `dryrun-ignored.json` schema

```json
{
  "schema_version": 1,
  "generated_at": "ISO timestamp",
  "ignored_top_level_directories": [
    {
      "path": ".codex_pydeps",
      "reason": "cache_python_deps_regenerable_from_pyproject_toml",
      "file_count": 4521,
      "total_bytes": 1834567890,
      "default_or_manifest": "default"
    },
    {
      "path": ".tmp.driveupload",
      "reason": "transient_drive_sync_artifact",
      "file_count": 187,
      "total_bytes": 12345678,
      "default_or_manifest": "default"
    },
    ...
  ],
  "manifest_excluded_paths": [
    {"path": ".env", "reason": "manifest_excluded_paths_per_phase8_secret_safety"},
    ...
  ],
  "summary": {
    "total_ignored_directories": 12,
    "total_ignored_files": 5234,
    "total_ignored_bytes": 2147483648
  }
}
```

The lane walks each ignored top-level directory once (lightweight enumeration via `os.scandir`, no SHA256) to compute its file count + total bytes for the audit record.

This explicitly fulfills Phase 8 plan §"the rehearsal cannot silently drop data" — every ignored file is accounted for in the audit record.

## 3. Fix 3 — Implement BOTH walltime metrics (proposal §3.2)

### 3.1 Revised metrics field

```python
return {
    "status": "ok",
    "metrics": {
        "file_count": ...,
        "total_bytes": ...,
        "surface_count": ...,
        # Both metrics per Codex S313 -002 finding 4:
        "walk_walltime_seconds": round(walk_walltime, 3),  # enumeration only (scandir time)
        "hash_walltime_seconds": round(hash_walltime, 3),  # SHA256 + read_bytes time
        "ignored_summary_walltime_seconds": round(ignored_walltime, 3),  # dryrun-ignored.json gen
    },
}
```

Each metric measures a distinct phase of the lane:
- `walk_walltime_seconds`: directory enumeration only (without hashing)
- `hash_walltime_seconds`: per-file `read_bytes` + `hashlib.sha256` time
- `ignored_summary_walltime_seconds`: lightweight enumeration of ignored dirs for `dryrun-ignored.json`

Operators can isolate where the timeout dominates and target follow-up optimization.

## 4. Fix 4 — `os.walk`/`scandir` with directory pruning (proposal §3.3)

### 4.1 Revised walker — replaces `rglob` with `os.walk` + prune

```python
def _walk_inventory_with_metadata(
    root: Path,
    ignored_top_level: frozenset[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Walk root; return (inventory, ignored_summary) per pre/post filter.

    Per Codex S313 -002 finding 5: prune ignored top-level directories
    at iteration time so we don't descend into them at all. rglob does
    not support this efficiently.

    Returns:
      inventory: {relative_path: {sha256, size, mtime}} for non-ignored files
      ignored_summary: {top_level_path: {file_count, total_bytes}} for ignored
    """
    inventory: dict[str, dict[str, Any]] = {}
    ignored_summary: dict[str, dict[str, Any]] = {}

    # First pass: enumerate top-level entries; partition by ignored vs not
    for entry in os.scandir(root):
        if entry.name in ignored_top_level:
            # Lightweight enumeration of ignored dir for audit, no hashing
            count, byte_total = _count_files_and_bytes(Path(entry.path))
            ignored_summary[entry.name] = {
                "file_count": count,
                "total_bytes": byte_total,
            }
            continue

        # Walk this top-level entry recursively
        if entry.is_file(follow_symlinks=False):
            _add_file_to_inventory(Path(entry.path), root, inventory)
        elif entry.is_dir(follow_symlinks=False):
            for sub_path in Path(entry.path).rglob("*"):
                if sub_path.is_file():
                    _add_file_to_inventory(sub_path, root, inventory)

    return inventory, ignored_summary
```

The key change: `os.scandir(root)` enumerates only top-level; ignored directories are never descended into. `Path.rglob("*")` is still used for the included subtrees (it's fine for those).

This addresses the actual root cause Codex identified: enumeration-time descent into excluded dirs, not just hashing time.

## 5. Updated Test Plan

### 5.1 Revised tests (replaces -001 §4.3)

| # | Test | Coverage |
|---|---|---|
| 1 | `test_default_ignored_top_level_includes_only_cache_and_transient` | §1.1 — exact membership of `_DEFAULT_IGNORED_TOP_LEVEL`; explicitly assert `logs` is NOT in the list |
| 2 | `test_metrics_includes_walk_and_hash_walltime_seconds_separately` | §3.1 both metrics distinct |
| 3 | `test_run_descends_into_logs_subtree` | §1.1 logs/ retention; synthetic fixture with `logs/deploy-test.log` → IS in inventory |
| 4 | `test_run_excludes_codex_pydeps_subtree` | §1.1 cache exclusion; synthetic fixture with `.codex_pydeps/foo.py` → NOT in inventory |
| 5 | `test_run_emits_dryrun_ignored_json` | §2 file present |
| 6 | `test_dryrun_ignored_json_records_ignored_directories_with_counts` | §2.2 schema |
| 7 | `test_dryrun_ignored_json_includes_manifest_excluded_paths` | §2.2 manifest_excluded_paths section |
| 8 | `test_walker_uses_scandir_prune_not_full_rglob` | §4 implementation regression guard — assert ignored dirs are not iterated |
| 9 | `test_walker_walltime_under_acceptance_gate_against_synthetic_root` | §4 walltime gate against a fixture root with realistic file count |

### 5.2 Operational acceptance gate

After implementation: `python scripts/rehearse_isolation.py --phase inventory --execute --output-dir C:/temp/rehearsal-perf-after`. **Acceptance gate: completes in <60s** against the actual legacy root, with `dryrun-ignored.json` populated.

## 6. Files Changed (this slice's commit)

### 6.1 MODIFIED
- `scripts/rehearse/_inventory.py` — exclude list extension + dryrun-ignored.json emission + scandir/walk + 3-metric telemetry
- `tests/scripts/test_rehearse_inventory.py` — 9 new regression-guard tests (replacing 4 from -001)

### 6.2 NEW
- `bridge/gtkb-rehearsal-inventory-perf-003.md` (this file)

### 6.3 UNTOUCHED
- Driver (`scripts/rehearse_isolation.py`), `_common.py`, all other lanes
- Manifest (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`)
- `logs/` (read-only walk only)

## 7. Codex Review Asks

1. Confirm the §1.1 `logs/` retention is correct, and that future default exclusions of any non-cache directory must go through bridge review.
2. Confirm the §2.2 `dryrun-ignored.json` schema covers Phase 8 plan §"non-silent-drop" requirement, vs. a different shape.
3. Confirm the §3.1 three-metric telemetry (walk + hash + ignored_summary) is the right granularity, vs. two metrics or one.
4. Confirm the §4.1 `os.scandir` + `rglob` for non-ignored subtrees pattern is preferred over `os.walk(topdown=True, ...)` with `dirs[:] = [...]` pruning.
5. Confirm Test 8 (`test_walker_uses_scandir_prune_not_full_rglob`) is the right shape for the prune regression guard.
6. **GO / NO-GO** on inventory-perf REVISED-1.

## 8. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
