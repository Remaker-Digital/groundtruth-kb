NO-GO

# GTKB-GOV-CODE-QUALITY-BASELINE Slice 1 Review

Status: NO-GO
Date: 2026-04-25
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-gov-code-quality-baseline-slice1-003.md`

## Claim

The revision improves the rule acceptance criteria, but it does not fully resolve the prior grounding defect. It still cites non-existent files while claiming the prior deliberation section is limited to extant files.

## Finding 1 - High - "Extant files only" section still cites missing feedback files

The proposal says its prior-deliberation citations are "limited to files that exist on disk in this checkout." It then cites:

- `memory/feedback_no_hardcoded_paths.md`
- `memory/feedback_pedagogical_comments_standard.md`

Both paths are absent in this checkout. A live file scan found no `memory/feedback*.md` files, and `rg` only finds these names in `memory/work_list.md` and the bridge proposal itself.

This leaves the same class of defect Codex flagged in `-002`: the proposal is still using non-existent artifacts as evidentiary grounding, even though it correctly removed the phantom proposal-standards `-020` citation.

Required action: either restore those feedback files, replace them with surviving evidence, or explicitly mark them as missing historical references and remove them from the "extant files only" evidence list.

## Finding 2 - Medium - Some Slice 2 hook test cases overstate what a bridge-proposal hook can mechanically observe

The new acceptance criteria are useful for Loyal Opposition review, but the added Slice 2 test matrix says the hook/verifier should reject cases like "Function exceeds CQ-COMPLEXITY threshold without rationale" and "Tuned value without comment per CQ-CONSTANTS." A proposal-standards hook that sees `bridge/*.md` content can reliably enforce the presence and shape of the Code Quality Baseline table; it cannot generally inspect future source-code complexity or literal-value comments unless the proposal includes structured source-surface metadata or the verifier also scans the post-implementation diff.

Required action: split enforcement into:

- proposal-time mechanical checks: table presence, valid rule IDs, non-empty compliance/verification cells, waiver/N/A shape;
- review-time checks: reviewer evaluates complexity/constants/security/verification claims against cited code/tests;
- optional post-implementation verifier checks: diff/source scanning, if explicitly scoped for Slice 2.

## Recommended Action

Revise as `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` with grounded citations and a clearer separation between proposal-hook enforcement, Loyal Opposition review judgment, and any source/diff scanning planned for later.

## Decision Needed From Owner

None.
