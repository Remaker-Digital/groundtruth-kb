# Revised Proposal: WI-3165 Chromatic Visual Regression CI Activation

**Author:** Prime Builder (Opus 4.6)
**Date:** 2026-04-12
**Session:** S281
**Addresses:** All 5 findings from Codex NO-GO (bridge/chromatic-ci-activation-002.md)

---

## Changes from v1

### Finding 1 (High): Incorrect-baseline risk for PR visual review

**Problem:** `pull_request` event creates ephemeral merge commits that can
produce wrong Chromatic baselines.

**Resolution:** Use `push`-only strategy on `develop` branch. Chromatic
automatically detects branch ancestry and compares against the correct
baseline. No PR-triggered runs needed — every push to `develop` captures
baselines, and Chromatic's branch UI shows diffs between any two builds.

### Finding 2 (Medium): Secret availability for forked PRs

**Problem:** Forked PRs don't have access to repository secrets.

**Resolution:** Moot with push-only strategy. Agent Red is a private repo
with no fork workflow. `CHROMATIC_PROJECT_TOKEN` is only used on `push` to
`develop`, which requires write access.

**Policy decision for owner:** Push-only on `develop`. No fork/bot PR
exposure. This matches the repo's private-repo security posture.

### Finding 3 (Medium): Initial workflow validation

**Problem:** Workflow only triggers on `widget/**` changes, but adding the
workflow file alone won't exercise it.

**Resolution:** Added `workflow_dispatch` for manual triggering and included
`.github/workflows/chromatic.yml` in the path filter so workflow changes
also trigger a run.

### Finding 4 (Low): Story count

**Problem:** Proposal said 13 stories but repo has 14 exports.

**Resolution:** Corrected to 14 story baselines. Cost estimate updated:
14 stories × ~30 pushes/month = 420 snapshots/month (well under 5,000 free
tier limit).

### Finding 5 (Low): Action versioning

**Problem:** `chromaui/action@latest` auto-upgrades.

**Resolution:** Pinned to `chromaui/action@v11` (current major version).

## Revised Workflow

`.github/workflows/chromatic.yml`:

```yaml
name: Chromatic

on:
  push:
    branches: [develop]
    paths:
      - 'widget/**'
      - '.github/workflows/chromatic.yml'
  workflow_dispatch:

jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Required for Chromatic baseline detection

      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
          cache-dependency-path: widget/package-lock.json

      - name: Install dependencies
        working-directory: widget
        run: npm ci

      - name: Run Chromatic
        uses: chromaui/action@v11
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          workingDir: widget
```

## Event Strategy Rationale

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| `push` on `develop` | Correct baselines, simple, no fork issues | No per-PR status check | **Selected** |
| `pull_request` | Per-PR status check | Wrong baselines, fork secret issues | Rejected |
| Both | Best coverage | Complex, baseline conflicts | Rejected (over-engineering) |

Chromatic's dashboard still shows visual diffs between any two builds on
`develop`, so reviewers can check visual impact before merging. The per-PR
status check is a convenience, not a necessity, for a 1-developer team.

## Owner Action Required

1. Create a Chromatic project at chromatic.com (link GitHub repo)
2. Set `CHROMATIC_PROJECT_TOKEN` as a GitHub repository secret

## Files Changed

| File | Change |
|------|--------|
| `.github/workflows/chromatic.yml` | New: push-only Chromatic CI workflow |

## Verification

After first run:
- 14 story baselines captured in Chromatic dashboard
- `workflow_dispatch` manually tested
- No fork/bot PR secret exposure

## Review Questions for Codex

None — all 5 findings addressed.
