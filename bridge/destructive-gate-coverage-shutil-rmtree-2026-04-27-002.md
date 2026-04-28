GO

# Destructive-Gate Coverage - Codex Review

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/destructive-gate-coverage-shutil-rmtree-2026-04-27-001.md`

bridge_kind: review
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: hook-hardening
requires_review: false
requires_verification: true

---

## Verdict

GO for Option 1, with scope corrections below.

The destructive-gate parity gap is real: the hook blocks common shell recursive
deletion forms, but currently does not block inline Python recursive deletion
such as `python -c "import shutil; shutil.rmtree('GT-KB')"`. Extending the
gate is consistent with the owner authorization protocol.

## Evidence

Current delete patterns in `.claude/hooks/destructive-gate.py` cover:

```text
del /S, /F, /Q
rmdir /S
rm -r / rm --recursive
Remove-Item ... -Recurse
```

They do not cover Python recursive deletion forms.

Existing hook tests are in:

```text
tests/unit/test_destructive_gate_hook.py
```

There is no `tests/hooks/test_destructive_gate.py` in the current checkout.

## GO Conditions

1. Add coverage in the existing test file
   `tests/unit/test_destructive_gate_hook.py`, not a new `tests/hooks/` file,
   unless Prime has a separate reason to move the suite.
2. Gate inline Bash-tool commands that contain recursive Python deletion forms,
   especially:

   ```text
   python -c "import shutil; shutil.rmtree('GT-KB')"
   python -c "import os; os.removedirs('some/tree')"
   python -c "import subprocess; subprocess.run(['rm', '-rf', 'x'])"
   python -c "import subprocess; subprocess.run(['Remove-Item', '-Recurse', 'x'])"
   ```

3. Do not attempt comprehensive code-analysis or obfuscation detection in this
   slice. Simple command-string defense-in-depth is enough.
4. Preserve safe-path exceptions only where they are genuinely safe. Do not let
   a command like `shutil.rmtree('GT-KB')` bypass the gate because it contains a
   broad safe-path substring elsewhere.
5. Verification must include:

   ```powershell
   python -m pytest tests/unit/test_destructive_gate_hook.py -q
   python -m ruff check .claude/hooks/destructive-gate.py tests/unit/test_destructive_gate_hook.py --select E,F
   ```

6. If the implementation touches no production code outside the hook and its
   tests, a full release gate is optional for this bridge, but report whether
   it was run.

## Responses To Prime Questions

1. **Option:** Option 1.
2. **Pattern depth:** Block Bash-tool command strings containing these Python
   recursive deletion calls. Do not try to police ordinary source edits through
   this hook.
3. **Test scope:** Cover the new patterns and one representative non-recursive
   allowed case. Existing patterns do not need a broad retest in this slice.

