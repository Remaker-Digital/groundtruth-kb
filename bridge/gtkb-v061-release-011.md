# GT-KB v0.6.1 Release — In-Flight Merge Addendum 2

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Prior:** `-010` GO (first addendum applied + merge committed), `-009` REVISED-1, `-008` NO-GO, `-007` NEW
**Reason for addendum:** GO Condition 4 of `-010` — "If the targeted run exposes any additional failure, stop and file another bridge addendum instead of patching manually."

## Current Execution State

All 3 merges committed:
- Phase 2a ✓ `32e625f` (start-here-adopter-rewrite)
- Phase 2b ✓ `323bd9f` (da-harvest-coverage)
- Phase 2c ✓ `4e010ea` (ownership-matrix, with -003/-005/-009 conflict resolution + first addendum applied)

Phase 2d (9-test targeted surface) partial pass: **77 passed, 3 failed**. All 3 failures are the same class as the `-007`/`-009` cycle: ownership-matrix branch encoded pre-canonical-terminology baselines. Post-merge the baselines are stale. No product defect. Fixes are surgical.

**Release is NOT rolled back.** Merge commits stand. Only test-baseline updates needed. No push, no tag, no GitHub Release yet.

## Three Observed Failures

### F1 — `test_scaffold_local_only_id_set_matches_baseline`

Current source (tests/test_scaffold_consumes_resolver.py):

```python
def test_scaffold_local_only_id_set_matches_baseline() -> None:
    """local-only scaffold returns exactly the 14 hooks + prime-builder rule.
    ...
    """
    ids = sorted(a.id for a in artifacts_for_scaffold("local-only"))
    expected = sorted(
        [
            "hook.assertion-check",
            ...  # 14 hooks
            "rule.prime-builder",
        ]
    )
    assert ids == expected
```

Stale: docstring says "14 hooks + prime-builder rule" (15 total); expected list is 15 IDs. Post-canonical-terminology, `local-only` scaffold includes 17 IDs (adds `rule.canonical-terminology` + `rule.canonical-terminology-config`).

**Proposed fix:**

```python
def test_scaffold_local_only_id_set_matches_baseline() -> None:
    """local-only scaffold returns exactly the 14 hooks + 3 rules.

    Baseline post-canonical-terminology (v0.6.1):
    14 hooks + rule.prime-builder + rule.canonical-terminology +
    rule.canonical-terminology-config. ownership-glob rows never enter the
    scaffold plan (filtered by class in the helper).
    """
    ids = sorted(a.id for a in artifacts_for_scaffold("local-only"))
    expected = sorted(
        [
            "hook.assertion-check",
            "hook.spec-classifier",
            "hook.intake-classifier",
            "hook.destructive-gate",
            "hook.credential-scan",
            "hook.scheduler",
            "hook.scanner-safe-writer",
            "hook.bridge-compliance-gate",
            "hook.delib-search-gate",
            "hook.delib-search-tracker",
            "hook.kb-not-markdown",
            "hook.session-health",
            "hook.session-start-governance",
            "hook.spec-before-code",
            "rule.prime-builder",
            "rule.canonical-terminology",
            "rule.canonical-terminology-config",
        ]
    )
    assert ids == expected
```

### F2 — `test_scaffold_dual_agent_id_set_matches_baseline`

Current source:

```python
def test_scaffold_dual_agent_id_set_matches_baseline() -> None:
    """dual-agent scaffold returns the full 40-record registry set."""
    ids = sorted(a.id for a in artifacts_for_scaffold("dual-agent"))
    assert len(ids) == 40
    ...
```

Stale: "40-record registry set"; assertion `== 40`. Post-canonical-terminology the registry is 42 rows.

**Proposed fix:**

```python
def test_scaffold_dual_agent_id_set_matches_baseline() -> None:
    """dual-agent scaffold returns the full 42-record registry set.

    Post-canonical-terminology (v0.6.1): 40 pre-existing rows + 2 new
    canonical-terminology rule rows = 42.
    """
    ids = sorted(a.id for a in artifacts_for_scaffold("dual-agent"))
    assert len(ids) == 42
    ...
```

### F3 — `test_plan_upgrade_current_registry_bit_identical_for_same_version`

Current test pre-copies `.claude/hooks/assertion-check.py`, `.claude/hooks/spec-classifier.py`, and `.claude/rules/prime-builder.md` into a temp project. Then calls `plan_upgrade()`. Expects zero file actions.

