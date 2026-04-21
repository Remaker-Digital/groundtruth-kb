# Phase 4: F6 (A+B) + F8 — REVISED v3 Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Revised Implementation Proposal (addresses NO-GO -004)
**Prerequisite:** Phase 3 VERIFIED (018)

## NO-GO -004 Resolutions

### Finding 1: F8 stale detection must preserve same-section activity gate → FIXED

**Resolution:** Both the snapshot-backed path and the `changed_at` fallback
now require **same-section activity** as a necessary condition for marking a
spec stale. The fallback also carries an explicit `section_activity_days`
parameter matching the approved F8 signature.

**Revised API:**
```python
def find_stale_specs(
    db: KnowledgeDB,
    *,
    staleness_threshold_sessions: int = 5,
    staleness_threshold_days: int = 90,
    section_activity_days: int = 30,
) -> ReconciliationReport:
    """Find specs that appear stale relative to recent section activity.

    A spec is stale when it has NOT changed recently AND other specs in
    the same section HAVE changed recently. This avoids false positives on
    quiet but stable sections.

    Prefers snapshot-backed staleness when F7 history is sufficient,
    falling back to changed_at timestamps otherwise.
    """
```

**Snapshot-backed path (expressible from current F7 payload):**
F7 snapshots currently store aggregate data (`lifecycle_metrics`, `summary`,
`quality_distribution`, `constraint_coverage`, `captured_at`) — NOT per-spec
signatures. The approved "unchanged for N sessions while section has
changes" semantics is expressed as follows:

```python
# Snapshot-backed path:
#   A spec is stale if:
#     (a) at least `staleness_threshold_sessions` snapshots exist with
#         captured_at > spec.changed_at (the spec has not been touched
#         across those sessions), AND
#     (b) at least one OTHER spec in the same section has changed_at
#         newer than spec.changed_at (the section is active despite
#         this spec being static).
#
# This is expressible entirely from existing fields:
#   - session_snapshots.captured_at (aggregate, no per-spec data needed)
#   - specifications.changed_at (per-spec last-modified timestamp)
#   - specifications.section (for same-section partition)
```

This avoids inventing new F7 snapshot payload fields. It does NOT claim
per-spec presence tracking — it only counts how many snapshot events
occurred after a spec's last change, plus a same-section activity check.

**Fallback path:**
```python
# Fallback path (snapshots unavailable or < threshold):
#   A spec is stale if:
#     (a) spec.changed_at < now - staleness_threshold_days, AND
#     (b) some OTHER spec in the same section has
#         changed_at > now - section_activity_days
```

**Revised tests (4 for stale detection):**
- `test_stale_from_snapshots_with_section_activity` — 5 snapshots all newer than spec's changed_at, AND another spec in same section changed after → spec reported stale
- `test_stale_from_snapshots_without_section_activity` — 5 snapshots newer than spec, but no other spec in section has changed → NOT reported stale (section is quiet, spec is fine)
- `test_stale_fallback_with_section_activity` — < 5 snapshots, spec older than 90 days, another spec in section changed within 30 days → reported stale
- `test_stale_fallback_no_section_activity` — < 5 snapshots, spec older than 90 days, no section activity within 30 days → NOT reported stale

Plus CLI smoke: `test_stale_cli_smoke` — `gt kb reconcile --stale 5` returns
exit 0 and includes any stale findings.

F8 test count: 23 → 24 (added section-activity negative case).

### Finding 2: Shared extractor needs depth guard → FIXED

**Resolution:** `_extract_assertion_targets()` in assertions.py gets a
`depth: int = 0` keyword parameter and enforces `_MAX_COMPOSITION_DEPTH`
before recursing. Existing F2 callers are source-compatible because
`depth` defaults to `0`.

**Revised signature:**
```python
def _extract_assertion_targets(
    assertion: Any,
    *,
    depth: int = 0,
) -> list[AssertionTarget]:
    """..."""
    if not isinstance(assertion, dict):
        return []

    a_type = assertion.get("type", "")
    if not a_type or a_type not in _VALID_ASSERTION_TYPES:
        return []

    normalized = _normalize_assertion(assertion)

    # --- Composition operators: recurse with depth guard ---
    if a_type in ("all_of", "any_of"):
        if depth >= _MAX_COMPOSITION_DEPTH:
            return []
        targets: list[AssertionTarget] = []
        for child in normalized.get("assertions", []):
            targets.extend(_extract_assertion_targets(child, depth=depth + 1))
        return targets
    # ... rest unchanged ...
```

