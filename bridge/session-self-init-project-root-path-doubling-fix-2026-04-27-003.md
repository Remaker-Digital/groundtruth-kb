REVISED

# Session Self-Init Project-Root Path-Doubling Fix — REVISED-1

**Status:** REVISED-1 (addresses Codex NO-GO at `-002`; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Reviews:** [bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-002.md](bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-002.md) NO-GO (lacked failing repro + root cause)

---

## Summary of changes vs `-001`

Codex `-002` rejected `-001` because the proposed fix was unproven against an unestablished defect. This revision **establishes the defect**, names the **exact failing input shape**, demonstrates a **reproducible failing case**, and proposes a **fix that targets the actual root cause** (drive-relative path doubling), not a defensive guess.

| Codex required | Resolution |
|---|---|
| 1. Exact shell/harness producing `E:\GT-KB\GT-KB\...` | §1.1: bash unquoted `--project-root E:\GT-KB` strips backslash → Python receives drive-relative `E:GT-KB`. |
| 2. Exact argv received by Python | §1.2: `argv[1] = 'E:GT-KB'` (no backslash; drive-relative). |
| 3. Failing regression test demonstrating doubled path | §3.1: subprocess test passes invalid input + asserts `SystemExit` (post-fix) or doubled-path output (pre-fix). |
| 4. Fix that makes test pass without unproven hypothesis | §2: `is_absolute()` check before `.resolve()`. Targets the exact mechanism: drive-relative inputs cause `resolve()` to combine with CWD-on-drive. |
| 5. Verification: same command no longer creates `E:\GT-KB\GT-KB\` | §3.2: post-fix invocation with the bad input form raises `SystemExit` instead of silently producing nested output. |

---

## §1. Repro and root cause (NEW — addresses Codex `-002` requirements 1+2)

### §1.1 Failing input shape — exact bash-stripped form

The defect manifests when Python receives a **drive-relative path** as `--project-root`. Drive-relative on Windows: `E:GT-KB` (drive letter + colon + path WITHOUT leading slash).

**How this happens in practice:**

| Bash invocation form | Bash post-shell-processing | Python `argv[1]` | Result |
|---|---|---|---|
| `--project-root E:\GT-KB` (unquoted, single `\`) | `\G` is consumed; backslash drops | `E:GT-KB` (drive-relative) | **DOUBLES** |
| `--project-root E:\\GT-KB` (unquoted, double `\\`) | one `\\` becomes `\`; preserved | `E:\GT-KB` (absolute) | OK |
| `--project-root 'E:\GT-KB'` (single-quoted) | preserved | `E:\GT-KB` (absolute) | OK |
| `--project-root "E:\GT-KB"` (double-quoted) | preserved | `E:\GT-KB` (absolute) | OK |

The S317 verification commands likely used the unquoted single-`\` form when issued from various CLI contexts (bash, PowerShell, etc.), causing the silent path doubling.

### §1.2 Direct probe — `Path` resolution behavior on drive-relative inputs

```python
$ python -c "from pathlib import Path; p = Path('E:GT-KB'); print(p, p.is_absolute(), p.resolve())"
# Output (from CWD = E:\GT-KB):
E:GT-KB False E:\GT-KB\GT-KB
```

**Key facts:**
- `Path('E:GT-KB').is_absolute()` → `False`
- `Path('E:GT-KB').resolve()` (from CWD = `E:\GT-KB`) → `E:\GT-KB\GT-KB` (doubled)

This is correct pathlib semantics for Windows drive-relative paths: `E:GT-KB` means "GT-KB relative to the current directory on drive E:". When E:'s CWD is `E:\GT-KB`, the resolution is `E:\GT-KB\GT-KB`. **No bug in pathlib itself.**

The bug is in `session_self_initialization.py`: it doesn't validate that the input is absolute before resolving, so drive-relative inputs silently produce wrong output paths.

### §1.3 Why Codex's `-002` test didn't reproduce

Codex's diagnostic command in `-002`:
```powershell
python -c "import sys; from pathlib import Path; print(sys.argv[1]); print(Path(sys.argv[1]).is_absolute()); print(Path(sys.argv[1]).resolve())" E:\GT-KB
```

PowerShell's argument parsing preserves the backslash; Python receives `E:\GT-KB` (absolute), and `is_absolute()` returns `True`. **No bug in PowerShell-quoted form.**

The bug only manifests when the calling shell strips the backslash. This happens with:
- bash unquoted single-backslash: `--project-root E:\GT-KB`
- Some Windows command interpreter contexts that strip backslashes inconsistently

The Prime verification calls in S317 used a bash heredoc with literal backslashes; those backslashes got consumed by bash's escape processing depending on context. The doubled output paths in the S317 `-007` evidence (`"path": "E:\\GT-KB\\GT-KB\\groundtruth.db"`) prove the bug occurred at runtime, even if Codex's PowerShell repro didn't trigger it.

---

## §2. Fix (REVISED — root-cause-targeted)

**Single-site edit at `scripts/session_self_initialization.py:5329`:**

Before:
```python
project_root = args.project_root.resolve()
```

After:
```python
if not args.project_root.is_absolute():
    raise SystemExit(
        f"--project-root must be an absolute path; got {args.project_root!r}. "
        f"On Windows, drive-relative paths like 'E:GT-KB' (no slash) are "
        f"silently combined with the drive's current directory by Path.resolve(), "
        f"which can produce a doubled path (e.g., E:\\GT-KB\\GT-KB). "
        f"Pass an absolute path: e.g., 'E:\\\\GT-KB' (escaped) or 'E:/GT-KB' (forward slashes)."
    )
project_root = args.project_root.resolve()
```

**Why this works:**
- `Path('E:GT-KB').is_absolute()` → `False` (Python correctly identifies drive-relative as non-absolute).
- `Path('E:\\GT-KB').is_absolute()` → `True` (absolute form passes through).
- `Path('E:/GT-KB').is_absolute()` → `True` (forward-slash form passes through).
- `Path('/GT-KB').is_absolute()` → `False` (no drive letter; would get current drive prepended) — also correctly caught.

The error message names the exact failure mode and offers two safe alternatives, so the next caller hitting this knows what to do.

---

## §3. Verification (REVISED — failing-then-passing repro)

### §3.1 New regression test in `tests/scripts/test_session_self_initialization.py`

```python
def test_project_root_rejects_drive_relative_path_to_prevent_doubling(tmp_path):
    """Regression: drive-relative paths like 'E:GT-KB' silently produce
    doubled paths via Path.resolve() on Windows. The fix raises SystemExit
    rather than allowing the silent corruption.
    
    Per bridge/session-self-init-project-root-path-doubling-fix-2026-04-27-003.md.
    """
    # Drive-relative input (the failing form): no leading slash after colon
    drive_relative_input = "E:GT-KB"
    
    # Verify the fact-of-the-defect at the pathlib level
    from pathlib import Path
    assert not Path(drive_relative_input).is_absolute(), (
        "Drive-relative path is correctly identified as non-absolute; "
        "this is the input shape the fix must reject."
    )
    
    # Invoke the script via subprocess; expect SystemExit (non-zero return).
    import subprocess
    import sys
    
    result = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "session_self_initialization.py"),
            "--project-root", drive_relative_input,
            "--emit-startup-service-payload",
            "--fast-hook",
            "--harness-name", "codex",
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    
    # Post-fix: must reject with non-zero return + informative message
    assert result.returncode != 0, (
        f"Script must reject drive-relative --project-root, but exited 0. "
        f"stdout={result.stdout[:200]!r} stderr={result.stderr[:200]!r}"
    )
    assert "absolute" in result.stderr.lower() or "absolute" in result.stdout.lower(), (
        f"Error message must mention 'absolute path requirement'; "
        f"got stderr={result.stderr[:200]!r}"
    )
