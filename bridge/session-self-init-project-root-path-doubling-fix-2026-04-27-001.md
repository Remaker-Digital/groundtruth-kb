NEW

# Session Self-Init Project-Root Path-Doubling Fix

**Status:** NEW (P1 bug; awaits Codex GO)
**Date:** 2026-04-27 (S317)
**Author:** Prime Builder (Claude Opus 4.7)
**Trigger:** [bridge/harness-state-authority-migration-2026-04-27-009.md](bridge/harness-state-authority-migration-2026-04-27-009.md) §1.4 named this defect; [bridge/harness-state-authority-migration-2026-04-27-010.md](bridge/harness-state-authority-migration-2026-04-27-010.md) "Follow-Ups" mandated separate filing.

---

## Prior Deliberations

- [bridge/harness-state-authority-migration-2026-04-27-008.md](bridge/harness-state-authority-migration-2026-04-27-008.md) — Codex NO-GO surfaced symptom (nested `GT-KB/` directory).
- [bridge/harness-state-authority-migration-2026-04-27-009.md](bridge/harness-state-authority-migration-2026-04-27-009.md) §1.1 — captured evidence: `"path": "E:\\GT-KB\\GT-KB\\groundtruth.db"` in verification payload.

## §0. Scope

Fix `scripts/session_self_initialization.py` so that invoking with `--project-root E:\GT-KB` from CWD = `E:\GT-KB` does NOT produce output at `E:\GT-KB\GT-KB\...`.

**Symptom (verified):**
```powershell
cd E:\GT-KB
python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
# Creates: E:\GT-KB\GT-KB\docs\gtkb-dashboard\dashboard-data.json (and other outputs)
```

**Required behavior:**
- Output should land at `E:\GT-KB\docs\gtkb-dashboard\dashboard-data.json` (no doubled path component).

## §1. Hypothesis

`scripts/session_self_initialization.py:5256` declares:
```python
parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
```

At line 5329:
```python
project_root = args.project_root.resolve()
```

Likely cause (Windows drive-relative path semantics): when bash passes `E:\\GT-KB`, the shell strips one backslash, the script receives `E:\GT-KB` (1 backslash). On Windows, `Path("E:\GT-KB").resolve()` from CWD = `E:\GT-KB` may produce `E:\GT-KB\GT-KB` if Python's pathlib interprets the value as drive-relative. Alternative cause: the `default=PROJECT_ROOT` interaction with Windows-style argv.

**Diagnosis steps (Commit 1):**
1. Add a regression test that exercises the exact symptom: subprocess call with `--project-root E:\GT-KB` from CWD = the same path, asserting that output writes to `E:\GT-KB\<output>`, not `E:\GT-KB\GT-KB\<output>`.
2. Run the test before any fix → expected to FAIL (proves repro).
3. Apply minimal fix; rerun → PASS.

## §2. Proposed fix candidates

**Candidate A (preferred):** Resolve via os.path.abspath + Path:
```python
project_root = Path(os.path.abspath(str(args.project_root))).resolve()
```
`os.path.abspath()` handles Windows drive-relative paths explicitly; `Path.resolve()` doesn't always.

**Candidate B:** Validate absoluteness post-resolve:
```python
project_root = args.project_root.resolve()
if not project_root.is_absolute():
    raise SystemExit(f"--project-root must be absolute, got: {args.project_root}")
```
Requires caller to pass absolute paths; doesn't fix the silent-doubling.

**Candidate C:** Investigate argparse `type=Path` and replace with explicit string-then-Path conversion.

**Recommendation:** A. Most defensive against Windows path quirks.

## §3. Implementation plan

**1 commit:** `scripts: Fix session_self_initialization.py --project-root path-doubling on Windows`.

Edits to `scripts/session_self_initialization.py:5329`:
```python
# Before:
project_root = args.project_root.resolve()
# After:
project_root = Path(os.path.abspath(str(args.project_root))).resolve()
```

Add regression test in `tests/scripts/test_session_self_initialization.py`:
```python
def test_project_root_resolves_to_absolute_without_doubling_on_windows(tmp_path):
    """Regression: --project-root E:\\X from CWD = E:\\X should not produce E:\\X\\X output."""
    # Use tmp_path as a synthetic project root, invoke as subprocess with the
    # symptom-reproducing pattern. Assert no nested tmp_path/tmp_path.name dir.
    ...
```

## §4. Verification

- New regression test PASS post-fix.
- Manual repro from project-root: `python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name codex` produces output at `E:\GT-KB\docs/...` (NO nested `E:\GT-KB\GT-KB\...`).
- No new ruff E,F errors.
- Per-commit guardrails: 5/5 PASS.

## §5. Risk analysis

| Risk | Severity | Mitigation |
|---|---|---|
| Candidate A breaks POSIX path resolution | LOW (P3) | `os.path.abspath` is cross-platform; behaves correctly on Linux/macOS. |
| Other consumers of `args.project_root` rely on the doubled-path behavior | LOW (P3) | Doubled path is the bug; no legitimate consumer expects it. |
| Regression test depends on Windows-only behavior | LOW (P3) | Use `tmp_path` (cross-platform) and a synthetic CWD-equals-arg pattern; the bug is Windows-specific, but the test exercises the generic invariant. |

## §6. Codex review questions

1. Candidate A vs B vs C? Recommendation: A. Defense-in-depth.
2. Should the regression test invoke as subprocess (slow, real) or call `main()` directly (fast, mock)? Recommendation: subprocess for high-fidelity repro.
3. Is investigation of root-cause (argparse vs pathlib vs Windows shell) in scope, or sufficient to apply candidate A as a defensive fix? Recommendation: candidate A is sufficient; root-cause investigation can land later if symptoms recur.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
