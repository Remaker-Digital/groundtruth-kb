# Post-Implementation Report: Spec Hygiene — Verified-but-Untested (Tracks C/D/E)

**Author:** Prime Builder (Opus 4.6 / Claude Code, session S291+)
**Date:** 2026-04-14
**Status:** NEW — awaiting Codex VERIFIED
**Implements:** GO at `bridge/spec-hygiene-untested-verified-006.md`
**Scope:** 9 non-governance, non-SPA verified-but-untested specs (Tracks C, D, E)

---

## Summary

All 9 in-scope specs are now in a terminal state. 4 specs are verified with current,
non-stale, confirmed-passing evidence (terminal state a). 5 specs were reverted to
`implemented` with hygiene WIs (terminal state b). Zero assertions failed. SPEC-1837
preserved at 35 current rows.

---

## Pre-Implementation Baseline: SPEC-1837 (all 35 current rows)

Captured before any KB write. Full output:

```
TEST-10452  None  None::None
TEST-10453  None  None::None
TEST-10454  None  None::None
TEST-10475  pass  tests/multi_tenant/test_log_retention.py::test_three_collections
TEST-10476  pass  tests/multi_tenant/test_log_retention.py::test_starter_audit_365
TEST-10477  pass  tests/multi_tenant/test_log_retention.py::test_professional_audit_365
TEST-10478  pass  tests/multi_tenant/test_log_retention.py::test_enterprise_audit_unlimited
TEST-10479  pass  tests/multi_tenant/test_log_retention.py::test_api_key_usage_90_all_tiers
TEST-10480  pass  tests/multi_tenant/test_log_retention.py::test_alert_history_180_all_tiers
TEST-10481  pass  tests/multi_tenant/test_log_retention.py::test_starter_audit_logs
TEST-10482  pass  tests/multi_tenant/test_log_retention.py::test_enterprise_audit_unlimited
TEST-10483  pass  tests/multi_tenant/test_log_retention.py::test_custom_override_takes_precedence
TEST-10484  pass  tests/multi_tenant/test_log_retention.py::test_custom_override_only_affects_specified_collection
TEST-10485  pass  tests/multi_tenant/test_log_retention.py::test_unknown_collection_falls_back
TEST-10486  pass  tests/multi_tenant/test_log_retention.py::test_365_days_cutoff
TEST-10487  pass  tests/multi_tenant/test_log_retention.py::test_none_retention_returns_none
TEST-10488  pass  tests/multi_tenant/test_log_retention.py::test_zero_retention_returns_now
TEST-10489  pass  tests/multi_tenant/test_log_retention.py::test_defaults_to_utc_now
TEST-10490  pass  tests/multi_tenant/test_log_retention.py::test_path_format
TEST-10491  pass  tests/multi_tenant/test_log_retention.py::test_path_with_different_month
TEST-10492  pass  tests/multi_tenant/test_log_retention.py::test_defaults_to_now
TEST-10493  pass  tests/multi_tenant/test_log_retention.py::test_expired_before_cutoff
TEST-10494  pass  tests/multi_tenant/test_log_retention.py::test_none_timestamp_retained
TEST-10495  pass  tests/multi_tenant/test_log_retention.py::test_invalid_timestamp_retained
TEST-10496  pass  tests/multi_tenant/test_log_retention.py::test_custom_timestamp_field
TEST-10497  pass  tests/multi_tenant/test_log_retention.py::test_naive_timestamp_treated_as_utc
TEST-10498  pass  tests/multi_tenant/test_log_retention.py::test_empty_records
TEST-10499  pass  tests/multi_tenant/test_log_retention.py::test_single_record
TEST-10500  pass  tests/multi_tenant/test_log_retention.py::test_multiple_records
TEST-10501  pass  tests/multi_tenant/test_log_retention.py::test_compact_separators
TEST-10502  pass  tests/multi_tenant/test_log_retention.py::test_empty_records
TEST-10503  pass  tests/multi_tenant/test_log_retention.py::test_starter_summary_structure
TEST-10504  pass  tests/multi_tenant/test_log_retention.py::test_starter_has_cutoff_dates
TEST-10505  pass  tests/multi_tenant/test_log_retention.py::test_enterprise_audit_unlimited
TEST-10506  pass  tests/multi_tenant/test_log_retention.py::test_enterprise_api_key_still_90
```

**Total baseline rows:** 35 (3 with `last_result=None`, 32 passing with file)

---

## Per-Spec Disposition

### Track C — Backend API/script specs

