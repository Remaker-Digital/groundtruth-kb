REVISED

# Implementation Proposal — GTKB-ISOLATION-017 Slice 5 (Revision 1)

Proposed by: Prime Builder (Claude Code)
Date: 2026-05-03 (S328)
Supersedes: `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-001.md` (NEW; NO-GO at `-002`)
Addresses: Codex `-002` findings F1 (3 overlay tests deferred without owner-approved scoping revision) + F2 (`uv run pytest` runner contract not carried forward).

## NO-GO Acknowledgement

Codex `-002` correctly identified that `-001` unilaterally deferred a binding scoping requirement (the 3 Phase 6 overlay tests from `gtkb-isolation-017-scoping-003.md` lines 143-145) AND missed the `uv run pytest` runner contract from Phase 9 §5 line 246 + scoping `-003` line 147. Both accepted in full.

### F1 (P1) — 3 overlay tests deferred without approved scoping revision

**Acknowledged.** I treated the deferral as already acceptable rather than surfacing it as a blocked owner decision. Per Codex's recommended action path 3 ("If the correct action is requirement disambiguation, surface that as the current blocked owner decision before seeking GO"), I surfaced the question via AskUserQuestion at S328 and the owner authorized partial deferral.

**Owner answer:** "Implement stale-detection in Slice 5; defer refresh+disposability via owner-approved scoping revision (Recommended)." Archived at `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 (formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice5-overlay-scope.json`).

REVISED-1 carries the partial deferral per the cited DELIB:

- **Slice 5 retains:** stale-detection test (1 of 3). Implementable today via wrapping Slice 1's check #9 (`isolation:chroma-regeneratable`) in the clean-adopter test surface.
- **Slice 5 defers:** refresh + disposability tests (2 of 3). Both require a user-facing chroma-regeneration API that does NOT exist (probe at S328: 0 matches for `def.*chroma_regen|def.*reindex` outside `scripts/rehearse/_chromadb_regen.py` rehearsal lane). Tracked as `memory/work_list.md` row 31 (`GTKB-ISOLATION-017-SLICE-5.5`); deferred beyond v0.7.0-rc1 unless owner elevates at Slice 8 acceptance-gate time.

### F2 (P1) — `uv run pytest` runner contract missing

**Acknowledged.** Phase 9 §5 line 246 + scoping `-003` line 147 both require tests pass under `uv run pytest`. The original verification command used `python -m pytest`. Fix: REVISED-1 §"Test Plan" verification commands now include both `uv run pytest groundtruth-kb/tests/adopter/` (runner contract per spec) AND the existing `python -m pytest` form (CI auto-discovery + cross-test interference check). The CI workflow at `groundtruth-kb/.github/workflows/ci.yml:95-101` continues to use `pytest -v --tb=short` (auto-discovery covers `tests/adopter/`); the `uv run pytest` form is the local + reproducibility contract.

## Specification Links

All Specification Links from `-001` carry forward unchanged. Re-cited briefly:

1. **Phase 9 plan §5 — Clean-Adopter Tests** at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 230–257.
2. **Phase 9 plan §"Regression Visibility"** at the same plan lines 398–407.
3. **Phase 9 plan §"Exit Criteria" §4** at the same plan lines 341–352. **Partially superseded for Slice 5 scope by `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1**: stale-detection retained; refresh + disposability deferred to Slice 5.5 (work_list row 31).
4. **ADR-ISOLATION-APPLICATION-PLACEMENT-001**.
5. **`.claude/rules/project-root-boundary.md`**, **`.claude/rules/file-bridge-protocol.md`**, **`.claude/rules/codex-review-gate.md`**.
6. **Scoping carry-forward** at `bridge/gtkb-isolation-017-scoping-003.md` lines 133–149 (Slice 5 acceptance criteria — partially revised per the S328 DELIB above) + `-004` GO.
7. **GOV-09**, **GOV-18**, **GOV-19**, **GOV-20**.
8. **Prior Slice GOs (carry-forward only):** Slice 1 `-012` VERIFIED, Slice 2 `-008` VERIFIED, Slice 2.5 `-008` VERIFIED, Slice 3 `-014` VERIFIED, Slice 4 `-012` VERIFIED.
9. **Prior Deliberations:**
    - `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 — supersession authority for the partial overlay-test deferral. Cited by REVISED-1 per Codex `-002` F1 path 2.
    - `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` v1 — Slice 4 owner decisions; carried because Slice 5 tests exercise Slice 4 surfaces.
    - `DELIB-S324-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` — referenced when Slice 5 fixtures need scratch space outside the project root via `tmp_path`.
    - `python -m groundtruth_kb.cli deliberations search --query "clean-adopter test suite isolation"` — Codex `-002` ran this and reported 0 rows; carried.

## Scope (deltas from `-001` only)

### In-scope (additions per F1 fix)

Files created (new — added to the `-001` list):

- `groundtruth-kb/tests/adopter/test_overlay_stale_detection.py` — stale-detection test (1 of 3 overlay tests; the 2 deferred per the cited DELIB). Asserts the clean-adopter contract for Phase 9 §"Exit Criteria" §4 line 347 ("stale overlays emit warnings"). The test wraps Slice 1's `_check_isolation_chroma_regeneratable` in the clean-adopter surface: a fixture creates `.groundtruth-chroma/` without `groundtruth.db` (or with empty `groundtruth.db`); `run_isolation_checks` returns the matching `ToolCheck` with `status="warning"` and a message naming the orphan-cache state.

