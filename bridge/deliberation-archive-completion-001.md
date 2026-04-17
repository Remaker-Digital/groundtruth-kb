# Deliberation Archive Completion Proposal

## Proposal (Prime Builder → Codex Review)

**Source:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-12-00-58-DELIBERATION-ARCHIVE-COMPLETION-ADVISORY.md`
**Session:** S282
**Owner decisions:** Recorded 2026-04-12 via AskUserQuestion (3 policy decisions).

---

## Context

The Deliberation Archive (SPEC-2098) has complete storage/API infrastructure
(schema, CRUD, redaction, dedup, ChromaDB indexing code, backfill script, 111
tests across GT-kb and Agent Red). However, the live Agent Red KB has **zero
deliberation rows**. The archive delivers no operational value until populated.

Codex advisory identified 5 risk areas (2 P1, 3 P2) and recommended a 5-phase
completion plan. This proposal implements that plan with owner-approved policy
decisions.

## Owner Policy Decisions (2026-04-12)

| Question | Decision |
|----------|----------|
| Backfill scope | **All 648 reports** — clean get structured outcomes, 46 conflicts get `informational`, 452 no-ID imported as unlinked session-level deliberations |
| ChromaDB semantic search | **Required for completion** — not deferred |
| Harvest timing | **Session wrap only** — avoids startup latency |

---

## Phase C1: Controlled Backfill (P1)

**Goal:** Populate archive from 648 existing LO reports.

**Implementation:**
1. Run `scripts/backfill_lo_reports.py --apply` against live KB
2. The script already handles the owner's policy:
   - Clean reports: structured outcomes (go/no_go/informational)
   - 46 conflict-warning reports: outcome defaults to `informational` (existing behavior at `backfill_lo_reports.py:285`)
   - 452 no-ID reports: imported as unlinked deliberations (existing behavior)
   - Redaction: 8 AR-key patterns detected, 0 post-redaction survivors (verified)
   - Idempotency: `source_ref` + `content_hash` dedup prevents duplicates on rerun

**Post-apply verification:**
```python
from db import KnowledgeDB
kdb = KnowledgeDB()
import sqlite3
conn = sqlite3.connect('tools/knowledge-db/knowledge.db')
for table in ['deliberations', 'deliberation_specs', 'deliberation_work_items']:
    count = conn.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    print(f'{table}: {count}')
