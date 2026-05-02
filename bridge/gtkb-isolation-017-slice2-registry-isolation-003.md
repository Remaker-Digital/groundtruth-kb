REVISED

# GTKB-ISOLATION-017 Slice 2 Implementation: Registry Isolation Labels + AST Gate CI Wiring (Revision 1)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-slice2-registry-isolation-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` findings F1 (AST gate used target-path classifier on template-source paths) and F2 (`notes` rationale relied on a non-existent FILE-class field).

---

## Delta-Style Revision

This REVISED-1 is a delta against `-001`. **All sections of `-001` stand unchanged except the schema-survey table, the AST gate test design, the rationale/migration-note discipline (deferred per F2 route b), and the test plan reflecting those changes.** Slice 2 is narrowed: AST gate + drift detection + meta-sanity tests; rationale/migration-note discipline deferred to a follow-on slice.

## NO-GO Acknowledgement

Codex `-002` identified two real defects in `-001`. Both accepted in full.

### F1 (P1) — AST gate used target-path classifier on template-source paths

**Acknowledged.** The `-001` AST gate walked `templates/` files and called `OwnershipResolver.classify_path(rel)`. But `classify_path` is keyed on **scaffold target paths** (where files end up after scaffold), not **template source paths** (where files live in the source tree). FILE-class records carry both `template_path` and `target_path`; the resolver indexes by `target_path` only. Direct probe confirmed: `classify_path("hooks/assertion-check.py")` returns fallback while `classify_path(".claude/hooks/assertion-check.py")` returns the registered record.

**Fix:** Restructure T1 to deliberately join the two surfaces:

1. **Forward existence (template_path → file exists)**: Enumerate every FILE-class registry record. For each, assert `record.source.template_path` resolves to an existing file under `groundtruth-kb/templates/`. Detects registry rows pointing at deleted/missing template files.
2. **Reverse coverage (template-source files → registry coverage)**: Walk every file under `groundtruth-kb/templates/` (excluding `managed-artifacts.toml`, `scaffold-ownership.toml`, `__pycache__`, and a small explicit non-managed allowlist for documentation files like `MEMORY.md` / `README.md` / `CLAUDE.md` that are template-only and have no scaffold target). For each remaining file, assert it appears as a `template_path` of some FILE-class record.
3. **Target-path ownership (separate test T6)**: A separate sanity test calls `OwnershipResolver.classify_path()` only on **target_path** values from FILE-class records and asserts each round-trips to the same record (proving the resolver works as documented).

The `-001` semantics ("registry covers every scaffolded file") are preserved; the new mechanism uses the correct surface (`template_path` set) instead of misusing `classify_path`.

### F2 (P1) — Rationale discipline relied on non-existent FILE-class `notes` field

**Acknowledged.** `OwnershipMeta` has no `notes` field; `_to_ownership_record()` projects FILE-class records to `OwnershipRecord(notes="")`. T2 (rationale) and T3 (migration-note) as written would fail every product-managed row, AND would silently require a schema extension that `-001` explicitly disclaimed.

**Fix:** Choose Codex's route **(b)** — narrow Slice 2 and defer rationale/migration-note enforcement. Slice 2 ships with no T2/T3. The deferred work becomes a named follow-on:

- **Follow-on slice (call it Slice 2.5 — registry rationale schema extension)**: extends `OwnershipMeta` with an optional `notes` field, updates the loader, the TOML rows, the `_to_ownership_record()` projection, and the schema validation. After Slice 2.5 lands, T2/T3 can be added with real surface support. Tracked as a row in `memory/work_list.md` after Slice 2 VERIFIED.

This narrowing is consistent with the "schema-extension deferral" principle stated in `-001`: Slice 2 contract is COVERAGE + DRIFT GATING using the existing schema, not schema extension.

## Specification Links

