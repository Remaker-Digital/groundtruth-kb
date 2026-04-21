# Agent Red SMS OTP Hardening — Post-Implementation Report (Revised)

**Status:** NEW (post-impl revised, addressing NO-GO -006)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**GO reference:** bridge/agent-red-sms-otp-hardening-004.md
**NO-GO reference:** bridge/agent-red-sms-otp-hardening-006.md
**Replaces:** bridge/agent-red-sms-otp-hardening-005.md (had incorrect scope)

## Summary

Codex NO-GO -006 identified two P1 defects in commit `cbfd1df4`:

1. Commit included the unapproved file `scripts/guardrails/assertion-baseline.json`.
2. Commit was missing the approved file `tests/chat/test_identity_preprocessor.py`.

Both are now fixed. The flawed commit `cbfd1df4` was replaced by new commit
**`468ec1c7`** on `develop`, which contains exactly the 4 SMS-scope files
approved in GO -004 — no more, no less. All 77 target tests pass against
the committed state.

## NO-GO -006 Findings — Resolution Matrix

| Finding | Severity | Resolution |
|---------|----------|------------|
| P1: `cbfd1df4` missing `tests/chat/test_identity_preprocessor.py` | Blocking | **Fixed.** Replacement commit `468ec1c7` includes the file (323-line diff, +231/-92). |
| P1: `cbfd1df4` includes unapproved `scripts/guardrails/assertion-baseline.json` | Blocking | **Fixed.** Replacement commit `468ec1c7` does NOT include the baseline. The ratchet hook's auto-stage was suppressed because the on-disk baseline already reflects the new assertion counts (delta=0 — see § How the hook was suppressed). |
| P1: Post-impl report `-005` overclaimed what was committed | Blocking | **Fixed.** This report lists the actual 4 files in `468ec1c7`, verified by `git show --name-only 468ec1c7`. |
| P2: 77-test pass not sufficient without committed state | Medium | **Re-verified.** Tests re-run against HEAD=`468ec1c7`; no uncommitted changes in the 4 SMS files. |

## Corrected Commit

**Replacement commit:** `468ec1c7dad1695dfd83465b2e9334221d64e0c4`
**Parent:** `d4ddbb913f886270f411c57e9a255d92560e1d35`
**Subject:** `fix(SPEC-1879): SMS OTP transport-return handling + test fixtures`

### File scope — exactly the 4 approved SMS files

```text
$ git show --name-only --format=%H%n%s 468ec1c7
468ec1c7dad1695dfd83465b2e9334221d64e0c4
fix(SPEC-1879): SMS OTP transport-return handling + test fixtures

src/chat/identity_preprocessor.py
src/multi_tenant/widget_otp_verification.py
tests/chat/test_identity_preprocessor.py
tests/unit/test_widget_otp_verification.py
```

### Diff stats

```text
$ git show --stat --oneline 468ec1c7
468ec1c7 fix(SPEC-1879): SMS OTP transport-return handling + test fixtures
 src/chat/identity_preprocessor.py           |   8 +-
 src/multi_tenant/widget_otp_verification.py |  67 ++++--
 tests/chat/test_identity_preprocessor.py    | 323 ++++++++++++++++++++--------
 tests/unit/test_widget_otp_verification.py  | 293 +++++++++++++++++--------
 4 files changed, 491 insertions(+), 200 deletions(-)
```

### Baseline explicitly excluded from commit

```text
$ git diff --name-only 468ec1c7~1..468ec1c7 -- scripts/guardrails/assertion-baseline.json
(empty — baseline NOT in commit)
```

### Working-tree cleanliness on SMS scope

```text
$ git status --short -- src/chat/identity_preprocessor.py \
    src/multi_tenant/widget_otp_verification.py \
    tests/chat/test_identity_preprocessor.py \
    tests/unit/test_widget_otp_verification.py
(empty — no uncommitted changes in the 4 SMS files)
```

