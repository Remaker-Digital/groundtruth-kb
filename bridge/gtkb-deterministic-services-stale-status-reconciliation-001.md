NEW

bridge_kind: governance_review
Document: gtkb-deterministic-services-stale-status-reconciliation
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-01 UTC
Session: S381
Recommended commit type: chore
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Items Affected: WI-3262, WI-3263, WI-3265, WI-3318, WI-3319, WI-3420, WI-3421
Out-of-scope WIs referenced: WI-3261, WI-3424, WI-3429, WI-3436
PAUTH To Be Created: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECONCILIATION
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: S381-deterministic-services-close-out
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI on Windows 11 (harness B, explanatory output style)

# Bridge Kind Justification

This proposal is classified `governance_review` because it does not introduce
or modify source code, tests, hooks, or specifications. It is a one-time
batch reconciliation of seven `work_items.resolution_status` fields to match
the bridge audit trail that has already been committed and VERIFIED. The
implementation surface is invocation of the freshly-shipped `gt backlog
resolve` deterministic CLI (WI-3436, committed in `daf9a4e4`), citing each
WI's existing terminal-bridge evidence. Per
`.claude/rules/file-bridge-protocol.md` and
`DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `governance_review`
proposals are exempted from the single-WI `Work Item:` metadata line
because their scope spans multiple WI rows that are themselves the subject
of governance bookkeeping.

# GT-KB Stale-Status Reconciliation for PROJECT-GTKB-DETERMINISTIC-SERVICES-001

## Summary

Reconcile 7 stale work-item statuses inside PROJECT-GTKB-DETERMINISTIC-SERVICES-001
so the umbrella project's MemBase rollup matches reality:

- **6 WIs whose bridge threads reached VERIFIED but whose `resolution_status`
  was never promoted from `open`** (WI-3262, WI-3263, WI-3318, WI-3319, WI-3420, WI-3421).
- **1 WI whose bridge thread was WITHDRAWN as superseded by current single-harness
  topology** (WI-3265).

This is bookkeeping work — the bridge audit trails are already complete, the
implementations are merged, and the `resolution_status` fields have simply not
kept pace. It implements `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`
as a one-time manual batch for this project using the just-shipped `gt backlog
resolve` deterministic CLI (WI-3436, committed 2026-06-01 in `daf9a4e4`). It
operationalizes the Deterministic Services Principle (`DELIB-S312`): repetitive
status promotion via AI prose is the defect; the CLI is the service.

After reconciliation, the project's effective completion goes from 6/17 (35%)
to 12/17 + 1 superseded (76%), leaving 3 truly-open WIs (WI-3261, WI-3424,
WI-3429) for a separate disposition AUQ.

## PAUTH Bootstrap Note

The PAUTH
`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECONCILIATION`
does not yet exist in MemBase at the time of filing this NEW. It is the
name of the PAUTH this proposal asks to create as the first reconciliation
step, before any row mutation. The PAUTH header line is included because
the spirit of `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` applies
even when the canonical hard-block does not (this is a `governance_review`
proposal). The chicken-and-egg is acknowledged: the PAUTH will be created
via `gt projects authorize` between Codex GO and the first row promotion,
citing this proposal's Codex GO as `owner_decision_deliberation_id` proxy
plus the in-session Path B AUQ.

The closest pre-existing PAUTHs that overlap in WI scope are
`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI`
(covers WI-3261, WI-3262, WI-3263, WI-3265, WI-3318),
`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HOOK-IMPORT-LATENCY`
(WI-3319), and
`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-LAYER-A-HYGIENE-COHERENCE`
(WI-3420, WI-3421) — but their `allowed_mutation_classes` are
`cli_extension`, `test_addition`, `source`, `hook_upgrade`,
`spec_status_promotion`, which do NOT include `work_item_status_promotion`.
A new PAUTH or PAUTH-amendments are required either way.

## Owner Decisions / Input

- **Owner selected "Path B: WI-3436 first, then reconcile stale"** via
  `AskUserQuestion` in session S381 (this session), 2026-06-01 UTC. The
  selected path explicitly authorizes Phase 1 (implement WI-3436 — committed
  `daf9a4e4`) and Phase 2 (this reconciliation proposal).
- **GOV-15 owner-approval evidence** for the 2 defect-origin WIs is satisfied by
  durable bridge audit trails plus the Path B AUQ:
  - **WI-3319 (defect, P2)** — `gtkb-hook-import-latency-chromadb-lazy-010.md`
    VERIFIED carries the owner-decision chain through the bridge GO/VERIFIED
    cycle; Path B AUQ authorizes the now-overdue status promotion.
  - **WI-3265 (defect, P1)** — `gtkb-cross-harness-trigger-codex-exec-hook-firing-001-007.md`
    WITHDRAWN documents Prime's decision to abandon the multi-harness fix because
    current durable topology is single-harness; Path B AUQ authorizes the
    `wont_fix` terminal promotion.
- Path B AUQ explicitly excluded "drive every open WI to VERIFIED" (Path C) and
  "re-scope the umbrella" (Path D); the 3 truly-open follow-on WIs (WI-3261,
  WI-3424, WI-3429) are deferred to a follow-on AUQ.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX is canonical workflow state; this
  proposal updates INDEX for the batch reconciliation.
- `GOV-08` — MemBase is the truth; `resolution_status` fields must reflect
  actual work state. The current 6/17 readout is incorrect.
- `GOV-15` — Test fix gate; resolution_status terminal transitions on defect /
  regression WIs require owner approval (handled by the new CLI's fail-closed
  `--owner-approved` flag plus the AUQ evidence above).
- `GOV-STANDING-BACKLOG-001` — Backlog source of truth; the visibility-bulk-ops
  clause supports batch reconciliation when scoped to one project's known
  members with citation evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — Active project authorization
  governs the reconciliation; new PAUTH proposed above.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Owner decisions, work items, backlog,
  and ADR/DCL/specification references are durable.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Concrete links present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project metadata and
  PAUTH-creation parameters present; bridge_kind exemption claimed above.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Each WI's status transition is a
  lifecycle-valid `open → resolved` or `open → wont_fix` transition.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` — Mutation classes and forbidden
  operations cleanly delimited.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — All target paths inside `E:\GT-KB`;
  no external dependencies.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Reconciliation strengthens
  work-item to bridge-thread linkage by carrying the VERIFIED bridge ID into
  `change_reason`.
