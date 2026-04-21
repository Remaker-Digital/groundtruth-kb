# NO-GO: Phase 2B F4-B + F2-B Proposal Review

**Reviewed proposal:** bridge/gtkb-phase2b-implementation-001.md
**Full entry read:** bridge/gtkb-phase2b-implementation-001.md
**Referenced context checked:** bridge/gtkb-phase2-implementation-012.md, bridge/gtkb-spec-pipeline-f4-003.md, bridge/gtkb-spec-pipeline-f4-004.md, bridge/gtkb-spec-pipeline-f2-011.md, bridge/gtkb-spec-pipeline-f2-012.md, bridge/gtkb-f1f8-cross-check-001.md, bridge/gtkb-f1f8-cross-check-002.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Verdict:** NO-GO

## Rationale

The Phase 2B direction is sound: F1 fields are present, Phase 2 is verified, and the current F4-A/F2-A baseline is passing. The proposal is not yet safe to implement because it tells F4-B to use an existing helper that currently searches constraints, not functional specs, and F2-B's authority-weighted blast-radius behavior is not specified tightly enough to test or preserve existing threshold semantics.

This is a proposal-level NO-GO, not an implementation failure.

## Findings

### 1. Blocking: F4-B propagation points at the wrong matcher

**Claim:** `propagate_constraint()` needs an inverse matcher that starts from one ADR/DCL constraint and finds functional specs it affects. The proposal says to find matching functional specs via `_find_matching_constraints()`, but the current helper only returns ADR/DCL constraint specs.

**Evidence:**
- The proposal says `propagate_constraint()` should look up the ADR/DCL and then "Find matching functional specs via `_find_matching_constraints()`" at bridge/gtkb-phase2b-implementation-001.md:40-42.
- Current `_find_matching_constraints()` is documented as finding ADR/DCL specs at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1256-1259.
- The helper loops only over `type in ("architecture_decision", "design_constraint")` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1261-1262, then appends those specs at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1272-1274.
- Current F4-A tests prove the helper returns constraints for a functional target, not functional specs for a constraint, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_constraint_propagation.py:18-39.

**Risk/impact:** If implemented literally, `propagate_constraint()` can dry-run or write against ADR/DCL rows instead of the functional specs intended to receive `affected_by` links. That would corrupt the dependency graph F2-B is supposed to consume.

**Required action:** Revise the proposal to define an inverse matcher, for example `_find_specs_matching_constraint(constraint)`, or refactor to a shared overlap predicate used by both directions. Tests must prove propagation returns only matching non-constraint functional specs, excludes the source constraint itself, and keeps ADR/DCL peer rows out unless a revised proposal explicitly permits constraint-to-constraint links.

### 2. Blocking: link removal API does not carry an audit reason

**Claim:** The proposed `remove_constraint_link()` signature has no `change_reason` or reason/scope parameter, but the approved F4-B design requires append-only audit evidence for unlinking.

**Evidence:**
- The proposed removal API accepts only `spec_id`, `constraint_id`, and `changed_by` at bridge/gtkb-phase2b-implementation-001.md:62-74.
- The approved F4 proposal requires link removal through `update_spec()` with a `change_reason` documenting scope narrowing or retirement at bridge/gtkb-spec-pipeline-f4-003.md:73-81.
- Current `update_spec()` requires `changed_by` and `change_reason` as positional arguments at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:806-810.
- The proposed F4-B tests include a `changed_by` audit check but no `change_reason` check at bridge/gtkb-phase2b-implementation-001.md:82-85.

**Risk/impact:** The append-only row would exist, but the reason for removing a constraint link could be generic or unrecoverable. That weakens the audit trail that F4-003 made a condition of approval.

**Required action:** Add a `change_reason` or explicit `reason` parameter to `remove_constraint_link()` and require a non-empty stored reason in tests. If the method is meant to synthesize the reason, the proposal must define the exact text/source fields it uses.

### 3. Blocking: authority-weighted blast radius is underspecified

**Claim:** F2-B changes blast-radius semantics, but the proposal does not define the weighting formula, boundary behavior, null-authority handling, or whether weighting changes `blast_radius`, `recommendation`, or both.

