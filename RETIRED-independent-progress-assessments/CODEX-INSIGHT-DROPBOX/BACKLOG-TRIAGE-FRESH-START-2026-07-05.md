# Fresh Backlog Triage Start

Date: 2026-07-05
Author: Codex / Prime Builder
Scope: Read-only kickoff inventory for a fresh backlog triage after recent GOV, dispatcher, bridge, and worktree changes.

## Claim

The backlog has been triaged recently, but only in targeted slices. A fresh triage is still warranted because recent bridge automation, verified-backlog reconciliation, project auto-retirement behavior, and owner approval packets have changed which items are still applicable.

Recent evidence:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/HIGH-PRIORITY-BACKLOG-TERMINALIZATION-2026-07-04.md` resolved stale high-priority rows `WI-4868`, `WI-4956`, and `WI-4545` after live VERIFIED evidence.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OWNER-APPROVAL-QUEUE-HIGH-PRIORITY-2026-07-05.md` queued 43 P2 / legacy-high open work items for owner approval.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/OWNER-APPROVAL-BATCH-A1-CONTENT-2026-07-05.md` records owner approval for Batch A1: `WI-5027`, `WI-4979`, `WI-4356`, `WI-4837`.
- The immediately preceding dispatch-capacity items are now already terminal: `WI-5029`, `WI-5030`, and `WI-5031` each have latest bridge status `VERIFIED` and were resolved by the verified-backlog reconciler on 2026-07-05.

## Live Backlog Counts

Commands:

```powershell
gt backlog list --resolution-status <status> --json
gt backlog list --resolution-status open --priority <priority> --json
gt backlog status --json
```

Resolution-status counts:

| Status | Count |
| --- | ---: |
| open | 186 |
| resolved | 3161 |
| verified | 63 |
| retired | 335 |
| wont_fix | 60 |

Open priority counts:

| Priority | Open count |
| --- | ---: |
| P0 | 0 |
| P1 | 0 |
| P2 | 39 |
| P3 | 41 |
| legacy high | 4 |
| medium | 0 |
| low | 93 |

Project rollup:

| Metric | Count |
| --- | ---: |
| projects | 309 |
| active projects | 46 |
| active projects with open items | 23 |
| active projects without open items | 23 |
| active memberships | 767 |
| doubled-prefix projects | 10 |

## Triage Lanes

### Reconciler Dry-Run Baseline

Command:

```powershell
python scripts/bridge_verified_backlog_reconciler.py --dry-run --json
```

Result:

| Field | Value |
| --- | --- |
| bridge documents scanned | 1572 |
| reconciler candidates | 19 |
| would resolve now | 0 |

Skip reasons:

| Reason | Count |
| --- | ---: |
| `linked_bridge_not_verified` | 9 |
| `no_related_bridge_threads` | 5 |
| `missing_parent_evidence` | 4 |
| `missing_bridge_document` | 1 |

Candidate IDs surfaced by the maintained reconciler: `WI-4356`, `WI-4369`, `WI-4823`, `WI-5009`, `WI-5028`, `WI-4536`, `WI-4669`, `WI-4719`, `WI-4726`, `WI-4736`, `WI-4754`, `WI-4822`, `WI-4824`, `WI-4825`, `WI-4401`, `WI-4411`, `WI-4436`, `WI-4465`, `WI-4508`.

Interpretation: there is no safe automatic verified-backlog resolution batch at this point. The fresh triage should treat these 19 as closure/rescope candidates, not as directly resolvable rows.

### Lane 1 - Already Completed / Reconciler-Caught

Use this lane for rows that have become terminal through recent bridge work and should not remain in implementation queues.

Confirmed examples:

| Work item | Current state | Evidence |
| --- | --- | --- |
| `WI-5029` | resolved | latest bridge `gtkb-wi5029-dispatch-cap-reconciliation-004.md` is `VERIFIED`; reconciler resolved row at `2026-07-05T09:43:07Z` |
| `WI-5030` | resolved | latest bridge `gtkb-wi5030-live-dispatch-capacity-benchmark-004.md` is `VERIFIED`; reconciler resolved row at `2026-07-05T10:07:30Z` |
| `WI-5031` | resolved | latest bridge `gtkb-wi5031-sqlite-busy-timeout-tuning-004.md` is `VERIFIED`; reconciler resolved row at `2026-07-05T10:02:18Z` |

Recommended next action: run this same bridge-thread coverage check over the P2 and P3 open lists before authorizing new implementation, because several rows may have become terminal after their initial capture.

### Lane 2 - Owner-Approved First Implementation Batch

Batch A1 has owner approval but still needs the normal bridge and implementation-start gates before protected source/test/config mutation.

| Work item | Purpose |
| --- | --- |
| `WI-5027` | Worktree finalization / commit-discipline cleanup |
| `WI-4979` | Generalized recurring work-tree hygiene actuator |
| `WI-4356` | Recurring work-tree hygiene and stash-stray cleanup mechanism |
| `WI-4837` | Post-VERIFIED finalization recovery path |

Recommended next action: start with `WI-5027`, because it reduces risk in every subsequent implementation and closure operation.

### Lane 3 - Next P2 / Legacy-High Approval Batch

The next likely owner-review package is Batch A2 from `OWNER-APPROVAL-QUEUE-HIGH-PRIORITY-2026-07-05.md`: `WI-5028`, `WI-4978`, `WI-5009`, `WI-4538`, `WI-4849`, `WI-4870`, `WI-4535`, `WI-4802`.

Recommended next action: before asking for more owner approval, run a bridge/recent-work drift check against these eight rows. Several are close cousins of recently implemented dispatcher/bridge lifecycle work and may need rescope or closure rather than fresh implementation.

### Lane 4 - Active Project Container Cleanup

There are 23 active projects with no open work items. These are project-lifecycle cleanup candidates, not implementation work, subject to keep-open guards and project authorization review.

Observed examples include:

- `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION`
- `PROJECT-GTKB-SOT-SINGLETON-COMPLETENESS`
- `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION`
- `PROJECT-GTKB-RUNTIME-ORCHESTRATION-DISCOVERY-ADVERSARIAL-REVIEW`
- `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-STABILITY`
- `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-FINALIZATION-TOOLING`
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-01-TRANSCRIPT-RESULT-CORPUS`
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-02-HARNESS-MODEL-CONFIG-TRUTH`
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-05-DIRECT-MANIPULATION-PREVENTION`
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-07-HARNESS-QUALITY-BENCHMARK-INTEGRATION`
- `PROJECT-HARNESS-EQUIVALENCE-PHASE-3-GAP-10-PRIORITIZATION-RELEASE-GATING`

Recommended next action: produce a dry-run project-retirement packet for the full 23, then retire only those with no active keep-open intent or pending bridge thread.

### Lane 5 - Low-Priority Advisory Residue

There are 93 open low-priority items. Keyword probes show many are `Route LO advisory: ...` rows created by the advisory router. These are likely high-yield cleanup candidates because many may be superseded by later GOV/ADR/DCL changes or already folded into newer work.

Recommended next action: triage these by source advisory date and topic cluster, not one-by-one implementation. Candidate dispositions should be `resolved`, `wont_fix`, `retired`, or `superseded_by`, with new implementation WIs created only for still-current concrete gaps.

## Recommended Operating Order

1. Finish a read-only drift check for the 39 P2, 4 legacy-high, and 41 P3 open rows against latest bridge status and recent completion evidence.
2. Execute owner-approved Batch A1 through normal bridge proposal / GO / implementation-start gates, starting with `WI-5027`.
3. Prepare a project-retirement dry run for the 23 active projects with no open work.
4. Triage legacy low-priority advisory residue in batches by topic and date.
5. Return to desirable P2/P3 implementation items once stale rows and dead project containers stop distorting the queue.

## Decision Needed From Owner

None yet. This packet is the kickoff inventory and routing proposal for the fresh triage.
