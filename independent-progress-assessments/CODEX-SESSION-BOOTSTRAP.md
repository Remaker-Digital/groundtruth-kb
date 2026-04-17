# Codex Session Bootstrap - Agent Red Customer Engagement

Purpose: one short startup file that makes Codex session behavior deterministic after restart.

## What To Expect On Restart

These changes take effect automatically when Codex starts in this workspace and reads `AGENTS.md`:

- Codex is review-first by default.
- Prime-requested reviews are Codex's standing top-priority task.
- Prime/Codex coordination uses the file bridge in `bridge/`.
- Proposal review, code review, and alternatives investigation are the primary work modes.
- The Codex review contract, checklists, and templates are part of the expected startup context.

These changes now activate automatically when `AGENTS.md` declares Loyal Opposition mode:

- non-mutating review-mode hook behavior

Optional local environment overrides remain available:

- force read-only behavior:
  - `LOYAL_OPPOSITION_READONLY=1`
  - `CODEX_REVIEW_MODE=1`
- temporarily allow builder-style hook behavior during an explicitly approved implementation session:
  - `LOYAL_OPPOSITION_READONLY=0`
  - `CODEX_REVIEW_MODE=0`

## Recommended Review-Session Startup

**Phase A — File bridge scan (first priority):**
1. Read `bridge/INDEX.md`.
2. Identify document entries whose latest status is `NEW` or `REVISED`.
3. Process actionable entries from oldest to newest using `.claude/rules/file-bridge-protocol.md`.
4. Report scan count: "File bridge scan: N entries processed."

**Phase B — Local bootstrap (after bridge obligations are clear):**
5. Start Codex in this workspace:
   `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
6. Review-mode hooks should auto-activate from `AGENTS.md`. Only set an environment flag if you need to force or override the detected mode.
7. Confirm Codex loads:
   - `AGENTS.md`
   - `independent-progress-assessments/CODEX-STANDING-PRIORITIES.md`
   - `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
   - `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md`
   - `independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md`
   - `independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md`
8. For substantial work, use:
   - `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`
   - `independent-progress-assessments/TEMPLATE-CODE-REVIEW.md`
   - `independent-progress-assessments/TEMPLATE-DECISION-MEMO.md`

## Quick Restart Prompt

Use this at the start of a new Codex session if needed:

```text
Start in the Agent Red Codex review role. Load AGENTS.md, independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md, independent-progress-assessments/CODEX-STANDING-PRIORITIES.md, independent-progress-assessments/CODEX-WAY-OF-WORKING.md, independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md, independent-progress-assessments/CODEX-LOYAL-OPPOSITION-RUNBOOK.md, and independent-progress-assessments/CODEX-KNOWLEDGE-BASE-INDEX.md. Prime-requested reviews are Codex's standing top priority. Use bridge/INDEX.md as the file-bridge review queue. Default to proposal review, code review, and alternatives investigation unless I explicitly ask for implementation.
```

## Read-Only Review Mode Behavior

When Loyal Opposition review mode is active, the local hook behavior should:

- skip scheduler mutation
- skip assertion-run pruning
- read session handoff without consuming it

## Boundary

- The `.claude/` skills and hook changes are local-only because `.claude/` is git-ignored in this repo.
- The tracked baseline for intended setup lives in `config/agent-control/`.

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

