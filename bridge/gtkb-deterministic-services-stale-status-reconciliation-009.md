REVISED

bridge_kind: governance_advisory
Document: gtkb-deterministic-services-stale-status-reconciliation
Version: 009
Responds to: bridge/gtkb-deterministic-services-stale-status-reconciliation-008.md NO-GO
Author: Prime Builder (Codex, harness A)
Date: 2026-06-01 UTC
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: codex-desktop-2026-06-01-gtkb-pb
author_model: GPT-5
author_model_version: codex-session-2026-06-01
author_model_configuration: default-reasoning
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Items Affected: WI-3262, WI-3265, WI-3318, WI-3319, WI-3420, WI-3421, WI-3436
Project Authorization To Create: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECONCILIATION

# Deterministic Services Stale-Status Reconciliation - REVISED-4

## Claim

Reconcile seven stale `current_work_items` rows in
`PROJECT-GTKB-DETERMINISTIC-SERVICES-001` whose source bridge evidence is
already terminal (`VERIFIED` or `WITHDRAWN`) while leaving all genuinely open
deterministic-services work items untouched. This revision fixes the NO-GO
`-008` blocker by including `WI-3436`, whose implementation bridge
`bridge/gtkb-backlog-update-cli-slice-1-006.md` is `VERIFIED` while its MemBase
row remains `resolution_status=open`.

This is not a claim that the whole deterministic-services project is complete.
It is a bounded stale-row reconciliation batch. Rows such as `WI-3261`,
`WI-3424`, `WI-3429`, and `WI-4216` remain open and out of scope unless they
gain separate terminal bridge evidence and authorization.

## Revision Response To NO-GO -008

- Re-queried the live rows immediately before drafting this revision.
- Added `WI-3436` to the mutation set, PAUTH include list, commands,
  verification mapping, and acceptance criteria.
- Removed the false "only three truly-open WIs remain" completion claim.
- Preserved the valid `WI-3263` correction from `-007`: `WI-3263` is already
  `resolved` and remains out of scope.
- Re-dry-ran the exact row commands with current CLI syntax. All seven commands
  validated with `--dry-run --json`.

## Live Row Snapshot

Captured on 2026-06-01 from `gt backlog show <WI> --json`:

| WI | origin | stage | resolution_status | In scope? | Source terminal bridge |
|---|---|---|---|---:|---|
| WI-3262 | new | backlogged | open | yes | `bridge/gtkb-discoverability-cli-slice-2-implementation-006.md` VERIFIED |
| WI-3265 | defect | backlogged | open | yes | `bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-007.md` WITHDRAWN |
| WI-3318 | new | created | open | yes | `bridge/gtkb-gt-bridge-propose-deterministic-cli-006.md` VERIFIED |
| WI-3319 | defect | created | open | yes | `bridge/gtkb-hook-import-latency-chromadb-lazy-010.md` VERIFIED |
| WI-3420 | new | backlogged | open | yes | `bridge/gtkb-hygiene-sweep-cli-004.md` VERIFIED |
| WI-3421 | new | backlogged | open | yes | `bridge/gtkb-hygiene-sweep-skill-008.md` VERIFIED |
| WI-3436 | improvement | backlogged | open | yes | `bridge/gtkb-backlog-update-cli-slice-1-006.md` VERIFIED |
| WI-3263 | hygiene | resolved | resolved | no | already terminal in MemBase |
| WI-3261 | new | backlogged | open | no | no terminal reconciliation scope here |
| WI-3424 | new | backlogged | open | no | needs net-new implementation |
| WI-3429 | new | backlogged | open | no | needs scoping and implementation |
| WI-4216 | new | backlogged | open | no | backlog-capture-only candidate |

## Owner Decisions / Input

- `DELIB-2737` records the S381 Path B owner decision: settle WI-3436 first,
  then reconcile stale deterministic-services rows.
- `DELIB-2737` also supplies the owner-approval basis for terminal transitions
  on defect-origin WIs `WI-3265` and `WI-3319`; the implementation commands
  include `--owner-approved` for those rows.
- No new owner decision is required for this revision. It corrects the row set
  to match the existing owner-approved Path B scope and live terminal bridge
  evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live `bridge/INDEX.md` remains the workflow
  source of truth; this revision only adds an append-only bridge entry.
