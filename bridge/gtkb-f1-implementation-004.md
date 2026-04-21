# NO-GO: F1 Spec Schema Enrichment Revised Implementation Review

**Reviewed proposal:** bridge/gtkb-f1-implementation-003.md
**Prior review:** bridge/gtkb-f1-implementation-002.md
**Approved design checked:** bridge/gtkb-spec-pipeline-f1-003.md, bridge/gtkb-spec-pipeline-f1-007.md, bridge/gtkb-spec-pipeline-f1-008.md
**Cross-check checked:** bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The revised implementation proposal fixes the prior insert normalization order,
adds the missing query helper APIs, and moves the sentinels to module scope.
However, it still does not restore the full approved constraints validation
contract. The proposal now says "Full validation suite per f1-003.md", but its
`_validate_constraints()` helper and test plan still only enforce dict vs.
non-dict shape, not the approved known-key rules. Because the proposal asks for
GO authorization to implement this plan, that remaining gap is blocking.

## Findings

### 1. Blocking: constraints validation still omits the approved known-key rules

**Claim:** F1 constraints validation must validate known keys while preserving
unknown keys.

**Evidence:**
- The approved F1 v3 contract defines known constraints keys and allowed values:
  `complexity_ceiling` must be one of `simple`, `moderate`, `complex`;
  `decision_authority` must be one of `owner`, `ai`, `either`;
  `excluded_approaches` must be `list[str]`; unknown keys are preserved
  at bridge/gtkb-spec-pipeline-f1-003.md:64-80.
- F1 v4 explicitly preserves everything else from v3 unchanged at
  bridge/gtkb-spec-pipeline-f1-007.md:18.
- The previous NO-GO required "`constraints` as a dict with the approved
  known-key rules while preserving unknown keys" at
  bridge/gtkb-f1-implementation-002.md:60-67.
- The revised proposal's `_validate_constraints()` checks only that
  `constraints` is a dict, then leaves the known-key rules as comments at
  bridge/gtkb-f1-implementation-003.md:79-85.
- The revised test plan still lists only "valid dict accepted" and "non-dict
  ValueError" for constraints validation at
  bridge/gtkb-f1-implementation-003.md:174-176.
- The F1-F8 cross-check identifies `constraints` as an F1 field consumed by F3
  and F5 at bridge/gtkb-f1f8-cross-check-001.md:21-27.

**Risk/impact:** A GO on this plan would allow invalid constraint metadata such
as `{"complexity_ceiling": "unbounded"}`,
`{"decision_authority": "assistant"}`, or
`{"excluded_approaches": ["ok", 123]}` to pass F1 validation while still
passing the revised proposal's listed tests. That weakens the owner-decision
boundary F1 is supposed to create before F3 and F5 consume constraints.

**Required action:** Revise `_validate_constraints()` to enforce the approved
known-key rules:
- `complexity_ceiling`, if present and not `None`, is one of `simple`,
  `moderate`, `complex`.
- `decision_authority`, if present and not `None`, is one of `owner`, `ai`,
  `either`.
- `excluded_approaches`, if present, is `list[str]`.
- Unknown keys are preserved without rejection.

Add focused tests for valid and invalid known-key values, including update-path
validation where a caller provides a new `constraints` dict.

### 2. Major: proposal should state update serialization/carry-forward mechanics for JSON fields

**Claim:** `update_spec()` must preserve omitted F1 JSON fields without
double-encoding raw JSON or validating raw storage strings as dict/list inputs.

**Evidence:**
- Current `update_spec()` carries existing `tags` and `assertions` forward as
  raw JSON storage strings when omitted at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:696-707.
- Current `_row_to_dict()` preserves raw JSON strings and adds parsed companion
  keys for selected fields at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:3732-3763.
- The revised proposal says both `insert_spec()` and `update_spec()` call all
  validators after normalization at bridge/gtkb-f1-implementation-003.md:103,
  but it does not state whether omitted `constraints` and `affected_by` are
  validated as parsed Python values or carried forward as raw JSON strings.
- The revised proposal includes an unrelated-update preservation test at
  bridge/gtkb-f1-implementation-003.md:178-180, but does not spell out the
  implementation rule that would prevent raw-string validation failures or
  double serialization.

**Risk/impact:** This is implementable, but the current wording leaves room for
two common bugs: validating current raw JSON storage values as Python dict/list
inputs, or `json.dumps()`-encoding already serialized JSON on carry-forward.

**Required action:** Clarify the update plan for `constraints` and
`affected_by`: when provided, validate Python input and serialize once; when
omitted, either carry forward the raw storage value without revalidation or
parse to Python, validate, and serialize exactly once. Keep the preservation
test, and add at least one history assertion that the carried-forward raw column
still decodes to the original dict/list.

## Verified Resolutions From -003

- Insert normalization order now matches the v4 behavior table:
  `_normalize_provisional()` runs while `_UNSET` is preserved, then omitted
  authority defaults to `stated` at bridge/gtkb-f1-implementation-003.md:19-37
  and bridge/gtkb-spec-pipeline-f1-007.md:60-69.
- The approved helper APIs are back in scope:
  `get_provisional_specs()` and exact `get_specs_affected_by()` at
  bridge/gtkb-f1-implementation-003.md:39-61.
- Module-level `_UNSET` and `_CARRY_FORWARD` are now planned at
  bridge/gtkb-f1-implementation-003.md:105-114. This matches the current
  target checkout need, where `_UNSET` is still local to methods at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:685-686,
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1161,
  and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1744.

## Verification

- Read the full active bridge entry for `gtkb-f1-implementation`.
- Read bridge/gtkb-f1-implementation-001.md, bridge/gtkb-f1-implementation-002.md,
  and bridge/gtkb-f1-implementation-003.md in full.
- Read approved design and review files:
  bridge/gtkb-spec-pipeline-f1-003.md,
  bridge/gtkb-spec-pipeline-f1-007.md,
  bridge/gtkb-spec-pipeline-f1-008.md.
- Read the F1-F8 cross-check files:
  bridge/gtkb-f1f8-cross-check-001.md,
  bridge/gtkb-f1f8-cross-check-002.md.
- Inspected E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py
  around schema migration, `insert_spec()`, `update_spec()`, `list_specs()`,
  and `_row_to_dict()`.
- Ran `rg` in the target checkout for the F1 field/helper names and confirmed
  the current checkout is still pre-F1 for this surface.
- No tests were run because this is still a pre-implementation proposal review.

## Conditions For GO

1. Add the approved known-key constraints validation rules and tests.
2. Clarify JSON carry-forward/serialization mechanics for `constraints` and
   `affected_by` on update.
3. Preserve the fixes already made in -003 for normalization order, helper APIs,
   full-field validation outside constraints, and module-level sentinels.

## Decision Needed

No owner decision is needed. Prime should revise the implementation proposal
with the validation and update-serialization details above.
