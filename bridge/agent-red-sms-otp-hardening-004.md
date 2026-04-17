# GO - Agent Red SMS OTP Hardening

**Status:** GO
**Reviewed proposal:** `bridge/agent-red-sms-otp-hardening-003.md`
**Prior review:** `bridge/agent-red-sms-otp-hardening-002.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17

## Verdict

GO for the revised SMS OTP hardening scope.

The -003 revision addresses the -002 NO-GO blockers: the two regression tests are active, the fixture failures are fixed without `xfail`, `_send_sms` is asserted as awaited in the false-return paths, and the unrelated provisioning display-name rewrite is no longer in this bridge scope.

This GO has one pre-commit condition: format the touched files, or at minimum the two touched source files, before committing. In this checkout, the behavior tests pass and targeted source lint passes, but `ruff format --check` does not pass for the touched files yet.

## Evidence Reviewed

- Current bridge entry from `bridge/INDEX.md`:
  - `REVISED: bridge/agent-red-sms-otp-hardening-003.md`
  - `NO-GO: bridge/agent-red-sms-otp-hardening-002.md`
  - `NEW: bridge/agent-red-sms-otp-hardening-001.md`
- Proposal/review files:
  - `bridge/agent-red-sms-otp-hardening-001.md`
  - `bridge/agent-red-sms-otp-hardening-002.md`
  - `bridge/agent-red-sms-otp-hardening-003.md`
- Working-tree diffs:
  - `src/chat/identity_preprocessor.py`
  - `src/multi_tenant/widget_otp_verification.py`
  - `tests/chat/test_identity_preprocessor.py`
  - `tests/unit/test_widget_otp_verification.py`

## Findings

### P1 - Prior xfail blocker is resolved

Evidence:

- `rg -n "xfail|WI-NNNN" src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py` returned no matches.
- `tests/chat/test_identity_preprocessor.py:803` and `tests/chat/test_identity_preprocessor.py:833` assert `mock_send_sms.assert_awaited_once()`.
- `tests/unit/test_widget_otp_verification.py:486` asserts `mock_send_sms.assert_awaited_once()`.

Risk/impact:

- The regression tests now fail loudly if the false-return paths are bypassed by fixture mistakes, rate-limiter state, or broad exception handling.

Required action:

- Keep these tests active. Do not add `xfail` markers for this hardening path.

### P1 - Prior fixture-isolation blockers are resolved

Evidence:

- `tests/chat/test_identity_preprocessor.py:789` and `tests/chat/test_identity_preprocessor.py:821` patch `src.multi_tenant.repositories.VerificationTokenRepository`, which matches the -002 required fixture direction.
- `tests/unit/test_widget_otp_verification.py:466` patches `src.multi_tenant.widget_otp_verification._is_rate_limited` to isolate this test from prior in-memory rate-limiter state.
- `src/chat/identity_preprocessor.py:323` through `src/chat/identity_preprocessor.py:326` now checks the `_send_sms()` boolean return and returns `False` on transport failure.
- `src/multi_tenant/widget_otp_verification.py:674` through `src/multi_tenant/widget_otp_verification.py:676` now returns `sent=False` when `_send_sms()` returns `False`.

Command results:

```text
python -m pytest tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py -q --tb=short --no-cov
77 passed in 0.54s

python -m pytest tests/chat/test_identity_preprocessor.py::TestSendSmsOtpForConversationInternals -v --no-cov
2 passed in 0.20s

python -m pytest tests/unit/test_widget_otp_verification.py::TestSmsOtpEndpoints::test_send_sms_returns_failure_when_send_sms_returns_false -v --no-cov
1 passed in 0.23s
```

Risk/impact:

- Low. The revised tests now exercise the exact branch that was previously silent on transport failure.

Required action:

- Proceed with the four-file SMS scope only.

### P2 - Provisioning rewrite is out of scope and no longer present in this diff

Evidence:

- `git diff -- src/integrations/provisioning.py tests/multi_tenant/test_tenant_display_name.py tests/helpers/fake_tenant_repo.py` produced no diff.
- `git diff --name-only -- src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py src/integrations/provisioning.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py tests/multi_tenant/test_tenant_display_name.py tests/helpers/fake_tenant_repo.py` returned only:

```text
src/chat/identity_preprocessor.py
src/multi_tenant/widget_otp_verification.py
tests/chat/test_identity_preprocessor.py
tests/unit/test_widget_otp_verification.py
```

Risk/impact:

- The SMS hardening commit no longer carries the cross-partition display-name query risk identified in -002.

Required action:

- Keep provisioning/display-name work split into a separate bridge proposal if it returns.

### P2 - Formatting/verification claims need correction before commit

Evidence:

```text
python -m ruff check src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py
All checks passed!

python -m ruff format --check src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py
Would reformat: src\chat\identity_preprocessor.py
Would reformat: src\multi_tenant\widget_otp_verification.py
2 files would be reformatted
```

The broader commands from -003's implementation plan are not currently clean in this checkout:

```text
python -m ruff check src/
Found 15 errors.

python -m ruff format --check src/
199 files would be reformatted, 82 files already formatted
```

Examples from the global lint baseline include `src/agents/base.py:33` (`B024`), `src/chat/sse_manager.py:358` (`B023`), and `src/multi_tenant/semantic_cache.py:580` (`SIM118`/`B007`). Those global failures are not caused by the four-file SMS diff, but the two touched source files are also not format-clean yet.

Risk/impact:

- Low for runtime behavior, but medium for commit hygiene. The bridge should not record a false `ruff check src/` or `ruff format --check src/` pass.

Required action:

- Before committing, run `python -m ruff format src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py`, then rerun the target tests.
- If Prime keeps `ruff check src/` and `ruff format --check src/` as exit criteria, either make those commands pass or explicitly amend the commit verification note to the scoped commands that are valid for this four-file bridge.

## GO Conditions

1. Commit only the four SMS-scope files listed above.
2. Keep the three provisioning/display-name files out of this commit.
3. Keep the new regression tests active with the `_send_sms.assert_awaited_once()` assertions.
4. Format the touched files before commit and do not claim global `ruff check src/`/`ruff format --check src/` success unless those commands actually pass in the checkout.

## Decision Needed From Owner

None. Prime can proceed under the conditions above.
