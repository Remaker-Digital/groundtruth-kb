---
name: Visual verification via Chrome MCP is mandatory for all UI testing
description: Tests MUST include Chrome MCP visual inspection of each UI — no exceptions, regardless of time cost
type: feedback
---

Tests MUST include Chrome MCP verification of each UI. It is NOT acceptable to complete testing without a manual, visual inspection of each UI to verify that it functions completely and correctly from the perspective of a human user.

**Why:** The owner identified a systemic gap where UI testing was done via HTTP status codes and API responses, but never verified that the actual UI renders correctly in a browser. This led to "passing" tests while the widget launcher was invisible — a critical product failure.

**How to apply:**
- After any UI-affecting change, use Chrome MCP or Playwright to load the page and take a screenshot
- Verify visual elements are present, correctly positioned, and interactive
- Time required for this verification is irrelevant — always do it
- This applies to: widget launcher, admin console pages, Shopify storefront embed, any user-facing UI
- Never report a UI feature as "working" based solely on API responses
