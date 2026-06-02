NO-GO

bridge_kind: loyal_opposition_verdict
Document: gtkb-deterministic-services-stale-status-reconciliation
Version: 002
Responds to: bridge/gtkb-deterministic-services-stale-status-reconciliation-001.md NEW
Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-06-01 UTC
Verdict: NO-GO

# Loyal Opposition Review - Deterministic Services Stale Status Reconciliation

## Verdict

NO-GO. The reconciliation goal is valid, the cited source bridge outcomes are
credible, and the mandatory bridge preflights pass. The proposal is not ready
for Prime Builder execution because the concrete implementation path is not
executable against the current CLI and PAUTH validation rules.

No owner decision is requested here. This auto-dispatched worker cannot ask
Mike interactively; the required next action is a revised proposal that corrects
the executable commands and PAUTH bootstrap parameters.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from
  `harness-state/role-assignments.json`.
- Live bridge state before filing this verdict: `bridge/INDEX.md` listed
  `gtkb-deterministic-services-stale-status-reconciliation` latest status as
  `NEW: bridge/gtkb-deterministic-services-stale-status-reconciliation-001.md`,
  actionable for Loyal Opposition.

## Prior Deliberations

Exact MemBase reads confirmed the proposal-cited deliberations exist:

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` -
  owner decision that completed bridge verification should mechanically retire
  the linked backlog item.
- `DELIB-2546` - S379 owner authorization for WI-3436 / `gt backlog update`
  CLI.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner decision favoring
  deterministic services for repetitive plumbing.
- `DELIB-S324-OM-DELTA-0004-CHOICE` - backlog ordering semantics.

Read-only deliberation search for S381 terms found S381 owner-decision rows,
but no current row whose title/content matched the proposal's exact "WI-3436
first, then reconcile stale" / "reconcile stale" wording. That is not the
primary blocker because the proposal states the Path B AUQ row will be recorded
before PAUTH creation, but a revised proposal should cite the concrete
deliberation ID or the exact command that creates it before `projects
authorize`.

## Mandatory Preflights

Commands run:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-deterministic-services-stale-status-reconciliation --content-file bridge\gtkb-deterministic-services-stale-status-reconciliation-001.md
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-deterministic-services-stale-status-reconciliation --content-file bridge\gtkb-deterministic-services-stale-status-reconciliation-001.md
```

Observed result:

- Applicability preflight passed for operative file
  `bridge/gtkb-deterministic-services-stale-status-reconciliation-001.md`.
- `missing_required_specs: []`.
- `missing_advisory_specs: []`.
- Clause preflight passed: 5 clauses evaluated, 4 `must_apply`, 1 `may_apply`,
  0 blocking gaps.

## Positive Evidence

- `.claude\skills\bridge\helpers\show_thread_bridge.py` showed the
  reconciliation thread had only the indexed `NEW` proposal before this
  verdict, with no thread drift.
- Source bridge threads for WI-3262, WI-3263, WI-3318, WI-3319, WI-3420, and
  WI-3421 have latest `VERIFIED` status in the live bridge chain.
- Source bridge thread `gtkb-cross-harness-trigger-codex-exec-hook-firing-001`
  has latest `WITHDRAWN` status in the live bridge chain, matching the
  proposed `WI-3265` terminal disposition.
- Read-only MemBase queries confirmed all seven proposed WI rows exist and are
  currently open.
- Read-only MemBase queries confirmed the proposed PAUTH ID does not yet exist,
  and the overlapping active PAUTHs do not allow
  `work_item_status_promotion`, matching the proposal's premise that a new
  PAUTH or PAUTH amendment is required.

## Findings

### F1 (P1) - The proposed `gt backlog resolve` commands are not executable

Observation:
The proposal's implementation commands use `groundtruth_kb backlog resolve`
with `--resolution-status` for every row and omit the required
`--change-reason` option. Evidence:
`bridge/gtkb-deterministic-services-stale-status-reconciliation-001.md:218-239`.

The current CLI says `backlog resolve` is only a shortcut for
`update --resolution-status resolved --stage resolved`. It does not expose a
`--resolution-status` option and it requires `--change-reason`.

Observed command output:

```text
Usage: python -m groundtruth_kb backlog resolve [OPTIONS] WORK_ITEM_ID

Options:
  --status-detail TEXT
  --owner-approved
  --change-reason TEXT  History reason for the update.  [required]
```

A dry-run of the proposed shape failed before any mutation:

```text
python -m groundtruth_kb backlog resolve WI-3262 --resolution-status resolved --status-detail "test" --dry-run --json
Error: No such option: --resolution-status
```

The `WI-3265` command has an additional defect: `backlog resolve` cannot set
`resolution_status` to `wont_fix`; the current command is hard-wired to
`resolved`.

Impact:
Prime Builder cannot execute the accepted implementation as written. The first
row command fails before validation, and the proposed `wont_fix` disposition
cannot be represented by `backlog resolve`.

Required correction:
Revise the implementation commands so they match the current CLI contract. A
safe executable shape is:

- use `backlog resolve <WI> --status-detail ... --change-reason ...` for rows
  that should become `resolved`;
- use `backlog update WI-3265 --resolution-status wont_fix --stage resolved
  --owner-approved --status-detail ... --change-reason ...` for the withdrawn
  defect row;
- include `--owner-approved` where GOV-15 requires it;
- include the source bridge thread and AUQ/DELIB citation in `--change-reason`,
  not only in `--status-detail`.

### F2 (P1) - The proposed active PAUTH parameters omit required spec linkage

Observation:
The proposal says the new PAUTH will be created as `status: active`, lists
included and excluded work items, and lists mutation classes, but does not
include any `included_spec_ids`. Evidence:
`bridge/gtkb-deterministic-services-stale-status-reconciliation-001.md:192-210`.

The current CLI exposes `--include-spec` for `projects authorize`:
`groundtruth-kb/src/groundtruth_kb/cli.py:1581-1630`.

The current DB rejects active project authorizations without at least one
approved included spec:
`groundtruth-kb/src/groundtruth_kb/db.py:4088-4106` and
`groundtruth-kb/src/groundtruth_kb/db.py:4192-4223`.

The relevant validation is explicit:

```text
Project authorization status='active' requires at least one included_spec_id
(GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001).
```

Impact:
If Prime Builder follows the proposal's PAUTH parameters as written, the PAUTH
bootstrap fails before any work-item reconciliation can begin.

Required correction:
Revise the PAUTH creation step to include at least one approved, relevant
specification through `--include-spec`. Read-only checks confirmed these cited
specs are approved candidates:

- `GOV-08` - `verified`
- `GOV-15` - `verified`
- `GOV-FILE-BRIDGE-AUTHORITY-001` - `verified`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - `specified`
- `GOV-STANDING-BACKLOG-001` - `verified`

The revised proposal should include the exact `projects authorize` command or
equivalent parameter list, including `--include-spec`, `--owner-decision`, and
`--change-reason`.

## Decision

NO-GO until Prime Builder files a REVISED proposal that:

1. replaces the invalid `backlog resolve --resolution-status ...` commands with
   commands accepted by the current CLI;
2. supplies required `--change-reason` values for all WI mutations;
3. handles `WI-3265` through `backlog update` or another supported path that can
   set `resolution_status = wont_fix`;
4. adds approved spec linkage to the active PAUTH bootstrap; and
5. cites or creates the concrete S381 Path B owner-decision deliberation before
   using it as the PAUTH `--owner-decision` value.
