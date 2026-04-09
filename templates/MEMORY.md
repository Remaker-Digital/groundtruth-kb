# {{PROJECT_NAME}} Memory

> **Customize this template:** Replace placeholders and remove example entries.
> Update this file at the end of every session.

## Current Status

- **Version:** {{VERSION}}
- **Environment:** {{ENVIRONMENT_DESCRIPTION}}
- **Knowledge DB:** Run `gt summary` for current counts
- **Tests:** {{TEST_STATUS}}

## Operational Control Surfaces

- **Bridge / runtime inventory:** {{BRIDGE_INVENTORY_PATH_OR_NA}}
- **Automations / schedules:** {{AUTOMATION_SUMMARY_OR_NA}}
- **Current operational health notes:** {{OPS_HEALTH_NOTES}}

## Recent Sessions

- S1: [Describe what was done, key decisions, what's next]

## Quick Reference

- **Knowledge DB:** `gt --config groundtruth.toml summary`
- **Assertions:** `gt --config groundtruth.toml assert`
- **Web UI:** `gt --config groundtruth.toml serve`
- **Operational inventory:** `BRIDGE-INVENTORY.md` or equivalent project-owned file

> **Boundary rule:** If it tells the agent *what to do*, it goes in CLAUDE.md.
> If it tells the agent *what has been done* or *how to access something*, it goes here.
> All canonical project knowledge lives in the knowledge database — this file is
> operational memory, not the source of truth.
