# Bridge Reconciliation Correction Packet: VERIFIED Bridge Missing Terminal Backlog State

Specs: GOV-STANDING-BACKLOG-001, GOV-FILE-BRIDGE-AUTHORITY-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
WIs: WI-4235, WI-4236, WI-4237, WI-4238

Session type: Loyal Opposition bridge/backlog reconciliation packet
Reviewer: Codex / Loyal Opposition
Generated: 2026-06-02T17:09:30Z

## Claim

The live bridge queue has no Loyal Opposition-actionable `NEW` or `REVISED`
items, but the bridge/backlog reconciliation audit still exposes a bounded
single-class correction opportunity: VERIFIED bridge threads whose associated
current work items remain non-terminal. This packet does not approve or perform
any mutation; it provides Prime Builder with a concrete one-class correction
candidate set.

## Evidence

- Live bridge scan:
  `python .claude/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --format json`
- Live bridge scan result:
  `actionable: []`; latest status summary `ADVISORY=5`, `GO=18`, `NO-GO=21`,
  `VERIFIED=99`, `WITHDRAWN=42`.
- Audit source:
  `scripts/bridge_reconciliation_audit.py` through its read-only `run_audit`
  API.
- Audit result:
  185 bridge documents, 3,015 work items, 6,187 issues, mutation `none`.
- Counts by class:
  - `bridge_index_drift`: 3,872
  - `terminal_backlog_without_evidence`: 2,027
  - `missing_or_incorrect_related_bridge_threads`: 150
  - `verified_bridge_missing_terminal_backlog_state`: 120
  - `verified_bridge_without_backlog_match`: 18
- Packet source:
  `scripts/bridge_reconciliation_correction_packet.py` through its read-only
  `build_packet` API with
  `triage_class='verified_bridge_missing_terminal_backlog_state'` and
  `limit=12`.

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

| Bridge thread | Work item | Priority | Current status | Proposed mutation type |
| --- | --- | --- | --- | --- |
| `gtkb-agent-red-deployability-preservation-gate` | `WI-3248` | P0 | open/backlogged | backlog_terminal_status_update |
| `gtkb-agent-red-deployability-preservation-gate-slice-1-scoping` | `WI-3248` | P0 | open/backlogged | backlog_terminal_status_update |
| `gtkb-backlog-authorize-implementation-cli-slice-1` | `WI-3510` | P2 | open/backlogged | backlog_terminal_status_update |
| `gtkb-bridge-backlog-reconciliation-audit-cli` | `WI-3162` | P2 | new/backlogged | backlog_terminal_status_update |
| `gtkb-bridge-backlog-reconciliation-audit-cli` | `WI-4234` | P2 | open/backlogged | backlog_terminal_status_update |
| `gtkb-bridge-backlog-reconciliation-audit-cli` | `WI-4235` | P1 | open/backlogged | backlog_terminal_status_update |
| `gtkb-bridge-backlog-reconciliation-audit-cli` | `WI-4236` | P1 | open/backlogged | backlog_terminal_status_update |
| `gtkb-bridge-backlog-reconciliation-audit-cli` | `WI-4238` | P2 | open/backlogged | backlog_terminal_status_update |
| `gtkb-bridge-dispatcher-deferral-enforcement-repair` | `WI-3276` | P2 | open/created | backlog_terminal_status_update |
| `gtkb-bridge-dispatcher-deferral-enforcement-repair` | `WI-3308` | P1 | open/created | backlog_terminal_status_update |
| `gtkb-bridge-index-chain-deviation-detector` | `WI-4234` | P2 | open/backlogged | backlog_terminal_status_update |
| `gtkb-bridge-index-chain-deviation-detector` | `WI-4235` | P1 | open/backlogged | backlog_terminal_status_update |

## Risk / Impact

This class is high-signal because it names work items that already have
VERIFIED bridge evidence but still appear active in MemBase. Leaving the class
untriaged makes startup and backlog views overstate active work. The packet must
not be applied blindly: some rows may be umbrella items where a verified slice
does not close the parent.

## Recommended Action

Prime Builder should file a governed correction proposal for exactly this class
or a narrower subset of it. The proposal should explicitly exclude umbrella
items whose verified child slices do not close the parent, then request owner
approval for one concrete mutation batch before any MemBase update.

## Decision Needed From Owner

None from this Loyal Opposition packet. A future Prime correction proposal
should ask for one owner decision for this specific mutation class before
applying any terminal-state update.
