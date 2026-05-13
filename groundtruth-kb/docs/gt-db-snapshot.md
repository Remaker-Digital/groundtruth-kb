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
