REVISED
::init gtkb pb
::open build
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-41-57Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Implementation Proposal — WI-5666 complete bounded skill-reference sweep

bridge_kind: prime_proposal
Document: gtkb-wi5666-gitignore-docs-script-skill-refs
Version: 005
Responds to: bridge/gtkb-wi5666-gitignore-docs-script-skill-refs-004.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5666

target_paths: [".gitignore", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", "docs/procedures/per-thread-finalization-repair.md", "docs/harness-parity-phase-2-matrix.md"]

implementation_scope: documentation | configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Replace every current mapped bare skill-directory reference in the four
original WI-5666 targets. This supersedes the stopped two-pattern attempt:
the scope now includes all eight stale scratch patterns in .gitignore and all
six live documentation pointers, including the assertion-triage reference
omitted by the prior proposal. No source code, migration policy, fixture,
archive, generated artifact, or unrelated one-off script is in scope.

## Claim

Prime Builder proposes one bounded, whole-file-complete canonicalization slice.
No temporary source edit from version 003 is retained and no commit or terminal
verdict is claimed by that stopped attempt.

## Requirement Sufficiency

Existing requirements sufficient. WI-5666, the active scoped project
authorization, the canonical config/agent-control/gtkb-skill-rename-map.toml
mapping, and the owner-authorized skill-rename sweep define the complete
four-file acceptance boundary. No new owner decision is required.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- GOV-STANDING-BACKLOG-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001

## Prior Deliberations And Stopped Attempt

- DELIB-202667193 authorizes autonomous sweep slices while retaining per-slice
  Loyal Opposition GO and VERIFIED gates.
- bridge/gtkb-wi5666-gitignore-docs-script-skill-refs-003.md applied four
  temporary edits only to run the approved verification, found six additional
  stale .gitignore paths, and fully reverted them. It created no source diff
  and no commit.
- bridge/gtkb-wi5666-gitignore-docs-script-skill-refs-004.md requires a new
  proposal with scope capable of satisfying the whole-file acceptance contract.

## Exact Proposed Changes

- In .gitignore, canonicalize all eight stale patterns:
  bridge to gtkb-bridge at line 617; and verify to gtkb-verify at lines
  618, 619, 620, 672, 673, 674, and 675. The corresponding Codex verify
  paths use .codex/skills/gtkb-verify.
- In groundtruth-kb/docs/reference/canonical-terminology-detail.md, canonicalize
  bridge-propose to gtkb-bridge-propose and assertion-triage to
  gtkb-assertion-triage.
- In docs/procedures/per-thread-finalization-repair.md, canonicalize verify to
  gtkb-verify.
- In docs/harness-parity-phase-2-matrix.md, canonicalize both Claude and Codex
  bridge and verify paths to their gtkb-prefixed directories.
- Do not alter generic .claude/skills wildcard rules, historical evidence,
  config/file-reference-migration/wi5640.toml, or unrelated dirty files.

## Specification-Derived Verification Plan

| Property | Exact verification | Expected result |
| --- | --- | --- |
| Complete four-file reference closure | rg -n -o --pcre2 '\\.(?:claude|codex)/skills/(?:bridge|verify|bridge-propose|assertion-triage)(?:/|$)' -- .gitignore groundtruth-kb/docs/reference/canonical-terminology-detail.md docs/procedures/per-thread-finalization-repair.md docs/harness-parity-phase-2-matrix.md | No output. |
| Canonical pattern 617 | git check-ignore -q -- .claude/skills/gtkb-bridge/helpers/draft-x.md | Exit 0. |
| Canonical pattern 618 | git check-ignore -q -- .claude/skills/gtkb-verify/helpers/draft-x.md | Exit 0. |
| Canonical pattern 619 | git check-ignore -q -- .claude/skills/gtkb-verify/helpers/_temp_verdict_x | Exit 0. |
| Canonical pattern 620 | git check-ignore -q -- .claude/skills/gtkb-verify/helpers/x-draft-body.md | Exit 0. |
| Canonical pattern 672 | git check-ignore -q -- .claude/skills/gtkb-verify/helpers/tmp_gtkb-wi1-draft.md | Exit 0. |
| Canonical pattern 673 | git check-ignore -q -- .claude/skills/gtkb-verify/helpers/write_bridge_x.py | Exit 0. |
| Canonical pattern 674 | git check-ignore -q -- .codex/skills/gtkb-verify/helpers/tmp_gtkb-wi1-draft.md | Exit 0. |
| Canonical pattern 675 | git check-ignore -q -- .codex/skills/gtkb-verify/helpers/gtkb-wi1-draft-body.md | Exit 0. |
| Diff integrity | git diff --check -- .gitignore groundtruth-kb/docs/reference/canonical-terminology-detail.md docs/procedures/per-thread-finalization-repair.md docs/harness-parity-phase-2-matrix.md | Exit 0. |
| Bridge linkage | python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5666-gitignore-docs-script-skill-refs; python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5666-gitignore-docs-script-skill-refs | Both pass with no required gap. |

## Acceptance Criteria

- No mapped bare bridge, verify, bridge-propose, or assertion-triage directory
  reference remains in any of the four declared targets.
- Each of the eight renamed .gitignore patterns causes its canonical test path
  to be ignored.
- No generic wildcard rule, history, migration policy, fixture, generated
  artifact, or unrelated source file is changed.
- The implementation commit contains only the four declared targets, and the
  implementation report records all observed verification results before
  independent LO review.

## Cross-Harness Disposition

Claude and Codex scratch paths are both covered by their corresponding
canonical ignore patterns. No harness runtime behavior, adapter, hook, or
typed waiver changes are proposed.

## Risks And Rollback

Risk is limited to ignore-pattern precedence. The exact per-pattern
git check-ignore checks make that observable. Rollback is a separate governed
revert of the scoped four-file commit; the stopped version 003 remains
append-only evidence and is not amended or deleted.

## Owner Decisions / Input

No additional owner input is required. The revision expands to the complete
deterministic inventory required by the existing acceptance contract.

## Recommended Commit Type

fix

