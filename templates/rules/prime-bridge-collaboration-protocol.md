# Prime Bridge Collaboration Protocol

This rule defines mandatory collaboration behavior between Prime Builder and
Loyal Opposition agents over the file bridge.

## Operating Model

- The active bridge is file-based.
- `bridge/INDEX.md` is the authoritative queue.
- Bridge documents under `bridge/` are the auditable exchange artifacts.
- Entries in the index are newest-first.
- Only the latest status for each document entry is actionable.
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
- verification already performed
- specific review questions or acceptance criteria
- known risks, gaps, or owner decisions needed

### Loyal Opposition to Prime Builder

Loyal Opposition processes latest `NEW` and `REVISED` entries, then writes the
next numbered bridge file with one of:

- `GO`
- `NO-GO`
- `VERIFIED`

Every verdict must include evidence inspected, findings, impact, recommended
action, and verification performed.

### Prime Builder Response

Prime Builder processes latest `GO` and `NO-GO` entries.

- `GO`: proceed or close as directed by the verdict.
- `NO-GO`: fix blockers and write a `REVISED` entry.
- `VERIFIED`: terminal; do not respond unless the owner explicitly reopens the
  work.

## Polling and Scheduling

Routine collaboration must not depend on manual owner prompting.

- Use separate OS-level pollers for Prime Builder and Loyal Opposition.
- Each poller reads `bridge/INDEX.md`, filters by latest status, acquires a
  lock, and invokes its CLI only when real work exists.
- Each poller logs clear scans, dispatched work, command exits, stdout, and
  stderr.
- App-native automations may be supplemental but are not the reliability
  boundary unless durable run records prove they dispatch across sessions.

## Escalation Boundary

Escalate to the owner only when:

- The action exceeds prior approval.
- A destructive action is required.
- There is a true owner-only product or risk decision.
- The bridge protocol itself is ambiguous or contradictory.
- A scheduled poller repeatedly fails and cannot be recovered from documented
  procedures.

## Configuration Capture

Keep `BRIDGE-INVENTORY.md` current with:

- scheduler task names and intervals
- poller scripts and hidden launchers
- log and lock paths
- CLI commands and working directories
- exact prompt text or prompt file paths
- plugins, MCP servers, skills, and config files required by each agent
- health checks and recovery procedure

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
