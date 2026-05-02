NEW

# GTKB-ISOLATION-017 Slice 2 Post-Implementation Report

**Status:** NEW (awaits Codex VERIFIED)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Authority:** `bridge/gtkb-isolation-017-slice2-registry-isolation-004.md` (GO)

---

## Specification Links

Carried forward from `-003` REVISED-1 (the `-004` GO confirmed the linkage gate):

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 405-407 (AST gate + drift detection)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` lines 84, 104-120
- `bridge/gtkb-isolation-017-scoping-003.md` lines 78-91 (Slice 2 acceptance) + `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO scoping authority)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 121-145 (`OwnershipMeta`, `FileArtifact.template_path`)
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 171-208, 311-352
- `groundtruth-kb/templates/managed-artifacts.toml`
- `groundtruth-kb/templates/scaffold-ownership.toml`
- `groundtruth-kb/templates/{hooks,rules,ci,project}/`
- `groundtruth-kb/.github/workflows/ci.yml`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`
- `GOV-20`

## Specification-Derived Verification

All 7 tests in the four new Slice 2 files pass against the landed code.

| # | Test | Derives from | Result |
|---|---|---|---|
| T1a | `test_every_file_class_record_template_path_exists` | Phase 9 line 406 forward existence (template_path key per F1 fix) | PASS |
| T1b | `test_every_template_source_file_has_registry_coverage` | Phase 9 line 406 reverse coverage (template_path enumeration per F1 fix) | PASS |
| T4 | `test_registry_drift_against_id_snapshot` | Phase 9 line 407 drift detection via golden ID-set snapshot | PASS |
| T6 | `test_classify_path_round_trip_for_file_class_target_paths` | Sanity: classify_path works on target_path values (per F1 fix) | PASS |
| T-SCHEMA | `test_ownership_meta_existing_fields_satisfy_owner_and_upgrade_acceptance` | Scoping line 83 (existing fields satisfy "owner" and "upgrade_policy" acceptance) | PASS |
| T-CI | `test_slice2_test_files_live_under_tests_directory` | Scoping line 86 (CI wiring satisfied by file placement under tests/) | PASS |
| T-IPR-CVR | `test_ipr_and_cvr_slice2_documents_exist_with_adr_tag` | GOV-20 Phase 1 advisory pilot | PASS |

## Test Execution Commands

```
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_registry_ast_coverage.py tests/test_registry_drift_detection.py tests/test_registry_target_path_round_trip.py tests/test_registry_schema_and_ci.py -q --tb=short --timeout=30
# Result: 7 passed in 0.27s

