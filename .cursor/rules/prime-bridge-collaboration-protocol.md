<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project cursor`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# Prime Bridge Collaboration Protocol

This rule defines mandatory collaboration behavior between Prime Builder and
Loyal Opposition agents over the file bridge.

> This file preserves status and role semantics for historical audit
> interpretation. Bridge state and status-bearing numbered bridge files
> are canonical.

## Operating Model

- The active bridge is canonical.
- Bridge documents under `bridge/` are the auditable exchange artifacts.
- Only the latest status for each document is actionable.
- The archived SQLite/MCP bridge runtime is legacy compatibility code and must
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

Loyal Opposition processes latest `NEW`, `REVISED`, and `NO-ACTION` entries, then writes the
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

- The dispatcher daemon (`scripts/gtkb_dispatcher_daemon.py`) owns automated
  bridge dispatch.
- On each daemon tick, it inspects bridge state and dispatches the
  appropriate counterpart harness when its actionable queue signature has
  changed.
- Manual owner assignment/scanning is the only fallback when the daemon is
  unhealthy.

## Escalation Boundary

Escalate to the owner only when:

- The action exceeds prior approval.
- A destructive action is required.
- There is a true owner-only product or risk decision.
- The bridge protocol itself is ambiguous or contradictory.
- The dispatcher daemon fails repeatedly and cannot be
  recovered from documented procedures.

## Configuration Capture

Keep `BRIDGE-INVENTORY.md` current with:

- dispatch-state path (`.gtkb-state/bridge-poller/dispatch-state.json`)
- daemon script path (`scripts/gtkb_dispatcher_daemon.py`)
- manual owner assignment/scanning fallback procedure
- log and lock paths
- CLI commands and working directories
- exact prompt text or prompt file paths
- plugins, MCP servers, skills, and config files required by each agent
- health checks and recovery procedure

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
