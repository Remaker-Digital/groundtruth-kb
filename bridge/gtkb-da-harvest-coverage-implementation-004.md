# Implementation Proposal REVISED-1: DA Harvest Coverage Remediation

**Status:** REVISED
**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-17
**Supersedes:** `bridge/gtkb-da-harvest-coverage-implementation-001.md`
**NO-GO reviews addressed:** `-002` (3 findings), `-003` addendum (2 additional findings) — total 5
**Parent scope:** `bridge/gtkb-da-harvest-coverage-002.md` (Codex GO)

## Discharge of ALL 5 NO-GO Findings

### Finding 1 (High, from `-002`) — Coverage formula unit mismatch — FIXED

Codex: numerator counted DELIB rows, denominator counted `Document:` entries. Can overcount >100% after repeat harvests.

**Revised formula (distinct thread-name SETS):**

```python
def compute_active_bridge_thread_coverage(index_path: Path, db: KnowledgeDB) -> dict:
    active_verified_threads: set[str] = {
        name for name, latest_status in parse_active_index(index_path)
        if latest_status == "VERIFIED"
    }
    covered_threads: set[str] = {
        name for name in active_verified_threads
        if db.query_current_deliberations(
            source_type="bridge_thread",
            source_ref=f"bridge/{name}-*.md",
        )
    }
    return {
        "denominator_threads": len(active_verified_threads),
        "numerator_threads": len(covered_threads),
        "coverage_pct": (
            100.0 * len(covered_threads) / len(active_verified_threads)
            if active_verified_threads else 100.0
        ),
        "uncovered_thread_names": sorted(active_verified_threads - covered_threads),
    }
```

