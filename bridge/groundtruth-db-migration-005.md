# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v2)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-12
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 2 findings in `bridge/groundtruth-db-migration-004.md` (Codex NO-GO #2)

## NO-GO #2 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | Existing `knowledge.db.pre-backfill-20260412-135740` (80 MB) not accounted for | P1 | Phase 1f added: move backup to root as `groundtruth.db.pre-backfill-20260412-135740`, add ignore pattern. Owner deletion approval deferred — backup becomes inert under new naming at root. |
| 2 | Audit misses path-composed `knowledge.db` refs; incomplete harvest script scope; undecided settings.local.json | P2 | V7 audit broadened to `knowledge\.db` standalone. Phase 2 table expanded with all harvest script lines. `.claude/settings.local.json:72,78` explicitly added to Phase 4. |

## Cumulative NO-GO Resolution (versions 002 + 004)

All 5 findings from both NO-GO reviews are addressed:
1. `.gitignore:109` removes root DB ignore ✓ (v003)
2. `CHROMA_PATH` in test_deliberation_search.py explicitly migrated ✓ (v003)
3. Grep audit uses `rg --hidden` ✓ (v003, strengthened here)
4. Backup file disposition ✓ (new)
5. Broader audit + complete script scope + settings decision ✓ (new)

## Prior Deliberations

- DELIB-0224, DELIB-0651, DELIB-0317: Path conventions and nested-path fragility
- bridge/deliberation-archive-completion-004.md: `gt rebuild-index` stray DB hazard
- bridge/groundtruth-db-migration-002.md: NO-GO #1 (gitignore, CHROMA_PATH, audit scope)
- bridge/groundtruth-db-migration-004.md: NO-GO #2 (backup disposition, audit breadth)

## Objective

Move Agent Red Knowledge Database from `tools/knowledge-db/knowledge.db` to `groundtruth.db` at repo root. Move ChromaDB index from `tools/knowledge-db/.groundtruth-chroma/` to `.groundtruth-chroma/` at repo root. Leave `tools/knowledge-db/` as a pure shim/config directory with zero data files.

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

**1e. Update `.gitignore`**

Remove:
- Line 109: `groundtruth.db` (was ignoring stale root copy; now the DB lives here and must be tracked)
- Line 222: `tools/knowledge-db/knowledge.db.backup-*` (old backup pattern)

Add:
```gitignore
groundtruth.db.backup-*
groundtruth.db.pre-backfill-*
.groundtruth-chroma/
```

Keep existing:
```gitignore
*.db-shm
*.db-wal
```

**1f. Relocate existing backup (addresses NO-GO #2 finding 1)**

```bash
mv tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740 groundtruth.db.pre-backfill-20260412-135740
```

This is an untracked 80 MB safety backup from the S282 deliberation backfill (verified via bridge/deliberation-archive-completion-012.md VERIFIED). Moving it to root under the new naming convention makes it inert and covered by the `groundtruth.db.pre-backfill-*` gitignore pattern. Owner-approved deletion can happen in a future session; for now, it's harmless at root and ignored.

Verification: after move, confirm no `knowledge.db*` data files remain under `tools/knowledge-db/`:
```bash
ls tools/knowledge-db/knowledge.db* 2>/dev/null
# Expected: no output (all data files relocated)
```

### Phase 2: Active script updates

Files with hardcoded `knowledge.db` paths (direct or path-composed):

| File | Line(s) | Change |
|------|---------|--------|
| `src/quality_metrics/normalize.py` | 55, 86 | Default param → `"groundtruth.db"` |
| `scripts/harvest_session_deliberations.py` | **24** (docstring) | `Agent Red project KB at groundtruth.db` |
| `scripts/harvest_session_deliberations.py` | **48** | `KB_PATH = REPO_ROOT / "groundtruth.db"` |
| `scripts/harvest_session_deliberations.py` | **509** | `help="Path to groundtruth.db"` |
| `scripts/verify_all_specs.py` | 17 | `DB_PATH = PROJECT_ROOT / "groundtruth.db"` |
| `scripts/s174_kb_artifacts.py` | 13 | `DB_PATH = "groundtruth.db"` |
| `scripts/resolve_batch_wis_s117.py` | 131 | `sqlite3.connect('groundtruth.db')` |
| `scripts/backfill_lo_reports.py` | 375, 666 | Path and help text → `groundtruth.db` |
| `scripts/kb_linkage_repair.py` | 24 | `DB_PATH = PROJECT_ROOT / "groundtruth.db"` |
| `scripts/insert_batch6_coverage_s112.py` | 23 | `DB_PATH = ROOT / "groundtruth.db"` |
| `scripts/deliberation_health.py` | 31 | `KB_PATH = REPO_ROOT / "groundtruth.db"` |
| `scripts/deliberation_health.py` | 254 | `help="Path to groundtruth.db"` |
| `scripts/_insert_s136_prompt.py` | 6 | Update path resolution to repo root |
| `tools/knowledge-db/seed.py` | 587 | DB path → repo root `groundtruth.db` |
| `tools/knowledge-db/seed.py` | 603 | Backup naming → `groundtruth.db.backup-*` |

### Phase 3: Test file updates

| File | Line(s) | Change |
|------|---------|--------|
| `tests/unit/test_deliberation_search.py` | 8-9 (docstring) | `groundtruth.db` and `.groundtruth-chroma/` at repo root |
| `tests/unit/test_deliberation_search.py` | 24 | `KB_PATH = REPO_ROOT / "groundtruth.db"` |
| `tests/unit/test_deliberation_search.py` | 25 | `CHROMA_PATH = REPO_ROOT / ".groundtruth-chroma"` |
| `tests/unit/test_deliberation_search.py` | 30 | Skip reason → `"Requires groundtruth.db and .groundtruth-chroma index at repo root"` |
| `tests/transport/test_production_gate.py` | 348, 398 | `KnowledgeDB(str(PROJECT_ROOT / "groundtruth.db"))` |
| `tests/transport/test_governance_integrity.py` | 50, 52 | `src_db = _PROJECT_ROOT / "groundtruth.db"` |
| `tests/multi_tenant/test_s153_future_feature_verification.py` | 23 | `KB_PATH = ROOT / "groundtruth.db"` |
| `tests/multi_tenant/test_s153_batch12_spec_verification.py` | 28 | `KB_PATH = ROOT / "groundtruth.db"` |
| `tests/multi_tenant/test_s153_batch11_spec_verification.py` | 25 | `KB_PATH = ROOT / "groundtruth.db"` |
| `tests/multi_tenant/test_s153_testing_quality_specs.py` | 22 | `KB_PATH = ROOT / "groundtruth.db"` |

### Phase 4: Claude tooling updates (addresses NO-GO #2 finding 2)

| File | Line(s) | Change |
|------|---------|--------|
| `.claude/commands/open-items.md` | 13 | `sqlite3.connect('groundtruth.db')` |
| `.claude/skills/kb-assert/SKILL.md` | 35 | `sqlite3.connect('groundtruth.db')` |
| `.claude/skills/kb-query/SKILL.md` | 20 | Update path reference to `groundtruth.db` |
| `.claude/commands/check-db.md` | 11 | Update path reference to `groundtruth.db` |
| `.claude/hooks/assertion-check.py` | 520 | Update to resolve `groundtruth.db` at repo root (verify `KB_DIR` or `PROJECT_ROOT` resolution) |
| `.claude/settings.local.json` | 72 | Update allowlist: `sqlite3 "E:\\...groundtruth.db" ".tables"` |
| `.claude/settings.local.json` | 78 | Update allowlist: `sqlite3 groundtruth.db "SELECT..."` |

**Decision on `.claude/settings.local.json`:** Both lines 72 and 78 are functional permission patterns — they allow specific SQLite commands to run without manual approval. They must be updated to match the new DB name, otherwise the allowed commands would reference a non-existent file and operators would get unexpected permission prompts.

### Phase 5: Documentation updates

| File | Line(s) | Change |
|------|---------|--------|
| `CLAUDE.md` | 74 | `groundtruth.db` |
| `CLAUDE-ARCHITECTURE.md` | 225 | `groundtruth.db` |
| `docs/operations/session-wrap-up-procedure.md` | 15 | `KNOWLEDGE_DB` → `groundtruth.db` |
| `sonar-project.properties` | 15 | Exclusion → `groundtruth.db` |
| `docs/specification-scaffold/SPEC-TEMPLATE.md` | 120 | Example code |
| `docs/specification-scaffold/README.md` | 24 | Example code |

### Explicitly NOT changed

- **`scripts/archive/`** — Historical scripts (~20 files). Never rerun.
- **`bridge/` files** — Historical audit trail per protocol.
- **`docs/archive/BACKLOG-NEW-WORK-ITEMS-FROZEN.md`** — Frozen archive.
- **`MEMBASE-4-CLAUDE.md`** — Historical document.
- **`docs/owner-messages-all.json`** — Conversation log.
- **`.claude/hooks/.prime-bridge-wake-last-context.json`** — Transient session cache, auto-regenerated.
- **`tools/knowledge-db/db.py` lines 10, 82** — Docstring/comment context references. The functional code on line 42 is updated; the docstring references provide historical context about what the shim replaces.
- **`test_host/suites.py:97`** — Comment text, not a functional path.

## Verification Plan

### V1. Git tracking
```bash
git ls-files groundtruth.db
# Expected: groundtruth.db (tracked)

git ls-files tools/knowledge-db/knowledge.db
# Expected: (empty)

git status --short -- groundtruth.db tools/knowledge-db/knowledge.db .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma .gitignore
# Expected: only staged/committed changes, no surprise untracked entries
```

### V2. Functional smoke test
```bash
python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); import db; kdb = db.KnowledgeDB(); print(kdb.get_summary())"
```

### V3. Web UI
```bash
python tools/knowledge-db/app.py &
# Confirm starts on port 8090 and loads data
```

### V4. Deliberation semantic search
```bash
python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); import db; kdb = db.KnowledgeDB(); results = kdb.search_deliberations('credential scan'); print(f'{len(results)} results')"
```

### V5. Semantic search test suite
```bash
python -m pytest tests/unit/test_deliberation_search.py -q --tb=short
# Expected: 16 passed (NOT skipped)
# Record exact pass count in post-impl report
```

### V6. Assertion hook
```bash
python .claude/hooks/assertion-check.py 2>&1 | head -5
# Confirm finds DB and runs assertions
```

### V7. Hidden-aware path audit (broadened — addresses NO-GO #2 finding 2)

**Audit A — Broad `knowledge.db` sweep:**
```bash
rg --hidden -n "knowledge\.db" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!docs/owner-messages-all.json" -g "!MEMBASE-4-CLAUDE.md" -g "!.git/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json"
```
Expected: zero active matches. Any hit in `.claude/`, `scripts/`, `tests/`, `src/`, `tools/`, or docs is a blocker.

**Allowed survivors** (documented, non-functional):
- `tools/knowledge-db/db.py:10` — docstring historical context ("DB_PATH defaults to...")
- `tools/knowledge-db/db.py:82` — comment historical context ("built from tools/knowledge-db/groundtruth.toml")
- `test_host/suites.py:97` — comment text
- `memory/work_list.md` — WI description text (will be updated when WI is marked complete)

If db.py lines 10 and 82 are flagged, they are allowed because they are non-functional docstring/comment text in the shim module that provides historical context.

**Audit B — Nested ChromaDB path:**
```bash
rg --hidden -n "tools/knowledge-db/\.groundtruth-chroma|tools[/\\\\]knowledge-db[/\\\\]\.groundtruth-chroma" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!.git/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json"
```
Expected: zero matches.

### V8. Data directory clean check (addresses NO-GO #2 finding 1)
```bash
ls tools/knowledge-db/knowledge.db* 2>/dev/null
# Expected: no output

ls tools/knowledge-db/.groundtruth-chroma 2>/dev/null
# Expected: no output

ls tools/knowledge-db/
# Expected: db.py, app.py, groundtruth.toml, seed.py, assertions.py, __pycache__/, templates/, static/
# NOT expected: any .db, .db-*, or .groundtruth-chroma artifacts
```

### V9. Root file state
```bash
ls -la groundtruth.db .groundtruth-chroma/ groundtruth.db.pre-backfill-* 2>/dev/null
# Expected: groundtruth.db (tracked), .groundtruth-chroma/ (dir, ignored), pre-backfill backup (ignored)

git check-ignore -v groundtruth.db .groundtruth-chroma groundtruth.db.pre-backfill-20260412-135740
# Expected: groundtruth.db NOT ignored, .groundtruth-chroma IS ignored, pre-backfill IS ignored
```

## Rollback

```bash
git mv groundtruth.db tools/knowledge-db/knowledge.db
mv .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma
mv groundtruth.db.pre-backfill-20260412-135740 tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740
git checkout -- tools/knowledge-db/groundtruth.toml tools/knowledge-db/db.py .gitignore
# Revert all other modified files
```

Or `git revert <commit>` + manual backup file move-back.

## Risk Assessment

- **Low risk:** Mechanical rename with comprehensive hidden-aware audit
- **No runtime impact:** All production code uses the db.py shim; only local dev/CI paths change
- **ChromaDB index:** Binary data, `mv` preserves it. If corrupt, `gt deliberations rebuild-index` regenerates
- **Backup file:** Relocated, not deleted — no data loss risk. Owner can approve deletion later.
