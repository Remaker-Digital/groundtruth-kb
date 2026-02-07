# Cursor Knowledge Base Index — Agent Red Customer Experience

**Purpose:** Index of Cursor's independent knowledge base in this directory. Enables Cursor (and Mike) to see what exists and how to update it across sessions.  
**Location:** `independent-progress-assments/`.  
**Update:** When new artifacts are added or the update convention changes.

---

## 1. Contents of This Directory

| Artifact | Purpose |
|----------|---------|
| **CURSOR-WAY-OF-WORKING.md** | Style, approach, persona extracted from CLAUDE.md. How Cursor works with Mike. |
| **CURSOR-LOYAL-OPPOSITION-ROLE.md** | Definition of the loyal opposition role: scope, tone, how findings are recorded. |
| **CURSOR-KNOWLEDGE-BASE-INDEX.md** | This file. Index and update convention. |
| **KNOWLEDGE-MIKE.md** | Inferences about Mike: preferences, decision patterns, priorities. Improve over time. |
| **KNOWLEDGE-PROJECT.md** | Project-specific knowledge: key risks, open decisions, areas needing re-check. |
| **LOYAL-OPPOSITION-LOG.md** | Running log of opposition findings: date, area, finding, suggested action, status. |
| **EXEC-SUMMARY-REPORT-GUIDE.md** | Guide for creating Executive Summary reports: required questions, structure, style, data sources. Use when producing brief or expanded executive summaries. |
| **SESSION-START-PROMPT.md** | Reusable prompt to start a fresh session with Cursor in Loyal Opposition role. Copy block into new chat. |
| **PROMPT-ORGANIZE-REPORTS-IN-DROPBOX.md** | Reusable prompt to repeat the organize-reports-in-dropbox activity. Copy block when re-running this organization. |
| **CURSOR-INSIGHT-DROPBOX/** | Directory for reports, supporting research, INSIGHTS wrap-ups, and other artifacts. Consumed by Lead Builder when Loyal Opposition is offline. |
| **CURSOR-INSIGHT-DROPBOX/README.md** | Explains dropbox purpose, contents, and workflow. |
| **CURSOR-INSIGHT-DROPBOX/INSIGHTS-MM-DD-YYYY-HH-mm.md** | Session-specific wrap-up. Created when Mike says "wrap up." |
| **CURSOR-INSIGHT-DROPBOX/EXEC-SUMMARY-EXPANDED-2026-02-01.md** | Expanded executive summary (5× brief). |
| **CURSOR-INSIGHT-DROPBOX/EXEC-SUMMARY-EXPANDED-2026-02-01.html** | HTML version with branding, visual aids, ARR forecast. |
| **CURSOR-INSIGHT-DROPBOX/EXEC-SUMMARY-EXPANDED-2026-02-01.pdf** | PDF version. Generate via `node scripts/generate-exec-summary-pdf.mjs`. |
| **CURSOR-INSIGHT-DROPBOX/EXEC-SUMMARY-SUPPORTING-RESEARCH.md** | Supporting data for executive summary. |
| **CURSOR-INSIGHT-DROPBOX/ARR-FORECAST-ANALYSIS-2026-02-01.md** | ARR targets ($350K–$10M): customer counts, gross profit, time-to-reach. |
| **CURSOR-INSIGHT-DROPBOX/LAUNCH-READINESS-REPORT-2026-02-06.md** | Pre-GA launch readiness report: architecture, implementation, usability, compliance, cost; strengths and weaknesses; evidence-based. |
| **Third-Party-Assessment-Validation-Report.html** (project root) | Kiro’s validation of EXEC-SUMMARY-EXPANDED-2026-02-01; methodology and improvement guidance in EXEC-SUMMARY-REPORT-GUIDE §10. |

---

## 2. Update Convention

- **Every session (when working with Mike):**
  - Read `CURSOR-WAY-OF-WORKING.md` and `CURSOR-LOYAL-OPPOSITION-ROLE.md` to align style and role.
  - If new opposition findings: add entries to `LOYAL-OPPOSITION-LOG.md`; if a finding reflects a recurring risk or open decision, add or update `KNOWLEDGE-PROJECT.md`.
  - If new reliable inferences about Mike (preferences, how he decided something): add or update `KNOWLEDGE-MIKE.md`.

- **When CLAUDE.md working-style section changes:**
  - Update `CURSOR-WAY-OF-WORKING.md` so it stays in sync with CLAUDE.md.

- **When Mike clarifies the loyal opposition role (scope, tone, format):**
  - Update `CURSOR-LOYAL-OPPOSITION-ROLE.md` and, if needed, this index.

- **Append-only where it helps:** The opposition log is append-only for history; status (open/resolved/deferred) is updated in place. KNOWLEDGE-MIKE and KNOWLEDGE-PROJECT are living documents; revise or append as needed.

---

## 3. How to Use This Base at Session Start

1. Read **CURSOR-WAY-OF-WORKING.md** (and optionally **CURSOR-LOYAL-OPPOSITION-ROLE.md**).
2. Skim **KNOWLEDGE-MIKE.md** and **KNOWLEDGE-PROJECT.md** for current context.
3. Skim the most recent entries in **LOYAL-OPPOSITION-LOG.md** for open items.
4. Proceed with the highest-priority technical work item per CLAUDE.md, one item at a time, applying the way of working and raising opposition where relevant.

## 4. Session Wrap-Up (for Lead Builder Handoff)

- **When:** Mike asks "Is it a good time to end?" → Loyal Opposition agrees → Mike says "wrap up."
- **Action:** Create a **new** session-specific file **CURSOR-INSIGHT-DROPBOX/INSIGHTS-MM-DD-YYYY-HH-mm.md** (e.g. `INSIGHTS-02-01-2026-14:35.md`) with all relevant work from the session.
- **Purpose:** Lead Builder (Claude) consumes the latest INSIGHTS file when Loyal Opposition is offline.

## 5. Scope of File Operations

- **Within `independent-progress-assments/`:** Loyal Opposition may create, add, or modify documents at discretion; no explicit permission required.
- **Outside `independent-progress-assments/`:** Do **not** create, delete, or modify documents without explicit permission from Mike.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
