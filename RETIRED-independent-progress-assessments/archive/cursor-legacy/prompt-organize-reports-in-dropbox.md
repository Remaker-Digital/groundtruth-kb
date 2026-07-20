# Prompt: Organize Reports in Dropbox

**Purpose:** Reusable prompt to repeat the activity of organizing `independent-progress-assessments/` so reports live in the dropbox and the knowledge base root stays clean. Use in a future session with minimal loss or regression.

**Location:** `independent-progress-assessments/`.

---

## Prompt (copy block below)

```
Organize independent-progress-assessments so that reports and supporting research live in the dropbox, and the knowledge base root contains only guides, indexes, and logs.

**Rules:**
1. **Knowledge base root** (`independent-progress-assessments/`) â€” only: CURSOR-WAY-OF-WORKING, CURSOR-LOYAL-OPPOSITION-ROLE, CURSOR-KNOWLEDGE-BASE-INDEX, KNOWLEDGE-MIKE, KNOWLEDGE-PROJECT, LOYAL-OPPOSITION-LOG, EXEC-SUMMARY-REPORT-GUIDE, SESSION-START-PROMPT, and this prompt file.
2. **CURSOR-INSIGHT-DROPBOX** (`independent-progress-assessments/CURSOR-INSIGHT-DROPBOX/`) â€” all reports, supporting research, notes, and session wrap-ups (INSIGHTS-MM-DD-YYYY-HH-mm.md).

**Actions:**
- Move any reports or supporting research from the knowledge base root into CURSOR-INSIGHT-DROPBOX/.
- Update CURSOR-KNOWLEDGE-BASE-INDEX.md so report paths point to CURSOR-INSIGHT-DROPBOX/.
- If HTML reports reference project assets (e.g. logo), use path ../../branding/... when HTML lives in CURSOR-INSIGHT-DROPBOX/.
- If scripts generate PDFs from HTML, ensure paths point to CURSOR-INSIGHT-DROPBOX/.
- Update EXEC-SUMMARY-REPORT-GUIDE.md so it specifies reports go in CURSOR-INSIGHT-DROPBOX/.
- Add a log entry to LOYAL-OPPOSITION-LOG.md for this activity.

**Reference:** CURSOR-INSIGHT-DROPBOX/README.md and CURSOR-KNOWLEDGE-BASE-INDEX.md define the structure.
```

---

*Â© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