#### SPEC-0439 — Terminal state: (a) Verified with current evidence

**Spec:** The seed script MUST initialize tenants with `config_state`

**Historical test:** TEST-1482 v2 was `pass` for `tests/regression/test_migration_compat.py::test_config_state_default_is_active`.
The test ID was later recycled (v3 → different test, spec_id blank, stale).

**File/function existence check:**
```
SPEC-0439  file=YES  fn=YES  tests/regression/test_migration_compat.py::test_config_state_default_is_active
```

**Test run 2026-04-14:**
```
tests/regression/test_migration_compat.py::TestPreferencesDocumentFields::test_config_state_default_is_active PASSED
1 passed in 0.17s
```

**KB write:** Created TEST-11055 with `spec_id='SPEC-0439'`, `last_result='pass'`.

---

#### SPEC-0604 — Terminal state: (a) Verified with current evidence

**Spec:** A seed-generated widget key MUST be testable against the API

**Historical tests:** 5 distinct TEST IDs. TEST-1483 v2 was `fail` (excluded). TEST-1490
v2 was `pass` but is a regression test requiring a live server. TEST-1602/1603/1604 v2 were
`pass` in `tests/test_conftest_smoke.py` (unit-level smoke tests, no server required).

**Test run 2026-04-14:**
```
tests/test_conftest_smoke.py::TestAppClientAuth::test_protected_endpoint_no_auth_returns_401 PASSED
tests/test_conftest_smoke.py::TestAppClientAuth::test_protected_endpoint_with_api_key PASSED
tests/test_conftest_smoke.py::TestAppClientAuth::test_protected_endpoint_bad_key_returns_401 PASSED
3 passed in 4.10s
```

**KB writes:** Created TEST-11056, TEST-11057, TEST-11058 with `spec_id='SPEC-0604'`,
`last_result='pass'`. TEST-1483 (historical fail) not restored.

---

#### SPEC-1076 — Terminal state: (b) Reverted to implemented

**Spec:** POST /alerts/history/{alert_id}/acknowledge endpoint in superadmin_api

**Historical test:** TEST-1491 v2 was `skip` (not `pass`) in
`tests/regression/test_upgrade_regression.py::test_t1_24_superadmin_alert_history`.
Upgrade regression tests require a live server URL (`PROD_URL` env var). A `skip` result
is not valid passing evidence.

**KB writes:**
- `update_spec('SPEC-1076', status='implemented', ...)` — ok
- Created WI-3178: "Verified-but-untested spec hygiene: SPEC-1076 alert acknowledge
  endpoint needs real test coverage" (`origin='hygiene'`, `source_spec_id='SPEC-1076'`)

---

#### SPEC-1078 — Terminal state: (b) Reverted to implemented

**Spec:** GET /mfa/status endpoint in superadmin_api

**Historical test:** TEST-1492 v2 was `skip` in
`tests/regression/test_upgrade_regression.py::test_t1_25_superadmin_mfa_status`.
Same analysis as SPEC-1076: skip is not pass; live server required.

**KB writes:**
- `update_spec('SPEC-1078', status='implemented', ...)` — ok
- Created WI-3179: "Verified-but-untested spec hygiene: SPEC-1078 MFA status endpoint
  needs real test coverage" (`origin='hygiene'`, `source_spec_id='SPEC-1078'`)

---

#### SPEC-1097 — Terminal state: (a) Verified with current evidence

**Spec:** DELETE /named/{name} endpoint in tenant_config_api

**Historical tests:** TEST-1686/1687/1688/1689 v2 were all `pass` in
`tests/unit/test_config_processor.py`. Test IDs recycled (v3 → different tests, stale).

**Test run 2026-04-14:**
```
tests/unit/test_config_processor.py::TestNamedConfigurations::test_delete_named_config_success PASSED
tests/unit/test_config_processor.py::TestNamedConfigurations::test_delete_named_config_default_protected PASSED
tests/unit/test_config_processor.py::TestNamedConfigurations::test_delete_named_config_not_found PASSED
tests/unit/test_config_processor.py::TestNamedConfigurations::test_delete_named_config_unconfigured PASSED
4 passed in 0.22s
```

**KB writes:** Created TEST-11059, TEST-11060, TEST-11061, TEST-11062 with
`spec_id='SPEC-1097'`, `last_result='pass'`.

---

### Track D — Pricing/budget specs

#### SPEC-0661 — Terminal state: (b) Reverted to implemented

**Spec:** Pricing MUST include usage-based overage charges with documented thresholds

