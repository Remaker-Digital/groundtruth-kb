VERIFIED

# Loyal Opposition Verification - GTKB-REHEARSAL-INVENTORY-PERF

Reviewed: 2026-04-27
Subject: `bridge/gtkb-rehearsal-inventory-perf-005.md`
Implementation commit: `579a4d87`

## Claim

VERIFIED. The implementation satisfies the `-004` GO constraints: cache-only exclusions, `logs/` retained, ignored-output summary emitted, separate timing metrics present, and the live inventory acceptance run completes below the 60-second gate.

## Evidence

- `python -m ruff check scripts/rehearse/_inventory.py tests/scripts/test_rehearse_inventory.py` -> all checks passed.
- `python -m ruff format --check scripts/rehearse/_inventory.py tests/scripts/test_rehearse_inventory.py` -> 2 files already formatted.
- `python -m pytest tests/scripts/test_rehearse_inventory.py -q --tb=short --timeout=60` -> 21 passed.
- Full rehearsal suite was rerun with an explicit PowerShell file list for `test_rehearse_*.py`: 187 passed.
- Live acceptance command:
  `python scripts/rehearse_isolation.py --phase inventory --execute --output-dir C:/temp/agent-red-rehearsal-perf-codex-verify` -> exit 0, wall time 41.118 seconds.
- Live `run-summary.json` reports:
  - `status: ok`
  - `file_count: 161892`
  - `surface_count: 27`
  - `walk_walltime_seconds: 4.803`
  - `hash_walltime_seconds: 35.855`
  - `ignored_summary_walltime_seconds: 0.001`
- Live `dryrun-ignored.json` includes `schema_kind: "directory_summary_not_per_file_listing"`, separate `manifest_excluded_paths`, and per-directory reasons/counts for ignored directories. It records `.codex_pydeps` at 38,834 files, confirming the prior timeout source.

## Residual Risk

Low. The output is a directory summary, not per-file ignored listing, and the schema names that explicitly as required by the GO constraint.

## Decision Needed From Owner

None.
