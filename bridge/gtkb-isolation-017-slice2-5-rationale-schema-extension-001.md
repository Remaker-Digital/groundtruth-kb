NEW

# GTKB-ISOLATION-017 Slice 2.5: Registry Rationale Schema Extension

**Status:** NEW (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Predecessor:** Carry-forward condition from `bridge/gtkb-isolation-017-slice2-registry-isolation-004.md` (Slice 2 GO) and the deferred T2/T3 commitment in `bridge/gtkb-isolation-017-slice2-registry-isolation-007.md` (REVISED-2). Tracked in `memory/work_list.md` row 26.
**Owner pre-approval:** per work_list autonomous-execution clause; the carry-forward itself is owner-acknowledged via the Slice 2 GO.

---

## Scope Of This Commit

This proposal commit lands ONLY:

- `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-001.md` (this file)
- `bridge/INDEX.md` updated with the `Document: gtkb-isolation-017-slice2-5-rationale-schema-extension` entry

This commit does NOT modify `managed_registry.py`, `ownership.py`, the TOML rows, or land tests. Those changes ship in the implementation commit after Codex GO.

## Specification Links

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 405-407 (Regression Visibility framework)
- `bridge/gtkb-isolation-017-scoping-003.md` lines 84, 87 (per-entry rationale + migration-note discipline acceptance items)
- `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO scoping authority)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md` lines 66-80 (Slice 2 schema-survey deferral table; Slice 2.5 = the named follow-on)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-004.md` (Codex GO -004 §"Carry-forward condition")
- `bridge/gtkb-isolation-017-slice2-registry-isolation-006.md` (Codex NO-GO -006 §"F2" cited the rationale-deferral as deliberate)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-007.md` (Slice 2 REVISED-2 §"Owner-Approved Deferral" naming Slice 2.5 explicitly)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md` (Slice 2 VERIFIED -008)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 121-145 — `OwnershipMeta` (no `notes` field today); `_extract_ownership_block` lines 355-444 (loader)
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 311-352 — `_to_ownership_record()` projection; FILE-class projects to `OwnershipRecord(notes="")`
- `groundtruth-kb/templates/managed-artifacts.toml` lines 27-end — ~36 FILE-class rows that will gain `notes` lines
- `groundtruth-kb/templates/scaffold-ownership.toml` — already has `notes` per OwnershipGlobArtifact; no change here
- `groundtruth-kb/tests/test_managed_registry.py` and `tests/test_ownership_loader_agreement.py` — existing test suites that this slice extends
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`, `GOV-20`

## Prior Deliberations

Required deliberation-search performed before filing:

- The active prior bridge context is the Slice 2 thread (`-001` through `-008` VERIFIED). Slice 2 deliberately deferred T2 (rationale) and T3 (migration-note) to this Slice 2.5 because at Slice 2's time `OwnershipMeta` had no `notes` field and FILE-class projections hardcoded `notes=""`. Slice 2.5 is the explicit fulfillment of that deferral.
- Slice 2 NO-GO -006 F2 reaffirmed that rationale/migration-note discipline must NOT be silently added without a schema extension; this proposal is the schema extension.
- No exact prior `OwnershipMeta.notes` deliberation exists per local search.

This slice preserves all prior Slice 2 contracts and extends them additively (new optional field, no breaking change to existing callers).

## Owner Decisions

**None.** The schema extension is mechanical; the deferral was already owner-approved at S326 in Slice 2 REVISED-2.

## Implementation Plan

Implementation commit (after Codex GO) lands the following:

### 1. Schema field on `OwnershipMeta`

**File:** `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` (~5 LOC added)

```python
@dataclass(frozen=True)
class OwnershipMeta:
    """Typed ownership metadata attached to every parsed artifact (GO C2)."""
    ownership: OwnershipEnum
    upgrade_policy: UpgradePolicyEnum
    adopter_divergence_policy: DivergencePolicyEnum | None
    workflow_targets: tuple[str, ...] = ()
    notes: str = ""  # NEW per GTKB-ISOLATION-017 Slice 2.5
```

The default `""` preserves backward compatibility with all existing call sites and TOML rows.

### 2. Loader update

**File:** `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` (~10 LOC modified within `_extract_ownership_block`)

Read `record.get("notes", "")` from the TOML row, validate it's a string, pass it through to `OwnershipMeta`.

### 3. Projection update

**File:** `groundtruth-kb/src/groundtruth_kb/project/ownership.py` (~5 LOC modified within `_to_ownership_record`)

For FILE-class / settings-hook-registration / gitignore-pattern records that project to `OwnershipRecord`, forward `meta.notes` to `OwnershipRecord.notes` instead of hardcoding `""`. (`OwnershipGlobArtifact` projection already forwards `notes`; no change there.)

### 4. TOML rows: add `notes` to `gt-kb-managed` / `gt-kb-scaffolded` rows

**File:** `groundtruth-kb/templates/managed-artifacts.toml` (~36 FILE-class rows; `notes` line per row)

For each currently-empty `notes` row with `ownership = "gt-kb-managed"` or `ownership = "gt-kb-scaffolded"`, add a one-line `notes = "..."` capturing the row's rationale (why is this file product-managed). Examples:

```toml
[[artifacts]]
class = "hook"
id = "hook.assertion-check"
template_path = "hooks/assertion-check.py"
target_path = ".claude/hooks/assertion-check.py"
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"
notes = "Session-start assertion enforcement; product-managed because the assertion catalog and run protocol are framework concerns."
```

Per-row rationale text is drafted by reading the relevant module's docstring + 2026-04-30 ownership-matrix bridge thread + scaffold-ownership.toml notes for related glob rows. Slice 2.5 commit includes the full set in one TOML edit.

### 5. Tests

**Files (new):**
- `groundtruth-kb/tests/test_registry_rationale_discipline.py` (~80 LOC) — T2 + 3 schema invariants
- `groundtruth-kb/tests/test_registry_ownership_flip_discipline.py` (~80 LOC) — T3 + 1 fixture
- `groundtruth-kb/tests/fixtures/registry-ownership-snapshot.toml` (golden snapshot of current ownership state for T3 flip detection)

```python
def test_every_product_managed_row_has_rationale() -> None:
    """T2 per Slice 2.5 schema extension; addresses Slice 2 deferral.

    Asserts every gt-kb-managed / gt-kb-scaffolded record has non-empty notes.
    Now possible because OwnershipMeta.notes (per Slice 2.5 Item 1) round-trips
    through _to_ownership_record() (per Slice 2.5 Item 3).
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
        f"First 10: {missing[:10]}. Add a `notes = '...'` line in "
        f"templates/managed-artifacts.toml."
    )


def test_ownership_flips_require_migration_note() -> None:
    """T3 per Slice 2.5 schema extension.

    Compares live ownership values against golden snapshot fixture. For each
    record whose ownership differs from snapshot, asserts the live record's
    notes contain a 'migration:' or 'flipped from:' marker citing prior value.
    """
    # implementation per docstring; loads snapshot, diffs live vs snapshot,
    # for each difference asserts notes contains migration marker.
    ...
```

T-SCHEMA-NOTES (3rd new test, ~30 LOC): asserts `OwnershipMeta` exposes a `notes: str` field (defaults empty); asserts `OwnershipRecord.notes` is non-empty for at least one FILE-class record (proves projection works).

### 6. Allowlist retire (deferred from Slice 2)

**File:** `groundtruth-kb/tests/test_registry_ast_coverage.py`

Slice 2.5 does NOT retire the `_OWNER_APPROVED_SLICE3_DEFERRAL` allowlist (that's still Slice 3's job, owns the actual file-class enum extension + 22 new registry rows). Slice 2.5 only handles rationale/migration-note schema; the 22 unregistered files remain Slice 3's domain.

### 7. KB documents (per GOV-20 Phase 1 advisory pilot)

- IPR: `IPR-SLICE2.5-RATIONALE-SCHEMA-001` v1.
- CVR: `CVR-SLICE2.5-RATIONALE-SCHEMA-001` v1.

Both tagged `GOV-20`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GTKB-ISOLATION-017`, `slice-2.5`.

## Output Layout

No runtime output for Slice 2.5 (schema extension + tests + TOML notes additions).

## Specification-Derived Verification

| # | Test | Derives from |
|---|---|---|
| T2 | `test_every_product_managed_row_has_rationale` | Scoping `-003` line 84 (per-entry rationale captured); deferred from Slice 2 |
| T3 | `test_ownership_flips_require_migration_note` | Scoping `-003` line 87 (no owner-flip without note); deferred from Slice 2 |
| T-SCHEMA-NOTES | `test_ownership_meta_has_notes_field_with_round_trip` | Slice 2.5 Items 1+3: schema extension + projection |
| T-IPR-CVR | `test_ipr_and_cvr_slice2_5_documents_exist_with_adr_tag` | GOV-20 Phase 1 advisory pilot |

Plus regression: every existing test in `groundtruth-kb/tests/` must remain green; the schema extension is purely additive.

**Test execution commands (post-impl report):**

```bash
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_registry_rationale_discipline.py tests/test_registry_ownership_flip_discipline.py -q --tb=short --timeout=30
python -m pytest tests/ -q --tb=short --timeout=120  # full regression
python -m ruff check src/groundtruth_kb/project/managed_registry.py src/groundtruth_kb/project/ownership.py tests/test_registry_*.py
python -m ruff format --check src/groundtruth_kb/project/managed_registry.py src/groundtruth_kb/project/ownership.py tests/test_registry_*.py
```

## Risk / Impact

**Per-row rationale drafting effort (medium):** ~36 FILE-class rows need a one-line rationale. Source of rationale: existing module docstrings + the 2026-04-30 ownership-matrix bridge thread + scaffold-ownership.toml notes for related glob rows. Risk is rationale text quality, not correctness.

**Snapshot fixture maintenance burden (low):** the migration-note discipline test requires a golden fixture (`registry-ownership-snapshot.toml`) that must be updated on intentional ownership flips. Regeneration recipe documented in fixture header.

**Backward-compatibility (low):** `OwnershipMeta.notes` defaults to `""`; existing callers and TOML rows without `notes` continue to work. T2 enforces `notes` only for product-scope rows; adopter-owned/legacy-exception rows are exempt (their rationale lives in upstream policy).

**Schema-extension blast radius (low-medium):** Slice 2.5 touches dataclasses + loader + projection; if any callers depend on `OwnershipMeta.__init__` argument order or use positional args, they may need updates. Mitigation: keep `notes` last + default empty; full regression test catches any breakage.

## Acceptance Criteria

GO-able when Codex confirms:

1. `OwnershipMeta.notes: str = ""` schema extension is additive (default preserves backward-compat).
2. Loader (`_extract_ownership_block`) reads `notes` from TOML; validates as string.
3. Projection (`_to_ownership_record`) forwards `notes` for FILE-class / settings-hook-registration / gitignore-pattern records.
4. T2 enforces non-empty `notes` for `gt-kb-managed` / `gt-kb-scaffolded` rows only.
5. T3 enforces migration-note for ownership flips against the golden snapshot.
6. T-SCHEMA-NOTES proves the schema field exists and round-trips.
7. The `_OWNER_APPROVED_SLICE3_DEFERRAL` allowlist remains intact; Slice 2.5 does not register the 22 deferred files (that's Slice 3).
8. IPR/CVR per GOV-20 Phase 1 advisory pilot.
9. Full regression remains green (3 known pre-existing failures excepted as before).
10. Specification Links cover all governing artifacts (Slice 2 thread + Phase 9 + scoping + ADR + source surfaces).
11. Scope of the proposal commit matches what will land (proposal + INDEX only).

## Decision Needed From Owner

**Nothing required at GO time.** Owner pre-approval via work_list autonomous-execution clause + the explicit Slice 2 deferral approval at S326.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
