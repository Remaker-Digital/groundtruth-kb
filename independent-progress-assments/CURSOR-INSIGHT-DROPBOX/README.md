# Cursor Insight Dropbox — Agent Red Customer Experience

**Purpose:** Directory for all reports, supporting research, notes, and artifacts produced by Loyal Opposition (Cursor). Consumed by Lead Builder (Claude) when Loyal Opposition is offline.  
**Location:** `independent-progress-assments/CURSOR-INSIGHT-DROPBOX/`.

---

## Contents

### Session wrap-ups
| File | Purpose |
|------|---------|
| **INSIGHTS-MM-DD-YYYY-HH-mm.md** | Session-specific wrap-up. Example: `INSIGHTS-02-01-2026-14:35.md`. Created when Mike says "wrap up." |

### Reports and supporting research
| File | Purpose |
|------|---------|
| **EXEC-SUMMARY-EXPANDED-2026-02-01.md** | Expanded executive summary (5× brief). |
| **EXEC-SUMMARY-EXPANDED-2026-02-01.html** | HTML version with branding, visual aids, ARR forecast. |
| **EXEC-SUMMARY-EXPANDED-2026-02-01.pdf** | PDF version. Generate via `node scripts/generate-exec-summary-pdf.mjs`. |
| **EXEC-SUMMARY-SUPPORTING-RESEARCH.md** | Supporting data for executive summary. |
| **ARR-FORECAST-ANALYSIS-2026-02-01.md** | ARR targets: customer counts, gross profit, time-to-reach. |
| **README.md** | This file. |

**All reports, supporting research, notes, and other artifacts** should be created in this directory.

---

## File Naming

INSIGHTS files are **session-specific**. Format: **INSIGHTS-MM-DD-YYYY-HH-mm.md**

- **MM-DD-YYYY** = date when the report is created (month, day, year)
- **HH-mm** = time when the report is created (24-hour)

Example: `INSIGHTS-02-01-2026-14:35.md` = wrap-up created Feb 1, 2026 at 14:35 (2:35 PM).

---

## Workflow

1. **During session:** Loyal Opposition appraises, evaluates, questions; records findings in LOYAL-OPPOSITION-LOG.md and KNOWLEDGE-PROJECT.md as usual.
2. **Session end:** Mike asks "Is it a good time to end?" → Loyal Opposition agrees or suggests one more item.
3. **Wrap-up:** Mike says "wrap up" → Loyal Opposition creates a **new** INSIGHTS file with current date/time in the name (e.g. `INSIGHTS-02-01-2026-14:35.md`).
4. **Handoff:** Lead Builder (Claude) reads the latest INSIGHTS file when working on the project while Loyal Opposition is offline.

---

## Scope of Operations

- Loyal Opposition may create or add documents in `independent-progress-assments/` (including this dropbox) at discretion; no permission required.
- Loyal Opposition must **not** create, delete, or modify documents **outside** `independent-progress-assments/` without explicit permission from Mike.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
