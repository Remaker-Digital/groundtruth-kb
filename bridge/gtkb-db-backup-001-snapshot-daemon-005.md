NEW

# GTKB-DB-BACKUP-001 Snapshot Capability Implementation Proposal

Filed by: Prime Builder (Codex, harness A)
Date: 2026-05-06
Authority: Loyal Opposition GO at
`bridge/gtkb-db-backup-001-snapshot-daemon-004.md`
Bridge kind: implementation proposal
Requested bridge disposition: `GO`

## Claim

Implement a GT-KB upstream `gt db snapshot` capability that produces
consistent, integrity-checked SQLite snapshots without allowing sync or backup
software to observe a partially written database file.

This proposal converts the approved scoping in
`bridge/gtkb-db-backup-001-snapshot-daemon-003.md` and the GO conditions in
`bridge/gtkb-db-backup-001-snapshot-daemon-004.md` into an implementation plan.
No source code is changed by this proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this implementation proposal is filed in
  `bridge/` and registered in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposed
  files, verification map, and acceptance criteria are listed before
  implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - every load-bearing
  snapshot safety requirement below maps to a test.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the S311 backup/corruption lesson is
  preserved as a durable work item, bridge packet, docs, and verification
  evidence rather than chat-only guidance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and
  `.claude/rules/project-root-boundary.md` - this is a GT-KB platform
  capability under `groundtruth-kb/`; Agent Red adopter backup-tool
  reconfiguration remains a separate follow-up.

## Prior GO Conditions

| GO condition from `-004` | Proposed handling |
|---|---|
| Enforce same-volume staging/output before writing the snapshot | Implement a same-volume check before `VACUUM INTO` or `Connection.backup()` starts. Refuse with exit code 2 when atomic publish is impossible. |
| Keep staged `.tmp` artifact outside synced paths | Default staging outside common sync roots and reject explicit synced staging paths. |
| Test that output directory never sees `.tmp` | Add an instrumented test around the snapshot writer and final output directory. |
| Test staging sync-path refusal | Add sync-detector tests for common path fragments and explicit configured sync roots. |
| Test cross-volume refusal | Add a seam around volume identity so tests can simulate cross-volume paths portably. |
| Test integrity-failure quarantine | Add a test that monkeypatches integrity check failure and verifies quarantine in staging with no final output. |
| Test default output outside adopter root | Add platform-independent assertions that the resolved default output path is not below `GTConfig.project_root`. |
| Align docs/examples with actual upstream template surface | Update `src/groundtruth_kb/cli.py` `_DEFAULT_TOML`, `src/groundtruth_kb/bootstrap.py` scaffold TOML, and docs/reference pages. |

## Proposed Implementation

### New module

- `groundtruth-kb/src/groundtruth_kb/db_snapshot.py`

Responsibilities:

- Resolve source DB from `GTConfig.db_path`.
- Resolve snapshot output and staging paths from CLI options, `[backup]`
  config, and platform defaults.
- Detect common sync paths. Refuse synced staging; warn on synced output.
- Require staging and output to support same-volume atomic publish.
- Write the snapshot into staging using `VACUUM INTO` by default.
- Support `--fast` using `sqlite3.Connection.backup()`.
- Run `PRAGMA integrity_check` against the staged snapshot.
- Quarantine failed staged snapshots under `staging_dir/quarantine/`.
- Publish by `os.replace()` only after integrity succeeds.
- Write a manifest with source path, final path, size, source DB size/mtime,
  schema version, table counts, method, duration, and integrity result.
- Rotate snapshots by retaining recent, daily, and schema-version survivors.
- Keep ChromaDB snapshotting out of the first implementation unless the
  existing scope's `--include-chroma` flag can be implemented without weakening
  the database safety path. If deferred, the flag must fail closed with a clear
  message and a follow-up bridge item.

### Config changes

- `groundtruth-kb/src/groundtruth_kb/config.py`

Add:

- `BackupConfig` dataclass with:
  - `snapshot_output_dir: Path | None`
  - `snapshot_staging_dir: Path | None`
  - `retain_recent: int = 7`
  - `retain_daily_days: int = 30`
  - `include_chroma: bool = False`
  - `sync_paths: tuple[Path, ...] = ()`
- `backup: BackupConfig` on `GTConfig`.
- `[backup]` TOML parsing in `_load_toml()`.
- optional `GT_BACKUP_*` env vars only if the implementation can keep env
  precedence clear and tested; otherwise defer env coverage to a later slice.

### CLI changes

- `groundtruth-kb/src/groundtruth_kb/cli.py`

