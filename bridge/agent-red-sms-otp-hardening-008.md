# VERIFIED - Agent Red SMS OTP Hardening Post-Implementation Verification

**Status:** VERIFIED
**Reviewed report:** `bridge/agent-red-sms-otp-hardening-007.md`
**GO reference:** `bridge/agent-red-sms-otp-hardening-004.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-17

## Verdict

VERIFIED for the current implemented commit on `develop`:
`468ec1c7dad1695dfd83465b2e9334221d64e0c4`.

The implementation at current `HEAD` satisfies the `-004` GO conditions:
the commit contains the four approved SMS-scope files, does not include the
provisioning/display-name files, keeps the `_send_sms.assert_awaited_once()`
regression guards active, and the target tests and format check pass.

Important audit correction: `bridge/agent-red-sms-otp-hardening-007.md`
names `747b438c5f512e6006a95e25e1d8364c5f795c77` as the corrected commit and
describes `scripts/guardrails/assertion-baseline.json` as committed scope.
That is stale relative to the actual branch state verified here. `747b438c`
exists, but it is not an ancestor of current `HEAD`; current `HEAD` is
`468ec1c7` with the same parent and subject, and it contains only the four
approved SMS files. Treat this `-008` verification as the canonical audit
record for the implemented commit.

## Evidence Reviewed

- Bridge history:
  - `bridge/agent-red-sms-otp-hardening-001.md`
  - `bridge/agent-red-sms-otp-hardening-002.md`
  - `bridge/agent-red-sms-otp-hardening-003.md`
  - `bridge/agent-red-sms-otp-hardening-004.md`
  - `bridge/agent-red-sms-otp-hardening-005.md`
  - `bridge/agent-red-sms-otp-hardening-006.md`
  - `bridge/agent-red-sms-otp-hardening-007.md`
- Verified commit:
  - `468ec1c7dad1695dfd83465b2e9334221d64e0c4`
- Files verified:
  - `src/chat/identity_preprocessor.py`
  - `src/multi_tenant/widget_otp_verification.py`
  - `tests/chat/test_identity_preprocessor.py`
  - `tests/unit/test_widget_otp_verification.py`

## Findings

### P1 - Current HEAD satisfies the approved four-file SMS scope

Evidence:

```text
git show --name-only --format='%H%n%P%n%s' HEAD
468ec1c7dad1695dfd83465b2e9334221d64e0c4
d4ddbb913f886270f411c57e9a255d92560e1d35
fix(SPEC-1879): SMS OTP transport-return handling + test fixtures

src/chat/identity_preprocessor.py
src/multi_tenant/widget_otp_verification.py
tests/chat/test_identity_preprocessor.py
tests/unit/test_widget_otp_verification.py
```

```text
git show --stat --oneline --summary HEAD
468ec1c7 fix(SPEC-1879): SMS OTP transport-return handling + test fixtures
 src/chat/identity_preprocessor.py           |   8 +-
 src/multi_tenant/widget_otp_verification.py |  67 ++++--
 tests/chat/test_identity_preprocessor.py    | 323 ++++++++++++++++++++--------
 tests/unit/test_widget_otp_verification.py  | 293 +++++++++++++++++--------
 4 files changed, 491 insertions(+), 200 deletions(-)
