# NO-GO: Phase 2 F3 + F2-A + F4-A Revised Post-Implementation Verification

**Reviewed report:** bridge/gtkb-phase2-implementation-009.md
**Prior NO-GO:** bridge/gtkb-phase2-implementation-008.md
**GO reference:** bridge/gtkb-phase2-implementation-006.md
**Full entry read:** bridge/gtkb-phase2-implementation-001.md through bridge/gtkb-phase2-implementation-009.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The reported fixes for the three concrete implementation defects from
bridge/gtkb-phase2-implementation-008.md are present, and the broad verification
commands pass. However, the revised report explicitly retains a narrowed F2-A
public API instead of restoring the approved `operation, spec_data` contract or
submitting a revised F2 proposal. It also leaves Phase 2's approved tag-overlap
related-spec behavior unresolved and unimplemented.

These are contract issues, not CI issues. A VERIFIED response would ratify an
API and related-spec scope that the approved bridge proposal did not authorize.

## Findings

### 1. Blocking: F2-A public API remains narrowed without a revised proposal

**Claim:** Phase 2 cannot be VERIFIED while `KnowledgeDB.compute_impact()` keeps
the narrowed `spec_id`-only API after the prior NO-GO required either restoring
the approved contract or routing the narrowing through a revised bridge proposal.

**Evidence:**
- The approved F2 Phase A API is
  `compute_impact(operation: str, spec_data: dict, *, config: ImpactConfig | None = None)`
  at bridge/gtkb-spec-pipeline-f2-003.md:61-67.
- The approved Phase 2 proposal repeats the same method contract at
  bridge/gtkb-phase2-implementation-001.md:126-130.
- The prior NO-GO listed the `spec_id`-only signature as part of the contract
  mismatch at bridge/gtkb-phase2-implementation-008.md:46-48.
- The prior NO-GO required: "Restore the approved F2-A contract or submit a
  revised F2 bridge proposal that explicitly narrows it" at
  bridge/gtkb-phase2-implementation-008.md:59-60.
- The latest revised report acknowledges the narrowed signature is retained:
  "The `compute_impact(spec_id, *, config)` signature is retained rather than
  the `(operation, spec_data)` from the original F2 proposal" at
  bridge/gtkb-phase2-implementation-009.md:26-31.
- Current implementation still exposes only `spec_id`:
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1326-1341.
- Targeted command output in the target checkout:
  `signature: (self, spec_id: 'str', *, config: 'Any | None' = None) -> 'dict[str, Any]'`
  and
  `operation_spec_data_call: TypeError KnowledgeDB.compute_impact() takes 2 positional arguments but 3 were given`.

**Risk/impact:** The approved API supports advisory analysis of a proposed
operation and spec payload before the spec is inserted or updated. The retained
API can only analyze an existing persisted spec by ID. That narrows the owner
decision workflow and forces downstream callers to either persist first or build
their own pre-insert impact wrapper.

**Required action:** Either implement the approved public API, with backwards
compatibility for the current `spec_id` helper if desired, or submit a revised
F2 bridge proposal that explicitly narrows the API and obtain GO before asking
for Phase 2 verification.

### 2. Blocking: Phase 2 tag-overlap related-spec behavior is unresolved and absent

**Claim:** The approved Phase 2 proposal says related-spec discovery uses
`section/scope/tags` overlap. The latest implementation and report use only
section or scope overlap, without implementing tag-only overlap or explicitly
de-scoping it through the bridge.

**Evidence:**
- The approved Phase 2 proposal says: "Phase A uses: section/scope/tags overlap
  for related specs" at bridge/gtkb-phase2-implementation-001.md:132-133.
- The prior NO-GO required resolving whether Phase 2's tag overlap remains
  required and adding a tag-only regression test if retained at
  bridge/gtkb-phase2-implementation-008.md:59-64.
- The latest revised report says related-spec discovery now uses "section OR
  scope overlap" and lists only scope/report-shape regressions at
  bridge/gtkb-phase2-implementation-009.md:13-24.
- Current `compute_impact_analysis()` checks only section and scope for related
  specs at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:162-176.
- A targeted probe inserted two specs with different sections and scopes but the
  same tag. `db.compute_impact("SPEC-A")` returned
  `tag_only_related_ids: []`.
- `rg -n "tag_only|tag-only|tags.*overlap|overlap.*tags" tests/test_impact.py`
  returned no matches, and the same search in bridge/gtkb-phase2-implementation-009.md
  returned no matches.

**Risk/impact:** Tag-only relationships remain invisible in F2-A even though
Phase 2 authorized tags as part of related-spec discovery. That can understate
blast radius for cross-cutting areas where section/scope differ but tags encode
shared concerns.

**Required action:** Implement tag-overlap related-spec discovery and add a
tag-only regression test, or explicitly remove tag overlap through a revised
bridge proposal before requesting VERIFIED.

## Verified Resolved Points

- `git log --oneline -5` in the target checkout shows `85440db` on top of
  `35514fe` and `a21fa19`.
- `git status --short` in the target checkout returned only `?? _site_verify/`.
- Targeted Phase 2 checks passed:
  `python -m pytest tests/test_impact.py tests/test_quality_gate.py::TestF3QualityGate::test_f3_distribution_no_double_count -q --tb=short`
  returned `19 passed, 1 warning`.
- Broad checks pass:
  `python -m pytest -q --tb=short` returned `491 passed, 1 warning`.
- `python -m ruff check .` returned `All checks passed!`.
- `python -m ruff format --check .` returned `55 files already formatted`.
- `python scripts/check_docs_cli_coverage.py` returned
  `All documentation checks passed.`
- Same-glob conflict handling now compares exact-equal file targets before the
  glob limitation path at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:85-114.
- `get_quality_distribution()` now uses `MAX(rowid)` to select one latest row per
  spec at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1226-1252.
- The corresponding regression tests exist at
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_impact.py:305,
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_impact.py:318,
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_impact.py:335,
  and
  E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_quality_gate.py:230.

## Conditions For VERIFIED

1. Resolve the F2-A public API mismatch by implementing the approved
   `operation, spec_data` contract or by obtaining GO on a revised F2 proposal
   that explicitly narrows the API.
2. Resolve Phase 2 tag-overlap related-spec behavior by implementing it with a
   tag-only regression test or by obtaining GO on a revised proposal that
   explicitly removes it.
3. Re-run `python -m pytest -q --tb=short`, `python -m ruff check .`,
   `python -m ruff format --check .`, and
   `python scripts/check_docs_cli_coverage.py`.

## Decision Needed

No owner decision is needed if Prime restores the approved API and tag-overlap
behavior. Owner/Prime decision is needed only if Prime wants to narrow the
approved F2-A API or remove tag-overlap related-spec discovery.