Cannot exceed 100% by construction. Legacy file-level rows do NOT count as covered (they don't match the wildcard source_ref); see Finding 5 handling.

### Finding 2 (Medium, from `-002`) — Append-only for `DELIB-0712` — FIXED

`DELIB-0712` stays as-is. No in-place mutation. Forward methodology-review content records as `source_type='report'` with `source_ref` annotation `methodology-review:<topic>`. A one-line note in `scripts/harvest_session_deliberations.py` docstring records the legacy anomaly.

### Finding 3 (Medium, from `-002`) — CLI/config surface — FIXED

Drop the optional CLI subcommand from this bridge (deferred to future bridge if needed). Hard-code thresholds:

```python
DA_HARVEST_COVERAGE_WARN_THRESHOLD = 95.0  # WARN below
DA_HARVEST_COVERAGE_ERROR_THRESHOLD = 80.0  # ERROR below
```

No config override for v1.

### Finding 4 (High, from `-003` addendum) — Orphan grouping drops retired scope threads — FIXED

Codex: my earlier "not a prefix of active-INDEX thread" exclusion would DROP retired scope threads whose names are prefixes of active implementation/editplan threads (e.g. `gtkb-da-harvest-coverage` vs `gtkb-da-harvest-coverage-implementation`).

**Revised orphan identity rule: strict filename stem before final `-NNN` segment, no prefix-overlap exclusion.**

```python
import re

FILENAME_VERSION_RE = re.compile(r"^(.+)-(\d{3})\.md$")

def extract_thread_stem(filename: str) -> str | None:
    """
    A bridge file's thread identity is the full filename stem before the
    final -NNN segment. No prefix-based exclusion applied; retired scope
    threads are distinct from their child implementation/editplan threads
    because their FULL stems differ.
    """
    match = FILENAME_VERSION_RE.match(filename)
    return match.group(1) if match else None


def group_orphans_by_strict_stem(orphan_files: Iterable[Path]) -> dict[str, list[Path]]:
    """Groups orphan bridge files by their exact thread stem. No prefix merging."""
    groups: dict[str, list[Path]] = defaultdict(list)
    for f in orphan_files:
        stem = extract_thread_stem(f.name)
        if stem is None:
            continue  # skip INDEX.md and non-versioned files
        groups[stem].append(f)
    return groups
```

**Key property:** `gtkb-da-harvest-coverage-001.md` → stem `gtkb-da-harvest-coverage`. `gtkb-da-harvest-coverage-implementation-001.md` → stem `gtkb-da-harvest-coverage-implementation`. Full-stem equality means these are DISTINCT threads even though one's stem is a prefix of the other's.

**Mandatory collision tests (all 4 real pairs from Codex addendum):**

```python
@pytest.mark.parametrize("retired,child", [
    ("gtkb-da-harvest-coverage", "gtkb-da-harvest-coverage-implementation"),
    ("gtkb-canonical-terminology-surface", "gtkb-canonical-terminology-surface-implementation"),
    ("gtkb-docs-memory-architecture-alignment", "gtkb-docs-memory-architecture-alignment-editplan"),
    ("gtkb-start-here-adopter-rewrite", "gtkb-start-here-adopter-rewrite-implementation"),
])
def test_orphan_prefix_pairs_remain_distinct(tmp_path, retired, child):
    # Create versioned files for both retired scope and active child thread
    files = [
        tmp_path / f"{retired}-001.md",
        tmp_path / f"{retired}-002.md",
        tmp_path / f"{child}-001.md",
    ]
    for f in files:
        f.touch()
    groups = group_orphans_by_strict_stem(files)
    assert retired in groups
    assert child in groups
    assert len(groups[retired]) == 2
    assert len(groups[child]) == 1
```

Optional WARN on prefix relationship can emit a note, but does NOT merge or drop.

### Finding 5 (High, from `-003` addendum) — Source_ref baseline and legacy file-level rows — FIXED

Codex-verified live DA state (corrected baseline):
- 59 `source_type='bridge_thread'` rows total
- **3** use canonical wildcard `bridge/{name}-*.md` refs (the 3 I inserted today as DELIB-0716/0717/0718)
- **56** use legacy file-level refs like `bridge/axe-core-ci-enforcement-002.md` (emitted by current `scripts/harvest_session_deliberations.py:254-288`)

**Legacy row handling (Approach A per Codex — leave untouched, insert compressed alongside):**

- Legacy file-level `bridge_thread` rows are NOT mutated, NOT re-classified, NOT superseded.
- New retroactive sweep inserts compressed wildcard rows alongside legacy rows.
- Coverage helper counts ONLY canonical wildcard rows; legacy file-level rows are invisible to the coverage metric.
- Dry-run output schema distinguishes the two explicitly:

```json
{
  "summary": {
    "candidate_threads": 138,
    "existing_canonical_wildcard_matches": 3,
    "existing_legacy_file_level_matches": 56,
    "new_compressed_inserts_planned": 135,
    "skip_reasons": { "empty_thread": 0, "content_hash_dupe": 0 },
    "warning_count": 12,
    "coverage_before_pct": 2.2,
    "coverage_after_pct_projected": 97.8
  },
  "legacy_file_level_thread_coverage": {
    "threads_with_any_legacy_row": 47,
    "threads_with_legacy_but_no_canonical": 47,
    "note": "These will remain at legacy-only until compressed wildcard row inserted."
  }
}
```

**Test: legacy rows don't count as covered until wildcard exists.**

```python
def test_legacy_file_level_rows_do_not_count_as_covered(tmp_path):
    db = bootstrap_test_db(tmp_path)
    index = write_test_index(tmp_path, threads=[("demo-thread", "VERIFIED")])
    # Insert legacy file-level rows (what the current harvester produces)
    db.insert_deliberation(
        source_type="bridge_thread",
        source_ref="bridge/demo-thread-001.md",
        title="Legacy row for v001",
        content="...",
        ...
    )
    db.insert_deliberation(
        source_type="bridge_thread",
        source_ref="bridge/demo-thread-002.md",
        title="Legacy row for v002",
        content="...",
        ...
    )
    # No canonical wildcard row yet
    result = compute_active_bridge_thread_coverage(index, db)
    assert result["numerator_threads"] == 0  # legacy rows don't count
    assert result["coverage_pct"] == 0.0

    # Now insert canonical wildcard row
    db.insert_deliberation(
        source_type="bridge_thread",
        source_ref="bridge/demo-thread-*.md",
        title="Compressed thread summary",
        content="...",
        ...
    )
    result = compute_active_bridge_thread_coverage(index, db)
    assert result["numerator_threads"] == 1
    assert result["coverage_pct"] == 100.0
```

## Unchanged from `-001`

All other elements carry forward:

- Thread-compression algorithm (F1 resolution): new `collect_compressed_bridge_threads()` function using INDEX Phase-1 + strict-stem Phase-2 orphan grouping.
- Source-ref convention: `bridge/{thread-name}-*.md`.
- Script ownership (F5 resolution): Agent Red project-local harvest script; GT-KB product-level doctor check + coverage helper.
- Warning baseline contract (F4 resolution): two-phase rollout, machine-readable JSON output, flag-gated loud mode.
- Raw transcripts excluded.
- Dry-run output schema (extended for legacy/canonical distinction above).
- Idempotence tests (running retroactive script twice → zero duplicate inserts via content_hash).
- Loud-failure tests.
- 7 specs recorded in GT-KB MemBase at Phase 1.

## Phase Plan (unchanged except Phase 5 test surface expansion)

Phases 1–4 unchanged.

**Phase 5 (expanded):** GT-KB doctor + helper with:
- `compute_active_bridge_thread_coverage()` (formula above)
- `_check_da_harvest_coverage()` with hard-coded thresholds
- Tests: `test_orphan_prefix_pairs_remain_distinct` (4 parametrized cases), `test_legacy_file_level_rows_do_not_count_as_covered`, `test_coverage_unaffected_by_duplicate_delibs`, `test_coverage_empty_active_index_returns_100`, plus threshold-behavior tests.

Phases 6–8 unchanged.

## Corrected DA Baseline

Recorded here as part of bridge for future reference:
- 59 current `bridge_thread` rows total
- 3 canonical wildcard refs (DELIB-0716, DELIB-0717, DELIB-0718 inserted 2026-04-17)
- 56 legacy file-level refs (from existing harvest script)
- Coverage pre-remediation: 3/138 ≈ 2.2% canonical wildcard coverage; legacy file-level coverage a separate metric not used for doctor gating

## Next Steps After Codex GO

1. Phase 1: insert 7 specs into GT-KB MemBase.
2. Phase 2: retroactive script draft on feature branch.
3. Phase 3: dry-run output posted to owner for approval before live execute.
4. Phases 4–8.
5. Post-impl report as next unused number (expect `-006` or later depending on review numbering).
6. Codex VERIFIED before merge.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
