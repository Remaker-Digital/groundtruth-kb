# Phase 4: F6 (A+B) + F8 — Implementation Proposal

**Author:** Prime Builder (Opus 4.6)
**Session:** S288
**Date:** 2026-04-13
**Type:** Implementation Proposal
**Prerequisite:** Phase 3 VERIFIED (awaiting -017 review; F7 + F5 committed b2d425c)
**Approved designs:** F6-003 (GO: F6-004), F8-013 (GO: F8-014)
**Cross-check:** gtkb-f1f8-cross-check-001 (GO: -002)

## Rationale

Phase 4 closes the GT-KB spec pipeline by adding two final features:

- **F6 Project Scaffold Generator** — emits seed spec templates for new projects,
  with generated specs marked `authority='inferred'` so they are explicitly
  distinguished from owner-confirmed requirements until promoted.
- **F8 Provenance Reconciliation** — detects stale specs, orphaned assertions
  (file targets that no longer exist in the project tree), authority conflicts
  between aliased spec fields, and duplicate specs by title overlap.

Both features are independent of each other. F6 is implemented first because
it is self-contained (new module + CLI + a handful of tests). F8 builds on
the existing assertion infrastructure and F7 snapshot history and has the
larger test matrix (20 cases).

Neither F6 nor F8 is present in the current groundtruth-kb main branch:
`rg -n "scaffold_specs|reconciliation|_extract_file_targets"` returns no
matches. Phase 4 implements both end-to-end.

---

## F6: Project Scaffold Generator (Phase A + B)

### No New Tables

F6 writes generated specs via the existing `insert_spec()` API. Phase A uses
only existing schema; Phase B populates F1's `authority` field.

### Data Model

```python
# src/groundtruth_kb/spec_scaffold.py (NEW module)

@dataclass
class SpecScaffoldConfig:
    """Configuration for seed spec generation.

    NOT the same as ProjectProfile (which selects the project scaffold profile).
    """
    platform: str          # 'azure' | 'aws' | 'gcp' | 'self-hosted'
    tenancy: str           # 'multi-tenant' | 'single-tenant'
    auth_model: str        # 'magic-link' | 'password' | 'oauth' | 'api-key' | 'mixed'
    frontend: str          # 'spa' | 'ssr' | 'none'
    data_store: str        # 'cosmos' | 'postgres' | 'mysql' | 'dynamodb' | 'mongo'
    ai_components: bool = False
    compliance: list[str] = field(default_factory=list)  # ['gdpr', 'hipaa', 'soc2']


@dataclass
class ScaffoldReport:
    phases: list[dict[str, Any]]
    total_generated: int
    total_skipped: int
    specs: list[dict[str, Any]]  # For review before apply (dry-run)
```

### Authority Policy (Phase B)

Generated specs are **always** marked with `authority='inferred'` when F1 is
available (which it is). This prevents AI-generated templates from being
treated as owner directives before review. The owner confirms specs individually
or in batch to promote them to `authority='stated'`:

```python
db.update_spec(
    id=spec_id,
    changed_by="owner",
    change_reason="Owner confirmed scaffold spec",
    authority="stated",
)
```

### API

```python
def scaffold_specs(
    db: KnowledgeDB,
    config: SpecScaffoldConfig,
    *,
    dry_run: bool = True,
) -> ScaffoldReport
```

- `dry_run=True` (the default) returns a populated `ScaffoldReport` without
  writing any specs.
- `dry_run=False` writes the generated specs via `insert_spec()`, each with
  `authority='inferred'` and tag `scaffold-generated`.
- On non-empty KBs: skips any existing `GOV-*` handle (no overwrite),
  prefixes non-governance spec IDs with `_scaffold_` for easy identification,
  and reports `total_skipped`.

### Governance Template Library

Phase A generates a fixed set of **governance seed specs** derived from the
Agent Red GOV-01-20 set (using paraphrased, project-neutral language). Each
seed spec is keyed by a stable handle (`governance.spec-first`,
`governance.owner-consent`, `governance.deploy-gate`, etc.) so that non-empty
KB skip detection works reliably.

### Infrastructure Template Library

Phase A generates platform-specific infrastructure specs parameterized by
`SpecScaffoldConfig` fields:

- `infra.platform-{azure|aws|gcp|self-hosted}` — one spec describing the
  chosen deployment target
- `infra.tenancy-{multi-tenant|single-tenant}` — isolation requirements
- `infra.auth-{magic-link|password|oauth|api-key|mixed}` — authentication model
- `infra.data-store-{cosmos|postgres|...}` — persistence layer
- `infra.frontend-{spa|ssr|none}` — UI architecture
- `infra.ai-components` — generated when `ai_components=True`
- `infra.compliance-{gdpr|hipaa|soc2}` — one spec per item in `compliance`

### CLI

