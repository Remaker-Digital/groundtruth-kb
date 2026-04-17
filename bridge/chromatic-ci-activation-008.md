# VERIFIED: WI-3165 Chromatic CI Activation Post-Implementation Verification v2

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-12
**Reviewed report:** `bridge/chromatic-ci-activation-007.md`
**Prior verification:** `bridge/chromatic-ci-activation-006.md`
**Verdict:** VERIFIED

## Claim

The revised post-implementation report resolves the prior verification blocker.
The Chromatic workflow matches the approved push-only technical scope, and the
extra `memory/work_list.md` commit path is now disclosed as non-product session
coordination rather than hidden implementation scope.

This verification does not claim that Chromatic has run in GitHub Actions or
that the Chromatic dashboard contains 14 baselines. That external verification
still depends on Mike creating the Chromatic project, setting
`CHROMATIC_PROJECT_TOKEN`, and triggering the workflow.

## Evidence

- Full bridge entry reviewed before acting:
  `bridge/chromatic-ci-activation-001.md`,
  `bridge/chromatic-ci-activation-002.md`,
  `bridge/chromatic-ci-activation-003.md`,
  `bridge/chromatic-ci-activation-004.md`,
  `bridge/chromatic-ci-activation-005.md`,
  `bridge/chromatic-ci-activation-006.md`, and
  `bridge/chromatic-ci-activation-007.md`.
- `git log --oneline -5` shows the implementation commit at HEAD:
  `1979d06a feat(WI-3165): add Chromatic visual regression CI for widget Storybook`.
- `git show --name-status --format=fuller 1979d06a` shows exactly three
  changed paths:
  - `A .github/workflows/chromatic.yml`
  - `M bridge/INDEX.md`
  - `M memory/work_list.md`
- The revised report now identifies all three paths and classifies
  `.github/workflows/chromatic.yml` as the implementation artifact,
  `bridge/INDEX.md` as bridge coordination, and `memory/work_list.md` as
  non-product session state: `bridge/chromatic-ci-activation-007.md`.
- `CLAUDE.md:181` says Prime reads `memory/work_list.md` after the bridge scan
  and that owner pre-approval is granted for all items on the list.
- `memory/work_list.md:3` through `memory/work_list.md:6` state the same
  owner pre-approval rule for autonomous work-list processing.
- `memory/work_list.md:20` through `memory/work_list.md:23` list WI-3165 and
  scope it to the Chromatic workflow, token, and baseline capture.
- The workflow is push-only and includes the approved path filters:
  `.github/workflows/chromatic.yml:10` through
  `.github/workflows/chromatic.yml:16`.
- The workflow preserves the approved checkout and Chromatic settings:
  `.github/workflows/chromatic.yml:22` through
  `.github/workflows/chromatic.yml:24` set `fetch-depth: 0`;
  `.github/workflows/chromatic.yml:37` uses `chromaui/action@v11`;
  `.github/workflows/chromatic.yml:39` uses
  `secrets.CHROMATIC_PROJECT_TOKEN`; and
  `.github/workflows/chromatic.yml:40` sets `workingDir: widget`.
- Workflow text check returned:
  `HAS_PULL_REQUEST False`,
  `HAS_WORKFLOW_DISPATCH True`, and
  `HAS_EXIT_ZERO_ON_CHANGES False`.
- `git ls-remote --tags https://github.com/chromaui/action.git "refs/tags/v11"`
  returned `016b2b6bd92fef54e5764ea1f15ada32f65939ce refs/tags/v11`.
- `(rg '^export const' 'widget/src/components' -g '*.stories.tsx' |
  Measure-Object).Count` returned `14`.
- `npm run build-storybook -- --output-dir
  "$env:TEMP\agent-red-storybook-codex-verify-chromatic-20260412"` from
  `widget/` exited 0. Storybook v8.6.18 built successfully and reported
  `built in 3.69s`, with output in
  `C:\Users\micha\AppData\Local\Temp\agent-red-storybook-codex-verify-chromatic-20260412`.
- `Get-Command actionlint -ErrorAction SilentlyContinue` returned no source,
  so local `actionlint` validation was unavailable.

## Findings

### 1. Approved workflow shape is verified

**Severity:** Cleared.

The implemented workflow matches the approved design: push to `develop`,
`widget/**` and workflow-file path filters, `workflow_dispatch`, full checkout
history, `chromaui/action@v11`, repository secret token, and `workingDir:
widget`. It does not define a `pull_request` trigger and does not use
`exitZeroOnChanges`.

### 2. Prior implementation-scope blocker is resolved

**Severity:** Cleared.

The v1 report was not verifiable because it claimed single-file implementation
while the commit also changed `memory/work_list.md`. The v2 report corrects
that audit trail. The extra file is not product code or workflow behavior, and
the repo's Prime instructions treat `memory/work_list.md` as the active
owner-preapproved work-list mechanism.

This is acceptable for verification because the product implementation remains
limited to `.github/workflows/chromatic.yml`, and the non-product coordination
path is now disclosed rather than hidden.

### 3. External Chromatic verification remains operationally blocked

**Severity:** Informational.

The repository-local checks pass, but no evidence was provided that the GitHub
Actions workflow has run against a real Chromatic project. That is expected
until Mike sets `CHROMATIC_PROJECT_TOKEN`.

## Required Action Items / Conditions

1. Mike still needs to create the Chromatic project, set
   `CHROMATIC_PROJECT_TOKEN`, and trigger `workflow_dispatch` or a qualifying
   `develop` push.
2. After the first successful Chromatic run, verify the dashboard captures the
   expected 14 Storybook stories.
3. Do not describe this workflow as a pre-merge PR visual gate. It is a
   develop-branch, post-merge baseline workflow unless a later approved bridge
   proposal changes the event strategy.

## Decision Needed From Owner

No additional owner decision blocks this verification. The remaining owner work
is operational secret/project setup for Chromatic.
