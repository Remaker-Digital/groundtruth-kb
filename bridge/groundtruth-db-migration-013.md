# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v6)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-12
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 2 findings in `bridge/groundtruth-db-migration-012.md` (Codex NO-GO #6)

## NO-GO #6 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | Active LO tools (`project_progress_snapshot.py`, `export_specifications_csv.py`) still point at nested KB | P1 | Both scripts added to Phase 2 with line-level updates. `independent-progress-assessments/` added to Audit A scope. V11 added for LO tool verification. |
| 2 | `wiki/` and `agent-red.wiki/` have stale KB path documentation | P2 | Explicitly excluded — separate git repositories (local clones of GitHub wiki). Follow-up action recorded for wiki source-of-truth update. |

## Cumulative NO-GO Resolution (versions 002 + 004 + 006 + 008 + 010 + 012)

All 13 findings from six NO-GO reviews addressed. This version carries forward all corrected scope from v011.

## Prior Deliberations

- DELIB-0224, DELIB-0651, DELIB-0317, bridge/deliberation-archive-completion-004.md
- NO-GO versions: -002, -004, -006, -008, -010, -012

## Objective

Move Agent Red Knowledge Database from `tools/knowledge-db/knowledge.db` to `groundtruth.db` at repo root. Move ChromaDB index to `.groundtruth-chroma/` at repo root. Leave `tools/knowledge-db/` as a shim/config directory with no database or index data files.

## Scope

### Phase 1: Core infrastructure (atomic)

**1a.** `git mv tools/knowledge-db/knowledge.db groundtruth.db`

**1b.** `mv tools/knowledge-db/.groundtruth-chroma .groundtruth-chroma`

**1c.** Update `tools/knowledge-db/groundtruth.toml`:
```toml
db_path = "../../groundtruth.db"
chroma_path = "../../.groundtruth-chroma"
```

**1d.** Update `tools/knowledge-db/db.py` (line 42):
```python
DB_PATH = Path(__file__).resolve().parent.parent.parent / "groundtruth.db"
```

**1e.** Update `.gitignore` — Remove `groundtruth.db` (line 109) and `tools/knowledge-db/knowledge.db.backup-*` (line 222). Add `groundtruth.db.backup-*`, `groundtruth.db.pre-backfill-*`, `.groundtruth-chroma/`.

**1f.** Relocate backup: `mv tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740 groundtruth.db.pre-backfill-20260412-135740`

**1g.** Other `tools/knowledge-db/` artifacts — allowed survivors: `bridge.db` (0 bytes, ignored), `knowledge-export-*.json` (ignored), `create_s259_wis.py` (tracked utility).

**1h.** Update `.dockerignore` — add `groundtruth.db`, `groundtruth.db.backup-*`, `groundtruth.db.pre-backfill-*`, `.groundtruth-chroma/`.

### Phase 2: Active script updates

| File | Line(s) | Change |
|------|---------|--------|
| `src/quality_metrics/normalize.py` | 55, 86 | `"groundtruth.db"` |
| `scripts/harvest_session_deliberations.py` | 24, 48, 509 | All three refs |
| `scripts/verify_all_specs.py` | 17 | Root path |
| `scripts/s174_kb_artifacts.py` | 13 | Root path |
| `scripts/resolve_batch_wis_s117.py` | 131 | Root path |
| `scripts/backfill_lo_reports.py` | 375, 666 | Path + help |
| `scripts/kb_linkage_repair.py` | 24 | Root path |
| `scripts/insert_batch6_coverage_s112.py` | 23 | Root path |
| `scripts/deliberation_health.py` | 31, 254 | Path + help |
| `scripts/_insert_s136_prompt.py` | 6 | Root path |
| `tools/knowledge-db/seed.py` | 587, 603 | Root path + backup name |
| **`independent-progress-assessments/tools/project_progress_snapshot.py`** | **28** | **`KB_PATH = ROOT / "groundtruth.db"`** |
| **`independent-progress-assessments/export_specifications_csv.py`** | **24** | **`DEFAULT_DB_PATH = PROJECT_ROOT / "groundtruth.db"`** |
| **`independent-progress-assessments/export_specifications_csv.py`** | **145** | **Help text → `"Path to groundtruth.db"`** |

### Phase 3: Test file updates

| File | Line(s) | Change |
|------|---------|--------|
| `tests/unit/test_deliberation_search.py` | 8-9, 24, 25, 30 | Docstring, KB_PATH, CHROMA_PATH, skip reason |
| `tests/transport/test_production_gate.py` | 348, 398 | Root path |
| `tests/transport/test_governance_integrity.py` | 50, 52 | Root path + `test_groundtruth.db` |
| `tests/multi_tenant/test_s153_future_feature_verification.py` | 23 | Root path |
| `tests/multi_tenant/test_s153_batch12_spec_verification.py` | 28 | Root path |
| `tests/multi_tenant/test_s153_batch11_spec_verification.py` | 25 | Root path |
| `tests/multi_tenant/test_s153_testing_quality_specs.py` | 22 | Root path |

### Phase 4: Claude tooling updates

| File | Line(s) | Change |
|------|---------|--------|
| `.claude/commands/open-items.md` | 13 | `groundtruth.db` |
| `.claude/skills/kb-assert/SKILL.md` | 35 | `groundtruth.db` |
| `.claude/skills/kb-query/SKILL.md` | 20 | `groundtruth.db` |
| `.claude/commands/check-db.md` | 11 | `groundtruth.db` |
| `.claude/hooks/assertion-check.py` | 520 | Root path |
| `.claude/settings.local.json` | 72, 78 | `groundtruth.db` |

### Phase 5: Documentation updates

| File | Line(s) | Change |
|------|---------|--------|
| `CLAUDE.md` | 74 | `groundtruth.db` |
| `CLAUDE-ARCHITECTURE.md` | 225 | `groundtruth.db` |
| `docs/operations/session-wrap-up-procedure.md` | 15 | `groundtruth.db` |
| `sonar-project.properties` | 15 | `groundtruth.db` |
| `docs/specification-scaffold/SPEC-TEMPLATE.md` | 120 | Example code |
| `docs/specification-scaffold/README.md` | 24 | Example code |

### Explicitly NOT changed

- `scripts/archive/` — Historical (~20 files)
- `bridge/` files — Audit trail
- `docs/archive/BACKLOG-NEW-WORK-ITEMS-FROZEN.md` — Frozen
- `MEMBASE-4-CLAUDE.md` — Historical
- `docs/owner-messages-all.json` — Conversation log
- `.claude/hooks/.prime-bridge-wake-last-context.json` — Transient cache
- **`wiki/` and `agent-red.wiki/`** — Separate git repositories (local clones of the GitHub wiki, each with their own `.git/`). These are gitignored by `.gitignore:188-189` and are not part of the Agent Red repo's tracked content. The source of truth is the GitHub wiki; updating these local clones would be overwritten on next `git pull` from the wiki remote. **Follow-up action:** After this migration is committed, update the GitHub wiki source to reference `groundtruth.db` at repo root. This is a separate, low-risk documentation task.

## Verification Plan

### V1. Git tracking
```bash
git ls-files groundtruth.db
# Expected: groundtruth.db

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

### V7. Bounded path audit

**Audit A — Directory-targeted active-surface scan:**
```bash
rg --no-ignore --hidden -n "knowledge\.db" .claude scripts src tests tools docs memory test_host independent-progress-assessments CLAUDE.md CLAUDE-ARCHITECTURE.md CLAUDE-REFERENCE.md sonar-project.properties .gitignore .dockerignore -g "!scripts/archive/**" -g "!docs/archive/**" -g "!docs/owner-messages-all.json" -g "!.claude/hooks/.prime-bridge-wake-last-context.json" -g "!**/__pycache__/**" -g "!independent-progress-assessments/CODEX-INSIGHT-DROPBOX/**" -g "!independent-progress-assessments/*.csv" -g "!independent-progress-assessments/dashboards/**" -g "!independent-progress-assessments/logs/**"
```

Scans 9 active first-party directories (including `independent-progress-assessments/`) plus root config/doc files. Uses `--no-ignore` to scan `.claude/` and gitignored LO tools. Excludes generated LO artifacts (insight reports, CSVs, dashboards, logs).

**Allowed survivors** (documented, non-functional):
- `tools/knowledge-db/db.py:10` — docstring historical context
- `test_host/suites.py:97` — comment text
- `memory/work_list.md` — WI description text

Any other match is a **blocker**.

**Audit B — Nested ChromaDB path:**
```bash
rg --no-ignore --hidden -n "tools/knowledge-db/\.groundtruth-chroma" .claude scripts src tests tools docs memory test_host independent-progress-assessments -g "!scripts/archive/**" -g "!docs/archive/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json" -g "!**/__pycache__/**" -g "!independent-progress-assessments/CODEX-INSIGHT-DROPBOX/**"
```
Expected: zero matches.

**Audit C — Dedicated `.claude/` scan:**
```bash
rg --no-ignore --hidden -n "knowledge\.db" .claude -g "!**/*last-context.json" -g "!**/__pycache__/**"
```
Expected: zero matches after Phase 4.

### V8. Directory audit of `tools/knowledge-db/`
```bash
ls tools/knowledge-db/knowledge.db* 2>/dev/null && echo "BLOCKER" || echo "OK: no stale DB"
ls -d tools/knowledge-db/.groundtruth-chroma 2>/dev/null && echo "BLOCKER" || echo "OK: no stale chroma"
```

### V9. Root file state
```bash
git check-ignore -v groundtruth.db .groundtruth-chroma groundtruth.db.pre-backfill-20260412-135740
# Expected: groundtruth.db NOT ignored, .groundtruth-chroma IS ignored, pre-backfill IS ignored
```

### V10. Docker context verification

**Step 1 — Pattern inspection:**
```bash
rg -n "groundtruth|\.groundtruth-chroma|tools/knowledge-db" .dockerignore
```

**Step 2 — Docker-aware proof:**
```bash
cat > /tmp/Dockerfile.dbcheck <<'EOF'
FROM scratch
COPY groundtruth.db /test-db
EOF
docker build -f /tmp/Dockerfile.dbcheck -t dbcheck-test . 2>&1 | head -10
# Expected: COPY fails (file excluded by .dockerignore)
rm -f /tmp/Dockerfile.dbcheck
docker rmi dbcheck-test 2>/dev/null || true
```

### V11. Loyal Opposition tool verification (addresses NO-GO #6 finding 1)
```bash
python independent-progress-assessments/tools/project_progress_snapshot.py --help 2>&1 | head -3
# Expected: starts without "Knowledge DB not found" error

python independent-progress-assessments/export_specifications_csv.py --help 2>&1 | head -3
# Expected: starts without FileNotFoundError
```

## Follow-up Actions (post-migration, separate tasks)

1. **Update GitHub wiki source** — `wiki/Specifications.md` and `wiki/Developer-Onboarding.md` reference `tools/knowledge-db/knowledge.db`. Update the GitHub wiki remote to reference `groundtruth.db`. Low priority, documentation-only.

## Rollback

```bash
git mv groundtruth.db tools/knowledge-db/knowledge.db
mv .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma
mv groundtruth.db.pre-backfill-20260412-135740 tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740
git checkout -- tools/knowledge-db/groundtruth.toml tools/knowledge-db/db.py .gitignore .dockerignore
```

## Risk Assessment

- **Low risk:** Mechanical rename, bounded audit proven to complete in <1s
- **No runtime impact:** Production code uses db.py shim
- **No Docker impact:** `.dockerignore` excludes root KB assets; Docker build test verifies
- **LO tools:** Updated defaults prevent hard errors after migration
- **Wiki:** Excluded (separate repo), follow-up documented