- `GOV-08` - MemBase lifecycle fields must reflect actual work state.
- `GOV-15` - defect-origin terminal transitions require owner approval; the
  two defect rows use `--owner-approved` and cite `DELIB-2737`.
- `GOV-STANDING-BACKLOG-001` - backlog status reconciliation must remain visible
  and reviewable as a scoped bulk action.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the row mutations require a
  bounded PAUTH before execution.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner decisions, work items, bridge
  evidence, and status transitions stay durable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision
  carries concrete spec, project, and work-item linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below maps
  each linked governance claim to executable checks.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - governance-review
  exemption applies for the single `Work Item:` header, but this revision still
  lists project and affected work items explicitly.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - each proposed row mutation is a
  lifecycle transition from `open` to a terminal status.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - mutation class and forbidden
  operations are delimited in the PAUTH command.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside
  `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the reconciliation ties terminal
  bridge evidence to durable work-item state.
- `SPEC-AUQ-POLICY-ENGINE-001` - the governing owner decision was captured as a
  deterministic AUQ record, `DELIB-2737`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - bridge dispatch remains operative;
  this proposal does not alter dispatch mechanics.

## Prior Deliberations

- `DELIB-2737` - S381 Path B owner decision.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` - completed
  bridge verification should mechanically retire linked backlog work.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive status plumbing
  should move behind deterministic services.
- `DELIB-2546` - S379 owner authorization for `WI-3436` / `gt backlog update`;
  the implementation is now VERIFIED and is included in this stale-row batch.
- `DELIB-S324-OM-DELTA-0004-CHOICE` - backlog ordering semantics; unchanged by
  this status-only reconciliation.

## Target Paths

- `bridge/gtkb-deterministic-services-stale-status-reconciliation-*.md`
- `bridge/INDEX.md`
- `groundtruth.db` append-only `work_items` rows for `WI-3262`, `WI-3265`,
  `WI-3318`, `WI-3319`, `WI-3420`, `WI-3421`, and `WI-3436`
- `groundtruth.db` append-only `project_authorizations` row for the new PAUTH

No source code, tests, hook files, specs, or generated dashboard artifacts are
in scope.

## Implementation Commands After GO

Step 0 - create the active PAUTH:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml projects authorize PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --id PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECONCILIATION --owner-decision DELIB-2737 --name "Stale-status reconciliation batch (Path B Phase 2)" --scope "One-time batch promotion of 7 stale WI rows in PROJECT-GTKB-DETERMINISTIC-SERVICES-001 using gt backlog resolve/update, citing each WI source bridge VERIFIED/WITHDRAWN trail." --allowed-mutation work_item_status_promotion --include-work-item WI-3262 --include-work-item WI-3265 --include-work-item WI-3318 --include-work-item WI-3319 --include-work-item WI-3420 --include-work-item WI-3421 --include-work-item WI-3436 --exclude-work-item WI-3261 --exclude-work-item WI-3263 --exclude-work-item WI-3424 --exclude-work-item WI-3429 --exclude-work-item WI-4216 --include-spec GOV-08 --include-spec GOV-15 --include-spec GOV-STANDING-BACKLOG-001 --include-spec GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 --forbid source --forbid test_addition --forbid spec_status_promotion --forbid hook_upgrade --forbid cli_extension --change-reason "S381 Path B Phase 2 reconciliation PAUTH per DELIB-2737 and GO on gtkb-deterministic-services-stale-status-reconciliation." --json
```

Step 1 - reconcile the seven stale rows:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog resolve WI-3262 --status-detail "Resolved by stale-status reconciliation after source bridge VERIFIED: bridge/gtkb-discoverability-cli-slice-2-implementation-006.md." --change-reason "Reconcile WI-3262 to resolved based on VERIFIED source bridge bridge/gtkb-discoverability-cli-slice-2-implementation-006.md." --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog resolve WI-3318 --status-detail "Resolved by stale-status reconciliation after source bridge VERIFIED: bridge/gtkb-gt-bridge-propose-deterministic-cli-006.md." --change-reason "Reconcile WI-3318 to resolved based on VERIFIED source bridge bridge/gtkb-gt-bridge-propose-deterministic-cli-006.md." --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog resolve WI-3420 --status-detail "Resolved by stale-status reconciliation after source bridge VERIFIED: bridge/gtkb-hygiene-sweep-cli-004.md." --change-reason "Reconcile WI-3420 to resolved based on VERIFIED source bridge bridge/gtkb-hygiene-sweep-cli-004.md." --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog resolve WI-3421 --status-detail "Resolved by stale-status reconciliation after source bridge VERIFIED: bridge/gtkb-hygiene-sweep-skill-008.md." --change-reason "Reconcile WI-3421 to resolved based on VERIFIED source bridge bridge/gtkb-hygiene-sweep-skill-008.md." --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog resolve WI-3319 --owner-approved --status-detail "Resolved by stale-status reconciliation after source bridge VERIFIED: bridge/gtkb-hook-import-latency-chromadb-lazy-010.md; owner-approved via DELIB-2737." --change-reason "Reconcile defect WI-3319 to resolved based on VERIFIED source bridge bridge/gtkb-hook-import-latency-chromadb-lazy-010.md and DELIB-2737." --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog update WI-3265 --resolution-status wont_fix --stage resolved --owner-approved --status-detail "Closed wont_fix by stale-status reconciliation; source bridge WITHDRAWN as superseded by single-harness topology at bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-007.md; owner-approved via DELIB-2737." --change-reason "Reconcile defect WI-3265 to wont_fix based on WITHDRAWN source bridge bridge/gtkb-cross-harness-trigger-codex-exec-hook-firing-001-007.md and DELIB-2737." --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog resolve WI-3436 --status-detail "Resolved by stale-status reconciliation after source bridge VERIFIED: bridge/gtkb-backlog-update-cli-slice-1-006.md." --change-reason "Reconcile WI-3436 to resolved based on VERIFIED source bridge bridge/gtkb-backlog-update-cli-slice-1-006.md." --json
```

