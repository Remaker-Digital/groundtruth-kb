# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-12
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses all 3 findings in `bridge/groundtruth-db-migration-002.md` (Codex NO-GO)

## NO-GO Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | `.gitignore:109` still ignores `groundtruth.db` — moved DB would be untracked | P1 | Phase 1e now removes line 109, adds `.groundtruth-chroma/` ignore, keeps `*.db-shm`/`*.db-wal` |
| 2 | `CHROMA_PATH` in `test_deliberation_search.py:25` not migrated — test silently skips | P1 | Phase 3 now explicitly updates `CHROMA_PATH`, docstring, and skip reason. Verification includes running the test suite with pass count recorded. |
| 3 | Grep audit misses `.claude/` hidden paths and JSON files | P2 | Verification grep replaced with `rg --hidden` covering all file types, with documented allowed survivors |

## Prior Deliberations

- DELIB-0224, DELIB-0651, DELIB-0317: Prior reviews establishing path conventions and identifying nested-path fragility
- bridge/deliberation-archive-completion-004.md: Codex flagged `gt rebuild-index` creating stray `./groundtruth.db` as a config hazard
- bridge/groundtruth-db-migration-002.md: NO-GO identifying .gitignore, CHROMA_PATH, and audit gaps

## Objective

Move Agent Red Knowledge Database from `tools/knowledge-db/knowledge.db` to `groundtruth.db` at repo root. Move ChromaDB index from `tools/knowledge-db/.groundtruth-chroma/` to `.groundtruth-chroma/` at repo root.

## Scope

### Phase 1: Core infrastructure (atomic)

**1a. Move database file**
```
git mv tools/knowledge-db/knowledge.db groundtruth.db
```

**1b. Move ChromaDB index**
```
mv tools/knowledge-db/.groundtruth-chroma .groundtruth-chroma
```

**1c. Update `tools/knowledge-db/groundtruth.toml`**
```toml
# Before
db_path = "./knowledge.db"
chroma_path = "./.groundtruth-chroma"

# After
db_path = "../../groundtruth.db"
chroma_path = "../../.groundtruth-chroma"
```

**1d. Update `tools/knowledge-db/db.py` (line 42)**
```python
# Before
DB_PATH = Path(__file__).resolve().parent / "knowledge.db"

# After
DB_PATH = Path(__file__).resolve().parent.parent.parent / "groundtruth.db"
```

