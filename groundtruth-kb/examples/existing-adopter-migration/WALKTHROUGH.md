# Migration walkthrough — pre-isolation adopter to clean post-migration state

This walkthrough exercises the `gt project upgrade --apply --accept-migration`
flow against the pre-isolation tree in this example. The end state is an
adopter that satisfies every `isolation:*` doctor check.

## Prerequisites

- `gt` CLI installed (`pip install groundtruth-kb`).
- A working git environment (the upgrade flow requires a clean git tree).
- A workspace location for the migration. The example tree must be copied
  out of `<gt-kb-root>/groundtruth-kb/examples/` and into a workspace path
  before the upgrade runs (the upgrade mutates the tree in place).

## Step 1 — Stage the example into a workspace

```bash
# Copy the example tree to a workspace location of your choosing.
cp -r examples/existing-adopter-migration/ ~/projects/legacy-app/
cd ~/projects/legacy-app/

# The example does not ship a .git/ directory; initialize git here.
git init --initial-branch=main
git add -A
git commit -m "pre-migration snapshot"
```

## Step 2 — Confirm the pre-isolation shape

```bash
gt project doctor --profile dual-agent
```

Expected: at least four `isolation:*` checks report `fail` or `warning`:

- `isolation:service-endpoint` (raw-DB endpoint)
- `isolation:work-subject` (platform subject)
- `isolation:workstream-focus-hook-absent` (legacy hook present)
- `isolation:release-readiness-app-subject-header` (wrong header)

The doctor's overall status reflects these as a non-clean state. This is
the starting point.

## Step 3 — Apply the migration

The upgrade refuses by default on isolation failures. Pass
`--accept-migration` to opt into the one-shot auto-fix flow per
`DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE`
(decisions: `mandatory_at_upgrade` + `one_shot_migration_at_upgrade` +
`out_of_band_recipe_only`).

```bash
gt project upgrade --apply --accept-migration
```

The upgrade flow:

1. Runs the isolation pre-flight against the four failing checks.
2. Partitions them: 4 auto-fixable, 0 needs-adopter-input, 0 hard-refuse.
3. Creates a payload branch (`gt-upgrade-payload-<id>`).
4. Runs the auto-fixers:
   - `[service].endpoint` rewritten to the placeholder.
   - `current_subject` reset to `application` in `work-subject.json`.
   - `.claude/hooks/workstream-focus.py` deleted.
   - `memory/release-readiness.md` header normalized.
5. Applies any registry-diff file actions (no-op in this minimal example).
6. Merges the payload branch with `--no-ff`.
7. Writes the rollback receipt under `.claude/upgrade-receipts/active/`.

## Step 4 — Confirm the clean post-migration state

```bash
gt project doctor --profile dual-agent
```

Expected: every `isolation:*` check reports `pass` or `info`. The receipt
under `.claude/upgrade-receipts/active/<receipt_id>.json` records the
migration with an `isolation_migration` block enumerating the 4
auto-fixer outcomes.

## Step 5 — (Optional) Roll back

If the migration produced unexpected results, the receipt makes rollback
deterministic:

```bash
gt project rollback              # consume the latest receipt
```

Rollback runs `git revert -m 1 <merge_commit>` against the upgrade's merge
commit. The pre-migration state is restored byte-for-byte. The receipt
itself is NOT removed; it remains under `.claude/upgrade-receipts/active/`
for audit.

## Reference

- [Application/Platform Isolation](../../docs/architecture/isolation.md)
  §"Migrating an existing mixed-root project"
- [upgrade-receipts.md](../../docs/reference/upgrade-receipts.md)
- The Phase 8 rehearsal kit at `scripts/rehearse_isolation.py` and the
  recipe at `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`
  for non-destructive rehearsal of the migration before running it
  against production state.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
