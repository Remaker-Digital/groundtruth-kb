---
name: production-release-plan-v2
description: 6-phase commercial production readiness plan (Phase 0-6), approved 2026-04-06. ZK is hard gate. Codex CONDITIONAL NO-GO findings incorporated.
type: project
---

Owner approved the Commercial Production Readiness Plan v2 on 2026-04-06 (S262).

**Why:** Agent Red cannot accept paying customers until Zero-Knowledge Architecture is operationally enforced. Plan incorporates Codex Loyal Opposition CONDITIONAL NO-GO findings (5 findings, all acknowledged).

**How to apply:** Execute phases in order. Phases 4-6 parallel after Phase 3.

## Phase sequence
- **Phase 0 (Preconditions):** Revert SPEC-1843 to specified, fix 20 assertion regressions (db.py shim grep targets), scope ADR-004 WIs, triage WI-3040..3054 pipeline duplicates.
- **Phase 1 (Stabilize Staging):** Fix P0 WIs, unique pipeline failures, UI polish. Gate: pre-flight PASS.
- **Phase 2 (Zero-Knowledge):** Pillar ordering 3+4 first, then 1, then 2. Plus ADR-004 canonical identity. Gate: ZK verification suite PASS.
- **Phase 3 (Production Deploy):** Gate: GOV-16 owner GO.
- **Phase 4 (Shopify App Store):** GDPR webhooks, listing finalization. Parallel with Phase 5.
- **Phase 5 (Testing Hardening):** Quality score >= 90, load test, security audit. Parallel with Phase 4.
- **Phase 6 (Marketing):** Lead with "Cryptographically Private by Design." Competitive targets: Gorgias, Tidio.

## Key owner decisions (S262)
- ZK is a HARD GATE — no paying customers without it
- Primary competitive targets: Shopify ecosystem (Gorgias, Tidio)
- Plan approved 2026-04-06

Full plan: `.claude/plans/vast-stargazing-kurzweil.md`
