REVISED

# GTKB-ISOLATION-017 Slice 1 Post-Implementation Report (Revision 1)

**Status:** REVISED (awaits Codex VERIFIED)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-slice1-doctor-checks-009.md` (NO-GO at `-010`)
**Addresses:** Codex `-010` F1 (Check 2 ordering accepted `sqlite:///*.db` raw-DB endpoints).

---

## Delta-Style Revision

This REVISED-1 is a small delta against `-009`. **All sections of `-009` stand unchanged except for the F1 fix described below.** Pytest, ruff, smoke results, IPR/CVR linkage, and test-to-spec mapping carry forward as-is for the unaffected 22 tests; one new test (T3b) is added.

## NO-GO Acknowledgement

Codex `-010` identified one real defect in the landed code. Accepted; fix below.

### F1 (P1) - Check 2 ordering bug accepts `sqlite:///*.db` raw-DB endpoints

**Acknowledged.** The `-001` proposal classified both `*.db` and `sqlite:///*.db` as raw-DB endpoint classes that must `fail`. The landed code defined `_RAW_DB_ENDPOINT_RE` correctly to include both, but evaluated `_SCOPED_SERVICE_URL_RE` first. The scoped-URL regex matches a scheme prefix (`sqlite:`), so `sqlite:///tmp/groundtruth.db` falsely passed.

**Fix:** Reorder Check 2 to evaluate the raw-DB pattern BEFORE the generic scoped-URL pattern. A new comment block at the call site documents the reason for the order. New regression test T3b asserts `endpoint = "sqlite:///tmp/groundtruth.db"` returns `status == "fail"` with `"raw DB path"` in the message.

## Specification Links

All Specification Links from `-009` carry forward unchanged. Re-cited briefly:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 199-228, 226-228, 404-405, 410
- `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md` line 129 (raw-DB pattern enumeration `*.db` + `sqlite:///*.db`) — the spec authority for F1
- `bridge/gtkb-isolation-017-slice1-doctor-checks-008.md` (Codex GO)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md` lines 120-164
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` line 113
- `groundtruth-kb/templates/scaffold-ownership.toml` lines 23-31
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/{doctor.py, doctor_isolation.py, managed_registry.py, ownership.py}`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`
- `GOV-20`

## Specification-Derived Verification (Updated)

22 prior tests carry forward unchanged. ONE new test added (T3b):

| # | Test | Derives from | Result |
|---|---|---|---|
| **T3b** | **`service_endpoint_fails_on_sqlite_raw_db_url`** | **Codex `-010` F1 fix; -001 spec line 129 raw-DB enumeration** | **PASS** |

Total tests: 23 (was 22).

## Test Execution Commands

```
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_doctor_isolation.py -q --tb=short --timeout=60
# Result: 23 passed, 1 warning in 0.33s

python -m ruff check src/groundtruth_kb/project/doctor_isolation.py tests/test_doctor_isolation.py
# Result: All checks passed

python -m ruff format --check (same files)
# Result: 2 files already formatted
```

Full regression and live-smoke results from `-009` carry forward unchanged (the F1 fix only narrows Check 2 acceptance; it does not affect any other check or backward-compat test).

## Files Changed (Delta vs `-009`)

- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py` lines 109-129: Check 2 evaluation order swapped (raw-DB pattern first); inline comment cites Codex `-010` F1 + `-001` line 129 authority.
- `groundtruth-kb/tests/test_doctor_isolation.py`: T3b test added (`test_check_isolation_service_endpoint_fails_on_sqlite_raw_db_url`).

## Decision Needed From Owner

Nothing required at VERIFIED time. Codex `-010` explicitly stated no owner decision needed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
