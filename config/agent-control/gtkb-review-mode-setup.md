# Review Mode Setup

Purpose: define the intended low-risk operating posture for Codex review and investigation sessions.

## Review Mode Goals

- analysis-first
- no hidden state mutation
- evidence-heavy output
- additive artifacts by default

## Review-Mode Activation

In this workspace, review mode is auto-detected from `AGENTS.md` when the Loyal Opposition contract is active.

Optional explicit overrides:

- force read-only review mode:
  - `LOYAL_OPPOSITION_READONLY=1`
  - `CODEX_REVIEW_MODE=1`
- temporarily allow builder-style hook behavior during an explicitly approved implementation session:
  - `LOYAL_OPPOSITION_READONLY=0`
  - `CODEX_REVIEW_MODE=0`

## Expected Effect

When the local hooks support review mode, the active mode should:

- disable stateful scheduler rewrites
- disable session-prompt consumption
- disable assertion-run pruning
- preserve read-only context gathering

## Session Start (Two-Phase)

**Phase A — File bridge scan (first priority):**
1. Read current TAFE/dispatcher bridge state and the status-bearing numbered
   files under `bridge/`.
2. Process bridge threads whose latest status is `NEW` or `REVISED`.
3. Write review results as the next numbered bridge file and publish the
   resulting `GO`, `NO-GO`, or `VERIFIED` status through the governed bridge
   path.

**Phase B — Local bootstrap (after bridge obligations are clear):**
4. `AGENTS.md`
5. `.claude/rules/codex-way-of-working.md`
6. `.claude/rules/codex-review-operating-contract.md`
7. `.claude/rules/codex-loyal-opposition-runbook.md`
8. `.claude/rules/codex-knowledge-base-index.md`

## Deliverables

Use:

- `.claude/rules/template-code-review.md`
- `.claude/rules/template-decision-memo.md`
- Advisory Proposal bridge entries / Deliberation Archive records
  (`independent-progress-assessments/` is retired; do not write there)

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
