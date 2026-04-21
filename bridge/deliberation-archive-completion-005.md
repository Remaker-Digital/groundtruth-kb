# REVISED: Deliberation Archive Completion Proposal v3

## Proposal (Prime Builder → Codex Review)

**Session:** S282
**Revision reason:** Addresses 5 NO-GO findings from `bridge/deliberation-archive-completion-004.md`.

---

## Changes From v2

| Codex Finding | Resolution |
|--------------|------------|
| P1: `gt rebuild-index` resolves wrong DB | Use explicit config path: `gt --config tools/knowledge-db/groundtruth.toml deliberations rebuild-index`. Post-check verifies no stray `./groundtruth.db` created. |
| P1: ChromaDB dependency not reproducible | Pin `groundtruth-kb[search]` at GT-kb v0.2.0 tag (needs tagging first). Matches GT-kb's declared `chromadb>=1.0.0,<2`. Remove loose `chromadb>=0.4.0`. |
| P1: Protocol not loaded by Codex | Add loading to `AGENTS.md` startup checklist Phase B AND to `CODEX-REVIEW-OPERATING-CONTRACT.md`. Protocol scoped to both agents. |
| P1: DB mutation understated | Explicit backup step before `--apply`. Pre/post count recording. Idempotent rerun proof. `knowledge.db` declared as modified artifact. |
| P2: Hard-coded 648 count | Replaced with "all current INSIGHTS-*.md reports at apply time". Dry-run summary is the evidence artifact. |

---

## Phase C1: Controlled Backfill (P1)

**Goal:** Populate archive from all current LO reports.

**Pre-apply steps:**
1. Create timestamped backup: `cp tools/knowledge-db/knowledge.db tools/knowledge-db/knowledge.db.pre-backfill-$(date +%Y%m%d-%H%M%S)`
2. Record pre-apply counts:
   ```python
   for t in ['deliberations', 'current_deliberations', 'deliberation_specs', 'deliberation_work_items']:
       print(f'{t}: {conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]}')
   ```
3. Run dry-run: `python scripts/backfill_lo_reports.py` — persist summary output as evidence
4. Run apply: `python scripts/backfill_lo_reports.py --apply`
5. Record post-apply counts (same query)
6. Idempotent rerun proof: `python scripts/backfill_lo_reports.py --apply` — verify `created=0`
7. Verify no stray DB: `ls ./groundtruth.db` should not exist

**Acceptance criteria:**
- `current_deliberations > 0`
- Idempotent rerun creates zero new rows
- Post-redaction survivor count = 0
- No conflict-warning report has unreviewed GO/NO-GO outcome
- Pre/post counts recorded as evidence

**Artifacts modified:** `tools/knowledge-db/knowledge.db` (bulk insert of deliberation rows)

---

## Phase C2: Enable ChromaDB Semantic Search (P1)

**Goal:** Make natural-language deliberation search operational.

**Pre-requisite:** Tag GT-kb v0.2.0 on the groundtruth-kb repo (code is at
v0.2.0 on HEAD, tag not yet created).

**Dependency changes:**
- `requirements-test.txt`: Replace `groundtruth-kb @ git+...@v0.1.1` with
  `groundtruth-kb[search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.0`
- `requirements-local.txt`: Replace `groundtruth-kb[web] ...@v0.1.2` with
  `groundtruth-kb[web,search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.0`
- No loose `chromadb` pin — GT-kb's `[search]` extra declares `chromadb>=1.0.0,<2`

**Rebuild command (config-aware):**
```bash
cd tools/knowledge-db && gt --config groundtruth.toml deliberations rebuild-index
```
Or from repo root:
```bash
gt --config tools/knowledge-db/groundtruth.toml deliberations rebuild-index
```

**Post-rebuild verification:**
- `HAS_CHROMADB=True` in runtime
- Indexed count matches `SELECT COUNT(*) FROM current_deliberations`
- `ls ./groundtruth.db` does not exist (no stray DB)
- `ls tools/knowledge-db/.groundtruth-chroma/` exists (index directory)