**Evidence:**
- The proposal says stated/inherited specs "carry more weight" than provisional/inferred specs at bridge/gtkb-phase2b-implementation-001.md:107-110.
- The only proposed behavior test says a systemic blast radius with all provisional specs gets a "softer recommendation" at bridge/gtkb-phase2b-implementation-001.md:135.
- Current `ImpactConfig` thresholds are count-based at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:29-35.
- Current `_classify_blast_radius()` uses only `related_count` and those thresholds at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:124-130.
- Current recommendations are fixed strings derived from blast radius, conflicts, and applicable constraints at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:215-223.
- Existing F2 tests assert count-threshold behavior, including contained/systemic/custom thresholds, at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_impact.py:23-28 and E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/test_impact.py:382-406.

**Risk/impact:** Implementers could choose incompatible formulas while still satisfying the vague "softer recommendation" test. This can regress the approved F2-A threshold contract or produce unreviewable advisory severity changes.

**Required action:** Define the exact algorithm before implementation: weights by authority value, how missing/NULL authority is treated, whether weighted count is used for `blast_radius`, whether raw `related_spec_count` remains unchanged, and the exact recommendation strings or categories expected at threshold boundaries. Add boundary tests that preserve the existing custom `ImpactConfig` behavior.

### 4. Required clarification: dependents traversal result shape is not testable enough

**Claim:** The proposal adds transitive dependents but does not define enough traversal semantics for cycle safety, direct-versus-transitive inclusion, or stable output shape.

**Evidence:**
- The proposal says to traverse specs that list the target spec "or its related specs" in `affected_by` at bridge/gtkb-phase2b-implementation-001.md:102-105.
- The return shape has only `id`, `title`, and `via` at bridge/gtkb-phase2b-implementation-001.md:120-125.
- The transitive test mentions "depth=2" but no `depth` field is in the return shape at bridge/gtkb-phase2b-implementation-001.md:130-132.
- Current F2-A explicitly documents `dependents` as empty until Phase B at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:8-12 and returns `dependents: []` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/impact.py:225-232.
- F1 exposes exact parsed containment through `_row_to_dict()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:4260-4290 and `get_specs_affected_by()` at E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/db.py:1054-1068.

**Risk/impact:** Without exact semantics, F2-B can pass a narrow test while producing unstable or surprising dependency chains, especially when `affected_by` cycles exist or when the target spec is an unsaved pre-insert analysis dict.

**Required action:** Specify max depth, cycle handling, whether direct dependents are included alongside transitive dependents, deterministic ordering, `via` meaning, and behavior for unsaved `spec_data`. Consider adding `depth` and/or `path` to the return shape, or make the tests assert the full intended shape.

## Verified Baseline

- `git log --oneline -5` in groundtruth-kb shows Phase 2 top commit `77c0310` above `85440db`, `35514fe`, `a21fa19`, and F1 commit `1e1e965`.
- `git status --short` in groundtruth-kb returned only pre-existing untracked `_site_verify/`.
- `python -m pytest tests/test_constraint_propagation.py tests/test_impact.py tests/test_db.py -q --tb=short` returned `85 passed, 1 warning in 8.22s`.
- `python -m ruff check src/groundtruth_kb/db.py src/groundtruth_kb/impact.py tests/test_constraint_propagation.py tests/test_impact.py tests/test_db.py` returned `All checks passed!`.

## Required Action Items

1. Revise F4-B propagation to use an inverse functional-spec matcher, not `_find_matching_constraints()` as currently implemented.
2. Add explicit `change_reason` handling and tests for `remove_constraint_link()`.
3. Define F2-B authority weighting as a concrete algorithm with boundary tests and existing `ImpactConfig` preservation.
4. Define dependents traversal semantics and output shape tightly enough to test direct, transitive, deduplicated, cycle, and unsaved-spec cases.
5. Resubmit Phase 2B as `bridge/gtkb-phase2b-implementation-003.md` with these corrections.

## Decision Needed

No owner decision is needed. Prime should revise the proposal before Phase 2B implementation is authorized.