**1e. Update `.gitignore`** (addresses NO-GO finding #1)

Remove:
```
groundtruth.db                          # line 109 — was ignoring stale root copy; now the DB lives here
tools/knowledge-db/knowledge.db.backup-*  # line 222 — old backup pattern
```

Add:
```
groundtruth.db.backup-*
.groundtruth-chroma/
```

Keep existing:
```
*.db-shm
*.db-wal
```

### Phase 2: Active script updates

Files with hardcoded `tools/knowledge-db/knowledge.db` paths:

| File | Line(s) | Change |
|------|---------|--------|
| `src/quality_metrics/normalize.py` | 55, 86 | Default param → `"groundtruth.db"` |
| `scripts/harvest_session_deliberations.py` | 48 | `KB_PATH = REPO_ROOT / "groundtruth.db"` |
| `scripts/verify_all_specs.py` | 17 | `DB_PATH = PROJECT_ROOT / "groundtruth.db"` |
| `scripts/s174_kb_artifacts.py` | 13 | `DB_PATH = "groundtruth.db"` |
| `scripts/resolve_batch_wis_s117.py` | 131 | `sqlite3.connect('groundtruth.db')` |
| `scripts/backfill_lo_reports.py` | 375, 666 | Path and help text |
| `scripts/kb_linkage_repair.py` | 24 | `DB_PATH = PROJECT_ROOT / "groundtruth.db"` |
| `scripts/insert_batch6_coverage_s112.py` | 23 | `DB_PATH = ROOT / "groundtruth.db"` |
| `scripts/deliberation_health.py` | 31, 254 | Path and help text |
| `scripts/_insert_s136_prompt.py` | 6 | Update path resolution to repo root |
| `tools/knowledge-db/seed.py` | 587, 603 | DB path → repo root, backup naming → `groundtruth.db.backup-*` |
| `scripts/batch_assertions_round3.py` | Check | If uses path, update |

### Phase 3: Test file updates (addresses NO-GO finding #2)

| File | Line(s) | Change |
|------|---------|--------|
| `tests/unit/test_deliberation_search.py` | 8-9 (docstring) | Update to `groundtruth.db` and `.groundtruth-chroma/` at repo root |
| `tests/unit/test_deliberation_search.py` | 24 | `KB_PATH = REPO_ROOT / "groundtruth.db"` |
| `tests/unit/test_deliberation_search.py` | **25** | **`CHROMA_PATH = REPO_ROOT / ".groundtruth-chroma"`** |
| `tests/unit/test_deliberation_search.py` | 30 | Skip reason → `"Requires groundtruth.db and .groundtruth-chroma index at repo root"` |
| `tests/transport/test_production_gate.py` | 348, 398 | `KnowledgeDB(str(PROJECT_ROOT / "groundtruth.db"))` |
| `tests/transport/test_governance_integrity.py` | 50, 52 | `src_db = _PROJECT_ROOT / "groundtruth.db"` |
| `tests/multi_tenant/test_s153_future_feature_verification.py` | 23 | Update path |
| `tests/multi_tenant/test_s153_batch12_spec_verification.py` | 28 | Update path |
| `tests/multi_tenant/test_s153_batch11_spec_verification.py` | 25 | Update path |
| `tests/multi_tenant/test_s153_testing_quality_specs.py` | 22 | Update path |

### Phase 4: Claude tooling updates

| File | Line(s) | Change |
|------|---------|--------|
| `.claude/commands/open-items.md` | 13 | `sqlite3.connect('groundtruth.db')` |
| `.claude/skills/kb-assert/SKILL.md` | 35 | `sqlite3.connect('groundtruth.db')` |
| `.claude/skills/kb-query/SKILL.md` | 20 | Update path reference |
| `.claude/commands/check-db.md` | 11 | Update path reference |
| `.claude/hooks/assertion-check.py` | 520 | `db_path = PROJECT_ROOT / "groundtruth.db"` (verify PROJECT_ROOT resolves to repo root) |
| `.claude/settings.local.json` | 72 | Update functional SQLite path in allowlist pattern |

### Phase 5: Documentation updates

| File | Line(s) | Change |
|------|---------|--------|
| `CLAUDE.md` | 74 | `groundtruth.db` |
| `CLAUDE-ARCHITECTURE.md` | 225 | `groundtruth.db` |
| `docs/operations/session-wrap-up-procedure.md` | 15 | `KNOWLEDGE_DB` env var |
| `sonar-project.properties` | 15 | Update exclusion path |
| `docs/specification-scaffold/SPEC-TEMPLATE.md` | 120 | Example code |
| `docs/specification-scaffold/README.md` | 24 | Example code |

### Explicitly NOT changed

- **`scripts/archive/`** — Historical scripts, never rerun. ~20 files reference old path.
- **`bridge/` files** — Historical audit trail per protocol.
- **`docs/archive/BACKLOG-NEW-WORK-ITEMS-FROZEN.md`** — Frozen archive.
- **`MEMBASE-4-CLAUDE.md`** — Historical document.
- **`docs/owner-messages-all.json`** — Conversation log.
- **`.claude/hooks/.prime-bridge-wake-last-context.json`** — Transient cache, auto-regenerated each session. Allowed survivor.

## Verification Plan (addresses NO-GO finding #3)

### V1. Git tracking verification
```bash
git ls-files groundtruth.db
# Expected: groundtruth.db (tracked)

git ls-files tools/knowledge-db/knowledge.db
# Expected: (empty — removed from index)

git status --short -- groundtruth.db tools/knowledge-db/knowledge.db .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma .gitignore
# Expected: only staged/committed changes, no untracked data files
```

### V2. Functional smoke test
```bash
python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); import db; kdb = db.KnowledgeDB(); print(kdb.get_summary())"
```

### V3. Web UI verification
```bash
python tools/knowledge-db/app.py &
# Confirm it starts on port 8090 and loads data
```

### V4. Deliberation semantic search verification
```bash
python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); import db; kdb = db.KnowledgeDB(); results = kdb.search_deliberations('credential scan'); print(f'{len(results)} results')"
```

### V5. Semantic search test suite (addresses NO-GO finding #2)
```bash
python -m pytest tests/unit/test_deliberation_search.py -q --tb=short
# Expected: 16 passed (not skipped)
# Record exact pass count in post-implementation report
```

### V6. Assertion hook verification
```bash
python .claude/hooks/assertion-check.py 2>&1 | head -5
# Confirm it finds the DB and runs assertions
```

### V7. Hidden-aware path audit (addresses NO-GO finding #3)
```bash
rg --hidden -n "tools/knowledge-db/knowledge\.db" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!docs/owner-messages-all.json" -g "!MEMBASE-4-CLAUDE.md" -g "!.git/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json"
# Expected: zero matches

rg --hidden -n "tools/knowledge-db/\.groundtruth-chroma" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!.git/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json"
# Expected: zero matches
```

**Allowed survivors (documented):**
- `.claude/hooks/.prime-bridge-wake-last-context.json` — transient session cache, auto-regenerated
- `tools/knowledge-db/db.py` lines 10, 82 — docstring/comment references to old path in context (the functional code on line 42 is updated)
- `scripts/archive/` — historical scripts
- `bridge/` — historical audit trail
- `docs/archive/`, `MEMBASE-4-CLAUDE.md`, `docs/owner-messages-all.json` — frozen historical docs

### V8. Data directory verification
```bash
ls tools/knowledge-db/
# Expected: db.py, app.py, groundtruth.toml, seed.py, assertions.py, __pycache__/, templates/, static/
# NOT expected: knowledge.db, .groundtruth-chroma/
```

## Rollback

```bash
git mv groundtruth.db tools/knowledge-db/knowledge.db
mv .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma
git checkout -- tools/knowledge-db/groundtruth.toml tools/knowledge-db/db.py .gitignore
# Revert all other modified files
```

Or `git revert <commit>` since the DB file move is tracked.

## Risk Assessment

- **Low risk:** Mechanical rename with comprehensive hidden-aware grep-verified scope
- **No runtime impact:** All production code uses the db.py shim; only local dev/CI paths change
- **ChromaDB index:** Binary data, `mv` preserves it. If corrupt, `gt deliberations rebuild-index` regenerates
- **Backup pattern:** `seed.py` backup naming changes from `knowledge.db.backup-*` to `groundtruth.db.backup-*`
