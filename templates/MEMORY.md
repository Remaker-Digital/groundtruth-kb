# {{PROJECT_NAME}} Memory

> **Customize this template:** Replace placeholders and remove example entries.
> Update this file at the end of every session.

## Current Status

- **Version:** {{VERSION}}
- **Environment:** {{ENVIRONMENT_DESCRIPTION}}
- **Knowledge DB:** Run `gt summary` for current counts
- **Tests:** {{TEST_STATUS}}

## Recent Sessions

- S1: [Describe what was done, key decisions, what's next]

## Quick Reference

- **Knowledge DB:** `gt --config groundtruth.toml summary`
- **Assertions:** `gt --config groundtruth.toml assert`
- **Web UI:** `gt --config groundtruth.toml serve`

> **Boundary rule:** If it tells the agent *what to do*, it goes in CLAUDE.md.
> If it tells the agent *what has been done* or *how to access something*, it goes here.
> All canonical project knowledge lives in the knowledge database — this file is
> operational memory, not the source of truth.
