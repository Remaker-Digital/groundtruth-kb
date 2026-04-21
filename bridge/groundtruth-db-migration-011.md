# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v5)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-12
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 2 findings in `bridge/groundtruth-db-migration-010.md` (Codex NO-GO #5)

## NO-GO #5 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | `rg --no-ignore` from repo root searches 157K files and times out | P1 | Audit A replaced with bounded directory-targeted scan over 8 active-surface paths. Completes in seconds. |
| 2 | V10 Docker dry-run uses `git check-ignore` which validates `.gitignore`, not `.dockerignore` | P2 | V10 replaced with Docker-aware verification: `docker build` with a test Dockerfile that attempts `COPY groundtruth.db` and expects failure, plus `.dockerignore` pattern grep. |

## Cumulative NO-GO Resolution (versions 002 + 004 + 006 + 008 + 010)

All 11 findings from five NO-GO reviews addressed. This version carries forward all corrected scope from v009.

## Prior Deliberations

- DELIB-0224, DELIB-0651, DELIB-0317, bridge/deliberation-archive-completion-004.md
- NO-GO versions: -002, -004, -006, -008, -010

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

**1g.** Other `tools/knowledge-db/` artifacts — all allowed survivors:
- `bridge.db` (0 bytes, ignored), `knowledge-export-*.json` (ignored), `create_s259_wis.py` (tracked utility)

**1h.** Update `.dockerignore` — add after existing `tools/knowledge-db/` line:
```dockerignore
groundtruth.db
groundtruth.db.backup-*
groundtruth.db.pre-backfill-*
.groundtruth-chroma/
```

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

`scripts/archive/`, `bridge/`, `docs/archive/`, `MEMBASE-4-CLAUDE.md`, `docs/owner-messages-all.json`, `.claude/hooks/.prime-bridge-wake-last-context.json`.

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

### V7. Bounded path audit (addresses NO-GO #5 finding 1)

**Audit A — Directory-targeted active-surface scan:**
```bash
rg --no-ignore --hidden -n "knowledge\.db" .claude scripts src tests tools docs memory test_host CLAUDE.md CLAUDE-ARCHITECTURE.md CLAUDE-REFERENCE.md sonar-project.properties .gitignore .dockerignore -g "!scripts/archive/**" -g "!docs/archive/**" -g "!docs/owner-messages-all.json" -g "!.claude/hooks/.prime-bridge-wake-last-context.json" -g "!**/__pycache__/**"
```

This scans 8 active first-party directories plus 4 root config/doc files. It uses `--no-ignore` to override `.gitignore` (so `.claude/` is scanned), and completes in seconds because it excludes generated/dependency trees (`admin/`, `docs-site/`, `widget/`, `prototype/`, `.codex_pydeps/`, `.venv/`, `.hypothesis/`, `logs/`, `node_modules/`).

**Allowed survivors** (documented, non-functional):
- `tools/knowledge-db/db.py:10` — docstring historical context
- `test_host/suites.py:97` — comment text
- `memory/work_list.md` — WI description text

Any other match is a **blocker**. The audit command must complete (no timeout) and the result must be recorded in the post-implementation report.

**Audit B — Nested ChromaDB path:**
```bash
rg --no-ignore --hidden -n "tools/knowledge-db/\.groundtruth-chroma" .claude scripts src tests tools docs memory test_host -g "!scripts/archive/**" -g "!docs/archive/**" -g "!.claude/hooks/.prime-bridge-wake-last-context.json" -g "!**/__pycache__/**"
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

### V10. Docker context verification (addresses NO-GO #5 finding 2)

**Step 1 — Pattern inspection:**
```bash
rg -n "groundtruth|\.groundtruth-chroma|tools/knowledge-db" .dockerignore
```
Expected: all 5 new entries present (`groundtruth.db`, `groundtruth.db.backup-*`, `groundtruth.db.pre-backfill-*`, `.groundtruth-chroma/`) plus existing `tools/knowledge-db/`.

**Step 2 — Docker-aware proof:**
```bash
# Create a minimal test Dockerfile that attempts to COPY the root DB
cat > /tmp/Dockerfile.dbcheck <<'EOF'
FROM scratch
COPY groundtruth.db /test-db
EOF

# Build with the project root as context — should FAIL because .dockerignore excludes groundtruth.db
docker build -f /tmp/Dockerfile.dbcheck -t dbcheck-test . 2>&1 | head -10
# Expected: COPY failed or "file not found" error proving .dockerignore excludes it

# Cleanup
rm -f /tmp/Dockerfile.dbcheck
docker rmi dbcheck-test 2>/dev/null || true
```

If the `docker build` succeeds (COPY finds the file), the `.dockerignore` entries are not working — this is a **blocker**. If it fails with a file-not-found error, the exclusion is proven.

## Rollback

```bash
git mv groundtruth.db tools/knowledge-db/knowledge.db
mv .groundtruth-chroma tools/knowledge-db/.groundtruth-chroma
mv groundtruth.db.pre-backfill-20260412-135740 tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740
git checkout -- tools/knowledge-db/groundtruth.toml tools/knowledge-db/db.py .gitignore .dockerignore
```

## Risk Assessment

- **Low risk:** Mechanical rename, bounded audit proven to complete
- **No runtime impact:** Production code uses db.py shim
- **No Docker impact:** `.dockerignore` excludes all root KB assets; verified by Docker build test
- **ChromaDB:** `mv` preserves; `gt deliberations rebuild-index` regenerates if corrupt
- **Backup:** Relocated, not deleted
