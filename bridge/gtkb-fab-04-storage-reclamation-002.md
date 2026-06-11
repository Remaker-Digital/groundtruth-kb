NO-GO

# Loyal Opposition Review: gtkb-fab-04-storage-reclamation-001

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition, harness A
**Date:** 2026-06-11

## Review Scope

Reviewed the full bridge thread:

- `bridge/gtkb-fab-04-storage-reclamation-001.md`

Same-session self-review guard: this Codex LO session did not author the Prime
Builder proposal. The proposal was authored by Prime Builder harness B,
session `07ef97df-2cb3-45a4-9c32-be60d702f29c`.

Dependency and precedence check: after FAB-02 received GO, FAB-04 is the oldest
remaining LO-actionable FAB proposal in `bridge/INDEX.md`. It is also a P1
destructive storage-reclamation item, so target-path precision matters before
implementation starts.

## Applicability Preflight

```
## Applicability Preflight

- packet_hash: `sha256:a723d30f9752acdd1dd4f58717e27c9db6b1d77a1b9fe62904ef1e4d58e71c9d`
- bridge_document_name: `gtkb-fab-04-storage-reclamation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-04-storage-reclamation-001.md`
- operative_file: `bridge/gtkb-fab-04-storage-reclamation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

## Clause Applicability Preflight

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-fab-04-storage-reclamation`
- Operative file: `bridge\gtkb-fab-04-storage-reclamation-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Authority Evidence

- `groundtruth-kb\.venv\Scripts\gt.exe deliberations get DELIB-FAB04-REMEDIATION-20260610`
  returned version 1 with outcome `owner_decision`, work item `WI-4416`, and
  the destructive cleanup decisions cited by the proposal.
- `PAUTH-FAB04-20260610` is active for `PROJECT-FABLE-INVESTIGATION`, includes
  `WI-4416`, and allows `file_deletion`, `repository_state`, `config`,
  `source`, and `docs`.
- The PAUTH forbids deleting the live `groundtruth.db` or any current MemBase
  file, deleting git-registered worktrees, and deleting tracked files outside
  the stated scope.

## Findings

### FINDING-P1-001 - `target_paths` omit planned test and repository-state mutations

The proposal's `target_paths` list does not cover all paths the proposal says
implementation will mutate.

The body proposes extending `scripts/hygiene/stray_detector.py` and verifying
with `pytest platform_tests/scripts/test_work_tree_stray_detector.py`, but
`platform_tests/scripts/test_work_tree_stray_detector.py` is not present in
`target_paths`. That test file exists in the repository, so either the proposal
expects a test edit and must list it, or it must explicitly say the existing
test is reused unchanged.

The body also proposes `git lfs prune` and `git gc`. The current `target_paths`
list names `.git/cursor/**` and `.git/*.index`, but not the material
repository-state paths affected by those commands, such as `.git/lfs/**`,
`.git/objects/**`, `.git/packed-refs`, or other `.git` state rewritten by GC.
Because this proposal is intentionally destructive and repository-state-heavy,
those paths cannot be left implicit.

**Impact:** Prime Builder could receive a GO whose implementation authorization
packet does not actually cover the planned destructive repository-state and
test-surface changes. That undermines the target-path guard before the riskiest
part of this work starts.

**Required change:** File a REVISED proposal that either:

- expands `target_paths` to cover the planned test file and the relevant `.git`
  repository-state mutation surfaces for `git lfs prune` and `git gc`; or
- narrows the proposed implementation to only the already-listed paths and
  explicitly removes/defer the uncovered test and repository-state operations.

## Verdict

NO-GO. The owner decision, PAUTH, and mandatory bridge preflights are otherwise
adequate, but the proposal needs a target-path correction before Loyal
Opposition can authorize destructive storage reclamation.
