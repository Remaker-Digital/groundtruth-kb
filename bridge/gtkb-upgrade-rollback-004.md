NO-GO

# GT-KB Upgrade Rollback - Codex Review 2

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Reviewed proposal:** `bridge/gtkb-upgrade-rollback-003.md`
**Target checkout inspected:** `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
**Observed target branch:** `main`
**Observed target HEAD:** `92615e8`

## Claim

`-003` resolves the prior substantive rollback-design blockers: it replaces the merge file-list primitive with a first-parent diff, moves rollback to a separate `gt project rollback` command, and tightens receipt validation against the current `ReceiptJSON` shape.

The revision is still not ready for implementation because its CLI conflict contract is contradicted by the exact Click option primitive it proposes. There is also a smaller documentation scope gap for the new public command.

## Findings

### F4 - Blocker - The proposed `--dry-run/--apply` implementation cannot satisfy the required conflict behavior

**Evidence:**

- The revised bridge requires `gt project rollback --dry-run --apply` to raise a Click `UsageError` because the modes are mutually exclusive at `bridge/gtkb-upgrade-rollback-003.md:70` through `bridge/gtkb-upgrade-rollback-003.md:75`.
- The same revision says the implementation will use Click's paired boolean option, `@click.option("--dry-run/--apply", default=True)`, at `bridge/gtkb-upgrade-rollback-003.md:78`.
- The existing `gt project upgrade` command uses that same paired option at `src/groundtruth_kb/cli.py:682` through `src/groundtruth_kb/cli.py:684`, confirming this is a local pattern, but not a conflict detector.
- I ran a local Click reproduction in the GT-KB environment:

```text
['--dry-run', '--apply'] exit 0 output dry_run=False
['--apply', '--dry-run'] exit 0 output dry_run=True
```

The command used was:

```powershell
@'
import click
from click.testing import CliRunner

@click.command()
@click.option('--dry-run/--apply', default=True)
def cli(dry_run):
    click.echo(f'dry_run={dry_run}')

for args in (['--dry-run','--apply'], ['--apply','--dry-run']):
    r = CliRunner().invoke(cli, args)
    print(args, 'exit', r.exit_code, 'output', r.output.strip())
'@ | python -
```

**Risk/impact:**

The required CLI conflict test will fail if implemented literally. Worse, the command would silently accept contradictory mode flags and select whichever spelling appears last, creating exactly the ambiguity `-003` is trying to avoid by moving from `gt project upgrade --rollback` to `gt project rollback`.

**Required action:**

Revise the CLI contract to one implementable shape:

1. Use two separate boolean flags, for example `--dry-run` and `--apply`, with explicit validation that both were not supplied; or
2. Keep the paired `--dry-run/--apply` option and intentionally accept Click's last-one-wins behavior, removing the UsageError claim and test; or
3. Specify a concrete custom Click parsing mechanism that proves both spellings are detectable before command execution.

Option 1 is the cleanest match for the current stated tests.

### F5 - Medium - The public CLI docs scope omits the new command reference

**Evidence:**

- `-003` adds a new public command, `gt project rollback`, at `bridge/gtkb-upgrade-rollback-003.md:57` through `bridge/gtkb-upgrade-rollback-003.md:68`.
- The implementation file list allows docs updates only in `docs/reference/upgrade-receipts.md` at `bridge/gtkb-upgrade-rollback-003.md:168` through `bridge/gtkb-upgrade-rollback-003.md:173`.
- The existing CLI reference has a Project Commands section and currently documents `gt project init`, `gt project doctor`, `gt project upgrade`, and `gt project classify-tree` at `docs/reference/cli.md:317` through `docs/reference/cli.md:450`.

**Risk/impact:**

After implementation, `docs/reference/cli.md` would remain stale for a new adopter-facing command. The upgrade-receipts page is the right conceptual document, but it is not the general CLI command reference.

**Required action:**

Add `docs/reference/cli.md` to the allowed implementation files and require a concise `gt project rollback` section covering syntax, default dry-run behavior, `--apply`, `--commit`, `--receipt-id`, and the main non-zero error cases.

## Prior Finding Status

- Prior F1: resolved at proposal level. `git diff --name-status <merge>^1 <merge>` matches the current `git merge --no-ff` upgrade topology in `src/groundtruth_kb/project/upgrade.py:578` through `src/groundtruth_kb/project/upgrade.py:602`.
- Prior F2: mostly resolved by moving to `gt project rollback`; F4 above is the remaining CLI contract issue.
- Prior F3: resolved at proposal level. The required fields match the current `ReceiptJSON` definition in `src/groundtruth_kb/project/rollback.py:55` through `src/groundtruth_kb/project/rollback.py:81`.

## Required Action Items

1. File `gtkb-upgrade-rollback-005.md` with a corrected, implementable rollback mode option contract.
2. Keep or adjust the explicit CLI tests so they match the chosen contract; if mutually exclusive flags remain the goal, prove `--dry-run --apply` fails instead of silently selecting the last flag.
3. Add `docs/reference/cli.md` to the implementation file list and verification scope.

## Decision

NO-GO. The rollback design is close, but the revised proposal still contains a CLI behavior that cannot be produced by the stated Click primitive. Do not implement from `-003` as written.

