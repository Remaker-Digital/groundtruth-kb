# WI-3168: Migrate knowledge.db to groundtruth.db at repo root

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-12
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3

## Prior Deliberations

- DELIB-0224: GO on deliberation archive completion (established current `tools/knowledge-db/knowledge.db` path conventions)
- DELIB-0651: NO-GO on prior bridge thread that noted path resolution complexity as a risk
- DELIB-0317: LO advisory noting nested path resolution adds fragility
- bridge/deliberation-archive-completion-004.md (Codex): explicitly called out that `gt rebuild-index` resolving `./groundtruth.db` instead of `tools/knowledge-db/knowledge.db` was a configuration hazard

The stale root `groundtruth.db` was deleted in S282 (owner-approved), clearing the way for this migration.

## Objective

Move the Agent Red Knowledge Database from `tools/knowledge-db/knowledge.db` to `groundtruth.db` at the repository root. Move ChromaDB index from `tools/knowledge-db/.groundtruth-chroma/` to `.groundtruth-chroma/` at the repository root.

**Benefits:**
1. Name aligns with the GroundTruth KB project identity
2. Simpler path — `gt` CLI resolves `groundtruth.db` naturally from repo root
3. Eliminates config resolution complexity that caused DELIB-0651 issues
4. `tools/knowledge-db/` becomes a pure shim/config directory (no data files)

## Scope

### Phase 1: Core infrastructure (must be atomic)

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

**1d. Update `tools/knowledge-db/db.py` (lines 42)**
```python
# Before
DB_PATH = Path(__file__).resolve().parent / "knowledge.db"

# After
DB_PATH = Path(__file__).resolve().parent.parent.parent / "groundtruth.db"
```

**1e. Update `.gitignore`**
```
# Remove
tools/knowledge-db/knowledge.db.backup-*

# Add
groundtruth.db.backup-*
```
Note: `groundtruth.db` itself is already tracked by git (it was `knowledge.db`). The `.groundtruth-chroma/` directory should already be in `.gitignore` — verify and add if missing.

### Phase 2: Active script updates

Files with hardcoded `tools/knowledge-db/knowledge.db` paths that must be updated to use `groundtruth.db` (repo root relative) or the db.py shim:

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
| `scripts/_insert_s136_prompt.py` | 6 | Path resolution |
| `tools/knowledge-db/seed.py` | 587, 603 | DB path and backup path |
| `scripts/batch_assertions_round3.py` | Check | If uses path, update |

### Phase 3: Test file updates

| File | Line(s) | Change |
|------|---------|--------|
| `tests/unit/test_deliberation_search.py` | 24, 30 | `KB_PATH = REPO_ROOT / "groundtruth.db"` |
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
| `.claude/hooks/assertion-check.py` | 520 | `db_path = PROJECT_ROOT / "groundtruth.db"` (verify PROJECT_ROOT resolution) |

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
- **`.claude/settings.local.json`** — Allowlist patterns reference old path in regex; these are safety patterns not functional code. Update only the functional path (line 72).
- **`.claude/hooks/.prime-bridge-wake-last-context.json`** — Transient cache, auto-regenerated.

## Verification Plan

1. **Smoke test:** `python -c "import sys; sys.path.insert(0, 'tools/knowledge-db'); import db; kdb = db.KnowledgeDB(); print(kdb.get_summary())"` — confirms shim resolves new path
2. **Web UI:** `python tools/knowledge-db/app.py` — confirm it starts and loads data
3. **Deliberation search:** `python -c "... kdb.search_deliberations('test') ..."` — confirms ChromaDB index resolves
4. **Assertions:** `python .claude/hooks/assertion-check.py` — confirms hook finds DB
5. **Git status:** Verify `groundtruth.db` is tracked, no untracked data files in `tools/knowledge-db/`
6. **Grep audit:** `grep -r "tools/knowledge-db/knowledge.db" --include="*.py" --include="*.toml" --include="*.md" --include="*.properties"` excluding `scripts/archive/`, `bridge/`, `docs/archive/` — should return zero active matches

## Rollback

```bash
git mv groundtruth.db tools/knowledge-db/knowledge.db
mv .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma
git checkout -- tools/knowledge-db/groundtruth.toml tools/knowledge-db/db.py .gitignore
# Then git checkout all modified files
```

Or simply `git revert <commit>` since the DB file move is tracked by git.

## Risk Assessment

- **Low risk:** Mechanical rename with comprehensive grep-verified scope
- **No runtime impact:** All production code uses the db.py shim; only local dev/CI paths change
- **ChromaDB index:** Binary data, `mv` preserves it. If corrupt, `gt deliberations rebuild-index` regenerates it.
- **Backup pattern:** `seed.py` backup naming changes from `knowledge.db.backup-*` to `groundtruth.db.backup-*`
