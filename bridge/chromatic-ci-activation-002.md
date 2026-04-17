# NO-GO: WI-3165 Chromatic Visual Regression CI Activation

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-11
**Reviewed proposal:** `bridge/chromatic-ci-activation-001.md`
**Verdict:** NO-GO

## Claim

The widget Storybook/Chromatic infrastructure is present and the Storybook build
passes locally, but the proposed GitHub Actions workflow should not be approved
as written. The `pull_request` event shape can produce incorrect Chromatic
baselines, and the proposal does not define the repository-secret behavior for
forked PRs or other untrusted PR sources.

## Evidence

- Proposal uses `pull_request` with default checkout behavior:
  `bridge/chromatic-ci-activation-001.md:42`,
  `bridge/chromatic-ci-activation-001.md:44`,
  `bridge/chromatic-ci-activation-001.md:50`.
- Proposal uses `chromaui/action@latest` and a repository secret:
  `bridge/chromatic-ci-activation-001.md:66`,
  `bridge/chromatic-ci-activation-001.md:68`.
- Chromatic official docs recommend `push` events for Chromatic builds because
  `pull_request` can lose baselines or use an unexpected baseline from `main`.
  Source: <https://www.chromatic.com/docs/github-actions/>, "Recommended
  configuration for build events", lines 464-470 as opened during review.
- Chromatic official docs say that if `pull_request` is used, checkout should
  reference the PR head and set Chromatic branch/SHA/slug environment values.
  Source: <https://www.chromatic.com/docs/github-actions/>, lines 472-481.
- Chromatic official docs state forked repositories do not have access to
  repository secrets. Source: <https://www.chromatic.com/docs/github-actions/>,
  lines 220-222.
- Monorepo prerequisites are satisfied locally: `widget/package.json:16` has
  `build-storybook`, and `widget/.storybook/main.ts:12` targets
  `../src/components/**/*.stories.@(ts|tsx)`.
- Installed versions exist in the lockfile: `widget/package-lock.json:3057`
  for `chromatic`, `widget/package-lock.json:3059` resolves to
  `chromatic-11.29.0.tgz`, and `widget/package-lock.json:6099` resolves to
  `storybook-8.6.18.tgz`.
- Local verification command passed:
  `CI=true npm run build-storybook -- --output-dir %TEMP%\\agent-red-storybook-codex-<guid>`
  from `widget/`. Result: exit code 0; Storybook v8.6.18 built successfully
  in 3.50s with output in `%TEMP%`.
- Story baseline count in the proposal is wrong. `rg -n "^export const"
  widget/src/components -g "*.stories.tsx"` returned 14 story exports:
  seven in `widget/src/components/MessageBubble.stories.tsx:33` through
  `widget/src/components/MessageBubble.stories.tsx:102`, and seven in
  `widget/src/components/MessageList.stories.tsx:45` through
  `widget/src/components/MessageList.stories.tsx:146`. The proposal says
  "13 story baselines captured" at `bridge/chromatic-ci-activation-001.md:82`.
- No existing workflow file was present before implementation:
  `Test-Path .github/workflows/chromatic.yml` returned `False`.

## Findings

### 1. Incorrect-baseline risk for PR visual review

**Severity:** High

The proposal's PR workflow uses the default `pull_request` checkout shape. The
Chromatic docs warn this can compare against an unexpected baseline because
GitHub creates an ephemeral merge commit for `pull_request` workflows. This
directly threatens the stated objective of reliable PR visual diffs.

**Required action:** Revise the workflow event strategy. Prefer Chromatic's
recommended `push`-based configuration for relevant branches. If PR-triggered
runs are still required, add the documented PR-head checkout and Chromatic
environment variables before requesting approval again.

### 2. Secret availability for forked or untrusted PRs is undefined

**Severity:** Medium

The workflow requires `${{ secrets.CHROMATIC_PROJECT_TOKEN }}` on
`pull_request`. Chromatic documents that forked repositories do not have access
to repository secrets. As written, the proposal claims PR checks will appear for
PRs touching `widget/`, but it does not distinguish same-repository PRs from
forks or bot PRs.

**Required action:** Define the intended policy. Acceptable options include:
same-repository PRs only with an explicit skip/gating strategy for forks, a
push-only strategy, or an explicit owner-approved decision to expose a token for
open-source fork support.

### 3. Initial workflow validation is weak

**Severity:** Medium

The proposal filters both push and PR runs to `widget/**`, but the only proposed
changed file is `.github/workflows/chromatic.yml`. A PR that only adds the
workflow may not exercise the workflow. Existing repo workflows commonly include
`workflow_dispatch`, and several include their own workflow file in path
filters.

**Required action:** Add a validation path for the workflow itself and/or
`workflow_dispatch` so the first implementation can be exercised without a
throwaway widget change.

### 4. Story count and cost/test plan are inaccurate

**Severity:** Low

The proposal says 13 story baselines, but the repository currently exports 14
stories. The cost calculation and verification checklist should use 14 unless a
story is intentionally excluded.

**Required action:** Correct the baseline count and snapshot/month estimate, or
state which story will not be captured.

### 5. Action versioning is not pinned to the repo's reproducibility standard

**Severity:** Low

The proposal uses `chromaui/action@latest`. Chromatic documents that `latest`
auto-upgrades and that a major tag can avoid breaking changes while still
receiving non-breaking updates. The existing repository workflows generally pin
GitHub actions to major versions.

**Required action:** Pin the Chromatic action to an intentional major version or
explicitly document that the team accepts automatic Chromatic action upgrades.

## Recommended Revision

Submit a revised proposal that:

1. Uses a Chromatic-safe event strategy for branch/baseline detection.
2. Defines fork/bot PR behavior for `CHROMATIC_PROJECT_TOKEN`.
3. Adds `workflow_dispatch` and includes `.github/workflows/chromatic.yml` in
   the relevant path filters, or otherwise provides a first-run validation path.
4. Corrects the Storybook baseline count to 14.
5. Pins or explicitly justifies the Chromatic action version policy.

## Decision Needed From Owner

Mike needs to decide whether Chromatic should run on all PRs, same-repository
PRs only, or push events only. That decision determines the safe token and
baseline strategy.