**Historical test:** TEST-1456 v1 had `result=None` (never executed). It was an S198
placeholder with no confirmation of passing. The test file
`tests/performance/test_performance.py::test_cost_model_tier_pricing` exists on disk, but
a never-run test is not valid evidence (Condition 1 of the GO).

**KB writes:**
- `update_spec('SPEC-0661', status='implemented', ...)` — ok
- Created WI-3180: "Verified-but-untested spec hygiene: SPEC-0661 pricing overage
  thresholds need real test coverage" (`origin='hygiene'`, `source_spec_id='SPEC-0661'`)

---

#### SPEC-0811 — Terminal state: (b) Reverted to implemented

**Spec:** The pipeline budget MUST reflect a P50 of 7,000ms and a stage timeout of 8,000ms

**Historical test:** TEST-1464 v1 had `result=None` (never executed). Same analysis as
SPEC-0661.

**KB writes:**
- `update_spec('SPEC-0811', status='implemented', ...)` — ok
- Created WI-3181: "Verified-but-untested spec hygiene: SPEC-0811 pipeline budget
  P50/timeout needs real test coverage" (`origin='hygiene'`, `source_spec_id='SPEC-0811'`)

---

### Track E — Widget surface specs

#### SPEC-1138 — Terminal state: (b) Reverted to implemented

**Spec:** Define widget views: closed, prechat, otp, conversation, rating, offline_form,
issue_report (source: `widget/src/state/store.ts`)

**Historical test:** TEST-1668 v2 was `pass` in
`tests/unit/test_chat_endpoints.py::test_report_issue_conversation_not_found`. The test
function currently passes (confirmed 2026-04-14). However, behavioral inspection shows a
mismatch: the spec describes the frontend widget view state machine (defined in
`widget/src/state/store.ts`), while the test asserts backend HTTP 404 behavior for the
`/api/chat/conversations/{id}/issue` endpoint. The test does not assert which widget
views exist or their transition logic.

**KB writes:**
- `update_spec('SPEC-1138', status='implemented', ...)` — ok
- Created WI-3182: "Verified-but-untested spec hygiene: SPEC-1138 widget views definition
  needs real behavioral test" (`origin='hygiene'`, `source_spec_id='SPEC-1138'`)

---

#### SPEC-1165 — Terminal state: (a) Verified with current evidence

**Spec:** Implement startConversation HTTP method with visitor identity object
(source: `widget/src/transport/http.ts`)

**Historical test:** TEST-1681 v2 was `pass` in
`tests/unit/test_chat_session.py::test_start_with_visitor_identity`.

**Behavioral alignment check:** The spec requires that `startConversation` carries a
visitor identity object. The test verifies that `start_conversation()` called with a
`VisitorIdentity(customer_id=...)` propagates `customer_id` to the created conversation
document. This is direct evidence that the visitor identity contract is honoured in the
backend session manager — the surface that the widget's HTTP call targets.

**Test run 2026-04-14:**
```
tests/unit/test_chat_session.py::TestStartConversation::test_start_with_visitor_identity PASSED
1 passed in 0.20s
```

**KB write:** Created TEST-11063 with `spec_id='SPEC-1165'`, `last_result='pass'`.

---

## Post-Implementation Invariant Verification

Command (executed 2026-04-14):

```python
import sys
sys.path.insert(0, r'E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src')
from pathlib import Path
from groundtruth_kb.db import KnowledgeDB
from groundtruth_kb.config import GTConfig
from groundtruth_kb.gates import GateRegistry
# ... (standard db setup)

in_scope = ['SPEC-0439','SPEC-0604','SPEC-1076','SPEC-1078','SPEC-1097',
            'SPEC-0661','SPEC-0811','SPEC-1138','SPEC-1165']
for spec_id in in_scope:
    spec = db.get_spec(spec_id)
    status = spec['status']
    tests = db.list_tests(spec_id=spec_id)
    non_stale = [t for t in tests if t.get('last_result') not in (None, 'stale')]
    if status == 'verified' and len(non_stale) == 0:
        assert False, f"{spec_id} FAIL: still verified with zero non-stale tests"
```

**Actual output:**

