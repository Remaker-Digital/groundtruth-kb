# Proposal: WI-3165 Chromatic Visual Regression CI Activation

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-11
**Session:** S281
**Spec:** SPEC-2102

---

## Objective

Activate Chromatic visual regression testing in CI for the widget Storybook.
All infrastructure is already installed — this work item only adds the GitHub
Actions workflow and requires the owner to set the CHROMATIC_PROJECT_TOKEN
repository secret.

## Existing Infrastructure

- `widget/package.json`: `chromatic@^11.0.0`, `storybook@^8.6.0`,
  `@storybook/preact-vite@^8.6.0`, `@storybook/addon-essentials@^8.6.0`,
  `@storybook/addon-a11y@^8.6.0`
- `widget/src/components/MessageBubble.stories.tsx`: 7 story variants
  (UserMessage, AgentMessage, LongMessage, StreamingMessage, RetractedMessage,
  SystemMessage, MessageWithMarkdownLink)
- `widget/src/components/MessageList.stories.tsx`: 6 story variants
  (Empty, SingleMessage, Conversation, WithTypingIndicator, WithGreeting,
  ScrollOverflow, WithQuickActions — note: file has 7 exports but QuickActions
  is the 7th)
- `widget/package.json` scripts: `build-storybook: storybook build`

## Implementation Plan

### 1. Create GitHub Actions workflow

`.github/workflows/chromatic.yml`:

```yaml
name: Chromatic

on:
  push:
    branches: [develop]
    paths: ['widget/**']
  pull_request:
    paths: ['widget/**']

jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for Chromatic to detect changes

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: widget/package-lock.json

      - name: Install dependencies
        working-directory: widget
        run: npm ci

      - name: Run Chromatic
        uses: chromaui/action@latest
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          workingDir: widget
          exitZeroOnChanges: true  # Don't fail CI, just flag for review
```

### 2. Owner action: set repository secret

The owner must create a Chromatic project at chromatic.com and set the
`CHROMATIC_PROJECT_TOKEN` GitHub repository secret. This is a one-time manual
step that cannot be automated.

### 3. Verification

After the first Chromatic run:
- 13 story baselines captured
- PR status check appears on PRs touching widget/
- Visual diff review available in Chromatic dashboard

## Files Changed

| File | Change |
|------|--------|
| `.github/workflows/chromatic.yml` | New: Chromatic CI workflow |

## Test Plan

1. Push workflow to develop
2. Verify GitHub Actions runs on next widget/ change
3. Verify 13 stories appear in Chromatic dashboard
4. Create a test PR with a minor widget style change
5. Verify visual diff appears in Chromatic review

## Risk Assessment

- **Low risk:** No production code changes. Workflow only runs on widget/ path changes.
- **No new dependencies:** All npm packages already installed.
- **Graceful failure:** `exitZeroOnChanges: true` means Chromatic diffs don't block PRs — they're flagged for review.
- **Cost:** Chromatic free tier allows 5,000 snapshots/month. At 13 stories per run, that's ~384 runs/month — well within limits.

## Review Questions for Codex

None — this is a straightforward CI workflow addition using existing infrastructure.
