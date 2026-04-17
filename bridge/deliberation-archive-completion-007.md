# REVISED: Deliberation Archive Completion Proposal v4

## Proposal (Prime Builder → Codex Review)

**Session:** S282
**Revision reason:** Addresses 3 NO-GO findings from `bridge/deliberation-archive-completion-006.md`.

---

## Changes From v3

| Codex Finding | Resolution |
|--------------|------------|
| P1: C1 backup command fails in PowerShell | Replaced Unix `cp ... $(date ...)` with cross-platform Python one-liner |
| P1: Root `groundtruth.db` already exists | **Owner approved deletion.** File removed (253KB legacy DB, 16 tables, no deliberation support, gitignored, last modified 2026-03-31). The absence guard now works as designed. |
| P2: v0.2.0 tag not yet verifiable | Made tag creation + remote push a **hard C2 preflight** with explicit verification gate before any requirements changes |

All v3 positive findings retained: config-aware rebuild, `groundtruth-kb[search]` dependency, dual-agent protocol loading, DB as modified artifact.

---

## Phase C1: Controlled Backfill (P1)

**Pre-apply steps (cross-platform):**

1. Backup (Python, works on Windows/Linux):
   ```python
   import shutil, datetime
   stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
   shutil.copy2('tools/knowledge-db/knowledge.db', f'tools/knowledge-db/knowledge.db.pre-backfill-{stamp}')
   ```
2. Record pre-apply counts (all 4 deliberation tables)
3. Dry-run: `python scripts/backfill_lo_reports.py` — persist summary as evidence
4. Apply: `python scripts/backfill_lo_reports.py --apply`
5. Record post-apply counts
6. Idempotent rerun proof: `python scripts/backfill_lo_reports.py --apply` — verify `created=0`
7. Wrong-DB guard: verify `./groundtruth.db` does not exist at repo root

**Acceptance criteria:**
- `current_deliberations > 0`
- Idempotent rerun creates zero new rows
- Post-redaction survivor count = 0
- No conflict-warning report has unreviewed GO/NO-GO outcome
- Pre/post counts recorded as evidence
- `./groundtruth.db` absent (owner-approved deletion confirmed)

**Artifacts modified:** `tools/knowledge-db/knowledge.db`

---

## Phase C2: Enable ChromaDB Semantic Search (P1)

**Hard preflight gate — v0.2.0 tag must exist before requirements change:**

```bash
# In groundtruth-kb repo:
git tag v0.2.0
git push origin v0.2.0

# Verify from Agent Red (or any clean checkout):
git ls-remote --tags https://github.com/Remaker-Digital/groundtruth-kb.git refs/tags/v0.2.0
# Must return a SHA — if empty, STOP.
```

**Only after tag is verified on remote**, update Agent Red requirements:

- `requirements-test.txt`: Replace line 49 with
  `groundtruth-kb[search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.0`
- `requirements-local.txt`: Replace line 17 with
  `groundtruth-kb[web,search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@v0.2.0`

**Rebuild (config-aware):**
```bash
gt --config tools/knowledge-db/groundtruth.toml deliberations rebuild-index
```

**Post-rebuild verification:**
- `HAS_CHROMADB=True` in runtime
- Indexed count matches `SELECT COUNT(*) FROM current_deliberations` on `tools/knowledge-db/knowledge.db`
- `./groundtruth.db` does not exist at repo root
- `tools/knowledge-db/.groundtruth-chroma/` exists

**Clean-environment import check:**
```python
import groundtruth_kb
print(f'version: {groundtruth_kb.__version__}')  # must be 0.2.0
from groundtruth_kb.db import KnowledgeDB
print(f'upsert_deliberation_source: {hasattr(KnowledgeDB, "upsert_deliberation_source")}')
print(f'rebuild_deliberation_index: {hasattr(KnowledgeDB, "rebuild_deliberation_index")}')
import chromadb; print(f'chromadb: {chromadb.__version__}')
```

**Known-answer validation:** `tests/unit/test_deliberation_search.py` — 10 queries, >= 80% top-3.

**Files created:** `tests/unit/test_deliberation_search.py`
**Files modified:** `requirements-test.txt`, `requirements-local.txt`

---

## Phases C3–C6

Unchanged from v3:
- **C3:** Session-wrap harvest script + kb-session-wrap integration
- **C4:** Health metrics script + /check-deliberations skill
- **C5:** WI-3159 traceability repair + DOC-DELIB-COMPLETION
- **C6:** Behavioral protocol — `.claude/rules/deliberation-protocol.md`, CLAUDE.md addition, AGENTS.md item 14a, CODEX-REVIEW-OPERATING-CONTRACT.md checklist

---

## Execution Order

| Phase | Priority | Dependencies | Scope |
|-------|----------|-------------|-------|
| C6: Protocol | P1 | None | 1 rule file, 3 file edits |
| C1: Backfill | P1 | None | Script execution, DB backup |
| C2: ChromaDB | P1 | C1, GT-kb v0.2.0 tag on remote | 1 test, 2 requirement files |
| C3: Harvest | P1 | C1 | 1 script, 1 skill update |
| C4: Health | P2 | C1 | 1 script, 1 skill |
| C5: Traceability | P2 | C1-C3 | KB records |

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
