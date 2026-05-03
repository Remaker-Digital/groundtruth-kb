# BRIDGE-INVENTORY.md - _test_golden_dual_agent

> **Customize this template:** Replace placeholders and remove sections that do
> not apply. If your project does not use a bridge, multiple agents, or
> recurring operational automation, you can delete this file.

This file inventories the control surfaces that govern agent coordination,
bridge behavior, and recurring automation.

## Roles and ownership

| Agent / process | Primary responsibility | Reviewer / counterparty | Notes |
|-----------------|------------------------|--------------------------|-------|
| prime-builder | Implementation, specs, and project bootstrap | codex (Loyal Opposition) | Replace with your actual collaboration topology. |

## Runtime code artifacts

| Path | Purpose | Trigger / invocation | Owner |
|------|---------|----------------------|-------|
| bridge/INDEX.md + verified smart poller | File bridge queue for Prime Builder and Loyal Opposition review handoffs | Verified smart poller invokes project-owned scanner scripts | GoldenFixtureOwner |

Include:
- bridge entrypoints
- workers, pollers, supervisors, or listeners
- hook scripts
- health-check or recovery scripts
- message stores or runtime databases when relevant

## File bridge protocol

If this project uses the file bridge pattern, capture the exact status rules.

| Direction | Watches for latest status | Writes status | Terminal statuses |
|-----------|---------------------------|---------------|-------------------|
| Prime Builder -> Loyal Opposition | NEW, REVISED | GO, NO-GO, VERIFIED | VERIFIED |
| Loyal Opposition -> Prime Builder | GO, NO-GO | NEW, REVISED | VERIFIED |

Notes:
- `bridge/INDEX.md` is the authoritative queue when the file bridge is active.
- Entries are newest-first. Only the latest status for each document entry is
  actionable.
- `VERIFIED` is terminal and must not trigger Prime Builder action.
- Archived bridge runtimes or inactive queues should be marked inactive here.

## Poller status-file contract

Each OS-scheduler poller writes a JSON status file after every scan:

| Agent | Path |
|-------|------|
| Claude (Prime) | `independent-progress-assessments/bridge-automation/logs/claude-scan-status.json` |
| Codex (LO) | `independent-progress-assessments/bridge-automation/logs/codex-scan-status.json` |

Schema:
```json
{"updatedAtUtc": "<ISO8601-UTC>", "state": "<clear|dispatched|error|...>", "message": "<summary>"}
```

Freshness thresholds (used by `gt project doctor`):
- `< 4 min` → OK; `4–10 min` → WARN; `> 10 min` → ALARM; file absent → not started

## Directive and instruction surfaces

| Path | Kind | Purpose | Update trigger |
|------|------|---------|----------------|
| `CLAUDE.md` | startup rules | Replace with the actual purpose for this control surface. | Whenever the runtime or coordination rules change. |
| `MEMORY.md` | state file | Replace with the actual purpose for this control surface. | Whenever the runtime or coordination rules change. |
| TBD | TBD | Replace with the actual purpose for this control surface. | Whenever the runtime or coordination rules change. |

Include markdown files, rule files, prompt files, runbooks, and any other
control documents that change bridge or automation behavior.

## Agent CLI, prompts, plugins, and skills

| Agent / process | CLI command | Prompt source | Config files | Plugins / MCP / skills |
|-----------------|-------------|---------------|--------------|------------------------|
| Prime Builder | TBD | TBD | TBD | TBD |
| Loyal Opposition | TBD | TBD | TBD | TBD |

Capture the exact prompt passed to scheduled runs, or the path to the prompt
file. Prompt text is operational configuration when it changes bridge behavior.

## Scheduled tasks and automations

| Name | Schedule / trigger | Executor | Defined in | Failure signal |
|------|--------------------|----------|------------|----------------|
| file-bridge-smart-poller | Smart-poller registration interval or manual fallback | claude -p / codex exec via project-owned scanner scripts | bridge-os-poller-setup-prompt.md (legacy filename; smart-poller content) and BRIDGE-INVENTORY.md | No recent scan logs or stale actionable bridge entries |

Include recurring tasks from:
- app-native automations
- cron / Task Scheduler / systemd / launchd
- GitHub Actions schedules
- long-running local loops that function as schedulers

## Protocol rules

- **Message model:** File-based latest-status queue in bridge/INDEX.md. Entries are newest-first.
- **Reply rule:** Latest NEW/REVISED entries require Loyal Opposition verdicts; latest GO/NO-GO entries require Prime responses.
- **Retry rule:** Scheduled re-scan after the next interval; lock files prevent overlapping runs.
- **Health check:** Read bridge/INDEX.md, scheduler state, and recent scan logs.
- **Restart policy:** No long-running bridge process is required; update scheduled tasks after scanner or prompt changes.

Per ADR-0001: Three-Tier Memory Architecture, canonical project history lives in MemBase; this inventory is an operational control surface that must stay aligned with MemBase records.

## MemBase mapping

Record the canonical history for this control surface in MemBase:

- `environment_config`: Add KB IDs or notes here.
- `operation_procedure`: Add KB IDs or notes here.
- `document`: Add KB IDs or notes here.

## Last review

- **Reviewed by:** codex (Loyal Opposition)
- **Date:** TBD
- **Open follow-ups:** TBD
