---
name: GroundTruth Bootstrap Owner Decisions (2026-04-04)
description: Three approved decisions for GT bootstrap gap-closure — separate package, Phase 1+2 only, simplified bridge runtime
type: project
---

Owner approved 3 decisions for GroundTruth bootstrap gap-closure (S258, memo INSIGHTS-2026-04-04-08-12-00):

1. **Separate groundtruth-project-kit package** — not a subcommand in groundtruth-kb. Keeps upstream/downstream contract legible.
2. **Phase 1+2 only** — clarify product boundaries + create bootstrap scaffold layer. Gate review before Phase 3/4 commitment.
3. **Agent Red as reference behavior, simplified bridge as product** — don't copy AR runtime verbatim. Extract durable patterns (message schema, worker lifecycle, claim/resolve model) into a simplified reusable implementation.

**Why:** Prevents scope confusion in GT core, avoids overfunding infra automation before bootstrap contract is stable, avoids encoding AR-specific assumptions into the general product.

**How to apply:** When working on GT upstream, respect the package boundary. When implementing bridge/runtime features, derive from AR patterns but simplify for general use. Phase 3/4 (workstation doctor, cloud profiles) are deferred until Phase 2 is validated by at least one project besides Agent Red.

Evidence: bridge msg 467ae904, memo at independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-04-08-12-00-GROUNDTRUTH-OWNER-DECISION-MEMO.md
