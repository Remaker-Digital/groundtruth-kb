VERIFIED

# Session Self-Init Project-Root Path-Doubling Fix - Codex Verification

**Status:** VERIFIED
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-005.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: agent-red
implementation_scope: startup-hook
requires_review: false
requires_verification: false

---

## Verdict

VERIFIED.

Commit `5157681c` rejects drive-relative `--project-root` inputs before
`Path.resolve()` can silently create doubled paths. The regression test passes,
ruff is clean on the changed files, and the manual bad-input command exits
non-zero without creating `E:\GT-KB\GT-KB`.

## Verification Evidence

Targeted regression:

```powershell
python -m pytest tests/scripts/test_session_self_initialization.py::test_project_root_rejects_drive_relative_path_to_prevent_doubling -q
```

Result:

```text
1 passed
```

Ruff:

```powershell
python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F
```

Result:

```text
All checks passed!
```

Manual bad-input check:

```powershell
python scripts/session_self_initialization.py --project-root E:GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
```

Result:

```text
exit=1
--project-root must be an absolute path; got WindowsPath('E:GT-KB')...
nested=False
```

Commit `5157681c` also updates `scripts/guardrails/assertion-baseline.json` as
assertion-ratchet bookkeeping. That does not affect the verification outcome.

## Responses To Prime Questions

1. **Test message text robustness:** Current substring-level assertion is
   acceptable.
2. **GH-002 row-17 status update:** Defer. This fix does not close GH-002.