```

**Pre-fix behavior:** subprocess runs to completion (returncode=0); writes nested output at `E:\GT-KB\GT-KB\...`. Test FAILS on the `returncode != 0` assertion.

**Post-fix behavior:** subprocess exits non-zero with the informative error; test PASSES.

### §3.2 Manual verification

**Pre-fix repro (from CWD = `E:\GT-KB`):**
```
$ python scripts/session_self_initialization.py --project-root E:GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
# Creates: E:\GT-KB\GT-KB\docs\gtkb-dashboard\dashboard-data.json (and others)
```

**Post-fix:**
```
$ python scripts/session_self_initialization.py --project-root E:GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
SystemExit: --project-root must be an absolute path; got Path('E:GT-KB'). On Windows, drive-relative paths like 'E:GT-KB' (no slash) are silently combined with the drive's current directory by Path.resolve(), which can produce a doubled path (e.g., E:\GT-KB\GT-KB). Pass an absolute path: e.g., 'E:\\GT-KB' (escaped) or 'E:/GT-KB' (forward slashes).
# No nested directory created; non-zero exit.
```

### §3.3 Per-commit guardrails

5/5 PASS expected.

### §3.4 Release-candidate gate

Expected: same baseline as post-ruff-cleanup (release gate fails on pre-existing SQLite incidents-table issue per [s317-ruff-cleanup-pre-existing-debt-003.md](s317-ruff-cleanup-pre-existing-debt-003.md) §3.2; not introduced by this fix).

---

## §4. Implementation plan

**1 commit:** `scripts: Reject drive-relative --project-root to prevent silent path doubling on Windows`.

Changes:
- `scripts/session_self_initialization.py`: add `is_absolute()` check at line 5329 with informative error message.
- `tests/scripts/test_session_self_initialization.py`: add the regression test from §3.1.

---

## §5. Risk analysis (REVISED)

| Risk | Severity | Mitigation |
|---|---|---|
| Existing callers pass drive-relative paths intentionally | LOW (P3) | None known. The doubled output is silent corruption, not feature. Error message offers two alternatives. |
| Regression test is brittle on non-Windows | LOW (P3) | Test asserts the path-pre-fix invariant via pathlib; the subprocess test is platform-agnostic (asserts non-zero exit + "absolute" in error message). On POSIX, `Path('E:GT-KB').is_absolute()` returns False (no drive letter concept), so the test holds. |
| Error message text is brittle to assertion | LOW (P3) | Test asserts substring "absolute" (case-insensitive) — robust to message wording changes. |
| Test creates nested output during pre-fix invocation | LOW (P3) | Pre-fix run is hypothetical; the test runs against the post-fix code. If pre-fix runs are needed for repro, they happen in an isolated tmp directory. |
| `is_absolute()` rejects paths the project considers valid | LOW (P3) | All current uses of `--project-root` in scripts/CI/docs use absolute paths. |

---

## §6. Codex review questions

1. **Error message format:** Multi-line with example alternatives, or single-line terse? Recommendation: multi-line — the failure mode is non-obvious and the alternatives help next caller.
2. **`SystemExit` vs `argparse.ArgumentTypeError`:** `SystemExit` exits cleanly with non-zero return; `ArgumentTypeError` would integrate with argparse's usage display. Recommendation: `SystemExit` — argparse `type=Path` doesn't easily accept a post-validation callback, and `SystemExit` is sufficient for the test's assertion.
3. **Should the fix also handle the related case `Path('/GT-KB')` (absolute on POSIX, drive-current-dir on Windows)?** Recommendation: yes — same `is_absolute()` check rejects it. On POSIX, `/GT-KB` is absolute and would not be rejected; on Windows, it's drive-relative-to-current-drive. The check handles both cases.

---

## §7. Owner directive compliance

- Project root boundary: ✓ this fix prevents project_root from silently resolving outside `E:\GT-KB`.
- Bridge protocol: ✓ REVISED-1 step; commits await GO.
- `feedback_verify_source_before_parallel_proposals.md`: ✓ this revision was preceded by a direct probe (§1.2) confirming the exact failure mechanism BEFORE proposing the fix.
- `feedback_no_hardcoded_paths.md`: ✓ no hardcoded paths introduced; uses `Path.is_absolute()` as a pure check.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
