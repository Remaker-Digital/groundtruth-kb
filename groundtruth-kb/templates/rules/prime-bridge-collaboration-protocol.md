# Prime Bridge Collaboration Protocol

This rule defines mandatory collaboration behavior between Prime Builder and
Loyal Opposition agents over the file bridge.

> **GT-KB host note (2026-06-15):** In the GT-KB host after the
> TAFE/dispatcher cutover, retired bridge-index artifacts are not canonical
> bridge-state or dispatcher authority.

## Operating Model

- The active bridge is TAFE-backed and dispatcher-driven in current GT-KB
  hosts.
- Retired bridge-index artifacts are historical material, not dispatcher/TAFE
  state.
- Bridge documents under `bridge/` are the auditable exchange artifacts.
- Dispatcher/TAFE bridge state provides the latest actionable status for each
  document; no generated bridge-index artifact is part of current operation.
- Only the latest status for each document entry is actionable.
- The archived SQLite/MCP bridge runtime is historical legacy code and must
  not be used as the active coordination channel for new projects.

## Status Semantics

| Status | Written by | Meaning |
|--------|------------|---------|
| `NEW` | Prime Builder | New implementation report or review request |
| `REVISED` | Prime Builder | Revised submission after a prior verdict |
| `GO` | Loyal Opposition | Work is accepted or may proceed |
| `NO-GO` | Loyal Opposition | Blockers remain; Prime Builder must respond |
| `VERIFIED` | Loyal Opposition | Terminal verification; no Prime response is expected |

## Directional Rules

### Prime Builder to Loyal Opposition

Prime Builder writes `NEW` or `REVISED` entries when review is needed.

The submission must include:

- summary of work performed or proposed
- artifact paths and relevant KB IDs
- a `Specification Links` section citing every relevant governing specification,
  rule, ADR, DCL, proposal standard, or durable specification artifact
- a spec-to-test plan showing how tests are derived from the linked
  specifications
- verification already performed
- specific review questions or acceptance criteria
- known risks, gaps, or owner decisions needed

Implementation proposals without complete specification linkage are invalid and
must receive `NO-GO`.

Loyal Opposition MUST reject all implementation proposals that are not linked to
specifications. Without linked specifications, there MUST NOT be an approved
implementation plan.

### Loyal Opposition to Prime Builder

Loyal Opposition processes latest `NEW` and `REVISED` entries, then writes the
next numbered bridge file with one of:

- `GO`
- `NO-GO`
- `VERIFIED`

Every verdict must include evidence inspected, findings, impact, recommended
action, and verification performed.

For proposal review, Loyal Opposition must verify that every relevant
specification is linked and that proposed tests derive from those specifications.
For post-implementation verification, Loyal Opposition must carry forward the
linked specifications, confirm specification-derived tests were created or
identified, execute or inspect execution of those tests against the
implementation, and issue `NO-GO` instead of `VERIFIED` for any untested linked
specification unless an explicit owner waiver is documented.

### Prime Builder Response

Prime Builder processes latest `GO` and `NO-GO` entries.

- `GO`: proceed or close as directed by the verdict.
- `NO-GO`: fix blockers and write a `REVISED` entry.
- `VERIFIED`: terminal; do not respond unless the owner explicitly reopens the
  work.

## Bridge Dispatch Automation

Routine collaboration must not depend on manual owner prompting.

- The cross-harness event-driven trigger
  (`scripts/cross_harness_bridge_trigger.py`) is registered as PostToolUse
  and Stop hooks in `.claude/settings.json` and `.codex/hooks.json`.
- The trigger fires on tool-use and Stop events: when bridge state changes or
  the agent ends a turn, current GT-KB hosts inspect dispatcher/TAFE bridge
  state and dispatch the appropriate counterpart harness when its actionable
  queue signature has changed.
- Manual bridge scans remain available as a fallback when the trigger is
  unhealthy. Use dispatcher/TAFE bridge state and versioned bridge files in
  current GT-KB hosts.

## Escalation Boundary

Escalate to the owner only when:

- The action exceeds prior approval.
- A destructive action is required.
- There is a true owner-only product or risk decision.
- The bridge protocol itself is ambiguous or contradictory.
- The cross-harness event-driven trigger fails repeatedly and cannot be
  recovered from documented procedures.

## Configuration Capture

Keep `BRIDGE-INVENTORY.md` current with:

- hook registrations (`.claude/settings.json` and `.codex/hooks.json`)
- dispatch-state path (`.gtkb-state/bridge-poller/dispatch-state.json`)
- trigger script path (`scripts/cross_harness_bridge_trigger.py`)
- manual bridge-scan fallback procedure
- log and lock paths
- CLI commands and working directories
- exact prompt text or prompt file paths
- plugins, MCP servers, skills, and config files required by each agent
- health checks and recovery procedure

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
