---
name: UI Testing Tool Evaluation
description: Comparison of Applitools, Percy, Chromatic, axe-core for Agent Red visual/UX testing — Chromatic already installed
type: reference
---

## UI Testing Tool Evaluation (S281, 2026-04-11)

### Key Finding
Chromatic is already installed in `widget/package.json` (`chromatic@^11.0.0`).
Storybook is configured with `@storybook/preact-vite`, `addon-essentials`, and
`addon-a11y`. 13 story variants exist (`MessageBubble.stories.tsx`,
`MessageList.stories.tsx`). Only a CI step + project token are needed to activate.

axe-core is also partially present via `@storybook/addon-a11y` and via the
Python `tests/e2e/a11y_helpers.py` (SPEC-1846).

### Tool Comparison

| Tool | Free Tier | Playwright | Solo Dev Fit | Status |
|------|-----------|------------|-------------|--------|
| **Chromatic** | 5,000 snapshots/mo | Storybook-only | Excellent | **Already installed** |
| **axe-core** | Free (open source) | Native, low setup | Excellent | **Already partially integrated** |
| **Percy** | 5,000 screenshots/mo | Plugin, low setup | Good | Not installed |
| **Applitools** | 100 screenshots/mo | Native SDK | Fair (free tier tight) | Not installed |

### Recommended Order
1. **Activate Chromatic** — add GH Actions step + CHROMATIC_PROJECT_TOKEN (~1 hour)
2. **Add @axe-core/playwright** — automated WCAG CI enforcement (~30 min)
3. **Percy** — deferred, evaluate when E2E visual testing needs grow
4. **Applitools** — deferred, consider for multi-browser E2E visual parity
5. **Octomind** — free trial for auto-generated widget smoke tests (deferred)

### AI-Assisted E2E Tools
- **Momentic:** Limited fit — Claude Code already generates tests
- **Octomind:** Moderate fit — auto-generates Playwright tests from live app, self-heals selectors. Worth trial against staging widget after core tools are in place.
