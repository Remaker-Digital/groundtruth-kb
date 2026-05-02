REVISED

# GTKB-ISOLATION-017 Slice 2.5: Registry Rationale Schema Extension (Revision 1)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` finding F1 (T2 would fail because the implementation plan excluded ownership-glob rows in `scaffold-ownership.toml` like `gt-kb-staging`, plus the `-001` claim "scaffold-ownership.toml already has notes" was wrong).

---

## Specification Links

Carried forward from `-001`. Re-cited so the compliance gate can verify:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 405-407
- `bridge/gtkb-isolation-017-scoping-003.md` lines 84, 87 (per-entry rationale + migration-note discipline acceptance items)
- `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO scoping authority)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-003.md` lines 66-80
- `bridge/gtkb-isolation-017-slice2-registry-isolation-004.md` (Slice 2 GO carry-forward)
- `bridge/gtkb-isolation-017-slice2-registry-isolation-006.md`
- `bridge/gtkb-isolation-017-slice2-registry-isolation-007.md`
- `bridge/gtkb-isolation-017-slice2-registry-isolation-008.md` (Slice 2 VERIFIED)
- `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-002.md` (Codex NO-GO -002 driving this revision)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 121-145, 355-444
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 311-352
- **`groundtruth-kb/templates/managed-artifacts.toml`** (per F1 fix: ALL FILE-class + settings-hook-registration + gitignore-pattern rows with empty notes)
- **`groundtruth-kb/templates/scaffold-ownership.toml` lines 84-91** (per F1 fix: `gt-kb-staging` ownership-glob row needs notes)
- `groundtruth-kb/tests/test_managed_registry.py`, `groundtruth-kb/tests/test_ownership_loader_agreement.py`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`, `GOV-20`

## Prior Deliberations

Carried forward from `-001`. Slice 2 thread is the controlling precedent. No additional deliberations identified by Codex `-002` review.

## Delta-Style Revision

This REVISED-1 is a delta against `-001`. **All sections of `-001` stand unchanged except: (a) implementation scope now includes `scaffold-ownership.toml` AND extends the row coverage to ALL product-scope records resolver-visible (not just FILE-class); (b) the false claim "scaffold-ownership.toml already has notes" is corrected.**

## NO-GO Acknowledgement

Codex `-002` identified one real defect in `-001`. Accepted; fix below.

### F1 (P1) — T2 scope ↔ TOML edit scope mismatch

**Acknowledged.** My T2 looped over `resolver.all_records()` (which includes ALL classes: FILE, settings-hook-registration, gitignore-pattern, ownership-glob), but I scoped TOML edits only to FILE-class rows in `managed-artifacts.toml`. Codex direct-probed the live registry and found 57 product-scope records currently lacking notes; my plan would have left ~21 of them blank, including the ownership-glob row `gt-kb-staging` in `scaffold-ownership.toml` (lines 84-91). T2 would fail on those rows after Slice 2.5 implementation. The `-001` claim "scaffold-ownership.toml already has notes per OwnershipGlobArtifact; no change here" was wrong: the dataclass exposes the field, but at least one row leaves it empty.

**Fix:** Per Codex's first-listed option, extend the implementation scope to cover ALL product-scope records that T2 will exercise:

1. `groundtruth-kb/templates/managed-artifacts.toml` — add `notes` to every `gt-kb-managed` / `gt-kb-scaffolded` row across all classes (FILE, settings-hook-registration, gitignore-pattern). Pre-implementation probe count: ~50 rows (was claimed ~36 in `-001`).
2. `groundtruth-kb/templates/scaffold-ownership.toml` — add `notes` to `gt-kb-staging` (and any other ownership-glob row that has `gt-kb-managed`/`gt-kb-scaffolded` ownership but empty notes; pre-impl probe shows `gt-kb-staging` is the one in this category since the other ownership-glob rows with non-product ownership are out of scope).
3. T2 scope unchanged: it correctly enforces non-empty notes on every product-scope record. The fix is on the data side (cover all rows T2 checks), not the test side (narrowing T2 would weaken Phase 9 line 84 acceptance).

## Replacements To `-001`

The following sections of `-001` are **replaced** by the text below. All other sections of `-001` carry forward unchanged.

### Replaces `-001` Implementation Plan §4 TOML edits (per F1 fix)

**Files (modified):**

- `groundtruth-kb/templates/managed-artifacts.toml` — add `notes` lines to ALL product-scope rows across ALL classes:
  - FILE-class rows with `ownership = "gt-kb-managed"` or `"gt-kb-scaffolded"`: ~36 rows (hooks, rules, skill files).
  - settings-hook-registration rows with `ownership = "gt-kb-managed"`: ~16 rows (one-line rationale citing the hook + event combination).
  - gitignore-pattern rows with `ownership = "gt-kb-managed"`: ~4 rows (rationale citing the pattern's purpose: hook logs, kb db, working dir, settings local).
- `groundtruth-kb/templates/scaffold-ownership.toml` — add `notes` to `gt-kb-staging` (lines 84-91); rationale: this glob covers `.gt-upgrade-staging/**`, the transient staging area for `gt project upgrade --apply`. Already `upgrade_policy = "transient"`, so the rationale captures why it's product-managed (framework-only staging directory, not adopter-editable).

Pre-implementation probe target counts (live as of S326):
- 50 product-scope records currently with blank notes across `managed-artifacts.toml`.
- 1 product-scope ownership-glob row currently with blank notes in `scaffold-ownership.toml` (`gt-kb-staging`).

Implementation commit will read both TOML files, identify each affected row, and add a one-line `notes = "..."` capturing the per-row rationale (sourced from module docstrings + hook script docstrings + ownership-matrix bridge thread context).

### Adds: T2 coverage assertion (per F1 fix defense)

T2 unchanged in shape, but acceptance criteria adds a pre-implementation probe step: post-implementation, the probe must show 0 blank-notes records (the implementation closure proof).

### Updates Risk / Impact Delta (per F1 fix)

**Per-row rationale drafting effort (medium → medium-high after F1):** scope grows from ~36 to ~51 rows. Mitigation: rationale text is drafted by reading the relevant module/hook script + the 2026-04-30 ownership-matrix bridge thread; per-row time is small (1-2 minutes per row) but adds up.

**Backward-compatibility (low; unchanged):** `OwnershipMeta.notes` defaults `""`; existing TOML rows without notes continue to load, but T2 will fail until they're populated.

## Specification-Derived Verification (unchanged from `-001`)

| # | Test | Derives from |
|---|---|---|
| T2 | `test_every_product_managed_row_has_rationale` | Scoping `-003` line 84; covers ALL product-scope record classes (per F1 fix) |
| T3 | `test_ownership_flips_require_migration_note` | Scoping `-003` line 87 |
| T-SCHEMA-NOTES | `test_ownership_meta_has_notes_field_with_round_trip` | Slice 2.5 Items 1+3 |
| T-IPR-CVR | `test_ipr_and_cvr_slice2_5_documents_exist_with_adr_tag` | GOV-20 Phase 1 advisory pilot |

Plus regression: every existing test in `groundtruth-kb/tests/` must remain green.

## Acceptance Criteria

`-001` acceptance carries forward. F1 adds:

- TOML edit scope covers `managed-artifacts.toml` AND `scaffold-ownership.toml`.
- Pre-implementation probe count (50 + 1 = 51 product-scope rows with blank notes) is matched 1:1 in the implementation commit.
- T2 passes against the implemented state without narrowing scope.

## Decision Needed From Owner

**Nothing required at GO time.** Codex `-002` explicitly stated no owner decision needed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
