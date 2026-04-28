---
name: Pre-production means no graceful migration needed
description: Owner rejects incremental migration while in pre-production. Build target state directly, one-time DB migration is fine.
type: feedback
---

While in pre-production, graceful step-wise migration is unnecessary. The goal is to achieve the desired end-state as quickly as possible. No compatibility mapping, no read-time adapters, no legacy row handling.

**Why:** There are no production users to protect. Incremental migration adds complexity that only matters when you have live data you can't afford to lose or transform. Pre-production data can be migrated in one shot.

**How to apply:** When proposing architectural changes, do not add compatibility layers or gradual migration paths. Codex recommended incremental migration with compatibility mapping for the bridge — owner overruled: one-time DB migration, collapse to target schema directly. Apply this principle to any pre-production refactor (bridge, identity model, etc.).
