---
name: Architecture specification tagging (GOV-21 pending)
description: Cross-cutting specs tagged architectural=true, loaded before implementation — lightweight approach approved S219
type: project
---

## Decision (S219)

Owner approved **lightweight architecture spec tagging** over Codex's heavier proposal (ARCH-* artifact type, 3 hard gates, formal waivers).

**What to implement:**
1. Tag existing specs with `architectural: true` in KB — no new artifact type
2. Add CLAUDE.md workflow step: "Before implementation, load architectural specs via `db.query_specs(architectural=True)`"
3. Record cross-cutting constraint rewrites as proper testable specs (not aspirational)
4. Exception handling: if implementation contradicts an architectural spec, flag and get owner approval (same as GOV-02)
5. Add to session wrap-up: RCA should reference which architectural constraint failed or was missing

**Why lightweight:** ~10-20 architectural specs = ~3,000 tokens. Targeted retrieval requires a mapping system more complex than just reading 20 specs. Formal waivers and hard gates are enterprise governance for a 2-person team.

**Codex's good points we kept:**
- Enforceable constraint rewrites (testable, not aspirational)
- Exception/waiver path (via GOV-02 owner consent)
- RCA should reference architectural constraints

**How to apply:** Implement as GOV-21 in S220 or later session. Tag initial set of architectural specs. Add CLAUDE.md workflow step.
