NEW

# GTKB-REHEARSAL-INVENTORY-PERF — `_inventory.py` walk performance + exclude-list extension

**Status:** NEW (fix; awaits Codex GO)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Triggered by:** Loyal Opposition findings (S313, owner-forwarded), P2 finding: "Inventory execution is a performance/runnability concern. python scripts/rehearse_isolation.py --phase inventory --execute timed out after 120s, and full --phase all --execute timed out after 244s."

bridge_kind: prime_proposal
work_item_ids: [GTKB-ISOLATION-016]
spec_ids: []
target_project: agent-red
implementation_scope: scripts/rehearse/_inventory.py — extend `_DEFAULT_IGNORED_TOP_LEVEL` + add walltime telemetry; analysis-first

---

## Prior Deliberations

- Slice 2 GO at `bridge/gtkb-isolation-016-phase8-wave2-slice2-004.md` established `_DEFAULT_IGNORED_TOP_LEVEL = frozenset({".git", "__pycache__", "node_modules", ".groundtruth-chroma", ".tmp.driveupload"})`.
- Slice 2 `-003` REVISED §F1 fix: single-pass walk collects hash + size + mtime together (replaces a hash-only `hash_set_walk()` two-pass with TOCTOU concerns).

The Slice 2 design assumed the legacy root would be ~order-of-thousands files. Empirical state at S313 includes additional large transient/cache directories not in the original exclude list.

## 1. Scope

Two surgical changes to `scripts/rehearse/_inventory.py`:

1. **Extend `_DEFAULT_IGNORED_TOP_LEVEL`** to include large transient/cache directories observed in the legacy root that don't belong in a migration inventory.
2. **Add walltime telemetry** to the inventory result so future regressions are visible (`metrics.walk_walltime_seconds`, `metrics.hash_walltime_seconds`).

**Not in scope:** parallelizing the walk, switching to `os.scandir`, incremental hashing, hash-skip-by-size-and-mtime caching. Those are larger optimizations that can land if §1 doesn't fully resolve the timeout.

## 2. Evidence (Codex-cited; not yet directly reproduced by Prime)

```
python scripts/rehearse_isolation.py --phase inventory --execute   # timed out after 120s
python scripts/rehearse_isolation.py --phase all --execute         # timed out after 244s
```

### 2.1 Probable root cause analysis

`_walk_inventory_with_metadata()` in `_inventory.py:50-86` walks `LEGACY_ROOT` (= `E:/GT-KB/`) via `path.rglob("*")`, reading bytes for SHA256 of every file. Excluded top-level dirs:

```python
_DEFAULT_IGNORED_TOP_LEVEL = frozenset({
    ".git", "__pycache__", "node_modules",
    ".groundtruth-chroma", ".tmp.driveupload",
})
```

Top-level directories in `E:/GT-KB/` likely NOT excluded but probably should be:

| Directory | Why exclude | Estimated file count |
|---|---|---|
| `.codex_pydeps/` | Codex Python deps cache (azure_*, msal, etc.) | ~thousands |
| `.venv/` (if present) | Python virtualenv | ~thousands |
| `logs/` | Historical deploy logs (`deploy-*.log`) — Slice 9 inventories these separately | ~hundreds |
| `.tmp.driveupload/` | Already excluded ✓ | n/a |
| `.groundtruth-chroma/` | Already excluded ✓ | n/a |

**Hypothesis:** the timeout is dominated by enumerating + hashing `.codex_pydeps/` (Python package distributions including large `.dist-info/` and `.so/.pyd` binaries). At default 5-10ms per file for SHA256 + stat, 5,000+ unexcluded transient files = 25-50+ seconds dominated by this bucket.

The hypothesis can be confirmed by running with `--phase inventory --execute --output-dir <sandbox>` and timing each top-level directory's contribution. The proposal commits to instrumenting walltime; the fix commits to extending the exclude list with these candidates.

## 3. Proposed Change

### 3.1 Extend `_DEFAULT_IGNORED_TOP_LEVEL`

```python
# scripts/rehearse/_inventory.py
_DEFAULT_IGNORED_TOP_LEVEL: frozenset[str] = frozenset({
    ".git",
    "__pycache__",
    "node_modules",
    ".groundtruth-chroma",
    ".tmp.driveupload",
    # Added per LO P2 finding S313: transient/cache dirs that bloat
    # the inventory walk without contributing migration-relevant
    # file content.
    ".codex_pydeps",
    ".venv",
    "venv",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "logs",  # historical deploy logs; inventoried separately by Slice 9
    "htmlcov",  # coverage reports
})
```

### 3.2 Add walltime telemetry

Wrap the walk in a `time.perf_counter()` block; emit walltime as part of metrics:

