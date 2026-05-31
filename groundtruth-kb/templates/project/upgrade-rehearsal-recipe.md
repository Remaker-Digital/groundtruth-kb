# Isolation Migration — Rehearsal Recipe

This document describes the **out-of-band rehearsal recipe** for `gt project upgrade --apply --accept-migration` per `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` decision 7 (`out_of_band_recipe_only`).

The Phase 8 rehearsal driver (`scripts/rehearse_isolation.py`) runs a sandboxed dry-run of the migration in 12 phases, producing filtered-DB previews, classification manifests, and migration evidence. **`gt project upgrade` does NOT invoke the rehearsal driver itself.** Adopters run rehearsal out-of-band, review the preview, then re-run upgrade with `--accept-migration` if the preview is acceptable.

## Two-step recipe

### Step 1 — Run the rehearsal

```bash
python scripts/rehearse_isolation.py --execute \
    --output-dir <sandbox-path>
```

The sandbox path **must be outside the GT-KB project root** per `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`. Allowed sandbox patterns:

- Windows: `C:/temp/agent-red-rehearsal*`
- POSIX: `/tmp/agent-red-rehearsal*`

The driver enforces this constraint via `validate_sandbox_output_dir`. Attempts to direct output back into the project root are rejected with exit code 2.

### Step 2 — Inspect the rehearsal preview

The rehearsal output directory contains:

- `run-summary.json` — per-lane status (ok / skipped / error) + warnings.
- `db-filter-dryrun/` — filtered preview database (Wave 3) showing what records would survive the migration.
- Per-lane evidence files (path-rewrite mapping, CI inventory, classification manifests).

Verify the preview matches your expectation **before** running the actual migration.

### Step 3 — Run the migration

```bash
gt project upgrade --apply --accept-migration
```

This:

1. Re-runs the 9 isolation doctor checks via `_run_isolation_preflight`.
2. Refuses if check #1 (`isolation:adopter-root-placement`) fails — **adopter root must be relocated manually** to `<gt-kb-root>/applications/<name>/`.
3. Refuses if any of checks #4 / #5 / #7 / #9 fail — **needs adopter input**:
   - `isolation:no-writable-product-paths` — adopter has files in product-managed paths; decide what to keep.
   - `isolation:hooks-point-to-wrappers` — `.claude/settings.json` has hook commands that aren't wrapper-shaped; manually delete or rewrap each adopter customization (check passes once all hook commands point under `.claude/hooks/`, invoke `groundtruth_kb`, or use `${CLAUDE_PLUGIN_ROOT}`).
   - `isolation:chroma-regeneratable` — orphan ChromaDB cache; decide whether to regenerate or delete.
4. Runs the 4 in-place auto-fixers (checks #2, #3, #6, #8) inside a payload branch.
5. Writes a rollback receipt with an `isolation_migration` audit block recording each fixer's outcome + prior policy.

If the migration goes wrong, `gt project rollback` consumes the receipt and reverses the payload via `git revert -m 1 <merge_commit>`.

## What `--accept-migration` authorizes

Per `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` + the S328 owner AskUserQuestion answer (preserve-override scope):

- `--accept-migration` overrides `upgrade_policy=preserve` for **only** the bounded isolation-fix surface:
  - `groundtruth.toml` (check #2)
  - `.claude/session/work-subject.json` (check #3 — written, not modified)
  - `.claude/hooks/workstream-focus.py` (check #6 — DELETED)
  - `memory/release-readiness.md` (check #8)
- The override fires **only** when `--accept-migration` is set. Without the flag, no preserve files are touched.
- Any attempt to mutate a path outside this surface raises `IsolationPolicyOverrideViolation` (defense in depth).
- Each preserve-policy mutation is recorded in the rollback receipt's `isolation_migration.auto_fixed[].prior_policy` field for adopter audit.

## See also

- `scripts/rehearse_isolation.py` — the rehearsal driver source.
- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py` — the 9 isolation doctor checks.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` — `_PARTITION_*`, `_ISOLATION_FIX_SURFACE_FILES`, the 4 auto-fixers, `execute_upgrade(... accept_migration=True)` flow.
- `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-008.md` — Codex GO authorizing this slice.
- `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` — sandbox path exception governing rehearsal output.
- `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` — owner pre-decisions for Slice 4.
