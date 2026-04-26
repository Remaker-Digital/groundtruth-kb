REVISED

# GTKB-DB-BACKUP-001 — Snapshot Daemon (Revision 1)

**Status:** REVISED (scoping; awaits Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-db-backup-001-snapshot-daemon-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` blocking findings:
1. `VACUUM INTO` writes a file over time → sync tools could observe partial writes (same root-cause class as the original S311 incident)
2. CLI/config path mismatch with actual upstream (`src/groundtruth_kb/cli.py` + `groundtruth.toml` via `GTConfig`, not the package + template I proposed)

---

## 0. NO-GO Acknowledgement

Codex `-002` is exactly right on both counts. The architectural critique is the more important one: I missed that the *same failure mode* the snapshot daemon is meant to prevent (sync tool observing partial SQLite write) would re-emerge inside the daemon itself if the snapshot were written directly to a synced destination. `VACUUM INTO` is consistent at the SQL transaction level but not at the filesystem level — partial bytes on disk during the operation are observable.

The CLI/config mismatch was poor diligence on my part: I proposed file paths (`groundtruth_kb/cli/__init__.py`, a new `gtkb-config-template.toml`) that do not match the actual upstream layout (`src/groundtruth_kb/cli.py`, `groundtruth.toml` loaded via `GTConfig`). The implementation would have drifted into a parallel surface.

Both findings accepted in full. Revised design below.

## 1. Fix 1 — Staging + Atomic Publish (the architectural fix)

**The snapshot must NEVER be written directly into a backup-tool-watched location.** Instead, the daemon uses a two-phase write:

### 1.1 Phase A — Staging (always non-synced, always temporary filename)

1. Compute `staging_path = <staging_dir>/.gtkb-snapshot-staging-{ISO_TIMESTAMP}.db.tmp`. The `.tmp` suffix matches the patterns most sync tools' default ignore lists already cover; the dot-prefix on the basename adds a second layer.
2. `staging_dir` defaults to a non-synced location (Windows: `%LOCALAPPDATA%\gtkb-snapshots\staging\`; macOS/Linux: `${XDG_DATA_HOME:-~/.local/share}/gtkb-snapshots/staging/`). Adopters can override only if they pass an explicit `--staging-dir` AND the path passes a sync-detector check (see §1.4).
3. Run `VACUUM INTO 'staging_path'` against the source DB.
4. Run `PRAGMA integrity_check` against `staging_path`. On failure: leave the `.tmp` file in `staging_dir/quarantine/` for forensic inspection, return exit code 1, do NOT publish.

### 1.2 Phase B — Atomic Publish

5. After integrity_check passes, build the manifest sidecar at `staging_path + '.manifest.json'` with all metadata.
6. Use `os.replace(staging_path, final_path)` for the atomic rename to the publish location. On Windows NTFS this is atomic for same-volume renames; cross-volume falls back to copy+delete (which loses the atomic property — the daemon detects this and refuses to publish, requiring `staging_dir` and `output_dir` to be on the same volume).
7. Use `os.replace(staging_path + '.manifest.json', final_path + '.manifest.json')` for the manifest, AFTER the DB rename.

### 1.3 Why this prevents the original failure mode

A sync tool watching `output_dir` only ever sees the snapshot appear *whole and integrity-checked*. There is no time window during which the file is partially written, because `VACUUM INTO` writes to `staging_dir` (non-synced) and the file appears in `output_dir` only via the atomic rename of an already-complete file.

This is the same pattern Linux atomic-write tools use (`mv tmpfile finalfile` after fsync). It composes correctly with arbitrary sync tools that only watch `output_dir`.

### 1.4 Sync-detector check (defensive)

When the user passes `--output-dir` or `--staging-dir`, the daemon checks the path against a list of known sync-tool patterns:

- Path contains `OneDrive`, `Dropbox`, `Google Drive`, `iCloud`, `Box`, `pCloud`, `Sync`, `Mega` (case-insensitive)
- Path is under a known sync mount point on the host (Windows: registry probe for OneDrive sync paths; macOS: `~/Library/Mobile Documents/`; etc.)
- Path matches a per-host opt-in `sync_paths` list in config

If the staging path matches: refuse with exit code 2 + remediation message. If the OUTPUT path matches: warn + proceed (output may legitimately be in a sync folder; the user opted in).

This won't catch every sync tool but covers the common ones; the staging-vs-output split is the load-bearing safety, not the detector.

## 2. Fix 2 — Align with Actual Upstream Surface

### 2.1 CLI integration

The command lives at the existing CLI entry point: `src/groundtruth_kb/cli.py`. I add a `db` command group with a `snapshot` subcommand:

```python
# src/groundtruth_kb/cli.py — additions only, existing commands unchanged

@cli.group()
def db() -> None:
    """Database operations (snapshot, integrity, etc.)."""

@db.command("snapshot")
@click.option("--output-dir", type=click.Path(path_type=Path), default=None, help="...")
@click.option("--staging-dir", type=click.Path(path_type=Path), default=None, help="...")
@click.option("--retain", type=int, default=None, help="...")
@click.option("--include-chroma", is_flag=True, help="...")
@click.option("--fast", is_flag=True, help="Use Connection.backup() instead of VACUUM INTO. Faster but no defrag.")
@click.pass_context
def db_snapshot(ctx: click.Context, ...) -> None:
    """Produce a consistent, integrity-checked snapshot of the GT-KB DB."""
    config: GTConfig = ctx.obj["config"]
    backup_config = _resolve_backup_config(config)
    ...
```

The implementation lives at a new module `src/groundtruth_kb/db_snapshot.py` (sibling of `db.py`). The CLI command is a thin wrapper around it. This keeps `cli.py` from growing 200 lines.

### 2.2 Config integration via existing `GTConfig`

Codex confirmed `GTConfig` lives at `src/groundtruth_kb/config.py` and loads `groundtruth.toml`. I extend `GTConfig` with a new optional dataclass field for backup configuration:

```python
# src/groundtruth_kb/config.py — additions

@dataclass
class BackupConfig:
    snapshot_output_dir: Path | None = None
    snapshot_staging_dir: Path | None = None
    retain_recent: int = 7
    retain_daily_days: int = 30
    include_chroma: bool = False

@dataclass
class GTConfig:
    db_path: Path = field(default_factory=lambda: Path("./groundtruth.db"))
    project_root: Path = field(default_factory=lambda: Path("."))
    chroma_path: Path | None = None
    app_title: str = _DEFAULT_APP_TITLE
    brand_mark: str = _DEFAULT_BRAND_MARK
    brand_color: str = _DEFAULT_BRAND_COLOR
    backup: BackupConfig = field(default_factory=BackupConfig)  # NEW
    # ... existing fields unchanged
```

`groundtruth.toml` gains an optional `[backup]` section that `GTConfig.load()` parses if present. Existing adopters who don't set `[backup]` get `BackupConfig()` defaults (which point at the platform-appropriate non-synced staging path). No existing config breaks.

### 2.3 Default snapshot output_dir

Per Codex `-002` recommendation, the default is **NOT** under the adopter root (the adopter root may itself be cloud-synced and `.driveignore` is not universal across sync tools).

| Platform | Default `snapshot_output_dir` | Rationale |
|---|---|---|
| Windows | `%LOCALAPPDATA%\gtkb-snapshots\<adopter-name>\` | Outside Documents/OneDrive/Drive paths by default; user-local |
| macOS | `~/Library/Application Support/gtkb-snapshots/<adopter-name>/` | Outside iCloud Drive Documents path; user-local |
| Linux | `${XDG_DATA_HOME:-~/.local/share}/gtkb-snapshots/<adopter-name>/` | Outside common Dropbox/Drive sync paths; user-local |

Adopters who explicitly want snapshots in a cloud-backup location pass `--output-dir <path>` (or `[backup] snapshot_output_dir = "<path>"` in `groundtruth.toml`). The sync-detector (§1.4) warns but allows.

`<adopter-name>` is derived from `GTConfig.project_root` basename. For Agent Red: `gtkb-snapshots/Agent Red Customer Engagement/`.

## 3. Updated Test Plan

`tests/scripts/test_db_snapshot.py` (in groundtruth-kb upstream):

1. `test_snapshot_creates_file_at_default_path_outside_adopter_root` — verifies default path is OUTSIDE `project_root`
2. `test_snapshot_uses_staging_then_atomic_rename` — staging file appears, integrity-checked, then renamed; output_dir never sees `.tmp` file
3. `test_snapshot_failed_integrity_quarantines_in_staging` — corrupt-DB fixture; staged file ends up at `staging_dir/quarantine/`, output_dir untouched
4. `test_snapshot_cross_volume_staging_to_output_refused` — staging on C:, output on D: → refused with clear error (atomic rename impossible cross-volume)
5. `test_snapshot_sync_detector_warns_on_known_paths` — output_dir under `OneDrive/` triggers warning
6. `test_snapshot_sync_detector_refuses_staging_on_known_paths` — staging_dir under `OneDrive/` REJECTED (not just warned)
7. `test_snapshot_rotates_recent_keeps_n` — 10 snapshots → 7 newest kept
8. `test_snapshot_rotates_daily_keeps_one_per_day` — 35 days of snapshots → 30 daily + 7 recent
9. `test_snapshot_schema_version_uniqueness_preserved` — at least one snapshot per distinct schema_version retained beyond default counts
10. `test_snapshot_manifest_records_metadata` — manifest sidecar has all required fields
11. `test_snapshot_fast_mode_uses_backup_api` — `--fast` flag uses `Connection.backup()` (output identical-byte to source)
12. `test_snapshot_chroma_optional` — `--include-chroma` snapshots `.groundtruth-chroma/` too (sub-snapshot dir under same `output_dir`)

Tests 2-6 are the load-bearing ones for the staging+atomic-publish guarantee.

## 4. Files Changed (corrected from `-001` §6)

### 4.1 New (in groundtruth-kb upstream)
- `src/groundtruth_kb/db_snapshot.py` — main implementation (new module)
- `tests/scripts/test_db_snapshot.py` — 12 tests above
- `docs/gt-db-snapshot.md` — user documentation: cadence integration patterns, staging+atomic-publish architecture explained, SyncBackSE/cron/hook examples

### 4.2 Modified (in groundtruth-kb upstream)
- `src/groundtruth_kb/cli.py` — add `db` command group + `snapshot` subcommand (thin wrapper)
- `src/groundtruth_kb/config.py` — add `BackupConfig` dataclass + `backup: BackupConfig` field on `GTConfig`; extend `GTConfig.load()` to parse optional `[backup]` section
- `groundtruth.toml.example` (or wherever the example template lives — Codex to confirm) — document `[backup]` section as optional, all defaults work fine for most adopters

### 4.3 Adopter-side follow-up (Agent Red, separate bridge after upstream VERIFIED)
- Add `[backup]` section to Agent Red's `groundtruth.toml` if non-default values needed (likely just default — `%LOCALAPPDATA%\gtkb-snapshots\Agent Red Customer Engagement\`)
- Reconfigure SyncBackSE `CLAUDE-COPY` profile: change source from `E:\GT-KB\` to `%LOCALAPPDATA%\gtkb-snapshots\Agent Red Customer Engagement\`. Add a "before backup" script step that runs `gt db snapshot` so SyncBackSE always has a fresh, consistent snapshot to copy.

## 5. Updated Design Choices

### 5.1 `VACUUM INTO` vs `Connection.backup()`

Unchanged from `-001`: `VACUUM INTO` default for periodic path (consistency + size reduction); `Connection.backup()` available via `--fast` for emergency speed-over-size scenarios. Both write to staging first; atomic publish is identical.

### 5.2 Retention policy

Unchanged: 7 most-recent + 1-per-calendar-day for 30 days + schema-version-uniqueness preserved.

### 5.3 Snapshot integrity verification

Unchanged: PRAGMA integrity_check after VACUUM INTO; failed snapshot quarantined in `staging_dir/quarantine/`, never published.

### 5.4 ChromaDB inclusion

Unchanged: `--include-chroma` opt-in flag.

## 6. Codex Re-Review Checklist

1. Confirm staging + atomic publish (§1) closes the "sync observes partial write" failure class for the daemon itself.
2. Confirm sync-detector strategy (§1.4) is acceptable as defense-in-depth (refuses staging in synced paths; warns on output in synced paths).
3. Confirm CLI integration (§2.1) at `src/groundtruth_kb/cli.py` matches actual upstream layout.
4. Confirm `BackupConfig` extension to `GTConfig` (§2.2) is the right shape for adopter config (vs a separate config file).
5. Confirm default snapshot output dirs (§2.3) are OUTSIDE common cloud-sync paths on each platform.
6. Confirm tests 2-6 (§3) are the load-bearing tests for the staging+atomic-publish guarantee.
7. Confirm Agent Red adopter follow-up (§4.3) is correctly framed as a separate bridge (not bundled in upstream work).
8. **GO / NO-GO** on the revised scoping.

## 7. Decision Needed From Owner

None for the scoping. After Codex GO, Prime files the implementation bridge against `groundtruth-kb` upstream. After upstream VERIFIED, Agent Red adopts and Prime files the SyncBackSE-reconfiguration adopter-side bridge.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
