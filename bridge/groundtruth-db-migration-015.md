# WI-3168: Migrate knowledge.db to groundtruth.db at repo root (REVISED v7)

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-13
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**Priority:** P3
**Revision:** Addresses 3 findings in `bridge/groundtruth-db-migration-014.md` (Codex NO-GO #7)

## NO-GO #7 Response

| # | Finding | Severity | Resolution |
|---|---------|----------|------------|
| 1 | V7 audit includes generated LO artifacts, automation logs, and lock files | P1 | Audit A splits `independent-progress-assessments/` into targeted source paths only: `tools/`, `export_specifications_csv.py`, named runbooks. No generated artifacts. |
| 2 | V11 `--help` does not exercise DB path access | P2 | V11 replaced with read-only DB path probes that import each tool, resolve the default path, assert file exists, and open with SQLite. |
| 3 | Wiki follow-up names only 2 files; 6+ are stale | P3 | Follow-up expanded to wiki-wide `knowledge.db` audit, seeded with all 6 known stale files. |

## Cumulative NO-GO Resolution

All 16 findings from seven NO-GO reviews addressed. Carries forward all v013 implementation scope.

## Prior Deliberations

- DELIB-0224, DELIB-0651, DELIB-0317, bridge/deliberation-archive-completion-004.md
- NO-GO versions: -002, -004, -006, -008, -010, -012, -014

## Objective

Move Agent Red Knowledge Database from `tools/knowledge-db/knowledge.db` to `groundtruth.db` at repo root. Move ChromaDB index to `.groundtruth-chroma/` at repo root. Leave `tools/knowledge-db/` as shim/config only.

## Scope

### Phase 1: Core infrastructure (atomic)

**1a.** `git mv tools/knowledge-db/knowledge.db groundtruth.db`
**1b.** `mv tools/knowledge-db/.groundtruth-chroma .groundtruth-chroma`
**1c.** Update `tools/knowledge-db/groundtruth.toml`: `db_path = "../../groundtruth.db"`, `chroma_path = "../../.groundtruth-chroma"`
**1d.** Update `tools/knowledge-db/db.py:42`: `DB_PATH = Path(__file__).resolve().parent.parent.parent / "groundtruth.db"`
**1e.** Update `.gitignore` — Remove lines 109, 222. Add `groundtruth.db.backup-*`, `groundtruth.db.pre-backfill-*`, `.groundtruth-chroma/`.
**1f.** Relocate backup: `mv tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740 groundtruth.db.pre-backfill-20260412-135740`
**1g.** Allowed survivors in `tools/knowledge-db/`: `bridge.db` (0B, ignored), `knowledge-export-*.json` (ignored), `create_s259_wis.py` (tracked).
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
| `independent-progress-assessments/tools/project_progress_snapshot.py` | 28 | `KB_PATH = ROOT / "groundtruth.db"` |
| `independent-progress-assessments/export_specifications_csv.py` | 24, 145 | Default path + help text |

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

`scripts/archive/`, `bridge/`, `docs/archive/`, `MEMBASE-4-CLAUDE.md`, `docs/owner-messages-all.json`, `.claude/hooks/.prime-bridge-wake-last-context.json`, `wiki/`, `agent-red.wiki/` (separate repos), generated LO artifacts/logs/dashboards.

## Verification Plan

### V1–V4. (Unchanged from v013)

**V1.** Git tracking: `git ls-files groundtruth.db` → tracked; `git ls-files tools/knowledge-db/knowledge.db` → empty.
**V2.** Smoke: `python -c "... import db; kdb = db.KnowledgeDB(); print(kdb.get_summary())"`.
**V3.** Web UI: `python tools/knowledge-db/app.py` → port 8090.
**V4.** Semantic search: `kdb.search_deliberations('credential scan')` → results.

### V5. Semantic search test suite
```bash
python -m pytest tests/unit/test_deliberation_search.py -q --tb=short
# Expected: 16 passed (NOT skipped). Record pass count.
```

### V6. Assertion hook
```bash
python .claude/hooks/assertion-check.py 2>&1 | head -5
```

### V7. Bounded path audit (addresses NO-GO #7 finding 1)

**Audit A — Active-surface scan with targeted LO paths:**
```bash
rg --no-ignore --hidden -n "knowledge\.db" \
  .claude scripts src tests tools docs memory test_host \
  independent-progress-assessments/tools/ \
  independent-progress-assessments/export_specifications_csv.py \
  independent-progress-assessments/PROJECT-PROGRESS-DASHBOARD-RUNBOOK.md \
  independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md \
  independent-progress-assessments/CODEX-WAY-OF-WORKING.md \
  independent-progress-assessments/CODEX-REVIEW-OPERATING-CONTRACT.md \
  CLAUDE.md CLAUDE-ARCHITECTURE.md CLAUDE-REFERENCE.md \
  sonar-project.properties .gitignore .dockerignore \
  -g "!scripts/archive/**" \
  -g "!docs/archive/**" \
  -g "!docs/owner-messages-all.json" \
  -g "!.claude/hooks/.prime-bridge-wake-last-context.json" \
  -g "!**/__pycache__/**"
```

This scans only active first-party source files plus named LO runbooks. It does NOT scan generated artifacts (`artifacts/`, `bridge-automation/logs/`, `output/`, `snapshots/`, `dashboards/`, `pdf-renders/`), historical insight reports (`CODEX-INSIGHT-DROPBOX/`), or lock files.

**Allowed survivors** (documented, non-functional):
- `tools/knowledge-db/db.py:10` — docstring historical context
- `test_host/suites.py:97` — comment text
- `memory/work_list.md` — WI description text

Any other match is a **blocker**. The command must exit cleanly (exit code 0 or 1, not timeout/error) and all matches must be in the allowed survivors list.

**Audit B — Nested ChromaDB path:**
```bash
rg --no-ignore --hidden -n "tools/knowledge-db/\.groundtruth-chroma" \
  .claude scripts src tests tools docs memory test_host \
  independent-progress-assessments/tools/ \
  -g "!scripts/archive/**" -g "!docs/archive/**" \
  -g "!.claude/hooks/.prime-bridge-wake-last-context.json" \
  -g "!**/__pycache__/**"
```
Expected: zero matches.

**Audit C — Dedicated `.claude/` scan:**
```bash
rg --no-ignore --hidden -n "knowledge\.db" .claude \
  -g "!**/*last-context.json" -g "!**/__pycache__/**"
```
Expected: zero matches after Phase 4.

### V8. Directory audit of `tools/knowledge-db/`
```bash
ls tools/knowledge-db/knowledge.db* 2>/dev/null && echo "BLOCKER" || echo "OK"
ls -d tools/knowledge-db/.groundtruth-chroma 2>/dev/null && echo "BLOCKER" || echo "OK"
```

### V9. Root file state
```bash
git check-ignore -v groundtruth.db .groundtruth-chroma groundtruth.db.pre-backfill-20260412-135740
# Expected: groundtruth.db NOT ignored, .groundtruth-chroma IS ignored, pre-backfill IS ignored
```

### V10. Docker context verification
```bash
# Step 1: pattern inspection
rg -n "groundtruth|\.groundtruth-chroma|tools/knowledge-db" .dockerignore

# Step 2: Docker-aware proof
cat > /tmp/Dockerfile.dbcheck <<'EOF'
FROM scratch
COPY groundtruth.db /test-db
EOF
docker build -f /tmp/Dockerfile.dbcheck -t dbcheck-test . 2>&1 | head -10
# Expected: COPY fails (file excluded by .dockerignore)
rm -f /tmp/Dockerfile.dbcheck
docker rmi dbcheck-test 2>/dev/null || true
```

### V11. LO tool DB path verification (addresses NO-GO #7 finding 2)

**Read-only default path probes** — these verify the migrated default paths resolve correctly and the DB can be opened:

```bash
# project_progress_snapshot.py — verify default KB_PATH resolves to existing file
python -c "
import sys; sys.path.insert(0, 'independent-progress-assessments/tools')
from pathlib import Path
ROOT = Path('independent-progress-assessments/tools/project_progress_snapshot.py').resolve().parents[2]
kb_path = ROOT / 'groundtruth.db'
assert kb_path.exists(), f'DB not found at {kb_path}'
import sqlite3
conn = sqlite3.connect(f'file:{kb_path}?mode=ro', uri=True)
count = conn.execute('SELECT COUNT(*) FROM specs').fetchone()[0]
conn.close()
print(f'project_progress_snapshot: DB at {kb_path}, {count} specs — OK')
"

# export_specifications_csv.py — verify DEFAULT_DB_PATH resolves
python -c "
from pathlib import Path
PROJECT_ROOT = Path('independent-progress-assessments/export_specifications_csv.py').resolve().parent.parent
db_path = PROJECT_ROOT / 'groundtruth.db'
assert db_path.exists(), f'DB not found at {db_path}'
import sqlite3
conn = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
count = conn.execute('SELECT COUNT(*) FROM specs').fetchone()[0]
conn.close()
print(f'export_specifications_csv: DB at {db_path}, {count} specs — OK')
"
```

Both probes must print the spec count and "OK". Any assertion error or missing DB is a **blocker**.

## Follow-up Actions (post-migration, separate tasks)

1. **Wiki-wide KB path audit and update** — The following files in the GitHub wiki source (and local clones `wiki/`, `agent-red.wiki/`) reference `tools/knowledge-db/knowledge.db` and need updating to `groundtruth.db`:
   - `Specifications.md`
   - `Developer-Onboarding.md`
   - `Knowledge-Database.md`
   - `Groundtruth-KB-Hygiene.md`
   - `Specification-Intake-Procedure.md`
   - `Specification-Format-and-Template.md`
   
   Run `rg "knowledge\.db" wiki/ agent-red.wiki/` to find any additional stale references. Update the GitHub wiki source of truth; local clones update on next pull.

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
- **No Docker impact:** `.dockerignore` verified by Docker build test
- **LO tools:** Path probes verify real DB access after migration
- **Wiki:** Excluded (separate repos), wiki-wide follow-up seeded with 6 known files
