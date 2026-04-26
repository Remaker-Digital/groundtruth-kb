# Loyal Opposition Response: GTKB-DB-BACKUP-001 Snapshot Daemon Revision 1

Status: GO

## Claim

`bridge/gtkb-db-backup-001-snapshot-daemon-003.md` resolves the prior snapshot-daemon scoping blockers and is approved for implementation planning against upstream `groundtruth-kb`.

## Evidence

- The revised design requires snapshots to be written to a non-synced staging path first, not directly into the watched output directory.
- It requires `PRAGMA integrity_check` against the staged snapshot before publication.
- It publishes by same-volume `os.replace(...)` and refuses cross-volume staging/output combinations where atomic rename is not available.
- It distinguishes staging safety from output backup policy: synced output paths are allowed with a warning, while synced staging paths are refused.
- Upstream verification confirms the real CLI surface is `src/groundtruth_kb/cli.py` with console script `gt = "groundtruth_kb.cli:main"`.
- Upstream verification confirms configuration is loaded by `src/groundtruth_kb/config.py` from `groundtruth.toml`.

## Risk / Impact

The revised architecture closes the S311 failure class for the database file itself: sync software should only observe the final DB after it has been fully written and integrity checked.

There is a small multi-file publication caveat: the DB and manifest sidecar cannot be atomically published as a pair with two independent `os.replace(...)` calls. That is not a DB-corruption blocker, but the implementation should either tolerate a briefly missing manifest or publish snapshots inside a per-snapshot directory that is renamed into place as one unit.

## Recommended Action

Proceed with implementation under these conditions:

- Enforce same-volume staging/output before writing the snapshot.
- Keep the staged `.tmp` artifact outside synced paths.
- Add tests for output directory never seeing the `.tmp` file, staging sync-path refusal, cross-volume refusal, integrity-failure quarantine, and default output outside adopter root.
- Align docs/examples with the actual upstream template surface. There is no `gtkb-config-template.toml`; update `_DEFAULT_TOML`, docs, examples, or the actual scaffold source used by upstream.

## Decision Needed From Owner

None.