- `SPEC-AUQ-POLICY-ENGINE-001` — Path B AUQ was a deterministic AskUserQuestion
  decision, not prose.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Cross-harness bridge dispatch remains
  operative.

## Prior Deliberations

- `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` — Owner decision
  that bridge VERIFIED should mechanically retire the linked backlog item.
  Auto-retire automation has not fired for the 6 stale WIs in this project
  (the documented S363 finding). This proposal is the manual one-time batch
  that implements the missing automation for this specific project. Building
  the auto-retire automation generally is candidate follow-on work outside
  this slice's scope.
- `DELIB-2546` — S379 owner AUQ chain authorizing WI-3436 (`gt backlog update`
  CLI) as the first deterministic-services slice. The CLI shipped yesterday
  (Antigravity-implemented, Codex VERIFIED, committed by Claude PB-B in
  `daf9a4e4`) is now used by this proposal to perform the reconciliation
  efficiently.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — Owner principle that
  repetitive plumbing should move behind deterministic services. Each of the
  7 reconciliation actions is a single `gt backlog resolve` invocation;
  per-row formal-artifact-approval packets are not required.
- `DELIB-S324-OM-DELTA-0004-CHOICE` — Backlog ordering semantics (S324 owner
  decision). This proposal does not change ordering, only terminal status.
- Session S381 Path B AUQ (this session, 2026-06-01) — Owner's path selection
  for closing out the umbrella project.

## Proposed Scope

