# Plan-of-Record v4: Agent Red Production Readiness

**Status:** PLAN-OF-RECORD (default resume target after interrupts)
**Created:** S270 (2026-04-08)
**Version:** 7 — Step 16 added S295 (spec hygiene remediation, post-production); production operational at v1.98.92 (Step 15 closed S276)
**Owner approval:** GOV-16 APPROVED for production deploy (S276)
**Codex review:** v4 CI GO received (2026-04-09, commit 3c5b6359 all shards green); production deploy validated S276.
**Spec refs:** SPEC-1879, GOV-16, GOV-17
**Target:** v1.98.92 production-ready build (ACHIEVED S276); Step 14 (E2E phone OTP smoke) blocked on toll-free carrier approval; Step 16 (spec hygiene) pending post-production.

---

## Goal

Bring Agent Red from current non-operational production state (v1.98.89, DB reset
in S270, 1 tenant: Remaker Digital) to a production-ready v1.98.91 that includes
SPEC-1879 Phases 1-4 (phone identity channel) with all known defects resolved,
CI green, staging verified end-to-end, and owner approval per GOV-16.

**Two parallel tracks** (per Codex advisory v3):
1. **Release Promotion Track:** CI green, deploy-pipeline evidence, build, staging verify
2. **Production Recovery Track:** Validate single-tenant state, confirm operational baseline

## Current State (post Steps 1-7)

| Component | Status | Commit |
|-----------|--------|--------|
| Phase 1 (groundwork) | Codex GO | S266 |
| Phase 2A (SMS OTP + D1/D2/D3 fixes) | Codex GO | f4b44dde |
| Phase 3 (widget UI + 3 remediation rounds) | Codex GO (P2 follow-up noted) | 7fdff6f3 |
| Phase 4 (escalation gate + 3 P1 fixes) | Codex GO | f4b44dde |
| SPEC-1879 hardening | Codex GO | 2458a440 |
| CI lint | GREEN | 9b9fd35b |
| CI tests | S271: ~50 failures fixed (contact gate, env-markers, deps) | b2335dad |
| Deploy pipeline evidence | S271: all version literals dynamic, 30/30 tests | 6b2e6374 |
| Shared tier gate | Extracted to tier_utils.py | f4b44dde |
| E.164 regex | Fixed in both extraction paths | f4b44dde |
| ACS SMS provisioning | Unverified in staging AND production | Owner action |
| Production state | NON-OPERATIONAL (DB reset S270, 1 tenant) | Owner decision |

## Completed Steps (1-7)

Steps 1-4 (D1/D2/D3 defect fixes) and Steps 5-6 (Codex GO on all phases) are
complete. Step 7 (CI test fixes) addressed ~40 of ~52 known failures across
4 commits. These steps are retained here for traceability but require no further
action.

---

## Remaining Steps (8-16)

### Step 8: Verify CI test suite passes on develop ✅ (S271)

**Completed S271.** Two commits (6b2e6374, b2335dad) addressed:
- Deploy-pipeline evidence: all v1.98.90 literals replaced with _current_version()
- SPEC-1882 contact gate: customer_email added to 36 test fixtures
- 11 env-dependent test files marked `local_env` + CI exclusion
- Pillow added to requirements.txt (qrcode transitive dependency)
- Shopify billing confirm: shop.email extracted from GraphQL query

CI run triggered on b2335dad push. Results pending.

### Step 9: Fix remaining CI failures (if any)

**Status:** ~10 residual failures expected (agent shard: Python version; core shard:
transport mock). Pre-existing, not introduced by SPEC-1879. Classification:
- `test_plugin_dispatch`, `test_agent_app`, `test_base_agent`: pass locally, CI Python version issue
- `test_s175_scaling`: /ready returns 503 without transport (needs fixture)
- `test_s180_provider`, `test_superadmin_diagnostics`, `test_vectorization_scanner`: TBD
**Gate:** Residual failures must be classified. None may be SPEC-1879 regressions.

### Step 10: Fix Phase 3 P2 follow-up — pre-chat error rendering ✅ (already implemented)