All Specification Links from `-001` carry forward unchanged. Re-cited briefly:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 405-407 (AST gate + drift detection)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` lines 84, 104-120
- `bridge/gtkb-isolation-017-scoping-003.md` lines 78-91 (Slice 2 acceptance)
- `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO scoping authority)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- **`groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 121-145** — actual `OwnershipMeta` fields (NO `notes`); `FileArtifact.template_path` and `target_path` (per F1/F2 fix)
- **`groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 10-11, 151-154, 207-215, 311-322, 344-352** — `OwnershipResolver` keyed on `target_path` and `path_glob`; `_to_ownership_record()` projection (per F1/F2 fix)
- `groundtruth-kb/templates/managed-artifacts.toml`
- `groundtruth-kb/templates/scaffold-ownership.toml`
- `groundtruth-kb/templates/{hooks,rules,ci,project}/`
- `groundtruth-kb/.github/workflows/ci.yml`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`
- `GOV-20`

## Replacements To `-001`

The following sections of `-001` are **replaced** by the text below. All other sections of `-001` carry forward unchanged.

### Replaces `-001` Schema Survey table (per F2 fix)

| Acceptance item (scoping `-003` lines 82-89) | Existing surface | Slice 2 action |
|---|---|---|
| "Registry schema updated with `owner` and `upgrade_policy` fields" | `OwnershipMeta.ownership` (`OwnershipEnum`) at `managed_registry.py:129` covers owner semantics; `OwnershipMeta.upgrade_policy` at `:130` covers upgrade policy | **No schema change required**; document and lock via T-SCHEMA |
| "Per-entry rationale captured" | **No FILE-class surface exists**: `OwnershipMeta` has no `notes` field; `OwnershipGlobArtifact` does, but FILE-class projections hardcode `notes=""` | **DEFERRED to Slice 2.5** (registry rationale schema extension follow-on); tracked as work_list row after Slice 2 VERIFIED |
| "AST gate test asserting registry coverage of scaffolded files" | None | **NEW (corrected per F1)**: `tests/test_registry_ast_coverage.py` — forward (template_path → exists) + reverse (template file → registered template_path) |
| "AST gate wired into groundtruth-kb CI" | `.github/workflows/ci.yml` `test-base` lane | **Wired** by virtue of being a pytest test under `tests/`; verified by T-CI meta-test |
| "Migration-note discipline (no owner-flip without note)" | None | **DEFERRED to Slice 2.5** (depends on schema extension) |
| "Registry-drift detection in CI" | None | **NEW**: `tests/test_registry_drift_detection.py` compares the live `OwnershipResolver.all_records()` ID set against a deterministic golden snapshot |
| "Tests, IPR, CVR" | KB API | Implemented per GOV-20 Phase 1 advisory pilot |

**Net Slice 2 scope:** AST gate (T1+T6) + drift detection (T4) + schema lock (T-SCHEMA) + CI meta-test (T-CI) + GOV-20 IPR/CVR. Rationale/migration-note discipline deferred to a follow-on slice.

### Replaces `-001` Implementation Plan §1 (AST gate, per F1 fix)

**File (new):** `groundtruth-kb/tests/test_registry_ast_coverage.py` (~150 LOC)

```python
# Files in templates/ that are NOT scaffolded into adopter projects (e.g.,
# documentation, README templates rendered by string substitution rather
# than file-copy). These are excluded from the reverse-coverage walk.
_NON_SCAFFOLDED_TEMPLATE_FILES: frozenset[str] = frozenset({
    "MEMORY.md",
    "README.md",
    "CLAUDE.md",
    "BRIDGE-INVENTORY.md",
    "bridge-os-poller-setup-prompt.md",
    "managed-artifacts.toml",
    "scaffold-ownership.toml",
})


def test_every_file_class_record_template_path_exists() -> None:
    """T1a (forward): every FILE-class registry record's template_path
    resolves to an existing file under templates/.

    Detects registry rows pointing at deleted/missing template files.
    Per Codex `-002` F1 fix: uses template_path (the source-tree key),
    not target_path (the scaffold-key).
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    templates_root = _templates_dir()
    resolver = OwnershipResolver()
    missing: list[str] = []

    for record in resolver.all_records():
        if record.source_class != "file" or record.source is None:
            continue
        template_path = getattr(record.source, "template_path", None)
        if not template_path:
            continue
        if not (templates_root / template_path).is_file():
            missing.append(f"{record.id}: {template_path}")

    assert not missing, (
        f"{len(missing)} FILE-class registry rows reference missing template "
        f"files. First 5: {missing[:5]}. Either restore the template file or "
        f"remove the registry row in templates/managed-artifacts.toml."
    )


def test_every_template_source_file_has_registry_coverage() -> None:
    """T1b (reverse): every file under templates/ is referenced by some
    FILE-class registry row's template_path (or is in the explicit
    non-scaffolded allowlist).

    Per Codex `-002` F1 fix: uses template_path enumeration, not
    classify_path() (which is keyed on target_path).
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    templates_root = _templates_dir()
    resolver = OwnershipResolver()
    registered_template_paths: set[str] = set()
    for record in resolver.all_records():
        if record.source_class != "file" or record.source is None:
            continue
        template_path = getattr(record.source, "template_path", None)
        if template_path:
            registered_template_paths.add(template_path)

    unregistered: list[str] = []
    for path in templates_root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(templates_root).as_posix()
        if rel in _NON_SCAFFOLDED_TEMPLATE_FILES or path.name in _NON_SCAFFOLDED_TEMPLATE_FILES:
            continue
        if rel not in registered_template_paths:
            unregistered.append(rel)

    assert not unregistered, (
        f"AST gate failure: {len(unregistered)} template-source files lack "
        f"registry coverage (no FILE-class record's template_path matches). "
        f"First 5: {unregistered[:5]}. Add a FILE-class record to "
        f"templates/managed-artifacts.toml, OR add to the explicit "
        f"_NON_SCAFFOLDED_TEMPLATE_FILES allowlist if the file is "
        f"intentionally template-only (documentation, README)."
    )
