---
name: Widget/Chat Roadmap Owner Decisions (S253)
description: 4 owner decisions locked for re-baselined widget improvement proposal — stream-then-validate, fail-closed, WCAG AA, re-baseline approved
type: project
---

Owner decisions locked in S253 (2026-04-01) for the widget/chat improvement roadmap:

1. **Re-baseline approved** — reissue proposal with corrected scope per Codex review, not the original 97-WI draft.
   **Why:** Codex found stale facts (source attribution already ships, quality scaffolding exists, replay bug is contract mismatch not buffer expiry). Original WI estimates unreliable.
   **How to apply:** Phase 0 evidence correction before any implementation WIs.

2. **Stream-then-validate confirmed** — keep existing streaming model, add resumable recovery.
   **Why:** Buffer-then-deliver would sacrifice the product's low-latency streaming UX.
   **How to apply:** SSE recovery work = fix replay contract + add idempotency + failed-message UI as last resort. Not a delivery model change.

3. **Fail-closed confirmed** — unvalidated responses must NOT reach customers.
   **Why:** Product trust requires Critic validation. Graduated degradation = safe fallback or human escalation, not unvalidated delivery.
   **How to apply:** Per-tenant breaker isolation is fine, but breaker-open state must return safe fallback, not bypass validation.

4. **WCAG 2.1 AA confirmed** — not AAA.
   **Why:** AAA would require brand color changes (7:1 contrast fails #ff3621), conflicts with SPEC-1711 (proactive notifications) and SPEC-1835 (idle detection). No SaaS chat widget achieves full AAA. AA meets ADA/Section 508/EN 301 549.
   **How to apply:** Scope accessibility work to AA criteria only. AAA items may be cherry-picked as stretch but are not required for release.

Codex review report: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-01-23-29-13-S252-WIDGET-CHAT-PROPOSAL-REVIEW.md`
