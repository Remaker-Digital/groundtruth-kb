---
description: Run the code-reviewer agent on recent changes or a specific path. Produces confidence-filtered findings.
argument-hint: "[path or 'diff']"
---

# Quick Code Review

Run the `code-reviewer` agent on the specified target.

## Behavior

1. **Determine scope:**
   - If `$ARGUMENTS` is empty or `diff`: review `git diff HEAD` (unstaged + staged changes)
   - If `$ARGUMENTS` is a file path: review that specific file
   - If `$ARGUMENTS` is a directory: review all Python/TypeScript files in that directory

2. **Launch the code-reviewer agent** with the determined scope.

3. **Display the results** — confidence-filtered findings table with severity counts.

## Examples

```
/quick-review                          # Review current git diff
/quick-review diff                     # Same as above
/quick-review src/multi_tenant/auth.py # Review a specific file
/quick-review src/chat/                # Review all files in a directory
```
