NEW

bridge_kind: prime_proposal
Document: gtkb-fab-03-membase-backup
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4415
Project Authorization: PAUTH-FAB03-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 07ef97df-2cb3-45a4-9c32-be60d702f29c
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/install_db_snapshot_task.ps1", "groundtruth-kb/docs/gt-db-snapshot.md", "platform_tests/scripts/**"]

No KB mutation: FAB-03 performs NO MemBase mutation — `gt db snapshot` READS `groundtruth.db` to produce a consistent VACUUMed copy; the canonical store is unchanged. `groundtruth.db` is intentionally NOT in target_paths (the KB-mutation completeness flag is a false positive triggered by DB-backup language, not by any schema/data write).

---

# FAB-03 — Operationalize MemBase backup (Slice 1: scheduled snapshot + freshness check)

WI-4415 (FAB-03) of PROJECT-FABLE-INVESTIGATION. Finding: HYG-002.
Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

## Summary

The canonical 1.39 GB `groundtruth.db` (GOV-08 source of all project truth) has **no
durable backup**: it is gitignored, deliberately Drive-excluded (post-S311), and the
governed `gt db snapshot` tool (`db_snapshot.py`: VACUUM INTO + integrity-check + atomic
publish; bridge thread `GTKB-DB-BACKUP-001` VERIFIED, `DELIB-2178`) has **never been run
or scheduled**. The only existing copy is an unsanctioned SyncBackSE file-copy of the
live WAL DB *without* its `-wal`/`-shm` companions — the exact S311 corruption class —
whose last run exited `-107`. Two prior corruption incidents make the threat live.

Owner-approved (`DELIB-FAB03-REMEDIATION-20260610`): **staged backup** — Slice 1 here
(validate + schedule the snapshot, add a doctor freshness check, record retention), with
the off-machine upload leg as Slice 2; and **repoint the SyncBackSE mirror** to the
consistent snapshot output (owner-manual; guidance documented).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from specs.
- `GOV-STANDING-BACKLOG-001` — WI-4415 is the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-03-added artifacts (doctor check,
  install script, config keys, docs) are **in-root** under `E:\GT-KB`. The snapshot
  *output* directory is the tool's default **non-synced** location (`%LOCALAPPDATA%\gtkb-snapshots`,
  `db_snapshot.py` default) — intentionally outside the Drive-synced root to prevent the
  S311 sync-vs-WAL corruption; that is the sanctioned design of the VERIFIED
  `GTKB-DB-BACKUP-001` tool (`DELIB-2178`) and a regenerable runtime backup output, not a
  project artifact.

Governing rule (non-spec): `.claude/rules/project-root-boundary.md` (DB snapshots MUST NOT
sit on the Drive-synced `E:` volume; the non-synced output location is the anti-corruption
pattern, consistent with the Sandbox Output Exception rationale).

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-002 in the
  FAB-03 row); evidence frozen, do not re-derive.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB03-REMEDIATION-20260610` — this cluster's owner-decision set (AUQ batch).
- `DELIB-2178` + the VERIFIED `GTKB-DB-BACKUP-001` snapshot-daemon thread — this proposal
  *operationalizes* that already-VERIFIED tool (Slice 1); it does not re-implement it.

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB03-REMEDIATION-20260610`:

1. **Backup posture = Staged** — Slice 1 now (scheduled `gt db snapshot` + doctor
   freshness check + retention in `groundtruth.toml`); Slice 2 off-machine upload
   follow-on. (Rejected: local-only; full-upload-now; accept-risk.)
2. **Unsafe mirror = Repoint SyncBackSE to snapshot output** — owner reconfigures the
   'Backup-to-HDD' task to mirror the consistent snapshot output instead of the live WAL
   DB; corruption-safe G:\ copy retained. (Rejected: disable-mirror; leave-as-is.)

## Requirement Sufficiency

**Existing requirements sufficient.** The snapshot tool and its contract are already
VERIFIED under `GTKB-DB-BACKUP-001` (`DELIB-2178`); GOV-08 establishes the KB-as-truth
requirement this protects. FAB-03 operationalizes existing capability (schedule + doctor
freshness + retention config); no new requirement is needed. The doctor freshness check
encodes a derived invariant (a recent consistent snapshot must exist).

## Proposed Implementation

1. **Validate** — run `gt db snapshot` once; confirm a VACUUMed, integrity-checked file
   lands in the non-synced default output dir; record the size/timing.
2. **Schedule** (`scripts/install_db_snapshot_task.ps1`) — register a daily Windows
   scheduled task running `gt db snapshot` with the tool's retention; idempotent install.
3. **Doctor freshness check** (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`) —
   WARN/FAIL when the newest snapshot is older than a configurable threshold.
4. **Retention config** (`groundtruth.toml`) — record the snapshot retention policy keys.
5. **SyncBackSE repoint guidance** (`groundtruth-kb/docs/gt-db-snapshot.md`) — document how
   the owner reconfigures the HDD-mirror task to copy the consistent snapshot output rather
   than the live WAL DB (owner-manual third-party-tool action).
6. **Tests** (`platform_tests/scripts/**`) — doctor-freshness check (fresh PASS / stale
   WARN-FAIL with a fixture); install-script idempotency.

Slice 2 (off-machine upload leg per `GTKB-DB-BACKUP-001`) is a follow-on, not in this slice.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| GOV-08 (canonical DB must be recoverable) | a consistent snapshot exists in the non-synced output dir after a scheduled run; `PRAGMA integrity_check` = ok |
| `GTKB-DB-BACKUP-001` / `DELIB-2178` (consistent-snapshot contract) | doctor freshness check WARNs/FAILs on a stale-snapshot fixture, PASSes on a fresh one |
| project-root-boundary (no DB backup on synced volume) | install/config place snapshots in the non-synced output dir only; test asserts no snapshot path resolves under the Drive-synced root |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check`/`format --check` on changed `.py` |

## Acceptance Criteria

1. A scheduled task runs `gt db snapshot` daily to the non-synced output dir with retention.
2. The doctor freshness check exists, FAILs/WARNs on stale, PASSes on fresh, and is tested.
3. Retention keys recorded in `groundtruth.toml`; SyncBackSE repoint guidance documented.

## Owner Follow-Up Actions (tracked; do NOT gate VERIFIED)

- Reconfigure the SyncBackSE 'Backup-to-HDD' task to mirror the snapshot output (consistent)
  instead of the live WAL `groundtruth.db` (third-party-tool, owner-manual).
- Authorize/schedule the Slice 2 off-machine upload leg as a follow-on.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-03-membase-backup-001.md` with a matching `NEW` entry at the top
of `bridge/INDEX.md`; append-only, no prior bridge version deleted or rewritten. INDEX
remains canonical workflow state (`GOV-FILE-BRIDGE-AUTHORITY-001` preserved).

## Risk and Rollback

- **Risk:** scheduling overhead / disk use → snapshots are retention-bounded by the tool;
  daily cadence is modest for a 1.39 GB VACUUMed file on the non-synced volume.
- **Risk:** the repoint is owner-manual → documented step-by-step; until done, the new
  scheduled snapshot already provides a consistent local copy independent of SyncBackSE.
- **Rollback:** unregister the scheduled task and revert the doctor/config/docs edits; no
  data mutation to the live DB.

## Recommended Implementation Routing

Mostly mechanical (scheduled-task install, a doctor check, config + docs) — **cheap-model
eligible under supervision**, except the doctor-check edit to the project module which
Claude/Codex should review. The snapshot tool itself is untouched (already VERIFIED).

## Recommended Commit Type

`feat:` — operationalizes backup (scheduled task + doctor freshness check) with `chore:`-class
config/docs edits.
