# GT DB Snapshot

`gt db snapshot` creates a consistent SQLite backup artifact without asking
backup or sync tools to copy the live database triple.

The command stages the snapshot in a user-local directory, verifies it with
`PRAGMA integrity_check`, writes a manifest, and then publishes the completed
database with a same-volume atomic rename. Backup tools should copy the
published snapshot directory, not the live `groundtruth.db` file.

## Usage

```bash
gt --config groundtruth.toml db snapshot
```

Useful options:

```bash
gt db snapshot --output-dir "D:/Backups/gtkb-snapshots"
gt db snapshot --fast --json
gt db snapshot --retain 14 --daily-days 60
```

`VACUUM INTO` is the default because it produces a compact, consistent output.
`--fast` uses `sqlite3.Connection.backup()` when speed matters more than
defragmentation.

## Safety Contract

- Staging happens outside the output directory.
- Staging paths that look sync-managed are refused.
- Output paths that look sync-managed are allowed with a warning.
- Staging and output must be on the same volume so publication can use
  `os.replace`.
- Integrity-check failure leaves no published snapshot; the staged file moves
  to `staging/quarantine/`.

## Retention

By default, rotation keeps the seven most recent snapshots, one snapshot per
calendar day for 30 days, and at least one snapshot per observed
`schema_version`.

## Scheduling

GroundTruth KB ships the command, not a scheduler. Use Task Scheduler, cron,
backup-tool pre-scripts, or a project hook to run it at the cadence that fits
the adopter.

On Windows, the project includes an idempotent installer:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install_db_snapshot_task.ps1
```

This creates a `GTKB-DbSnapshot` scheduled task running daily at 03:00 under
the current user principal with `LogonType = S4U` (runs whether or not the user
is logged on, without storing a password).

## Repointing SyncBack / SyncBackSE

If a third-party backup tool (e.g., SyncBack, SyncBackSE, Acronis) currently
backs up `groundtruth.db` directly, repoint the profile to the snapshot output
directory instead:

1. Run `gt db snapshot` once so the output directory is populated.
2. In the backup tool, change the source from `E:\GT-KB\groundtruth.db` to
   `%LOCALAPPDATA%\gtkb-snapshots\GroundTruth-KB Platform\` (or the custom
   path in `groundtruth.toml` `[backup] snapshot_output_dir`).
3. The `manifest.json` in the snapshot directory records `schema_version`,
   `integrity_check`, and `source_db_size` for each snapshot — useful for
   restore triage.

This avoids lock contention and WAL-state corruption when the backup tool
copies the live database while GT-KB or an AI harness session holds an open
connection.

## Configuration

`groundtruth.toml` `[backup]` section:

| Key | Default | Description |
|-----|---------|-------------|
| `snapshot_output_dir` | `%LOCALAPPDATA%/gtkb-snapshots/<project-name>` | Override output directory |
| `retain_recent` | 7 | Keep this many most-recent snapshots |
| `retain_daily_days` | 30 | Keep one snapshot per calendar day for this many days |
| `include_chroma` | false | Also snapshot the ChromaDB vector index |

## Root Boundary Exception

The default snapshot output directory is outside `E:\GT-KB` by design. The
live `groundtruth.db` resides on a cloud-synced drive; writing VACUUM'd copies
to the same sync root risks corruption from concurrent sync operations.
`%LOCALAPPDATA%` is a non-synced, user-local directory. See
`.claude/rules/project-root-boundary.md` § DB-Snapshot Output Exception for
the governance contract and doctor enforcement.
