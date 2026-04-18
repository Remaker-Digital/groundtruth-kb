# {{PROJECT_NAME}} Memory

> **Customize this template:** Replace placeholders and remove example entries.
> Update this file at the end of every session.

This file is the MEMORY.md operational notepad per ADR-0001: Three-Tier Memory Architecture. Canonical knowledge lives in MemBase.

**Glossary:** canonical ADR-0001 vocabulary (MemBase, Deliberation Archive, Prime Builder, Loyal Opposition, etc.) is defined at `.claude/rules/canonical-terminology.md`.

## Current Status

- **Version:** {{VERSION}}
- **Environment:** {{ENVIRONMENT_DESCRIPTION}}
- **MemBase:** Run `gt summary` for current counts
- **Tests:** {{TEST_STATUS}}

## Operational Control Surfaces

- **Bridge / runtime inventory:** {{BRIDGE_INVENTORY_PATH_OR_NA}}
- **Automations / schedules:** {{AUTOMATION_SUMMARY_OR_NA}}
- **Current operational health notes:** {{OPS_HEALTH_NOTES}}

## Recent Sessions

- S1: [Describe what was done, key decisions, what's next]

## Quick Reference

- **MemBase:** `gt --config groundtruth.toml summary`
- **Assertions:** `gt --config groundtruth.toml assert`
- **Web UI:** `gt --config groundtruth.toml serve`
- **Operational inventory:** `BRIDGE-INVENTORY.md` or equivalent project-owned file

> **Boundary rule:** If it tells the agent *what to do*, it goes in CLAUDE.md.
> If it tells the agent *what has been done* or *how to access something*, it goes here.
> All canonical project knowledge lives in MemBase — this file is operational memory, not the source of truth. MEMORY.md can coordinate work, but it cannot make anything true.
