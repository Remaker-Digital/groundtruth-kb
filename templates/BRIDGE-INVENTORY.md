# BRIDGE-INVENTORY.md - {{PROJECT_NAME}}

> **Customize this template:** Replace placeholders and remove sections that do
> not apply. If your project does not use a bridge, multiple agents, or
> recurring operational automation, you can delete this file.

This file inventories the control surfaces that govern agent coordination,
bridge behavior, and recurring automation.

## Roles and ownership

| Agent / process | Primary responsibility | Reviewer / counterparty | Notes |
|-----------------|------------------------|--------------------------|-------|
| {{AGENT_OR_PROCESS_1}} | {{RESPONSIBILITY}} | {{REVIEWER}} | {{NOTES}} |

## Runtime code artifacts

| Path | Purpose | Trigger / invocation | Owner |
|------|---------|----------------------|-------|
| {{PATH_TO_ENTRYPOINT}} | {{WHAT_IT_DOES}} | {{HOW_IT_RUNS}} | {{OWNER}} |

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

## Directive and instruction surfaces

| Path | Kind | Purpose | Update trigger |
|------|------|---------|----------------|
| `CLAUDE.md` | startup rules | {{PURPOSE}} | {{WHEN_TO_UPDATE}} |
| `MEMORY.md` | state file | {{PURPOSE}} | {{WHEN_TO_UPDATE}} |
| {{OTHER_PATH}} | {{KIND}} | {{PURPOSE}} | {{WHEN_TO_UPDATE}} |

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
| {{AUTOMATION_NAME}} | {{SCHEDULE}} | {{EXECUTOR}} | {{SOURCE}} | {{FAILURE_SIGNAL}} |

Include recurring tasks from:
- app-native automations
- cron / Task Scheduler / systemd / launchd
- GitHub Actions schedules
- long-running resident loops that function as schedulers

## Protocol rules

- **Message model:** {{ASYNC_OR_TRANSACTIONAL_DESCRIPTION}}
- **Reply rule:** {{WHEN_MESSAGES_REQUIRE_REPLIES}}
- **Retry rule:** {{WHEN_TO_RETRY}}
- **Health check:** {{STARTUP_OR_LIVENESS_CHECK}}
- **Restart policy:** {{WHEN_RESTARTS_ARE_ALLOWED_OR_AVOIDED}}

## Knowledge database mapping

Record the canonical history for this control surface in the knowledge database:

- `environment_config`: {{ENV_CONFIG_IDS_OR_NOTES}}
- `operation_procedure`: {{PROCEDURE_IDS_OR_NOTES}}
- `document`: {{DOCUMENT_IDS_OR_NOTES}}

## Last review

- **Reviewed by:** {{REVIEWER}}
- **Date:** {{DATE}}
- **Open follow-ups:** {{FOLLOW_UPS}}