```
gt scaffold specs [--platform PLATFORM] [--tenancy TENANCY]
                  [--auth AUTH] [--frontend FRONTEND]
                  [--data-store DATA_STORE] [--ai-components]
                  [--compliance COMPLIANCE]... [--apply]
```

- Without `--apply`, performs a dry run and prints the generated specs.
- With `--apply`, writes the specs to the KB.

### File Touchpoints

- `src/groundtruth_kb/spec_scaffold.py` — NEW module (config dataclass,
  template library, `scaffold_specs()`, `ScaffoldReport`)
- `src/groundtruth_kb/cli.py` — `gt scaffold specs` subcommand
- `tests/test_spec_scaffold.py` — NEW, 6 tests
- `docs/reference/cli.md` — `gt scaffold specs` documentation

### Tests (6)

**Phase A (4):**
1. **Minimal config** — `SpecScaffoldConfig(platform='self-hosted', tenancy='single-tenant', auth_model='password', frontend='none', data_store='postgres')`; dry-run; verify governance + infra specs appear in report
2. **Full config** — all options populated including `ai_components=True` and `compliance=['gdpr','hipaa','soc2']`; verify all phases emit specs
3. **Non-empty KB skip** — pre-populate KB with a spec whose handle collides with a governance template; run scaffold (apply); verify that spec is skipped and reported, remaining specs generated
4. **Dry-run** — run with default `dry_run=True`; verify report populated and NO rows inserted into the DB

**Phase B (2):**
5. **Generated specs have `authority='inferred'`** — apply scaffold; verify all generated specs have `authority='inferred'` on the persisted row
6. **Owner confirmation promotes to `stated`** — apply scaffold; call `db.update_spec(id=..., authority='stated', ...)`; verify the new version has `authority='stated'` and the original `inferred` version is preserved in history

---

## F8: Provenance Reconciliation

### No New Tables

F8 reads existing spec columns, `affected_by_parsed`, `provisional_until`,
and F7's `session_snapshots` table. All detectors return in-memory reports.

### Typed File Target Extraction

F8 introduces `_extract_file_targets()` with type-specific dispatch rules
that mirror the assertion runner's file-target semantics. This is a
**separate helper** from F2's `_extract_assertion_targets()` because:

- F2 builds `AssertionTarget` (with `file_is_glob`) for conflict detection
  (same-file/same-pattern comparison).
- F8 builds `TypedFileTarget` (with `use_glob`) for dispatch decisions
  (should we glob-expand or literal-resolve?).

Both helpers can live in `assertions.py` next to
`_extract_assertion_targets()` and import the same internals
(`_normalize_assertion`, `_VALID_ASSERTION_TYPES`, `_MAX_COMPOSITION_DEPTH`).

```python
# src/groundtruth_kb/assertions.py (existing module)

_GLOB_CAPABLE_TYPES = frozenset({"grep", "grep_absent", "count"})


@dataclass(frozen=True)
class TypedFileTarget:
    assertion_type: str
    target: str
    use_glob: bool


def _extract_file_targets(
    assertion: Any,
    depth: int = 0,
) -> list[TypedFileTarget]:
    """Extract typed file targets with runner-matching dispatch.

    Plain-text (non-dict) assertions are silently skipped to match
    the runner's behavior in `_dispatch_single()` and the schema
    validator's treatment of non-dict entries as valid human notes.
    """
    # Guard at entry
    if not isinstance(assertion, dict):
        return []

    a_type = assertion.get("type", "")
    if a_type not in _VALID_ASSERTION_TYPES:
        return []

    # Composition: recurse, guard applies to each child
    if a_type in ("all_of", "any_of"):
        if depth >= _MAX_COMPOSITION_DEPTH:
            return []
        result: list[TypedFileTarget] = []
        for child in assertion.get("assertions", []):
            result.extend(_extract_file_targets(child, depth + 1))
        return result

    normalized = _normalize_assertion(assertion)
    file_target = normalized.get("file")

    # glob: always glob dispatch, target is the pattern
    if a_type == "glob":
        pattern = normalized.get("pattern")
        if pattern:
            return [TypedFileTarget("glob", pattern, use_glob=True)]
        return []

    # json_path, file_exists: always literal
    if a_type in ("json_path", "file_exists"):
        if file_target:
            return [TypedFileTarget(a_type, file_target, use_glob=False)]
        return []

    # grep, grep_absent, count: glob dispatch only when "*" in file_target
    if file_target:
        use_glob = a_type in _GLOB_CAPABLE_TYPES and "*" in file_target
        return [TypedFileTarget(a_type, file_target, use_glob=use_glob)]

    return []
```

### New Module

```python
# src/groundtruth_kb/reconciliation.py (NEW)

@dataclass
class ReconciliationReport:
    category: str  # 'orphans' | 'stale' | 'authority_conflicts' | 'duplicates'
    items: list[dict[str, Any]]
    count: int


def find_orphaned_assertions(
    db: KnowledgeDB,
    project_root: Path,
) -> ReconciliationReport
```

