# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v4)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-12
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 2 findings in `bridge/groundtruth-db-migration-008.md` (Codex NO-GO #4)

## NO-GO #4 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | `.dockerignore` does not exclude root KB assets from Docker build context | P1 | Phase 1h added: update `.dockerignore` with root KB assets. V10 added: Docker context verification. |
| 2 | `rg --hidden` still respects `.gitignore`, making `.claude/` invisible to audit | P2 | V7 split: Audit A uses `rg --no-ignore --hidden` with explicit exclusions; Audit C added as dedicated `.claude/` scan. |

## Cumulative NO-GO Resolution (versions 002 + 004 + 006 + 008)

All 9 findings from four NO-GO reviews are addressed:
1. `.gitignore:109` removes root DB ignore (v003) ✓
2. `CHROMA_PATH` in test_deliberation_search.py explicitly migrated (v003) ✓
3. Grep audit uses `rg --hidden` (v003, broadened v005, fixed v009) ✓
4. Backup file disposition (v005) ✓
5. Broader audit + complete harvest script scope + settings decision (v005) ✓
6. All data/helper artifacts in `tools/knowledge-db/` inventoried (v007) ✓
7. `test_knowledge.db` temp name updated (v007) ✓
8. `.dockerignore` updated for root KB assets (new) ✓
9. Audit scans `.claude/` despite gitignore (new) ✓

## Prior Deliberations

- DELIB-0224, DELIB-0651, DELIB-0317, bridge/deliberation-archive-completion-004.md
- bridge/groundtruth-db-migration-002.md (NO-GO #1), -004.md (#2), -006.md (#3), -008.md (#4)

## Objective

Move Agent Red Knowledge Database from `tools/knowledge-db/knowledge.db` to `groundtruth.db` at repo root. Move ChromaDB index from `tools/knowledge-db/.groundtruth-chroma/` to `.groundtruth-chroma/` at repo root. Leave `tools/knowledge-db/` as a shim/config directory with no database or index data files.

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
db_path = "../../groundtruth.db"
chroma_path = "../../.groundtruth-chroma"
```

**1d. Update `tools/knowledge-db/db.py` (line 42)**
```python
DB_PATH = Path(__file__).resolve().parent.parent.parent / "groundtruth.db"
```

**1e. Update `.gitignore`**

Remove:
- Line 109: `groundtruth.db`
- Line 222: `tools/knowledge-db/knowledge.db.backup-*`

Add:
```gitignore
groundtruth.db.backup-*
groundtruth.db.pre-backfill-*
.groundtruth-chroma/
```

Keep existing: `*.db-shm`, `*.db-wal`, `bridge.db`, `tools/knowledge-db/knowledge-export-*.json`.

**1f. Relocate existing backup**
```bash
mv tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740 groundtruth.db.pre-backfill-20260412-135740
```

**1g. Disposition of other `tools/knowledge-db/` artifacts**

| Artifact | Size | Git status | Disposition |
|----------|------|------------|-------------|
| `bridge.db` | 0 bytes | ignored | Allowed survivor (empty, globally ignored) |
| `knowledge-export-*.json` | ~1.2 MB | ignored | Allowed survivors (historical exports) |
| `create_s259_wis.py` | 7 KB | tracked | Allowed survivor (utility script, not data) |

**1h. Update `.dockerignore` (addresses NO-GO #4 finding 1)**

Replace:
```dockerignore
# Knowledge DB (51MB SQLite, development-only)
tools/knowledge-db/
```

With:
```dockerignore
# Knowledge DB (development-only, not runtime)
tools/knowledge-db/
groundtruth.db
groundtruth.db.backup-*
groundtruth.db.pre-backfill-*
.groundtruth-chroma/
```

This ensures root KB assets are excluded from Docker build contexts even though `tools/knowledge-db/` remains ignored (it still contains shim/config files that are not needed at runtime). All Docker builds using `.` as context (`build_orchestrator.py`, `build-api-gateway.yml`, `build-test-host.yml`, `build_agent_containers.py`) will continue to exclude KB data.

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
| `tests/unit/test_deliberation_search.py` | 8-9 | Docstring → root paths |
| `tests/unit/test_deliberation_search.py` | 24 | `KB_PATH = REPO_ROOT / "groundtruth.db"` |
| `tests/unit/test_deliberation_search.py` | 25 | `CHROMA_PATH = REPO_ROOT / ".groundtruth-chroma"` |
| `tests/unit/test_deliberation_search.py` | 30 | Skip reason → root paths |
| `tests/transport/test_production_gate.py` | 348, 398 | `PROJECT_ROOT / "groundtruth.db"` |
| `tests/transport/test_governance_integrity.py` | 50 | `src_db = _PROJECT_ROOT / "groundtruth.db"` |
| `tests/transport/test_governance_integrity.py` | 52 | `tmp_db = Path(tmp_dir) / "test_groundtruth.db"` |
| `tests/multi_tenant/test_s153_future_feature_verification.py` | 23 | Root path |
| `tests/multi_tenant/test_s153_batch12_spec_verification.py` | 28 | Root path |
| `tests/multi_tenant/test_s153_batch11_spec_verification.py` | 25 | Root path |
| `tests/multi_tenant/test_s153_testing_quality_specs.py` | 22 | Root path |

### Phase 4: Claude tooling updates

| File | Line(s) | Change |
|------|---------|--------|
| `.claude/commands/open-items.md` | 13 | `sqlite3.connect('groundtruth.db')` |
| `.claude/skills/kb-assert/SKILL.md` | 35 | `sqlite3.connect('groundtruth.db')` |
| `.claude/skills/kb-query/SKILL.md` | 20 | Path reference → `groundtruth.db` |
| `.claude/commands/check-db.md` | 11 | Path reference → `groundtruth.db` |
| `.claude/hooks/assertion-check.py` | 520 | Resolve `groundtruth.db` at repo root |
| `.claude/settings.local.json` | 72 | Allowlist → `groundtruth.db` |
| `.claude/settings.local.json` | 78 | Allowlist → `groundtruth.db` |

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

- `scripts/archive/` — Historical (~20 files)
- `bridge/` files — Audit trail
- `docs/archive/BACKLOG-NEW-WORK-ITEMS-FROZEN.md` — Frozen
- `MEMBASE-4-CLAUDE.md` — Historical
- `docs/owner-messages-all.json` — Conversation log
- `.claude/hooks/.prime-bridge-wake-last-context.json` — Transient cache

## Verification Plan

### V1. Git tracking
```bash
git ls-files groundtruth.db
# Expected: groundtruth.db (tracked)

git ls-files tools/knowledge-db/knowledge.db
# Expected: (empty)
```

### V2. Functional smoke test
```bash
python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); import db; kdb = db.KnowledgeDB(); print(kdb.get_summary())"
```

### V3. Web UI
```bash
python tools/knowledge-db/app.py &
# Confirm port 8090, loads data
```

### V4. Deliberation semantic search
```bash
python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); import db; kdb = db.KnowledgeDB(); results = kdb.search_deliberations('credential scan'); print(f'{len(results)} results')"
```

### V5. Semantic search test suite
```bash
python -m pytest tests/unit/test_deliberation_search.py -q --tb=short
# Expected: 16 passed (NOT skipped). Record pass count.
```

### V6. Assertion hook
```bash
python .claude/hooks/assertion-check.py 2>&1 | head -5
```

### V7. Path audit (addresses NO-GO #4 finding 2)

**Audit A — Unrestricted broad sweep (overrides .gitignore):**
```bash
rg --no-ignore --hidden -n "knowledge\.db" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!docs/owner-messages-all.json" -g "!MEMBASE-4-CLAUDE.md" -g "!.git/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json" -g "!**/__pycache__/**"
```

**Allowed survivors** (documented, non-functional):
- `tools/knowledge-db/db.py:10` — docstring historical context
- `test_host/suites.py:97` — comment text
- `memory/work_list.md` — WI description text

Any other match in `.claude/`, `scripts/` (non-archive), `tests/`, `src/`, `tools/`, or docs is a **blocker**.

**Audit B — Nested ChromaDB path:**
```bash
rg --no-ignore --hidden -n "tools/knowledge-db/\.groundtruth-chroma|tools[/\\\\]knowledge-db[/\\\\]\.groundtruth-chroma" -g "!bridge/**" -g "!scripts/archive/**" -g "!docs/archive/**" -g "!.git/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json" -g "!**/__pycache__/**"
```
Expected: zero matches.

**Audit C — Dedicated `.claude/` scan (addresses NO-GO #4 finding 2):**
```bash
rg --no-ignore --hidden -n "knowledge\.db" .claude -g "!.git/**" -g "!**/*last-context.json" -g "!**/__pycache__/**"
```
Expected: zero matches after Phase 4 updates. Any hit in `.claude/settings.local.json`, `.claude/commands/`, `.claude/skills/`, or `.claude/hooks/*.py` is a **blocker**.

### V8. Full directory audit of `tools/knowledge-db/`

**Expected tracked contents:** `db.py`, `app.py`, `groundtruth.toml`, `seed.py`, `assertions.py`, `create_s259_wis.py`, `__pycache__/`, `templates/`, `static/`.

**Allowed ignored survivors:** `bridge.db` (0 bytes), `knowledge-export-*.json` (historical).

**NOT expected:** `knowledge.db`, `knowledge.db.pre-backfill-*`, `.groundtruth-chroma/`.

```bash
ls tools/knowledge-db/knowledge.db* 2>/dev/null && echo "BLOCKER: stale DB data" || echo "OK: no stale DB"
ls -d tools/knowledge-db/.groundtruth-chroma 2>/dev/null && echo "BLOCKER: stale chroma" || echo "OK: no stale chroma"
```

### V9. Root file state
```bash
git check-ignore -v groundtruth.db .groundtruth-chroma groundtruth.db.pre-backfill-20260412-135740
# Expected: groundtruth.db NOT ignored, .groundtruth-chroma IS ignored, pre-backfill IS ignored
```

### V10. Docker context verification (addresses NO-GO #4 finding 1)
```bash
rg -n "groundtruth\.db|\.groundtruth-chroma|tools/knowledge-db" .dockerignore
# Expected: all five new lines present plus the existing tools/knowledge-db/ line

# Dry-run context check: confirm root KB assets would be excluded
echo "groundtruth.db" | git check-ignore --stdin --no-index -v 2>/dev/null || true
# Alternative: verify .dockerignore patterns manually match root assets
```

## Rollback

```bash
git mv groundtruth.db tools/knowledge-db/knowledge.db
mv .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma
mv groundtruth.db.pre-backfill-20260412-135740 tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740
git checkout -- tools/knowledge-db/groundtruth.toml tools/knowledge-db/db.py .gitignore .dockerignore
# Revert all other modified files
```

## Risk Assessment

- **Low risk:** Mechanical rename with comprehensive unrestricted audit
- **No runtime impact:** Production code uses db.py shim; only local dev/CI paths change
- **No Docker impact:** `.dockerignore` updated to exclude all root KB assets; build context size unchanged
- **ChromaDB index:** `mv` preserves; `gt deliberations rebuild-index` regenerates if corrupt
- **Backup:** Relocated, not deleted — no data loss risk
