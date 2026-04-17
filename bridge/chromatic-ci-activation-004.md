# GO: WI-3165 Chromatic Visual Regression CI Activation

**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-12
**Reviewed proposal:** `bridge/chromatic-ci-activation-003.md`
**Prior review:** `bridge/chromatic-ci-activation-002.md`
**Verdict:** GO

## Claim

The revised proposal addresses the five prior NO-GO findings well enough to
proceed with implementation. The approved scope is a push-only Chromatic
workflow for `develop`, not a per-PR visual regression gate.

## Evidence

- Full bridge entry reviewed: `bridge/chromatic-ci-activation-001.md`,
  `bridge/chromatic-ci-activation-002.md`, and
  `bridge/chromatic-ci-activation-003.md`.
- The revised proposal switches to push-only `develop` events:
  `bridge/chromatic-ci-activation-003.md:17`,
  `bridge/chromatic-ci-activation-003.md:19`,
  `bridge/chromatic-ci-activation-003.md:65`.
- The revised proposal keeps the token on trusted `push` execution and rejects
  fork/bot PR token exposure:
  `bridge/chromatic-ci-activation-003.md:26`,
  `bridge/chromatic-ci-activation-003.md:27`,
  `bridge/chromatic-ci-activation-003.md:30`,
  `bridge/chromatic-ci-activation-003.md:92`.
- The revised proposal adds both `workflow_dispatch` and the workflow file to
  the path filter:
  `bridge/chromatic-ci-activation-003.md:38`,
  `bridge/chromatic-ci-activation-003.md:66`,
  `bridge/chromatic-ci-activation-003.md:69`.
- The revised proposal corrects the story count to 14:
  `bridge/chromatic-ci-activation-003.md:46`,
  `bridge/chromatic-ci-activation-003.md:122`.
- The revised proposal pins Chromatic to the major tag:
  `bridge/chromatic-ci-activation-003.md:54`,
  `bridge/chromatic-ci-activation-003.md:90`.
- Official Chromatic GitHub Actions docs recommend `push` events for Chromatic
  because `pull_request` can use an unexpected baseline:
  <https://www.chromatic.com/docs/github-actions/> lines 464-470 as opened
  during review.
- Official Chromatic docs say forked repositories do not receive repository
  secrets and describe plaintext-token exposure as the cross-repository PR
  alternative:
  <https://www.chromatic.com/docs/github-actions/> lines 208-221 as opened
  during review.
- Official Chromatic docs support major-version action pinning with
  `chromaui/action@vX` and list GitHub tags as the source of available tags:
  <https://www.chromatic.com/docs/github-actions/> lines 223-230 as opened
  during review.
- `git ls-remote --tags https://github.com/chromaui/action.git "refs/tags/v11"`
  returned one matching `refs/tags/v11` tag, so `chromaui/action@v11` is a real
  action ref.
- Monorepo prerequisites are present: `widget/package.json:16` has
  `build-storybook`, `widget/package.json:31` has `chromatic`, and
  `widget/.storybook/main.ts:13` targets component story files.
- `rg -n "^export const" widget/src/components -g "*.stories.tsx"` found 14
  story exports across `MessageBubble.stories.tsx` and
  `MessageList.stories.tsx`; `(rg "^export const" ... | Measure-Object).Count`
  returned `14`.
- Local Storybook verification passed from `widget/`:
  `npm run build-storybook -- --output-dir C:\Users\micha\AppData\Local\Temp\agent-red-storybook-codex-97d6f3f201e54ddc90f430d68ba76551`.
  Result: exit code 0; Storybook v8.6.18 built successfully and reported
  preview output in 4.71s.
- No existing `.github/workflows/chromatic.yml` is present:
  `(Get-ChildItem .github/workflows -File -Filter chromatic.yml | Measure-Object).Count`
  returned `0`.

## Findings

### 1. Prior PR baseline risk is resolved

**Severity:** Previously High; cleared.

The revised workflow no longer uses the problematic default `pull_request`
checkout shape. The push-only strategy aligns with Chromatic's recommended
event model for reliable branch and baseline detection.

### 2. Token exposure policy is resolved

**Severity:** Previously Medium; cleared.

The proposal no longer requires repository secrets on forked PRs. The token is
only used for trusted `push` runs to `develop`, and the proposal explicitly
rejects fork/bot PR exposure for this private-repo workflow.

### 3. First-run validation path is addressed

**Severity:** Previously Medium; cleared.

The workflow can be triggered manually with `workflow_dispatch`, and the path
filter includes `.github/workflows/chromatic.yml`, so the initial workflow file
change is not excluded by its own `widget/**` filter.

### 4. Story count is corrected

**Severity:** Previously Low; cleared.

The revised proposal now uses 14 story baselines, matching the current story
exports in the repository.

### 5. Action pinning is addressed

**Severity:** Previously Low; cleared.

`chromaui/action@v11` follows Chromatic's documented major-version pinning
pattern and the `v11` tag exists upstream.

### 6. Push-only means no pre-merge PR gate

**Severity:** Low clarification.

The proposal explicitly selects `push` on `develop` and acknowledges "No per-PR
status check" at `bridge/chromatic-ci-activation-003.md:100`. The sentence at
`bridge/chromatic-ci-activation-003.md:105` saying reviewers can check impact
"before merging" should not be treated as a property of this workflow: a
develop-only push workflow runs after changes reach `develop`, unless someone
manually runs the workflow or later expands branch coverage.

**Required condition:** Implementation and follow-up verification must describe
this as a develop-baseline/post-merge visual check. Do not represent it as a
per-PR status check or pre-merge visual gate without a separate approved
workflow strategy.

## Required Action Items / Conditions

1. Implement only the proposed `.github/workflows/chromatic.yml` workflow.
2. Preserve `fetch-depth: 0`, `workingDir: widget`, and `chromaui/action@v11`.
3. Mike must create the Chromatic project and set the
   `CHROMATIC_PROJECT_TOKEN` repository secret before expecting a successful
   Chromatic run.
4. After implementation, verify an actual GitHub Actions run through
   `workflow_dispatch` or a `develop` push and confirm the Chromatic dashboard
   reports the expected 14 stories.
5. If pre-merge visual review becomes a requirement, submit a separate bridge
   proposal for branch-push or PR-head checkout behavior rather than extending
   this approved workflow implicitly.

## Decision Needed From Owner

No additional owner decision blocks implementation if Mike accepts the
push-only `develop` policy. The remaining owner action is operational: create
the Chromatic project and set `CHROMATIC_PROJECT_TOKEN`.
