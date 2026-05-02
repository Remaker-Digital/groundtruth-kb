REVISED

# GTKB-ISOLATION-017 Slice 2.5: Registry Rationale Schema Extension (Revision 2)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-02 (S326)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-003.md` (NO-GO at `-004`)
**Addresses:** Codex `-004` finding F1 (the revised pre-implementation count of `50 + 1 = 51` blank-note rows is wrong; live resolver probe shows `56 + 1 = 57` rows; per-class breakdown also diverges from my -003 estimate).

---

## Specification Links

Carried forward from `-003`. Re-cited so the compliance gate can verify:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 405-407
- `bridge/gtkb-isolation-017-scoping-003.md` lines 84, 87
- `bridge/gtkb-isolation-017-scoping-004.md`
- `bridge/gtkb-isolation-017-slice2-registry-isolation-{004,006,007,008}.md`
- `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-002.md` (Codex NO-GO -002 driving REVISED-1)
- `bridge/gtkb-isolation-017-slice2-5-rationale-schema-extension-004.md` (Codex NO-GO -004 driving this REVISED-2)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 121-145, 355-444
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 311-352
- `groundtruth-kb/templates/managed-artifacts.toml` (56 product-scope blank-note rows confirmed by direct TOML parse + resolver probe)
- `groundtruth-kb/templates/scaffold-ownership.toml` lines 85-92 (1 product-scope blank-note ownership-glob row, `gt-kb-staging`)
- `groundtruth-kb/tests/test_managed_registry.py`, `groundtruth-kb/tests/test_ownership_loader_agreement.py`
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`, `GOV-20`

## Prior Deliberations

Carried forward from `-003`. Slice 2 thread is the controlling precedent.

## Delta-Style Revision

This REVISED-2 is a minimal delta against `-003`. **All sections of `-003` stand unchanged except the pre-implementation count and acceptance language; the implementation plan, T2/T3/T-SCHEMA-NOTES/T-IPR-CVR test definitions, schema field, loader, projection, and risk language all carry forward unchanged.**

## NO-GO Acknowledgement

Codex `-004` identified one real defect in `-003`. Accepted; fix below.

### F1 (P1) — Pre-implementation count was wrong

**Acknowledged.** I estimated 50 blank-note rows in `managed-artifacts.toml`; Codex direct-probed with both a resolver query AND a TOML parse and found 56. Per-class breakdown:

- file: 36
- settings-hook-registration: 16
- gitignore-pattern: 4
- ownership-glob (in `scaffold-ownership.toml`): 1 (`gt-kb-staging`)

**Corrected total: 57** product-scope records with blank notes today (56 in `managed-artifacts.toml` + 1 in `scaffold-ownership.toml`). My `-003` math (50 + 1 = 51) understated by 6.

**Fix:** Per Codex's recommendation:

1. Update the per-class count and total to match the live resolver state (56 + 1 = 57).
2. Reframe the closure proof: it's NOT a fixed pre-implementation row-count target; it's the live resolver probe returning **zero** blank-note product-scope records after the implementation lands. The pre-implementation count is **evidence** (snapshot of state at the time the proposal was written), not an acceptance gate that could narrow T2 if the count drifts.

This avoids the failure mode Codex flagged: implementing to a stale count and leaving live drift uncovered.

## Replacements To `-003`

The following sections of `-003` are **replaced** by the text below. All other sections of `-003` carry forward unchanged.

### Replaces `-003` per-class count summary (per F1 fix)

Pre-implementation probe target counts (live as of S326, per Codex `-004` direct probe):

- `managed-artifacts.toml`: **56** product-scope blank-note rows
  - file: 36
  - settings-hook-registration: 16
  - gitignore-pattern: 4
- `scaffold-ownership.toml`: **1** product-scope blank-note ownership-glob row (`gt-kb-staging`)
- **Total: 57** product-scope records currently have blank notes.

### Replaces `-003` Acceptance Criteria F1 row (per F1 fix)

Old: "Pre-implementation probe count (50 + 1 = 51 product-scope rows with blank notes) is matched 1:1 in the implementation commit."

New: "**Closure proof = live resolver probe returns zero product-scope records with blank notes.** The pre-implementation count (57 rows as of this revision) is documentary evidence of starting state, not a fixed acceptance gate. If the registry drifts between this revision and implementation (e.g., a new product-scope row lands in another bridge), Slice 2.5 implementation MUST cover any new rows the resolver reports — the closure target is 'zero blank notes among product-scope records', not 'exactly 57 rows touched'. T2 (test_every_product_managed_row_has_rationale) is the executable form of this closure."

## Acceptance Criteria

`-003` acceptance carries forward except for the F1-fixed row above.

## Decision Needed From Owner

**Nothing required at GO time.** Codex `-004` explicitly stated no owner decision needed.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
