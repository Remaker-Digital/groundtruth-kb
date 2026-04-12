# CLAUDE.md — {{PROJECT_NAME}}

This file provides active guidance for AI assistants working on {{PROJECT_NAME}}.
It is loaded at the start of every session.

> **Customize this template:** Replace `{{PROJECT_NAME}}`, `{{COPYRIGHT}}`, and
> other placeholders with your project's values. Remove sections that don't apply.

---

## Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | {{PROJECT_NAME}} |
| **Type** | {{PROJECT_TYPE}} |
| **Status** | See MEMORY.md for current status |
| **Owner** | {{OWNER}} |

### Copyright Notice

All new work in this repository must include:

```
{{COPYRIGHT}}
```

---

## Roles

**Owner role:** Provides direction (what to build) and decisions (specifications to approve).

**Builder role (Claude / AI assistant):** Creates, manages, and maintains implementation artifacts.
Proposes specifications, implements approved changes, runs tests, and keeps the system consistent.

### GroundTruth Vision Filter

The owner should primarily add or revise specifications, answer clarification
questions, and make explicit trade-off decisions. When choosing implementation
options, prefer approaches that reduce routine owner burden through
specifications, automated checks, traceability, and deployment evidence.

Decision filter: Does this reduce the owner's role to specifications,
clarifications, and decisions?

### Optional operational inventory

If this project uses a bridge, multiple agents, scheduled pollers, or recurring
automations, maintain `BRIDGE-INVENTORY.md` (or an equivalent project-owned
inventory file) and keep it aligned with runtime entrypoints, schedules,
directives, and role exceptions.

---

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

---

## Knowledge Database

Access via Python API (`groundtruth_kb`) or CLI (`gt`). Web UI available via `gt serve`.

**Key principle:** All project knowledge lives in the knowledge database. Use `gt summary`
to check current status. Use `gt assert` to verify specifications against the codebase.

---

## Working with This Project

### Starting a New Session

```
Continue work on {{PROJECT_NAME}}.
Key files: CLAUDE.md, MEMORY.md, BRIDGE-INVENTORY.md (if used)
Next: [describe task].
```

### Session Wrap-Up

Before ending a session:
1. Update MEMORY.md with what was done and what's next
2. Run `gt assert` to confirm no regressions
3. Commit with session ID in the message

### Protected Behaviors

Never remove code, tests, features, or specifications without explicit owner approval.
If something looks wrong — ask rather than act.

---

*{{COPYRIGHT}}*
