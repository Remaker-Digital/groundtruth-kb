---
name: send-review
description: "Create an implementation proposal through the governed bridge-propose helper for Loyal Opposition review."
argument-hint: "<descriptive-name>"
allowed-tools: Read, Write, Edit, Bash, Glob
license: "Proprietary - Remaker Digital"
compatibility:
  - claude-code >= 1.0
metadata:
  project: agent-red-customer-experience
  category: bridge-coordination
  governance: file-bridge-protocol
---

# Send Review to Loyal Opposition

Compatibility alias for filing a Prime Builder proposal through the governed
`gtkb-bridge-propose` helper path. Do not write proposal files or edit the
bridge index from this skill directly.

**Arguments:** `$ARGUMENTS` = descriptive kebab-case name for the proposal (e.g., `widget-refactor`).

## Behavior

1. **Determine the descriptive name** from `$ARGUMENTS`. If not provided, derive
   a kebab-case `topic_slug` from the current work context.

2. **Draft the proposal content** with the required bridge sections from
   `.claude/rules/file-bridge-protocol.md`, including specification links,
   project/work-item metadata when implementation-targeting, prior
   deliberations, owner input when applicable, and a spec-derived verification
   plan.

3. **File through `gtkb-bridge-propose`.** Use the helper-mediated bridge writer
   described in `.claude/skills/bridge-propose/SKILL.md`. The helper performs
   credential scanning, bridge-compliance validation for Codex paths, proposal
   file creation, author metadata insertion, and governed bridge-index
   registration via `gtkb-bridge-propose`.

4. **Report** the helper result: created proposal path, bridge document slug,
   status line, and any helper error that blocked filing.

## Example

```
/send-review widget-refactor
```

The helper creates `bridge/widget-refactor-001.md` and reports a registration
like:
```
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
```

The example output above is produced by the bridge-propose helper. This skill is
only the caller-facing alias.
