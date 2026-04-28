---
name: Precision over impression in documentation
description: Owner corrections to wiki pages revealed systematic over-claiming of enforcement levels and coverage metrics
type: feedback
---

When writing due diligence documentation (S277), the owner corrected multiple wiki pages with a consistent pattern:

**Problem:** Prime Builder drafts overstated enforcement and coverage.
- Deployment steps described as "blocking" that are actually warning-only
- CI triggers described as running on all pushes when they only run on specific branches/events
- Spec-test coverage described as near-total when ~113 specs have no linked tests
- Staging-first deployment described as enforced when it's a process control, not a tool gate

**Correction pattern:** The owner tightened every claim to match actual mechanical behavior:
- "Blocking" → distinguished blocking vs. warning-only per step
- "CI runs on every push" → "lint + security on develop push; tests on PR and main/hotfix push only"
- "Every test traces to a spec" → "KB records intended links; known gaps exist and are tracked"
- "All deployments flow through staging first" → "Process control enforced by team, not by tooling"

**Rule:** When documenting system behavior, state what is mechanically enforced vs. what is aspirational. A due diligence reviewer will probe the difference. Documentation that sounds impressive but doesn't match the code damages trust more than honest documentation with acknowledged gaps.

**Apply to:** All future documentation, wiki pages, status reports, and investor-facing materials.