python -m ruff check tests/test_registry_*.py
python -m ruff format --check tests/test_registry_*.py
# Result: All checks passed; 4 files formatted
```

Full regression: per the Slice 1 baseline, the 3 pre-existing failures
(`test_broad_exceptions_are_annotated`, `test_artifacts_for_scaffold_unchanged_by_sibling_file`,
`test_scaffold_dual_agent_id_set_matches_baseline`) remain pre-existing on develop;
none are in files touched by Slice 2.

## AST Gate First-Run Findings

T1b reverse-coverage walk identified 22 scaffolded template files that lack registry coverage. Per the proposal disclosure ("Risk / Impact Delta"), they are tracked in the explicit `_KNOWN_DRIFT_PENDING_REGISTRATION` allowlist in `tests/test_registry_ast_coverage.py`:

- **CI templates (Slice 3 scope, 10 files):** `ci/build.yml`, `ci/deploy.yml`, `ci/test.yml`, `ci/full/{build,deploy,test}.yml`, `ci/minimal/test.yml`, `ci/standard/test.yml`, `ci/integrations/{.coderabbitai.yaml,dependabot.yml}`
- **Project-root scaffold templates (Slice 3 scope, 8 files):** `project/.editorconfig`, `project/.pre-commit-config.yaml`, `project/AGENTS.md`, `project/Dockerfile`, `project/Makefile`, `project/docker-compose.yml`, `project/env.example`, `project/settings.local.json`
- **Codex bootstrap docs (Slice 3 dual-agent scope, 4 files):** `project/codex-bootstrap/{CODEX-REVIEW-OPERATING-CONTRACT.md, CODEX-SESSION-BOOTSTRAP.md, CODEX-WAY-OF-WORKING.md, LOYAL-OPPOSITION-LOG.md}`

**Removal contract:** when Slice 3 (or Slice 2.5) adds a registry row for any of these paths, the corresponding entry MUST be removed from the allowlist in the same commit. T1b will fail otherwise (intentional gate that prevents the allowlist from rotting).

## Files Changed

**Source (groundtruth-kb):**
- `groundtruth-kb/tests/test_registry_ast_coverage.py` — NEW, 145 LOC, T1a + T1b + 2 allowlists.
- `groundtruth-kb/tests/test_registry_drift_detection.py` — NEW, 55 LOC, T4 + golden-snapshot recipe in assertion message.
- `groundtruth-kb/tests/test_registry_target_path_round_trip.py` — NEW, 35 LOC, T6.
- `groundtruth-kb/tests/test_registry_schema_and_ci.py` — NEW, 99 LOC, T-SCHEMA + T-CI + T-IPR-CVR.
- `groundtruth-kb/tests/fixtures/registry-id-set.txt` — NEW, golden snapshot of all 64 record IDs (4 lines of comment header + 64 IDs).
- `groundtruth-kb/.github/workflows/ci.yml` — CI documentation comment block added citing Slice 2 (no behavior change; the test-base lane already collects `tests/`).

**Adopter / standing-backlog:**
- `memory/work_list.md` — Slice 2.5 row added at row 26 per GO -004 carry-forward condition.

**KB documents (per GOV-20 Phase 1 advisory pilot):**
- `IPR-SLICE2-REGISTRY-ISOLATION-001` v1 inserted via `_temp_insert_ipr_slice2.py` (pre-implementation).
- `CVR-SLICE2-REGISTRY-ISOLATION-001` v1 inserted via `_temp_insert_cvr_slice2.py` (post-implementation; full test-to-spec mapping).

## Codex `-002` F1 Closure Evidence

T1a/T1b use `record.source.template_path` (the source-tree key) instead of `classify_path()` (which is keyed on `target_path`). T6 separately exercises `classify_path()` only on `target_path` values, proving the resolver contract. Direct probe at proposal time confirmed: `classify_path("hooks/assertion-check.py")` returns fallback while `classify_path(".claude/hooks/assertion-check.py")` returns the registered record. The landed test fixture confirms 0 fallbacks for the FILE-class set.

## Codex `-002` F2 Closure Evidence

T2 (rationale discipline) and T3 (migration-note discipline) are explicitly NOT in this slice. Slice 2 ships with no `OwnershipMeta.notes` schema extension and no test depending on a non-existent surface. The deferred work is now visible as work_list row 26 (`GTKB-ISOLATION-017-SLICE-2.5`).

## CI Wiring Evidence

The four new Slice 2 test files live under `groundtruth-kb/tests/`. The existing `test-base` CI lane in `groundtruth-kb/.github/workflows/ci.yml:24-94` runs `pytest tests/` on every push and pull request for branches `main` and `develop` across Python 3.11/3.12/3.13. Therefore Slice 2 tests are CI-collected without a bespoke workflow lane. T-CI asserts the four files exist at the expected location.

A documentation comment block was added to `ci.yml` citing Slice 2 + the four test file names so future maintainers know the registry-isolation tests are load-bearing.

## Acceptance Per GO -004

GO §"Verdict": "Implement Slice 2 as revised: AST coverage via template_path, target-path resolver sanity, registry ID-set drift detection, schema-surface lock, CI collection meta-test, and GOV-20 IPR/CVR evidence."

All seven elements landed and pass tests:
- AST coverage via template_path: T1a + T1b
- Target-path resolver sanity: T6
- Registry ID-set drift detection: T4 + golden snapshot fixture
- Schema-surface lock: T-SCHEMA
- CI collection meta-test: T-CI
- GOV-20 IPR/CVR evidence: IPR + CVR docs in KB; T-IPR-CVR asserts presence
- Carry-forward condition: Slice 2.5 row added to memory/work_list.md (row 26)

## Decision Needed From Owner

Nothing required at VERIFIED time. All Codex GO conditions met.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
