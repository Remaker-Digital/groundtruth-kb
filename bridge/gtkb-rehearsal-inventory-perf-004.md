GO

# Loyal Opposition Review - GTKB-REHEARSAL-INVENTORY-PERF REVISED-1

Reviewed: 2026-04-27
Subject: `bridge/gtkb-rehearsal-inventory-perf-003.md`
Scope: `_inventory.py` walk performance, cache-only exclusions, ignored summary, and timing telemetry

## Claim

GO, with reporting constraints. The revision fixes the prior blocking defect by retaining `logs/`, limiting new default exclusions to cache/transient directories, adding ignored-output reporting, and pruning ignored top-level directories before descent.

## Evidence

- The revision explicitly removes `logs/` from `_DEFAULT_IGNORED_TOP_LEVEL` and adds a test requiring `logs/deploy-test.log` to remain in inventory.
- The revised default exclusions are cache/transient surfaces: `.codex_pydeps`, `.venv`, `venv`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, and `htmlcov`.
- Live checkout has cache directories that plausibly explain the timeout, including `.codex_pydeps` with 38,834 files.
- The revision adds `dryrun-ignored.json`, `walk_walltime_seconds`, `hash_walltime_seconds`, `ignored_summary_walltime_seconds`, and an `os.scandir` top-level prune strategy.

## Required Implementation Constraints

- `dryrun-ignored.json` must include a reason for every default ignored directory and must separately list manifest-declared excluded paths.
- If the output summarizes ignored directories by count rather than listing every ignored file path, make that explicit in the schema name or documentation so it is not misrepresented as a per-file ignored manifest.
- Do not add any non-cache directory to `_DEFAULT_IGNORED_TOP_LEVEL` without a new bridge review.
- Preserve `logs/` in the authoritative inventory until a separate verified artifact assigns it a different treatment.

## Risk / Impact

Low after the constraints. The design reduces runtime risk without dropping migration-relevant evidence from the authoritative inventory.

## Verification Expected

- `python -m pytest tests/scripts/test_rehearse_inventory.py -q --tb=short`
- `python scripts/rehearse_isolation.py --phase inventory --execute --output-dir <sandbox>` completes under the revised gate and emits `inventory.json`, `runtime-manifest.toml`, `dryrun-ignored.json`, and `result.json`.
- `result.json` includes separate walk/hash/ignored-summary timings.

## Decision Needed From Owner

None.
