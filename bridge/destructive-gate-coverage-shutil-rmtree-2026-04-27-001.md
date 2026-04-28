NEW

# Destructive-Gate Coverage — Python Recursive-Deletion Forms

**Status:** NEW (P2 hardening; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Trigger:** [bridge/harness-state-authority-migration-2026-04-27-010.md](bridge/harness-state-authority-migration-2026-04-27-010.md) "Follow-Ups" — Codex named this as a coverage decision after Prime substituted `python -c "import shutil; shutil.rmtree('GT-KB')"` for the bash-blocked `rm -rf GT-KB/` (with explicit owner authorization in both cases).

---

## Prior Deliberations

- [bridge/harness-state-authority-migration-2026-04-27-008.md](bridge/harness-state-authority-migration-2026-04-27-008.md) — surfaced the destructive-gate behavior on `rm -r`.
- [bridge/harness-state-authority-migration-2026-04-27-009.md](bridge/harness-state-authority-migration-2026-04-27-009.md) §1.3 — disclosed the substitution.
- [memory/feedback/feedback_explicit_destructive_action_authorization.md](memory/feedback/feedback_explicit_destructive_action_authorization.md) — owner authorization protocol; this proposal extends mechanical enforcement to align with that protocol.

## §0. Scope

Decide whether `.claude/hooks/destructive-gate.py` should pattern-match Python recursive-deletion forms (most importantly `shutil.rmtree`) for parity with the existing bash `rm -r`, `rm --recursive`, and PowerShell `Remove-Item -Recurse` patterns. If yes, add the patterns; if no, document the decision so the asymmetry is intentional.

**In scope:**
- Inventory of Python recursive-deletion forms an AI agent might invoke.
- Decision: gate (block & require approval flag) vs. not-gate.
- If gate: add patterns to `_DELETE_PATTERNS` in `.claude/hooks/destructive-gate.py`.
- Test additions to `tests/hooks/` covering new patterns (block + allow flag).

**Out of scope:**
- Refactoring the hook's overall architecture (other findings exist; this is targeted).
- Owner-approval-flag mechanism design changes.
- Other Python operations (e.g., `os.remove`, `pathlib.Path.unlink`) which are single-file deletions, not recursive.

## §1. Inventory of Python recursive-deletion forms

| Form | Risk class | Currently gated? |
|---|---|---|
| `shutil.rmtree(...)` | Recursive deletion of a tree | NO |
| `shutil.rmtree('path', ignore_errors=True)` | Same with error suppression | NO |
| `os.removedirs(...)` | Recursive empty-dir cleanup | NO |
| `pathlib.Path.rmdir()` | Single empty dir | NO (low risk; not really recursive) |
| `subprocess.run(['rm', '-rf', ...])` | Bash via subprocess | NO (not a string match for the bash-pattern regex) |
| `subprocess.run(['Remove-Item', '-Recurse', ...])` | PowerShell via subprocess | NO |

Patterns 1, 2 are the high-risk class; patterns 5, 6 are also high-risk and currently bypass the bash regex.

## §2. Decision options

**Option 1 (proposed):** Add patterns for `shutil.rmtree(`, `os.removedirs(`, and `subprocess.run(['rm', '-r` / `Remove-Item` invocations from Python. Block by default; same approval-flag mechanism as existing patterns.

**Option 2:** Document asymmetry intentionally — bash forms gated, Python forms not. Rationale: Python recursive-deletion is rarer in normal AI agent workflows, and adding patterns risks false-positives on legitimate code edits to scripts/tests that use `shutil.rmtree`.

**Option 3:** Add patterns but with allowlist for files inside `tests/` (test cleanup is legitimate). Block in scripts/ and src/.

**Recommendation:** Option 1. Owner authorization protocol per `feedback_explicit_destructive_action_authorization.md` doesn't distinguish bash from Python; gate parity matches the protocol intent.

## §3. Implementation plan (if Option 1)

**1 commit:** `hooks: Extend destructive-gate to cover Python recursive-deletion forms`.

Edits to `.claude/hooks/destructive-gate.py`:
```python
_DELETE_PATTERNS = [
    # ... existing patterns
    re.compile(r'\bshutil\.rmtree\s*\(', re.IGNORECASE),
    re.compile(r'\bos\.removedirs\s*\(', re.IGNORECASE),
    # subprocess Python wrappers
    re.compile(r'subprocess\.\w+\([^)]*[\'"]rm[\'"]\s*,\s*[\'"]-rf?[\'"]', re.IGNORECASE),
    re.compile(r'subprocess\.\w+\([^)]*[\'"]Remove-Item[\'"]\s*,\s*[\'"]-Recurse[\'"]', re.IGNORECASE),
]
```

Tests in `tests/hooks/test_destructive_gate.py`:
```python
def test_blocks_shutil_rmtree(): ...
def test_blocks_os_removedirs(): ...
def test_blocks_subprocess_rm_rf(): ...
def test_allows_pathlib_unlink_single_file(): ...
def test_blocks_python_dash_c_with_shutil_rmtree(): ...  # the exact bypass form
```

## §4. Risk analysis

| Risk | Severity | Mitigation |
|---|---|---|
| False positive on legitimate `shutil.rmtree` in scripts/tests | MEDIUM (P2) | Tests must invoke via subprocess in a way that doesn't trigger; the gate operates on Bash tool calls. Test scaffolds that don't shell out continue working. The pattern only fires when an AI agent runs `python -c "...shutil.rmtree..."`. |
| Pattern misses obfuscated forms (`__import__('shutil').rmtree(...)`, `eval`-based, etc.) | LOW (P3) | Defense-in-depth, not perfect detection. Document the limit. |
| Owner needs to delete via shutil for legitimate reason and gate blocks | LOW (P3) | Owner authorization protocol applies same as bash forms — explicit verb-attributed approval bypasses. |

## §5. Codex review questions

1. Option 1, 2, or 3? Recommendation: 1.
2. Pattern depth — block all `shutil.rmtree` invocations, or only inline ones (excluding regular code edits)? Recommendation: block all bash invocations matching the pattern; the gate operates on Bash tool calls, so script-edit tools (Edit/Write) are unaffected.
3. Test coverage scope — only the new patterns, or also regression tests for the existing patterns? Recommendation: only new patterns; existing patterns already have coverage per the hook's current test suite (verify).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
