NEW

# GTKB-DB-BACKUP-001 Snapshot Capability Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-db-backup-001-snapshot-daemon
Version: 007
Author: Prime Builder (Codex, harness A)
Date: 2026-05-12 UTC
Responds-To: `bridge/gtkb-db-backup-001-snapshot-daemon-006.md`
Dispatch: `2026-05-12T22-13-57Z-prime-builder-3e0880` / single-harness mode `pb`
Recommended commit type: `feat:`

## Claim

Implemented the approved upstream `gt db snapshot` capability in
`groundtruth-kb`. The command creates an integrity-checked SQLite snapshot by
writing to staging first, validating the staged database, publishing with
same-volume `os.replace`, writing a manifest, and applying retention.

The first implementation defers ChromaDB capture by failing `--include-chroma`
closed before any snapshot paths are created, as allowed by the approved
implementation proposal and GO response.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation report is filed under
  `bridge/` and registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report
  carries forward the approved implementation proposal and links concrete
  source/test/doc changes to the governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - each approved safety
  requirement below maps to executed tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the S311 database-backup lesson is
  now preserved as a deterministic command, config surface, docs, and tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - this is a GT-KB platform
  capability under `groundtruth-kb`; Agent Red adopter backup-tool
  configuration remains a separate follow-up.
- `bridge/gtkb-db-backup-001-snapshot-daemon-005.md` - approved
  implementation proposal.
- `bridge/gtkb-db-backup-001-snapshot-daemon-006.md` - Loyal Opposition GO.

## Implementation Summary

- Added `groundtruth-kb/src/groundtruth_kb/db_snapshot.py`.
- Added `BackupConfig` and `[backup]` parsing to
  `groundtruth-kb/src/groundtruth_kb/config.py`.
- Added `gt db snapshot` to `groundtruth-kb/src/groundtruth_kb/cli.py`.
- Added optional `[backup]` examples to `gt init` and desktop bootstrap
  TOML scaffolds.
- Added snapshot documentation to `docs/reference/cli.md`,
  `docs/reference/configuration.md`, `docs/gt-db-snapshot.md`, and
  `mkdocs.yml`.
- Added `groundtruth-kb/tests/test_db_snapshot.py` and expanded
  config/CLI coverage.
- Ran ruff formatting over the touched source/tests; this also normalized one
  pre-existing formatting issue in `tests/test_cli.py`.

## Specification-Derived Verification

| Requirement / GO condition | Implementation evidence | Executed verification |
| --- | --- | --- |
| Same-volume staging/output is enforced before writing | `_validate_snapshot_paths()` refuses when `_same_volume()` is false, before `_create_snapshot_in_staging()` runs. | `test_cross_volume_staging_to_output_is_refused` |
| Staging is outside synced paths | `_is_synced_path()` rejects known sync markers and configured `sync_paths` for staging. | `test_synced_staging_dir_is_refused` |
| Synced output warns but is allowed | Output sync detection appends a warning instead of refusing. | `test_synced_output_dir_warns_and_succeeds` |
| Output never receives `.tmp` staging files | Staging file name is created only under `staging_dir`; publish uses `os.replace()` to final output. | `test_snapshot_uses_staging_file_then_atomic_publish` |
| Integrity check gates publication | `_integrity_check()` must return `ok`; failure moves the staged DB to `staging/quarantine/` and publishes nothing. | `test_integrity_failure_quarantines_and_skips_publish` |
| Default output avoids adopter root | `default_output_dir()` uses user-local data storage and project basename, not `project_root`. | `test_snapshot_default_output_dir_is_outside_project_root` |
| Manifest records audit metadata | Manifest includes source/final path, size, mtime, method, duration, integrity result, schema version, table counts, and warnings. | `test_manifest_records_snapshot_metadata` |
| Retention keeps recent, daily, and schema-version survivors | `rotate_snapshots()` keeps recent snapshots, daily survivors, and at least one snapshot per schema version. | `test_rotation_keeps_retain_recent`; `test_rotation_preserves_schema_versions` |
| `--fast` uses the backup path | Fast mode sets method `backup` and copies database contents through the backup writer. | `test_fast_mode_uses_backup_method_and_copies_data` |
| `--include-chroma` is safe if deferred | Chroma inclusion raises exit code 2 before output/staging directories are created. | `test_include_chroma_fails_closed_before_writing`; `test_gt_db_snapshot_cli_include_chroma_fails_closed` |
| CLI structured success path works | `gt db snapshot --json` returns final path and integrity result. | `test_gt_db_snapshot_cli_success_json` |
| `[backup]` TOML is parsed and anchored | `BackupConfig` loads output/staging paths, retention, Chroma flag, and sync paths from TOML. | `test_loads_backup_section` |

## Commands Executed

```text
python -m pytest tests/test_db_snapshot.py tests/test_config.py -q --tb=short
```

Observed result:

```text
33 passed, 1 warning in 0.92s
```

Warning: ChromaDB dependency emitted a deprecation warning for
`asyncio.iscoroutinefunction`. This is an existing dependency warning and did
not affect the snapshot tests.

```text
python -m pytest tests/test_cli.py -q --tb=short
```

Observed result:

```text
37 passed, 1 warning in 6.58s
```

```text
python -m pytest tests/test_db_snapshot.py tests/test_config.py tests/test_cli.py -q --tb=short
```

Observed result:

```text
70 passed, 1 warning in 7.52s
```

```text
python -m ruff check src/groundtruth_kb/db_snapshot.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/bootstrap.py tests/test_db_snapshot.py tests/test_config.py tests/test_cli.py
```

Observed result:

```text
All checks passed!
```

```text
python -m ruff format --check src/groundtruth_kb/db_snapshot.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py src/groundtruth_kb/bootstrap.py tests/test_db_snapshot.py tests/test_config.py tests/test_cli.py
```

Observed result:

```text
7 files already formatted
```

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/db_snapshot.py`
- `groundtruth-kb/src/groundtruth_kb/config.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/bootstrap.py`
- `groundtruth-kb/tests/test_db_snapshot.py`
- `groundtruth-kb/tests/test_config.py`
- `groundtruth-kb/tests/test_cli.py`
- `groundtruth-kb/docs/reference/cli.md`
- `groundtruth-kb/docs/reference/configuration.md`
- `groundtruth-kb/docs/gt-db-snapshot.md`
- `groundtruth-kb/mkdocs.yml`

## Baseline Accounting

- `tests/test_cli.py` had a pre-existing ruff-format issue; formatting the
  targeted verification file normalized that small style issue.
- The ChromaDB deprecation warning appears in targeted pytest runs because the
  optional dependency is installed in this environment. No test failed.
- Existing unrelated bridge worktree changes were present before this report
  was filed and were not modified by the snapshot implementation except for
  the required `bridge/INDEX.md` insertion for this thread.

## Out Of Scope

- No Agent Red file, SyncBackSE profile, Google Drive, OneDrive, Dropbox,
  production deployment, remote repository, or credential lifecycle was
  changed.
- ChromaDB snapshot capture remains deferred; the flag fails closed.

Owner action required: none.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
