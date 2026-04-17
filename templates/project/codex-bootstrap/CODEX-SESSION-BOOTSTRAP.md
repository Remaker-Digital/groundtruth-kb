# Codex Session Bootstrap - {{PROJECT_NAME}}

This document defines the mandatory startup sequence for every Codex session.
Execute phases A through C in order before beginning any assigned work.

---

## Phase A: File Bridge Sweep

1. **Read the index.** Open `bridge/INDEX.md` if it exists.
2. **Identify actionable entries.** Process document entries whose latest
   status is `NEW` or `REVISED`. Entries are newest-first; historical status
   lines are evidence, not current work.
3. **Review each entry.** Read the referenced bridge document and relevant
   artifacts.
4. **Write the response.** Create the next numbered bridge document and add a
   `GO`, `NO-GO`, or `VERIFIED` line at the top of the document entry in
   `bridge/INDEX.md`.
5. **Report.** Log the result: "File bridge scan: N entries processed."

If `bridge/INDEX.md` is missing, report that the file bridge is not initialized
and continue with Phase B. Do not use the archived SQLite/MCP bridge runtime as
the active queue for new projects.

---

## Phase B: Read Project Documents

Load and internalize the following documents in order:

1. `CLAUDE.md` -- Project rules, governance, and procedures.
2. `MEMORY.md` -- Current project state, versions, recent sessions.
   - MEMORY.md is the operational notepad per ADR-0001: Three-Tier Memory Architecture; canonical knowledge lives in MemBase.
3. `AGENTS.md` -- Loyal Opposition operating contract, if present.
4. `BRIDGE-INVENTORY.md` -- Bridge scripts, prompts, schedules, and recovery.
5. `independent-progress-assessments/LOYAL-OPPOSITION-LOG.md` -- Open items,
   pending decisions, and completed work from prior sessions, if present.

Note any discrepancies between documents. If MEMORY.md and CLAUDE.md conflict,
CLAUDE.md takes precedence (rules over state). Remember: MEMORY.md can coordinate work, but it cannot make anything true.

---

## Phase C: Check for Pending Review Requests

1. Confirm whether any latest `NEW` or `REVISED` entries remain in
   `bridge/INDEX.md`.
2. Check the insight dropbox for reports that reference unresolved items.
3. Prioritize pending bridge review requests over exploratory analysis.

Report your readiness state:

```text
Codex session [session_id] initialized.
- File bridge: [clear/actionable/degraded/not initialized]
- Documents loaded: [count]
- Pending reviews: [count]
- Ready to proceed: [yes/no + reason if no]
```

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
