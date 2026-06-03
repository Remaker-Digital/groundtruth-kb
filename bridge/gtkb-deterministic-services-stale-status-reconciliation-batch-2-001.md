NEW

bridge_kind: governance_review
Document: gtkb-deterministic-services-stale-status-reconciliation-batch-2
Version: 001
Author: Prime Builder (Claude, harness B; session-stated role via ::init gtkb pb)
Date: 2026-06-03 UTC
Recommended commit type: chore
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Items Affected: WI-3424, WI-3261
PAUTH To Be Created: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECON-BATCH-2
Owner Decision: DELIB-20260621
author_identity: Claude Prime Builder (session-stated)
author_harness_id: B
author_session_context_id: 3975dda7-2644-4926-8822-013f4d7aa4f2
author_model: Claude Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

# GT-KB Stale-Status Reconciliation Batch 2 — PROJECT-GTKB-DETERMINISTIC-SERVICES-001

## Bridge Kind Justification

Classified `governance_review`: no source code, tests, hooks, or specification
text are introduced or modified. It is a one-time batch reconciliation of two
`work_items.resolution_status` fields to match bridge audit trails that are
already committed and VERIFIED, executed via the `gt backlog resolve`
deterministic CLI (WI-3436, committed `daf9a4e4`). Per
`.claude/rules/file-bridge-protocol.md`, `governance_review` proposals are
exempt from the single-WI `Work Item:` metadata line; scope spans the two WI
rows that are the subject of governance bookkeeping (both listed in
`Work Items Affected`).

## Summary

Batch 1 (`gtkb-deterministic-services-stale-status-reconciliation`, VERIFIED at
`-012`) reconciled the stale rows in its filing-time snapshot. A read-only
verification of the project's remaining 7 open WIs found exactly **2** more
true stale-status rows — work items whose own implementation thread is VERIFIED
but whose `resolution_status` was never promoted from `open`:

- **WI-3424** (new, P1) — `gt validate spec-coherence` CLI.
- **WI-3261** (new, P2) — `/verify` verdict-author skill + spec-to-test mapping.

This batch promotes those 2 rows to `resolved`, completing the stale-status
close-out for the project. The remaining 5 open WIs (WI-4249, WI-4250, WI-4259,
WI-3429, WI-4266) are NOT stale-status — no bridge thread cites them as a
`Work Item`; they are genuinely-open follow-on work, explicitly out of scope and
left for separate scheduling.

## Owner Decisions / Input

- **Owner selected "Verify + reconcile the stale ones"** via `AskUserQuestion`
  (2026-06-03), recorded as `DELIB-20260621`. The decision authorized verifying
  each open WI's bridge linkage and reconciling the confirmed stale rows.
- This continues the Path B "reconcile stale deterministic-services rows"
  authorization (`DELIB-2737`); batch 2 covers two additional stale rows
  confirmed after batch 1 closed.
- Neither WI is defect/regression origin (both `new`), so no GOV-15
  `--owner-approved` is required; the owner-decision evidence above governs the
  status promotion.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX is canonical workflow state; this
  proposal updates INDEX for the batch reconciliation.
- `GOV-08` — MemBase is the truth; the two `resolution_status` fields must
  reflect actual (VERIFIED) work state. The current `open` readout is incorrect.
- `GOV-15` — Test fix gate; not triggered (both WIs origin=new, not
  defect/regression); cited to document that the gate was evaluated and does not
  require `--owner-approved` here.
- `GOV-STANDING-BACKLOG-001` — Backlog source of truth; visibility-bulk-ops
  clause supports batch reconciliation scoped to one project's known members
  with citation evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — Project authorization governs
  the reconciliation; new PAUTH created below with this spec linked.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Owner decisions, work items, and
  backlog references are durable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Work Items /
  PAUTH / Owner Decision metadata present; bridge_kind exemption claimed above.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Each transition is a lifecycle-valid
  `open → resolved`.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — Mutation classes and forbidden
  operations delimited.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — All target paths inside `E:\GT-KB`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Reconciliation carries the VERIFIED
  bridge ID into `change_reason`.
