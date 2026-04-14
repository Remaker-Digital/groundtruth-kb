# Phase 4: F6 (A+B) + F8 — REVISED Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Revised Implementation Proposal (addresses NO-GO -002)
**Prerequisite:** Phase 3 VERIFIED (018)

## NO-GO -002 Resolutions

### Finding 1: F6 omits scaffold_project() integration → FIXED

**Resolution:** Add `spec_scaffold: SpecScaffoldConfig | None = None` as an
optional field on `ScaffoldOptions`. When set, `scaffold_project()` calls
`scaffold_specs(db, options.spec_scaffold, dry_run=False)` after the KB is
initialized but before returning. Default `None` preserves existing
`gt project init` behavior unchanged.

**Integration point** (scaffold.py, after `_copy_*_templates()` and KB init):
```python
if options.spec_scaffold is not None:
    from groundtruth_kb.spec_scaffold import scaffold_specs
    db = KnowledgeDB(db_path=target / "groundtruth.db")
    scaffold_specs(db, options.spec_scaffold, dry_run=False)
```

**Test added:** `test_scaffold_project_with_spec_scaffold` creates a
`ScaffoldOptions` with `spec_scaffold=SpecScaffoldConfig(...)`, calls
`scaffold_project(options)`, and asserts the newly-created KB contains the
generated governance and infrastructure specs.

### Finding 2: F6 Phase B omits F3 quality validation → FIXED

**Resolution:** `scaffold_specs()` scores every generated spec via
`db.score_spec_quality()` and populates the returned `ScaffoldReport` with
per-spec quality results. In dry-run mode, the quality scores appear in the
report alongside the spec content. In apply mode, specs below the
`gold`/`silver` tier threshold trigger a warning in the report (but are
still written — the owner decides whether to keep them).

**Report addition:**
```python
@dataclass
class ScaffoldReport:
    phases: list[dict[str, Any]]
    total_generated: int
    total_skipped: int
    specs: list[dict[str, Any]]
    quality_summary: dict[str, int]      # tier → count
    low_quality_warnings: list[dict]     # per-spec warnings for needs-work/bronze
```

**Implementation sketch:**
```python
def scaffold_specs(db, config, *, dry_run=True) -> ScaffoldReport:
    generated: list[dict] = []
    quality_summary = {"gold": 0, "silver": 0, "bronze": 0, "needs-work": 0}
    warnings = []

    for spec_data in _generate_spec_data(config):
        if dry_run:
            # Score a synthetic spec for preview
            synthetic = {**spec_data, "version": 1, "id": spec_data["id"]}
            quality = db.score_spec_quality(synthetic)
        else:
            created = db.insert_spec(**spec_data, authority="inferred")
            quality = db.score_spec_quality(db.get_spec(created["id"]))

        tier = quality.get("tier", "needs-work")
        quality_summary[tier] = quality_summary.get(tier, 0) + 1
        if tier in ("bronze", "needs-work"):
            warnings.append({"id": spec_data["id"], "tier": tier, "score": quality.get("overall")})

        generated.append({**spec_data, "quality": quality})

    return ScaffoldReport(..., quality_summary=quality_summary, low_quality_warnings=warnings)
```

**Tests added:**
- `test_scaffold_quality_summary_populated` — apply scaffold, verify
  `ScaffoldReport.quality_summary` has tier counts
- `test_scaffold_low_quality_warning` — generate a deliberately low-quality
  template (minimal fields) and verify it appears in `low_quality_warnings`

### Finding 3: F8 stale detection has no tests and inconsistent fallback → FIXED

**Resolution:** Preserve the approved `changed_at` fallback explicitly. The
rule is now unambiguous:

```python
def find_stale_specs(
    db: KnowledgeDB,
    *,
    staleness_threshold_sessions: int = 5,
    staleness_threshold_days: int = 90,
) -> ReconciliationReport:
    """Find specs that appear stale across recent sessions or by timestamp.

    Prefers F7 snapshot history when sufficient. Falls back to changed_at
    timestamps when history is shorter than staleness_threshold_sessions.
    """
    snapshot_history = db.get_snapshot_history(limit=staleness_threshold_sessions)

    if len(snapshot_history) >= staleness_threshold_sessions:
        # Snapshot-backed path: find specs whose signature hasn't changed across N snapshots
        return _stale_from_snapshots(db, snapshot_history)

    # Bootstrap / fallback path: use changed_at
    cutoff = _now_minus_days(staleness_threshold_days)
    return _stale_from_changed_at(db, cutoff)
```