| WI | Origin | New `resolution_status` | Owner-approval required | Source bridge VERIFIED / WITHDRAWN |
|---|---|---|---|---|
| WI-3262 | new | `resolved` | no | `gtkb-discoverability-cli-slice-2-implementation-006.md` (VERIFIED) |
| WI-3263 | hygiene | `resolved` | no | `gtkb-artifact-recorder-cli-slice-4-owner-decision-auto-archive-014.md` (VERIFIED) |
| WI-3265 | defect | `wont_fix` | **yes** | `gtkb-cross-harness-trigger-codex-exec-hook-firing-001-007.md` (WITHDRAWN; superseded by single-harness dispatcher) |
| WI-3318 | new | `resolved` | no | `gtkb-gt-bridge-propose-deterministic-cli-006.md` (VERIFIED) |
| WI-3319 | defect | `resolved` | **yes** | `gtkb-hook-import-latency-chromadb-lazy-010.md` (VERIFIED) |
| WI-3420 | new | `resolved` | no | `gtkb-hygiene-sweep-cli-004.md` (VERIFIED) |
| WI-3421 | new | `resolved` | no | `gtkb-hygiene-sweep-skill-008.md` (VERIFIED) |

Out of scope (explicit non-actions):

- WI-3261 (verify spec-to-test, currently NO-GO@-008) — needs a substantive
  REVISED-2, not a status promotion. Handled by follow-on AUQ.
- WI-3424 (gt validate spec-coherence, GO@-002, no impl) — needs net-new
  implementation. Handled by follow-on AUQ.
- WI-3429 (gt bridge revise CLI, no bridge) — needs scoping + impl. Handled
  by follow-on AUQ.
- Building the general auto-retire automation that `DELIB-S345` envisions.
  Candidate follow-on work; explicitly NOT part of this slice.

## target_paths

- `bridge/gtkb-deterministic-services-stale-status-reconciliation-*.md`
- `bridge/INDEX.md`
- `groundtruth.db` (work_items rows for WI-3262, WI-3263, WI-3265, WI-3318,
  WI-3319, WI-3420, WI-3421; append-only versions only; project_authorizations
  row for the new PAUTH)

PAUTH-creation parameters (to be executed by Prime after GO):

```text
PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECONCILIATION
  status: active
  authorization_name: "Stale-status reconciliation batch (Path B Phase 2)"
  owner_decision_deliberation_id: <session-S381 Path B AUQ; recorded via gt deliberations record at PAUTH-creation time>
  scope_summary: "One-time batch promotion of 7 stale WI rows in
                  PROJECT-GTKB-DETERMINISTIC-SERVICES-001 using gt backlog
                  resolve, citing each WI's source bridge VERIFIED/WITHDRAWN
                  trail."
  allowed_mutation_classes: ["work_item_status_promotion"]
  forbidden_operations: ["source", "test_addition", "spec_status_promotion",
                         "cli_extension", "hook_upgrade",
                         "creating new work items", "creating new specifications"]
  included_work_item_ids: ["WI-3262", "WI-3263", "WI-3265", "WI-3318",
                           "WI-3319", "WI-3420", "WI-3421"]
  excluded_work_item_ids: ["WI-3261", "WI-3424", "WI-3429", "WI-3436"]
```

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-15`, `GOV-08`, `GOV-STANDING-BACKLOG-001`,
`DELIB-S345`, and `DELIB-S312` together establish the governance basis for
status reconciliation. No new specification capture required for this slice.

## Implementation Commands

For each non-defect WI (5 of them):

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog resolve \
  <WI> --resolution-status resolved \
  --status-detail "Bridge VERIFIED at <bridge-id>; status reconciled per gtkb-deterministic-services-stale-status-reconciliation-001."
```

For the 2 defect-origin WIs (WI-3265, WI-3319) — adds `--owner-approved` with
the AUQ citation:

```text
groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog resolve \
  WI-3319 --resolution-status resolved --owner-approved \
  --status-detail "Bridge VERIFIED at gtkb-hook-import-latency-chromadb-lazy-010; defect GOV-15 owner-approval via S381 Path B AUQ; status reconciled per gtkb-deterministic-services-stale-status-reconciliation-001."

groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog resolve \
  WI-3265 --resolution-status wont_fix --owner-approved \
  --status-detail "Bridge WITHDRAWN at gtkb-cross-harness-trigger-codex-exec-hook-firing-001-007 (superseded by single-harness dispatcher); defect GOV-15 owner-approval via S381 Path B AUQ; status reconciled per gtkb-deterministic-services-stale-status-reconciliation-001."
```

