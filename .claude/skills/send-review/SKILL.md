---
name: send-review
description: "Create an implementation proposal in bridge/ and add it to the bridge INDEX for Loyal Opposition review."
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

Create a proposal document in `bridge/` and register it in `bridge/INDEX.md` for
Loyal Opposition to pick up during its next scan.

**Arguments:** `$ARGUMENTS` = descriptive kebab-case name for the proposal (e.g., `widget-refactor`).

## Behavior

1. **Determine the descriptive name** from `$ARGUMENTS`. If not provided, derive
   from the current work context.

2. **Find the next version number** by scanning `bridge/` for existing files
   matching `{name}-*.md` and incrementing the highest version found, or
   starting at 001.

3. **Gather proposal content** from the current session:
   - Summary of what was implemented and why
   - Files changed and KB records affected
   - Specific review questions for Loyal Opposition (numbered)
   - Relevant commit hashes

4. **Write the proposal** to `bridge/{name}-{NNN}.md` with the gathered content.

5. **Update the index** by reading `bridge/INDEX.md` and inserting a new entry
   at the top (after the header comments):
   ```
   Document: {name}
   NEW: bridge/{name}-{NNN}.md
   ```

6. **Report** the file path and index entry created.

## Example

```
/send-review widget-refactor
```

Creates `bridge/widget-refactor-001.md` and adds to INDEX.md:
```
Document: widget-refactor
NEW: bridge/widget-refactor-001.md
```