**Tests added (3 for stale detection):**
- `test_stale_from_snapshots` — insert 5 snapshots, verify specs appearing in
  all 5 with no metric change are reported as stale
- `test_stale_fallback_to_changed_at` — with fewer than 5 snapshots, verify
  fallback path triggers and reports specs older than the day threshold
- `test_stale_cli_smoke` — `gt kb reconcile --stale 5` returns exit 0 and
  non-empty output when stale specs exist

F8 test count: 20 → 23.

### Finding 4: F8 authority-conflict semantics drift → FIXED

**Resolution:** The authority-conflict algorithm is explicitly redefined to
match the approved structural overlap model:

**Approved algorithm:**
1. Partition current specs into groups by `(section, scope)`.
2. Within each group, find all pairs `(spec_a, spec_b)` where:
   - `spec_a.authority == 'stated'` and `spec_b.authority == 'inferred'` (or vice versa)
   - `_extract_assertion_targets(spec_a.assertions)` and
     `_extract_assertion_targets(spec_b.assertions)` produce overlapping
     `(file_target, match_target)` pairs — using exact-string comparison
     (same semantics as F2 conflict detection)
3. Report each such pair as an authority conflict.

**Why this matters:** An `inferred` spec that structurally overlaps a `stated`
spec may be a misfired scaffold template or an AI-suggested variant that was
never promoted. The detector surfaces those cases so the owner can either
promote the inferred one, merge them, or remove one.

**Implementation sketch:**
```python
def find_authority_conflicts(db: KnowledgeDB) -> ReconciliationReport:
    from groundtruth_kb.assertions import _extract_assertion_targets

    specs = db.list_specs()
    groups: dict[tuple[str | None, str | None], list[dict]] = defaultdict(list)
    for s in specs:
        groups[(s.get("section"), s.get("scope"))].append(s)

    conflicts: list[dict] = []
    for (section, scope), members in groups.items():
        by_authority: dict[str, list[dict]] = {"stated": [], "inferred": []}
        for s in members:
            auth = s.get("authority")
            if auth in by_authority:
                by_authority[auth].append(s)

        for a in by_authority["stated"]:
            a_targets = _extract_targets_for_spec(a)
            for b in by_authority["inferred"]:
                b_targets = _extract_targets_for_spec(b)
                overlap = [
                    (ta, tb) for ta in a_targets for tb in b_targets
                    if ta.file_target == tb.file_target
                    and ta.match_target == tb.match_target
                ]
                if overlap:
                    conflicts.append({
                        "stated_spec": a["id"], "inferred_spec": b["id"],
                        "section": section, "scope": scope,
                        "overlapping_targets": len(overlap),
                    })

    return ReconciliationReport("authority_conflicts", conflicts, len(conflicts))
```

**Tests (3, unchanged):**
16. **Alias overlap** — `stated` spec uses `{"type":"grep","file":"x","pattern":"y"}`; `inferred` spec uses `{"type":"grep","target":"x","query":"y"}`; same (section, scope); conflict reported after alias normalization
17. **Composition overlap** — `stated` spec has `{"type":"all_of","assertions":[{"type":"grep","file":"x","pattern":"y"}]}`; `inferred` has the same grep as a top-level assertion; conflict reported
18. **Glob string match** — both specs have `{"type":"grep","file":"src/**/*.py","pattern":"TODO"}`; same (section, scope); conflict reported (exact string match on globs is correct, same semantics as F2)

### Finding 5: F8 proposes duplicate extractor → FIXED

**Resolution:** F8 reuses the existing `_extract_assertion_targets()` helper
(from F2, in assertions.py). No new `_extract_file_targets()` or
`TypedFileTarget` is added.

**Justification:** The existing `AssertionTarget.file_is_glob` field already
has the exact semantics F8 needs for dispatch:
- `grep`/`grep_absent`/`count` with `"*"` in file_target → `file_is_glob=True`
- `grep`/`grep_absent`/`count` without `"*"` → `file_is_glob=False`
- `glob` → always `file_is_glob=True`
- `file_exists`/`json_path` → always `file_is_glob=False`

The existing helper also handles: non-dict guard (returns `[]` at entry and
via composition recursion), `_normalize_assertion()` alias resolution,
`_VALID_ASSERTION_TYPES` filtering, and the `_MAX_COMPOSITION_DEPTH` limit.
The existing docstring already documents the dual F2/F8 purpose:

> "Used by F2 (Change Impact Analysis) and F8 (Provenance Reconciliation)
>  to build a machine-interpretable target set from assertion definitions."

F8's orphan detector uses `target.file_is_glob` to decide between glob and
literal dispatch:

```python
def find_orphaned_assertions(db, project_root):
    from groundtruth_kb.assertions import _extract_assertion_targets, _safe_glob, _safe_resolve

    orphans = []
    for spec in db.list_specs():
        for assertion in spec.get("_assertions_parsed") or []:
            for target in _extract_assertion_targets(assertion):
                if target.file_target is None:
                    continue
                if target.file_is_glob:
                    matches = _safe_glob(target.file_target, project_root)
                    if not matches:
                        orphans.append({"spec_id": spec["id"], "target": target.file_target, "reason": "glob zero matches"})
                else:
                    resolved = _safe_resolve(target.file_target, project_root)
                    if resolved is None or not resolved.exists():
                        orphans.append({"spec_id": spec["id"], "target": target.file_target, "reason": "file missing"})
    return ReconciliationReport("orphans", orphans, len(orphans))
```

**No changes to assertions.py are required for F8 orphan detection.** The
only assertions.py change that might still be useful is promoting
`_safe_glob` and `_safe_resolve` from module-private to package-visible so
reconciliation.py can import them without the underscore-private convention
violation. This is a one-line rename or an `__all__` addition, covered by
the existing assertion tests.

---

## Full Revised F6 Spec (8 tests)

### Module

`src/groundtruth_kb/spec_scaffold.py` — NEW
- `SpecScaffoldConfig` dataclass
- `ScaffoldReport` dataclass (with `quality_summary` and `low_quality_warnings`)
- `scaffold_specs(db, config, *, dry_run=True) -> ScaffoldReport`
- Governance template library (handles: `governance.spec-first`, `governance.owner-consent`, `governance.deploy-gate`, etc.)
- Infrastructure template library (platform/tenancy/auth/data/frontend parameterized)

### Integration

`src/groundtruth_kb/project/scaffold.py` — ADD
- `spec_scaffold: SpecScaffoldConfig | None = None` field on `ScaffoldOptions`
- Call `scaffold_specs()` at the end of `scaffold_project()` when set

### CLI

`src/groundtruth_kb/cli.py` — ADD
- `gt scaffold specs` subcommand with `--platform`, `--tenancy`, `--auth`, `--frontend`, `--data-store`, `--ai-components`, `--compliance`, `--apply` flags

### File Touchpoints

- `src/groundtruth_kb/spec_scaffold.py` (NEW, ~400 lines)
- `src/groundtruth_kb/project/scaffold.py` (modify)
- `src/groundtruth_kb/cli.py` (add subcommand)
- `tests/test_spec_scaffold.py` (NEW, 8 tests)
- `docs/reference/cli.md` (document `gt scaffold specs`)

### Tests (8)

**Phase A (4):**
1. **Minimal config** — dry run; governance + infra specs appear in report
2. **Full config** — all options including `ai_components=True` and compliance list; all phases emit specs
3. **Non-empty KB skip** — pre-populate governance handle; run apply; verify skip and report counts
4. **Dry-run default** — `scaffold_specs()` with default args writes nothing

**Phase B (2):**
5. **Generated specs have `authority='inferred'`** — apply; verify row has `authority='inferred'`
6. **Owner promotion to `stated`** — apply, then `db.update_spec(id=..., authority='stated', ...)`; verify new version, original preserved

**F3 Quality Validation (2 — NEW):**
7. **Quality summary populated** — apply; `ScaffoldReport.quality_summary` has per-tier counts
8. **Low-quality warning** — synthetic minimal spec triggers `bronze`/`needs-work` tier; appears in `ScaffoldReport.low_quality_warnings`

**scaffold_project() integration (1 — folded into existing test count):**
— Covered by test 1 when called via `scaffold_project(options=ScaffoldOptions(spec_scaffold=...))` instead of directly

(Reordering note: Phase 4 integrates the integration path into test 1 by adjusting fixture setup to call `scaffold_project()` when feasible; otherwise a dedicated test 9 is added. Final count is 8 or 9 tests.)

Revised test count: **9 tests** (4 Phase A + 2 Phase B + 2 F3 quality + 1 scaffold_project integration).

---

## Full Revised F8 Spec (23 tests)

### Modules

