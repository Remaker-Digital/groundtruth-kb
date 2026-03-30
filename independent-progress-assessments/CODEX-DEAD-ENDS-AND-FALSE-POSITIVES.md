# Codex Dead Ends And False Positives - Agent Red Customer Engagement

Purpose: preserve failed approaches, avoidable errors, and false positives so future review sessions do not repeat them.

## Recording Rules

- Record only reusable lessons.
- Focus on why the miss happened and how to prevent it.
- Prefer concrete verification rules over vague cautions.

## Entries

### 2026-03-17 - False positive on MEMORY.md absence

- issue:
  A prior audit incorrectly treated `memory/MEMORY.md` as missing from the workspace.
- why it happened:
  The check stopped at repo-local paths and did not verify Claude's auto-memory resolution path under the user-local `.claude/projects/.../memory/` directory.
- prevention rule:
  For any claim about Claude-resolved memory or session artifacts, verify both:
  1. repo-local path
  2. user-local Claude path
- source:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-17-18-09.md`

### 2026-03-17 - Audit signal fragmentation across overlapping files

- issue:
  One audit session produced overlapping findings across multiple files, which increased reconciliation work for Prime Builder.
- why it happened:
  There was no hard rule enforcing one canonical report per session.
- prevention rule:
  Produce one canonical `INSIGHTS-YYYY-MM-DD-HH-mm.md` file per session.
  Use appendices only for raw evidence or supporting material.
- source:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-17-18-09.md`

### 2026-03-25 - Review recommendations should separate immediate controls from optional later hardening

- issue:
  Large recommendation sets can mix immediate high-value changes with longer-term optimizations, which makes implementation ordering less clear.
- why it happened:
  Review output focused on completeness before sequencing.
- prevention rule:
  Separate:
  1. immediate role-shaping controls
  2. optional later hardening
  so the owner can approve a tighter first tranche.
- source:
  Codex configuration review session, 2026-03-25.

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
