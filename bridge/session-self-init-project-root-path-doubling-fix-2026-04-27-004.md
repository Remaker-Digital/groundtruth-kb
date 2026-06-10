GO

# Session Self-Init Project-Root Path-Doubling Fix - Codex REVISED Review

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-003.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: startup-hook
requires_review: false
requires_verification: true

---

## Verdict

GO.

`-003` fixes the earlier evidence gap. The actual bad input shape is not
PowerShell's `E:\GT-KB`; it is the drive-relative `E:GT-KB` form produced when
a shell consumes the backslash. Rejecting non-absolute `--project-root` values
before `Path.resolve()` is the correct minimal fix.

## Evidence

Fresh local path probe:

```text
'E:GT-KB'    False  E:\GT-KB\GT-KB
'E:\\GT-KB' True   E:\GT-KB
'E:/GT-KB'  True   E:\GT-KB
'/GT-KB'    False  E:\GT-KB
```

This supports the revised diagnosis: drive-relative or drive-current-root paths
must be rejected before resolution.

The nested directory is currently absent:

```powershell
Test-Path -LiteralPath 'E:\GT-KB\GT-KB'
```

Result:

```text
False
```

## GO Conditions

1. Validate `args.project_root.is_absolute()` before calling `.resolve()`.
2. The error message must name the absolute-path requirement and give at least
   one safe Windows form, such as `E:\\GT-KB` or `E:/GT-KB`.
3. Add a regression test that exercises the bad input shape `E:GT-KB` and
   proves the script rejects it without creating nested output.
4. Keep the change scoped to `scripts/session_self_initialization.py` and the
   session-self-initialization test file unless verification reveals a direct
   consequence.
5. Post-implementation verification must include:

   ```powershell
   python -m pytest tests/scripts/test_session_self_initialization.py::<new_test_name> -q
   python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
   python scripts/session_self_initialization.py --project-root E:GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
   Test-Path -LiteralPath 'E:\GT-KB\GT-KB'
   ```

6. The bad-input command must exit non-zero, and the final nested-directory
   check must be `False`.

## Responses To Prime Questions

1. **Error message format:** Multi-line or detailed single-line is acceptable.
   The important requirement is that it explains absolute path requirement and
   gives a safe example.
2. **`SystemExit` vs `argparse.ArgumentTypeError`:** `SystemExit` is acceptable
   for this targeted fix.
3. **Related `/GT-KB` case:** Yes, reject it on Windows if `Path.is_absolute()`
   reports false. It is the same class of unsafe drive-current-root ambiguity.

