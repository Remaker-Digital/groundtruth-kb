# Copilot Instructions — GroundTruth KB

This project uses specification-driven governance. Every change must trace
back to a specification or work item in the knowledge database.

## Before writing code

1. Read `CLAUDE.md` for project rules and workflow.
2. Read `groundtruth.toml` for project configuration.
3. If the assigned issue references a spec ID (e.g., SPEC-1234), that spec
   defines the requirements. Do not add features beyond what the spec states.
4. If no spec is referenced, implement only what the issue title and body
   describe — nothing more.

## Code standards

- Python 3.11+. Lint with ruff (see `pyproject.toml` for rules).
- All new files must include this copyright header as the first line:
  ```python
  # © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
  ```
  For TypeScript/JavaScript files:
  ```typescript
  // © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
  ```
- Every new function or class requires a test in `tests/`.
- Do not add dependencies to `pyproject.toml` without explicit approval in
  the issue body.
- Do not modify `src/groundtruth_kb/db.py` schema without a spec reference.

## What NOT to do

- Do not create documentation files (*.md) unless the issue specifically
  requests documentation.
- Do not refactor code beyond what the issue requires.
- Do not add type stubs, docstrings, or comments to files you did not change.
- Do not modify `groundtruth.toml`, `groundtruth.db`, or any file in
  `templates/` unless the issue explicitly targets those files.
- Do not run `gt seed` or modify governance specs (GOV-*).

## Commit messages

Use this format:
```
<type>(<scope>): <description>

Refs: <issue-number>
```

Types: `feat`, `fix`, `test`, `docs`, `chore`

## PR description

Include:
- What changed and why (reference the issue)
- Which files were modified
- How to verify the change (test command or manual check)

## Testing

Run `python -m pytest tests/ -q` before requesting review. All existing
tests must pass. New code must have new tests.

## Architecture

- `src/groundtruth_kb/` — core package (KB engine, CLI, assertions, gates)
- `src/groundtruth_kb/project/` — project scaffold, doctor, upgrade
- `src/groundtruth_kb/bridge/` — inter-agent bridge runtime
- `templates/` — scaffold templates (bundled in wheel)
- `tests/` — pytest test suite
- `docs/` — method documentation

Do not create new top-level directories or packages.
