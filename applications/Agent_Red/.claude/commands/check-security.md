---
description: Run the security-analyzer agent on a module or path. Produces OWASP pattern-table findings with severity ratings.
argument-hint: "<module-path>"
---

# Security Check

Run the `security-analyzer` agent on the specified module.

## Behavior

1. **Determine scope:**
   - If `$ARGUMENTS` is a file: analyze that file
   - If `$ARGUMENTS` is a directory: analyze all Python/TypeScript files in that directory
   - If `$ARGUMENTS` is empty: analyze `src/multi_tenant/` (the core API module)

2. **Launch the security-analyzer agent** with the determined scope.

3. **Display the results** — OWASP pattern-table findings with risk assessment.

## Examples

```
/check-security src/multi_tenant/auth.py        # Analyze auth module
/check-security src/integrations/               # Analyze all integration adapters
/check-security src/chat/                        # Analyze chat/agent modules
/check-security                                  # Default: analyze core API
```
