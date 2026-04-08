# Plan-of-Record: Agent Red Production Readiness

**Status:** PLAN-OF-RECORD (default resume target after interrupts)
**Created:** S270 (2026-04-08)
**Owner approval:** Pending
**Codex review:** v2 (addressing NO-GO findings from v1 review)
**Spec refs:** SPEC-1879, GOV-16, GOV-17
**Target:** v1.98.91 production-ready build

---

## Goal

Bring Agent Red from current production (v1.98.89, stable, no phone/SMS features)
to a production-ready v1.98.91 that includes SPEC-1879 Phases 1-4 (phone identity
channel) with all known defects resolved, Codex GO on every phase, and CI green.

## Current State

| Component | Status | Blockers |
|-----------|--------|----------|
| Phase 1 (groundwork) | Codex GO | None |
| Phase 2A (SMS OTP preprocessor) | Codex NO-GO (3 P1s) | Defects D1-D3 below |
| Phase 3 (widget UI) | Implemented, not reviewed | Depends on Phase 2A |
| Phase 4 (escalation gate) | Codex GO (working-tree scope, msg 92c91bac) | None |
| CI pipeline | ~52 failures | Import errors, env deps, webhook mocks |
| ACS SMS provisioning | Unverified in production | Owner action |

## Defects to Fix

### D1: Dual-state preprocessor blocks second channel (P1)

**Location:** `src/chat/identity_preprocessor.py:422-498` and `:508-589`
**Problem:** When email OTP is pending (`otp_sent_at` set), the email branch
returns early on any non-skip/non-OTP message at line 498, so phone detection
at line 639 never runs. Symmetrically, when SMS is pending, email detection
never runs.
**Root cause:** Each pending-state branch has a catch-all `return IdentityAction(action="none")`
at its end that prevents fall-through to subsequent detection.
**Fix:** After the OTP-code and skip-phrase checks in each pending branch,
add phone/email detection before the final `return`. Specifically:
- In the email-pending branch (lines 422-498): after the OTP check, before the
  final return, attempt phone extraction. If a phone is found, initiate SMS OTP
  (with tier gate) and update the conversation to dual-pending state.
- In the SMS-pending branch (lines 508-589): after the SMS-OTP check, before the
  final return, attempt email extraction. If an email is found, initiate email OTP
  and update the conversation. Email OTP takes precedence per spec.
**Files:** `src/chat/identity_preprocessor.py`
**Tests:** Add 4 tests:
  - email-pending + customer sends phone → SMS OTP sent, both pending
  - sms-pending + customer sends email → email OTP sent, both pending
  - email-pending + customer sends phone (starter tier) → blocked by tier gate
  - both-pending + customer sends 6-digit code → email OTP verified (precedence)

### D2: In-conversation SMS bypasses Professional+ tier gate (P1)

**Location:** `src/chat/identity_preprocessor.py:639-643`
**Problem:** `_send_sms_otp_for_conversation()` is called directly without
checking tenant tier. The widget endpoint (`widget_otp_verification.py:592`)
enforces `_check_tier_gate()` but the preprocessor path does not.
**Fix:** Import and call `_check_tier_gate` (or extract it to a shared location)
before calling `_send_sms_otp_for_conversation`. If the tenant is starter tier,
return `IdentityAction(action="none")` and let the conversation continue without
phone verification.
**Files:** `src/chat/identity_preprocessor.py`, possibly extract
`_check_tier_gate` to `src/multi_tenant/tier_utils.py` for reuse.
**Tests:** Add 2 tests:
  - starter-tier tenant sends phone number → no SMS sent, action=none
  - professional-tier tenant sends phone number → SMS sent, action=phone_received

### D3: Phone extraction regex not strict E.164 (P1)

**Location:** `src/chat/identity_preprocessor.py:44` and
`src/multi_tenant/customer_profile_service.py:76`
**Problem:** `_PHONE_EXTRACT_PATTERN = re.compile(r"(\+[1-9]\d{1,14})")` is
unanchored and greedily matches the first 2-15 digits after `+`. This means:
- `+155512345678901234` → extracts `+155512345678901` (truncated, wrong number)
- `+15551234567abc` → extracts `+15551234567` (valid but strips trailing chars)
**Fix:** Replace unanchored pattern with delimiter-aware extraction that rejects
adjacent word characters (letters, digits, underscore) and adjacent `+`:
1. Change extract pattern to `r"(?<![+\w])(\+[1-9]\d{1,14})(?!\w)"` — rejects
   adjacent alphanumeric context on both sides. This prevents:
   - overlong-digit truncation (`+155512345678901234` → no match, because the
     15-digit prefix `+155512345678901` would have `2` as a trailing word char)
   - trailing-alpha stripping (`+15551234567abc` → no match, `a` is `\w`)
   - embedded-word extraction (`call+15551234567now` → no match, `l` before `+`
     is `\w`, and `+` is in the lookbehind set)
   - double-plus (`++15551234567` → no match, first `+` is in lookbehind set)
2. Post-extraction validation: after extracting, verify the candidate passes
   `_PHONE_STRICT_PATTERN` (full-string E.164 check) as a defense-in-depth
   measure against any future regex regression.
