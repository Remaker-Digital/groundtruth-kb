NO-GO

# Loyal Opposition Review - GTKB-REHEARSAL-INVENTORY-PERF

Reviewed: 2026-04-27
Subject: `bridge/gtkb-rehearsal-inventory-perf-001.md`
Scope: `_inventory.py` walk performance and exclude-list extension

## Claim

NO-GO. The proposal correctly identifies the timeout risk, but the proposed default exclusions are too broad for the authoritative inventory lane and would hide migration-relevant evidence, especially `logs/`.

## Evidence

- `_inventory.py` currently builds the authoritative file inventory from `root.rglob("*")`, computes SHA-256, size, and mtime for every non-excluded file, and records `ignored_top_level`: `scripts/rehearse/_inventory.py:50` to `:80`, `:241` to `:256`.
- The runtime manifest currently excludes only `.env`, `.env.local`, `secrets/`, `groundtruth-artifacts/secrets/`, and `.tmp.driveupload/`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml:44` to `:50`.
- The proposal would add `logs` to `_DEFAULT_IGNORED_TOP_LEVEL`, describing it as historical deploy logs and saying Slice 9 inventories it separately: `bridge/gtkb-rehearsal-inventory-perf-001.md:79` and `:132`.
- Live `logs/` exists and contains production/build evidence, including many `build-*.log` files and a `visual-evidence` subtree. A local count found 1,239 files under `logs/`.
- Slice 9 is not a verified owner for this surface. Its current proposal was just returned `NO-GO`, partly because its production-effects inventory omitted core deployment surfaces.
- The Phase 8 plan requires the rehearsal inventory to classify every file under the legacy mixed root with hash, size, timestamp, classification source, and planned action, and requires ignored files to be written to `dryrun-ignored.json` so the rehearsal cannot silently drop data: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:96` to `:105`.
- The proposal claims both `metrics.walk_walltime_seconds` and `metrics.hash_walltime_seconds` in scope, but the implementation sketch records only a single combined `walk_walltime_seconds`: `bridge/gtkb-rehearsal-inventory-perf-001.md:31`, `:91` to `:106`.

## Risk / Impact

Excluding cache directories such as `.codex_pydeps`, `.venv`, `.pytest_cache`, `.ruff_cache`, and `.mypy_cache` is likely reasonable, but excluding `logs/` from the default authoritative inventory would remove real project evidence from the hash set without a replacement verified lane. That conflicts with the Phase 8 non-silent-drop requirement and weakens the pre/post hash stability gate.

## Required Revision

- Remove `logs` from the default ignore proposal unless a governing artifact explicitly classifies it as transient and the inventory emits a `dryrun-ignored.json` entry with rationale.
- Separate transient cache exclusions from migration-relevant evidence exclusions. `.codex_pydeps`, `.venv`, `venv`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, and `htmlcov` can be proposed as cache/transient defaults.
- Add explicit ignored-file reporting if the lane excludes additional top-level directories beyond manifest `excluded_paths`.
- Either implement both promised metrics (`walk_walltime_seconds` and `hash_walltime_seconds`) or narrow the proposal to one accurately named combined timing metric.
- Reconsider directory pruning. `Path.rglob("*")` still descends into ignored top-level directories before the current top-level skip check; an `os.walk`/`scandir` prune may be needed if enumeration, not hashing, remains material.

## Decision Needed From Owner

None. Prime should revise the proposal before implementation.
