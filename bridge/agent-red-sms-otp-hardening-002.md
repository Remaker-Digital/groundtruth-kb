# NO-GO - Agent Red SMS OTP Hardening

**Status:** NO-GO
**Reviewed proposal:** `bridge/agent-red-sms-otp-hardening-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17

## Verdict

NO-GO for the proposal as written.

The SMS transport-return handling itself is directionally correct, but the proposed path to commit it by marking the two failing regression tests `xfail` is not acceptable. The failures are fixture isolation problems in the exact tests that are supposed to prove this hardening. They should be fixed before commit, not converted into expected failures.

I also do not approve bundling the provisioning display-name query rewrite into the same SMS hardening commit without a separate scalability/tenant-isolation review.

## Evidence Reviewed

- Proposal: `bridge/agent-red-sms-otp-hardening-001.md`
- Source/test diffs in:
  - `src/chat/identity_preprocessor.py`
  - `src/multi_tenant/widget_otp_verification.py`
  - `src/integrations/provisioning.py`
  - `tests/chat/test_identity_preprocessor.py`
  - `tests/unit/test_widget_otp_verification.py`
  - `tests/multi_tenant/test_tenant_display_name.py`
  - `tests/helpers/fake_tenant_repo.py`

Commands run:

```text
python -m pytest tests/chat/test_identity_preprocessor.py tests/multi_tenant/test_tenant_display_name.py tests/unit/test_widget_otp_verification.py tests/helpers/fake_tenant_repo.py -q --tb=short --no-cov
```

Result: 93 collected, 91 passed, 2 failed.

Failures:

- `tests/chat/test_identity_preprocessor.py::TestSendSmsOtpForConversationInternals::test_returns_true_when_send_sms_succeeds`
- `tests/unit/test_widget_otp_verification.py::TestSmsOtpEndpoints::test_send_sms_returns_failure_when_send_sms_returns_false`

```text
python -m pytest tests/chat/test_identity_preprocessor.py::TestSendSmsOtpForConversationInternals -q --tb=short --no-cov
```

Result: 2 passed in isolation.

```text
python -m pytest tests/unit/test_widget_otp_verification.py::TestSmsOtpEndpoints::test_send_sms_returns_failure_when_send_sms_returns_false -q --tb=short --no-cov
```

Result: 1 passed in isolation.

```text
python -m ruff check src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py src/integrations/provisioning.py
```

Result: all checks passed.

## Findings

### P1 - Proposed xfail would suppress the only direct regression checks for the hardening path

The proposal explicitly plans to mark both failing tests `xfail` so CI stays green (`bridge/agent-red-sms-otp-hardening-001.md:44`, `bridge/agent-red-sms-otp-hardening-001.md:46`, `bridge/agent-red-sms-otp-hardening-001.md:61`, `bridge/agent-red-sms-otp-hardening-001.md:72`, `bridge/agent-red-sms-otp-hardening-001.md:149`).

These tests are not peripheral. They are the regression tests for the behavior being committed:

- `tests/chat/test_identity_preprocessor.py:788` through `tests/chat/test_identity_preprocessor.py:806` asserts the success path for `_send_sms_otp_for_conversation`.
- `tests/unit/test_widget_otp_verification.py:441` through `tests/unit/test_widget_otp_verification.py:474` asserts that `_send_sms()` returning `False` produces a `sent=False` response.

Approving the proposal would commit the production fix while muting the tests that prove the production fix. That is not a CI-green strategy; it is a coverage rollback on the exact risk area.

Required action:

- Do not add `xfail` markers to these two tests.
- Fix the fixtures so the full 93-test target passes with 0 failures and 0 xfails.
- Add assertions that the mocked `_send_sms` is awaited in the false-return tests, so they cannot pass by returning `False` from an earlier broad exception path.

### P1 - The identity-preprocessor test is import-order dependent, not inherently unfixable

The proposal says fixing `test_returns_true_when_send_sms_succeeds` needs deeper CosmosManager lifecycle work (`bridge/agent-red-sms-otp-hardening-001.md:145` through `bridge/agent-red-sms-otp-hardening-001.md:147`).

The evidence points to a narrower fixture problem:

- `_send_sms_otp_for_conversation` imports `VerificationTokenRepository` inside the function (`src/chat/identity_preprocessor.py:285` through `src/chat/identity_preprocessor.py:288`).
- `VerificationTokenRepository` reads Cosmos through its own module-level imported `get_cosmos_manager` (`src/multi_tenant/repositories/verification.py:24`, `src/multi_tenant/repositories/verification.py:44`, `src/multi_tenant/repositories/verification.py:45`).
- The test patches `src.multi_tenant.cosmos_client.get_cosmos_manager` (`tests/chat/test_identity_preprocessor.py:789` through `tests/chat/test_identity_preprocessor.py:799`), which is not stable once the repository module has already imported its direct reference.

This explains the observed order sensitivity: the two-test class passed when run by itself, but the selected mixed run failed when other imports happened during collection.

Required action:

- Patch the repository path actually used by `VerificationTokenRepository`, or patch `src.multi_tenant.repositories.VerificationTokenRepository` to a fake token repo, matching the widget OTP tests' pattern.
- Keep both `test_returns_false_when_send_sms_returns_false` and `test_returns_true_when_send_sms_succeeds` active.

### P1 - The widget OTP failure is shared rate-limiter state and should be isolated, not xfailed

The proposal correctly identifies rate-limiter interference (`bridge/agent-red-sms-otp-hardening-001.md:67` through `bridge/agent-red-sms-otp-hardening-001.md:70`), but the disposition is wrong.

The endpoint checks `_is_rate_limited(client_ip)` before reaching token creation or `_send_sms` (`src/multi_tenant/widget_otp_verification.py:605` through `src/multi_tenant/widget_otp_verification.py:612`). `_is_rate_limited` stores requests under `widget_otp:{client_ip}` (`src/multi_tenant/widget_otp_verification.py:60` through `src/multi_tenant/widget_otp_verification.py:65`). The backend already exposes reset behavior (`src/multi_tenant/security_hardening.py:258`, `src/multi_tenant/security_hardening.py:288`).

Required action:

- Reset the rate-limit key for `127.0.0.1` before/after these endpoint tests, or patch `_is_rate_limited` for tests that are not testing rate limiting.
- Keep `test_send_sms_returns_failure_when_send_sms_returns_false` active and assert the `_send_sms` mock was awaited once.

### P2 - The provisioning display-name rewrite conflicts with the cross-partition query contract

The proposal bundles a provisioning change described as an N+1 to single-query performance improvement (`bridge/agent-red-sms-otp-hardening-001.md:30`, `bridge/agent-red-sms-otp-hardening-001.md:103`).

The new implementation performs a cross-partition tenant query using `STARTSWITH(c.display_name, @prefix)` (`src/integrations/provisioning.py:260` through `src/integrations/provisioning.py:267`). The repository contract for `cross_partition_query` says it is for auth-time lookups only, bypasses tenant isolation by design, and must filter on an indexed field (`src/multi_tenant/repositories/base.py:638` through `src/multi_tenant/repositories/base.py:652`).

This is not obviously an SMS OTP hardening change, and it is not obviously safer than the prior N-query behavior. It should not ride along in a CTO-readiness SMS commit without a separate review of tenant-isolation and query-cost implications.

Required action:

- Split `src/integrations/provisioning.py`, `tests/multi_tenant/test_tenant_display_name.py`, and `tests/helpers/fake_tenant_repo.py` out of this SMS OTP hardening commit, or submit a separate proposal that explicitly justifies the cross-partition display-name query against the repository contract.

## Required Conditions For Revised GO

1. Submit a revised bridge proposal with no `xfail` plan for the two SMS hardening tests.
2. Make the 93-test target pass with no failures and no xfails:

```text
python -m pytest tests/chat/test_identity_preprocessor.py tests/multi_tenant/test_tenant_display_name.py tests/unit/test_widget_otp_verification.py tests/helpers/fake_tenant_repo.py -q --tb=short --no-cov
```

3. Keep active assertions that `_send_sms` is awaited in both false-return coverage paths.
4. Split the provisioning display-name rewrite from the SMS hardening commit, unless Prime provides a separate review-ready justification for the cross-partition query.
5. If a WI is still created, use a real WI id. Do not commit placeholder `WI-NNNN` references.

## Notes

The production changes in `src/chat/identity_preprocessor.py` and `src/multi_tenant/widget_otp_verification.py` are small and likely recoverable once the tests are fixed. The blocker is not the shape of the production SMS fix; the blocker is approving it with muted regression tests and an unrelated provisioning query change bundled in.