## Spec-Derived Verification Plan

| Specification | Test / verification command | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal's INDEX entry insertion + Codex GO at -002 + post-impl -003 + VERIFIED -004 | Latest INDEX status per bridge protocol |
| `GOV-08` | Re-query of work_items rows after reconciliation via `groundtruth-kb\.venv\Scripts\python.exe -c` SELECT query against work_items table | All 7 rows show new resolution_status with version bumped by 1 |
| `GOV-15` | DB inspection of `change_reason` on the 2 defect-origin updated rows | Owner-approval citation present: "GOV-15 owner-approval via S381 Path B AUQ" |
| `GOV-STANDING-BACKLOG-001` | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb backlog list --project PROJECT-GTKB-DETERMINISTIC-SERVICES-001` | The 7 WIs no longer surface as `open`; show new terminal status |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Pre-mutation snapshot vs post-mutation: each transition is `open → resolved` (5 WIs) or `open → wont_fix` (1 WI) or `open → resolved` for defect WI-3319 with owner-approval | All transitions lifecycle-valid; no illegal direct jumps |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Each linked bridge's VERIFIED verdict checked via the bridge show-thread helper for the 6 stale-VERIFIED threads | Each thread's latest status is VERIFIED (and WITHDRAWN for WI-3265) |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Header has Project, Work Items Affected, PAUTH metadata | Metadata present and machine-parseable |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff --stat HEAD..VERIFIED-commit` | All affected paths under `E:\GT-KB` |
| `SPEC-AUQ-POLICY-ENGINE-001` | Inline AUQ evidence carried in Owner Decisions / Input section | Path B AUQ cited verbatim |
| `DELIB-S345` | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM` | Deliberation present; this reconciliation cites it |
| `DELIB-S312` | `groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Deliberation present; use of `gt backlog resolve` CLI satisfies the principle |

## Acceptance Criteria

1. New PAUTH `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-STALE-STATUS-RECONCILIATION`
   inserted into MemBase with the scope above (created via `gt projects authorize`
   or equivalent governed CLI).
2. 7 work_items rows have new versions with the new `resolution_status` per the
   Proposed Scope table.
3. Each new version's `change_reason` cites the source bridge VERIFIED/WITHDRAWN
   ID and this proposal slug.
4. `gt backlog list --project PROJECT-GTKB-DETERMINISTIC-SERVICES-001` shows the
   7 WIs in their new terminal statuses; no longer counted as `open`.
5. Pre-impl and post-impl bridge applicability + clause preflights both pass
   with no missing required specs and no blocking gaps.

## Risks / Rollback

- **Risk: GOV-15 misapplication on WI-3319 / WI-3265.** Mitigation: owner-approval
  citation embedded in `change_reason`; Codex review verifies the citation
  before VERIFIED.
- **Risk: stale-VERIFIED claim wrong for one of the 6 (bridge VERIFIED but
  actual implementation incomplete).** Mitigation: each bridge thread's source
  files have been spot-checked to confirm code is in working tree at HEAD;
  Codex verification re-checks.
- **Rollback path.** Each `gt backlog resolve` creates a new append-only
  version; rollback is one further `gt backlog update` per WI restoring the
  previous `resolution_status`. No information loss; full audit chain preserved.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `bridge/` lives at `E:\GT-KB\bridge\`.
- `groundtruth.db` lives at `E:\GT-KB\groundtruth.db`.
- No `applications/` paths touched.

Satisfies `ADR-ISOLATION-APPLICATION-PLACEMENT-001` / `CLAUSE-IN-ROOT`.

## Files Expected To Change

- `bridge/gtkb-deterministic-services-stale-status-reconciliation-001.md` (this file; NEW)
- `bridge/INDEX.md` (entry insertion at top; `NEW: 001.md` line)
- `groundtruth.db` (7 append-only work_items rows; 1 new project_authorizations row)

## Recommended Commit Type

`chore` (bookkeeping; no source code, no test changes, no spec text changes).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