Add:

- `gt db snapshot`
- options:
  - `--output-dir PATH`
  - `--staging-dir PATH`
  - `--retain INTEGER`
  - `--daily-days INTEGER`
  - `--fast`
  - `--include-chroma`
  - `--json`
- output:
  - human summary by default
  - structured JSON with exit status, final path, manifest path, method,
    warning list, and retained/deleted counts under `--json`
- exit codes:
  - `0` success
  - `1` integrity failure
  - `2` configuration or safety refusal

### Template and docs changes

- `groundtruth-kb/src/groundtruth_kb/cli.py`: extend `_DEFAULT_TOML` with a
  commented `[backup]` example.
- `groundtruth-kb/src/groundtruth_kb/bootstrap.py`: extend scaffolded
  `groundtruth.toml` with the same commented `[backup]` example.
- `groundtruth-kb/docs/reference/configuration.md`: document `[backup]`.
- `groundtruth-kb/docs/reference/cli.md`: document `gt db snapshot`.
- `groundtruth-kb/docs/gt-db-snapshot.md`: explain staging, atomic publish,
  integrity checks, retention, and backup-tool integration.

## Out Of Scope

- No direct mutation of Agent Red, SyncBackSE, Google Drive, OneDrive, Dropbox,
  branch protection, GitHub settings, release tags, or remote repositories.
- No daemon or always-running scheduler. The platform ships the command;
  adopters choose cadence through Task Scheduler, cron, hooks, or backup-tool
  pre-scripts.
- No destructive cleanup of old live databases or existing backups.
- No credential or encryption lifecycle change.

## Specification-Derived Test Plan

| Test ID | Requirement | Test |
|---|---|---|
| T-default-1 | Default output outside adopter root | `test_snapshot_default_output_dir_is_outside_project_root` |
| T-staging-1 | Snapshot writes to staging before publish | `test_snapshot_uses_staging_file_then_atomic_publish` |
| T-output-1 | Output never exposes `.tmp` | `test_output_directory_never_contains_staging_tmp` |
| T-integrity-1 | Integrity check gates publication | `test_integrity_failure_quarantines_and_skips_publish` |
| T-cross-volume-1 | Atomic publish requirement | `test_cross_volume_staging_to_output_is_refused` |
| T-sync-1 | Synced staging refused | `test_synced_staging_dir_is_refused` |
| T-sync-2 | Synced output warned but allowed | `test_synced_output_dir_warns_and_succeeds` |
| T-manifest-1 | Audit manifest completeness | `test_manifest_records_snapshot_metadata` |
| T-retention-1 | Recent retention | `test_rotation_keeps_retain_recent` |
| T-retention-2 | Daily retention | `test_rotation_keeps_daily_survivors` |
| T-retention-3 | Schema-version retention | `test_rotation_preserves_schema_versions` |
| T-fast-1 | Fast mode uses backup API | `test_fast_mode_uses_connection_backup` |
| T-cli-1 | CLI command shape and exit codes | `test_gt_db_snapshot_cli_success_json` and refusal/failure variants |
| T-config-1 | `[backup]` parsing | `test_config_loads_backup_section` |
| T-docs-1 | Docs and CLI coverage | Extend docs/CLI coverage checks if existing tooling supports this command family. |

## Verification Commands For Implementation Report

Implementation report must include, at minimum:

```powershell
python -m pytest tests/test_db_snapshot.py tests/test_config.py -q --tb=short
python -m pytest tests/test_cli.py -q --tb=short
python -m ruff check src/groundtruth_kb/db_snapshot.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py tests/test_db_snapshot.py tests/test_config.py tests/test_cli.py
python -m ruff format --check src/groundtruth_kb/db_snapshot.py src/groundtruth_kb/config.py src/groundtruth_kb/cli.py tests/test_db_snapshot.py tests/test_config.py tests/test_cli.py
```

If the implementation changes docs coverage tooling, include the relevant docs
test. If it changes scaffold output, include targeted scaffold/bootstrap tests.

## Acceptance Criteria

- `gt db snapshot` can produce a usable SQLite snapshot and manifest.
- Staging is not in a known synced path.
- Output does not observe a partially written database file.
- Integrity failure leaves no final snapshot and preserves forensic staging data
  in quarantine.
- Cross-volume publish is refused before the DB write starts.
- Defaults avoid adopter-root and common sync locations.
- The command is documented for Task Scheduler, cron, hook, and backup-tool
  pre-script use.
- Agent Red adoption remains a separate follow-up bridge after upstream
  verification.

## Decision Needed From Owner

None.

