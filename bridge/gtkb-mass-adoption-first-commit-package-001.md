NEW

# GT-KB Mass Adoption First Commit Package Proposal

target_paths: ["E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement/bridge/INDEX.md", "E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement/bridge/*.md", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/*.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src/groundtruth_kb/project/*.py", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/templates/**", "E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/tests/*.py"]
bridge_kind: prime_proposal
implementation_scope: protocol
target_project: GroundTruth-KB mass-adoption readiness
work_item_ids: ["GTKB-MASS-001", "GTKB-GOV-012", "GTKB-CORE-001"]
requires_verification: true

## Status

NEW - Loyal Opposition review requested before any staging, commit, push, or
merge activity.

## Requested Verdict

GO to prepare a first commit package manifest and final pre-stage checklist, or
NO-GO with required revisions.

This proposal does not request permission to stage, commit, push, merge,
deploy, change credentials, force-add ignored files, rewrite history, or mutate
formal GT-KB artifacts. Those actions still require explicit owner approval.

## Claim

GT-KB mass adoption is ready for a controlled first package proposal after the
bridge-audit manifest was VERIFIED in
`bridge/gtkb-mass-adoption-bridge-audit-package-004.md` and after the current
GT-KB protocol implementation slices have bridge reports queued for Loyal
Opposition verification.

The next useful artifact is not a commit yet. It is a final package manifest
that tells Mike exactly what would be staged, what remains excluded, what
verification supports the package, and what owner approval would be needed.

## Priority Basis

- `GTKB-MASS-001` remains the top mass-adoption readiness work item after
  GT-KB proposal/verification gate enforcement.
- `bridge/gtkb-mass-adoption-bridge-audit-package-004.md` VERIFIED the narrow
  bridge-audit package manifest and explicitly required a fresh status check
  before later staging or commit.
- Current GT-KB upstream work includes protocol-scoped source/test changes for
  `GTKB-GOV-012` and `GTKB-CORE-001` that must be verified and packaged
  deliberately rather than mixed into an unclear dirty worktree commit.

## Scope In

1. Re-run git status in both relevant worktrees:
   - `E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement`
   - `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`
2. Re-run bridge status with protocol scope.
3. Produce a package manifest that separates:
   - bridge audit files;
   - GT-KB upstream source/test implementation files;
   - ignored reports;
   - generated/runtime artifacts;
   - unrelated or owner-owned dirty files.
4. Identify which bridge entries must be VERIFIED before the package can be
   staged.
5. Identify exact verification commands already run and any stale commands that
   must be rerun immediately before staging.
6. Produce a final pre-stage checklist with explicit owner approval gates.
7. File an implementation report on this bridge thread after the manifest is
   prepared.

## Scope Out

1. No `git add`, `git commit`, `git push`, merge, tag, release, or deployment.
2. No force-add of ignored reports.
3. No credential or environment mutation.
4. No cleanup of unrelated dirty files.
5. No `gt project upgrade --apply`.
6. No formal SPEC/GOV/PB/ADR/DCL/Deliberation Archive mutation.
7. No Agent Red application implementation changes.

## Proposed Package Classes

### Package A - Bridge Audit Trail

Include the current `bridge/INDEX.md` and referenced bridge files needed to
preserve the Prime Builder / Loyal Opposition audit trail, including files
created after the prior manifest if they remain untracked.

### Package B - GT-KB Protocol Implementation

Include only upstream GT-KB files tied to VERIFIED or GO-backed protocol work,
currently expected to include:

- bridge enforcement and gate files for `GTKB-GOV-012`;
- core-spec catalog/evaluator files for `GTKB-CORE-001`;
- read-only core-spec CLI files for `GTKB-CORE-001` after Phase 3A
  verification.

### Package C - Explicit Exclusions

Leave out ignored reports, generated runtime artifacts, unrelated dirty files,
application source changes, credentials, local settings, and any unverified
implementation handoff that has not reached the required lifecycle state.

## Verification Commands

Run in Agent Red:

```powershell
$env:PYTHONPATH='E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/src'
python -m groundtruth_kb bridge status --dir . --scope protocol
git diff --check -- bridge/INDEX.md bridge/*.md
python -m pytest tests/scripts/test_standing_backlog_harvest.py -q --tb=short
```

Run in GT-KB:

```powershell
python -m pytest -q --tb=short
python -m ruff check .
python -m ruff format --check .
python -m mypy --strict src tests
```

If full GT-KB mypy remains too broad for current repo policy, the manifest must
state the exact scoped mypy substitute and why it is acceptable for the package.

## Risks And Controls

### Risk: commit scope mixes verified and unverified protocol work

Control: classify files by bridge lifecycle and exclude any implementation
slice awaiting required Loyal Opposition verification unless Mike explicitly
approves a draft/review branch package.

### Risk: ignored reports disappear from the audit trail

Control: list ignored reports as evidence but do not force-add them unless Mike
explicitly approves an ignore-policy exception.

### Risk: staging starts before owner approval

Control: this proposal authorizes only manifest preparation and a pre-stage
checklist. Staging and commit remain separate owner-approved actions.

## Decision Needed From Owner

None at proposal time.

After Loyal Opposition review and manifest preparation, Mike will need one
explicit decision before any staging or commit: approve, revise, or defer the
exact package.
