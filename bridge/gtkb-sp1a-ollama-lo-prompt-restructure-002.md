WITHDRAWN

# Withdrawn: SP-1a — Ollama LO Prompt Restructure

**bridge_kind:** advisory (withdrawn)
**Withdrawn by:** Loyal Opposition (Goose E, session-scoped LO override)
**Date:** 2026-06-08
**Supersedes:** `gtkb-sp1a-ollama-lo-prompt-restructure-001.md` (preserved as historical audit trail)

## Withdrawal Rationale

Role-boundary violation. Per `.claude/rules/file-bridge-protocol.md` §Advisory Reports,
LO-authored advisory entries must be **non-dispatchable Axis-2 investigation reports** — they cite
findings, evidence, and recommendations, but do **not** include implementation `target_paths`,
`Recommended Implementation Scope` sections, or acceptance tests that presuppose Prime Builder
filing mechanics.

The `-001.md` filing crossed into Prime Builder territory by prescribing a specific implementation
restructure of `scripts/ollama_harness.py:build_system_prompt()`. This is an implementation proposal
masquerading as an advisory, authored by the wrong role.

## Owner Decision / Evidence

**Decision:** Owner (Mike, 2026-06-08 11:28) directed option 2 —
> "Convert to NEW implementation proposals for Prime — Withdraw the advisories and queue them for
> Prime Builder to file as formal NEW proposals with proper work-intent claims and spec linkage."

## Disposition

- Investigation findings (F1: preflight-as-blocking, F2: claim-before-write timing) preserved in
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-08-SP1-DISPATCH-FIX-INVESTIGATION.md`
- Scope transferred to owner-directed handoff: `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md`
- Prime Builder should refile as a NEW implementation proposal with proper work-intent claim,
  `Specification Links`, `Requirement Sufficiency` subsection, and preflight verification.

## Related Artifacts

- Sibling withdrawals: `gtkb-sp1b-dispatch-outcome-tracker-002.md`, `gtkb-sp1c-author-meets-reviewer-guard-002.md`, `gtkb-sp1d-turn-budget-optimization-002.md`
- Handoff directive: `bridge/gtkb-sp1-dispatch-reliability-prime-handoff-001.md`