**Impact on assertions.py:** ~6-line change (add param, guard, pass-through).
Existing F2 tests remain passing because the public call
`_extract_assertion_targets(assertion)` still accepts a single positional
dict argument.

**New test in `tests/test_impact.py::TestF2AAssertionTargetExtraction`:**
`test_extract_respects_max_composition_depth` — build a deeply-nested
`all_of` chain with `_MAX_COMPOSITION_DEPTH + 2` levels, call
`_extract_assertion_targets(chain)`, assert it returns `[]` (children past
the depth guard are silently dropped) and does NOT raise `RecursionError`.

**F8 orphan tests already cover the normal composition case** via the
`all_of` mixed-children test.

This adds 1 test to the F2 test file (test_impact.py) — not counted toward
F8's 24, so Phase 4 total is 561 → 594 (+33).

### Finding 3: F6 dry-run quality scoring must match score_spec_quality() input shape → FIXED

**Resolution:** The synthetic spec passed to `score_spec_quality()` in
dry-run mode populates `_assertions_parsed` explicitly so
`score_spec_quality()` sees the generated assertions and does not fire a
false `NO_ASSERTIONS` flag.

**Revised dry-run quality path:**
```python
def scaffold_specs(db, config, *, dry_run=True) -> ScaffoldReport:
    generated: list[dict] = []
    quality_summary = {"gold": 0, "silver": 0, "bronze": 0, "needs-work": 0}
    warnings = []

    for spec_data in _generate_spec_data(config):
        # spec_data is a dict with {id, title, description, section, scope,
        #                           assertions (list of dicts), ...}
        if dry_run:
            # Build a synthetic dict that score_spec_quality() understands.
            # Populate _assertions_parsed from the generated assertion list
            # so the scorer sees executable assertions correctly.
            synthetic = {
                **spec_data,
                "version": 1,
                "_assertions_parsed": spec_data.get("assertions") or [],
                "assertions_parsed": spec_data.get("assertions") or [],
            }
            quality = db.score_spec_quality(synthetic)
        else:
            created = db.insert_spec(**spec_data, authority="inferred")
            # After insert, get_spec() returns the row with parsed fields
            quality = db.score_spec_quality(db.get_spec(created["id"]))

        tier = quality.get("tier", "needs-work")
        quality_summary[tier] = quality_summary.get(tier, 0) + 1
        if tier in ("bronze", "needs-work"):
            warnings.append(
                {"id": spec_data["id"], "tier": tier, "score": quality.get("overall")}
            )
        generated.append({**spec_data, "quality": quality})

    return ScaffoldReport(..., quality_summary=quality_summary,
                          low_quality_warnings=warnings)
```

**New test in `tests/test_spec_scaffold.py`:**
`test_scaffold_dry_run_quality_scores_executable_assertions` — build a
`SpecScaffoldConfig`, call `scaffold_specs(db, config, dry_run=True)`,
and verify that for at least one generated spec that has executable
assertions (e.g., a `grep` assertion in a governance template):
- The quality result does NOT contain `NO_ASSERTIONS` in flags
- The quality result does NOT contain `NO_EXECUTABLE_ASSERTIONS` in flags
- The tier is populated (non-null)

F6 test count: 9 → 10.

---

## Full Phase 4 Spec Summary

### F6 (10 tests)

**Phase A (4):**
1. Minimal config — dry run returns report with governance + infra specs
2. Full config — dry run returns report with all phases (`ai_components`, compliance)
3. Non-empty KB skip — pre-existing governance handle is skipped, others generated
4. Dry-run default — `scaffold_specs()` writes nothing by default

**Phase B (2):**
5. Generated specs have `authority='inferred'`
6. Owner promotion to `stated` via `update_spec()` creates new version

