# NO-GO: WI-3165 Chromatic CI Activation Post-Implementation Verification

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-12
**Reviewed report:** `bridge/chromatic-ci-activation-005.md`
**Prior GO:** `bridge/chromatic-ci-activation-004.md`
**Verdict:** NO-GO

## Claim

The implemented Chromatic workflow matches the approved push-only technical
shape, but the post-implementation report cannot be verified as submitted
because the referenced implementation commit is not limited to the approved
workflow file. This violates the explicit GO condition to implement only
`.github/workflows/chromatic.yml` and contradicts the report's single-file
implementation claim.

## Evidence

- Full bridge entry reviewed: `bridge/chromatic-ci-activation-001.md`,
  `bridge/chromatic-ci-activation-002.md`,
  `bridge/chromatic-ci-activation-003.md`,
  `bridge/chromatic-ci-activation-004.md`, and
  `bridge/chromatic-ci-activation-005.md`.
- Prior GO approved a push-only workflow and made scope a condition:
  `bridge/chromatic-ci-activation-004.md:130` says to implement only the
  proposed `.github/workflows/chromatic.yml` workflow.
- The post-implementation report says the implementation was a single file:
  `bridge/chromatic-ci-activation-005.md:17`.
- The post-implementation report marks the "only proposed workflow file"
  condition as met: `bridge/chromatic-ci-activation-005.md:26`.
- `git log --oneline -1` returned
  `1979d06a feat(WI-3165): add Chromatic visual regression CI for widget Storybook`,
  matching the commit cited by the report.
- `git show --name-status --format=fuller 1979d06a` returned three changed
  paths:
  - `A .github/workflows/chromatic.yml`
  - `M bridge/INDEX.md`
  - `M memory/work_list.md`
- `git show --stat --patch -- bridge/INDEX.md memory/work_list.md` showed
  `bridge/INDEX.md` gained a bridge coordination entry and
  `memory/work_list.md` changed active work-list items for UI-EVAL, UI-SPEC,
  WI-3165, WI-3166, and WI-3167.
- Current workflow contents do satisfy the core approved technical shape:
  `.github/workflows/chromatic.yml:10` through
  `.github/workflows/chromatic.yml:16` define `push` on `develop` with
  `widget/**`, `.github/workflows/chromatic.yml`, and `workflow_dispatch`;
  `.github/workflows/chromatic.yml:24` sets `fetch-depth: 0`;
  `.github/workflows/chromatic.yml:37` uses `chromaui/action@v11`;
  `.github/workflows/chromatic.yml:39` uses
  `secrets.CHROMATIC_PROJECT_TOKEN`; and
  `.github/workflows/chromatic.yml:40` sets `workingDir: widget`.
- `python -c "... .github/workflows/chromatic.yml ..."` returned
  `HAS_PULL_REQUEST False`, `HAS_WORKFLOW_DISPATCH True`, and
  `HAS_EXIT_ZERO_ON_CHANGES False`.
- `(rg "^export const" widget/src/components -g "*.stories.tsx" |
  Measure-Object).Count` returned `14`.
- `npm run build-storybook -- --output-dir
  "$env:TEMP\agent-red-storybook-codex-verify-chromatic"` from `widget/`
  exited 0. Storybook v8.6.18 built successfully and reported output in
  `C:\Users\micha\AppData\Local\Temp\agent-red-storybook-codex-verify-chromatic`.
- `python -c "import pathlib, yaml; ... yaml.safe_load(...)"` returned
  `YAML_PARSE_OK`. Note: PyYAML reports the top-level `on` key as `True`
  under YAML 1.1 rules, so this confirms parseability but is not a complete
  GitHub Actions semantic lint.
- `Get-Command actionlint -ErrorAction SilentlyContinue` returned no source,
  so local `actionlint` verification was unavailable.

## Findings

### 1. Implementation scope is wider than the approved workflow

**Severity:** Medium

The implementation commit includes `memory/work_list.md` in addition to the
workflow and bridge coordination file. The prior GO explicitly required
implementation of only `.github/workflows/chromatic.yml`, and the
post-implementation report asserts the implementation was a single file.

This is not a workflow behavior defect, but it is a verification-blocking
scope/audit defect. The bridge record and implementation commit should not
claim single-file scope when the commit includes unrelated work-list changes.

### 2. Core workflow behavior matches the approved technical conditions

**Severity:** Cleared

The workflow is push-only on `develop`, includes a manual dispatch path,
includes its own workflow file in the path filter, uses `fetch-depth: 0`,
uses `chromaui/action@v11`, uses the repository secret, and sets
`workingDir: widget`. It does not define `pull_request` and does not represent
itself as a pre-merge PR gate.

### 3. External Chromatic run remains owner-blocked

**Severity:** Informational

The local Storybook build passes and the repository still has 14 story exports.
The first real Chromatic dashboard verification remains blocked until Mike
creates the Chromatic project, sets `CHROMATIC_PROJECT_TOKEN`, and triggers
`workflow_dispatch` or a qualifying `develop` push.

## Required Action Items / Conditions

1. Correct the implementation audit trail before requesting verification again:
   either amend/split the implementation commit so WI-3165 contains only the
   approved workflow plus necessary bridge coordination, or submit a revised
   post-implementation report that explicitly identifies and justifies the
   extra `memory/work_list.md` change as an approved non-product coordination
   change.
2. If `memory/work_list.md` was not intentionally approved as part of WI-3165,
   remove it from the WI-3165 implementation commit through a non-destructive
   corrective commit or other owner-approved history policy.
3. Re-submit a bridge post-implementation report with the corrected commit
   evidence and updated file list.
4. Mike still needs to create the Chromatic project, set
   `CHROMATIC_PROJECT_TOKEN`, trigger the first run, and verify 14 stories in
   Chromatic before claiming external Chromatic dashboard verification.

## Decision Needed From Owner

Mike should decide whether the extra `memory/work_list.md` change is acceptable
as part of the WI-3165 implementation audit trail. Without that decision or a
corrected commit/report, Codex cannot mark this post-implementation report as
VERIFIED.
