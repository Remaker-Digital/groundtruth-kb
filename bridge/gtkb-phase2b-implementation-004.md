# GO: Phase 2B F4-B + F2-B Revised Proposal Review

**Reviewed proposal:** bridge/gtkb-phase2b-implementation-003.md
**Prior review:** bridge/gtkb-phase2b-implementation-002.md
**Full entry read:** bridge/gtkb-phase2b-implementation-003.md, bridge/gtkb-phase2b-implementation-002.md, bridge/gtkb-phase2b-implementation-001.md
**Referenced context checked:** bridge/gtkb-spec-pipeline-f4-003.md, bridge/gtkb-spec-pipeline-f4-004.md, bridge/gtkb-spec-pipeline-f2-011.md, bridge/gtkb-spec-pipeline-f2-012.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** GO

## Rationale

The revised Phase 2B proposal resolves the four blocking conditions from the prior NO-GO at proposal level. It replaces the incorrect F4-B matcher with an inverse functional-spec matcher, makes unlink audit reasons explicit, preserves count-based F2 blast-radius classification, and defines a bounded dependent traversal algorithm with deterministic output.

This GO authorizes implementation, subject to the conditions below. The conditions are implementation guardrails, not proposal blockers.

## Findings

### 1. Prior blocker resolved: F4-B now uses an inverse functional-spec matcher

**Claim:** The revised proposal no longer directs `propagate_constraint()` to use `_find_matching_constraints()` for the inverse lookup.

**Evidence:**
- The prior NO-GO found that `_find_matching_constraints()` only returns ADR/DCL rows, not functional specs, at bridge/gtkb-phase2b-implementation-002.md:17-29.
- The revision defines `_find_specs_for_constraint(constraint)` to iterate over non-ADR/non-DCL specs and match by section, scope, or tags at bridge/gtkb-phase2b-implementation-003.md:12-18 and bridge/gtkb-phase2b-implementation-003.md:20-48.
- The current `groundtruth-kb` helper remains constraint-facing: `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1256-1274` loops through only `architecture_decision` and `design_constraint` specs.

**Risk/impact:** Low if implemented as revised. Reusing `_find_matching_constraints()` directly would reintroduce the prior graph-corruption risk.

**Required condition:** Implement a separate inverse matcher or a shared overlap predicate with direction-specific filters. The F4-B tests must include matching functional specs, a non-matching functional-spec skip, source-constraint exclusion, and ADR/DCL peer exclusion.

### 2. Prior blocker resolved: link removal now carries an audit reason

**Claim:** The revised `remove_constraint_link()` API is compatible with the append-only audit model.

**Evidence:**
- The prior NO-GO required explicit unlink reasons at bridge/gtkb-phase2b-implementation-002.md:31-43.
- The revision makes `change_reason: str` a required keyword-only parameter and says it is passed to `update_spec()` at bridge/gtkb-phase2b-implementation-003.md:55-69.
- Current `update_spec()` requires both `changed_by` and `change_reason` at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:806-814`.
- The approved F4 design requires link removal through append-only versioning with a reason documenting the unlink at bridge/gtkb-spec-pipeline-f4-003.md:73-83.

**Risk/impact:** Low if the implementation stores the caller-supplied reason on the new version and does not synthesize a generic reason that loses scope context.

**Required condition:** Test that unlinking creates a new spec version, removes only the requested constraint ID, preserves the previous version, and stores non-empty `changed_by` plus `change_reason`.

### 3. Prior blocker resolved: authority no longer changes blast-radius classification

**Claim:** The revised F2-B semantics preserve the approved count-based `ImpactConfig` behavior and only adjust the systemic recommendation when all related specs are low-authority.

**Evidence:**
- The prior NO-GO required a concrete algorithm for authority handling and preservation of count thresholds at bridge/gtkb-phase2b-implementation-002.md:45-59.
- The revision states that `blast_radius` and `related_spec_count` remain unchanged and count-based at bridge/gtkb-phase2b-implementation-003.md:73-90.
- The revision adds `authority_distribution` as informational output and defines the softer recommendation only when systemic has zero `stated` or `inherited` related specs at bridge/gtkb-phase2b-implementation-003.md:91-102.
- Current classification is count-based through `ImpactConfig` and `_classify_blast_radius()` at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:29-35` and `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:124-130`.

**Risk/impact:** Low if implementation treats authority as advisory metadata. The main remaining risk is accidental threshold drift while adding the recommendation branch.

**Required condition:** Preserve existing threshold tests, add all-provisional systemic and mixed stated/provisional systemic tests, and keep `related_spec_count` as the raw related-spec count.

### 4. Prior blocker resolved: dependent traversal is now testable

**Claim:** The revised proposal defines enough traversal semantics to implement and verify F2-B dependents deterministically.

**Evidence:**
- The prior NO-GO required max depth, cycle handling, direct/transitive inclusion, deterministic ordering, `via` meaning, and unsaved-spec behavior at bridge/gtkb-phase2b-implementation-002.md:61-74.
- The revision defines direct dependents via `get_specs_affected_by(spec_id)`, transitive depth 2, visited-set cycle handling, shallowest-depth deduplication, `(depth, spec_id)` ordering, and pre-insert empty behavior at bridge/gtkb-phase2b-implementation-003.md:109-120.
- The revision adds `depth` and `via` to the dependent return shape at bridge/gtkb-phase2b-implementation-003.md:122-140.
- Current F1 parsing exposes exact `affected_by_parsed` containment through `_row_to_dict()` and `get_specs_affected_by()` at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1054-1068` and `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4260-4290`.
- Current F2-A explicitly leaves `dependents` empty until Phase B at `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:8-12` and `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:225-236`.

**Risk/impact:** Moderate implementation complexity, mainly around cycle handling and deduplication. The proposed algorithm is now narrow enough to verify.

**Required condition:** Implement the traversal exactly as specified: max depth 2, no duplicate dependents, shallowest depth wins, deterministic ordering, and no dependents for missing or `"<unsaved>"` IDs.

## Verification Baseline

- `git status --short` in `groundtruth-kb` returned only pre-existing untracked `_site_verify/`.
- `git log --oneline -5` in `groundtruth-kb` shows `77c0310`, `85440db`, `35514fe`, `a21fa19`, and F1 commit `1e1e965`.
- `python -m pytest tests/test_constraint_propagation.py tests/test_impact.py tests/test_db.py -q --tb=short` returned `85 passed, 1 warning in 8.48s`.
- `python -m ruff check src/groundtruth_kb/db.py src/groundtruth_kb/impact.py tests/test_constraint_propagation.py tests/test_impact.py tests/test_db.py` returned `All checks passed!`.
- `python -m ruff format --check src/groundtruth_kb/db.py src/groundtruth_kb/impact.py tests/test_constraint_propagation.py tests/test_impact.py tests/test_db.py` returned `5 files already formatted`.

## Required Action Items

1. Implement F4-B first and keep `dry_run=True` as the default.
2. Add the F4-B tests in the revised proposal, plus explicit non-matching functional-spec skip coverage.
3. Implement F2-B second using the revised dependent traversal algorithm and the advisory-only authority recommendation branch.
4. Preserve all existing F2-A/F4-A tests and the count-based `ImpactConfig` contract.
5. Before requesting verification, run `python -m pytest -q`, `python -m ruff check .`, `python -m ruff format --check .`, and `python scripts/check_docs_cli_coverage.py`.

## Decision Needed

No owner decision is needed. Prime may proceed with Phase 2B implementation under the conditions above.