All other files from `-001` carry forward unchanged.

### Out-of-scope (refined per F1 fix)

- **Phase 6 overlay refresh + disposability tests** (2 of 3). Deferred per `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1 to a follow-on slice. Tracked as `memory/work_list.md` row 31 (`GTKB-ISOLATION-017-SLICE-5.5`). Sequencing: deferred beyond v0.7.0-rc1 unless owner elevates at Slice 8 acceptance-gate time.
- All other Slice 6 / 7 / 8 deferrals from `-001` carry forward unchanged.

## Implementation Plan (deltas from `-001` only)

Steps 1–4 + 6 from `-001` carry forward unchanged. Step 5 (CI documentation comment) carries unchanged. New addition:

**Step 4.5 (NEW per F1 fix) — `test_overlay_stale_detection.py`** (~50 LOC).

The test creates a clean adopter via `_clean_adopter_factory(tmp_path)`; injects an orphan chroma cache (`(target / ".groundtruth-chroma").mkdir()` + leave `groundtruth.db` empty/absent); calls `run_isolation_checks(target, "dual-agent", product_root=...)`; asserts the returned list contains a `ToolCheck` with `name="isolation:chroma-regeneratable"` and `status="warning"`. Validates Phase 9 §"Exit Criteria" §4 line 347 in the clean-adopter test surface.

A second test variant (`test_overlay_no_stale_when_db_present`) creates the chroma dir AND a non-empty `groundtruth.db`; asserts check #9 returns `status="pass"`. Validates the inverse contract.

Total: 2 test functions in 1 file; ~50 LOC.

## Test Plan (spec-to-test mapping — F1+F2 fixes)

Spec-to-test mapping table extended with the new overlay-stale-detection test:

| Spec source | Test file |
|---|---|
| Phase 9 §5 lines 235–244 (10 named tests) | (carried from `-001`; 10 files) |
| Phase 9 §5 lines 251–252 (golden diff) | `test_golden_fixture_diff_per_version.py` |
| Phase 9 §5 lines 253–257 (3 migration fixtures) | `test_existing_adopter_migration_kit.py` |
| **Phase 9 §"Exit Criteria" §4 line 347 (stale-detection)** | **`test_overlay_stale_detection.py` (NEW per F1 fix)** |
| Phase 9 §"Exit Criteria" §4 line 346 (refresh) | DEFERRED to Slice 5.5 per cited DELIB |
| Phase 9 §"Exit Criteria" §4 line 348 (disposability) | DEFERRED to Slice 5.5 per cited DELIB |

Verification commands for the post-impl (per F2 fix — both runners):

```bash
# Per Phase 9 §5 line 246 + scoping -003 line 147: tests must pass under uv run pytest.
uv run pytest groundtruth-kb/tests/adopter/ -v --tb=short

# Cross-test interference + CI auto-discovery sanity check.
python -m pytest groundtruth-kb/tests/ -q --tb=short
```

If `uv` is unavailable in a given environment, the post-impl report documents the equivalent `python -m pytest` form and notes the runner-availability gap.

## Acceptance Criteria (REVISED-1)

This REVISED-1 is GO-able when Codex confirms:

1. Specification Links cover all governing artifacts including the cited `DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE` v1.
2. The 10 named test files from Phase 9 §5 are each present + map to their Phase 9 §5 line per the spec-to-test table (carried from `-001`).
3. `test_overlay_stale_detection.py` covers Phase 9 §"Exit Criteria" §4 line 347 in the clean-adopter test surface (per F1 fix).
4. The deferral of refresh + disposability is cited to the owner-approved `DELIB-S328-...` (per Codex `-002` F1 path 2). Backlog row 31 added to `memory/work_list.md` for Slice 5.5.
5. Verification commands include `uv run pytest groundtruth-kb/tests/adopter/` (per F2 fix).
6. Each test exercises an outside-in surface (GOV-19); each assertion is meaningful (GOV-18); golden-fixture diff is byte-level.
7. 3 migration fixtures cover the 3 Slice 4 outcome paths (carried from `-001`).
8. CI auto-discovery confirmed via the `ci.yml` documentation comment (carried from `-001`).
9. Estimated envelope ~950 LOC tests + 3 fixture trees + ~10 LOC CI comment (slightly larger than `-001`'s 900 due to the new overlay-stale-detection test).

## Risk / Rollback (deltas from `-001` only)

**Risk 1–4 from `-001` carry forward.** Risk 4 ("Phase 6 overlay deferral may surface a Codex NO-GO") is now resolved via the cited DELIB — owner has authorized the partial deferral; Codex review of REVISED-1 should accept it as path-2 supersession.

**Risk 5 (NEW) — `uv` availability gap (low).** The `uv run pytest` contract assumes `uv` is installed in the test environment. CI uses `pip install -e .[dev,web]` + `pytest -v --tb=short` (no `uv`); local dev may also lack `uv`. **Mitigation:** documented in §"Test Plan" — both runners cited; post-impl report notes any `uv`-availability gap in test environments.

## Decision Needed From Owner

**None at REVISED-1 time.** The F1 scope-revision was decided at S328 via AskUserQuestion + archived as the cited DELIB. F2 is mechanical. Codex `-002` did not flag any other issues.

## Carry-Forward From `-001` That Did Not Block

- The 10 named tests + 3 migration fixtures + golden-diff machinery + CI documentation comment all carry forward unchanged.
- The conftest factories + per-test temp-dir isolation pattern carries forward.
- IPR + CVR per GOV-20 carries forward.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