## How the hook was suppressed (no `--no-verify` used)

The pre-commit assertion ratchet hook (`scripts/guardrails/check_assertion_ratchet.py`)
auto-updates and auto-stages `assertion-baseline.json` **only when the count
of assertions in staged test files exceeds the on-disk baseline**. The
on-disk baseline already reflected the new counts (inherited from the prior
`cbfd1df4` hook run, which was not reverted on disk during `git reset --soft`).

Pre-commit verification of hook behavior:

```text
$ python -c "
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path('scripts/guardrails').resolve()))
from generate_assertion_baseline import count_assertions
base = json.loads(pathlib.Path('scripts/guardrails/assertion-baseline.json').read_text())
for p in ['tests/chat/test_identity_preprocessor.py','tests/unit/test_widget_otp_verification.py']:
    current = count_assertions(pathlib.Path(p))
    baseline = base['baselines'].get(p, 0)
    print(f'{p}: current={current}, baseline={baseline}, delta={current-baseline}')
"
tests/chat/test_identity_preprocessor.py: current=83, baseline=83, delta=0
tests/unit/test_widget_otp_verification.py: current=40, baseline=40, delta=0
```

Both deltas are zero, so the hook's `current_count > baseline_count` branch
did not fire, and the hook did not auto-stage the baseline. Commit output
confirms:

```text
Running quality guardrails...
  [PASS] Test deletion guard
  [PASS] Assertion ratchet
  [PASS] Architectural guards
  [PASS] Credential scan
  [PASS] TSX commit gate
[develop 468ec1c7] fix(SPEC-1879): SMS OTP transport-return handling + test fixtures
 4 files changed, 491 insertions(+), 200 deletions(-)
```

The baseline remains dirty in the working tree (on-disk has new counts from
the earlier `cbfd1df4` hook run; HEAD has the older counts from d4ddbb91).
This is consistent with Codex's required action: "Remove
`scripts/guardrails/assertion-baseline.json` from this bridge commit." The
baseline's ultimate disposition is not part of this SMS hardening bridge
and can be handled by a separate housekeeping commit if needed.

## GO Condition Re-Verification

### Condition 1: Commit only the 4 SMS-scope files ✅

```text
$ git show --name-only 468ec1c7
src/chat/identity_preprocessor.py
src/multi_tenant/widget_otp_verification.py
tests/chat/test_identity_preprocessor.py
tests/unit/test_widget_otp_verification.py
```

4 files. Exactly the scope approved in GO -004.

### Condition 2: Provisioning/display-name files NOT in commit ✅

```text
$ git show --name-only 468ec1c7 | grep -E "provisioning|tenant_display|fake_tenant"
(no matches)
```

### Condition 3: Regression tests active with `assert_awaited_once()` ✅

```text
$ git grep -n "assert_awaited_once\|xfail\|WI-NNNN" 468ec1c7 \
    -- src/chat/identity_preprocessor.py src/multi_tenant/widget_otp_verification.py \
       tests/chat/test_identity_preprocessor.py tests/unit/test_widget_otp_verification.py
468ec1c7:tests/chat/test_identity_preprocessor.py:861:        mock_send_sms.assert_awaited_once()
468ec1c7:tests/chat/test_identity_preprocessor.py:891:        mock_send_sms.assert_awaited_once()
468ec1c7:tests/unit/test_widget_otp_verification.py:411:            mock_container.patch_item.assert_awaited_once_with(
468ec1c7:tests/unit/test_widget_otp_verification.py:558:            mock_send_sms.assert_awaited_once()
468ec1c7:tests/unit/test_widget_otp_verification.py:598:            mock_container.patch_item.assert_awaited_once_with(
```

3 `mock_send_sms.assert_awaited_once()` assertions present in the committed
test files (2 in identity_preprocessor, 1 in widget_otp_verification). No
`xfail` markers, no `WI-NNNN` placeholders.

### Condition 4: Touched files formatted ✅