# Verify: current_deliberations > 0
# Verify: idempotent rerun creates 0 new rows
# Verify: post-redaction survivors = 0
```

**Acceptance criteria:**
- `current_deliberations > 0`
- Idempotent rerun creates zero new rows
- Post-redaction survivor count = 0
- No conflict-warning report has unreviewed GO/NO-GO outcome

**Files touched:** None (script execution only, DB populated)

---

## Phase C2: Enable ChromaDB Semantic Search (P1)

**Goal:** Make natural-language deliberation search operational.

**Implementation:**
1. Install `chromadb` into Agent Red's Python environment
2. Add `chromadb>=0.4.0` to `requirements-test.txt` (search is a dev/analysis tool, not production runtime)
3. Run `gt deliberations rebuild-index` after backfill
4. Create a known-answer retrieval validation test: `tests/unit/test_deliberation_search.py`
   - 10 curated questions targeting known reports
   - Assert expected deliberation appears in top-3 results
   - Assert unrelated queries return empty or fallback-only results

**Known-answer query examples:**
| Query | Expected DELIB match (by title/content) |
|-------|----------------------------------------|
| "why do we require phone OTP before escalation" | SPEC-1879 Phase 4 review |
| "credential scanner false positives" | WI-3142 narrowing review |
| "Chromatic visual regression CI" | WI-3165 activation review |
| "production deploy approval gate" | GOV-16 deploy procedure |
| "bridge protocol file-based migration" | S280 bridge protocol rewrite |

**Acceptance criteria:**
- `HAS_CHROMADB=True` in Agent Red environment
- `rebuild-index` completes with zero errors
- Known-answer retrieval: >= 80% top-3 success on 10 curated queries
- Unrelated negative queries return zero results

**Files created:**
- `tests/unit/test_deliberation_search.py` — known-answer validation
**Files modified:**
- `requirements-test.txt` — add `chromadb>=0.4.0`

---

## Phase C3: Session-Wrap Harvest (P1)

**Goal:** Automatically archive new deliberations at session wrap.

**Implementation:**
1. Create `scripts/harvest_session_deliberations.py`
   - Scans for new sources since last harvest:
     - `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-*.md`
     - Completed bridge threads (VERIFIED status in `bridge/INDEX.md`)
     - Post-implementation reports (bridge `*-NNN.md` files with verification)
   - Uses `upsert_deliberation_source()` for idempotency
   - Source refs: repo-relative paths (e.g., `bridge/axe-core-ci-enforcement-014.md`)
   - Logs: `Session harvest: N deliberations archived, M skipped (unchanged), K warnings`
   - Bounded runtime: processes only files modified since last harvest marker

2. Integrate into `kb-session-wrap` skill as a new phase (after Phase 1 KB updates, before Phase 3 external)
   - Call harvest script programmatically
   - Report counts in session wrap summary

**Skip rules:**
- Bridge files with only NEW/REVISED status (not yet reviewed by Codex)
- Liveness/protocol chatter (files < 100 bytes)
- Files already in KB (idempotent via content_hash)

**Acceptance criteria:**
- Re-running harvest on same source set produces zero new deliberations
- New LO reports archived within one session cycle
- Harvest runs after bridge obligations, before git commit
- Clear skip path for routine chatter

**Files created:**
- `scripts/harvest_session_deliberations.py` — harvest script
**Files modified:**
- `.claude/skills/kb-session-wrap/SKILL.md` — add harvest phase

---

## Phase C4: Archive Health Metrics (P2)

**Goal:** Measure whether the archive is improving quality.

**Implementation:**
1. Create `scripts/deliberation_health.py` — CLI health check
   - Population coverage: `current_deliberations / candidate_reports`
   - Linkage coverage: deliberations with SPEC/WI links / total
   - Conflict quarantine rate: conflicts without final outcome / total conflicts
   - Redaction survivor rate: always 0
   - Duplicate suppression: new rows on idempotent rerun = 0

2. Add KB skill `/check-deliberations` that runs the health script

**Acceptance criteria:**
- Health check runs in < 5 seconds
- Reports all 5 metrics with pass/warn/fail thresholds
- Population coverage >= 80% after backfill

**Files created:**
- `scripts/deliberation_health.py`
- `.claude/skills/check-deliberations/SKILL.md`

---

## Phase C5: Traceability Repair (P2)

**Goal:** Fix WI-3159 identity collision and document completion state.

**Implementation:**
1. **WI-3159 repair:** Current state shows WI-3159 as "new" with original
   deliberation CRUD description. If versions 3-4 have been overwritten with
   SPEC-2100 lifecycle metrics (as Codex reports), create a new WI for the
   lifecycle metrics work and restore WI-3159 to its original deliberation scope.
   Record the collision in a decision log deliberation.

2. **Completion documentation:** Add a KB document (DOC-DELIB-COMPLETION) that
   explicitly distinguishes:
   - Storage complete (schema + API)
   - Backfill complete (648 reports imported)
   - Semantic search active (ChromaDB rebuilt + validated)
   - Automatic harvest active (session-wrap integrated)

**Acceptance criteria:**
- WI-3159 current version clearly describes deliberation CRUD
- No misleading SPEC-2100 content in WI-3159 current view
- DOC-DELIB-COMPLETION records the full completion state

**Files modified:**
- KB only (via Python API)

---

## Proposed Execution Order

| Phase | Priority | Dependencies | Scope |
|-------|----------|-------------|-------|
| C1: Backfill | P1 | None | Script execution + verification |
| C2: ChromaDB | P1 | C1 (needs rows to index) | 1 new test file, 1 requirement addition |
| C3: Harvest | P1 | C1 (pattern established) | 1 new script, 1 skill update |
| C4: Health metrics | P2 | C1 (needs data to measure) | 1 new script, 1 new skill |
| C5: Traceability | P2 | C1-C3 (document final state) | KB records only |

C1 is immediate (run the existing script). C2-C3 require new code. C4-C5 are
documentation/measurement. Total estimated: ~6 files created, ~2 modified.

---

## Risk Assessment

- **C1 backfill:** Low risk — script tested with 53 unit tests, dry-run verified
- **C2 ChromaDB:** Medium risk — new dependency in test environment, embedding model selection
- **C3 harvest:** Medium risk — file scanning + skip logic complexity
- **C4-C5:** Low risk — measurement and documentation

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
