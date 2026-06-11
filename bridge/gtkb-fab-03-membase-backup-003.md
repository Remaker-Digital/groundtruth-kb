REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-03-membase-backup
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4415
Project Authorization: PAUTH-FAB03-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 430d5513-21a1-4e1c-b244-743f2ca7ed00
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "scripts/install_db_snapshot_task.ps1", "groundtruth-kb/docs/gt-db-snapshot.md", "platform_tests/scripts/**", ".claude/rules/project-root-boundary.md", ".groundtruth/formal-artifact-approvals/2026-06-11-project-root-boundary-db-snapshot-exception.json"]

No KB mutation: FAB-03 performs NO MemBase mutation — `gt db snapshot` READS `groundtruth.db` to produce a consistent VACUUMed copy; the canonical store is unchanged. The owner-decision evidence (`DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611`) was captured out-of-band via the decision-capture path; it is not part of this proposal's implementation. `groundtruth.db` is intentionally NOT in target_paths (the KB-mutation completeness flag is a false positive triggered by DB-backup language).

---

# FAB-03 — Operationalize MemBase backup (Slice 1: scheduled snapshot + freshness check), REVISED

WI-4415 (FAB-03) of PROJECT-FABLE-INVESTIGATION. Finding: HYG-002.
Revises the proposal after the verification NO-GO at
`bridge/gtkb-fab-03-membase-backup-002.md` (FINDING-P1-001).

## Revision Scope

This revision addresses the single finding in the `-002` NO-GO:

> FINDING-P1-001 — Out-of-root snapshot output lacks a current root-boundary exception.

The Slice-1 design schedules `gt db snapshot` output and a doctor freshness check
against the tool's non-synced default `%LOCALAPPDATA%\gtkb-snapshots`, which is
**outside** `E:\GT-KB`. The active `.claude/rules/project-root-boundary.md`
forbids out-of-root GT-KB artifacts that are created, scheduled, or
doctor-verified as live evidence unless a formal exception covers them — and the
existing **Sandbox Output Exception** allowlists only rehearsal-class
`C:/temp/agent-red-rehearsal*` / `/tmp/agent-red-rehearsal*` paths. It does NOT
cover `%LOCALAPPDATA%\gtkb-snapshots`.

Per the owner decision recorded at `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611`
(AskUserQuestion, 2026-06-11), this revision keeps the off-root `%LOCALAPPDATA%`
output for stronger disaster recovery (a separate physical drive survives an `E:`
drive failure; co-locating backups under `E:\GT-KB` would lose live DB and
backups together) and **adds a formal DB-Snapshot Output Exception** to the
implementation scope:

1. **Rule amendment** — add a `## DB-Snapshot Output Exception` section to
   `.claude/rules/project-root-boundary.md`, structured exactly like the existing
   `## Sandbox Output Exception`: it authorizes a bounded DB-snapshot output path
   outside `E:\GT-KB`, cites `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611` as the
   owner-decision evidence, enumerates the allowlist
   (`%LOCALAPPDATA%\gtkb-snapshots` / the cross-platform equivalent), states the
   anti-corruption rationale (snapshots must avoid the Drive-synced `E:` volume
   that caused the S311 WAL corruption), and bounds the exception to regenerable
   snapshot output only (not canonical project state). Filed under a
   narrative-approval packet
   (`.groundtruth/formal-artifact-approvals/2026-06-11-project-root-boundary-db-snapshot-exception.json`).