```

```text
git show --name-only --format='' HEAD | Select-String -Pattern 'provisioning|tenant_display|fake_tenant'
(no output)
```

Risk/impact:

- Low. The current committed scope matches the `-004` GO file list and keeps
  the provisioning/display-name work out of this bridge.

Required action:

- None for implementation.

### P1 - Regression coverage is committed and active

Evidence:

```text
git grep -n "assert_awaited_once\|xfail\|WI-NNNN" HEAD -- src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py
HEAD:tests/chat/test_identity_preprocessor.py:861:        mock_send_sms.assert_awaited_once()
HEAD:tests/chat/test_identity_preprocessor.py:891:        mock_send_sms.assert_awaited_once()
HEAD:tests/unit/test_widget_otp_verification.py:411:            mock_container.patch_item.assert_awaited_once_with(
HEAD:tests/unit/test_widget_otp_verification.py:558:            mock_send_sms.assert_awaited_once()
HEAD:tests/unit/test_widget_otp_verification.py:598:            mock_container.patch_item.assert_awaited_once_with(
```

No `xfail` or `WI-NNNN` matches were present in the grep output.

Relevant current source/test line references:

- `src/chat/identity_preprocessor.py:324` checks `if not sent:` after the SMS
  transport call.
- `src/multi_tenant/widget_otp_verification.py:692` checks `if not sent:` and
  returns the failure response path.
- `tests/chat/test_identity_preprocessor.py:847` and
  `tests/chat/test_identity_preprocessor.py:879` patch
  `VerificationTokenRepository` directly.
- `tests/chat/test_identity_preprocessor.py:861` and
  `tests/chat/test_identity_preprocessor.py:891` assert the SMS mock was
  awaited.
- `tests/unit/test_widget_otp_verification.py:534` isolates rate limiting, and
  `tests/unit/test_widget_otp_verification.py:558` asserts the SMS mock was
  awaited.

Risk/impact:

- Low. The tests now guard against the earlier silent bypass and fixture
  masking problems identified in `-002`.

Required action:

- Keep these regression assertions active.

### P1 - Target tests and touched-file format check pass

Evidence:

```text
python -m pytest tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py -q --tb=short --no-cov
77 passed in 0.38s
```

```text
python -m ruff format --check src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py
4 files already formatted
```

```text
git status --short -- src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py
(no output)
```

Risk/impact:

- Low. The test and formatting evidence applies to the current committed
  four-file SMS state, not to an uncommitted change in one of those files.

Required action:

- None.

### P2 - Bridge report `-007` is stale on commit identity and baseline scope

Evidence:

```text
git log --oneline --decorate -8
468ec1c7 (HEAD -> develop) fix(SPEC-1879): SMS OTP transport-return handling + test fixtures
d4ddbb91 docs(bridge): gtkb-adoption-gap-closure post-impl report (G1+G2+G3 DONE)
...
```

```text
git merge-base --is-ancestor 747b438c5f512e6006a95e25e1d8364c5f795c77 HEAD
not_ancestor_exit_1
```

```text
git diff 747b438c5f512e6006a95e25e1d8364c5f795c77..468ec1c7dad1695dfd83465b2e9334221d64e0c4 --name-status -- src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py scripts/guardrails/assertion-baseline.json
M	scripts/guardrails/assertion-baseline.json
```

The only difference between the stale `747b438c` report target and current
`HEAD` in the reviewed pathset is the assertion baseline file. Current `HEAD`
does not commit that baseline file in this SMS hardening commit.

There is also an unrelated dirty working-tree modification in
`scripts/guardrails/assertion-baseline.json`:

```text
git status --short -- scripts/guardrails/assertion-baseline.json
 M scripts/guardrails/assertion-baseline.json
```

Risk/impact:

- Medium for audit clarity, low for the implementation. Downstream readers
  should not treat `-007`'s `747b438c` and five-file baseline narrative as the
  verified implementation record.

Required action:

- No implementation action is required for this bridge.
- Use this `-008` verification file, not `-007`, as the canonical record of
  the verified commit and file scope.
- Handle the dirty `scripts/guardrails/assertion-baseline.json` change in a
  separate workstream if it still matters; it is not part of the verified SMS
  hardening commit.

### P3 - Scoped ruff check still reports pre-existing test lint debt

Evidence:

```text
python -m ruff check src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py
Found 18 errors.
```

The reported errors are in `tests/chat/test_identity_preprocessor.py` and are
the same class previously treated as existing lint debt for this bridge
(`I001` import ordering and `UP017` `datetime.UTC` suggestions). The `-004`
blocking condition was touched-file formatting plus accurate verification
language, and the format check passes.

Risk/impact:

- Low for this verification. Do not use this bridge as evidence that scoped
  `ruff check` is clean.

Required action:

- None for SMS OTP verification. Track lint cleanup separately if desired.

## Verification Summary

Verified implementation commit: `468ec1c7dad1695dfd83465b2e9334221d64e0c4`.

The SMS OTP hardening implementation is accepted as complete for the file
bridge. The only caveat is audit hygiene: `-007`'s replacement-commit and
baseline-file narrative is stale, and this `-008` file supersedes it for
verification purposes.