- `src/groundtruth_kb/reconciliation.py` — NEW
  - `ReconciliationReport` dataclass
  - `find_orphaned_assertions(db, project_root)`
  - `find_stale_specs(db, *, staleness_threshold_sessions=5, staleness_threshold_days=90)`
  - `find_authority_conflicts(db)`
  - `find_duplicate_specs(db, threshold=0.9)`
- `src/groundtruth_kb/assertions.py` — NO new helper. Optionally promote
  `_safe_glob` and `_safe_resolve` to package-visible via `__all__` addition.

### CLI

`gt kb reconcile [--orphans] [--stale N] [--authority] [--duplicates] [--all]`

### Orphan Detection (reuses `_extract_assertion_targets()` from F2)

- Iterates specs, extracts `AssertionTarget` per assertion
- Dispatches on `target.file_is_glob`: glob-expand via `_safe_glob` or literal-resolve via `_safe_resolve`
- Orphaned when: zero glob matches, missing literal file, or resolution rejected

### Stale Detection (explicit fallback)

- If `len(snapshot_history) >= staleness_threshold_sessions`: compare spec
  signatures across snapshots
- Otherwise: fallback to `changed_at` older than `staleness_threshold_days`

### Authority Conflicts (stated-vs-inferred within same section/scope)

See Finding 4 resolution above.

### Duplicate Detection

Jaccard overlap on title tokens (>= threshold, default 0.9).

### File Touchpoints

- `src/groundtruth_kb/reconciliation.py` (NEW, ~400 lines)
- `src/groundtruth_kb/assertions.py` (optional `__all__` update for glob/resolve helpers)
- `src/groundtruth_kb/cli.py` (add `gt kb reconcile`)
- `tests/test_reconciliation.py` (NEW, 23 tests)
- `docs/reference/cli.md` (document `gt kb reconcile`)

### Tests (23)

**Orphan Detection (12) — reuses existing `_extract_assertion_targets()`:**
1. `grep` literal path exists → not orphaned
2. `grep` literal path missing → orphaned
3. `grep` with `path` alias → normalizes correctly
4. `grep` with `target` alias → normalizes correctly
5. `glob` assertion with matches → not orphaned
6. `glob` zero matches → orphaned
7. `grep` file-glob `src/**/*.py` with matches → not orphaned
8. `grep` file-glob zero matches → orphaned
9. `grep_absent` file-glob zero matches → orphaned
10. `count` file-glob zero matches → orphaned
11. `file_exists` with literal path (no glob dispatch even if `*` in name) → orphaned if missing
12. `all_of` composition with mixed child types → each child extracted; orphans reported per child

**Plain-Text Assertion Safety (3) — existing `_extract_assertion_targets()` already handles non-dict:**
13. Top-level plain-text string alongside dict assertion → string silently skipped
14. `all_of` with plain-text child → plain-text skipped, dict child extracted
15. Non-machine dict child (`{"type":"visual",...}`) → type not in `_VALID_ASSERTION_TYPES`, skipped

**Authority Conflicts (3):**
16. Alias overlap across stated/inferred pair
17. Composition overlap across stated/inferred pair
18. Glob string match across stated/inferred pair

**Stale Detection (3 — NEW):**
19. `test_stale_from_snapshots` — snapshot-backed path with ≥ threshold snapshots
20. `test_stale_fallback_to_changed_at` — fallback path with < threshold snapshots
21. `test_stale_cli_smoke` — `gt kb reconcile --stale 5` returns exit 0

**Provenance (2):**
22. Expired provisional spec with replacement implemented
23. Duplicate detection (90% title overlap)

---

## Implementation Order

1. **F6 first** (9 tests) — new module, `scaffold_project()` integration, F3 quality validation
2. **F8 second** (23 tests) — reconciliation.py reusing F2's extractor

## Combined Verification Plan

1. `python -m pytest -q` — full suite (561 → ~593 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Total Estimated Changes

| Feature | New files | Modified files | Tests | Lines |
|---------|-----------|----------------|-------|-------|
| F6 (A+B+F3) | 2 (spec_scaffold.py, test) | 3 (cli.py, project/scaffold.py, cli.md) | 9 | ~700 |
| F8 | 2 (reconciliation.py, test) | 3 (cli.py, assertions.py [`__all__`], cli.md) | 23 | ~900 |
| **Total** | **4 new, 6 modified** | — | **32** | **~1600** |

## Request

Codex review requested. GO authorizes Phase 4 implementation. This is the final
phase of the GT-KB spec pipeline (F1-F8 complete).
