# GT-KB v0.6.1 Release — In-Flight Merge Addendum (test assertion update)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17 (S300)
**Prior:** `-006.md` GO (implementation authorized, 4 conditions + N1 note)
**Reason for addendum:** GO Condition 3 — "If conflict resolution or targeted tests fail, stop and file a revised bridge addendum instead of continuing the release manually."

## Current Execution State

All three merges performed per plan. Conflict resolution complete per `-005`:

- Phase 2a ✓ `feat/start-here-adopter-rewrite` merged at `32e625f` (`--no-ff`, no conflicts)
- Phase 2b ✓ `feat/da-harvest-coverage` merged at `323bd9f` (`--no-ff`, auto-merged `doctor.py`)
- Phase 2b-gate ✓ 27 passed on `test_doctor_canonical_terminology.py` + `test_harvest_coverage_doctor.py` (N1 recommendation)
- Phase 2c ✓ `feature/ownership-matrix` merge is **in progress with conflicts resolved**:
  - `CHANGELOG.md` — combined canonical-terminology + ownership-matrix + harvest sections into unified `[Unreleased]`
  - `tests/test_managed_registry.py` — `test_registry_total_is_forty_two_records` name (start-here) + `_registry_records()` helper call (ownership-matrix); 42-record assertion
  - `templates/managed-artifacts.toml` — canonical-terminology rows now carry the `gt-kb-managed + overwrite + warn` ownership block per `-005 §F1` exact pattern
- Phase 2c-gate ✗ **1 of 39 targeted tests fails** — requires this addendum per GO Condition 3

**Merge is NOT committed. Working tree holds resolved conflicts.** No push, no tag, no GitHub Release.

## Observed Failure

```text
tests/test_ownership_loader_agreement.py::test_artifacts_for_scaffold_unchanged_by_sibling_file FAILED
  AssertionError: assert 17 == 15
   +  where 17 = len({'hook.assertion-check', ...})
```

Test source:

```python
def test_artifacts_for_scaffold_unchanged_by_sibling_file() -> None:
    """With scaffold-ownership.toml present, artifacts_for_scaffold still returns the original 40 IDs.
    ...
    """
    # Expected per proposal: local-only = 15 (14 hooks + 1 rule)
    ids = {a.id for a in artifacts_for_scaffold("local-only")}
    assert len(ids) == 15
```

## Root Cause

The test hardcodes a **pre-canonical-terminology** count: `15 = 14 hooks + 1 rule` for the `local-only` profile's `initial_profiles` set. That count was accurate on `feature/ownership-matrix` before the canonical-terminology work existed.

After merging `feat/start-here-adopter-rewrite`, `templates/managed-artifacts.toml` gained two new rule records:

- `rule.canonical-terminology` — `initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]`
- `rule.canonical-terminology-config` — same `initial_profiles`

Both include `local-only`, so `artifacts_for_scaffold("local-only")` correctly now returns `14 hooks + 3 rules = 17`.

The test's **purpose** (verify sibling `scaffold-ownership.toml` does not inflate the scaffold set) is still served — 17 is the correct registry-only count; the 8 ownership-glob rows from the sibling file are correctly excluded. Only the hardcoded expected count is stale.

## Why the analogous upgrade/doctor tests pass

The upgrade and doctor analogs use **class-filter assertions** rather than count assertions:

```python
def test_artifacts_for_upgrade_unchanged_by_sibling_file() -> None:
    for profile in ("local-only", "dual-agent", "dual-agent-webapp"):
        results = artifacts_for_upgrade(profile)
        for a in results:
            assert a.class_ != "ownership-glob", ...
```

These tests verify `ownership-glob` class absence (the structural invariant), not a specific count. They're immune to additive changes like canonical-terminology. Only the scaffold test encoded the count literally.

## Proposed Fix

Single-line change to `tests/test_ownership_loader_agreement.py`:

```diff
 def test_artifacts_for_scaffold_unchanged_by_sibling_file() -> None:
-    """With scaffold-ownership.toml present, artifacts_for_scaffold still returns the original 40 IDs.
+    """With scaffold-ownership.toml present, artifacts_for_scaffold excludes ownership-glob rows.
+
+    Post-canonical-terminology (v0.6.1): local-only profile scaffolds 17 = 14 hooks + 3 rules
+    (adds ``rule.canonical-terminology`` + ``rule.canonical-terminology-config`` beyond the
+    pre-canonical 15 = 14 hooks + 1 rule).

     The sibling file contains only ownership-glob records which are filtered
     out by the helper.
     """
-    # Expected per proposal: local-only = 15 (14 hooks + 1 rule)
+    # Expected post-canonical-terminology: local-only = 17 (14 hooks + 3 rules)
     ids = {a.id for a in artifacts_for_scaffold("local-only")}
-    assert len(ids) == 15
+    assert len(ids) == 17
```

Docstring updated to accurately reflect the post-merge state. Count assertion updated from 15 → 17. No other changes.

## Why this is a merge-integration update and not a defect

Both branches independently correct at their base:

- `feature/ownership-matrix` with count=15 was correct when authored (pre-canonical).
- `feat/start-here-adopter-rewrite` added 2 rows to `local-only` profile (correct per its spec).

Neither branch in isolation was wrong. Integration requires reconciling the hardcoded count. This is the class of fix that the bridge protocol's "stop and file addendum" condition is designed to surface — so that trivial-looking integration fixes are documented and reviewed rather than silently applied.

## Execution Plan Post-GO

On Codex GO of this addendum:

1. Apply the one-line test fix above.
2. Re-run: `python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py -q` → expect 39 passed.
3. Commit the ownership-matrix merge with message:
   ```
   Merge feature/ownership-matrix into main for v0.6.1 (resolved conflicts)
   ```
4. Resume Phase 2d (full 9-test surface + full pytest suite per `-003`).
5. Resume Phase 3 onwards per `-005` / `-006`.

If re-run reveals additional failures (not expected), file another addendum rather than manually patching.

## Files modified by this addendum (pending GO)

- `tests/test_ownership_loader_agreement.py` — single assertion + docstring update per diff above.

No other files. No change to the CHANGELOG resolution, TOML resolution, or `test_managed_registry.py` resolution from `-005` / `-006`.

## Out of Scope (unchanged)

- `gtkb-da-governance-completeness-implementation-016` GO — still separate track.
- `gtkb-rollback-receipts-008` NO-GO — still needs REVISED-4.
- `agent-red-session-wrap-automation-005` VERIFIED retirement — no code to ship.
- Zero Agent Red commits.

## Next Step

Codex review of this addendum.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
