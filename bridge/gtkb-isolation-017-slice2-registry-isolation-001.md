NEW

# GTKB-ISOLATION-017 Slice 2 Implementation: Registry Isolation Labels + AST Gate CI Wiring

**Status:** NEW (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Predecessor:** `bridge/gtkb-isolation-017-scoping-003.md` REVISED-1 GO at `-004`. Slice 2 of the 8-slice plan.
**Owner pre-approval:** per `memory/work_list.md` autonomous-execution clause + S324 priority elevation banner placing GTKB-ISOLATION program at TOP. Per scoping decision-map (`gtkb-isolation-017-scoping-003.md` lines 39-55), Slice 2 owns 0 of the 7 Phase 9 owner decisions.

---

## Scope Of This Commit

This proposal commit lands ONLY:

- `bridge/gtkb-isolation-017-slice2-registry-isolation-001.md` (this file)
- `bridge/INDEX.md` updated with the `Document: gtkb-isolation-017-slice2-registry-isolation` entry

This commit does NOT modify `managed_registry.py`, `ownership.py`, templates, CI workflows, or land tests. Those changes ship in the implementation commit after Codex GO. Explicit scope statement preempts proposal-vs-implementation divergence.

## Specification Links

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 405-407 — Regression Visibility: "AST gate ... must run in CI and fail on unregistered files or unmatched globs"; "Registry drift must be detectable"
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` lines 84, 104-120 — Authority matrix structure; per-row migration_action and rationale columns
- `bridge/gtkb-isolation-017-scoping-003.md` lines 78-91 — Slice 2 acceptance criteria carried forward
- `bridge/gtkb-isolation-017-scoping-004.md` — Codex GO scoping authority for this implementation slice
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — adopter-vs-product-root governance that Slice 2 enforces at the registry layer
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 52-118, 122-202 — existing `OwnershipEnum`, `OwnershipMeta` dataclass, `FileArtifact`/`SettingsHookRegistration`/`GitignorePattern`/`OwnershipGlobArtifact` types
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 104-280 — `OwnershipResolver` API
- `groundtruth-kb/templates/managed-artifacts.toml` — the registry of FILE-class records (~40 entries)
- `groundtruth-kb/templates/scaffold-ownership.toml` — the ownership-glob sibling map
- `groundtruth-kb/templates/{hooks,rules,ci,project}/` — the scaffolded-file source trees the AST gate walks
- `groundtruth-kb/.github/workflows/ci.yml` — existing CI lane that the AST gate wires into
- `.claude/rules/project-root-boundary.md` — Slice 2 lands under `E:\GT-KB`
- `.claude/rules/file-bridge-protocol.md` — Specification Linkage Gate, Specification-Derived Verification Gate
- `.claude/rules/codex-review-gate.md` — Codex GO required before implementation
- `GOV-09`, `GOV-20`

## Owner Decisions

**None for Slice 2.** Per the scoping Decision Map, all 7 Phase 9 owner decisions are owned by Slices 4, 6, 7, or 8.

## Schema Survey — What Already Exists

To preempt scope-overstatement (a recurring NO-GO class), this section maps Slice 2 acceptance items to existing schema:

| Acceptance item (scoping `-003` lines 82-89) | Existing surface | Slice 2 action |
|---|---|---|
| "Registry schema updated with `owner` and `upgrade_policy` fields" | `OwnershipMeta.ownership` (`OwnershipEnum`) at `managed_registry.py:129` covers owner semantics; `OwnershipMeta.upgrade_policy` at `:130` covers upgrade policy | **No schema change required**; document and lock via tests |
| "Per-entry rationale captured" | `OwnershipMeta.notes` field exists at `:131` (or `OwnershipRecord.notes` at `ownership.py:118`); some entries are blank | **Add `notes` requirement test**: every `gt-kb-managed`/`gt-kb-scaffolded` row MUST have non-empty `notes` (machine-checkable rationale) |
| "AST gate test asserting registry coverage of scaffolded files" | None | **NEW**: `tests/test_registry_ast_coverage.py` walks `templates/` and asserts each file is covered by FILE-class or ownership-glob |
| "AST gate wired into groundtruth-kb CI" | `.github/workflows/ci.yml` `test-base` lane | **Wired** by virtue of being a pytest test; verified by lane comment + a test asserting the test file lives under `tests/` (CI runs `tests/`) |
| "Migration-note discipline (no owner-flip without note)" | None | **NEW**: `tests/test_registry_ownership_flip_discipline.py` asserts that when a row's `ownership` value changes (vs a golden snapshot in `tests/fixtures/registry-ownership-snapshot.toml`), a paired migration-note row exists |
| "Registry-drift detection in CI" | None | **NEW**: drift test compares the live `OwnershipResolver.all_records()` output against a deterministic golden snapshot; mismatches fail with a remediation message |
| "Tests, IPR, CVR" | KB API | Implemented per GOV-20 Phase 1 advisory pilot |

**Key principle:** Slice 2 deliberately does NOT add a new `access_model` or `denied_operations` field to `OwnershipMeta` despite Phase 1 authority matrix mentioning denied/access semantics. That schema extension is deferred to a future slice (call it Slice 2.5 or a follow-on sub-slice) once Phase 3 environment-isolation work surfaces concrete denied-path semantics. Slice 2's contract is REGISTRY COVERAGE + DRIFT GATING using the existing schema; it does NOT extend the schema. This narrowing reduces NO-GO risk and keeps Slice 2 within its envelope.

## Implementation Plan

Implementation commit (after Codex GO) lands the following:

### 1. AST gate: registry coverage of scaffolded files

**File (new):** `groundtruth-kb/tests/test_registry_ast_coverage.py` (~120 LOC)

```python
def test_every_scaffolded_file_has_registry_coverage() -> None:
    """AST gate per Phase 9 §"Regression Visibility" line 406.

    Walks every file under groundtruth-kb/templates/ (excluding the registry
    files themselves) and asserts each is classified by OwnershipResolver as
    a non-fallback record. Fallback classifications (synthetic
    `__fallback__:...` records) indicate registry drift: a file exists that
    no FILE-class row and no ownership-glob covers.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    templates_root = _templates_dir()
    excluded = {"managed-artifacts.toml", "scaffold-ownership.toml"}
    resolver = OwnershipResolver()

    unregistered: list[str] = []
    for path in templates_root.rglob("*"):
        if not path.is_file():
            continue
        if path.name in excluded:
            continue
        # Skip `__pycache__` artifacts.
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(templates_root).as_posix()
        record = resolver.classify_path(rel)
        if record.source_class == "__fallback__":
            unregistered.append(rel)

    assert not unregistered, (
        f"AST gate failure: {len(unregistered)} scaffolded files lack registry "
        f"coverage. First 5: {unregistered[:5]}. Add a FILE-class record to "
        f"`templates/managed-artifacts.toml` or extend an ownership-glob in "
        f"`templates/scaffold-ownership.toml`."
    )
```

**Satisfies:** Phase 9 §"Regression Visibility" lines 405-406 ("AST gate ... must run in CI and fail on unregistered files").

### 2. Per-entry rationale (notes) discipline

**File (new):** `groundtruth-kb/tests/test_registry_rationale_discipline.py` (~50 LOC)

```python
def test_every_product_managed_row_has_rationale() -> None:
    """Per scoping `-003` line 84: per-entry rationale captured.

    Asserts every `gt-kb-managed` or `gt-kb-scaffolded` ownership record has
    non-empty `notes`. Adopter-owned and legacy-exception rows are exempt
    (their rationale lives in upstream policy, not the registry).
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    missing: list[str] = []
    for record in resolver.all_records():
        if record.ownership in ("gt-kb-managed", "gt-kb-scaffolded"):
            if not (record.notes or "").strip():
                missing.append(f"{record.id} ({record.ownership})")

    assert not missing, (
        f"{len(missing)} product-scope records lack `notes` rationale. "
        f"First 10: {missing[:10]}. Add a `notes = '...'` line explaining "
        f"why the file is product-managed."
    )
```

**Satisfies:** scoping `-003` line 84 ("Per-entry rationale captured").

### 3. Migration-note discipline (no owner-flip without note)

**File (new):** `groundtruth-kb/tests/test_registry_ownership_flip_discipline.py` (~80 LOC)
**Fixture (new):** `groundtruth-kb/tests/fixtures/registry-ownership-snapshot.toml` (golden snapshot of current state)

```python
def test_ownership_flips_require_migration_note() -> None:
    """Per scoping `-003` line 87: no owner-flip without migration note.

    Compares the live OwnershipResolver records against a golden snapshot
    in tests/fixtures/registry-ownership-snapshot.toml. For each record
    whose `ownership` value differs from the snapshot, asserts the live
    record has a `notes` line containing 'migration:' or 'flipped from:'
    citing the prior ownership value.

    To update the snapshot intentionally: edit a row's `ownership` AND add
    a `notes = "...migration: prev=<old> reason=<why>..."` line, then
    regenerate the snapshot via `python -m pytest --update-registry-snapshot`.
    """
    ...  # implementation per the docstring
```

**Snapshot file:** static TOML with `[[record]] id = "..." ownership = "..."` rows for every current record. Regeneration is a deliberate dev step (snapshot fixture, not auto-regenerated in CI).

**Satisfies:** scoping `-003` line 87.

### 4. Registry-drift detection

**File (new):** `groundtruth-kb/tests/test_registry_drift_detection.py` (~60 LOC)

```python
def test_registry_drift_against_snapshot() -> None:
    """Per Phase 9 §"Regression Visibility": Registry drift must be detectable.

    Compares the count + ID set of OwnershipResolver.all_records() against
    a golden count fixture. Counts diverging by more than 0 fail the test
    with a list of added/removed IDs and a remediation message pointing
    to the snapshot regeneration recipe.
    """
    ...
```

**Fixture (new):** `groundtruth-kb/tests/fixtures/registry-id-set.txt` — sorted list of all record IDs; updated only via deliberate regeneration step.

**Satisfies:** Phase 9 §"Regression Visibility" line 407 ("Registry drift must be detectable").

### 5. CI wiring (already satisfied via test placement)

The four new test files live under `groundtruth-kb/tests/`. The existing CI lane `test-base` (`groundtruth-kb/.github/workflows/ci.yml:24-58`) runs `pytest tests/` on push/PR for branches `main` and `develop` across Python 3.11/3.12/3.13. Therefore the AST gate, rationale discipline, ownership-flip discipline, and drift detection ALL run in CI by virtue of being pytest tests under `tests/`.

**Documentation step:** Add a comment block to `ci.yml` referencing GTKB-ISOLATION-017 Slice 2 next to the existing matrix-rationale comment, so future maintainers know the registry-coverage tests are load-bearing for isolation.

**Satisfies:** scoping `-003` line 86 ("AST gate wired into `groundtruth-kb` CI").

### 6. KB documents (per GOV-20 Phase 1 advisory pilot)

- Pre-implementation: `IPR-SLICE2-REGISTRY-ISOLATION-001` document inserted via `db.insert_document()` before code lands. Tagged `GOV-20`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GTKB-ISOLATION-017`, `slice-2`.
- Post-implementation: `CVR-SLICE2-REGISTRY-ISOLATION-001` document inserted after smoke + tests pass. Same tags. Documents test-to-spec mapping and live evidence.

## Output Layout (no runtime output for Slice 2)

Slice 2 has no runtime output directory (test files + fixtures + comment edits in source tree). All artifacts land under `E:\GT-KB\groundtruth-kb\tests\`.

## Specification-Derived Verification

| # | Test | Derives from |
|---|---|---|
| T1 | `test_every_scaffolded_file_has_registry_coverage` | Phase 9 §"Regression Visibility" line 406 (AST gate) |
| T2 | `test_every_product_managed_row_has_rationale` | scoping `-003` line 84 (per-entry rationale) |
| T3 | `test_ownership_flips_require_migration_note` | scoping `-003` line 87 (migration-note discipline) |
| T4 | `test_registry_drift_against_snapshot` | Phase 9 §"Regression Visibility" line 407 (drift detection) |
| T5 | `test_ast_gate_test_file_lives_under_tests_directory` | scoping `-003` line 86 (CI wiring; meta-test asserting test path) |
| T6 | `test_ast_gate_fallback_classification_indicates_drift` | sanity check that `OwnershipResolver.classify_path` returns `__fallback__:...` source_class for unregistered paths |
| T-IPR-CVR | `test_ipr_and_cvr_slice2_documents_exist_with_adr_tag` | GOV-20 Phase 1 advisory pilot |

Plus regression coverage: existing `groundtruth-kb/tests/` suite must remain green.

**Test execution commands** (post-implementation report):

```bash
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_registry_ast_coverage.py tests/test_registry_rationale_discipline.py tests/test_registry_ownership_flip_discipline.py tests/test_registry_drift_detection.py -q --tb=short --timeout=60
python -m pytest tests/ -q --tb=short --timeout=120  # full regression
python -m ruff check tests/test_registry_*.py
python -m ruff format --check tests/test_registry_*.py
```

Live smoke run: the AST gate run against the live `groundtruth-kb/templates/` tree should reveal the actual registry coverage state (expected to surface some unregistered files; if so, Slice 2 either adds the missing registry entries or files them as known-drift items per the migration-note discipline).

## Risk / Impact

**Snapshot fixture maintenance burden (medium):** the migration-note discipline test requires a golden fixture that must be updated whenever a row's ownership changes. Mitigation: regeneration recipe is one command; the deliberate-step requirement is the *point* of the discipline (preventing silent flips).

**AST gate first-run failures (medium):** running the AST gate against the live registry will likely surface one or more unregistered files (the registry has had organic growth without machine-checked coverage). Mitigation: implementation commit either adds the missing FILE-class rows OR documents them as deliberate exceptions in a follow-up fix-up commit. The post-implementation report enumerates any first-run gaps.

**No new schema fields (low):** Slice 2 deliberately does NOT extend `OwnershipMeta` with new fields. Future slices may add `access_model` / `denied_operations` once Phase 3 work surfaces concrete needs. T2/T3 use existing `notes` and `ownership` fields only.

**CI lane wiring (low):** the new tests live under `tests/`, which is already pytest-collected by the existing CI matrix. No workflow YAML change required beyond a documentation comment.

**Snapshot drift on unrelated PRs (low):** any PR that adds a new file to `templates/` without a registry entry will fail T1; any ownership change without a migration note will fail T3. This is the desired enforcement, not a regression.

## Acceptance Criteria

This proposal is GO-able when Codex confirms:

1. AST gate test (T1) walks every `templates/` file and asserts non-`__fallback__` classification.
2. Rationale discipline (T2) requires non-empty `notes` for `gt-kb-managed`/`gt-kb-scaffolded` records only.
3. Migration-note discipline (T3) compares ownership values against a golden snapshot; flips require a paired note.
4. Drift detection (T4) compares ID set against a golden fixture.
5. CI wiring is satisfied by test-file placement under `tests/`; documentation comment in `ci.yml` confirms intent.
6. Schema is NOT extended (existing `OwnershipMeta` fields are sufficient); deferred extensions noted as future-slice work.
7. IPR/CVR document creation steps in scope (T-IPR-CVR covers post-impl).
8. Specification Links covers all governing artifacts.
9. Scope of the proposal commit matches what will land (proposal + INDEX only).

## Decision Needed From Owner

**Nothing required at GO time.** Slice 2 owns 0 of the 7 Phase 9 owner decisions per the scoping Decision Map.

Optional follow-up (not blocking Slice 2):
- Whether the migration-note discipline should require a structured field (e.g., `migration_note = {prev_ownership = "X", reason = "Y"}`) instead of free-text `notes`. Not blocking; can tighten in a later slice if free-text proves error-prone.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
