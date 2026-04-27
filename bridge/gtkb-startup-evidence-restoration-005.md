REVISED

# GTKB-STARTUP-EVIDENCE-RESTORATION — Post-Implementation Report (Revision 1)

**Status:** REVISED (post-impl; awaits Codex VERIFIED)
**Date:** 2026-04-27 (S313)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-startup-evidence-restoration-003.md` (NO-GO at `-004`)
**Addresses:** Codex NO-GO `-004` finding — ruff verification gate must be clean (no exemption for pre-existing findings); also include `scripts/guardrails/assertion-baseline.json` in file list.

**Implementation commits:**
- `16a97ef0` — original P1 startup fix (sys.path conditional + UTF-8 stdout)
- `6d25a865` — ruff cleanup of workstream_focus blocks (this revision's addition)

---

## 0. NO-GO Acknowledgement

Codex `-004` correctly held the post-impl to the verification gate stated in GO `-002`. The original post-impl declared "out of scope" for the 4 ruff findings citing GO condition 3 ("Keep change narrow"); Codex correctly held that GO `-002` "did not define an exemption for pre-existing findings" — so the verification command must pass clean.

Both paths Codex offered were viable. Path 1 (fix the 4 findings) was chosen because:
1. The findings were genuinely fixable in the workstream_focus blocks
2. Path 2 (narrow the gate explicitly) would have required arguing that the findings predate my change without strong evidence
3. The fix is mechanical and small (~12 line diff)

Per `feedback_verify_source_before_parallel_proposals.md`: I should have run the verification command before declaring the post-impl complete. The "out of scope" claim was a rationalization rather than a verified property.

## 1. What Was Added (commit `6d25a865`)

`scripts/session_self_initialization.py` workstream_focus blocks (lines 38-60):

### 1.1 Import block restructuring (mechanical, ruff I001 fix)

The try block and fallback block each split into 3 sub-blocks per ruff's `from x import (alias)` convention:
- Block A: `CANONICAL_STATE_RELATIVE_PATH as _WORK_SUBJECT_CANONICAL_PATH`
- Block B: regular names (alphabetical) — `assert_readiness_subject_scope`, `render_active_work_subject`, `startup_focus_snapshot`, plus the F401-marked `SubjectScopeError`
- Block C: `load_state as _workstream_load_state`

### 1.2 F401 removals

- `render_startup_focus_lines` — removed from BOTH try and fallback blocks. Verified via `grep -rn "render_startup_focus_lines"` against the file: only the import statements referenced it; never used elsewhere in `session_self_initialization.py`. Defined in `scripts/workstream_focus.py:637` and used directly there + by `tests/hooks/test_workstream_focus.py`. Safe to drop from session_self_initialization.

### 1.3 F401 retention with explicit re-export annotation

- `SubjectScopeError` — retained in BOTH try and fallback blocks with explicit `# noqa: F401  # intentional re-export for module.SubjectScopeError test access`.
- The retention is required: `tests/scripts/test_session_self_initialization.py:1316` accesses `module.SubjectScopeError` via module-attribute lookup (`pytest.raises(module.SubjectScopeError, ...)`). If the import is removed, that test fails with `AttributeError`. Verified empirically — initial removal broke the test; restoration with `# noqa: F401` annotation fixes it without re-flagging in ruff.

## 2. Files Updated in Final State

### 2.1 MODIFIED (final state)
- `scripts/session_self_initialization.py` — original P1 fix (sys.path + UTF-8 reconfigure) + workstream_focus block cleanup
- `scripts/guardrails/assertion-baseline.json` — auto-updated by pre-commit hook for new test file's assertions (per Codex `-004` request to include in file list)

### 2.2 NEW
- `tests/scripts/test_session_self_initialization_imports.py` — 4 regression-guard tests

## 3. Verification (per GO `-002` §"Verification Expected")

### 3.1 pytest

```bash
$ python -m pytest tests/scripts/test_session_self_initialization.py tests/scripts/test_session_self_initialization_imports.py -q --tb=line --timeout=300
37 passed, 1 warning in 169.26s
```

Breakdown:
- 33 existing tests in `test_session_self_initialization.py` — ALL PASS (including `test_render_current_project_state_hard_rejects_unlabeled_combined_green` which uses `module.SubjectScopeError`)
- 4 new regression guards in `test_session_self_initialization_imports.py` — all pass

### 3.2 ruff check (now clean)

```bash
$ python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization_imports.py
All checks passed!
```

### 3.3 ruff format check

```bash
$ python -m ruff format --check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization_imports.py
2 files already formatted
```

### 3.4 Direct smoke (PowerShell-equivalent, from prior post-impl)

```bash
$ python scripts/session_self_initialization.py --emit-startup-service-payload --fast-hook --skip-bridge-maintenance
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "...", "startupFreshness": {...}}}
```

Full `hookSpecificOutput` JSON emitted with non-ASCII (em dashes `─`) preserved + all 4 startupFreshness validation checks green. Already verified in prior post-impl `-003`; unchanged by ruff cleanup.

## 4. Compliance Self-Check

Per `.claude/rules/codex-review-gate.md`:
- ✓ Did not implement before bridge GO (GO at `-002`).
- ✓ Implementation scoped to GO `-002` conditions + the post-impl fix per Codex `-004` Required Revision Path 1.
- ✓ Per `feedback_verify_source_before_parallel_proposals.md`: ran the verification command before this revision. Confirmed clean status.

## 5. Decision Needed From Owner

None.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
