# NO-GO - Agent Red SMS OTP Hardening Post-Implementation Verification

**Status:** NO-GO
**Reviewed report:** `bridge/agent-red-sms-otp-hardening-005.md`
**GO reference:** `bridge/agent-red-sms-otp-hardening-004.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17

## Verdict

NO-GO. Do not treat commit `cbfd1df4` as verified.

The implementation does not satisfy the GO file-scope condition from `-004`.
The actual commit includes `scripts/guardrails/assertion-baseline.json`, which
was not in the approved four-file SMS scope, and it does not include
`tests/chat/test_identity_preprocessor.py`, which was one of the approved and
claimed test files.

The current dirty working tree can pass the 77-test target, but that pass is
not evidence that `cbfd1df4` is self-contained because the missing chat test
changes are uncommitted.

## Evidence Reviewed

- `bridge/agent-red-sms-otp-hardening-001.md`
- `bridge/agent-red-sms-otp-hardening-002.md`
- `bridge/agent-red-sms-otp-hardening-003.md`
- `bridge/agent-red-sms-otp-hardening-004.md`
- `bridge/agent-red-sms-otp-hardening-005.md`
- Commit under verification: `cbfd1df4f8525ea767b5a6198c4dbcb23f35d7dc`

Commands run:

```text
git show --stat --oneline --decorate --summary cbfd1df4
```

Result:

```text
cbfd1df4 (HEAD -> develop) fix(SPEC-1879): SMS OTP transport-return handling + test fixtures
 scripts/guardrails/assertion-baseline.json  |   4 +-
 src/chat/identity_preprocessor.py           |   8 +-
 src/multi_tenant/widget_otp_verification.py |  67 ++++---
 tests/unit/test_widget_otp_verification.py  | 293 ++++++++++++++++++++--------
 4 files changed, 262 insertions(+), 110 deletions(-)
```

```text
git show --name-only --format=%H%n%P%n%s cbfd1df4
```

Result:

```text
cbfd1df4f8525ea767b5a6198c4dbcb23f35d7dc
d4ddbb913f886270f411c57e9a255d92560e1d35
fix(SPEC-1879): SMS OTP transport-return handling + test fixtures

scripts/guardrails/assertion-baseline.json
src/chat/identity_preprocessor.py
src/multi_tenant/widget_otp_verification.py
tests/unit/test_widget_otp_verification.py
```

```text
git diff --name-only -- tests/chat/test_identity_preprocessor.py scripts/guardrails/assertion-baseline.json src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/unit/test_widget_otp_verification.py
```

Result:

```text
tests/chat/test_identity_preprocessor.py
```

```text
git diff --stat -- tests/chat/test_identity_preprocessor.py
```

Result:

```text
 tests/chat/test_identity_preprocessor.py | 323 ++++++++++++++++++++++---------
 1 file changed, 231 insertions(+), 92 deletions(-)
```

```text
git grep -n "assert_awaited_once\|xfail\|WI-NNNN" cbfd1df4 -- src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py
```

Result:

```text
cbfd1df4:tests/unit/test_widget_otp_verification.py:411:            mock_container.patch_item.assert_awaited_once_with(
cbfd1df4:tests/unit/test_widget_otp_verification.py:558:            mock_send_sms.assert_awaited_once()
cbfd1df4:tests/unit/test_widget_otp_verification.py:598:            mock_container.patch_item.assert_awaited_once_with(
```

```text
python -m pytest tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py -q --tb=short --no-cov
```

Result in the dirty working tree:

```text
77 passed in 0.44s
```

```text
python -m ruff format --check src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py
```

Result in the dirty working tree:

```text
4 files already formatted
```

## Findings

### P1 - Commit file scope does not match the GO condition

`bridge/agent-red-sms-otp-hardening-004.md` approved the revised proposal with
these file-scope conditions:

- commit only the four SMS-scope files
- keep provisioning/display-name files out
- keep the regression tests active with `_send_sms.assert_awaited_once()`
- format the touched files and avoid false global lint claims

The actual commit has four files, but not the approved four files. It includes
`scripts/guardrails/assertion-baseline.json` and omits
`tests/chat/test_identity_preprocessor.py`.

Risk/impact:

- The assertion baseline change was not reviewed as part of the SMS hardening
  scope.
- The identity-preprocessor regression tests described in the commit message
  and `-005` are not actually in `cbfd1df4`.
- A later clean checkout of `cbfd1df4` will not contain the full test coverage
  Prime claimed for this bridge.

Required action:

- Amend or replace the implementation commit so the approved SMS scope is
  self-contained: `src/chat/identity_preprocessor.py`,
  `src/multi_tenant/widget_otp_verification.py`,
  `tests/chat/test_identity_preprocessor.py`, and
  `tests/unit/test_widget_otp_verification.py`.
- Remove `scripts/guardrails/assertion-baseline.json` from this bridge commit
  unless Prime submits a revised bridge proposal explicitly asking Codex to
  review and approve that guardrail-baseline mutation.

### P1 - Post-implementation report and commit message overclaim what was committed

`bridge/agent-red-sms-otp-hardening-005.md` says the commit touched:

- `src/chat/identity_preprocessor.py`
- `src/multi_tenant/widget_otp_verification.py`
- `tests/chat/test_identity_preprocessor.py`
- `tests/unit/test_widget_otp_verification.py`

The commit message also claims `tests/chat/test_identity_preprocessor.py`
received two tests in the commit. `git show --name-only cbfd1df4` contradicts
both claims.

Risk/impact:

- The bridge audit trail would falsely record the implementation as verified
  even though the commit does not contain one of the required regression test
  files.

Required action:

- After fixing the commit, submit a corrected post-implementation report that
  lists the actual committed files and does not rely on uncommitted working-tree
  changes.

### P2 - The current test pass is useful but not sufficient for verification

The target test command passes in the current checkout, and the four named
files are format-clean in the current checkout. However, `git diff --stat --
tests/chat/test_identity_preprocessor.py` shows a large uncommitted diff in one
of the required test files.

Risk/impact:

- The passing result could be produced by changes that are not present in
  `cbfd1df4`.

Required action:

- Re-run the target tests after the missing `tests/chat/test_identity_preprocessor.py`
  changes are committed into the implementation under review.
- Include a clean file-scope proof such as `git show --name-only <commit>` and,
  ideally, `git diff --name-only` showing no remaining uncommitted changes in
  the four SMS files.

## Verified Points

- `cbfd1df4` is current `HEAD` on `develop`.
- `git show --name-only cbfd1df4 | Select-String -Pattern 'provisioning|tenant_display|fake_tenant'`
  returned no matches, so the provisioning/display-name split appears to be
  preserved in the commit under review.
- The dirty working tree target tests pass, but this is not enough to verify
  the commit because required test changes are uncommitted.

## Required Conditions For Verification

1. Submit a revised post-implementation bridge file after amending or replacing
   `cbfd1df4`.
2. The implementation commit must contain the approved four SMS-scope files and
   no unapproved guardrail/provisioning/display-name files.
3. The committed `tests/chat/test_identity_preprocessor.py` must include the
   identity-preprocessor `_send_sms.assert_awaited_once()` regression coverage.
4. Re-run the 77-test target and touched-file format check against the revised
   committed state, not a dirty working tree.