```
SPEC-0439: status=verified  non_stale_tests=1  total_tests=1
  TEST-11055  pass  tests/regression/test_migration_compat.py::test_config_state_default_is_active
SPEC-0604: status=verified  non_stale_tests=3  total_tests=3
  TEST-11056  pass  tests/test_conftest_smoke.py::test_protected_endpoint_no_auth_returns_401
  TEST-11057  pass  tests/test_conftest_smoke.py::test_protected_endpoint_bad_key_returns_401
  TEST-11058  pass  tests/test_conftest_smoke.py::test_protected_endpoint_with_api_key
SPEC-1076: status=implemented  non_stale_tests=0  total_tests=0
SPEC-1078: status=implemented  non_stale_tests=0  total_tests=0
SPEC-1097: status=verified  non_stale_tests=4  total_tests=4
  TEST-11059  pass  tests/unit/test_config_processor.py::test_delete_named_config_success
  TEST-11060  pass  tests/unit/test_config_processor.py::test_delete_named_config_default_protected
  TEST-11061  pass  tests/unit/test_config_processor.py::test_delete_named_config_not_found
  TEST-11062  pass  tests/unit/test_config_processor.py::test_delete_named_config_unconfigured
SPEC-0661: status=implemented  non_stale_tests=0  total_tests=0
SPEC-0811: status=implemented  non_stale_tests=0  total_tests=0
SPEC-1138: status=implemented  non_stale_tests=0  total_tests=0
SPEC-1165: status=verified  non_stale_tests=1  total_tests=1
  TEST-11063  pass  tests/unit/test_chat_session.py::test_start_with_visitor_identity

All 9 specs pass the verified-with-evidence invariant. 0 assertions failed.
```

---

## SPEC-1837 Post-Check

```
TEST-10481: still SPEC-1837 (OK)
TEST-10482: still SPEC-1837 (OK)
TEST-10483: still SPEC-1837 (OK)
TEST-10484: still SPEC-1837 (OK)
TEST-10485: still SPEC-1837 (OK)
SPEC-1837 total current tests: 35 (baseline was 35)
```

All 35 SPEC-1837 baseline rows are intact. No SPEC-1837 row was modified.

---

## KB Write Summary

| Write | What | ID |
|-------|------|----|
| insert_test | SPEC-0439 regression test | TEST-11055 |
| insert_test | SPEC-0604 smoke test — no auth | TEST-11056 |
| insert_test | SPEC-0604 smoke test — bad key | TEST-11057 |
| insert_test | SPEC-0604 smoke test — valid key | TEST-11058 |
| insert_test | SPEC-1097 delete named — success | TEST-11059 |
| insert_test | SPEC-1097 delete named — protected | TEST-11060 |
| insert_test | SPEC-1097 delete named — not found | TEST-11061 |
| insert_test | SPEC-1097 delete named — unconfigured | TEST-11062 |
| insert_test | SPEC-1165 startConversation with identity | TEST-11063 |
| update_spec | SPEC-1076 → implemented | — |
| update_spec | SPEC-1078 → implemented | — |
| update_spec | SPEC-0661 → implemented | — |
| update_spec | SPEC-0811 → implemented | — |
| update_spec | SPEC-1138 → implemented | — |
| insert_work_item | SPEC-1076 hygiene WI | WI-3178 |
| insert_work_item | SPEC-1078 hygiene WI | WI-3179 |
| insert_work_item | SPEC-0661 hygiene WI | WI-3180 |
| insert_work_item | SPEC-0811 hygiene WI | WI-3181 |
| insert_work_item | SPEC-1138 hygiene WI | WI-3182 |

**Total: 9 test artifacts created, 5 specs reverted, 5 hygiene WIs created.**

---

## Conditions Addressed

| Condition | Addressed |
|-----------|-----------|
| C1 — Restored links must be current non-stale evidence | YES — all 9 new test artifacts have `last_result='pass'`, confirmed by actual test runs on 2026-04-14 |
| C2 — Preserve full SPEC-1837 current baseline (all 35 rows) | YES — baselined all 35 rows pre-write, post-check confirms all 35 intact |
| C3 — Post-report includes executable verification | YES — actual pytest output included per spec; invariant check script included with actual output |

---

## Verification Conditions (from proposal -005)

1. Each of the 9 in-scope specs is in terminal state (a) or (b). **PASS** ✓
2. SPEC-1837 current test coverage unchanged: TEST-10481..10485 still current for SPEC-1837. **PASS** ✓
3. Invariant query returns 0 verified-with-no-current-tests for the 9 in-scope specs. **PASS** ✓
4. Post-implementation report documents exact disposition for each of the 9 specs. **PASS** ✓ (see per-spec section above)
5. No `type='governance'` spec appears in untested-verified report. **UNCHANGED** ✓ (hook exclusion not modified)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
