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

**Phase A — Bridge sweep and Prime handshake (first priority):**
1. Query bridge for pending messages addressed to this agent via `list_inbox(agent=..., status="pending")`.
2. Process or reply to each pending message substantively.
3. Run `python codex_session_prime_handshake.py` to send Prime the required request: `"Report your current operating state"`.
4. Wait for the reply before proceeding with session work.

**Phase B — Local bootstrap (after bridge obligations are clear):**
5. `AGENTS.md`
6. `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
7. `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md`
8. `independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md`
9. `independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md`

## Deliverables

Use:

- `independent-progress-assessments/TEMPLATE-CODE-REVIEW.md`
- `independent-progress-assessments/TEMPLATE-DECISION-MEMO.md`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/`

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
