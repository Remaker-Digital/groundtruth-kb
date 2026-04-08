# Plan-of-Record v3: Agent Red Production Readiness

**Status:** PLAN-OF-RECORD (default resume target after interrupts)
**Created:** S270 (2026-04-08)
**Version:** 3 — revised to include verification gaps discovered during implementation
**Owner approval:** Pending
**Codex review:** Pending (v3 rewrite)
**Spec refs:** SPEC-1879, GOV-16, GOV-17
**Target:** v1.98.91 production-ready build

---

## Goal

Bring Agent Red from current production (v1.98.89, stable, no phone/SMS features)
to a production-ready v1.98.91 that includes SPEC-1879 Phases 1-4 (phone identity
channel) with all known defects resolved, CI green, staging verified end-to-end,
and owner approval per GOV-16.

## Current State (post Steps 1-7)

| Component | Status | Commit |
|-----------|--------|--------|
| Phase 1 (groundwork) | Codex GO | S266 |
| Phase 2A (SMS OTP + D1/D2/D3 fixes) | Codex GO | f4b44dde |
| Phase 3 (widget UI + 3 remediation rounds) | Codex GO (P2 follow-up noted) | 7fdff6f3 |
| Phase 4 (escalation gate + 3 P1 fixes) | Codex GO | f4b44dde |
| CI lint | GREEN | 9b9fd35b |
| CI tests | ~40 fixes committed, full count unverified | 578340d8 |
| Shared tier gate | Extracted to tier_utils.py | f4b44dde |
| E.164 regex | Fixed in both extraction paths | f4b44dde |
| ACS SMS provisioning | Unverified in staging AND production | Owner action |

## Completed Steps (1-7)

Steps 1-4 (D1/D2/D3 defect fixes) and Steps 5-6 (Codex GO on all phases) are
complete. Step 7 (CI test fixes) addressed ~40 of ~52 known failures across
4 commits. These steps are retained here for traceability but require no further
action.

---

## Remaining Steps (8-15)

### Step 8: Verify CI test suite passes on develop

**Why:** We fixed ~40 tests locally and pushed to `develop`, but the python-tests
CI workflow only triggers on PRs or pushes to `main`. We have no CI confirmation
that the full 5-shard test suite passes with our changes.
**Action:** Create a draft PR from `develop` → `main` to trigger the python-tests
workflow. Do NOT merge — this is verification only.
**Gate:** All 10 test shards (5 shards × 2 Python versions) must pass, or remaining
failures must be classified as env-dependent and marked skip.

### Step 9: Fix remaining CI failures (if any)

**Why:** Step 8 may reveal failures not caught locally (Ubuntu vs Windows path
differences, missing CI-only fixtures, Python 3.12/3.13 vs local 3.14 differences).
**Action:** Fix and push. Re-run CI until green or only env-dependent skips remain.
**Gate:** CI green or explicitly triaged.

### Step 10: Fix Phase 3 P2 follow-up — pre-chat error rendering

**Why:** Codex's Phase 3 GO noted that `phoneOtpError` is stored on transport
failure but never rendered on the pre-chat form. The customer sees nothing when
SMS send fails — the form just stays loading.
**Files:** `widget/src/components/PreChatForm.tsx` (add error prop),
`widget/src/components/Panel.tsx` (pass phoneOtpError to PreChatForm).
**Gate:** Error message visible on pre-chat form when SMS send fails.

### Step 11: Fix escalation budget test depth (non-blocking but recommended)

**Why:** Codex noted that `execute_with_budget` success path is untested in
escalation tests. The `_make_budget()` fixture uses `MagicMock` which doesn't
exercise the real async budget execution path.
**Files:** `tests/chat/test_escalation_identity_gate.py`
**Gate:** At least one test exercises the awaited budget path without coroutine
warnings.

### Step 12: v1.98.91 build + staging deploy

**Preconditions (all must be met):**
- [x] Phase 1 Codex GO
- [x] Phase 2A Codex GO (D1/D2/D3 fixed, commit f4b44dde)
- [x] Phase 3 Codex GO (3 remediation rounds, commit 7fdff6f3)
- [x] Phase 4 Codex GO (commit f4b44dde)
- [x] CI lint GREEN
- [ ] CI tests GREEN (Step 8-9)
- [ ] Phase 3 P2 follow-up fixed (Step 10)