**Closed 2026-04-09.** Codex confirmed code was already present on `develop`:
- `widget/src/components/Panel.tsx:428,:532,:939` — sets and passes `phoneOtpError` as `phoneError` prop to PreChatForm
- `widget/src/components/PreChatForm.tsx:49,:157-172` — `phoneError?: string` prop renders conditionally

No further action needed. Negative path smoke test (transport failure → error on pre-chat) is
still required in Step 14 to confirm the rendering at runtime.

### Step 11: Fix escalation budget test depth (non-blocking but recommended) ✅ (already implemented)

**Closed S275.** `TestEscalationBudgetPath` class already exists with 3 tests:
- `test_real_budget_awaits_handler` — real PipelineTimeoutBudget, `assert_awaited_once()`
- `test_real_budget_with_verified_phone` — phone-only identity with real budget
- `test_real_budget_timeout_degrades_gracefully` — 50ms budget, 10s handler, graceful degradation

All 15 tests pass locally (1.82s). Gate satisfied: 3 tests exercise the awaited budget path.

### Step 12: v1.98.91 build + staging deploy

**Preconditions (all must be met):**
- [x] Phase 1 Codex GO
- [x] Phase 2A Codex GO (D1/D2/D3 fixed, commit f4b44dde)
- [x] Phase 3 Codex GO (3 remediation rounds, commit 7fdff6f3)
- [x] Phase 4 Codex GO (commit f4b44dde)
- [x] CI lint GREEN
- [x] CI tests GREEN — 3c5b6359 all shards green, Codex GO 2026-04-09 (Step 8-9)
- [x] Phase 3 P2 follow-up confirmed implemented (Step 10 ✅)

**Action:** Run `python scripts/build.py v1.98.91` to build and push all images.
Deploy to staging via `python scripts/deploy.py staging v1.98.91`.

_Corrected 2026-04-10: Codex advisory INSIGHTS-2026-04-10-00-12-07 — script paths and positional arg signatures updated to match actual repo entrypoints._

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

### Step 14B: Production Recovery Validation (parallel with Steps 12-14)

**Why:** Production is non-operational after the S270 DB reset (encryption incident
remediation). One tenant exists (Remaker Digital, ee7f2360). Before deploying
v1.98.91, we must validate that the production baseline is correct.

**Validation checklist:**
1. Confirm production DB contains exactly 1 tenant (Remaker Digital)
2. Confirm no corrupted/encrypted data remains from the P0 incident
3. Confirm DEK secrets were deleted by owner (S264)
4. Confirm Key Vault access is functional (`AZURE_KEYVAULT_URL` + `MASTER_KEK_KEY_ID`)
5. Confirm production ACS SMS resource is provisioned (overlaps Step 13)

**Gate:** Production baseline validated, or recovery actions documented before deploy.

### Step 15: Production deploy (GOV-16 gate)

**Preconditions (all must be met):**
- [x] CI green (Steps 8-9) — 3c5b6359 Codex GO
- [x] Phase 3 P2 fixed (Step 10) — already implemented, confirmed
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

### Step 16: Spec hygiene remediation (post-production, non-blocking) 🔄 IN PROGRESS — 16.A/16.B/16.C complete; 16.D/16.E remain

**Phase 16.A — COMPLETE (S297).** The 22 verified-but-untested track is closed. Invariant: 0 verified requirement-type specs with 0 non-stale test links (excluding governance specs GOV-14/15/16 and owner-approved exception SPEC-GTKB-SCOPE per S297 decision, archived as DELIB-0711). 4 specs have current passing tests (SPEC-0439/0604/1097/1165); 15 specs reverted to implemented with 7 hygiene WIs (WI-3178–WI-3184) open; 3 governance specs verified by assertion runs; 1 scope-boundary spec excepted by owner.

**Scope:** Close the spec traceability gap identified across S275 and S291:
- **118 untested specs** (Phase 1.5 audit, S291):
  - 22 verified-but-untested — **CLOSED (S297).** S291 bridge work VERIFIED; Step 16.A closure verified with invariant query. 4 verified with tests, 15 reverted to implemented (7 hygiene WIs open), 3 governance (out-of-scope), 1 owner-excepted (SPEC-GTKB-SCOPE).
  - 90 implemented-untested (Phase 1.5 framing) — superseded by Phase 16.B classifier which re-scoped to 193 implemented-untested requirements. **CLOSED (S297).** 16.C four-stream remediation executed; 38 specs remain tracked via hygiene WIs (WI-3185..WI-3218, WI-3221..WI-3224). DELIB-0714 archives results.
  - 6 specified-untested — expected (specifications without implementation yet); no action.
