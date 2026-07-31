GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: cursor-20260716-lo-auto-process
author_model: Fireworks Kimi K2.7 Code
author_model_version: accounts/fireworks/models/kimi-k2p7-code
author_model_configuration: Cursor Agent interactive Loyal Opposition; ::init gtkb lo; auto-processing loop

# LO Review - WI-5388 Codex Window Monitor Generation Handoff

bridge_kind: loyal_opposition_review
Document: gtkb-wi5388-codex-window-monitor-generation-handoff
Version: 002
Date: 2026-07-16 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5388
Reviewed: bridge/gtkb-wi5388-codex-window-monitor-generation-handoff-001.md

## Verdict

GO.

## Rationale

Preflights passed:
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5388-codex-window-monitor-generation-handoff` → `preflight_passed: true`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5388-codex-window-monitor-generation-handoff` → 0 blocking gaps

The proposal is a bounded, non-impairing rollout of the already-reviewed WI-5368 matcher. It changes only the named mutex generation from v1 to v2 in `scripts/ops/codex_snapshot_window_hider.py` and updates the focused static test, so the scheduled launcher can start a v2 process alongside the still-live v1 process. No process is terminated, suspended, reprioritized, or replaced. After a natural host restart, only v2 returns.

This directly satisfies the owner directive to fix the console-window defect without making any harness less dispatchable.

## Conditions

- Implementation must fail closed unless the exact WI-5368 matcher is present in the committed parent.
- Only the named mutex generation and the focused static test may change; no process lifecycle or dispatch manipulation.
- Implementation report must verify v1/v2 coexistence, idempotence of repeated v2 launches, and that no harness role, eligibility, routing, or dispatchability value changes.
- Independent VERIFIED must precede any mechanical finalization.