**Behavior per type:**
- `glob`: resolve pattern via `_safe_glob()`; if it yields zero matches, the
  assertion is orphaned
- `json_path`, `file_exists`: resolve literal via `_safe_resolve()`; if the
  resolved path does not exist, orphaned
- `grep`/`grep_absent`/`count` with `use_glob=True`: glob pattern; orphaned if
  zero matches
- `grep`/`grep_absent`/`count` with `use_glob=False`: literal path; orphaned
  if file missing

```python
def find_stale_specs(
    db: KnowledgeDB,
    staleness_threshold_sessions: int = 5,
) -> ReconciliationReport
```

Uses F7's `get_snapshot_history()` to find specs that have not been mentioned
in any snapshot's derived state for the last N sessions. Bootstrap behavior:
if fewer than `staleness_threshold_sessions` snapshots exist, returns an
empty list (documented in the cross-check as a trailing indicator).

Falls back to `specifications.changed_at` when snapshot history is insufficient
for a full stale evaluation.

```python
def find_authority_conflicts(db: KnowledgeDB) -> ReconciliationReport
```

Detects cases where the same spec has inconsistent authority signals across
aliases (e.g., `affected_by` names conflict with the spec's own authority).
Uses `_find_matching_constraints()` and assertion-target alias overlap.

```python
def find_duplicate_specs(db: KnowledgeDB, threshold: float = 0.9) -> ReconciliationReport
```

Tokenizes spec titles into word sets, computes Jaccard overlap, reports pairs
where overlap >= threshold (default 0.9).

### CLI

```
gt kb reconcile [--orphans] [--stale N] [--authority] [--duplicates] [--all]
```

- Each flag enables one detector.
- `--all` enables all four.
- Output is a text report grouped by category.

### File Touchpoints

- `src/groundtruth_kb/assertions.py` — add `TypedFileTarget`, `_GLOB_CAPABLE_TYPES`, `_extract_file_targets()`
- `src/groundtruth_kb/reconciliation.py` — NEW module (detectors, report dataclass)
- `src/groundtruth_kb/cli.py` — `gt kb reconcile` subcommand
- `tests/test_reconciliation.py` — NEW, 20 tests
- `docs/reference/cli.md` — `gt kb reconcile` documentation

### Tests (20)

**Orphan Detection (12):**
1. `grep` literal path that exists → not orphaned
2. `grep` literal path that doesn't exist → orphaned
3. `grep` with `path` alias → normalizes via `_normalize_assertion()`
4. `grep` with `target` alias → normalizes
5. `glob` assertion that finds matches → not orphaned
6. `glob` assertion with zero matches → orphaned
7. `grep` with file-glob `src/**/*.py` matching files → not orphaned
8. `grep` with file-glob `src/**/*.py` with zero matches → orphaned
9. `grep_absent` with file-glob zero matches → orphaned (nothing to check)
10. `count` with file-glob zero matches → orphaned
11. `file_exists` with literal path (no glob dispatch even if `*` present) → orphaned if missing
12. `all_of` with mixed `grep` + `glob` + `grep_absent` children → each child extracted separately; orphans reported per child

**Plain-Text Assertion Safety (3):**
13. Top-level plain-text string assertion alongside a dict assertion → string silently skipped, dict processed
14. `all_of` with plain-text child and grep child → plain-text skipped, grep extracted
15. Non-machine dict child (`{"type": "visual", ...}`) → type not in `_VALID_ASSERTION_TYPES`, skipped

**Authority Conflicts (3):**
16. Same assertion target appears in two specs with different `authority` values → reported
17. Composition overlap: child of one spec's `all_of` matches child of another's → reported
18. Glob pattern matches identically → reported

**Provenance (2):**
19. Spec with `authority='provisional'` whose `provisional_until` target is now `implemented` → expired provisional reported
20. Two specs whose title tokens overlap >= 90% → duplicate pair reported

---

## Implementation Order

1. **F6 first** (6 tests) — self-contained, no assertion-internals changes
2. **F8 second** (20 tests) — add `TypedFileTarget` + `_extract_file_targets()` to assertions.py, then build reconciliation.py on top

## Combined Verification Plan

1. `python -m pytest -q` — full suite (561 → ~587 tests)
2. `python -m ruff check . && python -m ruff format --check .`
3. `python scripts/check_docs_cli_coverage.py`

## Total Estimated Changes

| Feature | New files | Modified files | Tests | Lines |
|---------|-----------|----------------|-------|-------|
| F6 (A+B) | 2 (spec_scaffold.py, test) | 2 (cli.py, cli.md) | 6 | ~650 |
| F8 | 2 (reconciliation.py, test) | 3 (assertions.py, cli.py, cli.md) | 20 | ~900 |
| **Total** | **4 new, 5 modified** | — | **26** | **~1550** |

## Request

Codex review requested. GO authorizes Phase 4 implementation. This is the final
phase of the GT-KB spec pipeline (F1-F8 complete).
