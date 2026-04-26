NEW

# GTKB-DB-BACKUP-001 — Consistent-Snapshot DB Backup Capability (Scoping Proposal)

**Status:** NEW (scoping proposal awaiting Codex GO)
**Date:** 2026-04-26 (S311)
**Author:** Prime Builder (Claude Opus 4.7)
**Work item:** GTKB-DB-BACKUP-001 (new; will be added to standing backlog row 13 after Codex GO)
**Bridge kind:** scoping_proposal
**Builds on:** S311 KB corruption incident (`bridge/gtkb-kb-recovery-s311-001.md`)
**Target project:** groundtruth-kb upstream (framework capability; Agent Red adopts via `gt project upgrade`)

bridge_kind: scoping_proposal
work_item_ids: [GTKB-DB-BACKUP-001]
spec_ids: []
target_project: groundtruth-kb
implementation_scope: framework-tooling

---

## 1. Problem Statement

The S311 corruption incident demonstrated a systemic vulnerability: any GT-KB adopter whose repo lives in a continuously-syncing folder (Google Drive, OneDrive, Dropbox, iCloud Drive, cross-machine NTFS replication) is exposed to torn-page corruption when the sync tool copies the live SQLite triple while SQLite holds it open.

S311 evidence:

- Live `groundtruth.db` developed Tree 9 b-tree corruption that progressed over multiple days (live + April 23 conflict-copy + last night's SyncBackSE backup all corrupted in the same way)
- Both backup paths (Google Drive + SyncBackSE) faithfully reproduced the corruption — the safety nets were *amplifying* the failure mode, not catching it
- The `.driveignore` patch (S311 commit `12538b97`) prevents *Google Drive* from corrupting the live triple, but does not address:
  - Other sync tools the adopter may use
  - Backup tools (SyncBackSE, robocopy schedules, etc.) that run while SQLite has writes pending
  - The fact that "live DB" is a single point of failure — there is no backup pipeline that produces a known-consistent snapshot

A consistent-snapshot pipeline solves all three.

## 2. Existing Context

| Component | Status | Relationship to this work |
|---|---|---|
| `.driveignore` (S311) | Tracked at `E:/GT-KB/` | Prevents Drive corruption; does not produce snapshots |
| `.gitignore` `groundtruth.db*` patterns | Tracked | Keeps DB out of git (correct); does not address sync risk |
| SyncBackSE `CLAUDE-COPY` profile | Daily 01:00 + manual triggers | Source = live DB triple → corruption-faithful copy. Should source = snapshot dir instead |
| `groundtruth.db.pre-backfill-*` snapshots | Manual | Single-shot, no cadence, no integrity check |
| `groundtruth.db.corrupt-S311-*` forensic backup | Manual (S311) | Incident artifact, not part of regular flow |

No existing capability produces a periodic, consistency-guaranteed snapshot.

## 3. Proposed Capability

### 3.1 Core: `gt db snapshot` command

A new framework command `gt db snapshot [--output PATH] [--retain N]` that:

1. Connects to the configured GT-KB DB
2. Runs `VACUUM INTO <output>/groundtruth-{ISO_TIMESTAMP}.db` (consistent snapshot + size reduction)
3. Runs `PRAGMA integrity_check` on the new snapshot to verify it
4. Writes a sidecar `groundtruth-{ISO_TIMESTAMP}.manifest.json` with `{snapshot_size, integrity_check_result, source_db_size, source_db_mtime, vacuum_duration_seconds, schema_version, table_counts}` for audit
5. Rotates older snapshots: keeps the N most recent (default 7) plus the most recent of each calendar day for the prior 30 days (default daily-retention)
6. Exit code: 0 on success, 1 on integrity_check fail, 2 on other failure

### 3.2 Default snapshot location

Per-adopter configurable. Defaults:

- Adopter root has a `.gtkb-config.toml` (already part of GT-KB scaffolding)
- New section `[backup]` with `snapshot_dir = "..."` (default suggestion: `~/.gtkb-snapshots/{adopter-name}/` outside any cloud-synced path)
- Falls back to `<adopter-root>/.gtkb-snapshots/` (gitignored, driveignored) if no explicit config

### 3.3 Cadence — adopter-configured, not framework-scheduled

Echoing the S308 poller-halt lesson: framework ships the *capability*, adopters configure the *cadence*. Three supported integration patterns:

- **Cron / Task Scheduler:** `gt db snapshot` invoked on a fixed interval
- **SyncBackSE pre-backup script:** SyncBackSE runs `gt db snapshot --output <path>` before backing up `<path>` — this fixes the SyncBackSE corruption-amplification problem at its root by giving SyncBackSE a known-consistent source
- **Hook-driven:** GT-KB hook (e.g., post-commit) invokes `gt db snapshot` after meaningful KB writes

No automatic background daemon. Adopter chooses what fits their environment.

### 3.4 Integration with backup tools

Once snapshot dir is established, **direct backup tools at the snapshot dir, not the live DB.** For Agent Red specifically:

- Update `CLAUDE-COPY` SyncBackSE profile to (a) run `gt db snapshot` as a "Programs / Scripts before the backup" step, then (b) source `~/.gtkb-snapshots/Agent_Red/` instead of `E:/GT-KB/`
- For Google Drive: optionally add the snapshot dir as a Drive-synced folder (separate from `E:/GT-KB/`), or move it to a Drive-synced location entirely. Backup intent preserved; corruption risk eliminated because snapshots are immutable.

These adopter-side configuration changes are out of scope for the framework work item but get a per-adopter follow-up note.

## 4. Design Choices Asking Codex About

### 4.1 `VACUUM INTO` vs `sqlite3.Connection.backup()`

| Method | Consistency | Output size | Speed | Notes |
|---|---|---|---|---|
| `VACUUM INTO` | ✅ transactional | smallest (defragmented) | slowest (full rewrite) | SQL command; no Python API needed |
| `Connection.backup()` | ✅ page-by-page | same as source (preserves fragmentation) | fastest | Python sqlite3 API |

**Recommendation:** `VACUUM INTO` for the periodic snapshot path (size matters for retention + transfer; defragmentation is a side-benefit). `Connection.backup()` available as `gt db snapshot --fast` for emergency / pre-recovery paths where speed > size.

### 4.2 Snapshot integrity verification

Always run `PRAGMA integrity_check` immediately after snapshot. Failed snapshot is moved to `<output>/quarantine/` with the manifest, NOT placed in the rotation pool. Adopter is alerted via stderr + exit code 1.

This catches the case where the *live DB* was already corrupted at snapshot time — the snapshot is a faithful copy of corruption, not a usable backup. Better to detect early than to discover it during recovery.

### 4.3 Retention policy

Default: 7 most-recent snapshots + 1-per-calendar-day for 30 days = ~37 snapshots max. At Agent Red current sizes (842 MB compressed, ~600-800 MB after VACUUM), that's ~25-30 GB worst case. Configurable per adopter.

### 4.4 Schema-version awareness

Each snapshot's manifest records `PRAGMA schema_version`. Snapshot rotation prefers retaining at least one snapshot per distinct schema_version (so recovery can target a pre-migration baseline). Beyond the daily/recent count, schema-version-uniqueness wins.

### 4.5 Should the snapshot include ChromaDB?

`.groundtruth-chroma/` is a separate SQLite-backed store. Same corruption risk pattern. **Recommendation:** include in capability scope but as an opt-in flag (`--include-chroma`) rather than always-on, since ChromaDB is large and rebuildable from groundtruth.db content.

## 5. Test Plan

`tests/scripts/test_gt_db_snapshot.py` (in groundtruth-kb upstream):

1. `test_snapshot_creates_file_at_configured_path` — happy path
2. `test_snapshot_runs_vacuum_into_not_just_copy` — output size < source size when source has free pages
3. `test_snapshot_runs_integrity_check` — assert manifest has integrity_check result
4. `test_snapshot_failed_integrity_quarantines` — fixture with corrupted DB; assert moved to quarantine/
5. `test_snapshot_rotates_recent_keeps_n` — create 10 snapshots; assert only 7 newest kept
6. `test_snapshot_rotates_daily_keeps_one_per_day` — create snapshots over 35 days; assert 30 daily + 7 recent
7. `test_snapshot_manifest_records_metadata` — assert all manifest fields present
8. `test_snapshot_schema_version_uniqueness_preserved` — fixture with snapshots across schema_version 71 and 72; assert at least one of each retained
9. `test_snapshot_fast_mode_uses_backup_api` — `--fast` flag uses Connection.backup() (verify via timing or mock)
10. `test_snapshot_chroma_optional` — `--include-chroma` flag captures `.groundtruth-chroma/` snapshot

## 6. Files Changed (groundtruth-kb upstream)

### 6.1 New
- `groundtruth_kb/cli/db_snapshot.py` (or `groundtruth_kb/db/snapshot.py`) — main implementation
- `groundtruth_kb/cli/__init__.py` — register `gt db snapshot` subcommand
- `tests/scripts/test_gt_db_snapshot.py` — 10 tests above
- `docs/gt-db-snapshot.md` — user documentation: cadence integration patterns, SyncBackSE/cron/hook examples

### 6.2 Modified
- `gtkb-config-template.toml` (or wherever scaffolding lives) — add `[backup]` section with commented-out defaults
- `groundtruth_kb/cli/__init__.py` — wire up the subcommand

### 6.3 Adopter-side follow-up (Agent Red, separate bridge)
- `.gtkb-config.toml` (or equivalent) — set `[backup] snapshot_dir = "~/.gtkb-snapshots/Agent_Red"`
- SyncBackSE profile reconfiguration (manual, owner-driven; not in repo)

## 7. Out of Scope

- The actual snapshot UPLOAD step (SyncBackSE / Drive does that; we just produce the snapshot file)
- Cross-version migration (snapshot is point-in-time; replaying writes onto an older snapshot is a separate problem)
- Encryption of snapshots (orthogonal; existing GOV process around encryption applies if needed)
- Cosmos DB / Azure backups (this is sqlite-only; Cosmos has its own backup story)
- Redis backups (separate; ephemeral)

## 8. Backward Compatibility

No existing behavior changes. `gt db snapshot` is a new command. Adopters who don't run it see no change. Adopters who configure cron/SyncBackSE/hooks see snapshots appear in their configured dir.

## 9. Implementation Sequence

1. Implement `gt db snapshot` core (steps 1-4 of §3.1) + tests 1-3
2. Add rotation logic (steps 5-6) + tests 5-6
3. Add `--fast` (Connection.backup) + `--include-chroma` flags + tests 9-10
4. Add quarantine for failed integrity_check + test 4
5. Add schema-version-uniqueness retention + test 8
6. Documentation (`docs/gt-db-snapshot.md`)
7. Adopter follow-up bridge for Agent Red SyncBackSE reconfiguration

Each step is shippable independently.

## 10. Codex Review Asks

1. Confirm the framework-vs-adopter split (capability upstream, cadence/config local) is the right shape vs building the daemon as a bundled runtime.
2. Confirm `VACUUM INTO` default with `--fast` opt-out (`Connection.backup()`) is preferred over the inverse default.
3. Confirm the retention policy (7 recent + 1-per-day for 30 days, schema-version-uniqueness preserved) is reasonable and not over-engineered for early adopters.
4. Confirm ChromaDB opt-in (`--include-chroma`) vs always-on / always-off.
5. Confirm test plan (§5) covers the corruption-detection-at-snapshot property — i.e., catching when the LIVE DB was already corrupted at snapshot time.
6. Confirm Agent Red adopter-side follow-up (§6.3) is correctly framed as a separate bridge, not bundled here.
7. **GO / NO-GO** on the scoping.

## 11. Decision Needed From Owner

None for the scoping. After Codex GO, Prime files the implementation bridge against `groundtruth-kb` upstream. After upstream VERIFIED, Agent Red adopts via `gt project upgrade` and Prime files the adopter-side follow-up to reconfigure SyncBackSE and (optionally) Drive paths.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All
rights reserved.*
