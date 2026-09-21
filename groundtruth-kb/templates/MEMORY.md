# {{PROJECT_NAME}} Memory

> **Customize this template:** Replace placeholders and remove example entries.
> Keep only useful operational observations; this file is not a session-progress dependency.

This file is the MEMORY.md operational notepad per ADR-0001: Three-Tier Memory Architecture. Canonical knowledge lives in MemBase.

**Glossary:** retrieve current canonical terms with `gt terms list`, `gt terms show <ID>` and `gt authority resolve`. Generated rule files and operational notes have no independent terminology authority.

## Current Status

- **Version:** {{VERSION}}
- **Environment:** {{ENVIRONMENT_DESCRIPTION}}
- **MemBase:** Run `gt status` (the `authority` component is PASS when the KB authority is ready and reachable)
- **Tests:** {{TEST_STATUS}}

## Operational Control Surfaces

- **Current runtime query:** {{SUPPORTED_RUNTIME_QUERY_OR_NA}}
- **Automations / schedules:** {{AUTOMATION_SUMMARY_OR_NA}}
- **Current operational health notes:** {{OPS_HEALTH_NOTES}}

## Recent Sessions

- S1: [Brief observations and pointers to current canonical records; re-query before acting]

## Quick Reference

- **MemBase:** `gt --config groundtruth.toml status`
- **Assertions:** `gt --config groundtruth.toml assert`
- **Current project:** `gt projects show <PROJECT_ID> --json`

> **Boundary rule:** Shared operating instructions belong in canonical harness-neutral sources and are projected where required.
> If it tells the agent *what has been done* or *how to access something*, it goes here.
> All canonical project knowledge lives in MemBase — this file is operational memory, not the source of truth. MEMORY.md can coordinate work, but it cannot make anything true.
