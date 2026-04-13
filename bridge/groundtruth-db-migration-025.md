# Post-Implementation Report: groundtruth-db-migration

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-13
**Work Item:** WI-3168
**Source Spec:** SPEC-2098
**GO version:** bridge/groundtruth-db-migration-024.md
**Implementation scope:** bridge/groundtruth-db-migration-015.md (Phases 1–5), -019.md (V8/V11), -023.md (Phase 1i/checkpoint)

## Summary

Migrated the Agent Red Knowledge Database from `tools/knowledge-db/knowledge.db` to `groundtruth.db` at the repository root. Moved ChromaDB semantic search index from `tools/knowledge-db/.groundtruth-chroma/` to `.groundtruth-chroma/` at root. Updated all active scripts, tests, Claude tooling, and documentation.

## Implementation Evidence

### Phase 1i: WAL Checkpoint (prerequisite)
- **Checkpoint result:** `(busy=0, log=0, checkpointed=0)`
- **WAL size after checkpoint:** 0 bytes (file absent after TRUNCATE)
- **Script exit:** 0 (PASS)
- Sidecars deleted after PASS: `knowledge.db-shm`, `knowledge.db-wal`

### Phase 1a: Database move
- `git mv tools/knowledge-db/knowledge.db groundtruth.db` — success

### Phase 1b: ChromaDB move
- `mv tools/knowledge-db/.groundtruth-chroma .groundtruth-chroma` — success

### Phase 1c: groundtruth.toml
- `db_path = "../../groundtruth.db"`, `chroma_path = "../../.groundtruth-chroma"` — updated

### Phase 1d: db.py shim
- `DB_PATH = Path(__file__).resolve().parent.parent.parent / "groundtruth.db"` — updated

### Phase 1e: .gitignore
- Removed: `groundtruth.db` (line 109), `tools/knowledge-db/knowledge.db.backup-*` (line 222)
- Added: `groundtruth.db.backup-*`, `groundtruth.db.pre-backfill-*`, `.groundtruth-chroma/`

### Phase 1f: Backup relocation
- `mv tools/knowledge-db/knowledge.db.pre-backfill-20260412-135740 groundtruth.db.pre-backfill-20260412-135740` — success

### Phase 1h: .dockerignore
- Added: `groundtruth.db`, `groundtruth.db.backup-*`, `groundtruth.db.pre-backfill-*`, `.groundtruth-chroma/`

### Phase 2: Active scripts (15 files updated)
- `src/quality_metrics/normalize.py` (lines 55, 86)
- `scripts/harvest_session_deliberations.py` (lines 24, 48, 509)
- `scripts/verify_all_specs.py` (line 17)
- `scripts/s174_kb_artifacts.py` (line 13)
- `scripts/resolve_batch_wis_s117.py` (line 131)
- `scripts/backfill_lo_reports.py` (lines 375, 666)
- `scripts/kb_linkage_repair.py` (line 24)
- `scripts/insert_batch6_coverage_s112.py` (line 23)
- `scripts/deliberation_health.py` (lines 31, 254)
- `scripts/_insert_s136_prompt.py` (line 6)
- `tools/knowledge-db/seed.py` (lines 587, 603)
- `independent-progress-assessments/tools/project_progress_snapshot.py` (line 28)
- `independent-progress-assessments/export_specifications_csv.py` (lines 24, 145)

### Phase 3: Tests (7 files updated)
- `tests/unit/test_deliberation_search.py` (lines 8-9, 24, 25, 30)
- `tests/transport/test_production_gate.py` (lines 348, 398)
- `tests/transport/test_governance_integrity.py` (lines 50, 52 — `test_groundtruth.db`)
- `tests/multi_tenant/test_s153_future_feature_verification.py` (line 23)
- `tests/multi_tenant/test_s153_batch12_spec_verification.py` (line 28)
- `tests/multi_tenant/test_s153_batch11_spec_verification.py` (line 25)
- `tests/multi_tenant/test_s153_testing_quality_specs.py` (line 22)

### Phase 4: Claude tooling (7 files updated)
- `.claude/commands/open-items.md` (line 13)
- `.claude/skills/kb-assert/SKILL.md` (line 35)
- `.claude/skills/kb-query/SKILL.md` (line 20)
- `.claude/commands/check-db.md` (line 11)
- `.claude/hooks/assertion-check.py` (line 520 — uses `PROJECT_DIR / "groundtruth.db"`)
- `.claude/settings.local.json` (lines 72, 78)

### Phase 5: Documentation (6 files updated)
- `CLAUDE.md` (line 74)
- `CLAUDE-ARCHITECTURE.md` (line 225)
- `docs/operations/session-wrap-up-procedure.md` (line 15)
- `sonar-project.properties` (line 15)
- `docs/specification-scaffold/SPEC-TEMPLATE.md` (line 120)
- `docs/specification-scaffold/README.md` (line 24)

## Verification Results

| Check | Result | Evidence |
|-------|--------|----------|
| V1: Git tracking | PASS | `groundtruth.db` tracked, `tools/knowledge-db/knowledge.db` removed from index |
| V2: Smoke test | PASS | `KnowledgeDB()` loads: 2,105 specs, 11,055 tests, 705 deliberations |
| V3: Web UI | SKIPPED | Manual verification (port 8090) |
| V4: Semantic search | PASS | 5 results for "credential scan" query |
| V5: Test suite | **PASS — 16/16 passed** | `test_deliberation_search.py` all green, not skipped |
| V6: Assertion hook | PASS | Quality Dashboard 92.1/100, DCL 4/4 passing |
| V7 Audit A | PASS | 3 matches, all allowed survivors: `db.py:10`, `suites.py:97`, `work_list.md:11` |
| V7 Audit B | PASS | 0 matches (nested ChromaDB) |
| V7 Audit C | PASS | 0 matches (`.claude/` clean) |
| V8: Directory audit | PASS | No `knowledge.db*`, no `groundtruth.db*`, no `.groundtruth-chroma`, no sidecars under `tools/knowledge-db/` |
| V9: Root file state | PASS | `groundtruth.db` NOT ignored, `.groundtruth-chroma` ignored, pre-backfill ignored |
| V10 Step 1 | PASS | All 5 `.dockerignore` entries present |
| V10 Step 2 | SKIPPED | Docker daemon not running; pattern inspection passed |
| V11 Probe A | PASS | `KB_PATH=E:\...\groundtruth.db`, 2,105 current specs |
| V11 Probe B | PASS | `DEFAULT_DB_PATH=E:\...\groundtruth.db`, 2,105 current specs |

## Follow-up Actions

1. **Wiki-wide KB path audit** — 6+ files in `wiki/` and `agent-red.wiki/` reference `tools/knowledge-db/knowledge.db`. Update GitHub wiki source of truth. Known files: `Specifications.md`, `Developer-Onboarding.md`, `Knowledge-Database.md`, `Groundtruth-KB-Hygiene.md`, `Specification-Intake-Procedure.md`, `Specification-Format-and-Template.md`.

## Not changed (per proposal)

- `scripts/archive/` (~20 files) — historical
- `bridge/` files — audit trail
- `docs/archive/`, `MEMBASE-4-CLAUDE.md`, `docs/owner-messages-all.json` — frozen historical
- `.claude/hooks/.prime-bridge-wake-last-context.json` — transient cache
- `wiki/`, `agent-red.wiki/` — separate git repositories
- `tools/knowledge-db/` allowed survivors: `bridge.db` (0 bytes), `knowledge-export-*.json`, `create_s259_wis.py`
