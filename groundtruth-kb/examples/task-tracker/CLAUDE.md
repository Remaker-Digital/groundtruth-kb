# CLAUDE.md — Task Tracker

This file provides active guidance for AI assistants working on the Task Tracker example project.

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | Task Tracker |
| **Type** | Example GroundTruth Project |
| **Status** | See MEMORY.md for current status |

## Workflow: Specification → Work Item → Test → Implementation

1. Owner requests change → record as specification(s) in knowledge database
2. Identify implementation gaps → create work items
3. Work item creation triggers test creation
4. Add work items to backlog → prioritize
5. Implement in backlog order
6. Execute tests → PASS or FAIL
7. FAIL → create new work item (verify spec → verify test → fix implementation)

### Spec-First Rule

When the owner describes what the system **must do**, **should do**, or states numbered criteria:
1. Record or verify specifications in the knowledge database
2. Create work items for any gaps
3. Present the backlog for prioritization
4. Only proceed to implementation after approval

## Knowledge Database

Access via `gt --config groundtruth.toml summary` or `gt --config groundtruth.toml serve`.

## Session Wrap-Up

Before ending a session:
1. Update MEMORY.md with what was done and what's next
2. Run `gt --config groundtruth.toml assert` to confirm no regressions
3. Commit with session ID in the message
