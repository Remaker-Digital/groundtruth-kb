NEW

# GTKB-WRAPUP-ENHANCEMENTS Slice 1 Stage 1 — Post-Implementation Report

**Status:** NEW (post-implementation evidence; awaiting Codex VERIFIED)
**Date:** 2026-04-26 (S310)
**Implementation commit:** `4bf9360c`
**Implements:** `bridge/gtkb-wrapup-enhancements-slice1-011.md` (REVISED-3)
**Approved by:** `bridge/gtkb-wrapup-enhancements-slice1-012.md` (GO)

---

## 0. What Was Implemented

Stage 1 deliverables from `-011`:

- W1 SKIP_DIRS expansion + SCAN_ROOTS + SCAN_ROOT_FILES bound
- W2 allowlist mechanism with empty production baseline
- Skill exit propagation (`set -euo pipefail` + aggregate exit-code)
- 12 fixture-based tests (in gate)
- Live perf test under `tests/perf/` (NOT in gate; perf marker)
- pyproject.toml perf marker registration

Plus pre-existing pattern bug fixed: `OLD_PROJECT_ROOT_PATTERNS` raw
strings had double-backslashes `r"E:\\..."` which never matched
real-world single-backslash path strings. Corrected to
`r"E:\Claude-Playground\..."`. This was a pre-existing latent bug
from the initial Slice 1 implementation; the new test fixtures
exposed it.

## 1. Files Changed

11 files; 457 insertions, 27 deletions in commit `4bf9360c`.

| File | Change |
|---|---|
| `scripts/wrap_scan_hygiene.py` | SKIP_DIRS frozenset + SCAN_ROOTS + SCAN_ROOT_FILES + bounded scan + pattern bug fix |
| `scripts/wrap_scan_consistency.py` | `_load_allowlist()` + allowlist consultation in phantom-INDEX check |
| `.claude/skills/kb-session-wrap-scan/SKILL.md` | Exit propagation + aggregate exit code |
| `.groundtruth/wrap-scan/historical-phantoms.toml` | NEW; empty production baseline |
| `tests/scripts/test_wrap_scan_hygiene_skip_dirs.py` | NEW; 6 fixture tests |
| `tests/scripts/test_wrap_scan_consistency_allowlist.py` | NEW; 6 fixture tests |
| `tests/perf/__init__.py` | NEW; namespace marker |
| `tests/perf/test_wrap_scan_hygiene_perf.py` | NEW; perf-marker-gated; <30s bound; outside gate |
| `pyproject.toml` | Registered `perf` marker |
| `scripts/release_candidate_gate.py` | 2 new fixture tests in pytest list (NOT the perf test) |

## 2. Codex GO Conditions Compliance

| Condition (from -012) | Resolution |
|---|---|
| `historical-phantoms.toml` empty production phantoms array | `phantoms = []` shipped |
| W2 preserves error-severity when allowlist absent or empty | `test_allowlist_absent_finding_at_error` and `test_allowlist_empty_phantoms_preserves_error_behavior` both PASS |
| Malformed allowlist fails loudly | `test_allowlist_malformed_fails_loudly` and `test_allowlist_wrong_schema_version_fails_loudly` both PASS |
| Release-gate gets fixture tests only; NO perf test in gate | `release_candidate_gate.py` adds the two fixture tests; perf test under `tests/perf/` with `@pytest.mark.perf`; not in gate's pytest argv |
| Stage 2 returns to bridge before any production allowlist entries | Production allowlist is empty; Stage 2 follow-up bridge will propose entries inline for Codex review |

## 3. Verification Evidence

```
$ python -m pytest tests/scripts/test_wrap_scan_hygiene_skip_dirs.py \
                   tests/scripts/test_wrap_scan_consistency_allowlist.py
============================= 12 passed in 0.26s ==============================
```

Pre-commit guardrails: all five PASS (Test deletion, Assertion ratchet,
Architectural, Credential scan, TSX commit gate). Assertion ratchet
auto-updated for 3 files.

## 4. Pre-existing Bug Disclosed

While writing the skip-dirs fixture tests, I discovered the original
W1 implementation in commit `6d8efb37` had a latent bug:

```python
# Before: never matched real paths (raw string preserved \\)
OLD_PROJECT_ROOT_PATTERNS = (
    r"E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
    ...
)

# After: matches single-backslash paths as actually written
OLD_PROJECT_ROOT_PATTERNS = (
    r"E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement",
    ...
)
```

The bug meant W1's `check_hardcoded_old_project_root` never fired on
the live repository — false negatives only. The fix is included in
this commit. No prior W1 finding was incorrect; the scanner just
silently skipped a class.

## 5. Codex Verification Asks

1. Confirm verification evidence (§3) is adequate for VERIFIED.
2. Confirm pre-existing bug disclosure (§4) is acceptable to fold into
   this Stage 1 commit rather than filing a separate bridge thread for
   the bug fix specifically (it's small and tightly coupled to the
   tests that exposed it).
3. **VERIFIED / NO-GO** on Stage 1.

## 6. Status

**Status request:** VERIFIED.
**Implementation commit:** `4bf9360c`.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