```

**Satisfies:** Phase 9 §"Regression Visibility" line 406 (AST gate; F1 fix uses correct surface).

### Replaces `-001` Implementation Plan §2-3 (deferred per F2 fix)

DEFERRED. T2 (rationale) and T3 (migration-note discipline) are removed from Slice 2 scope. They become a Slice 2.5 follow-on after the schema extension lands.

### Replaces `-001` Implementation Plan §4 (drift detection — minor edit)

**File (new):** `groundtruth-kb/tests/test_registry_drift_detection.py` (~80 LOC)
**Fixture (new):** `groundtruth-kb/tests/fixtures/registry-id-set.txt` — sorted list of all current record IDs.

```python
def test_registry_drift_against_id_snapshot() -> None:
    """T4: per Phase 9 §"Regression Visibility" line 407.

    Compares the live OwnershipResolver.all_records() ID set against a
    deterministic golden fixture. Mismatches fail with a list of added/
    removed IDs and a remediation message pointing to the snapshot
    regeneration recipe.
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    live_ids = sorted(r.id for r in resolver.all_records())
    snapshot_path = _fixtures_dir() / "registry-id-set.txt"
    expected_ids = sorted(
        line.strip()
        for line in snapshot_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    )

    added = sorted(set(live_ids) - set(expected_ids))
    removed = sorted(set(expected_ids) - set(live_ids))

    assert not added and not removed, (
        f"Registry drift detected:\n"
        f"  added ({len(added)}): {added[:5]}\n"
        f"  removed ({len(removed)}): {removed[:5]}\n"
        f"To intentionally accept this drift, regenerate the snapshot:\n"
        f"  python -c \"from groundtruth_kb.project.ownership import OwnershipResolver; "
        f"print('\\n'.join(sorted(r.id for r in OwnershipResolver().all_records())))\" "
        f"> tests/fixtures/registry-id-set.txt"
    )
```

**Satisfies:** Phase 9 §"Regression Visibility" line 407 ("Registry drift must be detectable").

### Replaces `-001` Specification-Derived Verification table (per F1+F2)

| # | Test | Derives from |
|---|---|---|
| **T1a** | `test_every_file_class_record_template_path_exists` | Phase 9 §"Regression Visibility" line 406 — forward existence (per F1 fix) |
| **T1b** | `test_every_template_source_file_has_registry_coverage` | Phase 9 §"Regression Visibility" line 406 — reverse coverage via template_path (per F1 fix) |
| **T4** | `test_registry_drift_against_id_snapshot` | Phase 9 §"Regression Visibility" line 407 (drift detection) |
| **T6** | `test_classify_path_round_trip_for_file_class_target_paths` | Sanity: `classify_path` works on target_path values (proves the resolver contract; per F1 fix to keep target-path classification scoped) |
| **T-SCHEMA** | `test_ownership_meta_existing_fields_satisfy_owner_and_upgrade_acceptance` | Documents that scoping `-003` line 83 acceptance ("`owner` and `upgrade_policy` fields") is satisfied by existing `OwnershipEnum.ownership` and `UpgradePolicyEnum.upgrade_policy` |
| **T-CI** | `test_registry_test_files_live_under_tests_directory` | scoping `-003` line 86 (CI wiring; meta-test asserting the new test files are pytest-collected) |
| **T-IPR-CVR** | `test_ipr_and_cvr_slice2_documents_exist_with_adr_tag` | GOV-20 Phase 1 advisory pilot |

Total tests: 7 (was 7 in -001; T2/T3 dropped, T1 split into T1a/T1b, T-SCHEMA added).

T2 (rationale discipline) and T3 (migration-note discipline) DEFERRED to follow-on Slice 2.5.

## Risk / Impact Delta

`-001` Risk/Impact carries forward except where deferred. Two updates:

**AST gate first-run failures (medium → medium-low after F1 narrowing):** running T1b against the live `templates/` tree may surface unregistered template-source files. Mitigation: implementation commit either adds the missing registry rows OR adds them to `_NON_SCAFFOLDED_TEMPLATE_FILES` allowlist with a comment explaining why.

**Snapshot fixture maintenance burden (medium → low after T2/T3 deferral):** only T4 maintains a fixture (registry-id-set.txt), and the regeneration recipe is one shell command in the assertion message itself.

## Acceptance Criteria

This proposal is GO-able when Codex confirms:

1. T1a uses `record.source.template_path` (not `classify_path`) for forward existence.
2. T1b uses the set of `template_path` values from FILE-class records (not `classify_path`) for reverse coverage; allowlist for non-scaffolded template files is explicit and documented.
3. T6 (sanity) is the only test that calls `classify_path`, scoped to `target_path` values.
4. T2 (rationale) and T3 (migration-note) are explicitly deferred to a follow-on slice; deferral is recorded as a work_list row after Slice 2 VERIFIED.
5. T4 drift detection uses an ID-set snapshot; regeneration recipe is in the assertion message.
6. T-SCHEMA documents that scoping line 83 acceptance is met by existing fields.
7. T-CI confirms test placement covers the CI-wiring acceptance.
8. IPR/CVR creation steps in scope.
9. Specification Links covers all governing artifacts.
10. Scope of the proposal commit matches what will land (proposal + INDEX only).

## Decision Needed From Owner

**Nothing required at GO time.** Both F1 and F2 fixes are mechanical; Codex `-002` explicitly stated no owner decision needed for either.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
