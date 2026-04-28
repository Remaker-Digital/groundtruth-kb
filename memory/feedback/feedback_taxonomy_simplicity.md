---
name: Artifact taxonomy simplicity
description: Owner directive — collapse architecture type into ADR/DCL model, resist taxonomy bloat
type: feedback
---

Collapse the plain `architecture` spec type into the ADR/DCL model. No standalone `type='architecture'` going forward.

**Why:** The artifact taxonomy is becoming bloated and crisp, consistent distinctions are eroded by a bloated taxonomy. If a taxonomy is so simple that it creates too many artifacts per type, the solution is to prune artifacts for redundancy and simplify language — not add more types.

**How to apply:**
- Structural/architectural specs should be rewritten as ADR (decision + context + alternatives) + DCL (machine-checkable constraint) pairs
- Do not create new artifact types to solve classification ambiguity — simplify existing artifacts instead
- When in doubt, prune before expanding
- The 4 mislabeled specs (SPEC-0206, SPEC-0360, SPEC-1667, SPEC-1843) are queued for rewrite as ADR+DCL pairs
- Existing `type='architecture'` specs (SPEC-1705, SPEC-1706) should also be migrated
