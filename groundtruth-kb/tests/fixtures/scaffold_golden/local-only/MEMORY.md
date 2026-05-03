# _test_golden_local_only Memory

> **Customize this template:** Replace placeholders and remove example entries.
> Update this file at the end of every session.

This file is the MEMORY.md operational notepad per ADR-0001: Three-Tier Memory Architecture. Canonical knowledge lives in MemBase.

**Glossary:** canonical ADR-0001 vocabulary (MemBase, Deliberation Archive, Prime Builder, Loyal Opposition, etc.) is defined at `.claude/rules/canonical-terminology.md`.

## Current Status

- **Version:** 0.1.0
- **Environment:** Local workstation bootstrap
- **MemBase:** Run `gt summary` for current counts
- **Tests:** Not run yet

## Operational Control Surfaces

- **Bridge / runtime inventory:** N/A
- **Automations / schedules:** None configured yet
- **Current operational health notes:** Bootstrap complete. Update after the first working session.

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