2. **Enforceable allowlist + doctor bound** — add a snapshot-output allowlist
   constant and a deterministic check (in
   `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, alongside the freshness
   check) confirming the configured/scheduled snapshot output resolves to an
   allowlisted path, mirroring how `_check_external_harness_exec_boundary` /
   `scripts/rehearse/_common.py::_OUTPUT_DIR_ALLOWLIST_PATTERNS` bound the sandbox
   exception.
3. **Rule-text-vs-source parity test** — add a test (in
   `platform_tests/scripts/**`) asserting the rule-text allowlist quotation equals
   the source allowlist constant, mirroring `test_rehearse_isolation.py`'s parity
   assertion, so rule and code never drift.
4. **Correct the misframing** — the `-001` text described the snapshot output as
   "consistent with the Sandbox Output Exception rationale"; this revision stops
   implying the rehearsal-only Sandbox Output Exception already authorizes
   `%LOCALAPPDATA%\gtkb-snapshots` and instead introduces the dedicated
   DB-Snapshot Output Exception above.

The Slice-1 operational scope (validate + schedule snapshot, doctor freshness
check, retention config, SyncBackSE repoint guidance) is otherwise unchanged.

## Summary

The canonical 1.39 GB `groundtruth.db` (GOV-08 source of all project truth) has
**no durable backup**: it is gitignored, deliberately Drive-excluded (post-S311),
and the governed `gt db snapshot` tool (VERIFIED under `GTKB-DB-BACKUP-001`,
`DELIB-2178`) has never been scheduled. Slice 1 validates + schedules the
snapshot to its non-synced output, adds a doctor freshness check + retention
config, documents the SyncBackSE repoint, and — per this revision — formally
authorizes the off-root snapshot output via a new root-boundary exception with an
enforceable allowlist + parity test.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge lifecycle authority for this proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived from specs.
- `GOV-STANDING-BACKLOG-001` — WI-4415 is the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-03 CODE/CONFIG/RULE/TEST/
  packet artifacts are **in-root** under `E:\GT-KB`. The snapshot *output*
  directory is the off-root `%LOCALAPPDATA%\gtkb-snapshots`, authorized by the new
  DB-Snapshot Output Exception added to `project-root-boundary.md` by this
  proposal (owner-decision evidence: `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611`),
  exactly as the rehearsal Sandbox Output Exception authorizes its allowlisted
  off-root rehearsal output.

## Isolation Placement Compliance

Every CODE, CONFIG, RULE, TEST, DOCS, and approval-packet artifact this proposal
creates or edits remains **in-root under `E:\GT-KB`**: `groundtruth.toml`, the
doctor check + allowlist in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`,
the install script, the docs, the parity test under `platform_tests/scripts/`,
the rule amendment to `.claude/rules/project-root-boundary.md`, and the
narrative-approval packet under `.groundtruth/formal-artifact-approvals/`. The
ONLY out-of-root element is the regenerable DB-snapshot **output**
(`%LOCALAPPDATA%\gtkb-snapshots`), which this proposal brings under an explicit,
owner-authorized, allowlist-bounded root-boundary exception — the sanctioned
pattern for regenerable runtime output that must avoid the Drive-synced `E:`
volume, identical in shape to the existing in-root Sandbox Output Exception.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-002 in the
  FAB-03 row); evidence frozen, do not re-derive.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB03-REMEDIATION-20260610` — this cluster's original owner-decision set
  (staged backup; repoint SyncBackSE); the `%LOCALAPPDATA%` choice is preserved.
- `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611` — the owner AUQ decision (this
  revision) selecting the formal off-root exception over an in-root redesign.
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` — the precedent
  owner decision that added the Sandbox Output Exception this exception mirrors.
- `DELIB-2178` + the VERIFIED `GTKB-DB-BACKUP-001` snapshot-daemon thread — this
  proposal operationalizes that already-VERIFIED tool; it does not re-implement it.

## Owner Decisions / Input

1. **Backup posture = Staged** (`DELIB-FAB03-REMEDIATION-20260610`, AUQ 2026-06-10)
   — Slice 1 now (scheduled `gt db snapshot` + doctor freshness + retention);
   Slice 2 upload follow-on. Unchanged.
2. **Unsafe mirror = Repoint SyncBackSE to snapshot output**
   (`DELIB-FAB03-REMEDIATION-20260610`, AUQ 2026-06-10). Unchanged.
3. **Snapshot-output root-boundary = Formal off-root exception**
   (`DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611`, AskUserQuestion 2026-06-11,
   session 430d5513). Owner chose to keep `%LOCALAPPDATA%` (stronger DR — survives
   an `E:` drive failure) and add a formal DB-Snapshot Output Exception with
   owner-decision evidence + an allowlist + tests, mirroring the Sandbox Output
   Exception. Rejected: in-root `.driveignore`-excluded redesign (co-locates
   backups on the same `E:` drive as the live DB — weaker DR).

## Requirement Sufficiency

**Existing requirements sufficient.** The snapshot tool + contract are already
VERIFIED under `GTKB-DB-BACKUP-001` (`DELIB-2178`); GOV-08 establishes the
KB-as-truth requirement this protects; the root-boundary rule already provides
the exception mechanism, and `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611`
supplies the owner-decision evidence authorizing this specific exception. No new
SPEC is needed: the DB-Snapshot Output Exception is a rule amendment of the same
form as the existing Sandbox Output Exception (a narrative section backed by an
owner-decision DELIB), not a new specification surface.

## Proposed Implementation

1. **Validate** — run `gt db snapshot` once; confirm a VACUUMed, integrity-checked
   file lands in `%LOCALAPPDATA%\gtkb-snapshots`; record size/timing.
2. **Schedule** (`scripts/install_db_snapshot_task.ps1`) — idempotent daily
   Windows task running `gt db snapshot` with the tool's retention.
3. **DB-Snapshot Output Exception** (`.claude/rules/project-root-boundary.md` +
   narrative-approval packet) — add the exception section per the Revision Scope
   above (allowlist, owner-decision citation, rationale, regenerable-output bound).
4. **Allowlist + doctor bound** (`groundtruth-kb/src/groundtruth_kb/project/doctor.py`)
   — a snapshot-output allowlist constant + a deterministic check that the
   scheduled/configured snapshot path resolves to an allowlisted location, plus
   the freshness check (WARN/FAIL when the newest snapshot is stale).
5. **Retention config** (`groundtruth.toml`) — record the snapshot retention keys.
6. **SyncBackSE repoint guidance** (`groundtruth-kb/docs/gt-db-snapshot.md`) —
   document the owner-manual HDD-mirror repoint to the snapshot output.
7. **Tests** (`platform_tests/scripts/**`) — doctor freshness (fresh PASS / stale
   WARN-FAIL); install idempotency; **allowlist enforcement** (out-of-allowlist
   path rejected); **rule-text-vs-source allowlist parity** (rule quotation ==
   source constant).

Slice 2 (off-machine upload leg per `GTKB-DB-BACKUP-001`) is a follow-on.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| GOV-08 (canonical DB must be recoverable) | a consistent snapshot exists in the non-synced output dir after a scheduled run; `PRAGMA integrity_check` = ok |
| `GTKB-DB-BACKUP-001` / `DELIB-2178` (consistent-snapshot contract) | doctor freshness check WARNs/FAILs on a stale-snapshot fixture, PASSes on a fresh one |
| `DELIB-FAB03-ROOT-BOUNDARY-EXCEPTION-20260611` (snapshot output bounded to the allowlist) | doctor allowlist check rejects an out-of-allowlist snapshot path; rule-text-vs-source parity test asserts the rule allowlist quotation equals the source constant |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (no unbounded out-of-root dependency) | all code/config/rule/test/packet artifacts in-root; the only out-of-root element (snapshot output) is allowlist-bounded by the new exception |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check`/`format --check` on changed `.py` |

## Acceptance Criteria

1. A scheduled task runs `gt db snapshot` daily to the allowlisted non-synced
   output dir with retention.
2. The doctor freshness check exists, FAILs/WARNs on stale, PASSes on fresh, tested.
3. The DB-Snapshot Output Exception is added to `project-root-boundary.md` (under a
   narrative-approval packet), with an enforceable allowlist + a rule-text-vs-source
   parity test; the rehearsal Sandbox Output Exception is no longer described as
   covering snapshot output.
4. Retention keys recorded in `groundtruth.toml`; SyncBackSE repoint guidance documented.

## Backlog Visibility

WI-4415 is the governed backlog authority for this work; the exception addition is
recorded under a formal-artifact-approval packet (no bulk backlog mutation).

## Owner Follow-Up Actions (tracked; do NOT gate VERIFIED)

- Reconfigure the SyncBackSE 'Backup-to-HDD' task to mirror the snapshot output
  (consistent) instead of the live WAL `groundtruth.db` (third-party-tool, manual).
- Authorize/schedule the Slice 2 off-machine upload leg as a follow-on.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-03-membase-backup-003.md` with a matching `REVISED`
entry inserted at the top of the `gtkb-fab-03-membase-backup` entry in
`bridge/INDEX.md`; append-only, no prior bridge version deleted or rewritten.
`bridge/INDEX.md` remains canonical workflow state (`GOV-FILE-BRIDGE-AUTHORITY-001`
preserved).

## Risk and Rollback

- **Risk:** scheduling overhead / disk use → retention-bounded by the tool; daily
  cadence is modest for a 1.39 GB VACUUMed file on the non-synced volume.
- **Risk:** the exception widens out-of-root authority → bounded by an explicit
  allowlist + a deterministic doctor check + a rule-text-vs-source parity test, so
  the exception cannot silently broaden; identical containment to the Sandbox
  Output Exception.
- **Rollback:** unregister the task; revert the doctor/config/docs/rule edits and
  remove the exception section + packet; no mutation to the live DB.

## Recommended Commit Type

`feat:` — operationalizes backup (scheduled task + doctor freshness + allowlist
check) and adds a governed root-boundary exception, with `chore:`-class config/docs
edits and a `docs:`-class rule amendment.