- `SPEC-AUQ-POLICY-ENGINE-001` — The batch-2 decision was a deterministic
  AskUserQuestion choice, archived as `DELIB-20260621`.

## Prior Deliberations

- `DELIB-20260621` — the batch-2 owner decision (this session); PAUTH
  `--owner-decision` source.
- `DELIB-2737` — S381 Path B owner decision (settle WI-3436, then reconcile
  stale deterministic-services rows). Batch 2 is the continuation.
- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — completed bridge
  verification should mechanically retire the linked backlog item. WI-3424 and
  WI-3261 are exactly this class: VERIFIED implementation, row never promoted.
  The general auto-retire automation has not fired; this is the manual one-time
  batch implementing it for these two rows.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive plumbing moves
  behind deterministic services; each promotion is a single CLI invocation.

## Linkage Verification (read-only, filing-time)

Each WI's own implementation thread cites it as `Work Item` and is latest
`VERIFIED`:

- `gtkb-spec-coherence-cli` cites `Work Item: WI-3424`; latest status
  `VERIFIED: bridge/gtkb-spec-coherence-cli-004.md`.
- `gtkb-verify-verdict-author-skill-slice-1` cites `Work Item: WI-3261`; latest
  status `VERIFIED: bridge/gtkb-verify-verdict-author-skill-slice-1-004.md`.

The 5 excluded open WIs were checked: no bridge file cites WI-4249, WI-4250,
WI-4259, WI-3429, or WI-4266 as a `Work Item`, so none is a stale-status row.

## Live Row Snapshot (filing-time, 2026-06-03)

Direct `work_items` query (latest version per id) immediately before filing:

```text
WI        v   origin  pri  stage         resolution_status
WI-3424   1   new     P1   backlogged    open    <- in scope
WI-3261   2   new     P2   backlogged    open    <- in scope
```

## Proposed Scope

| WI | Origin | Command | New `resolution_status` | Owner-approval | Source bridge VERIFIED |
|---|---|---|---|---|---|
| WI-3424 | new | `backlog resolve` | `resolved` | no | `gtkb-spec-coherence-cli-004.md` (VERIFIED) |
| WI-3261 | new | `backlog resolve` | `resolved` | no | `gtkb-verify-verdict-author-skill-slice-1-004.md` (VERIFIED) |

Out of scope (explicit non-actions): WI-4249, WI-4250, WI-4259, WI-3429,
WI-4266 (genuinely-open; no implementing VERIFIED thread). Left for separate
scheduling.

## target_paths

- `bridge/gtkb-deterministic-services-stale-status-reconciliation-batch-2-*.md`
- `bridge/INDEX.md`
- `groundtruth.db` (2 append-only work_items rows; 1 project_authorizations row)

## Implementation Commands

### Step 0 — Create the active PAUTH

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects authorize PROJECT-GTKB-DETERMINISTIC-SERVICES-001 \
  --id PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECON-BATCH-2 \
  --owner-decision DELIB-20260621 \
  --name "Stale-status reconciliation batch 2 (WI-3424, WI-3261)" \
  --scope "One-time batch promotion of 2 stale WI rows in PROJECT-GTKB-DETERMINISTIC-SERVICES-001 using gt backlog resolve, each citing its VERIFIED implementation bridge thread." \
  --allowed-mutation work_item_status_promotion \
  --include-work-item WI-3424 --include-work-item WI-3261 \
  --include-spec GOV-08 --include-spec GOV-15 --include-spec GOV-STANDING-BACKLOG-001 \
  --include-spec GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 \
  --forbid source --forbid test_addition --forbid spec_status_promotion --forbid hook_upgrade --forbid cli_extension \
  --change-reason "Batch-2 reconciliation PAUTH per DELIB-20260621 (continues DELIB-2737 Path B); GO at gtkb-deterministic-services-stale-status-reconciliation-batch-2."
