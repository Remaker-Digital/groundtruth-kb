# GO: F1 Spec Schema Enrichment Revised v3 Implementation Review

**Reviewed proposal:** bridge/gtkb-f1-implementation-005.md
**Prior reviews:** bridge/gtkb-f1-implementation-002.md, bridge/gtkb-f1-implementation-004.md
**Approved design checked:** bridge/gtkb-spec-pipeline-f1-003.md, bridge/gtkb-spec-pipeline-f1-007.md, bridge/gtkb-spec-pipeline-f1-008.md
**Cross-check checked:** bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** GO

## Rationale

The -005 revision resolves the two blocking defects from -004. It now specifies
the approved known-key constraints validator and clarifies that omitted F1 JSON
fields on update carry forward the existing raw storage string rather than
validating or serializing the raw value again.

This is sufficient to authorize F1 implementation. The GO is conditional on
preserving the exact raw-key carry-forward rule and adding the small validator
test coverage called out below.

## Findings

### 1. Blocking finding from -004 resolved: constraints known-key validation is now specified

**Claim:** F1 constraints validation must validate approved known keys while
preserving unknown keys.

**Evidence:**
- The approved F1 v3 contract requires `complexity_ceiling` values to be one
  of `simple`, `moderate`, `complex`; `decision_authority` values to be one of
  `owner`, `ai`, `either`; `excluded_approaches` to be `list[str]`; and unknown
  keys to be preserved at bridge/gtkb-spec-pipeline-f1-003.md:74.
- The prior NO-GO repeated that exact requirement at
  bridge/gtkb-f1-implementation-004.md:56-61.
- The -005 revision defines `_VALID_COMPLEXITY_CEILINGS` and
  `_VALID_DECISION_AUTHORITIES` at bridge/gtkb-f1-implementation-005.md:14-15.
- `_validate_constraints()` now rejects invalid `complexity_ceiling` values at
  bridge/gtkb-f1-implementation-005.md:32-37, invalid `decision_authority`
  values at bridge/gtkb-f1-implementation-005.md:39-44, and non-string
  `excluded_approaches` elements at bridge/gtkb-f1-implementation-005.md:46-58.
- Unknown keys are explicitly preserved without rejection at
  bridge/gtkb-f1-implementation-005.md:25.

**Risk/impact:** Low after revision. This restores the owner-decision boundary
needed before F3 and F5 consume `constraints`; the F1-F8 matrix identifies
`constraints` as an F1 field read by F3 and F5 at
bridge/gtkb-f1f8-cross-check-001.md:23.

**Required action:** Implement the validator as specified. Treat
`excluded_approaches` as a real `list[str]` field; do not silently accept other
container types.

### 2. Blocking finding from -004 resolved: update JSON carry-forward is now implementable

**Claim:** `update_spec()` must preserve omitted `constraints` and `affected_by`
without double-encoding JSON or validating raw storage strings as Python inputs.

**Evidence:**
- The current target checkout carries omitted JSON fields forward as raw storage
  strings for `tags` and `assertions` at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:696-707.
- The current `_row_to_dict()` starts from `d = dict(row)`, then only adds
  parsed companion keys; it does not overwrite the original raw JSON field at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3732-3763.
- The -005 revision states the update rule: provided JSON fields are validated
  as Python input and serialized once; omitted JSON fields carry forward the
  raw storage string at bridge/gtkb-f1-implementation-005.md:69-92.
- The chosen implementation approach uses `prev["constraints"]` /
  `prev.get("constraints")` as the raw value from `_row_to_dict()` and passes it
  directly to INSERT without re-serialization at
  bridge/gtkb-f1-implementation-005.md:108-122.
- The proposal adds roundtrip carry-forward tests for both JSON fields at
  bridge/gtkb-f1-implementation-005.md:124-137 and includes them in the revised
  test plan at bridge/gtkb-f1-implementation-005.md:154-155.

**Risk/impact:** Low if the implementation follows the chosen approach. The
only residual risk is copying the earlier illustrative placeholder keys
`_constraints_raw` / `_affected_by_raw`; those keys do not exist in the current
row conversion output.

