# VERIFIED: Phase 2B F4-B + F2-B Post-Implementation Review

**Reviewed report:** bridge/gtkb-phase2b-implementation-005.md
**GO reference:** bridge/gtkb-phase2b-implementation-004.md
**Full entry read:** bridge/gtkb-phase2b-implementation-005.md, bridge/gtkb-phase2b-implementation-004.md, bridge/gtkb-phase2b-implementation-003.md, bridge/gtkb-phase2b-implementation-002.md, bridge/gtkb-phase2b-implementation-001.md
**Target repo inspected:** E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
**Commit verified:** 7d166e4aee6ea34b58c0252da081c11de1c01e42
**Verdict:** VERIFIED

## Prior Deliberations

- DELIB-0706 is relevant context: GroundTruth KB spec-pipeline features are product capabilities, not Agent Red-specific custom work. Phase 2B continues that product direction.
- No harvested deliberation record was found specifically for the Phase 2B post-implementation report. The directly relevant prior review record is the active bridge thread, especially NO-GO `bridge/gtkb-phase2b-implementation-002.md` and GO `bridge/gtkb-phase2b-implementation-004.md`.

## Rationale

The Phase 2B implementation satisfies the GO conditions from `bridge/gtkb-phase2b-implementation-004.md`. The claimed commit is present, the touched code implements the approved F4-B and F2-B behaviors, and the claimed verification commands pass locally.

I found only non-blocking hardening/documentation notes. They do not prevent Phase 2B completion.

## Verification Performed

In `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`:

```text
git status --short
-> ?? _site_verify/

git log --oneline -5
-> 7d166e4 feat(F4-B,F2-B): constraint propagation writes + dependents traversal
-> 77c0310 fix(F2-A): restore approved (operation, spec_data) API + tag overlap discovery
-> 85440db fix(F2-A,F3): address NO-GO findings - scope overlap, same-glob conflicts, distribution tie-break
-> 35514fe feat(F2-A): change impact analysis - typed assertion targets + conflict detection
-> a21fa19 feat(F3,F4-A): spec quality gate + constraint lookup (Phase 2 partial)

python -m pytest tests/test_constraint_propagation.py tests/test_impact.py -q --tb=short
-> 42 passed, 1 warning in 4.47s

python -m pytest -q
-> 509 passed, 1 warning in 66.48s

python -m ruff check src/groundtruth_kb/db.py src/groundtruth_kb/impact.py tests/test_constraint_propagation.py tests/test_impact.py
-> All checks passed!

python -m ruff check .
-> All checks passed!

python -m ruff format --check .
-> 55 files already formatted

python scripts/check_docs_cli_coverage.py
-> All documentation checks passed.
```

The only repo status item is the pre-existing untracked `_site_verify/` generated output. It is not part of this Phase 2B implementation verdict.

## GO Condition Review

### 1. Inverse functional-spec matcher: MET

**Claim:** F4-B propagation no longer uses the wrong F4-A matcher and instead finds functional specs affected by an ADR/DCL constraint.

**Evidence:**
- `src/groundtruth_kb/db.py:1326-1356` implements `_find_specs_for_constraint()`.
- `src/groundtruth_kb/db.py:1339-1343` iterates current specs, excludes ADR/DCL peer specs, and excludes the source constraint ID.
- `src/groundtruth_kb/db.py:1345-1355` matches by section, scope, or tag overlap.
- `tests/test_constraint_propagation.py:186-243` covers dry-run, write propagation, already-linked skip, and ADR/DCL peer exclusion.

**Risk/impact:** The prior graph-corruption risk from using `_find_matching_constraints()` directly is resolved.

**Recommended action:** None required for Phase 2B completion.

### 2. Link removal audit reason: MET

**Claim:** `remove_constraint_link()` carries an explicit audit reason through append-only versioning.

**Evidence:**
- `src/groundtruth_kb/db.py:1406-1436` implements `remove_constraint_link()` with required keyword-only `change_reason`.
- `src/groundtruth_kb/db.py:1430-1435` calls `update_spec()` with `changed_by`, `change_reason`, and updated `affected_by`.
- `tests/test_constraint_propagation.py:245-261` verifies removal creates a new version and stores the caller's change reason.
- `tests/test_constraint_propagation.py:289-297` verifies propagation-created versions carry `changed_by="constraint-propagation"` and non-empty reason text.

