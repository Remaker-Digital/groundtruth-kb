---
name: Plan-of-Record Production Readiness
description: Active 16-step plan — production at v1.98.92, Step 14 blocked on carrier, Step 16 post-production spec hygiene
type: project
originSessionId: 160d795c-d357-4b8e-823c-683de1fb010a
---
Plan-of-Record (DOC-POR-001) for Agent Red production readiness and post-deploy hygiene.

**Status:** ACTIVE — Steps 1-13, 14B, 15 COMPLETE. Production at v1.98.92 (S276). Step 14 blocked on toll-free carrier. Step 16 (spec hygiene) PENDING post-production.

**16-Step Sequence:**
1-9. COMPLETE — all SPEC-1879 phases Codex GO, CI fixes.
10. COMPLETE — pre-chat error rendering (already implemented in Phase 3).
11. COMPLETE — escalation budget tests (S271, commit `189e4dc1`).
12. COMPLETE — v1.98.91 rebuilt, staging deploy, widget smoke PASS.
13. COMPLETE — toll-free `+18772178051` purchased, ACS_SMS_FROM set on staging + production. Carrier verification submitted (Application 346df3eb, 2026-04-09).
14. BLOCKED — E2E phone OTP smoke test (blocked by toll-free carrier approval; passive monitor `acs-tollfree-sms-verification-check` runs 09:15/21:15 local).
14B. COMPLETE — production recovery validated (1 tenant, all env vars, encryption ready).
15. COMPLETE — production deploy (v1.98.92, S276, GOV-16 APPROVED).
16. PENDING — **Spec hygiene remediation** (post-production, non-blocking). Scope: close 118 untested specs (22 verified-but-untested track VERIFIED S291; 90 implemented-untested deferred pending methodology review of Phase 1.5 artifact; 6 specified-untested expected) + 10,440 orphan tests of 11,066 total (94.3%, WI-3171). Five phases: 16.A promote verified remediation statuses; 16.B methodology review; 16.C P0b phantom-evidence audit (509 specs, deferred S292); 16.D orphan test rationalization (largest); 16.E exit verification. Rationale: external due diligence requires clean traceability; ambient backlog risks gap growth without forcing function.

**Remaining blockers:**
1. Step 14 — Toll-free SMS carrier verification approval (Application 346df3eb)
2. Step 16.B — Methodology review of Phase 1.5 audit artifact (deferred S292)

**Graceful degradation note:** Phone OTP degrades to bypass if SMS not working — same as v1.98.89. Production is operational.

**Full plan:** `docs/plans/PLAN-OF-RECORD-production-readiness.md`
