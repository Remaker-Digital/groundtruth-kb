---
name: Public docs are release-gated
description: Public documentation and wiki must be kept current with same rigor as product code — not advisory
type: feedback
---

Public documentation (and design documents published to the wiki) must not be an afterthought. They must be kept current and correct, with the same rigor as product code.

**Why:** Owner directive S218. Stale docs create support burden and erode trust. Codex found internal SPA console references leaked into public docs — this class of error should be caught by the same gates as code errors.

**How to apply:** When changing product behavior that affects public-facing docs, update the docs in the same commit/PR. Include docs accuracy in release checklists. Treat docs drift as a defect, not a nice-to-have.
