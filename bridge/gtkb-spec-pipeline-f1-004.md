# NO-GO: F1 Spec Schema Enrichment Revised Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f1-003.md  
**Prior review:** bridge/gtkb-spec-pipeline-f1-002.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The revision resolves the largest issues from v1: `type` is no longer proposed as new, legacy `authority` no longer defaults to `stated`, and priority normalization is removed. It is close, but still has two blocking contract contradictions that can produce a broken implementation.

## Findings

### 1. Blocking: `authority="stated"` default conflicts with provisional auto-detection

**Claim:** `insert_spec(provisional_until="SPEC-999")` without `authority` should auto-set `authority="provisional"`.

**Evidence:**
- Revision says new inserts default `authority` to `'stated'` at bridge/gtkb-spec-pipeline-f1-003.md:45.
- Revision says non-provisional specs must not set `provisional_until` at bridge/gtkb-spec-pipeline-f1-003.md:157.
- Revision says setting `provisional_until` auto-sets `authority='provisional'` when authority is not provided at bridge/gtkb-spec-pipeline-f1-003.md:160.
- Proposed signature uses `authority: str | None = "stated"` at bridge/gtkb-spec-pipeline-f1-003.md:173.
- Test case 11 expects `insert_spec(provisional_until='SPEC-999')` to become provisional at bridge/gtkb-spec-pipeline-f1-003.md:263.

**Risk/impact:** With the proposed signature, an omitted authority arrives as `"stated"`. The implementation cannot distinguish omitted authority from an explicit `authority="stated"` unless it uses a sentinel. INV-2 and INV-5 will fight each other, and one of the proposed tests must fail.

**Required action:** Use an explicit sentinel for omitted authority, or default `authority` to `None` and apply the `"stated"` default after provisional normalization. Add tests for both cases: omitted authority plus `provisional_until` auto-sets provisional, while explicit `authority="stated"` plus `provisional_until` raises.

### 2. Blocking: Python output type contract does not match the proposed `_row_to_dict()` implementation

**Claim:** `constraints` should return as `dict | None`, and `affected_by` should return as `list[str] | None`.

**Evidence:**
- Revision specifies `constraints` output as `dict | None` at bridge/gtkb-spec-pipeline-f1-003.md:60.
- Revision specifies `affected_by` output as `list[str] | None` at bridge/gtkb-spec-pipeline-f1-003.md:100.
- Revision proposes only adding both fields to `_row_to_dict()` JSON parsing at bridge/gtkb-spec-pipeline-f1-003.md:220.
- Current `_row_to_dict()` preserves the raw string field and adds `<field>_parsed` and `_<field>_parsed`; it does not replace the original field value. See E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3732 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3759.

**Risk/impact:** Callers and `get_specs_affected_by()` can accidentally inspect the raw JSON string instead of the parsed list. The proposal promises one API shape but specifies code that produces the existing raw-plus-parsed shape.

**Required action:** Pick one API contract and test it. Either preserve the existing pattern (`affected_by` raw string plus `affected_by_parsed`) and update the proposal, or deliberately replace the field value for these new fields and test backward compatibility for the existing JSON fields.

### 3. Major: The API diff includes unrelated or incorrect current-code references

**Evidence:**
- Proposed `insert_spec()` signature adds `parent_id=None` at bridge/gtkb-spec-pipeline-f1-003.md:171.
- Current `insert_spec()` has no `parent_id` parameter. Existing parent support is derived from dotted IDs via helper/listing functions, not a schema column. `rg -n "parent_id" src/groundtruth_kb/db.py tests docs` found helpers and child-listing only.
- Revision says validation is consistent with current `type` and tag validation at bridge/gtkb-spec-pipeline-f1-003.md:133, but current `insert_spec()` auto-detects type rather than validating a closed enum at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:579 and only serializes tags at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:614.

**Risk/impact:** The implementer may add an unrequested `parent_id` surface or model validation after non-existent current behavior, increasing API churn in a foundational migration.

**Required action:** Remove `parent_id` from F1 unless a separate schema/API change is intended. Correct the validation references and state plainly that authority/testability validation will be a new validation pattern for these new fields.

## Conditions For GO

1. Resolve the authority default/provisional normalization contradiction with a sentinel or equivalent explicit omitted-value handling.
2. Make the `constraints` and `affected_by` output contract match the actual `_row_to_dict()` behavior and tests.
3. Remove unrelated `parent_id` API churn and correct references to current validation behavior.

