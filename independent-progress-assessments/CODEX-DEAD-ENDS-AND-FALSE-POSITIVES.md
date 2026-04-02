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

### 2026-04-01 - GroundTruth packaging work was initially misframed as a PyPI requirement

- issue:
  The GroundTruth closeout analysis initially treated "installable by GitHub users" as if it necessarily meant "publish on PyPI."
- why it happened:
  The review collapsed three different distribution contracts into one:
  1. install from GitHub ref or tag
  2. install from a built release artifact
  3. install from a package index such as PyPI
- prevention rule:
  For packaging and distribution reviews, explicitly identify the intended contract before recommending work.
  Do not assume PyPI unless the owner explicitly requires index-based `pip install <name>` behavior.
- source:
  GroundTruth closeout correction cycle and correction audit, 2026-04-01.

### 2026-04-01 - Bridge dashboards can show stale "pending" state after a thread is already closed

- issue:
  Multiple April 1 review items appeared to remain pending in the conversational status summary even after Codex had already sent the substantive response and resolved the bridge thread.
- why it happened:
  The user-facing summary lagged the bridge record, and later protocol acknowledgements made the stale state look like live work.
- prevention rule:
  Before treating a "pending" item as real, verify the actual bridge thread state and canonical report rather than relying on conversational status text alone.
- source:
  S251 verification and OM advisory-review cycles, 2026-04-01.

---

Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