3. Apply the same fix to `customer_profile_service.py:76`.
**Verified:** All 9 test cases pass with this pattern (4 reject, 5 accept).
**Files:** `src/chat/identity_preprocessor.py`, `src/multi_tenant/customer_profile_service.py`
**Tests:** Add 7 tests (5 in preprocessor, 2 in customer_profile_service):
  - overlong digits `+155512345678901234` → no extraction
  - trailing alpha `+15551234567abc` → no extraction
  - embedded in word `call+15551234567now` → no extraction
  - double plus `++15551234567` → no extraction
  - valid E.164 `+15551234567` → extracted correctly
  - valid in sentence `my phone is +15551234567` → extracted correctly
  - valid with punctuation `(+15551234567)` → extracted correctly

---

## Implementation Sequence

All work on `develop` branch.

### Step 1: Extract shared tier gate utility

**Files:** Create `src/multi_tenant/tier_utils.py` (~15 lines), update
`src/multi_tenant/widget_otp_verification.py` to import from it.
**Why first:** D1 and D2 both need the tier gate, and extracting it avoids
duplication between widget and preprocessor paths.
**Tests:** Verify existing widget OTP tests still pass after import change.
**Estimated scope:** ~20 lines changed.

### Step 2: Fix E.164 regex (D3)

**Files:** `src/chat/identity_preprocessor.py` (lines 42-44),
`src/multi_tenant/customer_profile_service.py` (line 76).
**Why second:** This is the simplest fix and has no dependencies. It also
makes D1 safer (phone extraction in pending branches won't accept bad numbers).
**Tests:** 5 new tests in `tests/chat/test_identity_preprocessor.py` +
2 new tests in `tests/unit/test_customer_profile_service.py` (7 total).
**Estimated scope:** ~10 lines changed, ~50 lines of tests.

### Step 3: Add tier gate to preprocessor SMS path (D2)

**Files:** `src/chat/identity_preprocessor.py` (before line 643).
**Why third:** Blocks SMS sending for unauthorized tiers. Must be in place
before D1 adds more SMS-sending paths in the pending branches.
**Tests:** 2 new tests (starter blocked, professional allowed).
**Estimated scope:** ~10 lines changed, ~25 lines of tests.

### Step 4: Fix dual-state preprocessor (D1)

**Files:** `src/chat/identity_preprocessor.py` (lines 496-498 and 587-589).
**Why last:** Most complex change. Requires D2 (tier gate) and D3 (safe regex)
to be in place so the new paths are correct from the start.
**Tests:** 4 new tests for cross-channel detection during pending states.
**Estimated scope:** ~40 lines changed, ~60 lines of tests.

### Step 5: Codex review (Phase 2A re-review)

Send all 4 steps as a single remediation package to Codex for GO/NO-GO.
Include:
- File diffs (git diff from before Step 1)
- Test results (all identity preprocessor + customer profile tests)
- Explicit mapping of each Codex finding to its remediation

### Step 6: Phase 3 Codex review

Phase 3 (widget UI) was implemented in S267 but never sent for Codex review.
After Phase 2A GO, send Phase 3 for review.

### Step 7: CI test fixes (~52 remaining)

Address remaining CI failures in priority order:
1. TIER_PRICING import errors (shared constant moved)
2. Webhook mock shape mismatches
3. Environment-dependent path assertions
4. Pillow dependency (optional, mark tests as skip-if-missing)
**Estimated scope:** ~2 hours of test fixes.

### Step 8: v1.98.91 build + staging deploy

Build only after:
- [x] Phase 1 Codex GO
- [ ] Phase 2A Codex GO (after Steps 1-4)
- [ ] Phase 3 Codex GO
- [x] Phase 4 Codex GO (working-tree remediation GO, msg 92c91bac)
- [ ] CI lint GREEN
- [ ] CI tests GREEN (or only env-dependent skips)

Deploy to staging. Run widget smoke test. Verify SMS OTP flow end-to-end
(requires ACS SMS provisioning on staging).

### Step 9: ACS SMS production verification (owner action)

Owner must verify in Azure portal:
- `ACS_SMS_FROM` phone number is provisioned and active
- `AZURE_COMM_CONNECTION_STRING` is set in production Key Vault
- SMS sending works from production ACS resource

### Step 10: Production deploy (GOV-16 gate)

Deploy to production only after:
- All Codex GOs received
- Staging smoke passed
- ACS SMS verified
- Owner explicit approval (GOV-16)

---

## Resume Protocol

This plan is the **Plan-of-Record**. When returning from interrupting tasks:
1. Check which step was last completed
2. Resume at the next incomplete step

**Review isolation rule:** Do NOT begin Step 7 (CI fixes) on `develop` until
the Phase 2A re-review (Step 5) is adjudicated. CI fixes would contaminate the
scoped remediation diff and make the Codex review noisier. If blocked waiting
for Codex, surface the block to the owner rather than mixing unrelated work
into the review surface.

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Codex finds new defects in remediation | Delays build | Fix-and-resubmit cycle |
| ACS SMS not provisioned in prod | SMS fails silently | Step 9 owner verification |
| CI fixes reveal product defects | Scope expansion | Record as WIs, triage separately |
| Dual-state adds complexity | Future maintenance | Keep state machine well-documented |

---

*Plan-of-Record for Agent Red production readiness.*
*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
