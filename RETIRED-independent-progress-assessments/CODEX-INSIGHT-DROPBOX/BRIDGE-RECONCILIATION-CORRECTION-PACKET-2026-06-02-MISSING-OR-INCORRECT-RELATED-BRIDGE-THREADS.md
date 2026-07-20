# Bridge Reconciliation Correction Packet: Missing Or Incorrect Related Bridge Threads

Specs: GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
WIs: WI-4230, WI-4235, WI-4236, WI-4237, WI-4238

Session type: Loyal Opposition bridge/backlog reconciliation packet
Reviewer: Codex / Loyal Opposition
Generated: 2026-06-02T18:15:50Z

## Claim

The live bridge queue has no Loyal Opposition-actionable `NEW` or `REVISED`
items, but the bridge/backlog reconciliation audit still reports 156
`missing_or_incorrect_related_bridge_threads` findings. This packet isolates
the highest-priority candidates for the single class so Prime Builder can file
a governed repair proposal instead of treating all bridge/backlog drift as one
undifferentiated mutation.

## Evidence

- Live bridge scan:
  `python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json`
- Live bridge scan result after bridge closeout:
  `actionable: []`; latest status summary `ADVISORY=5`, `GO=15`, `NO-GO=21`,
  `VERIFIED=96`, `WITHDRAWN=42`.
- Audit source:
  `scripts/bridge_reconciliation_audit.py` through its read-only `run_audit`
  API.
- Audit result:
  6,210 issues, mutation `none`.
- Counts by class:
  - `bridge_index_drift`: 3,906
  - `terminal_backlog_without_evidence`: 2,027
  - `missing_or_incorrect_related_bridge_threads`: 156
  - `verified_bridge_missing_terminal_backlog_state`: 120
  - `verified_bridge_without_backlog_match`: 16
- Packet source:
  `scripts/bridge_reconciliation_correction_packet.py` through its read-only
  `build_packet` API with
  `triage_class='missing_or_incorrect_related_bridge_threads'` and `limit=25`.

## Candidate Packet

Required gates before any correction:

- Single triage class only.
- Owner decision recorded one at a time before mutation.
- Bridge GO for any mutation proposal.
- Implementation-start packet before file or MemBase mutation.
- Post-implementation report after mutation.
- Loyal Opposition verification before terminal closure.

Forbidden by this dry-run packet:

- No backlog update.
- No project update.
- No `bridge/INDEX.md` edit.
- No bridge writer helper invocation.
- No deliberation mutation.

Top candidates:

| Subject | Priority | Missing related bridge thread(s) | Proposed mutation type |
| --- | --- | --- | --- |
| `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` | P0 | `gtkb-secrets-purge-and-commit-enforcement-slice2-ci-prepush`; `gtkb-secrets-purge-and-commit-enforcement-slice3-history-purge-plan` | `related_bridge_threads_update` |
| `GTKB-STARTUP-ENHANCEMENTS` | P1 | `gtkb-backlog-hygiene-bundle-s349`; `gtkb-startup-enhancements-completion-reconciliation`; `gtkb-startup-enhancements-p1`; `gtkb-startup-enhancements-p2-freshness-contract` | `related_bridge_threads_update` |
| `GTKB-STARTUP-REFRACTOR-001` | P1 | `gtkb-startup-refractor-001` | `related_bridge_threads_update` |
| `WI-3249` | P0 | `gtkb-loyal-opposition-startup-symmetry-001` | `related_bridge_threads_update` |
| `WI-3250` | P0 | `gtkb-canonical-init-keyword-syntax-001` | `related_bridge_threads_update` |
| `WI-3251` | P1 | `gtkb-bridge-advisory-status-001` | `related_bridge_threads_update` |
| `WI-3252` | P0 | `gtkb-scaffold-upgrade-tier-a` | `related_bridge_threads_update` |
| `WI-3253` | P1 | `gtkb-role-session-lifecycle-simplification` | `related_bridge_threads_update` |
| `WI-3254` | P1 | `gtkb-session-start-formalization-001` | `related_bridge_threads_update` |
| `WI-3255` | P1 | `gtkb-single-harness-bridge-dispatcher-001` | `related_bridge_threads_update` |
| `WI-3257` | P0 | `gtkb-bridge-revision-skill-001` | `related_bridge_threads_update` |
| `WI-3258` | P0 | `gtkb-bridge-impl-report-skill-001` | `related_bridge_threads_update` |
| `WI-3259` | P1 | `gtkb-projects-skill-001` | `related_bridge_threads_update` |
| `WI-3264` | P0 | `gtkb-cross-harness-trigger-windows-rename-race-001` | `related_bridge_threads_update` |
| `WI-3268` | P2 | `gtkb-interactive-session-role-override-slice-10-regression-tests`; `gtkb-interactive-session-role-override-slice-9-rule-claude-agents-updates`; `gtkb-lo-hourly-quality-scout-advisory` | `related_bridge_threads_update` |
| `WI-3275` | P1 | `gtkb-mcp-stable-harness-surface-conversion` | `related_bridge_threads_update` |
| `WI-3277` | P2 | `gtkb-claude-axis-2-userpromptsubmit-bridge-surface` | `related_bridge_threads_update` |
| `WI-3279` | P1 | `gtkb-formal-artifact-packet-validator-cli` | `related_bridge_threads_update` |
| `WI-3281` | P2 | `gtkb-advisory-report-protocol-extension` | `related_bridge_threads_update` |
| `WI-3282` | P1 | `gtkb-backlog-hygiene-bundle-s349` | `related_bridge_threads_update` |
| `WI-3283` | P2 | `gtkb-backlog-hygiene-bundle-s349` | `related_bridge_threads_update` |
| `WI-3284` | P2 | `gtkb-backlog-hygiene-bundle-s349` | `related_bridge_threads_update` |
| `WI-3285` | P1 | `gtkb-backlog-hygiene-bundle-s349` | `related_bridge_threads_update` |
| `WI-3286` | P2 | `gtkb-backlog-hygiene-bundle-s349` | `related_bridge_threads_update` |

## Risk / Impact

The immediate risk is routing drift: work items can cite bridge threads that are
not currently discoverable from the live `bridge/INDEX.md`. That makes project
rollups, completion evidence, and Prime/Loyal Opposition continuation work
depend on stale or ambiguous linkage strings rather than the canonical bridge
queue.

The packet must not be applied mechanically. Some candidates may refer to
historical bridge files pruned from the active index, some may need
`bridge/INDEX.md` restoration, and others may need `related_bridge_threads`
normalization to canonical indexed paths. Prime Builder should classify the
candidate by repair mode before requesting any owner-approved mutation.

## Recommended Action

Prime Builder should consume this packet under `WI-4230` and `WI-4236`.
The first implementation proposal should split the 156 findings into:

1. backlog linkage strings that should be rewritten to current indexed bridge
   paths;
2. historical bridge threads that should be restored to `bridge/INDEX.md` or
   explicitly archived as no-longer-active;
3. detector false positives caused by slug-vs-path normalization.

Only after that classification should Prime Builder request one owner decision
for a concrete mutation batch.

## Decision Needed From Owner

None for this Loyal Opposition packet. A future Prime correction proposal
should ask for one owner decision for this specific mutation class before
updating MemBase linkage fields or the bridge index.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
