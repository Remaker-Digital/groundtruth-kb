# Agent Red SMS OTP Hardening — Revised (Tests Fixed + Scope Split)

**Status:** REVISED (addressing NO-GO -002 findings)
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Session:** S297
**Bridge thread:** agent-red-sms-otp-hardening
**Prior versions:** -001 (NEW), -002 (NO-GO)

## NO-GO -002 Findings Addressed

| Finding | Severity | Resolution |
|---------|----------|------------|
| P1: Proposed xfail would suppress regression tests for the hardening | High | **DROPPED.** Both tests now PASS via proper fixture fixes. No xfail markers added. |
| P1: Identity-preprocessor test needs narrower fixture fix | High | Applied: patch `VerificationTokenRepository` class directly (matches widget OTP pattern), drop cosmos_client patching in favor of repository-level patching |
| P1: Widget OTP test rate-limiter isolation | High | Applied: patch `_is_rate_limited` directly so prior-test rate-limiter state doesn't interfere |
| P2: Provisioning rewrite out of scope | Medium | **SPLIT.** Provisioning changes reverted to HEAD for this bridge. Will be handled separately with proper cross-partition-query justification. |
| Process: Use real WI id, not WI-NNNN | — | No WI created in this revision. Both tests pass cleanly; no tracking WI needed. |

## Prior Deliberations

- `DELIB-0714` (16.C phase complete) — cited for context, not blocking
- SPEC-1879 track (phone identity channel) — bridge precedent
- No prior DELIB on SMS OTP hardening beyond this thread

## Revised Scope (4 files, down from 7)

| File | Change |
|------|--------|
| `src/chat/identity_preprocessor.py` | Handle `_send_sms()` returning False (was silently ignored) |
| `src/multi_tenant/widget_otp_verification.py` | Same fix + returns informative error response |
| `tests/chat/test_identity_preprocessor.py` | +81 lines: 2 new tests with proper fixtures (both PASS) |
| `tests/unit/test_widget_otp_verification.py` | +47 lines: rate-limiter isolated fixture (test PASSES) |

**Dropped from scope** (split to separate future bridge):
- `src/integrations/provisioning.py` (cross-partition display_name query rewrite)
- `tests/multi_tenant/test_tenant_display_name.py`
- `tests/helpers/fake_tenant_repo.py`

All 3 provisioning files reverted to HEAD.

## Test Fix Details (addressing P1-A and P1-B)

### Test 1: `test_returns_true_when_send_sms_succeeds` + `test_returns_false_when_send_sms_returns_false`

**Original failure**: patching `src.multi_tenant.cosmos_client.get_cosmos_manager`
did not intercept `VerificationTokenRepository`'s module-level import of the
same name (already bound at import time).

**Fix applied**:
- Patch `src.multi_tenant.repositories.VerificationTokenRepository` with a
  `mock_token_repo` return value (matches the widget OTP tests' pattern)
- Both `delete_token` and `create_token` are AsyncMock stubs on the fake repo
- The code path never creates a real `VerificationTokenRepository`, so the
  internal `get_cosmos_manager` call never happens
- Added `mock_send_sms.assert_awaited_once()` to prevent the test from passing
  via an earlier broad-exception return path

### Test 2: `test_send_sms_returns_failure_when_send_sms_returns_false`

**Original failure**: `_is_rate_limited` fires on shared in-memory state from
prior tests before the mocked `_send_sms` is reached.

**Fix applied**:
- Patch `src.multi_tenant.widget_otp_verification._is_rate_limited` → returns
  False directly (this test is not about rate limiting)
- Added `mock_send_sms.assert_awaited_once()` to prevent rate-limiter or
  broad-exception early return from silently "passing" the test

## Verification (all commands PASS)

```text
$ python -m pytest tests/chat/test_identity_preprocessor.py \
    tests/unit/test_widget_otp_verification.py \
    -q --tb=short --no-cov
77 passed in 0.45s

$ python -m pytest tests/chat/test_identity_preprocessor.py::TestSendSmsOtpForConversationInternals \
    -v --no-cov
2 passed in 0.24s

$ python -m pytest \
    tests/unit/test_widget_otp_verification.py::TestSmsOtpEndpoints::test_send_sms_returns_failure_when_send_sms_returns_false \
    -v --no-cov
1 passed in 0.22s
```

**Target test run** (all 77 tests touched by this commit): **77 passed, 0 failed, 0 xfail.**

(Note: NO-GO -002 cited 93 tests because the original scope included the
3 provisioning-related files. Revised scope is 77 tests since those files
are no longer in this commit.)

## Implementation Plan

1. Run `ruff check src/` and `ruff format --check src/` — verify clean
2. Stage the 4 files only (no provisioning files)
3. Commit with message `fix(SPEC-1879): SMS OTP transport-return handling + test fixtures`
4. Do NOT push yet (15 unpushed develop commits are a separate CTO-prep concern;
   this commit just lands locally)

## Exit Criteria

1. Single commit touches exactly 4 files (2 src + 2 tests)
2. Full 77-test target passes with 0 failed, 0 xfail
3. Both new `assert_awaited_once()` assertions fire on the mocked `_send_sms`
4. `ruff check src/` clean, `ruff format --check src/` clean
5. No WI-NNNN placeholders; no provisioning files in commit

## Risks

- **Low**: test fixture pattern matches established widget OTP precedent
- **Low**: production code changes are minimal (5 lines + 4 lines)
- **Low**: no tests are muted; if future regression breaks the transport-return
  handling, both new tests would fail loudly
- **Medium**: 15 unpushed develop commits remain a separate CTO-prep concern;
  not addressed by this bridge

## What's Deferred (separate future bridge)

The provisioning display-name query rewrite (`src/integrations/provisioning.py`)
needs its own proposal with:
- Justification for cross-partition `STARTSWITH` query against the repository
  contract (auth-time-only, indexed fields)
- Tenant-isolation analysis (the new query reads across tenants)
- Query-cost comparison (current N+1 vs proposed single-query)
- Co-author: likely the same work should be a SPEC-level review, not just a
  bridge proposal

Scope for that future work: 3 files (provisioning.py + 2 test files) +
fake_tenant_repo.py helper.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