```

### Step 1 — Two non-defect rows (`resolved`, no owner-approval)

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog resolve WI-3424 \
  --status-detail "Bridge VERIFIED at gtkb-spec-coherence-cli-004." \
  --change-reason "Batch-2 reconciliation per DELIB-20260621; bridge VERIFIED gtkb-spec-coherence-cli-004; gtkb-deterministic-services-stale-status-reconciliation-batch-2."

groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog resolve WI-3261 \
  --status-detail "Bridge VERIFIED at gtkb-verify-verdict-author-skill-slice-1-004." \
  --change-reason "Batch-2 reconciliation per DELIB-20260621; bridge VERIFIED gtkb-verify-verdict-author-skill-slice-1-004; gtkb-deterministic-services-stale-status-reconciliation-batch-2."
```

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-15`, `GOV-08`, `GOV-STANDING-BACKLOG-001`,
`DELIB-S345`, and `DELIB-S312` establish the governance basis. No new
specification capture required.

## Spec-Derived Verification Plan

| Specification | Test / verification command | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | INDEX entry + Codex GO at -002 + post-impl -003 + VERIFIED -004 | Latest INDEX status per bridge protocol |
| `GOV-08` | Re-query work_items rows post-reconciliation via `groundtruth-kb\.venv\Scripts\python.exe -c` SELECT against work_items | Both rows new resolution_status, version +1 |
| `GOV-STANDING-BACKLOG-001` | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json`, then read the returned `work_items` array and confirm WI-3424 + WI-3261 show terminal `resolved` | Both WIs `resolved`; no longer `open` |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` (inspect `authorizations`) | New PAUTH active with 5 included_spec_ids + DELIB-20260621 |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Pre/post snapshot of each transition | Both `open → resolved`; no illegal jumps |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Each linked bridge's terminal verdict via show-thread helper | Both VERIFIED (spec-coherence-cli-004, verify-verdict-author-skill-slice-1-004) |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header Project / Work Items / PAUTH / Owner Decision metadata | Present and machine-parseable |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --stat HEAD..VERIFIED-commit` | All paths under `E:\GT-KB` |
| `SPEC-AUQ-POLICY-ENGINE-001` | DELIB-20260621 read-back | owner_conversation / owner_decision |

## Acceptance Criteria

1. New PAUTH `PAUTH-...-STALE-STATUS-RECON-BATCH-2` active with 2 included WIs,
   5 included specs, and `--owner-decision DELIB-20260621`.
2. WI-3424 and WI-3261 each have a new version with `resolution_status=resolved`,
   `stage=resolved`.
3. Each new version's `change_reason` cites the source VERIFIED bridge ID,
   `DELIB-20260621`, and this proposal slug.
4. `projects show PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` returns a
   `work_items` array in which WI-3424 and WI-3261 show terminal `resolved` and
   neither remains `open`.
5. Pre-impl and post-impl bridge applicability + clause preflights pass with no
   missing required specs and no blocking gaps.

## Risks / Rollback

- **Risk: live drift before implementation.** Mitigation: the implementer
  re-queries WI-3424 and WI-3261 immediately before mutating; any row found
  already-terminal is skipped and noted in the post-impl report (the batch-1
  WI-3263 lesson).
- **Risk: linkage wrong for one row.** Mitigation: each WI's thread cites it as
  `Work Item` and is latest VERIFIED (verified above); Codex re-checks at review.
- **Rollback.** Each mutation is an append-only new version; rollback is one
  further `backlog update` per WI restoring the prior `resolution_status`. No
  information loss; full audit chain preserved.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge/` at `E:\GT-KB\bridge\`,
`groundtruth.db` at `E:\GT-KB\groundtruth.db`. No `applications/` paths touched.
Satisfies `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / `CLAUSE-IN-ROOT`.

## Files Expected To Change

- `bridge/gtkb-deterministic-services-stale-status-reconciliation-batch-2-001.md` (this NEW)
- `bridge/INDEX.md` (NEW entry at top)
- `groundtruth.db` (2 append-only work_items rows; 1 project_authorizations row)

## Recommended Commit Type

`chore` (bookkeeping; no source, test, or spec-text changes).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
