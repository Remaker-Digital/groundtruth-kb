# Loyal Opposition Log — Agent Red Customer Experience

**Purpose:** Running log of Cursor's appraisals, evaluations, and questions (loyal opposition).  
**Location:** `independent-progress-assments/`.  
**Update:** Append new findings each session; update status (open → resolved/deferred) when Mike decides.

**Format per entry:** Date | Area | Finding | Evidence / context | Suggested action | Status

---

## Entries

### 2026-02-01 — Knowledge base and role setup

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Process | Cursor had no persistent knowledge of Mike or of opposition findings across sessions. | Mike's request to build a knowledge base and adopt loyal opposition. | Created CURSOR-WAY-OF-WORKING, CURSOR-LOYAL-OPPOSITION-ROLE, index, KNOWLEDGE-MIKE, KNOWLEDGE-PROJECT, and this log. | Resolved |

---

### 2026-02-01 — Insight dropbox and session wrap-up workflow

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Process | Mike requested a handoff mechanism: Loyal Opposition creates INSIGHTS.md at session end for Lead Builder (Claude) to use while Loyal Opposition is offline. | Mike's instruction to add to knowledge base. | Created CURSOR-INSIGHT-DROPBOX/, README.md; updated CURSOR-LOYAL-OPPOSITION-ROLE.md (§7), CURSOR-KNOWLEDGE-BASE-INDEX.md, SESSION-START-PROMPT.md. | Resolved |
| Process | Mike requested session-specific INSIGHTS files and scope rule for file operations. | Mike's follow-up: INSIGHTS-MM-DD-YYYY-hh:mm format; no create/delete/modify outside independent-progress-assments/ without permission. | Updated all dropbox docs to INSIGHTS-MM-DD-YYYY-HH-mm.md naming; added §8 scope rule to CURSOR-LOYAL-OPPOSITION-ROLE.md; added §5 to index; updated README and SESSION-START-PROMPT. | Resolved |
| Process | Mike requested expanded Executive Summary (5× length) and knowledge base guide for future reports. | Mike's request: same approach/style, 5× length, add report style/coverage to knowledge base for future use. | Created EXEC-SUMMARY-EXPANDED-2026-02-01.md; created EXEC-SUMMARY-REPORT-GUIDE.md (questions, structure, style, sources); updated index. | Resolved |
| Process | Mike requested HTML version of expanded report with visual aids and branding; add instructions to knowledge base. | Mike's request: HTML with graphs, charts, matrices, Mermaid, external links, logo and branding from branding/; Executive Summary always .md + .html. | Created EXEC-SUMMARY-EXPANDED-2026-02-01.html; added §8 HTML Report Requirements to EXEC-SUMMARY-REPORT-GUIDE.md; updated index. | Resolved |
| Process | Mike requested all reports moved to CURSOR-INSIGHT-DROPBOX; use dropbox for reports/supporting research; keep knowledge base root for guides/indexes/logs. | Mike's instruction. | Moved 5 files to CURSOR-INSIGHT-DROPBOX; updated HTML logo path, PDF script, index, README, report guide, role doc, project knowledge. | Resolved |

---

### 2026-02-01 — Seed: risks from existing assessment

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Planning | Admin frontend build (npm/TS/bundle) not validated for admin/shopify and admin/standalone. | CLAUDE.md "Next priority" item (1). | Run `npm install && npm run build` (or equivalent) in both admin shells; fix any failures; document result. | Open |
| Process | Widget bundle not yet copied into Theme App Extension assets. | CLAUDE.md "Next priority" item (2). | Copy built widget IIFE from widget build output to `extensions/agent-red-chat/assets/` and document. | Open |
| Testing | P2 launch-quality tests (~135) not executed. | COMPREHENSIVE-TEST-PLAN.md §6; CLAUDE.md. | Prioritize P2 test implementation/execution before launch. | Open |

---

### 2026-02-01 — Kiro third-party validation of Executive Summary

| Area | Finding | Evidence | Suggested action | Status |
|------|---------|----------|------------------|--------|
| Process | Kiro endorsed EXEC-SUMMARY-EXPANDED-2026-02-01 as substantially accurate (Grade A-). Minor discrepancies: test count (777 vs 930), router count (17 vs 19) attributed to snapshot timing. | Third-Party-Assessment-Validation-Report.html (Kiro); EXEC-SUMMARY-EXPANDED-2026-02-01.md. | Cursor: adopt §10 EXEC-SUMMARY-REPORT-GUIDE (metrics snapshot, source dating, validation-friendly claims, enhancement areas). | Resolved |
| Process | Executive Summary numeric claims (tests, routers, routes) should be sourced and dated so third-party validators know which snapshot was used. | Kiro report "Minor Discrepancies" table. | Added EXEC-SUMMARY-REPORT-GUIDE §10.1 (metrics snapshot, cite source, prefer derive-at-generation-time). | Resolved |
| Process | Validator recommended future reports: (1) specific prioritization of P2/integration work, (2) cloud cost summary if done, (3) technical debt/maintenance note. | Kiro report "Areas Where Assessment Could Be Enhanced". | Added EXEC-SUMMARY-REPORT-GUIDE §10.3 (enhancement areas) and §10.4 (reference to validation report). | Resolved |

---

## How to Add an Entry

1. Add a new row under the latest date block (or start a new date block).
2. Fill: Area (Technical / Process / Product / Commercial), Finding (one sentence), Evidence (doc/code reference), Suggested action (brief), Status (Open / Resolved / Deferred).
3. When Mike resolves or defers an item, change Status in place; optionally add a one-line "Resolution" column or note in the same row.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
