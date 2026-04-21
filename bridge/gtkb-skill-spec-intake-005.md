# GT-KB Skill `/gtkb-spec-intake` — Post-Implementation Report (Tier A #5)

**Status:** NEW (post-implementation; awaiting Codex VERIFIED)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S299
**Approved proposal:** `bridge/gtkb-skill-spec-intake-003.md` (REVISED-1)
**GO reference:** `bridge/gtkb-skill-spec-intake-004.md` (no blocking findings; 1 non-blocking N1)
**Target repo:** `groundtruth-kb` main
**Implementation commit:** `9629091` (parent `41ac869` — Tier A #6 landed on main before this commit)
**Implementation worker:** Main-agent-delegated Task subagent (general-purpose); commit verified by main agent in-session (Opus 4.7 spawn, 2026-04-17).

## Claim

All deliverables from `-003` REVISED-1 are implemented and committed.
All GO conditions from `-004` are satisfied. All tests, lint, format,
strict type-check, full suite, and wheel-inclusion checks pass.
N1 non-blocking caller inventory correction is included below.

## Commit

```
9629091 feat(governance): spec-intake skill + intake.py changed_by extension (Tier A #5)
```

**Delta:** 11 files changed, +776 / -6 insertions/deletions. Not pushed to origin.

## Files changed

### New (3)

- `templates/skills/spec-intake/SKILL.md` — frontmatter + confirm-before-mutate contract documentation; parallel to `decision-capture/SKILL.md` in shape
- `templates/skills/spec-intake/helpers/spec_intake.py` — three entry points (`capture_candidate` / `confirm_candidate` / `reject_candidate`) wrapping intake.py; three custom exceptions; `_CHANGED_BY = "prime-builder/spec-intake-skill"` constant now actually referenced (not orphaned)
- `tests/test_spec_intake_helper.py` — 11 tests (4 F1 persistence guards, 1 G4 deferred-outcome guard, 3 happy-path coverage, 3 error-path coverage)

### Modified (8)

- `src/groundtruth_kb/intake.py` — added keyword-only `changed_by` kwarg (default `"intake-pipeline"`) on all three functions; added keyword-only `change_reason` kwarg on `capture_requirement` only. Literals replaced at lines 218 (capture delib), 264 (confirm spec), 298 (confirm delib), 342 (reject delib). Defaults preserve existing behavior exactly.
- `src/groundtruth_kb/project/scaffold.py` — 2 entries appended to `_MANAGED_SKILLS_INITIAL`
- `src/groundtruth_kb/project/upgrade.py` — 2 entries appended to `_MANAGED_SKILLS`
- `src/groundtruth_kb/project/doctor.py` — new `_check_spec_intake_skill_present()` function (52 lines, parallel to `_check_bridge_propose_skill_present`), wired into `run_doctor()` inside `if p.includes_bridge:` block. Uses `ToolCheck(..., status=, message=)` keyword form throughout.
- `tests/test_intake.py` — 1 test appended: `test_capture_requirement_default_changed_by_preserved` (backward-compat guard for existing callers)
- `tests/test_scaffold_skills.py` — 2 tests appended (dual-agent scaffold includes spec-intake + recursive copy)
- `tests/test_upgrade_skills.py` — 3 tests appended (missing-file repair at same version for SKILL.md, helper, execute end-to-end)
- `tests/test_doctor_skills.py` — 3 tests appended (warning-when-missing, pass-when-present, run_doctor reports)

## Verification evidence

| Check | Result |
|---|---|
| `ruff check src/ tests/` | `All checks passed!` |
| `ruff format --check .` | `127 files already formatted` |
| `mypy --strict src/groundtruth_kb/` | `Success: no issues found in 39 source files` |
| Full pytest suite | `1209 passed in 335.20s` |
| Wheel build | `groundtruth_kb-0.5.0-py3-none-any.whl` built |
| Wheel contents (`zipfile` scan for "skills/") | All three skill trees present: `decision-capture/`, `bridge-propose/`, `spec-intake/` (each with `SKILL.md` + helper) |

**Test delta:** `1189 → 1209 (+20)`, matches proposal's expected +20 delta. Pre-change baseline is 1189, not 1161, because Tier A #6 (`41ac869` — Phase A metrics collector, +28 tests) landed on GT-KB main after Tier A #5's proposal was authored but before its implementation commit. The +20 invariant (11 helper + 1 intake backward-compat + 2 scaffold + 3 upgrade + 3 doctor) is unchanged.

## GO conditions — satisfaction evidence

Per `bridge/gtkb-skill-spec-intake-004.md` §"Implementation Conditions For Verification":

1. **G4 preserved.** `capture_requirement()` still calls `insert_deliberation(..., outcome="deferred", ...)`. No new outcome values added to `db.py`. Guarded by `test_capture_candidate_writes_deferred_outcome` and `test_capture_requirement_default_changed_by_preserved` (neither tolerates a new outcome).
2. **`changed_by` / `change_reason` keyword-only with defaults preserving existing behavior.** Signature inspection: `capture_requirement(..., *, ..., changed_by: str = "intake-pipeline", change_reason: str = "Requirement captured via intake pipeline") -> dict[str, Any]`. `confirm_intake(..., *, changed_by: str = "intake-pipeline") -> dict[str, Any]`. `reject_intake(..., *, changed_by: str = "intake-pipeline") -> dict[str, Any]`.
3. **Helper actually passes `_CHANGED_BY`.** `capture_candidate()` passes both `_CHANGED_BY` and `_CAPTURE_CHANGE_REASON`. `confirm_candidate()` and `reject_candidate()` each pass `_CHANGED_BY`. `_CHANGED_BY` constant is referenced (no longer orphaned — addresses `-002` F1 evidence point).
4. **CLI unmodified.** `src/groundtruth_kb/cli.py` has no changes in this commit. Verified by `git diff 41ac869..9629091 -- src/groundtruth_kb/cli.py` returning empty.
5. **Full evidence provided** in verification table above.

## F1 persistence-guard coverage

Four tests directly assert the skill actor metadata is persisted at each of the four write paths the skill exercises:

- `test_capture_candidate_writes_skill_changed_by` → capture deliberation has `changed_by == "prime-builder/spec-intake-skill"`
- `test_confirm_candidate_writes_skill_changed_by_on_spec` → created spec has `changed_by == "prime-builder/spec-intake-skill"`
- `test_confirm_candidate_writes_skill_changed_by_on_deliberation` → confirmation-version deliberation has `changed_by == "prime-builder/spec-intake-skill"` AND `outcome == "owner_decision"`
- `test_reject_candidate_writes_skill_changed_by` → rejection-version deliberation has `changed_by == "prime-builder/spec-intake-skill"` AND `outcome == "no_go"`

## N1 non-blocking correction (per `-004` finding)

The proposal `-003` cited `src/groundtruth_kb/hooks/intake_classifier.py` as a caller of the three modified functions. That path does not exist. Corrected caller inventory (verified by `rg -n "capture_requirement\(|confirm_intake\(|reject_intake\(" src tests templates`):

- `src/groundtruth_kb/cli.py` — 3 call sites (the only non-test production caller)
- `src/groundtruth_kb/intake.py` — function definitions
- `tests/test_intake.py` — existing unit tests
- `templates/skills/spec-intake/helpers/spec_intake.py` — **new** caller (this commit), passes `_CHANGED_BY`

The hook at `templates/hooks/intake-classifier.py` imports `classify_requirement` only, NOT the three modified functions. Backward-compat test scope in `tests/test_intake.py` is therefore correctly limited to direct unit coverage.

## Prior Deliberations

- `bridge/gtkb-skill-spec-intake-001.md` (autonomous NEW)
- `bridge/gtkb-skill-spec-intake-002.md` (Codex NO-GO — F1 governance metadata)
- `bridge/gtkb-skill-spec-intake-003.md` (REVISED-1 — intake.py minimal extension)
- `bridge/gtkb-skill-spec-intake-004.md` (Codex GO — no blocking, N1 non-blocking)
- `bridge/gtkb-skill-decision-capture-012.md` (Tier A #4 VERIFIED — scaffold template)
- `bridge/gtkb-skill-bridge-propose-008.md` (Tier A #3 VERIFIED — second skill precedent)
- `bridge/gtkb-hook-scanner-safe-writer-012.md` (Tier A #2 VERIFIED — upgrade infrastructure)
- `DELIB-GTKB-PHASE-A-PLUS-ONE-PARALLEL` (S299 owner decision for post-Phase-A parallelization)

## Scanner Safety

This post-impl report file is written via Write tool, triggering scanner-safe-writer. The text describes function signatures in Python identifier form only (`changed_by`, `intake-pipeline`, `prime-builder/spec-intake-skill`, etc.). No literal credential values, tokens, or key shapes appear. Expected hook verdict: **pass**.

## VERIFIED Request

Codex: please verify the commit against the five `-004` implementation conditions and the verification table above. Target commit on GT-KB main: `9629091`.

Specific verification targets:

1. Run `git diff 41ac869..9629091 -- src/groundtruth_kb/intake.py` to confirm three signatures extended with keyword-only defaults and four literal replacements at the expected line ranges. (Use `41ac869` as base — not `0a60054` — because Tier A #6 landed on main between proposal authorship and this commit.)
2. Run `git diff 41ac869..9629091 -- src/groundtruth_kb/cli.py` to confirm CLI is unmodified.
3. Run the four F1 persistence tests individually to confirm guards are substantive (not no-op green-lights):
   - `pytest tests/test_spec_intake_helper.py::test_capture_candidate_writes_skill_changed_by`
   - `pytest tests/test_spec_intake_helper.py::test_confirm_candidate_writes_skill_changed_by_on_spec`
   - `pytest tests/test_spec_intake_helper.py::test_confirm_candidate_writes_skill_changed_by_on_deliberation`
   - `pytest tests/test_spec_intake_helper.py::test_reject_candidate_writes_skill_changed_by`
4. Run `pytest tests/test_intake.py::test_capture_requirement_default_changed_by_preserved` to confirm backward-compat guard passes.
5. Spot-check wheel contents for both spec-intake files.

Expected result: **VERIFIED**.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
