NO-GO

# Destructive-Gate Coverage - Codex Post-Implementation Review

**Status:** NO-GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-003.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: hook-hardening
requires_review: false
requires_verification: true

---

## Verdict

NO-GO.

The new recursive Python deletion patterns work for the direct forms, and the
targeted tests pass. However, GO condition 4 is not satisfied: the command-wide
safe-path exception can still bypass a dangerous Python recursive deletion if
any safe-path substring appears elsewhere in the command.

## Passing Evidence

Targeted hook test:

```powershell
python -m pytest tests/unit/test_destructive_gate_hook.py -q
```

Result:

```text
16 passed
```

Ruff on changed hook/test files:

```powershell
python -m ruff check .claude/hooks/destructive-gate.py tests/unit/test_destructive_gate_hook.py --select E,F
```

Result:

```text
All checks passed!
```

The direct dangerous command is blocked:

```text
python -c "import shutil; shutil.rmtree('GT-KB')"
```

Result:

```text
BLOCKED: Destructive file operation detected. Pattern: \bshutil\.rmtree\b.
```

## Blocking Evidence

The same dangerous deletion is allowed when a safe-path substring appears
elsewhere in the command:

```text
python -c "import shutil; print('node_modules'); shutil.rmtree('GT-KB')"
```

Result:

```text
None
```

This variant also bypasses:

```text
python -c "import shutil; shutil.rmtree('GT-KB') # node_modules"
```

Result:

```text
None
```

Root cause: `_check_destructive()` applies `_is_safe_path(command)` to the
entire command string. That was already broad for shell deletes; with Python
recursive-deletion patterns, it lets unrelated safe-path text suppress a block
for an unsafe target.

## Required Fix

Revise the implementation so safe-path exceptions do not apply command-wide to
the new Python recursive-deletion patterns.

Acceptable approaches:

1. Treat Python recursive-deletion forms as always blocked, regardless of
   `_is_safe_path(command)`, or
2. Extract the actual deletion target for these Python forms and apply the
   safe-path check only to that target.

Option 1 is simpler and more stable for this hook. It has fewer parsing
artifacts and avoids giving a regex gate the job of understanding Python call
arguments.

Post-revision tests must include the two bypass cases above.

## Responses To Prime Questions

1. **Session-specific efficacy evidence:** Acceptable as supporting color, but
   not sufficient for verification while the safe-path bypass remains.
2. **Coverage gap acknowledgment:** Add a brief note if useful, but the blocker
   is not exotic obfuscation. It is a straightforward safe-path bypass.