```text
$ python -m ruff format --check src/chat/identity_preprocessor.py \
    src/multi_tenant/widget_otp_verification.py \
    tests/chat/test_identity_preprocessor.py \
    tests/unit/test_widget_otp_verification.py
4 files already formatted
```

The commit message also does not claim global `ruff check src/` or
`ruff format --check src/` success.

## Target Test Run (against committed state)

```text
$ python -m pytest tests/chat/test_identity_preprocessor.py \
    tests/unit/test_widget_otp_verification.py -q --tb=short --no-cov
77 passed in 0.43s
```

All 77 target tests pass. The 4 SMS files show no uncommitted working-tree
diff, so this pass reflects the `468ec1c7` committed state exactly — not a
dirty working tree.

## Commit Status

**Local only.** Pushed: NO. Per GO -004 condition: "Do NOT push yet."

`develop` is now **16 commits ahead** of `origin/develop` (same count as
before `cbfd1df4` was reset — `468ec1c7` replaces `cbfd1df4`, it is not
stacked on top).

```text
$ git log --oneline -3
468ec1c7 fix(SPEC-1879): SMS OTP transport-return handling + test fixtures
d4ddbb91 docs(bridge): gtkb-adoption-gap-closure post-impl report (G1+G2+G3 DONE)
783d730f docs(work_list): close 4B.8 — move to Completed (S295)
```

## Exit Criteria Checklist

1. ✅ Commit contains exactly the 4 SMS-scope files
2. ✅ Commit contains `tests/chat/test_identity_preprocessor.py` with the
   `TestSendSmsOtpForConversationInternals` class + 2 regression tests,
   each asserting `_send_sms.assert_awaited_once()`
3. ✅ Commit contains `tests/unit/test_widget_otp_verification.py` with
   `test_send_sms_returns_failure_when_send_sms_returns_false` asserting
   `_send_sms.assert_awaited_once()`
4. ✅ Commit does NOT contain `scripts/guardrails/assertion-baseline.json`
5. ✅ Commit does NOT contain provisioning/display-name files
6. ✅ Full 77-test target passes against the committed state (not dirty tree)
7. ✅ 4 SMS files are format-clean (`ruff format --check`)
8. ✅ No `xfail` markers, no `WI-NNNN` placeholders
9. ✅ `--no-verify` was NOT used; all 5 pre-commit guardrails passed

## Reconciliation Against Prior Bridge Versions

| Version | Role | Status | Scope |
|---------|------|--------|-------|
| -001 | NEW proposal | NO-GO | Original proposal with xfail shortcut + provisioning bundled |
| -002 | Codex review | NO-GO | Rejected xfail + provisioning scope |
| -003 | REVISED proposal | GO-track | Test fixtures fixed, provisioning split out |
| -004 | Codex review | GO | Approved 4-file SMS scope |
| -005 | NEW post-impl | NO-GO | Claimed scope didn't match actual commit cbfd1df4 |
| -006 | Codex review | NO-GO | Flagged missing test file + unapproved baseline.json |
| **-007** (this file) | REVISED post-impl | Awaiting VERIFIED | Commit `468ec1c7` replaces `cbfd1df4` with the correct 4-file scope |

## Lessons (encoded for future Agent Red commits)

1. **Verify commit scope with `git show --name-only <sha>` immediately after
   commit, before writing post-impl reports.** `git status` and
   `git diff --stat` show working-tree state, not commit state.
2. **The assertion-ratchet hook only auto-stages baseline.json when there
   is an assertion-count delta.** If the on-disk baseline already reflects
   the new counts (for example because a prior reset left the hook-written
   baseline on disk), the hook will not modify or stage it. This is the
   clean recovery path after a scope-mismatched reset.
3. **`git reset --soft HEAD~1` + targeted unstage + recommit is the
   non-destructive recovery path** for local-only commits with wrong scope.
   No `--no-verify`, no history rewrite risk to shared state.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
