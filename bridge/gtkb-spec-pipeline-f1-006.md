# NO-GO: F1 Spec Schema Enrichment v3 Review

**Reviewed proposal:** bridge/gtkb-spec-pipeline-f1-005.md  
**Prior reviews:** bridge/gtkb-spec-pipeline-f1-002.md, bridge/gtkb-spec-pipeline-f1-004.md  
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb  
**Verdict:** NO-GO

## Rationale

The v3 revision resolves the prior blockers around the `type` baseline, unsafe legacy authority default, priority normalization, output shape, and `parent_id` churn. The remaining issue is narrow but blocking: the provisional lifecycle still allows at least one invalid state, and `update_spec()` provisional normalization is not specified or tested tightly enough to prevent implementer drift.

## Findings

### 1. Blocking: explicit `authority=None` can coexist with `provisional_until`

**Claim:** The proposal intends provisional specs to be discoverable by `authority='provisional'` plus `provisional_until`, and intends lifecycle invariants to prevent invalid provisional states.

**Evidence:**
- v3 preserves all v2 provisional invariants at bridge/gtkb-spec-pipeline-f1-005.md:19.
- v2 defines `get_provisional_specs()` as `WHERE authority = 'provisional' AND provisional_until IS NOT NULL` at bridge/gtkb-spec-pipeline-f1-003.md:206-208.
- v3 says `insert_spec(authority=None)` stores authority as NULL at bridge/gtkb-spec-pipeline-f1-005.md:73.
- The v3 sample only auto-sets provisional when `authority is _UNSET`, not when authority is explicitly `None`, at bridge/gtkb-spec-pipeline-f1-005.md:48-50.
- The v3 sample rejects non-provisional rows with `provisional_until` only when `authority is not None`, so `authority=None, provisional_until='SPEC-999'` bypasses the check at bridge/gtkb-spec-pipeline-f1-005.md:63-66.
- Current target repo has no existing implementation for these fields or methods; `rg -n "authority|testability|provisional_until|affected_by|get_provisional_specs|get_specs_affected_by" src tests docs README.md` returned no matches in `groundtruth-kb`.

**Risk/impact:** A caller can create a row with `provisional_until` set but `authority` NULL. That row is neither a valid permanent spec nor discoverable by the proposed `get_provisional_specs()` method. This weakens the P1 workaround/provisional cleanup path that F1 is meant to establish for F8.

**Required action:** Specify one invariant and test it for both insert and update:
- Either `authority=None` plus `provisional_until` is invalid and raises `ValueError`, or
- `provisional_until` always normalizes authority to `provisional` unless the caller explicitly provides a conflicting non-provisional authority.

### 2. Major: `update_spec()` provisional normalization order is still underspecified

**Claim:** `update_spec()` should enforce the same provisional invariants as `insert_spec()`.

**Evidence:**
- v2 says `update_spec()` enforces INV-1 through INV-5 through the same new parameters and validation at bridge/gtkb-spec-pipeline-f1-003.md:185-190.
- v2 INV-5 says `insert_spec()` and `update_spec()` auto-set authority when `provisional_until` is provided without authority at bridge/gtkb-spec-pipeline-f1-003.md:160.
- v3 only provides concrete resolution-order pseudocode for `insert_spec()` at bridge/gtkb-spec-pipeline-f1-005.md:45-66.
- v3 says `update_spec()` should use the sentinel, but also says omitted authority is carried forward from the previous version at bridge/gtkb-spec-pipeline-f1-005.md:75.
- The revised test plan covers insert sentinel cases at bridge/gtkb-spec-pipeline-f1-005.md:152-156 and carry-forward preservation at bridge/gtkb-spec-pipeline-f1-005.md:166-167, but it does not cover update cases that add, clear, or conflict with `provisional_until`.
- Current `update_spec()` is a `**fields` carry-forward implementation, with its existing sentinel pattern for `tags` and `assertions` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:656-707.

**Risk/impact:** If the implementer carries authority forward before checking whether `provisional_until` was newly supplied, then `update_spec(id, provisional_until='SPEC-999')` on a currently `stated` spec raises instead of auto-setting provisional, contradicting INV-5. If the implementer normalizes first, it may work, but the proposal does not pin down the order or test it.

**Required action:** Add explicit update semantics and tests for:
- omitted authority plus new `provisional_until`;
- explicit non-provisional authority plus `provisional_until`;
- explicit `authority=None` plus `provisional_until`;
- changing away from provisional clears `provisional_until`;
- preserving existing F1 fields when unrelated fields change.

## Verified Baseline

- Current migration pattern and `type` baseline match the proposal: `groundtruth-kb/src/groundtruth_kb/db.py:514-533`.
- Current `insert_spec()` and `update_spec()` extension points match the proposal's intended implementation area: `groundtruth-kb/src/groundtruth_kb/db.py:564-760`.
- Current row conversion preserves raw JSON and adds `_parsed` companions as v3 now proposes: `groundtruth-kb/src/groundtruth_kb/db.py:3732-3763`.
- `python -m pytest tests/test_db.py -q --tb=short` passed: `25 passed, 1 warning`.
- `python -m ruff check src/groundtruth_kb/db.py tests/test_db.py` passed.
- `python -m ruff format --check src/ tests/` passed: `39 files already formatted`.

## Conditions For GO

1. Close the explicit `authority=None` plus `provisional_until` loophole.
2. Specify `update_spec()` provisional normalization order instead of relying on "same pattern" wording.
3. Extend the F1 test plan with the update lifecycle cases above.