```python
def run(...) -> dict[str, Any]:
    ...
    walk_start = time.perf_counter()
    files = _walk_inventory_with_metadata(root, excluded_top)
    walk_walltime = time.perf_counter() - walk_start
    ...
    return {
        "status": "ok",
        ...
        "metrics": {
            "file_count": ...,
            "total_bytes": ...,
            "surface_count": ...,
            "walk_walltime_seconds": round(walk_walltime, 3),
        },
        ...
    }
```

The `walk_walltime_seconds` metric surfaces in `result.json` so future regressions are visible in dashboard / CI / operator inspection.

### 3.3 No algorithm changes

Stay with single-pass `rglob("*")` + per-file SHA256. If §3.1's exclude extension doesn't reduce walltime sufficiently, follow-up bridge proposes:

- Switch to `os.walk` with directory-prune at iteration time (avoids descending into excluded dirs)
- Parallel hashing via `concurrent.futures.ThreadPoolExecutor`
- Hash-skip-by-stat caching (only re-hash if `(size, mtime)` differs from prior run)

These are deferred — the LO finding doesn't establish that they're needed yet.

## 4. Test Plan

### 4.1 Pre-fix baseline

Direct timing measurement (this proposal authorizes the measurement as part of analysis):

```bash
python scripts/rehearse_isolation.py --phase inventory --execute --output-dir C:/temp/rehearsal-perf-baseline
# Measure walltime, capture metrics.walk_walltime_seconds (after §3.2 lands)
```

### 4.2 Post-fix verification

After §3.1 + §3.2 land:

- Re-run `python scripts/rehearse_isolation.py --phase inventory --execute --output-dir C:/temp/rehearsal-perf-after`. **Acceptance gate: completes in <60s** (well under the 120s timeout LO observed).
- `result.json` contains `metrics.walk_walltime_seconds`.
- All 13 existing `test_rehearse_inventory.py` tests pass unchanged.

### 4.3 New regression guards

| # | Test | Coverage |
|---|---|---|
| 1 | `test_default_ignored_top_level_includes_codex_pydeps_and_venv` | §3.1 exclude list extension is mechanical; assert membership |
| 2 | `test_metrics_includes_walk_walltime_seconds` | §3.2 telemetry present |
| 3 | `test_walk_excludes_codex_pydeps_subtree` | Synthetic fixture with `.codex_pydeps/foo.py` → not in inventory |
| 4 | `test_walk_excludes_logs_subtree` | Synthetic fixture with `logs/deploy-test.log` → not in inventory |

Tests 3-4 use the existing `inventory_root=` fixture parameter.

### 4.4 Operational gate

A subsequent post-impl report MUST include actual walltime measurement against the live legacy root. If the measurement still exceeds 60s, file a follow-up bridge for §3.3 algorithm options.

## 5. Files Changed

### 5.1 MODIFIED
- `scripts/rehearse/_inventory.py` — exclude list extension + walltime telemetry.
- `tests/scripts/test_rehearse_inventory.py` — 4 new regression-guard tests.

### 5.2 NEW
- `bridge/gtkb-rehearsal-inventory-perf-001.md` (this file).

### 5.3 UNTOUCHED
- Driver (`scripts/rehearse_isolation.py`), `_common.py`, all other lanes.
- Manifest (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`).
- Live transient directories themselves — never written by the rehearsal.

## 6. Out of Scope

- Algorithm-level optimization (parallel hashing, scandir, incremental). Deferred to follow-up if §3.1 doesn't suffice.
- Changing the `_inventory.py` output schema beyond adding a metrics field.
- Manifest-level `excluded_paths` changes (the manifest's `excluded_paths` list is consumed alongside `_DEFAULT_IGNORED_TOP_LEVEL` per `_inventory.py:234-238`; this fix extends only the default fallback).
- Cross-platform exclude patterns (e.g., macOS `.DS_Store`); add only when project ships on macOS.

## 7. Codex Review Asks

1. Confirm the §3.1 exclude list extension is appropriate vs. risk of accidentally excluding a directory that contains migration-relevant content. Specifically: `logs/` contains deploy logs that Slice 9 inventories separately — the rehearsal walker excluding them is safe because Slice 9 owns that surface.
2. Confirm the §3.2 walltime telemetry placement (metrics field of result.json) is the right shape vs. emitting to a separate timing log.
3. Confirm the §4.4 acceptance gate (<60s for live legacy root walk) is the right threshold, vs. tighter (<30s) or looser (<120s).
4. Confirm the analysis-first stance — that §3 lands narrow exclude+telemetry now, with §3.3 algorithm options deferred to a follow-up bridge if measurement still shows the timeout — is preferred over filing a single bigger fix that includes algorithm changes upfront.
5. **GO / NO-GO** on this fix.

## 8. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
