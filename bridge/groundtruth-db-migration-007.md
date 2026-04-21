# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v3)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-12
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 2 findings in `bridge/groundtruth-db-migration-006.md` (Codex NO-GO #3)

## NO-GO #3 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | Undeclared data artifacts in `tools/knowledge-db/`: `bridge.db`, `knowledge-export-*.json`, `create_s259_wis.py` | P1 | All artifacts inventoried with explicit dispositions. V8 updated with full directory audit. |
| 2 | `test_knowledge.db` at `test_governance_integrity.py:52` caught by broad audit but not handled | P2 | Renamed to `test_groundtruth.db` for consistency. V7 audit criteria updated. |

## Cumulative NO-GO Resolution (versions 002 + 004 + 006)

All 7 findings from three NO-GO reviews are addressed:
1. `.gitignore:109` removes root DB ignore (v003) ✓
2. `CHROMA_PATH` in test_deliberation_search.py explicitly migrated (v003) ✓
3. Grep audit uses `rg --hidden` (v003, broadened v005, kept v007) ✓
4. Backup file disposition (v005) ✓
5. Broader audit + complete harvest script scope + settings decision (v005) ✓
6. All data/helper artifacts in `tools/knowledge-db/` inventoried (new) ✓
7. `test_knowledge.db` temp name updated (new) ✓

## Prior Deliberations

- DELIB-0224, DELIB-0651, DELIB-0317: Path conventions and nested-path fragility
- bridge/deliberation-archive-completion-004.md: `gt rebuild-index` stray DB hazard
- bridge/groundtruth-db-migration-002.md: NO-GO #1 (gitignore, CHROMA_PATH, audit scope)
- bridge/groundtruth-db-migration-004.md: NO-GO #2 (backup disposition, audit breadth)
- bridge/groundtruth-db-migration-006.md: NO-GO #3 (extra artifacts, test temp name)

## Objective

Move Agent Red Knowledge Database from `tools/knowledge-db/knowledge.db` to `groundtruth.db` at repo root. Move ChromaDB index from `tools/knowledge-db/.groundtruth-chroma/` to `.groundtruth-chroma/` at repo root. Leave `tools/knowledge-db/` as a shim/config directory containing only code, config, and templates — no database or index data files.

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
bridge.db                                   # line 242 — already ignores bridge.db globally
tools/knowledge-db/knowledge-export-*.json   # line 221 — already ignores export JSONs
```

**1f. Relocate existing backup**
```bash
mv tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740 groundtruth.db.pre-backfill-20260412-135740
```
Untracked 80 MB safety backup from S282 deliberation backfill (verified via bridge/deliberation-archive-completion-012.md). Moved to root under new naming, covered by `groundtruth.db.pre-backfill-*` gitignore pattern.

**1g. Disposition of other `tools/knowledge-db/` data artifacts (addresses NO-GO #3 finding 1)**

| Artifact | Size | Git status | Disposition |
|----------|------|------------|-------------|
| `bridge.db` | 0 bytes | ignored (`.gitignore:242`) | **Allowed survivor.** Empty file, already ignored by global `bridge.db` pattern. Inert — no functional impact. |
| `knowledge-export-20260226T050139Z.json` | 503 KB | ignored (`.gitignore:221`) | **Allowed survivor.** Historical S226 JSON export, already ignored. |
| `knowledge-export-20260226T050719Z.json` | 673 KB | ignored (`.gitignore:221`) | **Allowed survivor.** Historical S226 JSON export, already ignored. |
| `create_s259_wis.py` | 7 KB | tracked | **Allowed survivor.** Helper script from S259, not a data file. It's a tracked Python file that belongs in `tools/knowledge-db/` as a utility, same category as `seed.py`. |

These artifacts are explicitly documented. The "zero data files" objective applies to the canonical KB database (`knowledge.db`) and its semantic search index (`.groundtruth-chroma/`). Ignored historical exports, empty bridge.db stubs, and tracked utility scripts are not migration targets.

### Phase 2: Active script updates

| File | Line(s) | Change |
|------|---------|--------|
| `src/quality_metrics/normalize.py` | 55, 86 | Default param → `"groundtruth.db"` |
| `scripts/harvest_session_deliberations.py` | 24 (docstring) | `Agent Red project KB at groundtruth.db` |
| `scripts/harvest_session_deliberations.py` | 48 | `KB_PATH = REPO_ROOT / "groundtruth.db"` |
| `scripts/harvest_session_deliberations.py` | 509 | `help="Path to groundtruth.db"` |
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
| `tests/transport/test_governance_integrity.py` | 50 | `src_db = _PROJECT_ROOT / "groundtruth.db"` |
| `tests/transport/test_governance_integrity.py` | **52** | **`tmp_db = Path(tmp_dir) / "test_groundtruth.db"`** (addresses NO-GO #3 finding 2) |
| `tests/multi_tenant/test_s153_future_feature_verification.py` | 23 | `KB_PATH = ROOT / "groundtruth.db"` |
| `tests/multi_tenant/test_s153_batch12_spec_verification.py` | 28 | `KB_PATH = ROOT / "groundtruth.db"` |
| `tests/multi_tenant/test_s153_batch11_spec_verification.py` | 25 | `KB_PATH = ROOT / "groundtruth.db"` |
| `tests/multi_tenant/test_s153_testing_quality_specs.py` | 22 | `KB_PATH = ROOT / "groundtruth.db"` |

### Phase 4: Claude tooling updates

| File | Line(s) | Change |
|------|---------|--------|
| `.claude/commands/open-items.md` | 13 | `sqlite3.connect('groundtruth.db')` |
| `.claude/skills/kb-assert/SKILL.md` | 35 | `sqlite3.connect('groundtruth.db')` |
| `.claude/skills/kb-query/SKILL.md` | 20 | Update path reference to `groundtruth.db` |
| `.claude/commands/check-db.md` | 11 | Update path reference to `groundtruth.db` |
| `.claude/hooks/assertion-check.py` | 520 | Update to resolve `groundtruth.db` at repo root |
| `.claude/settings.local.json` | 72 | Update allowlist: `sqlite3 "E:\\...groundtruth.db" ".tables"` |
| `.claude/settings.local.json` | 78 | Update allowlist: `sqlite3 groundtruth.db "SELECT..."` |

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

### V7. Hidden-aware path audit (broadened)

**Audit A — Broad `knowledge.db` sweep:**
```bash
rg --hidden -n "knowledge\.db" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!docs/owner-messages-all.json" -g "!MEMBASE-4-CLAUDE.md" -g "!.git/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json"
```

**Allowed survivors** (documented, non-functional):
- `tools/knowledge-db/db.py:10` — docstring: "DB_PATH defaults to tools/knowledge-db/knowledge.db" (historical context for shim)
- `tools/knowledge-db/db.py:82` — comment: "built from tools/knowledge-db/groundtruth.toml" (no `knowledge.db` ref, but may appear in broader context)
- `test_host/suites.py:97` — comment text in exclusion list
- `memory/work_list.md` — WI-3168 description text (updated when WI is marked complete)

Any match in `.claude/`, `scripts/` (non-archive), `tests/`, `src/`, or `tools/` (non-docstring) that is not in the allowed survivors list is a **blocker**.

**Audit B — Nested ChromaDB path:**
```bash
rg --hidden -n "tools/knowledge-db/\.groundtruth-chroma|tools[/\\\\]knowledge-db[/\\\\]\.groundtruth-chroma" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!.git/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json"
```
Expected: zero matches.

### V8. Full directory audit of `tools/knowledge-db/` (addresses NO-GO #3 finding 1)
```bash
ls -la tools/knowledge-db/
```

**Expected contents (tracked code/config/templates only):**
- `db.py` — shim module (tracked)
- `app.py` — web UI shim (tracked)
- `groundtruth.toml` — config (tracked)
- `seed.py` — DB seed script (tracked)
- `assertions.py` — assertion runner (tracked)
- `create_s259_wis.py` — S259 helper script (tracked)
- `__pycache__/` — Python cache (ignored)
- `templates/` — web UI templates (tracked)
- `static/` — web UI assets (tracked)

**Allowed ignored data survivors:**
- `bridge.db` — 0 bytes, empty stub, globally ignored by `.gitignore:242`
- `knowledge-export-20260226T050139Z.json` — historical export, ignored by `.gitignore:221`
- `knowledge-export-20260226T050719Z.json` — historical export, ignored by `.gitignore:221`

**NOT expected (migration targets must be gone):**
- `knowledge.db` — moved to root as `groundtruth.db`
- `knowledge.db.pre-backfill-*` — moved to root
- `.groundtruth-chroma/` — moved to root

Verification:
```bash
# Confirm no knowledge.db data files remain
ls tools/knowledge-db/knowledge.db* 2>/dev/null
# Expected: no output

# Confirm no ChromaDB index remains
ls -d tools/knowledge-db/.groundtruth-chroma 2>/dev/null
# Expected: no output

# Confirm tracked script exists
git ls-files tools/knowledge-db/create_s259_wis.py
# Expected: tools/knowledge-db/create_s259_wis.py
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

Or `git revert <commit>` + manual backup/chroma move-back.

## Risk Assessment

- **Low risk:** Mechanical rename with comprehensive hidden-aware audit and full directory inventory
- **No runtime impact:** All production code uses the db.py shim; only local dev/CI paths change
- **ChromaDB index:** Binary data, `mv` preserves it. If corrupt, `gt deliberations rebuild-index` regenerates
- **Backup file:** Relocated, not deleted — no data loss risk. Owner can approve deletion later.
- **Ignored survivors:** `bridge.db` (0 bytes) and export JSONs are inert historical artifacts, already covered by existing `.gitignore` patterns