- **10,440 orphan tests of 11,066 total (94.3%)** — tests in the repo that do not link to any spec in the Knowledge DB. Separately tracked as proposed WI-3171 in `bridge/spec-hygiene-untested-verified-*.md`. Scope: for each orphan test, either link to an existing spec, create a new spec for the behavior it covers, or retire the test if it is redundant with an already-covered behavior.

**Preconditions:**
- [x] Step 15 (production deploy) COMPLETE — v1.98.92 deployed 2026-04 (S276), production operational, bridge infrastructure stable (S295).
- [x] Methodology review of Phase 1.5 artifact (S297) — pattern does not generalize; 193-spec scope partitioned into five classifier categories and remediated via four parallel sub-streams. See Phase 16.B/16.C below.

**Action (phased):**
1. **Phase 16.A** — ✅ COMPLETE (S297). Verified-but-untested track closed. Invariant passes with 0 violations. DELIB-0711 archives owner decision.
2. **Phase 16.B** — ✅ COMPLETE (S297). Methodology review VERIFIED (bridge `por-step16b-methodology-review-006`). 193 implemented-untested requirements partitioned into 5 categories (α' 151, β' 4, γ' 19, δ' 15, ζ' 4). Option B (multi-stream remediation) chosen via owner decision DELIB-0713. DELIB-0712 archives the methodology finding.
3. **Phase 16.C** — ✅ COMPLETE (S297). All 4 sub-streams VERIFIED: Stream A (-010, 151 α' refreshed via 122 update_test + 49 insert_test), Stream B (-006, 4 ζ' triaged via 1 WI + 3 relinks/18 fresh TEST IDs), Stream C (-004, 4 β' triaged via 1 relink + 3 WIs), Stream D (-010, 34 γ'+δ' hygiene WIs). Classifier transition: target_count 193 → 38. 38 open hygiene WIs (WI-3185..WI-3218 + WI-3221..WI-3224) track remediation backlog. 0 spec-status mutations. DELIB-0714 archives consolidated results.
4. **Phase 16.D** — Orphan test rationalization (WI-3171): batch-link, batch-retire, or per-test linkage. Expected to be the largest sub-phase (10,440 tests).
5. **Phase 16.E** — Re-run `python tools/knowledge-db/db.py assert` + orphan-test count verification. Exit when untested-spec count ≤ 6 (specified only) and orphan-test count ≤ 100 (sampling tolerance).

**Gate:** Spec traceability matrix is credible for external audit / due diligence (spec count matches implemented behavior; test count matches covered behaviors; no silent coverage gaps).

**Why this is a POR step and not a rolling backlog item:** External due diligence and go-to-market credibility require a clean traceability story. Leaving 118 untested specs and 10,440 orphan tests in ambient MEMORY.md backlog risks the gap growing (new untracked tests, new provisional specs) without a forcing function. Step 16 creates the forcing function.

**Ownership:** Prime Builder drives Phase 16.A–16.C; Phase 16.D (orphan tests) may be delegated to a subagent or scripted where the linkage inference is tractable; Phase 16.E requires owner confirmation that the exit metrics are met.

**Rollback plan:** Spec status changes in the KB are append-only (new version rows); all remediation is reversible via `db.update_spec(... version=N-1)`. Test deletions are git-reversible. No production impact.

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
| Escalation budget success path test | Codex Phase 4 GO | ✅ CLOSED — TestEscalationBudgetPath (3 tests, S275) |
| Pre-chat form phone error rendering | Codex Phase 3 GO | ✅ CLOSED — code already present (Panel.tsx:939, PreChatForm.tsx:157-172) |
| Widget-level automated tests for phone path | Codex Phase 3 v2 NO-GO | Medium |
| Python 3.14 local test timeout issue | S270 investigation | Low |

---

*Plan-of-Record v3 for Agent Red production readiness.*
*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