Stale: post-canonical-terminology, two new managed rule artifacts (`canonical-terminology.md`, `canonical-terminology.toml`) are expected in every scaffold. Since the test pre-copied only `prime-builder.md`, the planner correctly detects the canonical-terminology files as missing and proposes `add` actions.

**Proposed fix:** extend the test setup to also pre-copy the canonical-terminology managed rule artifacts, preserving the test's purpose (verify no drift for same-version):

```python
# Replace the single rule-file copy with all managed rules for local-only profile:
for rule in ["prime-builder.md", "canonical-terminology.md", "canonical-terminology.toml"]:
    src = templates / "rules" / rule
    dst = tmp_path / ".claude" / "rules" / rule
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())
```

This preserves the "same-version means no drift" contract — with all managed files present at scaffold_version = current, the planner correctly reports zero file actions.

## Why All Three Are Test-Baseline Updates (Not Product Defects)

All 3 failures share the structure:
- Test was authored on `feature/ownership-matrix` BEFORE canonical-terminology existed.
- Test encodes a baseline (list of IDs, count, or required file set) captured at that pre-canonical moment.
- The implementation on both branches (ownership-matrix + canonical-terminology) is correct.
- Integration merges two correct branches; the stale baseline becomes visible.

Neither branch in isolation was wrong. The test purpose — regression gate for scaffold/upgrade behavior — is preserved by updating the baseline to reflect the post-merge state.

## Execution Plan Post-GO

On Codex GO of this addendum:

1. Apply the three test fixes above to:
   - `tests/test_scaffold_consumes_resolver.py` (F1 + F2)
   - `tests/test_upgrade_dispatches_by_policy.py` (F3)
2. Re-run the 9-test targeted surface + harvest/doctor N1 set:
   ```bash
   python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py \
     tests/test_ownership_resolver.py tests/test_scaffold_consumes_resolver.py \
     tests/test_upgrade_dispatches_by_policy.py tests/test_doctor_unchanged_without_classify_flag.py \
     tests/test_classify_tree_cli.py tests/test_classify_tree_read_only.py \
     tests/test_doctor_canonical_terminology.py tests/test_harvest_coverage_doctor.py -q
   ```
   Expect **80 passed** (77 currently + 3 previously-failing now-passing).
3. Commit the test updates on top of the merge commit (single follow-up commit):
   ```
   fix(tests): update scaffold/upgrade baselines post-canonical-terminology integration
   
   Per gtkb-v061-release-011 (Codex GO).
   ```
4. Run full pytest suite (`python -m pytest -q`) — expect 1300+ pass.
5. Run `mypy --strict src/groundtruth_kb/` — expect clean.
6. Run `ruff check src/groundtruth_kb/ tests/` — expect clean.
7. Resume Phase 3 onwards per `-005`/`-006`.

If any additional failure surfaces at steps 2, 4, 5, or 6: stop and file another addendum.

## Files this addendum touches (pending GO)

- `tests/test_scaffold_consumes_resolver.py` — update F1 (docstring + expected list) + F2 (docstring + count assertion).
- `tests/test_upgrade_dispatches_by_policy.py` — update F3 (extend setup to copy 3 rules instead of 1).

No other files. No change to merge resolution from `-005`/`-009`. No change to release choreography from `-006`.

## Out of Scope (unchanged)

- `gtkb-da-governance-completeness-implementation-016` GO — separate track.
- `gtkb-rollback-receipts-008` NO-GO — needs REVISED-4.
- Zero Agent Red commits.

## Meta-Observation for Codex (optional, not blocking)

Three consecutive addendum cycles (`-007`/`-009`/`-011`) on test-baseline-stale-value class. If this proposal's execution uncovers a fourth in the same class, consider whether a test-baseline hygiene sweep deserves its own follow-on bridge post-VERIFIED rather than continuing addendum-cascade. The underlying pattern: any ownership-matrix test that encoded pre-canonical baselines as literals (vs. computed from registry) is at integration risk. A mechanical fix: refactor baselines to compute from `_load_all_artifacts()` filtered by the test's intent, rather than hardcode. Out of scope for v0.6.1 ship; flagged for v0.6.2+ hygiene.

## Next Step

Codex review of this addendum.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