`--related-bridge-threads` is intentionally omitted from these commands. The
current CLI stores that option as raw text, and direct PowerShell invocation
stripped embedded JSON quotes during dry-run probes. This reconciliation uses
`status_detail` and `change_reason` for source evidence rather than risking a
malformed linkage string or overwriting existing linkage such as `WI-3436`'s
current related-thread list.

## Specification-Derived Verification

Before filing this revision, these command shapes were executed with
`--dry-run --json`; all returned `updated: false`, `dry_run: true`, and the
expected field set:

- `backlog resolve WI-3262 ... --dry-run --json`
- `backlog resolve WI-3318 ... --dry-run --json`
- `backlog resolve WI-3420 ... --dry-run --json`
- `backlog resolve WI-3421 ... --dry-run --json`
- `backlog resolve WI-3319 --owner-approved ... --dry-run --json`
- `backlog update WI-3265 --resolution-status wont_fix --stage resolved --owner-approved ... --dry-run --json`
- `backlog resolve WI-3436 ... --dry-run --json`

After GO and execution, Prime must verify:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog show WI-3262 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog show WI-3265 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog show WI-3318 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog show WI-3319 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog show WI-3420 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog show WI-3421 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml backlog show WI-3436 --json
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb --config E:\GT-KB\groundtruth.toml projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
```

Expected results:

- `WI-3262`, `WI-3318`, `WI-3319`, `WI-3420`, `WI-3421`, and `WI-3436` have
  `resolution_status=resolved` and `stage=resolved`.
- `WI-3265` has `resolution_status=wont_fix` and `stage=resolved`.
- The new PAUTH exists, is active, includes only the seven in-scope rows, and
  allows only `work_item_status_promotion`.
- Out-of-scope open rows remain open.

## Acceptance Criteria

- LO confirms the `WI-3436` omission from `-007` is fixed.
- LO confirms this revision no longer claims complete deterministic-services
  closure.
- LO confirms `WI-3263` remains excluded because it is already terminal.
- LO confirms the seven command shapes are executable and owner-approved where
  GOV-15 requires it.
- LO grants GO for the bounded row reconciliation and PAUTH creation.

## Risk And Rollback

Risk is confined to MemBase lifecycle fields for seven rows and one PAUTH row.
The CLI writes append-only versions, so rollback is a follow-up append-only
correction using the same `gt backlog update` surface, with a change reason
citing this bridge thread. No source, test, hook, spec, or deployment surfaces
are touched.

## Decision Needed From Owner

None. This revision is still within `DELIB-2737` Path B: include the now-VERIFIED
`WI-3436` phase-1 row in the stale-status reconciliation rather than leaving it
open.
