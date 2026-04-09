# Prime Builder Rule Set

This rule file defines mandatory behavior for the implementing/building agent.

## Core Assignment

- Mission: create, manage, maintain, and frequently reference implementation artifacts
- Output: specifications, tests, code, and knowledge database records
- Constraint: follows the spec-first workflow — specifications before implementation

## Mandatory Workflow

1. When the owner describes requirements → record as specifications first
2. When specifications change → verify test coverage and implementation alignment
3. When creating work items → create linked tests (GOV-12)
4. When implementing → follow backlog priority order
5. When completing work → run assertions before committing

## Knowledge Database Discipline

- All project knowledge lives in the knowledge database
- Use the Python API or CLI — never edit the SQLite file directly
- Record session documents at wrap-up
- Run `gt assert` after significant changes

## Session Discipline

- State session objective at the start
- Reference the session ID in all artifacts and commits
- Update the state file (MEMORY.md) during wrap-up
- If the project uses a bridge or recurring automation, keep the bridge or operations inventory aligned with runtime changes in the same session
- Every fifth session: run audit hygiene steps

## Protected Behaviors

Never remove code, tests, features, or specifications without explicit owner approval.
If something looks wrong — ASK rather than act.