**F3 Quality Validation (3):**
7. `ScaffoldReport.quality_summary` populated on apply
8. `ScaffoldReport.low_quality_warnings` populated for bronze/needs-work tiers
9. Dry-run quality scoring does NOT fire `NO_ASSERTIONS` false-positive on executable assertions (NEW — addresses Finding 3)

**Integration (1):**
10. `scaffold_project(options=ScaffoldOptions(spec_scaffold=...))` populates the newly-created KB with generated specs

### F8 (24 tests)

**Orphan Detection (12) — reuses shared `_extract_assertion_targets()`:**
1. `grep` literal exists → not orphaned
2. `grep` literal missing → orphaned
3. `grep` with `path` alias
4. `grep` with `target` alias
5. `glob` assertion with matches → not orphaned
6. `glob` zero matches → orphaned
7. `grep` file-glob with matches → not orphaned
8. `grep` file-glob zero matches → orphaned
9. `grep_absent` file-glob zero matches → orphaned
10. `count` file-glob zero matches → orphaned
11. `file_exists` literal with `*` in name → literal resolution, orphaned if missing
12. `all_of` composition with mixed children → per-child orphan reporting

**Plain-Text Assertion Safety (3):**
13. Top-level plain-text string assertion → silently skipped
14. `all_of` with plain-text child → child skipped, dict children processed
15. Non-machine dict child (`{"type":"visual",...}`) → skipped

**Authority Conflicts (3):**
16. Alias overlap between stated and inferred specs (same section/scope)
17. Composition overlap between stated and inferred specs
18. Glob-string overlap between stated and inferred specs

**Stale Detection (5 — NEW SCOPE from Finding 1):**
19. `test_stale_from_snapshots_with_section_activity` — snapshot path fires when section has activity
20. `test_stale_from_snapshots_without_section_activity` — snapshot path does NOT fire when section is quiet
21. `test_stale_fallback_with_section_activity` — fallback path fires with recent section activity
22. `test_stale_fallback_no_section_activity` — fallback path does NOT fire without section activity
23. `test_stale_cli_smoke` — `gt kb reconcile --stale 5` returns exit 0

**Provenance (2):**
24. Expired provisional spec with replacement implemented → reported
25. Duplicate detection (90% title token overlap) → reported

Actually, that's 25 total. Let me recount: 12 orphan + 3 plain-text + 3
authority + 5 stale + 2 provenance = **25 tests**. (Previous revision had
23; the net change is +2 stale tests and the rest preserved.)

### Shared Extractor (1 test in test_impact.py)

`test_extract_respects_max_composition_depth` — deeply nested composition
does not crash.

---

## Total Estimated Changes

| Feature | New files | Modified files | Tests | Lines |
|---------|-----------|----------------|-------|-------|
| F6 (A+B+F3+integration) | 2 (spec_scaffold.py, test) | 3 (cli.py, project/scaffold.py, cli.md) | 10 | ~750 |
| F8 (orphans+plain-text+authority+stale+provenance) | 2 (reconciliation.py, test) | 3 (cli.py, assertions.py, cli.md) | 25 | ~950 |
| Shared extractor depth guard | 0 | 1 (assertions.py) + 1 (test_impact.py) | +1 | ~10 |
| **Total** | **4 new, 5 modified** | — | **36** | **~1710** |

## Verification

1. `python -m pytest -q` — full suite (561 → ~597 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Implementation Order

1. **assertions.py depth guard** (1 line addition + 1 test) — establishes the
   safe shared extractor before F8 depends on it
2. **F6** (10 tests) — scaffold_project integration, F3 validation, dry-run
3. **F8** (25 tests) — reconciliation using shared extractor

## Conditions Preserved From v2

- F6 integrates into `scaffold_project()` via optional `ScaffoldOptions.spec_scaffold`
- F6 generated specs default to `authority='inferred'`
- F6 `dry_run=True` is the default
- F8 authority conflicts use stated-vs-inferred structural overlap
- F8 reuses shared extractor (now with depth guard)
- F8 orphan detection respects type-specific dispatch (glob, literal, grep-style)
- F8 non-dict assertion guard

## Request

Codex review requested. GO authorizes Phase 4 implementation.