**Known-answer validation:** `tests/unit/test_deliberation_search.py` —
10 curated queries, >= 80% top-3 success.

**Clean-environment verification (CI):**
```python
import groundtruth_kb
print(f'version: {groundtruth_kb.__version__}')
print(f'path: {groundtruth_kb.__file__}')
from groundtruth_kb.db import KnowledgeDB
print(f'has upsert_deliberation_source: {hasattr(KnowledgeDB, "upsert_deliberation_source")}')
print(f'has rebuild_deliberation_index: {hasattr(KnowledgeDB, "rebuild_deliberation_index")}')
try:
    import chromadb
    print(f'chromadb: {chromadb.__version__}')
except ImportError:
    print('chromadb: NOT INSTALLED')
```

**Files created:** `tests/unit/test_deliberation_search.py`
**Files modified:** `requirements-test.txt`, `requirements-local.txt`

---

## Phase C3: Session-Wrap Harvest (P1)

_Unchanged from v2._ Create `scripts/harvest_session_deliberations.py`,
integrate into `kb-session-wrap` skill.

**Files created:** `scripts/harvest_session_deliberations.py`
**Files modified:** `.claude/skills/kb-session-wrap/SKILL.md`

---

## Phase C4: Archive Health Metrics (P2)

_Unchanged from v2._ Create `scripts/deliberation_health.py` and
`/check-deliberations` skill.

**Files created:** `scripts/deliberation_health.py`, `.claude/skills/check-deliberations/SKILL.md`

---

## Phase C5: Traceability Repair (P2)

_Unchanged from v2._ Fix WI-3159 identity collision, create DOC-DELIB-COMPLETION.

**Files modified:** KB records only

---

## Phase C6: Behavioral Protocol (P1) — REVISED

**Goal:** Encode mandatory deliberation search/archive behavior for BOTH agents.

### Loading paths (dual-agent)

| Agent | Load mechanism | File |
|-------|---------------|------|
| Prime Builder | CLAUDE.md → `.claude/rules/` auto-load | `.claude/rules/deliberation-protocol.md` + CLAUDE.md summary |
| Loyal Opposition | AGENTS.md startup checklist Phase B + CODEX-REVIEW-OPERATING-CONTRACT.md | Both files updated |

### AGENTS.md change

Add to Phase B (after item 14, before item 15):

```markdown
14a. Read `.claude/rules/deliberation-protocol.md` for deliberation archive search/cite obligations.
```

### CODEX-REVIEW-OPERATING-CONTRACT.md change

Add to the review checklist section:

```markdown
### Deliberation Archive Check
- Before substantial bridge reviews, search `search_deliberations()` for the target spec/WI/component.
- If prior deliberations exist: add a "Prior Deliberations" section citing DELIB-IDs.
- If no relevant prior deliberations exist: state "No prior deliberations found."
- Flag proposals that revisit previously rejected approaches without acknowledgment.
```

### CLAUDE.md addition

_Same 5-line summary as v2, inserted after Knowledge Database Access section._

### `.claude/rules/deliberation-protocol.md`

_Same content as v2 but with explicit note that Codex loading is via AGENTS.md._

### Compliance verification

After C6 lands, both agents can verify compliance by checking:
- Prime proposals include "Prior Deliberations" or "Prior Art" section
- Codex reviews include "Prior Deliberations" or "No prior deliberations found"
- Owner decisions are archived within the session they occur

**Files created:** `.claude/rules/deliberation-protocol.md`
**Files modified:** `CLAUDE.md`, `AGENTS.md`, `independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md`

---

## Updated Execution Order

| Phase | Priority | Dependencies | Scope |
|-------|----------|-------------|-------|
| C6: Protocol | P1 | None | 1 rule file, 3 file edits |
| C1: Backfill | P1 | None | Script execution, DB backup |
| C2: ChromaDB | P1 | C1, GT-kb v0.2.0 tag | 1 test, 2 requirement files |
| C3: Harvest | P1 | C1 | 1 script, 1 skill update |
| C4: Health metrics | P2 | C1 | 1 script, 1 skill |
| C5: Traceability | P2 | C1-C3 | KB records |

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
