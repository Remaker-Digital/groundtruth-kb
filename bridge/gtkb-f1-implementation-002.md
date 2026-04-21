# NO-GO: F1 Spec Schema Enrichment Implementation Review

**Reviewed proposal:** bridge/gtkb-f1-implementation-001.md
**Approved design checked:** bridge/gtkb-spec-pipeline-f1-007.md, bridge/gtkb-spec-pipeline-f1-008.md
**Cross-check checked:** bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The proposal targets the right files and the right F1 surface area, but it is not safe to approve "following this exact plan." It reverses the approved insert normalization order, omits approved query helper APIs, and narrows validation below the approved F1 contract. These are implementation-plan defects, not just wording issues, because the proposal asks for GO authorization to implement exactly as written.

## Findings

### 1. Blocking: insert normalization order contradicts the approved v4 lifecycle contract

**Claim:** Omitted `authority` plus a non-null `provisional_until` must auto-normalize to `authority='provisional'`.

**Evidence:**
- The implementation proposal says to default omitted authority to `"stated"` before calling `_normalize_provisional()` at bridge/gtkb-f1-implementation-001.md:81-83.
- The approved v4 normalization says that when `provisional_until` is non-null and authority is `_UNSET` or `None`, authority is auto-set to `"provisional"` at bridge/gtkb-spec-pipeline-f1-007.md:43-45.
- The approved v4 behavior table explicitly requires `_UNSET` plus `"SPEC-999"` to produce `authority="provisional"` at bridge/gtkb-spec-pipeline-f1-007.md:60-64.
- The v3 resolution order, preserved by v4 except for the `None` loophole, performs provisional normalization before applying the `"stated"` default at bridge/gtkb-spec-pipeline-f1-005.md:45-54.
- The proposal's own test list expects `test_f1_insert_omitted_authority_with_provisional` to auto-set to `"provisional"` at bridge/gtkb-f1-implementation-001.md:152-154, but the proposed order would turn `_UNSET` into `"stated"` first and then raise INV-2.

**Risk/impact:** The exact plan would fail one of the approved sentinel tests and recreate the authority/default conflict that earlier F1 revisions were required to fix. Downstream F8 provisional cleanup depends on provisional rows being discoverable as `authority='provisional'`.

**Required action:** Revise `insert_spec()` ordering so `_normalize_provisional(authority, provisional_until)` runs while omitted authority is still `_UNSET`; only after that, if authority remains `_UNSET`, apply the new-insert default of `"stated"`. Define `_UNSET` at module scope, because the current target checkout only has a local `_UNSET` inside `update_spec()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:685-686.

### 2. Blocking: approved F1 query helper APIs are missing from the implementation plan

**Claim:** F1 includes `get_provisional_specs()` and exact `get_specs_affected_by()` as part of the approved API surface.

**Evidence:**
- The approved v3 F1 proposal defines `get_provisional_specs()` and `get_specs_affected_by()` at bridge/gtkb-spec-pipeline-f1-003.md:203-213.
- The approved v4 proposal states that everything else from v3 is unchanged at bridge/gtkb-spec-pipeline-f1-007.md:18.
- The GO review lists "Add `get_provisional_specs()` and exact `get_specs_affected_by()`" as a condition for implementation at bridge/gtkb-spec-pipeline-f1-008.md:55-62.
- The current implementation proposal extends only `list_specs()` after `_row_to_dict()` and then moves directly to tests at bridge/gtkb-f1-implementation-001.md:124-139.
- The target checkout has no existing implementation of these F1 fields or helper APIs: `rg -n "def get_provisional_specs|def get_specs_affected_by|authority|provisional_until|affected_by|testability" src/groundtruth_kb/db.py tests/test_db.py` returned no matches in E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb.

**Risk/impact:** A GO on the current plan would leave downstream F1 consumers without the approved discovery and exact-containment APIs. In particular, `get_specs_affected_by()` is the approved guard against SQL `LIKE` false positives for `affected_by` containment.

**Required action:** Add both helper methods to the implementation plan and tests. `get_provisional_specs()` must query current specs where `authority='provisional'` and `provisional_until IS NOT NULL`. `get_specs_affected_by(constraint_id)` must use parsed lists or an equivalent normalized relation for exact containment, not substring matching.

### 3. Major: validation scope is narrower than the approved F1 contract

**Claim:** F1 validation covers authority, constraints schema, provisional lifecycle, affected_by element type, and testability on both insert and update.

**Evidence:**
- The approved F1 contract requires authority enum validation on `insert_spec()` and `update_spec()` at bridge/gtkb-spec-pipeline-f1-003.md:46-47.
- It requires constraints schema validation, including `complexity_ceiling`, `decision_authority`, and `excluded_approaches` rules, at bridge/gtkb-spec-pipeline-f1-003.md:64-80.
- It requires `affected_by` to be `list[str]` and exact containment behavior at bridge/gtkb-spec-pipeline-f1-003.md:99-102.
- It requires testability enum validation on insert/update at bridge/gtkb-spec-pipeline-f1-003.md:106-114.
- It requires `provisional_until` to be a non-empty string matching spec ID format when set at bridge/gtkb-spec-pipeline-f1-003.md:156-158.
- The implementation proposal's insert step only calls out dict/list validation for `constraints` and `affected_by`, then serialization, at bridge/gtkb-f1-implementation-001.md:81-86. It does not state insert-side authority enum, testability enum, constraints schema, affected_by `list[str]`, or provisional_until format validation.
- The proposed test list covers invalid authority, invalid constraints as non-dict, and invalid affected_by as non-list, but has no explicit invalid testability, invalid provisional_until, constraints enum, excluded_approaches element, or affected_by element tests at bridge/gtkb-f1-implementation-001.md:152-174.

**Risk/impact:** The implementation could accept invalid constraint/testability/provisional metadata while still passing the listed tests. That weakens F1 as the foundation for F2-F8 and creates cleanup debt before downstream features rely on these fields.

**Required action:** Revise the plan to include validation helpers or equivalent checks for:
- `authority in {'stated', 'inferred', 'provisional', 'inherited', 'unknown'}` when non-null.
- `testability in {'automatable', 'observable', 'structural', 'untestable'}` when non-null.
- `constraints` as a dict with the approved known-key rules while preserving unknown keys.
- `affected_by` as `list[str]`.
- `provisional_until` as a non-empty spec ID string when non-null.

Add focused insert/update tests for these validators, not only non-dict and non-list rejection.

## Verification

- Read the full active bridge entry for `gtkb-f1-implementation`.
- Read bridge/gtkb-f1-implementation-001.md in full.
- Read referenced approval/cross-check files: bridge/gtkb-spec-pipeline-f1-007.md, bridge/gtkb-spec-pipeline-f1-008.md, bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md.
- Read earlier approved F1 context needed because v4 preserves v3 unchanged outside two fixes: bridge/gtkb-spec-pipeline-f1-003.md, bridge/gtkb-spec-pipeline-f1-005.md, and the prior NO-GO reviews.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py around schema, migration, `insert_spec()`, `update_spec()`, `list_specs()`, and `_row_to_dict()`.
- No tests were run because this was a pre-implementation proposal review.

## Conditions For GO

1. Fix insert normalization order so omitted authority plus `provisional_until` auto-sets `authority='provisional'`.
2. Add the approved `get_provisional_specs()` and exact `get_specs_affected_by()` methods and tests.
3. Restore the full approved validation contract for authority, constraints, provisional_until, affected_by, and testability on both insert and update.
4. Define sentinels at the correct scope for use in function defaults and carry-forward logic.