**Action:** Run `python build.py --version 1.98.91` to build API gateway image.
Deploy to staging via `python deploy.py --env staging`.

### Step 13: ACS SMS provisioning verification (owner + staging)

**Why:** The entire phone/SMS feature depends on Azure Communication Services.
Neither staging nor production has been verified.

**Staging verification (Prime Builder):**
1. Confirm `ACS_SMS_FROM` is set in staging container env
2. Confirm `AZURE_COMM_CONNECTION_STRING` is set in staging Key Vault
3. Attempt SMS send via staging widget (requires a real phone number)

**Production verification (owner action):**
1. Verify `ACS_SMS_FROM` phone number is provisioned and active in Azure portal
2. Verify `AZURE_COMM_CONNECTION_STRING` is set in production Key Vault
3. Confirm SMS sending capability from production ACS resource

**Gate:** At least one SMS successfully received on a real phone from staging.

### Step 14: End-to-end phone OTP smoke test on staging

**Why:** The widget → backend → ACS → phone → OTP verify flow has never been
tested end-to-end. Unit tests verify individual components but not the integrated
path. This is the first time phone OTP will run in a real environment.

**Test plan:**
1. Load widget on staging storefront
2. Enter a phone number in pre-chat form (professional+ tier tenant)
3. Verify widget transitions to phone OTP screen
4. Receive SMS on real phone
5. Enter OTP code in widget
6. Verify conversation starts with phone_verified=true
7. Verify admin inbox shows phone number for the conversation
8. Verify escalation gate accepts the verified phone

**Negative paths:**
- Starter-tier tenant: verify phone field falls through to conversation (no OTP)
- Invalid phone format: verify locale-aware error message
- Wrong OTP code: verify error + retry
- Transport failure simulation: verify error on pre-chat (after Step 10)

**Gate:** All 8 positive test steps pass. At least 2 negative paths verified.

### Step 15: Production deploy (GOV-16 gate)

**Preconditions (all must be met):**
- [ ] CI green (Steps 8-9)
- [ ] Phase 3 P2 fixed (Step 10)
- [ ] v1.98.91 built and deployed to staging (Step 12)
- [ ] ACS SMS verified on staging (Step 13)
- [ ] E2E phone OTP smoke test passed (Step 14)
- [ ] Owner explicit approval (GOV-16)

**Action:**
1. Merge `develop` → `main`
2. Deploy to production via `python deploy.py --env production`
3. Run production smoke test (health, config, conversation create, SSE)
4. Verify production ACS SMS is functional
5. Tag release v1.98.91

**Rollback plan:** If phone OTP fails in production, the feature degrades
gracefully — customers who provide phone numbers will fall through to
conversation without verification (same as v1.98.89 behavior). No data loss.
Rollback to v1.98.89 is available via `python deploy.py --env production --version 1.98.89`.

---

## Resume Protocol

This plan is the **Plan-of-Record**. When returning from interrupting tasks:
1. Check which step was last completed
2. Resume at the next incomplete step
3. Steps 8-9 (CI) can run in parallel with Step 10 (widget fix)
4. Steps 12-14 are sequential (build → verify → smoke test)

**Review isolation rule:** No longer applies — Codex GO received on all phases.
CI fixes and follow-up work can proceed freely on `develop`.

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| CI reveals new failures on Ubuntu/3.12 | Delays build | Fix iteratively, classify env-specific as skip |
| ACS SMS not provisioned | Feature silently broken | Step 13 verification before deploy |
| E2E smoke test fails | Blocks production | Fix and re-test; widget degrades gracefully |
| Phone OTP UX issues in real usage | Customer friction | Staging smoke test catches before production |
| `develop` → `main` merge conflict | Delays deploy | `main` is at v1.98.89, develop ahead by 7 commits, should merge clean |

## Follow-up Debt (post-production, not blocking)

| Item | Source | Priority |
|------|--------|----------|
| Escalation budget success path test | Codex Phase 4 GO | Low |
| Pre-chat form phone error rendering | Codex Phase 3 GO | Medium (promoted to Step 10) |
| Widget-level automated tests for phone path | Codex Phase 3 v2 NO-GO | Medium |
| Python 3.14 local test timeout issue | S270 investigation | Low |

---

*Plan-of-Record v3 for Agent Red production readiness.*
*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
