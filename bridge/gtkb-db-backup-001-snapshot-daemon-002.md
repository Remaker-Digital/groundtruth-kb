# Loyal Opposition Response: GTKB-DB-BACKUP-001 Snapshot Daemon

Status: NO-GO

## Claim

`bridge/gtkb-db-backup-001-snapshot-daemon-001.md` is directionally useful but not approved as scoped. The proposal does not yet close the main failure class from S311: sync software observing a partially written SQLite artifact.

## Evidence

- The proposal allows snapshots under a Drive-synced GT-KB backup directory because snapshots are intended to be immutable.
- `VACUUM INTO` still creates a SQLite output file over time. Until the command completes, a continuously running sync client can observe and copy a partial output file.
- The proposed contract does not require a non-synced staging location, integrity check in staging, and atomic publish into the final snapshot directory.
- Upstream GroundTruth-KB currently exposes the CLI through `src/groundtruth_kb/cli.py` with console script `gt = "groundtruth_kb.cli:main"`. There is no existing `groundtruth_kb/cli/__init__.py` package matching the proposal's file list.
- Upstream configuration is `groundtruth.toml` loaded through `GTConfig` in `src/groundtruth_kb/config.py`. Existing configuration sections include `[groundtruth]`, `[gates]`, and `[search]`; there is no existing `[backup]` handling or `gtkb-config-template.toml` file matching the proposal.

## Risk / Impact

The current design could produce exactly the kind of externally observed partial SQLite file this work is meant to prevent.

The CLI/config path mismatch also creates implementation risk: the proposed files do not align with the current upstream package shape, so implementation could drift into a parallel command/config surface instead of the real `gt` entry point and `groundtruth.toml` loader.

## Recommended Action

Revise the scoping contract before implementation:

- Always write snapshots to a non-synced staging path or temporary filename ignored by sync tools.
- Run `PRAGMA integrity_check` against the staged snapshot before publication.
- Publish only by atomic move/rename into the final snapshot location after the DB and manifest are complete.
- Avoid defaulting to an adopter-root snapshot directory unless explicitly requested, because the adopter root itself may be cloud-synced and `.driveignore` is not universal across sync tools.
- Align the file plan with upstream: wire the command through the actual `src/groundtruth_kb/cli.py` entry point, and either extend `GTConfig` or explicitly parse `[backup]` from `groundtruth.toml`.

## Decision Needed From Owner

None.
