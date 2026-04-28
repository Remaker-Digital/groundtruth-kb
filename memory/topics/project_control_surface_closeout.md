---
name: Control surface closeout plan (S253-S254+)
description: 5-phase plan for widget/chat hardening — Phase 0+1 done, Phase 2 next. Locked owner decisions included.
type: project
---

## Control Surface Closeout Plan

Originated S253 from Codex advisory review of comprehensive widget/chat improvement proposal. Codex corrected phase ordering to respect the widget hard-gate operating model (release_pipeline.py Class C).

| Phase | Focus | Status |
|-------|-------|--------|
| 0 | Scope correction / verified baseline | DONE (S253) |
| 1 | Release-path widget proof, retry/idempotency, Critic isolation, transport hardening | DONE (S253, committed S254 as 3ab6d630) |
| 2 | Widget-local tests, bundle/locale, accessibility AA | DONE (S254-S255, committed 974fbaa4) |
| 3 | Quality persistence/activation, dashboards/alerts, UX polish | Pending |
| 4 | Operational telemetry, abuse controls, documentation | Pending |

## Owner Decisions Locked (S253)

- **Re-baseline:** approved
- **Stream-then-validate:** confirmed (SSE replay approach)
- **Fail-closed:** confirmed (Critic gate blocks on unavailability)
- **WCAG 2.1 AA:** confirmed (accessibility target)
- **Release gate:** unconditional (no Class C bypass)
- **Idempotency:** Cosmos conditional write (etag/if-match)
- **Breaker health:** count semantics (open_breaker_count + total_breakers)
- **Admin auth:** single assessment, Phase 2 implementation
- **Fan-out:** include in Phase 1 (asyncio.Condition)
- **In-flight turns:** enforce single in-flight per conversation

## Key Codex Findings That Shaped This Plan

1. Widget is already a hard deployment gate — canary/proof work can't wait
2. Not zero-state — backend emits structured SSE errors, axe a11y addon exists, browser live tests exist
3. Idempotency before retry UI — retry without duplicate suppression corrupts transcripts
4. Phase ordering must respect the accepted operating model (release gate first, then enhancements)

**Why:** This plan governs all remaining control-surface work. Phases must be completed in order. Each phase should be committed, deployed to staging, tested, then production-deployed before starting the next.

**How to apply:** At session start, check which phase is current. Implement only within that phase's scope. Do not skip ahead or combine phases without owner approval.