**Required action:** In implementation, carry omitted values forward from
`prev.get("constraints")` and `prev.get("affected_by")`, not from
`_constraints_raw` or `_affected_by_raw`.

### 3. Confirmed: the proposal preserves the previously accepted F1 surface

**Claim:** The -005 revision keeps the earlier fixes needed for F1
implementation.

**Evidence:**
- The -005 proposal explicitly preserves the -003 fixes for normalization
  order, helper APIs, sentinels, and enum validation at
  bridge/gtkb-f1-implementation-005.md:7.
- The -003 revision fixed insert ordering so `_normalize_provisional()` runs
  before the omitted-authority default at bridge/gtkb-f1-implementation-003.md:14-37,
  matching the v4 behavior table at bridge/gtkb-spec-pipeline-f1-007.md:58-69.
- The -003 revision restored `get_provisional_specs()` and exact
  `get_specs_affected_by()` at bridge/gtkb-f1-implementation-003.md:44-61,
  matching the approved new-method scope at bridge/gtkb-spec-pipeline-f1-003.md:203.
- The approved GO review for F1 requires adding the five nullable columns,
  validation/serialization, `_row_to_dict()` parsing, `list_specs()` filters,
  and the two helper methods at bridge/gtkb-spec-pipeline-f1-008.md:55-62.
- The current groundtruth-kb checkout remains pre-F1 for this surface:
  `rg -n "def get_provisional_specs|def get_specs_affected_by|authority|constraints|affected_by|testability" src/groundtruth_kb/db.py tests/test_db.py`
  found no F1 schema/API implementation matches beyond unrelated DCL text.

**Risk/impact:** Implementation drift is now the main risk. Downstream F2-B,
F3, F4-B, F5, F7, and F8 depend on these F1 field names and parsed companions,
as shown at bridge/gtkb-f1f8-cross-check-001.md:21-27 and
bridge/gtkb-f1f8-cross-check-001.md:51-58.

**Required action:** Implement the full F1 surface before dependent features
consume F1 fields.

## Implementation Conditions

1. Add explicit tests for invalid `decision_authority` and for update-path
   constraints validation when the caller provides a new `constraints` dict.
   The current -005 test plan covers invalid `complexity_ceiling` and invalid
   `excluded_approaches` element cases at bridge/gtkb-f1-implementation-005.md:148-150,
   but the approved known-key contract also deserves direct `decision_authority`
   and update-path coverage.
2. Decide explicitly whether `{"excluded_approaches": None}` is rejected or
   normalized. The approved schema says `excluded_approaches` is `list[str]`;
   accepting explicit JSON null would weaken that contract.
3. Preserve raw JSON keys in `_row_to_dict()` while adding
   `constraints_parsed`, `_constraints_parsed`, `affected_by_parsed`, and
   `_affected_by_parsed`.
4. Do not implement `get_specs_affected_by()` with SQL `LIKE`; use parsed list
   containment or a normalized relation.

## Verification

- Read the full active bridge entry for `gtkb-f1-implementation`.
- Read all referenced version files:
  bridge/gtkb-f1-implementation-001.md through
  bridge/gtkb-f1-implementation-005.md.
- Read approved design/review files:
  bridge/gtkb-spec-pipeline-f1-003.md,
  bridge/gtkb-spec-pipeline-f1-007.md,
  bridge/gtkb-spec-pipeline-f1-008.md.
- Read cross-check files:
  bridge/gtkb-f1f8-cross-check-001.md,
  bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py
  around schema creation, migration, `insert_spec()`, `update_spec()`,
  `list_specs()`, and `_row_to_dict()`.
- Ran `rg` in the target checkout for F1 field/helper names and confirmed the
  checkout is still pre-F1 for the schema/API being proposed.
- No tests were run because this is a pre-implementation proposal review.

## Decision Needed

No owner decision is needed before implementation. Prime can implement F1 under
the conditions above.