**Risk/impact:** The append-only audit requirement from the GO review is satisfied.

**Recommended action:** None required for Phase 2B completion.

### 3. Authority preserves count-based blast radius: MET

**Claim:** F2-B adds authority metadata and a narrow recommendation branch without changing count-based blast-radius classification.

**Evidence:**
- `src/groundtruth_kb/impact.py:242-244` still computes `related_count` and classifies blast radius via `_classify_blast_radius(related_count, cfg)`.
- `src/groundtruth_kb/impact.py:263-280` adds authority distribution and only softens the recommendation when blast radius is systemic, related specs exist, and there are zero `stated` or `inherited` related specs.
- `src/groundtruth_kb/impact.py:290-303` preserves raw `related_spec_count` and returns the new informational fields.
- `tests/test_impact.py:488-512` verifies authority distribution and the all-low-authority systemic recommendation branch.
- Existing impact tests remain passing, including the prior threshold and custom `ImpactConfig` coverage.

**Risk/impact:** The approved F2-A count-threshold contract is preserved.

**Recommended action:** None required for Phase 2B completion.

### 4. Bounded dependent traversal: MET

**Claim:** F2-B now populates dependents from `affected_by` with max depth 2, cycle safety, deduplication, and deterministic ordering.

**Evidence:**
- `src/groundtruth_kb/impact.py:138-180` implements `_find_dependents()` with early return for missing/`<unsaved>` ID, depth-1 direct lookup, depth-2 transitive lookup, visited-set cycle safety, and `(depth, id)` sorting.
- `src/groundtruth_kb/impact.py:260-261` wires dependents into `compute_impact_analysis()`.
- `tests/test_impact.py:418-483` covers direct dependents, transitive dependents, no dependents, cycle safety, and shallowest-depth deduplication.

**Risk/impact:** The previously empty Phase A `dependents` field now has the approved bounded semantics.

**Recommended action:** None required for Phase 2B completion.

## Non-Blocking Notes

### P3: Stale Phase A comments remain in impact documentation/tests

**Evidence:**
- `src/groundtruth_kb/impact.py:8-12` still says `dependents` is always empty and Phase B will add lookup.
- `tests/test_impact.py:338-339` still comments "Phase A: dependents is always empty" in a case that remains empty only because the test spec has no dependents.

**Risk/impact:** This can confuse future reviewers, but it does not affect runtime behavior or the Phase 2B API result.

**Recommended action:** Clean the comments in a documentation/hygiene pass.

### P3: Distribution fields are sparse dictionaries

**Evidence:**
- `src/groundtruth_kb/impact.py:263-273` creates `authority_distribution` and `testability_summary` only for values present in related specs.
- A read-only ad hoc check returned empty dictionaries when there were no related specs.

**Risk/impact:** This is acceptable if callers use `.get(key, 0)`, as the tests do, but it is less explicit than the proposal's example shape with named categories.

**Recommended action:** Either document the sparse-dict contract or zero-fill canonical keys in a future compatibility polish pass.

### P3: `propagate_constraint()` does not reject non-constraint IDs

**Evidence:**
- `src/groundtruth_kb/db.py:1368-1372` loads any existing spec ID and passes it to `_find_specs_for_constraint()`.
- A read-only ad hoc check showed `db.propagate_constraint("SPEC-A", dry_run=True)` can report another functional spec in the same section as linkable.

**Risk/impact:** Not a Phase 2B blocker because the approved GO conditions did not require rejecting non-ADR/DCL IDs, and `affected_by` supports spec-to-spec dependencies elsewhere in F2-B. If this method becomes CLI- or automation-facing, permissive input could create accidental section/tag-based dependency links.

**Recommended action:** Consider adding a guard that only auto-propagates `architecture_decision` and `design_constraint` rows, or rename/document the method if functional-spec propagation is intentional.

## GroundTruth KB Vision Filter

Phase 2B reduces owner burden. Constraint propagation writes `affected_by` links through append-only DB APIs, and impact analysis now surfaces dependent chains plus authority/testability metadata. That moves routine dependency tracing away from manual owner inspection and toward repeatable evidence in the KB.

The remaining P3 notes are polish and hardening items. They do not leave Mike responsible for routine spec/code reconciliation.

## Decision Needed

No owner decision is needed for Phase 2B completion.

Prime may treat `gtkb-phase2b-implementation` as complete.
